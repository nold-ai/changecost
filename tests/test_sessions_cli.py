import json
import sqlite3
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from typing import Any

import pytest
from typer.testing import CliRunner

from changecost.cli import app


class Journey:
    def __init__(self, directory):
        self.db = directory / "sessions.sqlite3"
        self.core = directory / "core.sqlite3"

    def invoke(self, *args, ok=True, human=False) -> Any:
        result = CliRunner().invoke(
            app,
            [
                "--db",
                str(self.core),
                "--format",
                "human" if human else "json",
                "session",
                "--session-db",
                str(self.db),
                *map(str, args),
            ],
        )
        assert result.exit_code == (0 if ok else 2), result.output
        assert not self.core.exists()
        return result.stdout if human else json.loads(result.stdout if ok else result.stderr)

    def start(self, name, guess=None, kind="feature", context="python/cli"):
        args = ["start", name, "--task-kind", kind, "--context", context]
        if guess is not None:
            args += ["--guess", str(guess)]
        return self.invoke(*args)

    def finish(self, name, tokens, outcome="completed", coverage="declared_session_total"):
        return self.invoke(
            "finish", name, "--tokens", tokens, "--outcome", outcome, "--coverage", coverage
        )

    def correct(self, name, tokens, revision, reason="measurement corrected", ok=True):
        return self.invoke(
            "correct",
            name,
            "--tokens",
            tokens,
            "--revision",
            revision,
            "--reason",
            reason,
            "--outcome",
            "completed",
            ok=ok,
        )


def assert_manual_history_evaluation(history):
    assert history["evaluation"]["included_count"] == 3
    assert history["evaluation"]["mean_absolute_error"]["numerator"] == "900"
    assert history["evaluation"]["mean_absolute_error"]["denominator"] == 3
    assert history["evaluation"]["mean_absolute_error"]["rounded_decimal"] == "300.000000"
    assert history["evaluation"]["excluded"] == {"pending": 1}
    assert history["manual"] is True and history["calibrated"] is False
    assert history["unit"] == "total_tokens"


def assert_corrected_measurement(measured):
    assert [m["tokens"] for m in measured["measurements"]] == [200, 300]
    assert measured["measurement"]["tokens"] == 300
    assert measured["error"]["signed_tokens"] == "-200"
    assert measured["error"]["absolute_percentage_error"]["rounded_decimal"] == "66.666667"


def assert_partial_history_evaluation(history):
    assert len(history["sessions"]) == 6
    assert history["evaluation"]["included_count"] == 2
    assert history["evaluation"]["excluded"] == {
        "unknown_forecast": 1,
        "partial_measurement": 1,
        "pending": 2,
    }
    assert history["evaluation"]["mean_absolute_error"]["numerator"] == "125"
    assert history["evaluation"]["mean_absolute_error"]["denominator"] == 2


def test_actual_cli_improves_then_worsens_and_keeps_old_forecasts(tmp_path):
    j = Journey(tmp_path)
    forecasts = []
    errors = []
    for name, tokens in [("one", 200), ("two", 200), ("three", 1000)]:
        started = j.start(name, guess=100 if name == "one" else None)
        forecasts.append(started["forecast"]["amount"])
        finished = j.finish(name, tokens)
        errors.append(finished["error"]["absolute_tokens"])
    assert forecasts == ["100", "200", "200"]
    assert errors == ["100", "0", "800"]
    fourth = j.start("four")
    assert fourth["forecast"]["amount"] == "200"
    assert fourth["forecast"]["sample_count"] == 3
    assert fourth["forecast"]["summary"] == {"minimum": "200", "median": "200", "maximum": "1000"}
    history = j.invoke("history")
    assert_manual_history_evaluation(history)
    assert j.invoke("show", "one")["forecast"]["amount"] == "100"


