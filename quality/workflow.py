"""Workflow syntax and conservative local/CI wiring checks."""

from __future__ import annotations

import subprocess
from pathlib import Path

import yaml


def validate(root: Path) -> list[str]:
    version = subprocess.run(
        ["actionlint", "--version"], capture_output=True, text=True, check=True
    )
    if version.stdout.splitlines()[0] != "1.7.12":
        return ["actionlint 1.7.12 is required"]
    paths = sorted((root / ".github/workflows").glob("*.yml"))
    paths += sorted((root / ".github/workflows").glob("*.yaml"))
    result = subprocess.run(
        ["actionlint", "-shellcheck=", "-pyflakes=", *map(str, paths)], cwd=root, check=False
    )
    errors = [] if result.returncode == 0 else ["workflow syntax validation failed"]
    config = yaml.load((root / ".github/workflows/quality.yml").read_text(), Loader=yaml.BaseLoader)
    events = config["on"]
    if not {"pull_request", "push", "workflow_dispatch"} <= events.keys():
        errors.append("quality workflow is missing a required event")
    for event in ("pull_request", "push"):
        if (
            events[event].get("branches") != ["main"]
            or {"paths", "paths-ignore"} & events[event].keys()
        ):
            errors.append(f"quality event incomplete: {event}")
    if config.get("permissions") != {"contents": "read"} or "pull_request_target" in events:
        errors.append("privileged quality workflow")
    text = (root / ".github/workflows/quality.yml").read_text()
    if "make check" not in text or "persist-credentials: false" not in text:
        errors.append("quality workflow must call the aggregate without persisted credentials")
    errors.extend(wiring_errors(config))
    return errors


def wiring_errors(config: dict) -> list[str]:
    job = config.get("jobs", {}).get("quality", {})
    errors = []
    if "if" in job or job.get("continue-on-error") not in {None, "false"}:
        errors.append("required quality job can be skipped or ignored")
    matrix = job.get("strategy", {}).get("matrix", {}).get("python", [])
    if matrix != ["3.11.15", "3.13.14"]:
        errors.append("required Python matrix changed without gate reconciliation")
    checks = [step for step in job.get("steps", []) if step.get("run", "").strip() == "make check"]
    if (
        len(checks) != 1
        or "if" in checks[0]
        or checks[0].get("continue-on-error") not in {None, "false"}
    ):
        errors.append("required aggregate must run unconditionally and propagate failure")
    return errors
