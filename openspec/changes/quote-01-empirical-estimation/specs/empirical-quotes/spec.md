# Produce deterministic empirical change-cost quotes

## Purpose

The pilot needs an explainable estimate whose calibration can be evaluated without leaking future settlements. Sparse or incompatible evidence must produce an honest unpriced result.

## ADDED Requirements

### Requirement: Deterministic quantiles

The estimator SHALL return repeatable nearest-rank p50 and p90 quantiles in one comparable economic unit.

#### Scenario: Known ordered sample

- **GIVEN** 20 comparable values from 1 through 20 USD
- **WHEN** the default estimator quotes them
- **THEN** p50 is 10 USD and p90 is 18 USD with n=20 and the algorithm version recorded.

#### Scenario: Permutation invariance

- **GIVEN** the same sample in a different input order
- **WHEN** a quote is recomputed with the same cutoff
- **THEN** quantiles and selected cohort are unchanged.

### Requirement: Backoff and unpriced

The estimator SHALL follow the documented cohort order and return unpriced when no cohort meets its recorded minimum sample count.

#### Scenario: Repository fallback

- **GIVEN** narrow cohorts below 20 but 25 comparable repository observations
- **WHEN** quote runs
- **THEN** repository-wide is selected with n=25 and narrower rejection reasons.

#### Scenario: Insufficient evidence

- **GIVEN** all cohorts below the configured minimum
- **WHEN** quote runs
- **THEN** an unpriced result includes counts and reason without zero quantiles.

#### Scenario: Incompatible units

- **GIVEN** 10 USD observations and 10 credit observations
- **WHEN** a USD quote requiring 20 peers runs
- **THEN** credits are excluded and the result is unpriced.

### Requirement: Historical information boundary

The estimator SHALL use only revisions available at the quote cutoff and SHALL exclude the target change from its own cohort.

#### Scenario: Late correction

- **GIVEN** an old settlement corrected after quote time
- **WHEN** the historical quote is replayed
- **THEN** the original known revision is used.

#### Scenario: Target exclusion

- **GIVEN** the target change already has settlement history
- **WHEN** a quote for that target runs
- **THEN** its own records do not contribute to n or quantiles.
