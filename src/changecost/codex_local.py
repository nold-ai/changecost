from __future__ import annotations

import hashlib
import json
import math
import os
import stat
from collections import Counter
from datetime import UTC, datetime
from importlib.resources import files
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, ValidationError

from changecost.models import Digest, Evidence, Identifier, Model, NativeUsage
from changecost.operations import common
from changecost.serialization import ContractError, reject_constant, unique_members
from changecost.store import Store, reference

MAX_BYTES = 10485760
MAX_RECORDS = 10000
MAX_DEPTH = 32
CATEGORIES = (
    "input_tokens",
    "cached_input_tokens",
    "cache_write_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
    "total_tokens",
)


class NativeDiagnostic(Model):
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
        "unsupported_source_categories",
        "unsupported_source_quantity",
        "invalid_source_lineage",
        "unsupported_source_classification",
        "unsupported_source_header",
        "native_identity_conflict",
        "source_projection_mismatch",
        "unsupported_profile",
        "unadmitted_source",
        "invalid_native_selection",
    ]
    ordinal: Annotated[int, Field(strict=True, ge=0, lt=MAX_RECORDS)] | None = None


class NativeImportError(ContractError):
    """A closed diagnostic, independent of parser exceptions and private source values."""

    def __init__(self, code, ordinal=None):
        self.diagnostic = NativeDiagnostic.model_validate(dict(code=code, ordinal=ordinal))
        suffix = "" if ordinal is None else f":{ordinal}"
        super().__init__(self.diagnostic.code + suffix)


class CodexSelection(Model):
    repository_id: Identifier
    path: Path
    profile_id: Identifier
    expected_sha256: Digest


class NativeImportResult(Model):
    evidence_ids: list[str]
    fact_count: int
    inserted_fact_count: int
    status: str = "partial_diagnostics"
    diagnostics: list[str] = ["unknown_coverage", "unknown_finality", "no_numeric_authority"]


def _digest(value) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    )
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _packaged_admission():
    return json.loads(files("changecost").joinpath("codex_admission.json").read_text())


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
        raise NativeImportError("unsafe_source")
    if before.st_size > MAX_BYTES:
        raise NativeImportError("source_byte_limit")
    chunks, size = [], 0
    while True:
        block = os.read(descriptor, min(65536, MAX_BYTES + 1 - size))
        if not block:
            break
        chunks.append(block)
        size += len(block)
        if size > MAX_BYTES:
            raise NativeImportError("source_byte_limit")
    after = os.fstat(descriptor)
    if _metadata(before) != _metadata(after) or size != before.st_size:
        raise NativeImportError("unstable_source")
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
            raise NativeImportError("unsafe_source")
        descriptor = os.open(
            parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory
        )
        return _read_descriptor(descriptor)
    except OSError:
        raise NativeImportError("unsafe_source") from None
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
                raise NativeImportError("source_depth_limit")
        elif value in (93, 125):
            depth -= 1


def _integer(text):
    if len(text.lstrip("-")) > 4096:
        raise NativeImportError("source_numeric_limit")
    return int(text)


def _fraction(text):
    if len(text) > 4096:
        raise NativeImportError("source_numeric_limit")
    value = float(text)
    if not math.isfinite(value):
        raise NativeImportError("invalid_source_number")
    return value


def _parse(raw: bytes):
    _depth(raw)
    lines = raw.splitlines()
    if not lines or len(lines) > MAX_RECORDS:
        raise NativeImportError("source_record_limit")
    result = []
    for ordinal, line in enumerate(lines):
        try:
            row = json.loads(
                line,
                object_pairs_hook=unique_members,
                parse_constant=reject_constant,
                parse_int=_integer,
                parse_float=_fraction,
            )
            if not isinstance(row, dict) or not isinstance(row.get("payload"), dict):
                raise ValueError("invalid row")
            result.append(row)
        except (ValueError, RecursionError, UnicodeError):
            raise NativeImportError("invalid_source_record", ordinal) from None
    return result


def _source_id(kind, value):
    return None if value is None else _digest(["codex-source-id-v1", kind, value])


def _canonical_fact(record: NativeUsage):
    lineage = record.ownership.model_dump(exclude={"state"})
    interval = (
        "unknown" if record.interval.state == "unknown" else record.interval.model_dump(mode="json")
    )
    return dict(
        fact_key=_digest(
            [
                "codex-request-fact-v1",
                record.event_identity,
                record.accounting_scope,
                record.source_category,
            ]
        ),
        event_key=record.event_identity,
        mapping_revision=record.mapping_revision,
        category=record.source_category,
        scope=record.accounting_scope,
        quantity=record.quantity,
        quantity_basis=record.quantity_basis,
        backend_presence=record.backend_presence,
        producer=record.producer.model_dump(),
        source_lineage=lineage,
        request_interval=interval,
        model=record.model,
        model_version=record.model_version,
        coverage=record.coverage,
        completeness=record.scope_completeness,
        finality=record.finality,
    )


def _validate_request_payload(payload, header):
    required = {"thread_id", "turn_id", "session_id", "root_turn_id", "response_id"}
    if set(payload) != required | {"usage", "turn_token_usage", "thread_token_usage"}:
        raise NativeImportError("unsupported_source_shape")
    if any(not isinstance(payload[name], str) or not payload[name].strip() for name in required):
        raise NativeImportError("missing_source_identity")
    if payload["thread_id"] != header.get("id") or payload["session_id"] != header.get(
        "session_id"
    ):
        raise NativeImportError("source_identity_mismatch")
    if not isinstance(payload["usage"], dict) or set(payload["usage"]) != set(CATEGORIES):
        raise NativeImportError("unsupported_source_categories")
    if any(type(value) is not int for value in payload["usage"].values()):
        raise NativeImportError("unsupported_source_quantity")
    parent = header.get("parent_thread_id")
    if parent is not None and (not isinstance(parent, str) or not parent.strip()):
        raise NativeImportError("invalid_source_lineage")
    return parent


