# Reconcile evidence into revisioned settlements

## Purpose

Retries and duplicate exports can inflate spend while missing charges can hide it. Reconciliation must preserve unknowns and corrections before provider-specific data enters the model.

## ADDED Requirements

### Requirement: Idempotent evidence and real retries

The reconciler SHALL ignore exact duplicate evidence while retaining distinct retry events.

#### Scenario: Duplicate versus retry

- **GIVEN** two copies of event A at USD 0.10 and distinct retry B at USD 0.20
- **WHEN** settlement runs
- **THEN** known billed USD is 0.30 with A counted once and B retained.

#### Scenario: Conflicting duplicate

- **GIVEN** one stable event key with two different amounts and no correction link
- **WHEN** the second record is imported
- **THEN** it is rejected as a conflict without silently choosing an amount.

### Requirement: Revisioned corrections

The reconciler SHALL retain prior settlement revisions and apply identifiable corrections exactly once.

#### Scenario: Corrected charge

- **GIVEN** a USD 0.40 billed event and a documented replacement USD 0.25 correction
- **WHEN** the correction is imported twice
- **THEN** the new amount is 0.25, not 0.65 or 0.10, and the previous revision remains inspectable.

#### Scenario: Correction arrives first

- **GIVEN** a correction targeting absent evidence
- **WHEN** settlement runs
- **THEN** it stays pending and completeness reports the unresolved target.

### Requirement: Honest economic completeness

Settlements SHALL separate incompatible units and unknown amounts and SHALL NOT add cumulative snapshots to event deltas.

#### Scenario: Mixed evidence

- **GIVEN** USD billed 1.00, 2 credits and an unknown charge
- **WHEN** settlement runs
- **THEN** separate USD and credit components appear, unknown count is one, and no grand money total is fabricated.

#### Scenario: Snapshot and deltas

- **GIVEN** a cumulative series and its underlying events
- **WHEN** the source has no verified precedence rule
- **THEN** the result is incomplete and the two lanes are not summed.

### Requirement: Auditable full-change coverage

Settlements SHALL distinguish reconciled source intervals from full-change coverage.
Full-change eligibility SHALL require a terminal Change with at least one Run, all
linked Runs terminal and complete supported coverage of their entire work intervals
for the requested economic identity. Coverage SHALL retain full RunRefs, linked-Run
membership, outcome revisions, source profiles, intervals and evidence references.
Missing or ambiguous coverage SHALL remain unknown, never inferred zero. Relevant
new evidence or bindings SHALL require a new coverage revision.

#### Scenario: Reconciled interval omits an attempt

- **GIVEN** a terminal Change with two Runs and a reconciled interval covering only the first
- **WHEN** full-change completeness is evaluated
- **THEN** the scoped subtotal remains available but full-change coverage is incomplete with the omitted Run identified.

#### Scenario: Terminal change with an open run

- **GIVEN** an accepted Change with a linked Run still open and some known charges
- **WHEN** full-change completeness is evaluated
- **THEN** it remains incomplete regardless of the Change outcome or the known subtotal.

#### Scenario: Missing evidence versus observed zero

- **GIVEN** one terminal Run lacks economic evidence while another has supported zero evidence covering its full work interval and requested unit
- **WHEN** their coverage is evaluated
- **THEN** the first stays unknown and only the second contributes an observed zero; a zero-run Change is ineligible rather than free.

#### Scenario: Evidence contradicts declared work bounds

- **GIVEN** a Run declared to end at 09:30 and attributed work evidence at 09:45
- **WHEN** full-change coverage is evaluated
- **THEN** it is incomplete until an explicit interval or audited attribution correction resolves the conflict, regardless of a reconciled source interval.

#### Scenario: Re-evaluate late coverage changes

- **GIVEN** a previously complete revision followed by a newly linked existing Run or unresolved late correction
- **WHEN** settlement is recomputed at the later cutoff
- **THEN** a new revision is incomplete until the additional coverage or correction is resolved, while replay at the earlier cutoff retains its original revision.

### Requirement: Outcomes and unbound remainder

Settlements SHALL preserve all linked retry and abandoned expenditure and expose unbound evidence separately.

