# Tasks

All implementation and research tasks below remain unchecked. Planning approval does not authorize product implementation or live collection.

## 1. Scope and prerequisites

- [ ] 1.1 Start the separately authorized implementation on a focused branch and read the proposal, design and capability spec; verify Git status preserves unrelated work.
- [ ] 1.2 Confirm prerequisite issues and evidence gates; verify the dependency links in [change order](../../CHANGE_ORDER.md) match GitHub before behavior work.

## 2. CLI presentation and checks

- [ ] 2.1 Write failing empty-store registration/quote/bind/import/outcome integration, JSON/stdout/stderr, incompatible-unit, incomplete-settlement (subtotals below and above budget), complete-total and advisory-exit tests; verify expected failures.
- [ ] 2.2 Implement consistent result/error presentation and scope-aware completeness checks before compatible budget comparisons; verify all five command families follow documented semantics.
- [ ] 2.3 Document a runnable fresh-store walkthrough and human/JSON examples, provisional-subtotal unknown results and exit codes in docs/cli.md; verify examples run against synthetic artifacts.

## 3. Actions example

- [ ] 3.1 Write failing escaping and no-shell-interpolation tests for summary rendering; verify malicious synthetic labels are treated as data.
- [ ] 3.2 Add an opt-in Actions example with read-only permissions and standalone artifact inputs; verify it runs offline without provider credentials and leaves budget advice nonblocking.
- [ ] 3.3 Document safe integration and artifact retention in docs/ci.md; verify no example changes branch protection, IDE settings or account configuration.

## 4. Integration and handoff

- [ ] 4.1 Run applicable repository gates and `openspec validate workflow-01-advisory-ci --strict --no-interactive`; verify all relevant checks pass and report unavailable tooling explicitly.
- [ ] 4.2 For behavior changes, record actual failing-before/passing-after commands, timestamps and results in TDD_EVIDENCE.md and run fresh SpecFact review; verify reviewed scope, tool/module versions and analyzer availability, resolving findings or documenting narrow exceptions. For research-only work, record evidence review without invented TDD.
- [ ] 4.3 Open a focused PR with docs, verification, limits and rollback; verify reciprocal proposal/issue links and native hierarchy/dependencies, and archive only after implementation is accepted.
