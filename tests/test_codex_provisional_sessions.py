import json
from pathlib import Path
from typing import Any

import pytest

from tests.test_sessions_cli import Journey


def counter_row(total, **changes):
    usage: dict[str, Any] = dict.fromkeys(
        (
            "input_tokens",
            "cached_input_tokens",
            "cache_write_input_tokens",
            "output_tokens",
            "reasoning_output_tokens",
            "total_tokens",
        ),
        total,
    )
    usage.update(changes)
    return {
        "type": "event_msg",
        "payload": {
            "type": "token_count",
            "info": {
                "total_token_usage": usage,
                "last_token_usage": dict.fromkeys(usage, 7),
                "model_context_window": 258400,
            },
        },
    }


def source(
    tmp_path,
    totals=(150, 200, 200),
    identity="PRIVATE-session",
    version="0.163.0-alpha.10.2",
    source_kind: str | dict = "vscode",
):
    path = tmp_path / f"PRIVATE-{identity}.jsonl"
    rows = [
        {
            "type": "session_meta",
            "payload": {
                "id": identity,
                "session_id": f"PRIVATE-runtime-{identity}",
                "originator": "Codex Desktop",
                "cli_version": version,
                "source": source_kind,
                "cwd": "PRIVATE-directory",
                "prompt": "PRIVATE-prompt",
            },
        }
    ]
    rows.extend(counter_row(total) for total in totals)
    path.write_bytes(b"".join(json.dumps(row).encode() + b"\n" for row in rows))
    return path


def start(j, name, guess=None, *, ok=True, source_kind="codex"):
    args = [
        "start",
        name,
        "--source",
        source_kind,
        "--task-kind",
        "feature",
        "--context",
        "python/cli",
    ]
    if guess is not None:
        args += ["--guess", str(guess)]
    return j.invoke(*args, ok=ok)


def capture(
    j,
    path: Path,
    name="a",
    *,
    revision=None,
    reason=None,
    outcome="completed",
    repository="repo",
    ok=True,
):
    args = [
        "capture-codex",
        name,
        "--file",
        path,
        "--repository-id",
        repository,
        "--outcome",
        outcome,
    ]
    if revision is not None:
        args += ["--revision", str(revision)]
    if reason is not None:
        args += ["--reason", reason]
    return j.invoke(*args, ok=ok)


def test_actual_cli_capture_then_next_forecast_keeps_provisional_authority(tmp_path):
    j = Journey(tmp_path)
    path = source(tmp_path)
    first = start(j, "a", 100)
    assert first["manual"] is False
    assert first["forecast"]["amount"] == "100"
    result = capture(j, path)
    assert result["capture"]["snapshot"]["reported_tokens"] == 200
    assert result["error"]["signed_tokens"] == "-100"
    assert result["error"]["absolute_percentage_error"]["rounded_decimal"] == "50.000000"
    assert result["capture"]["snapshot"]["counter_snapshot_count"] == 3
    assert result["measurement"] is None
    assert result["core_numeric_authority"] is result["billing_authority"] is False
    snapshot = result["capture"]["snapshot"]
    assert all(
        snapshot[key] == "unknown"
        for key in ("coverage", "completeness", "finality", "subagent_inclusion")
    )
    assert snapshot["producer_verified"] is False
    second = start(j, "b")
    assert second["forecast"]["amount"] == "200"
    assert second["forecast"]["sample_count"] == 1
    assert second["forecast"]["inputs"][0]["revision"] == 1
    history = j.invoke("history", "--source", "codex")
    assert history["learning_count"] == 1
    assert history["evaluation"]["included_count"] == 1
    assert j.invoke("history")["sessions"] == []
    assert j.start("manual")["forecast"]["source"] == "unknown"


def append(path, total):
    with path.open("ab") as stream:
        stream.write(json.dumps(counter_row(total)).encode() + b"\n")


