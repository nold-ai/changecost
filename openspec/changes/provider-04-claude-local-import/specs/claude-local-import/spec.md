# Claude Code project JSONL import

## Purpose

Import explicitly selected existing Claude Code project JSONL metadata under
independently approved version-specific accounting, preserving corrections,
replay and manual work attribution without inferred demand or monetary authority.

## ADDED Requirements

### Requirement: Explicit approved local sources

The reader SHALL accept only explicitly selected existing Claude Code project
JSONL files under independently approved producer/surface profiles. Approval
SHALL establish version-specific persisted-log semantics; selected hashes,
installed binaries, structural receipts and another surface's documentation SHALL
NOT grant approval. The reader SHALL NOT collect data or change account settings.

#### Scenario: Unapproved or ambiguous producer

- **GIVEN** a readable project log with an unknown version, incompatible profile or creation header that cannot identify later records' producer
- **WHEN** import is requested
- **THEN** it rejects before persistence with a safe unsupported-profile diagnostic rather than inheriting approval from the header, installed CLI or nearby rows

#### Scenario: Other Claude surfaces

- **GIVEN** ordinary chat, a Desktop coding transcript, IDE data, SDK/result stream, JSON container or SQLite/index source
- **WHEN** the project JSONL reader is requested
- **THEN** it remains unsupported in this lane despite similar usage fields

#### Scenario: Approval and acquisition identity are separate

- **GIVEN** caller-supplied profile/hash, synthetic fixtures or documentation without independent native approval
- **WHEN** numeric import eligibility is checked
- **THEN** it rejects before persistence and cannot activate a profile or substitute finite diagnostics for reusable reader support

### Requirement: Non-overlapping versioned accounting

The reader SHALL follow independently approved event/revision identity, ownership,
correction/reset, representation inclusion, cache and finality policy. It SHALL
retain unresolved accounting and coverage rather than infer first/last/maximum
precedence, additive totals or complete work from field presence.

#### Scenario: Overlapping or revised project records

- **GIVEN** project records repeat identities, change quantities or represent overlapping work
- **WHEN** approved accounting is applied
- **THEN** only approved representations/revisions contribute, and unresolved identity, precedence or inclusion cannot become numeric aggregation

#### Scenario: Cache categories and missing quantities

- **GIVEN** input, cache-read, cache-write and output observations with unverified inclusion, an absent quantity and an explicit zero
- **WHEN** native facts are projected
- **THEN** categories remain distinct, absence differs from zero and no unsupported sum or backend-presence claim is inferred

#### Scenario: Partial lineage and finality

- **GIVEN** missing root/subagent relationships, unresolved reset or nonterminal accounting intervals
- **WHEN** source support and full-demand coverage are assessed
- **THEN** unknown relationships, quantities and finality remain explicit; partial observations do not certify complete task usage or billed charges

#### Scenario: Portable contract does not fit source meaning

- **GIVEN** approved Claude categories, scope or lineage cannot fit the current native contract faithfully
- **WHEN** compatibility is assessed
- **THEN** the mapping remains blocked pending explicit reviewed contract amendment rather than relabeling facts, weakening Codex constraints or silently narrowing the reader outcome

### Requirement: Safe atomic read-only import

The reader SHALL allowlist bounded metadata from one stable read-only acquisition,
preserve original bytes and first provenance, and append approved facts/corrections
atomically. Semantic identity SHALL be independent of filename, ordinal, batch and
later acquisition digest. Corrections SHALL preserve predecessor and reason;
unresolved conflicts SHALL reject without partial persistence.

#### Scenario: Bound input and safe diagnostics

- **GIVEN** more than 10 MiB, 10,000 records or depth 32, a symlink/nonregular source, duplicate keys, malformed/truncated JSONL or invalid/nonfinite quantities
- **WHEN** import runs
- **THEN** it rejects atomically with a closed code and optional bounded ordinal without paths, source identities, payloads or parser exception text

#### Scenario: Private content and changing acquisition

- **GIVEN** private nested content or a file whose expected hash or acquisition identity/size/modification metadata does not match the read
- **WHEN** the reader acquires and projects metadata
- **THEN** private fields are never persisted/logged, mismatched or changing input rejects before persistence and no completeness or adversarial-writer protection is claimed

#### Scenario: Repeated snapshot and approved correction

- **GIVEN** an imported snapshot and a later independently approved correction
- **WHEN** each is imported repeatedly
- **THEN** exact semantic replay returns existing references without duplicate quantities, correction appends once with predecessor/reason and first-acquisition/admission provenance stays immutable

#### Scenario: Historical snapshot after correction

- **GIVEN** an accepted original revision followed by a valid correction
- **WHEN** the original accepted snapshot is imported again
- **THEN** it is a no-op, does not restore old quantities and does not fork or rewrite history

#### Scenario: Conflicting or stale correction batch

- **GIVEN** valid new facts plus a conflicting identity, stale predecessor, fork, cycle or unapproved reset/correction
- **WHEN** the batch is imported
- **THEN** the entire import rejects and stored facts, bindings and correction history remain unchanged

#### Scenario: Cross-provider identity and provenance

- **GIVEN** equal raw IDs in different providers or mismatched provider/profile/producer/admission associations
- **WHEN** import or portable-store validation runs
- **THEN** approved namespaces cannot collide, invalid associations reject and Claude support cannot broaden existing Codex admission

#### Scenario: Portable history and recovery

- **GIVEN** accepted facts/corrections, pre-reader records and a current-version exported bundle
- **WHEN** current-version roundtrip/recovery is exercised
- **THEN** identities, quantities, first provenance and correction links survive without changing old records; rollback preserves backups/history and discloses older-binary limitations

### Requirement: Explicit binding and separate authorities

The reader SHALL distinguish manual/provider/unbound attribution and native
usage/estimated money/billed money. It SHALL return exact safe evidence references
for separate manual binding. Source approval or binding SHALL NOT authorize native
demand learning, monetary settlement or calibration.

#### Scenario: Mutually exclusive import mode

- **GIVEN** project import combined with another native import, economic computation/import, lifecycle or binding selectors
- **WHEN** CLI mode validation runs
- **THEN** it rejects before acquisition/persistence; valid import stores unbound facts for later existing manual binding

#### Scenario: Repository coincidence and exact manual binding

- **GIVEN** imported sessions naming the repository without an approved Change join
- **WHEN** attribution is requested
- **THEN** evidence remains unbound until an exact reference is manually mapped to an existing Run and Change; identical binding is idempotent and conflicting reassignment rejects

#### Scenario: Bound facts do not promote authority

- **GIVEN** approved facts manually bound to a Run and Change
- **WHEN** demand, financial coverage or calibration eligibility is evaluated
- **THEN** no measurement policy, demand outcome, billed evidence or calibrated receipt is inferred; each authority remains independently gated

#### Scenario: Subscription estimate

- **GIVEN** a cost-like field or native usage under a subscription
- **WHEN** a forecast or settlement is requested
- **THEN** economic basis remains explicit, missing money differs from zero and no billed charge or calibrated demand authority is inferred
