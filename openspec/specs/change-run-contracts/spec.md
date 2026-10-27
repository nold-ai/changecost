# change-run-contracts Specification

## Purpose
Change-level accounting needs stable identity and portable evidence before provider adapters exist. Explicit binding prevents coincidental timestamps from becoming financial attribution.

## Requirements

### Requirement: Explicit record lifecycle

The system SHALL register Changes and Runs through bind without hand-authored state,
record explicit outcomes through settle, and preserve immutable identities and
revisioned outcome provenance. Registration SHALL be idempotent for identical inputs
and atomic on conflict. New Runs SHALL require an open Change. Financial completeness
SHALL NOT be inferred from a terminal outcome.

#### Scenario: Register from an empty store

- **GIVEN** an empty local store and explicit repository/change identifiers
- **WHEN** bind registers the Change, then registers a namespaced Run against it
- **THEN** an open Change, one open Run and their explicit binding exist without a custom artifact or direct database edit.

#### Scenario: Registration replay and conflict

- **GIVEN** an existing registered Run and its Change
- **WHEN** registration is repeated with the same inputs, then attempted with conflicting immutable metadata
- **THEN** the repeat is a no-op preserving timestamps and outcomes, and the conflict fails without partial mutation.

#### Scenario: Record outcome without monetary evidence

- **GIVEN** an open Change with a failed Run and a later successful retry but no known charges
- **WHEN** settle records the Run outcomes and marks the Change accepted
- **THEN** both attempts remain recorded with explicit outcome provenance while costs remain unknown/provisional.

#### Scenario: Correct a terminal outcome explicitly

- **GIVEN** a Change recorded as accepted
- **WHEN** settle requests abandoned, first without and then with an explicit outcome-correction flag and reason
- **THEN** the first request fails unchanged and the second appends a dated outcome revision preserving the previous accepted declaration.

#### Scenario: Refuse new runs after termination

- **GIVEN** an accepted or abandoned Change
- **WHEN** bind attempts to register a new Run for it
- **THEN** registration fails atomically, while later evidence for already registered Runs remains importable.

### Requirement: Revisioned work intervals

Runs SHALL retain nullable actual-work start/end UTC bounds, provenance and interval
revisions. Registration MAY supply an observed start; settle SHALL allow explicit
bound updates independent of outcome. Known bounds SHALL obey start <= end and not
lie after declaration time. Missing bounds SHALL stay unknown. Changing known bounds
SHALL require an explicit reasoned correction; invalid updates SHALL be atomic.

#### Scenario: Delayed outcome does not extend work

- **GIVEN** a Run registered at 09:00, its 09:10–09:30 work bounds declared at 09:40, and its outcome entered at 11:00
- **WHEN** its work interval is inspected
- **THEN** the closed interval remains 09:10–09:30 with its declaration provenance, not 09:00–11:00.

#### Scenario: Missing end and invalid correction

- **GIVEN** a Run with only a known work start
- **WHEN** an end before that start is submitted together with a terminal outcome
- **THEN** the whole request fails unchanged; the end remains unknown and no outcome update is applied.

#### Scenario: Correct an interval explicitly

- **GIVEN** new attributed evidence before a known work start
- **WHEN** a corrected start is submitted with the interval-correction flag and reason
- **THEN** a new interval revision is appended and downstream coverage evaluation receives the new reference, preserving the original interval for earlier cutoffs without computing financial reconciliation in this change.

### Requirement: Store-local historical availability

Every record, revision and relationship SHALL retain immutable first-successful-commit
availability and local transaction ordering in its destination store separately from
origin provenance. Imports SHALL
NOT backdate local availability and identical reimports SHALL preserve it. Historical
selection SHALL require every selected dependency to be locally available by cutoff.
Imported Quotes SHALL retain origin context without claiming destination replay of
history that was unavailable there. A captured local cutoff SHALL include a committed
snapshot boundary; wall time alone SHALL NOT admit a transaction committed after
that boundary. Unprovable historical membership SHALL return replay_unavailable.