def test_revision_retry_append_frozen_inputs_and_one_learning_attempt(tmp_path):
    j = Journey(tmp_path)
    path = source(tmp_path)
    original = path.read_bytes()
    start(j, "a", 100)
    first = capture(j, path)
    before = j.db.read_bytes()
    renamed = tmp_path / "PRIVATE-renamed"
    renamed.write_bytes(original)
    assert capture(j, renamed) == first
    assert j.db.read_bytes() == before
    frozen = start(j, "b")["forecast"]
    append(path, 300)
    second_bytes = path.read_bytes()
    second = capture(j, path, revision=1, reason="resumed")
    assert second["operation_revision"] == 2
    assert [c["snapshot"]["reported_tokens"] for c in second["captures"]] == [200, 300]
    assert j.invoke("show", "b")["forecast"] == frozen
    assert frozen["inputs"][0]["reported_tokens"] == 200
    assert frozen["inputs"][0]["source_sha256"] == first["capture"]["snapshot"]["source_sha256"]
    append(path, 400)
    capture(j, path, revision=2, reason="resumed again")
    before = j.db.read_bytes()
    old_first = capture(j, renamed)
    assert old_first["operation_revision"] == 1
    assert old_first["capture"]["revision"] == 3
    renamed.write_bytes(second_bytes)
    old_second = capture(j, renamed, revision=1, reason="resumed")
    assert old_second["operation_revision"] == 2 and old_second["capture"]["revision"] == 3
    assert j.db.read_bytes() == before
    next_forecast = start(j, "c")["forecast"]
    assert next_forecast["sample_count"] == 1
    assert next_forecast["amount"] == "400"
    assert j.invoke("history", "--source", "codex")["learning_count"] == 1


def test_manual_source_measurement_and_cohort_exclusions(tmp_path):
    j = Journey(tmp_path)
    j.start("manual", 50)
    j.finish("manual", 500)
    native = start(j, "a", 100)
    assert native["forecast"]["source"] == "user_guess"
    before = j.db.read_bytes()
    assert (
        j.invoke("finish", "a", "--tokens", 200, "--outcome", "completed", ok=False)["code"]
        == "session_conflict"
    )
    assert (
        j.invoke(
            "correct",
            "a",
            "--tokens",
            200,
            "--outcome",
            "completed",
            "--revision",
            1,
            "--reason",
            "wrong lane",
            ok=False,
        )["code"]
        == "session_conflict"
    )
    assert start(j, "manual", 50, ok=False)["code"] == "session_conflict"
    assert (
        j.invoke(
            "start",
            "a",
            "--task-kind",
            "feature",
            "--context",
            "python/cli",
            "--guess",
            100,
            ok=False,
        )["code"]
        == "session_conflict"
    )
    assert j.db.read_bytes() == before
    assert capture(j, tmp_path / "missing", "manual", ok=False)["code"] == "session_conflict"
    assert j.db.read_bytes() == before
    capture(j, source(tmp_path))
    assert j.start("next-manual")["forecast"]["amount"] == "500"
    assert {s["session_id"] for s in j.invoke("history")["sessions"]} == {"manual", "next-manual"}
    assert j.invoke("history", "--source", "codex")["evaluation"]["included_count"] == 1


def test_identity_is_global_and_repository_cannot_split_training(tmp_path):
    j = Journey(tmp_path)
    path = source(tmp_path)
    start(j, "a")
    start(j, "b")
    capture(j, path)
    before = j.db.read_bytes()
    assert capture(j, path, "b", repository="different", ok=False)["code"] == "session_conflict"
    assert (
        capture(j, path, repository="different", revision=1, reason="relabel", ok=False)["code"]
        == "session_conflict"
    )
    assert j.db.read_bytes() == before
    other = source(tmp_path, identity="PRIVATE-session", version="0.163.0-alpha.11.2")
    assert capture(j, other, "b", ok=False)["code"] == "session_conflict"
    assert j.db.read_bytes() == before


@pytest.mark.parametrize("version", ["0.163.0-alpha.10.2", "0.163.0-alpha.11.2"])
def test_distinct_runtime_identity_preserves_thread_deduplication(tmp_path, version):
    j = Journey(tmp_path)
    path = source(tmp_path, version=version)
    start(j, "a", 100)
    first = capture(j, path)
    assert first["capture"]["snapshot"]["reported_tokens"] == 200
    forecast = start(j, "b")["forecast"]
    assert forecast["amount"] == "200" and forecast["sample_count"] == 1
    rows = [json.loads(line) for line in path.read_bytes().splitlines()]
    rows[0]["payload"]["session_id"] = "PRIVATE-different-runtime"
    other = tmp_path / "PRIVATE-renamed-runtime.jsonl"
    other.write_bytes(b"".join(json.dumps(row).encode() + b"\n" for row in rows))
    before = j.db.read_bytes()
    assert capture(j, other, "b", ok=False)["code"] == "session_conflict"
    assert j.db.read_bytes() == before
    assert j.invoke("history", "--source", "codex")["learning_count"] == 1


