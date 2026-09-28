"""Documentation coverage, source drift and local references."""

from __future__ import annotations

import fnmatch
import hashlib
import re
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

from quality.repository import changed, digest, safe_path


def maintained(name: str) -> bool:
    return name.endswith(".md") or name == "llms.txt"


def anchors(text: str) -> set[str]:
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    counts: dict[str, int] = {}
    found: set[str] = set(re.findall(r'<a\s+(?:name|id)=["\']([^"\']+)', text))
    for title in re.findall(r"^#{1,6}\s+(.+?)\s*#*$", text, flags=re.M):
        slug = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        found.add(f"{slug}-{count}" if count else slug)
    return found


def link_errors(root: Path, name: str, files: set[str]) -> list[str]:
    text = re.sub(r"```.*?```", "", safe_path(root, name).read_text(), flags=re.S)
    targets = re.findall(r'\[[^\]]*\]\(([^\s)]+)(?:\s+"[^"]*")?\)', text)
    targets += re.findall(r"^\s*\[[^\]]+\]:\s*(\S+)", text, flags=re.M)
    errors: list[str] = []
    for target in targets:
        parsed = urlsplit(target.strip("<>"))
        if parsed.scheme or parsed.netloc:
            continue
        path = (root / name).parent / unquote(parsed.path) if parsed.path else root / name
        try:
            relative = path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            errors.append(f"invalid reference {name}: {target}")
            continue
        valid = relative in files or any(p.startswith(relative + "/") for p in files)
        if not valid:
            errors.append(f"missing reference {name}: {target}")
        elif (
            parsed.fragment
            and path.is_file()
            and maintained(relative)
            and unquote(parsed.fragment) not in anchors(path.read_text())
        ):
            errors.append(f"missing reference anchor {name}: {target}")
    return errors


def source_names(patterns: list[str], files: set[str]) -> set[str]:
    return {name for name in files if any(fnmatch.fnmatchcase(name, p) for p in patterns)}


def _entry_errors(
    root: Path,
    entry: dict[str, Any],
    files: set[str],
    before: dict[str, bytes],
    exceptions: dict[str, Any],
) -> list[str]:
    name = entry["path"]
    errors: list[str] = []
    patterns = entry.get("sources", [])
    if not entry.get("owner") or entry.get("kind") not in {"manual", "generated"} or not patterns:
        errors.append(f"invalid ownership: {name}")
    for pattern in patterns:
        if not source_names([pattern], files):
            errors.append(f"orphaned source {name}: {pattern}")
    sources = source_names(patterns, files | before.keys()) - {name, "quality/exceptions.json"}
    sources -= {e for e in files if e in {"llms.txt", "docs/commands.md"}}
    prose = re.sub(r"\d{4}-\d{2}-\d{2}", "<date>", (root / name).read_text()).strip()
    old_prose = re.sub(r"\d{4}-\d{2}-\d{2}", "<date>", before.get(name, b"").decode()).strip()
    if sources & changed(root, files, before) and prose == old_prose:
        record = exceptions.get(name, {})
        if not record.get("reason", "").strip() or record.get("digest") != digest(root, sources):
            errors.append(
                f"stale documentation: {name}; update it or review a content-bound rationale"
            )
    return errors


def validate(
    root: Path,
    files: set[str],
    mapping: dict[str, Any],
    before: dict[str, bytes],
    exceptions: dict[str, Any],
) -> list[str]:
    entries = mapping.get("documents", [])
    immutable = mapping.get("immutable", {})
    names = [entry["path"] for entry in entries]
    errors = [f"duplicate ownership: {n}" for n in set(names) if names.count(n) != 1]
    for name in sorted({n for n in files if maintained(n)} - set(names) - immutable.keys()):
        errors.append(f"unowned documentation: {name}")
    for name, record in immutable.items():
        path = safe_path(root, name)
        if (
            name not in files
            or not record.get("reason")
            or hashlib.sha256(path.read_bytes()).hexdigest() != record.get("sha256")
        ):
            errors.append(f"immutable provenance mismatch: {name}")
    for entry in entries:
        name = entry["path"]
        if name not in files:
            errors.append(f"orphaned document: {name}")
            continue
        errors.extend(_entry_errors(root, entry, files, before, exceptions))
        errors.extend(link_errors(root, name, files))
    return errors
