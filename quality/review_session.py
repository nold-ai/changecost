"""Persist bounded review decisions outside an agent's transient context."""

from __future__ import annotations

import argparse
import copy
import fcntl
import hashlib
import json
import math
import os
import re
import subprocess
import tempfile
import time
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

from quality import repository

SCHEMA_VERSION = 5
DEFAULT_BATCHES = 3
DEFAULT_MINUTES = 90
WAIT_LIMIT_MINUTES = 30
REQUEST_DEADLINE: ContextVar[float | None] = ContextVar("request_deadline", default=None)


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
        marker = path.with_name("genesis.json")
        if marker.exists():
            raise ValueError("session state lost; recover preserved genesis and history")
        genesis = {
            "schema_version": SCHEMA_VERSION,
            "change_id": change_id,
            "contract": copy.deepcopy(contract),
            "inputs": capture_inputs(root, contract["head"]),
            "initial_scope": capture_initial_scope(root, contract),
            "created_at": datetime.now(UTC).isoformat(),
        }
        if genesis["inputs"] != capture_inputs(root, contract["head"]):
            raise ConflictError("inputs changed during initialization")
        state = replay(genesis, [], [], None, 0)
        write_state(marker, genesis)
        write_state(path, state)
        return state


def initial_state(genesis: dict[str, Any]) -> dict[str, Any]:
    contract = genesis["contract"]
    return {
        "schema_version": SCHEMA_VERSION,
        "genesis": copy.deepcopy(genesis),
        "change_id": genesis["change_id"],
        "contract": copy.deepcopy(contract),
        "reviewed_head": contract["head"],
        "comparison_base": contract["base"],
        "pr_base": copy.deepcopy(contract["pr_base"]),
        "context_since": None,
        "inputs": copy.deepcopy(genesis["inputs"]),
        "budget": {"batches": DEFAULT_BATCHES, "minutes": DEFAULT_MINUTES},
        "batches": 0,
        "active_minutes": 0,
        "timing_measurements": [],
        "events": [],
        "provenance": [],
        "findings": [],
        "investigations": [],
        "scope_decisions": [],
        "evidence": [],
        "phase": "active",
        "pull_request": None,
        "usage": {"cached_input": None, "uncached_input": None, "output": None, "cost": None},
        "monitor": empty_monitor(),
        "observation_revision": 0,
        "revision": 0,
    }


def empty_monitor() -> dict[str, Any]:
    return {"snapshot": None, "data": None, "errors": [], "pending": []}


def validate_timestamp(value: Any) -> None:
    if not isinstance(value, str) or datetime.fromisoformat(value).tzinfo is None:
        raise ValueError("timestamp requires an explicit timezone")


def validate_inputs(inputs: Any, head: str) -> None:
    validate_commit_id(head, "reviewed head")
    if not isinstance(inputs, dict) or inputs.get("head") != head:
        raise ValueError("captured inputs do not match reviewed head")
    if not isinstance(inputs.get("digest"), str) or len(inputs["digest"]) != 64:
        raise ValueError("malformed captured input digest")
    if not isinstance(inputs.get("clean"), bool):
        raise ValueError("captured inputs require clean publication status")


def replay(
    genesis: dict[str, Any],
    events: list[Any],
    facts: list[Any],
    observation: Any,
    observation_revision: int,
) -> dict[str, Any]:
    validate_entries(events, ("id", "kind"))
    validate_entries(facts, ("event_id", "recorded_at"))
    validate_contract(genesis["contract"])
    validate_initial_scope(genesis["contract"], genesis["initial_scope"])
    validate_timestamp(genesis["created_at"])
    validate_inputs(genesis["inputs"], genesis["contract"]["head"])
    if integer(genesis.get("schema_version"), "schema version") != SCHEMA_VERSION or len(
        events
    ) != len(facts):
        raise ValueError("malformed genesis or event provenance cardinality")
    integer(observation_revision, "observation revision")
    state = initial_state(genesis)
    for event, provenance in zip(events, facts, strict=True):
        validate_event(event)
        if duplicate_event(state["events"], event):
            raise ValueError("duplicate persisted event identity")
        validate_provenance(event, provenance)
        apply_event(state, event, provenance)
        state["events"].append(copy.deepcopy(event))
        state["provenance"].append(copy.deepcopy(provenance))
    state["observation_revision"] = observation_revision
    state["revision"] = len(events) + observation_revision
    state["monitor"] = classify_observation(observation, state)
    return state


def validate_provenance(event: dict[str, Any], provenance: Any) -> None:
    if not isinstance(provenance, dict) or provenance.get("event_id") != event["id"]:
        raise ValueError("event provenance identity mismatch")
    validate_timestamp(provenance.get("recorded_at"))
    expected = {"event_id", "recorded_at"}
    if event["kind"] == "advance_head":
        expected.add("inputs")
        validate_inputs(provenance.get("inputs"), event["head"])
        if validate_adoption(event):
            expected.add("adoption")
            if provenance.get("adoption") != adoption_binding(event):
                raise ValueError("base adoption provenance mismatch")
    if provenance.keys() != expected:
        raise ValueError("unexpected event provenance fields")