#### Scenario: Backdated portable evidence

- **GIVEN** December evidence, mappings, outcomes and settlement revisions first imported into a destination in February
- **WHEN** a January quote cutoff is evaluated there
- **THEN** the core eligibility check excludes all of them despite earlier origin recorded/effective times, and reimport does not change February availability; no quote algorithm is required.

#### Scenario: Imported quote cannot recreate unavailable history

- **GIVEN** a January Quote from another store imported with all its referenced records in February
- **WHEN** destination replay requests the Quote's original January cutoff
- **THEN** the stored Quote is inspectable but replay returns replay_unavailable rather than claiming its inputs were locally known in January.

### Requirement: Versioned registration features

The system SHALL capture immutable normalized features/v1 inputs at Change
registration, using the documented value domains and UTC capture/record timestamps.
Invalid values SHALL reject the registration atomically. Portable replay SHALL
preserve the original snapshot and track local import availability separately.

#### Scenario: Normalize and preserve feature inputs

- **GIVEN** change_shape=" BugFix ", trajectory="ITERATIVE" and a blank execution_profile
- **WHEN** a Change is registered and exported/imported
- **THEN** its features/v1 snapshot remains bugfix, iterative and null with original capture/record times and separately recorded destination availability.

#### Scenario: Reject invalid or revised features

- **GIVEN** a request with an unrecognized feature value or a re-registration changing an existing snapshot
- **WHEN** registration is validated
- **THEN** the request fails without writing or relabeling the Change.

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

### Requirement: Complete run references

The system SHALL resolve the full structured RunRef (repository_id, provider, surface,
run_id) for identity and every Run reference, including portable mappings, command
selectors, outcomes and settlement coverage. A typed Run RecordRef may name a
unique immutable Run record containing that full tuple; it SHALL NOT resolve a
bare provider run_id or infer a missing namespace. Bare or incomplete selectors SHALL fail
without mutation; source-evidence namespace SHALL NOT substitute for the target RunRef.

#### Scenario: Replay colliding raw run identifiers

- **GIVEN** Runs with the same raw run_id in different repositories, providers or surfaces and distinct explicit evidence mappings
- **WHEN** they are exported and imported twice into a fresh store
- **THEN** each Run and mapping retains its full identity without collisions or cross-attribution.

#### Scenario: Reject an incomplete run selector

- **GIVEN** two Runs share a raw run_id across surfaces
- **WHEN** bind or settle selects only that raw run_id
- **THEN** it rejects the incomplete reference without changing either Run or its mappings.

#### Scenario: Preserve an explicit mapping target namespace

- **GIVEN** a manual source-evidence mapping explicitly selects a RunRef whose surface differs from the evidence surface
- **WHEN** the mapping is replayed and that full RunRef receives an outcome update
- **THEN** both operations target only the named Run, retain manual provenance and do not derive a replacement namespace from the source.

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
- **THEN** at most one assignment commits; the loser reports a conflict or retryable busy error without partial writes. Retrying after the winner commits reports the conflict.

### Requirement: Strict portable input boundary

The system SHALL reject duplicate JSON members, unknown schema/kind/fields at any
level, nonfinite values, numeric or boolean economic amounts and timezone-naive
or numeric timestamps before committing records. Amounts SHALL be finite decimal
strings or null and preserve exact value/scale through storage and export. Identities
SHALL be nonblank and exact; only documented feature fields are normalized. Portable
input SHALL be treated as data and SHALL NOT execute URLs, paths or instructions.

#### Scenario: Duplicate and coercible input

- **GIVEN** an otherwise valid bundle containing a repeated amount key, a numeric amount, NaN, an unknown nested field or a naive timestamp
- **WHEN** each malformed variant is imported
- **THEN** it fails without persisting any record or silently selecting/coercing a value.

#### Scenario: Exact storage beyond floating precision

