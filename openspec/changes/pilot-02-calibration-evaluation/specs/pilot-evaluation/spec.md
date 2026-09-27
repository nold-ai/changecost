# Evaluate attribution and chronological quote calibration

## Purpose

The pilot must test whether change-level cohorts add value over repository-wide history, while making unavailable source capabilities and small samples visible.

## ADDED Requirements

### Requirement: Leakage-free baseline comparison

Evaluation SHALL compare the candidate and repository-wide baseline chronologically using the same eligible evidence and economic units, scoring one initial pre-run Quote per Change. Their priced/unpriced availability SHALL match under shared repository fallback; unexpected asymmetry SHALL be reported as a comparison error rather than scored.

#### Scenario: Future correction

- **GIVEN** a correction arrives after an evaluated quote
- **WHEN** evaluation replays history
- **THEN** neither candidate nor baseline sees the correction early.

#### Scenario: Matched repository fallback

- **GIVEN** narrow cohorts below the minimum but sufficient comparable repository history
- **WHEN** candidate and baseline are evaluated at the same cutoff
- **THEN** both are priced with identical repository quantiles and sample counts; the candidate records its fallback reason.

#### Scenario: Joint insufficient evidence

- **GIVEN** comparable repository history below the shared minimum
- **WHEN** candidate and baseline are evaluated
- **THEN** both are unpriced and the report retains that case with counts and reasons outside accuracy metrics.

#### Scenario: Detect unexpected availability mismatch

- **GIVEN** a faulty replay result in which only one method is priced under the shared configuration
- **WHEN** evaluation validates the pair
- **THEN** it reports a comparison error and stops accuracy reporting for that run rather than hiding the mismatch.

### Requirement: Complete reproducible evaluation truth

Evaluation SHALL score only full-change truth with complete coverage of all linked
attempts in the requested economic identity. It SHALL record the truth cutoff and
settlement/coverage revisions separately from the quote cutoff. Unavailable complete
truth SHALL remain visible in exclusion counts, outside accuracy denominators.

#### Scenario: Refuse partial truth

- **GIVEN** a priced quote whose terminal Change has only a reconciled partial source interval
- **WHEN** evaluation computes calibration
- **THEN** that case is reported as missing full-change truth and does not enter the scored denominator or become a zero actual.

#### Scenario: Freeze later truth without leaking it

- **GIVEN** a complete corrected settlement available after the quote but before the declared truth cutoff
- **WHEN** the evaluation is replayed
- **THEN** the fixed truth revision is scored while quote reconstruction uses only its earlier evidence cutoff, and corrections after the truth cutoff affect neither result.

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
