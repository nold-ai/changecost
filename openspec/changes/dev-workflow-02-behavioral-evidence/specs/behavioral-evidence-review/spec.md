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
