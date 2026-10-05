"""Transactional local history and graph validation for portable contracts."""

from __future__ import annotations

import json
import os
import sqlite3
import tempfile
from collections import Counter, defaultdict
from collections.abc import Callable
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import TypeAdapter, ValidationError

from changecost.models import (
    MAX_SEQUENCE,
    Bundle,
    Change,
    ComputedSettlement,
    Cutoff,
    EconomicEvidence,
    Evidence,
    EvidenceBinding,
    Interval,
    Observation,
    Outcome,
    PortableRecord,
    Quote,
    RecordRef,
    Run,
    RunBinding,
    RunRef,
    Settlement,
    SourceCoverage,
    timestamp,
)
from changecost.serialization import ContractError

ADAPTER = TypeAdapter(PortableRecord)


def reference(record: PortableRecord) -> RecordRef:
    return RecordRef(kind=record.kind, record_id=record.record_id)


def key(ref: RecordRef) -> tuple[str, str]:
    return ref.kind, ref.record_id


def run_key(ref: RunRef) -> tuple[str, str, str, str]:
    return ref.repository_id, ref.provider, ref.surface, ref.run_id


def identity(record: PortableRecord) -> str:
    parts: Any = record.record_id
    if isinstance(record, Change):
        parts = [record.repository_id, record.change_id]
    elif isinstance(record, Run):
        parts = run_key(record.ref)
    elif isinstance(record, Evidence):
        parts = [
            record.provider,
            record.surface,
            record.profile,
            record.identity_scope,
            record.source_key,
            record.file_digest,
            record.ordinal,
        ]
    elif isinstance(record, RunBinding):
        parts = run_key(record.run)
    elif isinstance(record, EvidenceBinding):
        parts = key(record.evidence)
    return json.dumps([record.kind, parts], separators=(",", ":"))


def lookup(records: dict, ref: RecordRef, kind: str | None = None) -> PortableRecord:
    if kind is not None and ref.kind != kind:
        raise ContractError("wrong reference kind")
    if key(ref) not in records:
        raise ContractError("unknown record reference")
    return records[key(ref)]


def subject(record: PortableRecord) -> Any:
    if isinstance(record, Outcome):
        return key(record.subject)
    if isinstance(record, Interval):
        return run_key(record.run)
    if isinstance(record, (Settlement, ComputedSettlement)):
        return (
            (key(record.change), record.ledger_id)
            if isinstance(record, ComputedSettlement)
            else key(record.change)
        )
    return None


def revision_errors(record: PortableRecord, records: dict) -> None:
    if (
        not isinstance(record, (Outcome, Interval, Settlement, ComputedSettlement))
        or record.previous is None
    ):
        return
    prior = lookup(records, record.previous, record.kind)
    if subject(prior) != subject(record):
        raise ContractError("revision subject mismatch")
    if record.recorded_at < prior.recorded_at:
        raise ContractError("revision predates predecessor declaration")
    if isinstance(record, Outcome) and not record.reason:
        raise ContractError("outcome correction requires a reason")
    if isinstance(record, Interval) and isinstance(prior, Interval):
        changed = any(
            old is not None and old != new
            for old, new in ((prior.start, record.start), (prior.end, record.end))
        )
        if changed and not record.reason:
            raise ContractError("interval correction requires a reason")


def dependencies(
    record: PortableRecord, records: dict, runs: dict, bindings: dict, run_bindings: dict
) -> list[RecordRef]:
    from changecost.economic_graph import computed_refs, economic_refs, source_refs

    if isinstance(record, EconomicEvidence):
        return economic_refs(record, records, bindings)
    if isinstance(record, SourceCoverage):
        return source_refs(record, records, runs, bindings)
    if isinstance(record, ComputedSettlement):
        return computed_refs(record, records, runs, run_bindings)
    return core_dependencies(record, records, runs)