def integer(value: Any, label: str) -> int:
    validate_nonnegative(value, label)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{label} must be an integer")
    return value


def validate_contract(contract: dict[str, Any]) -> None:
    if not isinstance(contract, dict):
        raise ValueError("contract must be an object")
    required = {
        "requirements",
        "repository",
        "acceptance_criteria",
        "non_goals",
        "trust_boundary",
        "intended_files",
        "base",
        "pr_base",
        "head",
        "required_reviewers",
        "required_checks",
        "required_statuses",
    }
    missing = sorted(required - contract.keys())
    if missing:
        raise ValueError(f"contract missing: {', '.join(missing)}")
    validate_scope_contract(contract)
    validate_pr_base(contract["pr_base"])
    validate_gate_contract(contract)
    if not isinstance(contract["repository"], str) or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*", contract["repository"]
    ):
        raise ValueError("repository requires owner/name")


def nonblank(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value.strip())
        and value == value.strip()
        and not any(ord(char) < 32 or ord(char) == 127 for char in value)
    )


def string_list(value: Any, label: str, *, allow_empty: bool = False) -> None:
    if not isinstance(value, list) or not all(nonblank(item) for item in value):
        raise ValueError(f"{label} requires nonblank strings")
    if not allow_empty and not value:
        raise ValueError(f"{label} must not be empty")


def validate_scope_contract(contract: dict[str, Any]) -> None:
    for key in ("requirements", "acceptance_criteria", "required_reviewers", "non_goals"):
        string_list(contract[key], key, allow_empty=key == "non_goals")
    if not all(
        re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*(?:\[bot\])?", login)
        for login in contract["required_reviewers"]
    ):
        raise ValueError("required_reviewers requires exact GitHub logins")
    if not nonblank(contract["trust_boundary"]):
        raise ValueError("trust_boundary requires nonblank text")
    for key in ("base", "head"):
        validate_commit_id(contract[key], key)
    validate_manifest(contract["intended_files"])


def validate_commit_id(value: Any, label: str) -> None:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value):
        raise ValueError(f"{label} requires a full hexadecimal commit ID")


def validate_pr_base(value: Any) -> None:
    if not isinstance(value, dict) or value.keys() != {"ref", "sha"}:
        raise ValueError("pr_base requires ref and sha")
    ref = value["ref"]
    if not nonblank(ref) or re.search(r"[~^:?*\[\]\\\x00-\x20\x7f]", ref):
        raise ValueError("pr_base requires a valid branch ref")
    if any(part in ref for part in ("..", "@{", "//", "/.", ".lock/")):
        raise ValueError("pr_base requires a valid branch ref")
    if ref.startswith(("/", ".", "-")) or ref.endswith(("/", ".", ".lock")):
        raise ValueError("pr_base requires a valid branch ref")
    validate_commit_id(value["sha"], "pr_base sha")


def verified_commit(root: Path, commit: str) -> str:
    validate_commit_id(commit, "base")
    resolved = (
        repository.git(root, "rev-parse", "--verify", f"{commit}^{{commit}}").decode().strip()
    )
    if resolved != commit:
        raise ValueError("base identity must name a commit object, not a peeled tag")
    return resolved


def adoption_binding(event: dict[str, Any]) -> dict[str, Any]:
    return {"comparison_base": event["comparison_base"], "pr_base": event["pr_base"]}


def validate_adoption(event: dict[str, Any]) -> bool:
    if not {"comparison_base", "pr_base"} & event.keys():
        return False
    validate_commit_id(event.get("comparison_base"), "comparison_base")
    validate_pr_base(event.get("pr_base"))
    return True


def validate_manifest(manifest: Any) -> None:
    if not isinstance(manifest, dict) or not manifest:
        raise ValueError("intended_files requires a nonempty path fingerprint mapping")
    for name, fingerprint in manifest.items():
        validate_manifest_path(name)
        if fingerprint != "<absent>" and (
            not isinstance(fingerprint, str) or not re.fullmatch(r"[0-9a-f]{64}", fingerprint)
        ):
            raise ValueError("manifest fingerprint requires SHA256 or <absent>")


def validate_manifest_path(name: Any) -> None:
    if not nonblank(name) or "\\" in name:
        raise ValueError("manifest path requires a safe relative path")
    path = PurePosixPath(name)
    if (
        path.is_absolute()
        or ".." in path.parts
        or not path.parts
        or str(path) != name
        or path.parts[0] == ".git"
    ):
        raise ValueError("manifest path requires a normalized repository path")


