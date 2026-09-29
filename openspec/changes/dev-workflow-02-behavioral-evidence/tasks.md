# Tasks

## 1. Prepare the bounded pilot

- [x] 1.1 Revalidate the isolated branch against fresh main, reviewed scenario scope and native issue prerequisites; verify exact SHA, strict OpenSpec validation and issue/project metadata readback in PREPARATION_EVIDENCE.md.
- [x] 1.2 Initialize or recover the existing review-session contract with the complete intended-file manifest and capture the pilot measurement baseline; verify status/packet retains the actual binding and no existing counters were reset.

## 2. Content-bound review packet

- [x] 2.1 Derive packet validation tests from the new scenarios; observe failures for absent behavior, stale same-head inputs, incomplete dependency coverage, replaced/missing report bytes and skipped/unbound required evidence, recording commands and outcomes in TDD_EVIDENCE.md.
- [x] 2.2 Implement the minimal JSON packet validator/impact summary reusing the existing session binding and path/digest utilities; verify those tests pass without adding a completion engine or ledger.
- [x] 2.3 Document a runnable packet example and trust/coverage limitations in the behavioral-evidence guide; execute the example and verify specification/oracle/tool inputs are bound and unknown coverage cannot look green.

## 3. Independent lifecycle evidence

- [x] 3.1 Author the reference model from accepted lifecycle scenarios and a public-API adapter using real temporary SQLite; independently review that expected transitions do not import production decision helpers and record the bounded sequence/seed inventory.
- [x] 3.2 Run the same targeted traces against four faulty/repaired controls for retry/history, atomicity, chronology and one representation boundary; keep oracle/projection/trace unchanged, ensure faults reach real operation/SQLite state, and record relevant failing assertions then repaired passes, and verify generated sequences agree with existing real behavior after every operation.
- [x] 3.3 Document selected invariants, excluded contracts, reproduction commands and actual coverage in the guide/TDD evidence; run the applicable SpecFact non-capsule inventory/contract/drift/repro paths and record exact versions, binding, per-analyzer outcomes and limitations separately from domain-test evidence.

## 4. Dogfood review and documentation

- [x] 4.1 Update the four workflow skills and shared review guidance to pass stable intent plus delta/affected assumptions to follow-up reviewers; verify broader review triggers on unknown dependency/scope/boundary changes and final current-head gates remain mandatory.
- [x] 4.2 Update ownership/source mappings, curated index, generated llms.txt and Unreleased changelog; verify real missing/stale/repaired documentation/index controls and local/CI invocation parity using existing gate tests, without a version bump.
- [x] 4.3 Dogfood independent review and corrections with the packet and existing counters; publish an empirical pilot report with token categories, turns, batches, drift, pre-PR findings, escapes, minutes and unknown costs, distinguishing seeded detections from actual defects and historical context from causal claims.

- [x] 4.4 Correct independently confirmed native baseline-provenance gaps and Linux test-tooling blockers with red/green regressions, retaining exact prior identity and the independent oracle; record later results separately from fixed telemetry.

## 5. Final integration and handoff

- [ ] 5.1 Run strict OpenSpec validation and complete make check with explicit BASE_REF and intended-file manifest, plus the final staged-snapshot checks; obtain actual supported-Linux capsule evidence and resolve/justify findings without treating unavailable analyzers as passing.
- [ ] 5.2 Obtain fresh independent review-agent and CodeRabbit/current-head external review evidence, iterate within the retained review allowance, and create/update the focused PR after coordinator verification; read back issue links/metadata and report actual outcome, limitations and rollback without merging or deploying.
