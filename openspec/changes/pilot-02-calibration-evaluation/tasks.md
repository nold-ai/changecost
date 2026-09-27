# Tasks

All implementation and research tasks below remain unchecked. Planning approval does not authorize product implementation or live collection.

## 1. Scope and prerequisites

- [ ] 1.1 Start the separately authorized implementation on a focused branch and read the proposal, design and capability spec; verify Git status preserves unrelated work.
- [ ] 1.2 Confirm prerequisite issues and evidence gates; verify the dependency links in [change order](../../CHANGE_ORDER.md) match GitHub before behavior work.

## 2. Protocol and replay

- [ ] 2.1 Write the chronological protocol, metric formulas, exclusions and decision rubric before inspecting live outcomes; verify a review records the protocol version.
- [ ] 2.2 Write failing replay/leakage, repository-fallback equivalence, joint-unpriced, unexpected-asymmetry rejection, partial-truth exclusion, frozen-truth cutoff, unavailable cross-store history and denominator tests with synthetic fixtures; verify expected failures.
- [ ] 2.3 Implement one-initial-quote-per-change replay, the offline evaluation harness and repository-wide baseline with matched availability checks; verify exact synthetic metrics and rerun determinism.
- [ ] 2.4 Document invocation and environment in docs/pilot/evaluation.md; verify another contributor can reproduce the synthetic report.

## 3. Pilot assessment

- [ ] 3.1 Confirm both adapter dependencies and live collection authorization; verify each source capability is supported or explicitly reported as an unresolved gap.
- [ ] 3.2 Run authorized evidence replay and overhead measurements with recorded environment and input sizes; verify reports distinguish real observations from synthetic tests and omit sensitive data.
- [ ] 3.3 Publish aggregate calibration, width, attribution, abandoned expenditure, unknown counts and baseline comparison; verify every metric has units and denominators and the conclusion follows the pre-registered rubric.
- [ ] 3.4 Record continue/pivot/not-yet-validated reasoning and next evidence in docs/pilot/findings.md; verify unsupported capabilities are not claimed as validated.

## 4. Integration and handoff

- [ ] 4.1 Run applicable repository gates and `openspec validate pilot-02-calibration-evaluation --strict --no-interactive`; verify all relevant checks pass and report unavailable tooling explicitly.
- [ ] 4.2 For behavior changes, record actual failing-before/passing-after commands, timestamps and results in TDD_EVIDENCE.md and run fresh SpecFact review; verify reviewed scope, tool/module versions and analyzer availability, resolving findings or documenting narrow exceptions. For research-only work, record evidence review without invented TDD.
- [ ] 4.3 Open a focused PR with docs, verification, limits and rollback; verify reciprocal proposal/issue links and native hierarchy/dependencies, and archive only after implementation is accepted.