def capture_initial_scope(root: Path, contract: dict[str, Any]) -> dict[str, Any]:
    base = verified_commit(root, contract["base"])
    changed = repository.git(root, "diff", "--name-only", "--no-renames", "-z", base)
    staged = repository.git(root, "diff", "--cached", "--name-only", "--no-renames", "-z", base)
    untracked = repository.git(root, "ls-files", "--others", "--exclude-standard", "-z")
    names = set((changed + staged + untracked).decode().split("\0")) - {""}
    actual = {name: file_fingerprint(root, name) for name in contract["intended_files"]}
    facts = {
        "base": base,
        "pr_base_sha": verified_commit(root, contract["pr_base"]["sha"]),
        "files": actual,
        "changed_paths": sorted(names),
    }
    validate_initial_scope(contract, facts)
    return facts


def file_fingerprint(root: Path, name: str) -> str:
    path = repository.safe_path(root, name)
    if not path.exists():
        return "<absent>"
    if not path.is_file():
        raise ValueError("intended path is not a regular file")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_initial_scope(contract: dict[str, Any], facts: Any) -> None:
    if not isinstance(facts, dict) or facts.keys() != {
        "base",
        "pr_base_sha",
        "files",
        "changed_paths",
    }:
        raise ValueError("missing or malformed initial scope facts; recovery required")
    string_list(facts["changed_paths"], "initial changed paths", allow_empty=True)
    if facts["changed_paths"] != sorted(set(facts["changed_paths"])):
        raise ValueError("initial changed paths must be unique and sorted")
    for name in facts["changed_paths"]:
        validate_manifest_path(name)
    if facts["base"] != contract["base"] or facts["files"] != contract["intended_files"]:
        raise ValueError("initial manifest does not match captured inputs/base")
    if facts["pr_base_sha"] != contract["pr_base"]["sha"]:
        raise ValueError("initial PR base facts mismatch")
    if not set(facts["changed_paths"]) <= contract["intended_files"].keys():
        raise ValueError("initial manifest omits changed inputs")


def validate_gate_contract(contract: dict[str, Any]) -> None:
    for key in ("required_checks", "required_statuses"):
        value = contract[key]
        string_list(value, key, allow_empty=key == "required_statuses")
    if not contract["required_checks"]:
        raise ValueError("required_checks must name at least one expected CI check")


def capture_inputs(root: Path, expected_head: str) -> dict[str, Any]:
    validate_index_flags(root)
    head = repository.git(root, "rev-parse", "HEAD").decode().strip()
    if head != expected_head:
        raise ValueError("reviewed head differs from local HEAD")
    names = repository.git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
    files = set(names.decode().split("\0")) - {""}
    index = repository.git(root, "ls-files", "--stage", "-z")
    fingerprint = repository.digest(root, files).encode() + b"\0" + index
    clean = not repository.git(root, "status", "--porcelain", "--untracked-files=all")
    return {"head": head, "digest": hashlib.sha256(fingerprint).hexdigest(), "clean": clean}


def validate_index_flags(root: Path) -> None:
    records = repository.git(root, "ls-files", "-v", "-z").split(b"\0")
    if any(record[:1].islower() or record[:1] == b"S" for record in records if record):
        raise ValueError(
            "unsupported index flags: clear assume-unchanged/skip-worktree explicitly before review"
        )


def load(root: Path, change_id: str) -> dict[str, Any]:
    path = state_path(root, change_id)
    try:
        value = json.loads(path.read_text())
        marker = json.loads(path.with_name("genesis.json").read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"unreadable session state: {error}") from error
    if not isinstance(value, dict) or value.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported or malformed session state")
    try:
        validate_canonical_state(value, marker, change_id)
    except (KeyError, TypeError) as error:
        raise ValueError("malformed session history; recovery required") from error
    return value


def validate_canonical_state(state: dict[str, Any], marker: Any, change_id: str) -> None:
    if state.get("genesis") != marker or marker["change_id"] != change_id:
        raise ValueError("session genesis mismatch; recovery required")
    expected = replay(
        marker,
        state["events"],
        state["provenance"],
        state["monitor"]["data"],
        state["observation_revision"],
    )
    if json.dumps(state, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError("persisted state contradicts canonical history; recovery required")


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
        "bind_pr": ("repository",),
    }
    validate_entries([event], ("id", "kind"))
    if event["kind"] not in fields:
        raise ValueError("unknown persisted event kind")
    validate_entries([event], fields[event["kind"]])
    required_text = ("id", "kind", *fields[event["kind"]])
    for key in required_text:
        validate_event_text(event[key], key)
    if "supersedes" in event:
        validate_event_text(event["supersedes"], "supersedes")
    numeric_fields = {
        "active_minutes": ("minutes",),
        "extension": ("batches", "minutes"),
        "usage": ("cached_input", "uncached_input", "output", "cost"),
    }
    for key in numeric_fields.get(event["kind"], ()):
        default = None if event["kind"] == "active_minutes" else 0
        validate_nonnegative(event.get(key, default), key)


