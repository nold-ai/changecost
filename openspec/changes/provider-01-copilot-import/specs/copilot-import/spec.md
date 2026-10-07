# Import native Copilot IDE and CLI evidence

## Purpose

Copilot local telemetry may supply useful usage and billing units, but repeated span attributes and surface-specific session semantics need explicit handling.

## ADDED Requirements

### Requirement: Offline versioned import

The Copilot adapter SHALL import only independently inspected, feasibility-approved versioned local source profiles with documented acquisition and compatibility limits without changing user configuration.

#### Scenario: Unsupported profile

- **GIVEN** a file with an unverified schema version
- **WHEN** settle imports it
- **THEN** it fails clearly before storage and no IDE settings change.

#### Scenario: No network

- **GIVEN** a supported synthetic fixture and disabled network
- **WHEN** the adapter runs
- **THEN** supported normalized evidence is produced locally.

### Requirement: Copilot billing semantics

The adapter SHALL count an authoritative billing value once and keep nano AIU, multipliers and monetary amounts distinct.

#### Scenario: Repeated span billing

- **GIVEN** a verified invoke_agent root and child chat carrying the same 100 nano AIU
- **WHEN** the file is imported
- **THEN** the aggregate is 100 nano AIU, not 200, and no cash amount is inferred.

#### Scenario: Multiplier only

- **GIVEN** a record containing github.copilot.cost but no money
- **WHEN** normalization runs
- **THEN** the multiplier is retained as explanatory metadata and monetary cost remains unknown.

### Requirement: Attribution and privacy

The adapter SHALL distinguish verified provider joins, manual mappings and unbound evidence and SHALL NOT retain prompt content.

#### Scenario: Window is not conversation

- **GIVEN** an IDE window session shared by unrelated conversations
- **WHEN** no verified conversation join exists
- **THEN** events stay unbound unless explicitly mapped and the map is labeled manual.

#### Scenario: Content-bearing export

- **GIVEN** an otherwise supported record with prompt and tool-content fields
- **WHEN** normalization and diagnostics run
- **THEN** neither stored artifacts nor logs contain the content.

### Requirement: Regular-metadata and demand authority boundaries

The adapter SHALL use only independently approved explicit local source/version lanes without requiring new telemetry or administrator data. Missing optional exports SHALL remain capability gaps. Native source approval SHALL NOT automatically establish full-demand coverage, billed money or calibrated forecast authority.

#### Scenario: Missing ordinary usage

- **GIVEN** regular metadata with empty/zero placeholders or unresolved overlapping counters
- **WHEN** a native outcome is considered
- **THEN** unknown quantity stays unknown and no full-task training amount is fabricated

#### Scenario: Approved partial source

- **GIVEN** an inspected profile with only partial usage support
- **WHEN** demand or money authority is requested
- **THEN** separate versioned coverage/replay policy and its evidence gate apply; source approval alone does not suffice