def core_dependencies(record: PortableRecord, records: dict, runs: dict) -> list[RecordRef]:
    refs: list[RecordRef] = []
    if isinstance(record, (RunBinding, EvidenceBinding, Interval)):
        if run_key(record.run) not in runs:
            raise ContractError("unknown complete RunRef")
        refs.append(reference(runs[run_key(record.run)]))
        refs.extend(record.source_refs)
    if isinstance(record, (RunBinding, Quote, Settlement)):
        lookup(records, record.change, "change")
        refs.append(record.change)
    if isinstance(record, EvidenceBinding):
        lookup(records, record.evidence, "evidence")
        refs.append(record.evidence)
    if isinstance(record, Outcome):
        refs.append(record.subject)
    if isinstance(record, (Quote, Settlement)):
        refs.extend(record.inputs)
    if (
        isinstance(record, (Outcome, Interval, Settlement, ComputedSettlement))
        and record.previous is not None
    ):
        refs.append(record.previous)
    if isinstance(record, Settlement):
        refs.extend(coverage_refs(record, records, runs))
    return refs


def coverage_refs(record: Settlement, records: dict, runs: dict) -> list[RecordRef]:
    refs = []
    for entry in record.coverage:
        run = runs.get(run_key(entry.run))
        outcome = lookup(records, entry.outcome, "outcome")
        interval = lookup(records, entry.interval, "interval")
        if run is None or not isinstance(outcome, Outcome) or not isinstance(interval, Interval):
            raise ContractError("invalid coverage reference")
        if outcome.subject != reference(run) or interval.run != entry.run:
            raise ContractError("coverage subject mismatch")
        for evidence in entry.evidence:
            lookup(records, evidence, "evidence")
        refs.extend([reference(run), entry.outcome, entry.interval, *entry.evidence])
        refs.extend(coverage_bindings(entry, record.change, records))
    return refs


def coverage_bindings(entry, change: RecordRef, records: dict) -> list[RecordRef]:
    binding = next(
        (r for r in records.values() if isinstance(r, RunBinding) and r.run == entry.run), None
    )
    if binding is None or binding.change != change:
        raise ContractError("coverage Run is not bound to the settlement Change")
    refs = [reference(binding)]
    mappings = {key(r.evidence): r for r in records.values() if isinstance(r, EvidenceBinding)}
    for evidence in entry.evidence:
        mapping = mappings.get(key(evidence))
        if mapping is None or mapping.run != entry.run:
            raise ContractError("coverage evidence is not bound to the covered Run")
        refs.append(reference(mapping))
    return refs


def validate_subject(record: PortableRecord, records: dict) -> None:
    if isinstance(record, RunBinding):
        change = lookup(records, record.change, "change")
        if not isinstance(change, Change) or change.repository_id != record.run.repository_id:
            raise ContractError("cross-repository binding")
    if isinstance(record, Outcome):
        lookup(records, record.subject)
        outcomes = {
            "change": {"accepted", "abandoned"},
            "run": {"succeeded", "failed", "cancelled"},
        }
        if record.outcome not in outcomes.get(record.subject.kind, set()):
            raise ContractError("outcome does not match subject")
    revision_errors(record, records)


def graph_indexes(records: dict) -> tuple[dict, dict, dict]:
    runs, evidence_bindings, run_bindings = {}, {}, {}
    for record in records.values():
        if isinstance(record, Run):
            runs[run_key(record.ref)] = record
        elif isinstance(record, EvidenceBinding):
            evidence_bindings[key(record.evidence)] = record
        elif isinstance(record, RunBinding):
            run_bindings[run_key(record.run)] = record
    return runs, evidence_bindings, run_bindings


def validate_graph(records: dict) -> dict:
    runs, bindings, run_bindings = graph_indexes(records)
    domains: dict[str, tuple] = {}
    children: set[tuple] = set()
    graph = {}
    for ref_key, record in records.items():
        domain = identity(record)
        if domain in domains and domains[domain] != ref_key:
            raise ContractError("conflicting stable identity or binding")
        domains[domain] = ref_key
        validate_subject(record, records)
        if isinstance(record, (Outcome, Interval, Settlement, ComputedSettlement)):
            parent = key(record.previous) if record.previous else None
            chain_key = (record.kind, subject(record), parent)
            if chain_key in children:
                raise ContractError("revision history forks")
            children.add(chain_key)
        graph[ref_key] = {
            key(ref) for ref in dependencies(record, records, runs, bindings, run_bindings)
        }
        for ref in graph[ref_key]:
            if ref not in records:
                raise ContractError("unknown record reference")
    from changecost.economic_graph import validate_economics

    validate_economics(records)
    reject_cycles(graph)
    return graph


