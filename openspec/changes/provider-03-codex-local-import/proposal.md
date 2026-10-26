# Import existing local Codex coding-session metadata

## Why

Ordinary local Codex coding sessions contain candidate usage evidence without
Enterprise exports. Safe local learning requires verified version-specific identity
and accounting rather than assumptions from file presence.

## What Changes

- Accept explicitly selected existing local coding-session files under independently approved source profiles.
- Normalize allowlisted usage/model/identity/interval metadata with versioned deduplication, correction and ownership policy.
- Bind evidence manually to existing Changes/Runs; expose incomplete, unsupported and conflicting observations.
- Keep demand eligibility and billed settlement authority separate.

## Capabilities

### New Capabilities

- `codex-local-import`: Offline approved Codex local coding metadata import.

### Modified Capabilities

- `bounded-review-session`: Explicitly approved retirement of a merged earlier-stage PR, preserving the same review history and allowance for runtime verification.

- `change-run-contracts`: Add one portable diagnostic native-usage record beside
  Evidence, preserving quantity and provenance without economic or demand authority.

## Impact

Future reader, additive portable contract, graph validation and source-specific
policy tests, using an explicit native mode in the existing settle command and
the core store transaction. Documentation: provider feasibility, the
Codex/Claude metrics guide, CLI/settlement and [forecasting](../../../docs/forecasting.md).
This delivery adds plans only, no runtime reader or collection.

## Non-goals

No automatic scanning/watch service, ordinary chat import, account settings,
new telemetry, provider API, paid model request, prompt retention or inferred subscription charges.

## Dependencies

[Source feasibility #9](../archive/2026-10-08-pilot-01-source-feasibility/proposal.md) and delivered
[reconciliation #12](../archive/2026-10-02-settlement-01-reconciliation/proposal.md).
Demand use additionally requires its own policy under
[adaptive demand](../archive/2026-10-23-forecast-01-local-adaptive-demand/proposal.md); that feature
does not depend on this reader for its offline/synthetic implementation.
Reader delivery/archive depends on #9/#12 and its approved source policy, not #35.
Adaptive-demand integration is conditional on #35 delivery and a separately
approved demand policy; otherwise it is recorded as deferred follow-up.

## Preparation decision, 2026-10-23 Europe/Berlin

The maintainer selected #36 for planning and an architect review. Fresh main is
`6b6fab30e8030e04fc1a2d803000c640c9f64479`; #35 implementation and its correction
are accepted through PRs #43/#45. The 23 historical source profiles retain zero
approvals; the subsequent finite profile activation is recorded below.
The reader remains unimplemented. Exact finite semantic approval and canonical
activation are recorded below; reader/runtime assurance remains pending.

The existing normalized import carries economic records. Evidence alone has no
quantity, and existing economic records cannot preserve the native model, lineage,
source finality and snapshot provenance required here. Plan one strict portable
`NativeUsage` record and one atomic reader operation. Do not encode missing
metadata in identifiers or turn imported usage into a DemandObservation.

Native demand projection and its measurement/coverage policy are explicitly
deferred follow-up. Preserve all current synthetic demand and billed-money guards.
The reader does not backdate assessments, ecosystems or local availability.
The [design](design.md) records the compared shapes, interface and evidence gates;
[preparation evidence](PREPARATION_EVIDENCE.md) distinguishes installed protocol
shape from unapproved persisted-file semantics. This reconciliation is local and
unpublished, with no implementation, collection or publication authorization.

## Risks and rollback

Duplicate/corrected counters, partial lineage and private content -> approved
accounting policy, safe allowlists and conservative gaps. Scoped revert preserves
originals and imported history; any later migration needs backup/recovery tests.

## Source Tracking

The restored plan's [native accounting evidence](NATIVE_ACCOUNTING_EVIDENCE.md)
records the authorized 2026-10-23 inspection of four existing snapshots. The initial independent
adjudication approved no capability. Exact producer binding and accounting semantics
were blockers at that stage. No runtime reader, new collection or relaxed approval policy is
delivered by this investigation.

Planning approved 2026-10-07; native User Story under Attribution and settlement
#7 / Epic #4. GitHub issue: [#36](https://github.com/nold-ai/changecost/issues/36). Todo, unassigned,
undated; the user requested publication of these plans in a planning-only PR.
Implementation remains unstarted.

Native type/parent/dependencies/private-project Todo read back on 2026-10-07.

## Producer-binding planning decision, 2026-10-23

The [binding policy](PRODUCER_BINDING_POLICY.md) selects finite immutable snapshot
admission over general producer receipts. [The proposed profile](PROPOSED_PROFILE.json)
requests only serialized request diagnostics with partial coverage and unknown
model/time/finality/backend presence. Exact whole-file admission excludes later
appends and unreviewed lifecycle forms. Semantic approval, canonical activation and
runtime readiness remain separate gates. This proposal activates nothing.

Independent semantic review subsequently approved the exact finite profile and all
six decisions; see the [bound disposition](NATIVE_ACCOUNTING_EVIDENCE.md#independent-finite-mapping-approval).
This closed those semantic blockers for the selected snapshot only. Canonical
activation was authorized in the subsequent stage below; reader implementation
is still blocked and unstarted.

## Canonical activation boundary, 2026-10-23

The maintainer subsequently authorized canonical activation and contributor
admission/baseline maintenance. The exact approved profile and proof are now
registered; the original 23 profiles remain unchanged with zero approvals.
[Activation evidence](TDD_EVIDENCE.md) records the contributor-only behavior checks
and fresh independent verification. Earlier activation-pending statements record
the preceding planning stage. Reader/runtime implementation remains blocked and
unstarted; all ten reader implementation tasks remain unchecked.

## Runtime authorization and reconciliation, 2026-10-24 Europe/Berlin

The maintainer now explicitly authorizes the exact finite reader implementation.
Earlier planning-only and blocked statements above preserve historical scope.
The selected single NativeUsage kind, one public reader operation and one
Store.apply transaction are retained. Repository is carried on NativeUsage and
checked against exact manual bindings. One canonical fact representation owns
both projection hashing and semantic replay comparison. The package derivative
is generated and checked against the unchanged canonical register. No source
collection, new admission, demand/billing authority or publication is added.

The blocking public Store probe demonstrated fresh/existing atomic graph rejection
and immutable no-op availability. Private reproduction of retained authorized
bytes matched the approved 16-request/96-fact projection and exact profile/proof.
Runtime positive replay of those exact bytes produced no second insertion.
See TDD_EVIDENCE.md for actual commands and remaining assurance.


## Verification recovery authorization, 2026-10-24 Europe/Berlin

The maintainer requested verification through green results, preservation and supported
recovery of the existing review ledger, and a private branch push for fresh supported
Linux CI. Earlier no-publication statements describe the implementation stage. This
request permits the private CI bootstrap and subsequent corrections, not merge, release,
new admissions or collection. The historical source PR can be retired only after its
actual closed/merged identity, complete provider facts and adopted-main ancestry are
verified through the supported append-only transition. Every runtime gate remains open
until current evidence satisfies it. Neither recovery nor a private push is acceptance.
