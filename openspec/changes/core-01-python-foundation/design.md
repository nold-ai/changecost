# Design: Establish the reproducible Python CLI foundation

## Context

See [proposal](proposal.md) and [capability spec](specs/python-foundation/spec.md).
The preparation baseline contained documentation and hygiene gates, with no product
package. Implementation was authorized on 2026-09-28; the local branch now contains
the foundation. [Actual evidence](TDD_EVIDENCE.md) records completed checks and the
unresolved analyzer-runtime gate. This design states the contract, not proof of delivery.

## Goals / Non-Goals

**Goals:** Make the specified capability local, reproducible and explicit about missing evidence.

**Non-Goals:** No successful placeholder quote/settle operations, adapters, economic
schemas, release publishing/deployment, mandatory per-PR version bumps, module
signing/registry machinery, sibling-repository checks, or SpecFact runtime dependency.

## Decisions

1. Use Python >=3.11, src/changecost, Typer for the CLI and Pydantic for upcoming validated contracts. Declare metadata, Apache-2.0 license, entry point and dependencies in pyproject.toml; build wheels/sdists through Hatchling.

2. Use uv for resolution, a committed uv.lock, uv sync --locked and uv run --locked for contributor environments. Hatchling is the build backend, not the Hatch environment runner. Hatch and Poetry are viable alternatives but a second resolver/environment layer adds no pilot value. APM agent-package management is a separate concern. Replace the temporary requirements-dev.txt/manual venv instructions when this change is implemented; do not maintain two dependency authorities.

3. Use pytest, Ruff format/check and BasedPyright with explicit project configuration and pinned development resolution. Keep make check as the common local/CI entry point and add distinct documented targets for formatting, types, tests and review. No empty test suite or blanket type-ignore baseline.

4. Pin uv and supported CI Python versions at implementation time; test minimum 3.11 and one current supported version. Exercise built-wheel installation in a clean environment without SpecFact. CLI help/version must work offline; unimplemented operations must not report success.

5. Retain the manual SpecFact hook and make review, recording CLI/module versions and actual analyzer coverage. The complete aggregate must require review for behavior-affecting changes (source, tests, dependency/build configuration, validators and CI wiring); docs-only changes still run their applicable gates and record why behavior review is not applicable. A manual hook alone does not satisfy aggregate/CI coverage. A supported review runtime is a development requirement; unavailability is an explicit unresolved gate, not a passing product review.

### Package and CLI acceptance details

Normal verification uses locked sync/run/export commands: stale or absent locks
fail without rewriting them. Dependency updates use a separate deliberate lock
operation. Keep a build dependency group containing Hatchling in `pyproject.toml`
and `uv.lock`; derive temporary hashed build constraints from that group with
`uv export --locked --only-group build --no-emit-project`. Pass those constraints
to isolated `uv build --build-constraints ... --require-hashes`; test the backend
and transitive build dependency coverage. Do not assume an ordinary build consumes
the project lock. Derived constraints are disposable output, not a second manually
maintained dependency authority. Pin exact tooling after compatibility checks in
implementation; PATH versions observed during preparation are not automatic pins.

Build the wheel through the sdist, then install into a fresh environment containing
only declared runtime dependencies. Run its installed entry point from a temporary
directory outside the checkout, with no source-path injection and no SpecFact.
Installation may fetch dependencies; the installed CLI must run offline. A fixture
must block network attempts during execution rather than merely omit credentials.
Assert `changecost --help` and `changecost --version` exit zero, with the version
matching installed metadata. Bare invocation prints usage with a nonzero status;
unknown operations also fail clearly. Help/version/errors create no database,
configuration or evidence files in the working directory or user data locations.
Only the root help/version surface is delivered here; do not register the five
planned command families as working operations or introduce economic schemas.

Use explicit Hatchling distribution selections. Inspect wheel/sdist contents with
synthetic private-file sentinels to prove `.changecost/`, `.specfact/`, `artifacts/`,
credentials and raw provider evidence are excluded. Include the license, package
metadata and required build inputs; the sdist must build without the source checkout.
Pydantic remains the selected contract library; SQLite schemas and contract models
belong to `core-02-change-run-contracts`, not this packaging change.

## Repository gate contract

This foundation owns development quality gates before economic behavior is added.
`workflow-01-advisory-ci` later supplies a product budget-summary example; its
advisory exit policy does not make repository quality checks advisory. The baseline
bootstrap had only hygiene/OpenSpec automation. The local implementation now wires
the contracts below; full review assurance is still incomplete.

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
comparison SHA explicitly for diff-sensitive checks: check out the PR head SHA
and compare against its merge-base with the event's base SHA; use the push event's
`before` SHA for main, and a required explicit base for manual runs. Record the
checked head and base. Do not mix the default PR synthetic merge checkout with
head-only evidence or substitute HEAD~1 for a multi-commit push. Unresolvable
history fails with a diagnostic, not an empty diff.
Define two local inputs: `make check` inspects the working tree (including an
explicit manifest of intended new files), while commit hooks inspect the complete
Git index, including staged additions, renames and deletions. A temporary snapshot
must preserve the user's index and working files. Unstaged fixes cannot satisfy a
commit gate; an unstaged new file cannot satisfy a staged reference to that file.
Use the same leaf validator semantics with an explicit snapshot/root and base.
CI failures block the workflow result; configuring remote branch-protection rules is a separate action.

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

