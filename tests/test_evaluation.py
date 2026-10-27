"""Spec-derived offline timelines, exact metrics and authority exclusions."""

import copy
import json
from datetime import timedelta

import pytest
from typer.testing import CliRunner

from changecost.cli import app
from changecost.models import DemandObservation
from changecost.store import reference
from tests.evaluation_fixtures import (
    adaptive_fixture,
    economic_fixture,
    portable_timeline,
    write_inputs,
)


def evaluate(tmp_path, history, protocol):
    history_path, protocol_path = write_inputs(tmp_path, history, protocol)
    result = CliRunner().invoke(
        app,
        ["evaluate-synthetic", "--history", str(history_path), "--protocol", str(protocol_path)],
    )
    assert result.exit_code == 0, result.output
    return json.loads(result.stdout)["core"]


@pytest.mark.parametrize(
    "count,complete,status",
    [(19, True, "joint_unpriced"), (20, False, "missing_full_change_truth")],
)
def test_unpriced_and_partial_truth_never_become_zero(tmp_path, count, complete, status):
    report = evaluate(tmp_path, *economic_fixture(tmp_path, count, complete))
    assert report["economic"]["cases"][0]["status"] == status
    assert report["economic"]["candidate"]["count"] == 0
    assert report["economic"]["candidate"]["mean_absolute_error"] is None


def test_imported_quote_remains_without_authority(tmp_path):
    from changecost.quotes import compute_quote
    from changecost.store import Store
    from tests.test_reconciliation import NOW, scope

    history, protocol = economic_fixture(tmp_path)
    source = Store(tmp_path / "foreign", clock=lambda: NOW + timedelta(seconds=5))
    from changecost.serialization import loads_bundle

    source.import_bundle(loads_bundle(json.dumps(history["bundle"])))
    quote = compute_quote(source, "target", scope(), "foreign-quote")
    history["bundle"] = source.export_bundle().model_dump(mode="json", by_alias=True)
    history["deliveries"].append(
        dict(at=(NOW + timedelta(seconds=6)).isoformat(), records=[reference(quote).model_dump()])
    )
    protocol["cases"][0].update(
        imported_forecast=reference(quote).model_dump(),
        forecast_at=(NOW + timedelta(seconds=7)).isoformat(),
        truth_at=(NOW + timedelta(seconds=8)).isoformat(),
    )
    protocol["observation_at"] = (NOW + timedelta(seconds=8)).isoformat()
    report = evaluate(tmp_path, history, protocol)
    assert report["economic"]["cases"][0]["status"] == "replay_unavailable"
    assert report["economic"]["candidate"]["count"] == 0


@pytest.mark.parametrize(
    "peers,actual,complete,state",
    [
        ([], "2", True, "zero_knowledge"),
        (["1", "3"], "2", True, "learning"),
        (["1", "3"], "2", False, "learning"),
        (["1"] * 20, "100", True, "learning"),
    ],
)
def test_adaptive_availability_truth_and_failed_metrics(tmp_path, peers, actual, complete, state):
    history, protocol, _ = adaptive_fixture(tmp_path, peers=peers, actual=actual, complete=complete)
    report = evaluate(tmp_path, history, protocol)
    row = report["adaptive"]["cases"][0]
    assert row["methods"]["dimensional"]["state"] == state
    assert row["truth"]["status"] == ("complete" if complete else "omitted")
    assert report["algorithm_versions"]["demand"] == "observed-summary/v4"
    if not peers or not complete:
        assert row["methods"]["dimensional"]["signed_error"] is None
    elif actual == "100":
        assert row["methods"]["dimensional"]["signed_error"] == "-99"
        assert not row["methods"]["dimensional"]["synthetic_rubric_passed"]
    else:
        assert row["methods"]["dimensional"]["signed_error"] == "0"
        assert row["methods"]["dimensional"]["synthetic_rubric_passed"]


def test_frozen_truth_survives_later_correction_and_terminal_update(tmp_path):
    history, protocol, world = adaptive_fixture(tmp_path)
    before = evaluate(tmp_path, history, protocol)
    observation = next(
        r
        for r in world.store.records()
        if r.kind == "demand_observation" and r.run.run_id == "target-0"
    )
    world.tick()
    world.add(
        DemandObservation,
        "late-correction",
        **observation.model_dump(
            exclude={
                "kind",
                "schema_version",
                "record_id",
                "origin_store_id",
                "recorded_at",
                "effective_at",
                "previous",
                "reason",
                "quantity",
            }
        ),
        quantity="99",
        previous=reference(observation),
        reason="fixture",
    )
    world.tick()
    protocol["cases"][0]["updates"] = [world.time.isoformat()]
    after = evaluate(tmp_path, portable_timeline(world.store), protocol)
    assert after["adaptive"]["cases"] == before["adaptive"]["cases"]
    assert after["adaptive"]["shared_observed_truth_count"] == 1
    assert after["updates"][0]["adaptive"]["dimensional"]["initial"] is False
    assert (
        protocol["cases"][0]["change"]
        not in after["updates"][0]["adaptive"]["dimensional"]["peers"]
    )


