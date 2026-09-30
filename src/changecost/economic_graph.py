"""Reference and correction invariants shared by portable and normalized import."""

import json

from changecost.models import (
    Change,
    ComputedSettlement,
    EconomicEvidence,
    EconomicIdentity,
    Evidence,
    EvidenceBinding,
    Interval,
    Outcome,
    Run,
    RunBinding,
    SourceCoverage,
    SourceLocator,
)
from changecost.operations import stable_id
from changecost.serialization import ContractError


def source_key(source: SourceLocator) -> str:
    return json.dumps(source.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))


def evidence_id(source: SourceLocator) -> str:
    return stable_id("normalized_evidence", source_key(source))


def economic_key(record: EconomicEvidence) -> tuple[str, str]:
    return source_key(record.source), record.component_key


def economic_identity(component) -> EconomicIdentity:
    return EconomicIdentity.model_validate(component.model_dump(exclude={"amount"}))


def partition(source: SourceLocator) -> tuple:
    return (source.repository_id, source.provider, source.surface, source.profile, source.namespace)


def validate_replacement(record: EconomicEvidence, prior: EconomicEvidence) -> None:
    if (record.series, record.lane, record.start, record.end) != (
        prior.series,
        prior.lane,
        prior.start,
        prior.end,
    ):
        raise ContractError("replacement changes source subject/window")
    before, after = economic_identity(prior.component), economic_identity(record.component)
    if before.model_dump(exclude={"currency"}) != after.model_dump(exclude={"currency"}):
        raise ContractError("replacement changes economic identity")
    if before.currency != after.currency and (
        before.currency is not None or prior.component.amount is not None
    ):
        raise ContractError("replacement changes known currency")


def correction_graph(records: dict) -> dict:
    events = {economic_key(r): r for r in records.values() if isinstance(r, EconomicEvidence)}
    edges, children = {}, set()
    bindings = {
        r.evidence.record_id: r.run for r in records.values() if isinstance(r, EvidenceBinding)
    }
    for identity, record in events.items():
        if record.replaces is None:
            continue
        if partition(record.source) != partition(record.replaces):
            raise ContractError("cross-source correction")
        target = (source_key(record.replaces), record.component_key)
        if target in children:
            raise ContractError("correction history forks")
        children.add(target)
        edges[identity] = target
        if target in events:
            prior = events[target]
            validate_replacement(record, prior)
            left, right = (
                bindings.get(record.evidence.record_id),
                bindings.get(prior.evidence.record_id),
            )
            if left is not None and right is not None and left != right:
                raise ContractError("replacement changes attribution subject")
    for node in edges:
        validate_chain_subject(node, edges, events, bindings)
    return edges


def require(records: dict, ref, kind: str):
    record = records.get((ref.kind, ref.record_id))
    if ref.kind != kind or record is None:
        raise ContractError("invalid economic record reference")
    return record


def economic_refs(record: EconomicEvidence, records: dict) -> list:
    evidence = require(records, record.evidence, "evidence")
    if not isinstance(evidence, Evidence) or (
        evidence.provider,
        evidence.surface,
        evidence.profile,
        evidence.source_key,
    ) != (
        record.source.provider,
        record.source.surface,
        record.source.profile,
        evidence_id(record.source),
    ):
        raise ContractError("economic evidence identity mismatch")
    for binding in records.values():
        if (
            isinstance(binding, EvidenceBinding)
            and binding.evidence == record.evidence
            and binding.run.repository_id != record.source.repository_id
        ):
            raise ContractError("cross-repository economic binding")
    return [record.evidence]


def source_refs(record: SourceCoverage, records: dict, runs: dict) -> list:
    run = runs.get(tuple(record.run.model_dump().values()))
    if run is None:
        raise ContractError("unknown coverage Run")
    bindings = {
        r.evidence.record_id: r.run for r in records.values() if isinstance(r, EvidenceBinding)
    }
    for ref in record.evidence:
        require(records, ref, "evidence")
        if bindings.get(ref.record_id) != record.run:
            raise ContractError("source coverage evidence subject mismatch")
    from changecost.store import reference

    return [reference(run), *record.evidence]


def computed_refs(record: ComputedSettlement, records: dict, runs: dict) -> list:
    change = require(records, record.change, "change")
    if not isinstance(change, Change) or change.repository_id != record.scope.repository_id:
        raise ContractError("computed scope mismatch")
    members, membership_refs = computed_membership(record, records, runs, change)
    refs = [record.change, *record.inputs, *(e.reference for e in record.exclusions)]
    refs.extend(membership_refs)
    for exclusion in record.exclusions:
        item = require(records, exclusion.reference, "economic_evidence")
        if item.source.repository_id != record.scope.repository_id:
            raise ContractError("computed exclusion scope mismatch")
    for ref in record.inputs:
        validate_computed_input(record, records, ref, members)
    if record.previous is not None:
        refs.append(record.previous)
    return refs


def validate_economics(records: dict) -> None:
    seen = set()
    for record in records.values():
        if isinstance(record, EconomicEvidence):
            identity = economic_key(record)
            if identity in seen:
                raise ContractError("conflicting economic source identity")
            seen.add(identity)
    correction_graph(records)


def validate_chain_subject(node, edges, events, bindings):
    seen, subjects = set(), set()
    while node in events:
        if node in seen:
            raise ContractError("cyclic correction graph")
        seen.add(node)
        binding = bindings.get(events[node].evidence.record_id)
        if binding is not None:
            subjects.add(tuple(binding.model_dump().values()))
        if len(subjects) > 1:
            raise ContractError("replacement changes attribution subject")
        if node not in edges:
            return
        node = edges[node]


def validate_computed_input(record, records, ref, members):
    from changecost.store import key

    item = records.get(key(ref))
    allowed = {
        "change",
        "run",
        "run_binding",
        "evidence_binding",
        "outcome",
        "interval",
        "evidence",
        "economic_evidence",
        "source_coverage",
    }
    if item is None or ref.kind not in allowed:
        raise ContractError("invalid computed input role")
    validate_computed_subject(record, item, members)


def validate_computed_subject(record, item, members):
    from changecost.store import key, reference

    if isinstance(item, Change) and reference(item) != record.change:
        raise ContractError("computed Change subject mismatch")
    if isinstance(item, Outcome) and key(item.subject) not in members | {key(record.change)}:
        raise ContractError("computed outcome subject mismatch")
    if isinstance(item, (Interval, SourceCoverage, RunBinding)) and item.run not in record.runs:
        raise ContractError("computed Run dependency mismatch")
    if isinstance(item, Run) and item.ref not in record.runs:
        raise ContractError("computed Run dependency mismatch")
    if (
        isinstance(item, EconomicEvidence)
        and item.source.repository_id != record.scope.repository_id
    ):
        raise ContractError("computed economic input scope mismatch")
    if isinstance(item, EvidenceBinding) and item.run.repository_id != record.scope.repository_id:
        raise ContractError("computed binding scope mismatch")


def computed_membership(record, records, runs, change):
    from changecost.store import key, reference

    members = set()
    refs = []
    for member in record.runs:
        run = runs.get(tuple(member.model_dump().values()))
        if run is None or member.repository_id != change.repository_id:
            raise ContractError("invalid computed membership")
        binding = next(
            (
                r
                for r in records.values()
                if isinstance(r, RunBinding) and r.run == member and r.change == record.change
            ),
            None,
        )
        if binding is None or key(reference(run)) in members:
            raise ContractError("invalid computed membership binding")
        members.add(key(reference(run)))
        refs.extend([reference(run), reference(binding)])
    return members, refs
