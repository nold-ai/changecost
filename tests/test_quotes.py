"""Spec-derived synthetic Quote computation and historical replay acceptance."""

from datetime import timedelta
from decimal import localcontext

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
from changecost.store import Store, reference
from tests.test_reconciliation import NOW, START, add_coverage, event, import_events, scope


def peer(store, name, value, complete=True, **features):
    change = register_change(store, "repo", name, **features)
    run = register_run(
        store,
        RunRef(repository_id="repo", provider="synthetic", surface="fixture", run_id=name),
        name,
    )
    declare(store, reference(run), LifecycleDeclaration(start=START, end=NOW, outcome="succeeded"))
    ids = import_events(store, event(name, value, start=START.isoformat(), end=START.isoformat()))
    bind_evidence(store, ids[0], run.ref)
    if complete:
        add_coverage(store, run.ref, ids[0], start=START, end=NOW)
    declare(store, reference(change), LifecycleDeclaration(outcome="accepted"))
    return change


def setup(tmp_path):
    store = Store(tmp_path / "db", clock=lambda: NOW)
    register_change(store, "repo", "target")
    return store


def quote(store, operation="quote", minimum=20):
    from changecost.quotes import compute_quote

    return compute_quote(store, "target", scope(), operation, minimum)


def test_exact_quantiles_and_replay(tmp_path):
    from changecost.quotes import inspect_quote

    store = setup(tmp_path)
    for n in reversed(range(1, 21)):
        peer(store, str(n), str(n))
    with localcontext() as context:
        context.prec = 2
        result = quote(store)
    assert (result.p50.amount, result.p90.amount, result.sample_count) == ("10", "18", 20)
    assert result.estimation is not None
    assert result.estimation.synthetic
    assert result.cohort == "repository"
    before = store.export_bundle()
    assert inspect_quote(store, result)["economic_validation"] == "reproduced"
    assert store.export_bundle() == before
    peer(store, "late", "999")
    assert quote(store) == result
    assert inspect_quote(store, result)["economic_validation"] == "reproduced"
    assert not any(r.kind == "computed_settlement" for r in store.records())


def test_partial_zero_target_and_minimum(tmp_path):
    store = setup(tmp_path)
    peer(store, "zero", "0")
    peer(store, "gap", "7", False)
    result = quote(store, minimum=2)
    assert result.state == "unpriced" and result.p50.amount is None
    result = quote(store, "one", 1)
    assert result.p50.amount == "0" and result.sample_count == 1
    assert result.estimation is not None
    assert any(e.reason == "missing_supported_coverage" for e in result.estimation.exclusions)
    for invalid in (0, True, 1.5):
        before = store.export_bundle()
        with pytest.raises((ValueError, ContractError)):
            quote(store, str(invalid), invalid)  # type: ignore[arg-type]
        assert store.export_bundle() == before


def test_import_backup_and_kind_conflict(tmp_path):
    from changecost.quotes import inspect_quote
    from changecost.reconciliation import compute_settlement

    store = setup(tmp_path)
    peer(store, "peer", "1")
    result = quote(store, minimum=1)
    with pytest.raises(ContractError):
        compute_settlement(store, "target", scope(), "quote")
    compute_settlement(store, "target", scope(), "settle")
    with pytest.raises(ContractError):
        quote(store, "settle", 1)
    foreign = Store(tmp_path / "foreign", clock=lambda: NOW + timedelta(days=1))
    foreign.import_bundle(loads_bundle(dumps_bundle(store.export_bundle())))
    assert inspect_quote(foreign, result)["local_computation"] is False
    assert inspect_quote(foreign, result)["replay_eligibility"] == "replay_unavailable"
    store.backup(tmp_path / "backup")
    assert (
        inspect_quote(Store(tmp_path / "backup", clock=lambda: NOW), result)["economic_validation"]
        == "reproduced"
    )


def test_atomic_failure_and_missing_store(tmp_path, monkeypatch):
    store = Store(tmp_path / "missing", clock=lambda: NOW)
    with pytest.raises(ContractError):
        quote(store)
    assert not store.path.exists()
    store = setup(tmp_path)
    before = store.export_bundle()

    def fail(connection):
        raise ValueError("injected")

    monkeypatch.setattr(store, "commit", fail)
    with pytest.raises(ContractError):
        quote(store)
    assert store.export_bundle() == before


