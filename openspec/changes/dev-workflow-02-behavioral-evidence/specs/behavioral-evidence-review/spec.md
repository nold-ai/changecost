# Behavioral evidence review

## Purpose

Give contributors compact, current behavioral evidence and a bounded independent
lifecycle test oracle before repeated review, while preserving explicit uncertainty.

## ADDED Requirements

### Requirement: Review packets bind intent and evidence to actual inputs

The contributor tool SHALL validate a versioned packet containing intent, invariants,
trust boundaries, entrypoints, dependency-to-invariant mappings, assumptions, known
findings and evidence. Each evidence item SHALL retain its command/tool identity,
version when external, outcome, exact input binding, report reference and report
content digest. Declared binding SHALL cover the specification, oracle, generator
and configuration used; report files SHALL be checked without self-hashing the packet. Binding
SHALL include base, head and current contents of declared inputs, including absence.
Invalid, missing, changed or unbound required evidence SHALL yield incomplete/failure,
never a passing result. A packet SHALL supplement the existing review session, without
resetting its history or claiming authoritative PR completion.

#### Scenario: Reuse unchanged intent with fresh evidence

- **GIVEN** a complete packet bound to an inspected tree and declared requirements
- **WHEN** a contributor validates it against the same inputs
- **THEN** the tool reports which required evidence actually passed and retains all
  unknowns, findings and existing review-session obligations.

#### Scenario: Same-head change or omitted dependency

- **GIVEN** a previously passing packet
- **WHEN** a bound source/test/dependency changes without a commit, a declared input
  disappears, a report is missing or overwritten at the same path, or a changed path is not mapped to an invariant or explicit review scope
- **THEN** the affected evidence cannot remain passing and the result names stale
  or uncovered inputs requiring fresh review.

#### Scenario: Missing analyzer cannot become green

- **GIVEN** an external command exits successfully but its required analyzer is
  skipped, unavailable, unbound, or has no usable result
- **WHEN** its evidence is validated
- **THEN** that analyzer remains incomplete; an explicit not-applicable rationale
  is retained separately and cannot satisfy a required passing analyzer.

### Requirement: Independent bounded lifecycle oracle

The behavioral harness SHALL execute reproducible bounded synthetic operation
sequences against an independently authored reference model and the real existing
lifecycle/storage boundary. Expected outcomes SHALL come from the accepted scenarios,
not production validation/transition helpers. The harness SHALL compare acceptance,
rejection, resulting state and immutable history after every operation; rejection
SHALL preserve the pre-operation state. Reports SHALL identify seeds or concrete
sequences, checked invariants and generation limits without claiming exhaustive proof.

#### Scenario: Registration, replay and correction sequence

- **GIVEN** an empty store and synthetic Changes/Runs
- **WHEN** a sequence registers, repeats, conflicts, closes a Change and explicitly
  corrects outcomes or known interval bounds
- **THEN** the model agrees with real persistence on no-op retries, rejected new Runs
  after termination, append-only reasoned revisions and atomic combined declarations.

#### Scenario: Chronology and portable representation boundary

- **GIVEN** a captured local cutoff, two transactions at equal wall time, and a
  portable bundle imported into a later destination store
- **WHEN** historical eligibility, repeated import and invalid boundary values are tested
- **THEN** the harness detects admission after the captured sequence, backdated
  destination availability, changed retry history or partial writes on rejection.

### Requirement: Faulty and repaired controls demonstrate detection

The harness SHALL demonstrate detection with bounded deliberately faulty controls
for retry/history, transaction atomicity, chronological membership and representation
validation. Every control SHALL fail because its named invariant is violated and
SHALL pass when the fault is removed using the same input. Faults SHALL change exercised public-boundary behavior or persisted state after
reaching the real operation/SQLite boundary. The oracle, projection and trace SHALL
remain identical for faulty and repaired targets; injecting faults only into expected
results or output projection is not detection evidence. Controls SHALL remain
synthetic test fixtures and SHALL NOT weaken production validation.

