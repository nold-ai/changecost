## ADDED Requirements

### Requirement: Optional native runtime diagnostics

CI SHALL collect privacy-safe runtime metadata only when the native review report
exists, including after failed review. Diagnostic applicability SHALL NOT replace
or weaken required review evidence, and present malformed metadata SHALL fail.

#### Scenario: Documentation-only review is inapplicable

- **GIVEN** documentation-only inputs and no native review report
- **WHEN** the dispatcher and CI diagnostic selection run
- **THEN** review is explicitly inapplicable and diagnostic collection is skipped
- **AND** applicable repository checks still run.

#### Scenario: Required review produces no report

- **GIVEN** behavior-affecting inputs and a native process producing no fresh report
- **WHEN** the mandatory review gate runs
- **THEN** it fails for missing native evidence even though diagnostics are skipped.

#### Scenario: Present malformed report

- **GIVEN** a present malformed native report, including after failed review
- **WHEN** diagnostic collection runs
- **THEN** it returns a bounded safe error and nonzero exit without masking the original failure.

#### Scenario: Present valid report

- **GIVEN** a present native report with valid matching runtime metadata
- **WHEN** diagnostic collection runs
- **THEN** it writes privacy-safe metadata and exits zero without claiming native assurance.
