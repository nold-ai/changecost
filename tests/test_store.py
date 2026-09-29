"""Core lifecycle, transactional failure and historical replay acceptance."""

from datetime import UTC, datetime, timedelta

import pytest

from changecost.models import RecordRef, RunRef
from changecost.operations import (
    LifecycleDeclaration,
    bind_evidence,
    bind_run,
    declare,
    register_change,
    register_run,
)
from changecost.serialization import ContractError, dumps_bundle, loads_bundle
from changecost.store import Store, reference

NOW = datetime(2026, 9, 29, 10, tzinfo=UTC)
RUN = RunRef(repository_id="repo", provider="cursor", surface="ide", run_id="r")


@pytest.fixture
def store(tmp_path):
    return Store(tmp_path / "data.sqlite", clock=lambda: NOW, timeout=0)


def initialized(store):
    c = register_change(store, "repo", "c", change_shape=" BugFix ")
    r = register_run(store, RUN, "c")
    return c, r


def test_registration_replay_and_terminal_retry(store):
    c, r = initialized(store)
    before = store.export_bundle()
    assert register_change(store, "repo", "c", change_shape="bugfix") == c
    assert register_run(store, RUN, "c") == r
    assert store.export_bundle() == before
    declare(store, reference(r), LifecycleDeclaration(outcome="failed"))
    declare(store, reference(c), LifecycleDeclaration(outcome="accepted"))
    assert register_run(store, RUN, "c") == r
    with pytest.raises(ContractError):
        register_run(store, RUN.model_copy(update={"run_id": "new"}), "c")
    with pytest.raises(ContractError):
        register_change(store, "repo", "c", change_shape="feature")


def test_revision_corrections_are_atomic(store):
    c, r = initialized(store)
    declare(store, reference(r), LifecycleDeclaration(start=NOW - timedelta(hours=1)))
    before = store.export_bundle()
    with pytest.raises(ContractError):
        declare(
            store,
            reference(r),
            LifecycleDeclaration(end=NOW - timedelta(hours=2), outcome="succeeded"),
        )
    assert store.export_bundle() == before
    declare(store, reference(r), LifecycleDeclaration(end=NOW, outcome="succeeded"))
    declare(store, reference(c), LifecycleDeclaration(outcome="accepted"))
    before = store.export_bundle()
    with pytest.raises(ContractError):
        declare(store, reference(c), LifecycleDeclaration(outcome="abandoned"))
    assert store.export_bundle() == before
    declare(
        store,
        reference(c),
        LifecycleDeclaration(outcome="abandoned", correct_outcome=True, reason="correction"),
    )
    declare(
        store,
        reference(r),
        LifecycleDeclaration(
            start=NOW - timedelta(hours=2), correct_interval=True, reason="earlier work"
        ),
    )
    assert len([r for r in store.records() if r.kind == "outcome"]) == 3
    assert len([r for r in store.records() if r.kind == "interval"]) == 3


def test_bind_conflict_and_namespaces(store):
    c, r = initialized(store)
    other = register_change(store, "repo", "other")
    with pytest.raises(ContractError):
        bind_run(store, RUN, reference(other))
    another = register_run(store, RUN.model_copy(update={"surface": "cli"}), "c")
    assert another.record_id != r.record_id
    foreign = register_change(store, "foreign", "c")
    with pytest.raises(ContractError):
        bind_run(store, RUN, reference(foreign))
    with pytest.raises(ContractError):
        bind_evidence(store, "missing", RUN)
    assert c.features.change_shape == "bugfix"


