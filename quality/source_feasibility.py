"""Development-only source register, semantic controls and private inspection CLI."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

from quality.source_cases import STRATEGIES, evaluate_case
from quality.source_inspection import (
    EvidenceError,
    inspect_manifest,
    read_checked_document,
    read_document,
)

DECISIONS = ("authority", "interval", "replay", "reset", "correction", "exclusions")
CAPABILITIES = ("usage", "attribution", "billed_money", "finality")
DISPOSITIONS = {"supported", "partial", "unavailable", "unverified"}
CONCLUSIONS = {
    "cli-repeated-billing": ("authoritative_nano_aiu", "billed_money", "approved_profile"),
    "cli-missing-root": ("aggregate_billing", "completeness", "billed_money"),
    "multiplier-only": ("multiplier", "billed_money"),
    "ide-window-only": ("automatic_attribution", "unbound_record_count"),
    "tokens-only": ("input_tokens", "output_tokens", "cash_capability", "billed_money"),
    "timestamp-only": ("automatic_attribution", "unbound_record_count"),
    "ambiguous-overlap": ("completeness", "additive_total"),
    "correction": ("current_amount", "currency", "retained_revision_count", "approved_profile"),
    "codex-usage-snapshot": ("snapshot_total_tokens", "billed_money", "approved_profile"),
    "claude-estimated-cost": ("estimate_amount", "currency", "billed_money", "attribution"),
    "codex-rollout-cache-write": (
        "cache_write_field",
        "token_event_turn_id",
        "snapshot_total_tokens",
        "billed_money",
        "approved_profile",
    ),
    "claude-message-revisions": (
        "record_count",
        "request_count",
        "message_count",
        "usage_variant_count",
        "additive_total",
        "final_usage",
        "billed_money",
    ),
    "cursor-context-not-consumption": (
        "context_occupancy_tokens",
        "consumed_tokens",
        "billed_money",
        "session_finality",
        "approved_profile",
    ),
    "copilot-hosted-usage-boundaries": (
        "identity_namespaces_distinct",
        "overlapping_totals_additive",
        "missing_ephemeral_usage_is_zero",
        "final_session_nano_aiu",
        "billed_money",
        "approved_profile",
    ),
    "enterprise-projection-boundaries": (
        "cross_session_overlap",
        "native_wire_compatible",
        "consumed_tokens",
        "billing_correction_observed",
        "approved_profile",
    ),
    "copilot-container-absence": (
        "sdk_usage_checkpoint",
        "per_session_turn_usage",
        "consumed_tokens",
        "host_to_sdk_join",
        "approved_profile",
    ),
    "enterprise-message-counter-boundary": (
        "field_type_evidence",
        "repeat_semantics",
        "host_to_sdk_binding",
        "cache_inclusion",
        "additive_session_tokens",
        "billed_money",
        "approved_profile",
    ),
    "documented-example-not-wire-evidence": (
        "string_enum_valid_otlp_json",
        "integer_enum_valid_for_delta",
        "native_export_observed",
        "hook_mapping_verified",
        "approved_profile",
    ),
}
START = "<!-- source-profile-matrix:start -->"
END = "<!-- source-profile-matrix:end -->"
ROOT = Path(__file__).resolve().parents[1]

RESEARCH_PROFILES = (
    "copilot-cli",
    "copilot-ide",
    "cursor-personal-csv",
    "codex-app-server",
    "codex-desktop",
    "claude-2-1-275",
    "claude-2-1-215",
    "claude-2-1-257",
    "enterprise-copilot-projections",
    "enterprise-cursor-projections",
    "codex-ide",
    "claude-ide",
)


def profile_digest(profile):
    contents = {key: value for key, value in profile.items() if key != "approvals"}
    return hashlib.sha256(
        json.dumps(contents, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _https_destination(value):
    if not _text(value):
        return False
    parsed = urlsplit(value)
    return parsed.scheme == "https" and _text(parsed.hostname)


def _references_valid(references):
    if not isinstance(references, list) or not references:
        return False
    for reference in references:
        if not _text(reference["kind"]) or not _https_destination(reference["url"]):
            return False
        date.fromisoformat(reference["accessed"])
    return True


def _labels_valid(profile):
    return all(
        _text(profile[k]) and not any(c in profile[k] for c in "|\r\n")
        for k in ("provider", "surface", "version", "tier", "acquisition")
    )


def _capabilities_valid(capabilities):
    return set(capabilities) == set(CAPABILITIES) and all(
        value in DISPOSITIONS for value in capabilities.values()
    )


def _meanings_valid(profile):
    dispositions = set(profile["capabilities"].values())
    return (
        isinstance(profile["fields"], dict)
        and all(_text(k) and _text(v) for k, v in profile["fields"].items())
        and isinstance(profile["requirements"], list)
        and all(_text(v) for v in profile["requirements"])
        and (not dispositions.intersection({"supported", "partial"}) or bool(profile["fields"]))
        and (
            not dispositions.intersection({"partial", "unverified"})
            or bool(profile["requirements"])
        )
    )


def _profile_valid(profile, seen):
    identity = profile["id"]
    valid = bool(re.fullmatch(r"[a-z0-9-]{1,80}", identity)) and identity not in seen
    seen.add(identity)
    return (
        valid
        and _labels_valid(profile)
        and _capabilities_valid(profile["capabilities"])
        and _meanings_valid(profile)
        and _references_valid(profile["references"])
    )


def _evidence_valid(items):
    evidence = {}
    valid = isinstance(items, list) and bool(items)
    for item in items:
        valid = (
            valid
            and bool(re.fullmatch(r"[a-z0-9-]{1,80}", item["id"]))
            and item["id"] not in evidence
        )
        valid = (
            valid
            and bool(re.fullmatch(r"[a-f0-9]{64}", item["sha256"]))
            and item["origin"] in {"native", "synthetic", "documentation", "producer"}
            and _text(item.get("scope"))
        )
        evidence[item["id"]] = item
    return evidence, valid


def _approvals_valid(profile, evidence):
    approved = set()
    valid = isinstance(profile["approvals"], list)
    for proof in profile["approvals"]:
        item = evidence.get(proof["evidence_id"], {})
        capability = proof["capability"]
        valid = valid and capability in CAPABILITIES and capability not in approved
        valid = (
            valid
            and profile["capabilities"].get(capability) == "supported"
            and item.get("origin") == "native"
        )
        valid = (
            valid
            and item.get("sha256") == proof["sha256"]
            and profile_digest(profile) == proof["profile_digest"]
        )
        valid = valid and _text(proof["reviewer"]) and set(proof["decisions"]) == set(DECISIONS)
        valid = valid and all(_text(v) for v in proof["decisions"].values())
        approved.add(capability)
    return valid and all(
        v != "supported" or k in approved for k, v in profile["capabilities"].items()
    )


def validate_register(data) -> list[str]:
    """Validate reviewer bindings, never authenticate the human reviewer itself."""
    errors = []
    try:
        if (
            data["format"] != "source-profiles/v1"
            or not isinstance(data["profiles"], list)
            or not data["profiles"]
        ):
            return ["register-shape"]
        seen = set()
        for ordinal, profile in enumerate(data["profiles"]):
            evidence, valid = _evidence_valid(profile["evidence"])
            if not (
                _profile_valid(profile, seen) and valid and _approvals_valid(profile, evidence)
            ):
                errors.append(f"profile:{ordinal}:invalid-binding")
    except (KeyError, TypeError, ValueError, AttributeError):
        return ["register-shape"]
    return errors


def load_register(path: Path):
    data = read_document(path)
    if validate_register(data):
        raise EvidenceError("register-invalid")
    return data


def render_matrix(data):
    if validate_register(data):
        raise EvidenceError("register-invalid")
    lines = [
        START,
        "| Profile / version / tier | Usage | Attribution | Billed money | Finality |",
        "| --- | --- | --- | --- | --- |",
    ]
    for profile in data["profiles"]:
        name = f"{profile['id']} / {profile['version']} / {profile['tier']}"
        lines.append(
            "| " + " | ".join([name, *(profile["capabilities"][k] for k in CAPABILITIES)]) + " |"
        )
    return "\n".join([*lines, END])


def matrix_matches(text, data):
    return (
        not validate_register(data)
        and text.count(START) == 1
        and text.count(END) == 1
        and text[text.index(START) : text.index(END) + len(END)] == render_matrix(data)
    )


def check_cases(bundle) -> list[str]:
    try:
        samples = bundle["cases"]
        if len(samples) != len(STRATEGIES) or {s["id"] for s in samples} != set(STRATEGIES):
            return ["case-inventory"]
        errors = []
        for index, sample in enumerate(samples):
            expected = sample["expected"]
            if not isinstance(expected, dict):
                return ["case-invalid"]
            if set(expected) != set(CONCLUSIONS[sample["id"]]):
                errors.append(f"case:{index}:oracle-coverage")
                continue
            actual = evaluate_case(sample, STRATEGIES[sample["id"]])
            if (
                STRATEGIES[sample["id"]] == "hosted"
                and actual.get("checkpoint_conflict") is not False
            ):
                errors.append(f"case:{index}:conclusion-mismatch")
                continue
            if any(
                key not in actual or type(actual[key]) is not type(value) or actual[key] != value
                for key, value in expected.items()
            ):
                errors.append(f"case:{index}:conclusion-mismatch")
        return errors
    except (KeyError, TypeError, EvidenceError):
        return ["case-invalid"]


def _research_digest(register):
    entries = {(p["id"], e["id"]): e for p in register["profiles"] for e in p["evidence"]}
    hashes = set()
    for profile_id in RESEARCH_PROFILES:
        evidence = entries.get((profile_id, profile_id + "-e01"))
        if evidence is None or evidence["origin"] != "synthetic":
            raise EvidenceError("research-provenance-invalid")
        hashes.add(evidence["sha256"])
    if len(hashes) != 1:
        raise EvidenceError("research-provenance-invalid")
    return hashes.pop()


def _research_bundle(register):
    expected = _research_digest(register)
    try:
        return read_checked_document(
            ROOT / "docs/providers/fixtures/source-feasibility-cases.json", expected
        )
    except EvidenceError as error:
        if str(error) == "hash-mismatch":
            raise EvidenceError("research-provenance-invalid") from None
        raise


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise EvidenceError("arguments-invalid")


def main() -> int:
    parser = _Parser(description="Offline development evidence checks; no provider approval.")
    parser.add_argument(
        "--register", type=Path, default=ROOT / "docs/providers/source-profiles.json"
    )
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--matrix", action="store_true")
    try:
        args = parser.parse_args()
        register = load_register(args.register)
        if args.manifest:
            print(
                json.dumps(inspect_manifest(read_document(args.manifest), register), sort_keys=True)
            )
        elif args.matrix:
            print(render_matrix(register))
        else:
            errors = check_cases(_research_bundle(register))
            if not matrix_matches(
                (ROOT / "docs/providers/source-feasibility.md").read_text(), register
            ):
                errors.append("matrix-drift")
            print(json.dumps({"errors": errors, "semantic_approval": False}, sort_keys=True))
            return bool(errors)
        return 0
    except EvidenceError as error:
        print(error.public_diagnostic(), file=sys.stderr)
        return 1
    except (OSError, ValueError, TypeError):
        print("input-invalid", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
