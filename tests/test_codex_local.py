import hashlib
import json
import os
import subprocess
import sys
from datetime import UTC, datetime

import pytest
from rich.text import Text
from typer.testing import CliRunner

from changecost.cli import app
from changecost.serialization import ContractError
from changecost.store import Store
from tests.native_fixtures import synthetic_source


@pytest.fixture
def selected(tmp_path, monkeypatch):
    from changecost import codex_local

    path, raw, envelope = synthetic_source(tmp_path)
    monkeypatch.setattr(codex_local, "_packaged_admission", lambda: envelope)
    selection = codex_local.CodexSelection(
        repository_id="repo",
        path=path,
        profile_id="synthetic-only",
        expected_sha256=hashlib.sha256(raw).hexdigest(),
    )
    return codex_local, selection, raw, envelope


def assert_private_native_projection(store):
    text = store.export_bundle().model_dump_json()
    assert "PRIVATE" not in text
    facts = [r for r in store.records() if r.kind == "native_usage"]
    assert len(facts) == 12 and all(
        r.model is None and r.interval.state == "unknown" for r in facts
    )
    assert all(r.finality == r.scope_completeness == r.backend_presence == "unknown" for r in facts)
    assert all(r.ownership.state == "child" for r in facts)


def test_finite_replay_and_private_projection(selected, tmp_path):
    reader, selection, raw, envelope = selected
    store = Store(tmp_path / "db", clock=lambda: datetime(2026, 10, 24, tzinfo=UTC))
    first = reader.import_codex_file(store, selection)
    assert selection.path.read_bytes() == raw
    assert len(first.evidence_ids) == 2 and first.fact_count == 12
    before = store.export_bundle()
    copied = tmp_path / "renamed.jsonl"
    copied.write_bytes(raw)
    assert (
        reader.import_codex_file(store, selection.model_copy(update={"path": copied})).evidence_ids
        == first.evidence_ids
    )
    assert store.export_bundle() == before
    assert copied.read_bytes() == raw
    formatted = (
        b"\n".join(
            json.dumps(json.loads(line), separators=(",", ":")).encode()
            for line in raw.splitlines()
        )
        + b"\n"
    )
    selection.path.write_bytes(formatted)
    envelope["admission"]["source_sha256"] = hashlib.sha256(formatted).hexdigest()
    later = selection.model_copy(update={"expected_sha256": hashlib.sha256(formatted).hexdigest()})
    assert reader.import_codex_file(store, later).inserted_fact_count == 0
    assert store.export_bundle() == before
    assert_private_native_projection(store)
    assert selection.path.read_bytes() == formatted
    envelope["profile_digest"] = "f" * 64
    envelope["approval_digest"] = "e" * 64
    assert reader.import_codex_file(store, later).evidence_ids == first.evidence_ids
    assert selection.path.read_bytes() == formatted
    assert store.export_bundle() == before


@pytest.mark.parametrize(
    "raw",
    [
        b'{"x":1,"x":2}\n',
        b'{"x":NaN}\n',
        b'{"x":1e9999}\n',
        b'{"x":',
        b"\n",
        b'{"x":' + b"[" * 33 + b"0" + b"]" * 33 + b"}\n",
        b"{}\n" * 10001,
        b"x" * (10485760 + 1),
        b'{"x":' + b"1" * 4097 + b"}\n",
    ],
    ids=[
        "duplicate",
        "nan",
        "infinite",
        "truncated",
        "blank",
        "depth",
        "records",
        "bytes",
        "digits",
    ],
)
def test_bounded_rejection_private_and_atomic(selected, tmp_path, raw):
    reader, selection, _, _ = selected
    selection.path.write_bytes(raw)
    store = Store(tmp_path / "db")
    with pytest.raises(ContractError) as error:
        reader.import_codex_file(store, selection)
    assert "PRIVATE" not in str(error.value) and str(selection.path) not in str(error.value)
    assert not store.path.exists()


def test_unadmitted_append_and_production_fixture_rejected(selected, tmp_path, monkeypatch):
    reader, selection, raw, _ = selected
    store = Store(tmp_path / "db")
    reader.import_codex_file(store, selection)
    before = store.export_bundle().records
    selection.path.write_bytes(raw + b"{}\n")
    with pytest.raises(ContractError):
        reader.import_codex_file(store, selection)
    assert store.records() == before
    monkeypatch.undo()
    with pytest.raises(ContractError, match="unsupported_profile"):
        reader.import_codex_file(Store(tmp_path / "other"), selection)
    assert not (tmp_path / "other").exists()