def test_transfer_scenarios_are_separate_from_observed_quantiles(tmp_path):
    history, protocol, _ = adaptive_fixture(tmp_path, bridge=True)
    row = evaluate(tmp_path, history, protocol)["adaptive"]["cases"][0]
    scenario = row["methods"]["transfer"]
    assert scenario["interpretation"] == "scenario_diagnostic_not_observed_quantiles"
    assert scenario["median"] == "1"
    assert scenario["signed_error"] == "-1"
    assert scenario["support_count"] == scenario["donor_count"] == scenario["truth_count"] == 1
    assert "p50" not in scenario and "p90" not in scenario


def test_costly_rehearsal_does_not_pass_from_effort(tmp_path):
    history, protocol, _ = adaptive_fixture(tmp_path, rehearsal="100")
    row = evaluate(tmp_path, history, protocol)["adaptive"]["cases"][0]["methods"]["rehearsal"]
    assert not row["synthetic_rubric_passed"]
    assert row["rehearsal_overhead"]["amount"] == "100"
    assert row["net_benefit"] == "-100"


def test_unknown_ecosystem_is_no_forecast(tmp_path):
    history, protocol, _ = adaptive_fixture(tmp_path, unknown=True)
    row = evaluate(tmp_path, history, protocol)["adaptive"]["cases"][0]
    assert row["methods"]["dimensional"]["state"] == "zero_knowledge"
    assert "unknown_ecosystem" in row["methods"]["dimensional"]["exclusions"]


@pytest.mark.parametrize(
    "mutation",
    ["marker", "native", "private_field", "duplicate_case", "minimum", "late_registration"],
)
def test_invalid_experiment_rejects_without_payload_echo(tmp_path, mutation):
    history, protocol = economic_fixture(tmp_path)
    if mutation == "marker":
        history["provenance"] = "PRIVATE_SENTINEL"
    elif mutation == "native":
        next(r for r in history["bundle"]["records"] if r["kind"] == "evidence")["provider"] = (
            "codex"
        )
    elif mutation == "private_field":
        history["bundle"]["records"][0]["raw_prompt"] = "PRIVATE_SENTINEL"
    elif mutation == "duplicate_case":
        protocol["cases"].append(copy.deepcopy(protocol["cases"][0]))
    elif mutation == "minimum":
        protocol["economic_minimum"] = True
    else:
        protocol["registered_at"] = protocol["cases"][0]["forecast_at"]
    h, p = write_inputs(tmp_path, history, protocol)
    result = CliRunner().invoke(
        app, ["evaluate-synthetic", "--history", str(h), "--protocol", str(p)]
    )
    assert result.exit_code == 2
    assert "PRIVATE_SENTINEL" not in result.output and "raw_prompt" not in result.output


def test_economic_asymmetry_suppresses_all_accuracy(tmp_path, monkeypatch):
    from changecost import quotes

    original = quotes.estimate

    def asymmetric(*args, **kwargs):
        quote = original(*args, **kwargs)
        if kwargs.get("repository_only"):
            return quote.model_copy(update={"state": "unpriced"})
        return quote

    monkeypatch.setattr(quotes, "estimate", asymmetric)
    h, p = write_inputs(tmp_path, *economic_fixture(tmp_path))
    result = CliRunner().invoke(
        app, ["evaluate-synthetic", "--history", str(h), "--protocol", str(p)]
    )
    assert result.exit_code == 2
    report = json.loads(result.stdout)["core"]
    assert report["economic"]["status"] == "comparison_error"
    assert report["economic"]["candidate"] is report["economic"]["baseline"] is None


