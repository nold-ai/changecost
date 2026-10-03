"""Exact empirical Quotes from one committed offline reconciliation snapshot."""

import json
from contextlib import closing
from decimal import Decimal
from uuid import uuid4

from changecost.coverage import CoverageIndex
from changecost.economic_graph import correction_graph, economic_key
from changecost.models import (
    Change,
    CohortEvaluation,
    Component,
    Cutoff,
    EconomicEvidence,
    EconomicIdentity,
    EconomicScope,
    Estimation,
    EvidenceBinding,
    Quote,
    QuoteExclusion,
    QuotePeer,
    RecordRef,
    Run,
    RunBinding,
    identifier,
    timestamp,
)
from changecost.operations import change_in, common
from changecost.reconciliation import (
    ALGORITHM as RECONCILIATION,
)
from changecost.reconciliation import (
    POLICY,
    SnapshotIndex,
    computation_details,
    snapshot_records,
)
from changecost.serialization import ContractError
from changecost.store import (
    Store,
    computation_refs,
    key,
    read_records,
    reference,
    run_key,
    validate_graph,
)

ALGORITHM = "nearest-rank/v1"
LEVELS = [
    ("profile", ("change_shape", "trajectory", "execution_profile")),
    ("shape_trajectory", ("change_shape", "trajectory")),
    ("repository", ()),
]


def request_for(change, economic, minimum):
    return json.dumps(
        ["quote/v1", change.repository_id, change.change_id, economic, minimum], sort_keys=True
    )


def local_availability(connection):
    return {
        (kind, ident): (timestamp(at), sequence)
        for kind, ident, at, sequence in connection.execute(
            "SELECT kind,id,available_at,sequence FROM records"
        )
    }


def economic_work_records(records, members, context=None):
    """Retain earlier work in every visible correction-connected attributable input."""
    if context is not None:
        return [event for member in members for event in context.work_by_run[member]]
    return scanned_economic_work(records, members)


def scanned_economic_work(records, members):
    events = {economic_key(r): r for r in records.values() if isinstance(r, EconomicEvidence)}
    mapped = {
        key(r.evidence): run_key(r.run) for r in records.values() if isinstance(r, EvidenceBinding)
    }
    included = {
        name for name, event in events.items() if mapped.get(key(event.evidence)) in members
    }
    adjacent = {}
    for child, parent in correction_graph(records).items():
        adjacent.setdefault(child, set()).add(parent)
        adjacent.setdefault(parent, set()).add(child)
    pending = list(included)
    while pending:
        for neighbor in adjacent.get(pending.pop(), ()):
            if neighbor in events and neighbor not in included:
                included.add(neighbor)
                pending.append(neighbor)
    return [events[name] for name in included]


def change_run_bindings(records, change, context=None):
    if context is not None:
        return context.change_bindings[key(reference(change))]
    return [
        r for r in records.values() if isinstance(r, RunBinding) and r.change == reference(change)
    ]


def run_features_valid(records, run, change_availability, availability, bound, context=None):
    if bound > run.recorded_at or (run.observed_start is not None and bound > run.observed_start):
        return False
    if change_availability >= availability[key(reference(run))]:
        return False
    intervals = (
        context.all_intervals[run_key(run.ref)]
        if context is not None
        else [r for r in records.values() if r.kind == "interval" and r.run == run.ref]
    )
    return not any(r.start is not None and bound > r.start for r in intervals)


def feature_valid(records, change, availability, context=None):
    ref = key(reference(change))
    if context is not None and ref in context.feature_cache:
        return context.feature_cache[ref]
    valid = feature_timing_valid(records, change, availability, context)
    if context is not None:
        context.feature_cache[ref] = valid
    return valid


