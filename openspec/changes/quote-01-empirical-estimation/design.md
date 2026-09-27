# Design: Produce deterministic empirical change-cost quotes

## Context

See [proposal](proposal.md) and [capability spec](specs/empirical-quotes/spec.md).
The current repository contains documentation and hygiene gates, with no product
package or runtime. This design describes later implementation, not delivered behavior.

## Goals / Non-Goals

**Goals:** Make the specified capability local, reproducible and explicit about missing evidence.

**Non-Goals:** No ML model, price database, cross-currency conversion, automatic enforcement, or claim that p90 is a guaranteed budget.

## Decisions

1. Use nearest-rank empirical quantiles: for sorted n observations at p, choose index ceil(p*n)-1. Use Decimal ordering, no random sampling/interpolation and no rounding before selection. A quote is an embedded record with the selected unit/basis, n, algorithm version, cohort and evidence cutoff.

2. Pilot default minimum n is 20 comparable historical changes, configurable and recorded per quote; this is a transparent design default, not a validated statistical guarantee. Back off in fixed order: repository+change_shape+trajectory+execution_profile, then repository+change_shape+trajectory, then repository-wide. Missing features skip narrower levels with a recorded reason. Use explicit categorical input features, not prompt analysis.

3. All levels retain the same economic unit/currency/basis and requested outcome population. Include terminal accepted and abandoned changes for total attempt-budget quotes; record the population definition. Incomplete settlements and unresolved overlapping evidence are excluded with reasons. Never mix observed billed amounts and estimates to increase n.

4. Use only evidence recorded and available by the quote timestamp, with settlement effective time no later than cutoff. Select the revision known then, exclude the target change and future corrections. Keep eligible IDs/revision references and exclusion counts so explain and replay can reproduce selection.

5. If every cohort is below minimum, the unit is unavailable, or comparable values are missing, return unpriced with a structured reason and counts. No zero-price fallback. Provide separate quotes per requested economic unit; no grand total across units.

## Dependencies and evidence

- [settlement-01-reconciliation](../settlement-01-reconciliation/proposal.md)

Shared boundaries and current provider evidence are recorded in the
[source assessment](../../../docs/research/pilot-source-assessment.md).
No provider-specific mapping becomes supported merely by appearing in this plan.

## Risks / Trade-offs

- False precision → expose n, cohort and unpriced state.
- Future-data leakage → recorded-at cutoff and immutable revision references.
- Cohort mismatch → explicit population/unit filters retained at every backoff level.

## Migration Plan

After separate implementation authorization, land this change in dependency order
with spec-derived failing and passing evidence. Update docs/quotes.md, docs/contracts.md, and docs/cli.md.
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
