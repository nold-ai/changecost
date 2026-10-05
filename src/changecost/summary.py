"""Allowlisted, bounded Actions summaries; untrusted values remain data."""

from __future__ import annotations

import argparse
import json
import os
import unicodedata
from decimal import Decimal
from itertools import chain
from pathlib import Path

from changecost.advisory import compare
from changecost.models import Component, Cutoff, EconomicScope
from changecost.serialization import reject_constant, unique_members

LIMIT = 65_536
NOTICE = "\n\nSummary truncated to the 64 KiB display limit.\n"
ECONOMIC = ("amount", "economic_kind", "unit", "basis", "currency")


def escaped_tokens(value):
    for char in str(value):
        if unicodedata.category(char) in {"Cc", "Cf", "Cs"}:
            yield f"\\u{ord(char):04x}"
        elif char in "&<>\"'\\`*_{}[]()#+-.!|~":
            yield f"&#{ord(char)};"
        else:
            yield char


def validate_component(component, *, budget=False):
    if not isinstance(component, dict):
        raise ValueError("invalid component")
    value = Component.model_validate({k: component.get(k) for k in ECONOMIC})
    if budget:
        from decimal import Decimal

        if value.amount is None or Decimal(value.amount) < 0:
            raise ValueError("invalid budget")
    if "unknown_count" in component and (
        type(component["unknown_count"]) is not int or component["unknown_count"] < 0
    ):
        raise ValueError("invalid completeness")
    return value


def validate_authority(value):
    provenance = value.get("provenance")
    local = "locally_reproduced_synthetic; provider_support_not_verified"
    producer = "producer_assertion; provider_support_not_verified"
    if provenance not in (local, producer) or value.get("completeness") not in (
        "complete",
        "unknown",
    ):
        raise ValueError("invalid detail")
    if provenance == producer and value["completeness"] != "unknown":
        raise ValueError("producer completeness is unknown")
    if provenance == local and (
        value["record"]["kind"] == "settlement" or value.get("cutoff") is None
    ):
        raise ValueError("invalid local authority")


def validate_details(value):
    validate_authority(value)
    sample = value.get("sample_count")
    kind = value["record"]["kind"]
    if kind == "quote":
        if type(sample) is not int or sample < 0 or value.get("quantile") not in ("p50", "p90"):
            raise ValueError("invalid Quote details")
    elif sample is not None or value.get("quantile") is not None:
        raise ValueError("invalid Settlement details")
    scope = value.get("scope")
    if kind != "settlement":
        if not isinstance(scope, dict) or value.get("cutoff") is None:
            raise ValueError("missing computation scope or cutoff")
        EconomicScope.model_validate(scope)
        Cutoff.model_validate(value["cutoff"])
    elif value.get("cutoff") is not None or (scope is not None and not isinstance(scope, str)):
        raise ValueError("invalid legacy scope")


def validate_result(value):
    if not isinstance(value, dict) or value.get("schema") != "changecost/check-v1":
        raise ValueError("invalid check result")
    if value.get("status") not in ("within_budget", "over_budget", "unknown"):
        raise ValueError("invalid advisory status")
    record = value.get("record")
    if (
        not isinstance(record, dict)
        or record.get("kind") not in ("quote", "computed_settlement", "settlement")
        or not isinstance(record.get("record_id"), str)
    ):
        raise ValueError("invalid record")
    if record["kind"] == "settlement" and value["status"] != "unknown":
        raise ValueError("legacy settlement cannot have verified advice")
    budget = validate_component(value.get("budget"), budget=True)
    validate_reasons(value)
    validate_details(value)
    declared = value.get("declared")
    if not isinstance(declared, list):
        raise ValueError("invalid declarations")
    for component in declared:
        validate_component(component)
    if record["kind"] == "quote":
        validate_quote_declarations(value)
    validate_local_completeness(value, budget)
    validate_comparison(value, budget)


def validate_reasons(value):
    reasons = value.get("reasons")
    if not isinstance(reasons, list) or any(not isinstance(reason, str) for reason in reasons):
        raise ValueError("invalid reasons")
    if value["status"] == "unknown" and not reasons:
        raise ValueError("unknown advice requires reasons")


def validate_local_completeness(value, budget):
    if value["provenance"] != "locally_reproduced_synthetic; provider_support_not_verified":
        return
    complete = value["completeness"] == "complete"
    if value["record"]["kind"] == "quote":
        priced = validate_component(value["declared"][0]).amount is not None
        if complete != priced:
            raise ValueError("invalid local Quote completeness")
    if not complete:
        return
    selected = validate_component(selected_declaration(value))
    if selected.amount is None:
        raise ValueError("complete advice requires a selected value")
    if value["status"] == "unknown" and (
        selected.model_dump(exclude={"amount"}) == budget.model_dump(exclude={"amount"})
        or "incompatible_economic_identity" not in value["reasons"]
    ):
        raise ValueError("complete unknown advice requires economic incompatibility")


