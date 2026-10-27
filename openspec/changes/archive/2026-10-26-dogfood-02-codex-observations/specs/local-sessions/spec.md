## ADDED Requirements

### Requirement: Explicit approved native diagnostics
The system SHALL attach only the existing canonically admitted finite Codex source to an existing local session through an explicitly selected file and repository. The convenience selector SHALL resolve the packaged profile and expected digest without granting approval. Core import contracts SHALL remain unchanged.

#### Scenario: Selected approved snapshot
- **GIVEN** an existing session and the admitted exact source
- **WHEN** the user invokes session observe-codex with session ID, file and repository ID
- **THEN** the unchanged reader validates acquisition, strict JSON, exact admission, producer and projection
- **AND** the report retains six independent request/category quantities and hashed identities with source/profile/approval/projection/mapping/producer provenance, fixed unknowns and no raw IDs, path, prompts or pending record metadata

#### Scenario: Rejected source is read-only
- **GIVEN** a populated v1 session database
- **WHEN** changed or unadmitted source bytes, an unsafe source or invalid selection are supplied
- **THEN** the existing closed native diagnostic rejects before any database write or migration and leaves source/database bytes unchanged

#### Scenario: Missing or unfamiliar target
- **GIVEN** a missing session or an unfamiliar database
- **WHEN** an observation is requested
- **THEN** it rejects without creating or adopting storage

### Requirement: Immutable atomic native associations
The system SHALL store each source snapshot once as safe JSON and one immutable explicit link/event per session. It SHALL acquire and validate before migration and decide migration under the write lock. It SHALL reject conflicts atomically and preserve historical manual rows, forecasts and events.

#### Scenario: Exact retry and two explicit links
- **GIVEN** a valid snapshot attached to one session
- **WHEN** the user retries or explicitly attaches it to a second session
- **THEN** retry creates no event and the second link creates only its own event without duplicating facts

#### Scenario: Conflict and migration rollback
- **GIVEN** recognized populated v1 or v2 storage
- **WHEN** source identity, repository, semantic meaning or existing session link conflicts, or migration fails
- **THEN** the complete transaction rolls back including schema, snapshots, links and events

#### Scenario: Concurrent migration
- **GIVEN** v1 storage and concurrent valid observations
- **WHEN** each transaction rechecks schema/session under BEGIN IMMEDIATE
- **THEN** migration occurs once and committed links remain idempotent without losing manual history

#### Scenario: Read-only v1 and manual compatibility
- **GIVEN** exact recognized v1 or v2 storage
- **WHEN** show/history or existing manual start/finish/correct/retry runs
- **THEN** reads do not migrate and existing manual behavior and bootstrap no-clobber safety remain usable

### Requirement: Native diagnostics grant no totals or learning
The system SHALL report native diagnostics separately from manual forecast/measurement/error authority. Native facts SHALL NOT populate measurements, total errors, cohort samples or core Run/Change bindings. No category sum, reconstructed total, source finality or learning authority SHALL be inferred.

#### Scenario: Native-only observation
- **GIVEN** a frozen manual forecast without a manual measurement
- **WHEN** native partial diagnostics are attached
- **THEN** the forecast stays identical, native session total/error stay unknown and the report explicitly excludes native partials from learning and total-error evaluation

#### Scenario: Independent manual measurement
- **GIVEN** a native attachment and an independently entered declared manual total
- **WHEN** show/history or a later comparable forecast runs
- **THEN** the manual total retains its manual error and cohort eligibility while native diagnostics retain their exclusion

#### Scenario: Stored report without source
- **GIVEN** stored native diagnostics and an unavailable or changed source file
- **WHEN** show/history runs
- **THEN** it renders the saved safe diagnostics without reading that source
