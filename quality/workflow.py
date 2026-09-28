"""Workflow syntax and conservative local/CI wiring checks."""

from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

from quality import external_tools

CHECKOUT_ACTION = "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1"
AGGREGATE_COMMAND = "env -u MAKEFLAGS -u GNUMAKEFLAGS -u MFLAGS make check"
HEAD_REF = "${{ github.event.pull_request.head.sha || github.sha }}"

COMPARISON_ENV = {
    "EXPECTED_HEAD": HEAD_REF,
    "EVENT": "${{ github.event_name }}",
    "PR_BASE": "${{ github.event.pull_request.base.sha }}",
    "PUSH_BASE": "${{ github.event.before }}",
    "MANUAL_BASE": "${{ inputs.comparison_base }}",
}
# Deliberately validate the reviewed resolver, not arbitrary shell semantics.
COMPARISON_SCRIPT = """test "$(git rev-parse HEAD)" = "$EXPECTED_HEAD"
case "$EVENT" in
  pull_request) base=$(git merge-base HEAD "$PR_BASE") ;;
  push) base=$PUSH_BASE ;;
  workflow_dispatch) base=$MANUAL_BASE ;;
  *) exit 1 ;;
esac
resolved=$(git rev-parse --verify --end-of-options "$base^{commit}")
if test "$EVENT" = workflow_dispatch; then
  test "$resolved" != "$EXPECTED_HEAD"
fi
echo "BASE_REF=$resolved" >> "$GITHUB_ENV"
"""


def validate(root: Path) -> list[str]:
    actionlint = external_tools.executable(root, "actionlint")
    version = subprocess.run([actionlint, "--version"], capture_output=True, text=True, check=True)
    reported = version.stdout.splitlines()
    if not reported or reported[0] not in {"1.7.12", "v1.7.12"}:
        return ["actionlint 1.7.12 is required"]
    paths = sorted((root / ".github/workflows").glob("*.yml"))
    paths += sorted((root / ".github/workflows").glob("*.yaml"))
    result = subprocess.run(
        [actionlint, "-shellcheck=", "-pyflakes=", *map(str, paths)], cwd=root, check=False
    )
    errors = [] if result.returncode == 0 else ["workflow syntax validation failed"]
    for path in paths:
        candidate = yaml.load(path.read_text(), Loader=yaml.BaseLoader)
        errors.extend(f"{path.name}: {error}" for error in security_errors(candidate))
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
    text = (root / ".github/workflows/quality.yml").read_text()
    if "make check" not in text or "persist-credentials: false" not in text:
        errors.append("quality workflow must call the aggregate without persisted credentials")
    errors.extend(wiring_errors(config))
    return errors


def security_errors(config: dict) -> list[str]:
    """Apply the repository's read-only token and event policy to every workflow."""
    errors = []
    if config.get("permissions") != {"contents": "read"}:
        errors.append("workflow must declare contents: read permissions")
    if "pull_request_target" in config.get("on", {}):
        errors.append("privileged pull_request_target event is prohibited")
    if any(
        "permissions" in candidate and candidate["permissions"] != {"contents": "read"}
        for candidate in config.get("jobs", {}).values()
    ):
        errors.append("workflow jobs must retain contents: read permissions")
    return errors


def wiring_errors(config: dict) -> list[str]:
    job = config.get("jobs", {}).get("quality", {})
    errors = []
    if "if" in job or job.get("continue-on-error") not in {None, "false"}:
        errors.append("required quality job can be skipped or ignored")
    errors.extend(execution_errors(config))
    errors.extend(checkout_errors(job))
    errors.extend(capsule_setup_errors(job))
    errors.extend(comparison_errors(config))
    matrix = job.get("strategy", {}).get("matrix", {}).get("python", [])
    if matrix != ["3.11.15", "3.13.14"]:
        errors.append("required Python matrix changed without gate reconciliation")
    checks = [
        step for step in job.get("steps", []) if step.get("run", "").strip() == AGGREGATE_COMMAND
    ]
    if (
        len(checks) != 1
        or "if" in checks[0]
        or checks[0].get("continue-on-error") not in {None, "false"}
    ):
        errors.append("required aggregate must run unconditionally and propagate failure")
    return errors