def test_revisions_preserve_snapshots_and_retry_identity(tmp_path):
    j = Journey(tmp_path)
    original = j.start("a", guess=100)
    assert j.start("a", guess=100) == original
    j.finish("a", 200)
    before = j.start("b")
    assert before["forecast"]["inputs"] == [
        {"session_id": "a", "revision": 1, "tokens": 200, "outcome": "completed"}
    ]
    corrected = j.correct("a", 300, 1)
    assert corrected["operation_revision"] == 2
    assert j.correct("a", 300, 1) == corrected
    assert j.correct("a", 400, 1, ok=False)["code"] == "session_conflict"
    assert (
        j.invoke("finish", "a", "--tokens", 999, "--outcome", "completed", ok=False)["code"]
        == "session_conflict"
    )
    assert j.finish("a", 200)["operation_revision"] == 1
    assert j.start("a", guess=100)["forecast"] == original["forecast"]
    assert (
        j.invoke("start", "a", "--task-kind", "other", "--context", "python/cli", ok=False)["code"]
        == "session_conflict"
    )
    assert j.start("c")["forecast"]["inputs"][0]["revision"] == 2
    assert j.invoke("show", "b")["forecast"] == before["forecast"]
    measured = j.invoke("show", "a")
    assert_corrected_measurement(measured)
    assert j.start("c")["forecast"]["amount"] == "300"


def test_partials_unknown_pending_zero_and_cohort_filters(tmp_path):
    j = Journey(tmp_path)
    assert j.start("unknown")["forecast"]["source"] == "unknown"
    j.finish("unknown", 50)
    j.start("partial", guess=100)
    partial = j.finish("partial", 999, coverage="partial")
    assert partial["error"]["excluded_reason"] == "partial_measurement"
    assert partial["error"]["absolute_tokens"] is None
    j.start("pending")
    zero = j.start("zero")
    assert zero["forecast"]["amount"] == "50"
    assert zero["forecast"]["sample_count"] == 1
    measured = j.finish("zero", 0, outcome="failed")
    assert measured["error"]["absolute_tokens"] == "50"
    assert measured["error"]["absolute_percentage_error"] is None
    j.start("abandoned")
    j.finish("abandoned", 100, outcome="abandoned")
    learned = j.start("learned")
    assert learned["forecast"]["sample_count"] == 3
    assert learned["forecast"]["outcomes"] == {"completed": 1, "failed": 1, "abandoned": 1}
    assert j.start("other-context", context="python/api")["forecast"]["source"] == "unknown"
    assert j.start("other-kind", kind="bug-fix")["forecast"]["source"] == "unknown"
    history = j.invoke("history", "--task-kind", "feature", "--context", "python/cli")
    assert_partial_history_evaluation(history)


def test_partial_correction_changes_future_eligibility_only(tmp_path):
    j = Journey(tmp_path)
    j.start("a", 100)
    j.finish("a", 500, coverage="partial")
    unknown = j.start("b")
    assert unknown["forecast"]["amount"] is None
    j.correct("a", 300, 1)
    assert j.start("c")["forecast"]["amount"] == "300"
    assert j.invoke("show", "b")["forecast"] == unknown["forecast"]
    j.invoke(
        "correct",
        "a",
        "--tokens",
        400,
        "--revision",
        2,
        "--reason",
        "partial now",
        "--outcome",
        "failed",
        "--coverage",
        "partial",
    )
    assert j.start("d")["forecast"]["amount"] is None
    assert j.invoke("history")["evaluation"]["included_count"] == 0


@pytest.mark.parametrize(
    "args",
    [
        ["--help"],
        ["start", "--help"],
        ["finish", "--help"],
        ["start", "bad", "--task-kind", "", "--context", "x"],
        ["start", "bad", "--task-kind", "x", "--context", "\u2003"],
        ["start", "bad", "--task-kind", "x", "--context", "x", "--guess", "-1"],
        ["start", "bad", "--task-kind", "x", "--context", "x", "--guess", str(2**63)],
        ["finish", "bad", "--tokens", "-1", "--outcome", "completed"],
        ["finish", "bad", "--tokens", "2.5", "--outcome", "completed"],
        ["finish", "bad", "--tokens", "2", "--outcome", "invalid"],
        [
            "correct",
            "bad",
            "--tokens",
            "2",
            "--revision",
            "1",
            "--reason",
            "  ",
            "--outcome",
            "completed",
        ],
        ["start", "x" * 201, "--task-kind", "x", "--context", "x"],
    ],
)
def test_help_and_invalid_input_never_create_stores(tmp_path, args):
    j = Journey(tmp_path)
    j.invoke(*args, ok="--help" in args, human="--help" in args)
    assert not j.db.exists()


def test_missing_reads_and_unknown_finish_do_not_create_stores(tmp_path):
    j = Journey(tmp_path)
    assert j.invoke("history")["sessions"] == []
    assert j.invoke("show", "unknown", ok=False)["code"] == "session_not_found"
    assert (
        j.invoke("finish", "unknown", "--tokens", 1, "--outcome", "completed", ok=False)["code"]
        == "session_not_found"
    )
    assert not j.db.exists()


