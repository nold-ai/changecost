"""Chronological synthetic experiments in disposable destination stores."""

import hashlib
import json
import platform
import re
from collections import Counter
from contextlib import closing
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter_ns

from changecost import demand, quotes
from changecost.coverage import CoverageIndex
from changecost.demand_history import aggregate, change_members, current_revisions, initial_forecast
from changecost.evaluation_metrics import (
    adaptive_summary,
    coverage,
    economic_comparison,
    scenario_metrics,
)
from changecost.evaluation_models import (
    EvaluationCase,
    EvaluationProtocol,
    OmittedTruth,
    ScoredTruth,
    SyntheticHistory,
)
from changecost.models import (
    Bundle,
    Change,
    DemandObservation,
    EconomicEvidence,
    EvidenceBinding,
    Outcome,
    ValidationCase,
)
from changecost.reconciliation import computation_details, relevant, select, snapshot_records
from changecost.serialization import ContractError, loads_bundle, reject_constant, unique_members
from changecost.store import Store, key, reference, run_key

ALGORITHM = "observed-summary/v4"
MAX_BYTES = 16 * 1024 * 1024


def read_json(path: Path):
    with path.open("rb") as source:
        data = source.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ContractError("evaluation input exceeds limit")
    value = json.loads(
        data,
        object_pairs_hook=unique_members,
        parse_constant=reject_constant,
        parse_float=reject_constant,
    )
    bounded_numbers(value)
    return value, data


def bounded_numbers(value):
    pending = [value]
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)
        elif isinstance(item, str):
            match = re.fullmatch(r"-?\d+(?:\.\d+)?(?:[eE]([+-]?\d+))?", item)
            if match and (len(item) > 256 or abs(int(match.group(1) or "0")) > 256):
                raise ContractError("numeric magnitude exceeds evaluation limit")
            if re.fullmatch(r"-?\d+/\d+", item) and len(item) > 256:
                raise ContractError("numeric magnitude exceeds evaluation limit")


def safe_id(value: str) -> bool:
    return re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,199}", value) is not None


def validate_component_identifiers(value):
    pending = [value]
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            for name in ("unit", "basis"):
                if name in item and not safe_id(item[name]):
                    raise ContractError("unsafe component identifier")
            pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)


def validate_evaluation_record(record):
    validate_component_identifiers(record.model_dump())
    identifiers = [
        record.record_id,
        getattr(record, "change_id", "safe"),
        getattr(record, "scope_key", "safe"),
    ]
    if record.kind == "run":
        identifiers.extend([record.ref.run_id, record.ref.repository_id])
    if record.kind == "native_usage" or not all(safe_id(v) for v in identifiers):
        raise ContractError("unsupported evaluation record")
    provider = getattr(record, "provider", None)
    source = getattr(record, "source", None)
    run = getattr(record, "ref", None) if record.kind == "run" else None
    providers = [provider, getattr(source, "provider", None), getattr(run, "provider", None)]
    if any(p is not None and p != "synthetic" for p in providers):
        raise ContractError("only declared synthetic providers supported")


def validate_evaluation_scope(protocol):
    economic_ids = [
        value
        for value in protocol.economic_scope.economic.model_dump().values()
        if value is not None
    ]
    if not all(
        safe_id(v) for v in [protocol.version, protocol.economic_scope.repository_id, *economic_ids]
    ):
        raise ContractError("unsafe experiment identifier")


def validate_experiment(history, protocol):
    records = {key(reference(r)): r for r in history.bundle.records}
    scheduled = [key(ref) for delivery in history.deliveries for ref in delivery.records]
    if (
        len(records) != len(history.bundle.records)
        or len(set(scheduled)) != len(scheduled)
        or set(scheduled) != set(records)
    ):
        raise ContractError("each input record needs exactly one delivery")
    if [d.at for d in history.deliveries] != sorted(d.at for d in history.deliveries):
        raise ContractError("deliveries must be chronological")
    for record in records.values():
        validate_evaluation_record(record)
    validate_evaluation_scope(protocol)
    arrivals = {key(ref): d.at for d in history.deliveries for ref in d.records}
    for case in protocol.cases:
        validate_case(case, protocol, records, arrivals)
    return records


