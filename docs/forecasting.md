# Local adaptive demand forecasting — offline implementation

Status: accepted on 2026-10-18 and CLI-archived **2026-10-23 (Europe/Berlin)** after PR #43
and the issue-44 correction in PR #45. Native readers and measured calibration
remain separate.
The CLI provides separate demand forecasts alongside economic Quotes and advisory
checks. This document describes the
[adaptive-demand change](../openspec/changes/archive/2026-10-23-forecast-01-local-adaptive-demand/proposal.md).

Demand quantities, rates and decimal limits use a 4096-digit aligned integer and
fractional representation budget, including coefficients and either exponent
direction. Zero obeys the same bound. Each rational numerator and denominator is
limited to 4096 digits before exact conversion. Unsupported artifacts reject before
import persistence; ordinary exact values and v1/v2 replay remain supported.
Previously admitted values outside this budget now reject typed decoding. Preserve
their original exports and backups for diagnosis; records are never rewritten to
fit the limit. Legacy economic Amount admission is unchanged.

ChangeCost assesses the likely demand of a feature/task/story for individuals,
small teams and enterprise developers using supplied minimized artifacts. Native coding-agent readers remain planned.
No administrator export, additional telemetry, paid plan upgrade or global database
is required. Missing measurements stay missing; a free account is not evidence of
zero resource consumption.

## Evidence states

| State | Useful output | Limits |
| --- | --- | --- |
| Zero knowledge | Task-demand dimensions, assumptions and next evidence | No empirical token estimate, calibrated percentile or inferred charge |
| Learning | Actual comparable observations, sample counts and provisional scenarios | Sparse history is not validated accuracy |
| Transfer hypothesis | Scenario mapped through observed ecosystem comparisons | Mapping is directional/scoped, with confounding and uncertainty |
| Validated forecast | Empirical ranges for a tested ecosystem/component/population | Requires pre-registered evaluation and measured validation, not count alone |

The initial dimensions are scope, coupling, novelty, ambiguity, validation burden
and context demand. They remain separate low/moderate/high/unknown assessments,
with evidence and provenance. Ecosystem snapshots separately record provider,
surface, model/version, runtime, reasoning settings, harness and review workflow.
Changed or unknown contexts cannot inherit validation silently.

