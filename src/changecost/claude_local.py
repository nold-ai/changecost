from __future__ import annotations

import hashlib
import json
import math
import os
import stat
from dataclasses import dataclass
from datetime import UTC, datetime
from importlib.resources import files
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, ValidationError

from changecost.models import Digest, Evidence, Identifier, Model, NativeUsage, RecordRef
from changecost.operations import common
from changecost.serialization import ContractError, reject_constant, unique_members
from changecost.store import Store, reference

MAX_BYTES = 10485760
MAX_RECORDS = 10000
MAX_DEPTH = 32
Vector = tuple[int | None, ...]


class ClaudeProjectSelection(Model):
    repository_id: Identifier
    path: Path
    profile_id: Identifier
    expected_sha256: Digest


class ClaudeProjectImportResult(Model):
    evidence_refs: list[RecordRef]
    fact_count: int
    inserted_fact_count: int
    replayed_fact_count: int
    corrected_fact_count: int
    status: Literal["partial_diagnostics"] = "partial_diagnostics"
    diagnostics: tuple[str, ...] = (
        "unknown_coverage",
        "unknown_backend_finality",
        "no_numeric_authority",
    )


class ClaudeDiagnostic(Model):
    code: Literal[
        "unsafe_source",
        "source_byte_limit",
        "unstable_source",
        "source_depth_limit",
        "source_numeric_limit",
        "invalid_source_number",
        "source_record_limit",
        "invalid_source_record",
        "unsupported_source_shape",
        "missing_source_identity",
        "source_identity_mismatch",
        "unsupported_source_quantity",
        "unsupported_profile",
        "unadmitted_source",
        "invalid_native_selection",
        "native_identity_conflict",
        "unsupported_source_stage",
        "unsupported_producer",
        "invalid_source_lineage",
    ]
    ordinal: Annotated[int, Field(strict=True, ge=0, lt=MAX_RECORDS)] | None = None


class ClaudeProjectImportError(ContractError):
    def __init__(self, code, ordinal=None):
        self.diagnostic = ClaudeDiagnostic(code=code, ordinal=ordinal)
        suffix = "" if ordinal is None else f":{ordinal}"
        super().__init__(code + suffix)


@dataclass(frozen=True)
class _Event:
    identity: str
    session: str
    partial: Vector | None
    terminal: Vector | None


def _digest(value):
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
        ).encode()
    ).hexdigest()


@dataclass(frozen=True)
class _ApprovedClaude:
    kind: Literal["terminal215", "desktop308"]
    envelope: dict


def _claude_admissions():
    resources: tuple[tuple[Literal["terminal215", "desktop308"], str], ...] = (
        ("terminal215", "claude_admission.json"),
        ("desktop308", "claude_desktop308_admission.json"),
    )
    catalogue = tuple(
        _ApprovedClaude(kind, json.loads(files("changecost").joinpath(resource).read_text()))
        for kind, resource in resources
    )
    if len({entry.envelope["profile_id"] for entry in catalogue}) != len(catalogue):
        raise ClaudeProjectImportError("unsupported_profile")
    return catalogue


def _select_claude(profile_id):
    for entry in _claude_admissions():
        if entry.envelope["profile_id"] == profile_id:
            return entry
    raise ClaudeProjectImportError("unsupported_profile")


def _metadata(value):
    return (
        value.st_dev,
        value.st_ino,
        value.st_mode,
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
    )


def _read_descriptor(descriptor):
    before = os.fstat(descriptor)
    if not stat.S_ISREG(before.st_mode):
        raise ClaudeProjectImportError("unsafe_source")
    if before.st_size > MAX_BYTES:
        raise ClaudeProjectImportError("source_byte_limit")
    chunks, size = [], 0
    while True:
        block = os.read(descriptor, min(65536, MAX_BYTES + 1 - size))
        if not block:
            break
        chunks.append(block)
        size += len(block)
        if size > MAX_BYTES:
            raise ClaudeProjectImportError("source_byte_limit")
    after = os.fstat(descriptor)
    if _metadata(before) != _metadata(after) or size != before.st_size:
        raise ClaudeProjectImportError("unstable_source")
    return b"".join(chunks)


def _acquire(path: Path) -> bytes:
    directory = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    descriptor = None
    try:
        parts = path.absolute().parts[1:]
        for part in parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory)
            directory = child
        if not parts:
            raise ClaudeProjectImportError("unsafe_source")
        descriptor = os.open(
            parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory
        )
        before = os.stat(parts[-1], dir_fd=directory, follow_symlinks=False)
        if _metadata(before) != _metadata(os.fstat(descriptor)):
            raise ClaudeProjectImportError("unstable_source")
        raw = _read_descriptor(descriptor)
        after = os.stat(parts[-1], dir_fd=directory, follow_symlinks=False)
        if _metadata(before) != _metadata(after) or _metadata(after) != _metadata(
            os.fstat(descriptor)
        ):
            raise ClaudeProjectImportError("unstable_source")
        return raw
    except OSError:
        raise ClaudeProjectImportError("unsafe_source") from None
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(directory)


