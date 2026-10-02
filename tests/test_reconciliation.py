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


@pytest.mark.parametrize("foreign_kind", ["snapshot", "pending", "pending_namespace", "inherited"])
def test_foreign_change_does_not_contaminate_selection(tmp_path, foreign_kind):
    store, _, members = setup_change(tmp_path)
    target = event("target", "0.50", lane="snapshot", end=NOW.isoformat(), baseline_zero=True)
    target_id = import_events(store, target)[0]
    bind_evidence(store, target_id, members[0])
    add_coverage(store, members[0], target_id)
    before = compute(store, "before")
    assert before.full_change and before.subtotals[0].amount == "0.50"
    register_change(store, "repo", "foreign")
    other = RUN.model_copy(update={"run_id": "foreign"})
    register_run(store, other, "foreign", work_start=START - timedelta(hours=1))
    foreign = event(
        "foreign",
        "0.80",
        lane="snapshot",
        baseline_zero=True,
        start=(START - timedelta(hours=1)).isoformat(),
        end=(START - timedelta(minutes=30)).isoformat(),
    )
    if foreign_kind in {"pending", "pending_namespace"}:
        foreign.update(replaces=locator("absent"), correction_reason="pending")
        if foreign_kind == "pending_namespace":
            foreign["source"] = {**locator("foreign"), "namespace": "other-source"}
            foreign["replaces"] = {**locator("absent"), "namespace": "other-source"}
    foreign_id = import_events(store, foreign)[0]
    bind_evidence(store, foreign_id, other)
    if foreign_kind == "inherited":
        import_events(
            store,
            {
                **foreign,
                "source": locator("replacement"),
                "replaces": locator("foreign"),
                "correction_reason": "corrected",
            },
        )
    after = compute(store, "after")
    assert after.full_change and after.subtotals == before.subtotals
    assert after.unknown_reasons == before.unknown_reasons
    assert after.exclusions == before.exclusions
    assert after.inputs == before.inputs


class CountingRecords(dict):
    visits = 0

    def values(self):
        self.visits += len(self)
        return super().values()


def counted_economic_records(count):
    from changecost.models import EconomicInput
    from changecost.normalized import normalized_records
    from changecost.store import key

    records = CountingRecords()
    for index in range(count):
        pair = normalized_records(EconomicInput.model_validate(event(str(index))), "origin", NOW)
        records.update((key(reference(record)), record) for record in pair)
    return records


@pytest.mark.parametrize("count", [20, 40])
def test_economic_binding_lookup_does_not_rescan_records(count):
    from changecost.store import validate_graph

    records = counted_economic_records(count)
    validate_graph(records)
    assert records.visits <= 20 * count


@pytest.mark.parametrize("count", [20, 40])
def test_normalized_identity_lookup_does_not_rescan_records(tmp_path, monkeypatch, count):
    records = counted_economic_records(count)
    store = Store(tmp_path / "unused")
    monkeypatch.setattr(store, "apply", lambda operation: operation(records, "origin", NOW))
    additions, selectors = import_events(store, *(event("new-" + str(i)) for i in range(count)))
    assert len(additions) == 2 * count and len(selectors) == count
    assert records.visits <= 4 * count


def test_pending_chain_records_consulted_binding(tmp_path):
    store, _, members = setup_change(tmp_path)
    ident = import_events(
        store, event("pending", replaces=locator("missing"), correction_reason="fix")
    )[0]
    binding = bind_evidence(store, ident, members[0])
    result = compute(store)
    assert "pending_correction" in result.unknown_reasons
    assert reference(binding) in result.inputs


@pytest.mark.parametrize("foreign", [False, True])
def test_portable_explicit_binding_input_requires_member(tmp_path, foreign):
    store, _, members = setup_change(tmp_path)
    ident = import_events(store, event())[0]
    binding = bind_evidence(store, ident, members[0])
    result = compute(store)
    if foreign:
        register_change(store, "repo", "other")
        other = RUN.model_copy(update={"run_id": "other"})
        register_run(store, other, "other")
        other_id = import_events(store, event("other"))[0]
        binding = bind_evidence(store, other_id, other)
    claim = result.model_copy(
        update={
            "record_id": "producer",
            "ledger_id": "producer",
            "inputs": [*result.inputs, reference(binding)],
        }
    )
    before = store.export_bundle()
    bundle = before.model_copy(update={"records": [claim]})
    if foreign:
        with pytest.raises(ContractError):
            store.import_bundle(bundle)
        assert store.export_bundle() == before
    else:
        store.import_bundle(bundle)
        assert claim in store.records()


