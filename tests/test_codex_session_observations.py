import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from typer.testing import CliRunner

from changecost import codex_local
from changecost.cli import app
from changecost.sessions import SessionError, Sessions
from tests.native_fixtures import synthetic_source
from tests.test_sessions_cli import Journey


@pytest.fixture
def selected(tmp_path, monkeypatch):
    path, raw, envelope = synthetic_source(tmp_path)
    monkeypatch.setattr(codex_local, "_packaged_admission", lambda: envelope)
    return path, raw, envelope


def observe(journey, path, name="a", repository="repo", *, ok=True):
    return journey.invoke(
        "observe-codex", name, "--file", path, "--repository-id", repository, ok=ok
    )


def rows(path, tables=("sessions", "measurements", "events", "sqlite_sequence")):
    with sqlite3.connect(path) as connection:
        return {table: connection.execute(f"SELECT * FROM {table}").fetchall() for table in tables}


def version(path):
    with sqlite3.connect(path) as connection:
        return connection.execute("PRAGMA user_version").fetchone()[0]


def assert_native_projection(native, envelope):
    assert native["fact_count"] == 12 and native["request_count"] == 2
    for key in ("source_sha256", "projection_sha256", "mapping_revision"):
        assert native[key] == envelope["admission"][key]
    for key in ("profile_id", "profile_digest", "approval_digest"):
        assert native[key] == envelope[key]
    assert {fact["category"] for fact in native["facts"]} == set(codex_local.CATEGORIES)
    assert all(fact["scope"] == "request" for fact in native["facts"])
    assert all(fact["completeness"] == fact["finality"] == "unknown" for fact in native["facts"])


def assert_native_authority(observed):
    native = observed["native_diagnostics"]
    assert native["manual"] is False and native["unit"] == "source_category_tokens"
    assert native["association"] == "explicit_user_session_link_only"
    assert native["session_total"] is native["total_error"] is None
    assert native["learning_eligible"] is False
    assert observed["measurement"] is None and observed["measurements"] == []
    assert observed["error"]["excluded_reason"] == "native_partial_diagnostics"
    assert observed["error"]["absolute_tokens"] is None
    assert observed["manual_scope"] == observed["unit_scope"] == "forecast_measurements_and_error"


def test_observe_codex_actual_cli(tmp_path, selected):
    path, raw, envelope = selected
    journey = Journey(tmp_path)
    original = journey.start("a", 100)
    result = CliRunner().invoke(
        app,
        [
            "session",
            "--session-db",
            str(journey.db),
            "observe-codex",
            "a",
            "--file",
            str(path),
            "--repository-id",
            "repo",
        ],
    )
    assert result.exit_code == 0, result.output
    observed = json.loads(result.stdout)
    assert observed["forecast"] == original["forecast"]
    assert_native_projection(observed["native_diagnostics"], envelope)
    assert_native_authority(observed)
    assert path.read_bytes() == raw
    assert not journey.core.exists()


def test_exact_retry_two_links_no_duplicate_facts_or_events(tmp_path, selected):
    path, _, _ = selected
    journey = Journey(tmp_path)
    journey.start("a", 100)
    journey.start("b", 200)
    first = observe(journey, path)
    before = journey.db.read_bytes()
    assert observe(journey, path) == first
    assert journey.db.read_bytes() == before
    second = observe(journey, path, "b")
    tables = rows(journey.db, ("native_snapshots", "native_links", "events"))
    assert len(tables["native_snapshots"]) == 1
    assert len(json.loads(tables["native_snapshots"][0][2])["facts"]) == 12
    assert len(tables["native_links"]) == 2 and len(tables["events"]) == 4
    assert second["native_diagnostics"]["sequence"] != first["native_diagnostics"]["sequence"]
    assert journey.start("next")["forecast"]["inputs"] == []
    assert journey.invoke("history")["evaluation"]["excluded"] == {
        "native_partial_diagnostics": 2,
        "pending": 1,
    }


def test_independent_manual_totals_retain_errors_learning_and_frozen_estimates(tmp_path, selected):
    path, _, _ = selected
    journey = Journey(tmp_path)
    frozen = journey.start("a", 100)["forecast"]
    manual = journey.finish("a", 200)
    historical = journey.start("b")["forecast"]
    attached = observe(journey, path)
    for key in ("forecast", "measurement", "measurements", "error"):
        assert attached[key] == manual[key]
    assert attached["forecast"] == frozen
    assert attached["error"]["absolute_tokens"] == "100"
    journey.correct("a", 300, 1)
    assert journey.invoke("show", "b")["forecast"] == historical
    assert journey.start("c")["forecast"]["amount"] == "300"
    assert journey.invoke("show", "a")["native_diagnostics"]["learning_eligible"] is False
    assert journey.invoke("history")["evaluation"]["included_count"] == 1


def mutate_source(path, tmp_path, mutation):
    if mutation == "append":
        path.write_bytes(path.read_bytes() + b"{}\n")
    elif mutation == "replace":
        path.write_bytes(path.read_bytes().replace(b"PRIVATE-PROMPT", b"changed"))
    elif mutation == "missing":
        path.unlink()
    elif mutation == "symlink":
        link = tmp_path / "link"
        link.symlink_to(path)
        path = link
    elif mutation == "invalid":
        path.write_text("private malformed source")
    return path


