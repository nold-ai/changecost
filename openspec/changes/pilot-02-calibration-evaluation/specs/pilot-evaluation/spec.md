# Future live evaluation extensions

## Purpose

Extend the accepted synthetic-only contract through a separately authorized real-evidence boundary while preserving synthetic protections.

## MODIFIED Requirements

### Requirement: Complete reproducible evaluation truth

Offline synthetic evaluation SHALL score only full-change truth with complete coverage of all linked
attempts in the requested economic identity. It SHALL record the truth cutoff and
settlement/coverage revisions separately from the quote cutoff. Unavailable complete
truth SHALL remain visible in exclusion counts, outside accuracy denominators.

A separately authorized real-evidence boundary SHALL also apply these complete-truth
requirements to its approved live inputs. Unknown, partial or provisional native
counters SHALL remain outside full-change accuracy denominators.

The separately authorized real-evidence boundary SHALL also satisfy
`Leakage-free baseline comparison` and `Explicit metric denominators`, applying
their requirements and scenarios to approved live inputs. This extension SHALL
NOT change the synthetic-only entrypoint.

#### Scenario: Refuse partial truth

- **GIVEN** a priced quote whose terminal Change has only a reconciled partial source interval
- **WHEN** evaluation computes calibration
- **THEN** that case is reported as missing full-change truth and does not enter the scored denominator or become a zero actual.

#### Scenario: Freeze later truth without leaking it

- **GIVEN** a complete corrected settlement available after the quote but before the declared truth cutoff
- **WHEN** the evaluation is replayed
- **THEN** the fixed truth revision is scored while quote reconstruction uses only its earlier evidence cutoff, and corrections after the truth cutoff affect neither result.

#### Scenario: Provisional Codex counters are not complete truth

- **GIVEN** a terminal Change has only unknown, partial or provisional Codex thread counters
- **WHEN** evaluation selects full-change measured truth
- **THEN** the report retains the exclusion reason outside accuracy denominators and infers neither total-change demand nor billed money from those counters.

### Requirement: Reproducible honest conclusion

The offline synthetic evaluation report SHALL always declare
`synthetic_only_not_yet_validated` and report the protocol's registered `source_gaps`.
Optional measured overhead SHALL remain separate from deterministic report content.
Synthetic results SHALL NOT establish live accuracy, complete native truth, source
approval or calibrated accuracy.

A separately authorized live report SHALL separate real observations from synthetic
verification and document source gaps, measured overhead and next evidence before
drawing conclusions. Unverified provider money SHALL remain unvalidated. If live
evidence cannot distinguish improvement from the baseline, the report SHALL state
not yet validated and name the required next evidence.

#### Scenario: Small sample

- **GIVEN** synthetic evidence cannot establish live improvement from the baseline
- **WHEN** the decision rubric is applied
- **THEN** the conclusion remains `synthetic_only_not_yet_validated` and registered source gaps remain visible.

#### Scenario: Unavailable personal cash

- **GIVEN** Cursor exports contain no verified money
- **WHEN** the pilot report is written
- **THEN** Cursor monetary reconciliation is unvalidated and token results are labeled separately.

### Requirement: Chronological adaptive evaluation and scoped promotion

Offline synthetic adaptive diagnostics SHALL use pre-registered
historical, dimensional, transfer and rehearsal comparisons with scoped diagnostic
rubrics. Diagnostics SHALL score shared compatible complete synthetic truth,
report differing availability separately, and retain the selected ecosystem,
component, population and policy. The existing economic matched-availability
comparison SHALL remain unchanged. A reported `synthetic_rubric_passed` result
SHALL NOT create a passing live validation receipt or grant native calibration
or promotion authority.

Separately authorized live adaptive evaluation SHALL pre-register promotion criteria,
score shared compatible complete measured truth, and bind any passing validation
receipt to exact ecosystem, component, population and policy. It SHALL withhold or
withdraw applicable future validation when its registered metrics fail. If live
transfer widens uncertainty or underestimates more than target-only history,
validation SHALL be withheld or withdrawn for applicable future forecasts and the
failure SHALL remain visible. Partial native usage SHALL NOT establish full-task truth. These live duties require the
separate real-evidence boundary and cannot be satisfied by synthetic diagnostics.

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

#### Scenario: Partial native truth

- **GIVEN** native usage without complete all-attempts demand coverage
- **WHEN** calibration is scored
- **THEN** it remains outside full-task accuracy denominators and is not inferred from cash absence or zero placeholders

## ADDED Requirements

### Requirement: Separate prospective live authority and execution

Live assessment SHALL require separate evaluation authorization, exact selected-lane
source/reader approval, complete measurement authority and permitted data/consent.
Publication SHALL require approval of the proposed aggregate disclosure. The live
protocol SHALL freeze its manifest, rubric and independent-unit rule before target
outcomes, disclose prior exposure, preserve original-store authority and separate
forecast and truth cutoffs. Synthetic execution SHALL NOT satisfy these obligations.

#### Scenario: Dataset without real-evidence execution

- **GIVEN** a permitted complete dataset but only the shipped synthetic evaluator
- **WHEN** a contributor prepares a live assessment
- **THEN** live execution remains blocked pending a separately authorized implemented real-evidence boundary, without relabeling real input as synthetic.

#### Scenario: Prior exposure or changed registration

- **GIVEN** an analyst has seen target outcomes or changes a frozen manifest
- **WHEN** the assessment is reviewed
- **THEN** the original registration and amendments remain visible, prior exposure prevents a prospective claim for those cases, and unreviewed changes block the affected run.

#### Scenario: Analysis without publication approval or passing rubric

- **GIVEN** authorized analysis with no aggregate publication approval or a failed rubric
- **WHEN** the contributor proposes findings and validation
- **THEN** unauthorized aggregates are not published, a failed rubric creates no passing receipt, and live tasks and archival remain incomplete until actual acceptance evidence exists.
