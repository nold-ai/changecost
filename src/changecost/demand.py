"""Offline demand computation, scoped synthetic validation and immutable replay."""

import json
from contextlib import closing
from fractions import Fraction
from uuid import uuid4

from changecost.demand_graph import demand_lookup as lookup
from changecost.demand_history import (
    aggregate,
    ecosystem_identity,
    frozen_assessment,
    initial_forecast,
    peers,
    summaries,
)
from changecost.demand_scenarios import estimate_price, transfer_candidate
from changecost.models import (
    Cutoff,
    DemandForecast,
    DemandResult,
    DemandValidation,
    Exclusion,
    ValidationCase,
    ValidationMetrics,
    ValidationPolicy,
    identifier,
    timestamp,
)
from changecost.operations import change_in, common
from changecost.quotes import input_closure, local_availability
from changecost.reconciliation import snapshot_records
from changecost.serialization import ContractError
from changecost.store import (
    Store,
    key,
    metadata_row,
    original_computation_cutoff,
    read_records,
    reference,
    unique_computation_receipts,
    validate_graph,
)


def forecast_request(change, assessment, ecosystem, price=None, broad=False):
    return json.dumps(
        [
            "demand/v1",
            change.repository_id,
            change.change_id,
            assessment.record_id,
            ecosystem.record_id,
            price.record_id if price else None,
            broad,
        ],
        sort_keys=True,
    )


def validation_request(policy, cases):
    return json.dumps(
        ["demand-validation/v1", policy.record_id, [c.model_dump() for c in cases]], sort_keys=True
    )


def demand_computation_refs(connection, records):
    """Typed exact-request resolution; an untyped ID or portable label is insufficient."""
    result = set()
    for operation, request, ident in unique_computation_receipts(connection):
        forecast = records.get(("demand_forecast", ident))
        if isinstance(forecast, DemandForecast):
            change = lookup(records, forecast.change, "change")
            assessment = lookup(records, forecast.assessment, "task_assessment")
            ecosystem = lookup(records, forecast.ecosystem, "ecosystem")
            price = (
                lookup(records, forecast.price_request, "demand_price")
                if forecast.price_request
                else None
            )
            expected = forecast_request(
                change, assessment, ecosystem, price, forecast.broad_baseline
            )
            if operation == forecast.operation_id and request == expected:
                result.add(("demand_forecast", ident))
        validation = records.get(("demand_validation", ident))
        if isinstance(validation, DemandValidation):
            policy = lookup(records, validation.policy, "demand_validation_policy")
            if operation == validation.operation_id and request == validation_request(
                policy, validation.cases
            ):
                result.add(("demand_validation", ident))
    return result


def captured(connection, store):
    store_id, sequence, last_at = metadata_row(connection)
    now = timestamp(store.clock())
    if last_at is not None and timestamp(last_at) > now:
        raise ContractError("clock moved backwards")
    return Cutoff(store_id=store_id, sequence=sequence, at=now), last_at


def existing_result(connection, records, operation, request, kind):
    row = connection.execute(
        "SELECT request,record_id FROM computations WHERE operation_id=?", (operation,)
    ).fetchone()
    if row is None:
        return None
    if row[0] != request or (kind, row[1]) not in demand_computation_refs(connection, records):
        raise ContractError("operation ID already used for a different request")
    return records[(kind, row[1])]


def persist_result(store, connection, records, result, request, last_at):
    validate_graph({**records, key(reference(result)): result})
    store.insert(connection, [result], result.cutoff.sequence + 1, result.cutoff.at, last_at)
    connection.execute(
        "INSERT INTO computations VALUES (?,?,?)", (result.operation_id, request, result.record_id)
    )
    return result


def compute_demand(
    store: Store,
    repository_id,
    change_id,
    operation_id,
    assessment_id,
    ecosystem_id,
    price_id=None,
    broad_baseline=False,
):
    for value in (repository_id, change_id, operation_id, assessment_id, ecosystem_id):
        identifier(value)
    if type(broad_baseline) is not bool:
        raise ContractError("invalid baseline selector")
    with store.transaction() as connection:
        records = read_records(connection)
        change = change_in(records, repository_id, change_id)
        if change is None:
            raise ContractError("unknown Change")
        assessment = records.get(("task_assessment", assessment_id))
        ecosystem = records.get(("ecosystem", ecosystem_id))
        if assessment is None or ecosystem is None:
            raise ContractError("unknown assessment or ecosystem")
        price = records.get(("demand_price", price_id)) if price_id else None
        if price_id and price is None:
            raise ContractError("unknown price scenario")
        request = forecast_request(change, assessment, ecosystem, price, broad_baseline)
        existing = existing_result(connection, records, operation_id, request, "demand_forecast")
        if existing is not None:
            return existing
        cutoff, last_at = captured(connection, store)
        snapshot = snapshot_records(connection, cutoff, records)
        refs = [reference(change), reference(assessment), reference(ecosystem)]
        if price is not None:
            refs.append(reference(price))
        if any(key(r) not in snapshot for r in refs):
            raise ContractError("demand input unavailable at cutoff")
        result = estimate(
            snapshot,
            change,
            assessment,
            ecosystem,
            operation_id,
            cutoff,
            local_availability(connection),
            price,
            broad_baseline,
            applicable_validation(connection, snapshot, change, ecosystem),
        )
        return persist_result(store, connection, records, result, request, last_at)


