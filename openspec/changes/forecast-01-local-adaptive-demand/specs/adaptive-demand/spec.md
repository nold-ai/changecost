# Adaptive local demand forecasting

## ADDED Requirements

### Requirement: Bounded exact demand arithmetic

Demand decimal values SHALL have at most 4096 aligned integer and fractional digits, including their coefficient and positive or negative exponent span, before downstream exact arithmetic. Zero SHALL obey the same representational bound. Demand rational values SHALL have at most 4096 digits in each numerator and denominator component before Fraction conversion. Ordinary supported exact values and original numeric representations SHALL retain their existing behavior; legacy economic Amount admission SHALL remain unchanged.

#### Scenario: Compact extreme decimal exponent

- **GIVEN** a supplied demand observation, price rate or other demand decimal containing an extreme exponent, including zero or a negative exponent
- **WHEN** its typed artifact or portable bundle is admitted
- **THEN** it rejects before exact exponent expansion or persistence, leaves the existing store unchanged and does not echo the rejected value

#### Scenario: Oversized rational component

- **GIVEN** a supplied demand ratio with an oversized numerator or denominator
- **WHEN** its typed record is validated
- **THEN** it rejects before Fraction conversion, without changing interpreter limits

#### Scenario: Supported boundary and historical records

- **GIVEN** ordinary exact demand values and values within the inclusive digit bounds
- **WHEN** they are admitted, computed, retried, imported, replayed or recovered
- **THEN** their normal exact behavior and supported v1/v2 historical authority remain unchanged; economic Amount retains its existing contract

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

#### Scenario: A single historical task repeats the target scope

- **GIVEN** one eligible historical Change sharing the current target's frozen task scope
- **WHEN** a new forecast is computed
- **THEN** repeat-task dependence is disclosed even with n=1, without admitting target truth or changing observed quantities/counts; repeated peer scopes also retain the disclosure

#### Scenario: Versioned disclosure preserves historical replay

- **GIVEN** locally computed observed-summary/v1 forecasts and validation receipts
- **WHEN** a new observed-summary/v2 forecast adds target-aware dependence disclosure
- **THEN** v1 replay and idempotent retries retain their original payloads, v2 is separately reproducible, and portable decoding/recovery supports both versions without a product or database-schema version change

#### Scenario: Partial abandoned work

- **GIVEN** an abandoned multi-attempt Change with missing coverage for one attempt
- **WHEN** history is selected
- **THEN** the partial quantity remains diagnostic and excluded from full-task truth rather than zero or successful-only training

#### Scenario: Known work start survives an interval correction

- **GIVEN** a Run with an immutable observed start and a later corrected interval start
- **WHEN** its final observation covers the corrected interval but omits the earlier observed start
- **THEN** the attempt remains incomplete for learning and validation truth; observations covering both bounds remain eligible and earlier forecast replay remains unchanged

#### Scenario: The immutable known point follows the corrected window

- **GIVEN** a corrected interval and observation ending before the Run's immutable observed start
- **WHEN** complete accepted or abandoned Change truth is selected
- **THEN** the observation must contain the known point on both sides or remain incomplete, with equality eligible and valid earlier snapshots unchanged

#### Scenario: Missing observed start and corrected end

- **GIVEN** a Run without an observed start and a valid corrected interval
- **WHEN** complete coverage is assessed
- **THEN** the latest interval start/end govern completeness without treating registration time or superseded interval bounds as work boundaries

#### Scenario: Shared replay dependencies remain bounded

- **GIVEN** local validation generations sharing earlier forecast and receipt dependencies
- **WHEN** one forecast, validation or inspection operation reproduces those dependencies
- **THEN** each complete replay result is reused only within that operation and its exact authority/visible-input context; later operations, corrections, failed rubrics and imported claims cannot inherit cached authority

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

#### Scenario: Imported validation history continues structurally

- **GIVEN** an imported validation head and later independently eligible local evaluated outcomes
- **WHEN** a new local receipt is computed
- **THEN** it links the unique cutoff-visible structural predecessor without inheriting imported authority; reimport/retry remain idempotent and only the current locally reproduced head can support validation

