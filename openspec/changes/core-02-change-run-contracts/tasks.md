# Tasks

All implementation and research tasks below remain unchecked. Planning approval does not authorize product implementation or live collection.

## 1. Scope and prerequisites

- [ ] 1.1 Start the separately authorized implementation on a focused branch and read the proposal, design and capability spec; verify Git status preserves unrelated work.
- [ ] 1.2 Confirm prerequisite issues and evidence gates; verify the dependency links in [change order](../../CHANGE_ORDER.md) match GitHub before behavior work.

## 2. Contracts and serialization

- [ ] 2.1 Derive failing contract tests from each scenario, including non-finite decimals and unsupported versions; verify failures reflect absent contracts.
- [ ] 2.2 Implement versioned Pydantic records and portable JSON validation; verify exact round trips and invalid-value rejection pass.
- [ ] 2.3 Document field semantics, units, completeness and version policy in docs/contracts.md; verify synthetic examples validate.

## 3. Persistence and binding

- [ ] 3.1 Write failing transactional/restart/concurrent-bind tests; verify conflict and rollback behavior is not already satisfied by a test setup error.
- [ ] 3.2 Implement SQLite migrations, atomic writes and explicit bind with provenance; verify idempotency, competing writers and restart tests pass.
- [ ] 3.3 Document local path overrides, backups and binding correction limitations; verify a portable export survives restore into a fresh database.

## 4. Integration and handoff

- [ ] 4.1 Run applicable repository gates and `openspec validate core-02-change-run-contracts --strict --no-interactive`; verify all relevant checks pass and report unavailable tooling explicitly.
- [ ] 4.2 For behavior changes, record actual failing-before/passing-after commands, timestamps and results in TDD_EVIDENCE.md and run fresh SpecFact review; verify reviewed scope, tool/module versions and analyzer availability, resolving findings or documenting narrow exceptions. For research-only work, record evidence review without invented TDD.
- [ ] 4.3 Open a focused PR with docs, verification, limits and rollback; verify reciprocal proposal/issue links and native hierarchy/dependencies, and archive only after implementation is accepted.
