# Design: Establish the reproducible Python CLI foundation

## Context

See [proposal](proposal.md) and [capability spec](specs/python-foundation/spec.md).
The current repository contains documentation and hygiene gates, with no product
package or runtime. This design describes later implementation, not delivered behavior.

## Goals / Non-Goals

**Goals:** Make the specified capability local, reproducible and explicit about missing evidence.

**Non-Goals:** No successful placeholder quote/settle operations, adapters, economic
schemas, release publishing/deployment, mandatory per-PR version bumps, module
signing/registry machinery, sibling-repository checks, or SpecFact runtime dependency.

## Decisions

1. Use Python >=3.11, src/changecost, Typer for the CLI and Pydantic for upcoming validated contracts. Declare metadata, Apache-2.0 license, entry point and dependencies in pyproject.toml; build wheels/sdists through Hatchling.

2. Use uv for resolution, a committed uv.lock, uv sync --locked and uv run for contributor environments. Hatchling is the build backend, not the Hatch environment runner. Hatch and Poetry are viable alternatives but a second resolver/environment layer adds no pilot value. APM agent-package management is a separate concern. Replace the temporary requirements-dev.txt/manual venv instructions when this change is implemented; do not maintain two dependency authorities.

3. Use pytest, Ruff format/check and BasedPyright with explicit project configuration and pinned development resolution. Keep make check as the common local/CI entry point and add distinct documented targets for formatting, types, tests and review. No empty test suite or blanket type-ignore baseline.

4. Pin uv and supported CI Python versions at implementation time; test minimum 3.11 and one current supported version. Exercise built-wheel installation in a clean environment without SpecFact. CLI help/version must work offline; unimplemented operations must not report success.

5. Retain the manual SpecFact hook and make review, recording CLI/module versions and actual analyzer coverage. A supported review runtime is a development requirement; unavailability is an explicit unresolved gate, not a passing product review.

## Repository gate contract

This foundation owns development quality gates before economic behavior is added.
`workflow-01-advisory-ci` later supplies a product budget-summary example; its
advisory exit policy does not make repository quality checks advisory. The current
bootstrap only has hygiene/OpenSpec automation. The contracts below are planned,
not checks that already run.

### One local and CI check surface

Keep `make check` as the aggregate and document leaf targets for docs, metadata,
workflow syntax, language checks, tests and review. Pre-commit hooks invoke the
same leaf validators as CI, not the aggregate recursively. Pin tools through the
chosen uv resolution or explicit non-Python tool pins; no separate Hatch runtime.
Cheap format/syntax/metadata failures precede expensive tests/review. Fast local
hooks may scope work, but a clean CI checkout must run the complete applicable
contract and an aggregate cannot be green when a required child failed or skipped.

Run CI on every PR to main and push to main, including docs/skills/metadata/workflow
changes; no blanket docs-only bypass. Validate GitHub Actions with a pinned workflow
validator. Use read-only permissions, no persisted checkout credentials and no
privileged execution of PR code. Fetch sufficient history and pass a resolved
comparison SHA explicitly for diff-sensitive checks: PR merge-base to the tested
head, pre-push commit to the pushed head for main, and a documented explicit base
for manual runs. Unresolvable history fails with a diagnostic, not an empty diff.
Local checks use equivalent intended staged content, including new files; unstaged
docs must not satisfy a gate for a commit that omits them. CI failures block the
workflow result; configuring remote branch-protection rules is a separate action.

### Documentation ownership and consistency

Use one small repository-local ownership map covering maintained root docs,
`docs/**`, agent guidance and `llms.txt`. Each maintained page has a logical owner
component (not an invented person), canonical source paths/globs and an explicit
manual/generated classification. Validate coverage, unique mappings, actual
source matches and internal links/anchors. Removed/renamed sources or pages must
update the mapping. A new unmapped page fails; changing the ownership map itself
also runs validation. A last-reviewed date alone is not proof of consistency.

When tracked sources change, require the affected docs to be updated or a narrow
checked-in no-doc-change rationale bound to those source contents. Reusing a
rationale for different content fails. The implementation must define and test
that small record format; it is review evidence, not another task ledger. Keep
semantic review of prose/examples in the review workflow: machine checks establish
coverage and detectable drift, not that arbitrary English is correct.

