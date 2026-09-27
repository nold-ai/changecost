# Reconcile evidence into revisioned settlements

## Why

Retries and duplicate exports can inflate spend while missing charges can hide it. Reconciliation must preserve unknowns and corrections before provider-specific data enters the model.

## What Changes

- Normalize allowlisted evidence independently of provider parsers.
- Deduplicate imports, preserve actual retries and apply identifiable corrections as revisions.
- Aggregate bound and unbound evidence separately, retaining accepted and abandoned outcomes.

## Capabilities

### New Capabilities

- `evidence-reconciliation`: Reconcile evidence into revisioned settlements.

### Modified Capabilities

None; no main capability specs exist yet.

## Impact

Future implementation affects the standalone Python CLI and local evidence workflow.
Documentation: docs/settlement.md, docs/contracts.md, and docs/cli.md.
Verification: the scenarios in [the capability spec](specs/evidence-reconciliation/spec.md),
strict OpenSpec validation, applicable quality gates and truthful review evidence.
No runtime files or dependencies are introduced by this planning proposal.

## Non-goals

No inferred cash prices, universal invoice reconciliation guarantee, automatic attribution, provider API calls, or budget enforcement.

## Dependencies

- [core-02-change-run-contracts](../core-02-change-run-contracts/proposal.md)

Dependencies are implementation prerequisites; planning can proceed together.
See [change order](../../CHANGE_ORDER.md) and [source assessment](../../../docs/research/pilot-source-assessment.md).

## Decisions and uncertainty

The Python/local-first scope is confirmed. Provider access and prediction quality
remain To-Validate. See [design](design.md) for decisions and evidence gates.

## Risks and rollback

- Double counting → unique event keys and explicit lane precedence.
- Missing cost reads as free → unknown counters and provisional results.
- Late corrections contaminate backtests → keep both effective and recorded timestamps and immutable revisions.

Planning rollback: revert the planning commit and close linked tracking items if
abandoned, preserving history. Later runtime rollback must preserve portable
evidence and prior local database versions; do not erase financial history.

## Source Tracking

<!-- tracking:start -->
- GitHub issue: [#12](https://github.com/nold-ai/changecost/issues/12) (native type: User Story).
- Parent feature: [#7](https://github.com/nold-ai/changecost/issues/7) — Attribution and settlement.
- Parent epic: [#4](https://github.com/nold-ai/changecost/issues/4) — ChangeCost — validate change-level cost estimation and settlement.
- Project: [ChangeCost](https://github.com/orgs/nold-ai/projects/3) — private, status Todo.
- Source: maintainer-approved pilot plan, 2026-09-28 (Europe/Berlin).
- Tracking verified: 2026-09-28; implementation is unstarted, unassigned and undated.
<!-- tracking:end -->