- **GIVEN** amount "0.12345678901234567890123456789" and an aware timestamp with a nonzero UTC offset
- **WHEN** the record is stored, the process restarts and the record is exported
- **THEN** the decimal value/scale is unchanged and the timestamp denotes the same instant in UTC.

#### Scenario: Preserve opaque identities

- **GIVEN** two valid identifiers that differ in case and another that is blank
- **WHEN** they are validated
- **THEN** the distinct identifiers remain distinct, while the blank identifier is rejected without guessing or trimming it into another identity.

### Requirement: Explicit offline portable operations

The system SHALL provide atomic local artifact import through bind and record
inspection/export through explain without adding a command family. Mutually
exclusive modes, incomplete selectors and unsupported operations SHALL fail clearly.
Help, version, invalid invocation and read-only inspection SHALL NOT initialize a
store. Export SHALL use a consistent committed snapshot and SHALL NOT overwrite an
existing output file or leave a partial final artifact after failure.

#### Scenario: Import and inspect without a provider

- **GIVEN** a synthetic v1 bundle containing a Change, an unbound Run, a source-evidence reference and explicit relationships in arbitrary order
- **WHEN** bind imports the bundle, explain inspects it and exports it, and a fresh store imports that export twice
- **THEN** all references resolve with exact identities/history, the repeat is a no-op and no provider, network or SpecFact runtime is used.

#### Scenario: Invalid operation is read-only

- **GIVEN** no local database
- **WHEN** help/version, conflicting registration/import modes, incomplete selectors or inspection of the missing store are requested
- **THEN** help/version succeed, invalid operations fail and no configuration/database/evidence files are created.

#### Scenario: Inspect revisions in predecessor order

- **GIVEN** a Change or Run with correction chains whose record IDs sort opposite to predecessor order and whose declaration timestamps are equal
- **WHEN** explain returns lifecycle and settlement history
- **THEN** each chain is grouped by record kind and ordered from its original declaration to its latest revision using previous references, without changing stored records.

#### Scenario: Export failure preserves data

- **GIVEN** an existing output file or a simulated output failure during export
- **WHEN** explain exports the store
- **THEN** the original file/database is unchanged and no partial final artifact is exposed.

### Requirement: Lifecycle and algorithm separation

Core lifecycle operations SHALL record explicit outcomes and work intervals without
computing settlements or quotes. Quote and Settlement records SHALL be structurally
validated and preserved, including their input references, unknown reasons and
scope; accepting imported claims SHALL NOT certify local financial completeness or
provider support. Bare settlement computation, quote and budget checks SHALL remain
non-success until their respective capabilities are delivered.

#### Scenario: Outcome-only settlement command

- **GIVEN** a registered Run with no imported financial evidence
- **WHEN** settle records its terminal outcome, then a computation-only settlement request is attempted
- **THEN** the outcome is persisted, its cost remains unknown, and the unimplemented computation fails explicitly.

#### Scenario: Imported claims retain their provenance

- **GIVEN** a structurally valid foreign Settlement or mapping labeled reconciled or verified_provider
- **WHEN** it is imported and inspected
- **THEN** its origin claim remains visible, but import does not approve the source profile, relabel manual evidence, or establish locally verified completeness.

### Requirement: Atomic reference and revision integrity

All portable references SHALL resolve within existing records or the same complete
bundle. Revisions SHALL preserve their subject and form an acyclic predecessor chain.
Conflicting duplicate identities, missing predecessors and cross-repository
run-to-change bindings SHALL reject the entire write. Identical retries SHALL
preserve original timestamps, revisions and first local availability, including
a retry after the original response was lost or the Change became terminal.

#### Scenario: Invalid revision graph

- **GIVEN** an artifact with a missing predecessor, cyclic correction references or a predecessor for a different subject
- **WHEN** it is imported
- **THEN** the complete write fails without adding records or consuming visible revision history.

#### Scenario: Replay after response loss and terminal outcome

