"""Bounded exact reconciliation from a single committed local snapshot."""

from collections import defaultdict
from dataclasses import dataclass, field
from decimal import Decimal
from uuid import uuid4

from changecost.economic_graph import (
    correction_graph,
    economic_identity,
    economic_key,
    partition,
)
from changecost.models import (
    ComputedSettlement,
    Cutoff,
    EconomicEvidence,
    EconomicScope,
    EvidenceBinding,
    Exclusion,
    Subtotal,
    timestamp,
)
from changecost.normalized import MAX_RECORDS
from changecost.operations import change_in, common
from changecost.serialization import ContractError
from changecost.store import (
    Store,
    available,
    computation_refs,
    key,
    read_records,
    reference,
    run_key,
    validate_graph,
)

ALGORITHM = "settlement/v1"
POLICY = "synthetic/v1"
MAX_DIGITS = 4096


def exact_sum(values) -> str | None:
    values = list(values)
    if len(values) > MAX_RECORDS:
        raise ContractError("economic record count limit exceeded")
    if not values:
        return None
    parts = [Decimal(value).as_tuple() for value in values]
    exponents = [int(p.exponent) for p in parts]
    scale = min(0, *exponents)
    largest = max(len(p.digits) + exponent for p, exponent in zip(parts, exponents, strict=True))
    if max(1, largest) - scale > MAX_DIGITS:
        raise ContractError("aligned decimal digit limit exceeded")
    total = 0
    for part, exponent in zip(parts, exponents, strict=True):
        coefficient = int("".join(map(str, part.digits)))
        total += (-1 if part.sign else 1) * coefficient * 10 ** (exponent - scale)
    digits = str(abs(total)).zfill(1 - scale)
    if len(digits) > MAX_DIGITS:
        raise ContractError("result decimal digit limit exceeded")
    if scale < 0:
        digits = digits[:scale] + "." + digits[scale:]
    return ("-" if total < 0 else "") + digits


@dataclass
class Selection:
    selected: list[EconomicEvidence] = field(default_factory=list)
    effective: list[EconomicEvidence] = field(default_factory=list)
    exclusions: list[Exclusion] = field(default_factory=list)
    reasons: set[str] = field(default_factory=set)
    runs: dict = field(default_factory=dict)
    inputs: set = field(default_factory=set)

    def exclude(self, events, reason: str, unresolved: bool = True):
        self.exclusions.extend(Exclusion(reference=reference(e), reason=reason) for e in events)
        if unresolved:
            self.reasons.add(reason)


def relevant(event: EconomicEvidence, scope: EconomicScope) -> bool:
    if event.source.repository_id != scope.repository_id:
        return False
    identity = economic_identity(event.component)
    return identity == scope.economic or (
        identity.currency is None
        and event.component.amount is None
        and identity.model_dump(exclude={"currency"})
        == scope.economic.model_dump(exclude={"currency"})
    )


def chain_members(events: dict, leaf, edges: dict) -> tuple[list, bool]:
    chain = [events[leaf]]
    while leaf in edges:
        leaf = edges[leaf]
        if leaf not in events:
            return chain, False
        chain.append(events[leaf])
    return chain, True


def effective_events(records: dict, scope: EconomicScope, members=None) -> Selection:
    events = {
        economic_key(r): r
        for r in records.values()
        if isinstance(r, EconomicEvidence) and r.source.repository_id == scope.repository_id
    }
    if len(events) > MAX_RECORDS:
        raise ContractError("economic record count limit exceeded")
    edges = correction_graph(records)
    predecessors = set(edges.values())
    bindings = {key(r.evidence): r for r in records.values() if isinstance(r, EvidenceBinding)}
    result = Selection()
    for leaf in events.keys() - predecessors:
        chain, resolved = chain_members(events, leaf, edges)
        if not chain_relevant(chain, resolved, scope):
            continue
        select_chain(result, chain, resolved, bindings, members)
    return result


def in_window(event: EconomicEvidence, scope: EconomicScope) -> bool:
    if scope.start is None or scope.end is None:
        return True
    if event.start == event.end:
        return scope.start <= event.start < scope.end
    return event.start >= scope.start and event.end <= scope.end