def test_attribution_keeps_six_two_two_raw_denominator(tmp_path):
    from changecost.store import Store
    from tests.test_reconciliation import NOW, event, import_events

    history, protocol = economic_fixture(tmp_path, count=0)
    store = Store(tmp_path / "db", clock=lambda: NOW + timedelta(seconds=3))
    evidence = import_events(
        store, *(event(f"extra-{i}", None if i == 8 else "1") for i in range(9))
    )
    history = portable_timeline(store)
    run = next(r for r in history["bundle"]["records"] if r["kind"] == "run")
    # Binding provenance is a portable producer assertion, not provider verification.
    from changecost.models import EvidenceBinding, RecordRef
    from changecost.operations import common

    for i, item in enumerate(evidence[:7]):
        binding = EvidenceBinding(
            **common("fixture", NOW + timedelta(seconds=3), f"attribution-{i}"),
            evidence=RecordRef(kind="evidence", record_id=item),
            run=run["ref"],
            method="verified_provider" if i < 6 else "manual",
        )
        store.apply(lambda records, origin, now, binding=binding: ([binding], binding))
    report = evaluate(tmp_path, portable_timeline(store), protocol)["attribution"]
    assert report["raw_record_count"] == 10
    assert [
        report["coverage"][name]["numerator"] for name in ("provider", "manual", "unbound")
    ] == [6, 2, 2]
    assert report["coverage"]["provider"]["ratio"] == "3/5"
    assert report["coverage"]["provider"]["denominator"] == 10
    assert report["unknown_money_count"] == 1


def test_abandoned_retries_count_once_and_unknown_is_undefined(tmp_path):
    from changecost.models import RunRef
    from changecost.operations import (
        LifecycleDeclaration,
        bind_evidence,
        declare,
        register_change,
        register_run,
    )
    from changecost.store import Store
    from tests.test_reconciliation import NOW, START, add_coverage, event, import_events

    history, protocol = economic_fixture(tmp_path, count=0)
    store = Store(tmp_path / "db", clock=lambda: NOW + timedelta(seconds=3))
    change = register_change(store, "repo", "abandoned")
    for i, value in enumerate(("4", "6")):
        run = register_run(
            store,
            RunRef(
                repository_id="repo", provider="synthetic", surface="fixture", run_id=f"retry-{i}"
            ),
            "abandoned",
        )
        declare(store, reference(run), LifecycleDeclaration(start=START, end=NOW, outcome="failed"))
        evidence = import_events(store, event(f"retry-{i}", value))[0]
        bind_evidence(store, evidence, run.ref)
        add_coverage(store, run.ref, evidence)
    declare(store, reference(change), LifecycleDeclaration(outcome="abandoned"))
    report = evaluate(tmp_path, portable_timeline(store), protocol)["abandonment"]
    assert report["known_abandoned"] == "10" and report["known_total"] == "25"
    assert report["share"] == "2/5" and report["attempt_count"] == 3
    unknown = register_change(store, "repo", "unknown")
    declare(store, reference(unknown), LifecycleDeclaration(outcome="abandoned"))
    report = evaluate(tmp_path, portable_timeline(store), protocol)["abandonment"]
    assert report["share"] is None and report["unknown_count"] == 1


def test_scoped_local_validation_withdrawal_has_future_effect(tmp_path):
    from changecost.demand import compute_validation
    from tests.test_demand import World, evaluated_task, registered_policy

    world = World(tmp_path / "withdrawal")
    world.peer("one", ["1"])
    world.peer("three", ["3"])
    world.tick()
    first = registered_policy(world)
    case = evaluated_task(world, "pass", "2")
    receipt = compute_validation(world.store, first.record_id, [case], "pass-receipt")
    assert receipt.passed
    supported = world.forecast("supported")
    assert supported.result.state == "validated_forecast"
    world.tick()
    other = world.ecosystem("other-scope", "other-model")
    registered_policy(world, "other-rubric", ecosystem=reference(other))
    assert world.forecast("unrelated-policy").result.state == "validated_forecast"
    world.tick()
    second = registered_policy(world, "overlapping-rubric")
    failed = evaluated_task(world, "fail", "100")
    assert not compute_validation(world.store, second.record_id, [failed], "fail-receipt").passed
    assert world.forecast("future-withdrawn").result.state == "learning"
    assert world.forecast("future-withdrawn").result.validation is None


def test_transfer_only_additional_availability_has_no_observed_median(tmp_path):
    history, protocol, _ = adaptive_fixture(tmp_path, peers=(), bridge=True)
    for record in history["bundle"]["records"]:
        if record["kind"] == "change" and record["change_id"] == "bridge-target":
            record["repository_id"] = "bridge-repository"
        for field in ("ref", "run"):
            if (
                field in record
                and isinstance(record[field], dict)
                and record[field].get("run_id") == "bridge-target-0"
            ):
                record[field]["repository_id"] = "bridge-repository"
    report = evaluate(tmp_path, history, protocol)["adaptive"]
    methods = report["cases"][0]["methods"]
    assert methods["dimensional"]["state"] == "transfer_hypothesis"
    assert methods["dimensional"]["median"] is None
    assert methods["transfer"]["median"] == "1"
    assert report["availability"]["transfer"] == 1
    assert report["availability"]["dimensional"] == 0
    assert report["shared_observed_truth_count"] == 0


