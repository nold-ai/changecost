# Tasks

All implementation and research tasks below remain unchecked. Planning approval does not authorize product implementation or live collection.

## 1. Scope and prerequisites

- [ ] 1.1 Start the separately authorized implementation on a focused branch and read the proposal, design and capability spec; verify Git status preserves unrelated work.
- [ ] 1.2 Confirm prerequisite issues and evidence gates; verify the dependency links in [change order](../../CHANGE_ORDER.md) match GitHub before behavior work.

## 2. Personal export profile

- [ ] 2.1 Resolve the feasibility gate using actual sanitized personal headers; verify no profile relies on Enterprise-only access.
- [ ] 2.2 Write failing tokens-only, unsupported-header, unknown-cost and privacy tests; record expected failures.
- [ ] 2.3 Implement approved local CSV parsing and minimal normalization; verify token categories, unknown cash and atomic failures.
- [ ] 2.4 Document supported fields, source dates and limitations in docs/providers/cursor.md; verify no statement promises unobserved dollar or session data.

## 3. Mapping and overlap

- [ ] 3.1 Write failing exact-file replay, overlapping-file and manual-versus-provider binding tests; verify expected failures.
- [ ] 3.2 Implement explicit record mapping and overlap diagnostics; verify repeat imports are idempotent and ambiguous overlaps stay incomplete.
- [ ] 3.3 Document mapping provenance and reconciliation limits with synthetic examples; verify unbound records remain visible through settle and explain.

## 4. Integration and handoff

- [ ] 4.1 Run applicable repository gates and `openspec validate provider-02-cursor-import --strict --no-interactive`; verify all relevant checks pass and report unavailable tooling explicitly.
- [ ] 4.2 For behavior changes, record actual failing-before/passing-after commands, timestamps and results in TDD_EVIDENCE.md and run fresh SpecFact review; verify reviewed scope, tool/module versions and analyzer availability, resolving findings or documenting narrow exceptions. For research-only work, record evidence review without invented TDD.
- [ ] 4.3 Open a focused PR with docs, verification, limits and rollback; verify reciprocal proposal/issue links and native hierarchy/dependencies, and archive only after implementation is accepted.