@pytest.mark.parametrize("runtime_identity", [None, 1, True, [], {}, "", " ", "x" * 513])
def test_malformed_runtime_identity_rejects_without_mutation(tmp_path, runtime_identity):
    j = Journey(tmp_path)
    path = source(tmp_path)
    rows = [json.loads(line) for line in path.read_bytes().splitlines()]
    rows[0]["payload"]["session_id"] = runtime_identity
    raw = b"".join(json.dumps(row).encode() + b"\n" for row in rows)
    path.write_bytes(raw)
    start(j, "a")
    before = j.db.read_bytes()
    failed = capture(j, path, ok=False)
    assert failed["code"] == "missing_source_identity"
    assert j.db.read_bytes() == before and path.read_bytes() == raw
    assert "PRIVATE" not in json.dumps(failed)


@pytest.mark.parametrize("runtime_identity", [None, "PRIVATE-session", "x" * 512])
def test_optional_runtime_identity_preserves_compatible_headers(tmp_path, runtime_identity):
    j = Journey(tmp_path)
    path = source(tmp_path)
    rows = [json.loads(line) for line in path.read_bytes().splitlines()]
    if runtime_identity is None:
        rows[0]["payload"].pop("session_id")
    else:
        rows[0]["payload"]["session_id"] = runtime_identity
    path.write_bytes(b"".join(json.dumps(row).encode() + b"\n" for row in rows))
    start(j, "a")
    assert capture(j, path)["capture"]["snapshot"]["reported_tokens"] == 200


def test_unknown_forecast_trains_without_entering_mae_and_zero_retains_exact_error(tmp_path):
    j = Journey(tmp_path)
    start(j, "a")
    first = capture(j, source(tmp_path, totals=(0,)))
    assert first["error"]["excluded_reason"] == "unknown_forecast"
    assert start(j, "b")["forecast"]["amount"] == "0"
    second = capture(j, source(tmp_path, totals=(1,), identity="PRIVATE-second"), "b")
    assert second["error"]["absolute_tokens"] == "1"
    assert start(j, "c")["forecast"]["amount"] == "0.5"
    zero = capture(
        j, source(tmp_path, totals=(0,), identity="PRIVATE-third"), "c", outcome="failed"
    )
    assert zero["error"]["absolute_tokens"] == "0.5"
    assert zero["error"]["absolute_percentage_error"] is None
    history = j.invoke("history", "--source", "codex")
    assert history["learning_count"] == 3
    assert history["evaluation"]["included_count"] == 2
    assert history["evaluation"]["mean_absolute_error"]["numerator"] == "1.5"
    assert history["evaluation"]["mean_absolute_error"]["denominator"] == 2
    assert history["evaluation"]["excluded"] == {"unknown_forecast": 1}


def test_observed_versions_and_source_variants_share_semantic_cohort(tmp_path):
    j = Journey(tmp_path)
    start(j, "a", 100)
    capture(j, source(tmp_path))
    start(j, "b")
    child = {"subagent": {"thread_spawn": {"parent_thread_id": "PRIVATE-parent", "depth": 1}}}
    capture(
        j,
        source(tmp_path, (300,), "PRIVATE-child", "0.163.0-alpha.11.2", child),
        "b",
        outcome="abandoned",
    )
    third = start(j, "c")["forecast"]
    assert third["sample_count"] == 2 and third["amount"] == "250"
    assert {r["producer_version"] for r in third["inputs"]} == {
        "0.163.0-alpha.10.2",
        "0.163.0-alpha.11.2",
    }
    assert {r["source_kind"] for r in third["inputs"]} == {"vscode", "subagent.thread_spawn"}
    assert (
        j.invoke(
            "start",
            "other",
            "--source",
            "codex",
            "--task-kind",
            "different",
            "--context",
            "python/cli",
        )["forecast"]["amount"]
        is None
    )
    assert (
        j.invoke(
            "start",
            "other-context",
            "--source",
            "codex",
            "--task-kind",
            "feature",
            "--context",
            "other",
        )["forecast"]["amount"]
        is None
    )


