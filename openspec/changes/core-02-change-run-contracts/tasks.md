# Tasks

Prepared on 2026-09-29 against fresh main and the archived foundation/review specs.
Implementation and pre-promotion verification are complete at `fae72f330b2e8187521f2ed176b7bc0118f3575f`.
[PR #25](https://github.com/nold-ai/changecost/pull/25) is open for current-head review
and acceptance. Preparation probes are not product TDD. See
[preparation evidence](PREPARATION_EVIDENCE.md) and [implementation evidence](TDD_EVIDENCE.md).

## 1. Scope and prerequisite recovery

- [x] 1.1 Refresh main, reconcile this preparation/receipt by change identity, and start a focused implementation branch; verify #10 remains delivered, native dependencies and current specs still match, and unrelated work is preserved.
- [x] 1.2 Recover the bounded review contract without resetting history; bind the intended implementation paths, requirements, exact reviewer identities and current bases through an explicit scope/head transition, then verify status before edits. Run the supported-Linux preflight early when a feature branch is available; preserve macOS limitations.

## 2. Contracts and strict serialization

- [x] 2.1 Map every capability scenario to intended tests, then record genuine failing tests for exact decimals/scale/nulls, kind/unit/basis/currency, full identities, aware UTC timestamps, feature domains, duplicate JSON members, unknown fields/kinds/versions, privacy diagnostics and nonfinite/coercible values.
- [x] 2.2 Add Pydantic v2 as a declared locked runtime dependency and implement the smallest allowlisted records and bundle codec; verify section 2.1 tests pass on Python 3.11.15 and 3.13.14, and run locked dependency/license/advisory checks without SpecFact at runtime.
- [x] 2.3 Document the concrete v1 record/bundle fields, revision references, units, version policy and synthetic examples in docs/contracts.md; validate every example and register its documentation ownership/index entries.

## 3. Persistence, history and explicit binding

- [x] 3.1 Derive failing tests for fresh-store registration, identical replay after response loss/termination, conflicting identities, full RunRef collisions, both bindings, cross-repository rejection, immutable features, outcomes and work-interval correction atomicity; record actual failing commands before implementation.
- [x] 3.2 Implement SQLite version-1 initialization, explicit transactions, per-connection foreign keys, exact TEXT amounts, registration/bindings and append-only lifecycle revisions; verify section 3.1 tests pass and document the storage/lifecycle paths alongside their behavior.
- [x] 3.3 Add arbitrary-order bundle/reference, missing/cyclic/wrong-subject revision, destination availability, snapshot cutoff, delayed commit, clock regression, competing-writer, failed commit/migration, newer-schema and backup-versus-import tests; distinguish retryable busy from attribution conflict. Record genuine red/green cases separately from regressions that passed on first introduction.
- [x] 3.4 Implement atomic portable persistence and historical-eligibility primitives with destination-local availability and committed snapshot boundaries; verify section 3.3 tests including restart/response-loss retry pass. Document precise cutoff/clock limits and backup recovery without promising physical commit timestamps or implementing quote/reconciliation algorithms.

## 4. Offline command integration

- [x] 4.1 Record failing tests for bind registration/mapping/import modes, lifecycle-only settle, record inspection/export through explain, mutually exclusive modes, incomplete selectors, missing read-only stores, existing export files and interrupted export. Retain read-only help/version/bare/error and unimplemented quote/check tests.
- [x] 4.2 Implement only the planned core command surface; verify section 4.1 tests and an installed-wheel/sdist round trip outside the checkout with network blocked and no SpecFact. Replace the foundation test that settle is absent from help only when the operation is delivered; keep private-artifact exclusion proof.
- [x] 4.3 Create docs/cli.md and update README, docs/contracts.md, ownership metadata, CHANGELOG and generated llms/command references to reflect only implemented operations; execute the synthetic examples and verify deterministic regeneration and read-only validation.

## 5. Verification and handoff

- [x] 5.1 Run selected strict OpenSpec validation and make check with an explicit fresh comparison base and intended-file manifest; obtain actual supported-Linux full analyzer assurance, scoped independent reviews and all required checks without treating local missing analyzers as passing.
- [x] 5.2 Reconcile every scenario with actual TDD_EVIDENCE.md commands/results, verify scope/non-goals, docs/index/package versions and issue links/relationships, and record unresolved evidence honestly. Do not mark provider support, reconciliation or estimation delivered.
- [x] 5.3 Verify the final staged snapshot, commit/push through the verification stage, and open the focused implementation PR when requested; retain rollback/backup guidance and archive only after implementation acceptance.

Promotion checkpoint, 2026-09-29 (Europe/Berlin): GitHub run 36558317437 and both
native reports certify the cited implementation commit. The reviewed branch was
committed/pushed and ready PR #25 opened against main; fresh PR-head checks and
Codex/CodeRabbit review remain pending. Core-02 is intentionally not archived until
implementation acceptance. No merge, issue closure or release is claimed.
