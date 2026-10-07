# Claude local coding-session import

## ADDED Requirements

### Requirement: Explicit approved local sources

The Claude reader SHALL accept only explicitly selected existing local coding-session files with independently approved version/surface profiles, without collection or account configuration.

#### Scenario: Unapproved producer

- **GIVEN** a readable session with an unknown producer version
- **WHEN** import is requested
- **THEN** it rejects before persistence with a safe unsupported-profile code

#### Scenario: Ordinary desktop chat

- **GIVEN** a general chat export rather than an approved coding-session profile
- **WHEN** import is requested
- **THEN** it remains unsupported rather than inferred coding usage

### Requirement: Non-overlapping versioned accounting

The reader SHALL follow independently reviewed identity, ownership, correction, cache-inclusion and finality policy; Require version-specific request/message/record identity and correction precedence; no universal first/last or maximum-value rule. Keep result/assistant lanes separate until inclusion/finality is independently resolved; cache creation/read and estimated USD stay distinct.

#### Scenario: Overlapping counters

- **GIVEN** Desktop coding-agent session logs and Claude Code project logs are separate profiles from ordinary chat. Repeated message IDs sometimes change usage; SDK result/modelUsage and assistant messages can overlap. total_cost_usd is estimated, not Pro subscription billing.
- **WHEN** the reader aggregates
- **THEN** overlapping representations are not added and unresolved revisions/ownership remain explicit

#### Scenario: Partial lineage

- **GIVEN** a missing parent/subagent or nonterminal accounting interval
- **WHEN** full-demand or settlement support is assessed
- **THEN** partial diagnostics do not certify full-task quantities or billed charges

### Requirement: Safe atomic read-only import

The reader SHALL bound and allowlist metadata, preserve original bytes, reject unsafe/conflicting inputs atomically and retain replay/correction provenance without private content.

#### Scenario: Content and unstable file

- **GIVEN** private nested content or a file that changes while read
- **WHEN** a bounded import runs
- **THEN** content is excluded and unstable/invalid input cannot create a complete imported observation

#### Scenario: Repeated and corrected records

- **GIVEN** a repeated snapshot and later verified source correction
- **WHEN** they are imported
- **THEN** idempotent replay contributes no duplicate quantity and the selected revision is auditable

### Requirement: Explicit binding and separate authorities

The reader SHALL distinguish manual/provider/unbound attribution and native usage/estimated money/billed money; source approval SHALL NOT automatically authorize demand learning or financial advice.

#### Scenario: Repository coincidence

- **GIVEN** a session names the task repository but lacks an exact approved Change join
- **WHEN** import runs
- **THEN** evidence remains unbound until explicitly mapped to a Run and Change

#### Scenario: Subscription estimate

- **GIVEN** a cost-like field or native usage under a subscription
- **WHEN** a forecast or settlement is requested
- **THEN** economic basis stays explicit and no billed charge or calibrated demand authority is inferred
