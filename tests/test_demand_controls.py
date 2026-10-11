"""Adversarial demand boundary controls complement ordinary scenarios."""

from datetime import datetime, timedelta

import pytest
from typer.testing import CliRunner

from changecost.cli import app
from changecost.demand import inspect_demand
from changecost.models import (
    Assessment,
    DemandComponent,
    DemandObservation,
    MatchedComparison,
    PriceRate,
    PriceScenario,
    Quantity,
    Rehearsal,
    TransferHypothesis,
)
from changecost.quotes import compute_quote
from changecost.serialization import ContractError
from changecost.store import reference
from tests.test_demand import COMP, DIMS, NOW, World, make_bridge
from tests.test_reconciliation import scope


@pytest.fixture
def world(tmp_path):
    return World(tmp_path / "db")


def test_local_economic_id_cannot_launder_demand_authority(world):
    quote = compute_quote(world.store, "target", scope(), "economic")
    original = world.forecast()
    forged = original.model_copy(update={"record_id": quote.record_id, "operation_id": "economic"})
    world.store.apply(lambda records, origin, now: ([forged], None))
    view = inspect_demand(world.store, forged)
    assert not view["local_computation"] and view["demand_validation"] == "producer_claim"
    before = world.store.export_bundle()
    with pytest.raises(ContractError):
        world.forecast("economic")
    assert world.store.export_bundle() == before


def test_demand_cli_success_explain_and_financial_check_rejection(world):
    runner = CliRunner()
    request = [
        "--db",
        str(world.store.path),
        "quote",
        "--demand",
        "--repository-id",
        "repo",
        "--change-id",
        "target",
        "--operation-id",
        "cli",
        "--assessment-id",
        "a",
        "--ecosystem-id",
        "eco",
    ]
    result = runner.invoke(app, request)
    assert result.exit_code == 0, result.output
    import json

    payload = json.loads(result.stdout)
    assert payload["kind"] == "demand_forecast" and payload["result"]["state"] == "zero_knowledge"
    explanation = runner.invoke(
        app,
        [
            "--db",
            str(world.store.path),
            "explain",
            "--record-kind",
            "demand_forecast",
            "--record-id",
            payload["record_id"],
        ],
    )
    assert explanation.exit_code == 0
    assert json.loads(explanation.stdout)["demand_validation"] == "reproduced"
    world.time = datetime.fromisoformat(payload["recorded_at"])
    before = world.store.export_bundle()
    check = runner.invoke(
        app,
        [
            "--db",
            str(world.store.path),
            "check",
            "--record-kind",
            "demand_forecast",
            "--record-id",
            payload["record_id"],
            "--budget",
            "1",
            "--economic-kind",
            "monetary",
            "--unit",
            "USD",
            "--basis",
            "billed",
            "--currency",
            "USD",
        ],
    )
    assert check.exit_code == 2
    assert world.store.export_bundle() == before


def test_incompatible_price_and_zero_knowledge_price_are_atomic(world):
    wrong = world.add(
        PriceScenario,
        "wrong",
        effective_date=NOW,
        source="supplied",
        currency="USD",
        rates=[
            PriceRate(
                component=DemandComponent(category="output", unit="tokens", basis="observed"),
                rate="1",
            )
        ],
    )
    before = world.store.export_bundle()
    with pytest.raises(ContractError):
        world.forecast(price_id=wrong.record_id)
    assert world.store.export_bundle() == before
    correct = world.add(
        PriceScenario,
        "correct",
        effective_date=NOW,
        source="supplied",
        currency="USD",
        rates=[PriceRate(component=COMP, rate="1")],
    )
    before = world.store.export_bundle()
    with pytest.raises(ContractError):
        world.forecast(price_id=correct.record_id)
    assert world.store.export_bundle() == before


def test_supplied_rehearsal_is_not_an_observed_outcome(world):
    assessment = world.add(
        Assessment,
        "rehearsed",
        change=reference(world.change),
        dimensions=DIMS,
        scope_key="same-task",
        assessor="manual",
        evidence=["read-only supplied assessment"],
        rehearsal=Rehearsal(
            method="read_only_assessment",
            budget=Quantity(component=COMP, amount="10"),
            overhead=Quantity(component=COMP, amount="3"),
        ),
    )
    f = world.forecast(assessment_id=assessment.record_id)
    assert f.result.state == "zero_knowledge" and f.result.sample_count == 0
    assert not any(isinstance(r, DemandObservation) for r in world.store.records())


def test_target_bridge_and_multiple_competing_policies_are_diagnostic(world):
    pair = make_bridge(world)
    target_pair = world.add(
        MatchedComparison,
        "target-pair",
        source_change=reference(world.change),
        target_change=pair.target_change,
        source_ecosystem=pair.source_ecosystem,
        target_ecosystem=pair.target_ecosystem,
        scope_key="same-task",
    )
    world.add(
        TransferHypothesis,
        "target-bridge",
        source_ecosystem=pair.source_ecosystem,
        target_ecosystem=pair.target_ecosystem,
        component=COMP,
        dimensions=DIMS,
        comparisons=[reference(target_pair)],
    )
    f = world.forecast()
    assert any(e.reason == "target_excluded_from_bridge" for e in f.exclusions)
    world.add(
        TransferHypothesis,
        "duplicate-bridge",
        source_ecosystem=pair.source_ecosystem,
        target_ecosystem=pair.target_ecosystem,
        component=COMP,
        dimensions=DIMS,
        comparisons=[reference(pair)],
    )
    assert world.forecast("ambiguous").result.transfer is None


def test_clock_regression_cannot_rewrite_history(world):
    world.peer("one", ["1"])
    f = world.forecast()
    world.time = NOW - timedelta(days=1)
    with pytest.raises(ContractError):
        inspect_demand(world.store, f)


def test_unknown_fields_and_nonfinite_quantities_reject_without_payloads(world, tmp_path):
    with pytest.raises(ValueError):
        Quantity(component=COMP, amount="NaN")
    with pytest.raises(ValueError):
        Quantity.model_validate({"component": COMP.model_dump(), "amount": True})
    bundle = world.store.export_bundle().model_dump(mode="json", by_alias=True)
    bundle["records"][0]["prompt"] = "private-sentinel"
    import json

    path = tmp_path / "private.json"
    path.write_text(json.dumps(bundle))
    result = CliRunner().invoke(
        app, ["--db", str(world.store.path), "bind", "--import-artifact", str(path)]
    )
    assert result.exit_code == 2 and "private-sentinel" not in result.output


def test_explicit_economic_minimum_is_rejected_even_at_default(world):
    before = world.store.export_bundle()
    result = CliRunner().invoke(
        app,
        [
            "--db",
            str(world.store.path),
            "quote",
            "--demand",
            "--repository-id",
            "repo",
            "--change-id",
            "target",
            "--operation-id",
            "mixed",
            "--assessment-id",
            "a",
            "--ecosystem-id",
            "eco",
            "--minimum",
            "20",
        ],
    )
    assert result.exit_code == 2
    assert world.store.export_bundle() == before


@pytest.mark.parametrize("price_id", ["", " ", "\u2003"])
def test_blank_price_selector_rejects_without_persistence(world, price_id):
    before = world.store.export_bundle()
    with pytest.raises(ValueError, match="identifier"):
        world.forecast("blank-price", price_id=price_id)
    assert world.store.export_bundle() == before
    forecast = world.forecast("blank-price")
    assert forecast.price is None and forecast.price_request is None
