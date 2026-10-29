# claude-local-import Specification

## Purpose
Import explicitly selected existing Claude Code project JSONL metadata under
independently approved version-specific accounting, preserving corrections,
replay and manual work attribution without inferred demand or monetary authority.

## Requirements

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

- **GIVEN** ordinary chat, an unapproved Desktop coding transcript, IDE data, SDK/result stream, JSON container or SQLite/index source
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

#### Scenario: Exact 2.1.215 serialized stages

- **GIVEN** an independently approved exact 2.1.215 project profile and one event with coherent producer, session, optional agent, request and message metadata
- **WHEN** the selected snapshot contains agreeing explicit-null rows and agreeing supported terminal rows
- **THEN** null classifies partial and `end_turn` or `tool_use` classifies final serialized request stage, preserving four separate nullable categories with backend, interval, ownership and scope completeness unknown

#### Scenario: Terminal reason normalization across snapshots

- **GIVEN** accepted terminal facts and another valid snapshot of the same immutable event with equal four-category values but the other supported terminal reason
- **WHEN** the snapshot is imported
- **THEN** it is a no-op returning existing references because both supported reasons have the same canonical accounting meaning; raw reason history is neither stored nor hidden in revision fingerprints

#### Scenario: Terminal reason disagreement inside one snapshot

- **GIVEN** terminal rows for one event contain both `end_turn` and `tool_use`, even with equal quantities
- **WHEN** per-snapshot grammar is validated before normalization
- **THEN** the whole import rejects; missing, malformed or unsupported stop metadata also rejects

#### Scenario: Error-looking usage without identity

- **GIVEN** assistant usage lacks required session, request or message identity, including all-zero counters or client-error marker keys
- **WHEN** contributor grammar is validated
- **THEN** the import rejects atomically rather than skipping by missing identity, zero values or unverified error discriminators

#### Scenario: Closed user exclusion

- **GIVEN** a row with exact type `user`, a message object with exact role `user`, and no direct `usage` or `message.usage` member
- **WHEN** the project snapshot is classified
- **THEN** the row contributes no canonical facts; a missing/nonobject message, different role or present usage member, including null, rejects the entire snapshot

#### Scenario: Closed metadata exclusions

- **GIVEN** a row with exact type `attachment`, `queue-operation`, `last-prompt` or `mode` and no top-level `message` or direct `usage` member
- **WHEN** the project snapshot is classified
- **THEN** the row contributes no canonical facts and its nested payload grants no counter or coverage authority; a present message or usage member, including null, rejects the entire snapshot

#### Scenario: Unknown row grammar

- **GIVEN** any other row label, including `progress` or `system`, an incompatible excluded shape or an assistant without a proper message, role, usage or required identity
- **WHEN** a snapshot also contains otherwise valid new assistant facts
- **THEN** the entire import rejects without a generic type-name skip, recursive counter inspection or partial persistence

### Requirement: Safe atomic read-only import

The reader SHALL allowlist bounded metadata from one stable read-only acquisition,
preserve original bytes and first provenance, and append approved facts/corrections
atomically. Semantic identity SHALL be independent of filename, ordinal, batch and
later acquisition digest. Corrections SHALL preserve predecessor and reason;
unresolved conflicts SHALL reject without partial persistence.

#### Scenario: Growing retained history has bounded lookup work

- **GIVEN** an accepted selected snapshot with multiple events and a growing retained store containing unrelated events, repositories and approved profiles
- **WHEN** the reader resolves accepted event history inside the atomic persistence callback
- **THEN** whole-store history discovery is linear in retained records plus incoming events, with further history work restricted to matching event facts; inserts, replays, approved refinements and global identity conflicts preserve their existing results, first provenance and whole-batch rollback

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

#### Scenario: Retained partial stage permits positive refinement

- **GIVEN** accepted partial A and a later valid snapshot retaining canonical A in all four categories with the same immutable event metadata plus supported terminal B
- **WHEN** the later snapshot is imported
- **THEN** all four category revisions append once from their current partial predecessors with reason `claude-serialized-stage-refinement`, including when A and B have equal quantities

#### Scenario: First combined source accepts both stages now

- **GIVEN** a first valid snapshot contains partial A and terminal B for the same immutable event
- **WHEN** it is imported under the explicit initial combined-stage policy
- **THEN** four partial originals and four terminal corrections append atomically with current import timestamps, the same full-snapshot first acquisition/admission, exact category predecessors and the fixed refinement reason; only B supplies four current facts and no earlier import or acquisition is claimed

