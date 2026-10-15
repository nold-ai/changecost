"""Demand-mode parser and unchanged financial defaults."""

import json
import re

import pytest
from typer.testing import CliRunner

from changecost.cli import app
from tests.test_demand import World


@pytest.mark.parametrize("styled", [False, True])
def test_demand_mode_is_explicit_in_quote_help(styled):
    env = {"TERM": "xterm-256color" if styled else "dumb", "FORCE_COLOR": "1" if styled else ""}
    result = CliRunner().invoke(app, ["quote", "--help"], env=env, color=True)
    assert result.exit_code == 0
    if styled:
        assert "\x1b[" in result.stdout
    help_text = re.sub(r"\x1b\[[0-9;]*m", "", result.stdout)
    assert "--demand" in help_text
    assert "--assessment-id" in help_text


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


@pytest.mark.parametrize("price_id", ["", " ", "\u2003"])
def test_blank_optional_price_never_opens_store(tmp_path, price_id):
    world = World(tmp_path / "registered")
    before = world.store.export_bundle()
    request = [
        "quote",
        "--demand",
        "--repository-id",
        "repo",
        "--change-id",
        "target",
        "--operation-id",
        "blank-price",
        "--assessment-id",
        "a",
        "--ecosystem-id",
        "eco",
        "--price-id",
        price_id,
    ]
    result = CliRunner().invoke(app, ["--db", str(world.store.path), *request])
    assert result.exit_code == 2
    assert world.store.export_bundle() == before
    assert json.loads(result.stderr)["code"] == "invalid_request"
    db = tmp_path / "missing"
    result = CliRunner().invoke(app, ["--db", str(db), *request])
    assert result.exit_code == 2
    assert not db.exists()
    assert json.loads(result.stderr)["code"] == "invalid_request"
