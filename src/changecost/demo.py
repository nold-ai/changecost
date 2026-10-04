"""Offline synthetic advisory fixture, using public operations and portable coverage."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from changecost.advisory import budget_component, check_record
from changecost.models import (
    Bundle,
    EconomicIdentity,
    EconomicScope,
    RecordRef,
    RunRef,
    SourceCoverage,
)
from changecost.normalized import import_evidence
from changecost.operations import (
    LifecycleDeclaration,
    bind_evidence,
    common,
    declare,
    register_change,
    register_run,
)
from changecost.quotes import compute_quote
from changecost.reconciliation import compute_settlement
from changecost.store import Store, reference

ECONOMIC = dict(economic_kind="monetary", unit="USD", basis="billed", currency="USD")
START = datetime(2026, 9, 29, 9, tzinfo=UTC)
END = datetime(2026, 9, 29, 10, tzinfo=UTC)


def synthetic_peer(store, name, value, outcome="accepted"):
    change = register_change(store, "demo", name)
    run = register_run(
        store,
        RunRef(repository_id="demo", provider="synthetic", surface="fixture", run_id=name),
        name,
    )
    declare(store, reference(run), LifecycleDeclaration(start=START, end=END, outcome="succeeded"))
    event = dict(
        source=dict(
            repository_id="demo",
            provider="synthetic",
            surface="fixture",
            profile="synthetic/v1",
            namespace="opaque",
            identity_scope="namespaced",
            source_key=name,
        ),
        component_key="charge",
        component={**ECONOMIC, "amount": value},
        series="usage",
        lane="delta",
        start=START.isoformat(),
        end=START.isoformat(),
    )
    evidence = import_evidence(
        store,
        dict(
            schema="changecost/normalized-v1", repository_id="demo", batch_id=name, events=[event]
        ),
        "demo",
    )[0]
    bind_evidence(store, evidence, run.ref)
    source = store.export_bundle().source
    coverage = SourceCoverage(
        **common(source.store_id, source.at),
        run=run.ref,
        provider="synthetic",
        surface="fixture",
        profile="synthetic/v1",
        namespace="opaque",
        component_key="charge",
        policy_version="synthetic/v1",
        economic=EconomicIdentity.model_validate(ECONOMIC),
        start=START,
        end=END,
        final=True,
        evidence=[RecordRef(kind="evidence", record_id=evidence)],
    )
    store.import_bundle(Bundle(source=source, records=[coverage]))
    declare(store, reference(change), LifecycleDeclaration(outcome=outcome))


def create_demo(directory: Path):
    directory.mkdir(parents=True, exist_ok=True)
    database = directory / "synthetic.sqlite"
    if database.exists():
        raise ValueError("use a fresh demo directory")
    store = Store(database, clock=lambda: END)
    register_change(store, "demo", "target")
    scope = EconomicScope(repository_id="demo", economic=EconomicIdentity.model_validate(ECONOMIC))
    cold = compute_quote(store, "target", scope, "cold-start", 2)
    synthetic_peer(store, "ten", "10")
    synthetic_peer(store, "eighteen", "18", "abandoned")
    quote = compute_quote(store, "target", scope, "priced-quote", 2)
    settlement = compute_settlement(store, "ten", scope, "settlement")
    artifact = directory / "synthetic-bundle.json"
    artifact.write_text(store.export_bundle().model_dump_json(by_alias=True), encoding="utf-8")
    requests = (
        ("cold-start", cold, None),
        ("local-quote", quote, None),
        ("local-settlement", settlement, None),
        ("portable-claim", quote, artifact),
    )
    for label, record, portable in requests:
        result = check_record(
            store,
            reference(record),
            budget_component("15", "monetary", "USD", "billed", "USD"),
            artifact=portable,
        )
        (directory / f"{label}.json").write_text(
            json.dumps(result, ensure_ascii=True), encoding="utf-8"
        )
    return {"quote": quote.record_id, "settlement": settlement.record_id}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(create_demo(args.directory)))
    except (OSError, ValueError):
        parser.exit(2, "cannot create synthetic demo; use a fresh writable directory\n")


if __name__ == "__main__":
    main()