def test_normalized_features_use_narrow_cohort(tmp_path):
    store = setup(tmp_path)
    # Separate target registration creates supported immutable features before work.
    register_change(
        store,
        "repo",
        "featured",
        change_shape="bugfix",
        trajectory="single-pass",
        execution_profile="cursor-cli",
    )
    peer(
        store,
        "match",
        "2",
        change_shape=" BugFix ",
        trajectory="single-pass",
        execution_profile="cursor-cli",
    )
    from changecost.quotes import compute_quote

    result = compute_quote(store, "featured", scope(), "narrow", 1)
    # Fixture work predates registration, so narrow matching must reject it.
    assert result.cohort == "repository"
    assert result.estimation is not None
    assert any(e.reason == "missing_or_late_peer_features" for e in result.estimation.exclusions)


def test_typed_id_collision_cannot_forge_settlement_authority(tmp_path):
    from changecost.quotes import inspect_quote
    from changecost.reconciliation import compute_settlement, inspect_computation

    store = setup(tmp_path)
    result = quote(store)
    foreign = Store(tmp_path / "foreign", clock=lambda: NOW)
    register_change(foreign, "repo", "target")
    claim = compute_settlement(foreign, "target", scope(), "foreign")
    # Match the local target reference while retaining a distinct typed record claim.
    claim = claim.model_copy(update={"record_id": result.record_id, "change": result.change})
    from changecost.models import Bundle

    store.import_bundle(Bundle(source=foreign.snapshot(), records=[claim]))
    assert inspect_computation(store, claim)["local_computation"] is False
    assert inspect_quote(store, result)["local_computation"] is True
    own = compute_settlement(store, "target", scope(), "own")
    assert own.previous is None
    forged_quote = result.model_copy(update={"record_id": own.record_id})
    store.import_bundle(Bundle(source=store.snapshot(), records=[forged_quote]))
    assert inspect_quote(store, forged_quote)["local_computation"] is False


def test_signed_amounts_and_multiple_attempts(tmp_path):
    from changecost.quotes import compute_quote

    store = setup(tmp_path)
    change = peer(store, "retry", "-2")
    # Reopen explicitly, then add another attempt and reclose abandoned.
    run = additional_run(store, change, "retry-2")
    declare(store, reference(run), LifecycleDeclaration(start=START, end=NOW, outcome="cancelled"))
    evidence = import_events(store, event("retry-2", "3"))[0]
    bind_evidence(store, evidence, run.ref)
    add_coverage(store, run.ref, evidence)
    declare(
        store,
        reference(change),
        LifecycleDeclaration(outcome="abandoned", correct_outcome=True, reason="stop"),
    )
    result = compute_quote(store, "target", scope(), "retry-result", 1)
    assert result.p50.amount == "1" and result.sample_count == 1


def test_current_gap_and_late_correction_replay(tmp_path):
    from changecost.quotes import inspect_quote
    from changecost.reconciliation import compute_settlement

    store = setup(tmp_path)
    change = peer(store, "peer", "2")
    compute_settlement(store, "peer", scope(), "settlement")
    original = quote(store, "before", 1)
    run = additional_run(store, change, "gap")
    declare(store, reference(run), LifecycleDeclaration(start=START, end=NOW, outcome="failed"))
    declare(
        store,
        reference(change),
        LifecycleDeclaration(outcome="accepted", correct_outcome=True, reason="close"),
    )
    current = quote(store, "after", 1)
    assert current.state == "unpriced"
    assert inspect_quote(store, original)["economic_validation"] == "reproduced"


def test_malformed_metadata_rejects_import_atomically(tmp_path):
    from changecost.models import Bundle

    store = setup(tmp_path)
    peer(store, "p", "1")
    result = quote(store, minimum=1)
    payload = result.model_dump(mode="json", by_alias=True)
    payload["record_id"] = "malformed"
    payload["estimation"]["peers"][0]["change"] = {"kind": "change", "record_id": "missing"}
    before = store.export_bundle()
    with pytest.raises((ValueError, ContractError)):
        store.import_bundle(
            Bundle.model_validate({"source": store.snapshot(), "records": [payload]})
        )
    assert store.export_bundle() == before