#### Scenario: A detector is insensitive to its seeded fault

- **GIVEN** a control that deliberately violates one claimed invariant
- **WHEN** the behavioral test still passes or fails for an unrelated setup error
- **THEN** that control supplies no detection evidence and pilot acceptance remains
  incomplete until a relevant failure and repaired pass are observed.

### Requirement: Follow-up review uses affected assumptions without waiving gates

The review workflow SHALL provide stable intent plus the changed inputs, affected
invariants/assumptions, relevant mechanical evidence and unresolved findings to
follow-up reviewers. Missing dependency coverage, changed trust boundaries or new
scope SHALL require explicit renewed broader review. Final applicable quality,
independent review and external current-head reviewer requirements SHALL remain intact.

#### Scenario: Narrow correction inside the existing boundary

- **GIVEN** an independently reviewed packet and a correction confined to mapped inputs
- **WHEN** follow-up review starts
- **THEN** it reviews the delta and affected assumptions, reruns affected behavioral
  checks and preserves unrelated review findings/history and final mandatory gates.

#### Scenario: Boundary or unknown dependency changes

- **GIVEN** a follow-up correction with a new entrypoint, dependency or trust boundary
- **WHEN** impact cannot be justified by the existing mapping
- **THEN** the workflow requests renewed scope/architecture review instead of
  presenting the previous packet as sufficient coverage.

### Requirement: Pilot reports measured results and limitations

One dogfood pilot SHALL retain observed token categories, turn counts, correction
batches, input/assumption drifts, pre-PR discoveries, escaped findings and elapsed
minutes with provenance and observation boundaries. Cached input, uncached input
and output tokens SHALL remain separate; unavailable counters/costs SHALL remain
unknown. The report SHALL distinguish seeded control detections from genuine defects
and descriptive historical comparisons from causal efficiency or billing claims.
The existing review budget/replanning protocol SHALL remain authoritative.

#### Scenario: Incomplete telemetry or unfinished external review

- **GIVEN** missing billing rates, incomplete usage observations or pending required review
- **WHEN** the pilot report is produced
- **THEN** those fields and the pilot outcome remain explicitly unknown/incomplete,
  without fabricated zeros, savings percentages or a claimed completed review.

#### Scenario: Bounded stop and rollback

- **GIVEN** exhausted existing review allowance, a recurring investigated finding
  family or failure of a required detection control
- **WHEN** the pilot reaches its decision point
- **THEN** it records a replan/incomplete outcome and retains counters and evidence;
  rollback removes the added contributor tooling without changing stored user data.

### Requirement: Reused review baseline belongs to the selected change

An initial packet without a prior reviewed packet SHALL require broader review even
when its declared evidence is current. A supplied prior packet SHALL identify the
same change as the current packet; a foreign change SHALL yield controlled incomplete
evidence and require broader review. A valid same-change prior packet SHALL retain
the existing delta and affected-assumption behavior. Human review of prior-packet
provenance remains required; this tool does not authenticate review history.

#### Scenario: Initial current evidence has no reviewed baseline

- **GIVEN** a current complete evidence packet and no prior packet
- **WHEN** the contributor validates it
- **THEN** evidence can be current while broader review is explicitly required.

#### Scenario: Foreign prior packet cannot authorize narrow review

- **GIVEN** a structurally valid prior packet for a different change with matching maps
- **WHEN** it is supplied as the comparison baseline
- **THEN** validation is incomplete and requires broader review instead of reusing it.

#### Scenario: Matching reviewed baseline retains narrow delta review

- **GIVEN** a valid prior packet for the same change with unchanged intent and mappings
- **WHEN** only covered inputs differ
- **THEN** the tool retains the affected invariant/assumption summary and existing
  final-gate obligations without requiring broader review solely because a prior exists.

