# Native usage portability

## ADDED Requirements

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
