# Design

## Context

See [proposal](proposal.md) for motivation and [the delta](specs/behavioral-evidence-review/spec.md)
for acceptance. Base `999cb8f960785fe4ac0434d41a0892beca933191` includes public
`register_change`, `register_run`, `declare`, `Store.import_bundle`, `Store.snapshot`
and `Store.eligible`. `Store.apply` validates the whole candidate graph inside one
SQLite transaction; availability includes local sequence and time. Existing tests
cover individual cases, but do not provide an independent bounded state model.

`quality.review_session` already owns schema-8 scope, input epochs, findings,
correction/time allowances and PR monitoring. `quality.repository` supplies safe
path and content-digest utilities. The quality runner invokes the complete pytest
suite locally and in hosted CI; contributor helpers are excluded from distributions.

## Goals / Non-Goals

**Goals:** add a small evidence interface and test oracle that a reviewer can inspect
once and reuse, prove useful detector sensitivity, then measure one actual delivery.

**Non-Goals:** model all portable record kinds/economic graphs, infer a universal call
graph, modify SpecFact, create another review engine or replace final mandatory gates.
The independent model targets existing Change/Run lifecycle only. Runtime edits need
an observed defect and explicit scoped spec/test reconciliation before implementation.

## Decisions

### Keep one authority for review state

Add `quality/behavioral_evidence.py` as a small JSON packet validator/summary command.
It validates an explicit packet and current declared file fingerprints; it does not
execute arbitrary commands from the packet, poll services, reset sessions or decide
PR completion. Reuse existing safe-path/digest helpers where their contracts fit.
The packet reuses the existing `review_session.packet` binding verbatim: `head`,
`input_digest`, `epoch`, `comparison_base` and `pr_base`. It binds specification,
oracle and relevant tool/report contents as well as runtime inputs. There is no
second completion state machine. No migration of old
receipts is needed and no new event ledger is introduced.

The packet has a schema version, intent, invariant IDs and statements, trust boundary,
entrypoints, dependency/assumption mappings, known findings and evidence records.
Inputs use normalized repository-relative paths and SHA256 or explicit absence.
Evidence records include command/tool/version, required/applicable classification,
actual outcome, report path/content digest and captured binding. Recheck report bytes
and the specification/oracle/generator/configuration contents; missing or replaced
reports invalidate evidence, including ignored `.specfact/` files. Exclude the packet
itself from content binding to avoid self-hashing cycles. Required analyzer results must
explicitly pass; unknown/skipped/unavailable/stale results stay incomplete. Claims
about semantic coverage remain human review responsibilities. An exit code alone
is not an analyzer result. JSON is preferable to a new database or framework.

The impact summary compares a previous reviewed packet to the current inputs and
maps changed paths to affected invariants/assumptions. Every changed input must be
covered or trigger broader review. Explicitly mapped documentation/planning changes
may require review without a runtime invariant. Unchanged-path status alone cannot
prove unaffected semantics; incomplete dependency mapping is explicitly unknown.
Unknown/new dependency, entrypoint
or trust-boundary changes force renewed architecture review. Final check evidence
must bind the final tree even when interim LLM review is limited to a delta.

### Use a small independently authored model against real SQLite

Place a pure-Python reference model in `tests/behavioral_model.py` and sequence tests
in `tests/test_lifecycle_stateful.py`. Derive transition rules from Core-02 scenarios
before reading production transition internals for implementation. Do not call
`latest`, `validate_graph`, `revision_errors` or other production decision helpers
from the oracle. A thin adapter may construct public input records, call operations
and project public outputs into comparable facts; UUID generation/serialization
ordering is not expected behavior.

Keep a few explicit adversarial sequences and deterministic seeded sequences (for
example 8 seeds, at most 24 operations each). Report the actual chosen bounds and
seeds. Cover registration/replay/conflict, terminal new-Run rejection with existing
Run retry, reasoned outcome/interval revisions, combined-operation atomicity,
equal-time sequence cutoffs, later destination import/reimport, and one integer
representation boundary. The four sensitivity controls are the selected invariant
families, not a promise to mutate every existing contract. Excluded: all economic
record semantics, complete graph validation, concurrent-writer schedules, filesystem
failure permutations and exhaustive Unicode/date/decimal domains. Avoid a massive exhaustive suite; pytest and standard
library suffice, so no new dependency is needed. Existing focused unit tests remain.

