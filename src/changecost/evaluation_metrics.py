"""Exact metric formulas; only Wilson uncertainty is rounded for presentation."""

from collections import Counter, defaultdict
from decimal import Decimal, localcontext
from fractions import Fraction
from statistics import median


def coverage(numerator: int, denominator: int) -> dict:
    if not denominator:
        return dict(
            numerator=numerator,
            denominator=0,
            ratio=None,
            wilson95=None,
            undefined_reason="no_scored_truth",
        )
    with localcontext() as context:
        context.prec = 40
        n, z = Decimal(denominator), Decimal("1.959963984540054")
        p = Decimal(numerator) / n
        divisor = 1 + z * z / n
        center = (p + z * z / (2 * n)) / divisor
        half = z * (p * (1 - p) / n + z * z / (4 * n * n)).sqrt() / divisor
        bounds = [
            format(max(Decimal(0), center - half), ".6f"),
            format(min(Decimal(1), center + half), ".6f"),
        ]
    return dict(
        numerator=numerator,
        denominator=denominator,
        ratio=str(Fraction(numerator, denominator)),
        wilson95=bounds,
        undefined_reason=None,
    )


def average(values) -> str | None:
    return str(sum(values, Fraction(0)) / len(values)) if values else None


def economic_metrics(rows: list[dict], method: str) -> dict:
    scored = [r for r in rows if r["status"] == "scored"]
    actuals = [Fraction(r["truth"]["amount"]) for r in scored]
    predictions = [Fraction(r[method]["p50"]) for r in scored]
    uppers = [Fraction(r[method]["p90"]) for r in scored]
    return dict(
        count=len(scored),
        p50_coverage=coverage(
            sum(a <= p for a, p in zip(actuals, predictions, strict=True)), len(scored)
        ),
        p90_coverage=coverage(
            sum(a <= p for a, p in zip(actuals, uppers, strict=True)), len(scored)
        ),
        mean_signed_error=average([p - a for a, p in zip(actuals, predictions, strict=True)]),
        mean_absolute_error=average(
            [abs(p - a) for a, p in zip(actuals, predictions, strict=True)]
        ),
        mean_width=average([u - p for u, p in zip(uppers, predictions, strict=True)]),
    )


def economic_comparison(rows: list[dict], identity: dict) -> dict:
    asymmetric = any(r["status"] == "comparison_error" for r in rows)
    return dict(
        status="comparison_error" if asymmetric else "comparable",
        identity=identity,
        cases=rows,
        counts=dict(sorted(Counter(r["status"] for r in rows).items())),
        scored_outcome_counts=dict(
            sorted(Counter(r["truth"]["outcome"] for r in rows if r["status"] == "scored").items())
        ),
        candidate=None if asymmetric else economic_metrics(rows, "candidate"),
        baseline=None if asymmetric else economic_metrics(rows, "baseline"),
    )


def scenario_metrics(transfer, actual: Fraction | None) -> dict:
    values = sorted(Fraction(v) for v in transfer.scenarios)
    point = median(values)
    return dict(
        interpretation="scenario_diagnostic_not_observed_quantiles",
        minimum=str(values[0]),
        median=str(point),
        maximum=str(values[-1]),
        width=str(values[-1] - values[0]),
        support_count=transfer.pair_count,
        donor_count=transfer.donor_count,
        truth_count=int(actual is not None),
        signed_error=str(point - actual) if actual is not None else None,
        absolute_error=str(abs(point - actual)) if actual is not None else None,
        validation="not_eligible_for_measured_receipt",
    )


def adaptive_summary(rows: list[dict], minimum_independent_truth: int) -> dict:
    available = Counter()
    scored = Counter()
    for row in rows:
        for name, result in row["methods"].items():
            available[name] += int(result.get("median") is not None)
            scored[name] += int(result.get("signed_error") is not None)
    shared = [
        r
        for r in rows
        if all(
            r["methods"].get(m, {}).get("signed_error") is not None
            for m in ("repository", "dimensional")
        )
    ]
    return dict(
        cases=rows,
        eligible_case_count=len(rows),
        truth_categories={
            name: sum(r["truth"]["category"] == name for r in rows)
            for name in ("observed", "partial", "unavailable", "imputed")
        },
        outcome_counts=dict(
            sorted(Counter(r["truth"]["outcome"] or "unknown" for r in rows).items())
        ),
        minimum_independent_truth=minimum_independent_truth,
        availability=dict(sorted(available.items())),
        scored_counts=dict(sorted(scored.items())),
        shared_observed_truth_count=len(shared),
        shared_observed_metrics=shared_metrics(shared),
        distinct_scope_groups=len({r["scope_key"] for r in rows}),
        dependence="scope_groups_do_not_prove_independence",
    )


def observed_aggregate(rows, method):
    quantities = [row["methods"][method] for row in rows]
    metrics = [q["metrics"] for q in quantities]
    errors = [Fraction(q["signed_error"]) for q in quantities]
    return dict(
        count=len(rows),
        component=rows[0]["component"],
        observed_range_coverage=coverage(sum(m["covered"] for m in metrics), len(rows)),
        mean_signed_error=average(errors),
        mean_absolute_error=average([abs(e) for e in errors]),
        mean_width=average([Fraction(m["maximum_width"]) for m in metrics]),
        maximum_underestimate=str(max(Fraction(m["maximum_underestimate"]) for m in metrics)),
        maximum_overhead=str(max(Fraction(m["maximum_overhead"]) for m in metrics)),
    )


def shared_metrics(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row["policy"]["record_id"]].append(row)
    result = []
    for policy_id, group in sorted(groups.items()):
        independent = len({r["scope_key"] for r in group})
        result.append(
            dict(
                policy=policy_id,
                methods={
                    method: observed_aggregate(group, method)
                    for method in ("repository", "dimensional")
                },
                distinct_scope_groups=independent,
                minimum_registered_truth=group[0]["policy"]["minimum_truth"],
                independence_established=False,
            )
        )
    return result
