"""Read-only behavioral evidence validation; review_session retains authority."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, ValidationError

from quality import repository, review_session

Text = Annotated[str, StringConstraints(strict=True, strip_whitespace=False, pattern=r"\S")]
Digest = Annotated[str, StringConstraints(pattern=r"^(?:[a-f0-9]{64}|<absent>)$")]


class Document(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Dependency(Document):
    invariants: list[Text]
    assumptions: list[Text]
    review_scope: Text


class Evidence(Document):
    id: Text
    command: Text
    tool: Text
    version: Text
    required: bool
    applicable: bool
    outcome: Literal["pass", "fail", "skipped", "unavailable", "unknown", "not_applicable"]
    binding: dict[str, Any]
    report: Text
    report_sha256: Annotated[str, StringConstraints(pattern=r"^[a-f0-9]{64}$")]
    rationale: str = ""


class Packet(Document):
    schema_version: Literal[1]
    change_id: Text
    intent: Text
    invariants: dict[Text, Text] = Field(min_length=1)
    trust_boundary: Text
    entrypoints: list[Text] = Field(min_length=1)
    assumptions: dict[Text, Text]
    known_findings: list[Text]
    binding: dict[str, Any]
    inputs: dict[Text, Digest] = Field(min_length=1)
    input_roles: dict[Text, list[Text]]
    dependencies: dict[Text, Dependency]
    evidence: list[Evidence] = Field(min_length=1)


def validate_structure(value: Any) -> Packet:
    packet = Packet.model_validate(value)
    if type(value["schema_version"]) is not int:
        raise ValueError("schema_version must be integer 1")
    for name in packet.inputs:
        review_session.validate_manifest_path(name)
    for role in ("specification", "oracle", "generator", "configuration"):
        names = packet.input_roles.get(role, [])
        if not names or not set(names) <= packet.inputs.keys():
            raise ValueError(f"missing or undeclared {role} inputs")
    if packet.dependencies.keys() != packet.inputs.keys():
        raise ValueError("every input requires explicit dependency coverage")
    for dependency in packet.dependencies.values():
        if not set(dependency.invariants) <= packet.invariants.keys():
            raise ValueError("unknown invariant in dependency mapping")
        if not set(dependency.assumptions) <= packet.assumptions.keys():
            raise ValueError("unknown assumption in dependency mapping")
    identities = [item.id for item in packet.evidence]
    if len(set(identities)) != len(identities) or not any(e.required for e in packet.evidence):
        raise ValueError("unique evidence identities and required evidence are needed")
    return packet


def changed_paths(root: Path, base: str) -> set[str]:
    diff = repository.git(root, "diff", "--name-only", "--no-renames", "-z", base)
    staged = repository.git(root, "diff", "--cached", "--name-only", "--no-renames", "-z", base)
    untracked = repository.git(root, "ls-files", "--others", "--exclude-standard", "-z")
    return set((diff + staged + untracked).decode().split("\0")) - {""}


def check_evidence(root: Path, packet: Packet, binding: dict) -> tuple[list[str], list[str]]:
    passed, errors = [], []
    for item in packet.evidence:
        problems = []
        review_session.validate_manifest_path(item.report)
        fingerprint = review_session.file_fingerprint(root, item.report)
        if fingerprint != item.report_sha256:
            problems.append("missing or changed report")
        if item.binding != binding:
            problems.append("stale evidence binding")
        if item.required and (not item.applicable or item.outcome != "pass"):
            problems.append("required analyzer did not explicitly pass")
        if (not item.applicable or item.outcome == "not_applicable") and not item.rationale.strip():
            problems.append("not-applicable evidence needs rationale")
        if item.applicable and item.outcome == "not_applicable":
            problems.append("not-applicable outcome contradicts applicability")
        errors.extend(f"{item.id}: {problem}" for problem in problems)
        if item.required and not problems:
            passed.append(item.id)
    return passed, errors


def context_changes(packet: Packet, previous: Packet | None) -> dict[str, Any]:
    if previous is None:
        return {}
    changes: dict[str, Any] = {}
    before, after = sorted(previous.known_findings), sorted(packet.known_findings)
    if before != after:
        changes["known_findings"] = dict(previous=before, current=after)
    fields = {"command", "tool", "version", "required", "applicable", "rationale"}
    old = {e.id: e.model_dump(include=fields) for e in previous.evidence}
    new = {e.id: e.model_dump(include=fields) for e in packet.evidence}
    definitions = {
        key: dict(previous=old.get(key), current=new.get(key))
        for key in sorted(old.keys() | new.keys())
        if old.get(key) != new.get(key)
    }
    if definitions:
        changes["evidence_definitions"] = definitions
    return changes


def impact(packet: Packet, previous: Packet | None, actual: dict[str, str], uncovered: set[str]):
    before = previous.inputs if previous else packet.inputs
    changes = {
        name for name in before.keys() | actual.keys() if before.get(name) != actual.get(name)
    }
    affected = [packet.dependencies[name] for name in changes if name in packet.dependencies]
    broad = previous is None or bool(uncovered or changes - packet.dependencies.keys())
    if previous:
        broad |= any(
            getattr(packet, field) != getattr(previous, field)
            for field in (
                "intent",
                "trust_boundary",
                "entrypoints",
                "invariants",
                "assumptions",
                "dependencies",
                "input_roles",
            )
        )
    context = context_changes(packet, previous)
    return dict(
        context_changes=context,
        changed_inputs=sorted(changes | uncovered),
        affected_invariants=sorted({x for d in affected for x in d.invariants}),
        affected_assumptions=sorted({x for d in affected for x in d.assumptions}),
        broader_review_required=broad or bool(context),
    )


def validate_packet(root: Path, value: Any, previous: Any = None) -> dict[str, Any]:
    """Check evidence freshness, never execute commands or grant PR completion."""
    result: dict[str, Any] = dict(
        evidence_status="incomplete", errors=[], passed_required=[], broader_review_required=True
    )
    try:
        packet = validate_structure(value)
        prior = validate_structure(previous) if previous is not None else None
        if prior is not None and prior.change_id != packet.change_id:
            raise ValueError("previous packet must identify the same change")
        session = review_session.packet(root, packet.change_id)
        binding = session["binding"]
        index = review_session.index_entries(repository.git(root, "ls-files", "--stage", "-z"))
        actual = {
            name: review_session.input_fingerprint(root, name, index) for name in packet.inputs
        }
        uncovered = changed_paths(root, binding["comparison_base"]) - packet.inputs.keys()
        unbound = packet.inputs.keys() - session["reviewed_manifest"].keys()
        errors = []
        if unbound:
            errors.append(
                "inputs absent from authoritative session manifest: " + ", ".join(sorted(unbound))
            )
        if actual != packet.inputs:
            errors.append("stale declared input fingerprints")
        if packet.binding != binding:
            errors.append("packet binding differs from review session")
        captured = review_session.capture_inputs(
            root, binding["head"], session["reviewed_manifest"]
        )
        if captured["digest"] != binding["input_digest"]:
            errors.append("review session inputs changed; refresh before new evidence")
        if uncovered:
            errors.append("uncovered changed inputs: " + ", ".join(sorted(uncovered)))
        passed, evidence_errors = check_evidence(root, packet, binding)
        errors.extend(evidence_errors)
        result.update(impact(packet, prior, actual, uncovered | unbound))
        result.update(
            errors=errors,
            passed_required=passed if not errors else [],
            evidence_status="incomplete" if errors else "current",
            session_status=session["status"],
            known_findings=packet.known_findings,
            session_findings=session["unresolved_findings"],
            evidence=[e.model_dump() for e in packet.evidence],
        )
    except (ValueError, OSError, KeyError, TypeError, ValidationError) as error:
        result["errors"] = [str(error)]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("--previous", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        value = json.loads(args.packet.read_text())
        prior = json.loads(args.previous.read_text()) if args.previous else None
        result = validate_packet(args.root, value, prior)
    except (OSError, ValueError) as error:
        result = dict(evidence_status="incomplete", errors=[str(error)])
    print(json.dumps(result, indent=2))
    return 0 if result["evidence_status"] == "current" else 1


if __name__ == "__main__":
    raise SystemExit(main())
