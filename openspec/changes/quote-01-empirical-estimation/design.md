# Design: Produce deterministic empirical change-cost quotes

## Context

See [proposal](proposal.md) and [capability spec](specs/empirical-quotes/spec.md).
Reviewed 2026-10-03 (Europe/Berlin) against main
`3009b351d5108b60e9ba8649a9ef4aa0c0feb9f9`, after settlement PR #28 and archive PR #31.
The Python package, Typer CLI, exact portable Quote, immutable registration features,
SQLite layout 2 and normalized reconciliation are delivered. No estimator or native
provider parser runs. Main [contracts](../../specs/change-run-contracts/spec.md) and
[reconciliation](../../specs/evidence-reconciliation/spec.md) are the behavior boundary;
archived designs are historical rationale, not the current implementation inventory.

## Goals / Non-Goals

Compute explainable offline empirical quotes from auditable complete Changes. Reuse
existing identity, availability, reconciliation and coverage semantics. No ML, price
registry, conversions, provider policy, collection, budget enforcement or p90 guarantee.
Runtime implementation was separately authorized on 2026-10-03; provider collection remains outside scope.

## Decisions

1. **Quantiles and parameters.** For n exact sorted Decimal values, nearest-rank at
   probability p selects the one-based rank ceil(p*n), equivalently zero-based
   ceil(p*n)-1. Compute p50 and p90 without float conversion, interpolation or
   pre-selection rounding; integer rank arithmetic avoids ambient Decimal precision.
   Retain signed aggregates and observed zero without clipping. Default minimum n=20;
   accept a strict positive integer override and record it. The default and empirical
   p90 are pilot choices, not validated calibration or budget guarantees.

2. **Comparable population and backoff.** Require an explicitly selected repository
   and complete economic identity (kind, unit, currency, basis). The population is
   terminal accepted plus abandoned Changes with all linked attempts included. Use
   fixed levels: repository+change_shape+trajectory+execution_profile, then
   repository+change_shape+trajectory, then repository-wide. Each level retains the
   same population and economic identity. Choose the first meeting the minimum;
   record counts and rejection reasons. Never combine currencies, units, billed and
   estimated bases, or count a Change once per Run/revision. If none qualifies,
   emit unpriced with null p50/p90 amounts and explicit reasons; no zero fallback.

3. **Derive completeness at the Quote cutoff.** Capture one committed store-local
   cutoff including time and sequence, and prune unavailable records and transitive
   dependencies with the delivered snapshot evaluator. For each peer Change, reuse
   reconciliation's pure selection/aggregation/coverage path in that same snapshot
   and economic scope, with no partial source window. Do not write settlement
   records or invoke the settlement writer once per peer. A saved ComputedSettlement
   is historical evidence, not an eligibility cache: neither its old full_change flag
   nor an imported legacy/computed total can establish current completeness. Derive
   one amount and its supporting references from the normalized inputs visible then.
   This avoids depending on operators having precomputed every peer's settlement.

4. **Respect the closed source policy.** The existing supported full-change policy
   is synthetic/fixture, profile and policy synthetic/v1, namespace opaque, series
   usage, component_key charge, monetary billed USD. Only complete observations
   satisfying that policy can currently price a Quote; retain synthetic provenance.
   Other economic identities remain separately representable but unpriced absent a
   supported complete cohort. This change does not approve provider labels or add
   currency/unit support. Exclude open Changes/Runs, zero-run Changes, unknown amounts,
   missing/contradicted bounds, missing/unsupported coverage, potentially relevant
   unbound evidence and unresolved correction/lane/overlap cases with named reasons.
   Relevant changes before the cutoff invalidate earlier completeness; changes after
   it do not alter a historical Quote. Evaluate all linked retries, including failed
   or cancelled Runs and abandoned Changes. Supported zero evidence is an observation;
   absence of evidence is not zero.

<a id="feature-selection-and-capture-time"></a>

