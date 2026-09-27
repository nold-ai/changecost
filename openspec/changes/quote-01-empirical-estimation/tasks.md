# Tasks

All implementation and research tasks below remain unchecked. Planning approval does not authorize product implementation or live collection.

## 1. Scope and prerequisites

- [ ] 1.1 Start the separately authorized implementation on a focused branch and read the proposal, design and capability spec; verify Git status preserves unrelated work.
- [ ] 1.2 Confirm prerequisite issues and evidence gates; verify the dependency links in [change order](../../CHANGE_ORDER.md) match GitHub before behavior work.

## 2. Estimator and comparable cohorts

- [ ] 2.1 Write failing nearest-rank, permutation, mixed-unit and minimum-count tests; verify expected failures before estimator code.
- [ ] 2.2 Implement Decimal quantiles, eligibility and fixed cohort backoff; verify exact expected p50/p90 and explicit unpriced reasons.
- [ ] 2.3 Document estimator formula, minimum-count default and cohort order in docs/quotes.md; verify examples reproduce without unstated features.

## 3. Historical replay and explanation

- [ ] 3.1 Write failing future-correction, target-exclusion and historical-cutoff tests; record actual failure evidence.
- [ ] 3.2 Persist quote evidence references and cutoff and implement explainable replay; verify future changes cannot alter a stored historical quote.
- [ ] 3.3 Document population, exclusions and limits of empirical p90; verify explain shows n, unit/basis, backoff and excluded-evidence counts.

## 4. Integration and handoff

- [ ] 4.1 Run applicable repository gates and `openspec validate quote-01-empirical-estimation --strict --no-interactive`; verify all relevant checks pass and report unavailable tooling explicitly.
- [ ] 4.2 For behavior changes, record actual failing-before/passing-after commands, timestamps and results in TDD_EVIDENCE.md and run fresh SpecFact review; verify reviewed scope, tool/module versions and analyzer availability, resolving findings or documenting narrow exceptions. For research-only work, record evidence review without invented TDD.
- [ ] 4.3 Open a focused PR with docs, verification, limits and rollback; verify reciprocal proposal/issue links and native hierarchy/dependencies, and archive only after implementation is accepted.
