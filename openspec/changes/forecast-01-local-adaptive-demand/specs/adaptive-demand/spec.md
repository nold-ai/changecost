# Adaptive local demand forecasting

## ADDED Requirements

### Requirement: Honest zero knowledge

Demand forecasting SHALL return zero_knowledge with qualitative dimensions and missing-evidence requests when no applicable observations or bridge exist; it SHALL NOT invent empirical quantities, percentiles or charges.

#### Scenario: Empty store

- **GIVEN** a registered task and ecosystem with no evidence
- **WHEN** demand quote is requested
- **THEN** it returns zero_knowledge with no numeric usage estimate and records the unknowns

#### Scenario: Changed ecosystem

- **GIVEN** older validated history but a changed or unknown model/harness and no applicable bridge
- **WHEN** a forecast is created
- **THEN** older validation does not transfer and the new context remains zero_knowledge

### Requirement: Frozen task and ecosystem snapshots

The forecast SHALL retain versioned task dimensions, ecosystem qualifiers, provenance, unknowns and input availability before linked implementation work; outcomes SHALL remain separate.

#### Scenario: Late patch features

- **GIVEN** a final patch and retry count known only after work
- **WHEN** the initial forecast is replayed
- **THEN** neither becomes an initial predictor

#### Scenario: Unknown and mixed ecosystems

- **GIVEN** unknown model fields or attempts using several models
- **WHEN** observations are compared
- **THEN** unknowns are not equal known profiles and mixed work retains composition without an invented single-model label

### Requirement: Separate replayable demand authority

Demand records SHALL be distinct from financial Quotes and Features/v1. Computation SHALL preserve cutoff-visible policies, selected input revisions and local receipts without granting imported claims local authority.

#### Scenario: Economic compatibility

- **GIVEN** the new demand mode and old economic artifacts
- **WHEN** default quote/check and historical explain run
- **THEN** existing min-20, strict features, synthetic billed-USD support and financial advice remain unchanged

#### Scenario: Imported validation claim

- **GIVEN** a portable forecast claims validated state
- **WHEN** it is imported and explained
- **THEN** the producer claim is preserved but cannot establish local validation or cutoff availability

#### Scenario: Atomic operation replay

- **GIVEN** an existing operation ID is retried unchanged or reused with another demand request
- **WHEN** quote handles it
- **THEN** the same request returns its record and the conflict rejects without mutation

### Requirement: Incremental observed learning

Learning SHALL derive one eligible full terminal Change aggregate per compatible measurement identity, retaining all attempts/outcomes and selected revisions; incomplete or imagined observations SHALL NOT become training truth. The target Change and all its attempts/revisions SHALL be excluded from its own analogue, validation and transfer-calibration inputs, including later forecasts.

#### Scenario: Terminal target cannot teach its own forecast

- **GIVEN** a terminal target Change with observed quantities and a bridge pair containing one of its attempts
- **WHEN** an initial forecast, later update or historical explanation selects evidence
- **THEN** all target revisions/attempts and the pair are excluded; distinct historical repeat-task Changes may qualify with dependence disclosed

#### Scenario: Sparse target history

- **GIVEN** one compatible complete target observation
- **WHEN** another forecast is requested
- **THEN** learning exposes n=1 and provisional/observed summaries without a calibrated probability claim

#### Scenario: Reimport and correction

- **GIVEN** a repeated import followed by a valid corrected quantity
- **WHEN** learning is recomputed
- **THEN** the Change contributes once using the selected revision and earlier forecasts remain unchanged

#### Scenario: Partial abandoned work

- **GIVEN** an abandoned multi-attempt Change with missing coverage for one attempt
- **WHEN** history is selected
- **THEN** the partial quantity remains diagnostic and excluded from full-task truth rather than zero or successful-only training

### Requirement: Scoped directional transfer

A transfer hypothesis SHALL bind cutoff-visible matched comparisons, direction, measurement semantics, selection/mapping policy, support counts and residuals. Unresolved confounding SHALL NOT establish an isolated model effect.

#### Scenario: First matched pair

- **GIVEN** one compatible matched task in an older and newer ecosystem
- **WHEN** a transfer scenario is formed
- **THEN** it is labeled transfer_hypothesis with n=1 and no calibrated probability

#### Scenario: Simultaneous changes

- **GIVEN** task scope, model and review workflow all changed
- **WHEN** a comparison is proposed
- **THEN** confounding is exposed and no isolated model multiplier is claimed

#### Scenario: Incompatible categories and zero

- **GIVEN** different cache/category meanings or a zero donor denominator
- **WHEN** ratio transfer is considered
- **THEN** incompatible mapping is refused and zero never causes division or an invented ratio

#### Scenario: Future bridge

- **GIVEN** a useful comparison first becomes available after the forecast cutoff
- **WHEN** historical explain replays
- **THEN** the future pair is excluded and the earlier result is reproduced

### Requirement: Target evidence and validation policy

Forecasting SHALL prefer applicable target evidence, keep mapped donor data hypothetical, and require a pre-registered scoped validation policy plus measured local receipt before validated_forecast. Count alone SHALL NOT promote evidence.

#### Scenario: Target evidence grows

- **GIVEN** target observations arrive after a transfer scenario
- **WHEN** a later forecast is computed
- **THEN** target support is updated without treating mapped donors as measured target samples

#### Scenario: Count without proof

- **GIVEN** 20 observations but no applicable passing evaluation receipt
- **WHEN** validation is checked
- **THEN** the result remains unvalidated and the economic default is unchanged

#### Scenario: Policy drift

- **GIVEN** a validated profile changes or later evaluation fails
- **WHEN** a subsequent forecast is requested
- **THEN** old validation is inapplicable while earlier immutable records remain inspectable

### Requirement: Explicit economic scenarios

Demand quantities, effort, credits, estimated money and billed charges SHALL remain distinct. Optional price scenarios SHALL require compatible explicit rates with effective date, unit/basis and source provenance and SHALL NOT grant financial completeness or advisory authority.

#### Scenario: Subscription and missing cache

- **GIVEN** native token counts under a subscription with missing price/cache information
- **WHEN** a money scenario is requested
- **THEN** missing components remain unknown and neither subscription charge nor inferred rates become billed money

#### Scenario: Explicit compatible rates

- **GIVEN** a demand scenario and explicitly supplied compatible rates with effective date, unit/basis and source provenance
- **WHEN** an estimated monetary scenario is rendered
- **THEN** its assumptions, frozen rate provenance and estimated basis are visible and check does not treat it as a trusted economic Quote

#### Scenario: Missing rate provenance

- **GIVEN** supplied rates missing source, effective date or unit/basis
- **WHEN** an estimated monetary scenario is requested
- **THEN** the monetary scenario is rejected without inventing rates or granting financial/advisory authority

### Requirement: Optional bounded rehearsal and local privacy

Rehearsal SHALL be user-invoked and separately measured; forecasts SHALL store minimized assessments rather than prompts/raw reasoning/imagined outcomes. Local learning SHALL NOT share data or invoke models automatically.

#### Scenario: Imaginary implementation

- **GIVEN** an assessment describes hypothetical edits and passing tests
- **WHEN** an outcome import is attempted
- **THEN** imaginary results cannot become measured training truth and assessment overhead stays separate

#### Scenario: Opt out and login

- **GIVEN** no rehearsal request or sharing consent, with or without login
- **WHEN** local forecasting runs
- **THEN** no LLM request, telemetry enablement or outbound contribution occurs