def test_legacy_and_unsupported_quotes_inspect_without_authority(tmp_path):
    from changecost.models import Bundle
    from changecost.quotes import inspect_quote

    store = setup(tmp_path)
    result = quote(store)
    legacy = result.model_copy(update={"record_id": "legacy", "estimation": None})
    unsupported = result.model_copy(
        update={"record_id": "unsupported", "algorithm_version": "future/v9"}
    )
    store.import_bundle(Bundle(source=store.snapshot(), records=[legacy, unsupported]))
    for claim in (legacy, unsupported):
        inspection = inspect_quote(store, claim)
        assert inspection["economic_validation"] == "not_computed"
        assert inspection["local_computation"] is False
        assert inspection["replay_eligibility"] == "replay_unavailable"


def additional_run(store, change, name):
    from changecost.models import Run
    from changecost.operations import bind_run, common

    def operation(records, store_id, now):
        run = Run(
            **common(store_id, now),
            ref=RunRef(repository_id="repo", provider="synthetic", surface="fixture", run_id=name),
        )
        return [run], run

    run = store.apply(operation)
    bind_run(store, run.ref, reference(change))
    return run


@pytest.mark.parametrize(
    "profile,expected", [("cursor-cli", "profile"), ("copilot-cli", "shape_trajectory")]
)
def test_supported_pre_run_features_and_ordered_backoff(tmp_path, profile, expected):
    from changecost.quotes import compute_quote

    now = [NOW]
    store = Store(tmp_path / "db", clock=lambda: now[0])
    features = dict(change_shape="bugfix", trajectory="single-pass", execution_profile="cursor-cli")
    register_change(store, "repo", "target", **features)
    candidate = register_change(store, "repo", "peer", **{**features, "execution_profile": profile})
    now[0] += timedelta(seconds=1)
    run = register_run(
        store,
        RunRef(repository_id="repo", provider="synthetic", surface="fixture", run_id="peer"),
        "peer",
        work_start=now[0],
    )
    start = now[0]
    now[0] += timedelta(seconds=1)
    declare(store, reference(run), LifecycleDeclaration(end=now[0], outcome="succeeded"))
    evidence = import_events(
        store, event("peer", "-0.0001", start=start.isoformat(), end=start.isoformat())
    )[0]
    bind_evidence(store, evidence, run.ref)
    add_coverage(store, run.ref, evidence, start=start, end=now[0])
    declare(store, reference(candidate), LifecycleDeclaration(outcome="abandoned"))
    result = compute_quote(store, "target", scope(), "q", 1)
    assert result.cohort == expected and result.p50.amount == "-0.0001"
    assert result.estimation is not None
    assert [c.level for c in result.estimation.cohorts] == [
        "profile",
        "shape_trajectory",
        "repository",
    ]


@pytest.mark.parametrize(
    "changes",
    [
        dict(currency="EUR", unit="EUR"),
        dict(basis="estimated"),
        dict(economic_kind="nonmonetary", unit="credit", currency=None, basis="consumed"),
    ],
)
def test_unsupported_identity_stays_unpriced(tmp_path, changes):
    from changecost.models import EconomicScope
    from changecost.quotes import compute_quote

    store = setup(tmp_path)
    peer(store, "peer", "1")
    economic = {**scope().economic.model_dump(), **changes}
    result = compute_quote(
        store,
        "target",
        EconomicScope.model_validate(dict(repository_id="repo", economic=economic)),
        "other",
        1,
    )
    assert result.state == "unpriced" and result.sample_count == 0


def test_target_excluded_and_permutation_invariant(tmp_path):
    from changecost.quotes import estimate, local_availability
    from changecost.reconciliation import snapshot_records

    store = setup(tmp_path)
    peer(store, "peer", "1")
    peer(store, "target", "99")
    result = quote(store, minimum=1)
    assert result.p50.amount == "1" and result.sample_count == 1
    with store.connect(readonly=True) as connection:
        records = snapshot_records(connection, result.cutoff)
        target = records[("change", result.change.record_id)]
        replay = estimate(
            dict(reversed(list(records.items()))),
            target,
            scope(),
            1,
            result.cutoff,
            local_availability(connection),
        )
    excluded = {"record_id"}
    assert replay.model_dump(exclude=excluded) == result.model_dump(exclude=excluded)


