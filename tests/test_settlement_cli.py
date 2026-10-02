"""Public offline normalized import/compute/report mode acceptance."""

import json

from typer.testing import CliRunner

from changecost.cli import app
from changecost.models import RunRef
from changecost.operations import bind_evidence, register_change, register_run
from changecost.store import Store

runner = CliRunner()


def normalized_file(tmp_path):
    path = tmp_path / "normalized.json"
    path.write_text(
        json.dumps(
            {
                "schema": "changecost/normalized-v1",
                "repository_id": "repo",
                "batch_id": "example",
                "events": [
                    {
                        "source": {
                            "repository_id": "repo",
                            "provider": "synthetic",
                            "surface": "fixture",
                            "profile": "synthetic/v1",
                            "namespace": "opaque",
                            "identity_scope": "namespaced",
                            "source_key": "a",
                        },
                        "component_key": "charge",
                        "component": {
                            "economic_kind": "monetary",
                            "unit": "USD",
                            "currency": "USD",
                            "basis": "billed",
                            "amount": "0.25",
                        },
                        "series": "usage",
                        "lane": "delta",
                        "start": "2026-09-29T08:00:00Z",
                        "end": "2026-09-29T08:00:00Z",
                    }
                ],
            }
        )
    )
    return path


def test_cli_import_compute_explain(tmp_path):
    db = tmp_path / "db"
    path = normalized_file(tmp_path)
    result = runner.invoke(
        app, ["--db", str(db), "settle", "--import-evidence", str(path), "--repository-id", "repo"]
    )
    assert result.exit_code == 0, result.output
    evidence = json.loads(result.output)["evidence_ids"][0]
    store = Store(db)
    register_change(store, "repo", "change")
    run = RunRef(repository_id="repo", provider="synthetic", surface="fixture", run_id="r")
    register_run(store, run, "change")
    bind_evidence(store, evidence, run)
    args = [
        "--db",
        str(db),
        "settle",
        "--compute",
        "--repository-id",
        "repo",
        "--change-id",
        "change",
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
    ]
    result = runner.invoke(app, args)
    assert result.exit_code == 0, result.output
    computed = json.loads(result.output)
    assert computed["subtotals"][0]["amount"] == "0.25"
    assert json.loads(runner.invoke(app, args).output) == computed
    result = runner.invoke(
        app,
        [
            "--db",
            str(db),
            "explain",
            "--record-kind",
            "computed_settlement",
            "--record-id",
            computed["record_id"],
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["local_computation"] is True
    before = db.read_bytes()
    result = runner.invoke(
        app,
        [
            "--db",
            str(db),
            "explain",
            "--repository-remainder",
            "--repository-id",
            "repo",
            "--economic-kind",
            "monetary",
            "--unit",
            "USD",
            "--currency",
            "USD",
            "--basis",
            "billed",
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["bound"][0]["amount"] == "0.25"
    assert db.read_bytes() == before


def test_cli_invalid_modes_and_private_input_do_not_publish(tmp_path):
    path = normalized_file(tmp_path)
    db = tmp_path / "absent"
    cases = [
        ["settle", "--compute"],
        ["settle", "--import-evidence", str(path)],
        ["settle", "--compute", "--outcome", "accepted"],
        [
            "settle",
            "--import-evidence",
            str(path),
            "--repository-id",
            "repo",
            "--operation-id",
            "bad",
        ],
        ["settle", "--unit", "USD"],
        ["explain", "--repository-remainder", "--repository-id", "repo"],
    ]
    for args in cases:
        assert runner.invoke(app, ["--db", str(db), *args]).exit_code != 0
        assert not db.exists()
    data = json.loads(path.read_text())
    data["events"][0]["PRIVATE_SENTINEL"] = "private"
    path.write_text(json.dumps(data))
    result = runner.invoke(
        app, ["--db", str(db), "settle", "--import-evidence", str(path), "--repository-id", "repo"]
    )
    assert result.exit_code != 0 and "PRIVATE_SENTINEL" not in result.output
    assert not db.exists()