@pytest.mark.parametrize("database", ["core", "foreign", "empty", "text"])
def test_unfamiliar_files_reject_without_mutation_or_details(tmp_path, database):
    j = Journey(tmp_path)
    if database in {"core", "foreign"}:
        with sqlite3.connect(j.db) as connection:
            connection.execute("CREATE TABLE records (data TEXT)")
            if database == "core":
                connection.execute("PRAGMA user_version=2")
    elif database == "empty":
        j.db.touch()
    else:
        j.db.write_text("private invalid database")
    before = j.db.read_bytes()
    failed = j.invoke("start", "one", "--task-kind", "feature", "--context", "x", ok=False)
    assert failed["code"] == "session_store_unrecognized"
    assert "private" not in str(failed) and str(tmp_path) not in str(failed)
    assert j.db.read_bytes() == before


def test_process_restart_and_concurrent_starts_use_committed_history(tmp_path):
    j = Journey(tmp_path)
    j.start("a", 100)
    j.finish("a", 201)
    command = [
        sys.executable,
        "-m",
        "changecost",
        "--db",
        str(j.core),
        "session",
        "--session-db",
        str(j.db),
        "start",
        "b",
        "--task-kind",
        "feature",
        "--context",
        "python/cli",
    ]
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(
            executor.map(
                lambda _: subprocess.run(command, capture_output=True, text=True, check=True),
                range(2),
            )
        )
    assert json.loads(results[0].stdout) == json.loads(results[1].stdout)
    assert j.invoke("show", "b")["forecast"]["amount"] == "201"
    assert len(j.invoke("history")["sessions"]) == 2


def test_human_output_escapes_labels_and_shows_measurement(tmp_path):
    j = Journey(tmp_path)
    j.start("unsafe\x1b[31m", 100)
    result = j.invoke("show", "unsafe\x1b[31m", human=True)
    assert "\\u001b[31m" in result
    assert "\x1b[31m" not in result
    assert "Manual provisional" in result and "Estimate 100 tokens" in result
    j.finish("unsafe\x1b[31m", 200)
    assert "Manual measured total 200 tokens" in j.invoke("show", "unsafe\x1b[31m", human=True)


def test_demo_runs_real_cli_in_exclusive_directory(tmp_path):
    directory = tmp_path / "demo"
    command = [sys.executable, "-m", "changecost.session_demo", str(directory)]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    assert "300.000000 tokens" in result.stdout
    transcript = json.loads((directory / "transcript.json").read_text())
    assert [row["absolute_error"] for row in transcript["observed"]] == ["100", "0", "800"]
    assert transcript["fourth_forecast"]["amount"] == "200"
    assert len(transcript["steps"]) == 8
    before = (directory / "sessions.sqlite3").read_bytes()
    repeated = subprocess.run(command, capture_output=True, text=True)
    assert repeated.returncode == 2
    assert (directory / "sessions.sqlite3").read_bytes() == before
    assert not (directory / "unused-core.sqlite3").exists()


def test_concurrent_finish_and_start_freeze_only_committed_inputs(tmp_path):
    j = Journey(tmp_path)
    j.start("a", 100)
    prefix = [sys.executable, "-m", "changecost", "session", "--session-db", str(j.db)]
    commands = [
        [*prefix, "finish", "a", "--tokens", "201", "--outcome", "completed"],
        [*prefix, "start", "b", "--task-kind", "feature", "--context", "python/cli"],
    ]
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(
            executor.map(
                lambda command: subprocess.run(command, capture_output=True, text=True, check=True),
                commands,
            )
        )
    finished, started = [json.loads(result.stdout) for result in results]
    measurement = finished["measurement"]
    if measurement["sequence"] < started["start_sequence"]:
        assert started["forecast"]["amount"] == "201"
        assert started["forecast"]["inputs"][0]["revision"] == 1
    else:
        assert started["forecast"]["source"] == "unknown"
        assert started["forecast"]["inputs"] == []
    assert j.invoke("show", "b")["forecast"] == started["forecast"]