### Requirement: Bounded transitions preserve complete persisted evidence

The fixed-clock lifecycle oracle SHALL check the selected Bundle schema, source,
records and observations independently of production decision helpers. Rejected and
accepted model-no-op operations SHALL preserve the entire exported bundle, including
an absent fresh store. Accepted lifecycle appends SHALL preserve source identity and
schema, use the injected operation clock, advance beyond the previous committed
sequence, preserve every old record and observation, and produce exactly one local
observation per record with unique observation identities. All newly added local
observations SHALL share the new committed sequence and operation clock. Contiguous
sequence allocation is not required by this oracle.

#### Scenario: Accepted append mutates history or its availability boundary

- **GIVEN** a fixed-clock store with an existing change and a new accepted run
- **WHEN** a faulty operation rewrites old observation time/sequence, source identity,
  source sequence alone, or the new observations' time/sequence
- **THEN** the unchanged oracle and action trace detect the fault and the repaired
  production operation passes all complete-evidence checks.

#### Scenario: Fresh import retains origin evidence and coherent destination evidence

- **GIVEN** the selected chronology bundle imported into a fresh later-clock store
- **WHEN** the destination export is checked
- **THEN** records and all foreign observations are preserved, destination identity is
  distinct, its source time equals the injected clock, and exactly one new local
  observation per imported record uses that clock and the shared destination sequence.
- **AND** identical reimport preserves the entire destination export.

Changing clocks within a trace, concurrent writers, generalized merge imports and
observation-only imports remain outside this bounded pilot. Append-only assumptions
SHALL NOT be applied to those excluded import operations.

### Requirement: Follow-up packets preserve inspectable review context

The packet comparison SHALL expose changed advisory known-findings lists and changed
analyzer definitions with both previous and current values, requiring broader review
when they differ. Definitions SHALL be keyed by evidence ID and include command,
tool, version, required, applicable and rationale; additions/removals SHALL retain
the available descriptor and an explicit absent counterpart. These advisory strings
SHALL NOT decide authoritative finding dispositions or create another review ledger.
Execution outcome, binding and report path/digest refresh alone SHALL NOT require
broader review when the evidence remains current and definitions are unchanged.

#### Scenario: Advisory context disappears or is replaced

- **GIVEN** a same-change prior packet with known findings
- **WHEN** a follow-up removes or replaces that context
- **THEN** the result exposes both lists and requires broader review while retaining
  the existing review-session finding obligations unchanged.

#### Scenario: Evidence policy changes while current reports pass

- **GIVEN** a same-change prior packet with analyzer definitions
- **WHEN** evidence is removed, added, demoted or its command/tool/version/applicability/
  rationale changes
- **THEN** the result exposes old/new definitions for changed IDs and requires broader
  review even if remaining required evidence passes.

#### Scenario: Same policy receives fresh execution evidence

- **GIVEN** unchanged analyzer definitions and advisory findings
- **WHEN** outcomes, binding or report bytes/path are refreshed with valid current evidence
- **THEN** these execution changes alone do not require broader review, while current
  required non-passing evidence still returns incomplete.

### Requirement: Input identity covers executable mode and index state

Declared input identity SHALL bind content/absence, normalized user-execute Git mode,
and exact stage-zero index mode/blob or absence. Packet deltas and authoritative
session capture SHALL share this identity; report SHA256 remains a raw byte digest.
Unsupported or unmerged index entries SHALL be rejected. Changes require explicit
fresh capture/regeneration, without rewriting historical session events or reports.

#### Scenario: Mode or staged content changes without working byte changes

- **GIVEN** a declared input with identical working bytes
- **WHEN** its executable bit or staged mode/blob changes
- **THEN** old session evidence is stale and refreshed packet comparison identifies
  the path and its mapped assumptions/invariants, including on an already dirty base.

#### Scenario: Unsafe index type or conflict cannot become reviewed input