def test_changed_capture_needs_explicit_current_predecessor_and_prefix(tmp_path):
    j = Journey(tmp_path)
    path = source(tmp_path)
    start(j, "a")
    first_bytes = path.read_bytes()
    capture(j, path)
    before = j.db.read_bytes()
    assert capture(j, path, outcome="failed", ok=False)["code"] == "session_conflict"
    assert j.db.read_bytes() == before
    append(path, 300)
    assert capture(j, path, ok=False)["code"] == "session_conflict"
    assert j.db.read_bytes() == before
    capture(j, path, revision=1, reason="resumed")
    before = j.db.read_bytes()
    append(path, 400)
    assert capture(j, path, revision=1, reason="stale", ok=False)["code"] == "session_conflict"
    assert j.db.read_bytes() == before
    path.write_bytes(path.read_bytes().replace(b"PRIVATE-prompt", b"PRIVATE-change"))
    assert capture(j, path, revision=2, reason="rewrite", ok=False)["code"] == "session_conflict"
    path.write_bytes(first_bytes)
    assert capture(j, path, revision=2, reason="truncated", ok=False)["code"] == "session_conflict"
    assert j.db.read_bytes() == before


def test_byte_identical_explicit_outcome_correction_and_no_new_counter_append(tmp_path):
    j = Journey(tmp_path)
    path = source(tmp_path)
    start(j, "a", 300)
    capture(j, path)
    second = capture(j, path, revision=1, reason="outcome corrected", outcome="failed")
    assert second["capture"]["outcome"] == "failed"
    with path.open("ab") as stream:
        stream.write(b'{"type":"event_msg","payload":{"type":"task_complete"}}\n')
    third = capture(j, path, revision=2, reason="new source snapshot", outcome="failed")
    assert third["capture"]["snapshot"]["reported_tokens"] == 200
    assert start(j, "b")["forecast"]["sample_count"] == 1


@pytest.mark.parametrize(
    "mutation,code",
    [
        ("boolean", "unsupported_source_quantity"),
        ("negative", "unsupported_source_quantity"),
        ("overflow", "unsupported_source_quantity"),
        ("decrease", "source_counter_decreased"),
        ("missing-id", "missing_source_identity"),
        ("duplicate-header", "unsupported_source_header"),
        ("version", "unsupported_source_header"),
        ("originator", "unsupported_source_header"),
        ("source", "unsupported_source_header"),
        ("invalid-info", "unsupported_source_shape"),
        ("missing-counter", "missing_source_counter"),
        ("categories", "unsupported_source_categories"),
        ("duplicate-member", "invalid_source_record"),
        ("nonfinite", "invalid_source_record"),
        ("huge-number", "source_numeric_limit"),
        ("float-overflow", "invalid_source_number"),
        ("depth", "source_depth_limit"),
        ("invalid-json", "invalid_source_record"),
    ],
)
def test_source_rejections_are_safe_and_leave_all_bytes_unchanged(tmp_path, mutation, code):
    j = Journey(tmp_path)
    path = source(tmp_path)
    rows = [json.loads(line) for line in path.read_bytes().splitlines()]
    if mutation in {"boolean", "negative", "overflow"}:
        rows[-1]["payload"]["info"]["total_token_usage"]["total_tokens"] = {
            "boolean": True,
            "negative": -1,
            "overflow": 2**63,
        }[mutation]
    elif mutation == "decrease":
        rows.append(counter_row(1))
    elif mutation == "missing-id":
        rows[0]["payload"].pop("id")
    elif mutation == "duplicate-header":
        rows.append(rows[0])
    elif mutation in {"version", "originator", "source"}:
        rows[0]["payload"][
            {"version": "cli_version", "originator": "originator", "source": "source"}[mutation]
        ] = "PRIVATE-unsupported"
    elif mutation == "invalid-info":
        rows[-1]["payload"]["info"] = []
    elif mutation == "missing-counter":
        rows = rows[:1]
    elif mutation == "categories":
        rows[-1]["payload"]["info"]["total_token_usage"]["extra"] = 1
    raw = b"".join(json.dumps(row).encode() + b"\n" for row in rows)
    extras = {
        "duplicate-member": b'{"type":"event_msg","payload":{"PRIVATE":1,"PRIVATE":2}}\n',
        "nonfinite": b'{"type":"event_msg","payload":{"PRIVATE":NaN}}\n',
        "float-overflow": b'{"type":"event_msg","payload":{"PRIVATE":1e9999}}\n',
        "huge-number": b'{"type":"event_msg","payload":{"PRIVATE":' + b"1" * 4097 + b"}}\n",
        "depth": b'{"type":"event_msg","payload":{"PRIVATE":'
        + b"[" * 33
        + b"0"
        + b"]" * 33
        + b"}}\n",
        "invalid-json": b"PRIVATE invalid record\n",
    }
    raw += extras.get(mutation, b"")
    path.write_bytes(raw)
    start(j, "a")
    before = j.db.read_bytes()
    failed = capture(j, path, ok=False)
    assert failed["code"] == code
    assert j.db.read_bytes() == before and path.read_bytes() == raw
    assert "PRIVATE" not in json.dumps(failed) and str(tmp_path) not in json.dumps(failed)