- **GIVEN** a successful Run registration whose response was lost and a Change later marked accepted
- **WHEN** the identical registration is retried
- **THEN** the original record/binding is returned unchanged; a genuinely new Run against that terminal Change still fails.

#### Scenario: Cross-repository binding

- **GIVEN** a Run in repository A and a Change in repository B
- **WHEN** bind attempts the run-to-change relationship
- **THEN** it rejects the relationship atomically rather than attributing across repositories.

### Requirement: Historical visibility is committed and local

Historical eligibility SHALL require the locally committed snapshot boundary plus
all recorded/effective/availability constraints for every dependency. Origin
availability and transaction sequences SHALL NOT replace destination knowledge.
Unsafe backward-clock writes SHALL fail explicitly rather than backdate history.
A cutoff later than the current local snapshot SHALL be unavailable; it cannot
establish already-observed historical membership.

#### Scenario: Transaction spans a cutoff

- **GIVEN** a writer begins before a reader captures a cutoff but commits after that reader's snapshot
- **WHEN** the captured cutoff is replayed after commit
- **THEN** the new records are excluded despite a pre-cutoff transaction timestamp; a time-only cutoff without sufficient evidence returns replay_unavailable.

#### Scenario: Future cutoff cannot claim observed history

- **GIVEN** an imported Quote naming the destination store and an existing sequence but a cutoff later than the current snapshot
- **WHEN** explain evaluates inputs with future effective times
- **THEN** replay is unavailable and inspection leaves the store unchanged, even if those inputs would satisfy the claimed future time.

#### Scenario: Clock moves backwards

- **GIVEN** committed history whose local availability is later than the current wall clock
- **WHEN** a new historical write would backdate that history
- **THEN** it fails with a clock diagnostic and leaves the store unchanged.

### Requirement: Recoverable local persistence failures

Registration, bindings, imports, revisions and migrations SHALL commit all-or-nothing.
Busy/failed commits SHALL leave no partial writes and allow a safe retry. A newer
unsupported store schema SHALL fail without mutation; a failed migration SHALL
preserve the prior usable schema and data. A consistent database backup SHALL retain
store identity/history; portable import SHALL retain its distinct destination semantics.

#### Scenario: Commit and migration failure

- **GIVEN** an injected failure before commit or within a schema migration
- **WHEN** the operation is retried after reopening the store
- **THEN** no partial earlier operation exists, the prior schema/data remains usable, and a successful retry creates one result.

#### Scenario: Future schema and backup recovery

- **GIVEN** a store with a newer unsupported schema and a separate compatible consistent backup
- **WHEN** the newer store is opened, then the backup is restored to a separate path
- **THEN** opening the newer store fails unchanged, while the backup retains its original store identity and historical availability.

### Requirement: Allowlisted private data handling

Portable records SHALL retain only the declared economic/identity/provenance fields.
Prompt text, transcripts, credentials and raw provider payloads SHALL be rejected,
not silently retained in extras, logs or validation diagnostics. Distributions SHALL
continue to exclude local databases, exported evidence and review artifacts.

#### Scenario: Sensitive unknown field

- **GIVEN** a synthetic secret or prompt sentinel in an undeclared nested field
- **WHEN** import fails validation and package archives are inspected
- **THEN** neither stored records, diagnostics nor package contents contain that sentinel; the error identifies the validation boundary without echoing untrusted field names or values.

#### Scenario: Copied model fails revalidation without warning disclosure

- **GIVEN** a copied bundle, record or Run reference containing a wrong-typed private sentinel
- **WHEN** a public import or write boundary serializes it for strict revalidation
- **THEN** rejection emits neither serializer warnings nor sentinel-bearing public diagnostics, and leaves fresh or existing stores unchanged.

### Requirement: Portable sequence storage range

Observation sequences SHALL be strict integers from 1 through 2**63−1; Cutoff
sequences, including bundle sources and embedded Quote cutoffs, SHALL be strict
integers from 0 through 2**63−1. Revalidation before import SHALL reject values
outside that range without publishing a fresh store or changing an existing store.
Local allocation beyond the maximum SHALL raise a controlled contract error before
inserting new records. A retry or observation-only import requiring no new local
sequence SHALL remain valid at the maximum. JSON-only ordinals and sample counts
do not acquire this SQLite storage bound.