def estimate(
    records,
    change,
    assessment,
    ecosystem,
    operation,
    cutoff,
    availability,
    price=None,
    broad=False,
    validation=None,
):
    if assessment.change != reference(change) or not frozen_assessment(
        records, assessment, availability
    ):
        raise ContractError("assessment is not a frozen pre-work snapshot")
    policy = lookup(records, ecosystem.measurement_policy, "demand_policy")
    component = policy.component
    selected, cohort, excluded = peers(
        records, change, assessment, ecosystem, component, availability, broad
    )
    if ecosystem_identity(records, ecosystem) is None:
        selected = []
        excluded.append((reference(ecosystem), "unknown_ecosystem"))
    transfer, transfer_exclusions = transfer_candidate(
        records, change, assessment, ecosystem, component, availability
    )
    excluded.extend(transfer_exclusions)
    state = "learning" if selected else ("transfer_hypothesis" if transfer else "zero_knowledge")
    if validation is not None and selected:
        state = "validated_forecast"
    result = DemandResult(
        component=component,
        state=state,
        sample_count=len(selected),
        cohort=cohort,
        **summaries([v for _, v, _ in selected]),
        transfer=transfer,
        validation=reference(validation)
        if validation is not None and state == "validated_forecast"
        else None,
    )
    roots = set(records) - {k for k in records if k[0] in {"demand_forecast", "demand_validation"}}
    if validation is not None:
        roots.add(key(reference(validation)))
    inputs = input_closure(records, roots)
    return DemandForecast(
        **common(cutoff.store_id, cutoff.at, str(uuid4())),
        change=reference(change),
        assessment=reference(assessment),
        ecosystem=reference(ecosystem),
        operation_id=operation,
        cutoff=cutoff,
        result=result,
        inputs=[reference(records[k]) for k in sorted(inputs)],
        exclusions=[
            Exclusion(reference=r, reason=reason)
            for r, reason in sorted(excluded, key=lambda e: (key(e[0]), e[1]))
        ],
        peers=[reference(c) for c, _, _ in selected],
        next_evidence=["complete_compatible_bound_outcomes", "registered_measured_validation"]
        if state != "validated_forecast"
        else [],
        price=estimate_price(price, result) if price else None,
        price_request=reference(price) if price else None,
        broad_baseline=broad,
        initial=initial_forecast(records, change, cutoff),
        assumptions=[
            "synthetic_fixture_only",
            "observed_summaries_are_uncalibrated",
            "repeat_task_dependence",
        ]
        if len({a.scope_key for _, _, a in selected}) < len(selected)
        else ["synthetic_fixture_only", "observed_summaries_are_uncalibrated"],
    )


def demand_reproduced(connection, records, forecast):
    if not original_computation_cutoff(connection, forecast):
        return False
    snapshot = snapshot_records(connection, forecast.cutoff, records)
    if any(key(r) not in snapshot for r in forecast.inputs):
        return False
    change = lookup(snapshot, forecast.change, "change")
    assessment = lookup(snapshot, forecast.assessment, "task_assessment")
    ecosystem = lookup(snapshot, forecast.ecosystem, "ecosystem")
    price = (
        lookup(snapshot, forecast.price_request, "demand_price") if forecast.price_request else None
    )
    validation = applicable_validation(connection, snapshot, change, ecosystem)
    replay = estimate(
        snapshot,
        change,
        assessment,
        ecosystem,
        forecast.operation_id,
        forecast.cutoff,
        local_availability(connection),
        price,
        forecast.broad_baseline,
        validation,
    )
    exclude = {"record_id", "origin_store_id", "recorded_at", "effective_at"}
    return replay.model_dump(exclude=exclude) == forecast.model_dump(exclude=exclude)


