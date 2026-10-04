# empirical-quotes Specification

## Purpose
The pilot needs an explainable estimate whose calibration can be evaluated without leaking future settlements. Sparse or incompatible evidence must produce an honest unpriced result.

## Requirements

### Requirement: Deterministic quantiles

The estimator SHALL return repeatable nearest-rank p50 and p90 quantiles in one
comparable economic identity (kind, unit, currency and basis), using exact Decimal
ordering and integer rank arithmetic without floating conversion or intermediate
rounding. Signed aggregates and supported observed zero SHALL remain unchanged.

#### Scenario: Known ordered sample

- **GIVEN** 20 comparable values from 1 through 20 USD
- **WHEN** the default estimator quotes them
- **THEN** p50 is 10 USD and p90 is 18 USD with n=20 and the algorithm version recorded.

#### Scenario: Permutation invariance

- **GIVEN** the same sample in a different input order
- **WHEN** a quote is recomputed with the same cutoff
- **THEN** quantiles and selected cohort are unchanged.

### Requirement: Backoff and unpriced

The estimator SHALL follow the documented three-level cohort order with a default
minimum of 20 Changes and a configurable strict positive integer minimum. It SHALL
record that minimum, population, per-level counts and rejection reasons and return
unpriced with null quantiles when no cohort qualifies or complete source support is
unavailable. Every level SHALL retain the same economic identity and population.

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

#### Scenario: Configured minimum and invalid request

- **GIVEN** three comparable full-change observations and a minimum of 3, or an invalid minimum of 0, a boolean or a fraction
- **WHEN** quote validates and computes the request
- **THEN** the valid request records n=3 and minimum=3; each invalid request fails before creating a Quote, operation receipt or store.

#### Scenario: Economic identity remains separate

- **GIVEN** observations differing in currency, kind or billed/estimated basis despite otherwise matching features
- **WHEN** each cohort is selected for billed monetary USD
- **THEN** incompatible observations never increase n, and unsupported requested identities return unpriced without conversion.

### Requirement: Complete total-change observations

The estimator SHALL admit only one full-change aggregate per eligible terminal
Change at the quote cutoff. Every linked attempt SHALL be terminal with supported
coverage over its full work interval for the requested economic identity, as defined
by the delivered reconciliation policy. The estimator SHALL derive amounts and
completeness from normalized input selection at the Quote cutoff, without writing
settlement revisions or trusting saved/imported completeness flags. Reconciled
subsets, zero-run Changes and unresolved or missing coverage SHALL be excluded with
reasons at every cohort level, including fallback. Accepted and abandoned Changes
and all linked retry expenditure SHALL remain in the stated population. Currently
only the closed synthetic billed-USD policy proves full-change support; this
capability SHALL NOT add provider policies or infer real-source support from labels.

#### Scenario: Exclude a reconciled partial subtotal

- **GIVEN** 19 fully covered historical Changes and one accepted Change reconciled only for one of its two attempts
- **WHEN** a total-change quote requires 20 observations
- **THEN** the partial Change is excluded from every cohort and the result is unpriced rather than trained on its subtotal.

#### Scenario: Count all attempts once

- **GIVEN** a terminal Change with three terminal Runs fully covered in one economic unit and several settlement revisions
- **WHEN** it qualifies at the quote cutoff
- **THEN** one derived aggregate from its selected normalized economic, lifecycle and coverage inputs supplies the observation including all three attempts, not three observations or multiple settlement revisions.

#### Scenario: Supported zero and missing coverage

- **GIVEN** a fully covered synthetic billed-USD peer with explicit zero economic evidence and another terminal peer lacking evidence or coverage
- **WHEN** repository fallback selects observations
- **THEN** the zero counts once as zero and the missing peer is excluded with reasons rather than treated as free.

#### Scenario: Preserve abandoned and retry expenditure

- **GIVEN** an abandoned Change and an accepted Change with failed, cancelled and successful attempts, all fully covered
- **WHEN** a total attempt-budget Quote selects peers
- **THEN** both Changes contribute one exact aggregate each including every linked attempt, with the accepted-and-abandoned population recorded.

#### Scenario: Old completeness cannot hide a new gap

- **GIVEN** a saved full-change settlement followed before quote time by a newly linked existing Run, missing coverage or unresolved correction
- **WHEN** quote derives peer completeness at its committed cutoff
- **THEN** the peer is excluded until its gap is resolved, even if the old settlement still claims full_change=true; quote writes no new settlement revision.

