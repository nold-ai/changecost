# Tasks

## 1. Review-session contract

- [x] 1.1 Add the OpenSpec contract and workflow receipt format; verify strict OpenSpec validation accepts the artifacts.
- [x] 1.2 Add failing tests for valid, missing, malformed and conflicting review session state; verify they fail before the helper exists.
- [x] 1.3 Implement initialization, idempotent records, atomic state updates and deterministic status decisions; verify the new tests pass.

## 2. Finding and monitor decisions

- [x] 2.1 Add failing tests for budget limits, extensions, family escalation and stale dispositions; verify status decisions match the scenarios.
- [x] 2.2 Implement packet generation and the read-only paginated watcher with changed-state suppression; verify synthetic multi-page REST sources, GraphQL review threads/comments and API-error tests pass.
- [x] 2.3 Document calibration inputs and advisory adoption thresholds; verify no unavailable reviewer is reported as validated.

## 3. Workflow and documentation

- [x] 3.1 Update implementation, verification and promotion skills with shared session checkpoints and preflight rules; verify their documented commands match the helper.
- [x] 3.2 Add the lessons document, ownership mapping, generated references and Unreleased changelog entry; verify documentation checks and `make generate` outputs pass.

## 4. Verification

- [x] 4.1 Run focused tests, strict OpenSpec validation and relevant quality gates; record actual commands and results in TDD_EVIDENCE.md.
- [ ] 4.2 Run the supported-Linux review preflight when a feature branch is available, then record its actual head and outcome without claiming unsupported local capsule evidence.
- [ ] 4.3 Calibrate the local cross-family candidate on three concealed historical defects and repaired controls; record measured outcomes or the access/time limitation.
