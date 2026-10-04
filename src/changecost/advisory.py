"""Ephemeral budget advice: portable claims never acquire local authority."""

from __future__ import annotations

from contextlib import closing
from decimal import Decimal
from pathlib import Path
from typing import Any

from changecost.models import (
    Change,
    Component,
    ComputedSettlement,
    Cutoff,
    Quote,
    RecordRef,
    Settlement,
    amount,
    timestamp,
)
from changecost.quotes import quote_reproduced, replay_supported
from changecost.reconciliation import ALGORITHM, POLICY, computation_details, snapshot_records
from changecost.serialization import ContractError, loads_bundle
from changecost.store import (
    computation_refs,
    key,
    lookup,
    merge_portable_records,
    read_records,
    reference,
    validate_graph,
)

MATERIAL = (
    "scope",
    "subtotals",
    "runs",
    "inputs",
    "exclusions",
    "unknown_reasons",
    "full_change",
    "synthetic",
)


def compare(value: str, budget: str) -> str:
    return "over_budget" if Decimal(value) > Decimal(budget) else "within_budget"


def budget_component(budget, economic_kind, unit, basis, currency):
    amount(budget)
    if budget is None or Decimal(budget) < 0:
        raise ContractError("invalid budget")
    return Component(
        amount=budget, economic_kind=economic_kind, unit=unit, basis=basis, currency=currency
    )


def artifact_records(path):
    bundle = loads_bundle(Path(path).read_text())
    records = merge_portable_records({}, bundle, set())
    validate_graph(records)
    observations = {}
    for observation in bundle.observations:
        lookup(records, observation.reference)
        identity = (*key(observation.reference), observation.store_id)
        if identity in observations and observations[identity] != observation:
            raise ContractError("conflicting availability")
        observations[identity] = observation
    return records


def settlement_reproduced(connection, records, record):
    snapshot = snapshot_records(connection, record.cutoff, records)
    if not all(key(ref) in snapshot for ref in [record.change, *record.inputs]):
        return False
    details = computation_details(snapshot, snapshot[key(record.change)], record.scope)
    # The evaluator returns the complete deterministic evidence projection, without new IDs.
    return all(details[name] == getattr(record, name) for name in MATERIAL)


def metadata_snapshot(connection, now):
    rows = connection.execute("SELECT store_id,sequence,last_at FROM metadata").fetchmany(2)
    if len(rows) != 1:
        raise ContractError("invalid local store metadata")
    store_id, sequence, last_at = rows[0]
    # Existing cutoff/identifier/integer/timestamp validators define this boundary.
    cutoff = Cutoff.model_validate(
        dict(store_id=store_id, sequence=sequence, at=now if last_at is None else last_at)
    )
    if cutoff.at > now:
        raise ContractError("clock moved backwards")
    return cutoff


def local_verification(connection, records, record, metadata, now):
    if isinstance(record, Settlement):
        return False, ["legacy_producer_claim"]
    if key(reference(record)) not in computation_refs(connection, records):
        return False, ["no_local_computation_receipt"]
    supported = (
        replay_supported(record)
        if isinstance(record, Quote)
        else (record.algorithm_version == ALGORITHM and record.policy_version == POLICY)
    )
    if not supported:
        return False, ["unsupported_computation_version"]
    cutoff = record.cutoff
    if (
        cutoff.store_id != metadata.store_id
        or cutoff.sequence > metadata.sequence
        or cutoff.at > now
    ):
        return False, ["foreign_or_future_cutoff"]
    reproduced = (
        quote_reproduced(connection, records, record)
        if isinstance(record, Quote)
        else settlement_reproduced(connection, records, record)
    )
    return reproduced, [] if reproduced else ["historical_inputs_unavailable_or_result_mismatch"]


