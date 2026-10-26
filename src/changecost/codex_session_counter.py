"""Bounded local Codex lifetime counters with provisional authority only."""

from __future__ import annotations

import hashlib
import json
import math
import os
import stat
from dataclasses import asdict, dataclass
from pathlib import Path

from changecost.serialization import reject_constant, unique_members

MAX_BYTES = 128 * 1024 * 1024
MAX_RECORDS = 100_000
MAX_DEPTH = 32
MAPPING = "codex-desktop-session-counter/v1"
QUANTITY_BASIS = "latest-total-token-usage-total-tokens"
PRODUCER_FAMILY = "codex-desktop-observed-0163"
VERSIONS = {"0.163.0-alpha.10.2", "0.163.0-alpha.11.2"}
CATEGORIES = {
    "input_tokens",
    "cached_input_tokens",
    "cache_write_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
    "total_tokens",
}
TARGET = dict(
    mapping_revision=MAPPING,
    quantity_basis=QUANTITY_BASIS,
    producer_family=PRODUCER_FAMILY,
)


class CounterError(Exception):
    """Fixed diagnostics which never retain source values or parser exceptions."""

    def __init__(self, code: str, ordinal: int | None = None):
        super().__init__(code)
        self.code = code
        self.ordinal = ordinal

    def report(self) -> dict:
        result: dict = dict(
            schema="changecost/error-v1",
            code=self.code,
            message="provisional Codex source rejected",
        )
        if self.ordinal is not None:
            result["ordinal"] = self.ordinal
        return result


@dataclass(frozen=True)
class CodexCounterSnapshot:
    """Safe immutable projection, never an admission-bearing core observation."""

    source_identity_sha256: str
    source_sha256: str
    source_byte_count: int
    source_record_count: int
    reported_tokens: int
    counter_snapshot_count: int
    producer_version: str
    source_kind: str
    projection_sha256: str
    mapping_revision: str = MAPPING
    quantity_basis: str = QUANTITY_BASIS
    producer_family: str = PRODUCER_FAMILY
    producer_verified: bool = False
    coverage: str = "unknown"
    completeness: str = "unknown"
    finality: str = "unknown"
    subagent_inclusion: str = "unknown"

    def report(self) -> dict:
        return asdict(self)


def digest(value) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
        ).encode()
    ).hexdigest()


def _metadata(value):
    return (
        value.st_dev,
        value.st_ino,
        value.st_mode,
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
    )


def _integer(text):
    if len(text.lstrip("-")) > 4096:
        raise CounterError("source_numeric_limit")
    return int(text)


def _fraction(text):
    if len(text) > 4096:
        raise CounterError("source_numeric_limit")
    value = float(text)
    if not math.isfinite(value):
        raise CounterError("invalid_source_number")
    return value


def _depth(raw: bytes) -> None:
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
                raise CounterError("source_depth_limit")
        elif value in (93, 125):
            depth -= 1


def _parse(line: bytes, ordinal: int) -> dict:
    try:
        _depth(line)
        row = json.loads(
            line,
            object_pairs_hook=unique_members,
            parse_constant=reject_constant,
            parse_int=_integer,
            parse_float=_fraction,
        )
        if (
            not isinstance(row, dict)
            or not isinstance(row.get("type"), str)
            or not isinstance(row.get("payload"), dict)
        ):
            raise ValueError("invalid row")
        return row
    except CounterError as exc:
        raise CounterError(exc.code, ordinal) from None
    except (ValueError, RecursionError, UnicodeError):
        raise CounterError("invalid_source_record", ordinal) from None


def _source_kind(value) -> str:
    if value == "vscode":
        return "vscode"
    if isinstance(value, dict) and set(value) == {"subagent"}:
        variant = value["subagent"]
        if (
            isinstance(variant, dict)
            and set(variant) == {"thread_spawn"}
            and isinstance(variant["thread_spawn"], dict)
        ):
            return "subagent.thread_spawn"
    raise CounterError("unsupported_source_header")


def _header(payload: dict) -> dict:
    identity = payload.get("id")
    if not isinstance(identity, str) or not identity.strip() or len(identity) > 512:
        raise CounterError("missing_source_identity")
    runtime_identity = payload.get("session_id", identity)
    if (
        not isinstance(runtime_identity, str)
        or not runtime_identity.strip()
        or len(runtime_identity) > 512
    ):
        raise CounterError("missing_source_identity")
    if (
        payload.get("originator") != "Codex Desktop"
        or not isinstance(payload.get("cli_version"), str)
        or payload["cli_version"] not in VERSIONS
    ):
        raise CounterError("unsupported_source_header")
    return dict(
        source_identity_sha256=digest(["codex-provider-session-identity/v1", identity]),
        producer_version=payload["cli_version"],
        source_kind=_source_kind(payload.get("source")),
    )


