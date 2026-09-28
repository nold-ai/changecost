"""Offline version and new changelog evidence validation."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Any

from packaging.version import InvalidVersion, Version

from quality.repository import changed, digest


def version_errors(canonical: str, previous: str | None, versions: list[str]) -> list[str]:
    try:
        version = Version(canonical)
        if previous and version < Version(previous):
            return ["package version decreased"]
        if not versions or any(Version(v) != version for v in versions):
            return ["conflicting package version metadata"]
    except InvalidVersion as exc:
        return [f"invalid version: {exc}"]
    return []


def unreleased(text: str) -> set[str]:
    match = re.search(r"^## Unreleased\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not match:
        return set()
    return {
        re.sub(r"\s+", " ", entry).strip()
        for entry in re.findall(r"^- (.+(?:\n(?!- |#)[ \t]+.+)*)", match[1], re.M)
    }


def changelog_errors(current: str, previous: str) -> list[str]:
    current = re.sub(r"\d{4}-\d{2}-\d{2}", "<date>", current)
    previous = re.sub(r"\d{4}-\d{2}-\d{2}", "<date>", previous)
    new = unreleased(current) - unreleased(previous)
    if not any(len(re.findall(r"[A-Za-z]{2,}", entry)) >= 3 for entry in new):
        return ["missing substantive new Unreleased changelog entry"]
    return []


def validate(
    root: Path, files: set[str], before: dict[str, bytes], exceptions: dict[str, Any]
) -> list[str]:
    project = tomllib.loads((root / "pyproject.toml").read_text())["project"]
    lock = tomllib.loads((root / "uv.lock").read_text())
    versions = [p["version"] for p in lock["package"] if p["name"] == project["name"]]
    old_project = tomllib.loads(before.get("pyproject.toml", b"").decode()).get("project", {})
    errors = version_errors(project["version"], old_project.get("version"), versions)
    affected = changed(root, files, before) - {"CHANGELOG.md", "quality/exceptions.json"}
    record = exceptions.get("changelog", {})
    valid_exception = (
        record.get("reason", "").strip()
        and record.get("digest") == digest(root, affected)
        and all(
            p.startswith("tests/")
            or (p.endswith(".md") and not p.startswith(("openspec/", ".agents/")))
            for p in affected
        )
    )
    if affected and not valid_exception:
        errors.extend(
            changelog_errors(
                (root / "CHANGELOG.md").read_text(), before.get("CHANGELOG.md", b"").decode()
            )
        )
    return errors
