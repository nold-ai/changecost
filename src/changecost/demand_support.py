"""Actual selected validation evidence, separate from broad frozen metadata."""

from changecost.demand_graph import demand_lookup as lookup
from changecost.demand_scenarios import eligible_comparisons
from changecost.quotes import local_availability
from changecost.reconciliation import snapshot_records


def selected_validation_support(connection, records, receipt):
    support, visited = set(), set()
    pending = [(receipt, records)]
    availability = local_availability(connection)
    while pending:
        current, visible = pending.pop()
        identity = (current.model_dump_json(), tuple(sorted(visible)))
        if identity in visited:
            continue
        visited.add(identity)
        snapshot = snapshot_records(connection, current.cutoff, visible)
        for case in current.cases:
            support.add(case.truth)
            for ref in (case.forecast, case.baseline):
                if ref is None:
                    continue
                forecast = lookup(snapshot, ref, "demand_forecast")
                frozen = snapshot_records(connection, forecast.cutoff, snapshot)
                support.update(forecast.peers)
                support.update(transfer_support(frozen, forecast, availability))
                if forecast.result.validation is not None:
                    selected = lookup(frozen, forecast.result.validation, "demand_validation")
                    pending.append((selected, frozen))
    return support


def transfer_support(records, forecast, availability):
    transfer = forecast.result.transfer
    if transfer is None:
        return set()
    support = set(transfer.donors)
    hypothesis = lookup(records, transfer.hypothesis, "transfer_hypothesis")
    pairs = eligible_comparisons(
        records,
        lookup(records, forecast.change, "change"),
        lookup(records, forecast.assessment, "task_assessment"),
        hypothesis,
        availability,
        [],
        forecast.algorithm,
    )
    for pair, _source, _destination in pairs:
        support.update((pair.source_change, pair.target_change))
    return support