def test_null_counter_info_is_ignored_and_zero_signed64_bounds_are_supported(tmp_path):
    from changecost.codex_session_counter import read_codex_counter

    path = source(tmp_path, (0, 2**63 - 1))
    with path.open("ab") as stream:
        stream.write(b'{"type":"event_msg","payload":{"type":"token_count","info":null}}\n')
    snapshot, _ = read_codex_counter(path)
    assert snapshot.reported_tokens == 2**63 - 1 and snapshot.counter_snapshot_count == 2


def test_missing_and_manual_targets_reject_before_source_acquisition(tmp_path, monkeypatch):
    from changecost import sessions

    monkeypatch.setattr(
        sessions, "read_codex_counter", lambda *a, **k: pytest.fail("unexpected acquisition")
    )
    j = Journey(tmp_path)
    assert capture(j, tmp_path / "missing", ok=False)["code"] == "session_not_found"
    assert not j.db.exists()
    j.start("a")
    before = j.db.read_bytes()
    assert capture(j, tmp_path / "missing", ok=False)["code"] == "session_conflict"
    assert j.db.read_bytes() == before


def test_unsafe_sources_byte_row_limits_and_stability(tmp_path, monkeypatch):
    from changecost import codex_session_counter as reader

    path = source(tmp_path)
    link = tmp_path / "link"
    link.symlink_to(path)
    with pytest.raises(reader.CounterError, match="unsafe_source"):
        reader.read_codex_counter(link)
    directory_link = tmp_path / "dir-link"
    directory_link.symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(reader.CounterError, match="unsafe_source"):
        reader.read_codex_counter(directory_link / path.name)
    with monkeypatch.context() as patch:
        patch.setattr(reader, "MAX_BYTES", path.stat().st_size - 1)
        with pytest.raises(reader.CounterError, match="source_byte_limit"):
            reader.read_codex_counter(path)
    with monkeypatch.context() as patch:
        patch.setattr(reader, "MAX_RECORDS", 2)
        with pytest.raises(reader.CounterError, match="source_record_limit"):
            reader.read_codex_counter(path)
    accept = reader._Projection.accept

    def changed(self, row, ordinal):
        accept(self, row, ordinal)
        if ordinal == 0:
            with path.open("ab") as stream:
                stream.write(b'{"type":"event_msg","payload":{"type":"task_complete"}}\n')

    monkeypatch.setattr(reader._Projection, "accept", changed)
    with pytest.raises(reader.CounterError, match="unstable_source"):
        reader.read_codex_counter(path)


def test_source_exceeding_finite_bounds_streams_without_widening_exact_reader(tmp_path):
    from changecost import codex_local
    from changecost.codex_session_counter import read_codex_counter

    path = source(tmp_path, (123,))
    with path.open("ab") as stream:
        filler = (
            json.dumps({"type": "response_item", "payload": {"text": "PRIVATE" * 1000}}).encode()
            + b"\n"
        )
        for _ in range(5700):
            stream.write(filler)
    assert path.stat().st_size > 34 * 1024 * 1024
    snapshot, prefix = read_codex_counter(path, prefix_length=5)
    assert snapshot.reported_tokens == 123 and snapshot.source_record_count == 5702
    import hashlib

    assert prefix == hashlib.sha256(path.read_bytes()[:5]).hexdigest()
    with pytest.raises(codex_local.NativeImportError, match="source_byte_limit"):
        codex_local.read_codex_file(codex_local.select_codex_file("repo", path))
    assert codex_local.MAX_BYTES == 10485760 and codex_local.MAX_RECORDS == 10000