#### Scenario: Future validation history cannot be bypassed

- **GIVEN** a structural receipt head unavailable at the requested local cutoff
- **WHEN** a new receipt is requested
- **THEN** computation rejects before persistence rather than creating a parallel root or treating the future claim as local validation

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

#### Scenario: Imported forecast price provenance is bound

- **GIVEN** an imported demand forecast with an estimated price
- **WHEN** its declared price request is absent or differs from the estimated price source
- **THEN** the import rejects atomically before the forecast can enter demand history

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

### Requirement: Explicit demand invocation and deterministic summaries

Demand mode SHALL accept assessment/ecosystem references imported through the existing portable workflow, without money selectors. Mixed modes SHALL reject atomically. Learning SHALL report observed minimum/median/maximum and sample count, selecting complete dimensions before broad known-ecosystem history. Transfer SHALL use median ratios only and retain zero-denominator pairs diagnostically.

#### Scenario: Demand request without money
- **GIVEN** imported minimized assessment and ecosystem records
- **WHEN** quote demand mode references them without economic flags
- **THEN** a replayable separate demand record is created and mixed modes reject before persistence

#### Scenario: Complete all-attempt measurement
- **GIVEN** synthetic bound attempts with independent compatible full coverage
- **WHEN** an accepted or abandoned terminal Change enters history
- **THEN** every attempt contributes once, correction chains select their current revision, and partial or incompatible mixed work stays diagnostic

#### Scenario: Observed summaries
- **GIVEN** complete compatible historical quantities 1 and 3
- **WHEN** an unvalidated demand forecast selects history
- **THEN** n is 2 and observed minimum, median and maximum are 1, 2 and 3, without a calibrated percentile claim


#### Scenario: Explicitly blank optional price selector

- **GIVEN** demand mode with required assessment/ecosystem selectors and an explicitly empty or whitespace-only price identifier
- **WHEN** the forecast operation is requested
- **THEN** it rejects before opening or mutating the store and does not silently replace the supplied selector with omission


#### Scenario: Retrospective work registration in validation

- **GIVEN** candidate and baseline records marked initial before a Run was visible, followed by complete truth showing earlier work
- **WHEN** local validation is computed
- **THEN** each prediction's own cutoff must strictly precede all truth work bounds, otherwise measurement rejects without persistence; historical prediction replay remains unchanged

### Requirement: Versioned current temporal evidence and selected validation support
New forecasts SHALL use observed-summary/v3. At each cutoff, pre-work and validation truth guards SHALL inspect current Interval and DemandObservation revision heads, retain immutable Run.observed_start, and preserve registration/capture ordering. Superseded erroneous bounds SHALL NOT override the current correction. All existing observed-summary/v1 and v2 forecasts SHALL replay with their exact original temporal and validation applicability rules.

#### Scenario: Corrected historical temporal bound
- **GIVEN** a missing immutable Run start and an erroneous early interval or observation corrected to valid current bounds
- **WHEN** a new forecast or live validation is computed
- **THEN** current revision bounds determine eligibility, while a saved v1/v2 forecast retains its exact payload and idempotent retry.

#### Scenario: Target occurs in actual validation support
- **GIVEN** a passing local receipt whose candidate or baseline selected peers, donors, eligible bridge pair owners, or recursively selected validation evidence includes the current target
- **WHEN** a v3 forecast is computed for that target
- **THEN** the receipt cannot promote that forecast, including all target attempts and revisions. Generic frozen input metadata, excluded/zero-denominator comparisons and structural receipt predecessors alone do not count as selected training support.

#### Scenario: Explicit local receipt generation
- **GIVEN** a locally computed historical receipt with exact demand-validation/v1 request provenance
- **WHEN** it is replayed or retried with the same operation
- **THEN** its original temporal measurement rules and exact payload remain authoritative locally. New receipts use internal demand-validation/v2 request provenance and current revision measurement rules, including when evaluating legacy forecasts; imported labels confer no local authority. No portable schema field is added.
