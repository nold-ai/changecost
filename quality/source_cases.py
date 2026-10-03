"""Synthetic semantic detectors; these are hypotheses, never provider approval."""

from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation

from quality.source_inspection import EvidenceError

STRATEGIES = dict(
    zip(
        [
            "cli-repeated-billing",
            "cli-missing-root",
            "multiplier-only",
            "ide-window-only",
            "tokens-only",
            "timestamp-only",
            "ambiguous-overlap",
            "correction",
            "codex-usage-snapshot",
            "claude-estimated-cost",
            "codex-rollout-cache-write",
            "claude-message-revisions",
            "cursor-context-not-consumption",
            "copilot-hosted-usage-boundaries",
            "enterprise-projection-boundaries",
            "copilot-container-absence",
            "enterprise-message-counter-boundary",
            "documented-example-not-wire-evidence",
        ],
        [
            "spans",
            "spans",
            "spans",
            "spans",
            "tokens",
            "tokens",
            "tokens",
            "replacement",
            "snapshot",
            "cumulative",
            "rollout",
            "messages",
            "context",
            "hosted",
            "projection",
            "containers",
            "counters",
            "encoding",
        ],
        strict=True,
    )
)


def _integer(value):
    if value is not None and (type(value) is not int or value < 0):
        raise EvidenceError("invalid-quantity")
    return value


def _decimal(value):
    try:
        if not isinstance(value, str):
            raise EvidenceError("invalid-decimal")
        number = Decimal(value)
        if not number.is_finite() or number < 0:
            raise EvidenceError("invalid-decimal")
        return number
    except InvalidOperation:
        raise EvidenceError("invalid-decimal") from None


def _spans(rows):
    roots = {}
    conflict = False
    for row in rows:
        attrs = row.get("attributes", {})
        if (
            attrs.get("gen_ai.operation.name") == "invoke_agent"
            and "parent_span_id" in row
            and row["parent_span_id"] is None
        ):
            identity = (attrs.get("gen_ai.conversation.id"), row.get("span_id"))
            amount = _integer(attrs.get("github.copilot.nano_aiu"))
            if (
                not all(identity)
                or amount is None
                or identity in roots
                and roots[identity] != amount
            ):
                conflict = True
            roots[identity] = amount
    amount = sum(roots.values()) if roots and not conflict else None
    return {
        "authoritative_nano_aiu": amount,
        "aggregate_billing": "unverified",
        "completeness": "unknown",
        "multiplier": rows[0].get("attributes", {}).get("github.copilot.cost"),
        "automatic_attribution": "unavailable_for_sample",
        "unbound_record_count": len(rows),
    }


def _tokens(rows):
    return {
        "input_tokens": _integer(rows[0].get("input_tokens")),
        "output_tokens": _integer(rows[0].get("output_tokens")),
        "cash_capability": "unavailable_for_sample",
        "automatic_attribution": "unavailable_for_sample",
        "unbound_record_count": len(rows),
        "completeness": "unresolved_overlap",
        "additive_total": None,
    }


def _replacement(rows):
    revisions = {}
    valid = True
    for row in rows:
        key = (row.get("event_id"), _integer(row.get("revision")))
        _decimal(row.get("amount"))
        if key in revisions and revisions[key] != row:
            valid = False
        revisions[key] = row
    ordered = sorted(revisions.values(), key=lambda r: r["revision"])
    valid = (
        valid
        and len({r.get("event_id") for r in rows}) == 1
        and len({r.get("currency") for r in rows}) == 1
    )
    valid = valid and bool(ordered[0].get("event_id")) and bool(ordered[0].get("currency"))
    valid = valid and "replaces_revision" not in ordered[0]
    for before, after in zip(ordered, ordered[1:], strict=False):
        valid = valid and after.get("replaces_revision") == before["revision"]
    return {
        "current_amount": ordered[-1]["amount"] if valid else None,
        "currency": ordered[-1].get("currency"),
        "retained_revision_count": len(revisions),
    }


def _snapshot(rows):
    identities = {(r.get("threadId"), r.get("turnId")) for r in rows}
    totals = {r["tokenUsage"]["total"].get("totalTokens") for r in rows}
    return {
        "snapshot_total_tokens": _integer(next(iter(totals)))
        if len(totals) == 1 and len(identities) == 1 and all(next(iter(identities)))
        else None
    }


def _cumulative(rows):
    keys = {
        (r.get("metric"), r.get("unit"), r.get("temporality"), r.get("interval_start"))
        for r in rows
    }
    ends = {}
    bound = all(r.get("metric") and r.get("interval_start") and r.get("interval_end") for r in rows)
    valid = (
        bound
        and len(keys) == 1
        and all(r.get("temporality") == "cumulative" and r.get("unit") == "USD" for r in rows)
    )
    for row in sorted(rows, key=lambda r: r.get("interval_end", "")):
        value = _decimal(row.get("value"))
        end = row.get("interval_end")
        if end in ends and ends[end] != value or ends and value < max(ends.values()):
            valid = False
        ends[end] = value
    latest = max(rows, key=lambda r: r.get("interval_end", ""))
    return {
        "estimate_amount": latest["value"] if valid else None,
        "currency": latest.get("unit"),
        "attribution": "unbound",
    }