class CountingRuns(list):
    slots = 0

    def __contains__(self, value):
        self.slots += len(self)
        return super().__contains__(value)


@pytest.mark.parametrize("count", [10, 20])
@pytest.mark.parametrize("computed", [False, True])
def test_coverage_and_computed_binding_lookup_work(tmp_path, count, computed):
    from changecost.store import key, validate_graph

    store, _, members = setup_change(tmp_path, runs=count)
    ids = import_events(store, *(event(str(i)) for i in range(count)))
    for run, ident in zip(members, ids, strict=True):
        bind_evidence(store, ident, run)
        add_coverage(store, run, ident)
    result = compute(store) if computed else None
    records = CountingRecords((key(reference(record)), record) for record in store.records())
    declared = CountingRuns(result.runs) if result is not None else CountingRuns()
    if result is not None:
        records[key(reference(result))] = result.model_copy(update={"runs": declared})
    validate_graph(records)
    assert records.visits <= 12 * len(records)
    assert declared.slots <= 4 * count


@pytest.mark.parametrize("reverse", [False, True])
def test_binding_index_does_not_hide_conflicting_rows(tmp_path, reverse):
    from changecost.store import key, validate_graph

    store, _, members = setup_change(tmp_path, runs=2)
    ident = import_events(store, event())[0]
    original = bind_evidence(store, ident, members[0])
    conflicting = original.model_copy(update={"record_id": "conflict", "run": members[1]})
    rows = [*store.records(), conflicting]
    if reverse:
        rows.reverse()
    records = {key(reference(record)): record for record in rows}
    with pytest.raises(ContractError):
        validate_graph(records)


def test_later_foreign_binding_preserves_historical_unbound_inputs(tmp_path):
    from changecost.models import Evidence
    from changecost.operations import common

    store, _, members = setup_change(tmp_path)
    ids = import_events(store, event("target"), event("unbound"))
    bind_evidence(store, ids[0], members[0])
    add_coverage(store, members[0], ids[0])
    plain = Evidence(
        **common("origin", NOW, "plain"),
        provider="synthetic",
        surface="fixture",
        profile="synthetic/v1",
        identity_scope="namespaced",
        source_key="plain",
    )
    store.apply(lambda records, store_id, now: ([plain], None))
    historical = compute(store, "historical")
    assert reference(plain) in historical.inputs and not historical.full_change
    register_change(store, "repo", "foreign")
    other = RUN.model_copy(update={"run_id": "foreign"})
    register_run(store, other, "foreign")
    for ident in (ids[1], plain.record_id):
        bind_evidence(store, ident, other)
    assert compute(store, "historical") == historical
    destination = Store(tmp_path / "destination", clock=lambda: NOW)
    destination.import_bundle(store.export_bundle())
    assert historical in destination.records()


class CountedMembers(set):
    union_entries = 0

    def __or__(self, other):
        self.union_entries += len(self)
        return super().__or__(other)


@pytest.mark.parametrize("count", [10, 20])
def test_outcome_subject_lookup_does_not_copy_members(tmp_path, count):
    from changecost.economic_graph import validate_computed_subject
    from changecost.store import key

    store, _, members = setup_change(tmp_path, runs=count)
    result = compute(store)
    runs = [record for record in store.records() if record.kind == "run"]
    member_keys = CountedMembers(key(reference(run)) for run in runs)
    declared = {tuple(run.model_dump().values()) for run in members}
    outcomes = [
        record
        for record in store.records()
        if record.kind == "outcome" and record.subject.kind == "run"
    ]
    for outcome in outcomes:
        validate_computed_subject(result, outcome, member_keys, declared)
    assert member_keys.union_entries == 0


@pytest.mark.parametrize("subject", ["change", "run", "foreign"])
def test_computed_outcome_subject_membership_controls(tmp_path, subject):
    from changecost.economic_graph import validate_computed_subject
    from changecost.store import key

    store, change, members = setup_change(tmp_path)
    result = compute(store)
    runs = [record for record in store.records() if record.kind == "run"]
    member_keys = {key(reference(run)) for run in runs}
    declared = {tuple(run.model_dump().values()) for run in members}
    selected = reference(change) if subject == "change" else reference(runs[0])
    if subject == "foreign":
        other = register_change(store, "repo", "foreign")
        declare(store, reference(other), LifecycleDeclaration(outcome="abandoned"))
        selected = reference(other)
    outcome = next(
        record
        for record in store.records()
        if record.kind == "outcome" and record.subject == selected
    )
    if subject == "foreign":
        with pytest.raises(ContractError, match="outcome subject"):
            validate_computed_subject(result, outcome, member_keys, declared)
    else:
        validate_computed_subject(result, outcome, member_keys, declared)


