# Tasks

All implementation and research tasks below remain unchecked. Planning approval does not authorize product implementation or live collection.

## 1. Scope and prerequisites

- [ ] 1.1 Start the separately authorized implementation on a focused branch and read the proposal, design and capability spec; verify Git status preserves unrelated work.
- [ ] 1.2 Confirm prerequisite issues and evidence gates; verify the dependency links in [change order](../../CHANGE_ORDER.md) match GitHub before behavior work.

## 2. Normalization and identity

- [ ] 2.1 Write failing duplicate/retry/conflicting-key/cumulative-lane tests from the spec; verify expected failures before reconciliation code.
- [ ] 2.2 Implement minimal normalized evidence and dedupe rules; verify retry totals, exact-file idempotency and limited-overlap diagnostics.
- [ ] 2.3 Document evidence identity and supported dedupe guarantees in docs/settlement.md; verify examples distinguish snapshots and deltas.

## 3. Corrections and aggregation

- [ ] 3.1 Write failing correction-order, missing-cost, mixed-unit, partial-interval/open-run/zero-evidence coverage, late-binding, unknown/contradicted work-boundary and abandoned-outcome tests; record actual results.
- [ ] 3.2 Implement immutable settlement revisions, pending corrections, exact Decimal aggregates, revisioned full-change coverage and unbound remainder; verify all scenarios and restart replay pass.
- [ ] 3.3 Document provisional versus reconciled scope and explain traces; verify a synthetic corrected settlement can be traced to every contributing or excluded record.

## 4. Integration and handoff

- [ ] 4.1 Run applicable repository gates and `openspec validate settlement-01-reconciliation --strict --no-interactive`; verify all relevant checks pass and report unavailable tooling explicitly.
- [ ] 4.2 For behavior changes, record actual failing-before/passing-after commands, timestamps and results in TDD_EVIDENCE.md and run fresh SpecFact review; verify reviewed scope, tool/module versions and analyzer availability, resolving findings or documenting narrow exceptions. For research-only work, record evidence review without invented TDD.
- [ ] 4.3 Open a focused PR with docs, verification, limits and rollback; verify reciprocal proposal/issue links and native hierarchy/dependencies, and archive only after implementation is accepted.
