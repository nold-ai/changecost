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
second completion state machine. Original packet work needed no new event ledger. The post-replan changes below extend
existing session events with explicit validated fields; old histories retain their
obligations until new explicit recovery, without rewriting historical events.

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

The original pilot ran non-capsule import/contract analysis/drift/repro and preserved
versioned outputs under ignored `.specfact/`. Post-replan, retain the supported Linux
capsule gate; use minimal import only when structural inventory is needed. Contract
analysis is annotation inventory; non-selective drift, unbound sidecar and setup-limited
repro are not routine behavioral gates and are not rerun without changed relevant facts. Read analyzer
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
  rather than adding a ledger; extend only the existing authority as specified below.
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


## Authorized post-replan design (2026-09-30)

This section refines the original pilot in place. The original report and exact-head
receipt at f6ddbe48 remain unchanged. No model/runtime expansion, new DSL, provider
parser framework, cache optimization or CI matrix reduction is authorized.

### Minimal existing interfaces

- Extend an existing approved `scope_decision` with `resolves_findings`: exact existing
  escalation finding IDs, the current full binding and a verified closure-evidence
  reference. Require genuine verified fixed dispositions and current passing closure
  evidence whose explicit finding coverage includes every resolved ID; approval or allowance extension alone cannot resolve a family. Resolve
  only named historical escalation instances. Validate binding/evidence at insertion;
  accepted historical resolution survives later head adoption. Unlisted findings and any later escape
  remain actionable. Keep events, finding identity, investigation chronology and counters.
- Extend existing reviewer evidence with explicit native-completion records: exact
  provider login, review kind `code`, fetched comment identity and its current content
  digest, full head SHA and completion timestamp. The independent reviewer adjudicates
  the fetched source once; at record time the helper captures fetched author, comment
  identity, content digest and the explicit head/time association in that evidence
  event's existing provenance. Replay validates this retained provenance without
  consulting live network or the not-yet-restored monitor; using the evidence still
  requires the current fetched source receipt to match. Retain its source kind. Prefer normal REST review records. A native summary is not converted into a
  fabricated REST review. Wrong provider/head/kind, ambiguous abbreviated SHA, absent
  source, changed content or stale security metadata cannot satisfy code-review evidence.
  The full SHA is an explicit independently verified association of the code source
  to the current PR snapshot, not a requirement that provider prose literally prints
  40 characters. A short source SHA needs an unambiguous inspected association;
  security-summary metadata cannot supply it. Existing negative reviews, requested-reviewer state, failed/missing checks, unresolved
  threads/findings and report-coverage requirements remain independent blockers.
- Exhausted correction allowance blocks further fixes/investigations, but an explicit
  `watch --observe-only` path may collect already-running checks and accept bound adjudication.
  In this explicit mode a budget-only REPLAN remains visible in status but does not
  immediately terminate observation; actionable findings, other terminal blockers and
  the absolute deadline still stop it. The default watcher keeps normal terminal stops.
  Observation grants no budget and makes no requests/retries. Exact-limit completion
  remains possible only with every current obligation satisfied; over-limit is replan.
- Existing watcher defaults to one absolute 45-minute deadline from invocation; meaningful
  progress never resets it. Keep explicit legacy inactivity limits and zero one-shot
  collection, but no implicit 30-minute stop. Bound every fetch/sleep by the absolute
  deadline. Emit meaningful changes only and stop for actionable feedback, evidence
  ready for adjudication, terminal decision or deadline. Timeout is pending, never pass
  or a fabricated failure. No automatic review request, retry or budget extension.

Use these additions to existing event payloads, rather than a new event family:

- Reviewer evidence: `covers_findings: [finding_id, ...]` for explicit closure coverage;
  `provider_completions: [{reviewer, review_kind: "code", source: "comment:<id>",
  report_sha256, head, completed_at}]` for adjudicated native completion.
- Approved scope decision: `resolves_findings`, `binding`, `closure_evidence_id`.
  The reference must name prior passing reviewer evidence with matching insertion
  binding and coverage of every named fixed escalation finding.
- Existing captured event provenance retains selected fetched source facts at recording;
  event replay validates those facts before live-monitor restoration. No network in replay.
- `watch --observe-only`: narrowly bypass budget-exhaustion early termination, never
  malformed/stale inputs, new findings or failed gates. Omitted timeout means absolute
  45 minutes; explicit positive legacy timeout means the earlier of inactivity and
  absolute 45 minutes; zero performs one existing bounded collection.

### Selected operation by representation obligations

Each row is a selected observable obligation, not a generated Cartesian suite. Reuse
existing focused fixtures. Red/green proof must distinguish the faulty outcome from
setup errors and retain positive compatibility controls. Architecture review precedes
implementation. Existing lifecycle model obligations remain regression protection;
this replan adds no lifecycle fault families.