@pytest.mark.parametrize("count", [20, 40])
def test_correction_chain_subject_work_is_linear(monkeypatch, count):
    from changecost import economic_graph
    from changecost.models import EconomicInput, EvidenceBinding
    from changecost.normalized import normalized_records
    from changecost.operations import common
    from changecost.store import key

    records = {}
    for i in range(count):
        item = event(str(i))
        if i:
            item.update(replaces=locator(str(i - 1)), correction_reason="correction")
        pair = normalized_records(EconomicInput.model_validate(item), "origin", NOW)
        records.update((key(reference(record)), record) for record in pair)
        binding = EvidenceBinding(
            **common("origin", NOW, f"binding-{i}"), evidence=reference(pair[0]), run=RUN
        )
        records[key(reference(binding))] = binding
    original = economic_graph.validate_chain_subject
    visits = 0

    class CountedBindings(dict):
        def get(self, *args):
            nonlocal visits
            visits += 1
            return super().get(*args)

    def counted(node, edges, events, bindings, *args):
        return original(node, edges, events, CountedBindings(bindings), *args)

    monkeypatch.setattr(economic_graph, "validate_chain_subject", counted)
    economic_graph.correction_graph(records)
    assert visits <= 2 * count


@pytest.mark.parametrize("count", [20, 40])
def test_disjoint_file_overlap_work_is_bounded(monkeypatch, count):
    from changecost import reconciliation
    from changecost.models import EconomicInput
    from changecost.normalized import normalized_records

    rows = []
    for i in range(count):
        point = START + timedelta(seconds=i * 2)
        item = event(
            str(i),
            source={
                **locator(),
                "identity_scope": "file",
                "source_key": None,
                "file_digest": f"{i % 2:064x}",
                "ordinal": i,
            },
            start=point.isoformat(),
            end=point.isoformat(),
        )
        rows.append(normalized_records(EconomicInput.model_validate(item), "origin", NOW)[1])
    original = reconciliation.overlaps
    checks = 0

    def counted(left, right):
        nonlocal checks
        checks += 1
        return original(left, right)

    monkeypatch.setattr(reconciliation, "overlaps", counted)
    assert not reconciliation.ambiguous_file_overlap(rows)
    assert checks <= count


@pytest.mark.parametrize("bound", [False, True])
def test_repository_unknown_amount_reason(tmp_path, bound):
    from changecost.reconciliation import repository_report

    store, _, members = setup_change(tmp_path)
    ident = import_events(store, event(amount=None))[0]
    if bound:
        bind_evidence(store, ident, members[0])
    report = repository_report(store, scope())
    bucket = report["bound" if bound else "unbound"]
    assert bucket[0]["amount"] is None and bucket[0]["unknown_count"] == 1
    assert "unknown_amount" in report["unknown_reasons"]


@pytest.mark.parametrize("subject", ["unbound", "local", "foreign"])
def test_repository_plain_evidence_uncertainty(tmp_path, subject):
    from changecost.models import Evidence
    from changecost.operations import common
    from changecost.reconciliation import repository_report

    store, _, members = setup_change(tmp_path)
    plain = Evidence(
        **common("origin", NOW, "plain"),
        provider="synthetic",
        surface="fixture",
        profile="synthetic/v1",
        identity_scope="namespaced",
        source_key="plain",
    )
    store.apply(lambda records, store_id, now: ([plain], None))
    if subject != "unbound":
        run = members[0]
        if subject == "foreign":
            register_change(store, "elsewhere", "other")
            run = RUN.model_copy(update={"repository_id": "elsewhere"})
            register_run(store, run, "other")
        bind_evidence(store, plain.record_id, run)
    before = store.export_bundle()
    report = repository_report(store, scope())
    assert ("missing_economic_evidence" in report["unknown_reasons"]) == (subject != "foreign")
    assert any(e["reference"] == reference(plain).model_dump() for e in report["unresolved"]) == (
        subject != "foreign"
    )
    assert all(s["amount"] is None for s in [*report["bound"], *report["unbound"]])
    assert store.export_bundle() == before


