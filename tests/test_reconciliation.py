"""Synthetic acceptance scenarios for normalized economics and immutable computation."""

from datetime import UTC, datetime, timedelta
from decimal import localcontext
from itertools import permutations

import pytest

from changecost.models import RunRef
from changecost.operations import (
    LifecycleDeclaration,
    bind_evidence,
    declare,
    register_change,
    register_run,
)
from changecost.serialization import ContractError, dumps_bundle, loads_bundle
from changecost.store import ADAPTER, Store, reference

NOW = datetime(2026, 9, 29, 10, tzinfo=UTC)
START = NOW - timedelta(hours=1)
RUN = RunRef(repository_id="repo", provider="synthetic", surface="fixture", run_id="run")
IDENTITY = dict(economic_kind="monetary", unit="USD", currency="USD", basis="billed")


def locator(event="a", **updates):
    return dict(
        repository_id="repo",
        provider="synthetic",
        surface="fixture",
        profile="synthetic/v1",
        namespace="opaque",
        identity_scope="namespaced",
        source_key=event,
        file_digest=None,
        ordinal=None,
        **updates,
    )


def event(name="a", amount: str | None = "0.40", **updates):
    result = dict(
        source=locator(name),
        component_key="charge",
        component={**IDENTITY, "amount": amount},
        series="usage",
        lane="delta",
        start=START.isoformat(),
        end=START.isoformat(),
        baseline_zero=False,
        replaces=None,
        correction_reason=None,
    )
    result.update(updates)
    return result


def economic(name="a"):
    return dict(
        schema="changecost/v1",
        kind="economic_evidence",
        record_id=name,
        origin_store_id="origin",
        recorded_at=NOW.isoformat(),
        effective_at=START.isoformat(),
        evidence={"kind": "evidence", "record_id": "e"},
        **event(name),
    )


def test_portable_economic_kind_and_exact_amount():
    payload = economic()
    parsed = ADAPTER.validate_python(payload)
    assert parsed.model_dump(mode="json", by_alias=True)["component"]["amount"] == "0.40"
    for mutation in ({"raw_prompt": "PRIVATE"}, {"component": {**IDENTITY, "amount": 0.4}}):
        with pytest.raises(ValueError):
            ADAPTER.validate_python({**payload, **mutation})


def test_normalized_import_duplicate_retry_and_components(tmp_path):
    from changecost import normalized

    store = Store(tmp_path / "db", clock=lambda: NOW)
    batch = {
        "schema": "changecost/normalized-v1",
        "repository_id": "repo",
        "batch_id": "one",
        "events": [event(), event("b", "0.20"), event()],
    }
    selectors = normalized.import_evidence(store, batch, "repo")
    original = store.export_bundle()
    assert len(set(selectors)) == 2
    batch["batch_id"] = "two"
    batch["events"] = list(reversed(batch["events"]))
    assert set(normalized.import_evidence(store, batch, "repo")) == set(selectors)
    assert store.export_bundle() == original
    batch["events"] = [
        event(
            component_key="tokens",
            component=dict(
                economic_kind="nonmonetary", unit="token", currency=None, basis="input", amount="12"
            ),
        )
    ]
    assert normalized.import_evidence(store, batch, "repo") == [selectors[0]]
    assert len([r for r in store.records() if r.kind == "evidence"]) == 2
    assert len([r for r in store.records() if r.kind == "economic_evidence"]) == 3


def import_events(store, *events):
    from changecost.normalized import import_evidence

    return import_evidence(
        store,
        {
            "schema": "changecost/normalized-v1",
            "repository_id": "repo",
            "batch_id": "fixture",
            "events": list(events),
        },
        "repo",
    )


def setup_change(tmp_path, runs=1):
    store = Store(tmp_path / "db", clock=lambda: NOW, timeout=0)
    change = register_change(store, "repo", "change")
    members = []
    for i in range(runs):
        ref = RUN.model_copy(update={"run_id": str(i)})
        run = register_run(store, ref, "change", work_start=START)
        declare(
            store,
            reference(run),
            LifecycleDeclaration(end=NOW, outcome="failed" if i else "succeeded"),
        )
        members.append(ref)
    declare(store, reference(change), LifecycleDeclaration(outcome="accepted"))
    return store, change, members


