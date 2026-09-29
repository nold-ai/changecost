"""Real SQLite scenario traces and four public-boundary sensitivity controls."""

import json
import random
from copy import deepcopy
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from changecost.models import RecordRef, RunRef
from changecost.operations import LifecycleDeclaration, declare, register_change, register_run
from changecost.serialization import ContractError
from changecost.store import Store
from tests.behavioral_model import Action, Model

NOW = datetime(2026, 9, 29, 10, tzinfo=UTC)
SEEDS = tuple(range(8))
GENERATED_STEPS = 24


def timestamp(minutes):
    return None if minutes is None else NOW + timedelta(minutes=minutes)


def run_ref(name):
    return RunRef(repository_id="synthetic", provider="cursor", surface="ide", run_id=name)


def target_ref(store, target):
    record = next(
        r
        for r in store.records()
        if (r.kind == "change" and target == "c") or (r.kind == "run" and r.ref.run_id == target)
    )
    return RecordRef(kind=record.kind, record_id=record.record_id)


def execute(store, action):
    if action.kind == "change":
        register_change(store, "synthetic", "c", change_shape=action.value or "bugfix")
    elif action.kind == "run":
        start = timestamp(action.start)
        if action.naive and start is not None:
            start = start.replace(tzinfo=None)
        register_run(store, run_ref(action.target), "c", work_start=start)
    else:
        declare(
            store,
            target_ref(store, action.target),
            LifecycleDeclaration(
                outcome=action.value,
                start=timestamp(action.start),
                end=timestamp(action.end),
                correct_outcome=action.correction,
                correct_interval=action.correction,
                reason=action.reason or None,
            ),
        )


def projection(store):
    records = store.records()
    names = {
        r.record_id: ("c" if r.kind == "change" else r.ref.run_id)
        for r in records
        if r.kind in {"change", "run"}
    }
    model = Model()
    for record in records:
        if record.kind == "change":
            model.feature = record.features.change_shape
        elif record.kind == "run":
            model.runs[record.ref.run_id] = minutes(record.observed_start)
    for kind in ("outcome", "interval"):
        for record in history_order(records, kind):
            if kind == "outcome":
                model.outcomes.setdefault(names[record.subject.record_id], []).append(
                    record.outcome
                )
            else:
                model.intervals.setdefault(record.run.run_id, []).append(
                    (minutes(record.start), minutes(record.end))
                )
    assert sum(r.kind == "run_binding" for r in records) == len(model.runs), "run binding count"
    return model


def history_order(records, kind):
    remaining = [r for r in records if r.kind == kind]
    visited = set()
    while remaining:
        ready = [r for r in remaining if r.previous is None or r.previous.record_id in visited]
        assert ready, "history predecessor chain is broken"
        for record in ready:
            yield record
            visited.add(record.record_id)
            remaining.remove(record)


def minutes(value):
    return None if value is None else int((value - NOW).total_seconds() / 60)


def apply_checked(store, model, action, operation=execute):
    before = store.export_bundle() if store.path.exists() else None
    previous_model = deepcopy(model)
    expected = model.attempt(action)
    try:
        operation(store, action)
        accepted = True
    except (ContractError, ValidationError, StopIteration):
        accepted = False
    assert accepted == expected, "acceptance matches scenario model"
    after = store.export_bundle() if store.path.exists() else None
    if not expected:
        assert after == before, "rejected operation must preserve full history"
    elif model == previous_model:
        assert after == before, "accepted no-op must preserve full history"
    if before is not None and after is not None:
        assert all(r in after.records for r in before.records), "history must be immutable"
    if after is not None:
        assert projection(store) == model, "persisted state matches scenario model"


def trace(path, actions, operation=execute):
    store = Store(path, clock=lambda: NOW)
    model = Model()
    for action in actions:
        apply_checked(store, model, action, operation)
    return store


def targeted_actions():
    return [
        Action("change"),
        Action("run", start=-60),
        Action("run", start=-60),
        Action("change", value="feature"),
        Action("declare", end=-120, value="succeeded"),
        Action("declare", end=0, value="failed"),
        Action("declare", value="succeeded"),
        Action("declare", value="succeeded", start=-90, correction=True, reason="observed"),
        Action("declare", "c", "accepted"),
        Action("run", start=-60),
        Action("run", "r1"),
        Action("declare", "c", "abandoned", correction=True, reason="reviewed"),
    ]


def test_explicit_lifecycle_trace(tmp_path):
    trace(tmp_path / "trace.sqlite", targeted_actions())