def test_combined_lifecycle_retry_and_rejected_correction_preserve_history(store):
    _, run = initialized(store)
    target = reference(run)
    start, end = NOW - timedelta(hours=1), NOW
    declare(store, target, LifecycleDeclaration(outcome="failed", start=start, end=end))
    before = store.export_bundle()
    assert (
        declare(store, target, LifecycleDeclaration(outcome="failed", start=start, end=end)) == []
    )
    assert store.export_bundle() == before
    # A valid outcome correction must roll back if its paired interval is rejected.
    with pytest.raises(ContractError, match="interval correction requires flag and reason"):
        declare(
            store,
            target,
            LifecycleDeclaration(
                outcome="succeeded",
                start=start - timedelta(hours=1),
                correct_outcome=True,
                reason="reviewed correction",
            ),
        )
    assert store.export_bundle() == before
    revisions = declare(
        store,
        target,
        LifecycleDeclaration(
            outcome="succeeded",
            start=start - timedelta(hours=1),
            correct_outcome=True,
            correct_interval=True,
            reason="reviewed correction",
        ),
    )
    assert {r.kind for r in revisions} == {"outcome", "interval"}
    corrected = next(r for r in store.records() if r.kind == "interval" and r.previous)
    assert corrected.end == end
    assert corrected.reason == "reviewed correction"


def test_import_roundtrip_preserves_origin_and_destination_history(store, tmp_path):
    c, _ = initialized(store)
    source = store.export_bundle()
    dest = Store(tmp_path / "dest.sqlite", clock=lambda: NOW + timedelta(days=30))
    dest.import_bundle(loads_bundle(dumps_bundle(source)))
    assert dest.records() == store.records()
    before = dest.export_bundle()
    dest.import_bundle(source)
    assert dest.export_bundle() == before
    assert dest.eligible(reference(c), source.source) is False
    assert dest.eligible(reference(c), dest.snapshot()) is True
    prior_local_cutoff = dest.snapshot().model_copy(update={"at": NOW + timedelta(days=15)})
    assert not dest.eligible(reference(c), prior_local_cutoff)
    assert dest.snapshot().store_id != source.source.store_id
    assert any(o.store_id == source.source.store_id for o in before.observations)


def test_atomic_import_and_missing_reference(store, tmp_path):
    c, _ = initialized(store)
    source = store.export_bundle()
    bad = source.model_copy(update={"records": [r for r in source.records if r != c]})
    dest = Store(tmp_path / "missing.sqlite", clock=lambda: NOW)
    with pytest.raises(ContractError):
        dest.import_bundle(bad)
    assert not dest.path.exists()
    duplicate = c.model_copy(update={"change_id": "conflict"})
    with pytest.raises(ContractError):
        store.import_bundle(source.model_copy(update={"records": [*source.records, duplicate]}))
    assert store.export_bundle() == source


def test_cutoff_excludes_later_commits_even_with_same_time(store):
    first = register_change(store, "repo", "first")
    cutoff = store.snapshot()
    second = register_change(store, "repo", "second")
    assert store.eligible(reference(first), cutoff)
    assert not store.eligible(reference(second), cutoff)
    assert not store.eligible(reference(first), None)


def test_clock_regression_fails_without_mutation(store):
    initialized(store)
    before = store.export_bundle()
    store.clock = lambda: NOW - timedelta(seconds=1)
    with pytest.raises(ContractError, match="clock"):
        register_change(store, "repo", "new")
    store.clock = lambda: NOW
    assert store.export_bundle() == before


def test_busy_and_failed_commit_are_recoverable(store, monkeypatch):
    initialized(store)
    connection = store.connect()
    connection.execute("BEGIN IMMEDIATE")
    with pytest.raises(ContractError, match="busy"):
        register_change(store, "repo", "new")
    connection.rollback()
    connection.close()
    before = store.export_bundle()

    def fail(_connection):
        raise OSError("synthetic commit failure")

    original = store.commit
    monkeypatch.setattr(store, "commit", fail)
    with pytest.raises(ContractError):
        register_change(store, "repo", "new")
    assert store.export_bundle() == before
    monkeypatch.setattr(store, "commit", original)
    register_change(store, "repo", "new")


def test_newer_schema_and_consistent_backup(store, tmp_path):
    initialized(store)
    backup = tmp_path / "backup.sqlite"
    store.backup(backup)
    restored = Store(backup, clock=lambda: NOW)
    assert restored.export_bundle() == store.export_bundle()
    connection = store.connect()
    connection.execute("PRAGMA user_version=99")
    connection.close()
    original = store.path.read_bytes()
    with pytest.raises(ContractError, match="schema"):
        register_change(store, "repo", "other")
    assert store.path.read_bytes() == original
    assert len(restored.records()) == 3