def scope(**updates):
    from changecost.models import EconomicScope

    return EconomicScope.model_validate(dict(repository_id="repo", economic=IDENTITY, **updates))


def compute(store, op="op", **updates):
    from changecost.reconciliation import compute_settlement

    return compute_settlement(store, "change", scope(**updates), op)


def test_normalized_conflict_and_invalid_atomicity(tmp_path):
    store = Store(tmp_path / "db", clock=lambda: NOW)
    for invalid in [
        event(component={**IDENTITY, "amount": 0.4}),
        event(raw_prompt="PRIVATE"),
        event(start="yesterday"),
        event(source={**locator(), "namespace": 12}),
    ]:
        with pytest.raises(ContractError) as exc:
            import_events(store, event(), invalid)
        assert "PRIVATE" not in str(exc.value)
        assert not store.path.exists()
    import_events(store, event())
    before = store.export_bundle()
    with pytest.raises(ContractError):
        import_events(store, event("new"), event(amount="0.9"))
    assert store.export_bundle() == before
    import_events(store, event(source={**locator(), "namespace": "other"}))
    assert len([r for r in store.records() if r.kind == "economic_evidence"]) == 2


def test_replacement_pending_resolution_forks_cycles_and_currency(tmp_path):
    store, _, members = setup_change(tmp_path)
    replacement = event("b", "0.25", replaces=locator(), correction_reason="corrected")
    ids = import_events(store, replacement)
    bind_evidence(store, ids[0], members[0])
    pending = compute(store, "pending")
    assert pending.subtotals[0].amount is None
    assert "pending_correction" in pending.unknown_reasons
    ids = import_events(store, event())
    bind_evidence(store, ids[0], members[0])
    corrected = compute(store, "corrected")
    assert corrected.subtotals[0].amount == "0.25"
    assert compute(store, "pending") == pending
    before = store.export_bundle()
    for invalid in [
        event("c", "0.30", replaces=locator(), correction_reason="fork"),
        event(
            "c",
            component={**IDENTITY, "currency": "EUR", "amount": "0.30"},
            replaces=locator("b"),
            correction_reason="currency",
        ),
    ]:
        with pytest.raises(ContractError):
            import_events(store, invalid)
        assert store.export_bundle() == before
    ids = import_events(store, event("c", "0", replaces=locator("b"), correction_reason="reversal"))
    bind_evidence(store, ids[0], members[0])
    assert compute(store, "reversal").subtotals[0].amount == "0"
    other = Store(tmp_path / "cycle", clock=lambda: NOW)
    with pytest.raises(ContractError):
        import_events(
            other, event("a", replaces=locator("b"), correction_reason="cycle"), replacement
        )
    assert not other.path.exists()


def test_exact_aggregation_and_limits():
    from changecost.reconciliation import exact_sum

    with localcontext() as context:
        context.prec = 3
        for order in permutations(
            ["10000000000000000000000000000", "1", "-10000000000000000000000000000"]
        ):
            assert exact_sum(order) == "1"
        assert exact_sum(["0.10", "0.20"]) == "0.30"
        assert exact_sum(["-0.25", "0.10"]) == "-0.15"
        assert exact_sum([]) is None
        assert exact_sum(["0"]) == "0"
        assert exact_sum(["1e4095"]) == "1" + "0" * 4095
    for values in [["1e4096"], ["1", "1e-4096"], ["0"] * 100001]:
        with pytest.raises(ContractError, match="limit"):
            exact_sum(values)
    assert exact_sum(["0"] * 100000) == "0"


