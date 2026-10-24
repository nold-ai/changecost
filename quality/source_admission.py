"""Pure development checks for the finite request-observation admission contract.

Structural validity does not authenticate approval or the projection commitment.
"""

import re
from urllib.parse import urlsplit

PROJECTION_SCHEMA = {
    "schema": "codex-native-projection-v1",
    "canonical_json": (
        "UTF-8 json.dumps(sort_keys=True,separators=(comma,colon),"
        "ensure_ascii=True,allow_nan=False); exact integers; unique facts sorted by fact_key"
    ),
    "event_key_recipe": [
        "codex-request-event-v1",
        "Codex",
        "desktop-coding",
        "original_thread_id",
        "original_response_id",
    ],
    "fact_key_recipe": ["codex-request-fact-v1", "event_key", "request", "source_category"],
    "source_id_recipe": ["codex-source-id-v1", "kind(thread,turn,session)", "raw_source_value"],
    "fact_object_keys": [
        "backend_presence",
        "category",
        "completeness",
        "coverage",
        "event_key",
        "fact_key",
        "finality",
        "mapping_revision",
        "model",
        "model_version",
        "producer",
        "quantity",
        "quantity_basis",
        "request_interval",
        "scope",
        "source_lineage",
    ],
    "lineage_keys": ["header_parent_thread", "root_turn", "session", "thread", "turn"],
    "fixed_meaning": {
        "mapping_revision": "codex-request-observation-r1",
        "scope": "request",
        "quantity_basis": "serialized_source",
        "backend_presence": "unknown",
        "request_interval": "unknown",
        "model": None,
        "model_version": None,
        "coverage": "partial_observed_subset",
        "completeness": "unknown",
        "finality": "unknown",
    },
    "quantity": (
        "exact nonnegative JSONinteger,notbool;4096digitbound; "
        "selectedrequiredcategoryabsence rejects"
    ),
    "ignored_provenance": [
        "source_sha256",
        "profile_digest",
        "approval_digest",
        "source_ordinal",
        "first_local_availability",
        "admitted_snapshot_reference",
    ],
}

EXCLUDED_MEANINGS = {
    "session_meta": (
        "source metadata; producer claim independently reviewed, never inferred by runtime"
    ),
    "response_item": "private model/tool content; no quantities or corrections selected",
    "world_state": "model-visible context comparison baseline/patch; not usage authority",
    "turn_context": "configured context/model metadata; no served model join",
    "inter_agent_communication_metadata": (
        "causal trigger metadata; not usage or correction authority"
    ),
    "event_msg": "task/item lifecycle and overlapping token_count snapshots; no additive authority",
}

LIMITS = {"bytes": 10485760, "records": 10000, "depth": 32, "token_digits": 4096}

DECISIONS = {"authority", "interval", "replay", "reset", "correction", "exclusions"}
ADMISSION_KEYS = {
    "kind",
    "mapping_revision",
    "source_sha256",
    "format",
    "accepted_records",
    "expected_request_count",
    "expected_fact_count",
    "whole_record_count",
    "projection_sha256",
    "projection_schema",
    "classification",
    "producer_claim",
    "limits",
    "decisions",
}


def _shape(value, keys):
    return isinstance(value, dict) and set(value) == set(keys)


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _hash(value):
    return isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) is not None


def _count(value, minimum=0):
    return type(value) is int and minimum <= value <= 10000


def _https(value):
    if not isinstance(value, str):
        return False
    parsed = urlsplit(value)
    return parsed.scheme == "https" and bool(parsed.hostname)


def _classification_valid(c, a):
    if not _shape(
        c,
        {
            "records",
            "outer_record_counts",
            "event_payload_type_counts",
            "accepted_records",
            "contributing_outer_kind",
            "excluded_outer_kind_meanings",
            "source_refs",
        },
    ):
        return False
    refs = c["source_refs"]
    return (
        _classification_counts_valid(c, a)
        and c["accepted_records"] == a["accepted_records"]
        and all(type(v) is int for v in c["accepted_records"])
        and c["contributing_outer_kind"] == "token_usage_record"
        and c["excluded_outer_kind_meanings"] == EXCLUDED_MEANINGS
        and _shape(refs, {"rollout_variants", "world_state", "request_record"})
        and all(_https(v) for v in refs.values())
    )


