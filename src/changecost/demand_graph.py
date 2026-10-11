"""Typed demand dependency and correction boundaries; no financial authority."""

from typing import Any

from changecost.models import (
    Assessment,
    Change,
    DemandForecast,
    DemandObservation,
    DemandValidation,
    Ecosystem,
    MatchedComparison,
    TransferHypothesis,
    ValidationPolicy,
)
from changecost.serialization import ContractError


def demand_subject(record):
    from changecost.store import key, run_key

    if isinstance(record, DemandObservation):
        return run_key(record.run), record.component.model_dump_json()
    if isinstance(record, DemandValidation):
        return key(record.policy)
    return None


def demand_refs(record, records, runs, bindings, run_bindings):
    if isinstance(record, Assessment):
        demand_lookup(records, record.change, "change")
        return [record.change]
    if isinstance(record, Ecosystem):
        demand_lookup(records, record.measurement_policy, "demand_policy")
        return [record.measurement_policy]
    if isinstance(record, DemandObservation):
        return observation_refs(record, records, runs, bindings, run_bindings)
    if isinstance(record, (MatchedComparison, TransferHypothesis)):
        return comparison_refs(record, records)
    if isinstance(record, ValidationPolicy):
        demand_lookup(records, record.ecosystem, "ecosystem")
        return [record.ecosystem]
    if isinstance(record, DemandValidation):
        return validation_refs(record, records)
    if isinstance(record, DemandForecast):
        return forecast_refs(record, records)
    return []


def observation_refs(record, records, runs, bindings, run_bindings):
    from changecost.store import key, reference, run_key

    run = runs.get(run_key(record.run))
    assessment = demand_lookup(records, record.assessment, "task_assessment")
    demand_lookup(records, record.ecosystem, "ecosystem")
    mapping = run_bindings.get(run_key(record.run))
    if run is None or mapping is None or mapping.change != assessment.change:
        raise ContractError("demand observation requires exact Run/Change binding")
    if assessment.recorded_at >= record.start:
        raise ContractError("assessment must precede work")
    for evidence in record.evidence:
        demand_lookup(records, evidence, "evidence")
        if key(evidence) not in bindings or bindings[key(evidence)].run != record.run:
            raise ContractError("demand evidence requires exact Run binding")
    refs = [
        reference(run),
        reference(mapping),
        record.assessment,
        record.ecosystem,
        *record.evidence,
    ]
    refs.extend(reference(bindings[key(e)]) for e in record.evidence)
    return previous_refs(record, refs)


def comparison_refs(record, records):
    from changecost.store import key

    demand_lookup(records, record.source_ecosystem, "ecosystem")
    demand_lookup(records, record.target_ecosystem, "ecosystem")
    refs = [record.source_ecosystem, record.target_ecosystem]
    if isinstance(record, MatchedComparison):
        demand_lookup(records, record.source_change, "change")
        demand_lookup(records, record.target_change, "change")
        if record.source_change == record.target_change:
            raise ContractError("comparison needs distinct Changes")
        refs.extend([record.source_change, record.target_change])
    else:
        for pair in record.comparisons:
            demand_lookup(records, pair, "matched_comparison")
        if len({key(p) for p in record.comparisons}) != len(record.comparisons):
            raise ContractError("duplicate comparison")
        refs.extend(record.comparisons)
    return refs


def validation_refs(record, records):

    demand_lookup(records, record.policy, "demand_validation_policy")
    refs = [record.policy, *record.inputs]
    for case in record.cases:
        forecast = demand_lookup(records, case.forecast, "demand_forecast")
        truth = demand_lookup(records, case.truth, "change")
        if forecast.change != case.truth or not isinstance(truth, Change):
            raise ContractError("validation truth/forecast mismatch")
        refs.extend([case.forecast, case.truth])
        if case.baseline is not None:
            demand_lookup(records, case.baseline, "demand_forecast")
            refs.append(case.baseline)
    return previous_refs(record, refs)


def forecast_refs(record, records):

    assessment = demand_lookup(records, record.assessment, "task_assessment")
    demand_lookup(records, record.change, "change")
    demand_lookup(records, record.ecosystem, "ecosystem")
    if assessment.change != record.change:
        raise ContractError("forecast assessment/Change mismatch")
    refs = [record.change, record.assessment, record.ecosystem, *record.inputs, *record.peers]
    refs.extend(e.reference for e in record.exclusions)
    if record.result.transfer is not None:
        refs.append(record.result.transfer.hypothesis)
        for donor in record.result.transfer.donors:
            demand_lookup(records, donor, "change")
            refs.append(donor)
    if record.result.validation is not None:
        demand_lookup(records, record.result.validation, "demand_validation")
        refs.append(record.result.validation)
    if record.price_request is not None:
        demand_lookup(records, record.price_request, "demand_price")
        refs.append(record.price_request)
    return refs


def previous_refs(record, refs):
    if record.previous is not None:
        refs.append(record.previous)
    return refs


def demand_lookup(records, ref, kind) -> Any:
    """Resolve a graph-validated discriminator without widening store lookup's union."""
    from changecost.store import lookup

    return lookup(records, ref, kind)
