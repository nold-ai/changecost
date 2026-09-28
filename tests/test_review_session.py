"""Behavioral tests for bounded, persisted review-session decisions."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from quality import review_session

TEST_HEAD = ""


@pytest.fixture(autouse=True)
def git_fixture(tmp_path: Path) -> None:
    global TEST_HEAD
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".gitignore").write_text(".changecost/\n")
    subprocess.run(["git", "-C", str(tmp_path), "add", ".gitignore"], check=True)
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
        "acceptance_criteria": ["review evidence is current"],
        "non_goals": ["host authentication"],
        "trust_boundary": "configuration validation only",
        "intended_files": {"quality/example.py": "abc"},
        "base": "a" * 40,
        "head": TEST_HEAD,
        "required_reviewers": ["reviewer-a"],
        "required_checks": ["ci"],
        "required_statuses": [],
    }


def complete_snapshot() -> dict[str, object]:
    return {
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
    monotonic = iter((0.0, 0.0, 59.0, 61.0))
    monkeypatch.setattr(
        review_session, "gh_snapshot", lambda repository, pull_request: calls.append(1) or snapshot
    )
    monkeypatch.setattr(review_session.time, "monotonic", lambda: next(monotonic))
    monkeypatch.setattr(review_session.time, "sleep", lambda seconds: None)
    assert review_session.watch(tmp_path, "change", "nold-ai/changecost", 22, 1) == 0
    assert len(calls) == 2


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
    snapshot["threads"] = [{"id": "t", "isOutdated": True, "isResolved": False}]
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
    review_session.initialize(tmp_path, "change", contract())
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
    for index in range(900):
        review_session.record(
            tmp_path, "change", {"id": f"time-{index}", "kind": "active_minutes", "minutes": 0.1}
        )
    assert review_session.load(tmp_path, "change")["active_minutes"] == 90
    assert review_session.status(tmp_path, "change")["action"] == "replan"
    complete_session(tmp_path)
    assert review_session.status(tmp_path, "change")["action"] == "complete"
    review_session.record(tmp_path, "change", {"id": "resume", "kind": "phase", "phase": "active"})
    assert review_session.status(tmp_path, "change")["action"] == "replan"