def feature_timing_valid(records, change, availability, context):
    bindings = change_run_bindings(records, change, context)
    runs = (
        context.runs
        if context is not None
        else {run_key(r.ref): r for r in records.values() if isinstance(r, Run)}
    )
    change_availability = availability[key(reference(change))]
    bound = max(
        change.features.captured_at,
        change.features.recorded_at,
        change.recorded_at,
        change_availability[0],
    )
    earlier = economic_work_records(
        records, {run_key(binding.run) for binding in bindings}, context
    )
    if any(bound > event.start for event in earlier):
        return False
    return all(
        run_features_valid(
            records, runs[run_key(b.run)], change_availability, availability, bound, context
        )
        for b in bindings
    )


def lifecycle_inputs(records, members, context=None):
    if context is not None:
        return {
            key(reference(r))
            for member in members
            for r in [context.runs[member], *context.all_intervals[member]]
        }
    return {
        key(reference(r))
        for r in records.values()
        if (isinstance(r, Run) and run_key(r.ref) in members)
        or (r.kind == "interval" and run_key(r.run) in members)
    }


def economic_feature_inputs(records, members, context=None):
    economics = economic_work_records(records, members, context)
    refs = {key(reference(r)) for r in economics}
    evidence = {key(r.evidence) for r in economics}
    if context is not None:
        refs.update(key(reference(context.bindings[e])) for e in evidence if e in context.bindings)
    else:
        refs.update(
            key(reference(r))
            for r in records.values()
            if isinstance(r, EvidenceBinding) and key(r.evidence) in evidence
        )
    return refs


def feature_inputs(records, change, context=None):
    """References consulted to prove feature timing, including normalized work."""
    bindings = change_run_bindings(records, change, context)
    members = {run_key(binding.run) for binding in bindings}
    refs = {key(reference(change)), *(key(reference(r)) for r in bindings)}
    refs.update(lifecycle_inputs(records, members, context))
    refs.update(economic_feature_inputs(records, members, context))
    return refs


def input_closure(records, roots):
    graph = validate_graph(records)
    included = set(roots)
    pending = list(roots)
    while pending:
        for dependency in graph[pending.pop()]:
            if dependency not in included:
                included.add(dependency)
                pending.append(dependency)
    return included


def peer_features_valid(records, candidate, availability, context=None):
    return feature_valid(records, candidate, availability, context) and all(
        getattr(candidate.features, field) is not None
        for field in ("change_shape", "trajectory", "execution_profile")
    )


def zero_run_peer_details(records, candidate, scope, index, cache):
    """Reuse common empty-membership evidence without dropping candidate lifecycle refs."""
    outcome = index.outcomes.get(key(reference(candidate)))
    terminal = outcome is not None
    if terminal not in cache:
        details = computation_details(
            records, candidate, scope, index, hasattr(index, "shared_inputs")
        )
        cache[terminal] = details
        return details
    # Common evidence roots were retained when this lifecycle class was first evaluated.
    inputs = [reference(candidate)]
    if outcome is not None:
        inputs.append(reference(outcome))
    return {**cache[terminal], "inputs": inputs}


def peer_details(records, candidate, scope, index, cache):
    if index.change_bindings[key(reference(candidate))]:
        details = computation_details(
            records, candidate, scope, index, hasattr(index, "shared_inputs")
        )
        if details["full_change"] and hasattr(index, "shared_inputs"):
            details["inputs"] = computation_details(records, candidate, scope, index)["inputs"]
        return details
    return zero_run_peer_details(records, candidate, scope, index, cache)


