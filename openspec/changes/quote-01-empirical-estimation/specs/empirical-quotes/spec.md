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

### Requirement: Complete total-change observations

The estimator SHALL admit only one full-change aggregate per eligible terminal
Change at the quote cutoff. Every linked attempt SHALL be terminal with supported
coverage over its full work interval for the requested economic identity, as defined
by reconciliation. Reconciled subsets, zero-run Changes and unresolved or missing
coverage SHALL be excluded with reasons at every cohort level, including fallback.

#### Scenario: Exclude a reconciled partial subtotal

- **GIVEN** 19 fully covered historical Changes and one accepted Change reconciled only for one of its two attempts
- **WHEN** a total-change quote requires 20 observations
- **THEN** the partial Change is excluded from every cohort and the result is unpriced rather than trained on its subtotal.

#### Scenario: Count all attempts once

- **GIVEN** a terminal Change with three terminal Runs fully covered in one economic unit and several settlement revisions
- **WHEN** it qualifies at the quote cutoff
- **THEN** its selected complete revision supplies one observation including all three attempts, not three observations or multiple revisions.

### Requirement: Reproducible pre-quote features

The estimator SHALL use and embed normalized, versioned registration snapshots for
change_shape, trajectory and execution_profile. Narrow cohorts SHALL require matching
supported versions and pre-run features available by the quote cutoff. Missing, late
or incompatible feature evidence SHALL skip affected narrow levels with a reason,
without excluding otherwise eligible observations from repository-wide fallback.

#### Scenario: Equivalent normalized inputs

- **GIVEN** Changes registered with " BugFix " and "bugfix" plus equivalent other features and the same eligible evidence
- **WHEN** quotes select cohorts
- **THEN** both use the same canonical bugfix value and deterministic cohort membership, recording features/v1 and capture times.

#### Scenario: Ignore post-work feature reconstruction

- **GIVEN** a peer's category was reconstructed after its first run or became available after the quote cutoff
- **WHEN** a historical cohort is selected
- **THEN** that peer supplies no narrow-cohort feature match; its otherwise eligible cost can still enter repository-wide fallback.

#### Scenario: Missing or incompatible feature version

- **GIVEN** sufficient repository history but missing target features or an unsupported peer feature version
- **WHEN** quote considers narrow cohorts
- **THEN** affected levels or peer matches are skipped with reasons and repository fallback remains available.

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
