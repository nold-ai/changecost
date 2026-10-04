"""Allowlisted, bounded Actions summaries; untrusted values remain data."""

from __future__ import annotations

import argparse
import json
import os
import unicodedata
from itertools import chain
from pathlib import Path

from changecost.advisory import compare
from changecost.models import Component, Cutoff
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


def validate_details(value):
    for name in ("provenance", "completeness"):
        if not isinstance(value.get(name), str):
            raise ValueError("invalid detail")
    sample = value.get("sample_count")
    if sample is not None and (type(sample) is not int or sample < 0):
        raise ValueError("invalid sample count")
    if value.get("quantile") not in {None, "p50", "p90"}:
        raise ValueError("invalid quantile")
    if value.get("cutoff") is not None:
        Cutoff.model_validate(value["cutoff"])
    scope = value.get("scope")
    if scope is not None and not isinstance(scope, (str, dict)):
        raise ValueError("invalid scope")
    if isinstance(scope, dict):
        from changecost.models import EconomicScope

        EconomicScope.model_validate(scope)


def validate_result(value):
    if not isinstance(value, dict) or value.get("schema") != "changecost/check-v1":
        raise ValueError("invalid check result")
    if value.get("status") not in {"within_budget", "over_budget", "unknown"}:
        raise ValueError("invalid advisory status")
    record, reasons = value.get("record"), value.get("reasons")
    if (
        not isinstance(record, dict)
        or record.get("kind") not in {"quote", "computed_settlement", "settlement"}
        or not isinstance(record.get("record_id"), str)
    ):
        raise ValueError("invalid record")
    budget = validate_component(value.get("budget"), budget=True)
    if not isinstance(reasons, list) or any(not isinstance(r, str) for r in reasons):
        raise ValueError("invalid reasons")
    validate_details(value)
    declared = value.get("declared")
    if not isinstance(declared, list):
        raise ValueError("invalid declarations")
    for component in declared:
        validate_component(component)
    validate_comparison(value, budget)


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
        if (
            budget.amount is None
            or checked.amount is None
            or checked.model_dump(exclude={"amount"}) != budget.model_dump(exclude={"amount"})
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
    except (OSError, ValueError, UnicodeError):
        parser.exit(2, "cannot render or write advisory summary\n")


if __name__ == "__main__":
    main()