def evaluate_peers(records, change, scope, availability, context=None):
    peers = []
    exclusions = []
    dependencies = feature_inputs(records, change, context)
    index, empty_cache = context if context is not None else CoverageIndex(records), {}
    candidates = sorted(
        (
            r
            for r in records.values()
            if isinstance(r, Change) and r.repository_id == scope.repository_id and r != change
        ),
        key=lambda r: key(reference(r)),
    )
    for candidate in candidates:
        details = peer_details(records, candidate, scope, index, empty_cache)
        dependencies.update(key(r) for r in details["inputs"])
        exclusions.extend(
            QuoteExclusion(reference=e.reference, reason=e.reason) for e in details["exclusions"]
        )
        dependencies.update(key(e.reference) for e in details["exclusions"])
        if not details["full_change"]:
            exclusions.extend(
                QuoteExclusion(reference=reference(candidate), reason=r)
                for r in details["unknown_reasons"]
            )
            continue
        dependencies.update(feature_inputs(records, candidate, context))
        if not peer_features_valid(records, candidate, availability, context):
            exclusions.append(
                QuoteExclusion(
                    reference=reference(candidate), reason="missing_or_late_peer_features"
                )
            )
        peers.append(
            (
                candidate,
                QuotePeer(
                    change=reference(candidate),
                    amount=details["subtotals"][0].amount,
                    inputs=details["inputs"],
                ),
            )
        )
    if context is not None and candidates:
        dependencies.update(context.shared_inputs)
    return peers, exclusions, dependencies


def matching_peers(records, change, peers, fields, valid, availability, context=None):
    if not fields:
        return [p for _, p in peers]
    if not valid:
        return []
    return [
        p
        for c, p in peers
        if feature_valid(records, c, availability, context)
        and all(getattr(c.features, f) == getattr(change.features, f) for f in fields)
    ]


def select_cohort(records, change, peers, minimum, availability, context=None):
    evaluations = []
    selected = []
    chosen = "repository"
    for level, fields in LEVELS:
        valid = not fields or (
            feature_valid(records, change, availability, context)
            and all(getattr(change.features, f) is not None for f in fields)
        )
        matches = matching_peers(records, change, peers, fields, valid, availability, context)
        reason = (
            None
            if len(matches) >= minimum
            else ("missing_or_late_target_features" if not valid else "insufficient_samples")
        )
        evaluations.append(CohortEvaluation(level=level, count=len(matches), reason=reason))
        if not selected and len(matches) >= minimum:
            selected = matches
            chosen = level
    return selected, chosen, evaluations