def test_snapshot_lane_and_unknown_baseline(tmp_path):
    store, _, members = setup_change(tmp_path)
    ids = import_events(
        store,
        event("d", "0.20"),
        event("s", "0.50", lane="snapshot", end=NOW.isoformat(), baseline_zero=True),
    )
    for ident in ids:
        bind_evidence(store, ident, members[0])
    result = compute(store)
    assert result.subtotals[0].amount == "0.50"
    assert any(e.reason == "non_authoritative_lane" for e in result.exclusions)
    assert result.synthetic
    partial = compute(store, "partial", start=START + timedelta(minutes=1), end=NOW)
    assert partial.subtotals[0].amount is None
    assert "unsupported_snapshot_window" in partial.unknown_reasons


def test_operation_retry_portable_authority_and_backup(tmp_path):
    from changecost.reconciliation import inspect_computation

    store, change, members = setup_change(tmp_path)
    ids = import_events(store, event())
    bind_evidence(store, ids[0], members[0])
    first = compute(store)
    assert first.subtotals[0].amount == "0.40"
    ids = import_events(store, event("retry", "0.20"))
    bind_evidence(store, ids[0], members[0])
    assert compute(store) == first
    newer = compute(store, "new")
    assert newer.previous == reference(first)
    assert newer.cutoff.sequence > first.cutoff.sequence
    assert newer.subtotals[0].amount == "0.60"
    with pytest.raises(ContractError):
        compute(store, start=START, end=NOW)
    destination = Store(tmp_path / "foreign", clock=lambda: NOW)
    bundle = loads_bundle(dumps_bundle(store.export_bundle()))
    destination.import_bundle(bundle.model_copy(update={"records": list(reversed(bundle.records))}))
    destination.import_bundle(bundle)
    assert inspect_computation(destination, first)["local_computation"] is False
    assert inspect_computation(destination, first)["replay_eligibility"] == "replay_unavailable"
    assert compute(destination, "local").previous is None
    store.backup(tmp_path / "backup")
    backup = Store(tmp_path / "backup", clock=lambda: NOW)
    assert compute(backup) == first
    assert inspect_computation(backup, first)["local_computation"] is True
    assert inspect_computation(store, first)["current_eligibility"] == "snapshot_only"
    assert change in destination.records()


def test_incompatible_layout_unchanged(tmp_path):
    import sqlite3

    store = Store(tmp_path / "legacy", clock=lambda: NOW)
    connection = sqlite3.connect(store.path)
    connection.execute("PRAGMA user_version=1")
    connection.close()
    before = store.path.read_bytes()
    with pytest.raises(ContractError, match="unsupported store"):
        import_events(store, event())
    assert store.path.read_bytes() == before


def add_coverage(store, run, evidence, **updates):
    from changecost.models import SourceCoverage
    from changecost.operations import common

    def operation(records, store_id, now):
        payload = dict(
            **common(store_id, now),
            run=run,
            provider="synthetic",
            surface="fixture",
            profile="synthetic/v1",
            namespace="opaque",
            component_key="charge",
            policy_version="synthetic/v1",
            economic=IDENTITY,
            start=START,
            end=NOW,
            final=True,
            evidence=[{"kind": "evidence", "record_id": evidence}],
        )
        payload.update(updates)
        record = SourceCoverage.model_validate(payload)
        return [record], record

    return store.apply(operation)


def test_complete_synthetic_coverage_and_late_unbound(tmp_path):
    store, _, members = setup_change(tmp_path)
    ids = import_events(store, event())
    bind_evidence(store, ids[0], members[0])
    add_coverage(store, members[0], ids[0])
    full = compute(store)
    assert full.full_change and full.synthetic
    assert full.runs == members and full.unknown_reasons == []
    import_events(store, event("late", "0.20"))
    later = compute(store, "later")
    assert not later.full_change and "relevant_unbound_evidence" in later.unknown_reasons
    assert compute(store) == full


