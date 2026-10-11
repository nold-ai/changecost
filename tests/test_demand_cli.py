"""Demand-mode parser and unchanged financial defaults."""

import json

from typer.testing import CliRunner

from changecost.cli import app


def test_demand_mode_is_explicit_in_quote_help():
    result = CliRunner().invoke(app, ["quote", "--help"])
    assert result.exit_code == 0
    assert "--demand" in result.stdout
    assert "--assessment-id" in result.stdout


def test_incomplete_and_mixed_modes_never_create_store(tmp_path):
    for args in (
        [],
        ["--demand"],
        ["--demand", "--economic-kind", "monetary"],
        ["--assessment-id", "a"],
    ):
        db = tmp_path / "missing"
        result = CliRunner().invoke(
            app,
            [
                "--db",
                str(db),
                "quote",
                "--repository-id",
                "repo",
                "--change-id",
                "c",
                "--operation-id",
                "o",
                *args,
            ],
        )
        assert result.exit_code == 2
        assert not db.exists()
        assert json.loads(result.stderr)["code"] == "invalid_request"
