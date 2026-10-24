from datetime import UTC, datetime

import pytest

from changecost.models import Bundle, Evidence, RecordRef, RunRef
from changecost.operations import bind_evidence, common, register_change, register_run
from changecost.serialization import ContractError, dumps_bundle, loads_bundle
from changecost.store import Store, reference

NOW = datetime(2026, 10, 24, tzinfo=UTC)


def native(record_id="fact", **updates):
    from changecost.store import ADAPTER

    values = dict(
        **common("origin", NOW, record_id),
        kind="native_usage",
        repository_id="repo",
        evidence=RecordRef(kind="evidence", record_id="event"),
        mapping_revision="mapping",
        producer={"engine_version": "version", "client_surface": "desktop-coding"},
        first_acquisition_digest="a" * 64,
        first_admission={"profile_digest": "b" * 64, "approval_digest": "c" * 64},
        event_identity="d" * 64,
        source_category="total_tokens",
        accounting_scope="request",
        quantity=0,
        interval={"state": "unknown"},
        ownership={"state": "unknown"},
    )
    values.update(updates)
    return ADAPTER.validate_python(values)


def evidence():
    return Evidence(
        **common("origin", NOW, "event"),
        provider="Codex",
        surface="desktop-coding",
        profile="profile",
        identity_scope="namespaced",
        source_key="d" * 64,
    )


def test_native_roundtrip_backup_and_availability(tmp_path):
    store = Store(tmp_path / "db", clock=lambda: NOW)
    fact = native()
    store.apply(lambda records, sid, now: ([evidence(), fact], None))
    before = store.export_bundle()
    store.import_bundle(loads_bundle(dumps_bundle(before)))
    assert store.export_bundle() == before
    restored = Store(tmp_path / "portable", clock=lambda: NOW)
    restored.import_bundle(before)
    assert restored.records() == store.records()
    store.backup(tmp_path / "backup")
    assert Store(tmp_path / "backup", clock=lambda: NOW).export_bundle() == before
    assert fact.quantity == 0
    assert native(quantity=None).quantity is None
    assert set(r.kind for r in before.records) == {"native_usage", "evidence"}


@pytest.mark.parametrize(
    "quantity",
    [-1, True, 1.5, "1", 10**4096],
    ids=["negative", "bool", "fraction", "string", "digits"],
)
def test_native_exact_quantity(quantity):
    with pytest.raises(ValueError):
        native(quantity=quantity)


def test_native_corrections_and_atomic_graph_rejection(tmp_path):
    store = Store(tmp_path / "db", clock=lambda: NOW)
    first = native()
    second = native("revision", quantity=2, previous=reference(first), reason="correction")
    store.apply(lambda records, sid, now: ([evidence(), first, second], None))
    before = store.export_bundle()
    bad = native("fork", previous=reference(first), reason="correction")
    with pytest.raises(ContractError, match="fork"):
        store.apply(lambda records, sid, now: ([bad], None))
    assert store.export_bundle() == before
    mismatch = native(
        "wrong", source_category="input_tokens", previous=reference(second), reason="x"
    )
    with pytest.raises(ContractError, match="subject"):
        store.apply(lambda records, sid, now: ([mismatch], None))
    cycle = native("cycle", previous=RecordRef(kind="native_usage", record_id="cycle"), reason="x")
    with pytest.raises(ContractError):
        store.apply(lambda records, sid, now: ([cycle], None))
    assert store.export_bundle() == before


def test_native_repository_binding_and_duplicate_root(tmp_path):
    store = Store(tmp_path / "db", clock=lambda: NOW)
    store.apply(lambda records, sid, now: ([evidence(), native()], None))
    register_change(store, "foreign", "change")
    run = RunRef(repository_id="foreign", provider="Codex", surface="desktop-coding", run_id="r")
    register_run(store, run, "change")
    before = store.export_bundle()
    with pytest.raises(ContractError, match="repository"):
        bind_evidence(store, "event", run)
    with pytest.raises(ContractError):
        store.apply(lambda records, sid, now: ([native("duplicate")], None))
    assert store.export_bundle() == before


def test_old_bundle_still_reads():
    bundle = Bundle.model_validate(
        dict(source={"store_id": "old", "at": NOW, "sequence": 0}, records=[])
    )
    assert loads_bundle(dumps_bundle(bundle)) == bundle


def test_native_event_cannot_change_producer_to_mint_root(tmp_path):
    store = Store(tmp_path / "db", clock=lambda: NOW)
    store.apply(lambda records, sid, now: ([evidence(), native()], None))
    before = store.export_bundle()
    changed = native(
        "different", producer={"engine_version": "other", "client_surface": "desktop-coding"}
    )
    with pytest.raises(ContractError):
        store.apply(lambda records, sid, now: ([changed], None))
    assert store.export_bundle() == before


@pytest.mark.parametrize(
    "field", ["thread", "turn", "session", "root_turn", "header_parent_thread"]
)
def test_native_event_lineage_consistent_across_categories(tmp_path, field):
    store = Store(tmp_path / "db", clock=lambda: NOW)
    store.apply(lambda records, sid, now: ([evidence(), native()], None))
    before = store.export_bundle()
    ownership = {"state": "unknown", field: "f" * 64}
    changed = native("different-category", source_category="input_tokens", ownership=ownership)
    with pytest.raises(ContractError):
        store.apply(lambda records, sid, now: ([changed], None))
    assert store.export_bundle() == before
