# Verify personal-account source feasibility

## Purpose

Personal IDE and CLI accounts may expose usage without billable money or stable session joins. Establishing the accessible evidence prevents the pilot from promising Enterprise-only reconciliation.

## ADDED Requirements

### Requirement: Capability evidence matrix

The feasibility report SHALL distinguish documented availability from inspected personal-account evidence for each supported surface.
It SHALL cover Copilot IDE/CLI, personal Cursor, Codex CLI/app/IDE and Claude Code
CLI/IDE separately, recording installed or unknown versions and account regimes.

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

#### Scenario: Codex usage without billed cost

- **GIVEN** documented Codex usage events or a generated interface schema but no inspected account export
- **WHEN** token import and cash settlement are assessed
- **THEN** both observed capabilities remain unverified and token fields or quota percentages are not interpreted as billed money.

#### Scenario: Claude Code cost estimate

- **GIVEN** a Claude Code metric labeled as estimated USD and no billing evidence
- **WHEN** economic capability is assessed
- **THEN** the estimate remains distinct from a billed charge, including for subscription accounts.

#### Scenario: Repeated cumulative metrics

- **GIVEN** repeated usage snapshots or metric points with cumulative temporality
- **WHEN** feasibility of aggregation is assessed
- **THEN** the report requires identity, interval and reset evidence before additive totals and does not sum repeated snapshots or last values with encompassing totals.

#### Scenario: Installed CLI differs from recorded runtime

- **GIVEN** a local artifact records a different runtime version or envelope from the installed CLI's schema
- **WHEN** source compatibility is assessed
- **THEN** the profiles remain separate, extra usage categories are recorded without guessed conversion, and installed help does not certify the other runtime.

#### Scenario: Repeated messages with changing usage

- **GIVEN** distinct local record IDs repeat one request/message ID with equal or changed usage
- **WHEN** aggregation feasibility is assessed
- **THEN** the report records partial identity evidence, rejects per-record summation, and requires finality or revision evidence before choosing a total.

#### Scenario: Cursor context with empty usage counters

- **GIVEN** an inspected local Cursor conversation has nonzero context occupancy, empty usage data and zero message token counters
- **WHEN** usage and billing feasibility are assessed
- **THEN** context occupancy stays separate from consumed tokens, zero counters do not establish zero usage or cost, and a persisted completion flag does not prove session finality.

#### Scenario: Hosted Copilot identity and usage projections

- **GIVEN** a VS Code Agent Host session explicitly maps to a distinct SDK session, with turn usage and a durable usage checkpoint
- **WHEN** attribution and aggregation are assessed
- **THEN** the host and SDK identities stay distinct but linked, ephemeral-event absence is not zero usage, overlapping direct/aggregate totals are not added, and disagreeing session totals require finality evidence before settlement.

#### Scenario: Enterprise projections with withheld evidence

- **GIVEN** Enterprise-tier evidence consists of analyst projections with removed IDs, rebased times, truncated groups or synthetic quantities
- **WHEN** schema compatibility and attribution are assessed
- **THEN** the report distinguishes original field claims from transformed sample types, limits checks to preserved relationships, and does not infer native wire compatibility, cross-session timing or production consumption.

#### Scenario: Absence in a different source container

- **GIVEN** a session catalog or narrative checkpoint table lacks usage fields while the SDK event stream or per-session usage database was not inspected
- **WHEN** usage availability is assessed
- **THEN** absence remains scoped to the inspected container, with SDK usage and finality unverified rather than absent or zero.

#### Scenario: Custom session-log hook with disabled OTel

- **GIVEN** the maintainer reports OTel disabled and a custom hook parsing session logs and uploading converted fields without an Admin API call
- **WHEN** source feasibility is assessed
- **THEN** disabled collection is recorded separately from provider capability, native log fields are distinguished from hook transformations and receiver output, and classifier provenance, amount units, coverage and session binding require inspected evidence without requiring OTel enablement.

### Requirement: Safe reproducible fixtures

The evidence package SHALL provide synthetic or fully redacted fixtures with provenance and transformation notes without prompts, secrets or identifiable account data.

#### Scenario: Reviewable fixture

- **GIVEN** a proposed source fixture
- **WHEN** its inclusion is reviewed
- **THEN** the reviewer can verify documented shape and preserved joins while content and real identifiers are absent.