def _depth(raw: bytes):
    depth, quoted, escaped = 0, False, False
    for value in raw:
        if quoted:
            if escaped:
                escaped = False
            elif value == 92:
                escaped = True
            elif value == 34:
                quoted = False
        elif value == 34:
            quoted = True
        elif value in (91, 123):
            depth += 1
            if depth > MAX_DEPTH:
                raise ClaudeProjectImportError("source_depth_limit")
        elif value in (93, 125):
            depth -= 1


def _integer(text):
    if len(text.lstrip("-")) > 4096:
        raise ClaudeProjectImportError("source_numeric_limit")
    return int(text)


def _fraction(text):
    if len(text) > 4096:
        raise ClaudeProjectImportError("source_numeric_limit")
    value = float(text)
    if not math.isfinite(value):
        raise ClaudeProjectImportError("invalid_source_number")
    return value


def _parse(raw: bytes):
    _depth(raw)
    lines = raw.splitlines()
    if not lines or len(lines) > MAX_RECORDS:
        raise ClaudeProjectImportError("source_record_limit")
    result = []
    for ordinal, line in enumerate(lines):
        try:
            row = json.loads(
                line.decode("utf-8-sig"),
                object_pairs_hook=unique_members,
                parse_constant=reject_constant,
                parse_int=_integer,
                parse_float=_fraction,
            )
            if not isinstance(row, dict):
                raise ValueError("invalid row")
            result.append(row)
        except (ValueError, RecursionError, UnicodeError):
            raise ClaudeProjectImportError("invalid_source_record", ordinal) from None
    return result


def _identifier(value, ordinal):
    if not isinstance(value, str) or not value.strip():
        raise ClaudeProjectImportError("missing_source_identity", ordinal)
    return value


def _desktop_shape(row, policy, ordinal):
    grammar = policy["classification"]
    kind = row.get("type")
    if kind == grammar["contributing_type"]:
        shape = grammar["contributing_shape"]
    elif kind == grammar["user"]["type"]:
        shape = grammar["user"]
    elif kind == grammar["api_request_blob"]["type"]:
        shape = grammar["api_request_blob"]
    else:
        shape = next((item for item in grammar["metadata"] if item["type"] == kind), None)
    if shape is None or not set(row) <= set(shape["allowed_top_level_keys"]):
        raise ClaudeProjectImportError("unsupported_source_shape", ordinal)
    if not set(shape.get("required_members", ())) <= set(row):
        raise ClaudeProjectImportError("unsupported_source_shape", ordinal)
    return kind == grammar["api_request_blob"]["type"]


def _noncontributor(row, policy, ordinal, desktop=False):
    if desktop and _desktop_shape(row, policy, ordinal):
        message = row["message"]
        if isinstance(message, dict) and "usage" in message:
            raise ClaudeProjectImportError("unsupported_source_shape", ordinal)
        return True
    kind = row.get("type")
    grammar = policy["classification"]
    if kind == grammar["contributing_type"]:
        return False
    if kind == grammar["user"]["type"]:
        message = row.get("message")
        valid = (
            isinstance(message, dict)
            and message.get("role") == grammar["user"]["message.role"]
            and "usage" not in message
            and "usage" not in row
        )
    else:
        types = (
            [item["type"] for item in grammar["metadata"]]
            if desktop
            else grammar["metadata"]["types"]
        )
        valid = kind in types and "message" not in row and "usage" not in row
    if not valid:
        raise ClaudeProjectImportError("unsupported_source_shape", ordinal)
    return True


def _desktop_contributor(row, policy, ordinal):
    if row.get("entrypoint") != policy["required_entrypoint"]:
        raise ClaudeProjectImportError("unsupported_producer", ordinal)
    if row.get("isSidechain") is not False or "agentId" in row:
        raise ClaudeProjectImportError("invalid_source_lineage", ordinal)
    message = row["message"]
    if message.get("stop_reason") not in policy["terminal_stop_reasons"]:
        raise ClaudeProjectImportError("unsupported_source_stage", ordinal)
    if any(
        type(message["usage"].get(category)) is not int or message["usage"][category] < 0
        for category in policy["source_categories"]
    ):
        raise ClaudeProjectImportError("unsupported_source_quantity", ordinal)