def _project_row(payload, header, envelope, repository_id):
    parent = _validate_request_payload(payload, header)
    event = _digest(
        [
            "codex-request-event-v1",
            "Codex",
            "desktop-coding",
            payload["thread_id"],
            payload["response_id"],
        ]
    )
    lineage = dict(
        thread=_source_id("thread", payload["thread_id"]),
        turn=_source_id("turn", payload["turn_id"]),
        session=_source_id("session", payload["session_id"]),
        root_turn=_source_id("turn", payload["root_turn_id"]),
        header_parent_thread=_source_id("thread", parent),
    )
    admission = envelope["admission"]
    return [
        NativeUsage.model_validate(
            dict(
                **common(
                    "pending",
                    datetime(1970, 1, 1, tzinfo=UTC),
                    _digest(["codex-request-fact-v1", event, "request", category]),
                ),
                repository_id=repository_id,
                evidence={"kind": "evidence", "record_id": event},
                mapping_revision=admission["mapping_revision"],
                producer=admission["projection_schema"]["producer"],
                first_acquisition_digest=admission["source_sha256"],
                first_admission={
                    "profile_digest": envelope["profile_digest"],
                    "approval_digest": envelope["approval_digest"],
                },
                event_identity=event,
                source_category=category,
                accounting_scope="request",
                quantity=payload["usage"][category],
                interval={"state": "unknown"},
                ownership={"state": "child" if parent else "unknown", **lineage},
            )
        )
        for category in CATEGORIES
    ]


def _select_requests(rows, admission):
    classification = admission["classification"]
    outer = Counter(row.get("type") for row in rows)
    events = Counter(row["payload"].get("type") for row in rows if row.get("type") == "event_msg")
    selected = [index for index, row in enumerate(rows) if row.get("type") == "token_usage_record"]
    if (
        len(rows) != admission["whole_record_count"]
        or outer != classification["outer_record_counts"]
        or events != classification["event_payload_type_counts"]
        or selected != admission["accepted_records"]
    ):
        raise NativeImportError("unsupported_source_classification")
    headers = [row["payload"] for row in rows if row.get("type") == "session_meta"]
    if len(headers) != 1:
        raise NativeImportError("unsupported_source_header")
    return selected, headers[0]


def _project(rows, envelope, repository_id):
    admission = envelope["admission"]
    selected, header = _select_requests(rows, admission)
    facts = {}
    for ordinal in selected:
        for fact in _project_row(rows[ordinal]["payload"], header, envelope, repository_id):
            if fact.record_id in facts and _canonical_fact(
                facts[fact.record_id]
            ) != _canonical_fact(fact):
                raise NativeImportError("native_identity_conflict")
            facts[fact.record_id] = fact
    ordered = [facts[key] for key in sorted(facts)]
    if (
        len(selected) != admission["expected_request_count"]
        or len(ordered) != admission["expected_fact_count"]
        or _digest([_canonical_fact(fact) for fact in ordered]) != admission["projection_sha256"]
    ):
        raise NativeImportError("source_projection_mismatch")
    return ordered


def _persist(records, store_id, now, facts, envelope):
    existing = {
        (r.event_identity, r.accounting_scope, r.source_category): r
        for r in records.values()
        if isinstance(r, NativeUsage) and r.previous is None
    }
    additions, evidence_ids, inserted = [], [], 0
    events = {
        r.event_identity: records[(r.evidence.kind, r.evidence.record_id)]
        for r in existing.values()
    }
    for fact in facts:
        prior = existing.get((fact.event_identity, fact.accounting_scope, fact.source_category))
        if prior is not None:
            if prior.repository_id != fact.repository_id or _canonical_fact(
                prior
            ) != _canonical_fact(fact):
                raise NativeImportError("native_identity_conflict")
            evidence_ids.append(prior.evidence.record_id)
            continue
        event = fact.event_identity
        evidence = events.get(event)
        if evidence is None:
            evidence = records.get(("evidence", event))
            if evidence is not None:
                raise NativeImportError("native_identity_conflict")
            evidence = Evidence(
                **common(store_id, now, event),
                provider="Codex",
                surface="desktop-coding",
                profile=envelope["profile_id"],
                identity_scope="namespaced",
                source_key=event,
            )
            events[event] = evidence
            additions.append(evidence)
        additions.append(
            fact.model_copy(
                update={**common(store_id, now, fact.record_id), "evidence": reference(evidence)}
            )
        )
        evidence_ids.append(evidence.record_id)
        inserted += 1
    return additions, NativeImportResult(
        evidence_ids=list(dict.fromkeys(evidence_ids)),
        fact_count=len(facts),
        inserted_fact_count=inserted,
    )


def import_codex_file(store: Store, selection: CodexSelection) -> NativeImportResult:
    """Import the packaged exact snapshot or reject before any source-derived write."""
    try:
        selection = CodexSelection.model_validate(selection.model_dump())
        envelope = _packaged_admission()
        if selection.profile_id != envelope["profile_id"]:
            raise NativeImportError("unsupported_profile")
        raw = _acquire(selection.path)
        rows = _parse(raw)
        digest = hashlib.sha256(raw).hexdigest()
        if digest != selection.expected_sha256 or digest != envelope["admission"]["source_sha256"]:
            raise NativeImportError("unadmitted_source")
        facts = _project(rows, envelope, selection.repository_id)
    except (ValidationError, KeyError, TypeError, OSError):
        raise NativeImportError("invalid_native_selection") from None
    return store.apply(lambda records, sid, now: _persist(records, sid, now, facts, envelope))