def test_file_evidence_binding_and_origin_claim(store, tmp_path):
    from changecost.models import Evidence

    c, r = initialized(store)
    other = register_run(store, RUN.model_copy(update={"surface": "cli"}), "c")
    source = store.export_bundle()
    evidence = Evidence(
        record_id="row",
        origin_store_id="foreign",
        recorded_at=NOW,
        effective_at=NOW,
        provider="cursor",
        surface="export",
        profile="synthetic",
        identity_scope="file",
        file_digest="a" * 64,
        ordinal=0,
    )
    store.import_bundle(source.model_copy(update={"records": [evidence], "observations": []}))
    mapping = bind_evidence(store, "row", RUN)
    assert mapping.method == "manual" and mapping.run.surface == "ide"
    assert bind_evidence(store, "row", RUN) == mapping
    with pytest.raises(ContractError):
        bind_evidence(store, "row", other.ref)
    dest = Store(tmp_path / "copy.sqlite", clock=lambda: NOW + timedelta(days=1))
    dest.import_bundle(store.export_bundle())
    assert dest.records() == store.records()


def test_import_rejects_cyclic_wrong_subject_and_forked_revisions(store):
    from changecost.models import Outcome

    c, r = initialized(store)
    source = store.export_bundle()
    common = dict(origin_store_id="foreign", recorded_at=NOW, effective_at=NOW, reason="correct")
    first = Outcome.model_validate(
        dict(**common, record_id="a", subject=reference(c), outcome="accepted")
    )
    cycle_a = first.model_copy(update={"previous": RecordRef(kind="outcome", record_id="b")})
    cycle_b = first.model_copy(update={"record_id": "b", "previous": reference(first)})
    wrong = first.model_copy(
        update={
            "record_id": "b",
            "subject": reference(r),
            "outcome": "failed",
            "previous": reference(first),
        }
    )
    fork = first.model_copy(update={"record_id": "b"})
    for extras in [[cycle_a, cycle_b], [first, wrong], [first, fork]]:
        with pytest.raises(ContractError):
            store.import_bundle(source.model_copy(update={"records": extras, "observations": []}))
        assert store.export_bundle() == source


def test_quote_preserves_structure_but_foreign_replay_is_unavailable(store, tmp_path):
    from changecost.models import Component, Quote

    c, r = initialized(store)
    source = store.export_bundle()
    component = Component(
        economic_kind="monetary", unit="USD", basis="billed", currency="USD", amount=None
    )
    quote = Quote(
        record_id="quote",
        origin_store_id=source.source.store_id,
        recorded_at=NOW,
        effective_at=NOW,
        change=reference(c),
        state="unpriced",
        p50=component,
        p90=component,
        reason="insufficient_evidence",
        sample_count=0,
        cohort="repository",
        algorithm_version="future",
        cutoff=source.source,
        inputs=[reference(r)],
        features=c.features,
    )
    store.import_bundle(source.model_copy(update={"records": [quote], "observations": []}))
    dest = Store(tmp_path / "foreign.sqlite", clock=lambda: NOW + timedelta(days=1))
    dest.import_bundle(store.export_bundle())
    from changecost.cli import inspect_record

    result = inspect_record(dest, reference(quote))
    assert result["replay_eligibility"] == "replay_unavailable"
    assert result["record"]["p50"]["amount"] is None


def test_failed_initial_schema_has_no_published_store(tmp_path, monkeypatch):
    import changecost.store as module

    def interrupted(connection):
        connection.execute("CREATE TABLE partial(id TEXT)")
        raise OSError("interrupted migration")

    monkeypatch.setattr(module, "initialize", interrupted)
    store = Store(tmp_path / "new.sqlite", clock=lambda: NOW)
    with pytest.raises(ContractError):
        register_change(store, "repo", "c")
    assert not store.path.exists()