def test_quote_metadata_privacy_and_copied_payload_verification(tmp_path):
    from changecost.models import Bundle
    from changecost.quotes import inspect_quote

    store = setup(tmp_path)
    result = quote(store)
    payload = result.model_dump(mode="json", by_alias=True)
    payload["estimation"]["PRIVATE_SENTINEL"] = "private value"
    before = store.export_bundle()
    with pytest.raises(ValueError):
        Bundle.model_validate({"source": store.snapshot(), "records": [payload]})
    # CLI/import diagnostics sanitize Pydantic errors via the public import boundary.
    with pytest.raises(ContractError) as safe:
        store.import_bundle(
            store.export_bundle().model_copy(
                update={
                    "records": [result.model_copy(update={"estimation": payload["estimation"]})]
                }
            )
        )
    assert "PRIVATE_SENTINEL" not in str(safe.value) and "private value" not in str(safe.value)
    assert store.export_bundle() == before
    with pytest.raises(ContractError):
        inspect_quote(store, result.model_copy(update={"reason": "forged"}))


def test_backdated_import_and_future_cutoff(tmp_path):
    from changecost.models import Bundle
    from changecost.quotes import inspect_quote

    store = setup(tmp_path)
    original = quote(store, "before", 1)
    foreign = Store(tmp_path / "foreign", clock=lambda: NOW)
    peer(foreign, "late", "7")
    store.clock = lambda: NOW + timedelta(days=1)
    store.import_bundle(foreign.export_bundle())
    assert quote(store, "after", 1).state == "priced"
    assert inspect_quote(store, original)["economic_validation"] == "reproduced"
    future = original.model_copy(
        update={
            "record_id": "future",
            "cutoff": original.cutoff.model_copy(update={"at": NOW + timedelta(days=2)}),
        }
    )
    store.import_bundle(Bundle(source=store.snapshot(), records=[future]))
    assert inspect_quote(store, future)["replay_eligibility"] == "replay_unavailable"


def prework_peer(store, name="peer"):
    features = dict(change_shape="bugfix", trajectory="single-pass", execution_profile="cursor-cli")
    change = register_change(store, "repo", name, **features)
    now = store.clock()
    run = register_run(
        store,
        RunRef(repository_id="repo", provider="synthetic", surface="fixture", run_id=name),
        name,
    )
    end = now + timedelta(seconds=1)
    store.clock = lambda: end
    declare(store, reference(run), LifecycleDeclaration(start=now, end=end, outcome="succeeded"))
    evidence = import_events(store, event(name, "2", start=now.isoformat(), end=now.isoformat()))[0]
    bind_evidence(store, evidence, run.ref)
    add_coverage(store, run.ref, evidence, start=now, end=end)
    declare(store, reference(change), LifecycleDeclaration(outcome="accepted"))
    return change


@pytest.mark.parametrize("binding", ["direct", "retry", "correction_chain"])
def test_bound_economics_establish_earlier_target_work(tmp_path, binding):
    from changecost.quotes import compute_quote, inspect_quote

    store = Store(tmp_path / "db", clock=lambda: NOW)
    register_change(
        store,
        "repo",
        "target",
        change_shape="bugfix",
        trajectory="single-pass",
        execution_profile="cursor-cli",
    )
    run = register_run(
        store,
        RunRef(repository_id="repo", provider="synthetic", surface="fixture", run_id="target"),
        "target",
    )
    prework_peer(store)
    before = compute_quote(store, "target", scope(), "before-work-known", 1)
    assert before.cohort == "profile"
    if binding == "retry":
        run = register_run(
            store,
            RunRef(repository_id="repo", provider="synthetic", surface="fixture", run_id="retry"),
            "target",
        )
    if binding == "correction_chain":
        from tests.test_reconciliation import locator

        import_events(store, event("earlier", "3"))
        evidence = import_events(
            store,
            event(
                "replacement",
                "3",
                replaces=locator("earlier"),
                correction_reason="corrected",
            ),
        )[0]
    else:
        evidence = import_events(store, event("earlier", "3"))[0]
    bind_evidence(store, evidence, run.ref)
    after = compute_quote(store, "target", scope(), "after-work-known", 1)
    assert after.cohort == "repository"
    assert inspect_quote(store, before)["economic_validation"] == "reproduced"