@pytest.mark.parametrize("seed", SEEDS)
def test_bounded_generated_sequences(tmp_path, seed):
    rng = random.Random(seed)
    actions = [Action("change"), Action("run")]
    for _ in range(GENERATED_STEPS):
        kind = rng.choice(["change", "run", "declare"])
        if kind == "change":
            actions.append(Action(kind, value=rng.choice(["bugfix", "feature"])))
        elif kind == "run":
            actions.append(
                Action(kind, rng.choice(["r0", "r1", "r2"]), start=rng.choice([None, -60]))
            )
        else:
            actions.append(
                Action(
                    kind,
                    rng.choice(["r0", "r1", "c"]),
                    rng.choice(["failed", "succeeded", "accepted"]),
                    start=rng.choice([None, -60, -90]),
                    end=rng.choice([None, -120, 0]),
                    correction=rng.choice([True, False]),
                    reason=rng.choice(["", "observed"]),
                )
            )
    trace(tmp_path / f"seed-{seed}.sqlite", actions)


def faulty_retry(store, action):
    existed = store.path.exists()
    execute(store, action)
    if action.kind == "change" and existed:
        with store.connect() as connection:
            row = connection.execute("SELECT payload FROM records WHERE kind='change'").fetchone()
            payload = json.loads(row[0])
            payload["features"]["change_shape"] = "feature"
            connection.execute(
                "UPDATE records SET payload=? WHERE kind='change'", (json.dumps(payload),)
            )


def faulty_atomicity(store, action):
    if action.kind == "declare" and action.value and action.end is not None:
        execute(store, replace(action, start=None, end=None))
    execute(store, action)


def faulty_representation(store, action):
    try:
        execute(store, action)
    except (ContractError, ValidationError):
        if not action.naive:
            raise
        execute(store, replace(action, naive=False))


@pytest.mark.parametrize(
    "family,actions,operation,detector",
    [
        (
            "retry",
            [Action("change"), Action("change")],
            faulty_retry,
            "accepted no-op must preserve full history",
        ),
        (
            "atomicity",
            [
                Action("change"),
                Action("run", start=-60),
                Action("declare", value="succeeded", end=-120),
            ],
            faulty_atomicity,
            "rejected operation must preserve full history",
        ),
        (
            "representation",
            [Action("change"), Action("run", start=-60, naive=True)],
            faulty_representation,
            "acceptance matches scenario model",
        ),
    ],
)
def test_fault_then_repair(tmp_path, family, actions, operation, detector):
    with pytest.raises(AssertionError, match=detector):
        trace(tmp_path / f"{family}-fault.sqlite", actions, operation)
    trace(tmp_path / f"{family}-repaired.sqlite", actions)


class SequenceBlindStore(Store):
    def eligible(self, ref, cutoff):
        # Exercise real eligibility while deliberately removing the captured sequence boundary.
        if cutoff is None:
            return super().eligible(ref, cutoff)
        return super().eligible(
            ref, cutoff.model_copy(update={"sequence": self.snapshot().sequence})
        )


def chronology_trace(store_type, path):
    store = store_type(path, clock=lambda: NOW)
    register_change(store, "synthetic", "c")
    cutoff = store.snapshot()
    run = register_run(store, run_ref("r0"), "c")
    ref = RecordRef(kind="run", record_id=run.record_id)
    assert not store.eligible(ref, cutoff), "captured sequence excludes later same-time transaction"
    assert store.eligible(ref, store.snapshot())
    return store


def test_chronology_fault_then_repair_and_later_import(tmp_path):
    with pytest.raises(AssertionError, match="captured sequence excludes"):
        chronology_trace(SequenceBlindStore, tmp_path / "fault.sqlite")
    source = chronology_trace(Store, tmp_path / "source.sqlite")
    destination = Store(tmp_path / "destination.sqlite", clock=lambda: NOW + timedelta(days=30))
    bundle = source.export_bundle()
    destination.import_bundle(bundle)
    before = destination.export_bundle()
    destination.import_bundle(bundle)
    assert destination.export_bundle() == before, "reimport preserves destination history"
    for record in bundle.records:
        ref = RecordRef(kind=record.kind, record_id=record.record_id)
        assert not destination.eligible(ref, bundle.source), (
            "origin cutoff is not destination history"
        )
        cutoff = destination.snapshot().model_copy(update={"at": NOW + timedelta(days=1)})
        assert not destination.eligible(ref, cutoff), (
            "later destination import cannot backdate availability"
        )


def faulty_retry_sequence(store, action):
    existed = store.path.exists()
    execute(store, action)
    if action.kind == "change" and existed:
        with store.connect() as connection:
            connection.execute("UPDATE metadata SET sequence=sequence+1")


def faulty_retry_availability(store, action):
    existed = store.path.exists()
    execute(store, action)
    if action.kind == "change" and existed:
        with store.connect() as connection:
            connection.execute(
                "UPDATE records SET available_at=?", ((NOW - timedelta(days=1)).isoformat(),)
            )


@pytest.mark.parametrize("operation", [faulty_retry_sequence, faulty_retry_availability])
def test_retry_metadata_fault_then_repair(tmp_path, operation):
    actions = [Action("change"), Action("change")]
    with pytest.raises(AssertionError, match="accepted no-op must preserve full history"):
        trace(tmp_path / "fault.sqlite", actions, operation)
    trace(tmp_path / "repaired.sqlite", actions)