The explicit `quote --demand` mode creates a separate versioned forecast;
`explain` shows its frozen inputs, method, evidence state and limits. See the [CLI examples](cli.md#offline-demand-forecasting). Existing economic Quote invocation and budget
checks keep their present contract, including the synthetic billed-USD boundary.

## Learn without inventing outcomes

Freeze the task profile before implementation. Explicitly bind source evidence to
Runs and Changes, include retries and abandoned attempts, and retain corrections.
Only eligible complete measurements supply full-task learning truth. Partial logs,
unbound work, imaginary tests and absent counters remain diagnostic/unknown.
Complete observations cover the latest corrected interval and the Run's immutable
observed start when present. An absent observed start uses the current interval;
the known start must lie between both observation endpoints, including equal
endpoints. A corrected window ending before that point is incomplete.
registration time and superseded interval bounds do not become coverage boundaries.
Repeated imports and source revisions must not create additional training samples.
Earlier forecasts remain immutable; new evidence updates later assessments.

Older ecosystems remain candidate history. Matched comparisons, preferably the
same frozen task under both ecosystems, support explicit median-ratio hypotheses. Zero donor denominators remain diagnostic. A simultaneous task/model/harness change cannot establish
a model-only effect. Mapped observations remain hypothetical; actual target
history is preferred as it accumulates. No universal complexity-to-token coefficient
or automatic bridge chain is assumed.

Tokens, credits, human effort, wall time, estimated money and billed charges remain
distinct. Optional price scenarios require explicit compatible rates and basis;
subscription allowance cannot be inferred from list-price dollars.

## Rehearsal, privacy and validation

A user may supply a minimized read-only LLM assessment. Its own usage/overhead is
reported separately; hidden reasoning is not free simulation and imagined execution
is not measured truth. The CLI does not invoke a model automatically.

Local learning comes first. Future shared learning requires separate contribution
consent; login does not authorize sharing. No prompts, source transcripts or raw
reasoning are retained for learning.

[Evaluation #17](../openspec/changes/pilot-02-calibration-evaluation/proposal.md)
will compare historical-only, dimensional, transfer and rehearsal-assisted methods
chronologically. It reports calibration, underestimation, width, availability,
unknowns and overhead. The existing minimum-of-20 economic Quote default remains
unchanged and does not validate the new forecast.

Confidence: high in these boundaries, medium in practical forecast benefit.
Accounting, source coverage and transfer utility remain To-Validate. See
[research and architectural decisions](research/adaptive-demand-evidence.md).

## Delivered offline policy

Only `synthetic-demand/v1` on registered `synthetic/fixture` Runs is eligible.
Token categories require `tokens/observed`; wall time uses `milliseconds/elapsed`
and effort uses `seconds/measured`. Native evidence labels, declared completeness
and imported validation claims cannot approve a lane. Full terminal Change truth
sums every bound attempt, including failed retries and abandoned Changes. Any
missing, incompatible or incomplete attempt excludes the Change from learning.
Corrections select one current revision; forecast replay retains the old cutoff.

Complete six-dimension matches are selected first; otherwise a broad baseline
uses the known ecosystem. Output exposes observed minimum, median, maximum and
count, never calibrated percentiles. New observed-summary/v2 forecasts disclose
dependence when historical peers repeat each other's scope or the target's scope,
including one matching historical Change. Observed-summary/v1 snapshots retain
their original disclosure and exact replay; quantities and sample counts are unchanged.
Matched comparisons expose directional ratios, pair/donor counts, mapped scenarios
and residuals. Donor cohorts select complete same-dimension source history
independently from calibration pairs; their references/counts remain visible.
Target observations stay primary and donors never increase target n.
Competing overlapping hypotheses remain diagnostic, without automatic bridge chaining.

Task and ecosystem snapshots must be locally available before work. The `initial`
flag records cutoff-visible evidence: no registered attempt, or only known future
work bounds. Validation separately checks each candidate and baseline cutoff against
complete truth work bounds, including retrospectively registered Runs; equality or
later capture rejects measurement. Original forecast records and their snapshot
replay remain immutable. Retrospective portable imports may be inspectable without being eligible local
learning history. Backdating producer timestamps cannot establish local availability.

The offline API can exercise explicitly registered synthetic validation rubrics;
there is no automatic rubric, sample-count promotion or CLI evaluation command.
A receipt requires reproduced local initial forecasts, complete truth and a rubric
registered before assessed tasks. If a baseline is required, its exact frozen input
references must match the candidate, even when their capture clocks differ.
The latest overlapping rubric controls later applicability; equally available
competing policies leave validation unavailable. drift, failure or a
missing local passing receipt withdraws validation. Historical records retain their
original status. #17 owns actual pilot protocol registration, numerical thresholds,
chronological comparisons and measured validation before native evaluated outcomes.

Validation history includes imported structural predecessors. A new local receipt
links the unique cutoff-visible head but computes its own metrics from locally
eligible forecasts and truth. Imported claims never grant local validation authority.
A cutoff-visible foreign head prevents an older local receipt from representing
the current forecast lineage. A cutoff-unavailable structural head blocks new
receipt construction; forecasts still use their cutoff-visible history, and earlier
frozen forecasts replay unchanged.

Optional prices cover one explicitly supported component at a time and remain
estimated scenarios, with source, effective date, rate and currency retained.
Supplied read-only assessment rehearsal includes a same-unit budget and overhead;
its imagined outcomes and overhead never become task truth. Unknown fields such
as raw prompts or reasoning are rejected. Free-text evidence notes are bounded,
not automatically redacted: supply only minimized non-sensitive descriptions.

No publication or source approval follows from these offline tests. See
[implementation evidence](../openspec/changes/archive/2026-10-23-forecast-01-local-adaptive-demand/TDD_EVIDENCE.md)
for accepted checks, preserved failures and remaining historical review limits.

New forecasts use `observed-summary/v4`: chronology uses the current Interval and
DemandObservation revision heads visible at each cutoff, together with an immutable
known Run start. A corrected erroneous bound does not permanently exclude otherwise
eligible history. A v3/v4 forecast cannot use a validation receipt supported by its own
Change, including selected candidate/baseline peers, transfer donors, eligible bridge
owners and recursively selected validation receipts. Broad frozen metadata and
structural predecessors alone are not training support.

Stored v1/v2/v3 forecasts replay their exact original rules. The existing private local
computation request distinguishes original `demand-validation/v1` receipt measurement
from `demand-validation/v2` current temporal measurement and new
`demand-validation/v3` measurement with strict rubric preregistration. New live
receipts use current truth rules even with legacy candidates. Exact legacy retries preserve their request and payload.
These request markers are local provenance, not portable authority or schema fields.
A rollback of the default must retain v4 decoding/replay for already saved or exported
records, or restore a compatible pre-v4 backup when reverting the complete code.

A rubric must be declared and effective strictly before the evaluated assessment's
recorded, effective and local capture times, as well as arrive earlier in local
sequence ordering. Equality of declared timestamps is insufficient evidence of
preregistration. Importing a future rubric early and waiting until after evaluation
cannot establish authority. Equal local capture times can qualify when sequence
order and strictly earlier declared timestamps prove the required ordering.

New receipts and v4 forecasts enforce the same check through selected nested
validation receipts. A legacy receipt with valid timing remains usable; an invalid
one retains historical replay but cannot promote a current forecast. Rejected new
validation writes neither records nor computation markers. These are synthetic
offline controls, not evidence of native predictive accuracy or pilot approval.

## Finite Codex diagnostics, 2026-10-24

The separately authorized exact Codex snapshot reader stores diagnostic NativeUsage
and unbound Evidence. It creates no assessment, ecosystem, demand observation or
measurement policy. Even after exact manual binding, the existing synthetic-only
learning and financial guards remain unchanged. Broader readers, native demand
projection, calibration and evaluated outcomes need their own authorization and
evidence. See [finite import](settlement.md#import-the-approved-finite-codex-diagnostics).
