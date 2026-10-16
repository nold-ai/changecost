"""Behavioral tests for bounded, persisted review-session decisions."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
from types import SimpleNamespace
from typing import Any

import pytest

from quality import review_session

TEST_HEAD = ""
TEST_ROOT = Path()


@pytest.fixture(scope="session")
def committed_seed(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, str]:
    tmp_path = tmp_path_factory.mktemp("committed-seed")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".gitignore").write_text(".changecost/\n")
    (tmp_path / "input.txt").write_text("initial\n")
    subprocess.run(["git", "-C", str(tmp_path), "add", ".gitignore", "input.txt"], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(tmp_path),
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.com",
            "commit",
            "-qm",
            "initial",
        ],
        check=True,
    )
    head = subprocess.check_output(
        ["git", "-C", str(tmp_path), "rev-parse", "HEAD"], text=True
    ).strip()

    return tmp_path, head


@pytest.fixture(autouse=True)
def git_fixture(tmp_path: Path, committed_seed: tuple[Path, str]) -> None:
    global TEST_HEAD, TEST_ROOT

    seed, TEST_HEAD = committed_seed
    shutil.copytree(seed, tmp_path, dirs_exist_ok=True)
    TEST_ROOT = tmp_path


def contract() -> dict[str, object]:
    return session_contract(TEST_ROOT, TEST_HEAD)


def session_contract(root: Path, head: str) -> dict[str, object]:
    return {
        "requirements": ["tests pass"],
        "repository": "nold-ai/changecost",
        "acceptance_criteria": ["review evidence is current"],
        "non_goals": ["host authentication"],
        "trust_boundary": "configuration validation only",
        "intended_files": fixture_manifest(root),
        "base": head,
        "pr_base": {"ref": "main", "sha": head},
        "head": head,
        "required_reviewers": ["reviewer-a"],
        "required_checks": ["ci"],
        "required_statuses": [],
    }


def fixture_manifest(root: Path | None = None) -> dict[str, str]:
    root = TEST_ROOT if root is None else root
    names = subprocess.check_output(
        [
            "git",
            "-C",
            str(root),
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
        ],
        text=True,
    ).split("\0")
    return {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest()
        if (root / name).is_file()
        else "<absent>"
        for name in names
        if name
    }


def historical_capture(root: Path, declared: dict[str, str]) -> dict[str, Any]:
    """Compatibility oracle: preserve the schema-8 three-query byte construction."""
    git = review_session.repository.git
    flags = git(root, "ls-files", "-v", "-z").split(b"\0")
    if any(record[:1].islower() or record[:1] == b"S" for record in flags if record):
        raise ValueError("unsupported index flags")
    names = git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
    files = set(names.decode().split("\0")) - {""}
    index = git(root, "ls-files", "--stage", "-z")
    parsed = review_session.index_entries(index)
    fingerprints = {name: review_session.input_fingerprint(root, name, parsed) for name in declared}
    raw = review_session.repository.digest(root, files).encode() + b"\0" + index
    raw += b"\0" + json.dumps(fingerprints, sort_keys=True).encode()
    untracked = any(
        name not in parsed and review_session.file_fingerprint(root, name) != "<absent>"
        for name in declared
    )
    return {
        "head": git(root, "rev-parse", "HEAD").decode().strip(),
        "digest": hashlib.sha256(raw).hexdigest(),
        "clean": not untracked and not git(root, "status", "--porcelain", "--untracked-files=all"),
    }


def test_capture_acquires_git_inventory_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    declared = fixture_manifest(tmp_path)
    expected = historical_capture(tmp_path, declared)
    git = review_session.repository.git
    calls: list[tuple[str, ...]] = []

    def observed(root: Path, *args: str) -> bytes:
        calls.append(args)
        return git(root, *args)

    monkeypatch.setattr(review_session.repository, "git", observed)
    assert review_session.capture_inputs(tmp_path, TEST_HEAD, declared) == expected
    assert len([call for call in calls if call[0] == "ls-files"]) == 1
    assert len(calls) == 3
    assert ("rev-parse", "HEAD") in calls
    assert ("status", "--porcelain", "--untracked-files=all") in calls


@pytest.mark.parametrize(
    "change",
    ["pristine", "dirty", "staged", "deleted", "names", "ignored", "intent", "mode", "conflict"],
)
def test_capture_preserves_historical_fingerprint(tmp_path: Path, change: str) -> None:
    git = review_session.repository.git
    declared = fixture_manifest(tmp_path)
    if change in {"dirty", "staged"}:
        (tmp_path / "input.txt").write_text("changed\n")
        if change == "staged":
            git(tmp_path, "add", "input.txt")
            (tmp_path / "input.txt").write_text("working differs from index\n")
    if change == "deleted":
        (tmp_path / "input.txt").unlink()
    if change == "names":
        for name in ["tab\tfile", "line\nfile", "100644 deadbeef 0\tinput.txt", "unicode-\u00e4"]:
            (tmp_path / name).write_text("untracked\n")
            declared[name] = review_session.file_fingerprint(tmp_path, name)
        git(tmp_path, "add", "tab\tfile", "line\nfile")
    if change == "ignored":
        (tmp_path / ".changecost").mkdir()
        (tmp_path / ".changecost" / "ignored.txt").write_text("ignored but declared\n")
        declared.update({".changecost/ignored.txt": "declared", "planned.txt": "<absent>"})
    if change == "intent":
        (tmp_path / "new.txt").write_text("intent to add\n")
        git(tmp_path, "add", "-N", "new.txt")
        declared["new.txt"] = "declared"
    if change == "mode":
        git(tmp_path, "update-index", "--chmod=+x", "input.txt")
    if change == "conflict":
        blob = git(tmp_path, "rev-parse", "HEAD:input.txt").decode().strip()
        subprocess.run(
            ["git", "-C", str(tmp_path), "update-index", "--index-info"],
            input=f"100644 {blob} 1\tother.txt\n100644 {blob} 2\tother.txt\n",
            text=True,
            check=True,
        )
    assert review_session.capture_inputs(tmp_path, TEST_HEAD, declared) == historical_capture(
        tmp_path, declared
    )


@pytest.mark.parametrize("flag", ["--assume-unchanged", "--skip-worktree"])
def test_capture_rejects_undeclared_hidden_index_flags(tmp_path: Path, flag: str) -> None:
    review_session.repository.git(tmp_path, "update-index", flag, "input.txt")
    with pytest.raises(ValueError, match="index flags"):
        historical_capture(tmp_path, {})
    with pytest.raises(ValueError, match="index flags"):
        review_session.capture_inputs(tmp_path, TEST_HEAD, {})


@pytest.mark.parametrize(
    "raw", [b"H truncated", b"? \0", b"H\tname\0", b"X name\0", b"H bad\tname\0"]
)
def test_capture_rejects_malformed_git_inventory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, raw: bytes
) -> None:
    monkeypatch.setattr(review_session.repository, "git", lambda *args: raw)
    with pytest.raises(ValueError, match="malformed Git"):
        review_session.capture_index(tmp_path)


@pytest.fixture(scope="session")
def initialized_seed(
    tmp_path_factory: pytest.TempPathFactory, committed_seed: tuple[Path, str]
) -> Path:
    root = tmp_path_factory.mktemp("initialized-seed")
    seed, head = committed_seed
    shutil.copytree(seed, root, dirs_exist_ok=True)
    review_session.initialize(root, "change", session_contract(root, head))
    return root


def clone_session(seed: Path, root: Path, policy: dict[str, object]) -> dict[str, Any]:
    """Reuse pristine arrangement only; retain real replay and current Git checks."""
    state = review_session.load(seed, "change")
    assert state["revision"] == 0 and state["events"] == [] and state["phase"] == "active"
    assert state["batches"] == 0 and state["active_minutes"] == 0
    assert policy == state["contract"]
    assert (
        review_session.capture_inputs(root, state["reviewed_head"], policy["intended_files"])
        == (state["inputs"])
    )
    source = review_session.state_path(seed, "change").parent
    destination = review_session.state_path(root, "change").parent
    shutil.copytree(source, destination)
    return review_session.load(root, "change")


@pytest.fixture
def prepared_session(tmp_path: Path, initialized_seed: Path, git_fixture: None) -> dict[str, Any]:
    del git_fixture
    return clone_session(initialized_seed, tmp_path, contract())


def test_prepared_session_preserves_canonical_arrangement(
    tmp_path: Path, initialized_seed: Path, prepared_session: dict[str, Any]
) -> None:
    seed = review_session.load(initialized_seed, "change")
    assert prepared_session == seed
    assert review_session.load(tmp_path, "change") == seed
    assert (
        review_session.capture_inputs(tmp_path, TEST_HEAD, contract()["intended_files"])
        == (seed["inputs"])
    )
    assert review_session.status(tmp_path, "change")["action"] == "continue"


def test_prepared_session_files_and_events_are_isolated(
    tmp_path: Path,
    initialized_seed: Path,
    committed_seed: tuple[Path, str],
    prepared_session: dict[str, Any],
) -> None:
    other = tmp_path.parent / (tmp_path.name + "-other")
    committed, head = committed_seed
    shutil.copytree(committed, other)
    clone_session(initialized_seed, other, session_contract(other, head))
    names = [
        ".git/index",
        "input.txt",
        ".changecost/workflow/change/genesis.json",
        ".changecost/workflow/change/review-session.json",
    ]
    for name in names:
        assert (
            len({(root / name).stat().st_ino for root in (tmp_path, other, initialized_seed)}) == 3
        )
    review_session.record(tmp_path, "change", {"id": "one", "kind": "batch"})
    assert review_session.load(tmp_path, "change")["batches"] == 1
    assert review_session.load(other, "change") == prepared_session
    assert review_session.load(initialized_seed, "change") == prepared_session
    (tmp_path / "input.txt").write_text("changed\n")
    subprocess.run(["git", "-C", str(tmp_path), "add", "input.txt"], check=True)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"
    assert review_session.status(other, "change")["action"] == "continue"
    state = review_session.load(tmp_path, "change")
    state["batches"] = 0
    review_session.write_state(review_session.state_path(tmp_path, "change"), state)
    with pytest.raises(ValueError, match="contradicts canonical history"):
        review_session.load(tmp_path, "change")
    assert review_session.load(other, "change") == prepared_session
    assert review_session.load(initialized_seed, "change") == prepared_session


@pytest.mark.parametrize("fault", ["content", "index", "untracked", "policy", "seed"])
def test_prepared_session_rejects_changed_arrangement_before_copy(
    tmp_path: Path, initialized_seed: Path, fault: str
) -> None:
    policy = contract()
    seed = initialized_seed
    if fault in {"content", "index"}:
        (tmp_path / "input.txt").write_text("changed\n")
        if fault == "index":
            subprocess.run(["git", "-C", str(tmp_path), "add", "input.txt"], check=True)
            (tmp_path / "input.txt").write_text("initial\n")
    elif fault == "untracked":
        (tmp_path / "extra.txt").write_text("unexpected\n")
    elif fault == "policy":
        policy["trust_boundary"] = "different contract"
    else:
        seed = tmp_path.parent / (tmp_path.name + "-nonpristine")
        shutil.copytree(initialized_seed, seed)
        review_session.record(seed, "change", {"id": "one", "kind": "batch"})
    with pytest.raises(AssertionError):
        clone_session(seed, tmp_path, policy)
    assert not review_session.state_path(tmp_path, "change").parent.exists()


def complete_snapshot(epoch: str = "input-generation:0") -> dict[str, Any]:
    return {
        "_input_epoch": epoch,
        "requested_reviewers": [],
        "repository": "nold-ai/changecost",
        "pull_request": 24,
        "head": TEST_HEAD,
        "pr_base": {"ref": "main", "sha": TEST_HEAD},
        "checks": [
            {
                "check_runs": [
                    {
                        "name": "ci",
                        "status": "completed",
                        "conclusion": "success",
                        "started_at": "2099-01-01T00:00:00Z",
                    }
                ]
            }
        ],
        "statuses": [{"statuses": []}],
        "comments": [[]],
        "threads": [],
        "reviews": [
            [
                {
                    "id": 115,
                    "body": "",
                    "commit_id": TEST_HEAD,
                    "state": "APPROVED",
                    "user": {"login": "reviewer-a"},
                    "submitted_at": "2099-01-01T00:00:00Z",
                }
            ]
        ],
    }


def complete_session(tmp_path: Path, *, timing: bool = True) -> None:
    review_session.record_monitor_snapshot(tmp_path, "change", complete_snapshot())
    for category in ("gate", "reviewer"):
        review_session.record(
            tmp_path,
            "change",
            {
                "id": category,
                "kind": "evidence",
                "evidence_type": category,
                "result": "pass",
                "head": TEST_HEAD,
                "binding": review_session.evidence_binding(review_session.load(tmp_path, "change")),
                "reviewed_reports": review_session.report_receipts(complete_snapshot()),
            },
        )
    review_session.record(tmp_path, "change", {"id": "done", "kind": "phase", "phase": "complete"})
    if timing:
        review_session.record(
            tmp_path, "change", {"id": "completed-time", "kind": "active_minutes", "minutes": 0}
        )


def test_final_batch_completion_and_pending_precedence(
    tmp_path: Path, prepared_session: dict[str, Any]
) -> None:
    for index in range(3):
        review_session.record(tmp_path, "change", {"id": str(index), "kind": "batch"})
    complete_session(tmp_path)
    assert review_session.status(tmp_path, "change")["action"] == "complete"
    snapshot = complete_snapshot()
    snapshot["checks"] = [{"check_runs": [{"name": "test", "status": "in_progress"}]}]
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "replan"


@pytest.mark.parametrize(
    "field,value",
    [
        ("budget", {"minutes": "90", "batches": 3}),
        ("findings", [{}]),
        ("events", [None]),
        ("active_minutes", float("nan")),
        ("batches", -1),
        ("monitor", {"snapshot": None, "data": None, "errors": 1, "pending": []}),
    ],
)
def test_nested_corruption_fails_closed(
    tmp_path: Path, field: str, value: object, prepared_session: dict[str, Any]
) -> None:
    state = prepared_session
    state[field] = value
    review_session.write_state(review_session.state_path(tmp_path, "change"), state)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


def test_conflicting_duplicate_event_rejected(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
    review_session.record(tmp_path, "change", {"id": "x", "kind": "batch"})
    with pytest.raises(review_session.ConflictError):
        review_session.record(tmp_path, "change", {"id": "x", "kind": "phase", "phase": "paused"})


@pytest.mark.parametrize(
    "source,item,action",
    [
        ("checks", {"name": "ci", "status": "completed", "conclusion": "success"}, "continue"),
        ("checks", {"name": "ci", "status": "completed", "conclusion": "failure"}, "incomplete"),
        ("checks", {"name": "ci", "status": "completed", "conclusion": "skipped"}, "incomplete"),
        ("statuses", {"context": "ci", "state": "failure"}, "incomplete"),
        ("statuses", {"context": "ci", "state": "pending"}, "wait"),
    ],
)
def test_real_rest_states(tmp_path: Path, source: str, item: dict[str, str], action: str) -> None:
    review_session.initialize(tmp_path, "change", contract())
    snapshot = complete_snapshot()
    snapshot[source] = [
        {
            "check_runs" if source == "checks" else "statuses": [
                {**item, "started_at": "2099-01-01T00:00:00Z", "created_at": "2099-01-01T00:00:00Z"}
            ]
        }
    ]
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == action


def test_scope_resolution_names_pending_identity(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
    review_session.record(
        tmp_path, "change", {"id": "scope", "kind": "scope_decision", "decision": "pending"}
    )
    review_session.record(
        tmp_path,
        "change",
        {"id": "resolve", "kind": "scope_decision", "decision": "approved", "supersedes": "scope"},
    )
    assert review_session.status(tmp_path, "change")["action"] == "continue"


def test_fixed_escape_retains_escalation(tmp_path: Path, prepared_session: dict[str, Any]) -> None:
    for identity in ("one", "two"):
        review_session.record(
            tmp_path, "change", {"id": identity, "kind": "finding", "family": "f"}
        )
    review_session.record(
        tmp_path,
        "change",
        {"id": "fix-one", "kind": "disposition", "finding_id": "one", "disposition": "fixed"},
    )
    assert review_session.status(tmp_path, "change")["action"] == "continue"
    review_session.record(tmp_path, "change", {"id": "three", "kind": "finding", "family": "f"})
    review_session.record(
        tmp_path,
        "change",
        {"id": "fix-three", "kind": "disposition", "finding_id": "three", "disposition": "fixed"},
    )
    assert review_session.status(tmp_path, "change")["action"] == "investigate"
    review_session.record(
        tmp_path, "change", {"id": "investigate", "kind": "investigation", "family": "f"}
    )
    review_session.record(tmp_path, "change", {"id": "four", "kind": "finding", "family": "f"})
    assert review_session.status(tmp_path, "change")["action"] == "replan"


def test_missing_or_malformed_state_is_incomplete(tmp_path: Path) -> None:
    assert review_session.status(tmp_path, "missing")["action"] == "incomplete"
    path = review_session.state_path(tmp_path, "bad")
    path.parent.mkdir(parents=True)
    path.write_text("not json")
    assert review_session.status(tmp_path, "bad")["action"] == "incomplete"


def test_legacy_session_without_required_reviewer_contract_is_incomplete(tmp_path: Path) -> None:
    path = review_session.state_path(tmp_path, "legacy")
    path.parent.mkdir(parents=True)
    legacy = review_session.initialize(tmp_path, "current", contract())
    legacy["change_id"] = "legacy"
    del legacy["contract"]["required_reviewers"]
    path.write_text(json.dumps(legacy))
    assert review_session.status(tmp_path, "legacy")["action"] == "incomplete"


def test_budget_and_extension_keep_existing_counters(
    tmp_path: Path, prepared_session: dict[str, Any]
) -> None:
    review_session.record(
        tmp_path, "change", {"id": "finding", "kind": "finding", "family": "gate"}
    )
    for number in range(3):
        review_session.record(tmp_path, "change", {"id": f"batch-{number}", "kind": "batch"})
    result = review_session.status(tmp_path, "change")
    assert result["action"] == "replan"
    review_session.record(
        tmp_path,
        "change",
        {
            "id": "extension",
            "kind": "extension",
            "batches": 1,
            "minutes": 30,
            "approved_by": "maintainer",
        },
    )
    result = review_session.status(tmp_path, "change")
    assert result["action"] == "continue"
    assert result["batches"] == 3


def test_final_allowed_batch_requires_replanning_even_after_fixes(
    tmp_path: Path, prepared_session: dict[str, Any]
) -> None:
    review_session.record(
        tmp_path, "change", {"id": "finding", "kind": "finding", "family": "gate"}
    )
    review_session.record(
        tmp_path,
        "change",
        {"id": "fixed", "kind": "disposition", "finding_id": "finding", "disposition": "fixed"},
    )
    for number in range(3):
        review_session.record(tmp_path, "change", {"id": f"batch-{number}", "kind": "batch"})
    assert review_session.status(tmp_path, "change")["action"] == "replan"


def test_head_advance_preserves_budget_and_history(tmp_path: Path) -> None:
    state = review_session.initialize(tmp_path, "change", contract())
    review_session.record(tmp_path, "change", {"id": "batch", "kind": "batch"})
    subprocess.run(
        [
            "git",
            "-C",
            str(tmp_path),
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.com",
            "commit",
            "--allow-empty",
            "-qm",
            "next",
        ],
        check=True,
    )
    new_head = subprocess.check_output(
        ["git", "-C", str(tmp_path), "rev-parse", "HEAD"], text=True
    ).strip()
    review_session.record(
        tmp_path, "change", {"id": "advance", "kind": "advance_head", "head": new_head}
    )
    updated = review_session.load(tmp_path, "change")
    assert updated["reviewed_head"] == new_head
    assert updated["batches"] == 1
    assert updated["contract"] == state["contract"]


def test_partial_state_is_incomplete_instead_of_crashing(tmp_path: Path) -> None:
    path = review_session.state_path(tmp_path, "change")
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {"schema_version": 1, "change_id": "change", "contract": contract(), "events": []}
        )
    )
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


def test_finding_family_requires_investigation_then_replan(
    tmp_path: Path, prepared_session: dict[str, Any]
) -> None:
    review_session.record(
        tmp_path, "change", {"id": "one", "kind": "finding", "family": "pytest-config"}
    )
    review_session.record(
        tmp_path,
        "change",
        {"id": "fixed", "kind": "disposition", "finding_id": "one", "disposition": "fixed"},
    )
    review_session.record(tmp_path, "change", {"id": "batch", "kind": "batch"})
    review_session.record(
        tmp_path, "change", {"id": "two", "kind": "finding", "family": "pytest-config"}
    )
    assert review_session.status(tmp_path, "change")["action"] == "investigate"
    review_session.record(
        tmp_path,
        "change",
        {"id": "investigate", "kind": "investigation", "family": "pytest-config"},
    )
    review_session.record(
        tmp_path, "change", {"id": "three", "kind": "finding", "family": "pytest-config"}
    )
    assert review_session.status(tmp_path, "change")["action"] == "replan"


def test_record_is_idempotent_and_rejects_conflicting_writer(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
    first = review_session.record(tmp_path, "change", {"id": "batch", "kind": "batch"})
    duplicate = review_session.record(tmp_path, "change", {"id": "batch", "kind": "batch"})
    assert first["revision"] == duplicate["revision"]
    with pytest.raises(review_session.ConflictError):
        review_session.record(
            tmp_path, "change", {"id": "other", "kind": "batch"}, expected_revision=0
        )


def test_packet_keeps_unresolved_evidence_and_usage_units(
    tmp_path: Path, prepared_session: dict[str, Any]
) -> None:
    review_session.record(
        tmp_path,
        "change",
        {"id": "finding", "kind": "finding", "family": "workflow", "evidence": "report.json"},
    )
    review_session.record(
        tmp_path,
        "change",
        {"id": "usage", "kind": "usage", "cached_input": 10, "uncached_input": 2, "output": 1},
    )
    packet = review_session.packet(tmp_path, "change")
    assert packet["unresolved_findings"][0]["evidence"] == "report.json"
    assert packet["usage"] == {"cached_input": 10, "uncached_input": 2, "output": 1, "cost": None}


def test_disposition_does_not_transfer_without_an_exact_finding_id(
    tmp_path: Path, prepared_session: dict[str, Any]
) -> None:
    review_session.record(
        tmp_path, "change", {"id": "old", "kind": "finding", "family": "workflow"}
    )
    review_session.record(
        tmp_path,
        "change",
        {"id": "resolved", "kind": "disposition", "finding_id": "old", "disposition": "fixed"},
    )
    review_session.record(
        tmp_path, "change", {"id": "moved", "kind": "finding", "family": "workflow"}
    )
    assert review_session.packet(tmp_path, "change")["unresolved_findings"][0]["id"] == "moved"


def test_changed_monitor_snapshots_are_deduplicated(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
    pages = {"checks": [{"id": 1, "conclusion": "success"}], "reviews": []}
    first = review_session.record_monitor_snapshot(tmp_path, "change", pages)
    second = review_session.record_monitor_snapshot(
        tmp_path, "change", json.loads(json.dumps(pages))
    )
    assert first["changed"] is True
    assert second["changed"] is False


def test_monitor_error_leaves_session_incomplete(
    tmp_path: Path, prepared_session: dict[str, Any]
) -> None:
    review_session.record_monitor_snapshot(tmp_path, "change", {"errors": ["rate limited"]})
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


def test_monitor_waits_for_current_head_results_from_named_reviewers(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
    review_session.record_monitor_snapshot(
        tmp_path,
        "change",
        {
            **complete_snapshot(),
            "head": contract()["head"],
            "reviews": [
                [
                    {
                        "id": 446,
                        "body": "",
                        "commit_id": contract()["head"],
                        "state": "APPROVED",
                        "user": {"login": "other"},
                    }
                ]
            ],
        },
    )
    assert review_session.status(tmp_path, "change")["action"] == "wait"


def test_unchanged_watcher_timeout_fails_for_incomplete_session(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    prepared_session: dict[str, Any],
) -> None:
    review_session.record(
        tmp_path, "change", {"id": "scope", "kind": "scope_decision", "decision": "pending"}
    )
    snapshot = {"head": contract()["head"], "checks": []}
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    monkeypatch.setattr(review_session, "gh_snapshot", lambda repository, pull_request: snapshot)
    assert review_session.watch(tmp_path, "change", "nold-ai/changecost", 22, 0) == 1
    assert '"action": "incomplete"' in capsys.readouterr().out


def test_watcher_polls_after_a_changed_continue_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, prepared_session: dict[str, Any]
) -> None:
    snapshot = {
        **complete_snapshot(),
        "head": contract()["head"],
        "reviews": [
            [
                {
                    "id": 481,
                    "body": "",
                    "commit_id": contract()["head"],
                    "state": "APPROVED",
                    "user": {"login": "reviewer-a"},
                }
            ]
        ],
    }
    snapshot["checks"][0]["check_runs"][0]["status"] = "in_progress"
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    acknowledge_reports(tmp_path, "existing-review")
    calls: list[int] = []
    clock = [0.0]
    monkeypatch.setattr(
        review_session, "gh_snapshot", lambda repository, pull_request: calls.append(1) or snapshot
    )
    monkeypatch.setattr(review_session.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        review_session.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + seconds)
    )
    assert review_session.watch(tmp_path, "change", "nold-ai/changecost", 24, 1) == 0
    assert len(calls) == 3


def test_changed_monitor_head_and_empty_completion_are_incomplete(
    tmp_path: Path, prepared_session: dict[str, Any]
) -> None:
    review_session.record(
        tmp_path, "change", {"id": "complete", "kind": "phase", "phase": "complete"}
    )
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"
    review_session.record_monitor_snapshot(tmp_path, "change", {"head": "other"})
    assert (
        review_session.status(tmp_path, "change")["reason"]
        == "monitor evidence is for a different head"
    )


def test_snapshot_reads_each_paginated_review_source(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, bool]] = []

    def fake_gh(endpoint: str, *, paginate: bool = False) -> object:
        calls.append((endpoint, paginate))
        return (
            {
                "head": {"sha": TEST_HEAD},
                "base": {"ref": "main", "sha": TEST_HEAD},
                "requested_reviewers": [],
            }
            if not paginate
            else []
        )

    monkeypatch.setattr(review_session, "gh_json", fake_gh)
    monkeypatch.setattr(
        review_session,
        "gh_review_threads",
        lambda repository, pull_request: [
            {"id": "thread-1", "isResolved": False, "isOutdated": False, "comments": []}
        ],
    )
    snapshot = review_session.gh_snapshot("nold-ai/changecost", 22)
    assert snapshot["head"] == TEST_HEAD
    assert len([call for call in calls if call[1]]) == 8
    assert snapshot["threads"] == [
        {"id": "thread-1", "isResolved": False, "isOutdated": False, "comments": []}
    ]


def test_review_threads_and_comments_paginate(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_graphql(query: str, **variables: object) -> dict[str, object]:
        calls.append(variables)
        if "repository" in query:
            if variables.get("cursor") is None:
                return {
                    "data": {
                        "repository": {
                            "pullRequest": {
                                "reviewThreads": {
                                    "nodes": [
                                        {
                                            "id": "thread-1",
                                            "isResolved": False,
                                            "isOutdated": False,
                                            "comments": {
                                                "nodes": [{"id": "comment-1", "body": "first"}],
                                                "pageInfo": {
                                                    "hasNextPage": True,
                                                    "endCursor": "comment-cursor",
                                                },
                                            },
                                        }
                                    ],
                                    "pageInfo": {"hasNextPage": True, "endCursor": "thread-cursor"},
                                }
                            }
                        }
                    }
                }
            return {
                "data": {
                    "repository": {
                        "pullRequest": {
                            "reviewThreads": {
                                "nodes": [],
                                "pageInfo": {"hasNextPage": False, "endCursor": None},
                            }
                        }
                    }
                }
            }
        return {
            "data": {
                "node": {
                    "comments": {
                        "nodes": [{"id": "comment-2", "body": "second"}],
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                    }
                }
            }
        }

    monkeypatch.setattr(review_session, "gh_graphql", fake_graphql)
    threads = review_session.gh_review_threads("nold-ai/changecost", 22)
    assert [item["id"] for item in threads] == ["thread-1"]
    assert [item["id"] for item in threads[0]["comments"]] == ["comment-1", "comment-2"]
    assert [call.get("cursor") for call in calls] == [None, "comment-cursor", "thread-cursor"]


def test_graphql_errors_are_incomplete_evidence(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        review_session.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0, stdout='{"errors": [{"message": "forbidden"}]}', stderr=""
        ),
    )
    with pytest.raises(RuntimeError, match="forbidden"):
        review_session.gh_graphql("query { viewer { login } }")


@pytest.mark.parametrize("mutation", ["untracked", "tracked", "deleted"])
def test_reviewed_input_changes_fail_closed(tmp_path: Path, mutation: str) -> None:
    review_session.initialize(tmp_path, "change", contract())
    if mutation == "untracked":
        (tmp_path / "new.py").write_text("change")
    elif mutation == "tracked":
        (tmp_path / ".gitignore").write_text(".changecost/\n# changed\n")
    else:
        (tmp_path / ".gitignore").unlink()
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


@pytest.mark.parametrize("source", ["checks", "statuses", "reviews", "threads", "comments"])
def test_missing_source_cannot_complete(
    tmp_path: Path, source: str, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    del snapshot[source]
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


def test_outdated_unresolved_thread_blocks_completion(
    tmp_path: Path, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    snapshot["threads"] = [{"id": "t", "isOutdated": True, "isResolved": False, "comments": []}]
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "wait"


def test_cli_initialization_record_and_packet(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    payload = tmp_path / ".changecost" / "input.json"
    payload.parent.mkdir()
    for operation, data in (
        ("init", contract()),
        ("record", {"id": "pause", "kind": "phase", "phase": "paused"}),
        ("packet", {}),
        ("status", {}),
    ):
        payload.write_text(json.dumps(data))
        monkeypatch.setattr(
            "sys.argv",
            [
                "review-session",
                operation,
                "change",
                "--root",
                str(tmp_path),
                "--json",
                str(payload),
            ],
        )
        assert review_session.main() == 0
        assert json.loads(capsys.readouterr().out)


@pytest.mark.parametrize("operation", ["init", "record", "watch", "packet", "status"])
def test_cli_missing_input_is_incomplete(
    tmp_path: Path,
    operation: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        "sys.argv", ["review-session", operation, "missing", "--root", str(tmp_path)]
    )
    assert review_session.main() == 1
    assert json.loads(capsys.readouterr().out)["action"] == "incomplete"


@pytest.mark.parametrize("cursor", [None, "", "repeat"])
def test_invalid_cursor_fails_closed(cursor: str | None) -> None:
    with pytest.raises(ValueError, match="pagination"):
        review_session.next_cursor({"endCursor": cursor}, {"repeat"})


def test_subprocess_requests_are_bounded(monkeypatch: pytest.MonkeyPatch) -> None:
    timeouts = []

    def run(*args: object, **kwargs: object) -> SimpleNamespace:
        timeouts.append(kwargs.get("timeout"))
        return SimpleNamespace(returncode=0, stdout='{"data": {}}', stderr="")

    monkeypatch.setattr(review_session.subprocess, "run", run)
    assert review_session.gh_graphql("query") == {"data": {}}
    assert review_session.gh_json("repos/example/repo") == {"data": {}}
    assert timeouts == [60, 60]


def test_watcher_api_timeout_is_incomplete(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, prepared_session: dict[str, Any]
) -> None:

    def fail(*args: object) -> dict[str, object]:
        raise subprocess.TimeoutExpired("gh", 60)

    monkeypatch.setattr(review_session, "gh_snapshot", fail)
    assert review_session.watch(tmp_path, "change", "repo", 24, 0) == 1


@pytest.mark.parametrize(
    "kind,payload",
    [
        ("phase", {"phase": "invalid"}),
        ("disposition", {"finding_id": "absent", "disposition": "fixed"}),
        ("evidence", {"evidence_type": "bad", "result": "pass", "head": "x"}),
        ("active_minutes", {"minutes": -1}),
        ("extension", {"approved_by": "owner", "minutes": float("inf")}),
        ("advance_head", {"head": "short"}),
    ],
)
def test_invalid_events_do_not_mutate_state(
    tmp_path: Path, kind: str, payload: dict[str, object], prepared_session: dict[str, Any]
) -> None:
    before = review_session.load(tmp_path, "change")
    with pytest.raises(ValueError):
        review_session.record(tmp_path, "change", {"id": "bad", "kind": kind, **payload})
    assert review_session.load(tmp_path, "change") == before


def test_same_head_rebind_invalidates_passing_evidence(tmp_path: Path) -> None:
    scope = contract()
    assert isinstance(scope["intended_files"], dict)
    scope["intended_files"]["added.py"] = "<absent>"
    review_session.initialize(tmp_path, "change", scope)
    complete_session(tmp_path)
    (tmp_path / "added.py").write_text("new input")
    review_session.record(
        tmp_path, "change", {"id": "rebind", "kind": "advance_head", "head": TEST_HEAD}
    )
    review_session.record_monitor_snapshot(
        tmp_path, "change", complete_snapshot("input-generation:1")
    )
    review_session.record(
        tmp_path, "change", {"id": "done-again", "kind": "phase", "phase": "complete"}
    )
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


def test_staged_blob_change_invalidates_inputs_with_unchanged_worktree(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
    path = tmp_path / ".gitignore"
    original = path.read_text()
    path.write_text(original + "# staged\n")
    subprocess.run(["git", "-C", str(tmp_path), "add", ".gitignore"], check=True)
    path.write_text(original)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


def test_declared_missing_ci_check_blocks_completion(tmp_path: Path) -> None:
    policy = {**contract(), "required_checks": ["missing-ci"], "required_statuses": []}
    review_session.initialize(tmp_path, "change", policy)
    complete_session(tmp_path)
    assert review_session.status(tmp_path, "change")["action"] == "wait"


@pytest.mark.parametrize("disposition", ["invalid", "fixed"])
def test_corrupt_disposition_cannot_hide_unresolved_finding(
    tmp_path: Path, disposition: str
) -> None:
    review_session.initialize(tmp_path, "change", contract())
    review_session.record(tmp_path, "change", {"id": "one", "kind": "finding", "family": "f"})
    state = review_session.load(tmp_path, "change")
    state["findings"][0]["disposition"] = disposition
    review_session.write_state(review_session.state_path(tmp_path, "change"), state)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


def test_staged_mode_change_invalidates_reviewed_inputs(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
    subprocess.run(
        ["git", "-C", str(tmp_path), "update-index", "--chmod=+x", ".gitignore"], check=True
    )
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


def test_missing_declared_status_blocks_completion(tmp_path: Path) -> None:
    review_session.initialize(
        tmp_path, "change", {**contract(), "required_statuses": ["review-status"]}
    )
    complete_session(tmp_path)
    assert review_session.status(tmp_path, "change")["action"] == "wait"


@pytest.mark.parametrize(
    "field,value", [("required_checks", []), ("required_checks", "ci"), ("required_statuses", None)]
)
def test_gate_contract_requires_explicit_valid_identities(
    tmp_path: Path, field: str, value: object
) -> None:
    with pytest.raises(ValueError):
        review_session.initialize(tmp_path, "change", {**contract(), field: value})


def test_completion_requires_explicit_current_timing(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
    complete_session(tmp_path, timing=False)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"
    review_session.record(
        tmp_path, "change", {"id": "measured", "kind": "active_minutes", "minutes": 0}
    )
    assert review_session.status(tmp_path, "change")["action"] == "complete"
    assert review_session.load(tmp_path, "change")["active_minutes"] == 0
    review_session.record(
        tmp_path, "change", {"id": "refresh", "kind": "advance_head", "head": TEST_HEAD}
    )
    for category in ("gate", "reviewer"):
        review_session.record(
            tmp_path,
            "change",
            {
                "id": "new-" + category,
                "reviewed_reports": review_session.report_receipts(complete_snapshot()),
                "binding": review_session.evidence_binding(review_session.load(tmp_path, "change")),
                "kind": "evidence",
                "evidence_type": category,
                "head": TEST_HEAD,
                "result": "pass",
            },
        )
    review_session.record_monitor_snapshot(
        tmp_path, "change", complete_snapshot("input-generation:1")
    )
    review_session.record(
        tmp_path, "change", {"id": "new-done", "kind": "phase", "phase": "complete"}
    )
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"
    assert "elapsed-time measurement" in review_session.status(tmp_path, "change")["reason"]


def test_missing_minutes_in_persisted_event_requires_recovery(tmp_path: Path) -> None:
    state = review_session.initialize(tmp_path, "change", contract())
    state["events"].append({"id": "missing", "kind": "active_minutes"})
    review_session.write_state(review_session.state_path(tmp_path, "change"), state)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


@pytest.mark.parametrize(
    "login,states,expected",
    [
        ("reviewer-a", ["APPROVED", "CHANGES_REQUESTED"], "incomplete"),
        ("reviewer-a", ["CHANGES_REQUESTED", "APPROVED"], "complete"),
        ("reviewer-a", ["APPROVED", "PENDING"], "wait"),
        ("reviewer-a", ["APPROVED", "DISMISSED"], "wait"),
        ("human", ["CHANGES_REQUESTED"], "incomplete"),
    ],
)
def test_latest_reviewer_state_controls_completion(
    tmp_path: Path, login: str, states: list[str], expected: str
) -> None:
    review_session.initialize(tmp_path, "change", contract())
    complete_session(tmp_path)
    review_session.record(
        tmp_path, "change", {"id": "time", "kind": "active_minutes", "minutes": 0}
    )
    snapshot = complete_snapshot()
    snapshot["reviews"] = [
        [
            {
                "body": "",
                "id": index + 1,
                "commit_id": TEST_HEAD,
                "user": {"login": login},
                "state": state,
                "submitted_at": "2099-01-01T00:00:00Z",
            }
            for index, state in enumerate(states)
        ]
    ]
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    acknowledge_reports(tmp_path, "explicit-review")
    assert review_session.status(tmp_path, "change")["action"] == expected


@pytest.mark.parametrize(
    "paginate,payload", [(False, {"head": {"sha": "x"}}), (True, [[{"id": 1}], [{"id": 2}]])]
)
def test_rest_parser_reads_complete_pretty_json(
    monkeypatch: pytest.MonkeyPatch, paginate: bool, payload: object
) -> None:
    commands = []

    def run(command: list[str], **kwargs: object) -> SimpleNamespace:
        commands.append(command)
        return SimpleNamespace(returncode=0, stdout=json.dumps(payload, indent=2), stderr="")

    monkeypatch.setattr(review_session.subprocess, "run", run)
    assert review_session.gh_json("endpoint", paginate=paginate) == payload
    assert ("--slurp" in commands[0]) == paginate


def test_timing_timestamp_preserves_idempotence_and_restart(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
    event = {"id": "time", "kind": "active_minutes", "minutes": 2}
    first = review_session.record(tmp_path, "change", event)
    second = review_session.record(tmp_path, "change", event)
    assert second == first
    assert review_session.load(tmp_path, "change")["active_minutes"] == 2
    assert len(second["timing_measurements"]) == 1
    assert second["timing_measurements"][0]["recorded_at"].endswith("+00:00")
    assert second["events"][0] == event


def test_missing_minutes_ingestion_does_not_create_measurement(
    tmp_path: Path, prepared_session: dict[str, Any]
) -> None:
    with pytest.raises(ValueError):
        review_session.record(tmp_path, "change", {"id": "time", "kind": "active_minutes"})
    assert review_session.load(tmp_path, "change")["timing_measurements"] == []


def test_rest_parser_preserves_api_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        review_session.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=1, stdout="", stderr="rate limited"),
    )
    with pytest.raises(RuntimeError, match="rate limited"):
        review_session.gh_json("endpoint", paginate=True)


def test_cli_watch_reports_malformed_paginated_response(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    prepared_session: dict[str, Any],
) -> None:

    def snapshot(*args: object) -> dict[str, object]:
        raise ValueError("paginated API response must be a slurped page array")

    monkeypatch.setattr(review_session, "gh_snapshot", snapshot)
    monkeypatch.setattr(
        "sys.argv",
        [
            "review-session",
            "watch",
            "change",
            "--root",
            str(tmp_path),
            "--repo",
            "nold-ai/changecost",
            "--pr",
            "24",
            "--timeout-minutes",
            "0",
        ],
    )
    assert review_session.main() == 1
    assert '"action": "incomplete"' in capsys.readouterr().out


def test_review_supersession_spans_pages_and_ignores_old_head(tmp_path: Path) -> None:
    review_session.initialize(
        tmp_path, "change", {**contract(), "required_reviewers": ["reviewer-a[bot]"]}
    )
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    snapshot["reviews"] = [
        [
            {
                "id": 973,
                "body": "",
                "commit_id": TEST_HEAD,
                "user": {"login": "reviewer-a[bot]"},
                "state": "CHANGES_REQUESTED",
            }
        ],
        [
            {
                "id": 980,
                "body": "",
                "commit_id": TEST_HEAD,
                "user": {"login": "reviewer-a[bot]"},
                "state": "APPROVED",
                "submitted_at": "2099-01-01T00:00:00Z",
            },
            {
                "id": 986,
                "body": "",
                "commit_id": "old",
                "user": {"login": "reviewer-a[bot]"},
                "state": "CHANGES_REQUESTED",
            },
        ],
    ]
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    acknowledge_reports(tmp_path, "explicit-review")
    assert review_session.status(tmp_path, "change")["action"] == "complete"


def test_fractional_minutes_sum_canonically_across_restart_and_budget(
    tmp_path: Path, prepared_session: dict[str, Any]
) -> None:
    review_session.record(
        tmp_path, "change", {"id": "initial-time", "kind": "active_minutes", "minutes": 89}
    )
    for index in range(10):
        review_session.record(
            tmp_path, "change", {"id": f"time-{index}", "kind": "active_minutes", "minutes": 0.1}
        )
    assert review_session.load(tmp_path, "change")["active_minutes"] == 90
    assert review_session.status(tmp_path, "change")["action"] == "replan"
    complete_session(tmp_path)
    assert review_session.status(tmp_path, "change")["action"] == "complete"
    review_session.record(tmp_path, "change", {"id": "resume", "kind": "phase", "phase": "active"})
    assert review_session.status(tmp_path, "change")["action"] == "replan"


@pytest.mark.parametrize(
    "field,value",
    [
        ("batches", 0),
        ("batches", True),
        ("batches", 1.0),
        ("budget", {"batches": 100, "minutes": 9000}),
        ("scope_decisions", []),
        ("phase", "paused"),
        ("usage", {"cached_input": 123, "uncached_input": None, "output": None, "cost": None}),
        ("revision", 0),
        ("investigations", []),
        ("evidence", []),
    ],
)
def test_every_derived_cache_reconciles_with_history(
    tmp_path: Path, field: str, value: object, prepared_session: dict[str, Any]
) -> None:
    for event in (
        {"id": "batch", "kind": "batch"},
        {"id": "scope", "kind": "scope_decision", "decision": "pending"},
        {"id": "investigation", "kind": "investigation", "family": "f"},
        {
            "id": "evidence",
            "binding": review_session.evidence_binding(review_session.load(tmp_path, "change")),
            "kind": "evidence",
            "evidence_type": "gate",
            "head": TEST_HEAD,
            "result": "pass",
        },
    ):
        review_session.record(tmp_path, "change", event)
    state = review_session.load(tmp_path, "change")
    state[field] = value
    review_session.write_state(review_session.state_path(tmp_path, "change"), state)
    with pytest.raises(ValueError, match="canonical"):
        review_session.load(tmp_path, "change")
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


def test_deleted_state_cannot_reinitialize_budget(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
    review_session.state_path(tmp_path, "change").unlink()
    with pytest.raises(ValueError, match="recover"):
        review_session.initialize(tmp_path, "change", contract())


@pytest.mark.parametrize("dirty", ["tracked", "untracked", "staged"])
def test_dirty_frozen_inputs_cannot_claim_published_completion(tmp_path: Path, dirty: str) -> None:
    path = tmp_path / ("new.py" if dirty == "untracked" else ".gitignore")
    path.write_text(".changecost/\n# dirty\n")
    if dirty == "staged":
        subprocess.run(["git", "-C", str(tmp_path), "add", ".gitignore"], check=True)
    review_session.initialize(tmp_path, "change", contract())
    complete_session(tmp_path)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


@pytest.mark.parametrize("field,value", [("repository", "other/fork"), ("pull_request", 25)])
def test_monitor_target_cannot_change_on_shared_head(
    tmp_path: Path, field: str, value: object, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    snapshot[field] = value
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


def test_bot_identity_cannot_approve_for_or_erase_human(
    tmp_path: Path, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    snapshot["reviews"] = [
        [
            {
                "id": 1091,
                "body": "",
                "commit_id": TEST_HEAD,
                "state": "CHANGES_REQUESTED",
                "user": {"login": "reviewer-a"},
            },
            {
                "id": 1092,
                "body": "",
                "commit_id": TEST_HEAD,
                "state": "APPROVED",
                "user": {"login": "reviewer-a[bot]"},
            },
        ]
    ]
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


@pytest.mark.parametrize(
    "disposition,expected",
    [("non_finding", "continue"), ("fixed", "investigate"), ("accepted_exception", "investigate")],
)
def test_final_dispositions_preserve_only_genuine_escapes(
    tmp_path: Path, disposition: str, expected: str, prepared_session: dict[str, Any]
) -> None:
    for event in (
        {"id": "first", "kind": "finding", "family": "f"},
        {"id": "fixed", "kind": "disposition", "finding_id": "first", "disposition": "fixed"},
        {"id": "repeat", "kind": "finding", "family": "f"},
        {
            "id": "triaged",
            "kind": "disposition",
            "finding_id": "repeat",
            "disposition": disposition,
        },
    ):
        review_session.record(tmp_path, "change", event)
    assert review_session.status(tmp_path, "change")["action"] == expected


def test_monitor_cache_cannot_hide_raw_pending(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
    complete_session(tmp_path)
    state = review_session.load(tmp_path, "change")
    state["monitor"]["data"]["checks"][0]["check_runs"][0]["status"] = "in_progress"
    review_session.write_state(review_session.state_path(tmp_path, "change"), state)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


def test_avatar_noise_does_not_count_as_progress(
    tmp_path: Path, prepared_session: dict[str, Any]
) -> None:
    snapshot = complete_snapshot()
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    snapshot["reviews"][0][0]["user"]["avatar_url"] = "irrelevant"
    assert review_session.record_monitor_snapshot(tmp_path, "change", snapshot)["changed"] is False
    complete_session(tmp_path)
    assert review_session.status(tmp_path, "change")["action"] == "complete"


@pytest.mark.parametrize("error", [OSError("missing gh"), TypeError("null payload")])
def test_collection_failure_replaces_prior_green(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    error: Exception,
    prepared_session: dict[str, Any],
) -> None:
    complete_session(tmp_path)

    def fail(*args: object) -> dict[str, object]:
        raise error

    monkeypatch.setattr(review_session, "gh_snapshot", fail)
    assert review_session.watch(tmp_path, "change", "nold-ai/changecost", 24, 0) == 1
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


def test_old_observation_cannot_cross_same_head_epoch(
    tmp_path: Path, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    old = review_session.load(tmp_path, "change")["monitor"]["data"]
    review_session.record(
        tmp_path, "change", {"id": "refresh", "kind": "advance_head", "head": TEST_HEAD}
    )
    review_session.record_monitor_snapshot(tmp_path, "change", old)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


@pytest.mark.parametrize("remaining", [0, 0.25, 100])
def test_request_budget_caps_every_api_call(
    monkeypatch: pytest.MonkeyPatch, remaining: float
) -> None:
    monkeypatch.setattr(review_session.time, "monotonic", lambda: 100.0)
    token = review_session.REQUEST_DEADLINE.set(100 + remaining)
    try:
        if not remaining:
            with pytest.raises(ValueError, match="deadline"):
                review_session.request_timeout()
        else:
            assert review_session.request_timeout() == min(60, remaining)
    finally:
        review_session.REQUEST_DEADLINE.reset(token)


@pytest.mark.parametrize(
    "connection",
    [None, {"nodes": [], "pageInfo": None}, {"nodes": [], "pageInfo": {"hasNextPage": "false"}}],
)
def test_malformed_connection_cannot_mean_exhausted(connection: object) -> None:
    with pytest.raises(ValueError):
        review_session.validate_connection(connection)


@pytest.mark.parametrize("nonfinding_seed", [False, True])
def test_family_investigation_requires_prior_genuine_escape(
    tmp_path: Path, nonfinding_seed: bool, prepared_session: dict[str, Any]
) -> None:
    events = [
        {"id": "seed", "kind": "finding", "family": "configuration"},
        {"id": "fix", "kind": "disposition", "finding_id": "seed", "disposition": "fixed"},
        {"id": "early", "kind": "investigation", "family": "configuration"},
        {"id": "recurrence", "kind": "finding", "family": "configuration"},
    ]
    if nonfinding_seed:
        events.append(
            {
                "id": "revalidated",
                "kind": "disposition",
                "finding_id": "seed",
                "disposition": "non_finding",
            }
        )
    for event in events:
        review_session.record(tmp_path, "change", event)
    assert review_session.status(tmp_path, "change")["action"] == (
        "continue" if nonfinding_seed else "investigate"
    )


def test_replay_provenance_is_not_part_of_retry_payload(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
    event = {"id": "measurement", "kind": "active_minutes", "minutes": 0}
    recorded = review_session.record(tmp_path, "change", event)
    assert review_session.record(tmp_path, "change", event) == recorded
    recorded["provenance"][0]["event_id"] = "other"
    review_session.write_state(review_session.state_path(tmp_path, "change"), recorded)
    with pytest.raises(ValueError, match="identity"):
        review_session.load(tmp_path, "change")


def test_collection_captures_epoch_before_same_head_refresh(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    review_session.initialize(tmp_path, "change", contract())
    complete_session(tmp_path)

    def refresh_during_collection(*args: object) -> dict[str, Any]:
        review_session.record(
            tmp_path,
            "change",
            {"id": "concurrent-refresh", "kind": "advance_head", "head": TEST_HEAD},
        )
        return complete_snapshot()

    monkeypatch.setattr(review_session, "gh_snapshot", refresh_during_collection)
    snapshot = review_session.collect_snapshot(
        tmp_path, "change", "nold-ai/changecost", 24, 999999999
    )
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"
    assert (
        "monitor evidence is for another input binding"
        in review_session.load(tmp_path, "change")["monitor"]["errors"]
    )


@pytest.mark.parametrize("supersedes", [[], {}, 0, False, None, ""])
def test_invalid_scope_reference_is_rejected_before_persistence(
    tmp_path: Path, supersedes: object
) -> None:
    before = review_session.initialize(tmp_path, "change", contract())
    with pytest.raises(ValueError):
        review_session.record(
            tmp_path,
            "change",
            {
                "id": "scope",
                "kind": "scope_decision",
                "decision": "approved",
                "supersedes": supersedes,
            },
        )
    assert review_session.load(tmp_path, "change") == before


def test_successful_optimistic_retry_is_idempotent(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
    event = {"id": "batch", "kind": "batch"}
    recorded = review_session.record(tmp_path, "change", event, expected_revision=0)
    assert review_session.record(tmp_path, "change", event, expected_revision=0) == recorded
    with pytest.raises(review_session.ConflictError):
        review_session.record(
            tmp_path, "change", {"id": "new", "kind": "batch"}, expected_revision=0
        )


@pytest.mark.parametrize(
    "field,entries",
    [
        ("threads", [{"id": "t", "isResolved": True, "comments": []}]),
        ("threads", [{"id": "t", "isResolved": True, "isOutdated": False, "comments": [{}]}]),
        (
            "threads",
            [
                {
                    "id": "t",
                    "isResolved": True,
                    "isOutdated": False,
                    "comments": [{"id": "c", "body": None}],
                }
            ],
        ),
        ("comments", [[{}]]),
        ("comments", [[{"id": True, "body": "comment"}]]),
        ("comments", [[{"id": 123, "body": []}]]),
    ],
)
def test_nested_evidence_requires_complete_typed_fields(
    tmp_path: Path, field: str, entries: object, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    snapshot[field] = entries
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


@pytest.mark.parametrize("login", ["reviewer-a", "other-human"])
@pytest.mark.parametrize(
    "state", ["BROKEN", "approved", "changes_requested", "", None, 1, True, []]
)
def test_unknown_review_states_cannot_erase_rejection(
    tmp_path: Path, login: str, state: object, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    snapshot["reviews"][0].extend(
        [
            {
                "id": 1330,
                "body": "",
                "commit_id": TEST_HEAD,
                "state": "CHANGES_REQUESTED",
                "user": {"login": login},
            },
            {
                "id": 1331,
                "body": "",
                "commit_id": TEST_HEAD,
                "state": state,
                "user": {"login": login},
            },
        ]
    )
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


@pytest.mark.parametrize(
    "state,action",
    [
        ("APPROVED", "complete"),
        ("COMMENTED", "complete"),
        ("CHANGES_REQUESTED", "incomplete"),
        ("DISMISSED", "wait"),
        ("PENDING", "wait"),
    ],
)
def test_documented_review_states_preserve_completion_policy(
    tmp_path: Path, state: str, action: str
) -> None:
    review_session.initialize(tmp_path, "change", contract())
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    snapshot["reviews"][0][0]["state"] = state
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == action


@pytest.mark.parametrize("login", ["reviewer-a", "other-human"])
@pytest.mark.parametrize("later", ["COMMENTED", "PENDING", "DISMISSED"])
def test_review_objection_survives_nonapproving_later_review(
    tmp_path: Path, login: str, later: str, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    snapshot["reviews"] += [
        [
            {
                "body": "",
                "id": 100,
                "commit_id": TEST_HEAD,
                "state": "CHANGES_REQUESTED",
                "user": {"login": login},
            }
        ],
        [{"body": "", "id": 101, "commit_id": TEST_HEAD, "state": later, "user": {"login": login}}],
    ]
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    acknowledge_reports(tmp_path, "explicit-review")
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"
    snapshot["reviews"][-1][0]["state"] = "APPROVED"
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "complete"


@pytest.mark.parametrize(
    "field,value",
    [
        ("requirements", None),
        ("requirements", []),
        ("requirements", [" "]),
        ("acceptance_criteria", "pass"),
        ("non_goals", False),
        ("trust_boundary", {}),
        ("trust_boundary", " "),
        ("repository", "/repo"),
        ("repository", "owner/../repo"),
        ("repository", "owner/repo\n"),
        ("required_reviewers", [" "]),
        ("required_checks", ["\t"]),
        ("required_statuses", ["context\n"]),
        ("base", None),
        ("base", "HEAD"),
        ("base", "f" * 40),
        ("head", True),
        ("intended_files", None),
        ("intended_files", {}),
        ("intended_files", {"../outside": "a" * 64}),
        ("intended_files", {".gitignore": "fake"}),
        ("intended_files", {".gitignore": "a" * 64}),
        ("intended_files", {".gitignore": "<absent>"}),
    ],
)
def test_initial_contract_requires_usable_verified_scope(
    tmp_path: Path, field: str, value: object
) -> None:
    policy = {**contract(), field: value}
    with pytest.raises(ValueError):
        review_session.initialize(tmp_path, "change", policy)
    assert not review_session.state_path(tmp_path, "change").exists()


@pytest.mark.parametrize("kind", ["dirty", "staged", "untracked", "deleted", "renamed"])
def test_initial_manifest_covers_every_changed_input(tmp_path: Path, kind: str) -> None:
    policy = contract()
    path = tmp_path / "input.txt"
    if kind == "untracked":
        (tmp_path / "new.py").write_text("new")
    elif kind == "deleted":
        path.unlink()
    elif kind == "renamed":
        path.rename(tmp_path / "renamed")
    else:
        path.write_text(".changecost/\n# change\n")
        if kind == "staged":
            subprocess.run(["git", "-C", str(tmp_path), "add", "input.txt"], check=True)
    with pytest.raises(ValueError):
        review_session.initialize(tmp_path, "change", policy)
    updated = {**policy, "intended_files": fixture_manifest()}
    review_session.initialize(tmp_path, "change", updated)


def test_initial_manifest_allows_planned_absence_and_retry_after_advance(tmp_path: Path) -> None:
    policy = contract()
    policy["intended_files"] = {**fixture_manifest(), "planned.py": "<absent>"}
    before = review_session.initialize(tmp_path, "change", policy)
    (tmp_path / "planned.py").write_text("planned")
    review_session.record(
        tmp_path, "change", {"id": "refresh", "kind": "advance_head", "head": TEST_HEAD}
    )
    after = review_session.initialize(tmp_path, "change", policy)
    assert after["contract"] == before["contract"]
    assert after["inputs"] != before["inputs"]


@pytest.mark.parametrize(
    "name",
    [".", "./input.txt", "a//b", "a/../b", "/input.txt", ".git/config", "bad\\path", "bad\npath"],
)
def test_manifest_paths_are_normalized_and_safe(tmp_path: Path, name: str) -> None:
    with pytest.raises(ValueError):
        review_session.initialize(
            tmp_path, "change", {**contract(), "intended_files": {name: "<absent>"}}
        )


def test_manifest_symlink_cannot_bind_another_file(tmp_path: Path) -> None:
    (tmp_path / "link").symlink_to(tmp_path / "input.txt")
    policy = contract()
    with pytest.raises(ValueError):
        review_session.initialize(tmp_path, "change", policy)


def test_original_rejection_dismissal_is_recomputed_from_fresh_snapshot(
    tmp_path: Path, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    rejection = {
        "body": "",
        "id": 100,
        "commit_id": TEST_HEAD,
        "state": "CHANGES_REQUESTED",
        "user": {"login": "reviewer-a"},
    }
    snapshot["reviews"] += [
        [rejection],
        [
            {
                "body": "",
                "id": 101,
                "commit_id": TEST_HEAD,
                "state": "COMMENTED",
                "user": {"login": "reviewer-a"},
            }
        ],
    ]
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    acknowledge_reports(tmp_path, "explicit-review")
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"
    rejection["state"] = "DISMISSED"
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "complete"


@pytest.mark.parametrize(
    "other_login,old_head",
    [("other-human", False), ("reviewer-a[bot]", False), ("reviewer-a", True)],
)
def test_other_identity_or_head_cannot_clear_objection(
    tmp_path: Path, other_login: str, old_head: bool, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    snapshot["reviews"] += [
        [
            {
                "id": 1512,
                "body": "",
                "commit_id": TEST_HEAD,
                "state": "CHANGES_REQUESTED",
                "user": {"login": "reviewer-a"},
            }
        ],
        [
            {
                "id": 1514,
                "body": "",
                "commit_id": "old" if old_head else TEST_HEAD,
                "state": "APPROVED",
                "user": {"login": other_login},
            }
        ],
    ]
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


@pytest.mark.parametrize("flag", ["--assume-unchanged", "--skip-worktree"])
@pytest.mark.parametrize("phase", ["init", "advance", "completion"])
def test_unsupported_index_flags_cannot_hide_inputs(tmp_path: Path, flag: str, phase: str) -> None:
    policy = contract()
    if phase != "init":
        review_session.initialize(tmp_path, "change", policy)
        complete_session(tmp_path)
    subprocess.run(["git", "-C", str(tmp_path), "update-index", flag, "input.txt"], check=True)
    before = subprocess.check_output(["git", "-C", str(tmp_path), "ls-files", "-v"])
    if phase == "completion":
        assert review_session.status(tmp_path, "change")["action"] == "incomplete"
    elif phase == "advance":
        (tmp_path / "input.txt").write_text("hidden change")
        with pytest.raises(ValueError, match="index flags"):
            review_session.record(
                tmp_path, "change", {"id": "refresh", "kind": "advance_head", "head": TEST_HEAD}
            )
    else:
        (tmp_path / "input.txt").write_text("hidden change")
        policy["intended_files"] = {".gitignore": fixture_manifest()[".gitignore"]}
        with pytest.raises(ValueError, match="index flags"):
            review_session.initialize(tmp_path, "change", policy)
    assert subprocess.check_output(["git", "-C", str(tmp_path), "ls-files", "-v"]) == before


@pytest.mark.parametrize("action", ["complete", "investigate", "replan", "incomplete"])
def test_watch_emits_unchanged_local_terminal(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    action: str,
    prepared_session: dict[str, Any],
) -> None:
    complete_session(tmp_path)
    if action != "complete":
        review_session.record(
            tmp_path, "change", {"id": "active", "kind": "phase", "phase": "active"}
        )
    if action == "replan":
        for index in range(3):
            review_session.record(tmp_path, "change", {"id": f"batch-{index}", "kind": "batch"})
    elif action == "investigate":
        for event in (
            {"id": "first", "kind": "finding", "family": "f"},
            {"id": "fixed", "kind": "disposition", "finding_id": "first", "disposition": "fixed"},
            {"id": "escape", "kind": "finding", "family": "f"},
        ):
            review_session.record(tmp_path, "change", event)
    elif action == "incomplete":
        review_session.record(
            tmp_path, "change", {"id": "scope", "kind": "scope_decision", "decision": "pending"}
        )
    monkeypatch.setattr(review_session, "gh_snapshot", lambda *args: complete_snapshot())
    assert review_session.watch(tmp_path, "change", "nold-ai/changecost", 24, 0) == int(
        action == "incomplete"
    )
    assert json.loads(capsys.readouterr().out)["action"] == action


def test_watch_deadline_rechecks_local_budget(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    prepared_session: dict[str, Any],
) -> None:
    complete_session(tmp_path)
    review_session.record(tmp_path, "change", {"id": "active", "kind": "phase", "phase": "active"})
    clock = [0.0]
    monkeypatch.setattr(review_session.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(review_session, "gh_snapshot", lambda *args: complete_snapshot())

    def sleep(seconds: float) -> None:
        clock[0] += seconds
        if clock[0] >= 60:
            for index in range(3):
                review_session.record(tmp_path, "change", {"id": f"batch-{index}", "kind": "batch"})

    monkeypatch.setattr(review_session.time, "sleep", sleep)
    assert review_session.watch(tmp_path, "change", "nold-ai/changecost", 24, 1) == 0
    assert json.loads(capsys.readouterr().out)["action"] == "replan"


@pytest.mark.parametrize("object_format", ["sha1", "sha256"])
def test_full_commit_format_survives_real_refresh(tmp_path: Path, object_format: str) -> None:
    root = tmp_path / "format-repo"
    subprocess.run(["git", "init", "-q", f"--object-format={object_format}", str(root)], check=True)
    (root / ".gitignore").write_text(".changecost/\n")
    subprocess.run(["git", "-C", str(root), "add", ".gitignore"], check=True)

    def commit(message: str) -> str:
        subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "-c",
                "user.name=Test",
                "-c",
                "user.email=test@example.com",
                "commit",
                "--allow-empty",
                "-qm",
                message,
            ],
            check=True,
        )
        return subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
        ).strip()

    first = commit("initial")
    policy = {
        **contract(),
        "head": first,
        "base": first,
        "pr_base": {"ref": "main", "sha": first},
        "intended_files": {
            ".gitignore": hashlib.sha256((root / ".gitignore").read_bytes()).hexdigest()
        },
    }
    review_session.initialize(root, "change", policy)
    review_session.record(root, "change", {"id": "batch", "kind": "batch"})
    second = commit("next")
    review_session.record(root, "change", {"id": "advance", "kind": "advance_head", "head": second})
    loaded = review_session.load(root, "change")
    assert loaded["reviewed_head"] == second
    assert loaded["batches"] == 1
    assert loaded["contract"] == policy


@pytest.mark.parametrize("value", ["short", "g" * 40, "g" * 64, "a" * 39, "a" * 65, True, None, 42])
def test_commit_identity_rule_is_shared_by_contract_and_replay(
    tmp_path: Path, value: object
) -> None:
    state = review_session.initialize(tmp_path, "change", contract())
    with pytest.raises(ValueError):
        review_session.validate_contract({**contract(), "head": value})
    event = {"id": "advance", "kind": "advance_head", "head": value}
    with pytest.raises(ValueError):
        review_session.record(tmp_path, "change", event)
    facts = {
        "event_id": "advance",
        "recorded_at": "2026-09-29T00:00:00+00:00",
        "inputs": {**state["inputs"], "head": value},
    }
    with pytest.raises(ValueError):
        review_session.replay(state["genesis"], [event], [facts], None, 0)
    assert review_session.load(tmp_path, "change") == state


@pytest.mark.parametrize("head", ["f" * 40, "f" * 64])
def test_valid_format_head_still_must_match_actual_git(tmp_path: Path, head: str) -> None:
    state = review_session.initialize(tmp_path, "change", contract())
    with pytest.raises(ValueError, match="local HEAD"):
        review_session.record(
            tmp_path, "change", {"id": "wrong", "kind": "advance_head", "head": head}
        )
    assert review_session.load(tmp_path, "change") == state


def test_changed_terminal_watch_emits_one_packet(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    prepared_session: dict[str, Any],
) -> None:
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    snapshot["checks"][0]["check_runs"][0]["started_at"] = "2100-01-01T00:00:00Z"
    monkeypatch.setattr(review_session, "gh_snapshot", lambda *args: snapshot)
    assert review_session.watch(tmp_path, "change", "nold-ai/changecost", 24, 0) == 0
    assert json.loads(capsys.readouterr().out)["packet"]["status"]["action"] == "complete"


def test_watch_timeout_preserves_incomplete_exit(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], prepared_session: dict[str, Any]
) -> None:
    review_session.record(
        tmp_path, "change", {"id": "pending", "kind": "scope_decision", "decision": "pending"}
    )
    assert review_session.watch_timeout(tmp_path, "change") == 1
    assert json.loads(capsys.readouterr().out)["action"] == "incomplete"


@pytest.mark.parametrize(
    "base", [None, {}, {"ref": "main", "sha": "short"}, {"ref": [], "sha": "a" * 40}]
)
def test_target_base_contract_rejects_malformed(tmp_path: Path, base: Any) -> None:
    policy = contract()
    policy["pr_base"] = base
    with pytest.raises(ValueError):
        review_session.initialize(tmp_path, "change", policy)


@pytest.mark.parametrize("field,value", [("ref", "release"), ("sha", "a" * 40)])
def test_same_head_target_base_drift_is_incomplete(
    tmp_path: Path, field: str, value: str, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    snapshot["pr_base"][field] = value
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


def test_base_adoption_retains_history_and_rejects_stale_local_payload(tmp_path: Path) -> None:
    original = contract()
    review_session.initialize(tmp_path, "change", original)
    complete_session(tmp_path)
    before = review_session.load(tmp_path, "change")
    old = dict(before["evidence"][0], id="cloned-old-pass")
    review_session.record(tmp_path, "change", {"id": "batch", "kind": "batch"})
    state = review_session.record(
        tmp_path,
        "change",
        {
            "id": "adopt",
            "kind": "advance_head",
            "head": TEST_HEAD,
            "comparison_base": TEST_HEAD,
            "pr_base": {"ref": "release", "sha": TEST_HEAD},
        },
    )
    assert state["contract"] == original
    assert state["batches"] == 1
    assert state["pr_base"]["ref"] == "release"
    assert state["context_since"]
    with pytest.raises(ValueError, match="binding"):
        review_session.record(tmp_path, "change", old)
    packet = review_session.packet(tmp_path, "change")
    assert packet["binding"]["pr_base"] == state["pr_base"]
    snapshot = complete_snapshot("input-generation:1")
    snapshot["pr_base"] = state["pr_base"]
    snapshot["checks"][0]["check_runs"][0].pop("started_at")
    snapshot["reviews"][0][0].pop("submitted_at")
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.load(tmp_path, "change")["monitor"]["pending"]
    snapshot["checks"][0]["check_runs"][0]["started_at"] = "2099-01-01T00:00:00Z"
    snapshot["reviews"][0][0]["submitted_at"] = "2099-01-01T00:00:00Z"
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert not review_session.load(tmp_path, "change")["monitor"]["pending"]


@pytest.mark.parametrize("field", ["ref", "sha"])
def test_collection_rechecks_target_base(monkeypatch: pytest.MonkeyPatch, field: str) -> None:
    reads = 0

    def api(endpoint: str, *, paginate: bool = False) -> Any:
        nonlocal reads
        if paginate:
            return []
        reads += 1
        base = {"ref": "main", "sha": TEST_HEAD}
        if reads == 2:
            base[field] = "release" if field == "ref" else "a" * 40
        return {"head": {"sha": TEST_HEAD}, "base": base, "requested_reviewers": []}

    monkeypatch.setattr(review_session, "gh_json", api)
    monkeypatch.setattr(review_session, "gh_review_threads", lambda *args: [])
    with pytest.raises(ValueError, match="base changed"):
        review_session.gh_snapshot("nold-ai/changecost", 24)


@pytest.mark.parametrize("field", ["comparison_base", "pr_base"])
def test_atomic_base_adoption_rejects_partial_or_unavailable(tmp_path: Path, field: str) -> None:
    before = review_session.initialize(tmp_path, "change", contract())
    event: dict[str, Any] = {
        "id": "adopt",
        "kind": "advance_head",
        "head": TEST_HEAD,
        "comparison_base": TEST_HEAD,
        "pr_base": {"ref": "main", "sha": TEST_HEAD},
    }
    del event[field]
    with pytest.raises(ValueError):
        review_session.record(tmp_path, "change", event)
    assert review_session.load(tmp_path, "change") == before


@pytest.mark.parametrize(
    "value", [None, "not-time", "2026-09-29T00:00:00", "2000-01-01T00:00:00Z", 1]
)
@pytest.mark.parametrize("lane", ["checks", "statuses", "reviews"])
def test_base_adoption_requires_fresh_positive_remote_evidence(
    tmp_path: Path, lane: str, value: Any
) -> None:
    policy = contract()
    policy["required_statuses"] = ["security"]
    review_session.initialize(tmp_path, "change", policy)
    state = review_session.record(
        tmp_path,
        "change",
        {
            "id": "adopt",
            "kind": "advance_head",
            "head": TEST_HEAD,
            "comparison_base": TEST_HEAD,
            "pr_base": {"ref": "release", "sha": TEST_HEAD},
        },
    )
    snapshot = complete_snapshot("input-generation:1")
    snapshot["pr_base"] = state["pr_base"]
    snapshot["checks"][0]["check_runs"][0]["started_at"] = state["context_since"]
    snapshot["reviews"][0][0]["submitted_at"] = state["context_since"]
    snapshot["statuses"] = [
        {
            "statuses": [
                {"context": "security", "state": "success", "created_at": state["context_since"]}
            ]
        }
    ]
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert not review_session.load(tmp_path, "change")["monitor"]["pending"]
    items = {
        "checks": (snapshot["checks"][0]["check_runs"][0], "started_at"),
        "statuses": (snapshot["statuses"][0]["statuses"][0], "created_at"),
        "reviews": (snapshot["reviews"][0][0], "submitted_at"),
    }
    item, key = items[lane]
    item[key] = value
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.load(tmp_path, "change")["monitor"]["pending"]
    snapshot["reviews"][0].append(
        {
            "id": 1840,
            "body": "",
            "commit_id": TEST_HEAD,
            "state": "CHANGES_REQUESTED",
            "user": {"login": "other"},
            "submitted_at": "2000-01-01T00:00:00Z",
        }
    )
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.load(tmp_path, "change")["monitor"]["errors"]


def test_base_adoption_replay_does_not_read_git(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    policy = contract()
    review_session.initialize(tmp_path, "change", policy)
    subprocess.run(
        [
            "git",
            "-C",
            str(tmp_path),
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.com",
            "commit",
            "--allow-empty",
            "-qm",
            "base tip",
        ],
        check=True,
    )
    tip = subprocess.check_output(
        ["git", "-C", str(tmp_path), "rev-parse", "HEAD"], text=True
    ).strip()
    state = review_session.record(
        tmp_path,
        "change",
        {
            "id": "adopt",
            "kind": "advance_head",
            "head": tip,
            "comparison_base": TEST_HEAD,
            "pr_base": {"ref": "main", "sha": tip},
        },
    )

    def no_git(*args: Any) -> Any:
        raise AssertionError("replay must not read Git")

    monkeypatch.setattr(review_session.repository, "git", no_git)
    assert review_session.load(tmp_path, "change") == state
    assert review_session.initialize(tmp_path, "change", policy) == state


@pytest.mark.parametrize("phase", ["initial", "adopt"])
@pytest.mark.parametrize("field", ["comparison", "target"])
def test_bases_require_commit_objects_not_annotated_tag_ids(
    tmp_path: Path, phase: str, field: str
) -> None:
    subprocess.run(
        [
            "git",
            "-C",
            str(tmp_path),
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.com",
            "tag",
            "-a",
            "base-tag",
            "-m",
            "annotated",
        ],
        check=True,
    )
    tag = subprocess.check_output(
        ["git", "-C", str(tmp_path), "rev-parse", "refs/tags/base-tag"], text=True
    ).strip()
    assert tag != TEST_HEAD
    policy = contract()
    if phase == "initial":
        if field == "comparison":
            policy["base"] = tag
        else:
            policy["pr_base"] = {"ref": "main", "sha": tag}
        with pytest.raises(ValueError):
            review_session.initialize(tmp_path, "change", policy)
        return
    before = review_session.initialize(tmp_path, "change", policy)
    event = {
        "id": "adopt-tag",
        "kind": "advance_head",
        "head": TEST_HEAD,
        "comparison_base": tag if field == "comparison" else TEST_HEAD,
        "pr_base": {"ref": "main", "sha": tag if field == "target" else TEST_HEAD},
    }
    with pytest.raises(ValueError):
        review_session.record(tmp_path, "change", event)
    assert review_session.load(tmp_path, "change") == before


@pytest.mark.parametrize("result", ["APPROVED", "COMMENTED"])
def test_required_rerequest_waits_and_cancellation_reuses_only_valid_evidence(
    tmp_path: Path, result: str, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    snapshot["reviews"][0][0]["state"] = result
    snapshot["requested_reviewers"] = [{"login": "reviewer-a"}]
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "wait"
    snapshot["requested_reviewers"] = []
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "complete"
    snapshot["reviews"] = [[]]
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "wait"


@pytest.mark.parametrize(
    "value",
    [None, {}, "reviewer-a", [None], [{}], [{"login": 7}], [{"login": ""}], [{"login": "a b"}]],
)
def test_malformed_requested_users_invalidate_green(
    tmp_path: Path, value: Any, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    snapshot["requested_reviewers"] = value
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


def test_missing_requested_users_invalidate_green(
    tmp_path: Path, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    del snapshot["requested_reviewers"]
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


@pytest.mark.parametrize("first,last", [([], ["reviewer-a"]), (["reviewer-a"], [])])
def test_request_changes_during_collection_fail_closed(
    monkeypatch: pytest.MonkeyPatch, first: list[str], last: list[str]
) -> None:
    users = iter((first, last))

    def api(endpoint: str, *, paginate: bool = False) -> Any:
        if paginate:
            return []
        return {
            "head": {"sha": TEST_HEAD},
            "base": {"ref": "main", "sha": TEST_HEAD},
            "requested_reviewers": [{"login": login} for login in next(users)],
        }

    monkeypatch.setattr(review_session, "gh_json", api)
    monkeypatch.setattr(review_session, "gh_review_threads", lambda *args: [])
    with pytest.raises(ValueError, match="request"):
        review_session.gh_snapshot("nold-ai/changecost", 24)


def test_request_identity_normalization_is_semantic_and_bot_exact(
    tmp_path: Path, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    snapshot["requested_reviewers"] = [{"login": "reviewer-a[bot]"}, {"login": "other"}]
    assert review_session.record_monitor_snapshot(tmp_path, "change", snapshot)["changed"]
    assert review_session.status(tmp_path, "change")["action"] == "complete"
    snapshot["requested_reviewers"] = [
        {"login": "other", "avatar_url": "changed"},
        {"login": "reviewer-a[bot]"},
        {"login": "other"},
    ]
    assert not review_session.record_monitor_snapshot(tmp_path, "change", snapshot)["changed"]
    snapshot["requested_reviewers"].append({"login": "reviewer-a"})
    assert review_session.record_monitor_snapshot(tmp_path, "change", snapshot)["changed"]
    assert review_session.status(tmp_path, "change")["action"] == "wait"


@pytest.mark.parametrize("blocking", ["rejection", "old-head", "exhausted"])
def test_request_cancellation_cannot_override_existing_blocks(
    tmp_path: Path, blocking: str, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    if blocking == "rejection":
        snapshot["reviews"][0][0]["state"] = "CHANGES_REQUESTED"
    elif blocking == "old-head":
        snapshot["reviews"][0][0]["commit_id"] = "a" * 40
    else:
        review_session.record(
            tmp_path, "change", {"id": "over", "kind": "active_minutes", "minutes": 91}
        )
    snapshot["requested_reviewers"] = [{"login": "reviewer-a"}]
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    snapshot["requested_reviewers"] = []
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] != "complete"


def test_request_order_during_collection_is_not_drift(monkeypatch: pytest.MonkeyPatch) -> None:
    users = iter(
        (
            [{"login": "a"}, {"login": "b"}],
            [{"login": "b", "avatar_url": "changed"}, {"login": "a"}],
        )
        * 2
    )

    def api(endpoint: str, *, paginate: bool = False) -> Any:
        if paginate:
            return []
        return {
            "head": {"sha": TEST_HEAD},
            "base": {"ref": "main", "sha": TEST_HEAD},
            "requested_reviewers": next(users),
        }

    monkeypatch.setattr(review_session, "gh_json", api)
    monkeypatch.setattr(review_session, "gh_review_threads", lambda *args: [])
    assert review_session.gh_snapshot("nold-ai/changecost", 24)["head"] == TEST_HEAD


@pytest.mark.parametrize("identity", ["genesis", "bind-pr", "0", "input-generation:0"])
def test_refresh_epoch_is_independent_of_caller_identity(tmp_path: Path, identity: str) -> None:
    state = review_session.initialize(tmp_path, "change", contract())
    initial_epoch = review_session.binding_epoch(state)
    snapshot = {**complete_snapshot(), "_input_epoch": initial_epoch}
    event = {"id": identity, "kind": "advance_head", "head": TEST_HEAD}
    refreshed = review_session.record(tmp_path, "change", event)
    assert review_session.binding_epoch(refreshed) == "input-generation:1"
    assert review_session.binding_epoch(refreshed) != initial_epoch
    assert review_session.record(tmp_path, "change", event) == refreshed
    with pytest.raises(ValueError, match="binding"):
        review_session.record(
            tmp_path,
            "change",
            {
                "id": "stale-proof",
                "kind": "evidence",
                "evidence_type": "gate",
                "head": TEST_HEAD,
                "result": "pass",
                "binding": review_session.evidence_binding(state),
            },
        )
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.load(tmp_path, "change")["monitor"]["errors"]
    second = review_session.record(
        tmp_path, "change", {"id": "next", "kind": "advance_head", "head": TEST_HEAD}
    )
    assert review_session.binding_epoch(second) == "input-generation:2"
    assert second["events"][0]["id"] == identity


def test_auto_bind_selects_unused_identity_and_retains_scope_ids(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
    for identity in ("bind-pr", "bind-pr:1", "bind-pr:2"):
        review_session.record(
            tmp_path, "change", {"id": identity, "kind": "scope_decision", "decision": "pending"}
        )
    review_session.select_target(tmp_path, "change", "nold-ai/changecost", 24)
    state = review_session.load(tmp_path, "change")
    assert state["events"][-1]["id"] == "bind-pr:3"
    assert [item["id"] for item in state["scope_decisions"]] == [
        "bind-pr",
        "bind-pr:1",
        "bind-pr:2",
    ]
    review_session.select_target(tmp_path, "change", "nold-ai/changecost", 24)
    assert review_session.load(tmp_path, "change") == state
    with pytest.raises(ValueError):
        review_session.select_target(tmp_path, "change", "nold-ai/changecost", 25)


@pytest.mark.parametrize("targets", [(24, 24), (24, 25)])
def test_concurrent_auto_bind_targets_are_atomic(tmp_path: Path, targets: tuple[int, int]) -> None:
    review_session.initialize(tmp_path, "change", contract())
    barrier = Barrier(2)

    def bind(target: int) -> str:
        barrier.wait(timeout=5)
        try:
            review_session.select_target(tmp_path, "change", "nold-ai/changecost", target)
        except ValueError:
            return "conflict"
        return "bound"

    with ThreadPoolExecutor(max_workers=2) as workers:
        outcomes = list(workers.map(bind, targets))
    state = review_session.load(tmp_path, "change")
    assert len(state["events"]) == 1
    assert outcomes.count("bound") == (2 if targets[0] == targets[1] else 1)
    assert state["pull_request"] in targets


def test_concurrent_caller_and_generated_bind_identity_do_not_overwrite(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
    barrier = Barrier(2)

    def write(kind: str) -> str:
        barrier.wait(timeout=5)
        if kind == "auto":
            review_session.select_target(tmp_path, "change", "nold-ai/changecost", 24)
            return "bound"
        try:
            review_session.record(
                tmp_path,
                "change",
                {"id": "bind-pr", "kind": "scope_decision", "decision": "pending"},
            )
        except review_session.ConflictError:
            return "conflict"
        return "recorded"

    with ThreadPoolExecutor(max_workers=2) as workers:
        outcomes = list(workers.map(write, ("auto", "caller")))
    state = review_session.load(tmp_path, "change")
    assert state["pull_request"] == 24
    assert outcomes[0] == "bound"
    assert len({event["id"] for event in state["events"]}) == len(state["events"])
    assert bool(state["scope_decisions"]) == (outcomes[1] == "recorded")


@pytest.mark.parametrize("epoch", [0, 0.0, False, "genesis", "0"])
def test_epoch_aliases_cannot_reuse_monitor_or_local_results(tmp_path: Path, epoch: Any) -> None:
    state = review_session.initialize(tmp_path, "change", contract())
    review_session.record_monitor_snapshot(
        tmp_path, "change", {**complete_snapshot(), "_input_epoch": epoch}
    )
    assert review_session.load(tmp_path, "change")["monitor"]["errors"]
    binding = review_session.evidence_binding(state)
    binding["epoch"] = epoch
    with pytest.raises(ValueError, match="binding"):
        review_session.record(
            tmp_path,
            "change",
            {
                "id": "proof",
                "kind": "evidence",
                "evidence_type": "gate",
                "head": TEST_HEAD,
                "result": "pass",
                "binding": binding,
            },
        )


def test_ordinary_events_and_monitor_updates_do_not_advance_epoch(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
    complete_session(tmp_path)
    state = review_session.load(tmp_path, "change")
    assert review_session.binding_epoch(state) == "input-generation:0"
    event = {"id": "input-generation:99", "kind": "batch"}
    review_session.record(tmp_path, "change", event)
    state = review_session.record(tmp_path, "change", event)
    assert state["batches"] == 1
    assert review_session.binding_epoch(state) == "input-generation:0"


@pytest.mark.parametrize("blank", [" ", "\t", "\n", "\u00a0", "\u2003"])
@pytest.mark.parametrize("field", ["id", "approved_by", "family", "supersedes"])
def test_event_semantic_strings_reject_whitespace_without_mutating_state(
    tmp_path: Path, blank: str, field: str, prepared_session: dict[str, Any]
) -> None:
    before = review_session.record(
        tmp_path, "change", {"id": "spent", "kind": "active_minutes", "minutes": 90}
    )
    events = {
        "id": {"id": blank, "kind": "batch"},
        "approved_by": {
            "id": "extension",
            "kind": "extension",
            "approved_by": blank,
            "minutes": 90,
        },
        "family": {"id": "finding", "kind": "finding", "family": blank},
        "supersedes": {
            "id": "resolution",
            "kind": "scope_decision",
            "decision": "approved",
            "supersedes": blank,
        },
    }
    with pytest.raises(ValueError):
        review_session.record(tmp_path, "change", events[field])
    assert review_session.load(tmp_path, "change") == before


@pytest.mark.parametrize("pending_first", [False, True])
def test_packet_uses_one_receipt_revision(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    pending_first: bool,
    prepared_session: dict[str, Any],
) -> None:
    complete_session(tmp_path)
    complete = review_session.load(tmp_path, "change")
    review_session.record(
        tmp_path, "change", {"id": "scope", "kind": "scope_decision", "decision": "pending"}
    )
    pending = review_session.load(tmp_path, "change")
    first, second = (pending, complete) if pending_first else (complete, pending)
    calls = 0

    def changing_load(*args: Any) -> Any:
        nonlocal calls
        calls += 1
        return first if calls == 1 else second

    monkeypatch.setattr(review_session, "load", changing_load)
    result = review_session.packet(tmp_path, "change")
    assert calls == 1
    assert result["status"]["revision"] == first["revision"]
    assert bool(result["scope_decisions"]) == pending_first
    assert result["status"]["action"] == ("incomplete" if pending_first else "complete")


@pytest.mark.parametrize("action", ["complete", "incomplete"])
def test_changed_watch_exit_and_snapshot_match_packet(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], action: str
) -> None:
    opposite = "incomplete" if action == "complete" else "complete"
    handoff = {"status": {"action": action}, "monitor": {"data": {"source": "same revision"}}}
    monkeypatch.setattr(review_session, "collect_snapshot", lambda *args: {"source": "superseded"})
    monkeypatch.setattr(review_session, "record_monitor_snapshot", lambda *args: {"changed": True})
    monkeypatch.setattr(review_session, "status", lambda *args: {"action": opposite})
    monkeypatch.setattr(review_session, "packet", lambda *args: handoff)
    result = review_session.watch(tmp_path, "change", "nold-ai/changecost", 24, 0)
    output = json.loads(capsys.readouterr().out)
    assert result == int(action == "incomplete")
    assert output["packet"] == handoff
    assert output["snapshot"] == handoff["monitor"]["data"]


def test_valid_padded_event_references_remain_exact(
    tmp_path: Path, prepared_session: dict[str, Any]
) -> None:
    finding = {"id": " finding id ", "kind": "finding", "family": " family label "}
    first = review_session.record(tmp_path, "change", finding)
    assert review_session.record(tmp_path, "change", finding) == first
    review_session.record(
        tmp_path,
        "change",
        {"id": "fix", "kind": "disposition", "finding_id": finding["id"], "disposition": "fixed"},
    )
    review_session.record(
        tmp_path, "change", {"id": " scope id ", "kind": "scope_decision", "decision": "pending"}
    )
    state = review_session.record(
        tmp_path,
        "change",
        {
            "id": "resolution",
            "kind": "scope_decision",
            "decision": "approved",
            "supersedes": " scope id ",
        },
    )
    assert state["findings"][0]["id"] == finding["id"]
    assert state["findings"][0]["family"] == finding["family"]
    assert not review_session.scope_pending(state)
    assert state["findings"][0]["disposition"] == "fixed"


@pytest.mark.parametrize(
    "field", ["id", "approved_by", "family", "finding_id", "supersedes", "kind"]
)
def test_persisted_blank_semantic_event_requires_recovery(tmp_path: Path, field: str) -> None:
    state = review_session.initialize(tmp_path, "change", contract())
    events = {
        "id": {"id": " ", "kind": "batch"},
        "approved_by": {
            "id": "extend",
            "kind": "extension",
            "approved_by": "\u00a0",
            "minutes": 90,
        },
        "family": {"id": "finding", "kind": "finding", "family": "\t"},
        "finding_id": {
            "id": "fix",
            "kind": "disposition",
            "finding_id": " ",
            "disposition": "fixed",
        },
        "supersedes": {
            "id": "resolve",
            "kind": "scope_decision",
            "decision": "approved",
            "supersedes": " ",
        },
        "kind": {"id": "event", "kind": " "},
    }
    event = events[field]
    state["events"].append(event)
    state["provenance"].append({"event_id": event["id"], "recorded_at": "2026-09-29T00:00:00Z"})
    review_session.write_state(review_session.state_path(tmp_path, "change"), state)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


def test_packet_retains_real_input_drift_validation(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
    complete_session(tmp_path)
    (tmp_path / "input.txt").write_text("unreviewed edit\n")
    packet = review_session.packet(tmp_path, "change")
    assert packet["status"]["action"] == "incomplete"
    assert "inputs changed" in packet["status"]["reason"]


@pytest.mark.parametrize("axis,values", [("batches", (2, 3, 4)), ("minutes", (89, 90, 91))])
@pytest.mark.parametrize("disposition", ["fixed", "accepted_exception"])
def test_exhausted_budget_overrides_remaining_family_investigation(
    tmp_path: Path,
    axis: str,
    values: tuple[int, int, int],
    disposition: str,
    prepared_session: dict[str, Any],
) -> None:
    for event in [
        {"id": "f1", "kind": "finding", "family": "inputs"},
        {"id": "fix1", "kind": "disposition", "finding_id": "f1", "disposition": "fixed"},
        {"id": "b1", "kind": "batch"},
        {"id": "f2", "kind": "finding", "family": "inputs"},
        {"id": "fix2", "kind": "disposition", "finding_id": "f2", "disposition": disposition},
    ]:
        review_session.record(tmp_path, "change", event)
    complete_session(tmp_path)
    state = review_session.load(tmp_path, "change")
    for value in values:
        state["batches" if axis == "batches" else "active_minutes"] = value
        expected = "investigate" if value == values[0] else "replan"
        assert review_session.decision(state)[0] == expected


def test_remote_resolved_thread_does_not_create_local_adjudication(
    tmp_path: Path, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    snapshot["threads"] = [
        {
            "id": "thread-a",
            "isResolved": True,
            "isOutdated": False,
            "comments": [{"id": "comment-a", "body": "actionable concern"}],
        }
    ]
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


def acknowledge_reports(tmp_path: Path, identity: str) -> dict[str, Any]:
    state = review_session.load(tmp_path, "change")
    event = {
        "id": identity,
        "kind": "evidence",
        "evidence_type": "reviewer",
        "head": TEST_HEAD,
        "result": "pass",
        "binding": review_session.evidence_binding(state),
        "reviewed_reports": review_session.report_receipts(state["monitor"]["data"]),
    }
    review_session.record(tmp_path, "change", event)
    return event


def reviewed_thread_snapshot() -> dict[str, Any]:
    snapshot = complete_snapshot()
    snapshot["threads"] = [
        {
            "id": "thread-a",
            "isResolved": True,
            "isOutdated": False,
            "comments": [{"id": "comment-a", "body": "review this"}],
        }
    ]
    return snapshot


@pytest.mark.parametrize("change", ["edit", "add-comment", "add-thread", "extra-coverage"])
def test_changed_report_content_requires_explicit_revalidation(
    tmp_path: Path, change: str, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    snapshot = reviewed_thread_snapshot()
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    event = acknowledge_reports(tmp_path, "reviewed")
    assert review_session.record(tmp_path, "change", event) == review_session.load(
        tmp_path, "change"
    )
    assert review_session.status(tmp_path, "change")["action"] == "complete"
    if change == "edit":
        snapshot["threads"][0]["comments"][0]["body"] = "changed concern"
    elif change == "add-comment":
        snapshot["threads"][0]["comments"].append({"id": "comment-b", "body": "another concern"})
    elif change == "add-thread":
        snapshot["threads"].append(
            {
                "id": "thread-b",
                "isResolved": True,
                "isOutdated": True,
                "comments": [{"id": "comment-b", "body": "human concern"}],
            }
        )
    else:
        event = {
            **event,
            "id": "extra",
            "reviewed_reports": {**event["reviewed_reports"], "thread:stale": "a" * 64},
        }
        review_session.record(tmp_path, "change", event)
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"
    acknowledge_reports(tmp_path, "revalidated")
    assert review_session.status(tmp_path, "change")["action"] == "complete"


def test_thread_adjudication_does_not_override_unresolved_or_local_findings(
    tmp_path: Path, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    snapshot = reviewed_thread_snapshot()
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    acknowledge_reports(tmp_path, "reviewed")
    receipts = review_session.packet(tmp_path, "change")["report_receipts"]
    snapshot["threads"][0].update(isResolved=False, isOutdated=True)
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "wait"
    assert review_session.packet(tmp_path, "change")["report_receipts"] == receipts
    snapshot["threads"][0]["isResolved"] = True
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "complete"
    review_session.record(
        tmp_path, "change", {"id": "local-defect", "kind": "finding", "family": "inputs"}
    )
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


@pytest.mark.parametrize(
    "coverage", [None, [], {"": "a" * 64}, {"thread": "short"}, {"thread": True}]
)
def test_malformed_thread_coverage_rejected_at_ingestion_and_replay(
    tmp_path: Path, coverage: Any
) -> None:
    state = review_session.initialize(tmp_path, "change", contract())
    event = {
        "id": "review",
        "kind": "evidence",
        "evidence_type": "reviewer",
        "head": TEST_HEAD,
        "result": "pass",
        "binding": review_session.evidence_binding(state),
        "reviewed_reports": coverage,
    }
    with pytest.raises(ValueError):
        review_session.record(tmp_path, "change", event)
    with pytest.raises(ValueError):
        review_session.replay(
            state["genesis"],
            [event],
            [{"event_id": "review", "recorded_at": "2026-09-29T00:00:00Z"}],
            None,
            0,
        )


@pytest.mark.parametrize(
    "thread", [{}, {"id": "t", "isResolved": True, "isOutdated": False, "comments": [{}]}]
)
def test_malformed_report_has_no_usable_receipt(
    tmp_path: Path, thread: Any, prepared_session: dict[str, Any]
) -> None:
    snapshot = complete_snapshot()
    snapshot["threads"] = [thread]
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    packet = review_session.packet(tmp_path, "change")
    assert packet["report_receipts"] is None
    assert packet["status"]["action"] == "incomplete"


@pytest.mark.parametrize("extension", ["batches", "minutes", "both"])
def test_family_budget_extension_must_cover_each_exhausted_axis(
    tmp_path: Path,
    extension: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    prepared_session: dict[str, Any],
) -> None:
    for event in [
        {"id": "f1", "kind": "finding", "family": "inputs"},
        {"id": "fix1", "kind": "disposition", "finding_id": "f1", "disposition": "fixed"},
        {"id": "b1", "kind": "batch"},
        {"id": "f2", "kind": "finding", "family": "inputs"},
        {"id": "fix2", "kind": "disposition", "finding_id": "f2", "disposition": "fixed"},
    ]:
        review_session.record(tmp_path, "change", event)
    complete_session(tmp_path)
    for n in (2, 3):
        review_session.record(tmp_path, "change", {"id": f"b{n}", "kind": "batch"})
    review_session.record(
        tmp_path, "change", {"id": "elapsed", "kind": "active_minutes", "minutes": 90}
    )
    assert review_session.packet(tmp_path, "change")["status"]["action"] == "replan"
    review_session.record(
        tmp_path,
        "change",
        {
            "id": "extension",
            "kind": "extension",
            "approved_by": "maintainer",
            "batches": 1 if extension in {"batches", "both"} else 0,
            "minutes": 1 if extension in {"minutes", "both"} else 0,
        },
    )
    assert review_session.status(tmp_path, "change")["action"] == (
        "investigate" if extension == "both" else "replan"
    )
    monkeypatch.setattr(review_session, "gh_snapshot", lambda *args: complete_snapshot())
    assert review_session.watch(tmp_path, "change", "nold-ai/changecost", 24, 0) == 0
    output = json.loads(capsys.readouterr().out)
    action = output.get("packet", {"status": output})["status"]["action"]
    assert action == ("investigate" if extension == "both" else "replan")


@pytest.mark.parametrize("refresh", ["input", "base"])
def test_thread_coverage_cannot_transfer_to_new_binding(tmp_path: Path, refresh: str) -> None:
    review_session.initialize(tmp_path, "change", contract())
    complete_session(tmp_path)
    review_session.record_monitor_snapshot(tmp_path, "change", reviewed_thread_snapshot())
    old = acknowledge_reports(tmp_path, "reviewed")
    event: dict[str, Any] = {"id": "refresh", "kind": "advance_head", "head": TEST_HEAD}
    if refresh == "base":
        event.update(comparison_base=TEST_HEAD, pr_base={"ref": "release", "sha": TEST_HEAD})
    review_session.record(tmp_path, "change", event)
    with pytest.raises(ValueError, match="binding"):
        review_session.record(tmp_path, "change", {**old, "id": "old-report-new-id"})


@pytest.mark.parametrize("axis,values", [("batches", (2, 3, 4)), ("active_minutes", (89, 90, 91))])
@pytest.mark.parametrize("phase", ["complete", "active", "paused"])
def test_satisfied_completion_exception_is_exactly_bounded(
    tmp_path: Path,
    axis: str,
    values: tuple[int, int, int],
    phase: str,
    prepared_session: dict[str, Any],
) -> None:
    complete_session(tmp_path)
    state = review_session.load(tmp_path, "change")
    state["phase"] = phase
    for index, value in enumerate(values):
        state[axis] = value
        if phase == "complete":
            expected = "complete" if index < 2 else "replan"
        else:
            expected = ("continue" if phase == "active" else "wait") if index == 0 else "replan"
        assert review_session.decision(state)[0] == expected


def test_thread_receipt_digest_is_order_independent_and_complete() -> None:
    snapshot = reviewed_thread_snapshot()
    snapshot["threads"][0]["comments"].append({"id": "second-page-comment", "body": "later page"})
    receipt = review_session.report_receipts(snapshot)
    snapshot["threads"][0]["comments"].reverse()
    assert review_session.report_receipts(snapshot) == receipt
    snapshot["threads"][0]["comments"][0]["body"] = "edited later page"
    assert review_session.report_receipts(snapshot) != receipt


@pytest.mark.parametrize("refresh", [False, True])
@pytest.mark.parametrize("epoch", ["missing", None, False, 0, 0.0, [], "", "old-generation"])
def test_missing_or_invalid_observation_epoch_replaces_green(
    tmp_path: Path, refresh: bool, epoch: Any, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    if refresh:
        review_session.record(
            tmp_path, "change", {"id": "refresh", "kind": "advance_head", "head": TEST_HEAD}
        )
    snapshot = complete_snapshot()
    if epoch == "missing":
        snapshot.pop("_input_epoch", None)
    else:
        snapshot["_input_epoch"] = epoch
    assert review_session.record_monitor_snapshot(tmp_path, "change", snapshot)["changed"]
    state = review_session.load(tmp_path, "change")
    assert state["monitor"]["errors"]
    packet = review_session.packet(tmp_path, "change")
    assert packet["status"]["action"] == "incomplete"
    assert packet["report_receipts"] is None
    assert not review_session.record_monitor_snapshot(tmp_path, "change", snapshot)["changed"]
    assert review_session.load(tmp_path, "change") == state


@pytest.mark.parametrize("generation", [0, 1, 2])
def test_explicit_current_epoch_is_accepted_and_prior_epoch_stays_stale(
    tmp_path: Path, generation: int
) -> None:
    review_session.initialize(tmp_path, "change", contract())
    for index in range(generation):
        event = {"id": f"refresh-{index}", "kind": "advance_head", "head": TEST_HEAD}
        first = review_session.record(tmp_path, "change", event)
        assert review_session.record(tmp_path, "change", event) == first
    snapshot = complete_snapshot(f"input-generation:{generation}")
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    state = review_session.load(tmp_path, "change")
    assert not state["monitor"]["errors"]
    assert review_session.packet(tmp_path, "change")[
        "report_receipts"
    ] == review_session.report_receipts(snapshot)
    snapshot["_input_epoch"] = f"input-generation:{generation - 1}"
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"
    assert review_session.packet(tmp_path, "change")["report_receipts"] is None


def test_collection_error_without_epoch_replaces_prior_green(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)

    def unavailable(*args: Any) -> Any:
        raise RuntimeError("API unavailable")

    monkeypatch.setattr(review_session, "gh_snapshot", unavailable)
    observation = review_session.collect_snapshot(tmp_path, "change", "nold-ai/changecost", 24, 60)
    assert "_input_epoch" not in observation
    review_session.record_monitor_snapshot(tmp_path, "change", observation)
    state = review_session.load(tmp_path, "change")
    assert "API unavailable" in state["monitor"]["errors"]
    assert review_session.packet(tmp_path, "change")["status"]["action"] == "incomplete"
    assert review_session.packet(tmp_path, "change")["report_receipts"] is None


@pytest.mark.parametrize("count,minutes,expected", [(3, 0.1, 90.3), (5, 0.2, 91.0)])
def test_fractional_budget_and_elapsed_time_share_exact_boundary(
    tmp_path: Path, count: int, minutes: float, expected: float, prepared_session: dict[str, Any]
) -> None:
    review_session.record(
        tmp_path, "change", {"id": "base-time", "kind": "active_minutes", "minutes": 90}
    )
    for index in range(count):
        review_session.record(
            tmp_path,
            "change",
            {
                "id": f"grant-{index}",
                "kind": "extension",
                "approved_by": "maintainer",
                "minutes": minutes,
            },
        )
        review_session.record(
            tmp_path,
            "change",
            {"id": f"time-{index}", "kind": "active_minutes", "minutes": minutes},
        )
    complete_session(tmp_path)
    state = review_session.load(tmp_path, "change")
    assert state["budget"]["minutes"] == state["active_minutes"] == expected
    assert review_session.status(tmp_path, "change")["action"] == "complete"
    review_session.record(
        tmp_path, "change", {"id": "continue", "kind": "phase", "phase": "active"}
    )
    assert review_session.status(tmp_path, "change")["action"] == "replan"


@pytest.mark.parametrize(
    "kind,key",
    [
        ("extension", "minutes"),
        ("active_minutes", "minutes"),
        ("usage", "cost"),
        ("usage", "cached_input"),
    ],
)
def test_aggregate_overflow_rejects_atomically_and_replay_fails_closed(
    tmp_path: Path, kind: str, key: str
) -> None:
    review_session.initialize(tmp_path, "change", contract())
    first = {"id": "first", "kind": kind, key: 1e308}
    if kind == "extension":
        first["approved_by"] = "maintainer"
    state = review_session.record(tmp_path, "change", first)
    path = review_session.state_path(tmp_path, "change")
    original = path.read_bytes()
    second = {**first, "id": "second"}
    with pytest.raises(ValueError):
        review_session.record(tmp_path, "change", second)
    assert path.read_bytes() == original
    assert review_session.load(tmp_path, "change") == state
    state["events"].append(second)
    state["provenance"].append({"event_id": "second", "recorded_at": "2026-09-29T00:00:00Z"})
    review_session.write_state(path, state)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


@pytest.mark.parametrize("key", ["cached_input", "uncached_input", "output", "cost"])
def test_usage_components_remain_canonical_across_retries_and_reload(
    tmp_path: Path, key: str, prepared_session: dict[str, Any]
) -> None:
    for index in range(3):
        event = {"id": f"usage-{index}", "kind": "usage", key: 0.1}
        before = review_session.load(tmp_path, "change")["revision"]
        state = review_session.record(tmp_path, "change", event, expected_revision=before)
        assert review_session.record(tmp_path, "change", event, expected_revision=before) == state
        review_session.record(
            tmp_path, "change", {"id": f"phase-{index}", "kind": "phase", "phase": "active"}
        )
    usage = review_session.load(tmp_path, "change")["usage"]
    assert usage[key] == 0.30000000000000004
    assert all(value is None for name, value in usage.items() if name != key)


def test_canonical_extensions_retain_integer_batches_and_original_retry(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
    for index in range(3):
        event = {
            "id": f"extension-{index}",
            "kind": "extension",
            "approved_by": "maintainer",
            "minutes": 0.1,
            "batches": 1,
        }
        before = review_session.load(tmp_path, "change")["revision"]
        state = review_session.record(tmp_path, "change", event, expected_revision=before)
        assert review_session.record(tmp_path, "change", event, expected_revision=before) == state
        review_session.record(
            tmp_path, "change", {"id": f"usage-{index}", "kind": "usage", "cost": 0}
        )
    state = review_session.load(tmp_path, "change")
    assert state["budget"] == {"batches": 6, "minutes": 90.3}
    assert type(state["budget"]["batches"]) is int
    assert len(state["events"]) == 6


@pytest.mark.parametrize("components", [[float("inf")], [float("nan")], [1e308, 1e308]])
def test_finite_sum_rejects_nonfinite_aggregates(components: list[float]) -> None:
    with pytest.raises(ValueError):
        review_session.finite_sum(components)


@pytest.mark.parametrize("phase", ["active", "paused", "complete"])
def test_fractional_budget_decisions_survive_refresh_and_zero_grants(
    tmp_path: Path, phase: str
) -> None:
    review_session.initialize(tmp_path, "change", contract())
    for index in range(5):
        review_session.record(
            tmp_path,
            "change",
            {
                "id": f"grant-{index}",
                "kind": "extension",
                "minutes": 0.2,
                "approved_by": "maintainer",
            },
        )
    for event in [
        {"id": "zero", "kind": "extension", "minutes": 0, "approved_by": "maintainer"},
        {"id": "batch-only", "kind": "extension", "batches": 1, "approved_by": "maintainer"},
        {"id": "refresh", "kind": "advance_head", "head": TEST_HEAD},
    ]:
        review_session.record(tmp_path, "change", event)
    review_session.record_monitor_snapshot(
        tmp_path, "change", complete_snapshot("input-generation:1")
    )
    complete_session(tmp_path)
    # Restore the explicit current monitor after the initial-generation helper.
    review_session.record_monitor_snapshot(
        tmp_path, "change", complete_snapshot("input-generation:1")
    )
    state = review_session.load(tmp_path, "change")
    assert state["budget"] == {"batches": 4, "minutes": 91.0}
    state["phase"] = phase
    for minutes in [90.9, 91.0, 91.1]:
        state["active_minutes"] = minutes
        action = review_session.decision(state)[0]
        if phase == "complete":
            assert action == ("complete" if minutes <= 91 else "replan")
        elif minutes >= 91:
            assert action == "replan"
        else:
            assert action in {"continue", "wait"}


@pytest.mark.parametrize(
    "kind,key",
    [
        ("active_minutes", "minutes"),
        ("extension", "minutes"),
        ("usage", "cached_input"),
        ("usage", "uncached_input"),
        ("usage", "output"),
        ("usage", "cost"),
    ],
)
@pytest.mark.parametrize("sign", [1, -1])
def test_oversized_measurements_reject_atomically_and_recover(
    tmp_path: Path, kind: str, key: str, sign: int, prepared_session: dict[str, Any]
) -> None:
    event = {"id": "large", "kind": kind, key: sign * 10**1000, "approved_by": "maintainer"}
    path = review_session.state_path(tmp_path, "change")
    original = path.read_bytes()
    with pytest.raises(ValueError):
        review_session.record(tmp_path, "change", event)
    assert path.read_bytes() == original
    state = review_session.load(tmp_path, "change")
    state["events"].append(event)
    state["provenance"].append({"event_id": "large", "recorded_at": "2026-09-29T00:00:00Z"})
    review_session.write_state(path, state)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


def test_large_integer_batches_remain_exact_through_replay(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
    event = {"id": "large", "kind": "extension", "batches": 10**1000, "approved_by": "maintainer"}
    state = review_session.record(tmp_path, "change", event)
    assert state["budget"]["batches"] == 3 + 10**1000
    assert review_session.load(tmp_path, "change") == state
    assert review_session.record(tmp_path, "change", event) == state
    with pytest.raises(ValueError):
        review_session.record(
            tmp_path, "change", {**event, "id": "negative", "batches": -(10**1000)}
        )
    with pytest.raises(review_session.ConflictError):
        review_session.record(
            tmp_path, "change", {"id": "next", "kind": "batch"}, expected_revision=10**1000
        )


@pytest.mark.parametrize("value", [10**1000, -(10**1000), True, 1.5])
def test_numeric_pr_identity_mismatch_invalidates_prior_green(
    tmp_path: Path, value: Any, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    snapshot["pull_request"] = value
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"
    assert review_session.packet(tmp_path, "change")["report_receipts"] is None


@pytest.mark.parametrize("value", [10**1000, -(10**1000), True, 1.5])
def test_numeric_observation_revision_retains_integer_contract(
    tmp_path: Path, value: Any, prepared_session: dict[str, Any]
) -> None:
    state = review_session.load(tmp_path, "change")
    state["observation_revision"] = value
    state["revision"] = value
    review_session.write_state(review_session.state_path(tmp_path, "change"), state)
    if type(value) is int and value >= 0:
        assert review_session.load(tmp_path, "change")["revision"] == value
    else:
        assert review_session.status(tmp_path, "change")["action"] == "incomplete"


def test_oversized_measurement_cli_is_structured_incomplete(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    prepared_session: dict[str, Any],
) -> None:
    event_path = tmp_path / ".changecost" / "oversized.json"
    event_path.write_text(
        json.dumps({"id": "large", "kind": "active_minutes", "minutes": 10**1000})
    )
    monkeypatch.setattr(
        "sys.argv",
        ["review-session", "record", "change", "--root", str(tmp_path), "--json", str(event_path)],
    )
    assert review_session.main() == 1
    assert json.loads(capsys.readouterr().out)["action"] == "incomplete"


@pytest.mark.parametrize("mode", ["untracked", "staged", "committed"])
def test_advance_rejects_undeclared_path_atomically(tmp_path: Path, mode: str) -> None:
    review_session.initialize(tmp_path, "change", contract())
    (tmp_path / "outside.txt").write_text("new scope\n")
    if mode != "untracked":
        subprocess.run(["git", "-C", str(tmp_path), "add", "outside.txt"], check=True)
    if mode == "committed":
        subprocess.run(
            [
                "git",
                "-C",
                str(tmp_path),
                "-c",
                "user.name=Test",
                "-c",
                "user.email=test@example.com",
                "commit",
                "-qm",
                "outside",
            ],
            check=True,
        )
    head = review_session.repository.git(tmp_path, "rev-parse", "HEAD").decode().strip()
    path = review_session.state_path(tmp_path, "change")
    original = path.read_bytes()
    with pytest.raises(ValueError):
        review_session.record(
            tmp_path, "change", {"id": "refresh", "kind": "advance_head", "head": head}
        )
    assert path.read_bytes() == original


def test_explicit_scope_approval_recaptures_planned_absent_file(tmp_path: Path) -> None:
    original = contract()
    review_session.initialize(tmp_path, "change", original)
    assert isinstance(original["intended_files"], dict)
    manifest = {**original["intended_files"], "outside.txt": "<absent>"}
    review_session.record(
        tmp_path,
        "change",
        {
            "id": "approval",
            "kind": "scope_decision",
            "decision": "approved",
            "intended_files": manifest,
        },
    )
    (tmp_path / "outside.txt").write_text("new approved content\n")
    event = {
        "id": "refresh",
        "kind": "advance_head",
        "head": TEST_HEAD,
        "scope_decision_id": "approval",
    }
    state = review_session.record(tmp_path, "change", event)
    assert (
        state["reviewed_manifest"]["outside.txt"]
        == hashlib.sha256(b"new approved content\n").hexdigest()
    )
    assert state["contract"] == original
    assert (
        review_session.packet(tmp_path, "change")["reviewed_manifest"] == state["reviewed_manifest"]
    )
    assert review_session.record(tmp_path, "change", event) == state
    assert review_session.load(tmp_path, "change") == state


@pytest.mark.parametrize("decision", ["pending", "rejected", "deferred", "missing", "unrelated"])
def test_scope_refresh_requires_selected_approved_manifest(tmp_path: Path, decision: str) -> None:
    review_session.initialize(tmp_path, "change", contract())
    event = {
        "id": "approval",
        "kind": "scope_decision",
        "decision": decision,
        "intended_files": {"outside.txt": "<absent>"},
    }
    if decision != "missing":
        if decision == "unrelated":
            event = {"id": "approval", "kind": "scope_decision", "decision": "approved"}
        review_session.record(tmp_path, "change", event)
    path = review_session.state_path(tmp_path, "change")
    original = path.read_bytes()
    with pytest.raises(ValueError):
        review_session.record(
            tmp_path,
            "change",
            {
                "id": "refresh",
                "kind": "advance_head",
                "head": TEST_HEAD,
                "scope_decision_id": "approval",
            },
        )
    assert path.read_bytes() == original


def test_scope_contraction_is_not_implicitly_reexpanded(tmp_path: Path) -> None:
    original = contract()
    assert isinstance(original["intended_files"], dict)
    original["intended_files"]["outside.txt"] = "<absent>"
    review_session.initialize(tmp_path, "change", original)
    review_session.record(
        tmp_path,
        "change",
        {
            "id": "expand",
            "kind": "scope_decision",
            "decision": "approved",
            "intended_files": original["intended_files"],
        },
    )
    narrowed = {
        key: value for key, value in original["intended_files"].items() if key != "outside.txt"
    }
    review_session.record(
        tmp_path,
        "change",
        {
            "id": "narrow",
            "kind": "scope_decision",
            "decision": "approved",
            "intended_files": narrowed,
        },
    )
    review_session.record(
        tmp_path,
        "change",
        {
            "id": "contract",
            "kind": "advance_head",
            "head": TEST_HEAD,
            "scope_decision_id": "narrow",
        },
    )
    (tmp_path / "outside.txt").write_text("explicitly reconsidered\n")
    with pytest.raises(ValueError):
        review_session.record(
            tmp_path, "change", {"id": "implicit", "kind": "advance_head", "head": TEST_HEAD}
        )
    state = review_session.record(
        tmp_path,
        "change",
        {
            "id": "explicit",
            "kind": "advance_head",
            "head": TEST_HEAD,
            "scope_decision_id": "expand",
        },
    )
    assert "outside.txt" in state["reviewed_manifest"]
    assert state["contract"] == original


@pytest.mark.parametrize("mode", ["edit", "delete", "rename"])
def test_scope_refresh_recaptures_changes_and_checks_rename_destination(
    tmp_path: Path, mode: str
) -> None:
    review_session.initialize(tmp_path, "change", contract())
    path = tmp_path / "input.txt"
    if mode == "edit":
        path.write_text("edited\n")
    elif mode == "delete":
        path.unlink()
    else:
        path.rename(tmp_path / "renamed.txt")
    event = {"id": "refresh", "kind": "advance_head", "head": TEST_HEAD}
    if mode == "rename":
        with pytest.raises(ValueError):
            review_session.record(tmp_path, "change", event)
    else:
        state = review_session.record(tmp_path, "change", event)
        assert state["reviewed_manifest"]["input.txt"] == review_session.file_fingerprint(
            tmp_path, "input.txt"
        )
        assert "input.txt" in state["provenance"][-1]["scope"]["changed_paths"]


def test_refresh_scope_replay_rejects_forged_manifest_without_filesystem(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    review_session.initialize(tmp_path, "change", contract())
    state = review_session.record(
        tmp_path, "change", {"id": "refresh", "kind": "advance_head", "head": TEST_HEAD}
    )
    monkeypatch.setattr(
        review_session, "capture_inputs", lambda *args: pytest.fail("replay read filesystem")
    )
    assert review_session.load(tmp_path, "change") == state
    state["provenance"][-1]["scope"]["files"]["outside.txt"] = "<absent>"
    review_session.write_state(review_session.state_path(tmp_path, "change"), state)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


def test_refresh_rejects_concurrent_scope_capture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    review_session.initialize(tmp_path, "change", contract())
    capture = review_session.capture_initial_scope

    def racing_capture(*args: Any) -> Any:
        result = capture(*args)
        (tmp_path / "input.txt").write_text("concurrent edit")
        return result

    monkeypatch.setattr(review_session, "capture_initial_scope", racing_capture)
    path = review_session.state_path(tmp_path, "change")
    before = path.read_bytes()
    with pytest.raises(review_session.ConflictError):
        review_session.record(
            tmp_path, "change", {"id": "refresh", "kind": "advance_head", "head": TEST_HEAD}
        )
    assert path.read_bytes() == before


def test_adopted_comparison_base_controls_refreshed_scope(tmp_path: Path) -> None:
    original = contract()
    review_session.initialize(tmp_path, "change", original)
    (tmp_path / "outside.txt").write_text("new baseline")
    subprocess.run(["git", "-C", str(tmp_path), "add", "outside.txt"], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(tmp_path),
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.com",
            "commit",
            "-qm",
            "baseline",
        ],
        check=True,
    )
    head = review_session.repository.git(tmp_path, "rev-parse", "HEAD").decode().strip()
    event = {"id": "refresh", "kind": "advance_head", "head": head}
    with pytest.raises(ValueError):
        review_session.record(tmp_path, "change", event)
    state = review_session.record(
        tmp_path,
        "change",
        {**event, "comparison_base": head, "pr_base": {"ref": "main", "sha": head}},
    )
    assert state["provenance"][-1]["scope"]["changed_paths"] == []
    assert state["comparison_base"] == head
    assert state["contract"] == original


@pytest.mark.parametrize("initial,mutation", [(False, "create"), (True, "edit"), (True, "delete")])
def test_declared_ignored_files_invalidate_input_binding(
    tmp_path: Path, initial: bool, mutation: str
) -> None:
    path = tmp_path / ".changecost" / "declared.txt"
    path.parent.mkdir(exist_ok=True)
    if initial:
        path.write_text("original")
    scope = contract()
    assert isinstance(scope["intended_files"], dict)
    scope["intended_files"][".changecost/declared.txt"] = review_session.file_fingerprint(
        tmp_path, ".changecost/declared.txt"
    )
    state = review_session.initialize(tmp_path, "change", scope)
    assert state["inputs"]["clean"] is not initial
    if mutation == "delete":
        path.unlink()
    else:
        path.write_text("<deleted>" if mutation == "create" else "changed")
    result = review_session.status(tmp_path, "change")
    assert result["action"] == "incomplete"
    assert "inputs changed" in result["reason"]


@pytest.mark.parametrize("ignore_source", ["info", "global", "negated", "tracked"])
def test_declared_binding_respects_ignore_sources_without_hiding_content(
    tmp_path: Path, ignore_source: str
) -> None:
    name = "input.txt" if ignore_source == "tracked" else "declared.txt"
    ignore = tmp_path / ".git" / ("global-ignore" if ignore_source == "global" else "info/exclude")
    ignore.parent.mkdir(parents=True, exist_ok=True)
    ignore.write_text(name + "\n" + ("!" + name + "\n" if ignore_source == "negated" else ""))
    if ignore_source == "global":
        subprocess.run(
            ["git", "-C", str(tmp_path), "config", "core.excludesFile", str(ignore)], check=True
        )
    path = tmp_path / name
    path.write_text("initial\n")
    scope = contract()
    assert isinstance(scope["intended_files"], dict)
    scope["intended_files"][name] = review_session.file_fingerprint(tmp_path, name)
    state = review_session.initialize(tmp_path, "change", scope)
    assert state["inputs"]["clean"] is (ignore_source == "tracked")
    path.write_text("changed\n")
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


def test_approved_ignored_path_uses_new_binding_keys(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
    manifest = fixture_manifest()
    manifest[".changecost/approved.txt"] = "<absent>"
    review_session.record(
        tmp_path,
        "change",
        {
            "id": "approve",
            "kind": "scope_decision",
            "decision": "approved",
            "intended_files": manifest,
        },
    )
    state = review_session.record(
        tmp_path,
        "change",
        {
            "id": "refresh",
            "kind": "advance_head",
            "head": TEST_HEAD,
            "scope_decision_id": "approve",
        },
    )
    assert state["inputs"]["clean"]
    (tmp_path / ".changecost" / "unrelated.txt").write_text("evidence output")
    assert review_session.status(tmp_path, "change")["action"] == "continue"
    (tmp_path / ".changecost" / "approved.txt").write_text("materialized")
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


def test_ignored_declared_race_during_refresh_rejects_atomically(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    scope = contract()
    assert isinstance(scope["intended_files"], dict)
    scope["intended_files"][".changecost/racing.txt"] = "<absent>"
    review_session.initialize(tmp_path, "change", scope)
    capture = review_session.capture_initial_scope

    def race(*args: Any) -> Any:
        result = capture(*args)
        (tmp_path / ".changecost" / "racing.txt").write_text("created during capture")
        return result

    monkeypatch.setattr(review_session, "capture_initial_scope", race)
    path = review_session.state_path(tmp_path, "change")
    before = path.read_bytes()
    with pytest.raises(review_session.ConflictError):
        review_session.record(
            tmp_path, "change", {"id": "refresh", "kind": "advance_head", "head": TEST_HEAD}
        )
    assert path.read_bytes() == before


@pytest.mark.parametrize("field", ["checks", "statuses", "reviews"])
@pytest.mark.parametrize("timestamp", [None, "2000-01-01T00:00:00Z", "bad", "2026-01-01T00:00:00"])
def test_initial_context_requires_timestamped_fresh_positives(
    tmp_path: Path, field: str, timestamp: Any
) -> None:
    scope = contract()
    scope["required_statuses"] = ["status-ci"]
    review_session.initialize(tmp_path, "change", scope)
    state = review_session.load(tmp_path, "change")
    snapshot = complete_snapshot()
    snapshot["checks"][0]["check_runs"][0]["started_at"] = state["genesis"]["created_at"]
    snapshot["reviews"][0][0]["submitted_at"] = state["genesis"]["created_at"]
    snapshot["statuses"] = [
        {
            "statuses": [
                {
                    "context": "status-ci",
                    "state": "success",
                    "created_at": state["genesis"]["created_at"],
                }
            ]
        }
    ]
    entries = {
        "checks": (snapshot["checks"][0]["check_runs"][0], "started_at"),
        "statuses": (snapshot["statuses"][0]["statuses"][0], "created_at"),
        "reviews": (snapshot["reviews"][0][0], "submitted_at"),
    }
    item, key = entries[field]
    item[key] = timestamp
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] != "continue"
    assert review_session.load(tmp_path, "change")["monitor"]["pending"]


def test_initial_freshness_floor_retains_identity_across_refreshes(tmp_path: Path) -> None:
    original = contract()
    state = review_session.initialize(tmp_path, "change", original)
    floor = state["genesis"]["created_at"]
    assert state["context_since"] == floor
    event = {"id": "refresh", "kind": "advance_head", "head": TEST_HEAD}
    state = review_session.record(tmp_path, "change", event)
    assert state["context_since"] == floor
    assert review_session.record(tmp_path, "change", event) == state
    assert review_session.initialize(tmp_path, "change", original) == state
    assert review_session.load(tmp_path, "change")["context_since"] == floor
    snapshot = complete_snapshot("input-generation:1")
    snapshot["checks"][0]["check_runs"][0]["started_at"] = floor
    snapshot["reviews"][0][0]["submitted_at"] = floor
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert not review_session.load(tmp_path, "change")["monitor"]["pending"]


@pytest.mark.parametrize(
    "timestamp,expected",
    [
        ("2026-09-29T01:00:00.123456Z", True),
        ("2026-09-29T03:00:00.123456+02:00", True),
        ("2026-09-29T01:00:00Z", False),
        ("2026-09-29T01:00:00.123457Z", True),
    ],
)
def test_initial_timestamp_boundary_is_exact_and_timezone_aware(
    timestamp: str, expected: bool
) -> None:
    assert review_session.timestamp_after(timestamp, "2026-09-29T01:00:00.123456+00:00") is expected


@pytest.mark.parametrize("kind", ["symlink", "directory", "unreadable"])
def test_declared_ignored_nonregular_or_unreadable_is_incomplete(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, kind: str
) -> None:
    name = ".changecost/special"
    scope = contract()
    assert isinstance(scope["intended_files"], dict)
    scope["intended_files"][name] = "<absent>"
    review_session.initialize(tmp_path, "change", scope)
    path = tmp_path / name
    if kind == "symlink":
        path.symlink_to("missing-target")
    elif kind == "directory":
        path.mkdir()
    else:
        path.write_text("unreadable")
        read = Path.read_bytes

        def denied(selected: Path) -> bytes:
            if selected == path:
                raise PermissionError("fixture unreadable")
            return read(selected)

        monkeypatch.setattr(Path, "read_bytes", denied)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


@pytest.mark.parametrize("surface", ["reviews", "comments"])
def test_nonthread_report_changes_require_local_adjudication(
    tmp_path: Path, surface: str, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    if surface == "reviews":
        snapshot["reviews"][0][0]["body"] = "actionable top-level finding"
    else:
        snapshot["comments"] = [[{"id": 23, "body": "actionable PR comment"}]]
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


@pytest.mark.parametrize("surface", ["reviews", "comments"])
@pytest.mark.parametrize("mutation", ["add", "edit", "delete"])
def test_all_report_changes_require_exact_current_receipts(
    tmp_path: Path, surface: str, mutation: str
) -> None:
    review_session.initialize(tmp_path, "change", contract())
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    report = {"id": 42, "body": "historical informational report"}
    if surface == "reviews":
        report.update({"commit_id": "a" * 40, "state": "COMMENTED", "user": {"login": "human"}})
    snapshot[surface].append([report])
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    acknowledge_reports(tmp_path, "initial-all")
    assert review_session.status(tmp_path, "change")["action"] == "complete"
    if mutation == "add":
        snapshot[surface].append([{**report, "id": 43}])
    elif mutation == "edit":
        report["body"] = "new actionable concern"
    else:
        snapshot[surface].pop()
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"
    acknowledge_reports(tmp_path, "revalidated-all")
    assert review_session.status(tmp_path, "change")["action"] == "complete"


@pytest.mark.parametrize("surface", ["reviews", "comments"])
@pytest.mark.parametrize(
    "field,value",
    [("id", None), ("id", True), ("id", "1"), ("id", 0), ("body", None), ("body", 17)],
)
def test_malformed_nonthread_reports_replace_green(
    tmp_path: Path, surface: str, field: str, value: Any, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    if surface == "comments":
        snapshot[surface] = [[{"id": 1, "body": ""}]]
    snapshot[surface][0][0][field] = value
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    state = review_session.load(tmp_path, "change")
    assert state["monitor"]["errors"]
    assert review_session.packet(tmp_path, "change")["report_receipts"] is None
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


@pytest.mark.parametrize("surface", ["reviews", "comments"])
def test_duplicate_nonthread_ids_across_pages_fail_closed(tmp_path: Path, surface: str) -> None:
    review_session.initialize(tmp_path, "change", contract())
    snapshot = complete_snapshot()
    if surface == "comments":
        snapshot[surface] = [[{"id": 1, "body": ""}]]
    snapshot[surface].append([dict(snapshot[surface][0][0])])
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.load(tmp_path, "change")["monitor"]["errors"]
    assert review_session.report_receipts(snapshot) is None


def test_report_namespaces_and_metadata_do_not_collide_or_revoke_coverage(
    tmp_path: Path, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    snapshot["reviews"][0][0]["id"] = 42
    snapshot["comments"] = [[{"id": 42, "body": ""}], [{"id": 43, "body": "second"}]]
    snapshot["threads"] = [
        {
            "id": "42",
            "isResolved": True,
            "isOutdated": False,
            "comments": [{"id": "comment:42", "body": ""}],
        }
    ]
    receipts = review_session.report_receipts(snapshot)
    assert receipts is not None and set(receipts) == {
        "review:42",
        "comment:42",
        "comment:43",
        "thread:42",
    }
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    acknowledge_reports(tmp_path, "all-namespaces")
    snapshot["comments"].reverse()
    snapshot["comments"][0][0].update(
        {"updated_at": "2099-01-01T00:00:00Z", "reactions": {"+1": 99}}
    )
    snapshot["reviews"][0][0]["user"]["avatar_url"] = "changed"
    snapshot["reviews"][0][0]["state"] = "COMMENTED"
    snapshot["threads"][0]["isOutdated"] = True
    assert review_session.report_receipts(snapshot) == receipts
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "complete"


@pytest.mark.parametrize("duplicate", [False, True])
def test_required_neutral_check_cannot_satisfy_completion(
    tmp_path: Path, duplicate: bool, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    neutral = {**snapshot["checks"][0]["check_runs"][0], "conclusion": "neutral"}
    if duplicate:
        snapshot["checks"].append({"check_runs": [neutral]})
    else:
        snapshot["checks"] = [{"check_runs": [neutral]}]
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"
    assert review_session.load(tmp_path, "change")["monitor"]["errors"]


@pytest.mark.parametrize("required", [True, False])
@pytest.mark.parametrize(
    "conclusion",
    [
        "success",
        "neutral",
        "skipped",
        "failure",
        "cancelled",
        "timed_out",
        "action_required",
        "stale",
        "startup_failure",
        "unknown",
        None,
    ],
)
def test_check_conclusion_policy_preserves_required_positive_assurance(
    tmp_path: Path, required: bool, conclusion: Any, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    item = {
        **snapshot["checks"][0]["check_runs"][0],
        "name": "ci" if required else "optional",
        "conclusion": conclusion,
    }
    if required:
        snapshot["checks"] = [{"check_runs": [item]}]
    else:
        snapshot["checks"].append({"check_runs": [item]})
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    expected = (
        "complete"
        if conclusion == "success" or (not required and conclusion == "neutral")
        else "incomplete"
    )
    assert review_session.status(tmp_path, "change")["action"] == expected


@pytest.mark.parametrize(
    "status", ["queued", "in_progress", "waiting", "pending", "requested", "unknown"]
)
def test_uncompleted_checks_never_become_positive(
    tmp_path: Path, status: str, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    snapshot["checks"][0]["check_runs"][0]["status"] = status
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] != "complete"
    assert review_session.load(tmp_path, "change")["monitor"]["pending"]


def mock_collection_passes(
    monkeypatch: pytest.MonkeyPatch, snapshots: list[dict[str, Any]]
) -> list[int]:
    reads = [0]

    def selected() -> dict[str, Any]:
        return snapshots[min((max(reads[0], 1) - 1) // 2, len(snapshots) - 1)]

    def api(endpoint: str, **kwargs: Any) -> Any:
        if endpoint.endswith("/pulls/24"):
            reads[0] += 1
            snap = selected()
            return {
                "head": {"sha": snap["head"]},
                "base": snap["pr_base"],
                "requested_reviewers": snap["requested_reviewers"],
            }
        snap = selected()
        for suffix, field in [
            ("check-runs?per_page=100", "checks"),
            ("status?per_page=100", "statuses"),
            ("reviews?per_page=100", "reviews"),
            ("comments?per_page=100", "comments"),
        ]:
            if endpoint.endswith(suffix):
                return snap[field]
        raise AssertionError(endpoint)

    monkeypatch.setattr(review_session, "gh_json", api)
    monkeypatch.setattr(review_session, "gh_review_threads", lambda *args: selected()["threads"])
    return reads


@pytest.mark.parametrize("surface", ["checks", "statuses", "reviews", "comments", "threads"])
def test_remote_collection_rejects_between_pass_surface_drift(
    monkeypatch: pytest.MonkeyPatch, surface: str
) -> None:
    first = complete_snapshot()
    second = json.loads(json.dumps(first))
    if surface == "checks":
        second[surface][0]["check_runs"][0]["conclusion"] = "failure"
    elif surface == "statuses":
        second[surface] = [{"statuses": [{"context": "other", "state": "pending"}]}]
    elif surface == "reviews":
        second[surface][0][0]["body"] = "new finding"
    elif surface == "comments":
        second[surface] = [[{"id": 1, "body": "new finding"}]]
    else:
        second[surface] = [
            {
                "id": "thread",
                "isResolved": False,
                "isOutdated": False,
                "comments": [{"id": "comment", "body": "new finding"}],
            }
        ]
    mock_collection_passes(monkeypatch, [first, second])
    with pytest.raises(ValueError):
        review_session.gh_snapshot("nold-ai/changecost", 24)


@pytest.mark.parametrize(
    "surface,field,value",
    [
        ("check", "status", "in_progress"),
        ("check", "started_at", "2000-01-01T00:00:00Z"),
        ("status", "state", "failure"),
        ("status", "created_at", "2000-01-01T00:00:00Z"),
        ("review", "state", "CHANGES_REQUESTED"),
        ("review", "commit_id", "a" * 40),
        ("review", "submitted_at", "2000-01-01T00:00:00Z"),
        ("thread", "isResolved", False),
        ("thread", "isOutdated", True),
    ],
)
def test_verification_pass_preserves_lifecycle_and_freshness(
    monkeypatch: pytest.MonkeyPatch, surface: str, field: str, value: Any
) -> None:
    first = reviewed_thread_snapshot()
    first["statuses"] = [
        {"statuses": [{"context": "ci", "state": "success", "created_at": "2099-01-01T00:00:00Z"}]}
    ]
    second = json.loads(json.dumps(first))
    items = {
        "check": second["checks"][0]["check_runs"][0],
        "status": second["statuses"][0]["statuses"][0],
        "review": second["reviews"][0][0],
        "thread": second["threads"][0],
    }
    items[surface][field] = value
    snapshots = iter([first, second])
    monkeypatch.setattr(review_session, "collect_remote_snapshot", lambda *args: next(snapshots))
    with pytest.raises(ValueError, match="changed"):
        review_session.gh_snapshot("nold-ai/changecost", 24)


def test_consistent_passes_return_second_with_harmless_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = complete_snapshot()
    first["comments"] = [[{"id": 1, "body": "one"}, {"id": 2, "body": "two"}]]
    second = json.loads(json.dumps(first))
    second["comments"] = [[second["comments"][0][0]], [second["comments"][0][1]]]
    second["reviews"][0][0]["user"]["avatar_url"] = "new"
    second["comments"][0][0]["reactions"] = {"+1": 1}
    snapshots = iter([first, second])
    monkeypatch.setattr(review_session, "collect_remote_snapshot", lambda *args: next(snapshots))
    assert review_session.gh_snapshot("nold-ai/changecost", 24) is second


@pytest.mark.parametrize("failure", ["api", "malformed", "timeout"])
def test_second_pass_failure_replaces_prior_green(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    calls = [0]

    def collect(*args: Any) -> Any:
        calls[0] += 1
        if calls[0] == 1:
            return complete_snapshot()
        if failure == "malformed":
            return {"errors": ["partial pages"]}
        if failure == "timeout":
            raise subprocess.TimeoutExpired("gh", 1)
        raise RuntimeError("API failure")

    monkeypatch.setattr(review_session, "collect_remote_snapshot", collect)
    observed = review_session.collect_snapshot(tmp_path, "change", "nold-ai/changecost", 24, 100)
    review_session.record_monitor_snapshot(tmp_path, "change", observed)
    assert calls == [2]
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"
    assert review_session.packet(tmp_path, "change")["report_receipts"] is None


def test_two_passes_share_one_decreasing_request_deadline(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, prepared_session: dict[str, Any]
) -> None:
    ticks = iter([100, 110])
    monkeypatch.setattr(review_session.time, "monotonic", lambda: next(ticks))
    timeouts = []

    def collect(*args: Any) -> Any:
        timeouts.append(review_session.request_timeout())
        return complete_snapshot()

    monkeypatch.setattr(review_session, "collect_remote_snapshot", collect)
    observed = review_session.collect_snapshot(tmp_path, "change", "nold-ai/changecost", 24, 150)
    assert timeouts == [50, 40]
    assert "errors" not in observed


def test_dirty_working_mode_change_invalidates_capture(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("already dirty\n")
    review_session.initialize(tmp_path, "change", contract())
    path.chmod(path.stat().st_mode ^ 0o100)
    result = review_session.status(tmp_path, "change")
    assert result["action"] == "incomplete"
    assert "inputs changed" in result["reason"]


@pytest.mark.parametrize("mode,stage", [("120000", "0"), ("100644", "1")])
def test_declared_unsupported_index_is_rejected(tmp_path: Path, mode: str, stage: str) -> None:
    blob = review_session.repository.git(tmp_path, "rev-parse", "HEAD:input.txt").decode().strip()
    subprocess.run(
        ["git", "-C", str(tmp_path), "update-index", "--force-remove", "input.txt"], check=True
    )
    subprocess.run(
        ["git", "-C", str(tmp_path), "update-index", "--index-info"],
        input=f"{mode} {blob} {stage}\tinput.txt\n",
        text=True,
        check=True,
    )
    with pytest.raises(ValueError, match="unsupported or unmerged"):
        review_session.input_fingerprint(tmp_path, "input.txt")


def test_input_identity_ignores_mtime_and_report_hash_is_raw(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    before = review_session.input_fingerprint(tmp_path, "input.txt")
    path.touch()
    assert review_session.input_fingerprint(tmp_path, "input.txt") == before
    assert (
        review_session.file_fingerprint(tmp_path, "input.txt")
        == hashlib.sha256(path.read_bytes()).hexdigest()
    )


# Post-replan selected coordinator obligations (O1-O6).
def escalated_session(root: Path, *, closure_before_fixed: bool = False) -> dict[str, Any]:
    review_session.initialize(root, "change", contract())
    events = [
        {"id": "first", "kind": "finding", "family": "inputs"},
        {"id": "fix-first", "kind": "disposition", "finding_id": "first", "disposition": "fixed"},
        {"id": "escape", "kind": "finding", "family": "inputs"},
        {"id": "audit", "kind": "investigation", "family": "inputs"},
        {"id": "later", "kind": "finding", "family": "inputs"},
        {"id": "fix-escape", "kind": "disposition", "finding_id": "escape", "disposition": "fixed"},
        {"id": "fix-later", "kind": "disposition", "finding_id": "later", "disposition": "fixed"},
    ]
    for event in events[:-2] if closure_before_fixed else events:
        review_session.record(root, "change", event)
    complete_session(root)
    state = review_session.load(root, "change")
    review_session.record(
        root,
        "change",
        {
            "id": "closure",
            "kind": "evidence",
            "evidence_type": "reviewer",
            "result": "pass",
            "head": TEST_HEAD,
            "binding": review_session.evidence_binding(state),
            "covers_findings": ["escape", "later"],
            "reviewed_reports": review_session.report_receipts(complete_snapshot()),
        },
    )
    if closure_before_fixed:
        for event in events[-2:]:
            review_session.record(root, "change", event)
    return {
        "id": "resolution",
        "kind": "scope_decision",
        "decision": "approved",
        "approved_by": "independent-reviewer",
        "resolves_findings": ["escape", "later"],
        "binding": review_session.evidence_binding(state),
        "closure_evidence_id": "closure",
    }


def test_named_family_resolution_preserves_history_and_reopens(tmp_path: Path) -> None:
    resolution = escalated_session(tmp_path)
    before = review_session.load(tmp_path, "change")
    review_session.record(tmp_path, "change", resolution)
    assert review_session.status(tmp_path, "change")["action"] == "complete"
    after = review_session.load(tmp_path, "change")
    assert after["findings"] == before["findings"]
    assert after["batches"] == before["batches"]
    review_session.record(
        tmp_path, "change", {"id": "new-escape", "kind": "finding", "family": "inputs"}
    )
    review_session.record(tmp_path, "change", {"id": "active", "kind": "phase", "phase": "active"})
    assert review_session.status(tmp_path, "change")["action"] == "replan"


@pytest.mark.parametrize(
    "mutation", ["unknown", "not-escalated", "uncovered", "stale", "missing-closure", "nonfixed"]
)
def test_named_family_resolution_rejects_unverified_claim(tmp_path: Path, mutation: str) -> None:
    resolution = escalated_session(tmp_path)
    if mutation in {"unknown", "not-escalated", "uncovered"}:
        resolution["resolves_findings"] = [
            {"unknown": "absent", "not-escalated": "first", "uncovered": "other"}[mutation]
        ]
    if mutation == "uncovered":
        review_session.record(
            tmp_path, "change", {"id": "other", "kind": "finding", "family": "inputs"}
        )
        review_session.record(
            tmp_path,
            "change",
            {
                "id": "other-fix",
                "kind": "disposition",
                "finding_id": "other",
                "disposition": "fixed",
            },
        )
    if mutation == "stale":
        resolution["binding"] = {**resolution["binding"], "input_digest": "0" * 64}
    if mutation == "missing-closure":
        resolution["closure_evidence_id"] = "absent"
    if mutation == "nonfixed":
        review_session.record(
            tmp_path,
            "change",
            {
                "id": "exception",
                "kind": "disposition",
                "finding_id": "later",
                "disposition": "accepted_exception",
            },
        )
    with pytest.raises(ValueError, match="resolution|closure"):
        review_session.record(tmp_path, "change", resolution)


def native_completion(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    review_session.initialize(root, "change", contract())
    complete_session(root)
    snapshot = complete_snapshot()
    snapshot["reviews"] = [[]]
    snapshot["comments"] = [
        [{"id": 900, "body": "Native code review finished", "user": {"login": "reviewer-a"}}]
    ]
    review_session.record_monitor_snapshot(root, "change", snapshot)
    state = review_session.load(root, "change")
    receipts = review_session.report_receipts(snapshot)
    assert receipts is not None
    evidence = {
        "id": "native",
        "kind": "evidence",
        "evidence_type": "reviewer",
        "result": "pass",
        "head": TEST_HEAD,
        "binding": review_session.evidence_binding(state),
        "reviewed_reports": receipts,
        "provider_completions": [
            {
                "reviewer": "reviewer-a",
                "review_kind": "code",
                "source": "comment:900",
                "report_sha256": receipts["comment:900"],
                "head": TEST_HEAD,
                "completed_at": "2099-01-01T00:00:00Z",
            }
        ],
    }
    return snapshot, evidence


def test_native_completion_replays_and_requires_unchanged_source(tmp_path: Path) -> None:
    snapshot, evidence = native_completion(tmp_path)
    review_session.record(tmp_path, "change", evidence)
    assert review_session.status(tmp_path, "change")["action"] == "complete"
    state = review_session.load(tmp_path, "change")
    assert state["monitor"]["data"]["reviews"] == [[]]
    assert state["provenance"][-1]["provider_sources"]
    snapshot["comments"][0][0]["body"] += " edited"
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] != "complete"


@pytest.mark.parametrize(
    "field,value",
    [
        ("reviewer", "wrong-bot"),
        ("review_kind", "security"),
        ("source", "comment:901"),
        ("report_sha256", "0" * 64),
        ("head", "a" * 40),
        ("head", "abcdef0"),
        ("completed_at", "2000-01-01T00:00:00Z"),
    ],
)
def test_native_completion_rejects_misbound_source(tmp_path: Path, field: str, value: str) -> None:
    _, evidence = native_completion(tmp_path)
    evidence["provider_completions"][0][field] = value
    with pytest.raises(ValueError):
        review_session.record(tmp_path, "change", evidence)


@pytest.mark.parametrize("kind", ["batch", "investigation"])
def test_exhaustion_blocks_new_correction_authority(
    tmp_path: Path, kind: str, prepared_session: dict[str, Any]
) -> None:
    for index in range(3):
        review_session.record(tmp_path, "change", {"id": str(index), "kind": "batch"})
    with pytest.raises(ValueError, match="budget"):
        review_session.record(
            tmp_path, "change", {"id": "unauthorized", "kind": kind, "family": "inputs"}
        )


@pytest.mark.parametrize("timeout", [None, 30])
def test_watch_default_is_absolute_despite_progress(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    timeout: int | None,
    prepared_session: dict[str, Any],
) -> None:
    complete_session(tmp_path)
    clock = [0.0]
    deadlines = []

    def collect(*args: Any) -> dict[str, Any]:
        deadlines.append(args[-1])
        clock[0] += 600
        snapshot = complete_snapshot()
        snapshot["checks"][0]["check_runs"][0]["status"] = "in_progress"
        snapshot["checks"][0]["check_runs"][0]["status"] = (
            "queued" if len(deadlines) % 2 else "in_progress"
        )
        return snapshot

    monkeypatch.setattr(review_session.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        review_session.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + seconds)
    )
    monkeypatch.setattr(review_session, "collect_snapshot", collect)
    assert review_session.watch(tmp_path, "change", "nold-ai/changecost", 24, timeout) == 0
    assert deadlines and max(deadlines) == 2700
    assert len(deadlines) == 5


@pytest.mark.parametrize(
    "objection",
    [
        "failed",
        "pending",
        "missing",
        "requested",
        "negative",
        "thread",
        "finding",
        "input",
        "author",
        "absent",
    ],
)
def test_native_completion_never_waives_objections(tmp_path: Path, objection: str) -> None:
    snapshot, evidence = native_completion(tmp_path)
    review_session.record(tmp_path, "change", evidence)
    assert review_session.status(tmp_path, "change")["action"] == "complete"
    mutations: dict[str, Callable[[], object]] = {
        "failed": lambda: snapshot["checks"][0]["check_runs"][0].update(conclusion="failure"),
        "pending": lambda: snapshot["checks"][0]["check_runs"][0].update(status="in_progress"),
        "missing": lambda: snapshot.update(checks=[]),
        "requested": lambda: snapshot.update(requested_reviewers=[{"login": "reviewer-a"}]),
        "negative": lambda: snapshot.update(
            reviews=[[{**complete_snapshot()["reviews"][0][0], "state": "CHANGES_REQUESTED"}]]
        ),
        "thread": lambda: snapshot.update(
            threads=[{"id": "t", "isResolved": False, "isOutdated": False, "comments": []}]
        ),
        "finding": lambda: review_session.record(
            tmp_path, "change", {"id": "new", "kind": "finding", "family": "other"}
        ),
        "input": lambda: (tmp_path / "input.txt").write_text("changed"),
        "author": lambda: snapshot["comments"][0][0]["user"].update(login="impostor"),
        "absent": lambda: snapshot.update(comments=[[]]),
    }
    mutations[objection]()
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] != "complete"


def test_named_resolution_survives_refresh_without_resolving_unlisted(tmp_path: Path) -> None:
    resolution = escalated_session(tmp_path)
    resolution["resolves_findings"] = ["escape"]
    review_session.record(tmp_path, "change", resolution)
    assert review_session.status(tmp_path, "change")["action"] == "replan"
    resolution = {**resolution, "id": "resolve-later", "resolves_findings": ["later"]}
    review_session.record(tmp_path, "change", resolution)
    review_session.record(
        tmp_path, "change", {"id": "refresh", "kind": "advance_head", "head": TEST_HEAD}
    )
    assert review_session.family_decision(review_session.load(tmp_path, "change")) is None


@pytest.mark.parametrize("blocker", ["none", "family", "finding", "failed", "thread", "input"])
def test_observe_only_is_budget_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, blocker: str
) -> None:
    if blocker == "family":
        escalated_session(tmp_path)
        review_session.record(
            tmp_path, "change", {"id": "active", "kind": "phase", "phase": "active"}
        )
    else:
        review_session.initialize(tmp_path, "change", contract())
    review_session.record_monitor_snapshot(tmp_path, "change", complete_snapshot())
    acknowledge_reports(tmp_path, "baseline-reports")
    for index in range(3):
        review_session.record(tmp_path, "change", {"id": f"batch-{index}", "kind": "batch"})
    if blocker == "finding":
        review_session.record(
            tmp_path, "change", {"id": "new", "kind": "finding", "family": "other"}
        )
    if blocker == "input":
        (tmp_path / "input.txt").write_text("drift")
    clock = [0.0]
    polls = []

    def collect(*args: Any) -> dict[str, Any]:
        polls.append(clock[0])
        snapshot = complete_snapshot()
        snapshot["checks"][0]["check_runs"][0]["status"] = "in_progress"
        if blocker == "failed":
            snapshot["checks"][0]["check_runs"][0].update(status="completed", conclusion="failure")
        if blocker == "thread":
            snapshot["threads"] = [
                {"id": "t", "isResolved": False, "isOutdated": False, "comments": []}
            ]
        return snapshot

    monkeypatch.setattr(review_session.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        review_session.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + seconds)
    )
    monkeypatch.setattr(review_session, "collect_snapshot", collect)
    review_session.watch(tmp_path, "change", "nold-ai/changecost", 24, 1, observe_only=True)
    assert (len(polls) > 1) == (blocker == "none")
    state = review_session.load(tmp_path, "change")
    assert state["batches"] == 3
    assert review_session.status(tmp_path, "change")["action"] != "complete"


def test_native_provenance_replay_rejects_tampering(tmp_path: Path) -> None:
    _, evidence = native_completion(tmp_path)
    review_session.record(tmp_path, "change", evidence)
    state = review_session.load(tmp_path, "change")
    state["provenance"][-1]["provider_sources"][0]["reviewer"] = "impostor"
    with pytest.raises(ValueError, match="retained fetched"):
        review_session.replay(state["genesis"], state["events"], state["provenance"], None, 0)


@pytest.mark.parametrize("kind", ["closure", "native"])
def test_new_durable_claim_requires_actual_current_inputs(tmp_path: Path, kind: str) -> None:
    if kind == "closure":
        event = escalated_session(tmp_path)
    else:
        _, event = native_completion(tmp_path)
    (tmp_path / "input.txt").write_text("unreviewed mutation")
    with pytest.raises(ValueError, match="inputs changed"):
        review_session.record(tmp_path, "change", event)


def test_watcher_keeps_waiting_after_incomplete_native_adjudication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    snapshot, evidence = native_completion(tmp_path)
    evidence.pop("provider_completions")
    evidence["result"] = "incomplete"
    review_session.record(tmp_path, "change", evidence)
    clock = [0.0]
    calls = []
    monkeypatch.setattr(review_session.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        review_session.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + seconds)
    )
    monkeypatch.setattr(
        review_session, "collect_snapshot", lambda *args: calls.append(1) or snapshot
    )
    assert review_session.watch(tmp_path, "change", "nold-ai/changecost", 24, 1) == 0
    assert len(calls) == 3
    assert review_session.status(tmp_path, "change")["action"] == "wait"


@pytest.mark.parametrize("review_state", ["PENDING", "DISMISSED"])
def test_native_fallback_cannot_override_present_rest_state(
    tmp_path: Path, review_state: str
) -> None:
    snapshot, evidence = native_completion(tmp_path)
    review_session.record(tmp_path, "change", evidence)
    assert review_session.status(tmp_path, "change")["action"] == "complete"
    snapshot["reviews"] = complete_snapshot()["reviews"]
    snapshot["reviews"][0][0]["state"] = review_state
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    acknowledge_reports(tmp_path, "adjudicated-current-rest-report")
    assert review_session.status(tmp_path, "change")["action"] == "wait"
    assert review_session.load(tmp_path, "change")["monitor"]["pending"]


@pytest.mark.parametrize(
    "timestamp,expected", [("2000-01-01T00:00:00Z", "wait"), ("2099-01-01T00:00:00Z", "complete")]
)
def test_existing_rest_keeps_its_own_freshness(
    tmp_path: Path, timestamp: str, expected: str
) -> None:
    snapshot, evidence = native_completion(tmp_path)
    review_session.record(tmp_path, "change", evidence)
    snapshot["reviews"] = complete_snapshot()["reviews"]
    snapshot["reviews"][0][0]["submitted_at"] = timestamp
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    acknowledge_reports(tmp_path, "adjudicated-existing-rest")
    assert review_session.status(tmp_path, "change")["action"] == expected


def closure_event(root: Path, identity: str, result: str, covers: list[str]) -> dict[str, Any]:
    state = review_session.load(root, "change")
    return {
        "id": identity,
        "kind": "evidence",
        "evidence_type": "reviewer",
        "result": result,
        "head": TEST_HEAD,
        "binding": review_session.evidence_binding(state),
        "covers_findings": covers,
        "reviewed_reports": review_session.report_receipts(state["monitor"]["data"]),
    }


def test_resolution_rejects_future_finding_coverage(tmp_path: Path) -> None:
    resolution = escalated_session(tmp_path)
    covered = ["escape", "later", "future"]
    review_session.record(tmp_path, "change", closure_event(tmp_path, "premature", "pass", covered))
    review_session.record(
        tmp_path, "change", {"id": "future", "kind": "finding", "family": "inputs"}
    )
    review_session.record(
        tmp_path,
        "change",
        {"id": "fix-future", "kind": "disposition", "finding_id": "future", "disposition": "fixed"},
    )
    resolution.update(closure_evidence_id="premature", resolves_findings=covered)
    with pytest.raises(ValueError, match="closure.*finding|finding.*closure"):
        review_session.record(tmp_path, "change", resolution)


@pytest.mark.parametrize(
    "contradiction", ["accepted_exception", "non_finding", "fail", "incomplete"]
)
def test_resolution_rejects_intervening_contradiction_and_accepts_fresh_closure(
    tmp_path: Path, contradiction: str
) -> None:
    resolution = escalated_session(tmp_path)
    if contradiction in {"accepted_exception", "non_finding"}:
        review_session.record(
            tmp_path,
            "change",
            {
                "id": "contradiction",
                "kind": "disposition",
                "finding_id": "later",
                "disposition": contradiction,
            },
        )
        review_session.record(
            tmp_path,
            "change",
            {
                "id": "fixed-again",
                "kind": "disposition",
                "finding_id": "later",
                "disposition": "fixed",
            },
        )
    else:
        review_session.record(
            tmp_path, "change", closure_event(tmp_path, "contradiction", contradiction, ["later"])
        )
        acknowledge_reports(tmp_path, "current-reports")
    with pytest.raises(ValueError, match="closure.*contradict|contradict.*closure"):
        review_session.record(tmp_path, "change", resolution)
    review_session.record(
        tmp_path, "change", closure_event(tmp_path, "fresh-closure", "pass", ["escape", "later"])
    )
    resolution["closure_evidence_id"] = "fresh-closure"
    review_session.record(tmp_path, "change", resolution)
    assert review_session.status(tmp_path, "change")["action"] == "complete"


@pytest.mark.parametrize("closure_before_fixed", [False, True])
def test_known_closure_and_administrative_fixed_orders_are_valid(
    tmp_path: Path, closure_before_fixed: bool
) -> None:
    resolution = escalated_session(tmp_path, closure_before_fixed=closure_before_fixed)
    review_session.record(
        tmp_path, "change", {"id": "unrelated", "kind": "finding", "family": "unrelated"}
    )
    review_session.record(
        tmp_path,
        "change",
        {
            "id": "unrelated-exception",
            "kind": "disposition",
            "finding_id": "unrelated",
            "disposition": "accepted_exception",
        },
    )
    review_session.record(
        tmp_path,
        "change",
        closure_event(tmp_path, "unrelated-negative", "incomplete", ["unrelated"]),
    )
    acknowledge_reports(tmp_path, "current-report-coverage")
    review_session.record(tmp_path, "change", resolution)
    assert review_session.status(tmp_path, "change")["action"] == "complete"


@pytest.mark.parametrize("gate", ["pending", "missing"])
def test_new_report_hands_off_before_pending_gates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, gate: str, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    snapshot["checks"][0]["check_runs"][0]["status"] = "in_progress"
    if gate == "missing":
        snapshot["checks"] = [{"check_runs": []}]
    snapshot["comments"] = [[{"id": 902, "body": "New potentially actionable feedback"}]]
    clock = [0.0]
    calls: list[int] = []
    monkeypatch.setattr(review_session.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        review_session.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + seconds)
    )
    monkeypatch.setattr(
        review_session, "collect_snapshot", lambda *args: calls.append(1) or snapshot
    )
    assert review_session.watch(tmp_path, "change", "nold-ai/changecost", 24, 1) == 0
    assert calls == [1]
    assert review_session.status(tmp_path, "change")["action"] == "wait"


@pytest.mark.parametrize("report", ["acknowledged-incomplete", "check-only-progress"])
def test_pending_gates_do_not_repeat_unchanged_report_handoff(
    tmp_path: Path, report: str, prepared_session: dict[str, Any]
) -> None:
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    snapshot["checks"][0]["check_runs"][0]["status"] = "in_progress"
    if report == "acknowledged-incomplete":
        snapshot["comments"] = [[{"id": 903, "body": "Still awaiting provider completion"}]]
        review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
        state = review_session.load(tmp_path, "change")
        review_session.record(
            tmp_path,
            "change",
            {
                "id": "acknowledged",
                "kind": "evidence",
                "evidence_type": "reviewer",
                "result": "incomplete",
                "head": TEST_HEAD,
                "binding": review_session.evidence_binding(state),
                "reviewed_reports": review_session.report_receipts(snapshot),
            },
        )
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.review_handoff(tmp_path, "change") is None
    snapshot["checks"][0]["check_runs"][0]["status"] = "queued"
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.review_handoff(tmp_path, "change") is None
    assert review_session.status(tmp_path, "change")["action"] == "wait"
