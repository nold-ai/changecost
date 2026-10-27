"""Closed experiment inputs and immutable checkpoint results."""

from dataclasses import dataclass
from fractions import Fraction
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from changecost.models import Bundle, EconomicScope, Identifier, RecordRef, Timestamp


class ExperimentModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)


class Delivery(ExperimentModel):
    at: Timestamp
    records: tuple[RecordRef, ...]


class SyntheticHistory(ExperimentModel):
    schema_version: Literal["changecost/synthetic-evaluation-history-v1"] = Field(alias="schema")
    provenance: Literal["synthetic_fixture_only"]
    bundle: Bundle
    deliveries: tuple[Delivery, ...]


class AdaptiveSelection(ExperimentModel):
    assessment: RecordRef
    ecosystem: RecordRef
    policy: RecordRef
    rehearsal_assessment: RecordRef | None = None


class EvaluationCase(ExperimentModel):
    id: Identifier
    change: RecordRef
    forecast_at: Timestamp
    truth_at: Timestamp
    adaptive: AdaptiveSelection | None = None
    imported_forecast: RecordRef | None = None
    updates: tuple[Timestamp, ...] = ()

    @model_validator(mode="after")
    def chronology(self):
        if self.change.kind != "change" or self.forecast_at >= self.truth_at:
            raise ValueError("invalid case chronology")
        if any(at <= self.forecast_at for at in self.updates):
            raise ValueError("invalid update chronology")
        if len(set(self.updates)) != len(self.updates):
            raise ValueError("duplicate update")
        return self


class EvaluationProtocol(ExperimentModel):
    schema_version: Literal["changecost/evaluation-protocol-v1"] = Field(alias="schema")
    version: Identifier
    provenance: Literal["synthetic_fixture_only"]
    registered_at: Timestamp
    economic_scope: EconomicScope
    economic_minimum: Annotated[int, Field(strict=True)]
    minimum_independent_truth: Annotated[int, Field(strict=True, gt=0)]
    formula: Literal["exact-errors-wilson95-scenario-median/v1"]
    methods: tuple[Literal["repository", "dimensional", "transfer", "rehearsal"], ...]
    cases: tuple[EvaluationCase, ...]
    observation_at: Timestamp
    source_gaps: tuple[
        Literal[
            "native_truth_unapproved",
            "cursor_money_unverified",
            "small_sample",
            "provider_unavailable",
        ],
        ...,
    ]

    @model_validator(mode="after")
    def registration(self):
        if self.economic_minimum != 20 or self.economic_scope.start is not None:
            raise ValueError("evaluation needs full-change minimum twenty")
        if (
            set(self.methods) != {"repository", "dimensional", "transfer", "rehearsal"}
            or len(self.methods) != 4
        ):
            raise ValueError("register all comparison methods")
        if not self.cases or len({c.id for c in self.cases}) != len(self.cases):
            raise ValueError("duplicate or missing cases")
        if len({(c.change.kind, c.change.record_id) for c in self.cases}) != len(self.cases):
            raise ValueError("one initial case per Change")
        if any(self.registered_at >= c.forecast_at for c in self.cases):
            raise ValueError("protocol is not preregistered")
        if self.observation_at < max(c.truth_at for c in self.cases):
            raise ValueError("observation precedes truth")
        return self


@dataclass(frozen=True)
class ScoredTruth:
    amount: Fraction
    outcome: str
    attempts: tuple[str, ...]
    dependencies: tuple[RecordRef, ...]


@dataclass(frozen=True)
class OmittedTruth:
    reasons: tuple[str, ...]
    attempts: tuple[str, ...]
    dependencies: tuple[RecordRef, ...]


Truth = ScoredTruth | OmittedTruth