def test_delayed_commit_is_not_admitted_to_captured_snapshot(store):
    import threading

    from changecost.models import Change, Features
    from changecost.operations import common

    initialized(store)
    waiting = threading.Event()
    release = threading.Event()
    errors = []

    def operation(records, store_id, now):
        waiting.set()
        assert release.wait(5)
        c = Change(
            **common(store_id, now, "later"),
            repository_id="repo",
            change_id="later",
            features=Features(captured_at=now, recorded_at=now),
        )
        return [c], c

    def writer():
        try:
            store.apply(operation)
        except Exception as exc:
            errors.append(exc)

    thread = threading.Thread(target=writer)
    thread.start()
    assert waiting.wait(5)
    cutoff = store.snapshot()
    release.set()
    thread.join(5)
    assert not thread.is_alive() and not errors
    assert not store.eligible(RecordRef(kind="change", record_id="later"), cutoff)
    assert store.eligible(RecordRef(kind="change", record_id="later"), store.snapshot())


def settlement_fixture(store):
    from changecost.models import Component, Coverage, Evidence, EvidenceBinding, Settlement
    from changecost.operations import common

    c, r = initialized(store)
    outcome, interval = declare(
        store, reference(r), LifecycleDeclaration(outcome="failed", start=NOW, end=NOW)
    )
    source = store.export_bundle()
    evidence = Evidence(
        **common("producer", NOW, "evidence"),
        provider="cursor",
        surface="export",
        profile="synthetic",
        identity_scope="file",
        file_digest="b" * 64,
        ordinal=0,
    )
    mapping = EvidenceBinding(
        **common("producer", NOW, "mapping"),
        evidence=reference(evidence),
        run=r.ref,
        method="verified_provider",
        source_refs=[reference(evidence)],
    )
    amounts = [
        Component(
            economic_kind="monetary",
            unit="USD",
            basis="billed",
            currency="USD",
            amount="0.1234567890123456789012345678900",
        )
    ]
    for unit, value in [
        ("input_tokens", "100"),
        ("provider_credit", "2"),
        ("nano_aiu", "50"),
        ("unknown_credit", None),
    ]:
        amounts.append(
            Component(
                economic_kind="nonmonetary",
                unit=unit,
                basis="reported",
                currency=None,
                amount=value,
            )
        )
    settlement = Settlement(
        **common("producer", NOW, "settlement"),
        change=reference(c),
        components=amounts,
        completeness="provisional",
        scope="declared runs",
        coverage=[
            Coverage(run=r.ref, outcome=outcome, interval=interval, evidence=[reference(evidence)])
        ],
        inputs=[reference(evidence)],
        unknown_reasons=["unknown_credit"],
    )
    return source, evidence, mapping, settlement


@pytest.mark.parametrize("completeness", ["provisional", "reconciled"])
def test_settlement_exact_storage_restart_and_claim_roundtrip(store, tmp_path, completeness):
    source, evidence, mapping, settlement = settlement_fixture(store)
    store.import_bundle(
        source.model_copy(update={"records": [settlement, mapping, evidence], "observations": []})
    )
    revision = settlement.model_copy(
        update={
            "record_id": "settlement-revision",
            "previous": reference(settlement),
            "completeness": completeness,
        }
    )
    store.import_bundle(source.model_copy(update={"records": [revision], "observations": []}))
    restarted = Store(store.path, clock=lambda: NOW)
    stored = next(r for r in restarted.records() if r.kind == "settlement")
    assert stored == settlement
    assert stored.components[0].amount == "0.1234567890123456789012345678900"
    assert [c.amount for c in stored.components[1:]] == ["100", "2", "50", None]
    dest = Store(tmp_path / "roundtrip.sqlite", clock=lambda: NOW + timedelta(days=1))
    wire = loads_bundle(dumps_bundle(restarted.export_bundle()))
    dest.import_bundle(wire)
    before = dest.export_bundle()
    dest.import_bundle(wire)
    assert dest.export_bundle() == before
    assert dest.records() == restarted.records()
    assert next(r for r in dest.records() if r.record_id == "settlement-revision") == revision
    from changecost.cli import inspect_record

    assert (
        next(r for r in dest.records() if r.kind == "evidence_binding").method
        == "verified_provider"
    )
    assert "not_verified" in inspect_record(dest, reference(settlement))["provenance_status"]


