"""Allowlisted portable records; accepting provenance does not authenticate it."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from typing import Annotated, Literal, Self

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, model_validator


def identifier(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("expected a nonblank identifier")
    return value


def timestamp(value: object) -> datetime:
    if isinstance(value, str):
        if not re.fullmatch(
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
            r"(?:\.[0-9]{1,6})?(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])",
            value,
        ):
            raise ValueError("expected an aware RFC3339 timestamp")
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("expected an aware RFC3339 timestamp")
    try:
        return value.astimezone(UTC)
    except OverflowError as exc:
        raise ValueError("timestamp outside supported UTC range") from exc


def amount(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not re.fullmatch(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?", value):
        raise ValueError("expected a finite decimal string or null")
    try:
        if not Decimal(value).is_finite():
            raise ValueError("expected a finite decimal")
    except InvalidOperation as exc:
        raise ValueError("expected a finite decimal") from exc
    return value


MAX_SEQUENCE = 2**63 - 1

Identifier = Annotated[str, BeforeValidator(identifier)]
Timestamp = Annotated[datetime, BeforeValidator(timestamp)]
Amount = Annotated[str | None, BeforeValidator(amount)]
Kind = Literal[
    "change",
    "run",
    "evidence",
    "run_binding",
    "evidence_binding",
    "outcome",
    "interval",
    "quote",
    "settlement",
    "economic_evidence",
    "source_coverage",
    "computed_settlement",
    "task_assessment",
    "demand_policy",
    "ecosystem",
    "demand_observation",
    "matched_comparison",
    "transfer_hypothesis",
    "demand_price",
    "demand_forecast",
    "demand_validation_policy",
    "demand_validation",
]


class Model(BaseModel):
    model_config = ConfigDict(
        extra="forbid", frozen=True, populate_by_name=True, hide_input_in_errors=True
    )


class RecordRef(Model):
    kind: Kind
    record_id: Identifier


class RunRef(Model):
    repository_id: Identifier
    provider: Identifier
    surface: Identifier
    run_id: Identifier


class Cutoff(Model):
    store_id: Identifier
    at: Timestamp
    sequence: Annotated[int, Field(strict=True, ge=0, le=MAX_SEQUENCE)]


class Features(Model):
    version: Literal["features/v1"] = "features/v1"
    captured_at: Timestamp
    recorded_at: Timestamp
    change_shape: str | None = None
    trajectory: str | None = None
    execution_profile: str | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize(cls, values: object) -> object:
        if not isinstance(values, dict):
            return values
        result = dict(values)
        domains = {
            "change_shape": {"bugfix", "feature", "refactor", "docs", "maintenance", "other"},
            "trajectory": {"single-pass", "iterative", "investigative"},
            "execution_profile": {
                "copilot-cli",
                "copilot-ide",
                "cursor-cli",
                "cursor-ide",
                "mixed",
            },
        }
        for key, domain in domains.items():
            value = result.get(key)
            if value is not None:
                if not isinstance(value, str):
                    raise ValueError("invalid feature")
                value = (
                    value.strip(" \t\n\r\v\f").translate(
                        str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")
                    )
                    or None
                )
                if value is not None and value not in domain:
                    raise ValueError("invalid feature")
            result[key] = value
        return result


class Component(Model):
    economic_kind: Literal["monetary", "nonmonetary"]
    unit: Identifier
    basis: Identifier
    currency: str | None = None
    amount: Amount

    @model_validator(mode="after")
    def currency_matches(self) -> Self:
        if self.currency is not None and not re.fullmatch("[A-Z]{3}", self.currency):
            raise ValueError("invalid currency")
        if self.economic_kind == "nonmonetary" and self.currency is not None:
            raise ValueError("nonmonetary currency must be null")
        if self.economic_kind == "monetary" and self.amount is not None and self.currency is None:
            raise ValueError("known money requires currency")
        return self


class Record(Model):
    schema_version: Literal["changecost/v1"] = Field(default="changecost/v1", alias="schema")
    record_id: Identifier
    origin_store_id: Identifier
    recorded_at: Timestamp
    effective_at: Timestamp


class Change(Record):
    kind: Literal["change"] = "change"
    repository_id: Identifier
    change_id: Identifier
    features: Features
    commit_ref: Identifier | None = None
    pr_ref: Identifier | None = None

    @model_validator(mode="after")
    def captured_at_registration(self) -> Self:
        if (
            self.features.captured_at != self.recorded_at
            or self.features.recorded_at != self.recorded_at
        ):
            raise ValueError("feature timestamps must match registration")
        return self


class Run(Record):
    kind: Literal["run"] = "run"
    ref: RunRef
    observed_start: Timestamp | None = None
    provider_session_id: Identifier | None = None
    trace_id: Identifier | None = None

    @model_validator(mode="after")
    def start_observed_before_registration(self) -> Self:
        if self.observed_start is not None and self.observed_start > self.recorded_at:
            raise ValueError("observed start cannot postdate registration")
        return self


class Evidence(Record):
    kind: Literal["evidence"] = "evidence"
    provider: Identifier
    surface: Identifier
    profile: Identifier
    identity_scope: Literal["namespaced", "file"]
    source_key: Identifier | None = None
    file_digest: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")] | None = None
    ordinal: Annotated[int, Field(strict=True, ge=0)] | None = None

    @model_validator(mode="after")
    def scoped_identity(self) -> Self:
        if self.identity_scope == "file":
            if self.file_digest is None or self.ordinal is None or self.source_key is not None:
                raise ValueError("file identity requires digest and ordinal only")
        elif self.source_key is None or self.file_digest is not None or self.ordinal is not None:
            raise ValueError("namespaced identity requires source key only")
        return self


class Provenance(Record):
    method: Literal["manual", "verified_provider"] = "manual"
    source_refs: list[RecordRef] = Field(default_factory=list)


class RunBinding(Provenance):
    kind: Literal["run_binding"] = "run_binding"
    run: RunRef
    change: RecordRef


class EvidenceBinding(Provenance):
    kind: Literal["evidence_binding"] = "evidence_binding"
    evidence: RecordRef
    run: RunRef


class Outcome(Record):
    kind: Literal["outcome"] = "outcome"
    subject: RecordRef
    outcome: Literal["accepted", "abandoned", "succeeded", "failed", "cancelled"]
    previous: RecordRef | None = None
    reason: Identifier | None = None


class Interval(Provenance):
    kind: Literal["interval"] = "interval"
    run: RunRef
    start: Timestamp | None = None
    end: Timestamp | None = None
    previous: RecordRef | None = None
    reason: Identifier | None = None

    @model_validator(mode="after")
    def ordered_bounds(self) -> Self:
        if self.start is not None and self.end is not None and self.start > self.end:
            raise ValueError("work start is after end")
        if any(t is not None and t > self.recorded_at for t in (self.start, self.end)):
            raise ValueError("work bound is after declaration")
        return self


class QuotePeer(Model):
    change: RecordRef
    amount: Amount
    inputs: list[RecordRef]


class CohortEvaluation(Model):
    level: Literal["profile", "shape_trajectory", "repository"]
    count: Annotated[int, Field(strict=True, ge=0)]
    reason: Identifier | None = None


class QuoteExclusion(Model):
    reference: RecordRef
    reason: Identifier


class Estimation(Model):
    version: Identifier = "estimation/v1"
    minimum: Annotated[int, Field(strict=True, gt=0)]
    population: Literal["accepted_and_abandoned"] = "accepted_and_abandoned"
    reconciliation_version: Identifier = "settlement/v1"
    policy_version: Identifier = "synthetic/v1"
    synthetic: bool
    cohorts: list[CohortEvaluation]
    peers: list[QuotePeer]
    exclusions: list[QuoteExclusion]


class Quote(Record):
    kind: Literal["quote"] = "quote"
    change: RecordRef
    state: Literal["priced", "unpriced"]
    p50: Component
    p90: Component
    reason: Identifier | None = None
    sample_count: Annotated[int, Field(strict=True, ge=0)]
    cohort: Identifier
    algorithm_version: Identifier
    cutoff: Cutoff
    inputs: list[RecordRef]
    features: Features | None = None
    estimation: Estimation | None = None

    @model_validator(mode="after")
    def quantiles(self) -> Self:
        if self.p50.model_dump(exclude={"amount"}) != self.p90.model_dump(exclude={"amount"}):
            raise ValueError("quantile units differ")
        if self.state == "priced":
            if self.p50.amount is None or self.p90.amount is None or self.sample_count == 0:
                raise ValueError("priced quote requires values and samples")
            if Decimal(self.p50.amount) > Decimal(self.p90.amount):
                raise ValueError("quantiles out of order")
        elif self.p50.amount is not None or self.p90.amount is not None or not self.reason:
            raise ValueError("unpriced quote requires null quantiles and reason")
        return self

    def estimation_peer_refs(self, metadata: Estimation) -> set[tuple[str, str]]:
        peer_refs = [(p.change.kind, p.change.record_id) for p in metadata.peers]
        if len(set(peer_refs)) != len(peer_refs) or any(
            p.change.kind != "change" or p.amount is None for p in metadata.peers
        ):
            raise ValueError("invalid Quote peers")
        return set(peer_refs)

    def validate_estimation_references(self, metadata: Estimation) -> None:
        refs = {(r.kind, r.record_id) for r in self.inputs}
        referenced = self.estimation_peer_refs(metadata) | {
            (r.kind, r.record_id) for p in metadata.peers for r in p.inputs
        }
        referenced.update((e.reference.kind, e.reference.record_id) for e in metadata.exclusions)
        if not referenced <= refs:
            raise ValueError("Quote metadata references missing inputs")

    def validate_estimation_samples(self, metadata: Estimation) -> None:
        if self.sample_count != len(metadata.peers) or (
            self.state == "priced" and self.sample_count < metadata.minimum
        ):
            raise ValueError("Quote sample count inconsistent")
        if self.state == "unpriced" and metadata.peers:
            raise ValueError("unpriced Quote has selected peers")

    @model_validator(mode="after")
    def estimation_inputs(self) -> Self:
        if self.estimation is not None:
            self.validate_estimation_references(self.estimation)
            self.validate_estimation_samples(self.estimation)
        return self


class Coverage(Model):
    run: RunRef
    outcome: RecordRef
    interval: RecordRef
    evidence: list[RecordRef]


class Settlement(Record):
    kind: Literal["settlement"] = "settlement"
    change: RecordRef
    components: list[Component]
    completeness: Literal["provisional", "reconciled"]
    scope: Identifier
    coverage: list[Coverage]
    inputs: list[RecordRef]
    unknown_reasons: list[Identifier]
    previous: RecordRef | None = None


class EconomicIdentity(Model):
    economic_kind: Literal["monetary", "nonmonetary"]
    unit: Identifier
    basis: Identifier
    currency: str | None = None

    @model_validator(mode="after")
    def valid_identity(self) -> Self:
        Component(**self.model_dump(), amount=None)
        return self


class SourceLocator(Model):
    repository_id: Identifier
    provider: Identifier
    surface: Identifier
    profile: Identifier
    namespace: Identifier
    identity_scope: Literal["namespaced", "file"]
    source_key: Identifier | None = None
    file_digest: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")] | None = None
    ordinal: Annotated[int, Field(strict=True, ge=0)] | None = None

    @model_validator(mode="after")
    def scoped(self) -> Self:
        if self.identity_scope == "namespaced":
            if self.source_key is None or self.file_digest is not None or self.ordinal is not None:
                raise ValueError("invalid namespaced source")
        elif self.file_digest is None or self.ordinal is None or self.source_key is not None:
            raise ValueError("invalid file source")
        return self


class EconomicInput(Model):
    source: SourceLocator
    component_key: Identifier
    component: Component
    series: Identifier
    lane: Literal["delta", "snapshot"]
    start: Timestamp
    end: Timestamp
    baseline_zero: Annotated[bool, Field(strict=True)] = False
    replaces: SourceLocator | None = None
    correction_reason: Identifier | None = None

    @model_validator(mode="after")
    def valid_window(self) -> Self:
        if self.start > self.end:
            raise ValueError("reversed source interval")
        if (self.replaces is None) != (self.correction_reason is None):
            raise ValueError("replacement requires locator and reason")
        if self.lane == "delta" and self.baseline_zero:
            raise ValueError("delta cannot declare a snapshot baseline")
        return self


class EconomicEvidence(Record, EconomicInput):
    kind: Literal["economic_evidence"] = "economic_evidence"
    evidence: RecordRef


class SourceCoverage(Record):
    kind: Literal["source_coverage"] = "source_coverage"
    run: RunRef
    provider: Identifier
    surface: Identifier
    profile: Identifier
    namespace: Identifier
    component_key: Identifier
    policy_version: Identifier
    economic: EconomicIdentity
    start: Timestamp
    end: Timestamp
    final: Annotated[bool, Field(strict=True)]
    evidence: list[RecordRef]

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.start > self.end or not self.evidence:
            raise ValueError("invalid coverage window or absent support")
        return self


class EconomicScope(Model):
    repository_id: Identifier
    economic: EconomicIdentity
    start: Timestamp | None = None
    end: Timestamp | None = None

    @model_validator(mode="after")
    def window(self) -> Self:
        if (self.start is None) != (self.end is None):
            raise ValueError("source window requires both bounds")
        if self.start is not None and self.end is not None and self.start > self.end:
            raise ValueError("reversed source window")
        return self


class Exclusion(Model):
    reference: RecordRef
    reason: Identifier


class Subtotal(Model):
    economic: EconomicIdentity
    amount: Amount
    unknown_count: Annotated[int, Field(strict=True, ge=0)]


class ComputedSettlement(Record):
    kind: Literal["computed_settlement"] = "computed_settlement"
    change: RecordRef
    operation_id: Identifier
    ledger_id: Identifier
    cutoff: Cutoff
    algorithm_version: Identifier
    policy_version: Identifier
    scope: EconomicScope
    subtotals: list[Subtotal]
    runs: list[RunRef]
    inputs: list[RecordRef]
    exclusions: list[Exclusion]
    unknown_reasons: list[Identifier]
    full_change: Annotated[bool, Field(strict=True)]
    synthetic: Annotated[bool, Field(strict=True)]
    previous: RecordRef | None = None


MAX_DEMAND_DIGITS = 4096


def nonnegative(value: object) -> str:
    result = amount(value)
    if result is None or Decimal(result) < 0:
        raise ValueError("expected nonnegative finite quantity")
    parts = Decimal(result).as_tuple()
    exponent = int(parts.exponent)
    if max(1, len(parts.digits) + exponent) - min(0, exponent) > MAX_DEMAND_DIGITS:
        raise ValueError("demand decimal digit limit exceeded")
    return result


def rational(value: object) -> str:
    from fractions import Fraction

    if not isinstance(value, str) or not re.fullmatch(r"-?\d+(?:/\d+)?", value):
        raise ValueError("expected exact rational string")
    if any(len(part.lstrip("-")) > MAX_DEMAND_DIGITS for part in value.split("/")):
        raise ValueError("demand rational digit limit exceeded")
    try:
        return str(Fraction(value))
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError("invalid rational") from exc


Nonnegative = Annotated[str, BeforeValidator(nonnegative)]
Rational = Annotated[str, BeforeValidator(rational)]
Ordinal = Literal["low", "moderate", "high", "unknown"]


class Dimensions(Model):
    scope: Ordinal = "unknown"
    coupling: Ordinal = "unknown"
    novelty: Ordinal = "unknown"
    ambiguity: Ordinal = "unknown"
    validation: Ordinal = "unknown"
    context: Ordinal = "unknown"


class DemandComponent(Model):
    category: Literal[
        "input", "output", "cache_read", "cache_write", "reasoning", "wall_time", "effort"
    ]
    unit: Identifier
    basis: Identifier


class Quantity(Model):
    component: DemandComponent
    amount: Nonnegative


class Rehearsal(Model):
    method: Literal["read_only_assessment"]
    budget: Quantity
    overhead: Quantity

    @model_validator(mode="after")
    def bounded(self) -> Self:
        if self.budget.component != self.overhead.component or Decimal(
            self.overhead.amount
        ) > Decimal(self.budget.amount):
            raise ValueError("assessment overhead exceeds compatible budget")
        return self


class DemandRecord(Record):
    version: Literal["demand/v1"] = "demand/v1"


class Assessment(DemandRecord):
    kind: Literal["task_assessment"] = "task_assessment"
    change: RecordRef
    dimensions: Dimensions
    scope_key: Identifier
    assessor: Annotated[str, Field(min_length=1, max_length=128)]
    evidence: Annotated[
        list[Annotated[str, Field(min_length=1, max_length=256)]], Field(max_length=16)
    ]
    rehearsal: Rehearsal | None = None


class MeasurementPolicy(Record):
    kind: Literal["demand_policy"] = "demand_policy"
    version: Identifier
    component: DemandComponent
    population: Literal["accepted_and_abandoned"] = "accepted_and_abandoned"


class Ecosystem(DemandRecord):
    kind: Literal["ecosystem"] = "ecosystem"
    provider: Identifier
    surface: Identifier
    model: Identifier | None
    model_version: Identifier | None
    runtime: Identifier | None
    reasoning: Identifier | None
    harness: Identifier | None
    review: Identifier | None
    measurement_policy: RecordRef


class DemandObservation(DemandRecord):
    kind: Literal["demand_observation"] = "demand_observation"
    run: RunRef
    assessment: RecordRef
    ecosystem: RecordRef
    component: DemandComponent
    quantity: Nonnegative | None
    start: Timestamp
    end: Timestamp
    final: Annotated[bool, Field(strict=True)]
    complete: Annotated[bool, Field(strict=True)]
    evidence: list[RecordRef]
    previous: RecordRef | None = None
    reason: Identifier | None = None

    @model_validator(mode="after")
    def bounds(self) -> Self:
        if self.start > self.end or self.end > self.recorded_at or not self.evidence:
            raise ValueError("invalid observation bounds or evidence")
        if (self.previous is None) != (self.reason is None):
            raise ValueError("correction requires predecessor and reason")
        return self


class MatchedComparison(DemandRecord):
    kind: Literal["matched_comparison"] = "matched_comparison"
    source_change: RecordRef
    target_change: RecordRef
    source_ecosystem: RecordRef
    target_ecosystem: RecordRef
    scope_key: Identifier
    confounding: list[Identifier] = Field(default_factory=list)


class TransferHypothesis(DemandRecord):
    kind: Literal["transfer_hypothesis"] = "transfer_hypothesis"
    source_ecosystem: RecordRef
    target_ecosystem: RecordRef
    component: DemandComponent
    dimensions: Dimensions
    method: Literal["median-ratio/v1"] = "median-ratio/v1"
    population: Literal["accepted_and_abandoned"] = "accepted_and_abandoned"
    comparisons: Annotated[list[RecordRef], Field(min_length=1)]


class PriceRate(Model):
    component: DemandComponent
    rate: Nonnegative


class PriceScenario(DemandRecord):
    kind: Literal["demand_price"] = "demand_price"
    effective_date: Timestamp
    source: Identifier
    currency: Annotated[str, Field(pattern=r"^[A-Z]{3}$")]
    rates: Annotated[list[PriceRate], Field(min_length=1)]

    @model_validator(mode="after")
    def unique_rates(self) -> Self:
        identities = [r.component.model_dump_json() for r in self.rates]
        if len(set(identities)) != len(identities):
            raise ValueError("duplicate rate identity")
        return self


class TransferResult(Model):
    hypothesis: RecordRef
    ratio: Rational
    pair_count: Annotated[int, Field(strict=True, gt=0)]
    donor_count: Annotated[int, Field(strict=True, gt=0)]
    donors: Annotated[list[RecordRef], Field(min_length=1)]
    cohort: Literal["dimensions"] = "dimensions"
    state: Literal["transfer_hypothesis"] = "transfer_hypothesis"
    scenarios: list[Rational]
    residuals: list[Rational]


def validate_observed_summaries(result):
    quantities = (result.minimum, result.median, result.maximum)
    if result.sample_count:
        if result.minimum is None or result.median is None or result.maximum is None:
            raise ValueError("invalid observed summaries")
        if not Decimal(result.minimum) <= Decimal(result.median) <= Decimal(result.maximum):
            raise ValueError("invalid observed summaries")
    elif any(q is not None for q in quantities):
        raise ValueError("unobserved summaries must be absent")


class DemandResult(Model):
    component: DemandComponent
    state: Literal["zero_knowledge", "learning", "transfer_hypothesis", "validated_forecast"]
    sample_count: Annotated[int, Field(strict=True, ge=0)]
    cohort: Literal["dimensions", "ecosystem"]
    minimum: Nonnegative | None = None
    median: Nonnegative | None = None
    maximum: Nonnegative | None = None
    transfer: TransferResult | None = None
    validation: RecordRef | None = None

    @model_validator(mode="after")
    def state_consistent(self) -> Self:
        validate_observed_summaries(self)
        if self.state == "zero_knowledge" and (self.sample_count or self.transfer):
            raise ValueError("zero knowledge contains no numeric estimate")
        if self.state == "transfer_hypothesis" and (self.transfer is None or self.sample_count):
            raise ValueError("transfer-only state requires scenario without target samples")
        if (self.state == "validated_forecast") != (self.validation is not None):
            raise ValueError("validation reference/state mismatch")
        if self.state in {"learning", "validated_forecast"} and not self.sample_count:
            raise ValueError("observed state requires samples")
        return self


class EstimatedPrice(Model):
    source: RecordRef
    currency: str
    amount: Rational
    basis: Literal["estimated"] = "estimated"


class DemandForecast(DemandRecord):
    kind: Literal["demand_forecast"] = "demand_forecast"
    change: RecordRef
    assessment: RecordRef
    ecosystem: RecordRef
    operation_id: Identifier
    algorithm: Literal["observed-summary/v1", "observed-summary/v2", "observed-summary/v3"] = (
        "observed-summary/v3"
    )
    cutoff: Cutoff
    result: DemandResult
    inputs: list[RecordRef]
    exclusions: list[Exclusion]
    peers: list[RecordRef]
    next_evidence: list[Identifier]
    price: EstimatedPrice | None = None
    price_request: RecordRef | None = None
    broad_baseline: Annotated[bool, Field(strict=True)] = False
    initial: Annotated[bool, Field(strict=True)]
    assumptions: list[Identifier]


class ValidationPolicy(DemandRecord):
    kind: Literal["demand_validation_policy"] = "demand_validation_policy"
    ecosystem: RecordRef
    component: DemandComponent
    population: Literal["accepted_and_abandoned"] = "accepted_and_abandoned"
    minimum_truth: Annotated[int, Field(strict=True, gt=0)]
    nominal_coverage: Rational
    coverage_tolerance: Rational
    maximum_underestimate: Rational
    maximum_width: Nonnegative
    maximum_overhead: Nonnegative
    require_baseline: Annotated[bool, Field(strict=True)]

    @model_validator(mode="after")
    def rubric(self) -> Self:
        from fractions import Fraction

        if (
            not 0 <= Fraction(self.nominal_coverage) <= 1
            or not 0 <= Fraction(self.coverage_tolerance) <= 1
            or Fraction(self.maximum_underestimate) < 0
        ):
            raise ValueError("invalid explicit validation rubric")
        return self


class ValidationCase(Model):
    forecast: RecordRef
    truth: RecordRef
    baseline: RecordRef | None = None


class ValidationMetrics(Model):
    count: Annotated[int, Field(strict=True, ge=0)]
    covered: Annotated[int, Field(strict=True, ge=0)]
    maximum_underestimate: Rational
    maximum_width: Rational
    maximum_overhead: Rational
    mean_error: Rational
    baseline_error: Rational | None = None


class DemandValidation(DemandRecord):
    kind: Literal["demand_validation"] = "demand_validation"
    policy: RecordRef
    cases: list[ValidationCase]
    metrics: ValidationMetrics
    passed: Annotated[bool, Field(strict=True)]
    operation_id: Identifier
    cutoff: Cutoff
    inputs: list[RecordRef]
    previous: RecordRef | None = None


PortableRecord = Annotated[
    Change
    | Run
    | Evidence
    | RunBinding
    | EvidenceBinding
    | Outcome
    | Interval
    | Quote
    | Settlement
    | EconomicEvidence
    | SourceCoverage
    | ComputedSettlement
    | Assessment
    | MeasurementPolicy
    | Ecosystem
    | DemandObservation
    | MatchedComparison
    | TransferHypothesis
    | PriceScenario
    | DemandForecast
    | ValidationPolicy
    | DemandValidation,
    Field(discriminator="kind"),
]


class Observation(Model):
    reference: RecordRef
    store_id: Identifier
    available_at: Timestamp
    sequence: Annotated[int, Field(strict=True, ge=1, le=MAX_SEQUENCE)]


class Bundle(Model):
    schema_version: Literal["changecost/v1"] = Field(default="changecost/v1", alias="schema")
    source: Cutoff
    records: list[PortableRecord]
    observations: list[Observation] = Field(default_factory=list)