def overlaps(left, right) -> bool:
    # Point endpoints are conservatively ambiguous for file deduplication.
    return left.start <= right.end and right.start <= left.end


def choose_series(events: list[EconomicEvidence], result: Selection, scope: EconomicScope, index):
    if ambiguous_file_overlap(events):
        result.exclude(events, "dedupe_limited_overlap")
        return []
    snapshots = [e for e in events if e.lane == "snapshot"]
    if snapshots:
        return select_snapshot(events, result, scope, index)
    return select_deltas(events, result, scope)


def ambiguous_file_overlap(events) -> bool:
    files = {e.source.file_digest for e in events if e.source.identity_scope == "file"}
    if len(files) <= 1:
        return False
    # Keep the furthest endpoints for two distinct digests (including namespaced None).
    furthest = []
    for event in sorted(events, key=lambda e: e.start):
        digest = event.source.file_digest
        other = next((prior for prior in furthest if prior.source.file_digest != digest), None)
        if other is not None and overlaps(other, event):
            return True
        same = next((prior for prior in furthest if prior.source.file_digest == digest), None)
        if same is None or event.end > same.end:
            furthest = [prior for prior in furthest if prior.source.file_digest != digest]
            furthest.append(event)
            furthest = sorted(furthest, key=lambda e: e.end, reverse=True)[:2]
    return False


def select_snapshot(events, result, scope, index):
    snapshots = [e for e in events if e.lane == "snapshot"]
    from changecost.coverage import supported_event

    if len(snapshots) != 1 or any(not supported_event(e) for e in events):
        result.exclude(events, "unsupported_temporal_lane")
        return []
    snapshot = snapshots[0]
    run = result.runs[key(reference(snapshot))]
    exact = exact_snapshot_window(snapshot, run, scope, index)
    subjects = {str(result.runs[key(reference(e))]) for e in events}
    if not snapshot.baseline_zero or not exact or len(subjects) != 1:
        result.exclude(events, "unsupported_snapshot_window")
        return []
    result.exclude([e for e in events if e != snapshot], "non_authoritative_lane", False)
    return [snapshot]


def select_deltas(events, result, scope):
    included = []
    for event in events:
        if in_window(event, scope):
            included.append(event)
        elif (
            scope.start is not None
            and scope.end is not None
            and (event.start < scope.end and event.end > scope.start)
        ):
            result.exclude([event], "partial_source_window")
        else:
            result.exclude([event], "outside_scope", False)
    return included


def select(records: dict, scope: EconomicScope, members=None, index=None) -> Selection:
    from changecost.coverage import CoverageIndex

    index = index if index is not None else CoverageIndex(records)
    result = effective_events(records, scope, members)
    series = defaultdict(list)
    for event in result.selected:
        series[(partition(event.source), event.series, event.component_key)].append(event)
    result.effective = list(result.selected)
    result.selected = []
    for events in series.values():
        result.selected.extend(choose_series(events, result, scope, index))
    return result


def subtotals(events, scope: EconomicScope) -> list[Subtotal]:
    groups = defaultdict(list)
    groups[scope.economic.model_dump_json()] = []
    for event in events:
        groups[economic_identity(event.component).model_dump_json()].append(event.component.amount)
    from changecost.models import EconomicIdentity

    return [
        Subtotal(
            economic=EconomicIdentity.model_validate_json(identity),
            amount=exact_sum(v for v in values if v is not None),
            unknown_count=values.count(None),
        )
        for identity, values in sorted(groups.items())
    ]


def snapshot_records(connection, cutoff: Cutoff, records=None) -> dict:
    records = read_records(connection) if records is None else records
    from changecost.models import Observation, RecordRef

    observations = {
        (kind, ident): Observation(
            reference=RecordRef(kind=kind, record_id=ident),
            store_id=cutoff.store_id,
            available_at=at,
            sequence=sequence,
        )
        for kind, ident, at, sequence in connection.execute(
            "SELECT kind,id,available_at,sequence FROM records"
        )
    }
    graph = validate_graph(records)
    included = {k for k, r in records.items() if available(r, observations.get(k), cutoff)}
    dependents = defaultdict(list)
    for ref, dependencies in graph.items():
        for dependency in dependencies:
            dependents[dependency].append(ref)
    pending = list(records.keys() - included)
    while pending:
        for child in dependents[pending.pop()]:
            if child in included:
                included.remove(child)
                pending.append(child)
    return {k: records[k] for k in included}