#### Scenario: Oversized portable sequence
- **GIVEN** an artifact or copied model with sequence 2**63 or 2**100
- **WHEN** imported through the library or CLI
- **THEN** validation fails, the CLI exits 2 without traceback/payload echo, and no store changes are published.

#### Scenario: Last local transaction sequence
- **GIVEN** a store at sequence 2**63−2
- **WHEN** a new record is committed
- **THEN** its sequence is exactly 2**63−1; a subsequent new record is rejected atomically, while identical retries and observation-only imports remain valid.

### Requirement: Unreleased economic record extensions

The evolving internal changecost/v1 contract SHALL represent economic evidence,
source-coverage assertions and computed settlements as distinct known record kinds
within the unreleased 0.x product. It SHALL retain explicit identities, exact amount
strings, provenance and destination-local availability. Existing identity-only
Evidence and imported Settlement records SHALL NOT gain fabricated economic or
completeness values. Unknown record kinds, fields and versions SHALL still reject
atomically. No published-product compatibility guarantee is implied by the label.

#### Scenario: Existing and new records in one artifact

- **GIVEN** existing Change/Run/evidence identities plus known economic, coverage and computed-settlement records using the current internal schema
- **WHEN** a compatible checkout exports and imports them twice in arbitrary reference order
- **THEN** exact values, all reference relationships and revision history survive with destination-local availability and no duplicate records.

#### Scenario: Preserve minimal imported claims

- **GIVEN** an identity-only Evidence record and a minimal imported Settlement from the earlier checkout
- **WHEN** a checkout with reconciliation reads their known fields
- **THEN** missing economics remain unknown and the Settlement remains an origin claim, without fabricated cutoff, full-change membership or local computation status.

#### Scenario: Strict rejection remains in force

- **GIVEN** an artifact with an unknown version, record kind or nested field
- **WHEN** import is attempted
- **THEN** it fails without partial records or a published fresh store, using safe diagnostics instead of silently accepting an unsupported schema.

### Requirement: Portable computation provenance and local authority

Computed settlement records SHALL preserve operation identity, input cutoff,
algorithm/policy versions, requested economic/window scope, subtotals, unknowns,
complete Run membership, supporting/excluded inputs and predecessor references.
Economic records SHALL reference their stable core Evidence identity and component
key. Coverage assertions SHALL retain their exact source/economic/window scope.
All present RecordRefs SHALL resolve with correct kinds/subjects in the same atomic
graph; unresolved correction source locators SHALL remain distinct typed data.
Local computation authority SHALL depend on a locally committed receipt, never a
portable producer label or claimed origin store ID.

#### Scenario: Replay does not create local verification

- **GIVEN** a foreign computed settlement with a producer-asserted local origin ID and complete-looking coverage metadata
- **WHEN** its artifact is imported
- **THEN** provenance stays inspectable but import does not mint a local computation receipt, certify coverage or make unavailable historical inputs locally eligible.

#### Scenario: Invalid computation dependency

- **GIVEN** an artifact with a computed result referring to another Change's outcome, an absent core Evidence record or a forked computed predecessor chain
- **WHEN** the combined graph is validated
- **THEN** the batch is rejected atomically while a well-typed unresolved source correction locator alone does not relax core reference validation.

### Requirement: Safe incompatible preview store handling

A checkout SHALL distinguish the internal SQLite layout from product and artifact
version labels. An unsupported internal layout SHALL fail unchanged with a
controlled diagnostic; help, invalid commands and read-only inspection SHALL NOT
silently upgrade, downgrade or recreate it. Backup with the matching checkout SHALL
preserve local history. Portable import into a separate supported fresh store SHALL
establish new destination history and SHALL NOT claim original-cutoff replay.

