# Design: Local adaptive task-demand forecasts

## Context

The Python/SQLite runtime, normalized imports, economic Quotes and advisory behavior
are delivered. Offline demand learning is locally implemented; acceptance is pending.
Native readers remain planned. Trusted economic coverage
is restricted to synthetic billed USD. Existing Features/v1 cannot represent the
new task/ecosystem dimensions. See [proposal](proposal.md) and
[research](../../../docs/research/adaptive-demand-evidence.md).

## Goals / Non-Goals

Provide an honest cold start, incremental local learning and testable transfer.
No global service, collector, universal complexity formula, hidden paid simulation
or weakening of existing financial completeness/replay policies.

## Decisions

### 1. Separate demand records and authorities

Introduce versioned task assessment, ecosystem snapshot, demand observation,
transfer hypothesis, validation policy/receipt and demand forecast records through
the current portable dispatcher and transactional store. Reuse explicit Change/Run
references, revision and local availability machinery where it suffices. Do not
reuse financial Quote fields for uncalibrated demand or widen Features/v1 implicitly.
An additive reviewed internal schema and backward-read/backup tests are required
before implementation. Imported records remain producer claims; import cannot
create local computation or validation authority.

Source semantic approval, demand-measurement eligibility and complete billed-money
authority are three independent gates. A demand policy identifies quantities,
identity/ownership, cache inclusion, revision/finality and full-work coverage.
Native tokens can qualify without billed USD. Partial measurements remain useful
diagnostics but cannot supply full-task forecast truth. Synthetic data verifies
behavior and cannot establish native calibration.

### 2. Snapshot the question before work

Use scope, coupling, novelty, ambiguity, validation burden and context demand as
separate ordinal dimensions (low/moderate/high/unknown), with concise evidence and
assessor/model provenance. Unknown is not low. Existing code/dependencies may inform
the estimate; eventual patch size, actual retries and turns are outcome diagnostics.
Freeze inputs before the first visible endpoint of any linked implementation Run.
Read-only rehearsal is a separately identified assessment activity with its own
usage; it cannot silently become implementation work or disappear from overhead.
Initial forecasts and later diagnostic revisions remain distinguishable.

An ecosystem snapshot includes provider/surface, reported model identity/version,
producer runtime, reasoning settings, harness, review configuration and measurement
policy version. Account/auth context is an economic/acquisition qualifier, never a
quantity conversion. Unknown material fields cannot establish equivalence. Aliases
and unobserved vendor changes cannot certify a stable model; disclose this limit.
Mixed-model work retains composition and ownership; never assign an aggregate to a
single model merely because it produced the last response.

### 3. Learn from comparable observed work

Rebuild deterministic derived learning from cutoff-visible selected revisions;
do not increment an opaque accumulator that double-counts reimports/corrections.
Use one full terminal Change aggregate per compatible ecosystem/component, retaining
all bound attempts and abandoned work. Completed Runs of an open Change are
diagnostics until full-change eligibility is established. Unknown/partial coverage
and ambiguous attribution remain excluded with counts and reasons. Corrections
can change subsequent forecasts without modifying stored earlier forecasts.

For every forecast, exclude the target Change and all its attempts/revisions from
analogue cohorts, validation inputs and bridge calibration, including later updates
after the target is terminal. Distinct historical Changes repeating the same frozen
scope may remain eligible; disclose their repeat-task dependence rather than
claiming independent samples. Explain records the excluded identities/reasons.

Start with exact known-ecosystem matching and transparent analogy tiers: complete
dimension-profile match, then a same-ecosystem broad baseline. Record each tier's
sample counts and exclusions. No hidden ordinal weighting or trained regression is
introduced. Sparse observations may show observed sample summaries and provisional
scenarios, but not calibrated percentiles. Adding a known dimension may narrow a
cohort; evaluation must test whether this actually helps.

### 4. Transfer is a directional, scoped hypothesis

Construct a bridge from explicit matched-task comparison records, preferentially
the same frozen task scope/repository baseline executed in both ecosystems. Use
complete compatible measurement categories and outcome populations; acceptance-only
pairs must not masquerade as all-outcome evidence. Other matches require declared
criteria and confounding labels. Simultaneous task/model/harness changes cannot
establish an isolated model multiplier. Pair selection and mapping policy must be
available before the forecast cutoff. Never select pairs after seeing target errors.

For positive source quantities use the median observed target/source ratio within
the declared dimension/population scope; preserve exact arithmetic and defer display
rounding. Source zero cannot supply a ratio: retain the zero pair diagnostically. The initial method is median-ratio only. Do not mix policies or
compose bridge chains automatically. Store pairs, direction, method/version,
residuals and counts. One comparison can label a hypothesis, not probability coverage.
Mapped donor observations are provisional scenarios and never measured target rows.

Prefer eligible target observations over mapped donors for the normal target
baseline. Keep transfer as a separately labeled candidate when target history is
sparse, and evaluate it against target-only history chronologically. No pseudo-counts
or synthetic donor replication. Changed/confounded semantics invalidate applicability.

### 5. Evidence states are component-specific