Use real temporary SQLite databases and public operations for positive evidence.
Seed targeted public-boundary faults or test-only persisted-state mutations for four named families:
retry/history mutation, partial combined update, cutoff sequence omission and invalid
representation admission. The same expected model/sequence must reject the fault
and accept the repaired real behavior with unchanged oracle, projection and trace.
Each fault must reach the real operation/SQLite boundary; altering only expected
values or the adapter output projection is prohibited. A fixture failing during setup is not proof.
Keep injected faults out of shipped code and record exact detector assertions.

### Reuse SpecFact only for demonstrated capabilities

On 2026-09-29 (Europe/Berlin), CLI 0.55.4 with codebase 0.41.16/project 0.41.27
was inspected alongside current generated command references:
[core llms.txt](https://github.com/nold-ai/specfact-cli/blob/main/llms.txt) and
[modules llms.txt](https://github.com/nold-ai/specfact-cli-modules/blob/main/llms.txt).
The inspected modules main commit was `b3ca3014c8d0e064b860856d4b560a2591999532`.
Installed `code import`, contract analysis and drift/repro commands provide useful
inventory/mapping evidence, but they do not establish domain behavior automatically.
A local generator probe found no extractor/harness from the empty pure-Python
contract; an OpenAPI contract produced adapter dispatch rather than domain imports.
Saved probe evidence is described in preparation evidence, not bundled transcripts.

Run applicable non-capsule import/contract analysis/drift/repro on the actual pilot
inputs and preserve versioned outputs under ignored `.specfact/`. Read analyzer
execution/coverage individually. Sidecar results or Semgrep/Bandit coverage must not
be inferred from a top-level success. Independent lifecycle checks supply the domain
binding absent from the generator. The existing supported-Linux SpecFact capsule gate
remains a separate required assurance path; unsupported macOS is not a pass.

### Bound adoption and measure actual work

Prepare/implement/verify/promote guidance should request the packet at first review
and delta plus affected assumptions later, with one writer and stable-tree readers.
Dogfood it on this change. Preserve schema-8 counters; inspect status before each
correction batch and publication. Default stop criteria remain three correction
batches or 90 active minutes, recurrence after investigation, unresolved scope or
missing required evidence. Extensions require the existing explicit maintainer record.
A failed sensitivity control blocks the claimed behavioral assurance.

Record phase boundaries, model/context, tokens (cached input, uncached input, output),
turn counts, correction batches, input/assumption drift, genuine pre-PR findings,
escapes and minutes. Measurements may be snapshots of available local session metadata;
retain provenance/coverage and avoid double counting parent/worker histories. Missing
monetary prices or observations stay null/unknown. Existing foundation/bounded/Core-02
retrospectives are descriptive context only; no copied uncommitted report is required.
Acceptance is functioning current evidence, meaningful controls and an honest measured
outcome, not a predetermined savings claim. A single pilot cannot identify causality.

## Risks / Trade-offs

- Model repeats production assumptions → derive it from scenarios, independent review
  and fault controls; record model omissions explicitly.
- Packet becomes a second platform → one file schema and validator; reuse the session
  rather than changing its ledger or reviewer chronology.
- Narrow review misses dependency effects → complete declared mapping, broader review
  on unknown changes, and mandatory current-head final gates.
- Analyzer provides a false green → require per-analyzer executed outcome and binding;
  retain unsupported/unknown evidence and the separate capsule requirement.

## Migration Plan

Add isolated contributor tooling and tests first with observed red/green controls;
update docs/skills, mappings, generated index and Unreleased changelog. Run selected
strict OpenSpec validation, full `make check` with explicit base/manifest, independent
review, CodeRabbit and hosted Linux assurance. Publish only after the coordinator's
verified handoff; no merge/deployment is part of this plan. Roll back by reverting the
new contributor files/docs while retaining ignored experiment/session evidence.

## Open Questions

Actual detection yield, available complete token observations and billing effect are
empirical outputs of the pilot. They do not change implementation scope or acceptance.
