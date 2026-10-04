"""Output boundaries through real Typer parsing, independent of formatter helpers."""

import json

import pytest
from typer.testing import CliRunner

from changecost.cli import app

runner = CliRunner()


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["private-unknown"],
        ["--format", "private-format"],
        ["quote", "--private-option"],
        ["bind"],
        ["settle"],
        ["explain"],
        ["check"],
    ],
)
def test_safe_parser_and_request_errors(tmp_path, args):
    db = tmp_path / "private-store"
    result = runner.invoke(app, ["--db", str(db), *args])
    assert result.exit_code == 2
    assert result.stdout == ""
    error = json.loads(result.stderr)
    assert error["schema"] == "changecost/error-v1"
    assert error["code"] in {"invalid_request", "unavailable_input"}
    assert "private" not in result.stderr
    assert not db.exists()


@pytest.mark.parametrize("flag", ["--help", "--version"])
def test_offline_help_and_version(tmp_path, flag):
    db = tmp_path / "absent"
    result = runner.invoke(app, ["--db", str(db), flag])
    assert result.exit_code == 0
    assert not db.exists()


def test_human_registration_and_json_stability(tmp_path):
    db = tmp_path / "db"
    args = [
        "--db",
        str(db),
        "bind",
        "--register-change",
        "--repository-id",
        "repo",
        "--change-id",
        "change",
    ]
    original = runner.invoke(app, args)
    assert original.exit_code == 0, original.output
    explicit = runner.invoke(app, ["--format", "json", *args])
    assert json.loads(explicit.stdout) == json.loads(original.stdout)
    human = runner.invoke(app, ["--format", "human", *args])
    assert human.exit_code == 0, human.output
    assert "change" in human.stdout and "repo" in human.stdout
    assert not human.stdout.startswith("{")


@pytest.mark.parametrize("family", ["bind", "quote", "settle", "check", "explain"])
@pytest.mark.parametrize("format", ["json", "human"])
def test_all_family_parser_diagnostics(tmp_path, family, format):
    result = runner.invoke(
        app, ["--db", str(tmp_path / "private"), "--format", format, family, "--private-option"]
    )
    assert result.exit_code == 2 and result.stdout == ""
    assert "private" not in result.stderr
    if format == "json":
        assert json.loads(result.stderr)["schema"] == "changecost/error-v1"
    assert not (tmp_path / "private").exists()


def test_all_family_human_operation_values(tmp_path):
    from tests.test_advisory import check_args, priced, settlement

    quote_store, quote = priced(tmp_path / "quote")
    settlement_store, record = settlement(tmp_path / "settlement")
    invocations = [
        (
            quote_store,
            [
                "quote",
                "--repository-id",
                "repo",
                "--change-id",
                "target",
                "--operation-id",
                "quote-operation",
                "--minimum",
                "2",
                "--economic-kind",
                "monetary",
                "--unit",
                "USD",
                "--currency",
                "USD",
                "--basis",
                "billed",
            ],
        ),
        (
            settlement_store,
            [
                "settle",
                "--compute",
                "--repository-id",
                "repo",
                "--change-id",
                "change",
                "--operation-id",
                "op",
                "--economic-kind",
                "monetary",
                "--unit",
                "USD",
                "--currency",
                "USD",
                "--basis",
                "billed",
            ],
        ),
        (quote_store, check_args(quote)),
        (
            settlement_store,
            ["explain", "--record-kind", "computed_settlement", "--record-id", record.record_id],
        ),
    ]
    for store, args in invocations:
        before = store.path.read_bytes()
        output = runner.invoke(app, ["--db", str(store.path), "--format", "human", *args])
        assert output.exit_code == 0, output.output
        assert "USD" in output.stdout and "billed" in output.stdout
        assert not output.stdout.startswith("{")
        assert store.path.read_bytes() == before


def test_terminal_controls_remain_data():
    from changecost.presentation import human

    value = {"label": "\x1b[31m\n\r\x00\u202e世界"}
    output = human(value)
    assert "\x1b" not in output and "\x00" not in output and "\u202e" not in output
    assert "世界" in output and "\\u001b" in output


@pytest.mark.parametrize(
    "prefix,format",
    [
        (["--format", "human", "--format", "json"], "json"),
        (["--format", "json", "--format", "human"], "human"),
        (["--format=human", "--format=json"], "json"),
        (["--format", "human", "--format", "private-invalid"], "json"),
        (["--db", "quote", "--format", "human"], "human"),
        (["--db", "check", "--format", "human"], "human"),
        (["--db", "--format=human"], "json"),
        (["--db", "--format", "--format", "human"], "human"),
    ],
)
@pytest.mark.parametrize("failure", [["check", "--private-option"], ["--private-root-option"]])
def test_effective_global_format_parser_failures(tmp_path, monkeypatch, prefix, format, failure):
    monkeypatch.chdir(tmp_path)
    output = runner.invoke(app, [*prefix, *failure])
    assert output.exit_code == 2 and output.stdout == ""
    assert "private" not in output.stderr
    if format == "json":
        assert json.loads(output.stderr)["schema"] == "changecost/error-v1"
    else:
        assert output.stderr == "invalid request\n"
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    "prefix,format",
    [
        (["--format", "human", "--format", "json"], "json"),
        (["--format", "json", "--format", "human"], "human"),
        (["--db", "quote", "--format", "human"], "human"),
        (["--db", "--format=human"], "json"),
    ],
)
def test_effective_format_console(tmp_path, prefix, format):
    import subprocess
    import sys

    output = subprocess.run(
        [sys.executable, "-m", "changecost", *prefix, "check", "--private-option"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert output.returncode == 2 and output.stdout == ""
    assert "private" not in output.stderr and "Traceback" not in output.stderr
    if format == "json":
        assert json.loads(output.stderr)["schema"] == "changecost/error-v1"
    else:
        assert output.stderr == "invalid request\n"
    assert list(tmp_path.iterdir()) == []