Ownership covers maintained `openspec/**` artifacts and `.agents/skills/**` as
well as the docs above; archived historical evidence needs named handling, not
silent exclusion. Source-content digests for rationales exclude the rationale
record itself and generated output that derives from it, avoiding self-reference;
renames, deletions and changed scope invalidate a reused rationale.

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

## Preparation evidence

Reviewed on 2026-09-28 (Europe/Berlin) against fetched main
`141b9b3ea5226dad672b0910e6ccf79f2403f8b7` at 13:45:08 +02:00.
PR [#21](https://github.com/nold-ai/changecost/pull/21) is merged; issue #9 is
closed but its source-inspection tasks 2.1/2.2 remain partial. Foundation issue
[#10](https://github.com/nold-ai/changecost/issues/10) is open/Todo, a native User
Story under #6 in private project 3, with no native blocked-by relationships.
These observations establish selection, not implementation completion.

| Claim | Finding and impact |
| --- | --- |
| Package/gates already exist | Confirmed absent: no pyproject, lock, source package or tests at this baseline; Makefile runs hygiene and OpenSpec only. All foundation tasks were pending at preparation; see current tasks/evidence. |
| Current bootstrap versions | CI pins OpenSpec 1.13.0 and Python 3.12; local OpenSpec is 1.13.2, pre-commit 4.6.2, uv 0.12.19 and Python 3.14.7. Reconcile local/CI pins during implementation; no compatibility pass follows from installation. |
| Review readiness | Installed SpecFact CLI 0.55.4 and review module 0.50.1 were inspected. No analyzer run was performed in this preparation; resolve runtime/coverage on the actual Python package before claiming review completion. |
| Provider feasibility as a gate | No foundation dependency edge exists. Partial source research remains relevant to later adapters, not package/help or repository validators. |
| Bootstrap language comments | `requirements-dev.txt` and `.gitignore` still say language is undecided. Remove the obsolete requirements authority and correct the comment during implementation. |

Primary documentation accessed 2026-09-28 (Europe/Berlin):

- [uv locking/sync](https://docs.astral.sh/uv/concepts/projects/sync/): ordinary
  run can update the lock; `--locked` rejects drift, whereas `--frozen` skips the
  freshness check. Use locked verification.
- [uv builds](https://docs.astral.sh/uv/concepts/projects/build/) and
  [exports](https://docs.astral.sh/uv/concepts/projects/export/): build constraints
  and hashes control build resolution. Local uv 0.12.19 help confirms the planned
  build/export flags; the package-specific build remains to be tested.
- [Hatchling file selection](https://hatch.pypa.io/latest/config/build/): explicit
  wheel/sdist selections support a small distribution; inspect archive members
  and build the sdist in isolation to verify the chosen configuration.
- [GitHub workflow events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows):
  PR events default to a synthetic merge SHA. Select the head explicitly so gate
  evidence and comparison inputs refer to the same contents.

Confidence: high in pending scope and no dependency blocker; medium in tooling
readiness until locked install/build, CI matrix and review analyzers are exercised.
No material product decision is outstanding. Implementation must verify exact
pins, the second supported Python version, dependency licenses/advisories and the
supported SpecFact runtime before reporting ready-to-merge. No delivery duration
is estimated; this is package plus repository-validator work, without paid
infrastructure or provider calls.

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
Use synthetic fixtures; there is no deployed service or database migration in
this foundation. Revert its implementation commit and recreate the development
environment from the restored dependency authority if rollback is needed. Preserve
all local provider evidence. Planning rollback reverts only this reconciliation;
keep the existing implementation story unless its work is explicitly abandoned.

## Verification

Each requirement has Given/When/Then scenarios. Exercise negative paths and privacy
boundaries alongside the success cases. Run strict OpenSpec validation and applicable
repository gates; record actual results, not anticipated test or review outcomes.

## Implemented choices and remaining verification

The local implementation uses initial unreleased version `0.1.0.dev0`, Typer for
help/version, Python 3.11.15/3.13.14 and the committed uv lock. Pydantic remains
selected for future contracts; adding an unused runtime dependency is deferred to
that change. `quality/` is repository-only tooling and is excluded from artifacts.
Its JSON ownership/index inputs are small explicit inventories, not a docs framework.
The complete aggregate runs every applicable leaf and returns nonzero for missing
review assurance. Current macOS and Docker namespace diagnostics remain unresolved;
no review waiver, runtime descriptor or security-control change was introduced.
See [implementation evidence](TDD_EVIDENCE.md) for actual commands and limits.
