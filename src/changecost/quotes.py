"""Exact empirical Quotes from one committed offline reconciliation snapshot."""

import json
from contextlib import closing
from decimal import Decimal
from uuid import uuid4

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


def economic_work_records(records, members):
    """Retain earlier work in every visible correction-connected attributable input."""
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


def feature_valid(records, change, availability):
    bindings = [
        r for r in records.values() if isinstance(r, RunBinding) and r.change == reference(change)
    ]
    runs = {run_key(r.ref): r for r in records.values() if isinstance(r, Run)}
    bounds = [
        change.features.captured_at,
        change.features.recorded_at,
        change.recorded_at,
        availability[key(reference(change))][0],
    ]
    earlier = economic_work_records(records, {run_key(binding.run) for binding in bindings})
    if any(max(bounds) > event.start for event in earlier):
        return False
    for binding in bindings:
        run = runs[run_key(binding.run)]
        if max(bounds) > run.recorded_at or (
            run.observed_start is not None and max(bounds) > run.observed_start
        ):
            return False
        if availability[key(reference(change))] >= availability[key(reference(run))]:
            return False
        # Declared earlier work disqualifies reconstructed features.
        intervals = [r for r in records.values() if r.kind == "interval" and r.run == run.ref]
        if any(r.start is not None and max(bounds) > r.start for r in intervals):
            return False
    return True


def feature_inputs(records, change):
    """References consulted to prove feature timing, including normalized work."""
    bindings = [
        r for r in records.values() if isinstance(r, RunBinding) and r.change == reference(change)
    ]
    members = {run_key(binding.run) for binding in bindings}
    refs = {key(reference(change)), *(key(reference(r)) for r in bindings)}
    refs.update(
        key(reference(r))
        for r in records.values()
        if (isinstance(r, Run) and run_key(r.ref) in members)
        or (r.kind == "interval" and run_key(r.run) in members)
    )
    economics = economic_work_records(records, members)
    refs.update(key(reference(r)) for r in economics)
    evidence = {key(r.evidence) for r in economics}
    refs.update(
        key(reference(r))
        for r in records.values()
        if isinstance(r, EvidenceBinding) and key(r.evidence) in evidence
    )
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


def estimate(records, change, scope, minimum, cutoff, availability):
    peers = []
    exclusions = []
    dependencies = feature_inputs(records, change)
    candidates = sorted(
        (
            r
            for r in records.values()
            if isinstance(r, Change) and r.repository_id == scope.repository_id and r != change
        ),
        key=lambda r: key(reference(r)),
    )
    for candidate in candidates:
        details = computation_details(records, candidate, scope)
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
        dependencies.update(feature_inputs(records, candidate))
        if not feature_valid(records, candidate, availability) or any(
            getattr(candidate.features, field) is None
            for field in ("change_shape", "trajectory", "execution_profile")
        ):
            exclusions.append(
                QuoteExclusion(
                    reference=reference(candidate), reason="missing_or_late_peer_features"
                )
            )
        total = details["subtotals"][0].amount
        peers.append(
            (
                candidate,
                QuotePeer(change=reference(candidate), amount=total, inputs=details["inputs"]),
            )
        )
    evaluations = []
    selected = []
    chosen = "repository"
    for level, fields in LEVELS:
        valid = not fields or (
            feature_valid(records, change, availability)
            and all(getattr(change.features, f) is not None for f in fields)
        )
        matches = [
            p
            for c, p in peers
            if not fields
            or (
                valid
                and feature_valid(records, c, availability)
                and all(getattr(c.features, f) == getattr(change.features, f) for f in fields)
            )
        ]
        reason = (
            None
            if len(matches) >= minimum
            else ("missing_or_late_target_features" if not valid else "insufficient_samples")
        )
        evaluations.append(CohortEvaluation(level=level, count=len(matches), reason=reason))
        if not selected and len(matches) >= minimum:
            selected = matches
            chosen = level
    dependencies = input_closure(records, dependencies)
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
            RecordRef.model_validate(dict(kind=k, record_id=i)) for k, i in sorted(dependencies)
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


def inspect_quote(store: Store, record: Quote | RecordRef):
    with closing(store.connect(readonly=True)) as connection:
        connection.execute("BEGIN")
        records = read_records(connection)
        ref = record if isinstance(record, RecordRef) else reference(record)
        stored = records.get(key(ref))
        if not isinstance(stored, Quote):
            raise ContractError("unknown Quote")
        if isinstance(record, Quote) and stored != record:
            raise ContractError("Quote does not match immutable stored record")
        record = stored
        local = key(reference(record)) in computation_refs(connection, records)
        store_id, sequence, last_at = connection.execute("SELECT * FROM metadata").fetchone()
        supported = (
            record.estimation is not None
            and record.algorithm_version == ALGORITHM
            and record.estimation.version == "estimation/v1"
            and record.estimation.policy_version == POLICY
            and record.estimation.reconciliation_version == RECONCILIATION
        )
        eligible = (
            supported
            and record.cutoff.store_id == store_id
            and record.cutoff.sequence <= sequence
            and record.cutoff.at <= timestamp(store.clock())
        )
        reproduced = False
        if eligible and record.estimation is not None:
            snapshot = snapshot_records(connection, record.cutoff, records)
            if all(key(r) in snapshot for r in [record.change, *record.inputs]):
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
                reproduced = result.model_dump(exclude=excluded) == record.model_dump(
                    exclude=excluded
                )
        observation = connection.execute(
            "SELECT available_at,sequence FROM records WHERE kind=? AND id=?", key(ref)
        ).fetchone()
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
