# Reconcile evidence into revisioned settlements

## Why

Retries and duplicate exports can inflate spend while missing charges can hide it. Reconciliation must preserve unknowns and corrections before provider-specific data enters the model.

## What Changes

- Normalize allowlisted economic evidence independently of provider parsers, retaining
  Core-02 identities, explicit bindings and destination-local availability.
- Deduplicate imports, preserve actual retries and apply identifiable corrections as revisions.
- Aggregate bound and unbound evidence separately, retaining accepted and abandoned outcomes.
- Record auditable full-change coverage separately from reconciled source intervals;
  incomplete attempts never become total-change observations.
- Define semantic deduplication, replacement correction graphs, authoritative temporal
  lanes and bounded exact arithmetic.
- Add snapshot-bound, operation-idempotent computed revisions and explain traces,
  keeping imported assertions and synthetic coverage distinct from local verification.

## Capabilities

### New Capabilities

- `evidence-reconciliation`: Reconcile evidence into revisioned settlements.

### Modified Capabilities

- `change-run-contracts`: extend the evolving internal `changecost/v1` records
  with economic evidence, coverage assertions and computed settlements while
  retaining strict boundaries and separating local computation from imported claims.
  See [the portable delta](specs/change-run-contracts/spec.md).

## Impact

The local/unpublished implementation is based on merged main
`999cb8f960785fe4ac0434d41a0892beca933191`; implementation was authorized on 2026-09-29.
Implementation affects `src/changecost/models.py`, serialization/store
boundaries, a focused reconciliation module, existing CLI/operations, contract/store
tests and new reconciliation/CLI tests. Reuse Python/Decimal/SQLite/Pydantic;
no new runtime dependency or provider framework is justified.
Documentation: docs/settlement.md, docs/contracts.md, and docs/cli.md.
Verification: the scenarios in [the capability spec](specs/evidence-reconciliation/spec.md),
strict OpenSpec validation, applicable quality gates and truthful review evidence.
Runtime files implement the planned behavior without new dependencies; verification remains pending.

## Non-goals

No inferred cash prices, universal invoice reconciliation guarantee, automatic attribution, provider API calls, or budget enforcement.

## Dependencies

- [core-02-change-run-contracts](../2026-09-29-core-02-change-run-contracts/proposal.md)

Dependencies are implementation prerequisites; planning can proceed together.
See [change order](../../../CHANGE_ORDER.md) and [source assessment](../../../../docs/research/pilot-source-assessment.md).

## Decisions and uncertainty

The Python/local-first scope is confirmed. Provider access and prediction quality
remain To-Validate. The delivered economic-field and cutoff gaps, numerical probes
and dated primary sources are recorded in [preparation evidence](PREPARATION_EVIDENCE.md).
All changes belong to the unreleased 0.x alpha/preview feasibility study; package
`0.1.0.dev0` and the existing internal artifact label are retained. There is no
public v2 release or backward-compatibility programme in scope. See [design](design.md)
for the settled development boundary and evidence gates.

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
- Project: [ChangeCost](https://github.com/orgs/nold-ai/projects/3) — private, status Done.
- Source: maintainer-approved pilot plan, 2026-09-28 (Europe/Berlin).
- Implementation: authorized 2026-09-29, merged in [PR #28](https://github.com/nold-ai/changecost/pull/28) on 2026-10-02.
- Acceptance: maintainer requested settlement closeout and normal CLI synchronization/archive on 2026-10-02.
- Tracking readback: 2026-10-02; #12 CLOSED/Done, User Story, parent #7, prerequisite #11 and labels retained.
- Archive: OpenSpec CLI 1.13.2, `openspec archive settlement-01-reconciliation --yes`; 17 added requirements synchronized into main specs.
- Historical 2026-09-29 reopening/Todo preparation evidence remains in [PREPARATION_EVIDENCE.md](PREPARATION_EVIDENCE.md).
<!-- tracking:end -->