def test_cutoff_economic_correction_replays_original_peer_amount(tmp_path):
    from changecost.quotes import inspect_quote
    from tests.test_reconciliation import locator

    store = setup(tmp_path)
    peer(store, "peer", "2")
    original = quote(store, "original", 1)
    run = next(r for r in store.records() if r.kind == "run")
    replacement = event("corrected", "4", replaces=locator("peer"), correction_reason="corrected")
    evidence = import_events(store, replacement)[0]
    bind_evidence(store, evidence, run.ref)
    add_coverage(store, run.ref, evidence)
    revised = quote(store, "revised", 1)
    assert revised.p50.amount == "4"
    assert original.p50.amount == "2"
    assert inspect_quote(store, original)["economic_validation"] == "reproduced"


def test_quote_inputs_exclude_unconsulted_foreign_repository_and_import_closure(tmp_path):
    from changecost.models import Bundle
    from changecost.normalized import import_evidence
    from changecost.quotes import inspect_quote

    store = setup(tmp_path)
    peer(store, "peer", "2")
    change = register_change(store, "private-repository", "private-change")
    run = register_run(
        store,
        RunRef(
            repository_id="private-repository",
            provider="synthetic",
            surface="fixture",
            run_id="private-run",
        ),
        "private-change",
    )
    foreign_event: dict = event("private-economic", "999")
    foreign_event["source"]["repository_id"] = "private-repository"
    evidence = import_evidence(
        store,
        dict(
            schema="changecost/normalized-v1",
            repository_id="private-repository",
            batch_id="foreign",
            events=[foreign_event],
        ),
        "private-repository",
    )[0]
    bind_evidence(store, evidence, run.ref)
    foreign = [
        reference(r) for r in store.records() if r.kind in ("change", "run") and r in (change, run)
    ]
    foreign_ids = {
        r.record_id
        for r in store.records()
        if (r.kind == "economic_evidence" and r.source.repository_id == "private-repository")
        or (r.kind == "evidence" and r.record_id == evidence)
    }
    result = quote(store, minimum=1)
    assert not any(r in result.inputs for r in foreign)
    assert not any(r.record_id in foreign_ids for r in result.inputs)
    needed = {(r.kind, r.record_id) for r in result.inputs}
    records = [r for r in store.records() if (r.kind, r.record_id) in needed] + [result]
    destination = Store(tmp_path / "target-only", clock=store.clock)
    destination.import_bundle(Bundle(source=store.snapshot(), records=records))
    assert inspect_quote(destination, result)["local_computation"] is False


def test_quote_inputs_retain_relevant_unbound_and_feature_timing_inputs(tmp_path):
    store = Store(tmp_path / "db", clock=lambda: NOW)
    register_change(
        store,
        "repo",
        "target",
        change_shape="bugfix",
        trajectory="single-pass",
        execution_profile="cursor-cli",
    )
    run = register_run(
        store,
        RunRef(repository_id="repo", provider="synthetic", surface="fixture", run_id="target"),
        "target",
    )
    prework_peer(store)
    timing = import_events(store, event("earlier-target", "3"))[0]
    bind_evidence(store, timing, run.ref)
    unbound = import_events(store, event("relevant-unbound", "5"))[0]
    result = quote(store, minimum=1)
    ids = {r.record_id for r in result.inputs}
    assert timing in ids and unbound in ids
    assert run.record_id in ids
    assert result.estimation is not None
    assert any(e.reason == "relevant_unbound_evidence" for e in result.estimation.exclusions)


def test_quote_inputs_keep_unattributed_raw_evidence_without_guessing_repository(tmp_path):
    from changecost.models import Evidence
    from changecost.operations import common

    store = setup(tmp_path)
    peer(store, "peer", "2")

    def operation(records, store_id, now):
        record = Evidence(
            **common(store_id, now),
            provider="unverified",
            surface="fixture",
            profile="unknown/v1",
            identity_scope="namespaced",
            source_key="unattributed",
        )
        return [record], record

    unknown = store.apply(operation)
    result = quote(store, minimum=1)
    assert reference(unknown) in result.inputs
    assert result.state == "unpriced"


