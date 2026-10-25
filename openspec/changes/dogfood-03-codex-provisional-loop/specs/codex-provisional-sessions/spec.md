## ADDED Requirements

### Requirement: Explicit provisional target and separate learning
The system SHALL freeze a Codex provisional target only when `start --source codex` is explicitly selected. Manual SHALL remain the default. Native headers SHALL identify manual false and provisional authority without granting billing, calibration or core numeric authority. Comparable native forecasts SHALL use one latest terminal capture per distinct bound identity with exact task/context/target/producer-family semantics and exact median arithmetic.

#### Scenario: Capture then forecast
- **GIVEN** a new Codex attempt with a before-work guess
- **WHEN** an explicitly selected compatible file and repository are captured with an explicit terminal outcome
- **THEN** the latest cumulative source counter receives provisional target error and trains the next exact cohort member once
- **AND** unknown coverage, completeness, provider finality, subagent inclusion and unverified producer claims remain explicit

#### Scenario: Frozen estimates and unknown forecasts
- **GIVEN** a frozen forecast containing earlier capture revisions and quantities
- **WHEN** an earlier attempt is refreshed or an unestimated attempt is captured
- **THEN** old forecasts stay unchanged and latest captures train future forecasts
- **AND** unestimated attempts do not enter the MAE denominator, which is disclosed separately from learning count

#### Scenario: Manual isolation
- **GIVEN** manual and Codex attempts with identical task/context labels
- **WHEN** manual start retry, finish/correct, forecast or default history runs
- **THEN** Codex membership cannot be reinterpreted as manual, source switching rejects, manual partial exclusion remains, and native/manual errors and samples never pool

### Requirement: Bounded source-reported lifetime counter
The system SHALL stream only one explicitly selected stable no-follow regular file with at most 128 MiB, 100,000 rows and depth 32. It SHALL reject duplicate members, nonfinite numbers, excessive numeric lexemes, missing or ambiguous identities and unsupported pinned producer shapes using safe fixed diagnostics. It SHALL retain only safe projected counter state and hashes.

#### Scenario: Overlapping counters and larger source
- **GIVEN** a compatible source exceeding the finite reader bounds with repeated cumulative snapshots and overlapping categories/last counts
- **WHEN** capture runs
- **THEN** only the latest total_token_usage.total_tokens is used, never sums or baseline subtraction
- **AND** the exact finite reader and canonical approvals are unchanged

#### Scenario: Unsupported or malformed source
- **GIVEN** a missing identity, unsupported producer, malformed nonnull token payload, boolean/negative/overflow counter, decreasing counter, unstable file, symlink, duplicate member, excessive depth/bytes/rows or invalid JSON
- **WHEN** capture runs
- **THEN** it rejects without persisting private source values or modifying database/source bytes

### Requirement: Immutable captures with global identity and atomic retries
The system SHALL bind one domain-separated provider identity hash of the header `id` (thread identity) to one attempt globally, excluding runtime `session_id`, path/repository/mapping from identity. An optional header `session_id` SHALL independently be a nonblank string of at most 512 characters and MAY differ from the thread identity. First capture SHALL bind one repository. Append refresh SHALL require an expected predecessor, nonblank reason, unchanged semantics/identity/repository, exact old-prefix hash, no shrink and no decreasing counter. Captures SHALL be immutable and supply one latest training sample per attempt.

#### Scenario: Duplicate and renamed source
- **GIVEN** a captured provider identity
- **WHEN** identical selected bytes/payload are retried from a renamed file
- **THEN** no new event/revision is created
- **AND** a second attempt or changed repository cannot duplicate its learning

#### Scenario: Distinct thread and runtime identities
- **GIVEN** a compatible header with distinct nonblank thread `id` and runtime `session_id`
- **WHEN** the source is captured and another attempt selects the same thread with a changed runtime `session_id`
- **THEN** the first capture trains once and the duplicate attempt rejects without database mutation
- **AND** an absent runtime `session_id` remains supported while malformed runtime identities reject

#### Scenario: Append and old operation retry
- **GIVEN** a saved capture and compatible appended bytes
- **WHEN** refresh supplies the current predecessor and reason
- **THEN** one immutable revision is appended and future learning still counts one attempt
- **AND** retrying identical old bytes and payload after a later capture returns the old operation_revision with the current report view

#### Scenario: Rewritten or concurrent capture
- **GIVEN** a populated store
- **WHEN** a prefix is rewritten, source shrinks, outcome changes without correction, predecessor is stale, or concurrent conflicting captures race
- **THEN** the rejected transaction leaves database bytes unchanged without partial identity binding, capture, event or migration

### Requirement: Versioned store and readable safe output
The system SHALL recognize exact v1/v2/v3 schemas, migrate writes atomically, preserve manual and finite history, and keep read-only v1/v2 reports unmigrated. Existing committed no-clobber bootstrap SHALL remain. Human output SHALL be concise while full safe JSON remains inspectable and control characters remain escaped.

#### Scenario: Migration and finite compatibility
- **GIVEN** populated v1 or v2 storage
- **WHEN** native start upgrades to v3 or finite observation runs on v3
- **THEN** manual forecasts, measurements, finite diagnostics and event history remain intact without downgrade
- **AND** injected migration/insertion failure rolls back all bytes/schema

#### Scenario: Safe concise summary
- **GIVEN** a pending or captured session and optional finite diagnostics
- **WHEN** human show/history runs without reopening source files
- **THEN** it shows guess/cohort forecast, sample count, source-reported total, high/low absolute and relative error, revision/outcome, unknowns and evaluated/learning counts
- **AND** it omits private paths/raw identity/prompts and full fact arrays while JSON retains safe provenance and finite diagnostic exclusion