def _contributor(row, policy, ordinal, desktop=False):
    message = row.get("message")
    if (
        not isinstance(message, dict)
        or message.get("role") != "assistant"
        or not isinstance(message.get("usage"), dict)
    ):
        raise ClaudeProjectImportError("unsupported_source_shape", ordinal)
    if desktop:
        _desktop_contributor(row, policy, ordinal)
    session = _identifier(row.get("sessionId"), ordinal)
    request = _identifier(row.get("requestId"), ordinal)
    response = _identifier(message.get("id"), ordinal)
    _identifier(row.get("uuid"), ordinal)
    if row.get("version") != policy["producer"]["engine_version"]:
        raise ClaudeProjectImportError("unsupported_producer", ordinal)
    child, agent = row.get("isSidechain"), row.get("agentId")
    if (
        type(child) is not bool
        or (child and not isinstance(agent, str))
        or (not child and agent is not None)
    ):
        raise ClaudeProjectImportError("invalid_source_lineage", ordinal)
    if agent is not None:
        _identifier(agent, ordinal)
    if "stop_reason" not in message:
        raise ClaudeProjectImportError("unsupported_source_stage", ordinal)
    stop = message["stop_reason"]
    if stop is not None and stop not in policy["terminal_stop_reasons"]:
        raise ClaudeProjectImportError("unsupported_source_stage", ordinal)
    values = tuple(message["usage"].get(category) for category in policy["source_categories"])
    if any(value is not None and (type(value) is not int or value < 0) for value in values):
        raise ClaudeProjectImportError("unsupported_source_quantity", ordinal)
    metadata = (session, agent, request, response, row["version"], child)
    return metadata, values, stop


def _events(rows, policy, desktop=False):
    groups, requests, messages, uuids = {}, {}, {}, {}
    for ordinal, row in enumerate(rows):
        if _noncontributor(row, policy, ordinal, desktop):
            continue
        if "uuid" in row:
            uuid = _identifier(row["uuid"], ordinal)
            meaning = json.dumps(row, sort_keys=True, separators=(",", ":"))
            if uuid in uuids and uuids[uuid] != meaning:
                raise ClaudeProjectImportError("source_identity_mismatch", ordinal)
            uuids[uuid] = meaning
        metadata, values, stop = _contributor(row, policy, ordinal, desktop)
        session, agent, request, response, _, _ = metadata
        for index, identity in ((requests, request), (messages, response)):
            if identity in index and index[identity] != metadata:
                raise ClaudeProjectImportError("source_identity_mismatch", ordinal)
            index[identity] = metadata
        group = groups.setdefault(metadata, {})
        stage = "partial" if stop is None else "final"
        observation = (values, stop)
        if stage in group and group[stage] != observation:
            raise ClaudeProjectImportError("native_identity_conflict", ordinal)
        group[stage] = observation
    return tuple(
        _Event(
            _digest(["claude-project-event-v1", "Claude", "project-jsonl", *metadata[:4]]),
            _digest(["claude-project-source-id-v1", "session", metadata[0]]),
            group["partial"][0] if "partial" in group else None,
            group["final"][0] if "final" in group else None,
        )
        for metadata, group in groups.items()
    )


def _canonical_fact(record):
    return record.model_dump(
        mode="json",
        exclude={
            "schema_version",
            "schema",
            "kind",
            "record_id",
            "origin_store_id",
            "recorded_at",
            "effective_at",
            "evidence",
            "first_acquisition_digest",
            "first_admission",
            "previous",
            "reason",
        },
    )


def _revision_id(record):
    fact = _digest(
        ["claude-project-fact-v1", record.event_identity, "request", record.source_category]
    )
    return _digest(["claude-project-revision-v1", fact, _canonical_fact(record)])


def _project(event, values, stage, envelope, repository_id, source_digest):
    policy = envelope["admission"]
    result = []
    for category, quantity in zip(policy["source_categories"].values(), values, strict=True):
        fact = NativeUsage.model_validate(
            dict(
                **common("pending", datetime(1970, 1, 1, tzinfo=UTC), "pending"),
                repository_id=repository_id,
                evidence=RecordRef(kind="evidence", record_id=event.identity),
                mapping_revision=policy["mapping_revision"],
                producer=policy["producer"],
                first_acquisition_digest=source_digest,
                first_admission={
                    "profile_digest": envelope["profile_digest"],
                    "approval_digest": envelope["approval_digest"],
                },
                event_identity=event.identity,
                source_category=category,
                accounting_scope="request",
                quantity=quantity,
                interval={"state": "unknown"},
                ownership={"state": "unknown", "session": event.session},
                finality=stage,
            )
        )
        result.append(fact.model_copy(update={"record_id": _revision_id(fact)}))
    return result


