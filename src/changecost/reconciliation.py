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
    RunBinding,
    Subtotal,
    timestamp,
)
from changecost.normalized import MAX_RECORDS
from changecost.operations import change_in, common
from changecost.serialization import ContractError
from changecost.store import Store, available, key, read_records, reference, validate_graph

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


def effective_events(records: dict, scope: EconomicScope) -> Selection:
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
        result.inputs.update(key(reference(r)) for r in chain)
        mappings = [bindings[key(r.evidence)] for r in chain if key(r.evidence) in bindings]
        subjects = {tuple(m.run.model_dump().values()) for m in mappings}
        if len(subjects) > 1:
            raise ContractError("replacement changes attribution subject")
        if not resolved:
            result.exclude(chain, "pending_correction")
            continue
        record = chain[0]
        result.runs[key(reference(record))] = mappings[0].run if mappings else None
        result.inputs.update(key(reference(m)) for m in mappings)
        result.selected.append(record)
        result.exclude(chain[1:], "replaced", unresolved=False)
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


def choose_series(events: list[EconomicEvidence], result: Selection, scope: EconomicScope, records):
    files = {e.source.file_digest for e in events if e.source.identity_scope == "file"}
    if len(files) > 1 and any(
        a.source.file_digest != b.source.file_digest and overlaps(a, b)
        for a in events
        for b in events
    ):
        result.exclude(events, "dedupe_limited_overlap")
        return []
    snapshots = [e for e in events if e.lane == "snapshot"]
    if snapshots:
        from changecost.coverage import supported_event

        if len(snapshots) != 1 or any(not supported_event(e) for e in events):
            result.exclude(events, "unsupported_temporal_lane")
            return []
        snapshot = snapshots[0]
        run = result.runs[key(reference(snapshot))]
        from changecost.operations import latest

        interval = latest(records, "interval", tuple(run.model_dump().values())) if run else None
        exact = interval is not None and (interval.start, interval.end) == (
            snapshot.start,
            snapshot.end,
        )
        if scope.start is not None:
            exact = exact and (scope.start, scope.end) == (snapshot.start, snapshot.end)
        subjects = {str(result.runs[key(reference(e))]) for e in events}
        if not snapshot.baseline_zero or not exact or len(subjects) != 1:
            result.exclude(events, "unsupported_snapshot_window")
            return []
        result.exclude([e for e in events if e != snapshot], "non_authoritative_lane", False)
        return [snapshot]
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


def select(records: dict, scope: EconomicScope) -> Selection:
    result = effective_events(records, scope)
    series = defaultdict(list)
    for event in result.selected:
        series[(partition(event.source), event.series, event.component_key)].append(event)
    result.effective = list(result.selected)
    result.selected = []
    for events in series.values():
        result.selected.extend(choose_series(events, result, scope, records))
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


def snapshot_records(connection, cutoff: Cutoff) -> dict:
    records = read_records(connection)
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
    while True:
        narrowed = {k for k in included if graph[k] <= included}
        if narrowed == included:
            return {k: records[k] for k in included}
        included = narrowed


def computation_result(records, change, scope, operation_id, cutoff, store_id, now, previous):
    from changecost.coverage import assess_coverage, supported_event

    selection = select(records, scope)
    bindings = {
        tuple(r.run.model_dump().values()): r
        for r in records.values()
        if isinstance(r, RunBinding) and r.change == reference(change)
    }
    members = [bindings[k].run for k in sorted(bindings)]
    selected = [e for e in selection.selected if selection.runs[key(reference(e))] in members]
    reasons, supporting = assess_coverage(records, change, members, selection, selected, scope)
    totals = subtotals(selected, scope)
    reasons.update(selection.reasons)
    if any(t.unknown_count for t in totals):
        reasons.add("unknown_amount")
    if not selected:
        reasons.add("missing_economic_evidence")
    inputs = selection.inputs | supporting | {key(reference(change))}
    from changecost.models import RecordRef

    return ComputedSettlement(
        **common(store_id, now),
        change=reference(change),
        operation_id=operation_id,
        ledger_id=previous.ledger_id if previous else str(uuid4()),
        cutoff=cutoff,
        algorithm_version=ALGORITHM,
        policy_version=POLICY,
        scope=scope,
        subtotals=totals,
        runs=members,
        inputs=[RecordRef.model_validate(dict(kind=k, record_id=i)) for k, i in sorted(inputs)],
        exclusions=selection.exclusions,
        unknown_reasons=sorted(reasons),
        full_change=not reasons,
        synthetic=bool(selected) and all(supported_event(e) for e in selected),
        previous=reference(previous) if previous else None,
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
            if existing[0] != request:
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
        local_ids = {row[0] for row in connection.execute("SELECT record_id FROM computations")}
        local = [
            r
            for r in all_records.values()
            if isinstance(r, ComputedSettlement)
            and r.record_id in local_ids
            and r.change == reference(change)
        ]
        parents = {r.previous.record_id for r in local if r.previous is not None}
        previous = next((r for r in local if r.record_id not in parents), None)
        result = computation_result(
            records, change, scope, operation_id, cutoff, store_id, now, previous
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
        stored = read_records(connection).get(key(reference(record)))
        if stored != record:
            raise ContractError("computation does not match immutable stored record")
        local = (
            connection.execute(
                "SELECT 1 FROM computations WHERE record_id=?", (record.record_id,)
            ).fetchone()
            is not None
        )
    finally:
        connection.close()
    eligible = local and all(store.eligible(ref, record.cutoff) for ref in record.inputs)
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
    selection = select(records, scope)
    bound = [e for e in selection.selected if selection.runs[key(reference(e))] is not None]
    unbound = [e for e in selection.selected if selection.runs[key(reference(e))] is None]
    return dict(
        cutoff=cutoff.model_dump(mode="json"),
        bound=[s.model_dump() for s in subtotals(bound, scope)],
        unbound=[s.model_dump() for s in subtotals(unbound, scope)],
        unresolved=[e.model_dump() for e in selection.exclusions],
        unknown_reasons=sorted(selection.reasons),
    )


def chain_relevant(chain, resolved: bool, scope: EconomicScope) -> bool:
    if resolved:
        return relevant(chain[0], scope)
    return any(relevant(event, scope) for event in chain)
