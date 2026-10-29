# Offline synthetic evaluation

## Purpose

Describe the delivered synthetic evaluator, its chronological comparisons and its strict separation from future live assessment authority.

## ADDED Requirements

### Requirement: Leakage-free baseline comparison

Offline synthetic evaluation SHALL compare the candidate and repository-wide baseline chronologically using the same eligible evidence and economic units, scoring one initial pre-run Quote per Change. Their priced/unpriced availability SHALL match under shared repository fallback with a minimum of 20 comparable Changes; unexpected asymmetry SHALL be reported as a comparison error rather than scored.

#### Scenario: Future correction

- **GIVEN** a correction arrives after an evaluated quote
- **WHEN** evaluation replays history
- **THEN** neither candidate nor baseline sees the correction early.

#### Scenario: Unavailable imported history

- **GIVEN** an imported historical Quote whose evidence and bindings were not available in the destination at its cutoff
- **WHEN** chronological evaluation requests replay there
- **THEN** the report records replay_unavailable outside scored cases, rather than reconstructing source-store knowledge from backdated origin fields.

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

Offline synthetic evaluation SHALL score only full-change truth with complete coverage of all linked
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

### Requirement: Deterministic offline evaluation report

Evaluation SHALL accept portable synthetic history and a versioned pre-registered
protocol through a documented local CLI or API, reuse existing quote replay and
demand validation, and produce deterministic aggregate report content. It SHALL
report scored and omitted cases with truth eligibility, compare frozen initial
forecasts against the broad repository baseline, and separate later updates.
Synthetic report acceptance SHALL NOT establish live calibration or complete the
separately authorized pilot assessment.

#### Scenario: Reproduce a synthetic report

- **GIVEN** the same portable synthetic history, destination availability and pre-registered protocol version
- **WHEN** a contributor repeats the documented evaluation
- **THEN** aggregate report content and exclusion counts match, adaptive availability remains separate from economic matched availability, and overhead measurements are labeled separately.

#### Scenario: Exclude the target and keep updates separate

- **GIVEN** a target Change has multiple attempts, revisions and later diagnostic forecasts
- **WHEN** the initial forecast is evaluated
- **THEN** all target attempts and revisions remain outside its peer, transfer calibration and validation inputs, exactly one initial forecast is scored, and later updates remain separate even after terminal completion.

### Requirement: Explicit metric denominators

Offline synthetic evaluation SHALL report metric definitions, units, counts and unknown cases alongside calibration, width, attribution and abandoned expenditure.

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

The offline synthetic evaluation report SHALL always declare
`synthetic_only_not_yet_validated` and report the protocol's registered `source_gaps`.
Optional measured overhead SHALL remain separate from deterministic report content.
Synthetic results SHALL NOT establish live accuracy, complete native truth, source
approval or calibrated accuracy.

#### Scenario: Small sample

- **GIVEN** synthetic evidence cannot establish live improvement from the baseline
- **WHEN** the decision rubric is applied
- **THEN** the conclusion remains `synthetic_only_not_yet_validated` and registered source gaps remain visible.

### Requirement: Chronological adaptive evaluation and scoped promotion

Offline synthetic adaptive diagnostics SHALL use pre-registered
historical, dimensional, transfer and rehearsal comparisons with scoped diagnostic
rubrics. Diagnostics SHALL score shared compatible complete synthetic truth,
report differing availability separately, and retain the selected ecosystem,
component, population and policy. The existing economic matched-availability
comparison SHALL remain unchanged. A reported `synthetic_rubric_passed` result
SHALL NOT create a passing live validation receipt or grant native calibration
or promotion authority.

#### Scenario: Additional transfer availability

- **GIVEN** a target-only method has no range but transfer produces a labeled scenario
- **WHEN** adaptive comparison runs
- **THEN** the additional availability is reported separately, shared eligible cases are scored and no economic comparison rule is weakened

#### Scenario: Future outcome or selected pair

- **GIVEN** a truth correction or bridge selection is first known after forecast time
- **WHEN** the initial forecast is evaluated
- **THEN** prediction uses only cutoff-visible inputs and scoring uses the separately frozen truth cutoff

#### Scenario: Failure to improve

- **GIVEN** an observed method fails the registered synthetic coverage, underestimation, width, overhead or baseline-error rubric
- **WHEN** adaptive diagnostics report the case
- **THEN** `synthetic_rubric_passed` is false, the diagnostic failure remains visible, and no passing live validation receipt is created

#### Scenario: Count and overhead

- **GIVEN** many samples or an expensive rehearsal without passing scoped metrics
- **WHEN** the synthetic rubric is assessed
- **THEN** sample count and assessment effort alone do not establish calibrated accuracy

### Requirement: Safe synthetic experiment boundary

The offline evaluator SHALL use an isolated disposable store, strict versioned
inputs, asserted synthetic provenance and allowlisted report fields. It SHALL NOT
restore imported computation receipts, inspect transcripts or open the ordinary
runtime database. Unsupported native kinds and malformed inputs SHALL fail safely.

#### Scenario: Preserve destination authority

- **GIVEN** portable foreign forecasts and backdated origin observations
- **WHEN** an isolated synthetic experiment imports them
- **THEN** they remain replay_unavailable and are never scored as local computations.

#### Scenario: Scenario diagnostics are not observed quantiles

- **GIVEN** transfer emits scenario arrays without observed summaries
- **WHEN** the registered diagnostic formula computes their median and extent
- **THEN** the report labels scenario diagnostics with separate support, donor and truth counts and creates no validation receipt.

#### Scenario: Safe repeated execution

- **GIVEN** a valid asserted synthetic experiment and an existing runtime database
- **WHEN** the command runs twice or rejects an unsafe input
- **THEN** the runtime database is unchanged, core results are deterministic, errors contain no rejected values, and optional timing is separate.

#### Scenario: Bound every accepted numeric spelling

- **GIVEN** decimal or rational numeric strings using ASCII or Unicode decimal digits
- **WHEN** either a numeric string exceeds 256 characters or its decimal exponent has magnitude above 256
- **THEN** evaluation rejects it before model parsing and exact arithmetic, without echoing the value; bounded equivalent spellings retain exact numeric semantics.

#### Scenario: Safe nested component identifiers

- **GIVEN** an economic or demand component, including policy and rehearsal budget/overhead components
- **WHEN** its unit or basis violates the report identifier grammar of 1–200 ASCII letters, digits, underscores, periods, colons and hyphens starting with a letter or digit
- **THEN** evaluation rejects the input before computation or report projection without echoing the identifier.
