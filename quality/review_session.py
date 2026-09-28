"""Persist bounded review decisions outside an agent's transient context."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import math
import os
import subprocess
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from quality import repository

SCHEMA_VERSION = 1
DEFAULT_BATCHES = 3
DEFAULT_MINUTES = 90
WAIT_LIMIT_MINUTES = 30


class ConflictError(ValueError):
    """Raised when a writer attempts to update an obsolete state revision."""


def state_path(root: Path, change_id: str) -> Path:
    if not change_id or "/" in change_id or change_id in {".", ".."}:
        raise ValueError("change id must be a single non-empty path component")
    return root / ".changecost" / "workflow" / change_id / "review-session.json"


def initialize(root: Path, change_id: str, contract: dict[str, Any]) -> dict[str, Any]:
    validate_contract(contract)
    path = state_path(root, change_id)
    with state_lock(path):
        if path.exists():
            existing = load(root, change_id)
            if existing["contract"] != contract:
                raise ConflictError("session already exists with a different contract")
            return existing
        state: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "revision": 0,
            "change_id": change_id,
            "contract": contract,
            "reviewed_head": contract["head"],
            "inputs": capture_inputs(root, contract["head"]),
            "budget": {"batches": DEFAULT_BATCHES, "minutes": DEFAULT_MINUTES},
            "batches": 0,
            "active_minutes": 0,
            "events": [],
            "findings": [],
            "investigations": [],
            "scope_decisions": [],
            "evidence": [],
            "usage": {"cached_input": None, "uncached_input": None, "output": None, "cost": None},
            "monitor": {"snapshot": None, "data": None, "errors": [], "pending": []},
            "phase": "active",
        }
        write_state(path, state)
        return state


def validate_contract(contract: dict[str, Any]) -> None:
    if not isinstance(contract, dict):
        raise ValueError("contract must be an object")
    required = {
        "requirements",
        "acceptance_criteria",
        "non_goals",
        "trust_boundary",
        "intended_files",
        "base",
        "head",
        "required_reviewers",
        "required_checks",
        "required_statuses",
    }
    missing = sorted(required - contract.keys())
    if missing:
        raise ValueError(f"contract missing: {', '.join(missing)}")
    if not isinstance(contract["required_reviewers"], list) or not all(
        isinstance(reviewer, str) and reviewer for reviewer in contract["required_reviewers"]
    ):
        raise ValueError("required_reviewers must be a list of non-empty GitHub logins")
    validate_gate_contract(contract)


def validate_gate_contract(contract: dict[str, Any]) -> None:
    for key in ("required_checks", "required_statuses"):
        value = contract[key]
        if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
            raise ValueError(f"{key} must be an explicit list of gate identities")
    if not contract["required_checks"]:
        raise ValueError("required_checks must name at least one expected CI check")


def capture_inputs(root: Path, expected_head: str) -> dict[str, str]:
    head = repository.git(root, "rev-parse", "HEAD").decode().strip()
    if head != expected_head:
        raise ValueError("reviewed head differs from local HEAD")
    names = repository.git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
    files = set(names.decode().split("\0")) - {""}
    index = repository.git(root, "ls-files", "--stage", "-z")
    fingerprint = repository.digest(root, files).encode() + b"\0" + index
    return {"head": head, "digest": hashlib.sha256(fingerprint).hexdigest()}


def load(root: Path, change_id: str) -> dict[str, Any]:
    path = state_path(root, change_id)
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"unreadable session state: {error}") from error
    if not isinstance(value, dict) or value.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported or malformed session state")
    if value.get("change_id") != change_id or not isinstance(value.get("events"), list):
        raise ValueError("malformed session identity or events")
    if not isinstance(value.get("contract"), dict):
        raise ValueError("malformed session contract")
    validate_contract(value["contract"])
    validate_state_fields(value)
    validate_nested_state(value)
    return value


def validate_state_fields(value: dict[str, Any]) -> None:
    required = {
        "revision": int,
        "reviewed_head": str,
        "budget": dict,
        "batches": (int, float),
        "active_minutes": (int, float),
        "findings": list,
        "investigations": list,
        "scope_decisions": list,
        "evidence": list,
        "usage": dict,
        "monitor": dict,
        "phase": str,
    }
    if any(not isinstance(value.get(key), expected) for key, expected in required.items()):
        raise ValueError("malformed session state fields")
    if value["phase"] not in {"active", "paused", "complete"}:
        raise ValueError("malformed session phase")
    if (
        not {"batches", "minutes"} <= value["budget"].keys()
        or not {"snapshot", "data", "errors", "pending"} <= value["monitor"].keys()
    ):
        raise ValueError("malformed session budget or monitor")


def validate_nonnegative(value: Any, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be numeric")
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{label} must be finite and nonnegative")


def validate_entries(entries: Any, fields: tuple[str, ...]) -> None:
    if not isinstance(entries, list):
        raise ValueError("malformed entry list")
    for item in entries:
        if not isinstance(item, dict) or any(
            not isinstance(item.get(key), str) or not item[key] for key in fields
        ):
            raise ValueError("malformed persisted entry")


def validate_nested_state(state: dict[str, Any]) -> None:
    for key in ("revision", "batches", "active_minutes"):
        validate_nonnegative(state[key], key)
    for key in ("batches", "minutes"):
        validate_nonnegative(state["budget"][key], key)
    collections = {
        "events": ("id", "kind"),
        "findings": ("id", "family", "disposition"),
        "investigations": ("id", "family"),
        "scope_decisions": ("id", "decision"),
        "evidence": ("id", "evidence_type", "result", "head"),
    }
    for key, fields in collections.items():
        validate_entries(state[key], fields)
    for event in state["events"]:
        validate_event(event)
    validate_event_references(state["events"])
    validate_disposition_history(state)
    validate_monitor_state(state["monitor"])
    validate_inputs_usage(state)


def validate_inputs_usage(state: dict[str, Any]) -> None:
    inputs = state.get("inputs")
    if not isinstance(inputs, dict) or not all(
        isinstance(inputs.get(key), str) for key in ("head", "digest")
    ):
        raise ValueError("missing or malformed reviewed inputs; recovery required")
    for key in ("cached_input", "uncached_input", "output", "cost"):
        if key not in state["usage"]:
            raise ValueError("malformed usage")
        if state["usage"][key] is not None:
            validate_nonnegative(state["usage"][key], key)


def validate_monitor_state(monitor: dict[str, Any]) -> None:
    for key in ("errors", "pending"):
        if not isinstance(monitor[key], list) or not all(
            isinstance(item, str) for item in monitor[key]
        ):
            raise ValueError("malformed monitor messages")
    if monitor["data"] is not None and not isinstance(monitor["data"], dict):
        raise ValueError("malformed monitor data")


def validate_event(event: dict[str, Any]) -> None:
    fields = {
        "batch": (),
        "active_minutes": (),
        "extension": ("approved_by",),
        "finding": ("family",),
        "disposition": ("finding_id", "disposition"),
        "investigation": ("family",),
        "scope_decision": ("decision",),
        "evidence": ("evidence_type", "result", "head"),
        "usage": (),
        "phase": ("phase",),
        "advance_head": ("head",),
    }
    validate_entries([event], ("id", "kind"))
    if event["kind"] not in fields:
        raise ValueError("unknown persisted event kind")
    validate_entries([event], fields[event["kind"]])
    numeric_fields = {
        "active_minutes": ("minutes",),
        "extension": ("batches", "minutes"),
        "usage": ("cached_input", "uncached_input", "output", "cost"),
    }
    for key in numeric_fields.get(event["kind"], ()):
        validate_nonnegative(event.get(key, 0), key)


def validate_event_references(events: list[dict[str, Any]]) -> None:
    findings: set[str] = set()
    identities: set[str] = set()
    for event in events:
        if event["id"] in identities:
            raise ValueError("duplicate persisted event identity")
        identities.add(event["id"])
        if event["kind"] == "finding":
            findings.add(event["id"])
        if event["kind"] == "disposition" and event["finding_id"] not in findings:
            raise ValueError("persisted disposition names an unknown finding")


def validate_disposition_history(state: dict[str, Any]) -> None:
    expected: dict[str, str] = {}
    for event in state["events"]:
        if event["kind"] == "finding":
            expected[event["id"]] = "unresolved"
        if event["kind"] == "disposition":
            if event["disposition"] not in {"fixed", "non_finding", "accepted_exception"}:
                raise ValueError("malformed persisted disposition")
            expected[event["finding_id"]] = event["disposition"]
    actual = {item["id"]: item["disposition"] for item in state["findings"]}
    if actual != expected:
        raise ValueError("finding dispositions contradict recorded events; recovery required")


def write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(state, indent=2, sort_keys=True) + "\n"
    descriptor, temporary = tempfile.mkstemp(prefix="review-session-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w") as output:
            output.write(payload)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def state_lock(path: Path) -> Any:
    path.parent.mkdir(parents=True, exist_ok=True)
    with (path.parent / "review-session.lock").open("a+") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def record(
    root: Path, change_id: str, event: dict[str, Any], *, expected_revision: int | None = None
) -> dict[str, Any]:
    path = state_path(root, change_id)
    with state_lock(path):
        state = load(root, change_id)
        validate_event(event)
        if expected_revision is not None and state["revision"] != expected_revision:
            raise ConflictError(f"expected revision {expected_revision}, found {state['revision']}")
        event_id = event.get("id")
        kind = event.get("kind")
        if not isinstance(event_id, str) or not event_id or not isinstance(kind, str):
            raise ValueError("event requires non-empty id and kind")
        if duplicate_event(state["events"], event):
            return state
        apply_event(state, event)
        if kind == "advance_head":
            state["inputs"] = capture_inputs(root, state["reviewed_head"])
        state["events"].append(event)
        state["revision"] += 1
        validate_nested_state(state)
        write_state(path, state)
        return state


def duplicate_event(events: list[dict[str, Any]], event: dict[str, Any]) -> bool:
    existing = next((item for item in events if item["id"] == event["id"]), None)
    if existing is not None and existing != event:
        raise ConflictError("event identity already has a different payload")
    return existing is not None


def apply_event(state: dict[str, Any], event: dict[str, Any]) -> None:
    handlers = {
        "batch": add_batch,
        "active_minutes": add_active_minutes,
        "extension": add_extension,
        "finding": add_finding,
        "disposition": add_disposition,
        "investigation": add_investigation,
        "scope_decision": add_scope_decision,
        "evidence": add_evidence,
        "usage": add_usage,
        "phase": set_phase,
        "advance_head": advance_head,
    }
    try:
        handlers[event["kind"]](state, event)
    except KeyError as error:
        raise ValueError(f"unknown event kind: {event['kind']}") from error


def add_batch(state: dict[str, Any], event: dict[str, Any]) -> None:
    del event
    state["batches"] += 1


def add_active_minutes(state: dict[str, Any], event: dict[str, Any]) -> None:
    minutes = number(event, "minutes")
    if minutes < 0:
        raise ValueError("active minutes cannot be negative")
    state["active_minutes"] += minutes


def add_extension(state: dict[str, Any], event: dict[str, Any]) -> None:
    if not event.get("approved_by"):
        raise ValueError("budget extension requires approved_by")
    state["budget"]["batches"] += int(number(event, "batches", 0))
    state["budget"]["minutes"] += number(event, "minutes", 0)


def add_finding(state: dict[str, Any], event: dict[str, Any]) -> None:
    if not isinstance(event.get("family"), str) or not event["family"]:
        raise ValueError("finding requires family")
    state["findings"].append({**event, "batch": state["batches"], "disposition": "unresolved"})


def add_disposition(state: dict[str, Any], event: dict[str, Any]) -> None:
    finding_id = event.get("finding_id")
    disposition = event.get("disposition")
    accepted = {"fixed", "non_finding", "accepted_exception"}
    if not isinstance(finding_id, str) or disposition not in accepted:
        raise ValueError("disposition requires finding_id and a reviewed disposition")
    for finding in state["findings"]:
        if finding["id"] == finding_id:
            finding["disposition"] = disposition
            return
    raise ValueError("disposition names an unknown finding")


def add_investigation(state: dict[str, Any], event: dict[str, Any]) -> None:
    require_field(event, "family", "investigation")
    state["investigations"].append(event)


def add_scope_decision(state: dict[str, Any], event: dict[str, Any]) -> None:
    require_field(event, "decision", "scope decision")
    supersedes = event.get("supersedes")
    if supersedes and not any(
        item["id"] == supersedes and item["decision"] == "pending"
        for item in state["scope_decisions"]
    ):
        raise ValueError("scope resolution must name an existing pending decision")
    state["scope_decisions"].append(event)


def add_evidence(state: dict[str, Any], event: dict[str, Any]) -> None:
    require_field(event, "result", "evidence")
    if event.get("evidence_type") not in {"gate", "reviewer"}:
        raise ValueError("evidence requires evidence_type gate or reviewer")
    require_field(event, "head", "evidence")
    state["evidence"].append(event)


def add_usage(state: dict[str, Any], event: dict[str, Any]) -> None:
    for key in ("cached_input", "uncached_input", "output", "cost"):
        if key in event:
            value = number(event, key)
            prior = state["usage"][key]
            state["usage"][key] = value if prior is None else prior + value


def set_phase(state: dict[str, Any], event: dict[str, Any]) -> None:
    if event.get("phase") not in {"active", "paused", "complete"}:
        raise ValueError("unknown phase")
    state["phase"] = event["phase"]


def advance_head(state: dict[str, Any], event: dict[str, Any]) -> None:
    head = event.get("head")
    if not isinstance(head, str) or len(head) != 40:
        raise ValueError("advance_head requires a 40-character head")
    state["reviewed_head"] = head
    state["phase"] = "active"
    state["monitor"] = {"snapshot": None, "data": None, "errors": [], "pending": []}


def require_field(event: dict[str, Any], field: str, name: str) -> None:
    if not event.get(field):
        raise ValueError(f"{name} requires {field}")


def number(event: dict[str, Any], key: str, default: int | float | None = None) -> float:
    value = event.get(key, default)
    validate_nonnegative(value, key)
    return float(value)


def status(root: Path, change_id: str) -> dict[str, Any]:
    try:
        state = load(root, change_id)
        if capture_inputs(root, state["reviewed_head"]) != state["inputs"]:
            raise ValueError(
                "reviewed repository inputs changed; recovery or explicit head advancement required"
            )
    except ValueError as error:
        return {"action": "incomplete", "reason": str(error)}
    action, reason = decision(state)
    return {
        "action": action,
        "reason": reason,
        "revision": state["revision"],
        "batches": state["batches"],
        "active_minutes": state["active_minutes"],
        "budget": state["budget"],
    }


def decision(state: dict[str, Any]) -> tuple[str, str]:
    terminal = terminal_decision(state)
    family = family_decision(state)
    if terminal and terminal[0] == "complete" and family:
        return family
    if terminal and terminal[0] != "wait":
        return terminal
    budget = budget_decision(state)
    if budget:
        return budget
    return family or terminal or ("continue", "within budget with no escalation trigger")


def terminal_decision(state: dict[str, Any]) -> tuple[str, str] | None:
    if state["monitor"].get("head") and state["monitor"]["head"] != state["reviewed_head"]:
        return "incomplete", "monitor evidence is for a different head"
    if state["monitor"]["errors"]:
        return "incomplete", "monitor evidence is incomplete"
    scope = scope_pending(state)
    if scope:
        return "incomplete", "scope decision is pending"
    if state["monitor"].get("pending"):
        return "wait", "monitor is awaiting current-head reviewer results"
    if state["phase"] == "complete":
        return completed_decision(state)
    if state["phase"] == "paused":
        return "wait", "session is paused"
    return None


def scope_pending(state: dict[str, Any]) -> bool:
    resolved = {
        item.get("supersedes") for item in state["scope_decisions"] if item["decision"] != "pending"
    }
    return any(
        item["decision"] == "pending" and item["id"] not in resolved
        for item in state["scope_decisions"]
    )


def completed_decision(state: dict[str, Any]) -> tuple[str, str]:
    if unresolved_findings(state):
        return "incomplete", "completed session has unresolved findings"
    if not completion_evidence(state) or state["monitor"].get("head") != state["reviewed_head"]:
        return "incomplete", "completion lacks current gate and reviewer evidence"
    if (
        state["batches"] > state["budget"]["batches"]
        or state["active_minutes"] > state["budget"]["minutes"]
    ):
        return "replan", "completion exceeded the review budget"
    return "complete", "completion recorded with no unresolved findings"


def budget_decision(state: dict[str, Any]) -> tuple[str, str] | None:
    if state["active_minutes"] >= state["budget"]["minutes"]:
        return "replan", "active review-time budget is exhausted"
    if state["batches"] >= state["budget"]["batches"]:
        return "replan", "correction-batch budget is exhausted"
    return None


def family_decision(state: dict[str, Any]) -> tuple[str, str] | None:
    corrected, investigated, escaped, post_investigation = family_history(state)
    del corrected
    if post_investigation:
        return (
            "replan",
            f"finding family {sorted(post_investigation)[0]} escaped after investigation",
        )
    pending = escaped - investigated
    return (
        ("investigate", f"finding family {sorted(pending)[0]} escaped after correction")
        if pending
        else None
    )


def family_history(state: dict[str, Any]) -> tuple[set[str], set[str], set[str], set[str]]:
    investigated: set[str] = set()
    corrected: set[str] = set()
    families: dict[str, str] = {}
    escaped: set[str] = set()
    post_investigation: set[str] = set()
    for event in state["events"]:
        family = event.get("family", "")
        kind = event["kind"]
        if kind == "investigation":
            investigated.add(family)
        if kind == "disposition" and event["disposition"] == "fixed":
            corrected.add(families[event["finding_id"]])
        if kind != "finding":
            continue
        families[event["id"]] = family
        if family not in corrected:
            continue
        if family in investigated:
            post_investigation.add(family)
        escaped.add(family)
    return corrected, investigated, escaped, post_investigation


def unresolved_findings(state: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in state["findings"] if item.get("disposition") == "unresolved"]


def completion_evidence(state: dict[str, Any]) -> bool:
    required = {"gate", "reviewer"}
    latest = {
        item["evidence_type"]: item["result"]
        for item in current_evidence(state)
        if item.get("head") == state["reviewed_head"]
    }
    completed = {category for category, result in latest.items() if result == "pass"}
    return required <= completed


def current_evidence(state: dict[str, Any]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for event in state["events"]:
        if event["kind"] == "advance_head":
            evidence.clear()
        if event["kind"] == "evidence":
            evidence.append(event)
    return evidence


def packet(root: Path, change_id: str) -> dict[str, Any]:
    state = load(root, change_id)
    return {
        "change_id": change_id,
        "contract": state["contract"],
        "reviewed_head": state["reviewed_head"],
        "status": status(root, change_id),
        "unresolved_findings": unresolved_findings(state),
        "investigations": state["investigations"],
        "evidence": state["evidence"],
        "scope_decisions": state["scope_decisions"],
        "usage": state["usage"],
        "monitor": state["monitor"],
    }


def record_monitor_snapshot(
    root: Path, change_id: str, snapshot: dict[str, Any]
) -> dict[str, bool]:
    path = state_path(root, change_id)
    with state_lock(path):
        state = load(root, change_id)
        canonical = json.dumps(snapshot, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(canonical.encode()).hexdigest()
        if state["monitor"]["snapshot"] == digest:
            return {"changed": False}
        state["monitor"]["snapshot"] = digest
        state["monitor"]["data"] = snapshot
        contract = {**state["contract"], "head": state["reviewed_head"]}
        state["monitor"]["errors"] = monitor_errors(snapshot, contract)
        state["monitor"]["pending"] = monitor_pending(snapshot, contract)
        state["monitor"]["head"] = snapshot.get("head")
        state["revision"] += 1
        write_state(path, state)
        return {"changed": True}


def gh_snapshot(repository: str, pull_request: int) -> dict[str, Any]:
    endpoints = {
        "checks": f"repos/{repository}/commits/{{head}}/check-runs?per_page=100",
        "statuses": f"repos/{repository}/commits/{{head}}/status?per_page=100",
        "reviews": f"repos/{repository}/pulls/{pull_request}/reviews?per_page=100",
        "comments": f"repos/{repository}/issues/{pull_request}/comments?per_page=100",
    }
    pull = gh_json(f"repos/{repository}/pulls/{pull_request}")
    head = pull["head"]["sha"]
    result: dict[str, Any] = {"head": head, "requested_reviewers": pull["requested_reviewers"]}
    for name, endpoint in endpoints.items():
        result[name] = gh_json(endpoint.format(head=head), paginate=True)
    result["threads"] = gh_review_threads(repository, pull_request)
    if gh_json(f"repos/{repository}/pulls/{pull_request}")["head"]["sha"] != head:
        raise ValueError("PR head changed during collection")
    return result


def gh_review_threads(repository: str, pull_request: int) -> list[dict[str, Any]]:
    owner, name = repository.split("/", 1)
    query = """query($owner:String!,$name:String!,$number:Int!,$cursor:String) {
      repository(owner:$owner,name:$name) { pullRequest(number:$number) {
        reviewThreads(first:100,after:$cursor) { nodes { id isResolved isOutdated
          comments(first:100) { nodes { id body } pageInfo { hasNextPage endCursor } }
        } pageInfo { hasNextPage endCursor } }
      } } }"""
    cursor: str | None = None
    threads: list[dict[str, Any]] = []
    seen: set[str] = set()
    while True:
        result = gh_graphql(query, owner=owner, name=name, number=pull_request, cursor=cursor)
        page = result["data"]["repository"]["pullRequest"]["reviewThreads"]
        for thread in page["nodes"]:
            thread["comments"] = complete_thread_comments(thread)
            threads.append(thread)
        if not page["pageInfo"]["hasNextPage"]:
            return threads
        cursor = next_cursor(page["pageInfo"], seen)


def complete_thread_comments(thread: dict[str, Any]) -> list[dict[str, Any]]:
    comments = thread["comments"]
    nodes = comments["nodes"]
    page_info = comments["pageInfo"]
    seen: set[str] = set()
    query = """query($id:ID!,$cursor:String) {
      node(id:$id) { ... on PullRequestReviewThread {
        comments(first:100,after:$cursor) { nodes { id body } pageInfo { hasNextPage endCursor } }
      } }
    }"""
    while page_info["hasNextPage"]:
        result = gh_graphql(query, id=thread["id"], cursor=next_cursor(page_info, seen))
        comments = result["data"]["node"]["comments"]
        nodes.extend(comments["nodes"])
        page_info = comments["pageInfo"]
    return nodes


def next_cursor(page_info: dict[str, Any], seen: set[str]) -> str:
    cursor = page_info.get("endCursor")
    if not isinstance(cursor, str) or not cursor or cursor in seen:
        raise ValueError("incomplete pagination: missing or repeated cursor")
    seen.add(cursor)
    return cursor


def gh_graphql(query: str, **variables: Any) -> dict[str, Any]:
    command = ["gh", "api", "graphql", "-f", f"query={query}"]
    command.extend(
        value
        for key, value in variables.items()
        if value is not None
        for value in ("-F", f"{key}={value}")
    )
    result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=60)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "gh graphql failed")
    payload = json.loads(result.stdout)
    if payload.get("errors"):
        messages = (error.get("message", "GraphQL error") for error in payload["errors"])
        raise RuntimeError("; ".join(messages))
    return payload


def gh_json(endpoint: str, *, paginate: bool = False) -> Any:
    command = ["gh", "api", endpoint]
    if paginate:
        command.append("--paginate")
    result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=60)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "gh api failed")
    values = [json.loads(line) for line in result.stdout.splitlines() if line]
    return values if paginate else values[0]


def monitor_errors(snapshot: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    errors = list(snapshot.get("errors", []))
    if errors:
        return errors
    head = snapshot.get("head")
    if head != contract["head"]:
        return ["monitor evidence is for a different head"]
    try:
        validate_snapshot(snapshot)
    except ValueError as error:
        return [str(error)]
    return failed_external_checks(snapshot)


def validate_snapshot(snapshot: dict[str, Any]) -> None:
    missing = [
        key
        for key in ("checks", "statuses", "reviews", "threads", "comments")
        if not isinstance(snapshot.get(key), list)
    ]
    if missing:
        raise ValueError(f"monitor evidence is missing or malformed: {', '.join(missing)}")
    page_items(snapshot["checks"], "check_runs")
    page_items(snapshot["statuses"], "statuses")
    for key in ("reviews", "comments"):
        for page in snapshot[key]:
            validate_entries(page, ())
    validate_entries(snapshot["threads"], ("id",))
    for thread in snapshot["threads"]:
        if not isinstance(thread.get("isResolved"), bool):
            raise ValueError("malformed thread resolution")


def failed_external_checks(snapshot: dict[str, Any]) -> list[str]:
    failed_checks = [
        run.get("name", "unnamed check")
        for run in page_items(snapshot.get("checks", []), "check_runs")
        if run.get("status") == "completed" and run.get("conclusion") not in {"success", "neutral"}
    ]
    errors = [f"failed current-head check: {name}" for name in failed_checks]
    errors.extend(
        f"failed current-head status: {item.get('context', 'unnamed status')}"
        for item in page_items(snapshot["statuses"], "statuses")
        if item.get("state") not in {"success", "pending"}
    )
    return errors


def monitor_pending(snapshot: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    if monitor_errors(snapshot, contract):
        return []
    pending = reviewer_pending(snapshot, contract)
    pending.extend(missing_gates(snapshot, contract))
    pending.extend(
        f"current-head check is pending: {run.get('name', 'unnamed check')}"
        for run in page_items(snapshot["checks"], "check_runs")
        if run.get("status") != "completed"
    )
    pending.extend(
        f"current-head status is pending: {item.get('context', 'unnamed status')}"
        for item in page_items(snapshot["statuses"], "statuses")
        if item.get("state") == "pending"
    )
    pending.extend(
        "unresolved review thread" for thread in snapshot["threads"] if not thread.get("isResolved")
    )
    return pending


def missing_gates(snapshot: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    checks = {item.get("name") for item in page_items(snapshot["checks"], "check_runs")}
    statuses = {item.get("context") for item in page_items(snapshot["statuses"], "statuses")}
    pending = [
        f"required check is missing: {name}"
        for name in contract["required_checks"]
        if name not in checks
    ]
    pending.extend(
        f"required status is missing: {name}"
        for name in contract["required_statuses"]
        if name not in statuses
    )
    return pending


def reviewer_pending(snapshot: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    reviews = [review for page in snapshot.get("reviews", []) for review in page]
    current_logins = {
        str(review.get("user", {}).get("login", "")).removesuffix("[bot]")
        for review in reviews
        if review.get("commit_id") == snapshot["head"]
        and review.get("state") in {"APPROVED", "COMMENTED", "CHANGES_REQUESTED"}
    }
    return [
        f"required reviewer has no current-head result: {reviewer}"
        for reviewer in contract["required_reviewers"]
        if reviewer.removesuffix("[bot]") not in current_logins
    ]


def page_items(pages: list[Any], key: str) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for page in pages:
        if not isinstance(page, dict) or not isinstance(page.get(key), list):
            raise ValueError("malformed paginated API collection")
        validate_entries(page[key], ())
        result.extend(page[key])
    return result


def watch(
    root: Path, change_id: str, repository: str, pull_request: int, timeout_minutes: int
) -> int:
    if not 0 <= timeout_minutes <= WAIT_LIMIT_MINUTES:
        raise ValueError(f"watch timeout must be between 0 and {WAIT_LIMIT_MINUTES} minutes")
    deadline = time.monotonic() + timeout_minutes * 60
    intervals = (15, 30, 60)
    index = 0
    while True:
        try:
            snapshot = gh_snapshot(repository, pull_request)
            outcome = record_monitor_snapshot(root, change_id, snapshot)
        except (RuntimeError, KeyError, ValueError, subprocess.TimeoutExpired) as error:
            snapshot = {"errors": [str(error)]}
            outcome = record_monitor_snapshot(root, change_id, snapshot)
        current = status(root, change_id)
        if outcome["changed"]:
            deadline = time.monotonic() + timeout_minutes * 60
            print(json.dumps({"packet": packet(root, change_id), "snapshot": snapshot}, indent=2))
        if current["action"] == "incomplete":
            if not outcome["changed"]:
                print(json.dumps(current, indent=2))
            return 1
        if current["action"] in {"complete", "investigate", "replan"}:
            return 0
        if time.monotonic() >= deadline:
            print(json.dumps({"action": "wait", "reason": "watch timeout"}))
            return 0
        time.sleep(intervals[min(index, len(intervals) - 1)])
        index += 1


def argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("init", "record", "status", "packet", "watch"))
    parser.add_argument("change_id")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--json", dest="input_json", type=Path)
    parser.add_argument("--expected-revision", type=int)
    parser.add_argument("--repo")
    parser.add_argument("--pr", type=int)
    parser.add_argument("--timeout-minutes", type=int, default=WAIT_LIMIT_MINUTES)
    return parser


def dispatch(args: argparse.Namespace) -> Any:
    if args.operation in {"init", "record"}:
        if args.input_json is None:
            raise ValueError(f"{args.operation} requires --json file")
        payload = json.loads(args.input_json.read_text())
        if args.operation == "init":
            return initialize(args.root, args.change_id, payload)
        return record(args.root, args.change_id, payload, expected_revision=args.expected_revision)
    if args.operation == "status":
        return status(args.root, args.change_id)
    return packet(args.root, args.change_id)


def main() -> int:
    args = argument_parser().parse_args()
    try:
        if args.operation == "watch":
            if not args.repo or args.pr is None:
                raise ValueError("watch requires --repo and --pr")
            return watch(args.root, args.change_id, args.repo, args.pr, args.timeout_minutes)
        output = dispatch(args)
    except (ConflictError, OSError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"action": "incomplete", "reason": str(error)}))
        return 1
    print(json.dumps(output, indent=2, sort_keys=True))
    return 1 if output.get("action") == "incomplete" else 0


if __name__ == "__main__":
    raise SystemExit(main())