def validate_case(case, protocol, records, arrivals):
    change = records.get(key(case.change))
    if (
        not isinstance(change, Change)
        or change.repository_id != protocol.economic_scope.repository_id
        or not safe_id(case.id)
    ):
        raise ContractError("invalid evaluation target")
    if arrivals[key(case.change)] >= case.forecast_at:
        raise ContractError("target unavailable before forecast")
    if case.imported_forecast and (
        key(case.imported_forecast) not in arrivals
        or arrivals[key(case.imported_forecast)] >= case.forecast_at
    ):
        raise ContractError("imported forecast unavailable")
    if case.adaptive:
        selection = case.adaptive
        for ref in [
            selection.assessment,
            selection.ecosystem,
            selection.policy,
            *([selection.rehearsal_assessment] if selection.rehearsal_assessment else []),
        ]:
            if key(ref) not in records or arrivals[key(ref)] >= case.forecast_at:
                raise ContractError("adaptive selector unavailable")
        assessment = records[key(selection.assessment)]
        policy = records[key(selection.policy)]
        if assessment.kind != "task_assessment" or policy.kind != "demand_validation_policy":
            raise ContractError("invalid adaptive selector")
        validate_registration(protocol, selection, records, arrivals)


def validate_registration(protocol, selection, records, arrivals):
    policy = records[key(selection.policy)]
    assessments = [selection.assessment]
    if selection.rehearsal_assessment:
        assessments.append(selection.rehearsal_assessment)
    for ref in assessments:
        assessment = records[key(ref)]
        first = min(assessment.recorded_at, assessment.effective_at, arrivals[key(ref)])
        if protocol.registered_at >= first:
            raise ContractError("protocol postdates assessment")
        if max(policy.recorded_at, policy.effective_at, arrivals[key(selection.policy)]) >= first:
            raise ContractError("policy postdates assessment")


def economic_initial(records, change, cutoff):
    members = {run_key(run.ref) for run, _ in change_members(records, change)}
    work = quotes.economic_work_records(records, members)
    return initial_forecast(records, change, cutoff, ALGORITHM) and all(
        cutoff.at < r.start for r in work
    )


def cutoff_view(cutoff):
    return dict(
        destination="synthetic_destination", at=cutoff.at.isoformat(), sequence=cutoff.sequence
    )


def reference_views(refs):
    return [r.model_dump() for r in sorted(refs, key=key)]


def economic_truth(records, change, scope):
    details = computation_details(records, change, scope)
    attempts = tuple(sorted(r.run_id for r in details["runs"]))
    dependencies = tuple(details["inputs"])
    if not details["full_change"]:
        return OmittedTruth(tuple(details["unknown_reasons"]), attempts, dependencies)
    outcome = CoverageIndex(records).outcomes[key(reference(change))].outcome
    return ScoredTruth(Fraction(details["subtotals"][0].amount), outcome, attempts, dependencies)


def truth_view(truth, cutoff):
    result = dict(
        cutoff=cutoff_view(cutoff),
        attempts=list(truth.attempts),
        dependencies=reference_views(truth.dependencies),
    )
    if isinstance(truth, OmittedTruth):
        return dict(**result, status="omitted", reasons=list(truth.reasons))
    return dict(**result, status="complete", amount=str(truth.amount), outcome=truth.outcome)


def quote_view(quote):
    return dict(
        state=quote.state,
        p50=quote.p50.amount,
        p90=quote.p90.amount,
        sample_count=quote.sample_count,
        cohort=quote.cohort,
        fallback=[c.reason for c in quote.estimation.cohorts if c.reason]
        if quote.estimation
        else [],
    )


