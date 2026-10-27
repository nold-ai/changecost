# codex-local-import Specification

## Purpose
Import explicitly selected local Codex session evidence through independently approved finite profiles, preserving diagnostic provenance without granting demand or financial authority.

## Requirements

### Requirement: Explicit approved local sources

The Codex reader SHALL accept only explicitly selected existing local coding-session files with independently approved version/surface profiles, without collection or account configuration.

#### Scenario: Unapproved producer

- **GIVEN** a readable session with an unknown producer version
- **WHEN** import is requested
- **THEN** it rejects before persistence with a safe unsupported-profile code

#### Scenario: Native CLI diagnostic boundary

- **GIVEN** an unsupported native profile or a malformed source record
- **WHEN** import rejects through the native CLI mode
- **THEN** its error-v1 response retains a closed diagnostic code and optional bounded zero-based ordinal without source values, paths, identities or parser exception text; other modes retain their existing errors

#### Scenario: Ordinary desktop chat

- **GIVEN** a general chat export rather than an approved coding-session profile
- **WHEN** import is requested
- **THEN** it remains unsupported rather than inferred coding usage

#### Scenario: Retained creation header

- **GIVEN** a session retains a creation-version header and logical session identity while later records may have been appended by a different engine, process or client
- **WHEN** the exact producer and coding-session profile is assessed
- **THEN** that header or logical session identity alone cannot approve the later records and numeric import rejects without the mapping's independent producer binding

### Requirement: Non-overlapping versioned accounting

The reader SHALL select one independently approved request or snapshot accounting representation for each exact producer/surface/profile and mapping revision. It SHALL preserve stable event identity, revision/reset interpretation, root/subagent ownership and source finality according to that mapping. Reported cache, reasoning and total categories SHALL remain distinct when inclusion is unproven. Indexed metadata and overlapping request/turn/thread snapshots SHALL NOT become additional contributions to the same quantity.

#### Scenario: Overlapping counters

- **GIVEN** persisted request-level token_usage_record fields, legacy event_msg/token_count snapshots and indexed tokens_used metadata describe overlapping work
- **WHEN** the reader aggregates
- **THEN** only the approved representation supplies source facts, overlapping categories are not added and unresolved revision/ownership stays explicit

#### Scenario: Partial lineage

- **GIVEN** a missing parent/subagent or nonterminal accounting interval
- **WHEN** full-demand or settlement support is assessed
- **THEN** partial diagnostics do not certify full-task quantities or billed charges

#### Scenario: Producer defaults and estimated snapshots

- **GIVEN** the producer serializes absent backend detail fields as zero or replaces legacy snapshots with context estimates
- **WHEN** native accounting meaning is assessed
- **THEN** source-defaulted zero is not represented as proven explicit backend zero and estimated snapshots cannot become additive request usage

#### Scenario: Best-effort usage and configured model

- **GIVEN** usage records can omit responses without usage, include incomplete responses and lack request intervals or served-model identity
- **WHEN** an approved partial diagnostic mapping is applied
- **THEN** missing records do not become zero work, usage presence does not certify successful finality and persistence time or configured turn model does not establish request interval or served model

### Requirement: Safe atomic read-only import

The reader SHALL bound and allowlist metadata, preserve original bytes, reject unsafe/conflicting inputs atomically and retain replay/correction provenance without private content.

#### Scenario: Bound input and private diagnostics

- **GIVEN** a selected file exceeding 10 MiB, 10,000 records or depth 32, a symlink/nonregular file, duplicate JSON keys, malformed/truncated data or nonfinite/invalid token counts
- **WHEN** native import is requested
- **THEN** it rejects atomically with bounded code/ordinal diagnostics and no private values, source paths, source identities or parser exception text in output

#### Scenario: Selected snapshot identity

- **GIVEN** a selected expected SHA-256 that differs from the acquired bytes or file identity/size/modification metadata that changes during acquisition
- **WHEN** the reader hashes and parses its single bounded read-only acquisition
- **THEN** import rejects before persistence, preserves source bytes and does not claim adversarial concurrent-writer protection from a stat comparison

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

#### Scenario: Native import mode and later binding

- **GIVEN** an approved native file import requested together with normalized economic import, settlement computation or lifecycle selectors
- **WHEN** CLI mode validation runs
- **THEN** it rejects before persistence, while a valid native-only import stores unbound Evidence and NativeUsage for a later existing exact manual binding operation

#### Scenario: Bound diagnostic source facts