| ID | Transition / representations | Required observation and negative control | Positive / boundary |
| --- | --- | --- | --- |
| O1 | Corrected family -> investigated escape -> approved scope resolution; event IDs and live binding | Unknown/unlisted/nonfixed finding, missing/stale closure or allowance-only approval does not clear escalation | Closure explicitly covers each named finding; validated historical resolution survives head adoption; all 10 prior batch events and chronology survive replay |
| O2 | Resolved historical family -> later genuine escape | A new finding cannot inherit an old resolution; unrelated family stays blocked | Historic fixed instances stay preserved and resolved without hiding later events |
| O3 | Pending reviewer -> native code completion; REST and comment source | Wrong author/head/kind, ambiguous short SHA, absent/edited source and stale security metadata cannot pass | Exact provider/adjudicated-full-SHA/current-digest/timestamp satisfies only that provider; retained source provenance replays offline; normal REST remains supported |
| O4 | Positive reviewer proof plus objections / changed context | Required failure/pending check, requested review, negative review, unresolved thread/local finding or changed input/report still blocks | Unchanged complete bound evidence is reusable; summary remains labeled summary |
| O5 | Final correction -> exhausted budget -> observe/adjudicate/complete | Further correction or investigation blocked; pending evidence not complete; counters cannot reset | Explicit --observe-only collects in-flight evidence despite budget-only REPLAN; no fix authority; exact-limit completion allowed, over-limit replan |
| O6 | Watch starts -> meaningful/unchanged progress -> deadline | Repeated changes never extend absolute 45-minute bound; no automatic review/retry/extension | Zero one-shot and explicitly requested shorter inactivity stop preserved; timeout pending |
| O7 | Routine versus risk review selection; YAML and workflow contract | Routine changes do not require or automatically invoke CodeRabbit; explicit risk cannot omit it | Codex always required; security/trust, persistence/data-loss, assurance/gates or contradictory evidence require both |
| O8 | Publish code head -> CI/review/ledger receipt; tracked milestone versus PR body | Old-head receipt cannot prove new head; receipt-only publication creates no source-head cycle | Exact-head complete ledger plus linked checks/reviews is authoritative live acceptance; historic f6dd remains negative |

Excluded: automatic semantic parsing of arbitrary bot prose, forged-source resistance
beyond existing trusted checkout/GitHub identities, provider availability guarantees,
new runtime/oracle semantics, exhaustive schema fuzzing and causal cost prediction.

### Finite review and evidence ownership

Local high-effort review checks this table/architecture once before implementation;
subsequent local review closes affected obligations/dependencies. One full Codex review
follows mechanical stabilization. CodeRabbit additionally applies to the O7 risk list;
this assurance-policy change requires both. No generic extra local full scan or CLI
CodeRabbit by default; explicit user requests override. Fresh required provider coverage
and mechanical gates must describe the final head; narrow review is not stale-head reuse.
Set only `.coderabbit.yaml` `reviews.auto_review.enabled` to false; existing labels and
keyword are absent. Manual `@coderabbitai full review` requests the initial required
review; `@coderabbitai review` requests later stable increments. Repository configuration
does not control external Codex app automation. Official controls and command semantics
were checked 2026-09-30 at https://docs.coderabbit.ai/configuration/auto-review and
https://docs.coderabbit.ai/guides/commands.

One correction batch is a collected finding set plus fixes/verification, not monitoring,
clean closure or one commit. First recurrence causes one bounded selected-matrix audit;
another post-investigation recurrence stops for explicit replan. For this authorized
phase, retain 10 recorded batches and grant at most 3 more (ceiling 13); retain recorded
15.67495325 partial active minutes and grant 90 additional (ceiling 105.67495325).
The existing extension event records these cumulative ceilings; history is never reset.
No further automatic allowance applies.

The PR body is the canonical published live verification index; the existing session
is scope/findings/history authority. Tracked tasks/TDD/report are immutable publication
milestones. Task 5.3 stays unchecked at publication; after actual exact-head completion,
the ledger and PR receipt record its acceptance with the SHA. Do not claim the tracked
OpenSpec checkbox count is complete or make a receipt-only source commit. A subsequent
explicit archival lifecycle may reconcile that milestone using already verified proof.

Capture post-replan telemetry at preparation completion, first stable post-replan
candidate publication, and final handoff. Preserve original cutoff separately; record
cached/uncached/output tokens, responses, actual sets versus events and elapsed units.
No billing saving is inferred. Rollback reverts the scoped contributor changes while
retaining original and post-replan evidence; existing user stores are untouched.
