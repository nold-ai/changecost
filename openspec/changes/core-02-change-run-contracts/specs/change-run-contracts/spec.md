# Define change, run, quote and settlement contracts

## Purpose

Change-level accounting needs stable identity and portable evidence before provider adapters exist. Explicit binding prevents coincidental timestamps from becoming financial attribution.

## ADDED Requirements

### Requirement: Explicit stable binding

The system SHALL bind runs to changes only through explicit, namespaced identifiers and SHALL preserve binding provenance.

#### Scenario: Repeated binding

- **GIVEN** an existing run-to-change binding
- **WHEN** the same bind request is repeated
- **THEN** one binding remains and the result is idempotent.

#### Scenario: Conflicting binding

- **GIVEN** a run already bound to change A
- **WHEN** a bind to change B is attempted
- **THEN** the request fails without changing A or prior provenance.

#### Scenario: Ambiguous run

- **GIVEN** a run with only nearby timestamps
- **WHEN** changes are loaded
- **THEN** the run remains unbound.

### Requirement: Portable exact contracts

The system SHALL round-trip changecost/v1 records without losing exact amounts, units, completeness, identities or correction history.

#### Scenario: Decimal round trip

- **GIVEN** a USD billed amount 0.1000001 and an unknown credit amount
- **WHEN** records are exported then imported
- **THEN** the exact decimal and unknown remain distinct without conversion.

#### Scenario: Unsupported version

- **GIVEN** a changecost/v2 artifact
- **WHEN** it is imported
- **THEN** a clear version error occurs without partial writes.

### Requirement: Transactional persistence

The system SHALL reject invalid or conflicting writes atomically and preserve local history across restarts.

#### Scenario: Partial failure

- **GIVEN** an artifact with one valid and one conflicting record
- **WHEN** import runs
- **THEN** neither record is newly committed.

#### Scenario: Concurrent binding

- **GIVEN** two writers propose different changes for the same run
- **WHEN** both commit attempts finish
- **THEN** only one valid binding exists and the other reports a conflict.