5. **Feature capture.** Require a registered target Change. Embed its immutable
   features/v1 snapshot, including null values and registration reference. For target
   and peers, narrow levels require supported versions and all fields used at that
   level, locally available by cutoff and captured before first Run registration or
   known earlier work. Use both local availability/order and declared observed work
   bounds; backdating effective_at cannot qualify a late snapshot. Unsupported feature-version imports remain atomically rejected by the existing
   strict Features contract; no support expansion is introduced. Missing/late fields
   skip affected levels or matches with reasons, without excluding otherwise complete
   observations from repository-wide fallback. Never derive trajectory from retries,
   outcomes, prompts or post-work reconstruction. Later diagnostic Quotes are distinct
   from the first pre-run forecast used by eventual evaluation.

6. **Existing Quote extension.** Retain kind quote and its current base fields. Add
   optional versioned estimation metadata so older imported Quotes remain readable;
   locally computed Quotes require this metadata. It records the positive minimum,
   population, reconciliation algorithm/source-policy versions, synthetic status,
   ordered cohort evaluations, per-peer Change reference/derived amount/supporting
   references and exclusion reasons. The existing algorithm_version records nearest-
   rank estimation and inputs carries all consulted record dependencies, including
   membership, outcomes, work bounds, coverage, mappings and correction chains.
   Keep canonical ordering by full typed references for stable selection and explain.
   Metadata is allowlisted and exact decimal amounts remain strings. Optional presence
   alone does not certify local calculation; explain recomputes from the immutable
   cutoff/parameters and compares the recorded result before reporting reproducibility.
   Legacy imported Quotes without metadata remain economic_validation=not_computed.

7. **Atomic computation and replay.** Implement quote on an existing registered
   Change with explicit repository/economic selectors and a caller operation ID.
   Capture inputs and persist the Quote plus a local idempotency receipt in one
   writer transaction. Same request/operation-ID retry returns the original result,
   even after new evidence; conflicting reuse fails unchanged. Reuse the existing
   computations table without changing layout 2: retain a globally unique operation
   namespace and validate receipt record kind/request, so a settlement operation ID
   cannot be reinterpreted as a Quote. No new receipt table or automatic migration.
   Explain remains read-only, checks the exact stored payload and local receipt in one
   snapshot, and separates local authority from reproducible inputs. Portable import
   cannot manufacture that authority; a consistent backup preserves it. Origin cutoff
   and destination availability remain distinct; foreign/future/time-only cutoffs cannot
   prove local historical replay. Replay recomputes with the stored supported algorithm
   and policy, feature snapshot and inputs; unsupported versions report unavailable.

## Dependencies and evidence

Settlement is the sole implementation dependency and is delivered/archived. Inspect
[preparation evidence](PREPARATION_EVIDENCE.md) for code/CLI sources and limits.
Source inspection remains necessary for provider adapters, not for this synthetic
estimator. Synthetic verification does not establish live calibration or provider support.

## Risks / Trade-offs

- False completeness or precision → derive coverage at cutoff, separate identities,
  retain n/unknowns/synthetic status, and keep unsupported cohorts unpriced.
- Future leakage or unstable cohort order → committed availability and full-reference
  ordering, immutable features and stored parameters; compare historical replay.
- Persistence/provenance mistakes → operation-kind checks, atomic retries, strict
  import validation and same-snapshot read-only verification of stored payloads.

## Migration and rollback

Use existing layout 2 and changecost/v1; extend optional Quote metadata without a
public v2 compatibility programme or package bump. Validate older Quote imports and
same-layout backup recovery. Older checkouts can reject newly extended records;
export/backup first and restore into a separate compatible checkout/path rather than
letting an older program write a newer payload. Preserve original stores/evidence.
Planning rollback restores the scoped stash's reviewed files or reverts a later plan
commit and reconciles issue text, retaining history; no issue closure is needed merely
because planning is rolled back.

## Verification

Use the spec's acceptance scenarios for real failing-before/passing-after runtime
proof during the authorized implementation. Cover quantiles, cohort matching, cutoff
eligibility, source trust, metadata round trips, idempotent writes and privacy together
with their docs in each task group. Review the operation × representation obligations
independently before implementation; close affected obligations after corrections.
Stabilize mechanical gates before exact-head Codex and additional CodeRabbit review
because this change touches persistence and imported-claim trust. Preserve required
Python/Linux assurance and all bounded-session history; do not add a generic full
local/CLI scan by default. PR/ledger evidence records live acceptance; tracked tasks
are publication snapshots, never prechecked from anticipated review outcomes.
