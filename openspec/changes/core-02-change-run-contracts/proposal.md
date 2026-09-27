# Define change, run, quote and settlement contracts

## Why

Change-level accounting needs stable identity and portable evidence before provider adapters exist. Explicit binding prevents coincidental timestamps from becoming financial attribution.

## What Changes

- Define versioned Change, Run, Quote and Settlement records, source-evidence references and portable evidence-to-run and run-to-change bindings that retain complete structured Run references.
- Persist validated records transactionally in local SQLite, with explicit registration and outcome updates through bind and settle.
- Capture immutable, versioned pre-work cohort features when registering a change.
- Record revisioned actual-work intervals and store-local availability for every record and relationship, preventing backdated portable imports from leaking into history.
- Provide changecost/v1 portable artifacts with exact economic values, provenance and revision history; require currency for known money and mark it non-applicable for nonmonetary quantities.

## Capabilities

### New Capabilities

- `change-run-contracts`: Define change, run, quote and settlement contracts.

### Modified Capabilities

None; no main capability specs exist yet.

## Impact

Future implementation affects the standalone Python CLI and local evidence workflow.
Documentation: docs/contracts.md, docs/cli.md, and README.md.
Verification: the scenarios in [the capability spec](specs/change-run-contracts/spec.md),
strict OpenSpec validation, applicable quality gates and truthful review evidence.
No runtime files or dependencies are introduced by this planning proposal.

## Non-goals

No provider importers, price service, distributed ledger, remote storage, automatic Git/IDE attribution, or additional public command family.

## Dependencies

- [core-01-python-foundation](../core-01-python-foundation/proposal.md)

Dependencies are implementation prerequisites; planning can proceed together.
See [change order](../../CHANGE_ORDER.md) and [source assessment](../../../docs/research/pilot-source-assessment.md).

## Decisions and uncertainty

The Python/local-first scope is confirmed. Provider access and prediction quality
remain To-Validate. See [design](design.md) for decisions and evidence gates.

## Risks and rollback

- Identity collision → namespace identifiers and enforce uniqueness.
- Float drift or unit mixing → Decimal strings and explicit unit/basis validation.
- Interrupted migration → transaction plus portable backup; never destructively downgrade a database.

Planning rollback: revert the planning commit and close linked tracking items if
abandoned, preserving history. Later runtime rollback must preserve portable
evidence and prior local database versions; do not erase financial history.

## Source Tracking

<!-- tracking:start -->
- GitHub issue: [#11](https://github.com/nold-ai/changecost/issues/11) (native type: User Story).
- Parent feature: [#6](https://github.com/nold-ai/changecost/issues/6) — Local core and contracts.
- Parent epic: [#4](https://github.com/nold-ai/changecost/issues/4) — ChangeCost — validate change-level cost estimation and settlement.
- Project: [ChangeCost](https://github.com/orgs/nold-ai/projects/3) — private, status Todo.
- Source: maintainer-approved pilot plan, 2026-09-28 (Europe/Berlin).
- Tracking verified: 2026-09-28; implementation is unstarted, unassigned and undated.
<!-- tracking:end -->