#### Scenario: Positive message counters without accounting boundaries

- **GIVEN** a producer reports integer message-token paths but shares only synthetic values and no stable identity or complete accounting interval
- **WHEN** the source profile is assessed
- **THEN** field/type evidence is partial, while cache inclusion, repeat semantics, session totals and billed money remain unverified; positive values do not establish an additive usage ledger.

#### Scenario: Documentation-derived examples with encoding discrepancies

- **GIVEN** a regenerated bundle includes synthetic OTLP-shaped JSON, normalized usage objects or candidate CSV headers
- **WHEN** fixture admission is reviewed
- **THEN** arithmetic and identity checks are reported separately from official encoding/schema checks, concrete mismatches are recorded without altering received bytes, and synthetic joins or amounts do not verify the custom hook or native export compatibility.

### Requirement: Canonical profile register and honest approval

The closeout SHALL maintain versioned per-surface profiles with acquisition routes,
versions/tier, dated citations, opaque evidence identity/hash, capability dispositions,
verified field meanings and exact unresolved evidence. A deterministic compact
matrix SHALL derive from the register. Validation SHALL NOT infer approval from
synthetic, producer-reported or documentation-only evidence. Approved capabilities
SHALL reference inspected native evidence and a named independent semantic review;
structural inspection alone SHALL NOT establish accounting finality or completeness.
The semantic attestation SHALL bind the exact profile/version/capability and evidence
SHA-256, with explicit authority, interval, replay/reset/correction and exclusion
decisions. This contributor attestation is not independent authentication of facts.

#### Scenario: Stale matrix or fabricated approval

- **GIVEN** a changed profile with an unchanged matrix, or approval citing synthetic evidence
- **WHEN** the research checker runs
- **THEN** it rejects the stale matrix or unsupported approval with safe diagnostics.

#### Scenario: Useful partial delivery without native evidence

- **GIVEN** passing tooling tests but missing intended Copilot/Cursor native source evidence
- **WHEN** completion is assessed
- **THEN** the report retains exact blockers, profile approval and issue #9 remain incomplete.

### Requirement: Bounded private offline source inspection

The development-only inspector SHALL accept explicit registered profiles and
sanitation field paths for JSON, JSONL and CSV evidence using a local manifest.
It SHALL verify SHA-256 before parsing, reject malformed UTF-8, duplicate JSON
members/CSV headers, unsupported formats/profiles, non-finite numbers, symlinks,
files over 10 MiB, over 10,000 records or nesting over 32. Original bytes SHALL
remain unchanged. Public diagnostics/reports SHALL contain safe evidence IDs,
hashes, counts, types and location codes without raw paths, field names, identifiers,
payload values or exception messages. Inspection SHALL be offline and read-only. Limits SHALL apply to manifests/registers
and actual bytes captured from the same non-symlink regular file descriptor used
for hashing and parsing. Caller-controlled metadata SHALL not bypass output privacy.

#### Scenario: Malformed or changed private evidence

- **GIVEN** bad bytes, changed hashes, duplicate members/headers or excessive input
- **WHEN** inspection runs
- **THEN** it rejects safely, preserves source bytes and emits no private data.

#### Scenario: Allowlisted metadata summary

- **GIVEN** a native file with declared allowlisted metadata plus private undeclared content
- **WHEN** a local explicit-profile inspection runs
- **THEN** only permitted field types/counts and opaque provenance appear, with no semantic approval.

#### Scenario: Retained public reports preserve registered opaque provenance

- **GIVEN** explicit registered opaque profile/evidence references, including distinct
  evidence references sharing bytes or the same evidence label in different profiles
- **WHEN** inspections are reordered, replayed or retained separately from the private manifest
- **THEN** each public report preserves its validated registered profile/evidence pair
- **AND** failures after reference validation retain that safe reference with a fixed error code
- **AND** unknown, ambiguous or unsafe reference labels fail with redacted fixed diagnostics
- **AND** caller labels, native source identifiers, paths, field names and payloads remain private
- **AND** report provenance does not establish semantic approval or finality.

### Requirement: Independent executable research conclusions