@dataclass
class Experiment:
    store: Store
    protocol: EvaluationProtocol
    quotes: dict = field(default_factory=dict)
    forecasts: dict = field(default_factory=dict)
    economic: list = field(default_factory=list)
    adaptive: list = field(default_factory=list)
    updates: list = field(default_factory=list)

    def forecast(self, case: EvaluationCase, *, update=False):
        if case.imported_forecast:
            self.quotes[case.id] = None
            return
        change = next(
            r for r in self.store.records() if isinstance(r, Change) and reference(r) == case.change
        )
        operation = f"evaluation-{case.id}-{self.store.clock().isoformat()}"
        candidate = quotes.compute_quote(
            self.store, change.change_id, self.protocol.economic_scope, operation
        )
        with closing(self.store.connect(readonly=True)) as connection:
            records = snapshot_records(connection, candidate.cutoff)
            baseline = quotes.estimate(
                records,
                records[key(case.change)],
                self.protocol.economic_scope,
                20,
                candidate.cutoff,
                quotes.local_availability(connection),
                repository_only=True,
            )
        if update:
            self.updates.append(
                dict(
                    case=case.id,
                    at=self.store.clock().isoformat(),
                    candidate=quote_view(candidate),
                    baseline=quote_view(baseline),
                    primary=False,
                )
            )
        else:
            self.quotes[case.id] = (candidate, baseline)
        if case.adaptive:
            forecasts = self.demand_forecasts(case, change, operation)
            if update:
                self.updates[-1]["adaptive"] = {
                    name: dict(
                        state=f.result.state, initial=f.initial, peers=reference_views(f.peers)
                    )
                    for name, f in forecasts.items()
                }
            else:
                self.forecasts[case.id] = forecasts

    def demand_forecasts(self, case, change, operation):
        selection = case.adaptive
        result = {}
        for name, assessment, broad in [
            ("repository", selection.assessment, True),
            ("dimensional", selection.assessment, False),
            *(
                [
                    ("rehearsal_repository", selection.rehearsal_assessment, True),
                    ("rehearsal", selection.rehearsal_assessment, False),
                ]
                if selection.rehearsal_assessment
                else []
            ),
        ]:
            result[name] = demand.compute_demand(
                self.store,
                demand.DemandRequest(
                    change.repository_id,
                    change.change_id,
                    f"{operation}-{name}",
                    assessment.record_id,
                    selection.ecosystem.record_id,
                    broad_baseline=broad,
                ),
            )
        return result

    def score(self, case):
        cutoff = self.store.snapshot()
        with closing(self.store.connect(readonly=True)) as connection:
            records = snapshot_records(connection, cutoff)
            change = records[key(case.change)]
            truth = economic_truth(records, change, self.protocol.economic_scope)
            row: dict = dict(case=case.id, truth=truth_view(truth, cutoff))
            pair = self.quotes[case.id]
            if pair is None:
                record = records.get(key(case.imported_forecast))
                if record is None or record.kind not in {"quote", "demand_forecast"}:
                    raise ContractError("imported forecast unavailable")
                inspect = quotes.inspect_quote if record.kind == "quote" else demand.inspect_demand
                row.update(
                    status=inspect(self.store, record)["replay_eligibility"],
                    candidate=None,
                    baseline=None,
                )
            else:
                candidate, baseline = pair
                row.update(
                    candidate=quote_view(candidate),
                    baseline=quote_view(baseline),
                    forecast_cutoff=cutoff_view(candidate.cutoff),
                )
                row["status"] = self.economic_status(
                    connection, records, change, truth, candidate, baseline
                )
            self.economic.append(row)
            if case.adaptive and case.id in self.forecasts:
                self.adaptive.append(self.score_adaptive(connection, records, case, cutoff))

    def economic_status(self, connection, records, change, truth, candidate, baseline):
        if candidate.state != baseline.state:
            return "comparison_error"
        if not quotes.quote_reproduced(connection, records, candidate):
            return "replay_unavailable"
        if not economic_initial(records, change, candidate.cutoff):
            return "not_initial"
        if candidate.state == "unpriced":
            return "joint_unpriced"
        return "missing_full_change_truth" if isinstance(truth, OmittedTruth) else "scored"

    def score_adaptive(self, connection, records, case, cutoff):
        selection = case.adaptive
        policy = records[key(selection.policy)]
        ecosystem = records[key(selection.ecosystem)]
        assessment = records[key(selection.assessment)]
        actual, _, reason = aggregate(
            records,
            records[key(case.change)],
            ecosystem,
            policy.component,
            quotes.local_availability(connection),
            ALGORITHM,
        )
        methods = {}
        forecasts = self.forecasts[case.id]
        for name, forecast in forecasts.items():
            baseline = forecasts[
                "rehearsal_repository" if name.startswith("rehearsal") else "repository"
            ]
            methods[name] = observed_metrics(
                connection, records, policy, case, forecast, baseline, actual
            )
        transfer = forecasts["dimensional"].result.transfer
        if transfer is not None:
            forecast = forecasts["dimensional"]
            initial = initial_forecast(
                records, records[key(case.change)], forecast.cutoff, ALGORITHM
            )
            methods["transfer"] = scenario_metrics(transfer, actual if initial else None)
        else:
            methods["transfer"] = dict(state="unavailable", median=None, truth_count=0)
        members = {run_key(r.ref) for r, _ in change_members(records, records[key(case.change)])}
        revisions = [
            reference(r)
            for r in current_revisions(records, DemandObservation)
            if run_key(r.run) in members
        ]
        return dict(
            case=case.id,
            scope_key=assessment.scope_key,
            policy=policy.model_dump(
                include={
                    "record_id",
                    "ecosystem",
                    "component",
                    "population",
                    "minimum_truth",
                    "nominal_coverage",
                    "coverage_tolerance",
                    "maximum_underestimate",
                    "maximum_width",
                    "maximum_overhead",
                    "require_baseline",
                }
            ),
            component=policy.component.model_dump(),
            truth=dict(
                status="complete" if actual is not None else "omitted",
                amount=str(actual) if actual is not None else None,
                reason=reason,
                category="observed"
                if actual is not None
                else "partial"
                if reason == "incomplete_demand_coverage"
                else "unavailable",
                outcome=next(
                    (
                        r.outcome
                        for r in current_revisions(records, Outcome)
                        if r.subject == case.change
                    ),
                    None,
                ),
                cutoff=cutoff_view(cutoff),
                revisions=reference_views(revisions),
            ),
            methods=methods,
        )


