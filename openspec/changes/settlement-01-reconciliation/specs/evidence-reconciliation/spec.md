# Reconcile evidence into revisioned settlements

## Purpose

Retries and duplicate exports can inflate spend while missing charges can hide it. Reconciliation must preserve unknowns and corrections before provider-specific data enters the model.

## ADDED Requirements

### Requirement: Idempotent evidence and real retries

The reconciler SHALL ignore exact duplicate evidence while retaining distinct retry events.

#### Scenario: Duplicate versus retry

- **GIVEN** two copies of event A at USD 0.10 and distinct retry B at USD 0.20
- **WHEN** settlement runs
- **THEN** known billed USD is 0.30 with A counted once and B retained.

#### Scenario: Conflicting duplicate

- **GIVEN** one stable event key with two different amounts and no correction link
- **WHEN** the second record is imported
- **THEN** it is rejected as a conflict without silently choosing an amount.

### Requirement: Revisioned corrections

The reconciler SHALL retain prior settlement revisions and apply identifiable corrections exactly once.

#### Scenario: Corrected charge

- **GIVEN** a USD 0.40 billed event and a documented replacement USD 0.25 correction
- **WHEN** the correction is imported twice
- **THEN** the new amount is 0.25, not 0.65 or 0.10, and the previous revision remains inspectable.

#### Scenario: Correction arrives first

- **GIVEN** a correction targeting absent evidence
- **WHEN** settlement runs
- **THEN** it stays pending and completeness reports the unresolved target.

### Requirement: Honest economic completeness

Settlements SHALL separate incompatible units and unknown amounts and SHALL NOT add cumulative snapshots to event deltas.

#### Scenario: Mixed evidence

- **GIVEN** USD billed 1.00, 2 credits and an unknown charge
- **WHEN** settlement runs
- **THEN** separate USD and credit components appear, unknown count is one, and no grand money total is fabricated.

#### Scenario: Snapshot and deltas

- **GIVEN** a cumulative series and its underlying events
- **WHEN** the source has no verified precedence rule
- **THEN** the result is incomplete and the two lanes are not summed.

### Requirement: Auditable full-change coverage

Settlements SHALL distinguish reconciled source intervals from full-change coverage.
Full-change eligibility SHALL require a terminal Change with at least one Run, all
linked Runs terminal and complete supported coverage of their entire work intervals
for the requested economic identity. Coverage SHALL retain full RunRefs, linked-Run
membership, outcome revisions, source profiles, intervals and evidence references.
Missing or ambiguous coverage SHALL remain unknown, never inferred zero. Relevant
new evidence or bindings SHALL require a new coverage revision.

#### Scenario: Reconciled interval omits an attempt

- **GIVEN** a terminal Change with two Runs and a reconciled interval covering only the first
- **WHEN** full-change completeness is evaluated
- **THEN** the scoped subtotal remains available but full-change coverage is incomplete with the omitted Run identified.

#### Scenario: Terminal change with an open run

- **GIVEN** an accepted Change with a linked Run still open and some known charges
- **WHEN** full-change completeness is evaluated
- **THEN** it remains incomplete regardless of the Change outcome or the known subtotal.

#### Scenario: Missing evidence versus observed zero

- **GIVEN** one terminal Run lacks economic evidence while another has supported zero evidence covering its full work interval and requested unit
- **WHEN** their coverage is evaluated
- **THEN** the first stays unknown and only the second contributes an observed zero; a zero-run Change is ineligible rather than free.

#### Scenario: Evidence contradicts declared work bounds

- **GIVEN** a Run declared to end at 09:30 and attributed work evidence at 09:45
- **WHEN** full-change coverage is evaluated
- **THEN** it is incomplete until an explicit interval or audited attribution correction resolves the conflict, regardless of a reconciled source interval.

#### Scenario: Re-evaluate late coverage changes

- **GIVEN** a previously complete revision followed by a newly linked existing Run or unresolved late correction
- **WHEN** settlement is recomputed at the later cutoff
- **THEN** a new revision is incomplete until the additional coverage or correction is resolved, while replay at the earlier cutoff retains its original revision.

### Requirement: Outcomes and unbound remainder

Settlements SHALL preserve all linked retry and abandoned expenditure and expose unbound evidence separately.

#### Scenario: Accepted after retries

- **GIVEN** an accepted change with two failed runs and one successful run
- **WHEN** it is settled
- **THEN** all three known expenditures are included.

#### Scenario: Unbound abandoned evidence

- **GIVEN** an abandoned bound run and one ambiguous unbound event
- **WHEN** repository totals are requested
- **THEN** abandoned spend is retained and the ambiguous event remains outside change totals.