def validate_quote_declarations(value):
    declared = value["declared"]
    if len(declared) != 2:
        raise ValueError("invalid Quote declarations")
    p50, p90 = [validate_component(component) for component in declared]
    identity = EconomicScope.model_validate(value["scope"]).economic.model_dump()
    if any(component.model_dump(exclude={"amount"}) != identity for component in (p50, p90)):
        raise ValueError("invalid Quote declaration identity")
    if (p50.amount is None) != (p90.amount is None):
        raise ValueError("invalid Quote declaration pair")
    if (
        p50.amount is not None
        and p90.amount is not None
        and (value["sample_count"] == 0 or Decimal(p50.amount) > Decimal(p90.amount))
    ):
        raise ValueError("invalid priced Quote declarations")


def selected_declaration(value):
    if value["record"]["kind"] == "quote":
        return value["declared"][0 if value["quantile"] == "p50" else 1]
    identity = EconomicScope.model_validate(value["scope"]).economic.model_dump()
    matching = [
        component
        for component in value["declared"]
        if validate_component(component).model_dump(exclude={"amount"}) == identity
    ]
    if len(matching) != 1 or matching[0].get("unknown_count") != 0:
        raise ValueError("invalid selected subtotal")
    return matching[0]


def validate_selected_comparison(value, checked):
    declared = validate_component(selected_declaration(value))
    if (
        declared.amount is None
        or checked.amount is None
        or declared.model_dump(exclude={"amount"}) != checked.model_dump(exclude={"amount"})
        or Decimal(declared.amount) != Decimal(checked.amount)
    ):
        raise ValueError("comparison differs from selected declaration")


def validate_comparison(value, budget):
    comparison = value.get("comparison")
    if value["status"] == "unknown":
        if comparison is not None:
            raise ValueError("unknown advice cannot have a verified value")
    else:
        if (
            value.get("completeness") != "complete"
            or value.get("provenance")
            != "locally_reproduced_synthetic; provider_support_not_verified"
            or value["reasons"]
            or value.get("cutoff") is None
        ):
            raise ValueError("invalid verified comparison")
        checked = validate_component(comparison)
        validate_selected_comparison(value, checked)
        if (
            budget.amount is None
            or checked.amount is None
            or checked.model_dump(exclude={"amount"}) != budget.model_dump(exclude={"amount"})
            or checked.model_dump(exclude={"amount"})
            != EconomicScope.model_validate(value["scope"]).economic.model_dump()
            or compare(checked.amount, budget.amount) != value["status"]
        ):
            raise ValueError("invalid comparison")


def summary_fields(value):
    yield "Status", value["status"]
    for key in ("kind", "record_id"):
        yield key, value["record"][key]
    for key in ECONOMIC:
        yield f"Budget {key}", value["budget"].get(key)
    for key in ("provenance", "completeness", "sample_count", "quantile"):
        yield key, value.get(key)
    yield from detail_fields(value)
    for reason in value["reasons"]:
        yield "Reason", reason


def detail_fields(value):
    for label, amounts in (
        ("Verified", [value.get("comparison")]),
        ("Declared", value["declared"]),
    ):
        for component in amounts:
            if component is not None:
                for key in ECONOMIC:
                    yield f"{label} {key}", component.get(key)
    scope = value.get("scope")
    if isinstance(scope, dict):
        for key in ("repository_id", "start", "end"):
            yield f"Scope {key}", scope.get(key)
    elif isinstance(scope, str):
        yield "Scope", scope
    if value.get("cutoff") is not None:
        for key in ("store_id", "at", "sequence"):
            yield f"Cutoff {key}", value["cutoff"].get(key)


def render_summary(value) -> str:
    validate_result(value)
    parts = ["## ChangeCost advisory\n\n"]
    used = len(parts[0].encode())
    maximum = LIMIT - len(NOTICE.encode())
    for label, detail in summary_fields(value):
        prefix = f"{label}: "
        for token in chain((prefix,), escaped_tokens(detail), ("\n\n",)):
            size = len(token.encode())
            if used + size > maximum:
                return "".join(parts) + NOTICE
            parts.append(token)
            used += size
    return "".join(parts)


def write_summary(value, path: Path):
    rendered = render_summary(value)
    with Path(path).open("a", encoding="utf-8") as target:
        target.write(rendered)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result", type=Path)
    args = parser.parse_args()
    try:
        value = json.loads(
            args.result.read_text(),
            object_pairs_hook=unique_members,
            parse_constant=reject_constant,
        )
        destination = os.environ.get("GITHUB_STEP_SUMMARY")
        if not destination:
            raise ValueError("missing summary destination")
        write_summary(value, Path(destination))
    except (OSError, ValueError, UnicodeError, RecursionError):
        parser.exit(2, "cannot render or write advisory summary\n")


if __name__ == "__main__":
    main()