def _usage(value) -> dict:
    if not isinstance(value, dict) or set(value) != CATEGORIES:
        raise CounterError("unsupported_source_categories")
    if any(
        type(quantity) is not int or not 0 <= quantity <= 2**63 - 1 for quantity in value.values()
    ):
        raise CounterError("unsupported_source_quantity")
    return value


def _counter(payload: dict) -> int | None:
    if "info" not in payload:
        raise CounterError("unsupported_source_shape")
    info = payload["info"]
    if info is None:
        return None
    if not isinstance(info, dict):
        raise CounterError("unsupported_source_shape")
    total = _usage(info.get("total_token_usage"))["total_tokens"]
    _usage(info.get("last_token_usage"))
    return total


@dataclass
class _Projection:
    header: dict | None = None
    latest: int | None = None
    snapshots: int = 0

    def accept(self, row: dict, ordinal: int) -> None:
        try:
            if row["type"] == "session_meta":
                if self.header is not None or ordinal != 0:
                    raise CounterError("unsupported_source_header")
                self.header = _header(row["payload"])
            elif row["type"] == "event_msg" and row["payload"].get("type") == "token_count":
                value = _counter(row["payload"])
                if value is not None:
                    if self.latest is not None and value < self.latest:
                        raise CounterError("source_counter_decreased")
                    self.latest = value
                    self.snapshots += 1
        except CounterError as exc:
            raise CounterError(exc.code, ordinal) from None

    def snapshot(self, source_hash: str, size: int, records: int) -> CodexCounterSnapshot:
        if self.header is None:
            raise CounterError("missing_source_identity")
        if self.latest is None:
            raise CounterError("missing_source_counter")
        projection = dict(
            **TARGET,
            **self.header,
            reported_tokens=self.latest,
            counter_snapshot_count=self.snapshots,
        )
        return CodexCounterSnapshot(
            **self.header,
            source_sha256=source_hash,
            source_byte_count=size,
            source_record_count=records,
            reported_tokens=self.latest,
            counter_snapshot_count=self.snapshots,
            projection_sha256=digest(projection),
        )


def _read_descriptor(descriptor: int, prefix_length: int) -> tuple[CodexCounterSnapshot, str]:
    before = os.fstat(descriptor)
    if not stat.S_ISREG(before.st_mode):
        raise CounterError("unsafe_source")
    if before.st_size > MAX_BYTES:
        raise CounterError("source_byte_limit")
    source_hash, prefix_hash = hashlib.sha256(), hashlib.sha256()
    projection = _Projection()
    size, records = 0, 0
    with os.fdopen(descriptor, "rb", closefd=False) as stream:
        while line := stream.readline(MAX_BYTES + 1 - size):
            previous_size = size
            size += len(line)
            if size > MAX_BYTES:
                raise CounterError("source_byte_limit")
            if records >= MAX_RECORDS:
                raise CounterError("source_record_limit")
            source_hash.update(line)
            prefix_hash.update(line[: max(0, prefix_length - previous_size)])
            projection.accept(_parse(line, records), records)
            records += 1
    after = os.fstat(descriptor)
    if _metadata(before) != _metadata(after) or size != before.st_size:
        raise CounterError("unstable_source")
    return projection.snapshot(source_hash.hexdigest(), size, records), prefix_hash.hexdigest()


def read_codex_counter(path: Path, *, prefix_length: int = 0) -> tuple[CodexCounterSnapshot, str]:
    """Stream the explicit file and hash exactly the requested predecessor prefix."""
    if type(prefix_length) is not int or not 0 <= prefix_length <= MAX_BYTES:
        raise ValueError("invalid prefix length")
    directory = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    descriptor = None
    try:
        parts = path.absolute().parts[1:]
        for part in parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory)
            directory = child
        if not parts:
            raise CounterError("unsafe_source")
        descriptor = os.open(
            parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory
        )
        return _read_descriptor(descriptor, prefix_length)
    except OSError:
        raise CounterError("unsafe_source") from None
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(directory)