def quote_inspection_claim(tmp_path, claim_kind):
    from changecost.models import Bundle

    store = setup(tmp_path)
    peer(store, "peer", "1")
    original = quote(store, minimum=1)
    claim = original
    if claim_kind == "foreign":
        destination = Store(tmp_path / "destination", clock=lambda: NOW)
        destination.import_bundle(store.export_bundle())
        store = destination
    elif claim_kind in {"legacy", "unsupported"}:
        changes = {"record_id": claim_kind}
        if claim_kind == "legacy":
            changes["estimation"] = None
        else:
            changes["algorithm_version"] = "future/v9"
        claim = original.model_copy(update=changes)
        store.import_bundle(Bundle(source=store.snapshot(), records=[claim]))
    return store, original, claim


def quote_database_snapshot(store):
    with store.connect(readonly=True) as connection:
        return tuple(connection.iterdump())


@pytest.mark.parametrize("claim_kind", ["computed", "legacy", "unsupported", "foreign"])
@pytest.mark.parametrize("by_reference", [False, True])
def test_quote_explanation_rejects_backward_clock_without_mutation(
    tmp_path, claim_kind, by_reference
):
    from changecost.quotes import inspect_quote

    store, original, claim = quote_inspection_claim(tmp_path, claim_kind)
    later = NOW + timedelta(hours=2)
    store.clock = lambda: later
    register_change(store, "repo", "later")
    before = quote_database_snapshot(store)
    record = reference(claim) if by_reference else claim
    store.clock = lambda: NOW + timedelta(hours=1)
    with pytest.raises(ContractError, match="clock moved backwards"):
        store.export_bundle()
    with pytest.raises(ContractError, match="clock moved backwards"):
        inspect_quote(store, record)
    assert quote_database_snapshot(store) == before
    if claim_kind != "foreign":
        assert quote(store, minimum=1) == original
        assert quote_database_snapshot(store) == before
    store.clock = lambda: later
    explanation = inspect_quote(store, record)
    expected = "reproduced" if claim_kind == "computed" else "not_computed"
    assert explanation["economic_validation"] == expected
    assert quote_database_snapshot(store) == before
    store.clock = lambda: later + timedelta(hours=1)
    assert inspect_quote(store, record)["economic_validation"] == expected
    assert quote_database_snapshot(store) == before


def test_quote_explanation_reads_clock_once(tmp_path):
    from changecost.quotes import inspect_quote

    store = setup(tmp_path)
    result = quote(store)
    readings = iter([NOW])
    store.clock = lambda: next(readings)
    assert inspect_quote(store, result)["economic_validation"] == "reproduced"


class CountedQuoteSnapshot(dict):
    """Measure record traversal across the estimator rather than wall-clock timing."""

    def __init__(self, records):
        super().__init__(records)
        self.visits = 0

    def values(self):
        self.visits += len(self)
        return super().values()


def empty_peers(store, count):
    from changecost.models import Change, Features, Outcome
    from changecost.operations import common

    def operation(records, store_id, now):
        additions = []
        for n in range(count):
            change = Change(
                **common(store_id, now),
                repository_id="repo",
                change_id=f"empty-{n}",
                features=Features(captured_at=now, recorded_at=now),
            )
            additions.append(change)
            if n % 2:
                additions.append(
                    Outcome(**common(store_id, now), subject=reference(change), outcome="abandoned")
                )
        return additions, additions

    return store.apply(operation)


def test_zero_attempt_peer_growth_is_bounded_and_diagnostics_preserved(
    tmp_path, monkeypatch, record_property
):
    from changecost import quotes

    original = quotes.estimate
    visits = []

    def measured(records, *arguments):
        counted = CountedQuoteSnapshot(records)
        result = original(counted, *arguments)
        visits.append(counted.visits)
        return result

    monkeypatch.setattr(quotes, "estimate", measured)
    for count in (32, 64, 128):
        store = setup(tmp_path / str(count))
        records = empty_peers(store, count)
        result = quote(store, minimum=1)
        assert result.state == "unpriced" and result.p50.amount is None
        assert result.sample_count == 0 and result.cohort == "repository"
        assert result.estimation is not None
        reasons = {(e.reference.record_id, e.reason) for e in result.estimation.exclusions}
        for change in [r for r in records if r.kind == "change"]:
            assert (change.record_id, "no_linked_runs") in reasons
            assert (change.record_id, "missing_economic_evidence") in reasons
            assert ((change.record_id, "open_change") in reasons) == (
                int(change.change_id.split("-")[1]) % 2 == 0
            )
        assert {(r.kind, r.record_id) for r in records} <= {
            (r.kind, r.record_id) for r in result.inputs
        }
    record_property("record_visits", visits)
    assert visits[1] < 3 * visits[0]
    assert visits[2] < 3 * visits[1]


