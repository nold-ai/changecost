"""Offline Quote command and safe selector diagnostics."""

import json

from typer.testing import CliRunner

from changecost.cli import app
from tests.test_quotes import peer, setup


def test_quote_command_and_explanation(tmp_path):
    store = setup(tmp_path)
    peer(store, "peer", "1")
    args = [
        "--db",
        str(store.path),
        "quote",
        "--repository-id",
        "repo",
        "--change-id",
        "target",
        "--operation-id",
        "request",
        "--economic-kind",
        "monetary",
        "--unit",
        "USD",
        "--currency",
        "USD",
        "--basis",
        "billed",
        "--minimum",
        "1",
    ]
    runner = CliRunner()
    result = runner.invoke(app, args)
    assert result.exit_code == 0, result.output
    record = json.loads(result.output)
    assert record["p50"]["amount"] == "1"
    assert json.loads(runner.invoke(app, args).output) == record
    explanation = runner.invoke(
        app,
        [
            "--db",
            str(store.path),
            "explain",
            "--record-kind",
            "quote",
            "--record-id",
            record["record_id"],
        ],
    )
    assert explanation.exit_code == 0, explanation.output
    assert json.loads(explanation.output)["economic_validation"] == "reproduced"


def test_quote_invalid_minimum_does_not_create_store(tmp_path):
    path = tmp_path / "missing"
    result = CliRunner().invoke(
        app,
        [
            "--db",
            str(path),
            "quote",
            "--repository-id",
            "repo",
            "--change-id",
            "target",
            "--operation-id",
            "request",
            "--economic-kind",
            "monetary",
            "--unit",
            "USD",
            "--currency",
            "USD",
            "--basis",
            "billed",
            "--minimum",
            "0",
        ],
    )
    assert result.exit_code != 0
    assert not path.exists()
