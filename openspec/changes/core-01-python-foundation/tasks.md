# Tasks

All implementation and research tasks below remain unchecked. Planning approval does not authorize product implementation or live collection.

## 1. Scope and prerequisites

- [ ] 1.1 Start the separately authorized implementation on a focused branch and read the proposal, design and capability spec; verify Git status preserves unrelated work.
- [ ] 1.2 Confirm prerequisite issues and evidence gates; verify the dependency links in [change order](../../CHANGE_ORDER.md) match GitHub before behavior work.

## 2. Package and environment

- [ ] 2.1 Create the authorized implementation branch and derive packaging/help acceptance tests; run them before package code and record the actual missing-behavior failure.
- [ ] 2.2 Add pyproject.toml, src layout, Typer entry point, Hatchling build and uv.lock; verify locked sync, wheel/sdist build and clean-wheel help/version pass.
- [ ] 2.3 Replace bootstrap environment documentation and redundant dependency declarations; verify README commands work in a fresh environment and SpecFact is absent from runtime dependencies.

## 3. Development quality

- [ ] 3.1 Configure Ruff, BasedPyright and pytest, then run deliberate failure probes; verify gates detect actual defects before removing probes.
- [ ] 3.2 Update make targets, hooks and pinned CI setup; verify local and CI run the same checks on Python 3.11 and the chosen additional supported version.
- [ ] 3.3 Document uv versus Hatchling responsibilities and review runtime setup; verify actual SpecFact tool/module versions and analyzer coverage are recorded without fabricated passes.
- [ ] 3.4 Derive failing ownership/consistency fixtures for new unmapped docs, orphaned source mappings, broken links/anchors and reused no-doc-change rationales; implement a small ownership map/checker and verify repaired fixtures pass while original research hashes remain unchanged.
- [ ] 3.5 Write failing stale/missing/duplicate llms and command/skill inventory tests; implement deterministic offline generation from local canonical sources plus a read-only check mode, migrate the index, and verify repeat generation is byte-stable without publishing planned commands.
- [ ] 3.6 Write failing changelog/version fixtures for absent new Unreleased entries, stale exceptions and disagreement among package/CLI/build/lock versions; implement checks with explicit comparison bases and verify unreleased no-bump, initial-version and narrow editorial exceptions without PyPI access.
- [ ] 3.7 Wire the same leaf docs/metadata/workflow validators into pre-commit, documented make targets and CI without recursion or docs-only bypass; test staged additions versus unstaged fixes, complete CI inventory, trigger parity, missing-history failures and aggregate propagation of failed/skipped required checks.
- [ ] 3.8 Add pinned workflow syntax validation and scoped locked-dependency advisory/license checks; verify malformed workflow rejection, actual audit coverage and honest unavailable-data handling with least-privilege CI and no publication/deployment jobs.

## 4. Integration and handoff

- [ ] 4.1 Run applicable repository gates and `openspec validate core-01-python-foundation --strict --no-interactive`; verify all relevant checks pass, docs ownership/changelog/version/generated-index evidence matches the final contents, and unavailable tooling is reported explicitly.
- [ ] 4.2 For behavior changes, record actual failing-before/passing-after commands, timestamps and results in TDD_EVIDENCE.md and run fresh SpecFact review; verify reviewed scope, tool/module versions and analyzer availability, resolving findings or documenting narrow exceptions. For research-only work, record evidence review without invented TDD.
- [ ] 4.3 Open a focused PR with docs, verification, limits and rollback; verify reciprocal proposal/issue links and native hierarchy/dependencies, and archive only after implementation is accepted.