def observed_metrics(connection, records, policy, case, forecast, baseline, actual):
    result: dict = dict(
        state=forecast.result.state,
        interpretation="observed_summary_not_quantiles",
        median=forecast.result.median,
        minimum=forecast.result.minimum,
        maximum=forecast.result.maximum,
        sample_count=forecast.result.sample_count,
        initial=forecast.initial,
        peers=reference_views(forecast.peers),
        exclusions=sorted({e.reason for e in forecast.exclusions}),
        signed_error=None,
        synthetic_rubric_passed=False,
    )
    assessment = records[key(forecast.assessment)]
    if assessment.rehearsal:
        result["rehearsal_overhead"] = assessment.rehearsal.overhead.model_dump()
        result["net_benefit"] = None
        result["net_benefit_undefined_reason"] = "no_compatible_scored_comparison"
    if actual is None or forecast.result.median is None:
        return result
    validation_case = ValidationCase(
        forecast=reference(forecast), truth=case.change, baseline=reference(baseline)
    )
    try:
        metrics, passed = demand.measure_validation(
            demand.ReplayContext(connection), records, policy, [validation_case], ALGORITHM
        )
    except ContractError as exc:
        result["ineligible_reason"] = eligibility_reason(str(exc))
        return result
    signed = Fraction(forecast.result.median) - actual
    result.update(
        signed_error=str(signed),
        absolute_error=str(abs(signed)),
        metrics=metrics.model_dump(),
        synthetic_rubric_passed=passed,
    )
    assessment = records[key(forecast.assessment)]
    if assessment.rehearsal:
        overhead = assessment.rehearsal.overhead
        result["rehearsal_overhead"] = overhead.model_dump()
        result["net_benefit_undefined_reason"] = None
        result["net_benefit"] = (
            str(Fraction(metrics.baseline_error) - abs(signed) - Fraction(overhead.amount))
            if metrics.baseline_error is not None and overhead.component == policy.component
            else None
        )
    return result


