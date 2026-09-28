# Tasks

Research and fixture work was authorized on 2026-09-28, then extended to Codex and
Claude Code with explicit local-artifact inspection authorization. No live
collection or runtime adapter work is included. See [research evidence](RESEARCH_EVIDENCE.md).

## 1. Scope and prerequisites

- [x] 1.1 Start the separately authorized implementation on a focused branch and read the proposal, design and capability spec; verify Git status preserves unrelated work.
- [x] 1.2 Confirm prerequisite issues and evidence gates; verify the dependency links in [change order](../../CHANGE_ORDER.md) match GitHub before behavior work.

## 2. Evidence inventory

- [ ] 2.1 Record per-surface source/version/tier and exact access steps; verify every matrix row has a citation or observed-evidence reference.
- [ ] 2.2 Inspect authorized sanitized headers and representative events, including missing fields and repeated billing attributes; verify the matrix distinguishes supported, partial, unavailable and unverified.
- [x] 2.3 Document the evidence gate and exclusions in docs/providers/source-feasibility.md; verify each planned adapter capability has an explicit disposition.

## 3. Fixture contract

- [x] 3.1 Define allowlisted fields and deterministic ID replacement for each feasible source; verify a redaction review finds no prompts, secrets or actual account identifiers.
- [x] 3.2 Provide synthetic edge cases for missing IDs/costs, duplicates and corrections plus provenance notes; verify they preserve required joins without claiming they are live pilot observations.
- [x] 3.3 Record unresolved evidence requests and downstream blocking decisions; verify unavailable capabilities do not appear as supported in adapter docs.

## 4. Integration and handoff

- [x] 4.1 Run applicable repository gates and `openspec validate pilot-01-source-feasibility --strict --no-interactive`; verify all relevant checks pass and report unavailable tooling explicitly.
- [x] 4.2 For behavior changes, record actual failing-before/passing-after commands, timestamps and results in TDD_EVIDENCE.md and run fresh SpecFact review; verify reviewed scope, tool/module versions and analyzer availability, resolving findings or documenting narrow exceptions. For research-only work, record evidence review without invented TDD.
- [ ] 4.3 Open a focused PR with docs, verification, limits and rollback; verify reciprocal proposal/issue links and native hierarchy/dependencies, and archive only after implementation is accepted.

## Remaining evidence

Tasks 2.1 and 2.2 are partially complete: documented acquisition routes, installed
Codex/Claude CLI metadata and selected local artifact shapes are recorded. Exact
Copilot OTel acquisition/exports and other harnesses remain unverified. The inspected
hosted session uses Personal Free, confirmed by the maintainer.
The authorized VS Code hosted Copilot session supplies an explicit host/SDK link,
turn token fields and a durable nano-AIU checkpoint; differing session totals and
coverage/finality still require evidence. Cursor 3.22.7 Basic (maintainer-reported) now supplies
local identity/context evidence; its usage CSV and consumption semantics remain
unverified. Empty/zero usage fields are not proof of zero consumption or cost.
Codex/Claude usage finality, billing basis and complete
coverage also remain unverified. No source profile is approved for adapter import.
Enterprise artifact comparison is complete for the supplied projections; native
log-to-hook mappings, upload payloads, SDK usage, unwrapped events and cross-source identities remain
unverified. Work OTel is reported globally disabled, so OTel acquisition is not a
prerequisite for that custom-source assessment; CSV remains uninspected.
V2 adds producer-reported message-counter paths and positive synthetic examples;
18 authored research cases cover the current boundaries. Received artifact integrity
passes, with duplicate JSON members and an OTLP string-enum mismatch recorded as
fixture-admission findings. No native parser or hook mapping is verified. These
limits do not complete tasks 2.1/2.2.
Verification and PR promotion are now separately authorized. Task 4.3 remains
pending through review/acceptance; tasks 2.1/2.2 and archival remain incomplete.
