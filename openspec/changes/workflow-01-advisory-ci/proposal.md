# Expose advisory CLI checks and GitHub summaries

## Why

Developers need readable and machine-consumable results from the standalone CLI without turning an unvalidated quote into a blocking budget policy.

## What Changes

- Present quote, bind, settle, check and explain consistently in human and JSON formats, including a complete fresh-store registration and outcome workflow.
- Compare compatible budgets with explicit advisory statuses; incomplete settlement totals remain unknown rather than treating known subtotals as final.
- Provide a GitHub Actions example that writes a safe job summary using local artifacts.
- Keep implemented CLI examples, documentation ownership and generated command/agent
  references current through the foundation's existing quality gates.

## Capabilities

### New Capabilities

- `advisory-workflow`: Expose advisory CLI checks and GitHub summaries.

### Modified Capabilities

None; no main capability specs exist yet.

## Impact

Future implementation affects the standalone Python CLI and local evidence workflow.
Documentation: docs/cli.md, docs/ci.md, and README.md.
Verification: the scenarios in [the capability spec](specs/advisory-workflow/spec.md),
strict OpenSpec validation, applicable quality gates and truthful review evidence.
No runtime files or dependencies are introduced by this planning proposal.

## Non-goals

No required budget-status enforcement, PR comment bot, hosted service, dashboard,
provider account setup or SpecFact runtime integration. Repository quality gates
are owned by `core-01-python-foundation` and remain blocking independently of
advisory budget results.

## Dependencies

- [quote-01-empirical-estimation](../quote-01-empirical-estimation/proposal.md)

Dependencies are implementation prerequisites; planning can proceed together.
See [change order](../../CHANGE_ORDER.md) and [source assessment](../../../docs/research/pilot-source-assessment.md).

## Decisions and uncertainty

The Python/local-first scope is confirmed. Provider access and prediction quality
remain To-Validate. See [design](design.md) for decisions and evidence gates.

## Risks and rollback

- Advice becomes enforcement → explicit exit semantics and opt-in workflow.
- Untrusted labels execute or misrender → safe argument handling and escaped bounded summaries.
- JSON hides uncertainty → required completeness and structured unknown reasons.

Planning rollback: revert the planning commit and close linked tracking items if
abandoned, preserving history. Later runtime rollback must preserve portable
evidence and prior local database versions; do not erase financial history.

## Source Tracking

<!-- tracking:start -->
- GitHub issue: [#16](https://github.com/nold-ai/changecost/issues/16) (native type: User Story).
- Parent feature: [#8](https://github.com/nold-ai/changecost/issues/8) — Quotes and developer workflow.
- Parent epic: [#4](https://github.com/nold-ai/changecost/issues/4) — ChangeCost — validate change-level cost estimation and settlement.
- Project: [ChangeCost](https://github.com/orgs/nold-ai/projects/3) — private, status Todo.
- Source: maintainer-approved pilot plan, 2026-09-28 (Europe/Berlin).
- Tracking verified: 2026-09-28; implementation is unstarted, unassigned and undated.
<!-- tracking:end -->
