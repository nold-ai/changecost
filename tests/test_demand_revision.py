"""Versioned temporal correction and actual validation-support boundaries."""

from datetime import timedelta
from functools import partial

import pytest

import changecost.demand as demand
from changecost.models import DemandObservation
from changecost.operations import LifecycleDeclaration, declare
from changecost.store import reference
from tests.test_demand import NOW, World, evaluated_task, registered_policy


@pytest.fixture
def world(tmp_path):
    return World(tmp_path / "revision-db")


def test_current_target_selected_validation_support_is_excluded(world):
    world.peer("seed", ["2"])
    world.peer("target", ["2"])
    world.tick()
    policy = registered_policy(world)
    case = evaluated_task(world, "evaluation", "2")
    receipt = demand.compute_validation(world.store, policy.record_id, [case], "receipt")
    assert receipt.passed
    records = {(r.kind, r.record_id): r for r in world.store.export_bundle().records}
    assert reference(world.change) in records[(case.forecast.kind, case.forecast.record_id)].peers
    forecast = world.forecast("self-trained-validation")
    assert forecast.result.state == "learning"
    assert forecast.result.validation is None


def test_current_corrected_interval_restores_peer_eligibility(world):
    _change, observations = world.peer("peer", ["9"])
    observation = observations[0]
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
            start=NOW - timedelta(seconds=1),
            correct_interval=True,
            reason="erroneous early bound",
        ),
    )
    world.tick()
    declare(
        world.store,
        reference(run),
        LifecycleDeclaration(
            start=observation.start, correct_interval=True, reason="corrected bound"
        ),
    )
    forecast = world.forecast("current-corrected")
    assert forecast.result.sample_count == 1
    assert forecast.result.median == "9"
    assert demand.inspect_demand(world.store, forecast)["demand_validation"] == "reproduced"


def test_new_default_is_v4(world):
    assert world.forecast().algorithm == "observed-summary/v4"


def correct_observation(world, observation, ident, **updates):
    values = observation.model_dump(
        exclude={
            "record_id",
            "origin_store_id",
            "recorded_at",
            "effective_at",
            "kind",
            "previous",
            "reason",
        }
    )
    return world.add(
        DemandObservation,
        ident,
        **(
            values
            | {"previous": reference(observation), "reason": "correct temporal bound"}
            | updates
        ),
    )


@pytest.mark.parametrize("version", ["observed-summary/v2", "observed-summary/v3"])
def test_new_receipt_current_observation_truth_and_legacy_candidates(world, monkeypatch, version):
    world.peer("seed", ["2"])
    world.tick()
    policy = registered_policy(world)
    with monkeypatch.context() as legacy:
        legacy.setattr(demand, "ForecastInputs", partial(demand.ForecastInputs, algorithm=version))
        case = evaluated_task(world, "observed-truth", "2", advance_baseline=True)
    observation = next(
        r for r in world.store.export_bundle().records if r.record_id == "observed-truth-o"
    )
    assessment = next(
        r for r in world.store.export_bundle().records if r.record_id == "observed-truth-a"
    )
    world.tick()
    wrong = correct_observation(
        world,
        observation,
        "wrong-observation",
        start=assessment.recorded_at + timedelta(microseconds=1),
    )
    world.tick()
    correct_observation(world, wrong, "restored-observation", start=observation.start)
    receipt = demand.compute_validation(
        world.store, policy.record_id, [case], "current-truth-receipt"
    )
    assert receipt.passed
    with world.store.connect(readonly=True) as connection:
        request = connection.execute(
            "SELECT request FROM computations WHERE operation_id=?", (receipt.operation_id,)
        ).fetchone()[0]
        assert demand.validation_generation(request) == "demand-validation/v3"
        context = demand.ReplayContext(connection)
        assert demand.validation_reproduced(context, demand.read_records(connection), receipt)
    assert (
        demand.compute_validation(world.store, policy.record_id, [case], receipt.operation_id)
        == receipt
    )