def reject_cycles(graph: dict) -> None:
    pending = {ref: len(deps) for ref, deps in graph.items()}
    dependents: dict[Any, list] = defaultdict(list)
    for ref, deps in graph.items():
        for dep in deps:
            dependents[dep].append(ref)
    ready = [ref for ref, count in pending.items() if count == 0]
    visited = 0
    while ready:
        ref = ready.pop()
        visited += 1
        for child in dependents[ref]:
            pending[child] -= 1
            if pending[child] == 0:
                ready.append(child)
    if visited != len(graph):
        raise ContractError("cyclic record references")


def read_records(connection: sqlite3.Connection) -> dict:
    return {
        (kind, ident): ADAPTER.validate_json(payload)
        for kind, ident, payload in connection.execute(
            "SELECT kind,id,payload FROM records ORDER BY kind,id"
        )
    }


def unique_computation_receipts(connection):
    rows = list(connection.execute("SELECT operation_id,request,record_id FROM computations"))
    counts = Counter(record_id for _, _, record_id in rows)
    return [row for row in rows if counts[row[2]] == 1]


def computation_refs(connection, records) -> set:
    """Resolve receipts by typed payload and its exact validated request."""
    from changecost.quotes import request_for

    result = set()
    for operation_id, request, record_id in unique_computation_receipts(connection):
        settlement = records.get(("computed_settlement", record_id))
        if isinstance(settlement, ComputedSettlement):
            change = lookup(records, settlement.change, "change")
            if not isinstance(change, Change):
                raise ContractError("expected Change")
            expected = settlement.scope.model_dump_json() + ":" + change.change_id
            if request == expected and operation_id == settlement.operation_id:
                result.add(("computed_settlement", record_id))
        quote = records.get(("quote", record_id))
        if isinstance(quote, Quote) and quote.estimation is not None:
            change = lookup(records, quote.change, "change")
            expected = request_for(
                change, quote.p50.model_dump(exclude={"amount"}), quote.estimation.minimum
            )
            if request == expected:
                result.add(("quote", record_id))
    return result


def record_availability(connection, record, store_id, *, maximum_sequence=None):
    """Validate selected stored availability before any computation trust decision."""
    row = connection.execute(
        "SELECT available_at,sequence FROM records WHERE kind=? AND id=?",
        key(reference(record)),
    ).fetchone()
    if row is None:
        return None
    observation = Observation(
        reference=reference(record),
        store_id=store_id,
        available_at=row[0],
        sequence=row[1],
    )
    if maximum_sequence is not None and (
        type(maximum_sequence) is not int
        or maximum_sequence < 0
        or observation.sequence > maximum_sequence
    ):
        raise ContractError("selected availability exceeds committed sequence")
    return observation


def original_computation_cutoff(connection, record) -> bool:
    """Supported producers insert one result immediately after its captured cutoff."""
    availability = record_availability(connection, record, record.cutoff.store_id)
    if availability is None:
        return False
    return (
        record.cutoff.sequence == availability.sequence - 1
        and record.cutoff.at == availability.available_at
        and record.origin_store_id == record.cutoff.store_id
        and record.recorded_at == record.cutoff.at
        and record.effective_at == record.cutoff.at
    )


def initialize(connection: sqlite3.Connection) -> None:
    for statement in (
        "CREATE TABLE computations(operation_id TEXT PRIMARY KEY, "
        "request TEXT NOT NULL, record_id TEXT NOT NULL)",
        "CREATE TABLE metadata(store_id TEXT NOT NULL, sequence INTEGER NOT NULL, last_at TEXT)",
        "CREATE TABLE records(kind TEXT NOT NULL,id TEXT NOT NULL,identity TEXT NOT NULL UNIQUE,"
        "payload TEXT NOT NULL,available_at TEXT NOT NULL,sequence INTEGER NOT NULL,"
        "PRIMARY KEY(kind,id))",
        "CREATE TABLE observations(kind TEXT NOT NULL,id TEXT NOT NULL,store_id TEXT NOT NULL,"
        "available_at TEXT NOT NULL,sequence INTEGER NOT NULL,PRIMARY KEY(kind,id,store_id),"
        "FOREIGN KEY(kind,id) REFERENCES records(kind,id))",
    ):
        connection.execute(statement)
    connection.execute("INSERT INTO metadata VALUES (?,0,NULL)", (str(uuid4()),))
    connection.execute("PRAGMA user_version=2")