@pytest.mark.parametrize(
    "failure",
    [
        "omitted_run",
        "open_run",
        "zero_runs",
        "no_coverage",
        "unverified",
        "bounds",
        "endpoint",
        "unknown",
        "zero_duration",
        "unsupported_source",
    ],
)
def test_coverage_failure_modes(tmp_path, failure):
    store, change, members = setup_change(
        tmp_path, runs=0 if failure == "zero_runs" else 2 if failure == "omitted_run" else 1
    )
    if failure == "zero_runs":
        assert not compute(store).full_change
        return
    item = coverage_failure_event(failure)
    ids = import_events(store, item)
    bind_evidence(store, ids[0], members[0])
    if failure not in {"no_coverage", "zero_duration"}:
        add_coverage(
            store,
            members[0],
            ids[0],
            profile="manual" if failure == "unverified" else "synthetic/v1",
        )
    if failure == "bounds":
        record = next(r for r in store.records() if r.kind == "run")
        declare(
            store,
            reference(record),
            LifecycleDeclaration(end=START, correct_interval=True, reason="corrected"),
        )
    if failure == "open_run":
        # Add an explicitly linked existing open Run via portable atomic import.
        from changecost.models import Run, RunBinding
        from changecost.operations import common

        ref = RUN.model_copy(update={"run_id": "open"})

        def operation(records, store_id, now):
            return [
                Run(**common(store_id, now), ref=ref),
                RunBinding(**common(store_id, now), run=ref, change=reference(change)),
            ], None

        store.apply(operation)
    assert not compute(store).full_change


def test_repository_buckets_and_file_overlap(tmp_path):
    from changecost.reconciliation import repository_report

    store, _, members = setup_change(tmp_path)
    ids = import_events(store, event(), event("unbound", "0.20"))
    bind_evidence(store, ids[0], members[0])
    before = store.export_bundle()
    report = repository_report(store, scope())
    assert report["bound"][0]["amount"] == "0.40"
    assert report["unbound"][0]["amount"] == "0.20"
    assert store.export_bundle() == before
    files = [
        event(
            str(i),
            "9",
            source={
                **locator(),
                "identity_scope": "file",
                "source_key": None,
                "file_digest": str(i) * 64,
                "ordinal": 0,
            },
            series="files",
        )
        for i in (1, 2)
    ]
    import_events(store, *files)
    report = repository_report(store, scope())
    assert "dedupe_limited_overlap" in report["unknown_reasons"]
    assert report["unbound"][0]["amount"] == "0.20"


def test_unknown_currency_resolution_and_unit_partitions(tmp_path):
    from changecost.reconciliation import repository_report

    store, _, members = setup_change(tmp_path)
    unknown = event(component={**IDENTITY, "currency": None, "amount": None})
    ids = import_events(store, unknown)
    bind_evidence(store, ids[0], members[0])
    first = compute(store)
    assert sum(s.unknown_count for s in first.subtotals) == 1
    assert all(s.amount is None for s in first.subtotals)
    ids = import_events(
        store, event("fixed", "0.25", replaces=locator(), correction_reason="currency found")
    )
    bind_evidence(store, ids[0], members[0])
    assert compute(store, "fixed").subtotals[0].amount == "0.25"
    assert compute(store) == first
    import_events(
        store,
        event("eur", component={**IDENTITY, "currency": "EUR", "unit": "EUR", "amount": "2"}),
        event("estimate", component={**IDENTITY, "basis": "estimated", "amount": "3"}),
    )
    assert repository_report(store, scope())["bound"][0]["amount"] == "0.25"


@pytest.mark.parametrize("failure", ["commit", "busy", "exhausted", "digits"])
def test_compute_failure_atomicity(tmp_path, monkeypatch, failure):
    from changecost.models import MAX_SEQUENCE

    store, _, members = setup_change(tmp_path)
    ids = import_events(store, event(amount="1e4096" if failure == "digits" else "0.40"))
    bind_evidence(store, ids[0], members[0])
    connection = store.connect()
    if failure == "exhausted":
        connection.execute("UPDATE metadata SET sequence=?", (MAX_SEQUENCE,))
    before = store.export_bundle()
    if failure == "busy":
        connection.execute("BEGIN IMMEDIATE")
    if failure == "commit":

        def fail(_connection):
            raise ContractError("injected commit failure")

        monkeypatch.setattr(store, "commit", fail)
    try:
        with pytest.raises(ContractError):
            compute(store)
    finally:
        connection.rollback()
        connection.close()
    assert store.export_bundle() == before
    connection = store.connect(readonly=True)
    assert connection.execute("SELECT COUNT(*) FROM computations").fetchone()[0] == 0
    connection.close()


