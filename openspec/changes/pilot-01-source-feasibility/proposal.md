# Verify personal-account source feasibility

## Why

Personal IDE and CLI accounts may expose usage without billable money or stable session joins. Establishing the accessible evidence prevents the pilot from promising Enterprise-only reconciliation.

## What Changes

- Record a dated access and capability matrix for Copilot IDE, Copilot CLI,
  personal Cursor exports, Codex CLI/app/IDE usage and Claude Code CLI/IDE metrics.
- Define source-specific identifiers, economic units, completeness, correction semantics, and safe fixture requirements.
- Classify each capability as supported, partial, unavailable, or unverified and gate adapter implementation accordingly.

## Capabilities

### New Capabilities

- `source-feasibility`: Verify personal-account source feasibility.

### Modified Capabilities

None; no main capability specs exist yet.

## Impact

Future implementation affects the standalone Python CLI and local evidence workflow.
Documentation: docs/providers/source-feasibility.md, docs/providers/fixtures.md, and docs/research/pilot-source-assessment.md.
The maintainer also authorized comparison of supplied Enterprise Cursor/Copilot
projections on 2026-09-28, without extending adapter or collection scope.
The maintainer extended research scope to Codex and Claude Code on 2026-09-28;
docs/providers/codex-claude-metrics.md records their interfaces and evidence gaps.
This adds no adapter implementation or live collection.
Verification: the scenarios in [the capability spec](specs/source-feasibility/spec.md),
strict OpenSpec validation, applicable quality gates and truthful review evidence.
No runtime files or dependencies are introduced by this planning proposal.

## Non-goals

No account changes, paid plans, live collection in this planning delivery, Enterprise collector, undocumented scraping, or adapter implementation.

## Dependencies

None.

Dependencies are implementation prerequisites; planning can proceed together.
See [change order](../../CHANGE_ORDER.md) and [source assessment](../../../docs/research/pilot-source-assessment.md).

## Decisions and uncertainty

The Python/local-first scope is confirmed. Provider access and prediction quality
remain To-Validate. See [design](design.md) for decisions and evidence gates.

## Risks and rollback

- Provider access changes → date/version every observation and recheck before implementation.
- Redaction destroys join evidence → retain synthetic relationships and review the manifest.
- Unavailable exports → narrow documented support; leave dependent implementation blocked where no feasible path exists.

Planning rollback: revert the planning commit and close linked tracking items if
abandoned, preserving history. Later runtime rollback must preserve portable
evidence and prior local database versions; do not erase financial history.

## Source Tracking

<!-- tracking:start -->
- GitHub issue: [#9](https://github.com/nold-ai/changecost/issues/9) (native type: User Story).
- Parent feature: [#5](https://github.com/nold-ai/changecost/issues/5) — Pilot evidence.
- Parent epic: [#4](https://github.com/nold-ai/changecost/issues/4) — ChangeCost — validate change-level cost estimation and settlement.
- Project: [ChangeCost](https://github.com/orgs/nold-ai/projects/3) — private, status Todo.
- Source: maintainer-approved pilot plan, 2026-09-28 (Europe/Berlin).
- Tracking baseline: 2026-09-28; issue Todo, unassigned and undated. Research is
  underway locally; personal-source inspection remains pending. See [research evidence](RESEARCH_EVIDENCE.md).
<!-- tracking:end -->