#### Scenario: Accepted after retries

- **GIVEN** an accepted change with two failed runs and one successful run
- **WHEN** it is settled
- **THEN** all three known expenditures are included.

#### Scenario: Unbound abandoned evidence

- **GIVEN** an abandoned bound run and one ambiguous unbound event
- **WHEN** repository totals are requested
- **THEN** abandoned spend is retained and the ambiguous event remains outside change totals.

### Requirement: Strict normalized economic input

The reconciler SHALL accept a versioned, allowlisted local normalized evidence input
with explicit repository/source scope, stable evidence identity, one exact economic
component, temporal lane/interval and correction semantics. It SHALL retain source
provenance without raw payloads and reject unknown fields, nonfinite/coercible
amounts, invalid timestamps and conflicting scope atomically. Normalized input is
not a provider parser or an approval of the named source profile.

#### Scenario: Identity without an economic value

- **GIVEN** a stored Core-02 evidence identity with no economic payload
- **WHEN** settlement computes its repository scope
- **THEN** that identity is not treated as an observed zero and completeness explains the missing economic evidence.

#### Scenario: Safe failed import

- **GIVEN** a batch with a valid event and another containing an unknown nested field with a private sentinel or a numeric amount
- **WHEN** normalized import validates the complete batch
- **THEN** it fails without partial records or a newly published store, and diagnostics do not echo the sentinel.

### Requirement: Semantic source identity and deduplication limits

Normalized import SHALL resolve stable source identities before persistence, retain
first successful availability, and ignore transport order or local ingest metadata
when comparing the economic semantics of a repeat. Distinct retry identities SHALL
remain distinct. File-scoped identity SHALL guarantee only exact-file/row replay;
ambiguous overlap across files SHALL remain unresolved, never silently additive.
All references and original committed identities SHALL remain consistent on replay.

#### Scenario: Re-export with different transport metadata

- **GIVEN** the same namespaced event and semantic payload in two normalized batches with different batch IDs and input order
- **WHEN** both are imported
- **THEN** one economic event and its stable binding target remain, with original stored provenance and availability unchanged.

#### Scenario: Overlapping file identities

- **GIVEN** two different file digests whose rows may cover the same source event without a stable cross-file identity
- **WHEN** settlement evaluates the overlapping source scope
- **THEN** the ambiguous partition is excluded from the unambiguous subtotal with a dedupe-limited reason, and cannot establish reconciled or full-change coverage.

### Requirement: Pending correction resolution without broken references

A missing correction target SHALL be retained as a typed source locator rather
than a dangling portable record reference. Only a unique, valid replacement chain
within one source/economic identity SHALL affect an aggregate. Resolved cycles,
forks, incompatible targets and changes to known economic identity SHALL reject the incoming
batch atomically. Pending or otherwise unresolved chains SHALL be disclosed and
excluded from the unambiguous subtotal. Core record-reference validation SHALL
remain strict.

#### Scenario: Target becomes available later

- **GIVEN** a replacement for source event A persisted before A and a captured earlier cutoff
- **WHEN** A later arrives and settlement is recomputed
- **THEN** the later revision counts the replacement once, the earlier replay remains pending, and no core record reference was allowed to dangle.

#### Scenario: Ambiguous correction graph

- **GIVEN** an existing replacement of A and a batch introducing a second successor, a cycle, or a target in a different economic identity
- **WHEN** import validates the combined resolved source graph
- **THEN** the batch fails without replacing prior records or choosing a winner by arrival time.

#### Scenario: Explicit reversal

- **GIVEN** a billed USD 0.40 event and a documented replacement-zero reversal in the same source/economic identity
- **WHEN** both are settled and the reversal is replayed
- **THEN** the effective amount is exactly zero, the original remains inspectable, and no negative-delta interpretation or double application occurs.

### Requirement: Authoritative temporal lanes

Each selected source series SHALL use one locally supported authoritative lane.
Cumulative values SHALL NOT be summed across snapshots or added to their underlying
event deltas. A snapshot SHALL represent only its proven baseline/reset and covered
attribution/window. Missing baselines, unexplained resets, overlap, gaps or mixed
attribution SHALL remain unresolved. The pilot SHALL NOT interpolate, prorate or
infer a snapshot difference to manufacture a complete interval.