def _rollout(rows):
    events = [r["payload"] for r in rows if r.get("payload", {}).get("type") == "token_count"]
    totals = {r["info"]["total_token_usage"].get("total_tokens") for r in events}
    sessions = {
        (r["payload"].get("id"), r["payload"].get("cli_version"))
        for r in rows
        if r.get("type") == "session_meta"
    }
    bound = len(sessions) == 1 and all(next(iter(sessions)))
    return {
        "cache_write_field": "present"
        if events
        and all("cache_write_input_tokens" in r["info"]["total_token_usage"] for r in events)
        else "absent",
        "token_event_turn_id": "present"
        if events and all(r.get("turn_id") for r in events)
        else "absent",
        "snapshot_total_tokens": _integer(next(iter(totals)))
        if bound and len(totals) == 1
        else None,
    }


def _messages(rows):
    variants = {json.dumps(r["message"].get("usage"), sort_keys=True) for r in rows}
    return {
        "record_count": len(rows),
        "request_count": len({r.get("requestId") for r in rows}),
        "message_count": len({r["message"].get("id") for r in rows}),
        "usage_variant_count": len(variants),
        "additive_total": None,
        "final_usage": "unverified",
    }


def _context(rows):
    occupancy = [r["contextTokensUsed"] for r in rows if "contextTokensUsed" in r]
    return {
        "context_occupancy_tokens": _integer(occupancy[0]) if len(occupancy) == 1 else None,
        "consumed_tokens": None,
        "session_finality": "unverified",
    }


def _checkpoint_identity(record, default_scope):
    # This optional per-record namespace is authored fixture context, not wire data.
    context = record.get("synthetic_context", {"sdk_session_id": default_scope})
    if not isinstance(context, dict):
        raise EvidenceError("case-shape")
    identity = (context.get("sdk_session_id"), record.get("id"))
    return identity if all(isinstance(v, str) and v.strip() for v in identity) else None


def _checkpoint_conflicts(rows, scope):
    amounts = {}
    unresolved = False
    conflict = False
    for record in rows:
        if record.get("type") != "session.usage_checkpoint":
            continue
        data = record.get("data", {})
        if not isinstance(data, dict):
            raise EvidenceError("case-shape")
        amount = _integer(data.get("totalNanoAiu"))
        identity = _checkpoint_identity(record, scope)
        if amount is None or identity is None:
            unresolved = True
            continue
        conflict = conflict or (identity in amounts and amounts[identity] != amount)
        amounts[identity] = amount
    if conflict:
        return True
    return None if unresolved else False


def _hosted(rows, sample):
    identity = sample.get("identity_evidence", {})
    return {
        "identity_namespaces_distinct": bool(
            identity.get("host_session_id")
            and identity.get("sdk_session_id")
            and identity["host_session_id"] != identity["sdk_session_id"]
        ),
        "checkpoint_conflict": _checkpoint_conflicts(rows, identity.get("sdk_session_id")),
        "overlapping_totals_additive": False,
        "missing_ephemeral_usage_is_zero": False,
        "final_session_nano_aiu": None,
    }


def _projection(rows):
    return {
        "cross_session_overlap": "unverified",
        # Synthetic shape probes cannot establish native wire compatibility.
        "native_wire_compatible": False,
        "consumed_tokens": None,
        "billing_correction_observed": any("replaces_revision" in r for r in rows),
    }


def _containers(rows):
    exported = any(r.get("payload_exported") for r in rows)
    return {
        "payload_export_reported": exported,
        "sdk_usage_checkpoint": "not inspected",
        "per_session_turn_usage": "not inspected",
        "consumed_tokens": None,
        "host_to_sdk_join": "unverified",
    }


def _counters(rows):
    integers = all(
        type(r.get("v", {}).get("metadata", {}).get(k)) is int
        for r in rows
        for k in ("promptTokens", "outputTokens")
    )
    return {
        "field_type_evidence": "producer-reported integer paths" if integers else "unverified",
        "repeat_semantics": "unverified",
        "host_to_sdk_binding": "unverified",
        "cache_inclusion": "unverified",
        "additive_session_tokens": None,
    }


def _encoding(rows):
    values = [r.get("aggregationTemporality") for r in rows]
    return {
        "string_enum_valid_otlp_json": False,
        "integer_enum_valid_for_delta": any(type(v) is int and v == 1 for v in values),
        "native_export_observed": False,
        "hook_mapping_verified": False,
    }


_DETECTORS = {
    "spans": _spans,
    "tokens": _tokens,
    "replacement": _replacement,
    "snapshot": _snapshot,
    "cumulative": _cumulative,
    "rollout": _rollout,
    "messages": _messages,
    "context": _context,
    "projection": _projection,
    "containers": _containers,
    "counters": _counters,
    "encoding": _encoding,
}


def evaluate_case(sample, strategy):
    try:
        rows = sample["records"]
        if not isinstance(rows, list) or not rows or not all(isinstance(r, dict) for r in rows):
            raise EvidenceError("case-shape")
        result = _hosted(rows, sample) if strategy == "hosted" else _DETECTORS[strategy](rows)
        return {"billed_money": None, "approved_profile": False, **result}
    except (KeyError, TypeError, IndexError):
        raise EvidenceError("case-shape") from None
