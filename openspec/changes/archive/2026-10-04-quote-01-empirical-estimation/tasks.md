# Tasks

Preparation reconciled and runtime implementation explicitly authorized on 2026-10-03
(Europe/Berlin). Implementation and exact-head verification completed in merged
PR #32 on 2026-10-03. The maintainer requested native CLI archival on 2026-10-04;
this closeout reconciles publication checkpoints against the accepted PR evidence.
Provider collection remains separate.

## 1. Fresh scope and obligation review

- [x] 1.1 On separate implementation authorization, refresh main, inspect issue #15 and dependency #12, recover the matching preparation receipt/stash and preserve unrelated work; verify semantic readiness against current main specs/code before applying the immutable OID.
- [x] 1.2 Recover the existing bounded session without resetting counters; explicitly record the authorized runtime path/hash scope and advance its binding. Obtain one independent high-effort review of operation × representation obligations, including cutoff/coverage, Quote metadata, import/backup and operation-kind boundaries; retain selected mappings and reviewed fingerprints.

## 2. Snapshot-derived comparable observations

- [x] 2.1 Write spec-derived failing tests for complete versus partial/unsupported/forged peers, late gaps, terminal outcomes, abandoned/retry totals, observed zero and economic identity separation; record genuine missing-behavior failures before implementation.
- [x] 2.2 Reuse committed snapshot pruning and pure reconciliation selection/coverage to derive one aggregate per peer at Quote cutoff without writing settlement revisions; verify the preceding scenarios pass, including current synthetic-only eligibility and no reliance on saved completeness flags.
- [x] 2.3 Update docs/quotes.md and docs/contracts.md with current source policy, population and exclusion semantics; verify examples use supported synthetic evidence and distinguish imported claims from computed completeness.

## 3. Deterministic estimation and feature backoff

- [x] 3.1 Write failing exact nearest-rank, permutation, signed/zero amount, positive minimum, feature normalization/timing/version, three-level backoff and target-exclusion tests; verify missing estimator behavior causes each failure.
- [x] 3.2 Implement integer-rank Decimal selection, strict recorded minimum (default 20), immutable supported pre-run feature matching and reasoned fallback; verify 1–20 USD yields p50=10 and p90=18, no identity mixing and explicit null unpriced quantiles.
- [x] 3.3 Document formula, parameter/default limits, feature capture rules and ordered cohort counts/reasons in docs/quotes.md; verify examples reproduce and make no calibration or p90 budget guarantee.

## 4. Atomic Quote persistence, replay and CLI

- [x] 4.1 Write failing metadata/legacy round-trip, response-loss retry, cross-kind operation-ID collision, safe atomic rollback, forged authority, privacy, backdated imports, sequence cutoff, late correction and foreign/future/unsupported replay tests; record actual failures before the corresponding implementation.
- [x] 4.2 Extend the existing Quote with optional versioned metadata required for locally computed Quotes; implement quote's one-transaction snapshot/write/receipt through existing layout 2 and operation namespace, and one-read-snapshot explain/replay. Verify exact peer/support/exclusion provenance, immutable historical results and every preceding failure boundary without creating settlement revisions.
- [x] 4.3 Update installed CLI integration tests, docs/cli.md, docs/contracts.md, docs/quotes.md, Unreleased changelog, ownership/index and generated references; verify actual offline command examples, older Quote imports and consistent backup recovery. Keep package 0.1.0.dev0 and check local/CI documentation freshness.

## 5. Verification and later delivery

- [x] 5.1 Record actual failing-before/passing-after commands, timestamps, scope and outcomes in TDD_EVIDENCE.md; run strict selected OpenSpec validation, explicit-base make check and applicable staged-snapshot checks. Retain native supported-Linux capsule/Python matrix evidence; missing analyzers remain incomplete.
- [x] 5.2 After mechanical stabilization, close selected independent obligations and require exact-head Codex plus CodeRabbit review for persistence/import trust. Reuse already-running required reviews, preserve bounded history and verify actual provider/check evidence; do not add a generic full local/CLI scan by default or precheck live acceptance.
- [x] 5.3 Hand off to separately requested verification/promotion with current docs, PR/ledger acceptance evidence, actual issue sync and retained stash OID. Commit/push/PR tasks remain pending until requested and completed; archive only after explicit implementation acceptance using the OpenSpec CLI.

## Accepted implementation closeout — 2026-10-04 (Europe/Berlin)

[PR #32](https://github.com/nold-ai/changecost/pull/32) merged on 2026-10-03
at 17:58:36 Europe/Berlin, merge commit
`5f43c32d09e6d1b167c352ad16cabea555d84ec2`, accepted feature head
`b83c2dc2fd4ae292bcdf1b532858d6bac8360d40`. GitHub readback on 2026-10-04
confirmed MERGED, both quality matrix checks successful and CodeRabbit successful.
Issue #15 is Closed/Done; prerequisite #12 is closed.

The accepted PR verification index records 1,147 tests, two installed-wheel
offline CLI proofs, 11 strict OpenSpec validations, configured staged checks,
independent defect/documentation closure, exact-head Codex/CodeRabbit completion
and all six review threads resolved with retained dispositions.
[Native run 37129770275](https://github.com/nold-ai/changecost/actions/runs/37129770275)
passed Python 3.11.15 and 3.13.14 with all ten analyzers and full assurance.
These are accepted feature results, not checks of this new archive/planning diff.
Earlier red/green failures, native failures, prior-head results and accepted
advisories remain preserved in TDD_EVIDENCE.md and the final PR index.

The earlier local archive draft in another worktree remains intact and unpublished;
its historical receipt records completed bounded history without reset. This
worktree performs its own native archive against fresh main
`340668e6b74bfb7ccab15efe13830555bc6dd7ef` (including merged PR #33).
The prior preparation stash `be9e9d6613b03e83dd05de0033abb2b34ce04a89` is a
historical recovery pointer, not asserted to exist in this worktree.
Calibration, prediction accuracy and provider approvals remain To-Validate.