def test_safe_concise_human_output_and_stored_reports_need_no_source(tmp_path, monkeypatch):
    from changecost import sessions

    j = Journey(tmp_path)
    path = source(tmp_path)
    name = "a\x1b[31m\u2028private-label"
    start(j, name, 100)
    capture(j, path, name)
    path.unlink()
    monkeypatch.setattr(
        sessions, "read_codex_counter", lambda *a, **k: pytest.fail("unexpected read")
    )
    before = j.db.read_bytes()
    human = j.invoke("show", name, human=True)
    history = j.invoke("history", "--source", "codex", human=True)
    report = j.invoke("show", name)
    assert len(human.splitlines()) < 12
    assert "Codex provisional" in human and "Source-reported lifetime counter 200 tokens" in human
    assert "Estimate low" in human and "50.00%" in human and "Revision 1" in human
    assert "\\u001b[31m" in human and "\\u2028" in human and "\x1b" not in human
    assert "Learning attempts 1" in history and "evaluated 1" in history
    assert "Coverage UNKNOWN" in human and "Producer claim unverified" in human
    assert "manual: True" not in human and "source_sha256" not in human
    combined = json.dumps(report) + human + history
    assert "PRIVATE" not in combined and str(tmp_path) not in combined
    assert b"PRIVATE" not in j.db.read_bytes() and j.db.read_bytes() == before


def test_v1_v2_reads_and_native_upgrade_preserve_history_and_finite_observe_on_v3(
    tmp_path, monkeypatch
):
    from changecost import codex_local
    from tests.native_fixtures import synthetic_source
    from tests.test_codex_session_observations import observe, rows, version

    j = Journey(tmp_path)
    j.start("manual", 100)
    j.finish("manual", 200)
    original = j.invoke("show", "manual")
    before = j.db.read_bytes()
    assert j.invoke("history", "--source", "codex")["sessions"] == []
    assert j.db.read_bytes() == before and version(j.db) == 1
    finite, _, envelope = synthetic_source(tmp_path)
    monkeypatch.setattr(codex_local, "_packaged_admission", lambda: envelope)
    observe(j, finite, "manual")
    assert version(j.db) == 2
    historical = rows(j.db, ("sessions", "measurements", "native_snapshots", "native_links"))
    before = j.db.read_bytes()
    j.invoke("history", "--source", "codex")
    assert j.db.read_bytes() == before and version(j.db) == 2
    start(j, "a", 100)
    assert version(j.db) == 3
    assert rows(j.db, ("measurements", "native_snapshots", "native_links")) == {
        k: historical[k] for k in ("measurements", "native_snapshots", "native_links")
    }
    assert j.invoke("show", "manual")["forecast"] == original["forecast"]
    observed = observe(j, finite, "a")
    assert (
        observed["manual"] is False and observed["native_diagnostics"]["learning_eligible"] is False
    )
    assert version(j.db) == 3
    capture(j, source(tmp_path))
    assert j.start("next-manual")["forecast"]["amount"] == "200"


@pytest.mark.parametrize("phase", ["migration", "capture"])
def test_failed_migration_or_capture_rolls_back_every_byte(tmp_path, monkeypatch, phase):
    from changecost.sessions import CaptureOperation, Sessions
    from tests.test_codex_session_observations import version

    j = Journey(tmp_path)
    j.start("manual", 100)
    j.finish("manual", 200)
    if phase == "migration":
        before = j.db.read_bytes()
        migrate = Sessions.migrate_codex

        def fail_migration(connection):
            migrate(connection)
            raise RuntimeError("interrupted")

        monkeypatch.setattr(Sessions, "migrate_codex", staticmethod(fail_migration))
        with pytest.raises(RuntimeError, match="interrupted"):
            Sessions(j.db).start("a", "feature", "python/cli", source="codex")
        assert version(j.db) == 1
    else:
        start(j, "a")
        before = j.db.read_bytes()
        insert = Sessions.insert_capture

        def fail_capture(self, *args):
            insert(self, *args)
            raise RuntimeError("interrupted")

        monkeypatch.setattr(Sessions, "insert_capture", fail_capture)
        with pytest.raises(RuntimeError, match="interrupted"):
            Sessions(j.db).capture_codex(
                "a", source(tmp_path), "repo", CaptureOperation("completed")
            )
    assert j.db.read_bytes() == before


