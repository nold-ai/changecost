# Import accessible personal Cursor usage exports

## Purpose

Personal Cursor exports cannot be assumed to expose Enterprise OTel identifiers or dollar charges. A useful importer must describe exactly which evidence is accessible.

## ADDED Requirements

### Requirement: Personal-source boundary

The Cursor adapter SHALL accept only personal-account export profiles supported by the feasibility evidence and SHALL NOT require Enterprise access.

#### Scenario: Enterprise fields missing

- **GIVEN** a supported personal fixture lacking conversation IDs
- **WHEN** import runs
- **THEN** usage imports without pretending Enterprise fields exist.

#### Scenario: Unknown headers

- **GIVEN** a file outside supported profiles
- **WHEN** import runs
- **THEN** it fails with a safe unsupported-format diagnostic and no partial writes.

### Requirement: Unknown cash and separate tokens

The adapter SHALL preserve available token categories and SHALL represent missing monetary cost as unknown.

#### Scenario: Tokens-only export

- **GIVEN** a row containing 100 input and 20 output tokens but no dollar cost
- **WHEN** settlement runs
- **THEN** the two token quantities remain distinguishable and cash cost is unknown rather than zero.

#### Scenario: Unverified monetary field

- **GIVEN** a cost-looking column without documented basis
- **WHEN** normalization runs
- **THEN** it is not silently labeled billed USD.

### Requirement: Attribution and overlap honesty

The adapter SHALL distinguish manual mappings from provider-backed joins and SHALL disclose identity limitations in overlapping exports.

#### Scenario: Manual attribution

- **GIVEN** a source row without session ID and an explicit mapping to run R
- **WHEN** the row is imported
- **THEN** it is linked to R with manual provenance.

#### Scenario: Ambiguous overlap

- **GIVEN** two overlapping files without stable row IDs
- **WHEN** both are imported
- **THEN** overlap cannot yield a fully reconciled additive total until resolved.

#### Scenario: Identical file replay

- **GIVEN** an already imported file
- **WHEN** it is imported again
- **THEN** the known evidence count and totals do not increase.
