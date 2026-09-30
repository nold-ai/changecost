"""Closed synthetic coverage policy; producer labels never certify real sources."""

from changecost.economic_graph import economic_identity
from changecost.models import Evidence, EvidenceBinding, Run, RunBinding, SourceCoverage
from changecost.operations import latest
from changecost.store import key, reference


def policy_identity(scope) -> bool:
    return scope.economic.model_dump() == dict(
        economic_kind="monetary", unit="USD", basis="billed", currency="USD"
    )


def supported_event(event) -> bool:
    source = event.source
    return (
        source.provider,
        source.surface,
        source.profile,
        source.namespace,
        event.component_key,
        event.series,
    ) == ("synthetic", "fixture", "synthetic/v1", "opaque", "charge", "usage")


def supports(coverage, run, interval, events, scope) -> bool:
    if (
        coverage.run,
        coverage.provider,
        coverage.surface,
        coverage.profile,
        coverage.namespace,
        coverage.component_key,
        coverage.policy_version,
    ) != (run, "synthetic", "fixture", "synthetic/v1", "opaque", "charge", "synthetic/v1"):
        return False
    if not coverage.final or coverage.economic != scope.economic:
        return False
    if coverage.start > interval.start or coverage.end < interval.end:
        return False
    # Start-inclusive/end-exclusive source windows must affirmatively cover point endpoints.
    if any(e.start == e.end and not coverage.start <= e.start < coverage.end for e in events):
        return False
    evidence = {key(ref) for ref in coverage.evidence}
    return bool(events) and all(key(e.evidence) in evidence for e in events)


def assess_run(records, run, selection, selected, scope):
    reasons, refs = set(), set()
    run_record = next(r for r in records.values() if isinstance(r, Run) and r.ref == run)
    refs.add(key(reference(run_record)))
    outcome = latest(records, "outcome", key(reference(run_record)))
    interval = latest(records, "interval", tuple(run.model_dump().values()))
    refs.update(lifecycle_refs(outcome, interval))
    if outcome is None:
        reasons.add("open_run")
    if interval is None or missing_bounds(interval):
        reasons.add("missing_work_bounds")
        return reasons, refs
    all_events = [e for e in selection.effective if selection.runs[key(reference(e))] == run]
    if any(e.start < interval.start or e.end > interval.end for e in all_events):
        reasons.add("contradicted_work_bounds")
    events = [e for e in selected if selection.runs[key(reference(e))] == run]
    reasons.update(event_coverage_reasons(records, run, interval, events, scope, refs))
    return reasons, refs


def event_coverage_reasons(records, run, interval, events, scope, refs):
    reasons = set()
    if not events:
        reasons.add("missing_economic_evidence")
    if not policy_identity(scope) or (run.provider, run.surface) != ("synthetic", "fixture"):
        reasons.add("unknown_source_applicability")
    if any(not supported_event(e) for e in events):
        reasons.add("unsupported_source_policy")
    coverage = [r for r in records.values() if isinstance(r, SourceCoverage) and r.run == run]
    refs.update(key(reference(r)) for r in coverage)
    if not any(supports(c, run, interval, events, scope) for c in coverage):
        reasons.add("missing_supported_coverage")
    if partial_scope(scope, interval):
        reasons.add("partial_change_scope")
    return reasons


def assess_coverage(records, change, members, selection, selected, scope):
    reasons, refs = set(), set()
    outcome = latest(records, "outcome", key(reference(change)))
    if outcome is None:
        reasons.add("open_change")
    else:
        refs.add(key(reference(outcome)))
    if not members:
        reasons.add("no_linked_runs")
    for run in members:
        run_reasons, run_refs = assess_run(records, run, selection, selected, scope)
        reasons.update(run_reasons)
        refs.update(run_refs)
    refs.update(
        key(reference(r))
        for r in records.values()
        if isinstance(r, RunBinding) and r.change == reference(change)
    )
    if any(selection.runs[key(reference(e))] is None for e in selection.selected):
        reasons.add("relevant_unbound_evidence")
    missing = unpriced_evidence(records, members)
    if missing:
        reasons.add("missing_economic_evidence")
        refs.update(missing)
    if any(economic_identity(e.component) != scope.economic for e in selected):
        reasons.add("unresolved_economic_identity")
    return reasons, refs


def partial_scope(scope, interval) -> bool:
    return scope.start is not None and (scope.start > interval.start or scope.end < interval.end)


def missing_bounds(interval) -> bool:
    return interval is None or interval.start is None or interval.end is None


def lifecycle_refs(*records) -> set:
    return {key(reference(record)) for record in records if record is not None}


def unpriced_evidence(records, members) -> set:
    refs = set()
    bindings = {key(r.evidence): r for r in records.values() if isinstance(r, EvidenceBinding)}
    economics = {key(r.evidence) for r in records.values() if r.kind == "economic_evidence"}
    for record in records.values():
        if not isinstance(record, Evidence) or key(reference(record)) in economics:
            continue
        binding = bindings.get(key(reference(record)))
        if binding is None or binding.run in members:
            refs.add(key(reference(record)))
    return refs
