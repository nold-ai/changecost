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