@pytest.mark.parametrize("variant", ["wrong_change", "wrong_evidence_run", "unbound_evidence"])
def test_settlement_coverage_requires_matching_attribution(store, variant):
    source, evidence, mapping, settlement = settlement_fixture(store)
    other = register_change(store, "foreign", "other")
    other_run = register_run(store, RUN.model_copy(update={"repository_id": "foreign"}), "other")
    records = [evidence, mapping, settlement]
    if variant == "wrong_change":
        records[-1] = settlement.model_copy(update={"change": reference(other)})
    elif variant == "wrong_evidence_run":
        records[1] = mapping.model_copy(update={"run": other_run.ref})
    else:
        records.remove(mapping)
    before = store.export_bundle()
    with pytest.raises(ContractError):
        store.import_bundle(source.model_copy(update={"records": records, "observations": []}))
    assert store.export_bundle() == before


def test_settlement_cutoff_includes_attribution_availability(store):
    source, evidence, mapping, settlement = settlement_fixture(store)
    store.import_bundle(
        source.model_copy(update={"records": [evidence, mapping, settlement], "observations": []})
    )
    cutoff = store.snapshot()
    assert store.eligible(reference(settlement), cutoff)
    # A claimed future-effective attribution cannot enter an earlier replay.
    source2, evidence2, mapping2, settlement2 = settlement_fixture(
        Store(store.path.with_name("future.sqlite"), clock=lambda: NOW)
    )
    future = Store(store.path.with_name("future.sqlite"), clock=lambda: NOW)
    future.import_bundle(
        source2.model_copy(
            update={
                "records": [
                    evidence2,
                    mapping2.model_copy(update={"effective_at": NOW + timedelta(days=1)}),
                    settlement2,
                ],
                "observations": [],
            }
        )
    )
    assert not future.eligible(reference(settlement2), future.snapshot())


def test_delayed_outcomes_keep_work_bounds_and_retry_history(store):
    c, r = initialized(store)
    start, end = NOW + timedelta(minutes=10), NOW + timedelta(minutes=30)
    store.clock = lambda: NOW + timedelta(minutes=40)
    declare(store, reference(r), LifecycleDeclaration(start=start, end=end))
    store.clock = lambda: NOW + timedelta(hours=2)
    declare(store, reference(r), LifecycleDeclaration(outcome="failed"))
    retry = register_run(store, RUN.model_copy(update={"run_id": "retry"}), "c")
    declare(store, reference(retry), LifecycleDeclaration(outcome="succeeded"))
    declare(store, reference(c), LifecycleDeclaration(outcome="accepted"))
    intervals = [r for r in store.records() if r.kind == "interval"]
    assert len(intervals) == 1 and (intervals[0].start, intervals[0].end) == (start, end)
    assert {r.outcome for r in store.records() if r.kind == "outcome"} == {
        "failed",
        "succeeded",
        "accepted",
    }
    assert not any(r.kind == "settlement" for r in store.records())


def test_unbound_and_all_run_namespaces_survive_arbitrary_order(store, tmp_path):
    from changecost.models import Run
    from changecost.operations import common

    c, first = initialized(store)
    register_change(store, "other", "c")
    variants = [
        RUN.model_copy(update={field: "other"})
        for field in ["repository_id", "provider", "surface"]
    ]
    for ref in variants:
        register_run(store, ref, "c")
    orphan = Run(
        **common("producer", NOW, "orphan"), ref=RUN.model_copy(update={"run_id": "orphan"})
    )
    source = store.export_bundle()
    source = source.model_copy(update={"records": [orphan, *reversed(source.records)]})
    destination = Store(tmp_path / "namespaces.sqlite", clock=lambda: NOW)
    destination.import_bundle(source)
    destination.import_bundle(source)
    runs = [r for r in destination.records() if r.kind == "run"]
    assert len(runs) == 5 and len({tuple(r.ref.model_dump().values()) for r in runs}) == 5
    assert not any(r.kind == "run_binding" and r.run == orphan.ref for r in destination.records())


