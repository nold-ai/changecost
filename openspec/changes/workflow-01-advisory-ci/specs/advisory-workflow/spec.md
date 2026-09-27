# Expose advisory CLI checks and GitHub summaries

## Purpose

Developers need readable and machine-consumable results from the standalone CLI without turning an unvalidated quote into a blocking budget policy.

## ADDED Requirements

### Requirement: Stable human and JSON output

The CLI SHALL expose the five approved command families with parseable JSON output and diagnostics on stderr.

#### Scenario: Machine output

- **GIVEN** a successful quote request using JSON
- **WHEN** the command completes
- **THEN** stdout parses as one versioned result including unit/basis, completeness and evidence count.

#### Scenario: Bad input

- **GIVEN** a malformed artifact
- **WHEN** a command runs in JSON mode
- **THEN** it exits nonzero with a structured error and no misleading successful result.

### Requirement: Advisory budget semantics

Budget checks SHALL remain advisory and SHALL compare only compatible known economic values. A settlement whose requested comparison scope is provisional or incomplete SHALL return unknown with the known subtotal and reason, even when that subtotal exceeds budget. Only complete compatible settlement totals or priced quote values SHALL produce within_budget or over_budget.

#### Scenario: Over budget

- **GIVEN** a priced p90 of 18 USD billed and budget 15 USD billed
- **WHEN** check runs
- **THEN** status is over_budget and process exit is zero.

#### Scenario: Unknown comparison

- **GIVEN** an unpriced quote or credit budget against USD
- **WHEN** check runs
- **THEN** status is unknown with an explanation and exit zero.

#### Scenario: Missing charge below budget

- **GIVEN** a settlement with 10 USD billed known, one missing USD charge and a 15 USD billed budget for the same scope
- **WHEN** check runs
- **THEN** status is unknown with the 10 USD subtotal and missing-charge reason, never within_budget, and exit is zero.

#### Scenario: Provisional subtotal above budget

- **GIVEN** a provisional settlement with 20 USD billed known and an unresolved correction against a 15 USD billed budget
- **WHEN** check runs
- **THEN** status is unknown with its provisional subtotal and correction reason, not a claimed final over_budget result, and exit is zero.

#### Scenario: Complete settlement within budget

- **GIVEN** a complete 10 USD billed settlement and a compatible 15 USD billed budget for its declared scope
- **WHEN** check runs
- **THEN** status is within_budget and exit is zero.

### Requirement: Safe standalone CI summary

The CI example SHALL use local artifacts without provider credentials and SHALL render untrusted values as data.

#### Scenario: Malicious display value

- **GIVEN** an artifact label containing shell substitution and Markdown syntax
- **WHEN** the summary example executes
- **THEN** no embedded command runs and the label is safely rendered.

#### Scenario: Advisory only

- **GIVEN** an over-budget valid artifact
- **WHEN** the example workflow runs
- **THEN** the job records advice without imposing a required budget gate.
