# Tasks

Implementation was authorized on 2026-09-28. Checked tasks have local evidence in
[TDD_EVIDENCE.md](TDD_EVIDENCE.md). Full analyzer assurance and remote CI/PR work
remain pending; live collection is not authorized.

## 1. Scope and prerequisites

- [x] 1.1 Refresh main and reconcile this preparation by change identity using the shared workflow; start the separately authorized implementation on a focused branch, read proposal/design/spec and verify Git status preserves unrelated work.
- [ ] 1.2 Confirm #10 remains pending with no prerequisite edges; recheck [preparation evidence](design.md#preparation-evidence), choose exact compatible tool pins/Python matrix and verify a supported SpecFact review setup before claiming behavior gates complete.

## 2. Package and environment

- [x] 2.1 Derive packaging/help/version, empty/unknown invocation, read-only offline execution, missing/stale lock and private-file exclusion acceptance tests; run before package code and record failures caused by missing behavior rather than broken test tooling.
- [x] 2.2 Add pyproject.toml, src layout, root Typer help/version and uv.lock; constrain/hash build dependencies from the locked build group, verify drift rejection, build the wheel through the sdist, inspect both archives and run installed-wheel tests outside the checkout without SpecFact.
- [x] 2.3 Replace bootstrap environment docs and requirements-dev.txt authority, correct obsolete language comments and document locked commands/build constraints; verify README commands in a fresh environment, runtime dependency isolation and no economic commands/models/database added.

## 3. Development quality

- [x] 3.1 Configure Ruff, BasedPyright and pytest, then run deliberate failure probes; verify gates detect actual defects before removing probes.
- [ ] 3.2 Update make targets, hooks and pinned CI setup; verify local and CI run the same checks on Python 3.11 and the chosen additional supported version.
- [x] 3.3 Document uv versus Hatchling responsibilities and review runtime setup; verify actual SpecFact tool/module versions and analyzer coverage are recorded without fabricated passes.
- [x] 3.4 Derive failing ownership/consistency fixtures for new unmapped docs, orphaned source mappings, broken links/anchors and reused no-doc-change rationales; implement a small ownership map/checker and verify repaired fixtures pass while original research hashes remain unchanged; cover maintained OpenSpec/skill files, rename/delete cases and non-self-referential rationale digests, and document the map/rationale format.
- [x] 3.5 Write failing stale/missing/duplicate llms and command/skill inventory tests; implement deterministic offline generation from local canonical sources plus a read-only check mode, migrate the index, and verify repeat generation is byte-stable without publishing planned commands; document generator inputs and regeneration/check commands.
- [x] 3.6 Write failing changelog/version fixtures for absent new Unreleased entries, stale exceptions and disagreement among package/CLI/build/lock versions; implement checks with explicit comparison bases and verify unreleased no-bump, initial-version and narrow editorial exceptions without PyPI access; document comparison bases, version policy and exception format.
- [x] 3.7 Wire the same leaf docs/metadata/workflow validators into pre-commit, documented make targets and CI without recursion or docs-only bypass; test working-tree manifests versus complete staged snapshots, unstaged fixes/missing targets, PR head/base and multi-commit push intervals, complete CI inventory and aggregate propagation of failed/skipped/stale required checks; document snapshot modes and behavior-review applicability.
- [x] 3.8 Add pinned workflow syntax validation and scoped locked-dependency advisory/license checks; verify malformed workflow rejection, actual audit coverage and honest unavailable-data handling with least-privilege CI and no publication/deployment jobs.

## 4. Integration and handoff

- [ ] 4.1 Run applicable repository gates and `openspec validate core-01-python-foundation --strict --no-interactive`; verify all relevant checks pass, docs ownership/changelog/version/generated-index evidence matches the final contents, and unavailable tooling is reported explicitly.
- [ ] 4.2 Record actual failing-before/passing-after commands, timestamps and results in TDD_EVIDENCE.md throughout implementation, then run fresh SpecFact review on the final contents; verify scope, versions and analyzer availability, resolving findings or documenting narrow exceptions. Preparation checks do not count as product TDD.
- [ ] 4.3 Open a focused PR with docs, verification, limits and rollback; verify reciprocal proposal/issue links and native hierarchy/dependencies, and archive only after implementation is accepted.

## Outstanding validation

Tasks 1.2, 4.1 and 4.2 retain pending capsule assurance because SpecFact cannot
execute its required capsules on macOS or within the available Docker namespace
policy. On 2026-09-28 the maintainer accepted this known local limitation and
assigned capsule execution to GitHub CI; it no longer blocks this change’s
commit/push handoff after the passing local checks and independent reviews.
Both Python matrix aggregates ran all other checks successfully. Task 3.2 has
local matrix and executable wiring evidence. [PR #22](https://github.com/nold-ai/changecost/pull/22)
is open with the combined preparation and implementation. Its first remote CI run
failed both capsule setup and the Go-built actionlint version check. The next run
executed capsules and passed workflow validation, but full review found complexity,
coverage, an isolated uv fixture failure and an analyzer dependency mismatch.
Run 36429886815 then passed nine analyzers, with only uv's isolated interpreter
probe incompatible with the capsule wrapper. The required host-side lock proof
CI comparison wiring and external-validator collision corrections remain subject
to fresh hosted validation; task 4.3 remains incomplete
until final review and tracking verification. No required gate was waived.