def execution_errors(config: dict) -> list[str]:
    """Keep all quality run steps on the reviewed shell and repository directory."""
    expected = {"run": {"shell": "bash", "working-directory": "."}}
    job = config.get("jobs", {}).get("quality", {})
    errors = []
    if job.get("defaults") != expected:
        errors.append("quality execution defaults must declare Bash and repository root")
    if config.get("defaults") not in (None, expected):
        errors.append("workflow execution defaults differ from the reviewed context")
    for step in job.get("steps", []):
        if "run" in step and any(
            step.get(key, value) != value for key, value in expected["run"].items()
        ):
            errors.append("quality step execution context differs from Bash/repository root")
    return errors


def capsule_setup_errors(job: dict) -> list[str]:
    """Check the reviewed capsule host and required namespace prerequisite wiring."""
    errors = []
    if job.get("runs-on") != "ubuntu-24.04":
        errors.append("capsule prerequisite requires the reviewed Ubuntu 24.04 runner")
    setup = [step for step in job.get("steps", []) if step.get("id") == "capsule-userns"]
    if (
        len(setup) != 1
        or "if" in setup[0]
        or setup[0].get("continue-on-error") not in {None, "false"}
    ):
        errors.append("capsule namespace setup is missing or can be skipped")
    elif setup[0].get("env", {}).get("SPECFACT_CODE_REVIEW_CAPSULE_CACHE") != (
        "${{ runner.temp }}/changecost-capsules"
    ):
        errors.append("capsule cache must match the job-local AppArmor attachment")
    return errors


def comparison_errors(config: dict) -> list[str]:
    """Reject alternate bases that could silently empty the required CI diff."""
    job = config.get("jobs", {}).get("quality", {})
    steps = job.get("steps", [])
    errors = []
    scopes = [config, job, *steps]
    if any("BASE_REF" in scope.get("env", {}) for scope in scopes):
        errors.append("comparison base cannot be overridden by workflow/job/step environment")
    resolvers = [step for step in steps if step.get("name") == "Resolve comparison base"]
    if len(resolvers) != 1:
        return [*errors, "required comparison resolver is missing or duplicated"]
    resolver = resolvers[0]
    errors.extend(resolver_errors(resolver))
    checks = [step for step in steps if step.get("run", "").strip() == AGGREGATE_COMMAND]
    if checks and steps.index(resolver) > steps.index(checks[0]):
        errors.append("comparison resolver must precede the aggregate")
    if any("BASE_REF=" in step.get("run", "") for step in steps if step is not resolver):
        errors.append("comparison base must be exported only by the reviewed resolver")
    return errors


def resolver_errors(step: dict) -> list[str]:
    """Keep exact event inputs and the small reviewed shell resolver in sync."""
    errors = []
    if "if" in step or step.get("continue-on-error") not in {None, "false"}:
        errors.append("required comparison resolver can be skipped or ignored")
    if step.get("env") != COMPARISON_ENV:
        errors.append("comparison resolver event inputs differ from the reviewed contract")
    actual = [line.strip() for line in step.get("run", "").splitlines() if line.strip()]
    expected = [line.strip() for line in COMPARISON_SCRIPT.splitlines() if line.strip()]
    if actual != expected:
        errors.append("comparison resolver script differs from the reviewed contract")
    return errors


def checkout_errors(job: dict) -> list[str]:
    """Validate the one reviewed checkout before any repository commands run."""
    steps = job.get("steps", [])
    checkouts = [step for step in steps if step.get("uses", "").startswith("actions/checkout@")]
    if len(checkouts) != 1 or steps[0] is not checkouts[0]:
        return ["exactly one checkout must be the first quality step"]
    checkout = checkouts[0]
    errors = []
    expected = {"ref": HEAD_REF, "fetch-depth": "0", "persist-credentials": "false"}
    if checkout.get("uses") != CHECKOUT_ACTION or checkout.get("with") != expected:
        errors.append("checkout must retain the reviewed action pin, event head and safe inputs")
    if "if" in checkout or checkout.get("continue-on-error") not in {None, "false"}:
        errors.append("required checkout can be skipped or ignored")
    return errors
