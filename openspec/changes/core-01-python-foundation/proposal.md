# Establish the reproducible Python CLI foundation

## Why

The repository currently runs documentation hygiene only. A reproducible Python package and explicit development gates are needed before adding any economic behavior.

## What Changes

- Introduce the future src-layout package and installable CLI entry point.
- Make pyproject.toml and uv.lock authoritative for development and builds.
- Add meaningful installation/CLI smoke tests and formatting, typing, test and SpecFact review gates.
- Add executable documentation ownership/consistency, generated `llms.txt` integrity,
  changelog and package-version consistency checks with shared pre-commit/CI entry points.
- Prove the gates reject stale or malformed artifacts, including docs-only and
  workflow-only changes; keep repository quality separate from advisory cost checks.
- Make lock/build drift, installed-wheel isolation, read-only CLI behavior and
  staged-versus-working-tree checks explicit acceptance cases.

## Capabilities

### New Capabilities

- `python-foundation`: Establish the reproducible Python CLI foundation.

### Modified Capabilities

None; no main capability specs exist yet.

## Impact

Implementation affects the standalone Python CLI and repository quality workflow.
Documentation: README.md, CONTRIBUTING.md, llms.txt, CHANGELOG.md,
docs/agent-rules/50-quality-gates-and-review.md, documentation ownership metadata,
and CI contributor instructions. Implementation will add small repository-local
validators, fixtures and generated command/skill reference artifacts.
Verification: the scenarios in [the capability spec](specs/python-foundation/spec.md),
strict OpenSpec validation, applicable quality gates and truthful review evidence.
The original planning proposal added no runtime; the current branch includes its
authorized implementation alongside the prepared artifacts.

## Non-goals

No successful placeholder quote/settle operations, adapters, economic schemas,
release publishing/deployment, per-PR release bumps, registry/module signing,
cross-repository documentation checkout, hosted service, or SpecFact runtime dependency.

## Dependencies

None. PR [#21](https://github.com/nold-ai/changecost/pull/21) merged the preceding
source-feasibility research. Its remaining provider evidence gaps do not block
this independent foundation or authorize provider imports.

Dependencies are implementation prerequisites; planning can proceed together.
See [change order](../../CHANGE_ORDER.md) and [source assessment](../../../docs/research/pilot-source-assessment.md).

## Decisions and uncertainty

The Python/local-first scope is confirmed. Provider access and prediction quality
remain To-Validate. The [preparation evidence](design.md#preparation-evidence)
records the fresh baseline, tool drift and unresolved implementation verification.
The preparation changed planning only. The maintainer subsequently authorized
implementation on 2026-09-28; see [current task evidence](TDD_EVIDENCE.md), including
the unresolved required analyzer runtime.

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
- Tracking verified: 2026-09-28; GitHub remains Todo, unassigned and undated.
  Implementation exists locally; required verification and publication remain pending.
<!-- tracking:end -->