#### Scenario: Earlier development store is preserved

- **GIVEN** a store using a layout unsupported by the current preview checkout
- **WHEN** an operation tries to open it
- **THEN** it fails without changing the file and identifies the need for a matching checkout or explicit recovery, without an automatic migration or data deletion.

#### Scenario: Recovery without invented history

- **GIVEN** a consistent original-store backup and an artifact exported by its matching checkout
- **WHEN** the artifact is imported into a separate fresh store supported by a later preview checkout
- **THEN** source identities and claims remain but destination availability is new; the original backup and checkout remain the path for original local-history recovery.

### Requirement: Portable diagnostic native usage

The local core SHALL preserve approved-reader native usage as a strict additive portable NativeUsage record linked to Evidence. It SHALL retain exact source profile and mapping identity, producer version, first-acquisition snapshot digest, opaque native identity, reported model/version, source quantity category and accounting scope, nullable quantity/interval/lineage/finality and explicit immutable correction provenance. These source facts SHALL NOT confer demand or financial authority. Source totals and categories with unverified inclusion SHALL remain distinct; source quantity categories SHALL NOT be constrained to demand component categories.

#### Scenario: Unbound quantity roundtrip

- **GIVEN** approved-reader usage with no Run binding and a reported total category
- **WHEN** it is stored, exported and imported into another current-version store
- **THEN** its exact quantity, category, provenance and unknown fields survive without a fabricated economic component, assessment or demand observation

#### Scenario: Missing, zero and unknown inclusion

- **GIVEN** an absent quantity, an explicit zero and overlapping input/cache/reasoning/total source categories
- **WHEN** native source facts are validated and replayed
- **THEN** absence differs from zero, categories remain separately identified and no sum or equivalence is inferred from their presence

### Requirement: Atomic native identity and correction history

Native import SHALL append Evidence and NativeUsage together through the existing store transaction. Approved semantic identity SHALL be independent of filename, batch label, file ordinal and subsequent acquisition digest. Exact semantic replay SHALL return existing references without adding quantity or rewriting first-acquisition provenance. Changed semantics under the same identity SHALL reject the entire import. A separately identified correction SHALL retain its predecessor and reason and reject forks/cycles; reset or changed-window meaning SHALL require explicit approved source policy. Missing approved stable identity SHALL reject numeric import rather than silently adopt file order as event identity.

#### Scenario: Same event in a later snapshot

- **GIVEN** one approved native event already imported and a later separately approved and admitted snapshot containing the same event plus additional bytes
- **WHEN** its semantic identity and values match
- **THEN** replay returns the original references and first-acquisition digest, contributes no duplicate quantity and does not conflict merely because the new snapshot hash differs

#### Scenario: Conflicting batch and immutable correction

- **GIVEN** a batch containing one new event and one conflicting existing identity
- **WHEN** native import is attempted
- **THEN** neither event persists, whereas a separately approved correction with a new revision identity retains auditable predecessor/reason and never rewrites prior facts

#### Scenario: Portability and rollback boundary

- **GIVEN** existing records without NativeUsage and a current-version store containing the additive kind
- **WHEN** current code reads old bundles or exports the new records for recovery
- **THEN** old records retain their behavior and new native provenance survives current-version roundtrip, while documentation discloses that older binaries can reject the new kind and rollback preserves backups/history

#### Scenario: Admission provenance does not mint duplicate usage

- **GIVEN** an existing response event and equal canonical facts replayed through a later approved admission
- **WHEN** profile, proof or acquisition digests differ
- **THEN** existing references, first source/admission digests and availability remain immutable; producer or lineage changes under the same key reject atomically

#### Scenario: Native repository and event consistency

- **GIVEN** native facts share an original event across source categories or a later exact manual Evidence binding
- **WHEN** a portable fact changes that event's producer or reported lineage, or binds its repository to a Run in another repository
- **THEN** the entire transaction rejects without minting a profile-dependent duplicate event or changing original availability
