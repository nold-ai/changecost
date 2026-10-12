# Local adaptive demand forecasting — offline implementation

Status: offline implementation authorized **2026-10-11 (Europe/Berlin)**, locally
implemented on the feature branch; acceptance and native collection remain pending.
The CLI provides separate demand forecasts alongside economic Quotes and advisory
checks. This document describes the
[adaptive-demand change](../openspec/changes/forecast-01-local-adaptive-demand/proposal.md).

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

Optional prices cover one explicitly supported component at a time and remain
estimated scenarios, with source, effective date, rate and currency retained.
Supplied read-only assessment rehearsal includes a same-unit budget and overhead;
its imagined outcomes and overhead never become task truth. Unknown fields such
as raw prompts or reasoning are rejected. Free-text evidence notes are bounded,
not automatically redacted: supply only minimized non-sensitive descriptions.

No publication or source approval follows from these offline tests. See
[implementation evidence](../openspec/changes/forecast-01-local-adaptive-demand/TDD_EVIDENCE.md)
for actual checks and outstanding Linux/review gates.
