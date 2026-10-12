"""Explicit directional hypotheses and separately priced scenarios."""

from fractions import Fraction
from statistics import median

from changecost.demand_graph import demand_lookup as lookup
from changecost.demand_history import (
    CohortSelection,
    aggregate,
    ecosystem_identity,
    known_dimensions,
    peers,
)
from changecost.models import EstimatedPrice, TransferHypothesis, TransferResult
from changecost.serialization import ContractError
from changecost.store import key, reference


def matching_hypotheses(records, assessment, ecosystem, component, exclusions):
    hypotheses = sorted(
        (r for r in records.values() if isinstance(r, TransferHypothesis)),
        key=lambda r: r.record_id,
    )
    for hypothesis in hypotheses:
        target_eco = lookup(records, hypothesis.target_ecosystem, "ecosystem")
        if (
            ecosystem_identity(records, target_eco) != ecosystem_identity(records, ecosystem)
            or hypothesis.component != component
        ):
            continue
        if not known_dimensions(assessment) or hypothesis.dimensions != assessment.dimensions:
            exclusions.append((reference(hypothesis), "incompatible_transfer_dimensions"))
            continue
        yield hypothesis


def transfer_candidate(
    records, target, assessment, ecosystem, component, availability, algorithm="observed-summary/v3"
):
    exclusions, candidates = [], []
    for hypothesis in matching_hypotheses(records, assessment, ecosystem, component, exclusions):
        ratios, pairs = pair_values(
            records, target, assessment, hypothesis, availability, exclusions, algorithm
        )
        if not ratios:
            continue
        ratio = median(ratios)
        source_eco = lookup(records, hypothesis.source_ecosystem, "ecosystem")
        donor_history, _cohort, _diagnostics = peers(
            records,
            target,
            assessment,
            source_eco,
            component,
            availability,
            selection=CohortSelection(algorithm=algorithm),
        )
        donors = [d for d in donor_history if d[2].dimensions == assessment.dimensions]
        if not donors:
            exclusions.append((reference(hypothesis), "no_compatible_donor_history"))
            continue
        candidates.append(mapped_transfer(hypothesis, ratio, pairs, donors))
    # Competing overlapping hypotheses need a selected version, not file-order preference.
    if len(candidates) > 1:
        exclusions.extend((c.hypothesis, "ambiguous_transfer_hypotheses") for c in candidates)
        return None, exclusions
    return (candidates[0] if candidates else None), exclusions


def mapped_transfer(hypothesis, ratio, pairs, donors):
    return TransferResult(
        hypothesis=reference(hypothesis),
        ratio=str(ratio),
        pair_count=len(pairs),
        donor_count=len(donors),
        donors=[reference(c) for c, _v, _a in donors],
        scenarios=[str(v * ratio) for _c, v, _a in donors],
        residuals=[str(b - ratio * a) for a, b in pairs],
    )


def pair_values(
    records,
    target,
    assessment,
    hypothesis,
    availability,
    exclusions,
    algorithm="observed-summary/v3",
):
    selected = eligible_comparisons(
        records, target, assessment, hypothesis, availability, exclusions, algorithm
    )
    return [b / a for _pair, a, b in selected], [(a, b) for _pair, a, b in selected]


def eligible_comparisons(
    records, target, assessment, hypothesis, availability, exclusions, algorithm
):
    component = hypothesis.component
    selected, used = [], set()
    source_eco = lookup(records, hypothesis.source_ecosystem, "ecosystem")
    target_eco = lookup(records, hypothesis.target_ecosystem, "ecosystem")
    for ref in hypothesis.comparisons:
        pair = lookup(records, ref, "matched_comparison")
        reason = pair_rejection(pair, target, hypothesis, used)
        if reason:
            exclusions.append((ref, reason))
            continue
        source = lookup(records, pair.source_change, "change")
        destination = lookup(records, pair.target_change, "change")
        a, sa, ar = aggregate(records, source, source_eco, component, availability, algorithm)
        b, ta, br = aggregate(records, destination, target_eco, component, availability, algorithm)
        if (
            ar
            or br
            or a is None
            or b is None
            or sa is None
            or ta is None
            or sa.scope_key != pair.scope_key
            or ta.scope_key != pair.scope_key
            or sa.dimensions != assessment.dimensions
            or ta.dimensions != assessment.dimensions
        ):
            exclusions.append((ref, "incomplete_or_confounded_pair"))
            continue
        if a == 0:
            exclusions.append((ref, "zero_donor_denominator"))
            continue
        used.update([key(pair.source_change), key(pair.target_change)])
        selected.append((pair, a, b))
    return selected


def pair_rejection(pair, target, hypothesis, used):
    if reference(target) in (pair.source_change, pair.target_change):
        return "target_excluded_from_bridge"
    if pair.confounding:
        return "confounded_pair"
    if (
        pair.source_ecosystem != hypothesis.source_ecosystem
        or pair.target_ecosystem != hypothesis.target_ecosystem
    ):
        return "incompatible_pair_direction"
    if key(pair.source_change) in used or key(pair.target_change) in used:
        return "dependent_pair_reuse"
    return None


def estimate_price(price, result):
    rates = [rate for rate in price.rates if rate.component == result.component]
    if len(rates) != 1 or len(price.rates) != 1:
        raise ContractError("missing or incompatible component rates")
    quantity = result.median
    if quantity is None and result.transfer is not None:
        quantity = str(median(Fraction(v) for v in result.transfer.scenarios))
    if quantity is None:
        raise ContractError("zero knowledge has no usage quantity to price")
    return EstimatedPrice(
        source=reference(price),
        currency=price.currency,
        amount=str(Fraction(quantity) * Fraction(rates[0].rate)),
    )
