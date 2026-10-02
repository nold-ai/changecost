# Extend internal contracts for unreleased reconciliation

## ADDED Requirements

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
