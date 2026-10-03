"""Bounded, read-only inspection. Diagnostics deliberately contain no source data."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import os
import stat
from pathlib import Path
from typing import Any

MAX_BYTES = 10 * 1024 * 1024
MAX_RECORDS = 10_000
MAX_DEPTH = 32


class EvidenceError(ValueError):
    """A fixed, public diagnostic code."""


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise EvidenceError("duplicate-member")
        result[key] = value
    return result


def _constant(_value):
    raise EvidenceError("nonfinite-number")


def _bounded(value, depth=0):
    if depth > MAX_DEPTH:
        raise EvidenceError("depth-limit")
    if isinstance(value, float) and not math.isfinite(value):
        raise EvidenceError("nonfinite-number")
    if isinstance(value, (dict, list)):
        if len(value) > MAX_RECORDS:
            raise EvidenceError("record-limit")
        for child in value.values() if isinstance(value, dict) else value:
            _bounded(child, depth + 1)


def _read(path: Path) -> bytes:
    """Hash and parse the same bounded bytes from one regular, non-link descriptor."""
    descriptor = None
    try:
        absolute = path.absolute()
        descriptor = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
        for component in absolute.parts[1:-1]:
            child = os.open(
                component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor
            )
            os.close(descriptor)
            descriptor = child
        leaf = os.open(
            absolute.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=descriptor
        )
        with os.fdopen(leaf, "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise EvidenceError("source-not-regular")
            raw = stream.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise EvidenceError("byte-limit")
        return raw
    except OSError:
        raise EvidenceError("source-unavailable") from None
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _parse(raw: bytes, fmt: str) -> Any:
    try:
        text = raw.decode("utf-8")
        if fmt == "json":
            value = json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant)
        elif fmt == "jsonl":
            lines = text.splitlines()
            if len(lines) > MAX_RECORDS or any(not line.strip() for line in lines):
                raise EvidenceError("record-limit-or-empty-line")
            value = [
                json.loads(line, object_pairs_hook=_pairs, parse_constant=_constant)
                for line in lines
            ]
        elif fmt == "csv":
            reader = csv.reader(io.StringIO(text, newline=""), strict=True)
            header = next(reader, [])
            if not header or len(set(header)) != len(header):
                raise EvidenceError("csv-header")
            rows = []
            for row in reader:
                if len(rows) >= MAX_RECORDS or len(row) != len(header):
                    raise EvidenceError("csv-shape")
                rows.append(row)
            value = [dict(zip(header, row, strict=True)) for row in rows]
        else:
            raise EvidenceError("unsupported-format")
        _bounded(value)
        return value
    except (UnicodeError, json.JSONDecodeError, csv.Error, RecursionError, OverflowError):
        raise EvidenceError("malformed-input") from None


def read_document(path: Path) -> Any:
    return _parse(_read(path), "json")


def _kind(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    return "object" if isinstance(value, dict) else "array"


def _field_types(rows, fields):
    if not isinstance(fields, list) or any(
        not isinstance(f, list) or not f or any(not isinstance(k, str) for k in f) for f in fields
    ):
        raise EvidenceError("field-selector")
    kinds = []
    for field in fields:
        counts = {}
        for row in rows:
            current = row
            for component in field:
                if not isinstance(current, dict) or component not in current:
                    kind = "missing"
                    break
                current = current[component]
            else:
                kind = _kind(current)
            counts[kind] = counts.get(kind, 0) + 1
        kinds.append(counts)
    return kinds


def inspect_manifest(manifest, register) -> list[dict]:
    """Structural findings only; caller-selected fields are reported by ordinal."""
    _bounded(manifest)
    _bounded(register)
    try:
        if manifest["format"] != "source-inspection/v1" or not isinstance(
            manifest["entries"], list
        ):
            raise EvidenceError("manifest-shape")
        profiles = {p["id"]: p for p in register["profiles"]}
        reports = []
        for index, entry in enumerate(manifest["entries"]):
            profile = profiles[entry["profile"]]
            evidence = next(e for e in profile["evidence"] if e["id"] == entry["evidence_id"])
            raw = _read(Path(entry["path"]))
            digest = hashlib.sha256(raw).hexdigest()
            if digest != entry["sha256"] or digest != evidence["sha256"]:
                raise EvidenceError("hash-mismatch")
            value = _parse(raw, entry["format"])
            rows = value if isinstance(value, list) else [value]
            kinds = _field_types(rows, entry["fields"])
            reports.append(
                {
                    "entry": index,
                    "sha256": digest,
                    "bytes": len(raw),
                    "records": len(rows),
                    "field_types": kinds,
                    "semantic_approval": False,
                }
            )
        return reports
    except (KeyError, TypeError, StopIteration, ValueError) as error:
        if isinstance(error, EvidenceError):
            raise
        raise EvidenceError("manifest-binding") from None
