"""End-user offline evaluation command and privacy boundary."""

import json

import pytest
from typer.testing import CliRunner

from changecost.cli import app
from tests.evaluation_fixtures import adaptive_fixture, economic_fixture, write_inputs


def test_economic_report_cli_and_unchanged_runtime_store(tmp_path):
    history, protocol = write_inputs(tmp_path, *economic_fixture(tmp_path))
    ordinary = tmp_path / "ordinary.sqlite3"
    ordinary.write_bytes(b"untouched runtime store")
    args = [
        "--db",
        str(ordinary),
        "evaluate-synthetic",
        "--history",
        str(history),
        "--protocol",
        str(protocol),
    ]
    result = CliRunner().invoke(app, args)
    assert result.exit_code == 0, result.output
    report = json.loads(result.stdout)
    case = report["core"]["economic"]["cases"][0]
    assert case["candidate"]["p50"] == case["baseline"]["p50"] == "10"
    assert case["candidate"]["p90"] == case["baseline"]["p90"] == "18"
    assert case["truth"]["amount"] == "15"
    metrics = report["core"]["economic"]["candidate"]
    assert metrics["p50_coverage"]["numerator"] == 0
    assert metrics["p90_coverage"]["numerator"] == 1
    assert metrics["mean_width"] == "8"
    assert metrics["mean_signed_error"] == "-5"
    assert report["core"]["conclusion"] == "synthetic_only_not_yet_validated"
    assert ordinary.read_bytes() == b"untouched runtime store"
    assert CliRunner().invoke(app, args).stdout == result.stdout


def test_measurements_are_separate_and_failures_clean_up(tmp_path, monkeypatch):
    from pathlib import Path

    from changecost import evaluation

    h, p = write_inputs(tmp_path, *economic_fixture(tmp_path))
    normal = evaluation.evaluate_synthetic(h, p)
    measured = evaluation.evaluate_synthetic(h, p, measure_runs=2)
    assert normal["core"] == measured["core"]
    assert normal["measurements"] is None
    assert len(measured["measurements"]["runs_ms"]) == 2
    assert measured["measurements"]["input_bytes"] == h.stat().st_size + p.stat().st_size
    assert measured["measurements"]["nondeterministic"]
    paths = []

    def fail(history, protocol, path):
        paths.append(Path(path).parent)
        raise ValueError("PRIVATE_SENTINEL")

    monkeypatch.setattr(evaluation, "run_history", fail)
    result = CliRunner().invoke(
        app, ["evaluate-synthetic", "--history", str(h), "--protocol", str(p)]
    )
    assert result.exit_code == 2 and "PRIVATE_SENTINEL" not in result.output
    assert paths and not paths[0].exists()


def test_missing_paths_are_not_echoed(tmp_path):
    result = CliRunner().invoke(
        app,
        [
            "evaluate-synthetic",
            "--history",
            str(tmp_path / "PRIVATE_SENTINEL"),
            "--protocol",
            str(tmp_path / "missing"),
        ],
    )
    assert result.exit_code == 2 and "PRIVATE_SENTINEL" not in result.output


def test_extreme_numeric_input_rejects_before_exact_arithmetic(tmp_path):
    history, protocol = economic_fixture(tmp_path)
    next(r for r in history["bundle"]["records"] if r["kind"] == "economic_evidence")["component"][
        "amount"
    ] = "1e1000"
    h, p = write_inputs(tmp_path, history, protocol)
    result = CliRunner().invoke(
        app, ["evaluate-synthetic", "--history", str(h), "--protocol", str(p)]
    )
    assert result.exit_code == 2


@pytest.mark.parametrize(
    "amount", ["1e١٠٠٠", "١" * 257, "1." + "١" * 255], ids=["exponent", "integer", "decimal"]
)
def test_unicode_numeric_bounds_reject(tmp_path, amount):
    history, protocol = economic_fixture(tmp_path, count=0)
    next(r for r in history["bundle"]["records"] if r["kind"] == "economic_evidence")["component"][
        "amount"
    ] = amount
    h, p = write_inputs(tmp_path, history, protocol)
    result = CliRunner().invoke(
        app, ["evaluate-synthetic", "--history", str(h), "--protocol", str(p)]
    )
    assert result.exit_code == 2, result.output
    assert amount not in result.output


@pytest.mark.parametrize(
    "fraction", ["١" * 255 + "/1", "1/" + "١" * 255], ids=["numerator", "denominator"]
)
def test_unicode_fraction_bounds_reject(tmp_path, fraction):
    history, protocol, _ = adaptive_fixture(tmp_path)
    policy = next(
        r for r in history["bundle"]["records"] if r["kind"] == "demand_validation_policy"
    )
    policy["maximum_underestimate"] = fraction
    h, p = write_inputs(tmp_path, history, protocol)
    result = CliRunner().invoke(
        app, ["evaluate-synthetic", "--history", str(h), "--protocol", str(p)]
    )
    assert result.exit_code == 2, result.output
    assert fraction not in result.output


@pytest.mark.parametrize("field", ["unit", "basis"])
@pytest.mark.parametrize("location", ["policy", "rehearsal"])
def test_nested_component_identifier_rejects_without_echo(tmp_path, field, location):
    history, protocol, _ = adaptive_fixture(tmp_path, rehearsal="1")
    records = history["bundle"]["records"]
    unsafe = "PRIVATE SENTINEL /customer/prompt"
    if location == "policy":
        record = next(r for r in records if r["kind"] == "demand_validation_policy")
        record["component"][field] = unsafe
    else:
        record = next(r for r in records if r["kind"] == "task_assessment" and r["rehearsal"])
        for quantity in ("budget", "overhead"):
            record["rehearsal"][quantity]["component"][field] = unsafe
    h, p = write_inputs(tmp_path, history, protocol)
    result = CliRunner().invoke(
        app, ["evaluate-synthetic", "--history", str(h), "--protocol", str(p)]
    )
    assert result.exit_code == 2, result.output
    assert unsafe not in result.output


@pytest.mark.parametrize("amount", ["١٥", "١.٥e١", "15e٠"])
def test_bounded_unicode_amount_keeps_exact_truth(tmp_path, amount):
    history, protocol = economic_fixture(tmp_path, count=0)
    truth = next(
        r
        for r in history["bundle"]["records"]
        if r["kind"] == "economic_evidence" and r["component"]["amount"] == "15"
    )
    truth["component"]["amount"] = amount
    h, p = write_inputs(tmp_path, history, protocol)
    result = CliRunner().invoke(
        app, ["evaluate-synthetic", "--history", str(h), "--protocol", str(p)]
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["core"]["economic"]["cases"][0]["truth"]["amount"] == "15"


@pytest.mark.parametrize("field", ["run_id", "case", "version", "source_gap"])
def test_other_projected_identifiers_reject_without_echo(tmp_path, field):
    history, protocol = economic_fixture(tmp_path, count=0)
    unsafe = "PRIVATE SENTINEL /customer/prompt"
    if field == "run_id":
        for record in history["bundle"]["records"]:
            for name in ("ref", "run"):
                if isinstance(record.get(name), dict) and "run_id" in record[name]:
                    record[name]["run_id"] = unsafe
    elif field == "case":
        protocol["cases"][0]["id"] = unsafe
    elif field == "version":
        protocol["version"] = unsafe
    else:
        protocol["source_gaps"] = [unsafe]
    h, p = write_inputs(tmp_path, history, protocol)
    result = CliRunner().invoke(
        app, ["evaluate-synthetic", "--history", str(h), "--protocol", str(p)]
    )
    assert result.exit_code == 2, result.output
    assert unsafe not in result.output