def eligibility_reason(message):
    allowed = {
        "complete validation truth unavailable",
        "incompatible forecast/truth",
        "rubric overhead units incompatible",
        "forecast was not captured before truth work",
        "late validation predictors",
        "validation needs reproduced local forecast",
    }
    if message not in allowed:
        raise ContractError("inconsistent evaluation protocol")
    return message.replace(" ", "_")


def attribution(records, scope):
    events = [r for r in records.values() if isinstance(r, EconomicEvidence) and relevant(r, scope)]
    bindings = {key(r.evidence): r for r in records.values() if isinstance(r, EvidenceBinding)}
    counts = Counter(
        "unbound"
        if key(e.evidence) not in bindings
        else "provider"
        if bindings[key(e.evidence)].method == "verified_provider"
        else "manual"
        for e in events
    )
    selection = select(records, scope)
    diagnostics = Counter(e.reason for e in selection.exclusions)
    return dict(
        raw_record_count=len(events),
        effective_event_count=len(selection.selected),
        coverage={
            name: coverage(counts[name], len(events)) for name in ("provider", "manual", "unbound")
        },
        unknown_money_count=sum(e.component.amount is None for e in events),
        known_amount=str(
            sum(
                (
                    Fraction(e.component.amount)
                    for e in selection.selected
                    if e.component.amount is not None
                ),
                Fraction(0),
            )
        ),
        diagnostics=dict(sorted(diagnostics.items())),
        duplicate_count=diagnostics["duplicate"],
        conflict_count=diagnostics["conflict"],
        pending_correction_count=diagnostics["pending_correction"],
        diagnostic_denominator=len(events),
        identity=scope.economic.model_dump(),
    )


def terminal_truths(records, scope):
    outcomes = {key(r.subject): r for r in current_revisions(records, Outcome)}
    return [
        economic_truth(records, r, scope)
        for r in records.values()
        if isinstance(r, Change)
        and r.repository_id == scope.repository_id
        and key(reference(r)) in outcomes
    ]


def abandoned_share(records, scope):
    truths = terminal_truths(records, scope)
    complete = [t for t in truths if isinstance(t, ScoredTruth)]
    unknown = len(truths) - len(complete)
    total = sum((t.amount for t in complete), Fraction(0))
    abandoned = sum((t.amount for t in complete if t.outcome == "abandoned"), Fraction(0))
    return dict(
        identity=scope.economic.model_dump(),
        terminal_count=len(truths),
        unknown_count=unknown,
        attempt_count=sum(len(t.attempts) for t in truths),
        known_total=str(total),
        known_abandoned=str(abandoned),
        share=str(abandoned / total) if not unknown and total else None,
        undefined_reason="unknown_terminal_amount"
        if unknown
        else "zero_terminal_amount"
        if not total
        else None,
        outcomes=dict(sorted(Counter(t.outcome for t in complete).items())),
    )