def test_competing_attribution_retries_observe_winner(store):
    from changecost.models import Run, RunBinding
    from changecost.operations import common

    a = register_change(store, "repo", "a")
    b = register_change(store, "repo", "b")
    source = store.export_bundle()
    run = Run(**common("source", NOW, "unbound"), ref=RUN)
    store.import_bundle(source.model_copy(update={"records": [run], "observations": []}))
    import threading

    started, release = threading.Event(), threading.Event()
    errors = []

    def operation(records, store_id, now):
        started.set()
        assert release.wait(5)
        binding = RunBinding(**common(store_id, now, "winner"), run=RUN, change=reference(a))
        return [binding], binding

    def writer():
        try:
            store.apply(operation)
        except Exception as exc:
            errors.append(exc)

    thread = threading.Thread(target=writer)
    thread.start()
    assert started.wait(5)
    try:
        with pytest.raises(ContractError, match="busy"):
            bind_run(store, RUN, reference(b))
    finally:
        release.set()
        thread.join(5)
    assert not thread.is_alive() and not errors
    with pytest.raises(ContractError, match="conflicting"):
        bind_run(Store(store.path, clock=lambda: NOW), RUN, reference(b))
    bindings = [r for r in store.records() if r.kind == "run_binding"]
    assert len(bindings) == 1 and bindings[0].change == reference(a)


def test_future_cutoff_cannot_admit_future_effective_inputs(store):
    from changecost.cli import inspect_record
    from changecost.models import Change, Component, Features, Quote
    from changecost.operations import common

    registered = register_change(store, "repo", "registered")
    source = store.export_bundle()
    future = Change(
        **{**common("producer", NOW, "future"), "effective_at": NOW + timedelta(days=1)},
        repository_id="repo",
        change_id="future",
        features=Features(captured_at=NOW, recorded_at=NOW),
    )
    store.import_bundle(source.model_copy(update={"records": [future], "observations": []}))
    cutoff = store.snapshot().model_copy(update={"at": NOW + timedelta(days=2)})
    component = Component(economic_kind="monetary", unit="USD", basis="billed", amount=None)
    quote = Quote(
        **common("producer", NOW, "future-quote"),
        change=reference(registered),
        state="unpriced",
        p50=component,
        p90=component,
        reason="unknown",
        sample_count=0,
        cohort="synthetic",
        algorithm_version="synthetic",
        cutoff=cutoff,
        inputs=[reference(future)],
    )
    store.import_bundle(source.model_copy(update={"records": [quote], "observations": []}))
    before = store.export_bundle()
    assert not store.eligible(reference(future), cutoff)
    assert inspect_record(store, reference(quote))["replay_eligibility"] == "replay_unavailable"
    assert store.export_bundle() == before


@pytest.mark.parametrize("kind", ["outcome", "interval", "settlement"])
def test_inspection_orders_each_revision_chain_by_predecessor(store, kind):
    from changecost.cli import inspect_record
    from changecost.models import Interval, Outcome, Settlement
    from changecost.operations import common

    change, run = initialized(store)
    if kind == "outcome":
        original = Outcome(
            **common("producer", NOW, "z-original"), subject=reference(run), outcome="failed"
        )
        target = reference(run)
    elif kind == "interval":
        original = Interval(**common("producer", NOW, "z-original"), run=run.ref, start=NOW)
        target = reference(run)
    else:
        original = Settlement(
            **common("producer", NOW, "z-original"),
            change=reference(change),
            components=[],
            completeness="provisional",
            scope="synthetic",
            coverage=[],
            inputs=[],
            unknown_reasons=["unknown"],
        )
        target = reference(change)
    updates = {"record_id": "a-correction", "previous": reference(original)}
    if kind in {"outcome", "interval"}:
        updates["reason"] = "correction"
    second = original.model_copy(update=updates)
    third = second.model_copy(update={"record_id": "m-latest", "previous": reference(second)})
    bundle = store.export_bundle()
    store.import_bundle(
        bundle.model_copy(update={"records": [third, second, original], "observations": []})
    )
    before = store.export_bundle()
    history = inspect_record(store, target)["revisions"]
    assert [r["record_id"] for r in history if r["kind"] == kind] == [
        "z-original",
        "a-correction",
        "m-latest",
    ]
    assert store.export_bundle() == before