def test_metadata_inventory_is_not_selected_training_support(world):
    world.peer("seed", ["2"])
    world.tick()
    policy = registered_policy(world)
    case = evaluated_task(world, "independent", "2")
    receipt = demand.compute_validation(
        world.store, policy.record_id, [case], "independent-receipt"
    )
    forecast = world.forecast("independent-current")
    assert forecast.result.state == "validated_forecast"
    with world.store.connect(readonly=True) as connection:
        records = demand.read_records(connection)
        candidate = records[(case.forecast.kind, case.forecast.record_id)]
        assert reference(world.change) in candidate.inputs
        assert reference(world.change) not in demand.selected_validation_support(
            connection, records, receipt
        )


def test_nested_selected_receipt_support_excludes_target(world):
    world.peer("seed", ["2"])
    world.tick()
    policy = registered_policy(world)
    first_case = evaluated_task(world, "target", "2")
    first = demand.compute_validation(world.store, policy.record_id, [first_case], "first-receipt")
    observation = next(r for r in world.store.export_bundle().records if r.record_id == "target-o")
    world.tick()
    correct_observation(world, observation, "target-partial", complete=False)
    second_case = evaluated_task(world, "outer", "2")
    records = {(r.kind, r.record_id): r for r in world.store.export_bundle().records}
    candidate = records[(second_case.forecast.kind, second_case.forecast.record_id)]
    assert reference(world.change) not in candidate.peers
    assert candidate.result.validation == reference(first)
    second = demand.compute_validation(
        world.store, policy.record_id, [second_case], "outer-receipt"
    )
    assert second.passed
    assert world.forecast("nested-current").result.state == "learning"


@pytest.mark.parametrize("algorithm", ["observed-summary/v1", "observed-summary/v2"])
def test_legacy_conservative_payload_and_request_retry_recovery(
    world, monkeypatch, tmp_path, algorithm
):
    _change, observations = world.peer("seed", ["2"])
    observation = observations[0]
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
            start=NOW - timedelta(seconds=1), correct_interval=True, reason="erroneous"
        ),
    )
    world.tick()
    declare(
        world.store,
        reference(run),
        LifecycleDeclaration(start=observation.start, correct_interval=True, reason="corrected"),
    )
    with monkeypatch.context() as legacy:
        legacy.setattr(
            demand, "ForecastInputs", partial(demand.ForecastInputs, algorithm=algorithm)
        )
        old = world.forecast("legacy-conservative")
    assert old.result.sample_count == 0
    current = world.forecast("current-corrected")
    assert current.result.sample_count == 1
    before = world.store.export_bundle()
    assert world.forecast("legacy-conservative") == old
    assert world.store.export_bundle() == before
    for forecast in (old, current):
        assert demand.inspect_demand(world.store, forecast)["demand_validation"] == "reproduced"
    world.store.backup(tmp_path / "versioned-backup")
    from changecost.store import Store

    restored = Store(tmp_path / "versioned-backup", clock=lambda: world.time)
    for forecast in (old, current):
        assert demand.inspect_demand(restored, forecast)["demand_validation"] == "reproduced"


@pytest.mark.parametrize("bad", ["{}", "[]", "[[1]]", "null", '["demand-validation/v99"]'])
def test_unknown_private_receipt_generation_is_not_authority(world, bad):
    world.peer("seed", ["2"])
    policy = registered_policy(world)
    case = evaluated_task(world, "bad-generation", "2")
    receipt = demand.compute_validation(world.store, policy.record_id, [case], "typed-receipt")
    with world.store.connect() as connection:
        connection.execute(
            "UPDATE computations SET request=? WHERE operation_id=?", (bad, receipt.operation_id)
        )
        connection.commit()
    with world.store.connect(readonly=True) as connection:
        records = demand.read_records(connection)
        assert (receipt.kind, receipt.record_id) not in demand.demand_computation_refs(
            connection, records
        )
        assert not demand.validation_reproduced(demand.ReplayContext(connection), records, receipt)
    assert world.forecast("bad-generation-current").result.state == "learning"