def _classification_counts_valid(c, a):
    outer = c["outer_record_counts"]
    return (
        _count(c["records"], 1)
        and c["records"] == a["whole_record_count"]
        and _shape(outer, {*EXCLUDED_MEANINGS, "token_usage_record"})
        and all(_count(v) for v in outer.values())
        and sum(outer.values()) == c["records"]
        and outer["token_usage_record"] == a["expected_request_count"]
        and _event_counts_valid(c["event_payload_type_counts"], outer, a)
    )


def _event_counts_valid(events, outer, a):
    return (
        _shape(
            events,
            {
                "task_started",
                "thread_settings_applied",
                "item_completed",
                "token_count",
                "task_complete",
            },
        )
        and all(_count(v) for v in events.values())
        and sum(events.values()) == outer["event_msg"]
        and events["token_count"] == a["expected_request_count"]
    )


def _producer_valid(profile, a):
    claim = a["producer_claim"]
    schema = a["projection_schema"]
    if not _shape(
        claim,
        {
            "engine_version",
            "client_surface",
            "client_build",
            "trust",
            "corroboration_artifact_sha256",
            "claim_scope",
        },
    ):
        return False
    producer = {k: claim[k] for k in ("engine_version", "client_surface", "client_build")}
    return (
        profile["provider"] == "Codex"
        and claim["engine_version"] == profile["version"]
        and _text(claim["engine_version"])
        and claim["client_surface"] == "desktop-coding"
        and profile["surface"]
        == "Desktop coding-subagent serialized request observations; finite exact snapshot"
        and claim["client_build"] is None
        and _text(claim["trust"])
        and _text(claim["claim_scope"])
        and _hash(claim["corroboration_artifact_sha256"])
        and _shape(schema, {*PROJECTION_SCHEMA, "producer"})
        and schema["producer"] == producer
        and all(schema[k] == v for k, v in PROJECTION_SCHEMA.items())
    )


def admission_valid(profile, evidence):
    """Check finite metadata and native proof relations without reading any source."""
    if "admission" not in profile:
        return not (
            profile["provider"] == "Codex" and profile["capabilities"]["usage"] == "supported"
        )
    a = profile["admission"]
    if not _shape(a, ADMISSION_KEYS):
        return False
    return (
        _mapping_valid(profile, a)
        and _membership_valid(a)
        and _admission_policy_valid(a)
        and _classification_valid(a["classification"], a)
        and _producer_valid(profile, a)
        and _native_usage_proof_valid(profile, evidence, a)
    )


def _mapping_valid(profile, a):
    return (
        profile["capabilities"]
        == {
            "usage": "supported",
            "attribution": "partial",
            "billed_money": "unverified",
            "finality": "unverified",
        }
        and a["kind"] == "finite-snapshot-admission-v1"
        and a["mapping_revision"] == "codex-request-observation-r1"
        and a["format"] == "jsonl"
        and _hash(a["source_sha256"])
        and _hash(a["projection_sha256"])
    )


def _membership_valid(a):
    records = a["accepted_records"]
    return (
        _count(a["whole_record_count"], 1)
        and _count(a["expected_request_count"], 1)
        and type(a["expected_fact_count"]) is int
        and a["expected_fact_count"] == 6 * a["expected_request_count"]
        and isinstance(records, list)
        and all(type(v) is int and 0 <= v < a["whole_record_count"] for v in records)
        and records == sorted(set(records))
        and len(records) == a["expected_request_count"]
    )


def _admission_policy_valid(a):
    return (
        _shape(a["limits"], LIMITS)
        and all(type(a["limits"][k]) is int and a["limits"][k] == v for k, v in LIMITS.items())
        and _shape(a["decisions"], DECISIONS)
        and all(_text(v) for v in a["decisions"].values())
    )


def _native_usage_proof_valid(profile, evidence, a):
    proofs = [p for p in profile["approvals"] if p["capability"] == "usage"]
    return len(proofs) == 1 and (
        proofs[0]["sha256"] == a["source_sha256"]
        and proofs[0]["decisions"] == a["decisions"]
        and evidence[proofs[0]["evidence_id"]]["origin"] == "native"
        and evidence[proofs[0]["evidence_id"]]["sha256"] == a["source_sha256"]
    )
