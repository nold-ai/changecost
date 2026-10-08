# Import accessible personal Cursor usage exports

## Why

Personal Cursor exports cannot be assumed to expose Enterprise OTel identifiers or dollar charges. A useful importer must describe exactly which evidence is accessible.

## What Changes

- Import independently approved existing personal usage sources when available; classify regular local metadata and missing exports separately rather than promise a CSV on every plan.
- Preserve token categories and distinguish absent money from observed zero.
- Support explicit manual mappings and unbound records without inventing conversation joins.

## Capabilities

### New Capabilities

- `cursor-import`: Import accessible personal Cursor usage exports.

### Modified Capabilities

None; delivered main capabilities are preserved. New additive requirements are defined in this change; source/policy approval remains separate.

## Impact

Future implementation affects the standalone Python CLI and local evidence workflow.
Documentation: docs/providers/cursor.md, docs/providers/source-feasibility.md, and docs/cli.md.
Verification: the scenarios in [the capability spec](specs/cursor-import/spec.md),
strict OpenSpec validation, applicable quality gates and truthful review evidence.
No runtime files or dependencies are introduced by this planning proposal.

## Non-goals

No Enterprise OTel collector, Admin API dependency, undocumented editor database scraping, synthetic invoice pricing, or promised automatic session attribution.

## Dependencies

- [pilot-01-source-feasibility](../archive/2026-10-08-pilot-01-source-feasibility/proposal.md)
- [settlement-01-reconciliation](../archive/2026-10-02-settlement-01-reconciliation/proposal.md)

Dependencies are implementation prerequisites; planning can proceed together.
See [change order](../../CHANGE_ORDER.md) and [source assessment](../../../docs/research/pilot-source-assessment.md).

## Decisions and uncertainty

The Python/local-first scope is confirmed. Provider access and prediction quality
remain To-Validate. See [design](design.md) for decisions and evidence gates.

## Risks and rollback

- Personal export changes → explicit profile signature and dated feasibility evidence.
- Overlapping rows lack identity → disclose incomplete dedupe and block false final totals.
- Tokens mistaken for cash → separate units and unknown monetary components.

Planning rollback: revert the planning commit and close linked tracking items if
abandoned, preserving history. Later runtime rollback must preserve portable
evidence and prior local database versions; do not erase financial history.

## Source Tracking

<!-- tracking:start -->
- GitHub issue: [#14](https://github.com/nold-ai/changecost/issues/14) (native type: User Story).
- Parent feature: [#7](https://github.com/nold-ai/changecost/issues/7) — Attribution and settlement.
- Parent epic: [#4](https://github.com/nold-ai/changecost/issues/4) — ChangeCost — validate change-level cost estimation and settlement.
- Project: [ChangeCost](https://github.com/orgs/nold-ai/projects/3) — private, status Todo.
- Source: maintainer-approved pilot plan, 2026-09-28 (Europe/Berlin).
- Tracking verified: 2026-09-28; implementation is unstarted, unassigned and undated.
<!-- tracking:end -->