@pytest.mark.parametrize("confounded", [False, True])
def test_future_or_confounded_pair_does_not_enter_initial_transfer(tmp_path, confounded):
    history, protocol, _ = adaptive_fixture(tmp_path, bridge=True)
    if confounded:
        next(r for r in history["bundle"]["records"] if r["kind"] == "matched_comparison")[
            "confounding"
        ] = ["task-and-model"]
    else:
        moved = []
        for delivery in history["deliveries"]:
            selected = [
                r
                for r in delivery["records"]
                if r["kind"] in {"matched_comparison", "transfer_hypothesis"}
            ]
            moved.extend(selected)
            delivery["records"] = [r for r in delivery["records"] if r not in selected]
        history["deliveries"].append(dict(at=protocol["cases"][0]["truth_at"], records=moved))
    methods = evaluate(tmp_path, history, protocol)["adaptive"]["cases"][0]["methods"]
    assert methods["transfer"]["state"] == "unavailable"


@pytest.mark.parametrize("actual", ["1", "100"])
def test_transfer_point_errors_distinguish_useful_and_harmful(tmp_path, actual):
    history, protocol, _ = adaptive_fixture(
        tmp_path, peers=("100", "100"), actual=actual, bridge=True
    )
    methods = evaluate(tmp_path, history, protocol)["adaptive"]["cases"][0]["methods"]
    transfer = int(methods["transfer"]["absolute_error"])
    target = int(methods["dimensional"]["absolute_error"])
    assert (transfer < target) == (actual == "1")
    assert methods["dimensional"]["median"] == "100"
    assert methods["transfer"]["validation"] == "not_eligible_for_measured_receipt"


def test_economic_truth_correction_freezes_independently(tmp_path):
    from changecost.operations import bind_evidence
    from changecost.store import Store
    from tests.test_reconciliation import NOW, add_coverage, event, import_events, locator

    history, protocol = economic_fixture(tmp_path)
    store = Store(tmp_path / "db", clock=lambda: NOW + timedelta(seconds=3))
    run = next(r for r in store.records() if r.kind == "run" and r.ref.run_id == "target")
    start = NOW + timedelta(seconds=2)
    evidence = import_events(
        store,
        event(
            "corrected-truth",
            "17",
            start=start.isoformat(),
            end=start.isoformat(),
            replaces=locator("truth"),
            correction_reason="corrected",
        ),
    )[0]
    bind_evidence(store, evidence, run.ref)
    add_coverage(store, run.ref, evidence, start=start, end=NOW + timedelta(seconds=3))
    corrected = evaluate(tmp_path, portable_timeline(store), protocol)
    assert corrected["economic"]["cases"][0]["truth"]["amount"] == "17"
    assert corrected["economic"]["cases"][0]["candidate"]["p50"] == "10"
    store.clock = lambda: NOW + timedelta(seconds=5)
    evidence = import_events(
        store,
        event(
            "late-truth",
            "999",
            start=start.isoformat(),
            end=start.isoformat(),
            replaces=locator("corrected-truth"),
            correction_reason="late",
        ),
    )[0]
    bind_evidence(store, evidence, run.ref)
    add_coverage(store, run.ref, evidence, start=start, end=NOW + timedelta(seconds=3))
    after = evaluate(tmp_path, portable_timeline(store), protocol)
    assert after["economic"]["cases"] == corrected["economic"]["cases"]


@pytest.mark.parametrize("payload", ['{"schema":1,"schema":2}', '{"x":NaN}', "{"])
def test_malformed_json_has_only_safe_error(tmp_path, payload):
    h, p = tmp_path / "h", tmp_path / "p"
    h.write_text(payload)
    p.write_text("{}")
    result = CliRunner().invoke(
        app, ["evaluate-synthetic", "--history", str(h), "--protocol", str(p)]
    )
    assert result.exit_code == 2
    assert json.loads(result.stderr)["message"] == "invalid request"


def test_adaptive_aggregate_has_shared_metrics_and_no_quantile_claim(tmp_path):
    history, protocol, _ = adaptive_fixture(tmp_path)
    summary = evaluate(tmp_path, history, protocol)["adaptive"]
    metric = summary["shared_observed_metrics"][0]["methods"]["dimensional"]
    assert metric["count"] == 1
    assert metric["observed_range_coverage"]["numerator"] == 1
    assert metric["observed_range_coverage"]["denominator"] == 1
    assert metric["mean_signed_error"] == "0"
    assert metric["mean_width"] == "2"
    assert metric["component"]["unit"] == "tokens"
    assert "p50_coverage" not in metric


