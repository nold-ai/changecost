# Design: Evaluate attribution and chronological quote calibration

## Context

See [proposal](proposal.md) and [capability spec](specs/pilot-evaluation/spec.md).
The current repository contains documentation and hygiene gates, with no product
package or runtime. This design describes later implementation, not delivered behavior.

## Goals / Non-Goals

**Goals:** Make the specified capability local, reproducible and explicit about missing evidence.

**Non-Goals:** No fabricated live measurements, collection during planning, product launch claim, employee ranking, ML training, enforcement threshold or paid infrastructure.

## Decisions

1. Replay quotes in timestamp order using only revisions available at each cutoff in the Quote's store context. Apply destination availability to every dependency; portable origin timestamps cannot establish local historical knowledge. Report cross-store replay_unavailable separately and exclude it from scoring without backdating imports. Both candidate and repository-wide baseline use identical unit/basis, eligibility, population, minimum count and quantile method; the baseline omits narrow cohort features. The candidate's final repository fallback is exactly the baseline cohort, so availability must match: both priced when it meets the minimum, otherwise both unpriced. Score paired priced cases and report jointly unpriced cases with counts/reasons. If observed availability differs, report a comparison/configuration error and stop accuracy reporting for that run rather than treating it as a supported pilot outcome.

Use one initial pre-run Quote per evaluated Change, with the frozen feature snapshot
and cutoff defined by the [estimator contract](../archive/2026-10-04-quote-01-empirical-estimation/design.md#feature-selection-and-capture-time).
Later diagnostic quotes do not create extra observations. Missing features lead to
repository fallback for the candidate, not removal of baseline-eligible history.

2. Report p50/p90 empirical coverage as count(actual <= quantile)/priced comparable count, with numerator and denominator; report signed errors and interval width p90-p50 in original units. Include sample-count uncertainty (for example Wilson intervals for coverage), not a claim that observed 90% is a guarantee. Require the same full-change coverage contract for evaluation truth as for historical quote peers; reconciled partial intervals are not actual total-change costs. Freeze and report a separate truth as-of cutoff and selected complete settlement/coverage revisions for reproducibility, including later corrections known at that cutoff without leaking them into quote-time history. Cases with unavailable complete truth remain in reported exclusion/unknown counts, outside accuracy denominators; never score them as zero.

3. Attribution reports provider-backed bound, manually bound and unbound record counts separately, plus their comparable economic totals. Denominator is all eligible observed records, not only those already bound. Missing money contributes to unknown counts. Report duplicate/conflict/pending-correction rates and completeness alongside apparent binding coverage.

4. Abandoned expenditure is abandoned terminal-change amount divided by all terminal-change amount within the same unit/basis; zero or unknown denominator yields undefined, not zero. Include linked retries in both applicable totals. Outcome provenance must be explicit.

5. Measure CLI wall time in milliseconds and local storage/input bytes for stated fixture sizes and runtime environment; report repeated measurements with method rather than universal speed claims. No external telemetry service is required.

6. Pre-register the protocol and decision rubric before live results: compare paired calibration and width against the baseline; report feasibility and overhead separately. If intervals/sample size do not support improvement, classify as not yet validated. A source unavailable at the gate is a recorded coverage gap, not synthetic live support; adapter dependencies remain incomplete until explicitly re-scoped. No fixed sample target from the research guarantees success.

## Dependencies and evidence

- [provider-01-copilot-import](../provider-01-copilot-import/proposal.md)
- [provider-02-cursor-import](../provider-02-cursor-import/proposal.md)
- [quote-01-empirical-estimation](../archive/2026-10-04-quote-01-empirical-estimation/proposal.md)
- [workflow-01-advisory-ci](../workflow-01-advisory-ci/proposal.md)

Shared boundaries and current provider evidence are recorded in the
[source assessment](../../../docs/research/pilot-source-assessment.md).
No provider-specific mapping becomes supported merely by appearing in this plan.

## Risks / Trade-offs

- Selection bias → report unpriced and unbound cases with full denominators.
- Leakage → chronological revision-aware replay for both methods.
- Small or unavailable evidence → uncertainty and not-yet-validated conclusion, never invented measurements.

## Migration Plan

After separate implementation authorization, land this change in dependency order
with spec-derived failing and passing evidence. Update docs/pilot/evaluation.md, docs/pilot/findings.md, and docs/providers/source-feasibility.md.
Use synthetic fixtures before any authorized real-data evaluation. This is unreleased;
there is no deployed service to migrate. For local schema changes, export/backup
before migration and validate recovery without deleting the previous data.

Rollback the implementation commit if its checks fail; restore a compatible local
backup rather than forcing an older program to write a newer database. Planning
rollback is a commit revert plus closing the associated issue, preserving history.

## Verification

Each requirement has Given/When/Then scenarios. Exercise negative paths and privacy
boundaries alongside the success cases. Run strict OpenSpec validation and applicable
repository gates; record actual results, not anticipated test or review outcomes.