def test_legacy_receipt_retry_uses_exact_original_generation(world):
    world.peer("seed", ["2"])
    policy = registered_policy(world)
    case = evaluated_task(world, "legacy-receipt-eval", "2")
    receipt = demand.compute_validation(world.store, policy.record_id, [case], "old-request")
    old_request = demand.validation_request(policy, [case], "demand-validation/v1")
    with world.store.connect() as connection:
        connection.execute(
            "UPDATE computations SET request=? WHERE operation_id=?",
            (old_request, receipt.operation_id),
        )
        connection.commit()
    before = world.store.export_bundle()
    assert (
        demand.compute_validation(world.store, policy.record_id, [case], "old-request") == receipt
    )
    assert world.store.export_bundle() == before
    with world.store.connect(readonly=True) as connection:
        assert (
            connection.execute(
                "SELECT request FROM computations WHERE operation_id='old-request'"
            ).fetchone()[0]
            == old_request
        )
        context = demand.ReplayContext(connection)
        assert demand.validation_reproduced(context, demand.read_records(connection), receipt)
        assert any(
            len(identity) == 4 and identity[2] == "observed-summary/v1"
            for identity in context.completed
        )


@pytest.mark.parametrize("algorithm", ["observed-summary/v2", "observed-summary/v3"])
def test_selected_transfer_donor_support_is_target_support(world, algorithm, monkeypatch):
    from changecost.models import MatchedComparison, TransferHypothesis
    from tests.test_demand import COMP, DIMS

    source_eco = world.ecosystem("source", "old-model")
    target, _observations = world.peer("target", ["3"], eco=source_eco)
    destination, _observations = world.peer("destination", ["2"])
    pair = world.add(
        MatchedComparison,
        "target-pair",
        source_change=reference(target),
        target_change=reference(destination),
        source_ecosystem=reference(source_eco),
        target_ecosystem=reference(world.eco),
        scope_key="same-task",
    )
    world.add(
        TransferHypothesis,
        "target-bridge",
        source_ecosystem=reference(source_eco),
        target_ecosystem=reference(world.eco),
        component=COMP,
        dimensions=DIMS,
        comparisons=[reference(pair)],
    )
    policy = registered_policy(world)
    with monkeypatch.context() as selected:
        selected.setattr(
            demand, "ForecastInputs", partial(demand.ForecastInputs, algorithm=algorithm)
        )
        case = evaluated_task(world, "transfer-evaluation", "2")
    receipt = demand.compute_validation(world.store, policy.record_id, [case], "donor-receipt")
    assert receipt.passed
    with world.store.connect(readonly=True) as connection:
        records = demand.read_records(connection)
        candidate = records[(case.forecast.kind, case.forecast.record_id)]
        assert reference(target) not in candidate.peers
        assert reference(target) in candidate.result.transfer.donors
        assert reference(target) in demand.selected_validation_support(connection, records, receipt)
    assert world.forecast("current-donor-support").result.state == "learning"


def test_unselected_structural_previous_is_not_training_support(world):
    world.peer("seed", ["2"])
    world.tick()
    policy = registered_policy(world)
    first_case = evaluated_task(world, "target", "2")
    first = demand.compute_validation(
        world.store, policy.record_id, [first_case], "previous-target"
    )
    observation = next(r for r in world.store.export_bundle().records if r.record_id == "target-o")
    world.tick()
    correct_observation(world, observation, "target-incomplete", complete=False)
    second_case = evaluated_task(world, "independent-new", "2")
    records = {(r.kind, r.record_id): r for r in world.store.export_bundle().records}
    candidate = records[(second_case.forecast.kind, second_case.forecast.record_id)]
    assert second_case.baseline is not None
    baseline = records[(second_case.baseline.kind, second_case.baseline.record_id)]
    # Structural traversal oracle: remove the selected receipt edge from these
    # detached records while retaining broad inventory and structural previous.
    records[(candidate.kind, candidate.record_id)] = candidate.model_copy(
        update={"result": candidate.result.model_copy(update={"validation": None})}
    )
    records[(baseline.kind, baseline.record_id)] = baseline.model_copy(
        update={"result": baseline.result.model_copy(update={"validation": None})}
    )
    second = first.model_copy(
        update={
            "record_id": "structural-only",
            "cases": [second_case],
            "previous": reference(first),
            "cutoff": world.forecast("structural-cutoff").cutoff,
        }
    )
    with world.store.connect(readonly=True) as connection:
        assert reference(world.change) not in demand.selected_validation_support(
            connection, records, second
        )