#### Scenario: Supported snapshot for an exact window

- **GIVEN** a supported synthetic series with a verified zero baseline and a cumulative USD 0.50 snapshot for exactly one Run interval, plus repeated constituent deltas
- **WHEN** the local policy selects the snapshot lane
- **THEN** the subtotal is USD 0.50 once, the deltas are traced as excluded, and the result remains explicitly synthetic.

#### Scenario: Reset or partial window

- **GIVEN** a cumulative value with an unknown reset boundary, a gap, or a window spanning multiple attribution targets
- **WHEN** a narrower Change interval is requested
- **THEN** no amount is inferred for that interval and the affected series prevents completeness.

### Requirement: Exact bounded aggregation

Known subtotals SHALL use exact decimal arithmetic independent of ambient precision
and input ordering, with no floating-point conversion or intermediate rounding.
Every result SHALL separate kind, unit, currency and basis, retain unknown counts
and reasons, and distinguish no known observations from observed zero. Exceeding
explicit computation resource limits SHALL fail atomically rather than round,
truncate or omit evidence. Original source amount strings SHALL remain unchanged.

#### Scenario: Precision and cancellation

- **GIVEN** same-identity decimal amounts 10000000000000000000000000000, 1 and -10000000000000000000000000000 under a low ambient Decimal precision
- **WHEN** each input permutation is settled
- **THEN** the known subtotal is exactly 1 in every order and source strings remain unchanged.

#### Scenario: Unknown currency and empty known set

- **GIVEN** an unknown monetary amount without currency, known USD billed 1.00, known EUR billed 2.00 and USD estimated 3.00
- **WHEN** settlement reports the components
- **THEN** it shows separate economic identities, retains the unknown-currency observation without assigning USD, and produces no cross-currency or billed/estimated grand total.

#### Scenario: Resource boundary

- **GIVEN** a job beyond a declared record-count or aligned-decimal-digit limit
- **WHEN** computation is attempted
- **THEN** it returns a controlled limit diagnostic without publishing a partial revision or silently discarding existing evidence.

### Requirement: Snapshot-bound immutable computation

A computed settlement SHALL retain a committed input cutoff, algorithm/source-policy
versions, explicit scope, complete selected/excluded input provenance and structured
unknown reasons. It SHALL compute from one consistent snapshot and publish one
immutable local revision atomically. Imported producer claims SHALL remain distinct
from the local computed chain. An identical operation-ID retry SHALL return its
original revision; reuse with different arguments SHALL fail. A new operation ID
SHALL record a new revision and cutoff even if amounts are unchanged.

#### Scenario: Response lost after commit

- **GIVEN** a successful computation whose response was lost and subsequently imported evidence
- **WHEN** the identical operation ID is retried
- **THEN** it returns the original revision and cutoff unchanged; a new operation ID is required to include later evidence.

#### Scenario: Writer changes inputs

- **GIVEN** another writer imports evidence or a binding during computation
- **WHEN** a computed revision is published
- **THEN** its recorded snapshot and input membership are consistent, or the whole operation fails with a retryable diagnostic; it never combines independently observed states.

#### Scenario: Imported claim cannot take over local history

- **GIVEN** an imported Settlement marked reconciled and a local computed revision for the same Change
- **WHEN** the claim is inspected or imported again
- **THEN** it remains an origin claim, cannot become the local chain head or local completeness proof, and identical import preserves both histories.

#### Scenario: Foreign replay and late evidence

- **GIVEN** a computed settlement imported into a different store after its original cutoff
- **WHEN** the destination inspects it or requests replay at that cutoff
- **THEN** the origin result stays inspectable but unavailable destination history yields replay_unavailable, with no backdated availability or recomputation masquerading as the original result.

### Requirement: Coverage policy and absence provenance

