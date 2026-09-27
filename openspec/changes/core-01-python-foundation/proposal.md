# Establish the reproducible Python CLI foundation

## Why

The repository currently runs documentation hygiene only. A reproducible Python package and explicit development gates are needed before adding any economic behavior.

## What Changes

- Introduce the future src-layout package and installable CLI entry point.
- Make pyproject.toml and uv.lock authoritative for development and builds.
- Add meaningful installation/CLI smoke tests and formatting, typing, test and SpecFact review gates.

## Capabilities

### New Capabilities

- `python-foundation`: Establish the reproducible Python CLI foundation.

### Modified Capabilities

None; no main capability specs exist yet.

## Impact

Future implementation affects the standalone Python CLI and local evidence workflow.
Documentation: README.md, CONTRIBUTING.md, docs/agent-rules/50-quality-gates-and-review.md, and CI contributor instructions.
Verification: the scenarios in [the capability spec](specs/python-foundation/spec.md),
strict OpenSpec validation, applicable quality gates and truthful review evidence.
No runtime files or dependencies are introduced by this planning proposal.

## Non-goals

No successful placeholder quote/settle operations, adapters, economic schemas, release publishing, service, or SpecFact runtime dependency.

## Dependencies

None.

Dependencies are implementation prerequisites; planning can proceed together.
See [change order](../../CHANGE_ORDER.md) and [source assessment](../../../docs/research/pilot-source-assessment.md).

## Decisions and uncertainty

The Python/local-first scope is confirmed. Provider access and prediction quality
remain To-Validate. See [design](design.md) for decisions and evidence gates.

## Risks and rollback

- Tool drift → commit uv.lock and pin bootstrap/CI tool versions.
- Duplicate environment ownership → one uv workflow with Hatchling only for builds.
- Unavailable review runtime → document the gap and resolve it before claiming the behavior gate complete.

Planning rollback: revert the planning commit and close linked tracking items if
abandoned, preserving history. Later runtime rollback must preserve portable
evidence and prior local database versions; do not erase financial history.

## Source Tracking

<!-- tracking:start -->
- GitHub issue: [#10](https://github.com/nold-ai/changecost/issues/10) (native type: User Story).
- Parent feature: [#6](https://github.com/nold-ai/changecost/issues/6) — Local core and contracts.
- Parent epic: [#4](https://github.com/nold-ai/changecost/issues/4) — ChangeCost — validate change-level cost estimation and settlement.
- Project: [ChangeCost](https://github.com/orgs/nold-ai/projects/3) — private, status Todo.
- Source: maintainer-approved pilot plan, 2026-09-28 (Europe/Berlin).
- Tracking verified: 2026-09-28; implementation is unstarted, unassigned and undated.
<!-- tracking:end -->