def test_unsafe_scope_identifier_and_economic_unit_reject(tmp_path):
    history, protocol, _ = adaptive_fixture(tmp_path)
    next(r for r in history["bundle"]["records"] if r["kind"] == "task_assessment")["scope_key"] = (
        "/private/customer/prompt"
    )
    h, p = write_inputs(tmp_path, history, protocol)
    result = CliRunner().invoke(
        app, ["evaluate-synthetic", "--history", str(h), "--protocol", str(p)]
    )
    assert result.exit_code == 2 and "/private/customer" not in result.output
    protocol["economic_scope"]["economic"]["unit"] = "PRIVATE UNIT"
    h, p = write_inputs(tmp_path, *economic_fixture(tmp_path / "other"))
    data = json.loads(p.read_text())
    data["economic_scope"]["economic"]["unit"] = "PRIVATE UNIT"
    p.write_text(json.dumps(data))
    result = CliRunner().invoke(
        app, ["evaluate-synthetic", "--history", str(h), "--protocol", str(p)]
    )
    assert result.exit_code == 2 and "PRIVATE UNIT" not in result.output


def test_earlier_economic_work_cannot_be_scored_as_initial(tmp_path):
    from tests.test_reconciliation import NOW

    history, protocol = economic_fixture(tmp_path)
    for record in history["bundle"]["records"]:
        if record["kind"] == "economic_evidence" and record["source"]["source_key"] == "truth":
            record["start"] = record["end"] = NOW.isoformat()
        if record["kind"] == "source_coverage" and record["run"]["run_id"] == "target":
            record["start"] = NOW.isoformat()
    row = evaluate(tmp_path, history, protocol)["economic"]["cases"][0]
    assert "contradicted_work_bounds" in row["truth"]["reasons"]
    assert row["status"] == "not_initial"


def test_late_policy_rejected_even_for_cold_start(tmp_path):
    history, protocol, _ = adaptive_fixture(tmp_path, peers=())
    policy_id = protocol["cases"][0]["adaptive"]["policy"]["record_id"]
    policy = next(r for r in history["bundle"]["records"] if r["record_id"] == policy_id)
    policy["recorded_at"] = protocol["cases"][0]["forecast_at"]
    h, p = write_inputs(tmp_path, history, protocol)
    result = CliRunner().invoke(
        app, ["evaluate-synthetic", "--history", str(h), "--protocol", str(p)]
    )
    assert result.exit_code == 2


def test_independent_truth_minimum_must_be_registered(tmp_path):
    history, protocol = economic_fixture(tmp_path)
    protocol.pop("minimum_independent_truth", None)
    h, p = write_inputs(tmp_path, history, protocol)
    result = CliRunner().invoke(
        app, ["evaluate-synthetic", "--history", str(h), "--protocol", str(p)]
    )
    assert result.exit_code == 2


def test_zero_terminal_spend_is_undefined(tmp_path):
    history, protocol = economic_fixture(tmp_path, count=0)
    next(r for r in history["bundle"]["records"] if r["kind"] == "economic_evidence")["component"][
        "amount"
    ] = "0"
    result = evaluate(tmp_path, history, protocol)["abandonment"]
    assert result["share"] is None and result["undefined_reason"] == "zero_terminal_amount"


def test_pending_correction_keeps_raw_and_effective_denominators(tmp_path):
    from changecost.store import Store
    from tests.test_reconciliation import NOW, event, import_events, locator

    history, protocol = economic_fixture(tmp_path, count=0)
    store = Store(tmp_path / "db", clock=lambda: NOW + timedelta(seconds=3))
    import_events(
        store, event("pending", "7", replaces=locator("absent"), correction_reason="fixture")
    )
    attribution = evaluate(tmp_path, portable_timeline(store), protocol)["attribution"]
    assert attribution["pending_correction_count"] == 1
    assert attribution["raw_record_count"] == attribution["diagnostic_denominator"] == 2
    assert attribution["effective_event_count"] == 1


def test_partial_demand_has_explicit_truth_category_denominator(tmp_path):
    history, protocol, _ = adaptive_fixture(tmp_path, complete=False)
    result = evaluate(tmp_path, history, protocol)["adaptive"]
    assert result["truth_categories"] == {
        "observed": 0,
        "partial": 1,
        "unavailable": 0,
        "imputed": 0,
    }
    assert result["outcome_counts"] == {"accepted": 1}
