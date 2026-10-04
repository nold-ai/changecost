# Produce deterministic empirical change-cost quotes

## Why

The pilot needs an explainable estimate whose calibration can be evaluated without leaking future settlements. Sparse or incompatible evidence must produce an honest unpriced result.

## What Changes

- Generate embedded p50/p90 records using deterministic empirical quantiles over auditable full-change observations, excluding reconciled partial subtotals.
- Use documented cohort backoff over immutable features/v1 registration snapshots, with sample counts and reasons.
- Derive each peer aggregate from the delivered reconciliation evaluator at one committed Quote cutoff; do not trust saved or imported completeness claims or write settlement revisions.
- Extend the existing Quote with versioned estimation metadata, reproducible peer/exclusion references and explicit synthetic provenance; retain older imported claims as inspectable records.
- Persist evidence cutoff and estimator parameters and return unpriced when comparable evidence is insufficient.

## Capabilities

### New Capabilities

- `empirical-quotes`: Produce deterministic empirical change-cost quotes.

### Modified Capabilities

None. Reuse the delivered `change-run-contracts` and `evidence-reconciliation`
requirements without altering lifecycle or provider coverage policy.

## Impact

The Python package, SQLite store, portable Quote contract and offline settlement
computation are delivered. This checkout adds `quote` and extends `explain` within
that standalone local workflow, without new dependencies; final verification and
publication are tracked in its tasks/evidence.
Documentation: docs/quotes.md, docs/contracts.md, and docs/cli.md.
Verification: the scenarios in [the capability spec](specs/empirical-quotes/spec.md),
strict OpenSpec validation, applicable quality gates and truthful review evidence.
The authorized runtime adds the estimator module and tests, retaining existing
portable contracts, SQLite layout and runtime dependencies.

## Non-goals

No ML model, price database, cross-currency conversion, automatic enforcement, or claim that p90 is a guaranteed budget.

## Dependencies

- [settlement-01-reconciliation](../2026-10-02-settlement-01-reconciliation/proposal.md)

Settlement is delivered in PR #28 and archived by PR #31. It satisfies the only
implementation prerequisite. Provider adapters and source-feasibility completion
are not prerequisites for synthetic quote verification; no provider policy is added.
See [change order](../../../CHANGE_ORDER.md) and [source assessment](../../../../docs/research/pilot-source-assessment.md).

## Decisions and uncertainty

The Python/local-first scope is confirmed. Provider access and prediction quality
remain To-Validate. Only the delivered closed synthetic billed-USD policy currently
proves full-change coverage. Other identities return unpriced rather than gaining
support through this plan. The default minimum of 20 peers and empirical p90 are
pilot design choices, not accuracy or budget guarantees. See [design](design.md)
and [preparation evidence](PREPARATION_EVIDENCE.md).

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
- Tracking reviewed: 2026-10-03 (Europe/Berlin); #15 remains Open/Todo,
  unassigned and undated. Parent #8 and native prerequisite #12 are retained.
- Preparation: locally prepared/unpublished on `codex/prepare-quote-01-empirical-estimation`;
  selected delivery is a scoped stash. No estimator implementation or planning PR is claimed.
<!-- tracking:end -->

## Authorized implementation status

Runtime implementation was explicitly authorized on 2026-10-03 (Europe/Berlin).
This checkout implements the prepared synthetic-only boundary; tasks and
[TDD evidence](TDD_EVIDENCE.md) retain actual verification and publication status.