def validate_event_text(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} requires non-whitespace text")


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
        if expected_revision is not None:
            integer(expected_revision, "expected revision")
        if duplicate_event(state["events"], event):
            return state
        if expected_revision is not None and state["revision"] != expected_revision:
            raise ConflictError(f"expected revision {expected_revision}, found {state['revision']}")
        return persist_event(root, change_id, state, event)


def persist_event(
    root: Path, change_id: str, state: dict[str, Any], event: dict[str, Any]
) -> dict[str, Any]:
    """Persist a validated event while the caller holds the session lock."""
    provenance: dict[str, Any] = {
        "event_id": event["id"],
        "recorded_at": datetime.now(UTC).isoformat(),
    }
    capture_event_facts(root, event, provenance)
    observation = None if event["kind"] in {"advance_head", "bind_pr"} else state["monitor"]["data"]
    updated = replay(
        state["genesis"],
        [*state["events"], event],
        [*state["provenance"], provenance],
        observation,
        state["observation_revision"],
    )
    write_state(state_path(root, change_id), updated)
    return updated


def capture_event_facts(root: Path, event: dict[str, Any], provenance: dict[str, Any]) -> None:
    if event["kind"] != "advance_head":
        return
    provenance["inputs"] = capture_inputs(root, event["head"])
    if validate_adoption(event):
        verified_commit(root, event["comparison_base"])
        verified_commit(root, event["pr_base"]["sha"])
        provenance["adoption"] = copy.deepcopy(adoption_binding(event))


def duplicate_event(events: list[dict[str, Any]], event: dict[str, Any]) -> bool:
    existing = next((item for item in events if item["id"] == event["id"]), None)
    if existing is not None and json.dumps(existing, sort_keys=True) != json.dumps(
        event, sort_keys=True
    ):
        raise ConflictError("event identity already has a different payload")
    return existing is not None


def apply_event(state: dict[str, Any], event: dict[str, Any], provenance: dict[str, Any]) -> None:
    if event["kind"] == "active_minutes":
        add_active_minutes(state, event, provenance)
        return
    if event["kind"] == "advance_head":
        advance_head(state, event)
        state["inputs"] = copy.deepcopy(provenance["inputs"])
        if "adoption" in provenance:
            state.update(copy.deepcopy(provenance["adoption"]))
            state["context_since"] = provenance["recorded_at"]
        return
    handlers = {
        "batch": add_batch,
        "extension": add_extension,
        "finding": add_finding,
        "disposition": add_disposition,
        "investigation": add_investigation,
        "scope_decision": add_scope_decision,
        "evidence": add_evidence,
        "usage": add_usage,
        "phase": set_phase,
        "bind_pr": bind_pr,
    }
    try:
        handlers[event["kind"]](state, event)
    except KeyError as error:
        raise ValueError(f"unknown event kind: {event['kind']}") from error


def add_batch(state: dict[str, Any], event: dict[str, Any]) -> None:
    del event
    state["batches"] += 1


def add_active_minutes(
    state: dict[str, Any], event: dict[str, Any], provenance: dict[str, Any]
) -> None:
    minutes = number(event, "minutes")
    if minutes < 0:
        raise ValueError("active minutes cannot be negative")
    state["timing_measurements"].append(
        {"event_id": event["id"], "minutes": minutes, "recorded_at": provenance["recorded_at"]}
    )
    state["active_minutes"] = math.fsum(item["minutes"] for item in state["timing_measurements"])


def add_extension(state: dict[str, Any], event: dict[str, Any]) -> None:
    if not event.get("approved_by"):
        raise ValueError("budget extension requires approved_by")
    state["budget"]["batches"] += integer(event.get("batches", 0), "extension batches")
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
    if event["decision"] not in {"pending", "approved", "rejected", "deferred"}:
        raise ValueError("unknown scope decision")
    supersedes = event.get("supersedes")
    if "supersedes" in event and (not isinstance(supersedes, str) or not supersedes):
        raise ValueError("scope supersedes must be a nonempty event identity")
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
    if event["result"] not in {"pass", "fail", "incomplete"}:
        raise ValueError("unknown evidence result")
    if event.get("binding") != evidence_binding(state) or event["head"] != state["reviewed_head"]:
        raise ValueError("evidence binding is missing or stale")
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
    validate_commit_id(head, "advance_head")
    state["reviewed_head"] = head
    state["phase"] = "active"
    state["monitor"] = {"snapshot": None, "data": None, "errors": [], "pending": []}


def bind_pr(state: dict[str, Any], event: dict[str, Any]) -> None:
    number = integer(event.get("pull_request"), "pull request")
    if number == 0 or event.get("repository") != state["contract"]["repository"]:
        raise ValueError("selected pull-request source mismatches contract")
    if state["pull_request"] is not None and state["pull_request"] != number:
        raise ValueError("pull request already bound; cannot switch source")
    state["pull_request"] = number


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
    except ValueError as error:
        return {"action": "incomplete", "reason": str(error)}
    return status_from_state(root, state)