def imported_rubric_world(tmp_path, field, offset):
    from changecost.store import Store

    source = World(tmp_path / "source")
    policy = registered_policy(source)
    policy = policy.model_copy(update={field: source.time + timedelta(seconds=4) + offset})
    bundle = source.store.export_bundle()
    bundle = bundle.model_copy(
        update={
            "records": [policy if r.record_id == policy.record_id else r for r in bundle.records]
        }
    )
    world = World.__new__(World)
    world.time = source.time
    world.store = Store(tmp_path / "imported", clock=lambda: world.time)
    world.store.import_bundle(bundle)
    world.change, world.assessment = source.change, source.assessment
    world.policy, world.eco = source.policy, source.eco
    world.peer("seed", ["2"])
    return world, policy


@pytest.mark.parametrize("field", ["recorded_at", "effective_at"])
@pytest.mark.parametrize("offset", [timedelta(0), timedelta(days=1)])
def test_intrinsic_rubric_preregistration_rejects_atomically(tmp_path, field, offset):
    from changecost.serialization import ContractError

    world, policy = imported_rubric_world(tmp_path, field, offset)
    case = evaluated_task(world, "evaluated", "2")
    world.time = max(world.time, policy.recorded_at, policy.effective_at) + timedelta(seconds=1)
    before = world.store.export_bundle()
    with world.store.connect(readonly=True) as connection:
        computations = connection.execute("SELECT * FROM computations").fetchall()
    with pytest.raises(ContractError, match="rubric was not registered"):
        demand.compute_validation(world.store, policy.record_id, [case], "invalid-rubric")
    assert world.store.export_bundle() == before
    with world.store.connect(readonly=True) as connection:
        assert connection.execute("SELECT * FROM computations").fetchall() == computations


@pytest.mark.parametrize("field", ["recorded_at", "effective_at"])
def test_earlier_intrinsic_rubric_remains_valid(tmp_path, field):
    world, policy = imported_rubric_world(tmp_path, field, -timedelta(microseconds=1))
    case = evaluated_task(world, "valid", "2")
    receipt = demand.compute_validation(world.store, policy.record_id, [case], "valid-rubric")
    assert receipt.passed
    assert world.forecast("promoted").result.state == "validated_forecast"


