"""Behavioral tests for bounded, persisted review-session decisions."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from quality import review_session

TEST_HEAD = ""
TEST_ROOT = Path()


@pytest.fixture(autouse=True)
def git_fixture(tmp_path: Path) -> None:
    global TEST_HEAD, TEST_ROOT
    TEST_ROOT = tmp_path
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
    TEST_HEAD = subprocess.check_output(
        ["git", "-C", str(tmp_path), "rev-parse", "HEAD"], text=True
    ).strip()


def contract() -> dict[str, object]:
    return {
        "requirements": ["tests pass"],
        "repository": "nold-ai/changecost",
        "acceptance_criteria": ["review evidence is current"],
        "non_goals": ["host authentication"],
        "trust_boundary": "configuration validation only",
        "intended_files": fixture_manifest(),
        "base": TEST_HEAD,
        "head": TEST_HEAD,
        "required_reviewers": ["reviewer-a"],
        "required_checks": ["ci"],
        "required_statuses": [],
    }


def fixture_manifest() -> dict[str, str]:
    names = subprocess.check_output(
        [
            "git",
            "-C",
            str(TEST_ROOT),
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
        ],
        text=True,
    ).split("\0")
    return {
        name: hashlib.sha256((TEST_ROOT / name).read_bytes()).hexdigest()
        if (TEST_ROOT / name).is_file()
        else "<absent>"
        for name in names
        if name
    }


def complete_snapshot() -> dict[str, Any]:
    return {
        "repository": "nold-ai/changecost",
        "pull_request": 24,
        "head": TEST_HEAD,
        "checks": [
            {"check_runs": [{"name": "ci", "status": "completed", "conclusion": "success"}]}
        ],
        "statuses": [{"statuses": []}],
        "comments": [[]],
        "threads": [],
        "reviews": [
            [{"commit_id": TEST_HEAD, "state": "APPROVED", "user": {"login": "reviewer-a"}}]
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
            },
        )
    review_session.record(tmp_path, "change", {"id": "done", "kind": "phase", "phase": "complete"})
    if timing:
        review_session.record(
            tmp_path, "change", {"id": "completed-time", "kind": "active_minutes", "minutes": 0}
        )


def test_final_batch_completion_and_pending_precedence(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
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
def test_nested_corruption_fails_closed(tmp_path: Path, field: str, value: object) -> None:
    state = review_session.initialize(tmp_path, "change", contract())
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
    snapshot[source] = [{"check_runs" if source == "checks" else "statuses": [item]}]
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


def test_fixed_escape_retains_escalation(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
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


def test_budget_and_extension_keep_existing_counters(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
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


def test_final_allowed_batch_requires_replanning_even_after_fixes(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
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


def test_finding_family_requires_investigation_then_replan(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
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


def test_packet_keeps_unresolved_evidence_and_usage_units(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
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


def test_disposition_does_not_transfer_without_an_exact_finding_id(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
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


def test_monitor_error_leaves_session_incomplete(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
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
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    review_session.initialize(tmp_path, "change", contract())
    review_session.record(
        tmp_path, "change", {"id": "scope", "kind": "scope_decision", "decision": "pending"}
    )
    snapshot = {"head": contract()["head"], "checks": []}
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    monkeypatch.setattr(review_session, "gh_snapshot", lambda repository, pull_request: snapshot)
    assert review_session.watch(tmp_path, "change", "nold-ai/changecost", 22, 0) == 1
    assert '"action": "incomplete"' in capsys.readouterr().out


def test_watcher_polls_after_a_changed_continue_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    review_session.initialize(tmp_path, "change", contract())
    snapshot = {
        **complete_snapshot(),
        "head": contract()["head"],
        "reviews": [
            [
                {
                    "commit_id": contract()["head"],
                    "state": "APPROVED",
                    "user": {"login": "reviewer-a"},
                }
            ]
        ],
    }
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


def test_changed_monitor_head_and_empty_completion_are_incomplete(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
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
            {"head": {"sha": "head"}, "requested_reviewers": []}
            if not paginate
            else [{"page": endpoint}]
        )

    monkeypatch.setattr(review_session, "gh_json", fake_gh)
    monkeypatch.setattr(
        review_session,
        "gh_review_threads",
        lambda repository, pull_request: [{"id": "thread-1", "isResolved": False}],
    )
    snapshot = review_session.gh_snapshot("nold-ai/changecost", 22)
    assert snapshot["head"] == "head"
    assert len([call for call in calls if call[1]]) == 4
    assert snapshot["threads"] == [{"id": "thread-1", "isResolved": False}]


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
def test_missing_source_cannot_complete(tmp_path: Path, source: str) -> None:
    review_session.initialize(tmp_path, "change", contract())
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    del snapshot[source]
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


def test_outdated_unresolved_thread_blocks_completion(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
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


def test_watcher_api_timeout_is_incomplete(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    review_session.initialize(tmp_path, "change", contract())

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
    tmp_path: Path, kind: str, payload: dict[str, object]
) -> None:
    review_session.initialize(tmp_path, "change", contract())
    before = review_session.load(tmp_path, "change")
    with pytest.raises(ValueError):
        review_session.record(tmp_path, "change", {"id": "bad", "kind": kind, **payload})
    assert review_session.load(tmp_path, "change") == before


def test_same_head_rebind_invalidates_passing_evidence(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
    complete_session(tmp_path)
    (tmp_path / "added.py").write_text("new input")
    review_session.record(
        tmp_path, "change", {"id": "rebind", "kind": "advance_head", "head": TEST_HEAD}
    )
    review_session.record_monitor_snapshot(tmp_path, "change", complete_snapshot())
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
                "kind": "evidence",
                "evidence_type": category,
                "head": TEST_HEAD,
                "result": "pass",
            },
        )
    review_session.record_monitor_snapshot(tmp_path, "change", complete_snapshot())
    review_session.record(
        tmp_path, "change", {"id": "new-done", "kind": "phase", "phase": "complete"}
    )
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


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
            {"id": index + 1, "commit_id": TEST_HEAD, "user": {"login": login}, "state": state}
            for index, state in enumerate(states)
        ]
    ]
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
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


def test_missing_minutes_ingestion_does_not_create_measurement(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
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
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    review_session.initialize(tmp_path, "change", contract())

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
                "commit_id": TEST_HEAD,
                "user": {"login": "reviewer-a[bot]"},
                "state": "CHANGES_REQUESTED",
            }
        ],
        [
            {"commit_id": TEST_HEAD, "user": {"login": "reviewer-a[bot]"}, "state": "APPROVED"},
            {
                "commit_id": "old",
                "user": {"login": "reviewer-a[bot]"},
                "state": "CHANGES_REQUESTED",
            },
        ],
    ]
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "complete"


def test_fractional_minutes_sum_canonically_across_restart_and_budget(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
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
    tmp_path: Path, field: str, value: object
) -> None:
    review_session.initialize(tmp_path, "change", contract())
    for event in (
        {"id": "batch", "kind": "batch"},
        {"id": "scope", "kind": "scope_decision", "decision": "pending"},
        {"id": "investigation", "kind": "investigation", "family": "f"},
        {
            "id": "evidence",
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
    tmp_path: Path, field: str, value: object
) -> None:
    review_session.initialize(tmp_path, "change", contract())
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    snapshot[field] = value
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


def test_bot_identity_cannot_approve_for_or_erase_human(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    snapshot["reviews"] = [
        [
            {"commit_id": TEST_HEAD, "state": "CHANGES_REQUESTED", "user": {"login": "reviewer-a"}},
            {"commit_id": TEST_HEAD, "state": "APPROVED", "user": {"login": "reviewer-a[bot]"}},
        ]
    ]
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


@pytest.mark.parametrize(
    "disposition,expected",
    [("non_finding", "continue"), ("fixed", "investigate"), ("accepted_exception", "investigate")],
)
def test_final_dispositions_preserve_only_genuine_escapes(
    tmp_path: Path, disposition: str, expected: str
) -> None:
    review_session.initialize(tmp_path, "change", contract())
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


def test_avatar_noise_does_not_count_as_progress(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
    snapshot = complete_snapshot()
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    snapshot["reviews"][0][0]["user"]["avatar_url"] = "irrelevant"
    assert review_session.record_monitor_snapshot(tmp_path, "change", snapshot)["changed"] is False
    complete_session(tmp_path)
    assert review_session.status(tmp_path, "change")["action"] == "complete"


@pytest.mark.parametrize("error", [OSError("missing gh"), TypeError("null payload")])
def test_collection_failure_replaces_prior_green(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, error: Exception
) -> None:
    review_session.initialize(tmp_path, "change", contract())
    complete_session(tmp_path)

    def fail(*args: object) -> dict[str, object]:
        raise error

    monkeypatch.setattr(review_session, "gh_snapshot", fail)
    assert review_session.watch(tmp_path, "change", "nold-ai/changecost", 24, 0) == 1
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"


def test_old_observation_cannot_cross_same_head_epoch(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
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
    tmp_path: Path, nonfinding_seed: bool
) -> None:
    review_session.initialize(tmp_path, "change", contract())
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
    tmp_path: Path, field: str, entries: object
) -> None:
    review_session.initialize(tmp_path, "change", contract())
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
    tmp_path: Path, login: str, state: object
) -> None:
    review_session.initialize(tmp_path, "change", contract())
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    snapshot["reviews"][0].extend(
        [
            {"commit_id": TEST_HEAD, "state": "CHANGES_REQUESTED", "user": {"login": login}},
            {"commit_id": TEST_HEAD, "state": state, "user": {"login": login}},
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
    tmp_path: Path, login: str, later: str
) -> None:
    review_session.initialize(tmp_path, "change", contract())
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    snapshot["reviews"] += [
        [
            {
                "id": 100,
                "commit_id": TEST_HEAD,
                "state": "CHANGES_REQUESTED",
                "user": {"login": login},
            }
        ],
        [{"id": 101, "commit_id": TEST_HEAD, "state": later, "user": {"login": login}}],
    ]
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
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


def test_original_rejection_dismissal_is_recomputed_from_fresh_snapshot(tmp_path: Path) -> None:
    review_session.initialize(tmp_path, "change", contract())
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    rejection = {
        "id": 100,
        "commit_id": TEST_HEAD,
        "state": "CHANGES_REQUESTED",
        "user": {"login": "reviewer-a"},
    }
    snapshot["reviews"] += [
        [rejection],
        [
            {
                "id": 101,
                "commit_id": TEST_HEAD,
                "state": "COMMENTED",
                "user": {"login": "reviewer-a"},
            }
        ],
    ]
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "incomplete"
    rejection["state"] = "DISMISSED"
    review_session.record_monitor_snapshot(tmp_path, "change", snapshot)
    assert review_session.status(tmp_path, "change")["action"] == "complete"


@pytest.mark.parametrize(
    "other_login,old_head",
    [("other-human", False), ("reviewer-a[bot]", False), ("reviewer-a", True)],
)
def test_other_identity_or_head_cannot_clear_objection(
    tmp_path: Path, other_login: str, old_head: bool
) -> None:
    review_session.initialize(tmp_path, "change", contract())
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    snapshot["reviews"] += [
        [{"commit_id": TEST_HEAD, "state": "CHANGES_REQUESTED", "user": {"login": "reviewer-a"}}],
        [
            {
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
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], action: str
) -> None:
    review_session.initialize(tmp_path, "change", contract())
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
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    review_session.initialize(tmp_path, "change", contract())
    review_session.record_monitor_snapshot(tmp_path, "change", complete_snapshot())
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
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    review_session.initialize(tmp_path, "change", contract())
    complete_session(tmp_path)
    snapshot = complete_snapshot()
    snapshot["comments"] = [[{"id": 1, "body": "new evidence"}]]
    monkeypatch.setattr(review_session, "gh_snapshot", lambda *args: snapshot)
    assert review_session.watch(tmp_path, "change", "nold-ai/changecost", 24, 0) == 0
    assert json.loads(capsys.readouterr().out)["packet"]["status"]["action"] == "complete"


def test_watch_timeout_preserves_incomplete_exit(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    review_session.initialize(tmp_path, "change", contract())
    review_session.record(
        tmp_path, "change", {"id": "pending", "kind": "scope_decision", "decision": "pending"}
    )
    assert review_session.watch_timeout(tmp_path, "change") == 1
    assert json.loads(capsys.readouterr().out)["action"] == "incomplete"
