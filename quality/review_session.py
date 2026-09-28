"""Persist bounded review decisions outside an agent's transient context."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import subprocess
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any

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
        "budget": {"batches": DEFAULT_BATCHES, "minutes": DEFAULT_MINUTES},
        "batches": 0,
        "active_minutes": 0,
        "events": [],
        "findings": [],
        "investigations": [],
        "scope_decisions": [],
        "evidence": [],
        "usage": {"cached_input": None, "uncached_input": None, "output": None, "cost": None},
        "monitor": {"snapshot": None, "errors": [], "pending": []},
        "phase": "active",
    }
    write_state(path, state)
    return state


def validate_contract(contract: dict[str, Any]) -> None:
    required = {
        "requirements",
        "acceptance_criteria",
        "non_goals",
        "trust_boundary",
        "intended_files",
        "base",
        "head",
        "required_reviewers",
    }
    missing = sorted(required - contract.keys())
    if missing:
        raise ValueError(f"contract missing: {', '.join(missing)}")
    if not isinstance(contract["required_reviewers"], list) or not all(
        isinstance(reviewer, str) and reviewer for reviewer in contract["required_reviewers"]
    ):
        raise ValueError("required_reviewers must be a list of non-empty GitHub logins")


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
    return value


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
        if expected_revision is not None and state["revision"] != expected_revision:
            raise ConflictError(f"expected revision {expected_revision}, found {state['revision']}")
        event_id = event.get("id")
        kind = event.get("kind")
        if not isinstance(event_id, str) or not event_id or not isinstance(kind, str):
            raise ValueError("event requires non-empty id and kind")
        if any(item["id"] == event_id for item in state["events"]):
            return state
        apply_event(state, event)
        state["events"].append(event)
        state["revision"] += 1
        write_state(path, state)
        return state


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
    state["findings"].append(
        {**event, "batch": state["batches"], "disposition": event.get("disposition", "unresolved")}
    )


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
    state["scope_decisions"].append(event)


def add_evidence(state: dict[str, Any], event: dict[str, Any]) -> None:
    require_field(event, "result", "evidence")
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


def require_field(event: dict[str, Any], field: str, name: str) -> None:
    if not event.get(field):
        raise ValueError(f"{name} requires {field}")


def number(event: dict[str, Any], key: str, default: int | float | None = None) -> float:
    value = event.get(key, default)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{key} must be numeric")
    return float(value)


def status(root: Path, change_id: str) -> dict[str, Any]:
    try:
        state = load(root, change_id)
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
    if terminal:
        return terminal
    budget = budget_decision(state)
    if budget:
        return budget
    family = family_decision(state)
    return family or ("continue", "within budget with no escalation trigger")


def terminal_decision(state: dict[str, Any]) -> tuple[str, str] | None:
    if state["monitor"]["errors"]:
        return "incomplete", "monitor evidence is incomplete"
    if any(item.get("decision") == "pending" for item in state["scope_decisions"]):
        return "incomplete", "scope decision is pending"
    if state["monitor"].get("head") and state["monitor"]["head"] != state["contract"]["head"]:
        return "incomplete", "monitor evidence is for a different head"
    if state["phase"] == "complete":
        if unresolved_findings(state):
            return "incomplete", "completed session has unresolved findings"
        if not completion_evidence(state):
            return "incomplete", "completion lacks current gate and reviewer evidence"
        return "complete", "completion recorded with no unresolved findings"
    if state["phase"] == "paused":
        return "wait", "session is paused"
    if state["monitor"].get("pending"):
        return "wait", "monitor is awaiting current-head reviewer results"
    return None


def budget_decision(state: dict[str, Any]) -> tuple[str, str] | None:
    if state["active_minutes"] >= state["budget"]["minutes"]:
        return "replan", "active review-time budget is exhausted"
    if state["batches"] >= state["budget"]["batches"] and unresolved_findings(state):
        return "replan", "correction-batch budget is exhausted"
    return None


def family_decision(state: dict[str, Any]) -> tuple[str, str] | None:
    investigated = {item["family"] for item in state["investigations"]}
    for family, count in escaped_family_counts(state).items():
        if count >= 2 and family in investigated:
            return "replan", f"finding family {family} escaped after investigation"
        if count >= 1 and family not in investigated:
            return "investigate", f"finding family {family} escaped after correction"
    return None


def escaped_family_counts(state: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    corrected: set[str] = set()
    for finding in state["findings"]:
        family = finding["family"]
        if finding.get("disposition") == "fixed":
            corrected.add(family)
        elif family in corrected:
            counts[family] = counts.get(family, 0) + 1
    return counts


def unresolved_findings(state: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in state["findings"] if item.get("disposition") == "unresolved"]


def completion_evidence(state: dict[str, Any]) -> bool:
    required = {"gate", "reviewer"}
    completed = {
        item.get("kind")
        for item in state["evidence"]
        if item.get("result") == "pass" and item.get("head") == state["contract"]["head"]
    }
    return required <= completed


def packet(root: Path, change_id: str) -> dict[str, Any]:
    state = load(root, change_id)
    return {
        "change_id": change_id,
        "contract": state["contract"],
        "status": status(root, change_id),
        "unresolved_findings": unresolved_findings(state),
        "investigations": state["investigations"],
        "evidence": state["evidence"],
        "scope_decisions": state["scope_decisions"],
        "usage": state["usage"],
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
        state["monitor"]["errors"] = monitor_errors(snapshot, state["contract"])
        state["monitor"]["pending"] = monitor_pending(snapshot, state["contract"])
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
    while True:
        result = gh_graphql(query, owner=owner, name=name, number=pull_request, cursor=cursor)
        page = result["data"]["repository"]["pullRequest"]["reviewThreads"]
        for thread in page["nodes"]:
            thread["comments"] = complete_thread_comments(thread)
            threads.append(thread)
        if not page["pageInfo"]["hasNextPage"]:
            return threads
        cursor = page["pageInfo"]["endCursor"]


def complete_thread_comments(thread: dict[str, Any]) -> list[dict[str, Any]]:
    comments = thread["comments"]
    nodes = comments["nodes"]
    page_info = comments["pageInfo"]
    query = """query($id:ID!,$cursor:String) {
      node(id:$id) { ... on PullRequestReviewThread {
        comments(first:100,after:$cursor) { nodes { id body } pageInfo { hasNextPage endCursor } }
      } }
    }"""
    while page_info["hasNextPage"]:
        result = gh_graphql(query, id=thread["id"], cursor=page_info["endCursor"])
        comments = result["data"]["node"]["comments"]
        nodes.extend(comments["nodes"])
        page_info = comments["pageInfo"]
    return nodes


def gh_graphql(query: str, **variables: Any) -> dict[str, Any]:
    command = ["gh", "api", "graphql", "-f", f"query={query}"]
    command.extend(
        value
        for key, value in variables.items()
        if value is not None
        for value in ("-F", f"{key}={value}")
    )
    result = subprocess.run(command, capture_output=True, text=True, check=False)
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
    result = subprocess.run(command, capture_output=True, text=True, check=False)
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
        return errors
    if contract["required_reviewers"] and "reviews" not in snapshot:
        return ["monitor evidence is missing reviews"]
    return errors


def monitor_pending(snapshot: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    if snapshot.get("errors") or snapshot.get("head") != contract["head"]:
        return []
    head = snapshot["head"]
    required_reviewers = contract["required_reviewers"]
    if required_reviewers and "reviews" not in snapshot:
        return []
    reviews = [review for page in snapshot.get("reviews", []) for review in page]
    current_logins = {
        review.get("user", {}).get("login")
        for review in reviews
        if review.get("commit_id") == head and review.get("state") != "PENDING"
    }
    return [
        f"required reviewer has no current-head result: {reviewer}"
        for reviewer in required_reviewers
        if reviewer not in current_logins
    ]


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
            outcome = record_monitor_snapshot(
                root, change_id, gh_snapshot(repository, pull_request)
            )
        except (RuntimeError, KeyError, json.JSONDecodeError) as error:
            outcome = record_monitor_snapshot(root, change_id, {"errors": [str(error)]})
        current = status(root, change_id)
        if outcome["changed"]:
            print(json.dumps(packet(root, change_id), indent=2))
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("init", "record", "status", "packet", "watch"))
    parser.add_argument("change_id")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--json", dest="input_json", type=Path)
    parser.add_argument("--expected-revision", type=int)
    parser.add_argument("--repo")
    parser.add_argument("--pr", type=int)
    parser.add_argument("--timeout-minutes", type=int, default=0)
    args = parser.parse_args()
    try:
        if args.operation == "init":
            if args.input_json is None:
                raise ValueError("init requires --json contract file")
            output: Any = initialize(
                args.root, args.change_id, json.loads(args.input_json.read_text())
            )
        elif args.operation == "record":
            if args.input_json is None:
                raise ValueError("record requires --json event file")
            output = record(
                args.root,
                args.change_id,
                json.loads(args.input_json.read_text()),
                expected_revision=args.expected_revision,
            )
        elif args.operation == "status":
            output = status(args.root, args.change_id)
        elif args.operation == "packet":
            output = packet(args.root, args.change_id)
        else:
            if not args.repo or args.pr is None:
                raise ValueError("watch requires --repo and --pr")
            return watch(args.root, args.change_id, args.repo, args.pr, args.timeout_minutes)
    except (ConflictError, OSError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"action": "incomplete", "reason": str(error)}))
        return 1
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