All eighteen existing research cases SHALL have computed semantic conclusions
independent of their declared expectations. Checks SHALL preserve exact units,
Decimal amounts, missing/zero distinctions, duplicate/cumulative/replacement
relationships, identity scopes, ephemeral/durable boundaries and synthetic/native
provenance. Faulty/repaired controls SHALL demonstrate actual detection without
changing the evaluator to fit an expected result.

#### Scenario: Overcounted replay or fabricated money

- **GIVEN** replayed roots, overlapping totals, cumulative points, replacements or a multiplier
- **WHEN** semantic checks run against a false additive or monetary expectation
- **THEN** they reject the wrong claim and pass the repaired expectation from unchanged inputs.

#### Scenario: Uncertain source boundary

- **GIVEN** context occupancy, conflicting checkpoint totals, missing identities, absent containers or rebased projections
- **WHEN** semantic conclusions are computed
- **THEN** consumption, finality, joins and native compatibility remain explicitly unknown where evidence cannot establish them.

#### Scenario: Checkpoint progress versus identity conflict

- **GIVEN** cumulative SDK checkpoints with an explicit SDK session scope and event identity
- **WHEN** totals change across distinct event identities or repeat identically under one identity
- **THEN** those checkpoints do not establish a conflict; different totals under the same session/event identity do establish a conflict, and missing identity leaves the conflict assessment unresolved.
- **AND** totals remain non-additive and final session consumption remains unknown. Synthetic per-record scope metadata is distinct from native wire fields and cannot establish provider support.

#### Scenario: Invalid replacement revision or cumulative interval

- **GIVEN** a boolean/noninteger replacement revision or malformed, timezone-free, reversed cumulative interval
- **WHEN** synthetic conclusions are computed
- **THEN** invalid revision types reject safely and invalid intervals leave the estimate unresolved; valid offset timestamps are ordered by their UTC instants, with normalized starts and conflicting equal endpoints handled explicitly.

#### Scenario: Absent checkpoint evidence and conflict precedence

- **GIVEN** no checkpoint records, or a checkpoint missing its amount or namespaced identity
- **WHEN** checkpoint conflicts are assessed
- **THEN** absence or incomplete evidence leaves the conclusion unresolved unless a demonstrated same-session/event amount conflict exists; finality remains unknown and totals remain non-additive.

#### Scenario: Complete exact identities before affirmative scope

- **GIVEN** root conversation/span, snapshot thread/turn, rollout session/version or hosted host/SDK identities
- **WHEN** an affirmative identity-dependent total or distinct-namespace claim is computed
- **THEN** every required identity is a nonblank string, including Unicode whitespace checks; missing/null/nonstring identities leave totals or scope claims unavailable. Exact valid strings remain distinct without trimming or normalization.

#### Scenario: Complete correction economic and revision identity

- **GIVEN** synthetic correction revisions with event, currency and billing basis labels
- **WHEN** current amount is selected
- **THEN** every label is a nonblank string and the exact (event, currency, billing basis) key is stable; missing or mixed economic bases remain unresolved. Mandatory revisions and supplied replacement references are present exact nonnegative integers excluding booleans, nulls and coerced values. Replay/history and precise amounts remain unchanged; no billed money or native support is inferred.

#### Scenario: Per-record quantity validation before replay collapse

- **GIVEN** snapshot or rollout totals containing integer/boolean or integer/equal-float aliases in either order
- **WHEN** unique quantity/replay conclusions are computed
- **THEN** every individual total is checked against the existing exact nonnegative integer rule before grouping; malformed types reject, missing quantities remain unknown, exact zero and valid replay stay distinct from missing, and conflicting valid integers remain unresolved.

#### Scenario: Observed rows versus correlated message identities

- **GIVEN** Claude records with missing or malformed record/request/message identifiers, including partially valid rows
- **WHEN** request/message correlation counts are computed
- **THEN** those identity counts remain unresolved; physical row count and observed usage-variant count retain their structural meaning. Exact complete labels and stable record-to-request/message mapping support known distinct counts; conflicting mapping under one record identity stays unresolved. Finality/additive/native support remain unknown.

#### Scenario: Complete cumulative metric series identity