def test_response_loss_returns_original_and_import_cannot_extend_local_ledger(tmp_path):
    from changecost.models import ComputedSettlement

    store, _, members = setup_change(tmp_path)
    ids = import_events(store, event())
    bind_evidence(store, ids[0], members[0])
    first = compute(store)
    # A producer can copy origin fields but cannot mint local operation authority.
    forged = ComputedSettlement.model_validate(
        {
            **first.model_dump(),
            "record_id": "forged",
            "operation_id": "forged",
            "previous": reference(first),
        }
    )
    bundle = store.export_bundle()
    before = bundle
    with pytest.raises(ContractError):
        store.import_bundle(bundle.model_copy(update={"records": [forged]}))
    assert store.export_bundle() == before
    assert compute(store) == first


def test_three_link_correction_rejects_changed_attribution_at_import(tmp_path):
    store, _, members = setup_change(tmp_path, runs=2)
    ids = import_events(store, event("a"), event("b", replaces=locator("a"), correction_reason="b"))
    bind_evidence(store, ids[0], members[0])
    ids = import_events(store, event("c", replaces=locator("b"), correction_reason="c"))
    before = store.export_bundle()
    with pytest.raises(ContractError):
        bind_evidence(store, ids[0], members[1])
    assert store.export_bundle() == before


def test_cross_change_evidence_does_not_break_independent_compute(tmp_path):
    store, _, members = setup_change(tmp_path)
    register_change(store, "repo", "second")
    other = RUN.model_copy(update={"run_id": "second"})
    register_run(store, other, "second")
    ids = import_events(store, event(), event("other", "1"))
    bind_evidence(store, ids[0], members[0])
    bind_evidence(store, ids[1], other)
    assert compute(store).subtotals[0].amount == "0.40"


def test_future_evidence_has_same_visibility_in_report_and_computation(tmp_path):
    from changecost.reconciliation import repository_report

    store, _, members = setup_change(tmp_path)
    ids = import_events(
        store,
        event(
            start=(NOW + timedelta(hours=1)).isoformat(), end=(NOW + timedelta(hours=1)).isoformat()
        ),
    )
    bind_evidence(store, ids[0], members[0])
    result = compute(store)
    assert result.subtotals[0].amount is None
    report = repository_report(store, scope())
    assert report["bound"][0]["amount"] is None


def test_portable_computed_wrong_subject_rejected(tmp_path):
    store, _, members = setup_change(tmp_path)
    ids = import_events(store, event())
    bind_evidence(store, ids[0], members[0])
    first = compute(store)
    other = register_change(store, "repo", "other")
    declare(store, reference(other), LifecycleDeclaration(outcome="abandoned"))
    foreign = next(
        r for r in store.records() if r.kind == "outcome" and r.subject == reference(other)
    )
    broken = first.model_copy(
        update={
            "record_id": "broken",
            "ledger_id": "independent",
            "inputs": [*first.inputs, reference(foreign)],
        }
    )
    before = store.export_bundle()
    with pytest.raises(ContractError):
        store.import_bundle(before.model_copy(update={"records": [broken]}))
    assert store.export_bundle() == before


def test_copied_normalized_model_is_revalidated(tmp_path):
    from changecost.normalized import NormalizedBatch, import_evidence

    batch = NormalizedBatch.model_validate(
        {
            "schema": "changecost/normalized-v1",
            "repository_id": "repo",
            "batch_id": "b",
            "events": [event()],
        }
    )
    bad = batch.events[0].model_copy(update={"component": {"private": "SENTINEL"}})
    store = Store(tmp_path / "db")
    with pytest.raises(ContractError) as exc:
        import_evidence(store, batch.model_copy(update={"events": [bad]}), "repo")
    assert "SENTINEL" not in str(exc.value)
    assert not store.path.exists()


