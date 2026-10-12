"""Synthetic spec-derived demand tests; no native calibration claims."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import pytest

import changecost.demand as demand
from changecost.demand import DemandRequest, compute_demand, compute_validation, inspect_demand
from changecost.models import (
    Assessment,
    DemandComponent,
    DemandObservation,
    Dimensions,
    Ecosystem,
    Evidence,
    EvidenceBinding,
    MatchedComparison,
    MeasurementPolicy,
    PriceRate,
    PriceScenario,
    Quantity,
    Rehearsal,
    RunRef,
    TransferHypothesis,
    ValidationCase,
    ValidationPolicy,
)
from changecost.operations import (
    LifecycleDeclaration,
    common,
    declare,
    register_change,
    register_run,
)
from changecost.serialization import ContractError, dumps_bundle, loads_bundle
from changecost.store import Store, reference

NOW = datetime(2026, 10, 11, 10, tzinfo=UTC)
COMP = DemandComponent(category="input", unit="tokens", basis="observed")
DIMS = Dimensions(
    scope="low", coupling="low", novelty="low", ambiguity="low", validation="low", context="low"
)


@dataclass(frozen=True)
class PeerOptions:
    eco: Ecosystem | None = None
    complete: bool = True
    outcome: str = "accepted"
    dims: Dimensions = DIMS
    provider: str = "synthetic"
    surface: str = "fixture"
    observed_start: bool = False


class World:
    def __init__(self, path):
        self.time = NOW
        self.store = Store(path, clock=lambda: self.time)
        self.change = register_change(self.store, "repo", "target")
        self.policy = self.add(
            MeasurementPolicy, "policy", version="synthetic-demand/v1", component=COMP
        )
        self.eco = self.ecosystem("eco", "model")
        self.assessment = self.assess(self.change, "a")

    def add(self, cls, ident, **kwargs):
        def operation(records, origin, now):
            record = cls(**common(origin, now, ident), **kwargs)
            return [record], record

        return self.store.apply(operation)

    def tick(self):
        self.time += timedelta(seconds=1)

    def ecosystem(self, ident, model, **kwargs):
        fields = dict(
            provider="synthetic",
            surface="fixture",
            model=model,
            model_version="1",
            runtime="fixture/v1",
            reasoning="normal",
            harness="fixture",
            review="none",
            measurement_policy=reference(self.policy),
        )
        return self.add(Ecosystem, ident, **(fields | kwargs))

    def assess(self, change, ident, **kwargs):
        fields = dict(
            change=reference(change),
            dimensions=DIMS,
            scope_key="same-task",
            assessor="manual",
            evidence=["synthetic assessment"],
        )
        return self.add(Assessment, ident, **(fields | kwargs))

    def peer(self, name, values, **kwargs):
        options = PeerOptions(**kwargs)
        self.tick()
        change = register_change(self.store, "repo", name)
        assessment = self.assess(change, name + "-a", dimensions=options.dims)
        self.tick()
        eco = options.eco or self.eco
        observations = []
        for i, value in enumerate(values):
            run = register_run(
                self.store,
                RunRef(
                    repository_id="repo",
                    provider=options.provider,
                    surface=options.surface,
                    run_id=f"{name}-{i}",
                ),
                name,
                work_start=self.time if options.observed_start else None,
            )
            start = self.time
            self.tick()
            declare(
                self.store,
                reference(run),
                LifecycleDeclaration(start=start, end=self.time, outcome="succeeded"),
            )
            evidence = self.add(
                Evidence,
                f"{name}-e{i}",
                provider="synthetic",
                surface="fixture",
                profile="synthetic-demand/v1",
                identity_scope="namespaced",
                source_key=f"{name}-{i}",
            )
            self.add(EvidenceBinding, f"{name}-b{i}", evidence=reference(evidence), run=run.ref)
            obs = self.add(
                DemandObservation,
                f"{name}-o{i}",
                run=run.ref,
                assessment=reference(assessment),
                ecosystem=reference(eco),
                component=COMP,
                quantity=value,
                start=start,
                end=self.time,
                final=True,
                complete=options.complete,
                evidence=[reference(evidence)],
            )
            observations.append(obs)
        declare(self.store, reference(change), LifecycleDeclaration(outcome=options.outcome))
        return change, observations

    def forecast(self, operation="f", **kwargs):
        selectors = DemandRequest(
            "repo",
            "target",
            operation,
            **(
                dict(assessment_id=self.assessment.record_id, ecosystem_id=self.eco.record_id)
                | kwargs
            ),
        )
        return compute_demand(self.store, selectors)


@pytest.fixture
def world(tmp_path):
    return World(tmp_path / "db")


def test_cold_start_retry_conflict_backup_and_portable_authority(world, tmp_path):
    f = world.forecast()
    assert f.result.state == "zero_knowledge"
    assert f.result.median is None and f.result.sample_count == 0
    before = world.store.export_bundle()
    assert world.forecast() == f
    assert world.store.export_bundle() == before
    with pytest.raises(ContractError):
        world.forecast(assessment_id="bad")
    assert inspect_demand(world.store, f)["demand_validation"] == "reproduced"
    world.store.backup(tmp_path / "backup")
    assert inspect_demand(Store(tmp_path / "backup", clock=lambda: world.time), f)[
        "local_computation"
    ]
    foreign = Store(tmp_path / "foreign", clock=lambda: world.time + timedelta(days=1))
    foreign.import_bundle(loads_bundle(dumps_bundle(before)))
    view = inspect_demand(foreign, f)
    assert not view["local_computation"] and view["replay_eligibility"] == "replay_unavailable"


def test_complete_change_aggregate_zero_abandoned_and_partial(world):
    world.peer("one", ["1", "2"])
    world.peer("two", ["0"], outcome="abandoned")
    world.peer("partial", ["100"], complete=False)
    f = world.forecast()
    assert f.result.state == "learning"
    assert f.result.sample_count == 2
    assert [f.result.minimum, f.result.median, f.result.maximum] == ["0", "1.5", "3"]
    assert any(e.reason == "incomplete_demand_coverage" for e in f.exclusions)
    assert f.result.validation is None


def test_correction_selected_once_and_historical_replay(world):
    _, observations = world.peer("one", ["2"])
    old = world.forecast("old")
    o = observations[0]
    world.tick()
    world.add(
        DemandObservation,
        "correction",
        **o.model_dump(
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
        quantity="4",
        previous=reference(o),
        reason="correction",
    )
    new = world.forecast("new")
    assert old.result.median == "2" and new.result.median == "4"
    assert new.result.sample_count == 1
    assert inspect_demand(world.store, old)["demand_validation"] == "reproduced"
    before = world.store.export_bundle()
    with pytest.raises(ContractError):
        world.add(
            DemandObservation,
            "fork",
            **o.model_dump(
                exclude={
                    "kind",
                    "schema_version",
                    "record_id",
                    "origin_store_id",
                    "recorded_at",
                    "effective_at",
                    "previous",
                    "reason",
                }
            ),
            previous=reference(o),
            reason="fork",
        )
    assert world.store.export_bundle() == before


def correct_observation_window(world, observation, interval_start, observation_start):
    run = next(
        r
        for r in world.store.export_bundle().records
        if r.kind == "run" and r.ref == observation.run
    )
    world.tick()
    declare(
        world.store,
        reference(run),
        LifecycleDeclaration(
            start=interval_start, correct_interval=True, reason="fixture interval correction"
        ),
    )
    return world.add(
        DemandObservation,
        observation.record_id + "-window-correction",
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
                "start",
            }
        ),
        start=observation_start,
        previous=reference(observation),
        reason="fixture observation window correction",
    )


@pytest.mark.parametrize("observed_start", [True, False])
@pytest.mark.parametrize("offset", [-500000, 0, 500000])
def test_complete_coverage_respects_known_start_and_latest_interval(world, observed_start, offset):
    _, observations = world.peer("window", ["9"], observed_start=observed_start)
    old = world.forecast("before-window-correction")
    observation = observations[0]
    corrected_start = observation.start + timedelta(microseconds=500000)
    boundary = observation.start if observed_start else corrected_start
    correct_observation_window(
        world, observation, corrected_start, boundary + timedelta(microseconds=offset)
    )
    current = world.forecast("after-window-correction")
    assert inspect_demand(world.store, old)["demand_validation"] == "reproduced"
    if offset <= 0:
        assert current.result.sample_count == 1 and current.result.median == "9"
    else:
        assert current.result.state == "zero_knowledge" and current.result.sample_count == 0
        assert any(e.reason == "incomplete_demand_coverage" for e in current.exclusions)


def test_target_unknown_ecosystem_and_exact_dimensions(world):
    world.peer("broad", ["100"], dims=DIMS.model_copy(update={"scope": "high"}))
    world.peer("exact", ["3"])
    assert world.forecast().result.median == "3"
    unknown = world.ecosystem("unknown", None)
    assert (
        world.forecast("unknown-f", ecosystem_id=unknown.record_id).result.state == "zero_knowledge"
    )
    # The terminal target never supplies its own truth, including later forecasts.
    declare(world.store, reference(world.change), LifecycleDeclaration(outcome="abandoned"))
    assert world.forecast("later").result.sample_count == 1


def test_late_assessment_unknown_dimensions_and_mixed_models(world):
    change, observations = world.peer("one", ["3"])
    late = world.assess(change, "late")
    with pytest.raises(ContractError):
        world.add(
            DemandObservation,
            "late-o",
            **observations[0].model_dump(
                exclude={
                    "kind",
                    "schema_version",
                    "record_id",
                    "origin_store_id",
                    "recorded_at",
                    "effective_at",
                    "assessment",
                    "previous",
                    "reason",
                }
            ),
            assessment=reference(late),
        )
    other = world.ecosystem("other", "other")
    _, obs = world.peer("mixed", ["2", "5"])
    world.tick()
    o = obs[1]
    world.add(
        DemandObservation,
        "mixed-correction",
        **o.model_dump(
            exclude={
                "kind",
                "schema_version",
                "record_id",
                "origin_store_id",
                "recorded_at",
                "effective_at",
                "ecosystem",
                "previous",
                "reason",
            }
        ),
        ecosystem=reference(other),
        previous=reference(o),
        reason="mixed",
    )
    f = world.forecast()
    assert f.result.sample_count == 1
    assert any(e.reason == "mixed_or_unknown_ecosystem" for e in f.exclusions)


def make_bridge(world, donor_value="3", target_value="1", confounding=None):
    source_eco = world.ecosystem("old-model", "old")
    source, _ = world.peer("donor", [donor_value], eco=source_eco)
    target, _ = world.peer("bridge-target", [target_value])
    pair = world.add(
        MatchedComparison,
        "pair",
        source_change=reference(source),
        target_change=reference(target),
        source_ecosystem=reference(source_eco),
        target_ecosystem=reference(world.eco),
        scope_key="same-task",
        confounding=confounding or [],
    )
    world.add(
        TransferHypothesis,
        "bridge",
        source_ecosystem=reference(source_eco),
        target_ecosystem=reference(world.eco),
        component=COMP,
        dimensions=DIMS,
        comparisons=[reference(pair)],
    )
    return pair


def test_directional_exact_ratio_target_preference_and_future_pair(world):
    old = world.forecast("old")
    make_bridge(world)
    f = world.forecast("with-bridge")
    assert f.result.state == "learning" and f.result.sample_count == 1
    assert f.result.transfer.ratio == "1/3"
    assert f.result.transfer.pair_count == 1
    assert inspect_demand(world.store, old)["demand_validation"] == "reproduced"
    assert old.result.transfer is None


@pytest.mark.parametrize("value,confounding", [("0", []), ("3", ["task-and-model"])])
def test_invalid_transfer_remains_diagnostic(world, value, confounding):
    make_bridge(world, donor_value=value, confounding=confounding)
    f = world.forecast()
    assert f.result.transfer is None
    assert f.result.sample_count == 1
    assert f.exclusions


def test_native_policy_label_count_and_imported_validation_do_not_promote(world):
    native = world.add(MeasurementPolicy, "native-policy", version="codex/native", component=COMP)
    eco = world.ecosystem("native", "model", measurement_policy=reference(native))
    world.peer("native-peer", ["100"], eco=eco)
    assert world.forecast("native-f", ecosystem_id=eco.record_id).result.state == "zero_knowledge"
    for n in range(20):
        world.peer(f"p{n}", ["1"])
    assert world.forecast().result.state == "learning"


def test_rehearsal_overhead_rates_and_privacy(world):
    with pytest.raises(ValueError):
        Rehearsal(
            budget=Quantity(component=COMP, amount="1"),
            overhead=Quantity(component=COMP, amount="2"),
            method="read_only_assessment",
        )
    with pytest.raises(ValueError):
        world.assessment.model_validate(world.assessment.model_dump() | {"prompt": "private"})
    world.peer("one", ["2"])
    price = world.add(
        PriceScenario,
        "price",
        effective_date=NOW,
        source="explicit-user-rate",
        currency="USD",
        rates=[PriceRate(component=COMP, rate="0.25")],
    )
    f = world.forecast(price_id=price.record_id)
    assert f.price.amount == "1/2" and f.price.basis == "estimated"
    with pytest.raises(ValueError):
        PriceScenario(**common("x", NOW, "invalid"), effective_date=NOW, currency="USD", rates=[])


def test_failed_commit_and_operation_mode_conflict_are_atomic(world, monkeypatch):
    before = world.store.export_bundle()

    def fail(_):
        raise OSError("fixture")

    monkeypatch.setattr(world.store, "commit", fail)
    with pytest.raises(ContractError):
        world.forecast()
    assert world.store.export_bundle() == before


def registered_policy(world, ident="rubric", **kwargs):
    fields = dict(
        ecosystem=reference(world.eco),
        component=COMP,
        minimum_truth=1,
        nominal_coverage="1",
        coverage_tolerance="0",
        maximum_underestimate="0",
        maximum_width="2",
        maximum_overhead="0",
        require_baseline=True,
    )
    return world.add(ValidationPolicy, ident, **(fields | kwargs))


def evaluated_task(world, name, actual, advance_baseline=False, retrospective_offset=None):
    world.tick()
    change = register_change(world.store, "repo", name)
    assessment = world.assess(change, name + "-a")
    if retrospective_offset is not None:
        world.tick()
    forecast = compute_demand(
        world.store,
        DemandRequest("repo", name, name + "-f", assessment.record_id, world.eco.record_id),
    )
    if advance_baseline:
        world.tick()
    baseline = compute_demand(
        world.store,
        DemandRequest(
            "repo",
            name,
            name + "-baseline",
            assessment.record_id,
            world.eco.record_id,
            broad_baseline=True,
        ),
    )
    world.tick()
    start = (
        forecast.cutoff.at + timedelta(microseconds=retrospective_offset)
        if retrospective_offset is not None
        else world.time
    )
    run = register_run(
        world.store,
        RunRef(repository_id="repo", provider="synthetic", surface="fixture", run_id=name),
        name,
        work_start=start if retrospective_offset is not None else None,
    )
    world.tick()
    declare(
        world.store,
        reference(run),
        LifecycleDeclaration(start=start, end=world.time, outcome="succeeded"),
    )
    evidence = world.add(
        Evidence,
        name + "-e",
        provider="synthetic",
        surface="fixture",
        profile="synthetic-demand/v1",
        identity_scope="namespaced",
        source_key=name,
    )
    world.add(EvidenceBinding, name + "-b", evidence=reference(evidence), run=run.ref)
    world.add(
        DemandObservation,
        name + "-o",
        run=run.ref,
        assessment=reference(assessment),
        ecosystem=reference(world.eco),
        component=COMP,
        quantity=actual,
        start=start,
        end=world.time,
        final=True,
        complete=True,
        evidence=[reference(evidence)],
    )
    declare(world.store, reference(change), LifecycleDeclaration(outcome="accepted"))
    return ValidationCase(
        forecast=reference(forecast), truth=reference(change), baseline=reference(baseline)
    )


def test_registered_measured_validation_foreign_claim_and_withdrawal(world, tmp_path):
    world.peer("one", ["1"])
    world.peer("three", ["3"])
    world.tick()
    policy = registered_policy(world)
    case = evaluated_task(world, "evaluation", "2")
    receipt = compute_validation(world.store, policy.record_id, [case], "receipt")
    assert receipt.passed and receipt.metrics.count == 1
    assert compute_validation(world.store, policy.record_id, [case], "receipt") == receipt
    supported = world.forecast("supported")
    assert supported.result.state == "validated_forecast"
    assert inspect_demand(world.store, supported)["demand_validation"] == "reproduced"
    foreign = Store(tmp_path / "foreign-validation", clock=lambda: world.time)
    foreign.import_bundle(world.store.export_bundle())
    claim = compute_demand(foreign, DemandRequest("repo", "target", "claim", "a", "eco"))
    assert claim.result.state == "zero_knowledge" and claim.result.validation is None
    failure = evaluated_task(world, "failed-evaluation", "50")
    failed = compute_validation(world.store, policy.record_id, [failure], "failed-receipt")
    assert not failed.passed
    assert world.forecast("withdrawn").result.state == "learning"
    assert inspect_demand(world.store, supported)["demand_validation"] == "reproduced"


def test_late_rubric_and_duplicate_validation_truth_reject(world):
    world.peer("one", ["1"])
    case = evaluated_task(world, "evaluation", "1")
    world.tick()
    policy = registered_policy(world)
    before = world.store.export_bundle()
    with pytest.raises(ContractError):
        compute_validation(world.store, policy.record_id, [case], "late")
    with pytest.raises(ContractError):
        compute_validation(world.store, policy.record_id, [case, case], "duplicates")
    assert world.store.export_bundle() == before


def test_initial_forecast_and_diagnostic_update_are_distinguishable(world):
    world.peer("one", ["1"])
    initial = world.forecast("initial")
    assert initial.initial is True
    world.tick()
    run = register_run(
        world.store,
        RunRef(repository_id="repo", provider="synthetic", surface="fixture", run_id="target-run"),
        "target",
    )
    declare(world.store, reference(run), LifecycleDeclaration(start=world.time))
    assert world.forecast("diagnostic").initial is False


def test_native_run_identity_cannot_be_laundered_by_synthetic_labels(world):
    world.peer("native", ["99"], provider="codex", surface="cli")
    forecast = world.forecast()
    assert forecast.result.state == "zero_knowledge"
    assert any(e.reason == "unsupported_native_run" for e in forecast.exclusions)


def test_overlapping_rubric_drift_and_failure_withdraw_prior_validation(world):
    world.peer("one", ["1"])
    world.peer("three", ["3"])
    world.tick()
    first = registered_policy(world)
    case = evaluated_task(world, "first-eval", "2")
    assert compute_validation(world.store, first.record_id, [case], "first-receipt").passed
    supported = world.forecast("supported")
    assert supported.result.state == "validated_forecast"
    world.tick()
    second = registered_policy(world, "second-rubric")
    assert world.forecast("drifted").result.state == "learning"
    case = evaluated_task(world, "second-eval", "50")
    assert not compute_validation(world.store, second.record_id, [case], "second-receipt").passed
    assert world.forecast("withdrawn").result.state == "learning"
    assert inspect_demand(world.store, supported)["demand_validation"] == "reproduced"


def test_baseline_with_advancing_clock_uses_identical_frozen_evidence(world):
    world.peer("one", ["1"])
    world.peer("three", ["3"])
    world.tick()
    policy = registered_policy(world)
    case = evaluated_task(world, "evaluation", "2", advance_baseline=True)
    receipt = compute_validation(world.store, policy.record_id, [case], "receipt")
    assert receipt.passed


def test_same_transaction_overlapping_rubrics_leave_validation_unavailable(world):
    world.peer("one", ["1"])
    world.peer("three", ["3"])
    world.tick()
    first = registered_policy(world, "template")
    world.tick()
    second = first.model_copy(
        update={"record_id": "tied-a", "recorded_at": world.time, "effective_at": world.time}
    )
    third = second.model_copy(update={"record_id": "tied-z"})
    world.store.apply(lambda records, origin, now: ([second, third], None))
    case = evaluated_task(world, "passing", "2")
    assert compute_validation(world.store, second.record_id, [case], "pass").passed
    failure = evaluated_task(world, "failing", "50")
    assert not compute_validation(world.store, third.record_id, [failure], "fail").passed
    assert world.forecast("ambiguous").result.state == "learning"


def test_transfer_maps_donor_cohort_separately_from_pair_support(world):
    old = world.forecast("before-bridge")
    make_bridge(world)
    source_eco = next(r for r in world.store.export_bundle().records if r.record_id == "old-model")
    donor, _ = world.peer("more-donor", ["300"], eco=source_eco)
    world.peer("partial-donor", ["999"], eco=source_eco, complete=False)
    forecast = world.forecast("mapped")
    transfer = forecast.result.transfer
    assert transfer.pair_count == 1 and transfer.donor_count == 2
    assert set(transfer.scenarios) == {"1", "100"}
    assert reference(donor) in transfer.donors
    assert forecast.result.sample_count == 1
    assert transfer.residuals == ["0"]
    assert inspect_demand(world.store, old)["demand_validation"] == "reproduced"


@pytest.mark.parametrize("offset", [-500_000, 0, 500_000, 1_000_000, 1_500_000])
def test_validation_rechecks_late_registered_truth_cutoffs(world, offset):
    world.peer("one", ["1"])
    world.peer("three", ["3"])
    world.tick()
    policy = registered_policy(world)
    case = evaluated_task(world, "retrospective", "2", True, offset)
    records = {(r.kind, r.record_id): r for r in world.store.export_bundle().records}
    forecast = records[(case.forecast.kind, case.forecast.record_id)]
    assert case.baseline is not None
    baseline = records[(case.baseline.kind, case.baseline.record_id)]
    assert forecast.initial and baseline.initial
    before = world.store.export_bundle()
    if offset <= 1_000_000:
        with pytest.raises(ContractError, match="before truth work"):
            compute_validation(world.store, policy.record_id, [case], "retrospective-receipt")
        assert world.store.export_bundle() == before
        assert world.forecast("not-promoted").result.state == "learning"
    else:
        receipt = compute_validation(world.store, policy.record_id, [case], "retrospective-receipt")
        assert receipt.passed
        assert world.forecast("promoted").result.state == "validated_forecast"
    for prediction in (forecast, baseline):
        assert inspect_demand(world.store, prediction)["demand_validation"] == "reproduced"


def test_validation_excludes_uncovered_immutable_run_start(world):
    world.peer("seed", ["2"])
    policy = registered_policy(world)
    case = evaluated_task(world, "coverage-evaluation", "2", retrospective_offset=1000000)
    observations = [
        r
        for r in world.store.export_bundle().records
        if r.kind == "demand_observation" and r.record_id == "coverage-evaluation-o"
    ]
    observation = observations[0]
    before_receipt = compute_validation(world.store, policy.record_id, [case], "complete-receipt")
    assert before_receipt.passed
    corrected_start = observation.start + timedelta(microseconds=500000)
    correct_observation_window(world, observation, corrected_start, corrected_start)
    before = world.store.export_bundle()
    with pytest.raises(ContractError, match="complete validation truth unavailable"):
        compute_validation(world.store, policy.record_id, [case], "partial-receipt")
    assert world.store.export_bundle() == before


def test_shared_validation_replay_is_operation_scoped_and_bounded(world, monkeypatch, tmp_path):
    world.peer("seed", ["2"])
    policy = registered_policy(world)
    for generation in range(4):
        case = evaluated_task(world, f"generation-{generation}", "2")
        assert compute_validation(
            world.store, policy.record_id, [case], f"receipt-{generation}"
        ).passed
    case = evaluated_task(world, "generation-final", "2")
    measured = []
    original = demand.measure_validation

    def counted(*args, **kwargs):
        measured.append(tuple(c.truth.record_id for c in args[3]))
        return original(*args, **kwargs)

    monkeypatch.setattr(demand, "measure_validation", counted)
    assert compute_validation(world.store, policy.record_id, [case], "receipt-final").passed
    assert len(measured) == len(set(measured)) == 5
    current = world.forecast("after-chain")
    before = world.store.export_bundle()
    for _ in range(2):
        measured.clear()
        assert inspect_demand(world.store, current)["demand_validation"] == "reproduced"
        assert len(measured) == len(set(measured)) == 5
    assert world.store.export_bundle() == before
    foreign = Store(tmp_path / "foreign-memo", clock=lambda: world.time + timedelta(days=1))
    foreign.import_bundle(loads_bundle(dumps_bundle(before)))
    assert inspect_demand(foreign, current)["demand_validation"] == "producer_claim"
    world.tick()
    failed_policy = registered_policy(world, "failed-rubric")
    failed_case = evaluated_task(world, "failed-memo-evaluation", "50")
    assert not compute_validation(
        world.store, failed_policy.record_id, [failed_case], "failed-memo-receipt"
    ).passed
    assert world.forecast("after-failed-rubric").result.state == "learning"
    assert inspect_demand(world.store, current)["demand_validation"] == "reproduced"