def status_from_state(root: Path, state: dict[str, Any]) -> dict[str, Any]:
    try:
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
    if not state["inputs"]["clean"]:
        return "incomplete", "published completion requires clean committed inputs"
    if unresolved_findings(state):
        return "incomplete", "completed session has unresolved findings"
    if not completion_evidence(state) or state["monitor"].get("head") != state["reviewed_head"]:
        return "incomplete", "completion lacks current gate and reviewer evidence"
    if not any(event["kind"] == "active_minutes" for event in current_binding_events(state)):
        return "incomplete", "completion lacks explicit current-input elapsed-time measurement"
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
    genuine = genuine_finding_ids(state)
    for event in state["events"]:
        family = event.get("family", "")
        kind = event["kind"]
        if kind == "investigation" and family in escaped:
            investigated.add(family)
        if genuine_correction(event, genuine):
            corrected.add(families[event["finding_id"]])
        if kind != "finding" or event["id"] not in genuine:
            continue
        families[event["id"]] = family
        if family not in corrected:
            continue
        if family in investigated:
            post_investigation.add(family)
        escaped.add(family)
    return corrected, investigated, escaped, post_investigation


def genuine_correction(event: dict[str, Any], genuine: set[str]) -> bool:
    return (
        event["kind"] == "disposition"
        and event["disposition"] == "fixed"
        and event["finding_id"] in genuine
    )


def genuine_finding_ids(state: dict[str, Any]) -> set[str]:
    return {item["id"] for item in state["findings"] if item["disposition"] != "non_finding"}


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
    return [event for event in current_binding_events(state) if event["kind"] == "evidence"]