Full-change decisions SHALL record the Change outcome, complete linked-Run set and
all Run outcome/interval/binding revisions, expected source/economic coverage and
supporting evidence known at the cutoff. Source coverage assertions SHALL be checked
against local supported policy; portable verified/reconciled labels SHALL NOT grant
support. Potentially relevant unbound evidence or unknown applicability SHALL block
full-change eligibility without being arbitrarily attributed. Synthetic policy
support SHALL remain explicitly synthetic, separate from real pilot observations.

#### Scenario: Forged completeness label

- **GIVEN** imported manual or unknown-profile evidence labeled verified_provider or reconciled by its producer
- **WHEN** local full-change eligibility is computed
- **THEN** unsupported coverage stays provisional regardless of those labels, and no provider compatibility is asserted.

#### Scenario: Relevant unbound evidence

- **GIVEN** terminal fully bounded Runs plus unbound evidence that could belong to the requested repository/source/unit interval
- **WHEN** full-change eligibility is evaluated
- **THEN** it is incomplete with the unbound evidence identified, while that evidence remains outside the Change subtotal.

#### Scenario: Complete synthetic coverage

- **GIVEN** a synthetic terminal Change with one or more terminal bounded Runs, supported explicit full-interval coverage for every required source/component and no unresolved evidence
- **WHEN** full-change eligibility is computed
- **THEN** it is eligible within the declared synthetic scope with exact membership and provenance, without claiming observed real-provider finality.

### Requirement: Offline computation and auditable reports

The existing settle command family SHALL expose mutually exclusive normalized-import,
lifecycle and computation modes. Computation SHALL require explicit Change/economic
scope and an operation ID. Explain SHALL report immutable revision inputs, exclusions,
cutoff, membership and unknown reasons; repository remainder reporting SHALL stay
read-only and separate unbound from bound totals. Help, invalid modes and read-only
inspection SHALL NOT create or migrate stores. Quote, budget checks and provider
parsers SHALL remain outside this capability.

#### Scenario: Local synthetic end-to-end computation

- **GIVEN** no provider connection and a synthetic normalized artifact with a duplicate, distinct retry, correction and explicit binding targets
- **WHEN** it is imported locally, bound, computed and explained through installed commands
- **THEN** exact separate subtotals and the correction/coverage trace are available without network or SpecFact runtime access.

#### Scenario: Reject mixed modes without side effects

- **GIVEN** no local store and a request mixing lifecycle declarations with computation/import options or omitting required compute selectors
- **WHEN** the command validates its arguments
- **THEN** it exits nonzero with safe diagnostics and creates no store or revision.

#### Scenario: Read-only repository remainder

- **GIVEN** bound and unbound events, accepted and abandoned Changes, and unresolved overlap in one source partition
- **WHEN** explain reports a repository/economic scope
- **THEN** each resolved event contributes to only its bound or unbound bucket, unresolved evidence is separately disclosed, and no synthetic Change record or duplicate revision is persisted.

### Requirement: Source component identity and explicit unknown resolution

One source event SHALL be able to carry separately identified economic components
without duplicating its core binding target. Corrections SHALL preserve component
identity, kind, unit and basis; known currency SHALL NOT change. An explicit
replacement MAY resolve previously unknown currency when the earlier monetary
amount was unknown, retaining its old unresolved revision and provenance.

#### Scenario: Multiple quantities for one event

- **GIVEN** one source event with distinct input-token, credit and billed-money component keys
- **WHEN** normalized input is imported twice and bound once
- **THEN** each component is counted once in its own economic identity through the same explicit evidence binding, without a false duplicate conflict or cross-unit sum.

#### Scenario: Later currency clarification

- **GIVEN** an unknown monetary amount with null currency and an explicit replacement reporting USD 0.25 for the same component
- **WHEN** the replacement is validated and computed at a later cutoff
- **THEN** the new revision contains USD 0.25 while the old cutoff remains unknown; replacing known USD with EUR is rejected atomically.

#### Scenario: Independent Change evidence cannot alter target selection

- **GIVEN** complete evidence for a target Change and explicitly bound evidence for another Change using the same source series, including snapshots, pending corrections or overlapping files
- **WHEN** the target Change is computed
- **THEN** the other Change's correction and lane policy does not alter the target subtotal, exclusions or completeness; inherited correction-chain bindings determine the subject, while genuinely unbound potentially relevant evidence remains conservative.

