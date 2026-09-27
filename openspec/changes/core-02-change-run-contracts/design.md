# Design: Define change, run, quote and settlement contracts

## Context

See [proposal](proposal.md) and [capability spec](specs/change-run-contracts/spec.md).
The current repository contains documentation and hygiene gates, with no product
package or runtime. This design describes later implementation, not delivered behavior.

## Goals / Non-Goals

**Goals:** Make the specified capability local, reproducible and explicit about missing evidence.

**Non-Goals:** No provider importers, price service, distributed ledger, remote storage, automatic Git/IDE attribution, or additional public command family.

## Decisions

1. Use Pydantic contracts with explicit kind and schema=changecost/v1. Change has a caller-supplied stable change_id within an explicit repository_id, optional commit/PR references and separate outcome. Run has a namespaced provider/surface/run_id plus optional provider session/trace IDs. Quote embeds quantiles or unpriced reason, unit/basis, cohort, evidence cutoff, algorithm version and creation time. Settlement embeds aggregate components, completeness, provenance and revision references.

2. Use standard-library SQLite under .changecost/changecost.sqlite3 by default, with explicit path override. Tables for records/bindings/revisions use uniqueness constraints and transactions; schema migrations are numbered. No ORM or daemon is needed. Portable JSON is independent of SQLite and contains only allowlisted economic metadata.

3. Bind takes explicit repository/change/run identifiers. Repeating the same association is idempotent; conflicting binding fails without mutation. A later explicitly requested rebind must be a separate audited correction, not a silent overwrite. Runs are not inferred from working branch, path or timestamps.

4. Decimal values serialize as finite decimal strings. Keep currency, unit and basis mandatory for known amounts; null means unknown and zero means observed zero. Reject NaN, infinity, unsupported major versions and incompatible aggregates. Round only presentation, with displayed precision and half-even rounding; keep original exact amounts.

5. Use UTC timestamps with offsets normalized, plus recorded_at and effective_at to support historical replay. Local display may use Europe/Berlin. Atomic import validates the entire artifact before commit; unknown versions and conflicts leave state unchanged. Export/import round trips retain stable IDs and correction links.

## Dependencies and evidence

- [core-01-python-foundation](../core-01-python-foundation/proposal.md)

Shared boundaries and current provider evidence are recorded in the
[source assessment](../../../docs/research/pilot-source-assessment.md).
No provider-specific mapping becomes supported merely by appearing in this plan.

## Risks / Trade-offs

- Identity collision → namespace identifiers and enforce uniqueness.
- Float drift or unit mixing → Decimal strings and explicit unit/basis validation.
- Interrupted migration → transaction plus portable backup; never destructively downgrade a database.

## Migration Plan

After separate implementation authorization, land this change in dependency order
with spec-derived failing and passing evidence. Update docs/contracts.md, docs/cli.md, and README.md.
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