@pytest.mark.parametrize("count,expected", [(5, "2.00"), (10, "4.00"), (20, "8.00")])
def test_computation_coverage_record_work_is_bounded(tmp_path, count, expected):
    from changecost.models import Subtotal
    from changecost.reconciliation import computation_details
    from changecost.store import key

    store, change, members = setup_change(tmp_path, runs=count)
    ids = import_events(store, *(event(str(i)) for i in range(count)))
    for run, ident in zip(members, ids, strict=True):
        bind_evidence(store, ident, run)
        add_coverage(store, run, ident)
    records = CountingRecords((key(reference(record)), record) for record in store.records())
    details = computation_details(records, change, scope())
    totals = details["subtotals"]
    assert isinstance(totals, list) and isinstance(totals[0], Subtotal)
    assert details["full_change"] and totals[0].amount == expected
    assert records.visits <= 12 * len(records)


@pytest.mark.parametrize("count", [20, 40])
def test_cutoff_pruning_dependency_work_is_bounded(monkeypatch, count):
    import sqlite3

    from changecost import reconciliation
    from changecost.models import Cutoff

    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE records (kind,id,available_at,sequence)")
    refs = [("outcome", str(i)) for i in range(count)]
    connection.executemany(
        "INSERT INTO records VALUES (?,?,?,?)", [(k, i, NOW.isoformat(), 1) for k, i in refs]
    )
    checks = 0

    class CountedDependencies(set):
        def __le__(self, other):
            nonlocal checks
            checks += 1
            return super().__le__(other)

        def __iter__(self):
            nonlocal checks
            checks += len(self)
            return super().__iter__()

    graph = {
        ref: CountedDependencies([refs[i + 1]] if i + 1 < count else [])
        for i, ref in enumerate(refs)
    }
    monkeypatch.setattr(
        reconciliation, "read_records", lambda conn: dict(zip(refs, range(count), strict=True))
    )
    monkeypatch.setattr(reconciliation, "validate_graph", lambda records: graph)
    monkeypatch.setattr(
        reconciliation, "available", lambda record, obs, cutoff: record != count - 1
    )
    try:
        assert (
            reconciliation.snapshot_records(
                connection, Cutoff(store_id="origin", at=NOW, sequence=1)
            )
            == {}
        )
    finally:
        connection.close()
    assert checks <= 3 * count


@pytest.mark.parametrize("count", [5, 10])
def test_inspection_uses_one_consistent_transaction(tmp_path, monkeypatch, count):
    from changecost.reconciliation import inspect_computation

    store, _, _ = setup_change(tmp_path, runs=count)
    result = compute(store)
    original = store.connect
    connections = 0

    def counted(*args, **kwargs):
        nonlocal connections
        connections += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(store, "connect", counted)
    assert inspect_computation(store, result)["replay_eligibility"] == "inputs_available"
    assert connections == 1


@pytest.mark.parametrize("count", [10, 20])
def test_coverage_does_not_rescan_global_events_per_run(tmp_path, monkeypatch, count):
    from changecost import reconciliation
    from changecost.store import key

    store, change, members = setup_change(tmp_path, runs=count)
    ids = import_events(store, *(event(str(i)) for i in range(count)))
    for run, ident in zip(members, ids, strict=True):
        bind_evidence(store, ident, run)
        add_coverage(store, run, ident)
    records = {key(reference(record)): record for record in store.records()}
    original = reconciliation.select
    visits = 0

    class CountedEvents(list):
        def __iter__(self):
            nonlocal visits
            visits += len(self)
            return super().__iter__()

    def counted(*args, **kwargs):
        selection = original(*args, **kwargs)
        selection.effective = CountedEvents(selection.effective)
        selection.selected = CountedEvents(selection.selected)
        return selection

    monkeypatch.setattr(reconciliation, "select", counted)
    assert reconciliation.computation_details(records, change, scope())["full_change"]
    assert visits <= 6 * count