def current_binding_events(state: dict[str, Any]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for event in state["events"]:
        if event["kind"] == "advance_head":
            events.clear()
        events.append(event)
    return events


def packet(root: Path, change_id: str) -> dict[str, Any]:
    state = load(root, change_id)
    return {
        "change_id": change_id,
        "contract": state["contract"],
        "reviewed_head": state["reviewed_head"],
        "binding": evidence_binding(state),
        "status": status_from_state(root, state),
        "unresolved_findings": unresolved_findings(state),
        "investigations": state["investigations"],
        "evidence": state["evidence"],
        "scope_decisions": state["scope_decisions"],
        "usage": state["usage"],
        "timing_measurements": state["timing_measurements"],
        "pull_request": state["pull_request"],
        "monitor": state["monitor"],
    }


def binding_epoch(state: dict[str, Any]) -> str:
    generation = sum(item["kind"] == "advance_head" for item in state["events"])
    return f"input-generation:{generation}"


def evidence_binding(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "head": state["reviewed_head"],
        "input_digest": state["inputs"]["digest"],
        "epoch": binding_epoch(state),
        "comparison_base": state["comparison_base"],
        "pr_base": copy.deepcopy(state["pr_base"]),
    }


def select_target(root: Path, change_id: str, repository_name: str, pull_request: int) -> None:
    with state_lock(state_path(root, change_id)):
        state = load(root, change_id)
        bind_target_locked(root, change_id, state, repository_name, pull_request)


def bind_target_locked(
    root: Path, change_id: str, state: dict[str, Any], repository_name: str, pull_request: int
) -> None:
    if repository_name != state["contract"]["repository"]:
        raise ValueError("selected repository differs from session contract")
    if state["pull_request"] is not None:
        if state["pull_request"] != pull_request:
            raise ValueError("selected pull request differs from bound target")
        return
    persist_event(
        root,
        change_id,
        state,
        {
            "id": unused_bind_identity(state),
            "kind": "bind_pr",
            "repository": repository_name,
            "pull_request": pull_request,
        },
    )


def unused_bind_identity(state: dict[str, Any]) -> str:
    occupied = {event["id"] for event in state["events"]}
    candidate = "bind-pr"
    suffix = 0
    while candidate in occupied:
        suffix += 1
        candidate = f"bind-pr:{suffix}"
    return candidate


def record_monitor_snapshot(
    root: Path, change_id: str, snapshot: dict[str, Any]
) -> dict[str, bool]:
    state = load(root, change_id)
    if (
        state["pull_request"] is None
        and snapshot.get("repository") == state["contract"]["repository"]
        and type(snapshot.get("pull_request")) is int
        and snapshot["pull_request"] > 0
    ):
        select_target(root, change_id, snapshot["repository"], snapshot["pull_request"])
    path = state_path(root, change_id)
    with state_lock(path):
        state = load(root, change_id)
        observation = {
            **snapshot,
            "_input_epoch": snapshot.get("_input_epoch", binding_epoch(state)),
        }
        monitor = classify_observation(observation, state)
        if state["monitor"]["snapshot"] == monitor["snapshot"]:
            return {"changed": False}
        updated = replay(
            state["genesis"],
            state["events"],
            state["provenance"],
            observation,
            state["observation_revision"] + 1,
        )
        write_state(path, updated)
        return {"changed": True}


def classify_observation(observation: Any, state: dict[str, Any]) -> dict[str, Any]:
    if observation is None:
        return empty_monitor()
    if not isinstance(observation, dict):
        raise ValueError("malformed observation receipt")
    contract = {
        **state["contract"],
        "head": state["reviewed_head"],
        "pull_request": state["pull_request"],
        "pr_base": state["pr_base"],
        "context_since": state["context_since"],
    }
    errors = monitor_errors(observation, contract)
    if observation.get("_input_epoch") != binding_epoch(state):
        errors.append("monitor evidence is for another input binding")
    pending = [] if errors else monitor_pending(observation, contract)
    meaningful = observation if errors else semantic_snapshot(observation)
    digest = hashlib.sha256(json.dumps(meaningful, sort_keys=True).encode()).hexdigest()
    return {
        "snapshot": digest,
        "data": copy.deepcopy(observation),
        "errors": errors,
        "pending": pending,
        "head": observation.get("head"),
    }


def selected_fields(value: dict[str, Any], names: tuple[str, ...]) -> dict[str, Any]:
    return {key: value[key] for key in names if key in value}


def semantic_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    result = selected_fields(
        snapshot, ("repository", "pull_request", "head", "pr_base", "_input_epoch")
    )
    result["requested_reviewers"] = requested_user_names(snapshot)
    result["checks"] = [
        selected_fields(
            item, ("id", "name", "head_sha", "status", "conclusion", "started_at", "completed_at")
        )
        for item in page_items(snapshot["checks"], "check_runs")
    ]
    result["statuses"] = [
        selected_fields(item, ("id", "context", "state", "description", "created_at", "updated_at"))
        for item in page_items(snapshot["statuses"], "statuses")
    ]
    result["reviews"] = [semantic_review(item) for page in snapshot["reviews"] for item in page]
    result["comments"] = [semantic_comment(item) for page in snapshot["comments"] for item in page]
    result["threads"] = [semantic_thread(item) for item in snapshot["threads"]]
    return result


def semantic_review(item: dict[str, Any]) -> dict[str, Any]:
    return {
        **selected_fields(item, ("id", "commit_id", "state", "body", "submitted_at")),
        "login": item["user"]["login"],
    }


def semantic_comment(item: dict[str, Any]) -> dict[str, Any]:
    return selected_fields(item, ("id", "body", "created_at", "updated_at", "path", "line"))


def semantic_thread(item: dict[str, Any]) -> dict[str, Any]:
    return {
        **selected_fields(item, ("id", "isResolved", "isOutdated", "path", "line")),
        "comments": [semantic_comment(comment) for comment in item.get("comments", [])],
    }


def gh_snapshot(repository: str, pull_request: int) -> dict[str, Any]:
    endpoints = {
        "checks": f"repos/{repository}/commits/{{head}}/check-runs?per_page=100",
        "statuses": f"repos/{repository}/commits/{{head}}/status?per_page=100",
        "reviews": f"repos/{repository}/pulls/{pull_request}/reviews?per_page=100",
        "comments": f"repos/{repository}/issues/{pull_request}/comments?per_page=100",
    }
    pull = gh_json(f"repos/{repository}/pulls/{pull_request}")
    requested = requested_user_names(pull)
    head = pull["head"]["sha"]
    result: dict[str, Any] = {
        "repository": repository,
        "pull_request": pull_request,
        "head": head,
        "pr_base": pull_base(pull),
        "requested_reviewers": pull["requested_reviewers"],
    }
    for name, endpoint in endpoints.items():
        result[name] = gh_json(endpoint.format(head=head), paginate=True)
    result["threads"] = gh_review_threads(repository, pull_request)
    final = gh_json(f"repos/{repository}/pulls/{pull_request}")
    if final["head"]["sha"] != head or pull_base(final) != result["pr_base"]:
        raise ValueError("PR head or base changed during collection")
    if requested != requested_user_names(final):
        raise ValueError("PR requested reviewers changed during collection")
    return result


def pull_base(pull: dict[str, Any]) -> dict[str, str]:
    value = {"ref": pull["base"]["ref"], "sha": pull["base"]["sha"]}
    validate_pr_base(value)
    return value


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
        validate_connection(page)
        for thread in page["nodes"]:
            thread["comments"] = complete_thread_comments(thread)
            threads.append(thread)
        if not page["pageInfo"]["hasNextPage"]:
            return threads
        cursor = next_cursor(page["pageInfo"], seen)


def complete_thread_comments(thread: dict[str, Any]) -> list[dict[str, Any]]:
    comments = thread["comments"]
    validate_connection(comments)
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
        validate_connection(comments)
        nodes.extend(comments["nodes"])
        page_info = comments["pageInfo"]
    return nodes


def validate_connection(connection: Any) -> None:
    if not isinstance(connection, dict):
        raise ValueError("missing GraphQL connection")
    validate_entries(connection.get("nodes"), ())
    info = connection.get("pageInfo")
    if not isinstance(info, dict) or not isinstance(info.get("hasNextPage"), bool):
        raise ValueError("malformed GraphQL pagination")


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
    result = subprocess.run(
        command, capture_output=True, text=True, check=False, timeout=request_timeout()
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "gh graphql failed")
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict):
        raise ValueError("malformed GraphQL response")
    if payload.get("errors"):
        validate_entries(payload["errors"], ("message",))
        messages = (error["message"] for error in payload["errors"])
        raise RuntimeError("; ".join(messages))
    return payload


