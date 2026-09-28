"""Behavioral tests for bounded, persisted review-session decisions."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from quality import review_session


def contract() -> dict[str, object]:
    return {
        "requirements": ["tests pass"],
        "acceptance_criteria": ["review evidence is current"],
        "non_goals": ["host authentication"],
        "trust_boundary": "configuration validation only",
        "intended_files": {"quality/example.py": "abc"},
        "base": "a" * 40,
        "head": "b" * 40,
        "required_reviewers": ["reviewer-a"],
    }


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
    monotonic = iter((0.0, 0.0, 61.0))
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