def test_empty_peer_cache_preserves_mixed_evidence_and_original_history(tmp_path):
    from changecost.models import Evidence
    from changecost.operations import common
    from changecost.quotes import inspect_quote
    from changecost.reconciliation import snapshot_records
    from tests.test_reconciliation import locator

    store = setup(tmp_path)
    peer(store, "complete", "2")
    original = quote(store, "priced", 1)
    assert original.p50.amount == "2"
    unbound = import_events(store, event("unbound", "3"))[0]
    pending = import_events(
        store, event("pending", "7", replaces=locator("not-arrived"), correction_reason="fix")
    )[0]

    def raw_evidence(records, store_id, now):
        raw = Evidence(
            **common(store_id, now),
            provider="unverified",
            surface="fixture",
            profile="unknown/v1",
            identity_scope="namespaced",
            source_key="raw",
        )
        return [raw], raw

    raw = store.apply(raw_evidence)
    foreign = register_change(store, "foreign", "irrelevant")
    baseline = quote(store, "uncertain", 1)
    additions = empty_peers(store, 32)
    result = quote(store, "many-empty", 1)
    assert result.state == baseline.state == "unpriced"
    assert result.sample_count == baseline.sample_count == 0
    inputs = {(r.kind, r.record_id) for r in result.inputs}
    assert {("evidence", unbound), ("evidence", pending), (raw.kind, raw.record_id)} <= inputs
    assert (foreign.kind, foreign.record_id) not in inputs
    assert result.estimation is not None
    assert any(e.reason == "pending_correction" for e in result.estimation.exclusions)
    with store.connect(readonly=True) as connection:
        records = snapshot_records(connection, result.cutoff)
    for candidate in [r for r in additions if r.kind == "change"]:
        assert_empty_peer_diagnostics(records, candidate, result, inputs)
    assert inspect_quote(store, original)["economic_validation"] == "reproduced"
    assert_quote_subset_import(store, result, inputs, tmp_path / "subset")


def assert_empty_peer_diagnostics(records, candidate, result, inputs):
    from changecost.reconciliation import computation_details

    details = computation_details(records, candidate, scope())
    assert {(r.kind, r.record_id) for r in details["inputs"]} <= inputs
    assert result.estimation is not None
    reasons = {
        e.reason for e in result.estimation.exclusions if e.reference == reference(candidate)
    }
    assert reasons == set(details["unknown_reasons"])


def assert_quote_subset_import(store, result, inputs, destination_path):
    from changecost.models import Bundle
    from changecost.quotes import inspect_quote

    subset = Bundle(
        source=store.snapshot(),
        records=[r for r in store.records() if (r.kind, r.record_id) in inputs] + [result],
    )
    destination = Store(destination_path, clock=lambda: NOW)
    destination.import_bundle(loads_bundle(dumps_bundle(subset)))
    assert inspect_quote(destination, result)["local_computation"] is False


def test_empty_peer_cache_replays_prior_full_reconciliation_result(tmp_path, monkeypatch):
    from changecost import quotes
    from changecost.reconciliation import computation_details
    from tests.test_reconciliation import locator

    store = setup(tmp_path)
    empty_peers(store, 32)
    import_events(store, event("unbound", "3"))
    import_events(store, event("pending", "7", replaces=locator("absent"), correction_reason="fix"))

    def full_details(records, candidate, economic_scope, index, cache):
        return computation_details(records, candidate, economic_scope)

    with monkeypatch.context() as previous:
        previous.setattr(quotes, "peer_details", full_details)
        original = quote(store, "full-reconciliation", 1)
    assert quotes.inspect_quote(store, original)["economic_validation"] == "reproduced"