def estimate(records, change, scope, minimum, cutoff, availability):
    context = SnapshotIndex(records, scope)
    peers, exclusions, dependencies = evaluate_peers(records, change, scope, availability, context)
    selected, chosen, evaluations = select_cohort(
        records, change, peers, minimum, availability, context
    )
    amounts = sorted((p.amount for p in selected), key=Decimal)
    n = len(amounts)
    quantiles = [amounts[(percent * n + 99) // 100 - 1] if n else None for percent in (50, 90)]
    component = scope.economic.model_dump()
    return Quote(
        **common(cutoff.store_id, cutoff.at, str(uuid4())),
        change=reference(change),
        state="priced" if n else "unpriced",
        p50=Component(**component, amount=quantiles[0]),
        p90=Component(**component, amount=quantiles[1]),
        reason=None if n else "insufficient_complete_cohort",
        sample_count=n,
        cohort=chosen,
        algorithm_version=ALGORITHM,
        cutoff=cutoff,
        inputs=[
            RecordRef.model_validate(dict(kind=k, record_id=i))
            for k, i in sorted(input_closure(records, dependencies))
        ],
        features=change.features,
        estimation=Estimation(
            minimum=minimum,
            synthetic=bool(peers),
            cohorts=evaluations,
            peers=selected,
            exclusions=sorted(exclusions, key=lambda e: (*key(e.reference), e.reason)),
        ),
    )


def compute_quote(
    store: Store, change_id: str, scope: EconomicScope, operation_id: str, minimum: int = 20
):
    scope = EconomicScope.model_validate(scope.model_dump(warnings=False))
    identifier(change_id)
    identifier(operation_id)
    if type(minimum) is not int or minimum <= 0 or scope.start is not None:
        raise ContractError("invalid Quote parameters")
    request = json.dumps(
        ["quote/v1", scope.repository_id, change_id, scope.economic.model_dump(), minimum],
        sort_keys=True,
    )
    with store.transaction() as connection:
        records = read_records(connection)
        existing = connection.execute(
            "SELECT request,record_id FROM computations WHERE operation_id=?", (operation_id,)
        ).fetchone()
        if existing:
            if existing[0] != request or ("quote", existing[1]) not in computation_refs(
                connection, records
            ):
                raise ContractError("operation ID already used for a different request")
            return records[("quote", existing[1])]
        store_id, sequence, last_at = connection.execute("SELECT * FROM metadata").fetchone()
        now = timestamp(store.clock())
        if last_at is not None and timestamp(last_at) > now:
            raise ContractError("clock moved backwards")
        cutoff = Cutoff(store_id=store_id, sequence=sequence, at=now)
        snapshot = snapshot_records(connection, cutoff, records)
        change = change_in(snapshot, scope.repository_id, change_id)
        if change is None:
            raise ContractError("unknown Change at input cutoff")
        result = estimate(snapshot, change, scope, minimum, cutoff, local_availability(connection))
        validate_graph({**records, key(reference(result)): result})
        store.insert(connection, [result], sequence + 1, now, last_at)
        connection.execute(
            "INSERT INTO computations VALUES (?,?,?)", (operation_id, request, result.record_id)
        )
        return result


def stored_quote(records, record):
    ref = record if isinstance(record, RecordRef) else reference(record)
    stored = records.get(key(ref))
    if not isinstance(stored, Quote):
        raise ContractError("unknown Quote")
    if isinstance(record, Quote) and stored != record:
        raise ContractError("Quote does not match immutable stored record")
    return stored, ref


def replay_supported(record):
    return (
        record.estimation is not None
        and record.algorithm_version == ALGORITHM
        and record.estimation.version == "estimation/v1"
        and record.estimation.policy_version == POLICY
        and record.estimation.reconciliation_version == RECONCILIATION
    )


def quote_reproduced(connection, records, record):
    snapshot = snapshot_records(connection, record.cutoff, records)
    if not all(key(r) in snapshot for r in [record.change, *record.inputs]):
        return False
    change = snapshot[key(record.change)]
    scope = EconomicScope(
        repository_id=change.repository_id,
        economic=EconomicIdentity(**record.p50.model_dump(exclude={"amount"})),
    )
    result = estimate(
        snapshot,
        change,
        scope,
        record.estimation.minimum,
        record.cutoff,
        local_availability(connection),
    )
    excluded = {"record_id", "recorded_at", "effective_at", "origin_store_id"}
    return result.model_dump(exclude=excluded) == record.model_dump(exclude=excluded)


def quote_explanation(record, ref, store_id, observation, local, reproduced):
    return dict(
        record=record.model_dump(mode="json", by_alias=True),
        revisions=[],
        availability=[
            dict(
                reference=ref.model_dump(),
                store_id=store_id,
                available_at=observation[0],
                sequence=observation[1],
            )
        ],
        provenance_status="producer_assertion; provider_support_not_verified",
        local_computation=local,
        replay_eligibility="inputs_available" if reproduced else "replay_unavailable",
        economic_validation="reproduced" if reproduced else "not_computed",
        replay_reason=None
        if reproduced
        else "unsupported_or_unavailable_inputs_or_result_mismatch",
    )


def inspect_quote(store: Store, record: Quote | RecordRef):
    with closing(store.connect(readonly=True)) as connection:
        connection.execute("BEGIN")
        records = read_records(connection)
        record, ref = stored_quote(records, record)
        local = key(reference(record)) in computation_refs(connection, records)
        store_id, sequence, last_at = connection.execute("SELECT * FROM metadata").fetchone()
        now = timestamp(store.clock())
        if last_at is not None and timestamp(last_at) > now:
            raise ContractError("clock moved backwards")
        eligible = (
            replay_supported(record)
            and record.cutoff.store_id == store_id
            and record.cutoff.sequence <= sequence
            and record.cutoff.at <= now
        )
        reproduced = eligible and quote_reproduced(connection, records, record)
        observation = connection.execute(
            "SELECT available_at,sequence FROM records WHERE kind=? AND id=?", key(ref)
        ).fetchone()
        return quote_explanation(record, ref, store_id, observation, local, reproduced)