The original research report/source export stay immutable with their existing
hashes. Register explicit path-specific provenance exemptions rather than rewriting
them or excluding all research/docs. Licenses and generated artifacts likewise
need named handling and reasons, not a blanket bypass or copied Jekyll frontmatter.

### llms.txt and executable command contracts

Replace the manual index with deterministic output from repository-local skill
metadata, declared documentation entry points and the implemented CLI help tree.
Keep generated command/option references and `llms.txt` synchronized through one
renderer with write and read-only check modes. The check reports a useful diff and
fails for missing, stale, duplicate or dangling entries. Render only implemented
CLI commands/options; planned capabilities remain clearly marked planning links.
Do not treat schema identifiers such as `changecost/v1` as package versions.

Run the renderer check both through pre-commit and the normal test/CI gate so
bypassing a hook cannot merge stale output. Skill metadata, command definitions,
documentation entry points, generator/config and generated-file edits all activate
it; full CI runs it regardless of narrow local triggers. Repeat generation must
be byte-stable and offline without SpecFact, sibling repos or provider access.
Test documented examples using named synthetic fixtures, never executing arbitrary
shell snippets extracted from documentation. Maintain clear ownership of generated
regions so contributor-authored text is not silently overwritten.

### Changelog and version freshness

`pyproject.toml` is the package version authority; derive CLI version from installed
metadata rather than maintaining a second literal. Compare it with built wheel/
sdist metadata, the project entry in `uv.lock` and any declared version references.
Reject inconsistent or decreasing versions against the explicit base; allow the
initial package version when no base package exists. No network/PyPI comparison,
release tag or publish step is needed for this unreleased project.

Meaningful product, contract or contributor-workflow changes require a substantive
Unreleased changelog entry relative to the comparison base. A narrow no-entry
rationale for an editorial/test-only change must identify its scope and be bound
to the reviewed contents; touching a date or retaining an old entry does not count.
Document and test exception handling; changed scope invalidates prior rationale.
Routine unreleased work keeps its version unless an explicit version decision
requires a bump. A deliberate bump must synchronize metadata/docs and its changelog
record. Do not require a bump for every doc, skill or planning PR, or manufacture
a release header for an unreleased change.

### Scoped security and proof

Retain secret detection, lockfile/license review and meaningful static checks for
the Python scope. Define a pinned dependency-advisory audit for the actual locked
dependencies, with a documented local command and CI coverage when dependencies
change. Unavailable advisory data is incomplete evidence, not zero vulnerabilities;
do not add remote services or copy SpecFact's signed-module exception machinery.
Record any reviewed exception narrowly with reason and scope.

Gate fixtures must first demonstrate rejection of missing ownership, stale command
or skill output, broken references, stale changelog/rationales, conflicting versions,
malformed workflows, missing comparison history and incomplete check execution.
Then repair the fixture and record passing evidence. Parity tests cover trigger and
command wiring, staged/untracked input and the aggregate failure result. Keep helper
code small and reviewable; avoid a general documentation framework.

## Reference adaptation

Local primary source snapshots inspected on 2026-09-28 (Europe/Berlin):

- `specfact-cli` at `d306d2a8e855cba493c8e5b07093565be75e89cc`:
  `.pre-commit-config.yaml`, `scripts/check_doc_frontmatter.py`,
  `scripts/check-documentation-accountability.py`, version-check wiring in
  `pyproject.toml`, and `.github/workflows/pr-orchestrator.yml`.
- `specfact-cli-modules` at `bdaab8a3fc48c7321d21127e2b0042946cd90bfa`:
  `.pre-commit-config.yaml`, `pyproject.toml`, `.github/workflows/docs-review.yml`,
  `scripts/generate-command-overview.py` and its llms freshness tests.

Adopt their canonical-source comparison, ownership, failure-probe and local/CI
parity patterns. Exclude multi-repo command registries, module signing, Jekyll,
publishing, PyPI-ahead checks and large job matrices unrelated to ChangeCost.

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
with spec-derived failing and passing evidence. Update README.md, CONTRIBUTING.md,
docs/agent-rules/50-quality-gates-and-review.md, llms.txt, CHANGELOG.md, ownership
metadata and CI contributor instructions. Migrate existing maintained documents
to explicit ownership and record path-specific exemptions without altering the
original research bytes. Document baseline selection and all local gate commands.
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