def record_values(record, quantile):
    if isinstance(record, Quote):
        selected = getattr(record, quantile)
        complete = record.state == "priced"
        reasons = [] if complete else [record.reason or "unpriced"]
        return (
            [record.p50.model_dump(mode="json"), record.p90.model_dump(mode="json")],
            selected.model_dump(mode="json"),
            complete,
            reasons,
        )
    if isinstance(record, ComputedSettlement):
        declared = [
            dict(**s.economic.model_dump(), amount=s.amount, unknown_count=s.unknown_count)
            for s in record.subtotals
        ]
        values = [
            s
            for s in declared
            if {k: s[k] for k in ("economic_kind", "unit", "basis", "currency")}
            == record.scope.economic.model_dump()
        ]
        complete = (
            record.full_change
            and not record.unknown_reasons
            and len(values) == 1
            and values[0]["unknown_count"] == 0
        )
        return (
            declared,
            values[0] if len(values) == 1 else None,
            complete,
            list(record.unknown_reasons),
        )
    return (
        [c.model_dump(mode="json") for c in record.components],
        None,
        False,
        ["legacy_producer_claim"],
    )


def comparison_details(selected, budget, verified, complete):
    identity = budget.model_dump(exclude={"amount"})
    compatible = selected is not None and {k: selected[k] for k in identity} == identity
    if (
        verified
        and complete
        and compatible
        and selected is not None
        and selected["amount"] is not None
    ):
        comparison = {k: selected[k] for k in (*identity, "amount")}
        return comparison, compare(selected["amount"], budget.amount), compatible
    return None, "unknown", compatible


def record_context(record, quantile, repository_id):
    if isinstance(record, ComputedSettlement):
        scope = record.scope.model_dump(mode="json")
    elif isinstance(record, Settlement):
        scope = record.scope
    else:
        scope = dict(
            repository_id=repository_id,
            economic=record.p50.model_dump(exclude={"amount"}),
            start=None,
            end=None,
        )
    return dict(
        scope=scope,
        cutoff=None if isinstance(record, Settlement) else record.cutoff.model_dump(mode="json"),
        sample_count=record.sample_count if isinstance(record, Quote) else None,
        quantile=quantile if isinstance(record, Quote) else None,
    )


def result_for(record, budget, quantile, verification, repository_id=None) -> dict[str, Any]:
    verified, reasons = verification
    declared, selected, complete, record_reasons = record_values(record, quantile)
    reasons = list(reasons) + record_reasons
    if not complete:
        reasons.append("incomplete_or_unpriced")
    comparison, status, compatible = comparison_details(selected, budget, verified, complete)
    if not compatible:
        reasons.append("incompatible_economic_identity")
    context = record_context(record, quantile, repository_id)
    return dict(
        schema="changecost/check-v1",
        status=status,
        record=reference(record).model_dump(),
        budget=budget.model_dump(mode="json"),
        comparison=comparison,
        declared=declared,
        scope=context["scope"],
        cutoff=context["cutoff"],
        provenance="locally_reproduced_synthetic; provider_support_not_verified"
        if verified
        else "producer_assertion; provider_support_not_verified",
        completeness="complete" if verified and complete else "unknown",
        sample_count=context["sample_count"],
        quantile=context["quantile"],
        reasons=sorted(set(reasons)),
    )


def selected_record(records, ref) -> Quote | ComputedSettlement | Settlement:
    record = lookup(records, ref)
    if not isinstance(record, (Quote, ComputedSettlement, Settlement)):
        raise ContractError("invalid record selection")
    return record


def record_repository(records, record):
    change = lookup(records, record.change)
    if not isinstance(change, Change):
        raise ContractError("invalid Change reference")
    return change.repository_id


def check_record(store, ref: RecordRef, budget: Component, quantile=None, artifact=None):
    component = budget_component(
        budget.amount, budget.economic_kind, budget.unit, budget.basis, budget.currency
    )
    if ref.kind not in {"quote", "computed_settlement", "settlement"}:
        raise ContractError("invalid record kind")
    if quantile is not None and (ref.kind != "quote" or quantile not in {"p50", "p90"}):
        raise ContractError("invalid quantile")
    quantile = quantile or "p90"
    if artifact is not None:
        records = artifact_records(artifact)
        record = selected_record(records, ref)
        return result_for(
            record,
            component,
            quantile,
            (False, ["artifact_producer_claim"]),
            record_repository(records, record),
        )
    with closing(store.connect(readonly=True)) as connection:
        connection.execute("BEGIN")
        now = timestamp(store.clock())
        metadata = metadata_snapshot(connection, now)
        records = read_records(connection)
        validate_graph(records)
        record = selected_record(records, ref)
        verified, reasons = local_verification(connection, records, record, metadata, now)
        return result_for(
            record,
            component,
            quantile,
            (verified, reasons),
            record_repository(records, record),
        )
