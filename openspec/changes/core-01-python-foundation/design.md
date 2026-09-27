# Design: Establish the reproducible Python CLI foundation

## Context

See [proposal](proposal.md) and [capability spec](specs/python-foundation/spec.md).
The current repository contains documentation and hygiene gates, with no product
package or runtime. This design describes later implementation, not delivered behavior.

## Goals / Non-Goals

**Goals:** Make the specified capability local, reproducible and explicit about missing evidence.

**Non-Goals:** No successful placeholder quote/settle operations, adapters, economic schemas, release publishing, service, or SpecFact runtime dependency.

## Decisions

1. Use Python >=3.11, src/changecost, Typer for the CLI and Pydantic for upcoming validated contracts. Declare metadata, Apache-2.0 license, entry point and dependencies in pyproject.toml; build wheels/sdists through Hatchling.

2. Use uv for resolution, a committed uv.lock, uv sync --locked and uv run for contributor environments. Hatchling is the build backend, not the Hatch environment runner. Hatch and Poetry are viable alternatives but a second resolver/environment layer adds no pilot value. APM agent-package management is a separate concern. Replace the temporary requirements-dev.txt/manual venv instructions when this change is implemented; do not maintain two dependency authorities.

3. Use pytest, Ruff format/check and BasedPyright with explicit project configuration and pinned development resolution. Keep make check as the common local/CI entry point and add distinct documented targets for formatting, types, tests and review. No empty test suite or blanket type-ignore baseline.

4. Pin uv and supported CI Python versions at implementation time; test minimum 3.11 and one current supported version. Exercise built-wheel installation in a clean environment without SpecFact. CLI help/version must work offline; unimplemented operations must not report success.

5. Retain the manual SpecFact hook and make review, recording CLI/module versions and actual analyzer coverage. A supported review runtime is a development requirement; unavailability is an explicit unresolved gate, not a passing product review.

## Dependencies and evidence

None.

Shared boundaries and current provider evidence are recorded in the
[source assessment](../../../docs/research/pilot-source-assessment.md).
No provider-specific mapping becomes supported merely by appearing in this plan.

## Risks / Trade-offs

- Tool drift → commit uv.lock and pin bootstrap/CI tool versions.
- Duplicate environment ownership → one uv workflow with Hatchling only for builds.
- Unavailable review runtime → document the gap and resolve it before claiming the behavior gate complete.

## Migration Plan

After separate implementation authorization, land this change in dependency order
with spec-derived failing and passing evidence. Update README.md, CONTRIBUTING.md, docs/agent-rules/50-quality-gates-and-review.md, and CI contributor instructions.
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