@pytest.mark.parametrize("snapshot", [False, True])
def test_full_coverage_cannot_hide_attributed_contradictions(tmp_path, snapshot):
    store, _, members = setup_change(tmp_path)
    items = [event()]
    if snapshot:
        items.append(
            event("snapshot", "0.50", lane="snapshot", end=NOW.isoformat(), baseline_zero=True)
        )
    ids = import_events(store, *items)
    for ident in ids:
        bind_evidence(store, ident, members[0])
    add_coverage(store, members[0], ids[-1])
    store.clock = lambda: NOW + timedelta(hours=1)
    after = NOW + timedelta(minutes=1)
    ids = import_events(
        store, event("contradiction", "0.20", start=after.isoformat(), end=after.isoformat())
    )
    bind_evidence(store, ids[0], members[0])
    result = compute(store, "contradiction", start=START, end=NOW)
    assert not result.full_change
    assert "contradicted_work_bounds" in result.unknown_reasons


def test_resolved_currency_excludes_historical_unknown_from_other_scope(tmp_path):
    from changecost.models import EconomicScope
    from changecost.reconciliation import repository_report

    store, _, members = setup_change(tmp_path)
    ids = import_events(
        store,
        event(component={**IDENTITY, "currency": None, "amount": None}),
        event("usd", "0.25", replaces=locator(), correction_reason="currency confirmed"),
    )
    for ident in ids:
        bind_evidence(store, ident, members[0])
    requested = EconomicScope.model_validate(
        {"repository_id": "repo", "economic": {**IDENTITY, "currency": "EUR"}}
    )
    result = repository_report(store, requested)
    assert result["bound"] == [
        {"economic": requested.economic.model_dump(), "amount": None, "unknown_count": 0}
    ]


def test_portable_dependency_roles_and_inspection_revalidation(tmp_path):
    from changecost.models import Exclusion
    from changecost.reconciliation import inspect_computation

    store, _, members = setup_change(tmp_path)
    ids = import_events(store, event())
    bind_evidence(store, ids[0], members[0])
    first = compute(store)
    other = register_change(store, "repo", "other")
    declare(store, reference(other), LifecycleDeclaration(outcome="abandoned"))
    outcome = next(
        r for r in store.records() if r.kind == "outcome" and r.subject == reference(other)
    )
    for patch in [
        {"exclusions": [Exclusion(reference=reference(outcome), reason="unsupported")]},
        {"inputs": [*first.inputs, reference(other)]},
    ]:
        forged = first.model_copy(update={"record_id": "forged", "ledger_id": "foreign", **patch})
        before = store.export_bundle()
        with pytest.raises(ContractError):
            store.import_bundle(before.model_copy(update={"records": [forged]}))
        assert store.export_bundle() == before
    with pytest.raises(ContractError):
        inspect_computation(store, first.model_copy(update={"full_change": True, "inputs": []}))


def test_unverified_profile_label_cannot_select_snapshot_lane(tmp_path):
    store, _, members = setup_change(tmp_path)
    source = {**locator(), "provider": "manual", "namespace": "unverified"}
    ids = import_events(
        store,
        event("d", source={**source, "source_key": "d"}),
        event(
            "s",
            "0.50",
            source={**source, "source_key": "s"},
            lane="snapshot",
            end=NOW.isoformat(),
            baseline_zero=True,
        ),
    )
    for ident in ids:
        bind_evidence(store, ident, members[0])
    result = compute(store)
    assert result.subtotals[0].amount is None
    assert "unsupported_temporal_lane" in result.unknown_reasons
    assert not result.synthetic