@pytest.mark.parametrize("generation", ["demand-validation/v1", "demand-validation/v2"])
@pytest.mark.parametrize("valid", [False, True])
def test_legacy_receipt_replay_retry_and_current_authority(
    tmp_path, monkeypatch, generation, valid
):
    outer_case = None
    offset = -timedelta(microseconds=1) if valid else timedelta(days=1)
    world, policy = imported_rubric_world(tmp_path, "effective_at", offset)
    with monkeypatch.context() as legacy:
        legacy.setattr(
            demand,
            "ForecastInputs",
            partial(demand.ForecastInputs, algorithm="observed-summary/v3"),
        )
        original_applicability = demand.applicable_validation
        legacy.setattr(
            demand,
            "applicable_validation",
            lambda c, r, t, e, a="observed-summary/v3": original_applicability(c, r, t, e, a),
        )
        case = evaluated_task(world, "historical", "2")
        world.time = max(world.time, policy.effective_at) + timedelta(seconds=1)
        original_request = demand.validation_request
        legacy.setattr(
            demand, "validation_request", lambda p, c, g=generation: original_request(p, c, g)
        )
        legacy.setattr(
            demand,
            "measure_validation",
            partial(demand.measure_validation, strict_registration=False),
        )
        receipt = demand.compute_validation(
            world.store, policy.record_id, [case], "historical-receipt"
        )
        saved = world.forecast("historical-promoted")
        if not valid:
            outer_case = evaluated_task(world, "nested-legacy", "2")
            outer = demand.compute_validation(
                world.store, policy.record_id, [outer_case], "outer-legacy"
            )
            assert outer.passed
    assert receipt.passed
    assert saved.result.state == "validated_forecast"
    before = world.store.export_bundle()
    assert (
        demand.compute_validation(world.store, policy.record_id, [case], receipt.operation_id)
        == receipt
    )
    assert world.forecast("historical-promoted") == saved
    assert world.store.export_bundle() == before
    with world.store.connect(readonly=True) as connection:
        assert demand.validation_reproduced(
            demand.ReplayContext(connection), demand.read_records(connection), receipt
        )
    assert demand.inspect_demand(world.store, saved)["demand_validation"] == "reproduced"
    if not valid:
        from changecost.serialization import ContractError

        assert outer_case is not None
        with pytest.raises(ContractError, match="rubric was not registered"):
            demand.compute_validation(world.store, policy.record_id, [outer_case], "nested-new")
        assert world.store.export_bundle() == before
    current = world.forecast("current-authority")
    assert current.result.state == ("validated_forecast" if valid else "learning")


@pytest.mark.parametrize("field", ["recorded_at", "effective_at"])
def test_late_imported_assessment_cannot_launder_rubric_order(world, monkeypatch, field):
    from changecost.serialization import ContractError

    world.peer("seed", ["2"])
    policy = registered_policy(world)

    def imported_assessment(change, ident):
        assessment = world.assessment.model_copy(
            update={
                "record_id": ident,
                "change": reference(change),
                "recorded_at": world.time,
                "effective_at": world.time,
                field: policy.recorded_at,
            }
        )
        bundle = world.store.export_bundle().model_copy(update={"records": [assessment]})
        world.store.import_bundle(bundle)
        return assessment

    monkeypatch.setattr(world, "assess", imported_assessment)
    case = evaluated_task(world, "late-import", "2")
    before = world.store.export_bundle()
    with pytest.raises(ContractError, match="rubric was not registered"):
        demand.compute_validation(world.store, policy.record_id, [case], "late-import-receipt")
    assert world.store.export_bundle() == before


def test_same_local_capture_time_retains_sequence_order(world, monkeypatch):
    from changecost.models import ValidationPolicy
    from tests.test_demand import COMP

    world.peer("seed", ["2"])
    policy = ValidationPolicy(
        **demand.common(world.store.export_bundle().source.store_id, NOW, "earlier-rubric"),
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
    world.store.import_bundle(world.store.export_bundle().model_copy(update={"records": [policy]}))
    original_tick = world.tick
    ticks = 0

    def skip_first_tick():
        nonlocal ticks
        if ticks:
            original_tick()
        ticks += 1

    monkeypatch.setattr(world, "tick", skip_first_tick)
    case = evaluated_task(world, "same-capture", "2")
    receipt = demand.compute_validation(
        world.store, policy.record_id, [case], "same-capture-receipt"
    )
    assert receipt.passed
    with world.store.connect(readonly=True) as connection:
        records = demand.read_records(connection)
        forecast = records[(case.forecast.kind, case.forecast.record_id)]
        availability = demand.local_availability(connection)
        policy_arrival = availability[(policy.kind, policy.record_id)]
        assessment_arrival = availability[(forecast.assessment.kind, forecast.assessment.record_id)]
        assert policy_arrival[0] == assessment_arrival[0]
        assert policy_arrival[1] < assessment_arrival[1]