#### Scenario: Bounded economic identity lookup work

- **GIVEN** a valid normalized batch and an existing economic graph within the documented limits
- **WHEN** evidence identity is matched during import or evidence bindings are checked during graph validation
- **THEN** each operation builds its lookup index once and performs direct per-record lookups, preserving deduplication and cross-repository rejection without repeated full-record scans for these lookups.


#### Scenario: Selection provenance follows retained chain decisions

- **GIVEN** foreign explicitly attributed chains and a retained pending correction whose explicit binding establishes its target Run
- **WHEN** a Change computation records immutable inputs
- **THEN** foreign chains contribute neither inputs nor exclusions, while the retained pending chain includes the consulted binding as provenance even before its predecessor arrives.

#### Scenario: Explicit mapping inputs respect declared membership

- **GIVEN** a portable computed result naming an EvidenceBinding input
- **WHEN** graph validation checks that dependency
- **THEN** its complete RunRef belongs to the declared settlement Runs; a foreign explicit mapping fails atomically. Historical plain/economic evidence that was unbound at its cutoff remains valid when later assigned elsewhere.

#### Scenario: Shared lookup indexes preserve validation boundaries

- **GIVEN** multiple coverage assertions and computed membership declarations
- **WHEN** a graph is validated
- **THEN** EvidenceBinding and RunBinding indexes are built once per validation, and declared Run membership once per computed result; duplicate conflicting bindings remain rejected regardless of input order. These guarantees concern the lookup steps, not whole-pipeline complexity.

#### Scenario: Outcome subject checks do not copy complete membership

- **GIVEN** a computed result with many declared Runs and their Outcome inputs
- **WHEN** each Outcome subject is validated
- **THEN** its membership is checked without copying the complete member set per Outcome; the target Change and member Run Outcomes remain allowed, while a foreign subject is rejected.

#### Scenario: Bounded correction and overlap validation

- **GIVEN** linear corrections, pending predecessors, and file or namespaced source windows within the input limits
- **WHEN** their attribution and overlap invariants are evaluated
- **THEN** correction chains visit each present node once, and overlap detection sorts windows and performs bounded per-window work; forks, cycles, inherited subject conflicts, known-currency changes and inclusive cross-file overlaps remain rejected or unresolved as before.

#### Scenario: Indexed coverage and cutoff dependency work

- **GIVEN** many linked Runs with lifecycle revisions, coverage assertions and economic events, or a dependency chain rooted in unavailable history
- **WHEN** computation selects its cutoff inputs and evaluates coverage
- **THEN** full-reference lifecycle, membership, coverage and event indexes are built once per operation, revision leaves determine lifecycle state regardless of insertion order, and cutoff invalidation visits each dependency edge once.

#### Scenario: Repository uncertainty without normalized economics

- **GIVEN** a selected unknown economic amount or identity-only Evidence without normalized economics
- **WHEN** a read-only repository report is requested
- **THEN** unknown subtotals name unknown_amount; potentially relevant identity-only Evidence names missing_economic_evidence and is identified as unresolved without fabricating an amount, while Evidence explicitly bound to another repository is omitted.

#### Scenario: Consistent inspection eligibility

- **GIVEN** an immutable stored computed result and its complete input dependency graph
- **WHEN** replay eligibility is inspected
- **THEN** the stored payload, local computation authority and all input availability are evaluated from one read transaction with one graph validation; cutoff bounds, origin-claim limits and transitive dependency availability remain enforced.

#### Scenario: Coverage assertions reuse selected event requirements

- **GIVEN** one Run with many selected point events or many economic components sharing Evidence, and many coverage assertions with small explicit evidence lists
- **WHEN** supported coverage is evaluated
- **THEN** distinct complete Evidence keys and selected point extrema are summarized once per Run group; each assertion separately checks its own references and point bounds, without unioning assertions or rescanning every selected component. Empty events, missing references, unsupported source policy and exclusive point end boundaries retain their uncertainty reasons.
