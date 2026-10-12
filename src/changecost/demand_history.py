"""Cutoff-derived full terminal Change demand; partial quantities stay diagnostic."""

from dataclasses import dataclass
from fractions import Fraction
from statistics import median

from changecost.demand_graph import demand_lookup as lookup
from changecost.models import (
    Change,
    DemandObservation,
    Evidence,
    Interval,
    MeasurementPolicy,
    Outcome,
    Run,
    RunBinding,
)
from changecost.store import key, reference, run_key

POLICY = "synthetic-demand/v1"
ECOSYSTEM_FIELDS = (
    "provider",
    "surface",
    "model",
    "model_version",
    "runtime",
    "reasoning",
    "harness",
    "review",
)


@dataclass(frozen=True)
class CohortSelection:
    """Paired cohort and chronology choices for one internal estimate."""

    broad: bool = False
    algorithm: str = "observed-summary/v3"


def ecosystem_identity(records, ecosystem):
    values = tuple(getattr(ecosystem, f) for f in ECOSYSTEM_FIELDS)
    if any(value is None for value in values):
        return None
    policy = lookup(records, ecosystem.measurement_policy, "demand_policy")
    return (*values, policy.version, policy.component.model_dump_json(), policy.population)


def policy_supported(records, ecosystem, component):
    policy = lookup(records, ecosystem.measurement_policy, "demand_policy")
    if (
        not isinstance(policy, MeasurementPolicy)
        or policy.version != POLICY
        or policy.component != component
    ):
        return False
    if (ecosystem.provider, ecosystem.surface) != ("synthetic", "fixture"):
        return False
    units = {"wall_time": ("milliseconds", "elapsed"), "effort": ("seconds", "measured")}
    expected = units.get(component.category, ("tokens", "observed"))
    return (component.unit, component.basis) == expected


def current_revisions(records, cls):
    rows = [r for r in records.values() if isinstance(r, cls)]
    parents = {key(r.previous) for r in rows if r.previous is not None}
    return [r for r in rows if key(reference(r)) not in parents]


def change_members(records, change):
    mappings = [
        r for r in records.values() if isinstance(r, RunBinding) and r.change == reference(change)
    ]
    runs = {run_key(r.ref): r for r in records.values() if isinstance(r, Run)}
    return [(runs[run_key(m.run)], m) for m in mappings]


def frozen_assessment(records, assessment, availability, algorithm="observed-summary/v3"):
    change = lookup(records, assessment.change, "change")
    captured = availability[key(reference(assessment))]
    bound = max(assessment.recorded_at, assessment.effective_at, captured[0])
    for run, _ in change_members(records, change):
        if captured >= availability[key(reference(run))]:
            return False
        points = work_points(records, run, algorithm)
        if any(p is not None and bound >= p for p in points):
            return False
    return True


def run_truth(records, run, ecosystem, component, availability, algorithm="observed-summary/v3"):
    if (run.ref.provider, run.ref.surface) != ("synthetic", "fixture"):
        return None, None, "unsupported_native_run"
    observations = [
        o
        for o in current_revisions(records, DemandObservation)
        if o.run == run.ref and o.component == component
    ]
    if len(observations) != 1:
        return None, None, "missing_demand_observation"
    observation = observations[0]
    reason = observation_rejection(
        records, observation, ecosystem, component, availability, algorithm
    )
    if reason:
        return None, observation, reason
    if observation.quantity is None or not complete_run(records, run, observation):
        return None, observation, "incomplete_demand_coverage"
    if not all(synthetic_evidence(records, e) for e in observation.evidence):
        return None, observation, "unsupported_native_evidence"
    return Fraction(observation.quantity), observation, None


def observation_rejection(records, observation, ecosystem, component, availability, algorithm):
    observed_eco = lookup(records, observation.ecosystem, "ecosystem")
    identity = ecosystem_identity(records, observed_eco)
    if identity is None or identity != ecosystem_identity(records, ecosystem):
        return "mixed_or_unknown_ecosystem"
    if not frozen_ecosystem(records, observed_eco, observation, availability):
        return "late_ecosystem_snapshot"
    if not policy_supported(records, observed_eco, component):
        return "unsupported_measurement_policy"
    assessment = lookup(records, observation.assessment, "task_assessment")
    if not frozen_assessment(records, assessment, availability, algorithm):
        return "late_assessment"
    return None


def synthetic_evidence(records, ref):
    evidence = lookup(records, ref, "evidence")
    return isinstance(evidence, Evidence) and (
        evidence.provider,
        evidence.surface,
        evidence.profile,
    ) == ("synthetic", "fixture", POLICY)