@pytest.mark.parametrize("mutation", ["append", "replace", "missing", "symlink", "invalid"])
def test_rejected_source_leaves_v1_database_and_source_unchanged(tmp_path, selected, mutation):
    path, _, _ = selected
    journey = Journey(tmp_path)
    journey.start("a", 100)
    path = mutate_source(path, tmp_path, mutation)
    source = path.read_bytes() if path.exists() else None
    before = journey.db.read_bytes()
    failed = observe(journey, path, ok=False)
    assert failed["code"] in {"invalid_source_record", "unadmitted_source", "unsafe_source"}
    assert journey.db.read_bytes() == before and version(journey.db) == 1
    assert (path.read_bytes() if path.exists() else None) == source
    assert "PRIVATE" not in json.dumps(failed) and str(tmp_path) not in json.dumps(failed)


def test_missing_session_rejects_before_source_read_and_never_creates_storage(
    tmp_path, monkeypatch
):
    def forbidden(_):
        pytest.fail("source must not be acquired for a missing target")

    monkeypatch.setattr(codex_local, "_acquire", forbidden)
    journey = Journey(tmp_path)
    assert observe(journey, tmp_path / "unused", ok=False)["code"] == "session_not_found"
    assert not journey.db.exists()
    journey.start("other")
    before = journey.db.read_bytes()
    assert observe(journey, tmp_path / "unused", ok=False)["code"] == "session_not_found"
    assert journey.db.read_bytes() == before


@pytest.mark.parametrize("database", ["core", "foreign", "empty", "text", "extra", "future"])
def test_native_rejects_unfamiliar_storage_before_acquisition(tmp_path, monkeypatch, database):
    journey = Journey(tmp_path)
    if database in {"core", "foreign"}:
        with sqlite3.connect(journey.db) as connection:
            connection.execute("CREATE TABLE records (data TEXT)")
            if database == "core":
                connection.execute("PRAGMA user_version=2")
    elif database == "empty":
        journey.db.touch()
    elif database == "text":
        journey.db.write_text("private invalid database")
    else:
        journey.start("a")
        with sqlite3.connect(journey.db) as connection:
            connection.execute(
                "CREATE TABLE foreign_table (data TEXT)"
                if database == "extra"
                else "PRAGMA user_version=3"
            )
    monkeypatch.setattr(codex_local, "_acquire", lambda _: pytest.fail("unexpected source read"))
    before = journey.db.read_bytes()
    assert observe(journey, tmp_path / "unused", ok=False)["code"] == "session_store_unrecognized"
    assert journey.db.read_bytes() == before


def assert_preserved_rows(path, saved):
    after = rows(path)
    for table in ("sessions", "measurements"):
        assert after[table] == saved[table]
    assert after["events"][:-1] == saved["events"]
    assert after["events"][-1][0] == saved["sqlite_sequence"][0][1] + 1


def test_populated_v1_read_and_manual_writes_then_native_migration_preserve_rows(
    tmp_path, selected
):
    path, _, _ = selected
    journey = Journey(tmp_path)
    journey.start("a", 100)
    journey.finish("a", 200)
    journey.start("b")
    journey.correct("a", 300, 1)
    assert version(journey.db) == 1
    before = journey.db.read_bytes()
    assert journey.invoke("show", "b")["forecast"]["amount"] == "200"
    journey.invoke("history")
    assert journey.db.read_bytes() == before
    saved = rows(journey.db)
    observe(journey, path)
    assert version(journey.db) == 2
    assert_preserved_rows(journey.db, saved)
    assert journey.finish("a", 200)["operation_revision"] == 1
    assert journey.correct("a", 300, 1)["operation_revision"] == 2
    assert journey.start("c")["forecast"]["amount"] == "300"
    journey.finish("c", 400)
    assert journey.correct("c", 500, 1)["measurement"]["tokens"] == 500


def test_migration_failure_rolls_back_schema_and_all_old_bytes(tmp_path, selected, monkeypatch):
    path, _, _ = selected
    journey = Journey(tmp_path)
    journey.start("a", 100)
    journey.finish("a", 200)
    before = journey.db.read_bytes()
    migrate = Sessions.migrate_native

    def fail(connection):
        migrate(connection)
        raise RuntimeError("migration interrupted")

    monkeypatch.setattr(Sessions, "migrate_native", staticmethod(fail))
    with pytest.raises(RuntimeError, match="migration interrupted"):
        Sessions(journey.db).observe_codex("a", codex_local.select_codex_file("repo", path))
    assert journey.db.read_bytes() == before and version(journey.db) == 1


def test_v1_post_migration_attachment_failure_rolls_back_everything(
    tmp_path, selected, monkeypatch
):
    path, _, _ = selected
    journey = Journey(tmp_path)
    journey.start("a")
    before = journey.db.read_bytes()

    def fail(*_):
        raise SessionError("session_conflict", "conflict")

    monkeypatch.setattr(Sessions, "record_native", fail)
    assert observe(journey, path, ok=False)["code"] == "session_conflict"
    assert journey.db.read_bytes() == before and version(journey.db) == 1


