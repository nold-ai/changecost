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


def record_key(record):
    return record.kind, record.record_id


def assert_observations(bundle, new_records, clock):
    identities = [
        (o.reference.kind, o.reference.record_id, o.store_id) for o in bundle.observations
    ]
    assert len(identities) == len(set(identities)), "observation identities must be unique"
    local = [o for o in bundle.observations if o.store_id == bundle.source.store_id]
    assert {record_key(o.reference) for o in local} == {record_key(r) for r in bundle.records}, (
        "local observations must cover stored records"
    )
    new_keys = {record_key(r) for r in new_records}
    for observation in local:
        if record_key(observation.reference) in new_keys:
            assert observation.available_at == clock, "new availability uses operation clock"
            assert observation.sequence == bundle.source.sequence, (
                "new availability uses source boundary"
            )


def assert_append(before, after):
    assert after.source.at == NOW, "source uses operation clock"
    previous_sequence = 0 if before is None else before.source.sequence
    assert after.source.sequence > previous_sequence, "append advances committed boundary"
    old_records = [] if before is None else before.records
    if before is not None:
        assert after.schema_version == before.schema_version, "schema must remain stable"
        assert after.source.store_id == before.source.store_id, "source identity must remain stable"
        assert all(r in after.records for r in before.records), "history must be immutable"
        assert all(o in after.observations for o in before.observations), (
            "observations must be immutable"
        )
    new_records = [r for r in after.records if r not in old_records]
    assert new_records, "accepted append adds records"
    assert_observations(after, new_records, NOW)


def assert_fresh_import(origin, destination, clock):
    assert destination.schema_version == origin.schema_version, "import preserves schema"
    assert destination.records == origin.records, "import preserves records"
    assert all(o in destination.observations for o in origin.observations), (
        "import preserves foreign observations"
    )
    assert destination.source.store_id != origin.source.store_id, (
        "destination has distinct identity"
    )
    assert destination.source.at == clock, "destination uses import clock"
    assert destination.source.sequence > 0, "destination has committed boundary"
    assert_observations(destination, destination.records, clock)


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
    else:
        assert after is not None, "accepted append must persist store"
        assert_append(before, after)
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
    assert_fresh_import(bundle, before, NOW + timedelta(days=30))
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


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param(
            "UPDATE records SET available_at='2026-09-28T10:00:00+00:00' WHERE kind='change'",
            id="old-time",
        ),
        pytest.param("UPDATE records SET sequence=99 WHERE kind='change'", id="old-sequence"),
        pytest.param("UPDATE metadata SET store_id='replaced-store'", id="source-identity"),
        pytest.param("UPDATE metadata SET sequence=sequence+1", id="source-boundary"),
        pytest.param(
            "UPDATE records SET available_at='2026-09-28T10:00:00+00:00' WHERE kind!='change'",
            id="new-time",
        ),
        pytest.param("UPDATE records SET sequence=1 WHERE kind!='change'", id="new-boundary"),
    ],
)
def test_append_history_fault_then_repair(tmp_path, sql):
    def faulty(store, action):
        execute(store, action)
        if action.kind == "run":
            with store.connect() as connection:
                connection.execute(sql)

    actions = [Action("change"), Action("run")]
    with pytest.raises(AssertionError):
        trace(tmp_path / "fault.sqlite", actions, faulty)
    trace(tmp_path / "repaired.sqlite", actions)


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param(
            "UPDATE observations SET available_at='2026-09-28T10:00:00+00:00'", id="foreign-history"
        ),
        pytest.param(
            "UPDATE records SET available_at='2026-09-28T10:00:00+00:00'", id="destination-clock"
        ),
    ],
)
def test_import_history_fault_then_repair(tmp_path, sql):
    origin = trace(tmp_path / "source.sqlite", [Action("change"), Action("run")]).export_bundle()
    clock = NOW + timedelta(days=30)
    for name, fault in [("fault", True), ("repaired", False)]:
        destination = Store(tmp_path / f"{name}.sqlite", clock=lambda: clock)
        destination.import_bundle(origin)
        if fault:
            with destination.connect() as connection:
                connection.execute(sql)
            with pytest.raises(AssertionError):
                assert_fresh_import(origin, destination.export_bundle(), clock)
        else:
            assert_fresh_import(origin, destination.export_bundle(), clock)


def test_rejected_fresh_store_remains_absent(tmp_path):
    store = trace(tmp_path / "absent.sqlite", [Action("run")])
    assert not store.path.exists()


@pytest.mark.parametrize("actions", [[Action("change")], [Action("change"), Action("run")]])
def test_successful_append_cannot_remove_store(tmp_path, actions):
    def faulty(store, action):
        execute(store, action)
        if action == actions[-1]:
            store.path.unlink()

    with pytest.raises(AssertionError, match="accepted append must persist store"):
        trace(tmp_path / "fault.sqlite", actions, faulty)
    trace(tmp_path / "repaired.sqlite", actions)