def complete_run(records, run, observation):
    intervals = [r for r in current_revisions(records, Interval) if r.run == run.ref]
    outcomes = [r for r in current_revisions(records, Outcome) if r.subject == reference(run)]
    if not observation.complete or not observation.final or observation.quantity is None:
        return False
    if len(intervals) != 1 or len(outcomes) != 1:
        return False
    interval = intervals[0]
    return (
        interval.start is not None
        and interval.end is not None
        and observation.start <= interval.start
        and (
            run.observed_start is None or observation.start <= run.observed_start <= observation.end
        )
        and observation.end >= interval.end
    )


def aggregate(records, change, ecosystem, component, availability, algorithm="observed-summary/v3"):
    terminal = [r for r in current_revisions(records, Outcome) if r.subject == reference(change)]
    if len(terminal) != 1:
        return None, None, "open_change"
    members = change_members(records, change)
    if not members:
        return None, None, "no_bound_attempts"
    total, assessments = Fraction(0), []
    for run, _mapping in members:
        value, observation, reason = run_truth(
            records, run, ecosystem, component, availability, algorithm
        )
        if reason or value is None or observation is None:
            return None, None, reason or "missing_demand_observation"
        total += value
        assessments.append(lookup(records, observation.assessment, "task_assessment"))
    if any(
        a.dimensions != assessments[0].dimensions or a.scope_key != assessments[0].scope_key
        for a in assessments
    ):
        return None, None, "incompatible_assessment_snapshots"
    return total, assessments[0], None


def peers(records, target, assessment, ecosystem, component, availability, selection=None):
    selection = selection or CohortSelection()
    candidates, exclusions = [], []
    for change in sorted(
        (
            r
            for r in records.values()
            if isinstance(r, Change) and r.repository_id == target.repository_id
        ),
        key=lambda c: c.record_id,
    ):
        if change.record_id == target.record_id:
            continue
        value, peer_assessment, reason = aggregate(
            records, change, ecosystem, component, availability, selection.algorithm
        )
        if reason:
            exclusions.append((reference(change), reason))
        else:
            candidates.append((change, value, peer_assessment))
    exact = (
        [p for p in candidates if p[2].dimensions == assessment.dimensions]
        if known_dimensions(assessment)
        else []
    )
    return (
        (exact if exact and not selection.broad else candidates),
        ("dimensions" if exact and not selection.broad else "ecosystem"),
        exclusions,
    )


def known_dimensions(assessment):
    return "unknown" not in assessment.dimensions.model_dump().values()


def decimal_string(value):
    """Exact finite decimal; ratios remain rationals until explicit presentation."""
    value = Fraction(value)
    denominator, twos, fives = value.denominator, 0, 0
    while denominator % 2 == 0:
        denominator //= 2
        twos += 1
    while denominator % 5 == 0:
        denominator //= 5
        fives += 1
    if denominator != 1:
        raise ValueError("quantity is not a finite decimal")
    places = max(twos, fives)
    numerator = value.numerator * 2 ** (places - twos) * 5 ** (places - fives)
    sign = "-" if numerator < 0 else ""
    digits = str(abs(numerator)).zfill(places + 1)
    if not places:
        return sign + digits
    return (sign + digits[:-places] + "." + digits[-places:]).rstrip("0").rstrip(".")


def summaries(values):
    if not values:
        return dict(minimum=None, median=None, maximum=None)
    return dict(
        minimum=decimal_string(min(values)),
        median=decimal_string(median(values)),
        maximum=decimal_string(max(values)),
    )


def temporal_rows(records, cls, algorithm):
    if algorithm == "observed-summary/v3":
        return current_revisions(records, cls)
    return [r for r in records.values() if isinstance(r, cls)]


def work_points(records, run, algorithm="observed-summary/v3"):
    points = [run.observed_start]
    points.extend(
        p
        for r in temporal_rows(records, Interval, algorithm)
        if r.run == run.ref
        for p in (r.start, r.end)
    )
    points.extend(
        r.start for r in temporal_rows(records, DemandObservation, algorithm) if r.run == run.ref
    )
    return [p for p in points if p is not None]


def initial_forecast(records, change, cutoff, algorithm="observed-summary/v3"):
    members = change_members(records, change)
    # A registered Run with unknown work bounds cannot prove a pre-execution quote.
    return not members or all(
        work_points(records, run, algorithm)
        and cutoff.at < min(work_points(records, run, algorithm))
        for run, _ in members
    )


def frozen_ecosystem(records, ecosystem, observation, availability):
    policy = lookup(records, ecosystem.measurement_policy, "demand_policy")
    refs = [reference(ecosystem), reference(policy)]
    bound = max(
        max(r.recorded_at, r.effective_at, availability[key(reference(r))][0])
        for r in (ecosystem, policy)
    )
    return bound < observation.start and all(
        availability[key(ref)] < availability[key(reference(observation))] for ref in refs
    )