def test_symlinks_and_nonregular_never_publish(selected, tmp_path):
    reader, selection, _, _ = selected
    link = tmp_path / "link"
    link.symlink_to(selection.path)
    parent = tmp_path / "parent"
    parent.symlink_to(tmp_path, target_is_directory=True)
    fifo = tmp_path / "fifo"
    os.mkfifo(fifo)
    for path in (link, parent / selection.path.name, fifo, tmp_path):
        with pytest.raises(ContractError):
            reader.import_codex_file(
                Store(tmp_path / "db"), selection.model_copy(update={"path": path})
            )
        assert not (tmp_path / "db").exists()


def test_conflicting_later_admission_rolls_back_new_event(selected, tmp_path):
    reader, selection, _, envelope = selected
    store = Store(tmp_path / "db", clock=lambda: datetime(2026, 10, 24, tzinfo=UTC))
    reader.import_codex_file(store, selection)
    before = store.export_bundle()
    _, raw, later = synthetic_source(
        tmp_path, counts=(4, 5), responses=("new-event", "PRIVATE-response-1")
    )
    envelope.clear()
    envelope.update(later)
    with pytest.raises(ContractError, match="native_identity_conflict"):
        reader.import_codex_file(
            store, selection.model_copy(update={"expected_sha256": hashlib.sha256(raw).hexdigest()})
        )
    assert store.export_bundle() == before


def test_changed_during_descriptor_read_rejects(selected, tmp_path, monkeypatch):
    reader, selection, _, _ = selected
    original = os.read
    changed = False

    def mutate(descriptor, count):
        nonlocal changed
        data = original(descriptor, count)
        if not changed:
            changed = True
            with selection.path.open("ab") as stream:
                stream.write(b" ")
        return data

    monkeypatch.setattr(reader.os, "read", mutate)
    with pytest.raises(ContractError, match="unstable_source"):
        reader.import_codex_file(Store(tmp_path / "db"), selection)
    assert not (tmp_path / "db").exists()


def test_native_binding_does_not_create_numeric_authority(selected, tmp_path):
    from changecost.models import EconomicScope, RunRef
    from changecost.operations import bind_evidence, register_change, register_run
    from changecost.reconciliation import compute_settlement

    reader, selection, _, _ = selected
    store = Store(tmp_path / "db")
    result = reader.import_codex_file(store, selection)
    register_change(store, "repo", "change")
    run = RunRef(repository_id="repo", provider="Codex", surface="desktop-coding", run_id="run")
    register_run(store, run, "change")
    for evidence_id in result.evidence_ids:
        bind_evidence(store, evidence_id, run)
    forbidden = {"demand_observation", "demand_policy", "source_coverage", "economic_evidence"}
    assert not forbidden & {record.kind for record in store.records()}
    scope = EconomicScope.model_validate(
        dict(
            repository_id="repo",
            economic=dict(economic_kind="monetary", unit="USD", currency="USD", basis="billed"),
        )
    )
    settlement = compute_settlement(store, "change", scope, "native-diagnostic")
    assert not settlement.full_change
    assert "missing_economic_evidence" in settlement.unknown_reasons


@pytest.mark.parametrize(
    "option",
    [
        "--compute",
        "--import-evidence",
        "--change-id",
        "--provider",
        "--surface",
        "--run-id",
        "--outcome",
        "--run-outcome",
        "--work-start",
        "--work-end",
        "--correct-outcome",
        "--correct-interval",
        "--reason",
        "--operation-id",
        "--economic-kind",
        "--unit",
        "--currency",
        "--basis",
        "--source-start",
        "--source-end",
    ],
)
def test_native_cli_exclusions_precede_acquisition(selected, tmp_path, monkeypatch, option):
    reader, selection, _, _ = selected

    def forbidden(_path):
        pytest.fail("native source acquired before CLI exclusion")

    monkeypatch.setattr(reader, "_acquire", forbidden)
    args = [
        "--db",
        str(tmp_path / "db"),
        "settle",
        "--repository-id",
        "repo",
        "--import-codex",
        str(selection.path),
        "--source-profile",
        selection.profile_id,
        "--source-sha256",
        selection.expected_sha256,
        option,
    ]
    if option not in {"--compute", "--correct-outcome", "--correct-interval"}:
        args.append("private")
    result = CliRunner().invoke(app, args)
    assert result.exit_code == 2
    assert not (tmp_path / "db").exists()