def run_history(history, protocol, path):
    records = validate_experiment(history, protocol)
    clock = [protocol.registered_at]
    store = Store(path, clock=lambda: clock[0])
    experiment = Experiment(store, protocol)
    events = [(d.at, 0, index, "delivery", d) for index, d in enumerate(history.deliveries)]
    for index, case in enumerate(protocol.cases):
        events.extend(
            [
                (case.forecast_at, 1, index, "forecast", case),
                (case.truth_at, 2, index, "truth", case),
            ]
        )
        events.extend((at, 3, index, "update", case) for at in case.updates)
    events.append((protocol.observation_at, 4, 0, "observation", None))
    observed = None
    for at, _, _, kind, value in sorted(events, key=lambda e: e[:3]):
        clock[0] = at
        if kind == "delivery":
            selected = [records[key(ref)] for ref in value.records]
            refs = {key(ref) for ref in value.records}
            observations = [o for o in history.bundle.observations if key(o.reference) in refs]
            store.import_bundle(
                Bundle(source=history.bundle.source, records=selected, observations=observations)
            )
            continue
        if kind == "forecast":
            experiment.forecast(value)
            continue
        if kind == "update":
            experiment.forecast(value, update=True)
            continue
        if kind == "truth":
            experiment.score(value)
            continue
        with closing(store.connect(readonly=True)) as connection:
            observed = snapshot_records(connection, store.snapshot())
    core = dict(
        schema="changecost/evaluation-report-v1",
        provenance="synthetic_fixture_only",
        protocol_version=protocol.version,
        algorithm_versions=dict(
            economic=quotes.ALGORITHM, demand=ALGORITHM, metrics=protocol.formula
        ),
        economic=economic_comparison(
            experiment.economic, protocol.economic_scope.economic.model_dump()
        ),
        adaptive=adaptive_summary(experiment.adaptive, protocol.minimum_independent_truth),
        updates=experiment.updates,
        attribution=attribution(observed, protocol.economic_scope),
        abandonment=abandoned_share(observed, protocol.economic_scope),
        source_gaps=list(protocol.source_gaps),
        conclusion="synthetic_only_not_yet_validated",
    )
    return core, path.stat().st_size


def evaluate_synthetic(history: Path, protocol: Path, *, measure_runs: int = 0) -> dict:
    """Evaluate asserted synthetic files without opening the user's runtime database."""
    try:
        if type(measure_runs) is not int or not 0 <= measure_runs <= 20:
            raise ContractError("invalid measurement run count")
        history_data, history_bytes = read_json(Path(history))
        protocol_data, protocol_bytes = read_json(Path(protocol))
        history_data["bundle"] = loads_bundle(json.dumps(history_data["bundle"]))
        parsed_history = SyntheticHistory.model_validate(history_data)
        parsed_protocol = EvaluationProtocol.model_validate(protocol_data)
        times, sizes, core = [], [], None
        with TemporaryDirectory(prefix="changecost-evaluation-") as directory:
            for index in range(max(1, measure_runs)):
                start = perf_counter_ns()
                current, size = run_history(
                    parsed_history, parsed_protocol, Path(directory) / f"run-{index}.sqlite3"
                )
                times.append(perf_counter_ns() - start)
                sizes.append(size)
                if core is not None and current != core:
                    raise ContractError("nondeterministic evaluation")
                core = current
        assert core is not None
        core.update(
            history_sha256=hashlib.sha256(history_bytes).hexdigest(),
            protocol_sha256=hashlib.sha256(protocol_bytes).hexdigest(),
        )
        measurements = (
            dict(
                runs_ms=[str(Fraction(n, 1000000)) for n in times],
                input_bytes=len(history_bytes) + len(protocol_bytes),
                store_bytes=sizes,
                python=platform.python_version(),
                platform=platform.system(),
                timer="perf_counter_ns",
                nondeterministic=True,
            )
            if measure_runs
            else None
        )
        return dict(core=core, measurements=measurements)
    except (ValueError, TypeError, KeyError, OSError, RecursionError) as exc:
        raise ContractError("invalid synthetic evaluation input") from exc