def import_claude_project(
    store: Store, selection: ClaudeProjectSelection
) -> ClaudeProjectImportResult:
    try:
        selection = ClaudeProjectSelection.model_validate(selection.model_dump())
        selected = _select_claude(selection.profile_id)
        envelope = selected.envelope
        raw = _acquire(selection.path)
        source_digest = hashlib.sha256(raw).hexdigest()
        if source_digest != selection.expected_sha256:
            raise ClaudeProjectImportError("unadmitted_source")
        events = _events(_parse(raw), envelope["admission"], selected.kind == "desktop308")
        if not events:
            return ClaudeProjectImportResult(
                evidence_refs=[],
                fact_count=0,
                inserted_fact_count=0,
                replayed_fact_count=0,
                corrected_fact_count=0,
            )
        return store.apply(
            lambda records, sid, now: _persist(
                records, sid, now, events, envelope, selection.repository_id, source_digest
            )
        )
    except ClaudeProjectImportError:
        raise
    except (ValidationError, KeyError, TypeError, OSError):
        raise ClaudeProjectImportError("invalid_native_selection") from None


HistoryState = Literal["empty", "partial", "terminal", "refined"]
_HISTORY_STATES: dict[frozenset[str], HistoryState] = {
    frozenset(): "empty",
    frozenset({"partial"}): "partial",
    frozenset({"final"}): "terminal",
    frozenset({"partial", "final"}): "refined",
}


def _stage_additions(history, incoming):
    state = _HISTORY_STATES[frozenset(history)]
    for stage, cohort in incoming.items():
        accepted = history.get(stage)
        if accepted is not None and any(
            _canonical_fact(fact) != _canonical_fact(accepted[fact.source_category])
            for fact in cohort
        ):
            raise ClaudeProjectImportError("native_identity_conflict")
    new_stages = set(incoming) - set(history)
    if state == "empty":
        return new_stages
    if state == "partial" and new_stages == {"final"} and "partial" in incoming:
        return new_stages
    if new_stages:
        raise ClaudeProjectImportError("native_identity_conflict")
    return set()


def _persist_event(records, store_id, now, event, incoming, envelope):
    history = {}
    for record in records.values():
        if isinstance(record, NativeUsage) and record.event_identity == event.identity:
            history.setdefault(record.finality, {})[record.source_category] = record
    new_stages = _stage_additions(history, incoming)
    evidence = records.get(("evidence", event.identity))
    additions = []
    if not history:
        if evidence is not None:
            raise ClaudeProjectImportError("native_identity_conflict")
        evidence = Evidence(
            **common(store_id, now, event.identity),
            provider="Claude",
            surface="project-jsonl",
            profile=envelope["profile_id"],
            identity_scope="namespaced",
            source_key=event.identity,
        )
        additions.append(evidence)
    if not isinstance(evidence, Evidence) or evidence.profile != envelope["profile_id"]:
        raise ClaudeProjectImportError("native_identity_conflict")
    corrected = 0
    for stage in ("partial", "final"):
        if stage not in new_stages:
            continue
        cohort = {}
        for fact in incoming[stage]:
            prior = history.get("partial", {}).get(fact.source_category)
            updates = {**common(store_id, now, fact.record_id), "evidence": reference(evidence)}
            if prior is not None:
                updates.update(
                    previous=reference(prior),
                    reason=envelope["admission"]["refinement_reason"],
                    first_acquisition_digest=prior.first_acquisition_digest,
                    first_admission=prior.first_admission,
                )
                corrected += 1
            accepted = fact.model_copy(update=updates)
            cohort[fact.source_category] = accepted
            additions.append(accepted)
        history[stage] = cohort
    return additions, reference(evidence), corrected


def _persist(records, store_id, now, events, envelope, repository_id, source_digest):
    additions, evidence_refs = [], []
    inserted = corrected = replayed = 0
    for event in events:
        incoming = {
            stage: _project(event, values, stage, envelope, repository_id, source_digest)
            for stage, values in (("partial", event.partial), ("final", event.terminal))
            if values is not None
        }
        accepted, evidence, corrections = _persist_event(
            records, store_id, now, event, incoming, envelope
        )
        count = sum(isinstance(record, NativeUsage) for record in accepted)
        inserted += count
        corrected += corrections
        replayed += 4 if count == 0 else 0
        additions.extend(accepted)
        evidence_refs.append(evidence)
    return additions, ClaudeProjectImportResult(
        evidence_refs=evidence_refs,
        fact_count=4 * len(events),
        inserted_fact_count=inserted,
        corrected_fact_count=corrected,
        replayed_fact_count=replayed,
    )