def computation_details(records, change, scope, index=None) -> dict:
    from changecost.coverage import CoverageIndex, assess_coverage, supported_event

    index = index if index is not None else CoverageIndex(records)
    bindings = {run_key(r.run): r for r in index.change_bindings[key(reference(change))]}
    members = [bindings[k].run for k in sorted(bindings)]
    selection = select(records, scope, set(bindings), index)
    selected = [
        e
        for e in selection.selected
        if selection.runs[key(reference(e))] is not None
        and run_key(selection.runs[key(reference(e))]) in bindings
    ]
    reasons, supporting = assess_coverage(index, change, members, selection, selected, scope)
    totals = subtotals(selected, scope)
    reasons.update(selection.reasons)
    if any(t.unknown_count for t in totals):
        reasons.add("unknown_amount")
    if not selected:
        reasons.add("missing_economic_evidence")
    inputs = selection.inputs | supporting | {key(reference(change))}
    from changecost.models import RecordRef

    return dict(
        scope=scope,
        subtotals=totals,
        runs=members,
        inputs=[RecordRef.model_validate(dict(kind=k, record_id=i)) for k, i in sorted(inputs)],
        exclusions=selection.exclusions,
        unknown_reasons=sorted(reasons),
        full_change=not reasons,
        synthetic=bool(selected) and all(supported_event(e) for e in selected),
    )


def compute_settlement(store: Store, change_id: str, scope: EconomicScope, operation_id: str):
    from changecost.models import identifier

    scope = EconomicScope.model_validate(scope.model_dump(warnings=False))
    identifier(operation_id)
    identifier(change_id)
    request = scope.model_dump_json() + ":" + change_id
    with store.transaction() as connection:
        existing = connection.execute(
            "SELECT request,record_id FROM computations WHERE operation_id=?", (operation_id,)
        ).fetchone()
        all_records = read_records(connection)
        if existing:
            if existing[0] != request or (
                "computed_settlement",
                existing[1],
            ) not in computation_refs(connection, all_records):
                raise ContractError("operation ID already used for a different request")
            return all_records[("computed_settlement", existing[1])]
        store_id, sequence, last_at = connection.execute("SELECT * FROM metadata").fetchone()
        now = timestamp(store.clock())
        if last_at is not None and timestamp(last_at) > now:
            raise ContractError("clock moved backwards")
        cutoff = Cutoff(store_id=store_id, at=now, sequence=sequence)
        records = snapshot_records(connection, cutoff)
        change = change_in(records, scope.repository_id, change_id)
        if change is None:
            raise ContractError("unknown Change at input cutoff")
        local_ids = computation_refs(connection, all_records)
        local = [
            r
            for r in all_records.values()
            if isinstance(r, ComputedSettlement)
            and key(reference(r)) in local_ids
            and r.change == reference(change)
        ]
        parents = {r.previous.record_id for r in local if r.previous is not None}
        previous = next((r for r in local if r.record_id not in parents), None)
        result = make_computation(
            computation_details(records, change, scope), change, operation_id, cutoff, previous
        )
        validate_graph({**all_records, key(reference(result)): result})
        store.insert(connection, [result], sequence + 1, now, last_at)
        connection.execute(
            "INSERT INTO computations VALUES (?,?,?)", (operation_id, request, result.record_id)
        )
        return result