- **GIVEN** imported native usage has subsequently been manually bound to an exact Run and Change
- **WHEN** demand or trusted financial coverage is evaluated
- **THEN** the existing synthetic-only gates remain effective and no DemandObservation, MeasurementPolicy, SourceCoverage or EconomicEvidence is inferred from reader approval or binding

#### Scenario: Approval cannot be supplied by a flag

- **GIVEN** a caller-selected profile/version/hash, structural inspection receipt or current installed CLI version without the matching independently approved native mapping
- **WHEN** native import is requested
- **THEN** it rejects as unsupported before persistence and cannot create an approval or relabel a different producer/surface

#### Scenario: Repository coincidence

- **GIVEN** a session names the task repository but lacks an exact approved Change join
- **WHEN** import runs
- **THEN** evidence remains unbound until explicitly mapped to a Run and Change

#### Scenario: Subscription estimate

- **GIVEN** a cost-like field or native usage under a subscription
- **WHEN** a forecast or settlement is requested
- **THEN** economic basis stays explicit and no billed charge or calibrated demand authority is inferred

### Requirement: Finite producer admission and partial diagnostic meaning

The initial mapping SHALL admit only a canonically approved whole-file SHA and frozen request subset, bound to independently adjudicated producer evidence and canonical projection. Header/version coincidence, caller assertions and unactivated proposals SHALL NOT grant admission. It SHALL preserve six serialized categories separately, mark backend presence unknown, retain partial reported lineage and keep served model/version, request interval, completeness and finality unknown. No native demand, financial or automatic attribution authority follows.

#### Scenario: Proposed approval is not runtime eligibility

- **GIVEN** an independently reviewed proposal without canonical activation or an implemented checked package derivative
- **WHEN** native import eligibility is assessed
- **THEN** it remains blocked; a positive planning report or caller flag cannot activate it

#### Scenario: Renamed copy and changed snapshot

- **GIVEN** an approved finite snapshot, a byte-identical regular copy and an appended or reformatted variant
- **WHEN** whole-file admission is checked
- **THEN** the copy shares admission and semantic replay while changed bytes reject until separately adjudicated and canonically admitted

#### Scenario: Unsupported lifecycle forms

- **GIVEN** an unreviewed resumed/forked history or distinct-ID corrective replacement
- **WHEN** the initial finite mapping is applied
- **THEN** changed bytes reject and selected rows require source-backed adjudication as direct response observations; no general correction/reset detector or counter differencing is claimed

#### Scenario: Serialized zero and missing served model

- **GIVEN** an admitted source zero and only configured-model context
- **WHEN** diagnostic facts are projected
- **THEN** the zero remains a serialized observation with unknown backend presence and served model/version remain null; no configured-model join establishes them

### Requirement: Canonical finite admission controls

Contributor tooling SHALL validate finite Codex admission payloads and their native usage approval bindings before accepting the canonical register. Supported Codex usage SHALL require a recognized finite admission, with exact whole-source and projection digests, bounded sorted unique record membership, consistent classification/cardinality, the reviewed projection schema and partial diagnostic policy, fixed acquisition limits, and a producer claim matching its profile. The usage proof SHALL bind the same native source, profile and six decisions. Structural validity SHALL NOT authenticate semantic approval or enable a runtime reader. The 23 historical profiles SHALL retain their original content and zero approvals; only the independently approved finite diagnostic profile may be activated in this change.

#### Scenario: Approved finite profile activation

- **GIVEN** the independently approved profile and exact six-decision proof
- **WHEN** they are added to the canonical register and the matrix is regenerated
- **THEN** contributor validation accepts 24 profiles with one finite usage approval, preserving the 23 historical profiles and all partial/unknown authority limits

#### Scenario: Rehashed malformed admission

- **GIVEN** an admission with missing or unsupported kind, changed projection semantics or limits, invalid record membership/classification, producer mismatch, or inconsistent source/proof decisions
- **WHEN** a structurally rebound proof is supplied to contributor validation
- **THEN** the register still rejects; recomputing a profile digest cannot bypass admission checks

#### Scenario: Activation does not enable import

- **GIVEN** the finite profile was canonically activated in the contributor-only stage on 2026-10-23, without separately authorized runtime implementation
- **WHEN** the authority conferred by that activation alone is inspected
- **THEN** that activation grants no implemented native reader, import command, packaged runtime admission or native demand/financial authority; the separately authorized finite reader stage must still satisfy its own runtime requirements
