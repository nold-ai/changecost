# Produce deterministic empirical change-cost quotes

## Why

The pilot needs an explainable estimate whose calibration can be evaluated without leaking future settlements. Sparse or incompatible evidence must produce an honest unpriced result.

## What Changes

- Generate embedded p50/p90 records using deterministic empirical quantiles.
- Use documented cohort backoff over immutable features/v1 registration snapshots, with sample counts and reasons.
- Persist evidence cutoff and estimator parameters and return unpriced when comparable evidence is insufficient.

## Capabilities

### New Capabilities

- `empirical-quotes`: Produce deterministic empirical change-cost quotes.

### Modified Capabilities

None; no main capability specs exist yet.

## Impact

Future implementation affects the standalone Python CLI and local evidence workflow.
Documentation: docs/quotes.md, docs/contracts.md, and docs/cli.md.
Verification: the scenarios in [the capability spec](specs/empirical-quotes/spec.md),
strict OpenSpec validation, applicable quality gates and truthful review evidence.
No runtime files or dependencies are introduced by this planning proposal.

## Non-goals

No ML model, price database, cross-currency conversion, automatic enforcement, or claim that p90 is a guaranteed budget.

## Dependencies

- [settlement-01-reconciliation](../settlement-01-reconciliation/proposal.md)

Dependencies are implementation prerequisites; planning can proceed together.
See [change order](../../CHANGE_ORDER.md) and [source assessment](../../../docs/research/pilot-source-assessment.md).

## Decisions and uncertainty

The Python/local-first scope is confirmed. Provider access and prediction quality
remain To-Validate. See [design](design.md) for decisions and evidence gates.

## Risks and rollback

- False precision → expose n, cohort and unpriced state.
- Future-data leakage → recorded-at cutoff and immutable revision references.
- Cohort mismatch → explicit population/unit filters retained at every backoff level.

Planning rollback: revert the planning commit and close linked tracking items if
abandoned, preserving history. Later runtime rollback must preserve portable
evidence and prior local database versions; do not erase financial history.

## Source Tracking

<!-- tracking:start -->
- GitHub issue: [#15](https://github.com/nold-ai/changecost/issues/15) (native type: User Story).
- Parent feature: [#8](https://github.com/nold-ai/changecost/issues/8) — Quotes and developer workflow.
- Parent epic: [#4](https://github.com/nold-ai/changecost/issues/4) — ChangeCost — validate change-level cost estimation and settlement.
- Project: [ChangeCost](https://github.com/orgs/nold-ai/projects/3) — private, status Todo.
- Source: maintainer-approved pilot plan, 2026-09-28 (Europe/Berlin).
- Tracking verified: 2026-09-28; implementation is unstarted, unassigned and undated.
<!-- tracking:end -->
