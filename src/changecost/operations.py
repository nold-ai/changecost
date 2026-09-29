"""Explicit lifecycle operations. No attribution inference or cost computation."""

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from changecost.models import (
    Change,
    EvidenceBinding,
    Features,
    Interval,
    Outcome,
    RecordRef,
    Run,
    RunBinding,
    RunRef,
)
from changecost.serialization import ContractError
from changecost.store import Store, key, lookup, reference, subject


def stable_id(kind: str, *values: str) -> str:
    return hashlib.sha256(json.dumps([kind, *values], ensure_ascii=True).encode()).hexdigest()


def common(store_id: str, now: datetime, record_id: str | None = None) -> dict:
    return dict(
        record_id=record_id or str(uuid4()),
        origin_store_id=store_id,
        recorded_at=now,
        effective_at=now,
    )


def change_in(records: dict, repository_id: str, change_id: str) -> Change | None:
    return next(
        (
            r
            for r in records.values()
            if isinstance(r, Change)
            and (r.repository_id, r.change_id) == (repository_id, change_id)
        ),
        None,
    )


def run_in(records: dict, ref: RunRef) -> Run:
    run = next((r for r in records.values() if isinstance(r, Run) and r.ref == ref), None)
    if run is None:
        raise ContractError("unknown complete RunRef")
    return run


def latest(records: dict, kind: str, target):
    revisions = [r for r in records.values() if r.kind == kind and subject(r) == target]
    predecessors = {key(r.previous) for r in revisions if r.previous is not None}
    return next((r for r in revisions if key(reference(r)) not in predecessors), None)


def register_change(store: Store, repository_id: str, change_id: str, **features) -> Change:
    def operation(records, store_id, now):
        existing = change_in(records, repository_id, change_id)
        at = existing.recorded_at if existing else now
        snapshot = Features(captured_at=at, recorded_at=at, **features)
        if existing:
            if existing.features != snapshot:
                raise ContractError("conflicting immutable features")
            return [], existing
        change = Change(
            **common(store_id, now, stable_id("change", repository_id, change_id)),
            repository_id=repository_id,
            change_id=change_id,
            features=snapshot,
        )
        return [change], change

    return store.apply(operation)


def registration_binding(records, run: Run, change: Change, store_id, now):
    for record in records.values():
        if isinstance(record, RunBinding) and record.run == run.ref:
            if record.change != reference(change):
                raise ContractError("conflicting run assignment")
            return record
    return RunBinding(
        **common(store_id, now, stable_id("run_binding", run.record_id)),
        run=run.ref,
        change=reference(change),
    )


def register_run(
    store: Store, ref: RunRef, change_id: str, work_start: datetime | None = None
) -> Run:
    # Revalidate model_copy callers as well as ordinary validated CLI input.
    ref = RunRef.model_validate(ref.model_dump(warnings=False))

    def operation(records, store_id, now):
        change = change_in(records, ref.repository_id, change_id)
        if change is None:
            raise ContractError("unknown Change")
        existing = next((r for r in records.values() if isinstance(r, Run) and r.ref == ref), None)
        if existing is not None:
            if existing.observed_start != work_start:
                raise ContractError("conflicting registration start")
            binding = registration_binding(records, existing, change, store_id, now)
            if key(reference(binding)) not in records:
                raise ContractError("registration cannot bind an existing unbound Run")
            return [], existing
        if latest(records, "outcome", key(reference(change))) is not None:
            raise ContractError("new Run requires an open Change")
        run = Run(
            **common(store_id, now, stable_id("run", *ref.model_dump().values())),
            ref=ref,
            observed_start=work_start,
        )
        binding = registration_binding(records, run, change, store_id, now)
        additions = [run, binding]
        if work_start is not None:
            additions.append(Interval(**common(store_id, now), run=ref, start=work_start))
        return additions, run

    return store.apply(operation)


