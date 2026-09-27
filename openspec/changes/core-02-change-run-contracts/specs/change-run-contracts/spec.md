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

### Requirement: Portable source-evidence mapping

The system SHALL expose a stable evidence reference for each imported source record
and SHALL support explicit evidence-to-run mappings through bind. References SHALL
retain provider/surface, source profile and identity scope. Mappings SHALL preserve
manual or verified-provider provenance and timestamps across portable artifact replay.
Unknown references and conflicting assignments SHALL fail atomically; identical
mappings SHALL be idempotent, without claiming cross-export identity for file-scoped rows.

#### Scenario: Map a source row without a session

- **GIVEN** an imported Cursor row without session ID, its exposed file-scoped evidence_id and an existing run R bound to change C
- **WHEN** bind explicitly maps that evidence_id to R
- **THEN** only the selected row is attributed to C through R with manual provenance and mapping timestamps; other rows remain unbound.

#### Scenario: Replay a manual mapping

- **GIVEN** a file-scoped evidence reference and its manual mapping to run R
- **WHEN** evidence, run and mapping are exported and imported twice into a fresh store
- **THEN** one association remains with the original identity scope, provenance and timestamps.

#### Scenario: Reject an unknown evidence selector

- **GIVEN** a bind request naming an evidence_id absent from storage
- **WHEN** the request is processed
- **THEN** it fails without adding evidence or a mapping.

#### Scenario: Reject conflicting record attribution

- **GIVEN** evidence already mapped to run R, manually or by a verified provider join
- **WHEN** bind attempts to map it to run S
- **THEN** the request fails without changing the original attribution or provenance.

### Requirement: Economic kind and currency

The system SHALL require kind, unit and basis for every economic component and a
currency for known monetary amounts. Nonmonetary quantities SHALL have currency=null
as not applicable; this SHALL NOT make a known quantity unknown. Null amounts SHALL
remain unknown and SHALL NOT be converted to zero or another economic kind.

#### Scenario: Round-trip known nonmonetary quantities

- **GIVEN** 100 input tokens, 2 provider credits and 50 nano AIU with distinct units, known amounts and currency=null
- **WHEN** the records are validated, exported and imported
- **THEN** each quantity stays known and exact in its original unit with currency not applicable, without inferred money.

#### Scenario: Reject known money without currency

- **GIVEN** a monetary amount of 1.00 with no currency
- **WHEN** the record is validated
- **THEN** it is rejected without persisting a guessed currency.

#### Scenario: Reject currency on a nonmonetary quantity

- **GIVEN** a token quantity with kind=nonmonetary and currency=USD
- **WHEN** the record is validated
- **THEN** it is rejected rather than interpreted as a monetary token price.

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
