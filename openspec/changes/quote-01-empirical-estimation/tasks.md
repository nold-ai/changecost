# Tasks

Preparation reconciled and runtime implementation explicitly authorized on 2026-10-03
(Europe/Berlin). Scoped runtime/docs tests are passing in this checkout; full verification,
publication and exact-head acceptance remain pending. Provider collection and archival
are outside this request.

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

- [ ] 5.1 Record actual failing-before/passing-after commands, timestamps, scope and outcomes in TDD_EVIDENCE.md; run strict selected OpenSpec validation, explicit-base make check and applicable staged-snapshot checks. Retain native supported-Linux capsule/Python matrix evidence; missing analyzers remain incomplete.
- [ ] 5.2 After mechanical stabilization, close selected independent obligations and require exact-head Codex plus CodeRabbit review for persistence/import trust. Reuse already-running required reviews, preserve bounded history and verify actual provider/check evidence; do not add a generic full local/CLI scan by default or precheck live acceptance.
- [ ] 5.3 Hand off to separately requested verification/promotion with current docs, PR/ledger acceptance evidence, actual issue sync and retained stash OID. Commit/push/PR tasks remain pending until requested and completed; archive only after explicit implementation acceptance using the OpenSpec CLI.