def gh_json(endpoint: str, *, paginate: bool = False) -> Any:
    command = ["gh", "api", endpoint]
    if paginate:
        command.extend(("--paginate", "--slurp"))
    result = subprocess.run(
        command, capture_output=True, text=True, check=False, timeout=request_timeout()
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "gh api failed")
    value = json.loads(result.stdout)
    if paginate and not isinstance(value, list):
        raise ValueError("paginated API response must be a slurped page array")
    return value


def request_timeout() -> float:
    deadline = REQUEST_DEADLINE.get()
    remaining = 60.0 if deadline is None else deadline - time.monotonic()
    if remaining <= 0:
        raise ValueError("watch collection deadline exhausted")
    return min(60.0, remaining)


def monitor_errors(snapshot: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    try:
        errors = snapshot.get("errors", [])
        if not isinstance(errors, list) or not all(isinstance(item, str) for item in errors):
            raise ValueError("malformed monitor errors")
        if errors:
            return list(errors)
        validate_snapshot_source(snapshot, contract)
        validate_snapshot(snapshot)
        return failed_external_checks(snapshot) + rejected_reviews(snapshot)
    except (ValueError, KeyError, TypeError) as error:
        return [str(error)]


def validate_snapshot_source(snapshot: dict[str, Any], contract: dict[str, Any]) -> None:
    integer(snapshot.get("pull_request"), "snapshot pull request")
    validate_pr_base(snapshot.get("pr_base"))
    for key in ("repository", "pull_request", "head", "pr_base"):
        if snapshot.get(key) != contract.get(key):
            raise ValueError(f"monitor evidence is for a different {key}")
    if not contract.get("pull_request"):
        raise ValueError("monitor source has no bound pull request")


def validate_snapshot(snapshot: dict[str, Any]) -> None:
    requested_user_names(snapshot)
    missing = [
        key
        for key in ("checks", "statuses", "reviews", "threads", "comments")
        if not isinstance(snapshot.get(key), list)
    ]
    if missing:
        raise ValueError(f"monitor evidence is missing or malformed: {', '.join(missing)}")
    validate_check_results(snapshot)
    for key in ("reviews", "comments"):
        for page in snapshot[key]:
            validate_entries(page, ())
    for review in [item for page in snapshot["reviews"] for item in page]:
        validate_review(review)
    for page in snapshot["comments"]:
        validate_comments(page, graphql=False)
    validate_entries(snapshot["threads"], ("id",))
    validate_threads(snapshot["threads"])


def validate_threads(threads: list[dict[str, Any]]) -> None:
    for thread in threads:
        if not isinstance(thread.get("isResolved"), bool) or not isinstance(
            thread.get("isOutdated"), bool
        ):
            raise ValueError("malformed thread resolution")
        validate_comments(thread.get("comments"), graphql=True)


def validate_comments(comments: Any, *, graphql: bool) -> None:
    validate_entries(comments, ())
    for comment in comments:
        identity = comment.get("id")
        valid_identity = (
            isinstance(identity, str) and bool(identity)
            if graphql
            else type(identity) is int and identity > 0
        )
        if not valid_identity or not isinstance(comment.get("body"), str):
            raise ValueError("comment requires a typed identity and body")


def validate_check_results(snapshot: dict[str, Any]) -> None:
    checks = page_items(snapshot["checks"], "check_runs")
    statuses = page_items(snapshot["statuses"], "statuses")
    validate_entries(checks, ("name", "status"))
    validate_entries(statuses, ("context", "state"))
    for check in checks:
        if check.get("head_sha", snapshot["head"]) != snapshot["head"]:
            raise ValueError("check result is for another head")
        if check.get("conclusion") is not None and not isinstance(check["conclusion"], str):
            raise ValueError("malformed check conclusion")


def validate_review(review: dict[str, Any]) -> None:
    validate_entries([review], ("commit_id", "state"))
    if review["state"] not in {
        "APPROVED",
        "CHANGES_REQUESTED",
        "COMMENTED",
        "DISMISSED",
        "PENDING",
    }:
        raise ValueError("unknown GitHub review state")
    if not isinstance(review.get("user"), dict):
        raise ValueError("review requires an exact author identity")
    validate_entries([review["user"]], ("login",))


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
    pending.extend(freshness_pending(snapshot, contract))
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


def timestamp_after(value: Any, since: str) -> bool:
    try:
        validate_timestamp(value)
        return datetime.fromisoformat(value) >= datetime.fromisoformat(since)
    except (ValueError, TypeError):
        return False


def freshness_pending(snapshot: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    since = contract.get("context_since")
    if since is None:
        return []
    groups = (
        (page_items(snapshot["checks"], "check_runs"), "name", "started_at", "required_checks"),
        (
            page_items(snapshot["statuses"], "statuses"),
            "context",
            "created_at",
            "required_statuses",
        ),
    )
    pending = []
    for items, identity, timestamp, required in groups:
        fresh = {item[identity] for item in items if timestamp_after(item.get(timestamp), since)}
        pending.extend(
            f"fresh evidence required after base adoption: {name}"
            for name in contract[required]
            if name not in fresh
        )
    fresh_reviewers = fresh_reviewer_names(snapshot, since)
    pending.extend(
        f"fresh reviewer evidence required after base adoption: {name}"
        for name in contract["required_reviewers"]
        if name not in fresh_reviewers
    )
    return pending


def fresh_reviewer_names(snapshot: dict[str, Any], since: str) -> set[str]:
    return {
        item["user"]["login"]
        for page in snapshot["reviews"]
        for item in page
        if item["commit_id"] == snapshot["head"]
        and item["state"] in {"APPROVED", "COMMENTED"}
        and timestamp_after(item.get("submitted_at"), since)
    }


def reviewer_pending(snapshot: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    latest = latest_review_states(snapshot)
    requested = requested_user_names(snapshot)
    return [
        f"required reviewer has no current-head result: {reviewer}"
        for reviewer in contract["required_reviewers"]
        if reviewer in requested or latest.get(reviewer) not in {"APPROVED", "COMMENTED"}
    ]


def requested_user_names(snapshot: dict[str, Any]) -> list[str]:
    users = snapshot.get("requested_reviewers")
    if not isinstance(users, list):
        raise ValueError("requested_reviewers requires an array")
    validate_entries(users, ("login",))
    names = []
    for user in users:
        login = user["login"]
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*(?:\[bot\])?", login):
            raise ValueError("requested reviewer requires an exact GitHub login")
        names.append(login)
    return sorted(set(names))


def latest_review_states(snapshot: dict[str, Any]) -> dict[str, str]:
    latest: dict[str, str] = {}
    reviews = [review for page in snapshot["reviews"] for review in page]
    for review in reviews:
        if review.get("commit_id") == snapshot["head"]:
            login = review["user"]["login"]
            state = review["state"]
            if latest.get(login) == "CHANGES_REQUESTED" and state != "APPROVED":
                continue
            latest[login] = state
    return latest


def rejected_reviews(snapshot: dict[str, Any]) -> list[str]:
    return [
        f"current-head reviewer requested changes: {login}"
        for login, state in latest_review_states(snapshot).items()
        if state == "CHANGES_REQUESTED"
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
        if index and time.monotonic() >= deadline:
            return watch_timeout(root, change_id)
        snapshot = collect_snapshot(
            root,
            change_id,
            repository,
            pull_request,
            deadline if timeout_minutes else time.monotonic() + 60,
        )
        outcome = record_monitor_snapshot(root, change_id, snapshot)
        if outcome["changed"]:
            deadline = time.monotonic() + timeout_minutes * 60
            handoff = packet(root, change_id)
            current = handoff["status"]
            print(json.dumps({"packet": handoff, "snapshot": handoff["monitor"]["data"]}, indent=2))
        else:
            current = status(root, change_id)
        terminal = emit_terminal(current, already_emitted=outcome["changed"])
        if terminal is not None:
            return terminal
        time.sleep(
            min(intervals[min(index, len(intervals) - 1)], max(0, deadline - time.monotonic()))
        )
        index += 1


def emit_terminal(current: dict[str, Any], *, already_emitted: bool = False) -> int | None:
    if current["action"] not in {"complete", "investigate", "replan", "incomplete"}:
        return None
    if not already_emitted:
        print(json.dumps(current, indent=2))
    return int(current["action"] == "incomplete")


def watch_timeout(root: Path, change_id: str) -> int:
    terminal = emit_terminal(status(root, change_id))
    if terminal is not None:
        return terminal
    print(json.dumps({"action": "wait", "reason": "watch timeout"}))
    return 0


def collect_snapshot(
    root: Path, change_id: str, repository_name: str, pull_request: int, deadline: float
) -> dict[str, Any]:
    token = REQUEST_DEADLINE.set(deadline)
    try:
        select_target(root, change_id, repository_name, pull_request)
        epoch = binding_epoch(load(root, change_id))
        return {**gh_snapshot(repository_name, pull_request), "_input_epoch": epoch}
    except (
        RuntimeError,
        OSError,
        KeyError,
        TypeError,
        ValueError,
        subprocess.TimeoutExpired,
    ) as error:
        return {"errors": [str(error)]}
    finally:
        REQUEST_DEADLINE.reset(token)


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