def inspect_demand(store, record):
    with closing(store.connect(readonly=True)) as connection:
        connection.execute("BEGIN")
        records = read_records(connection)
        ref = (
            record
            if hasattr(record, "kind") and not isinstance(record, DemandForecast)
            else reference(record)
        )
        stored = lookup(records, ref, "demand_forecast")
        if isinstance(record, DemandForecast) and record != stored:
            raise ContractError("forecast does not match stored record")
        current, _ = captured(connection, store)
        local = key(ref) in demand_computation_refs(connection, records)
        eligible = (
            stored.cutoff.store_id == current.store_id
            and stored.cutoff.sequence <= current.sequence
            and stored.cutoff.at <= current.at
        )
        reproduced = local and eligible and demand_reproduced(connection, records, stored)
        return dict(
            record=stored.model_dump(mode="json", by_alias=True),
            local_computation=local,
            replay_eligibility="inputs_available" if reproduced else "replay_unavailable",
            demand_validation="reproduced" if reproduced else "producer_claim",
            provenance_status="synthetic_offline; native_accuracy_not_established",
        )


def applicable_validation(connection, records, change, ecosystem):
    # Resolve the newest locally available overlapping rubric first. A new rubric
    # without a passing receipt conservatively withdraws current validation.
    identity = ecosystem_identity(records, ecosystem)
    if identity is None:
        return None
    component = lookup(records, ecosystem.measurement_policy, "demand_policy").component
    policies = [
        p
        for p in records.values()
        if isinstance(p, ValidationPolicy)
        and p.component == component
        and ecosystem_identity(records, lookup(records, p.ecosystem, "ecosystem")) == identity
    ]
    if not policies:
        return None
    availability = local_availability(connection)
    newest = max(availability[key(reference(p))] for p in policies)
    active = [p for p in policies if availability[key(reference(p))] == newest]
    if len(active) != 1:
        return None
    policy = active[0]
    local = demand_computation_refs(connection, records)
    receipts = [
        r
        for r in records.values()
        if isinstance(r, DemandValidation)
        and r.policy == reference(policy)
        and key(reference(r)) in local
    ]
    parents = {key(r.previous) for r in receipts if r.previous is not None}
    heads = [r for r in receipts if key(reference(r)) not in parents]
    if len(heads) != 1:
        return None
    receipt = heads[0]
    if any(case.truth == reference(change) for case in receipt.cases):
        return None
    if receipt.passed and validation_reproduced(connection, records, receipt):
        return receipt
    return None


def compute_validation(store, policy_id, cases, operation_id):
    """Compute a measured synthetic rubric receipt; #17 owns actual pilot registration."""
    identifier(operation_id)
    cases = [ValidationCase.model_validate(c.model_dump()) for c in cases]
    with store.transaction() as connection:
        records = read_records(connection)
        policy = records.get(("demand_validation_policy", policy_id))
        if not isinstance(policy, ValidationPolicy):
            raise ContractError("unknown validation policy")
        request = validation_request(policy, cases)
        existing = existing_result(connection, records, operation_id, request, "demand_validation")
        if existing is not None:
            return existing
        cutoff, last_at = captured(connection, store)
        snapshot = snapshot_records(connection, cutoff, records)
        if key(reference(policy)) not in snapshot:
            raise ContractError("validation policy unavailable")
        metrics, passed = measure_validation(connection, snapshot, policy, cases)
        current = [
            r
            for r in snapshot.values()
            if isinstance(r, DemandValidation)
            and r.policy == reference(policy)
            and key(reference(r)) in demand_computation_refs(connection, snapshot)
        ]
        parents = {key(r.previous) for r in current if r.previous}
        heads = [r for r in current if key(reference(r)) not in parents]
        if len(heads) > 1:
            raise ContractError("ambiguous validation history")
        receipt = DemandValidation(
            **common(cutoff.store_id, cutoff.at, str(uuid4())),
            policy=reference(policy),
            cases=cases,
            metrics=metrics,
            passed=passed,
            operation_id=operation_id,
            cutoff=cutoff,
            inputs=[reference(r) for r in snapshot.values()],
            previous=reference(heads[0]) if heads else None,
        )
        return persist_result(store, connection, records, receipt, request, last_at)


def validation_reproduced(connection, records, receipt):
    if not original_computation_cutoff(connection, receipt):
        return False
    snapshot = snapshot_records(connection, receipt.cutoff, records)
    if any(key(r) not in snapshot for r in receipt.inputs):
        return False
    try:
        metrics, passed = measure_validation(
            connection,
            snapshot,
            lookup(snapshot, receipt.policy, "demand_validation_policy"),
            receipt.cases,
        )
    except (ValueError, KeyError):
        return False
    return metrics == receipt.metrics and passed == receipt.passed