- **GIVEN** a staged symlink or unmerged entry, even with restored regular working bytes
- **WHEN** the input is captured or validated
- **THEN** capture rejects it instead of following or silently omitting index identity.

### Requirement: Expected payloads precede selected operation execution

The independent test model SHALL derive the complete accepted record multiset and
cardinality before invoking each selected public operation, from copied command/fixture
inputs and its own transition state. Expected semantics SHALL NOT be learned from the
operation return, observed export, production transition helpers or validators.
Deterministic test-only allocation fixtures may supply opaque IDs; their allocation
algorithm is not under test. All five selected kinds (Change, Run, RunBinding, Outcome,
Interval) SHALL compare complete canonical payloads, including full namespaced identity,
typed references, exact timestamps, optional fields, provenance and correction reasons.

#### Scenario: Extra or semantically changed record retains a lossy projection

- **GIVEN** a selected accepted lifecycle command with precomputed complete expected records
- **WHEN** actual SQLite records contain an extra record or altered identity/reference,
  timestamp precision, provenance, optional value or reason
- **THEN** exact payload multiset comparison fails and the unchanged repaired operation
  passes, without deriving expectations from the altered records.

### Requirement: Selected transitions conserve complete observation partitions

Accepted lifecycle append SHALL preserve the exact complete foreign-observation
multiset from before the operation (empty for a fresh store). Fresh selected import
SHALL produce a foreign-observation multiset exactly equal to every input observation,
with a destination identity distinct from the input observation identities. Equality
SHALL preserve every field and multiplicity, not merely subset membership. Existing
local identity uniqueness, one-observation-per-record, clock/boundary and immutable
old-local observation checks SHALL remain.

#### Scenario: Invented foreign provenance cannot pass append or fresh import

- **GIVEN** the selected real SQLite append/import transition and valid original evidence
- **WHEN** a faulty target adds a valid unique observation for an existing record under
  an unrelated third-party store identity
- **THEN** exact partition equality rejects it and the unchanged repaired transition
  passes, without extending the pilot to generalized merge imports.

The lifecycle source identity SHALL match the already established pre-call allocation
fixture even on first creation; before/after stability alone is insufficient when no
previous store exists. This does not test the opaque ID allocation algorithm.

### Requirement: Every consumed export anchors its schema and sequence scalars

Each non-absent export consumed by the bounded oracle, including before/after states
and fresh-import origin/destination, SHALL declare schema `changecost/v1`.
Source sequence SHALL have exact integer type (excluding boolean/float) and range
0 through 2**63-1. Every observation sequence SHALL have exact integer type and range
1 through 2**63-1. These independent envelope checks SHALL precede existing payload,
partition/history and relational checks, without calling production schema validators.

#### Scenario: Copied public exports retain numerically equal invalid scalar types

- **GIVEN** real public exports wrapped with a wrong schema, boolean/float source
  sequence or boolean/float observation sequence
- **WHEN** the same selected lifecycle trace consumes them
- **THEN** the oracle rejects each faulty envelope and accepts the repaired export,
  rather than treating numerical equality or historical consistency as schema proof.

### Requirement: Not-applicable evidence has consistent context and rationale

Evidence SHALL provide a nonblank rationale when applicable is false or its outcome
is not_applicable. Outcome not_applicable SHALL NOT claim applicable true. Required
analyzers SHALL still explicitly pass with applicable true; optional applicable
nonpassing outcomes remain advisory. Existing applicable false/pass evidence with a
rationale remains permitted as optional contextual evidence.

#### Scenario: Optional not-applicable outcome cannot bypass its rationale

- **GIVEN** a bound packet with passing required evidence and an optional not_applicable result
- **WHEN** applicability is true, or the rationale is missing/empty/whitespace
- **THEN** validation reports incomplete; applicable false with a nonblank rationale
  remains current, without relaxing required analyzer failures.
