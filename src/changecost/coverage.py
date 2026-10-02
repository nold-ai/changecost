"""Closed synthetic coverage policy; producer labels never certify real sources."""

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

from changecost.economic_graph import economic_identity
from changecost.models import (
    Evidence,
    EvidenceBinding,
    Interval,
    Outcome,
    Run,
    RunBinding,
    SourceCoverage,
)
from changecost.store import key, reference, run_key, subject


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


@dataclass(frozen=True)
class CoverageRequirements:
    evidence: set[tuple[str, str]]
    earliest_point: datetime | None
    latest_point: datetime | None
    has_events: bool


def event_requirements(events) -> CoverageRequirements:
    evidence, earliest, latest = set(), None, None
    for event in events:
        evidence.add(key(event.evidence))
        start = event.start
        if start == event.end:
            earliest = start if earliest is None else min(earliest, start)
            latest = start if latest is None else max(latest, start)
    return CoverageRequirements(evidence, earliest, latest, bool(events))


def supports(coverage, run, interval, requirements, scope) -> bool:
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
    if requirements.earliest_point is not None and requirements.earliest_point < coverage.start:
        return False
    if requirements.latest_point is not None and requirements.latest_point >= coverage.end:
        return False
    evidence = {key(ref) for ref in coverage.evidence}
    if len(requirements.evidence) > len(evidence):
        return False
    return requirements.has_events and requirements.evidence <= evidence


class CoverageIndex:
    """One snapshot's full-reference lookups and predecessor-defined lifecycle leaves."""

    def __init__(self, records):
        self.runs, self.outcomes, self.intervals, self.bindings = {}, {}, {}, {}
        self.coverage, self.change_bindings = defaultdict(list), defaultdict(list)
        self.evidence, self.economics = {}, set()
        revisions, predecessors = [], set()
        for record in records.values():
            self.add_record(record, revisions, predecessors)
        for record in revisions:
            if key(reference(record)) not in predecessors:
                target = self.outcomes if isinstance(record, Outcome) else self.intervals
                target[subject(record)] = record

    def add_record(self, record, revisions, predecessors):
        if isinstance(record, Run):
            self.runs[run_key(record.ref)] = record
            return
        if isinstance(record, (Outcome, Interval)):
            revisions.append(record)
            if record.previous is not None:
                predecessors.add(key(record.previous))
            return
        if isinstance(record, SourceCoverage):
            self.coverage[run_key(record.run)].append(record)
            return
        if isinstance(record, RunBinding):
            self.change_bindings[key(record.change)].append(record)
            return
        if isinstance(record, EvidenceBinding):
            self.bindings[key(record.evidence)] = record
            return
        if isinstance(record, Evidence):
            self.evidence[key(reference(record))] = record
            return
        if record.kind == "economic_evidence":
            self.economics.add(key(record.evidence))


def run_events(events, selection):
    grouped = defaultdict(list)
    for event in events:
        run = selection.runs[key(reference(event))]
        grouped[run_key(run) if run is not None else None].append(event)
    return grouped


def assess_run(index, run, effective, selected, scope):
    reasons, refs = set(), set()
    target = run_key(run)
    run_record = index.runs[target]
    refs.add(key(reference(run_record)))
    outcome = index.outcomes.get(key(reference(run_record)))
    interval = index.intervals.get(target)
    refs.update(lifecycle_refs(outcome, interval))
    if outcome is None:
        reasons.add("open_run")
    if interval is None or missing_bounds(interval):
        reasons.add("missing_work_bounds")
        return reasons, refs
    if any(e.start < interval.start or e.end > interval.end for e in effective):
        reasons.add("contradicted_work_bounds")
    reasons.update(event_coverage_reasons(index, run, interval, selected, scope, refs))
    return reasons, refs


def event_coverage_reasons(index, run, interval, events, scope, refs):
    reasons = set()
    if not events:
        reasons.add("missing_economic_evidence")
    if not policy_identity(scope) or (run.provider, run.surface) != ("synthetic", "fixture"):
        reasons.add("unknown_source_applicability")
    if any(not supported_event(e) for e in events):
        reasons.add("unsupported_source_policy")
    coverage = index.coverage[run_key(run)]
    refs.update(key(reference(r)) for r in coverage)
    requirements = event_requirements(events)
    if not any(supports(c, run, interval, requirements, scope) for c in coverage):
        reasons.add("missing_supported_coverage")
    if partial_scope(scope, interval):
        reasons.add("partial_change_scope")
    return reasons


def assess_coverage(index, change, members, selection, selected, scope):
    reasons, refs = set(), set()
    outcome = index.outcomes.get(key(reference(change)))
    if outcome is None:
        reasons.add("open_change")
    else:
        refs.add(key(reference(outcome)))
    if not members:
        reasons.add("no_linked_runs")
    effective_events = run_events(selection.effective, selection)
    selected_events = run_events(selected, selection)
    for run in members:
        target = run_key(run)
        run_reasons, run_refs = assess_run(
            index, run, effective_events[target], selected_events[target], scope
        )
        reasons.update(run_reasons)
        refs.update(run_refs)
    refs.update(key(reference(r)) for r in index.change_bindings[key(reference(change))])
    if any(selection.runs[key(reference(e))] is None for e in selection.selected):
        reasons.add("relevant_unbound_evidence")
    missing = unpriced_evidence(index, {run_key(run) for run in members})
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


def unpriced_evidence(index, members=None, repository_id=None) -> set:
    refs = set()
    for ref in index.evidence.keys() - index.economics:
        binding = index.bindings.get(ref)
        if (
            binding is None
            or (members is not None and run_key(binding.run) in members)
            or (repository_id is not None and binding.run.repository_id == repository_id)
        ):
            refs.add(ref)
    return refs