def test_concurrent_captures_serialize_and_reject_conflicting_revision(tmp_path, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    from changecost import sessions
    from changecost.sessions import CaptureOperation, SessionError, Sessions

    j = Journey(tmp_path)
    start(j, "a")
    path = source(tmp_path)
    barrier = Barrier(2)
    reader = sessions.read_codex_counter

    def together(*args, **kwargs):
        result = reader(*args, **kwargs)
        barrier.wait(timeout=10)
        return result

    monkeypatch.setattr(sessions, "read_codex_counter", together)

    def run(outcome):
        try:
            return Sessions(j.db).capture_codex("a", path, "repo", CaptureOperation(outcome))
        except SessionError as exc:
            return exc.code

    with ThreadPoolExecutor(max_workers=2) as executor:
        result = list(executor.map(run, ["completed", "failed"]))
    assert sum(isinstance(value, dict) for value in result) == 1
    assert "session_conflict" in result
    assert len(j.invoke("show", "a")["captures"]) == 1
    assert j.invoke("history", "--source", "codex")["learning_count"] == 1
    assert start(j, "b")["forecast"]["sample_count"] == 1


def test_full_row_bound_and_safe_ordinals_above_finite_limit(tmp_path):
    from changecost.codex_session_counter import MAX_RECORDS, CounterError, read_codex_counter

    path = source(tmp_path, (17,))
    valid = path.read_bytes()
    filler = b'{"type":"event_msg","payload":{"type":"task_complete"}}\n'
    path.write_bytes(valid + filler * (MAX_RECORDS - 2))
    snapshot, _ = read_codex_counter(path)
    assert snapshot.source_record_count == MAX_RECORDS
    with path.open("ab") as stream:
        stream.write(filler)
    with pytest.raises(CounterError, match="source_record_limit"):
        read_codex_counter(path)
    path.write_bytes(valid + filler * 10_001 + b"PRIVATE invalid\n")
    with pytest.raises(CounterError) as failure:
        read_codex_counter(path)
    assert failure.value.report() == dict(
        schema="changecost/error-v1",
        code="invalid_source_record",
        message="provisional Codex source rejected",
        ordinal=10_003,
    )


def test_concurrent_identical_capture_creates_one_revision_and_append_conflict_rolls_back(
    tmp_path, monkeypatch
):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    from changecost import sessions
    from changecost.sessions import CaptureOperation, Sessions

    j = Journey(tmp_path)
    start(j, "a")
    path = source(tmp_path)
    barrier = Barrier(2)
    reader = sessions.read_codex_counter

    def together(*args, **kwargs):
        result = reader(*args, **kwargs)
        barrier.wait(timeout=10)
        return result

    with monkeypatch.context() as patch:
        patch.setattr(sessions, "read_codex_counter", together)
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(
                executor.map(
                    lambda _: Sessions(j.db).capture_codex(
                        "a", path, "repo", CaptureOperation("completed")
                    ),
                    range(2),
                )
            )
    assert results[0] == results[1]
    assert len(results[0]["captures"]) == 1
    append(path, 300)
    capture(j, path, revision=1, reason="resumed")
    before = j.db.read_bytes()
    assert (
        capture(j, path, revision=1, reason="conflicting", ok=False)["code"] == "session_conflict"
    )
    assert j.db.read_bytes() == before


def test_invalid_source_options_help_and_foreign_database_do_not_mutate(tmp_path):
    import sqlite3

    j = Journey(tmp_path)
    j.invoke("capture-codex", "--help", human=True)
    assert not j.db.exists()
    assert start(j, "a", source_kind="other", ok=False)["code"] == "invalid_request"
    assert not j.db.exists()
    start(j, "a")
    before = j.db.read_bytes()
    assert (
        capture(j, tmp_path / "unread", revision=1, reason="missing", ok=False)["code"]
        == "session_conflict"
    )
    assert (
        capture(j, tmp_path / "unread", reason="unexpected", ok=False)["code"] == "invalid_request"
    )
    assert capture(j, tmp_path / "unread", repository="", ok=False)["code"] == "invalid_request"
    assert j.db.read_bytes() == before
    with sqlite3.connect(j.db) as connection:
        connection.execute("PRAGMA user_version=99")
    before = j.db.read_bytes()
    assert capture(j, tmp_path / "unread", ok=False)["code"] == "session_store_unrecognized"
    assert j.db.read_bytes() == before
