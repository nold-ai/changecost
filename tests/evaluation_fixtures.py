"""Portable declared synthetic timelines for the evaluation acceptance tests."""

import json
from datetime import timedelta

from changecost.models import RunRef
from changecost.operations import LifecycleDeclaration, bind_evidence, declare, register_run
from changecost.store import reference
from tests.test_quotes import peer, setup
from tests.test_reconciliation import NOW, add_coverage, event, import_events, scope


def economic_fixture(tmp_path, count=20, complete=True):
    store = setup(tmp_path)
    for n in range(1, count + 1):
        peer(store, str(n), str(n))
    first = store.export_bundle()
    target = next(r for r in first.records if r.kind == "change" and r.change_id == "target")
    forecast_at = NOW + timedelta(seconds=1)
    start = NOW + timedelta(seconds=2)
    end = NOW + timedelta(seconds=3)
    store.clock = lambda: end
    run = register_run(
        store,
        RunRef(repository_id="repo", provider="synthetic", surface="fixture", run_id="target"),
        "target",
        work_start=start,
    )
    declare(store, reference(run), LifecycleDeclaration(start=start, end=end, outcome="succeeded"))
    evidence = import_events(
        store, event("truth", "15", start=start.isoformat(), end=start.isoformat())
    )[0]
    bind_evidence(store, evidence, run.ref)
    if complete:
        add_coverage(store, run.ref, evidence, start=start, end=end)
    declare(store, reference(target), LifecycleDeclaration(outcome="accepted"))
    bundle = store.export_bundle()
    initial_refs = [reference(r).model_dump() for r in first.records]
    initial_keys = {(r.kind, r.record_id) for r in first.records}
    history = {
        "schema": "changecost/synthetic-evaluation-history-v1",
        "provenance": "synthetic_fixture_only",
        "bundle": bundle.model_dump(mode="json", by_alias=True),
        "deliveries": [
            {"at": NOW.isoformat(), "records": initial_refs},
            {
                "at": end.isoformat(),
                "records": [
                    reference(r).model_dump()
                    for r in bundle.records
                    if (r.kind, r.record_id) not in initial_keys
                ],
            },
        ],
    }
    protocol = {
        "schema": "changecost/evaluation-protocol-v1",
        "version": "synthetic-20261026-v1",
        "provenance": "synthetic_fixture_only",
        "registered_at": (NOW - timedelta(days=2)).isoformat(),
        "economic_scope": scope().model_dump(mode="json"),
        "economic_minimum": 20,
        "minimum_independent_truth": 1,
        "formula": "exact-errors-wilson95-scenario-median/v1",
        "methods": ["repository", "dimensional", "transfer", "rehearsal"],
        "cases": [
            {
                "id": "target",
                "change": reference(target).model_dump(),
                "forecast_at": forecast_at.isoformat(),
                "truth_at": (end + timedelta(seconds=1)).isoformat(),
                "updates": [],
            }
        ],
        "observation_at": (end + timedelta(seconds=1)).isoformat(),
        "source_gaps": ["native_truth_unapproved", "cursor_money_unverified"],
    }
    return history, protocol


def write_inputs(tmp_path, history, protocol):
    history_path, protocol_path = tmp_path / "history.json", tmp_path / "protocol.json"
    history_path.write_text(json.dumps(history))
    protocol_path.write_text(json.dumps(protocol))
    return history_path, protocol_path


def portable_timeline(store) -> dict:
    bundle = store.export_bundle()
    deliveries = {}
    for observation in bundle.observations:
        if observation.store_id == bundle.source.store_id:
            deliveries.setdefault((observation.available_at, observation.sequence), []).append(
                observation.reference.model_dump()
            )
    return dict(
        schema="changecost/synthetic-evaluation-history-v1",
        provenance="synthetic_fixture_only",
        bundle=bundle.model_dump(mode="json", by_alias=True),
        deliveries=[
            dict(at=at.isoformat(), records=refs) for (at, _), refs in sorted(deliveries.items())
        ],
    )


def adaptive_fixture(
    tmp_path,
    *,
    peers=("1", "3"),
    actual="2",
    complete=True,
    bridge=False,
    rehearsal=None,
    unknown=False,
):
    from changecost.models import Quantity, Rehearsal
    from tests.test_demand import COMP, World, make_bridge, registered_policy

    world = World(tmp_path / "adaptive-source")
    for index, value in enumerate(peers):
        world.peer(f"peer-{index}", [value], scope_key=f"independent-{index}")
    if bridge:
        make_bridge(world)
    world.tick()
    policy = registered_policy(world)
    world.tick()
    options = {}
    if rehearsal is not None:
        options["rehearsal"] = Rehearsal(
            method="read_only_assessment",
            budget=Quantity(component=COMP, amount=rehearsal),
            overhead=Quantity(component=COMP, amount=rehearsal),
        )
    assessment = world.assess(world.change, "evaluation-assessment")
    rehearsal_assessment = (
        world.assess(world.change, "rehearsal-assessment", **options)
        if rehearsal is not None
        else None
    )
    eco = world.ecosystem("unknown", None) if unknown else world.eco
    world.tick()
    forecast_at = world.time
    world.tick()
    world.peer("target", [actual], complete=complete, scope_key="same-task")
    world.tick()
    truth_at = world.time
    history = portable_timeline(world.store)
    protocol: dict = dict(
        schema="changecost/evaluation-protocol-v1",
        version="synthetic-20261026-v1",
        provenance="synthetic_fixture_only",
        registered_at=(NOW - timedelta(days=2)).isoformat(),
        economic_scope=scope().model_dump(mode="json"),
        economic_minimum=20,
        minimum_independent_truth=1,
        formula="exact-errors-wilson95-scenario-median/v1",
        methods=["repository", "dimensional", "transfer", "rehearsal"],
        cases=[
            dict(
                id="target",
                change=reference(world.change).model_dump(),
                forecast_at=forecast_at.isoformat(),
                truth_at=truth_at.isoformat(),
                adaptive=dict(
                    assessment=reference(assessment).model_dump(),
                    ecosystem=reference(eco).model_dump(),
                    policy=reference(policy).model_dump(),
                ),
                updates=[],
            )
        ],
        observation_at=truth_at.isoformat(),
        source_gaps=["native_truth_unapproved"],
    )
    if rehearsal_assessment is not None:
        protocol["cases"][0]["adaptive"]["rehearsal_assessment"] = reference(
            rehearsal_assessment
        ).model_dump()
    return history, protocol, world