@pytest.mark.parametrize("conflict_kind", ["repository", "provenance", "source", "meaning"])
def test_conflicts_are_atomic_and_keep_first_snapshot(tmp_path, selected, conflict_kind):
    path, _, envelope = selected
    journey = Journey(tmp_path)
    journey.start("a")
    journey.start("b")
    original = observe(journey, path)
    before = journey.db.read_bytes()
    repository = "repo"
    target = "a"
    if conflict_kind == "repository":
        repository, target = "different-repo", "b"
    elif conflict_kind == "provenance":
        envelope["approval_digest"] = "d" * 64
    else:
        path, _, replacement = synthetic_source(tmp_path, counts=(1, 2))
        envelope.update(replacement)
        if conflict_kind == "meaning":
            target = "b"
    assert observe(journey, path, target, repository, ok=False)["code"] == "session_conflict"
    assert journey.db.read_bytes() == before
    assert journey.invoke("show", "a") == original


def test_stored_reports_do_not_reopen_source_and_never_retain_private_data(
    tmp_path, selected, monkeypatch
):
    path, _, _ = selected
    journey = Journey(tmp_path)
    journey.start("a")
    original = observe(journey, path)
    path.unlink()
    monkeypatch.setattr(codex_local, "_acquire", lambda _: pytest.fail("read-only reopened source"))
    before = journey.db.read_bytes()
    assert journey.invoke("show", "a") == original
    history = journey.invoke("history")
    human = journey.invoke("show", "a", human=True)
    assert journey.db.read_bytes() == before
    saved = (
        json.dumps(history) + human + str(rows(journey.db, ("native_snapshots", "native_links")))
    )
    for private in ("PRIVATE", str(path), "pending", "store_id", "record_id", "created_at"):
        assert private not in saved
    assert b"PRIVATE" not in journey.db.read_bytes()
    assert "manual: False" in human and "native_partial_diagnostics" in human


def test_concurrent_observe_decides_migration_under_lock_and_reuses_events(
    tmp_path, selected, monkeypatch
):
    from changecost import sessions

    path, _, _ = selected
    journey = Journey(tmp_path)
    journey.start("a")
    journey.start("b")
    frozen = rows(journey.db, ("sessions", "measurements"))
    barrier = Barrier(2)
    read = sessions.read_codex_file

    def together(selection):
        result = read(selection)
        barrier.wait(timeout=10)
        return result

    monkeypatch.setattr(sessions, "read_codex_file", together)
    selection = codex_local.select_codex_file("repo", path)
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(
            executor.map(
                lambda name: Sessions(journey.db).observe_codex(name, selection), ["a", "b"]
            )
        )
    assert {result["session_id"] for result in results} == {"a", "b"}
    assert rows(journey.db, ("sessions", "measurements")) == frozen
    assert version(journey.db) == 2
    assert len(rows(journey.db, ("native_snapshots",))["native_snapshots"]) == 1
    with ThreadPoolExecutor(max_workers=2) as executor:
        repeated = list(
            executor.map(lambda _: Sessions(journey.db).observe_codex("a", selection), range(2))
        )
    assert repeated[0] == repeated[1]
    assert len(rows(journey.db, ("events",))["events"]) == 4


def test_json_quantities_keep_4096_digits_without_sqlite_integer_coercion(tmp_path, monkeypatch):
    quantity = 10**4095
    path, _, envelope = synthetic_source(tmp_path, counts=(quantity, 1))
    monkeypatch.setattr(codex_local, "_packaged_admission", lambda: envelope)
    journey = Journey(tmp_path)
    journey.start("a")
    diagnostic = observe(journey, path)["native_diagnostics"]
    assert sorted({fact["quantity"] for fact in diagnostic["facts"]}) == [1, quantity]
    assert journey.invoke("show", "a")["native_diagnostics"] == diagnostic
    assert journey.start("b")["forecast"]["inputs"] == []


def test_new_reader_projection_and_old_import_receipt_share_same_canonical_facts(
    tmp_path, selected
):
    from changecost.store import Store

    path, _, _ = selected
    selection = codex_local.select_codex_file("repo", path)
    diagnostic = codex_local.read_codex_file(selection).diagnostics()
    store = Store(tmp_path / "separate-core.sqlite3")
    first = codex_local.import_codex_file(store, selection)
    saved = store.path.read_bytes()
    replay = codex_local.import_codex_file(store, selection)
    assert replay.fact_count == first.fact_count == diagnostic["fact_count"] == 12
    assert replay.evidence_ids == first.evidence_ids
    assert replay.inserted_fact_count == 0 and first.inserted_fact_count == 12
    assert store.path.read_bytes() == saved


def test_native_help_and_invalid_selector_do_not_create_stores(tmp_path):
    journey = Journey(tmp_path)
    journey.invoke("observe-codex", "--help", human=True)
    assert (
        observe(journey, tmp_path / "unused", repository="", ok=False)["code"]
        == "invalid_native_selection"
    )
    assert not journey.db.exists()