- **GIVEN** cumulative cost points with absent, blank, nonstring or Boolean/integer-aliased metric labels
- **WHEN** accounting series keys are grouped
- **THEN** metric identity is an exact nonblank string before grouping; invalid or mixed exact identities leave the estimate unresolved
- **AND** original exact strings, Decimal quantity validation, UTC ordering/reset/conflict precedence and native approval boundaries remain unchanged.

#### Scenario: Projection fields do not demonstrate billing corrections

- **GIVEN** unsupported Enterprise projection rows with positive-looking replacement references, amounts or producer claims
- **WHEN** synthetic conclusions are computed
- **THEN** billing correction remains not demonstrated, native compatibility is false, and consumption, money and profile approval remain unverified.

#### Scenario: Retained revision count requires a complete single scope

- **GIVEN** correction rows with mixed or incomplete event/currency/billing-basis scopes
- **WHEN** current amount and retained revision count are computed
- **THEN** both remain unresolved rather than deduplicating unrelated events by bare revision
- **AND** complete same-scope history retains distinct revisions through replay, including when conflicts make current amount unavailable.

#### Scenario: Single-record token sample cannot hide additional quantities

- **GIVEN** the tokens-only sample has a second record, including an identical replay, conflicting quantities or malformed trailing quantities
- **WHEN** its explicitly selected single-record strategy evaluates evidence
- **THEN** it rejects the sample rather than returning the first record's quantities; other explicitly selected multi-record token boundary strategies remain unchanged.

#### Scenario: Partial capabilities retain evidence details

- **GIVEN** a profile declares any partial capability
- **WHEN** its verified field meanings or unresolved requirements are empty or malformed
- **THEN** the register rejects that profile; valid nonempty details remain required for partial claims, without requiring unresolved requirements on a fully resolved profile.

#### Scenario: Register details follow every capability disposition

- **GIVEN** any combination of supported, partial, unverified and unavailable capabilities
- **WHEN** the canonical register is validated, loaded or rendered as a matrix
- **THEN** any supported or partial capability requires nonempty valid verified field meanings, and any partial or unverified capability requires nonempty valid unresolved requirements; an entirely unavailable profile may leave both empty, and a fully resolved supported profile may leave requirements empty while retaining verified fields and independent native approval bindings.

#### Scenario: Timestamp normalization respects representable UTC bounds

- **GIVEN** a syntactically valid timezone-aware interval endpoint overflows during UTC normalization
- **WHEN** the cumulative evidence is evaluated
- **THEN** its interval remains unresolved through the existing safe result, preserving representable timestamps, reset/conflict semantics and Decimal validation precedence.

#### Scenario: Malformed nested case containers use safe diagnostics

- **GIVEN** a research record has a nested container of the wrong type
- **WHEN** any selected detector accesses that malformed shape
- **THEN** structural rejection uses the fixed case-shape/case-invalid diagnostic without a traceback or payload, while repaired originals and deliberate missing-evidence uncertainty remain unchanged.

#### Scenario: CSV fields share the advertised input byte bound

- **GIVEN** a valid CSV field or header exceeds the Python reader default but the received file remains within10MiB
- **WHEN** bounded inspection parses it
- **THEN** it permits the field up to the existing input bound and restores the prior parser field limit after success or failure; total-byte, row-width, duplicate-header and privacy guards remain enforced.

#### Scenario: Hosted checkpoint conclusions are a strategy obligation

- **GIVEN** the hosted strategy computes a checkpoint conflict or unresolved checkpoint identity/amount from a research bundle
- **WHEN** the bundle checker assesses semantic acceptance
- **THEN** it requires the computed checkpoint_conflict to be exactly false independently of declared fixture expectations, rejects true or unknown through a fixed conclusion diagnostic, and preserves the immutable historical fixture and all native finality/approval boundaries.
- **AND** exact replay and distinct identified progression remain conflict-free while a known conflict retains precedence over incomplete checkpoint evidence.

#### Scenario: Fixture expectation metadata rejects non-mapping shapes

- **GIVEN** research fixture expectations are a list, string, scalar or null, including a list of all required conclusion names
- **WHEN** the research checker validates the fixture
- **THEN** it rejects with the fixed case-invalid diagnostic before key coverage or mapping iteration, without traceback or payload disclosure. Valid mapping key coverage and exact value types retain their existing checks; repaired original fixtures pass unchanged.
