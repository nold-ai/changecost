"""Require actual, content-bound SpecFact assurance; missing evidence fails closed."""

from __future__ import annotations

import json
import shutil
import subprocess
import uuid
from pathlib import Path
from typing import Any

from quality import external_tools
from quality.repository import digest

REQUIRED = {
    "ruff",
    "radon",
    "semgrep-clean",
    "ai-bloat-ast",
    "ast-clean-code",
    "basedpyright",
    "pylint",
    "contracts",
    "semgrep-bugs",
    "targeted-pytest-coverage",
}


def evidence_errors(report: dict[str, Any], expected: str) -> list[str]:
    errors: list[str] = []
    if report.get("digest") != expected:
        errors.append("missing/stale review content digest")
    if report.get("assurance_status") != "PASS" or report.get(
        "has_unknown_required_evidence", True
    ):
        errors.append("review assurance is incomplete or failed")
    analyzers = {entry["id"]: entry for entry in report.get("analyzer_evidence", [])}
    for name in sorted(REQUIRED):
        entry = analyzers.get(name, {})
        if entry.get("evidence_outcome") != "PASS" or entry.get("execution_state") != "ran":
            errors.append(
                f"required analyzer incomplete: {name}: {entry.get('diagnostic', 'missing')}"
            )
    if report.get("ci_exit_code") != 0 or report.get("overall_verdict") != "PASS":
        errors.append("review did not pass full enforcement")
    return errors


def run(root: Path, files: set[str]) -> list[str]:
    output = root / f".specfact/code-review-{uuid.uuid4().hex}.json"
    output.parent.mkdir(exist_ok=True)
    before = digest(root, files)
    result = subprocess.run(
        [
            external_tools.executable(root, "specfact"),
            "code",
            "review",
            "run",
            "--scope",
            "full",
            "--include-tests",
            "--bug-hunt",
            "--enforcement",
            "full",
            "--json",
            "--out",
            str(output),
        ],
        cwd=root,
        check=False,
    )
    if not output.exists():
        return ["SpecFact produced no review report"]
    shutil.copyfile(output, root / ".specfact/code-review.json")
    report = json.loads(output.read_text())
    report["digest"] = before
    if digest(root, files) != before:
        return ["review inputs changed during execution"]
    # Sidecar binds the untouched native report to the complete input inventory.
    (root / ".specfact/review-binding.json").write_text(
        json.dumps({"digest": before, "files": sorted(files)}, indent=2) + "\n"
    )
    errors = evidence_errors(report, before)
    if result.returncode and not errors:
        errors.append(f"SpecFact exited {result.returncode}")
    return errors