def bind_run(store: Store, ref: RunRef, change_ref: RecordRef):
    def operation(records, store_id, now):
        run = run_in(records, ref)
        change = lookup(records, change_ref, "change")
        if not isinstance(change, Change):
            raise ContractError("expected Change")
        binding = registration_binding(records, run, change, store_id, now)
        return [binding], binding

    return store.apply(operation)


def bind_evidence(store: Store, evidence_id: str, ref: RunRef):
    def operation(records, store_id, now):
        run_in(records, ref)
        evidence = RecordRef(kind="evidence", record_id=evidence_id)
        lookup(records, evidence, "evidence")
        for record in records.values():
            if isinstance(record, EvidenceBinding) and record.evidence == evidence:
                if record.run != ref:
                    raise ContractError("conflicting evidence assignment")
                return [], record
        binding = EvidenceBinding(
            **common(store_id, now, stable_id("evidence_binding", evidence_id)),
            run=ref,
            evidence=evidence,
        )
        return [binding], binding

    return store.apply(operation)


@dataclass(frozen=True, kw_only=True)
class LifecycleDeclaration:
    """One atomic request to declare or explicitly correct lifecycle facts."""

    outcome: str | None = None
    start: datetime | None = None
    end: datetime | None = None
    correct_outcome: bool = False
    correct_interval: bool = False
    reason: str | None = None


def require_correction(correct: bool, reason: str | None, kind: str) -> None:
    if not correct or not reason or not reason.strip():
        raise ContractError(f"{kind} correction requires flag and reason")


def outcome_update(records, target, declaration: LifecycleDeclaration, store_id, now):
    if declaration.outcome is None:
        return []
    prior = latest(records, "outcome", key(target))
    if prior is not None and prior.outcome == declaration.outcome:
        return []
    if prior is not None:
        require_correction(declaration.correct_outcome, declaration.reason, "outcome")
    return [
        Outcome.model_validate(
            {
                **common(store_id, now),
                "subject": target,
                "outcome": declaration.outcome,
                "previous": reference(prior) if prior else None,
                "reason": declaration.reason if prior else None,
            }
        )
    ]


def interval_bounds(prior: Interval | None, declaration: LifecycleDeclaration):
    previous = (prior.start, prior.end) if prior else (None, None)
    return (
        declaration.start if declaration.start is not None else previous[0],
        declaration.end if declaration.end is not None else previous[1],
    )


def changes_known_bound(prior: Interval | None, bounds) -> bool:
    if prior is None:
        return False
    return any(
        old is not None and old != new
        for old, new in zip((prior.start, prior.end), bounds, strict=True)
    )


def interval_update(records, target, declaration: LifecycleDeclaration, store_id, now):
    if declaration.start is None and declaration.end is None:
        return []
    run = lookup(records, target, "run")
    if not isinstance(run, Run):
        raise ContractError("interval requires a Run")
    prior = latest(records, "interval", tuple(run.ref.model_dump().values()))
    bounds = interval_bounds(prior, declaration)
    if prior is not None and bounds == (prior.start, prior.end):
        return []
    changed = changes_known_bound(prior, bounds)
    if changed:
        require_correction(declaration.correct_interval, declaration.reason, "interval")
    return [
        Interval(
            **common(store_id, now),
            run=run.ref,
            start=bounds[0],
            end=bounds[1],
            previous=reference(prior) if prior else None,
            reason=declaration.reason if changed else None,
        )
    ]


def declare(store: Store, target: RecordRef, declaration: LifecycleDeclaration):
    if declaration.outcome is None and declaration.start is None and declaration.end is None:
        raise ContractError("settlement computation is not implemented; specify lifecycle fields")

    def operation(records, store_id, now):
        lookup(records, target)
        outcomes = outcome_update(records, target, declaration, store_id, now)
        intervals = interval_update(records, target, declaration, store_id, now)
        return [*outcomes, *intervals], [reference(r) for r in [*outcomes, *intervals]]

    return store.apply(operation)
