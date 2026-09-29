"""Offline command-family integration and failure boundaries."""

import json

import pytest
from typer.testing import CliRunner

from changecost.cli import app

runner = CliRunner()


def invoke(tmp_path, *args):
    return runner.invoke(app, ["--db", str(tmp_path / "db.sqlite"), *args])


def test_fresh_cli_registration_outcome_and_export(tmp_path):
    result = invoke(
        tmp_path, "bind", "--register-change", "--repository-id", "repo", "--change-id", "c"
    )
    assert result.exit_code == 0, result.output
    ident = json.loads(result.output)["record_id"]
    result = invoke(
        tmp_path,
        "bind",
        "--register-run",
        "--repository-id",
        "repo",
        "--change-id",
        "c",
        "--provider",
        "cursor",
        "--surface",
        "ide",
        "--run-id",
        "r",
    )
    assert result.exit_code == 0, result.output
    result = invoke(
        tmp_path, "settle", "--repository-id", "repo", "--change-id", "c", "--outcome", "accepted"
    )
    assert result.exit_code == 0, result.output
    result = invoke(tmp_path, "explain", "--repository-id", "repo", "--change-id", "c")
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["record"]["record_id"] == ident
    assert json.loads(result.output)["revisions"][0]["outcome"] == "accepted"
    artifact = tmp_path / "export.json"
    assert invoke(tmp_path, "explain", "--export-artifact", str(artifact)).exit_code == 0
    original = artifact.read_bytes()
    assert invoke(tmp_path, "explain", "--export-artifact", str(artifact)).exit_code != 0
    assert artifact.read_bytes() == original
    destination = tmp_path / "destination"
    destination.mkdir()
    result = invoke(destination, "bind", "--import-artifact", str(artifact))
    assert result.exit_code == 0, result.output
    assert invoke(destination, "bind", "--import-artifact", str(artifact)).exit_code == 0


@pytest.mark.parametrize(
    "args,success",
    [
        (["--help"], True),
        (["--version"], True),
        ([], False),
        (["quote"], False),
        (["check"], False),
        (["settle"], False),
        (["bind", "--register-change", "--register-run"], False),
        (["bind", "--register-change", "--repository-id", "repo"], False),
        (["bind", "--run-id", "r", "--evidence-id", "e"], False),
        (["explain", "--record-kind", "run", "--record-id", "r"], False),
        (["explain", "--repository-id", "repo", "--change-id", "c"], False),
    ],
)
def test_read_only_invalid_and_help(tmp_path, args, success):
    result = invoke(tmp_path, *args)
    assert (result.exit_code == 0) == success, result.output
    assert list(tmp_path.iterdir()) == []


def test_private_invalid_import_has_no_payload_diagnostic(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text('{"prompt":"PRIVATE_SENTINEL"}')
    result = invoke(tmp_path, "bind", "--import-artifact", str(path))
    assert result.exit_code != 0
    assert "PRIVATE_SENTINEL" not in result.output
    assert not (tmp_path / "db.sqlite").exists()


def test_export_failure_never_exposes_partial_file(tmp_path, monkeypatch):
    assert (
        invoke(
            tmp_path, "bind", "--register-change", "--repository-id", "repo", "--change-id", "c"
        ).exit_code
        == 0
    )
    import changecost.cli as cli

    def fail(_source, _target):
        raise OSError("synthetic publish failure")

    monkeypatch.setattr(cli.os, "link", fail)
    target = tmp_path / "out.json"
    result = invoke(tmp_path, "explain", "--export-artifact", str(target))
    assert result.exit_code != 0
    assert not target.exists()
    assert sorted(p.name for p in tmp_path.iterdir()) == ["db.sqlite"]


def test_supplied_empty_binding_mode_is_rejected_without_writes(tmp_path):
    result = invoke(
        tmp_path,
        "bind",
        "--register-change",
        "--repository-id",
        "repo",
        "--change-id",
        "c",
        "--evidence-id",
        "",
    )
    assert result.exit_code != 0
    assert list(tmp_path.iterdir()) == []
