# Verify personal-account source feasibility

## Purpose

Personal IDE and CLI accounts may expose usage without billable money or stable session joins. Establishing the accessible evidence prevents the pilot from promising Enterprise-only reconciliation.

## ADDED Requirements

### Requirement: Capability evidence matrix

The feasibility report SHALL distinguish documented availability from inspected personal-account evidence for each supported surface.

#### Scenario: No inspected export

- **GIVEN** official documentation but no user export
- **WHEN** a capability is assessed
- **THEN** its observed status is unverified and exact evidence needed is recorded.

#### Scenario: Enterprise-only capability

- **GIVEN** a personal Cursor account
- **WHEN** Enterprise OTel is considered
- **THEN** it is marked unavailable for this pilot without assuming an upgrade.

### Requirement: Economic and attribution gate

The report SHALL state which stable identifiers, economic units, billing bases and correction signals are actually available before an adapter mapping is approved.

#### Scenario: Tokens without money

- **GIVEN** a fixture containing token counts and no monetary field
- **WHEN** cash reconciliation is assessed
- **THEN** cash remains unavailable and usage import is assessed separately.

#### Scenario: Missing session identifier

- **GIVEN** records with only timestamps
- **WHEN** automatic attribution is assessed
- **THEN** time proximity is insufficient and records require explicit manual mapping or remain unbound.

### Requirement: Safe reproducible fixtures

The evidence package SHALL provide synthetic or fully redacted fixtures with provenance and transformation notes without prompts, secrets or identifiable account data.

#### Scenario: Reviewable fixture

- **GIVEN** a proposed source fixture
- **WHEN** its inclusion is reviewed
- **THEN** the reviewer can verify documented shape and preserved joins while content and real identifiers are absent.
