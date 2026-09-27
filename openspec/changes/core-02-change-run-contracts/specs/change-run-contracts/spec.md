# Define change, run, quote and settlement contracts

## Purpose

Change-level accounting needs stable identity and portable evidence before provider adapters exist. Explicit binding prevents coincidental timestamps from becoming financial attribution.

## ADDED Requirements

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
- **THEN** a new interval revision is appended and coverage is reevaluated, preserving the original interval for earlier cutoffs.

### Requirement: Store-local historical availability

Every record, revision and relationship SHALL retain immutable first-successful-commit
availability in its destination store separately from origin provenance. Imports SHALL
NOT backdate local availability and identical reimports SHALL preserve it. Historical
selection SHALL require every selected dependency to be locally available by cutoff.
Imported Quotes SHALL retain origin context without claiming destination replay of
history that was unavailable there.

#### Scenario: Backdated portable evidence

- **GIVEN** December evidence, mappings, outcomes and settlement revisions first imported into a destination in February
- **WHEN** a January quote cutoff is evaluated there
- **THEN** none is eligible despite earlier origin recorded/effective times, and reimport does not change February availability.

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

The system SHALL use the full structured RunRef (repository_id, provider, surface,
run_id) for identity and every Run reference, including portable mappings, command
selectors, outcomes and settlement coverage. Bare or incomplete selectors SHALL fail
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
- **THEN** only one valid binding exists and the other reports a conflict.