#### Scenario: Forged or unsupported completeness claims

- **GIVEN** an imported legacy or computed settlement claiming reconciled/full_change, or real-provider records labeled final without an approved policy
- **WHEN** quote evaluates history
- **THEN** claims do not establish eligibility, unsupported peers remain excluded, and an eligible synthetic Quote is explicitly synthetic.

### Requirement: Reproducible pre-quote features

The estimator SHALL use and embed normalized, versioned registration snapshots for
change_shape, trajectory and execution_profile. Narrow cohorts SHALL require matching
supported versions and pre-run features available by the quote cutoff. Missing or
late feature evidence SHALL skip affected narrow levels with a reason,
without excluding otherwise eligible observations from repository-wide fallback.
Unsupported feature-version records SHALL retain the existing strict atomic import
rejection; this capability SHALL NOT widen the stored Features contract.

#### Scenario: Equivalent normalized inputs

- **GIVEN** Changes registered with " BugFix " and "bugfix" plus equivalent other features and the same eligible evidence
- **WHEN** quotes select cohorts
- **THEN** both use the same canonical bugfix value and deterministic cohort membership, recording features/v1 and capture times.

#### Scenario: Ignore post-work feature reconstruction

- **GIVEN** a peer's category was reconstructed after its first run or became available after the quote cutoff
- **WHEN** a historical cohort is selected
- **THEN** that peer supplies no narrow-cohort feature match; its otherwise eligible cost can still enter repository-wide fallback.

#### Scenario: Missing valid features

- **GIVEN** sufficient repository history with valid features/v1 snapshots containing missing target or peer values
- **WHEN** quote considers narrow cohorts
- **THEN** affected levels or peer matches are skipped with reasons and repository fallback remains available.

#### Scenario: Reject unsupported feature version

- **GIVEN** a portable Change with an unsupported feature version
- **WHEN** import validates the artifact before quote selection
- **THEN** the whole import fails unchanged under the existing strict Features contract; no unsupported peer enters any cohort.

### Requirement: Historical information boundary

The estimator SHALL use only records, revisions and relationships recorded, effective and locally available at the quote cutoff, using the core store-local availability contract. It SHALL exclude the target change from its own cohort and SHALL reject cross-store historical replay when required inputs were unavailable there.

#### Scenario: Late correction

- **GIVEN** normalized economic evidence, outcome or interval revisions corrected after quote time
- **WHEN** the historical quote is replayed
- **THEN** the original normalized input revisions known at the committed cutoff determine the historical aggregate; no later correction or stored settlement total is substituted.

#### Scenario: Late-imported outcome and coverage

- **GIVEN** a peer's December normalized economics, complete coverage, bindings and terminal outcome first enter the current store in February
- **WHEN** a January Quote is replayed
- **THEN** the peer is excluded using destination availability even though its source dates predate the cutoff.

#### Scenario: Target exclusion

- **GIVEN** the target change already has settlement history
- **WHEN** a quote for that target runs
- **THEN** its own records do not contribute to n or quantiles.

#### Scenario: Same-time transaction ordering

- **GIVEN** a transaction begun before but committed after the Quote's captured input sequence, even with the same wall timestamp
- **WHEN** the Quote is computed and later replayed
- **THEN** the later transaction and its dependent records remain outside the original cohort.

#### Scenario: Historical Quote remains unchanged

- **GIVEN** a stored Quote followed by later corrections, imports, bindings or outcome/feature evidence
- **WHEN** explain replays the original supported parameters and cutoff
- **THEN** it reproduces the original peer amounts, cohort, counts and quantiles rather than substituting current knowledge.

#### Scenario: Foreign or future cutoff cannot certify replay

- **GIVEN** an imported Quote whose origin cutoff belongs to another store, a time-only or future cutoff, or an unsupported estimator/policy version
- **WHEN** explain requests historical reproducibility
- **THEN** inspection remains available but replay is unavailable with a reason and no mutation.

### Requirement: Computed Quote provenance and offline operations

