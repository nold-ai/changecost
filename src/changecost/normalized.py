"""Strict local normalized input, never a provider parser or collector."""

import json
from typing import Literal

from pydantic import Field, ValidationError

from changecost.economic_graph import economic_key, evidence_id
from changecost.models import EconomicEvidence, EconomicInput, Evidence, Identifier, Model
from changecost.operations import common, stable_id
from changecost.serialization import ContractError, reject_constant, unique_members
from changecost.store import Store, key, reference

MAX_RECORDS = 100000
MAX_INPUT_BYTES = 32 * 1024 * 1024


class NormalizedBatch(Model):
    schema_version: Literal["changecost/normalized-v1"] = Field(alias="schema")
    repository_id: Identifier
    batch_id: Identifier
    events: list[EconomicInput] = Field(max_length=MAX_RECORDS)


def load_input(text: str) -> dict:
    if len(text.encode()) > MAX_INPUT_BYTES:
        raise ContractError("normalized input size limit exceeded")
    try:
        return json.loads(text, object_pairs_hook=unique_members, parse_constant=reject_constant)
    except (ValueError, RecursionError) as exc:
        raise ContractError("invalid normalized JSON") from exc


def normalized_records(event: EconomicInput, store_id, now):
    ident = evidence_id(event.source)
    evidence = Evidence(
        **common(store_id, now, ident),
        provider=event.source.provider,
        surface=event.source.surface,
        profile=event.source.profile,
        identity_scope="namespaced",
        source_key=ident,
    )
    payload = common(store_id, now, stable_id("economic", ident, event.component_key))
    payload["effective_at"] = event.start
    economic = EconomicEvidence(**payload, evidence=reference(evidence), **event.model_dump())
    return evidence, economic


def import_evidence(store: Store, data: object, repository_id: str) -> list[str]:
    try:
        if isinstance(data, NormalizedBatch):
            data = data.model_dump(by_alias=True, warnings=False)
        batch = NormalizedBatch.model_validate(data)
        if batch.repository_id != repository_id or any(
            e.source.repository_id != repository_id for e in batch.events
        ):
            raise ContractError("normalized repository scope mismatch")
    except ValidationError as exc:
        raise ContractError("invalid normalized fields or values") from exc

    def operation(records, store_id, now):
        existing = {economic_key(r): r for r in records.values() if isinstance(r, EconomicEvidence)}
        additions, selectors = [], []
        for event in batch.events:
            evidence, economic = normalized_records(event, store_id, now)
            identity = economic_key(economic)
            prior = existing.get(identity)
            if prior is not None:
                prior_input = {k: getattr(prior, k) for k in event.model_dump()}
                if EconomicInput.model_validate(prior_input) != event:
                    raise ContractError("conflicting normalized source semantics")
                selectors.append(prior.evidence.record_id)
                continue
            evidence = next(
                (
                    r
                    for r in records.values()
                    if isinstance(r, Evidence)
                    and r.source_key == evidence.source_key
                    and (r.provider, r.surface, r.profile)
                    == (evidence.provider, evidence.surface, evidence.profile)
                ),
                evidence,
            )
            if key(reference(evidence)) not in records:
                records[key(reference(evidence))] = evidence
                additions.append(evidence)
            economic = economic.model_copy(
                update={"evidence": reference(records[key(reference(evidence))])}
            )
            existing[identity] = economic
            additions.append(economic)
            selectors.append(evidence.record_id)
        return additions, list(dict.fromkeys(selectors))

    return store.apply(operation)