zero_knowledge: no eligible target observations or applicable bridge; qualitative
assessment and missing-evidence requests only. Learning: observed target history,
explicit sample summaries/provisional scenarios, no validated-accuracy claim.
transfer_hypothesis: a compatible bridge informs a labeled scenario with its support
and limitations; retain target sample counts too. validated_forecast: a local
validation receipt supports the exact ecosystem/component/population/policy at the
cutoff. Historical count alone never promotes a result. Unknown model/harness or
changed measurement semantics cannot inherit validation.

Evaluation #17 registers a versioned promotion rubric before outcomes: minimum
truth count, nominal coverage/tolerance, underestimation and width limits, baseline
comparison, overhead and applicability scope. A missing rubric/receipt leaves
validation unavailable. Registering the rubric does not mean its criteria passed.
Drift/failing later evaluation withdraws validation for later forecasts, retaining
earlier receipts. The existing economic min-20 default remains unchanged and is
not a demand-accuracy guarantee. No fixed adaptive threshold is justified yet.

### 6. Explicit CLI, economics and privacy

Add `quote --demand` with explicit registered Change, assessment/ecosystem and
operation identity; preserve all existing default economic invocation/JSON behavior.
Demand output presents evidence state, quantity category, unit/basis, selected
history, assumptions, sample counts, cutoff and next evidence. `explain` replays the
new record using its frozen policy/input references, never today's knowledge.
Idempotent same requests return the same record; conflicting identities reject
atomically. Existing `check` never treats an uncalibrated demand scenario as a priced
Quote or approved financial budget result.

User-supplied rate scenarios require explicit effective date, unit/basis and source.
Keep input/output/cache/reasoning categories distinct and reject missing compatible
components; no inferred cache rate, currency exchange or subscription allocation.
Price scenarios stay estimated. Zero-knowledge output cannot manufacture usage to
price. Human effort/wall time are separate measured quantities, not token conversions.

Rehearsal is opt-in, read-only and bounded by a stated assessment budget. The CLI
accepts a minimized assessment artifact; it does not call a model automatically.
Retain concise dimensions/assumptions and observed overhead, never raw reasoning,
prompts or imaginary test results. Metadata storage is local and allowlisted.
Global learning is a later change with explicit contribution consent independent
of login. No outbound sharing is part of this implementation.

## Risks / Trade-offs

Sparse history -> expose sample counts and stay unvalidated. Confounded transfer ->
directional scopes and held-out chronological tests. Accounting/leakage -> versioned
policies, complete aggregates and immutable availability/cutoffs. Bounded rehearsal
can consume more than it saves; report overhead rather than promising a reduction.

## Migration Plan

Implement offline contracts/synthetic behavior first after separate authorization;
approved readers then enable individual native lanes. Back up/export before additive
SQLite changes, test old-record reads and recovery, and preserve earlier algorithms.
Rollback code with a compatible backup, never delete evidence to force compatibility.

## Verification

Derive failing tests from [requirements](specs/adaptive-demand/spec.md), record actual
red/green evidence, then applicable quality/LINUX gates and independent review.
Local offline implementation is recorded in TDD_EVIDENCE.md. Empirical accuracy,
native approval and final acceptance remain unclaimed.

## Authorized implementation contract — 2026-10-11 (Europe/Berlin)

The maintainer selected the offline #35 implementation. Supplied assessment and
ecosystem records enter through existing `bind --import-artifact`; `quote --demand`
references their record IDs. Money flags are required only in economic mode; mixed
requests reject before persistence. Explicit request IDs retain atomic retry semantics.

Add `demand/v1` versioned payloads within the unreleased `changecost/v1` envelope:
assessment, ecosystem, measurement policy, per-Run demand observation, matched
comparison, transfer hypothesis, validation policy/receipt and demand forecast.
SQLite layout stays version 2; old records remain readable and backups preserve
local receipts. Older executables must use compatible backups, not newer bundles.

Only the closed `synthetic-demand/v1` measurement policy can establish offline
full-Change demand truth. Every bound attempt needs terminal outcome, interval,
explicit evidence binding and complete final coverage. Native policy strings do not
approve readers or coverage. Corrections use predecessor chains; forks reject.

Select complete six-dimension matches, then broad known-ecosystem history. Unknown
material ecosystem fields never establish equivalence. Learning displays observed
minimum/median/maximum and n, without calibrated percentiles. Exact rational
arithmetic preserves nonterminating ratios; display rounding is separate.
Eligible target history produces the principal learning result; a directional
median-ratio transfer remains a separate candidate with residuals and pair counts.

Validation requires an explicit numerical rubric registered before evaluated work
and a locally computed measured receipt for its exact ecosystem/component/population.
A synthetic verification API exercises registration, chronological measured receipt
checks and later withdrawal without asserting native accuracy. #17 owns the actual
pilot protocol/rubric and measured comparisons; missing/failed receipts leave
forecasts unvalidated. Target Changes are excluded from receipt cases and bridges.

Offline acceptance does not require #36 or #17 delivery. Native integration requires
its independently approved reader/policy; #17 protocol preparation must precede
evaluated outcomes. Actual live comparisons and publication remain later stages.
