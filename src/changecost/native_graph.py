from changecost.models import Evidence, NativeUsage
from changecost.serialization import ContractError


def native_subject(record: NativeUsage) -> tuple:
    return (
        record.repository_id,
        record.event_identity,
        record.source_category,
        record.accounting_scope,
    )


def native_refs(record: NativeUsage, records, bindings):
    from changecost.store import key, lookup

    evidence = lookup(records, record.evidence, "evidence")
    if not isinstance(evidence, Evidence) or (
        evidence.provider not in {"Codex", "Claude"}
        or evidence.surface != record.producer.client_surface
        or evidence.identity_scope != "namespaced"
        or evidence.source_key != record.event_identity
    ):
        raise ContractError("invalid native evidence subject")
    binding = bindings.get(key(record.evidence))
    if binding is not None and binding.run.repository_id != record.repository_id:
        raise ContractError("native repository binding mismatch")
    return [record.evidence, *([record.previous] if record.previous else [])]


def validate_native(records):
    events = {}
    for record in records.values():
        if not isinstance(record, NativeUsage):
            continue
        meaning = (
            record.repository_id,
            record.evidence,
            record.producer.model_dump_json(),
            record.ownership.model_dump_json(),
        )
        if record.event_identity in events and events[record.event_identity] != meaning:
            raise ContractError("conflicting native event repository or evidence")
        events[record.event_identity] = meaning
    _validate_claude(records)


def _claude_association_valid(record, evidence, envelope):
    policy = envelope["admission"]
    return (
        evidence.provider == "Claude"
        and evidence.surface == "project-jsonl"
        and evidence.record_id == record.event_identity
        and evidence.profile == envelope["profile_id"]
        and record.mapping_revision == policy["mapping_revision"]
        and record.producer.model_dump() == policy["producer"]
        and record.first_admission.model_dump()
        == {
            "profile_digest": envelope["profile_digest"],
            "approval_digest": envelope["approval_digest"],
        }
    )


def _claude_stage_valid(record, selected):
    if selected.kind == "desktop308":
        return (
            record.finality == "final"
            and record.quantity is not None
            and record.previous is None
            and record.reason is None
        )
    return record.finality in {"partial", "final"}


def _claude_diagnostics_valid(record):
    return (
        record.model is None
        and record.model_version is None
        and record.interval.state == "unknown"
        and record.scope_completeness == "unknown"
        and record.ownership.state == "unknown"
        and record.ownership.session is not None
        and all(
            value is None
            for key, value in record.ownership.model_dump().items()
            if key not in {"state", "session"}
        )
    )


def _claude_record_valid(record, evidence, selected):
    from changecost.claude_local import _revision_id

    return (
        _claude_association_valid(record, evidence, selected.envelope)
        and record.source_category in selected.envelope["admission"]["source_categories"].values()
        and record.accounting_scope == "request"
        and _claude_stage_valid(record, selected)
        and _claude_diagnostics_valid(record)
        and record.record_id == _revision_id(record)
    )


def _claude_cohort_validations(cohort, policy):
    if set(cohort) != set(policy["source_categories"].values()):
        raise ContractError("incomplete Claude stage cohort")
    availability = {(r.origin_store_id, r.recorded_at, r.effective_at) for r in cohort.values()}
    if len(availability) != 1:
        raise ContractError("incoherent Claude stage cohort availability")


def _claude_refinement(record, predecessor, policy):
    expected = None if predecessor is None else ("native_usage", predecessor.record_id)
    actual = None if record.previous is None else (record.previous.kind, record.previous.record_id)
    reason = policy["refinement_reason"] if predecessor is not None else None
    if actual != expected or record.reason != reason:
        raise ContractError("invalid Claude refinement predecessor or reason")


def _claude_cohorts(event, policy):
    stages = {}
    provenance = set()
    for record in event:
        stage = stages.setdefault(record.finality, {})
        if record.source_category in stage:
            raise ContractError("conflicting Claude stage cohort")
        stage[record.source_category] = record
        provenance.add(
            (
                record.first_acquisition_digest,
                record.first_admission.model_dump_json(),
                record.mapping_revision,
            )
        )
    if len(provenance) != 1:
        raise ContractError("conflicting Claude first provenance")
    for cohort in stages.values():
        _claude_cohort_validations(cohort, policy)
    partial = stages.get("partial", {})
    for stage, cohort in stages.items():
        for category, record in cohort.items():
            predecessor = partial.get(category) if stage == "final" else None
            _claude_refinement(record, predecessor, policy)


def _has_claude_claim(record, evidence, envelope):
    policy = envelope["admission"]
    return any(
        (
            evidence.provider == "Claude",
            evidence.surface == policy["producer"]["client_surface"],
            record.producer.client_surface == policy["producer"]["client_surface"],
            record.mapping_revision == policy["mapping_revision"],
            evidence.profile == envelope["profile_id"],
            record.first_admission.profile_digest == envelope["profile_digest"],
            record.first_admission.approval_digest == envelope["approval_digest"],
        )
    )


def _validate_claude(records):
    from changecost.claude_local import _claude_admissions

    catalogue = _claude_admissions()
    events = {}
    for record in records.values():
        if not isinstance(record, NativeUsage):
            continue
        evidence = records.get((record.evidence.kind, record.evidence.record_id))
        if not isinstance(evidence, Evidence):
            continue
        if not any(_has_claude_claim(record, evidence, item.envelope) for item in catalogue):
            continue
        selected = next(
            (item for item in catalogue if item.envelope["profile_id"] == evidence.profile), None
        )
        if selected is None or not _claude_record_valid(record, evidence, selected):
            raise ContractError("unapproved Claude native association or meaning")
        event = events.setdefault(record.event_identity, (selected, []))
        if event[0] != selected:
            raise ContractError("conflicting Claude event profiles")
        event[1].append(record)
    for selected, event in events.values():
        _claude_cohorts(event, selected.envelope["admission"])