#### Scenario: Combined first-import counts and replay

- **GIVEN** initial A+B was accepted as two four-category cohorts, including when their quantities are equal
- **WHEN** result counts, A+B, A-only and B-only replay, store reopen and bundle recovery are checked
- **THEN** fact_count is four current selected categories, inserted_fact_count is eight history revisions on initial acceptance and corrected_fact_count is four predecessor-bearing revisions; later accepted replays add zero and C+B or C-only rejects atomically without summing historical quantities

#### Scenario: Both accepted stages replay after refinement

- **GIVEN** accepted partial A refined to terminal B
- **WHEN** A, B, A and B are imported again, including after store reopen or current-version bundle recovery
- **THEN** all imports return prior exact references with no downgrade or duplicates and unchanged first Evidence, acquisition and admission provenance

#### Scenario: Unsupported refinement cannot create historical acceptance

- **GIVEN** terminal-only first acceptance followed by an unseen partial, including a later combined snapshot containing that partial and known terminal B, a changed terminal vector, or partial A followed by a terminal snapshot without retained A
- **WHEN** that snapshot includes otherwise valid new facts
- **THEN** the entire batch rejects without any persistence or invented predecessor history

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

### Requirement: Exact Desktop 2.1.308 root terminal mapping

The reader SHALL additionally select the independently approved exact Desktop
2.1.308 profile through the existing public import operation. It SHALL preserve
2.1.215 corrections and finite Codex support without changing NativeUsage.

#### Scenario: Root terminal import and semantic replay

- **GIVEN** exact engine 2.1.308 and claude-desktop entrypoint on every assistant, isSidechain false, absent agentId, supported terminal reason and four present exact nonnegative integer quantities
- **WHEN** import and same-semantic replay through a different path/hash run, including reopened store and bundle recovery
- **THEN** four separate final facts are retained per event, literal zero is preserved, cache duration components are excluded, and original Evidence, acquisition, admission and timestamps survive replay

#### Scenario: Unsupported Desktop stages and quantities

- **GIVEN** a partial/null stop, child, missing/null/bool/negative counter, changed quantity, wrong producer, unknown key/type, malformed excluded row, predecessor or refinement reason
- **WHEN** the snapshot or portable bundle also contains valid new facts
- **THEN** the entire batch rejects without partial persistence or inherited 2.1.215 correction permission

#### Scenario: Closed Desktop exclusions

- **GIVEN** source rows use the approved per-type key subsets and required/absent members
- **WHEN** user, metadata and API blob exclusions are evaluated
- **THEN** user requires an object user-role message without immediate usage; metadata has no message or direct usage; API blobs have exactly hash/message/sessionId/type, opaque JSON message and no immediate message.usage if object; present-null usage rejects and no recursive accounting occurs

#### Scenario: Global identity and exact association

- **GIVEN** any of the seven recognized provider/surface/mapping/profile/proof claims from either approved mapping
- **WHEN** retained records are validated
- **THEN** exact evidence-profile policy applies and unknown, borrowed or mixed claims reject; Evidence ID equals event identity; cross-profile same-event conflicts reject atomically in either import order even for equal quantities, without including profile/version/path/hash in identity

#### Scenario: Separate authority remains unknown

- **GIVEN** accepted Desktop facts and external producer metadata association
- **WHEN** results are returned
- **THEN** backend finality, ownership, served model, complete coverage, money, demand and calibration are not granted; the external Desktop build is not runtime authenticated and broader Desktop lifecycle remains unsupported

#### Scenario: Consistent UTF-8 wire boundary and depth enforcement

- **GIVEN** a selected JSONL snapshot, including escaped quotes and nested ignored payloads
- **WHEN** the Claude reader parses each byte-delimited line
- **THEN** only UTF-8 text with an optional UTF-8 BOM is accepted; UTF-16/32 and malformed UTF-8 reject atomically, depth above 32 rejects, and valid U+2028/U+0085 characters inside strings do not create additional records

#### Scenario: Approved Desktop cost-state and mode exclusions

- **GIVEN** exact q4 approval and cost-state or mode rows within their closed top-level key upper bounds, with required type and absent message/direct usage
- **WHEN** import validates those metadata rows, including opaque modelUsage or cost values
- **THEN** they contribute no native facts, money, demand or inferred totals; unexpected keys and present-null message/usage reject the whole snapshot
