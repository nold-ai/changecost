# Evaluate attribution and chronological quote calibration

## Purpose

The pilot must test whether change-level cohorts add value over repository-wide history, while making unavailable source capabilities and small samples visible.

## ADDED Requirements

### Requirement: Leakage-free baseline comparison

Evaluation SHALL compare the candidate and repository-wide baseline chronologically using the same eligible evidence and economic units.

#### Scenario: Future correction

- **GIVEN** a correction arrives after an evaluated quote
- **WHEN** evaluation replays history
- **THEN** neither candidate nor baseline sees the correction early.

#### Scenario: One unpriced method

- **GIVEN** only one method has enough peers at a cutoff
- **WHEN** results are summarized
- **THEN** the case is counted as asymmetric availability and excluded from paired accuracy without disappearing.

### Requirement: Explicit metric denominators

Evaluation SHALL report metric definitions, units, counts and unknown cases alongside calibration, width, attribution and abandoned expenditure.

#### Scenario: Attribution denominator

- **GIVEN** 6 provider-bound, 2 manual and 2 unbound eligible records
- **WHEN** coverage is reported
- **THEN** all 10 form the denominator and provider-backed coverage is 6/10, not 8/8.

#### Scenario: Undefined spend share

- **GIVEN** no comparable known terminal spend
- **WHEN** abandoned share is calculated
- **THEN** the result is undefined with a reason, not 0%.

#### Scenario: Coverage and width

- **GIVEN** 10 comparable priced observations
- **WHEN** calibration is reported
- **THEN** coverage includes numerator/10 and uncertainty, with p90-p50 widths in the original unit.

### Requirement: Reproducible honest conclusion

The evaluation report SHALL separate synthetic verification from live observations and SHALL document source gaps and measured overhead before drawing conclusions.

#### Scenario: Unavailable personal cash

- **GIVEN** Cursor exports contain no verified money
- **WHEN** the pilot report is written
- **THEN** Cursor monetary reconciliation is unvalidated and token results are labeled separately.

#### Scenario: Small sample

- **GIVEN** available evidence cannot distinguish improvement from the baseline
- **WHEN** the decision rubric is applied
- **THEN** the outcome is not yet validated and required next evidence is stated.