def test_boundary_rejects_boolean_and_overflow_without_creating_database(tmp_path):
    from changecost.sessions import Measurement, Sessions

    sessions = Sessions(tmp_path / "sessions.sqlite3")
    for value in (True, False, -1, 2**63):
        with pytest.raises(ValueError):
            sessions.start("bad", "feature", "python/cli", value)
        with pytest.raises(ValueError):
            sessions.measure("bad", Measurement(value, "completed"))
    assert not sessions.path.exists()


def test_half_token_median_and_nonterminating_mae_keep_exact_denominators(tmp_path):
    j = Journey(tmp_path)
    j.start("one", 0)
    j.finish("one", 0)
    j.start("two")
    j.finish("two", 1)
    third = j.start("three")
    assert third["forecast"]["amount"] == "0.5"
    j.finish("three", 1)
    evaluation = j.invoke("history")["evaluation"]
    assert evaluation["mean_absolute_error"]["numerator"] == "1.5"
    assert evaluation["mean_absolute_error"]["denominator"] == 3
    assert evaluation["mean_absolute_error"]["rounded_decimal"] == "0.500000"
    j.start("four")
    j.finish("four", 2)
    j.start("five")
    j.finish("five", 2)
    j.start("six")
    j.finish("six", 3)
    mae = j.invoke("history")["evaluation"]["mean_absolute_error"]
    assert mae["denominator"] == 6
    assert mae["numerator"] == "5.5"
    assert mae["rounded_decimal"] == "0.916667"


@pytest.mark.parametrize("after_schema", [False, True])
def test_interrupted_first_creation_allows_normal_cli_retry(tmp_path, after_schema):
    j = Journey(tmp_path)
    script = """
import os
import sys
from pathlib import Path
from changecost.sessions import Sessions
initialize = Sessions.initialize
def interrupted(connection):
    if sys.argv[2] == "True":
        initialize(connection)
    os._exit(17)
Sessions.initialize = staticmethod(interrupted)
Sessions(Path(sys.argv[1])).start("first", "feature", "python/cli")
"""
    result = subprocess.run(
        [sys.executable, "-c", script, str(j.db), str(after_schema)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 17, result.stderr
    assert j.start("first")["session_id"] == "first"
    assert len(j.invoke("history")["sessions"]) == 1


def test_failed_first_creation_cleans_private_files(tmp_path, monkeypatch):
    from changecost.sessions import Sessions

    j = Journey(tmp_path)
    initialize = Sessions.initialize

    def failed(connection):
        initialize(connection)
        raise RuntimeError("initialization interrupted")

    with monkeypatch.context() as patch:
        patch.setattr(Sessions, "initialize", staticmethod(failed))
        with pytest.raises(RuntimeError, match="initialization interrupted"):
            Sessions(j.db).start("first", "feature", "python/cli")
    assert list(tmp_path.iterdir()) == []
    assert j.start("first")["session_id"] == "first"


def test_concurrent_first_creation_accepts_both_starts(tmp_path, monkeypatch):
    from changecost.sessions import Sessions

    j = Journey(tmp_path)
    initialize = Sessions.initialize
    preparing, release = Event(), Event()

    def paused(connection):
        if not preparing.is_set():
            preparing.set()
            assert release.wait(10), "first creator was not released"
        initialize(connection)

    monkeypatch.setattr(Sessions, "initialize", staticmethod(paused))
    with ThreadPoolExecutor(max_workers=1) as executor:
        first = executor.submit(Sessions(j.db).start, "first", "feature", "python/cli")
        try:
            assert preparing.wait(10), "first creator did not reach initialization"
            second = j.start("second")
        finally:
            release.set()
        assert first.result(timeout=10)["session_id"] == "first"
    assert second["session_id"] == "second"
    assert {s["session_id"] for s in j.invoke("history")["sessions"]} == {"first", "second"}
    assert set(tmp_path.iterdir()) == {j.db}


def test_first_creation_preserves_foreign_publication_collision(tmp_path, monkeypatch):
    from changecost.sessions import Sessions

    j = Journey(tmp_path)
    initialize = Sessions.initialize
    foreign = b"private foreign file"

    def appeared(connection):
        initialize(connection)
        j.db.write_bytes(foreign)

    monkeypatch.setattr(Sessions, "initialize", staticmethod(appeared))
    failure = j.invoke(
        "start", "first", "--task-kind", "feature", "--context", "python/cli", ok=False
    )
    assert failure["code"] == "session_store_unrecognized"
    assert j.db.read_bytes() == foreign
    assert set(tmp_path.iterdir()) == {j.db}