class Store:
    def __init__(self, path: Path, clock: Callable[[], datetime] | None = None, timeout: float = 5):
        self.path = Path(path)
        self.clock = clock or (lambda: datetime.now(UTC))
        self.timeout = timeout

    def connect(self, readonly: bool = False) -> sqlite3.Connection:
        if not self.path.is_file():
            raise ContractError("store does not exist")
        mode = "ro" if readonly else "rw"
        connection = sqlite3.connect(
            self.path.resolve().as_uri() + "?mode=" + mode,
            uri=True,
            isolation_level=None,
            timeout=self.timeout,
        )
        connection.execute("PRAGMA foreign_keys=ON")
        if connection.execute("PRAGMA user_version").fetchone()[0] != 2:
            connection.close()
            raise ContractError("unsupported store schema")
        return connection

    @contextmanager
    def transaction(self):
        fresh = not self.path.exists()
        connection = sqlite3.connect(":memory:", isolation_level=None) if fresh else self.connect()
        try:
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("BEGIN IMMEDIATE")
            if fresh:
                initialize(connection)
            yield connection
            self.commit(connection)
            if fresh:
                self.publish(connection, self.path)
        except (sqlite3.Error, OSError, ValueError) as exc:
            connection.rollback()
            if isinstance(exc, ContractError):
                raise
            message = (
                "store busy; retry the request"
                if isinstance(exc, sqlite3.OperationalError) and "locked" in str(exc)
                else "store operation failed"
            )
            raise ContractError(message) from exc
        finally:
            connection.close()

    def commit(self, connection: sqlite3.Connection) -> None:
        connection.execute("COMMIT")

    def publish(self, connection: sqlite3.Connection, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=".changecost-", dir=path.parent)
        os.close(fd)
        try:
            target = sqlite3.connect(temporary)
            try:
                connection.backup(target)
            finally:
                target.close()
            os.link(temporary, path)
        finally:
            Path(temporary).unlink(missing_ok=True)

    def apply(self, operation: Callable) -> Any:
        with self.transaction() as connection:
            records = read_records(connection)
            store_id, sequence, last_at = connection.execute("SELECT * FROM metadata").fetchone()
            now = timestamp(self.clock())
            additions, result = operation(dict(records), store_id, now)
            additions = [ADAPTER.validate_python(r.model_dump(warnings=False)) for r in additions]
            merged = dict(records)
            for record in additions:
                ref = key(reference(record))
                if ref in merged and merged[ref] != record:
                    raise ContractError("conflicting record identity")
                merged[ref] = record
            validate_graph(merged)
            new = [record for ref, record in merged.items() if ref not in records]
            if new:
                self.insert(connection, new, sequence + 1, now, last_at)
            return result

    def insert(self, connection, records, sequence: int, now: datetime, last_at: str | None):
        if sequence > MAX_SEQUENCE:
            raise ContractError("local transaction sequence exhausted")
        if last_at is not None and now < timestamp(last_at):
            raise ContractError("clock moved backwards")
        for record in records:
            connection.execute(
                "INSERT INTO records VALUES (?,?,?,?,?,?)",
                (
                    record.kind,
                    record.record_id,
                    identity(record),
                    record.model_dump_json(by_alias=True),
                    now.isoformat(),
                    sequence,
                ),
            )
        connection.execute("UPDATE metadata SET sequence=?,last_at=?", (sequence, now.isoformat()))

    def import_bundle(self, bundle: Bundle) -> None:
        # Revalidate even model_copy inputs; model_copy intentionally bypasses Pydantic validation.
        try:
            bundle = Bundle.model_validate(bundle.model_dump(warnings=False))
        except ValidationError as exc:
            raise ContractError("invalid portable record fields or values") from exc
        with self.transaction() as connection:
            self.import_into(connection, bundle)

    def import_into(self, connection, bundle: Bundle):
        records = read_records(connection)
        local_ids = computation_refs(connection, records)
        merged = merge_portable_records(records, bundle, local_ids)
        validate_graph(merged)
        store_id, sequence, last_at = connection.execute("SELECT * FROM metadata").fetchone()
        now = timestamp(self.clock())
        new = [record for ref, record in merged.items() if ref not in records]
        if new:
            self.insert(connection, new, sequence + 1, now, last_at)
        for observation in bundle.observations:
            lookup(merged, observation.reference)
            if observation.store_id != store_id:
                self.import_observation(connection, observation)

    def import_observation(self, connection, observation: Observation):
        ref = observation.reference
        values = (
            ref.kind,
            ref.record_id,
            observation.store_id,
            observation.available_at.isoformat(),
            observation.sequence,
        )
        existing = connection.execute(
            "SELECT * FROM observations WHERE kind=? AND id=? AND store_id=?", values[:3]
        ).fetchone()
        if existing is not None and existing != values:
            raise ContractError("conflicting origin availability")
        connection.execute("INSERT OR IGNORE INTO observations VALUES (?,?,?,?,?)", values)

    def export_bundle(self) -> Bundle:
        connection = self.connect(readonly=True)
        try:
            connection.execute("BEGIN")
            store_id, sequence, last_at = connection.execute("SELECT * FROM metadata").fetchone()
            now = timestamp(self.clock())
            if last_at and now < timestamp(last_at):
                raise ContractError("clock moved backwards")
            rows = connection.execute(
                "SELECT kind,id,?,available_at,sequence FROM records "
                "UNION ALL SELECT * FROM observations",
                (store_id,),
            ).fetchall()
            observations = [
                Observation(
                    reference=RecordRef(kind=kind, record_id=ident),
                    store_id=origin,
                    available_at=timestamp(at),
                    sequence=seq,
                )
                for kind, ident, origin, at, seq in sorted(rows)
            ]
            return Bundle(
                source=Cutoff(store_id=store_id, at=now, sequence=sequence),
                records=list(read_records(connection).values()),
                observations=observations,
            )
        finally:
            connection.close()

    def records(self) -> list[PortableRecord]:
        return self.export_bundle().records

    def snapshot(self) -> Cutoff:
        return self.export_bundle().source

    def eligible(self, ref: RecordRef, cutoff: Cutoff | None) -> bool:
        bundle = self.export_bundle()
        if (
            cutoff is None
            or cutoff.store_id != bundle.source.store_id
            or cutoff.sequence > bundle.source.sequence
            or cutoff.at > bundle.source.at
        ):
            return False
        records = {key(reference(record)): record for record in bundle.records}
        graph = validate_graph(records)
        observations = {
            key(o.reference): o for o in bundle.observations if o.store_id == cutoff.store_id
        }
        pending, seen = [key(ref)], set()
        while pending:
            current = pending.pop()
            if current in seen:
                continue
            seen.add(current)
            if not available(records.get(current), observations.get(current), cutoff):
                return False
            pending.extend(graph[current])
        return True

    def backup(self, destination: Path) -> None:
        connection = self.connect(readonly=True)
        try:
            self.publish(connection, destination)
        finally:
            connection.close()


def available(record, observation, cutoff: Cutoff) -> bool:
    if record is None or observation is None:
        return False
    return (
        observation.sequence <= cutoff.sequence
        and observation.available_at <= cutoff.at
        and record.recorded_at <= cutoff.at
        and record.effective_at <= cutoff.at
    )


def merge_portable_records(records, bundle, local_ids):
    merged = dict(records)
    local_ledgers = {
        r.ledger_id
        for r in records.values()
        if isinstance(r, ComputedSettlement) and key(reference(r)) in local_ids
    }
    for record in bundle.records:
        if (
            isinstance(record, ComputedSettlement)
            and record.ledger_id in local_ledgers
            and key(reference(record)) not in records
        ):
            raise ContractError("portable import cannot extend a local computed ledger")
        ref = key(reference(record))
        if ref in merged and merged[ref] != record:
            raise ContractError("conflicting record identity")
        merged[ref] = record
    return merged
