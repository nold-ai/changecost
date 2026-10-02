# Import native Copilot IDE and CLI evidence

## Why

Copilot local telemetry may supply useful usage and billing units, but repeated span attributes and surface-specific session semantics need explicit handling.

## What Changes

- Import user-provided Copilot IDE/CLI local files using versioned, feasibility-approved mappings.
- Preserve billing units and select authoritative evidence without counting repeated span values.
- Use verified provider identifiers or explicit manual mappings; expose ambiguous attribution and unsupported formats.

## Capabilities

### New Capabilities

- `copilot-import`: Import native Copilot IDE and CLI evidence.

### Modified Capabilities

None; no main capability specs exist yet.

## Impact

Future implementation affects the standalone Python CLI and local evidence workflow.
Documentation: docs/providers/copilot.md, docs/providers/source-feasibility.md, and docs/cli.md.
Verification: the scenarios in [the capability spec](specs/copilot-import/spec.md),
strict OpenSpec validation, applicable quality gates and truthful review evidence.
No runtime files or dependencies are introduced by this planning proposal.

## Non-goals

No SDK wrapper requirement, telemetry collector, automatic environment/IDE configuration, prompt storage, account API scraping, or dollars inferred from multipliers.

## Dependencies

- [pilot-01-source-feasibility](../pilot-01-source-feasibility/proposal.md)
- [settlement-01-reconciliation](../archive/2026-10-02-settlement-01-reconciliation/proposal.md)

Dependencies are implementation prerequisites; planning can proceed together.
See [change order](../../CHANGE_ORDER.md) and [source assessment](../../../docs/research/pilot-source-assessment.md).

## Decisions and uncertainty

The Python/local-first scope is confirmed. Provider access and prediction quality
remain To-Validate. See [design](design.md) for decisions and evidence gates.

## Risks and rollback

- Repeated billing attributes → fixture-tested authoritative root selection.
- Session ambiguity → verified joins or manual/unbound status.
- Content leakage → allowlist normalization and negative log/storage tests.

Planning rollback: revert the planning commit and close linked tracking items if
abandoned, preserving history. Later runtime rollback must preserve portable
evidence and prior local database versions; do not erase financial history.

## Source Tracking

<!-- tracking:start -->
- GitHub issue: [#13](https://github.com/nold-ai/changecost/issues/13) (native type: User Story).
- Parent feature: [#7](https://github.com/nold-ai/changecost/issues/7) — Attribution and settlement.
- Parent epic: [#4](https://github.com/nold-ai/changecost/issues/4) — ChangeCost — validate change-level cost estimation and settlement.
- Project: [ChangeCost](https://github.com/orgs/nold-ai/projects/3) — private, status Todo.
- Source: maintainer-approved pilot plan, 2026-09-28 (Europe/Berlin).
- Tracking verified: 2026-09-28; implementation is unstarted, unassigned and undated.
<!-- tracking:end -->
