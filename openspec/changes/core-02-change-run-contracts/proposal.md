# Define change, run, quote and settlement contracts

## Why

Change-level accounting needs stable identity and portable evidence before provider adapters exist. Explicit binding prevents coincidental timestamps from becoming financial attribution.

## What Changes

- Define versioned Change, Run, Quote and Settlement records, source-evidence references and portable evidence-to-run and run-to-change bindings that retain complete structured Run references.
- Persist validated records transactionally in local SQLite, with explicit registration and outcome updates through bind and settle.
- Capture immutable, versioned pre-work cohort features when registering a change.
- Record revisioned actual-work intervals and store-local availability for every record and relationship, preventing backdated portable imports from leaking into history.
- Expose explicit offline artifact import/export and record inspection through existing command families, with atomic rejection of malformed or privacy-sensitive inputs.
- Provide changecost/v1 portable artifacts with exact economic values, provenance and revision history; require currency for known money and mark it non-applicable for nonmonetary quantities.

## Capabilities

### New Capabilities

- `change-run-contracts`: Define change, run, quote and settlement contracts.

### Modified Capabilities

None. The archived `python-foundation` and `bounded-review-session` contracts
remain unchanged; new operations must preserve their applicable guarantees.

## Impact

Future implementation extends the existing help/version CLI with local contract
models, SQLite storage, `bind` registration/mapping/import, lifecycle-only `settle`,
and record inspection/export through `explain`. Pydantic v2 becomes a declared
runtime dependency only during implementation; no ORM or provider SDK is needed.
Documentation: docs/contracts.md, docs/cli.md, and README.md.
Verification: the scenarios in [the capability spec](specs/change-run-contracts/spec.md),
strict OpenSpec validation, applicable quality gates and truthful review evidence.
No runtime files or dependencies are introduced by this planning proposal.

## Non-goals

No provider importers, economic reconciliation/aggregation, empirical estimation,
budget checks, price service, distributed ledger, remote storage, automatic Git/IDE
attribution, protected verifier redesign, or additional public command family.
Quote/Settlement records can be validated and preserved without implementing the
algorithms that later produce them.

## Dependencies

- [core-01-python-foundation](../archive/2026-09-29-core-01-python-foundation/proposal.md)

Dependencies are implementation prerequisites; planning can proceed together.
See [change order](../../CHANGE_ORDER.md) and [source assessment](../../../docs/research/pilot-source-assessment.md).

## Decisions and uncertainty

The Python/local-first scope and delivered foundation are confirmed. Preparation
on 2026-09-29 reconciles strict portable validation, transaction failures, revision
identity and the boundary with reconciliation/quotes. See [design](design.md) and
[preparation evidence](PREPARATION_EVIDENCE.md). Provider access, the Pydantic lock
and runtime behavior remain To-Validate until their respective implementation gates.

## Risks and rollback

- Identity collision → namespace identifiers and enforce uniqueness.
- Float drift or unit mixing → Decimal strings and explicit unit/basis validation.
- Interrupted migration → transaction plus consistent SQLite backup; never destructively downgrade a database.

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
- Preparation rechecked: 2026-09-29; #10 is closed after merged PR #22.
- Implementation authorized 2026-09-29 and implemented locally; GitHub CI verification and publication remain pending. The issue remains unassigned and undated.
<!-- tracking:end -->