def test_valid_native_cli_has_safe_receipt(selected, tmp_path):
    _, selection, _, _ = selected
    result = CliRunner().invoke(
        app,
        [
            "--db",
            str(tmp_path / "db"),
            "settle",
            "--repository-id",
            "repo",
            "--import-codex",
            str(selection.path),
            "--source-profile",
            selection.profile_id,
            "--source-sha256",
            selection.expected_sha256,
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["fact_count"] == 12
    assert "PRIVATE" not in result.output


def test_cli_native_mode_rejects_before_store(tmp_path):
    db = tmp_path / "db"
    result = CliRunner().invoke(
        app,
        [
            "--db",
            str(db),
            "settle",
            "--import-codex",
            "PRIVATE",
            "--source-profile",
            "p",
            "--source-sha256",
            "a" * 64,
            "--repository-id",
            "repo",
            "--compute",
        ],
    )
    assert result.exit_code == 2
    assert "No such option" not in result.output
    assert not db.exists()


@pytest.mark.parametrize("colored", [False, True], ids=["plain", "colored"])
def test_cli_exposes_explicit_native_selection(colored):
    env = os.environ.copy()
    env.update(TERM="xterm-256color", GITHUB_ACTIONS="true")
    env.pop("NO_COLOR", None)
    env.pop("_TYPER_FORCE_DISABLE_TERMINAL", None)
    env["FORCE_COLOR"] = "1"
    if not colored:
        env["NO_COLOR"] = "1"
        env["_TYPER_FORCE_DISABLE_TERMINAL"] = "1"
    result = subprocess.run(
        [sys.executable, "-m", "changecost", "settle", "--help"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    assert ("\x1b[" in result.stdout) is colored
    visible = Text.from_ansi(result.stdout).plain
    assert "--import-codex" in visible
    assert "--source-profile" in visible
    assert "--source-sha256" in visible


def test_native_cli_preserves_safe_unsupported_code(tmp_path):
    result = CliRunner().invoke(
        app,
        [
            "--db",
            str(tmp_path / "db"),
            "settle",
            "--repository-id",
            "repo",
            "--import-codex",
            "PRIVATE-path",
            "--source-profile",
            "PRIVATE-profile",
            "--source-sha256",
            "a" * 64,
        ],
    )
    assert result.exit_code == 2
    assert json.loads(result.output)["code"] == "unsupported_profile"
    assert "PRIVATE" not in result.output
    assert not (tmp_path / "db").exists()


def test_native_cli_preserves_safe_invalid_ordinal(selected, tmp_path):
    _, selection, _, _ = selected
    selection.path.write_bytes(b'{"type":"private","payload":{"private":NaN}}\n')
    result = CliRunner().invoke(
        app,
        [
            "--db",
            str(tmp_path / "db"),
            "settle",
            "--repository-id",
            "repo",
            "--import-codex",
            str(selection.path),
            "--source-profile",
            selection.profile_id,
            "--source-sha256",
            selection.expected_sha256,
        ],
    )
    payload = json.loads(result.output)
    assert result.exit_code == 2
    assert payload["code"] == "invalid_source_record" and payload["ordinal"] == 0
    assert "private" not in result.output and "PRIVATE" not in result.output
    assert not (tmp_path / "db").exists()


@pytest.mark.parametrize(
    "bad",
    [True, -1, 1.5, None, "1", 10**4096],
    ids=["bool", "negative", "fraction", "missing", "string", "digits"],
)
def test_selected_category_exact_semantics_reject_before_store(selected, tmp_path, bad):
    reader, selection, raw, envelope = selected
    rows = [json.loads(line) for line in raw.splitlines()]
    rows[1]["payload"]["usage"]["total_tokens"] = bad
    changed = b"".join(json.dumps(row).encode() + b"\n" for row in rows)
    selection.path.write_bytes(changed)
    envelope["admission"]["source_sha256"] = hashlib.sha256(changed).hexdigest()
    with pytest.raises(ContractError):
        reader.import_codex_file(
            Store(tmp_path / "db"),
            selection.model_copy(update={"expected_sha256": hashlib.sha256(changed).hexdigest()}),
        )
    assert not (tmp_path / "db").exists()


def test_strict_parser_boundaries_have_repaired_controls(selected):
    reader, _, _, _ = selected
    valid = b'{"type":"ignored","payload":{"x":1}}\n'
    assert len(reader._parse(valid * 10000)) == 10000
    with pytest.raises(ContractError, match="source_record_limit"):
        reader._parse(valid * 10001)
    assert reader._parse(b'{"type":"ignored","payload":{"text":"[\\"{}]"}}\n')
    for bad in (
        b'{"type":"ignored","payload":{"x":1,"x":2}}\n',
        b'{"type":"ignored","payload":{"x":NaN}}\n',
        b'{"type":"ignored","payload":{"x":1e9999}}\n',
        b'{"type":"ignored","payload":{"x":' + b"1" * 4097 + b"}}\n",
    ):
        with pytest.raises(ContractError, match="invalid_source_record:0"):
            reader._parse(bad)
    assert reader._parse(valid)