@pytest.mark.parametrize("case", ["baseline", "multiple", "mixed", "partial_delta", "file_replay"])
def test_temporal_and_file_acceptance(tmp_path, case):
    store, _, members = setup_change(tmp_path, runs=2)
    snapshot = event(
        "s", "0.50", lane="snapshot", end=NOW.isoformat(), baseline_zero=case != "baseline"
    )
    events = [snapshot, event("d", "0.20")]
    if case == "multiple":
        events.append(event("s2", "0.60", lane="snapshot", end=NOW.isoformat(), baseline_zero=True))
    if case == "partial_delta":
        events = [event(end=NOW.isoformat())]
    if case == "file_replay":
        events = [
            event(
                source={
                    **locator(),
                    "identity_scope": "file",
                    "source_key": None,
                    "file_digest": "a" * 64,
                    "ordinal": 0,
                }
            )
        ]
    ids = import_events(store, *events)
    before = store.export_bundle()
    assert import_events(store, *events) == ids
    assert store.export_bundle() == before
    for i, ident in enumerate(ids):
        bind_evidence(store, ident, members[1] if case == "mixed" and i == 1 else members[0])
    result = (
        compute(store, start=START + timedelta(minutes=1), end=NOW)
        if case == "partial_delta"
        else compute(store)
    )
    if case == "file_replay":
        assert result.subtotals[0].amount == "0.40"
    else:
        assert result.subtotals[0].amount is None
        assert not result.full_change


def test_observed_zero_multiple_retries_abandoned_and_missing(tmp_path):
    from changecost.reconciliation import repository_report

    store, change, members = setup_change(tmp_path, runs=2)
    ids = import_events(store, event("a", "0"), event("retry", "0"))
    for run, ident in zip(members, ids, strict=True):
        bind_evidence(store, ident, run)
        add_coverage(store, run, ident)
    result = compute(store)
    assert result.full_change and result.subtotals[0].amount == "0"
    declare(
        store,
        reference(change),
        LifecycleDeclaration(outcome="abandoned", correct_outcome=True, reason="abandoned"),
    )
    later = compute(store, "abandoned")
    assert later.full_change
    assert repository_report(store, scope())["bound"][0]["amount"] == "0"
    assert compute(store) == result


def test_new_component_reuses_portably_assigned_core_record_id(tmp_path):
    from changecost.models import RecordRef

    store = Store(tmp_path / "source", clock=lambda: NOW)
    import_events(store, event())
    bundle = store.export_bundle()
    rewritten = []
    for record in bundle.records:
        if record.kind == "evidence":
            record = record.model_copy(update={"record_id": "portable-evidence"})
        if record.kind == "economic_evidence":
            record = record.model_copy(
                update={"evidence": RecordRef(kind="evidence", record_id="portable-evidence")}
            )
        rewritten.append(record)
    target = Store(tmp_path / "target", clock=lambda: NOW)
    target.import_bundle(bundle.model_copy(update={"records": rewritten, "observations": []}))
    ids = import_events(
        target,
        event(
            component_key="tokens",
            component=dict(
                economic_kind="nonmonetary", unit="token", basis="input", currency=None, amount="12"
            ),
        ),
    )
    assert ids == ["portable-evidence"]
    assert len([r for r in target.records() if r.kind == "evidence"]) == 1


def test_source_coverage_rejects_foreign_evidence_subject(tmp_path):
    store, _, members = setup_change(tmp_path, runs=2)
    ids = import_events(store, event())
    bind_evidence(store, ids[0], members[0])
    before = store.export_bundle()
    with pytest.raises(ContractError):
        add_coverage(store, members[1], ids[0])
    assert store.export_bundle() == before


def coverage_failure_event(failure):
    item = event()
    if failure == "unknown":
        item = event(amount=None)
    if failure == "bounds":
        item = event(
            start=(START + timedelta(minutes=1)).isoformat(),
            end=(START + timedelta(minutes=1)).isoformat(),
        )
    if failure == "endpoint":
        item = event(start=NOW.isoformat(), end=NOW.isoformat())
    if failure == "unsupported_source":
        item = event(source={**locator(), "profile": "manual"})
    return item
