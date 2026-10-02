# Design: Reconcile evidence into revisioned settlements

## Context

Prepared on 2026-09-29 against main `999cb8f960785fe4ac0434d41a0892beca933191`.
Core-02 is merged and archived. Its Python package implements strict identity,
bindings, lifecycle declarations, portable replay and committed historical eligibility.
It deliberately implements no economic reconciler. Evidence is identity-only;
Settlement currently stores an imported claim, not computation provenance.
See [code and research findings](PREPARATION_EVIDENCE.md) and the
[capability scenarios](specs/evidence-reconciliation/spec.md).

This document specifies the implementation authorized on 2026-09-29. CLI/schema
documentation describes the working checkout; verification and acceptance remain pending.

## Goals / Non-Goals

Provide offline normalized import, exact scoped subtotals, immutable correction and
settlement history, and explicit full-change eligibility. Reuse core identities and
local availability; keep the five existing command families.

No provider parser, live collection, automatic attribution, exchange-rate/pricing
lookup, invoice guarantee, quotes, budget enforcement, plugin framework or runtime
SpecFact dependency. Synthetic policy tests do not approve any real provider.

## Unreleased 0.x development boundary

Maintainer clarification, 2026-09-29: all approved pilot changes belong to the
first pre-v1 alpha/preview feasibility study. No version has been published.
The package remains `0.1.0.dev0`; this preparation does not bump it. The
[public project site](https://changecost.dev/) describes an unreleased pilot
(accessed 2026-09-29), not a stable product or a published compatibility promise.

Evolve the current strict `changecost/v1` internal artifact schema in place.
That label is a schema identifier, not a product 1.0 release. Do not introduce
`changecost/v2`, dual public format support or a general migration framework for
this planned first-version work. New known record kinds and fields belong to the
same developing contract; unknown versions/kinds/fields still fail validation.
Older checkouts may reject new records. Document the tested repository revision
with fixtures instead of promising cross-checkout compatibility.

Keep existing core records and their semantics intact where practical: lifecycle,
identities, amount strings, binding provenance and local history are still needed.
Recognize the earlier minimal Settlement shape as an imported producer claim;
missing economic/coverage details do not become known or complete through defaults.
Do not relabel old data, invent missing values or silently overwrite local stores.

Use the existing common envelope and stable references for three narrowly scoped
record kinds. Exact field validators are implemented from these declared roles:

| Record | Required content beyond common provenance |
| --- | --- |
| `economic_evidence` | Core Evidence reference, repository/source namespace, stable component key, exact Component, series/lane, event/window bounds, and optional typed replacement locator/reason. |
| `source_coverage` | Explicit source/profile/policy version, full RunRef or declared source scope, economic identity, coverage window/finality assertion and supporting Evidence references; local support remains independently checked. |
| `computed_settlement` | Change reference, operation ID, opaque local ledger ID, input Cutoff, algorithm/policy version, requested economic/window scope, known subtotals and unknown counts/reasons, full linked-Run membership, lifecycle/binding/coverage/input/exclusion references, and optional previous computed revision. |

Legacy `settlement` records remain producer claims; the separate computed kind
avoids rewriting their predecessor chains. Portable records cannot mint a local
computation receipt. New known reference kinds must participate in the same atomic
reference graph and destination-availability checks.

The local computation receipt may require a new internal SQLite layout marker.
That marker is independent of package and artifact version labels. If the layout
is incompatible, reject the older store unchanged with a controlled diagnostic;
do not add automatic upgrade/downgrade or silently rebuild it. Preserve a backup
and document export with its matching checkout, then import into a separate fresh
store. That import starts new destination history and cannot reproduce the original
local cutoff; retaining the original store/checkout is the historical recovery path.
This is a pre-release safety boundary, not a multi-version support programme.

## Reconciliation decisions

1. Retain core Evidence as the identity referenced by bind. A separate allowlisted
   economic record references that identity and carries repository scope, one
   Component, source namespace/series, a lane, event or covered interval, correction
   semantics and source declaration provenance. Source records without economics
   remain identities, not zero-value economic events.
2. Use a typed locator (provider, surface, profile, source namespace and stable key,
   or full file identity) for correction targets. It is data, not a RecordRef.
   A missing target remains pending; dangling RecordRefs still fail core validation.
3. Same normalized source identity and semantic payload is a no-op regardless of
   transport order, ingest timestamp or request ID. Preserve original records and
   first availability. Conflicting semantics require a uniquely identified correction.
4. Only replacement corrections are supported initially. Replace an effective leaf
   once; do not add replacement to original or interpret it as a signed delta.
   Explicit reversal is a replacement zero with reason/profile evidence. Reject
   resolved cycles, forks, cross-profile/source/subject targets and changes to known
   economic identity (the explicit unknown-currency resolution below is allowed). A pending chain is excluded from the unambiguous subtotal and blocks
   completeness until resolved; do not silently choose a branch.
5. Aggregate event deltas only within one exact kind/unit/currency/basis identity.
   Cumulative snapshots remain separately identified: choose a locally supported
   authoritative lane for an exact series, never both. Only a snapshot with a
   proven baseline/reset and matching attribution/window may represent that window.
   No snapshot subtraction, interpolation, proration or generic provider transform
   is added in this pilot. Ambiguous series are excluded with reasons.
6. Capture a single committed input snapshot and immutable input cutoff. Compute
   and append inside the same writer transaction, or prove an unchanged snapshot
   before publishing. Independent per-record fresh reads cannot prove one snapshot.
   Existing time-only, future, foreign and unavailable cutoff limitations persist.
7. Preserve a local computed revision chain separate from imported producer claim
   chains. Every request names a stable operation ID. Identical retry returns the
   existing revision, preserving its cutoff and timestamps; reuse with different
   arguments fails. New operation IDs create explicit revisions, including when
   amounts are unchanged, so late bindings or coverage decisions remain auditable.
8. Reporting uses an explicit economic identity and optional source-interval scope.
   A scoped reconciled amount is not a full-change observation. Store the Change
   outcome reference, exact linked Run set, outcome/interval/binding revisions,
   source-policy version, source-coverage evidence and unresolved reasons. Recompute
   for new cutoffs; importing an origin claim never certifies it locally.
9. Full-change eligibility requires a nonempty linked Run set, terminal outcomes,
   known work bounds, complete supported coverage across all required sources and
   components, and no unknown values, unresolved overlaps/corrections, contradicted
   bounds or potentially relevant unbound evidence. Require explicit zero support.
   Never derive attribution from timestamp proximity; do not narrow work bounds
   merely to fit a charge interval. Missing applicability facts block completeness.
10. Locally recognized synthetic fixtures exercise positive completeness paths.
    Manual/unknown real profiles can retain provisional known amounts and reasons,
    but cannot become verified by declaring a portable label or CLI flag. No real
    provider completeness policy is approved in this change. Synthetic outputs
    stay explicitly synthetic and cannot masquerade as real pilot observations.
11. Sum exact decimal coefficients at a common exponent using checked precision or
    integer arithmetic, independent of ambient decimal context and record order.
    Preserve source strings. Do not use SQL sum/total, float or display quantization.
    Bound each job to 100000 economic records and 4096 aligned decimal digits as
    explicit pilot resource defaults. Exceeding either fails before publishing a
    result; never truncate, drop evidence or silently round. These are design limits,
    not provider measurements. Verify signed values, cancellation and extreme exponents.
12. One command family remains settle: explicit --compute mode, repository/change
    selectors, economic identity and --operation-id. Lifecycle mode remains separate
    and cannot be combined with computation/import options. Core bind keeps portable
    replay. explain exposes immutable trace, cutoff, membership and unknown reasons;
    repository remainder is a read-only report, not a fabricated Change/Settlement.
    quote/check and native provider file adapters remain unimplemented.


## Data responsibilities and trust boundary

A normalized batch has its own explicit input schema and no caller-generated
storage record IDs. It names repository, provider/surface/profile and opaque source
namespace, identity scope, event/series identity, aware UTC event or window bounds,
one economic Component with a stable source component key, lane and optional
replacement target/reason. Multiple components from the same source event share
its core Evidence identity and have distinct component keys; do not confuse input
tokens, credits and money with conflicting duplicates of one value. File identity
uses SHA256 and ordinal; namespaced identities include a privacy-preserving source
partition so independent accounts/streams cannot collide. Do not retain raw account
identifiers, prompt content or unrestricted payload fields.

`settle --import-evidence PATH --repository-id ID` is the normalized-input mode;
its versioned strict envelope is not a native provider format. Validate the entire
batch, normalize stable identity, then write identity/economic records atomically.
`bind --import-artifact` remains exact portable replay and must not weaken core
identity conflicts or remap stored record IDs silently. Re-export transport changes
are handled at normalization, before immutable core records exist. Repeat imports
return existing evidence selectors and do not append observation/record timestamps.
Future provider adapters may call this same normalizer after their own evidence gates.

Economic records retain the core evidence reference used by `bind`; they do not
infer the target Run from event times. A typed pending-target source locator is
never passed to core graph validation as an unresolved RecordRef. Once resolvable,
its graph must be acyclic and nonbranching before any effective amount changes.
Amounts remain null or exact signed decimal strings. A replacement preserves the
source namespace, attribution subject, component key, kind/unit/basis and any
known currency. An explicit correction may resolve a previously unknown currency
when its value was unknown; it cannot change one known currency into another.
Keep the earlier unknown revision visible. Changed attribution
is not silently implemented as an economic correction.

Source coverage needs explicit scope, unit, interval, policy/profile version and
source-evidence references. Define expected sources from local supported policy
and each complete RunRef, not from only the rows that happened to arrive. An
unknown expected source or applicability remains a reason for incompleteness.
Only an explicitly named synthetic fixture policy is supported for positive full
coverage in this stage. Manual/unknown real profiles may produce provisional known
subtotals but cannot become final through a label, CLI flag or arbitrary policy file.
No generic extensible profile registry is needed: a small closed local policy set
and an explicit unsupported result suffice.

Computed results retain known subtotals and unknown counts per exact economic
identity. With no known observations, known subtotal is null; an observed known
zero is a distinct value. Ambiguous identities/series are excluded rather than
included in an apparently safe subtotal. Exact signed adjustments may make totals
negative; do not clamp refunds to zero. Currency-null unknown money cannot be
assigned to a known currency bucket without evidence. Results list unresolved
components separately; no cross-identity grand total is emitted.

## Full-change coverage

Coverage and cost are independent. Full-change eligibility requires a terminal
Change with at least one explicitly linked Run; every Run must be terminal, with
known revisioned bounds and supported coverage of its entire work interval for the
requested economic identity. The source policy determines all expected streams
and components. Preserve failed/cancelled retries and abandoned Change expenditure.
Missing bounds, source finality, components or amounts prevent full-change eligibility.
Zero requires explicit supported evidence. A zero-duration known interval still
requires affirmative coverage/zero evidence; no interval-length shortcut is permitted.

Store the complete linked Run set and all binding, outcome, interval and evidence
references, including the Change outcome, in the revision. Record the one input
cutoff and absence/unresolved reasons: positive dependency references alone cannot
prove that no omitted Run, unbound event or later source correction existed.
Potentially relevant unbound events are determined conservatively from explicit
repository/source/economic/window scope; unknown applicability blocks eligibility.
No time-proximity inference may attribute them to a Change.

Define source windows explicitly as start-inclusive/end-exclusive; a point event
at the end is outside that source window. Run-end equality is not itself a
contradiction, but full coverage needs a proof covering an attributed endpoint
when the source uses point events. Missing source boundary semantics remain
unsupported; do not interpolate, prorate or silently trim user-declared work bounds.

Late input, binding or lifecycle changes require a new computed revision and cutoff.
An old full-change result is only a statement about its original snapshot. Explain
must not display its flag as current eligibility without evaluating the new state.
An imported old claim cannot reconstruct destination knowledge or certify an earlier
cutoff. Local recomputation has a new local provenance even if its amount matches.

## Transactions, idempotency and failures

Compute from records plus observations captured in one transaction. Reserve the
writer before determining the local cutoff when the same request will append a
revision. Apply snapshot filters once to that immutable in-memory input set;
calling today's per-reference `Store.eligible` repeatedly would reopen snapshots.
A later physical commit is not backdated into the input cutoff. Persist the result
and operation-ID receipt atomically, and keep the result's own availability separate
from the cutoff of its inputs. Export/inspect stays read-only.

An identical operation ID with identical requested scope returns its prior result,
even if new inputs exist; differing arguments conflict. A new operation ID always
captures a new snapshot and appends a revision. Concurrent operations either
serialize with a valid predecessor or return a controlled retryable failure. Keep
imported producer claim chains separate from one local computed ledger per Change;
no imported claim may take over a local head. Local computation status is established
by the receipt written atomically by the local operation, not by a portable origin
store ID or producer label. Portable replay preserves the claim but cannot mint that
local receipt; a consistent database backup retains it. Record scope on each ledger revision
so different requested identities/windows do not masquerade as revisions of the
same observation. Never average revisions into additional quote peers.

Inject failure before commit, during fresh-store publication and after successful commit/before
response. Verify rollback/no partial publication, exact retry and sequence-exhaustion
handling. Unsupported store layouts/artifact versions fail without mutation under
the unreleased development policy above. No automated migration is required.

## Alternatives and rationale

| Choice | Rejected alternative and reason |
| --- | --- |
| Normalize source identity before core insertion | Relax immutable core RecordRef/identity checks: breaks portable replay and binding integrity. |
| Typed unresolved locator | Missing core references: conflicts with the merged atomic graph boundary. |
| One authoritative lane with explicit uncertainty | Sum snapshots plus deltas or choose the last seen point: double counts and ignores reset/coverage semantics. |
| Checked exact sums | Bare Decimal `sum` or SQL aggregate: observed precision loss in the preparation probes. |
| Snapshot plus explicit membership | Current per-record eligibility calls alone: cannot prove absence or one shared snapshot. |
| Separate local and imported claim history | Trust imported reconciled flags or attach them as local head: treats assertion as local verification. |
| Closed synthetic/manual policy boundary | Approve real provider completeness from docs or add a generic plugin framework: unsupported and outside scope. |

## Verification and implementation sequencing

Keep specs first; derive tests, observe genuine failures, implement the smallest
behavior, then record actual passing commands in TDD_EVIDENCE.md. Portable fields,
store compatibility and input/privacy boundaries land before economic algorithms.
Each subsequent task group includes its tests and documentation; do not defer them
to a final catch-all group. Required later matrix: Python 3.11.15 and 3.13.14,
installed-wheel/sdist offline CLI proof and supported Linux native analyzer assurance.
No passing fixture in this preparation is product TDD.

## Risks, resources and rollback

- False finality → supported-policy coverage, explicit unknowns and synthetic labeling.
- Double counting/correction races → stable source identity, validated replacement chains and atomic revision publication.
- Resource blow-up or precision loss → bounded exact arithmetic and atomic rejection at explicit limits.

The 100000-record/4096-aligned-digit limits are proposed pilot safeguards, not
benchmarks or provider requirements. Record them in implementation docs and test
both edges. The project remains unreleased; no package version bump or release is
needed for planning. No paid infrastructure or real-data collection is required.

Before using a checkout with an incompatible internal store layout, retain a
consistent backup and the matching earlier checkout. Verify backup recovery and
separate fresh-store import; never downgrade a populated store or confuse portable
reimport with historical restore. Revert planning changes through their eventual
commit/stash while retaining issue/review history. Reverting this plan does not
reopen completed Core-02 work or waive provider feasibility gates.


## Consolidated bounded-work repair — 2026-10-02

Validate correction chains from their leaves once, with shared visited state;
unvisited nodes identify cycles, and missing predecessors remain pending. Retain
fork, currency and inherited-binding subject checks. Overlap uses sorted starts
and the furthest ends for two distinct digests (including namespaced null), with
inclusive endpoints and the prior two-file prerequisite.

Build full-RunRef, coverage, binding and lifecycle-leaf indexes once per operation;
leaf identity follows previous references, never timestamp or insertion order.
Group effective and selected events by full RunRef once and use set membership.
Cutoff pruning seeds unavailable records and invalidates reverse dependents once.
Inspection reuses one transaction for exact payload, local receipt authority,
cutoff bounds and one validated availability snapshot for every input.

Repository remainder computes each bucket once, adds unknown_amount for unknown
values, and discloses identity-only Evidence lacking economics as unresolved
missing_economic_evidence. Unbound identity-only Evidence stays conservative;
explicit bindings scope it to the repository without creating monetary values.
No source policy, provider capability, schema or package version is expanded.


### Coverage assertion closure — 2026-10-02

Per-Run event grouping alone did not remove supports() rescans per assertion.
Summarize the selected group once as a distinct full Evidence-key set, point
minimum/maximum and has_events. Each assertion keeps its own policy, economic,
finality, full-work interval and evidence-set predicates. Point extrema retain
inclusive starts and exclusive ends. Reject insufficient distinct evidence
cardinality before subset evaluation; subsequent work is proportional to each
assertion's actual references. Never union assertions. Retain references to all
consulted assertions even when their individual support checks fail.