The quote command SHALL require an existing registered target, explicit repository
and economic identity, and an operation ID. It SHALL capture one committed snapshot
and atomically persist a Quote with local idempotency receipt, versioned estimation
metadata, exact peer aggregates/support references, target features, parameters,
cohort evaluations, exclusions and synthetic provenance. Existing Quote fields
SHALL remain supported; older imported Quotes without estimation metadata SHALL
remain inspectable producer claims. Portable claims SHALL NOT establish local
computation authority. Explain SHALL verify the exact stored payload and evaluate
local receipt and replay eligibility from one read snapshot, retaining safe offline
diagnostics and strict allowlisted data. Receipt operation IDs SHALL be unique
across quote and settlement computations; identical retries SHALL preserve the
original result/cutoff and conflicting reuse SHALL fail unchanged.

#### Scenario: Metadata round trip and legacy claim

- **GIVEN** a newly computed Quote and an older valid Quote without estimation metadata
- **WHEN** they are exported/imported and inspected
- **THEN** exact decimals, parameters, peer/exclusion references and feature snapshot survive, the older claim remains readable, and import creates no local computation authority or historical availability.

#### Scenario: Response loss and operation-kind conflict

- **GIVEN** a successful Quote whose response was lost and later evidence, or an operation ID already used by settlement
- **WHEN** the identical Quote request retries or a conflicting request reuses that ID
- **THEN** the identical retry returns its original Quote without adding history; conflicting arguments or kind fail atomically without interpreting another record as a Quote.

#### Scenario: Safe atomic failure and read-only explanation

- **GIVEN** a missing target/store, invalid selectors or metadata, a private sentinel in an undeclared field, or an injected pre-commit failure
- **WHEN** quote or import fails, then explain inspects a stored Quote
- **THEN** no partial Quote or receipt is published, diagnostics omit private field names/values, and explanation leaves records and local availability unchanged without network access.

#### Scenario: Explanation rejects a backward local clock

- **GIVEN** a stored computed, foreign, legacy or unsupported Quote and later committed local availability
- **WHEN** explain reads it by reference or exact payload while the wall clock is earlier than that availability
- **THEN** it captures the clock once in its existing read transaction, rejects the rollback with a safe clock diagnostic before replay eligibility, and leaves records, receipts and observations unchanged.
- **AND** equality with the latest local availability is allowed; restoration permits the original replay, while an identical durable Quote retry preserves its original result even during clock rollback.

#### Scenario: Zero-attempt cohort evaluation remains bounded

- **GIVEN** many open or terminal Changes without linked attempts, including imported records and repository-wide unattributed or unresolved economic evidence
- **WHEN** quote evaluates eligible peers from its committed snapshot
- **THEN** growth in snapshot record visits remains near-linear for additional zero-attempt Changes; all incomplete-peer reasons, Change/outcome references and relevant unbound/correction evidence remain auditable without repeated full reconciliation for each empty peer.
- **AND** run-bearing peers retain complete reconciliation and historical replay behavior; this adds no provider policy or arbitrary cohort-count limit.

#### Scenario: Linked-peer snapshot evaluation remains bounded

- **GIVEN** many Changes with linked attempts, including open attempts, terminal attempts with missing or complete bounds, multiple attempts and supported observed zero expenditure
- **WHEN** quote evaluates them from one committed snapshot
- **THEN** structural/source indices are built once, additional peers visit their member data and genuinely shared uncertainty rather than repeatedly scanning the full snapshot.
- **AND** member filtering precedes economic series/lane selection; exact amounts, exclusions, order, dependency references and historical algorithm-v1 replay match full reconciliation, including pending corrections, temporal ambiguity and unattributed evidence.

#### Scenario: Shared source uncertainty avoids repeated work

- **GIVEN** linked peers and many resolved unbound economic deltas or unattributed raw evidence, with linear persisted Quote output
- **WHEN** quote evaluates the committed snapshot
- **THEN** shared source selection, temporal summaries and aggregate input roots are prepared once and member-dependent interaction is evaluated without repeating all shared work per peer.
- **AND** member-first lane/file/window selection and exact historical output remain unchanged; pending corrections or whole-series exclusions retain their literal repeated provenance when the output itself requires it.

#### Scenario: End-only lifecycle work constrains feature timing

- **GIVEN** cutoff-visible lifecycle evidence with any non-null start or end before feature capture, including an older end-only Interval followed by a complete revision or another linked attempt
- **WHEN** target or otherwise complete peer features are matched
- **THEN** every visible endpoint constrains pre-work eligibility; late features skip narrow cohorts while complete peers remain usable in repository fallback.
- **AND** equal or later endpoints are valid, cutoff-late declarations/imports cannot change an earlier valid Quote replay, and previously stored invalid results remain immutable rather than being rewritten or falsely certified.
