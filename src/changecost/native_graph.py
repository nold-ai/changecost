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
        evidence.provider != "Codex"
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
