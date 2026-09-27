# Tasks

All implementation and research tasks below remain unchecked. Planning approval does not authorize product implementation or live collection.

## 1. Scope and prerequisites

- [ ] 1.1 Start the separately authorized implementation on a focused branch and read the proposal, design and capability spec; verify Git status preserves unrelated work.
- [ ] 1.2 Confirm prerequisite issues and evidence gates; verify the dependency links in [change order](../../CHANGE_ORDER.md) match GitHub before behavior work.

## 2. Evidence inventory

- [ ] 2.1 Record per-surface source/version/tier and exact access steps; verify every matrix row has a citation or observed-evidence reference.
- [ ] 2.2 Inspect authorized sanitized headers and representative events, including missing fields and repeated billing attributes; verify the matrix distinguishes supported, partial, unavailable and unverified.
- [ ] 2.3 Document the evidence gate and exclusions in docs/providers/source-feasibility.md; verify each planned adapter capability has an explicit disposition.

## 3. Fixture contract

- [ ] 3.1 Define allowlisted fields and deterministic ID replacement for each feasible source; verify a redaction review finds no prompts, secrets or actual account identifiers.
- [ ] 3.2 Provide synthetic edge cases for missing IDs/costs, duplicates and corrections plus provenance notes; verify they preserve required joins without claiming they are live pilot observations.
- [ ] 3.3 Record unresolved evidence requests and downstream blocking decisions; verify unavailable capabilities do not appear as supported in adapter docs.

## 4. Integration and handoff

- [ ] 4.1 Run applicable repository gates and `openspec validate pilot-01-source-feasibility --strict --no-interactive`; verify all relevant checks pass and report unavailable tooling explicitly.
- [ ] 4.2 For behavior changes, record actual failing-before/passing-after commands, timestamps and results in TDD_EVIDENCE.md and run fresh SpecFact review; verify reviewed scope, tool/module versions and analyzer availability, resolving findings or documenting narrow exceptions. For research-only work, record evidence review without invented TDD.
- [ ] 4.3 Open a focused PR with docs, verification, limits and rollback; verify reciprocal proposal/issue links and native hierarchy/dependencies, and archive only after implementation is accepted.