@pytest.mark.parametrize("reverse", [False, True])
def test_coverage_index_uses_revision_leaves_and_complete_run_refs(tmp_path, reverse):
    from changecost.coverage import CoverageIndex
    from changecost.operations import latest
    from changecost.store import key, run_key

    store, change, members = setup_change(tmp_path)
    run = next(record for record in store.records() if record.kind == "run")
    declare(
        store,
        reference(run),
        LifecycleDeclaration(
            outcome="failed",
            end=NOW - timedelta(minutes=1),
            correct_outcome=True,
            correct_interval=True,
            reason="corrected",
        ),
    )
    declare(
        store,
        reference(change),
        LifecycleDeclaration(outcome="abandoned", correct_outcome=True, reason="corrected"),
    )
    register_change(store, "other-repo", "other")
    foreign = RUN.model_copy(update={"repository_id": "other-repo", "run_id": members[0].run_id})
    foreign_run = register_run(store, foreign, "other", work_start=START)
    declare(store, reference(foreign_run), LifecycleDeclaration(outcome="cancelled", end=START))
    rows = store.records()
    if reverse:
        rows.reverse()
    records = {key(reference(record)): record for record in rows}
    index = CoverageIndex(records)
    assert index.outcomes[key(reference(run))] == latest(records, "outcome", key(reference(run)))
    assert index.outcomes[key(reference(change))].outcome == "abandoned"
    assert index.intervals[run_key(members[0])].end == NOW - timedelta(minutes=1)
    assert index.intervals[run_key(foreign)].end == START
    assert index.runs[run_key(foreign)] == foreign_run


@pytest.mark.parametrize("field", ["sequence", "available_at", "recorded_at", "effective_at"])
def test_cutoff_snapshot_keeps_all_availability_boundaries(tmp_path, field):
    from changecost.models import Cutoff, Observation
    from changecost.store import available

    store, change, _ = setup_change(tmp_path)
    cutoff = Cutoff(store_id="origin", at=NOW, sequence=1)
    observation = Observation(
        reference=reference(change), store_id="origin", available_at=NOW, sequence=1
    )
    assert available(change, observation, cutoff)
    if field in {"recorded_at", "effective_at"}:
        change = change.model_copy(update={field: NOW + timedelta(microseconds=1)})
    else:
        observation = observation.model_copy(
            update={field: 2 if field == "sequence" else NOW + timedelta(microseconds=1)}
        )
    assert not available(change, observation, cutoff)


@pytest.mark.parametrize("count", [10, 20])
@pytest.mark.parametrize(
    "layout, measured",
    [("points", "start"), ("shared_components", "start"), ("shared_components", "evidence")],
)
def test_coverage_assertion_work_tracks_declared_inputs(
    tmp_path, monkeypatch, count, layout, measured
):
    from changecost.coverage import CoverageIndex, event_coverage_reasons
    from changecost.models import EconomicEvidence
    from changecost.reconciliation import select
    from changecost.store import key, run_key, validate_graph

    store, _, members = setup_change(tmp_path)
    items = [event(str(i)) for i in range(count)]
    if layout == "shared_components":
        items = [event("shared", component_key=f"charge{i}") for i in range(count - 1)]
        items.append(event("missing"))
    ids = import_events(store, *items)
    for ident in ids:
        bind_evidence(store, ident, members[0])
    for i in range(count):
        add_coverage(store, members[0], ids[i] if layout == "points" else ids[0])
    records = {key(reference(record)): record for record in store.records()}
    validate_graph(records)
    index = CoverageIndex(records)
    selected = sorted(
        select(records, scope()).selected, key=lambda e: e.evidence.record_id != ids[0]
    )
    original = EconomicEvidence.__getattribute__
    visits = {"start": 0, "evidence": 0}

    def counted(self, name):
        if name in visits:
            visits[name] += 1
        return original(self, name)

    monkeypatch.setattr(EconomicEvidence, "__getattribute__", counted)
    refs = set()
    reasons = event_coverage_reasons(
        index, members[0], index.intervals[run_key(members[0])], selected, scope(), refs
    )
    assert "missing_supported_coverage" in reasons
    assert ("unsupported_source_policy" in reasons) == (layout == "shared_components")
    assert refs == {key(reference(c)) for c in index.coverage[run_key(members[0])]}
    assert visits[measured] <= 2 * count


@pytest.mark.parametrize("complete_assertion", [False, True])
def test_coverage_requires_one_assertion_to_cover_selected_group(tmp_path, complete_assertion):
    from changecost.models import RecordRef

    store, _, members = setup_change(tmp_path)
    ids = import_events(store, event("one"), event("two"))
    assertion = None
    for ident in ids:
        bind_evidence(store, ident, members[0])
        assertion = add_coverage(store, members[0], ident)
    assert assertion is not None
    if complete_assertion:
        combined = assertion.model_copy(
            update={
                "record_id": "complete",
                "evidence": [RecordRef(kind="evidence", record_id=ident) for ident in ids],
            }
        )
        store.apply(lambda records, store_id, now: ([combined], None))
    result = compute(store)
    assert result.full_change == complete_assertion
    assert ("missing_supported_coverage" in result.unknown_reasons) != complete_assertion
    assert result.subtotals[0].amount == "0.80"