def measured_case(connection, records, policy, case, availability):
    forecast = lookup(records, case.forecast, "demand_forecast")
    truth = lookup(records, case.truth, "change")
    eco = lookup(records, policy.ecosystem, "ecosystem")
    if key(case.forecast) not in demand_computation_refs(
        connection, records
    ) or not demand_reproduced(connection, records, forecast):
        raise ContractError("validation needs reproduced local forecast")
    if (
        forecast.change != case.truth
        or forecast.result.sample_count == 0
        or forecast.result.component != policy.component
        or not forecast.initial
    ):
        raise ContractError("incompatible forecast/truth")
    if ecosystem_identity(
        records, lookup(records, forecast.ecosystem, "ecosystem")
    ) != ecosystem_identity(records, eco):
        raise ContractError("incompatible validation ecosystem")
    assessment = lookup(records, forecast.assessment, "task_assessment")
    if availability[key(reference(policy))] >= availability[key(reference(assessment))]:
        raise ContractError("rubric was not registered before evaluated task")
    actual, _assessment, reason = aggregate(records, truth, eco, policy.component, availability)
    if reason or actual is None:
        raise ContractError("complete validation truth unavailable")
    if not frozen_assessment(records, assessment, availability):
        raise ContractError("late validation predictors")
    return forecast, actual, assessment


def baseline_error(connection, records, policy, case, forecast, actual):
    if case.baseline is None:
        if policy.require_baseline:
            raise ContractError("registered rubric requires baseline")
        return None
    baseline = lookup(records, case.baseline, "demand_forecast")
    if (
        not baseline.broad_baseline
        or baseline.change != case.truth
        or baseline.assessment != forecast.assessment
        or baseline.ecosystem != forecast.ecosystem
        or not baseline.initial
        or baseline.inputs != forecast.inputs
    ):
        raise ContractError("baseline uses different frozen evidence")
    if (
        key(case.baseline) not in demand_computation_refs(connection, records)
        or not demand_reproduced(connection, records, baseline)
        or baseline.result.median is None
    ):
        raise ContractError("baseline unavailable")
    return abs(actual - Fraction(baseline.result.median))


def measure_validation(connection, records, policy, cases):
    availability = local_availability(connection)
    seen = set()
    errors, baselines, underestimates, widths, overheads = [], [], [], [], []
    covered = 0
    for case in cases:
        if key(case.truth) in seen:
            raise ContractError("duplicate validation truth")
        seen.add(key(case.truth))
        forecast, actual, assessment = measured_case(
            connection, records, policy, case, availability
        )
        predicted = Fraction(forecast.result.median)
        errors.append(abs(actual - predicted))
        underestimate = max(Fraction(0), actual - predicted)
        underestimates.append(underestimate)
        widths.append(Fraction(forecast.result.maximum) - Fraction(forecast.result.minimum))
        covered += Fraction(forecast.result.minimum) <= actual <= Fraction(forecast.result.maximum)
        if (
            assessment.rehearsal is not None
            and assessment.rehearsal.overhead.component != policy.component
        ):
            raise ContractError("rubric overhead units incompatible")
        overheads.append(
            Fraction(assessment.rehearsal.overhead.amount) if assessment.rehearsal else Fraction(0)
        )
        baseline = baseline_error(connection, records, policy, case, forecast, actual)
        if baseline is not None:
            baselines.append(baseline)
    count = len(cases)
    metrics = ValidationMetrics(
        count=count,
        covered=covered,
        maximum_underestimate=str(max(underestimates, default=Fraction(0))),
        maximum_width=str(max(widths, default=Fraction(0))),
        maximum_overhead=str(max(overheads, default=Fraction(0))),
        mean_error=str(sum(errors) / count if count else Fraction(0)),
        baseline_error=str(sum(baselines) / count)
        if baselines and len(baselines) == count
        else None,
    )
    coverage = Fraction(covered, count) if count else Fraction(0)
    passed = count >= policy.minimum_truth and abs(
        coverage - Fraction(policy.nominal_coverage)
    ) <= Fraction(policy.coverage_tolerance)
    passed = (
        passed
        and Fraction(metrics.maximum_underestimate) <= Fraction(policy.maximum_underestimate)
        and Fraction(metrics.maximum_width) <= Fraction(policy.maximum_width)
        and Fraction(metrics.maximum_overhead) <= Fraction(policy.maximum_overhead)
    )
    if policy.require_baseline:
        passed = (
            passed
            and metrics.baseline_error is not None
            and Fraction(metrics.mean_error) <= Fraction(metrics.baseline_error)
        )
    return metrics, bool(passed)
