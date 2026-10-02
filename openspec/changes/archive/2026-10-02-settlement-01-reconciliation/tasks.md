# Tasks

Prepared against merged main `999cb8f960785fe4ac0434d41a0892beca933191` on
2026-09-29. These are **implementation tasks**; checks below record observed progress. Preparation probes
and archived Core-02 checks are not evidence that reconciliation is implemented.
The maintainer confirmed unreleased 0.x development; the [design](design.md)
evolves the current internal artifact schema without a public v2 or migration programme.
Implementation was authorized on 2026-09-29. Live collection remains outside scope.

## 1. Scope, developing contracts and recovery

- [x] 1.1 Refresh main, recover this prepared change and bounded review receipt by stable identity, and verify Core-02 delivery and native dependencies; preserve unrelated work and record current base/head/scope without resetting prior counters.
- [x] 1.2 Read the prepared portable delta before behavior code; derive exact replay of existing/new known records, unknown-field/version rejection, copied-model/privacy and incompatible-store non-mutation tests, observe expected failures, and record exact commands in TDD_EVIDENCE.md.
- [x] 1.3 Extend the existing internal schema with the minimum typed economic/coverage/computed-settlement records; verify section 1.2 tests on both required Python versions and update docs/contracts.md with exact fields, unreleased status, tested checkout, limits and trust boundary.

## 2. Normalized import and semantic identity

- [x] 2.1 Derive failing normalized-batch tests for duplicate versus distinct retry, changing transport metadata, source-namespace collisions, per-event component identity, file/row replay and ambiguous cross-file overlap; retain existing strict portable replay tests.
- [x] 2.2 Implement allowlisted normalized input and semantic deduplication before immutable core insertion; verify full-batch atomicity, stable bind selectors, first availability, unknown fields/coercions and sanitized diagnostics without relaxing core identity/reference checks.
- [x] 2.3 Add failing and passing installed-CLI tests for `settle --import-evidence` with explicit repository selection, bounded input and offline synthetic fixtures; document normalized input and dedupe limits in docs/settlement.md and docs/cli.md.

## 3. Replacement corrections and temporal lanes

- [x] 3.1 Derive failing scenarios for replacement replay, pending target arrival, reversal-zero, cycles/forks, incompatible target/economic identity, mixed lanes, reset/baseline gaps and partial-window attribution; distinguish tests failing for missing behavior from broken tooling.
- [x] 3.2 Implement typed pending source locators and validated replacement chains with atomic resolution; verify original and later cutoff views, source history retention and no dangling core references or repeated adjustment.
- [x] 3.3 Implement the closed supported-lane policy and explicit unresolved partitions; verify no snapshot-plus-delta sum, no inferred snapshot subtraction/proration, supported synthetic exact-window totals and unsupported real-profile diagnostics. Document traces and limits beside the implemented behavior.

## 4. Exact components and immutable computation

- [x] 4.1 Derive failing tests for low ambient Decimal precision, input-order invariance, cancellation, scale, null/zero separation, unknown currency, signed values and record/aligned-digit limit edges; implement exact checked aggregation and verify no float/SQL numeric path or silent truncation.
- [x] 4.2 Derive failing tests for one committed input snapshot, captured local cutoff, sequence exhaustion, competing writers, failure before commit and response loss; implement atomic local computed revisions and operation-ID receipts, verifying original retries versus new-cutoff recomputation.
- [x] 4.3 Verify local computed chains remain distinct from imported producer claim chains, arbitrary-order portable replay stays atomic, foreign history yields replay_unavailable and a consistent backup retains local history. Document computation fields, provenance and recovery.

## 5. Coverage and repository remainder

- [x] 5.1 Derive failing coverage tests for omitted/open Runs, zero-run Changes, absent/zero evidence, missing/contradicted work bounds, source-window endpoints, unknown source applicability, relevant unbound evidence and late bindings/outcome/interval/correction changes.
- [x] 5.2 Implement explicit Change/Run membership, outcome/interval/binding revisions, expected source components and policy-bound coverage; verify one positive synthetic fixture and every negative scenario without trusting imported verified/reconciled labels or relabeling synthetic evidence as real observations.
- [x] 5.3 Implement scoped known/unknown subtotals and read-only bound/unbound/unresolved repository reporting; verify accepted/abandoned retries are retained, resolved events occur in only one bucket and no artificial Change or cross-identity grand total is created. Update docs/settlement.md examples.

## 6. Offline CLI, documentation and acceptance

- [x] 6.1 Derive failing compute/explain CLI tests for explicit economic/Change/operation selectors, mixed-mode errors, missing stores and privacy-safe failures; implement the minimal command integration and verify lifecycle/help/read-only behavior stays intact while quote/check/provider parsers remain undelivered.
- [x] 6.2 Execute documented synthetic import-bind-compute-explain and portable round trips from installed wheel/sdist outside the checkout with network blocked and no SpecFact runtime; verify package/private-artifact exclusion and update README, contracts/CLI/settlement docs, ownership metadata, changelog and generated references.
- [x] 6.3 Run strict selected/all OpenSpec validation, make check with explicit fresh comparison base and intended-file manifest, both required Python suites, independent scoped reviews and fresh supported-Linux native analyzer assurance. Record actual failures/fixes/accepted limits without claiming missing analyzers passed.
- [x] 6.4 Verify final staged/default-HEAD and aggregate checks, align issue acceptance/status and native hierarchy/dependencies with actual delivery, then commit/push/promote only when requested. Preserve rollback/backup guidance and archive through the full OpenSpec CLI only after implementation acceptance.


Implementation acceptance: 19/19 tasks complete, reconciled on 2026-10-02
(Europe/Berlin). The earlier 17/19 handoff was a frozen pre-publication milestone.
[Merged PR #28](https://github.com/nold-ai/changecost/pull/28) records final local
quality, both Python suites, staged/default-HEAD and aggregate checks, supported-Linux
native assurance and both provider review completions at head
`beedfd16f3af233e2f7ceb8dbcecf5baa2bd7bf1`. Its merge commit is
`1f55b767066d9834765f92a427b5eb9dc653a315`.
Fresh GitHub readback confirms #12 CLOSED/Done, native User Story, parent #7 and
prerequisite #11; the labels and hierarchy are retained. The maintainer explicitly
accepted settlement closeout and requested normal CLI spec synchronization and
archival on 2026-10-02. This reconciles completed work without rerunning or
relabeling historical failures. See [actual evidence](TDD_EVIDENCE.md) for the final
acceptance sources and retained limits. Provider adapters and live collection are
not delivered by this change.