def inspect_computation(store: Store, record: ComputedSettlement) -> dict:
    connection = store.connect(readonly=True)
    try:
        connection.execute("BEGIN")
        records = read_records(connection)
        stored = records.get(key(reference(record)))
        if stored != record:
            raise ContractError("computation does not match immutable stored record")
        local = key(reference(record)) in computation_refs(connection, records)
        store_id, sequence, last_at = connection.execute("SELECT * FROM metadata").fetchone()
        now = timestamp(store.clock())
        if last_at is not None and timestamp(last_at) > now:
            raise ContractError("clock moved backwards")
        cutoff = record.cutoff
        eligible = False
        if (
            local
            and cutoff.store_id == store_id
            and cutoff.sequence <= sequence
            and cutoff.at <= now
        ):
            snapshot = snapshot_records(connection, cutoff, records)
            eligible = all(key(ref) in snapshot for ref in record.inputs)
    finally:
        connection.close()
    return dict(
        local_computation=local,
        replay_eligibility="inputs_available" if eligible else "replay_unavailable",
        current_eligibility="snapshot_only",
    )


def repository_report(store: Store, scope: EconomicScope) -> dict:
    scope = EconomicScope.model_validate(scope.model_dump(warnings=False))
    connection = store.connect(readonly=True)
    try:
        connection.execute("BEGIN")
        store_id, sequence, last_at = connection.execute("SELECT * FROM metadata").fetchone()
        now = timestamp(store.clock())
        if last_at is not None and timestamp(last_at) > now:
            raise ContractError("clock moved backwards")
        cutoff = Cutoff(store_id=store_id, at=now, sequence=sequence)
        records = snapshot_records(connection, cutoff)
    finally:
        connection.close()
    from changecost.coverage import CoverageIndex, unpriced_evidence

    index = CoverageIndex(records)
    selection = select(records, scope, index=index)
    bound = [e for e in selection.selected if selection.runs[key(reference(e))] is not None]
    unbound = [e for e in selection.selected if selection.runs[key(reference(e))] is None]
    bound_totals, unbound_totals = subtotals(bound, scope), subtotals(unbound, scope)
    if any(s.unknown_count for s in [*bound_totals, *unbound_totals]):
        selection.reasons.add("unknown_amount")
    missing = unpriced_evidence(index, repository_id=scope.repository_id)
    if missing:
        selection.exclude([records[ref] for ref in sorted(missing)], "missing_economic_evidence")
    return dict(
        cutoff=cutoff.model_dump(mode="json"),
        bound=[s.model_dump() for s in bound_totals],
        unbound=[s.model_dump() for s in unbound_totals],
        unresolved=[e.model_dump() for e in selection.exclusions],
        unknown_reasons=sorted(selection.reasons),
    )


def chain_relevant(chain, resolved: bool, scope: EconomicScope) -> bool:
    if resolved:
        return relevant(chain[0], scope)
    return any(relevant(event, scope) for event in chain)


def select_chain(result, chain, resolved, bindings, members):
    mappings = [bindings[key(r.evidence)] for r in chain if key(r.evidence) in bindings]
    subjects = {tuple(m.run.model_dump().values()) for m in mappings}
    if len(subjects) > 1:
        raise ContractError("replacement changes attribution subject")
    if members is not None and subjects and subjects.isdisjoint(members):
        return
    result.inputs.update(key(reference(r)) for r in chain)
    result.inputs.update(key(reference(m)) for m in mappings)
    if not resolved:
        result.exclude(chain, "pending_correction")
        return
    record = chain[0]
    result.runs[key(reference(record))] = mappings[0].run if mappings else None
    result.selected.append(record)
    result.exclude(chain[1:], "replaced", unresolved=False)


def exact_snapshot_window(snapshot, run, scope, index):
    if run is None:
        return False
    interval = index.intervals.get(run_key(run))
    if interval is None:
        return False
    exact = (interval.start, interval.end) == (
        snapshot.start,
        snapshot.end,
    )
    if scope.start is not None:
        exact = exact and (scope.start, scope.end) == (snapshot.start, snapshot.end)
    return exact


def make_computation(details, change, operation_id, cutoff, previous):
    return ComputedSettlement(
        **common(cutoff.store_id, cutoff.at),
        change=reference(change),
        operation_id=operation_id,
        ledger_id=previous.ledger_id if previous else str(uuid4()),
        cutoff=cutoff,
        algorithm_version=ALGORITHM,
        policy_version=POLICY,
        previous=reference(previous) if previous else None,
        **details,
    )
