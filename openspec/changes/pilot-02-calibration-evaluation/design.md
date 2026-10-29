# Design: Evaluate attribution and chronological quote calibration

## Current remaining scope, 2026-10-29 Europe/Berlin

The shipped synthetic evaluator contract is synchronized in main through CLI archive `2026-10-29-reconcile-accepted-workflow-and-offline-evaluation-specs`. This active change retains the real-evidence boundary, live/native extensions, actual assessment, conditional integration and incomplete historical proof. Earlier proposal/design text below remains planning history. The synthetic entrypoint still rejects native usage and non-synthetic providers, and no live work is complete.

## Context

See [proposal](proposal.md) and [capability spec](specs/pilot-evaluation/spec.md).
The Python runtime, normalized reconciliation, economic Quotes and advisory
workflow are delivered. This design describes future source/evaluation behavior;
financial verification remains limited to synthetic billed USD.

## Goals / Non-Goals

**Goals:** Make the specified capability local, reproducible and explicit about missing evidence.

**Non-Goals:** No fabricated live measurements, collection during planning, product launch claim, employee ranking, opaque ML training, enforcement threshold or paid infrastructure. Deterministic analogy/transfer and optional supplied rehearsal assessments are in scope.

## Decisions

1. Replay quotes in timestamp order using only revisions available at each cutoff in the Quote's store context. Apply destination availability to every dependency; portable origin timestamps cannot establish local historical knowledge. Report cross-store replay_unavailable separately and exclude it from scoring without backdating imports. Both candidate and repository-wide baseline use identical unit/basis, eligibility, population, minimum count of 20 and quantile method; the baseline omits narrow cohort features. The candidate's final repository fallback is exactly the baseline cohort, so availability must match: both priced when it meets the minimum, otherwise both unpriced. Score paired priced cases and report jointly unpriced cases with counts/reasons. If observed availability differs, report a comparison/configuration error and stop accuracy reporting for that run rather than treating it as a supported pilot outcome.

Use one initial pre-run Quote per evaluated Change, with the frozen feature snapshot
and cutoff defined by the [estimator contract](../archive/2026-10-04-quote-01-empirical-estimation/design.md#feature-selection-and-capture-time).
Later diagnostic quotes do not create extra observations. Exclude the target Change and every linked attempt and revision from its own historical peers, transfer calibration and validation inputs. Report later updates separately, including updates after the target becomes terminal. Missing features lead to
repository fallback for the candidate, not removal of baseline-eligible history.

2. Report p50/p90 empirical coverage as count(actual <= quantile)/priced comparable count, with numerator and denominator; report signed errors and interval width p90-p50 in original units. Include sample-count uncertainty (for example Wilson intervals for coverage), not a claim that observed 90% is a guarantee. Require the same full-change coverage contract for evaluation truth as for historical quote peers; reconciled partial intervals are not actual total-change costs. Freeze and report a separate truth as-of cutoff and selected complete settlement/coverage revisions for reproducibility, including later corrections known at that cutoff without leaking them into quote-time history. Unknown, partial and provisional Codex thread counters cannot establish full-change demand truth or billing authority. Cases with unavailable complete truth remain in reported exclusion/unknown counts, outside accuracy denominators; never score them as zero.

3. Attribution reports provider-backed bound, manually bound and unbound record counts separately, plus their comparable economic totals. Denominator is all eligible observed records, not only those already bound. Missing money contributes to unknown counts. Report duplicate/conflict/pending-correction rates and completeness alongside apparent binding coverage.

4. Abandoned expenditure is abandoned terminal-change amount divided by all terminal-change amount within the same unit/basis; zero or unknown denominator yields undefined, not zero. Include linked retries in both applicable totals. Outcome provenance must be explicit.

5. Measure CLI wall time in milliseconds and local storage/input bytes for stated fixture sizes and runtime environment; report repeated measurements with method rather than universal speed claims. No external telemetry service is required.

6. Pre-register the protocol and decision rubric before live results: compare paired calibration and width against the baseline; report feasibility and overhead separately. If intervals/sample size do not support improvement, classify as not yet validated. A source unavailable at the gate is a recorded coverage gap, not synthetic live support; the 2026-10-07 revision makes adapter prerequisites lane-specific without approving unavailable mappings. No fixed sample target from the research guarantees success.

## Runnable outcome and reuse

After separate implementation authorization, a contributor supplies portable
synthetic history and a versioned, pre-registered protocol to the local CLI or API
and receives a deterministic aggregate report. The report compares frozen initial
forecasts against the broad repository baseline, separates adaptive availability,
and records omitted cases with truth eligibility and exclusion reasons. Stable
inputs, destination availability and protocol versions produce identical report
content. Measured wall time and environment belong in a separate section.

Reuse `src/changecost/quotes.py` replay and destination-availability checks and
`src/changecost/demand.py` validation computation. Existing synthetic receipt
computation does not replace pilot protocol registration. Add only missing case
orchestration, aggregate metrics and report output. Preserve the delivered economic
and adaptive contracts rather than introducing a parallel estimator or validation
engine. Document invocation in `docs/pilot/evaluation.md` and qualified conclusions
in `docs/pilot/findings.md`. Both documents were absent at the historical preparation baseline. They now exist
and describe the offline implementation merged in PR #48.

Accepting the offline protocol and synthetic report proves reproducibility only.
It does not complete live assessment, approve collection or produce a measured
full-change calibration receipt. Each live lane needs separate explicit
authorization and complete eligible truth before the registered rubric can
support a scoped accuracy conclusion.

## Preparation checkpoint, 2026-10-26

This documentation-only preparation uses fresh main
`ffd8dff568f11e6e9283b00badbce6c98a0b5580`. The integration owner is the sole
writer for lifecycle, correlated docs and issue synchronization. The scoped
artifact writer owns only this change's proposal, design, tasks and capability
spec. No runtime boundary changes, runtime probe or new provider approval apply.

Inspection confirms reusable `quote_reproduced` and `inspect_quote` in
`src/changecost/quotes.py`, and `compute_validation`, `validation_reproduced` and
`case_metrics` in `src/changecost/demand.py`. The missing deliverable is evaluation
orchestration and reporting. The independent upfront obligation review identified
this distinction before these edits.

Native blockers #11, #12, #15, #16 and #35 are closed. PR #47's four changes are
archived with synchronized main specs. Their 12 unchecked historical tasks and
the narrow Linux Python 3.11 native timeout UNKNOWN exception remain limitations.
Archival does not turn them into passing evidence. Finite Codex diagnostic usage
and provisional thread summaries do not provide complete evaluation truth.

Primary risks are leakage across availability cutoffs, selection bias from omitted
truth, and synthetic results misrepresented as calibration. Frozen cutoffs,
explicit denominators and separate live acceptance address those risks. No
external capability claim is added. Relevant checks are selected strict OpenSpec
validation and the integration owner's documentation gates and affected scope
review. No product tests are claimed for this preparation. Future runtime cost
and duration remain unmeasured. Roll back only this preparation's artifact diff,
preserving archival and unrelated edits.

## Dependencies and evidence

- [forecast-01-local-adaptive-demand](../archive/2026-10-23-forecast-01-local-adaptive-demand/proposal.md)
- Delivered core-02 #11 and reconciliation #12.
- Approved readers #13/#14 and Codex/Claude are prerequisites only for their respective native evaluation lanes, not universal gates.
- [quote-01-empirical-estimation](../archive/2026-10-04-quote-01-empirical-estimation/proposal.md)
- [workflow-01-advisory-ci](../archive/2026-10-06-workflow-01-advisory-ci/proposal.md)

Shared boundaries and current provider evidence are recorded in the
[source assessment](../../../docs/research/pilot-source-assessment.md).
No provider-specific mapping becomes supported merely by appearing in this plan.

## Risks / Trade-offs

- Selection bias → report unpriced and unbound cases with full denominators.
- Leakage → chronological revision-aware replay for both methods.
- Small or unavailable evidence → uncertainty and not-yet-validated conclusion, never invented measurements.

## Migration Plan

After separate implementation authorization, land this change in dependency order
with spec-derived failing and passing evidence. Update docs/pilot/evaluation.md, docs/pilot/findings.md, and docs/providers/source-feasibility.md.
Use synthetic fixtures before any authorized real-data evaluation. This is unreleased;
there is no deployed service to migrate. For local schema changes, export/backup
before migration and validate recovery without deleting the previous data.

Rollback the implementation commit if its checks fail; restore a compatible local
backup rather than forcing an older program to write a newer database. Planning
rollback is a commit revert plus closing the associated issue, preserving history.

## Verification

Each requirement has Given/When/Then scenarios. Exercise negative paths and privacy
boundaries alongside the success cases. Run strict OpenSpec validation and applicable
repository gates; record actual results, not anticipated test or review outcomes.

## Adaptive-demand evaluation — 2026-10-07

The existing economic Quote comparison above retains matched availability,
min-20/identity/population and complete truth requirements. Adaptive methods have
different justified availability; report zero_knowledge/learning/transfer/validated
counts separately, compare errors on shared eligible measured truth, and report
additional forecast availability instead of declaring it a configuration error.

Register the protocol/version and promotion rubric before target outcomes:
minimum independent full-change truth count, nominal coverage/tolerance and its
uncertainty, signed underestimation limits, width, baseline comparison, overhead,
ecosystem/component/population and applicable measurement versions. No adaptive
count threshold is validated yet. Without a registered rubric and passing measured
receipt, results remain learning/hypothesis, never validated_forecast.

Compare broad same-ecosystem history, exact dimension-profile analogy, directional
matched-pair transfer and optional rehearsal-assisted assessment. Retain one initial
forecast per Change plus separate update diagnostics. No donor pseudo-samples or
post-hoc pair/policy selection. Evaluate new models/harnesses, same-task bridges,
confounded scope changes, useful and harmful transfer, target-only preference,
withdrawal after drift, and observed/imputed/partial/unavailable truth separately.
Freeze the truth revision/cutoff independently of input availability. Economic and
native demand truth require their respective complete coverage policies; full
token truth need not contain billed money. Partial counters cannot establish total
demand. Include abandoned/retried work and outcome-specific denominator breakdowns.

Rehearsal consumes separately measured resources; report assessment overhead and
net forecast benefit. Imagined results and paid implementation probes are not native
ground truth for pre-execution assessment. Record p50/p90 coverage only where a
method actually emits supported empirical quantities; qualitative cold starts are
availability/decision observations, not fabricated zero-error predictions.

Synthetic/offline protocol can be implemented before native readers. Each live
lane requires its approved reader/policy and separate evaluation authorization.
One unavailable provider cannot block another. Register, approve, implement and
evaluate are distinct statuses; no native readiness or accuracy is claimed now.

## Authorized offline implementation synthesis, 2026-10-26

The maintainer now authorizes offline tasks 2.1 through 2.7. Live assessment,
provider admission, merge and release remain separate. The sole implementation
writer owns the runtime delta until handoff; verification owns aggregate checks.

The selected design uses a portable Bundle, ordered deliveries, one forecast and
one truth checkpoint per Change, and optional diagnostic update checkpoints.
`evaluate_synthetic(history, protocol, measure_runs=0)` owns strict parsing and a
disposable Store with an injected clock. The additive `evaluate-synthetic` command
prints a safe JSON report without opening the ordinary application database.
No portable record kind or persistent schema migration is added.

Economic comparison reuses `quotes.estimate`, its peer eligibility and nearest-rank
quantiles. An optional repository-only selector defaults to existing behavior.
The report-only baseline uses the candidate's exact cutoff and fixed minimum 20.
Imported forecasts retain foreign authority and remain replay unavailable.
Truth is scored when its checkpoint occurs and retained before future deliveries.
Scored and omitted truth are distinct immutable outcomes with cutoff, revision,
dependency and linked-attempt references. Generated destination IDs are normalized;
portable input references are retained. Any economic availability asymmetry
suppresses every accuracy metric for that run.

Adaptive observed summaries and transfer scenarios have separate denominators.
All new measurement calls explicitly use observed-summary/v4. Scenario diagnostics
use the median, minimum and maximum of the emitted scenario array and exact signed
point error, never observed quantiles or measured-validation receipts. Rehearsal
uses its own same-assessment broad comparator. Net benefit subtracts overhead from
absolute-error reduction only when units match. Dedicated fixture tests exercise
local successful validation, later overlapping failure and scoped future withdrawal.

The protocol registers exact identities, formula versions, coverage Wilson 95%
intervals rounded to six decimal places, promotion limits and source gaps before
target assessments/work. Synthetic provenance is an assertion, not a real-data
detector. Unsupported native kinds and unknown fields reject with safe errors.
The permanent conclusion is synthetic_only_not_yet_validated.

The critical proofs are foreign import refusal, exact 20-peer repository fallback
and unchanged results after later truth corrections. The first fixture expects
USD 10 p50, USD 18 p90, USD 8 width and USD -5 signed p50 error against USD 15
truth. Test those before expanding report metadata. Main remains
ffd8dff568f11e6e9283b00badbce6c98a0b5580. Existing archive and planning edits are
preserved. No new external costs apply; execution overhead remains unmeasured.
Rollback removes the additive evaluator and optional selector without migrating
or deleting user data.


## Offline protocol review and boundary correction, 2026-10-27

Independent documentation review accepted protocol `synthetic-20261026-v1` for
synthetic-only evaluation at prospective tree
`81c39ff0ea8447b9b44558cc1917270254d41360`. Its reviewed formula is
`exact-errors-wilson95-scenario-median/v1`; all four methods, scoped policy rubric,
registration/arrival ordering and separate forecast/truth cutoffs are concrete.
Task 2.1 is therefore complete for the offline scope. The review and actual
correction RED/GREEN evidence are recorded in [TDD_EVIDENCE.md](TDD_EVIDENCE.md).
Historical compound TDD gaps and unauthorized Stage 3 live assessment remain open.

Numeric bounds cover the Unicode decimal digits accepted by existing numeric
models before those models or exact arithmetic run. A central traversal checks
component unit/basis identifiers, including selected policy and nested rehearsal
budget/overhead, before report generation. These are bounded synthetic input
contracts, not proof that caller-supplied records are fictional.

## Live preparation checkpoint, 2026-10-27 Europe/Berlin

The maintainer selected "Prepare the live assessment; keep #17 active" and chose
a planning PR. This authorizes documentation and lifecycle reconciliation only.
The offline synthetic CLI/API is merged in [PR #48](https://github.com/nold-ai/changecost/pull/48)
at `401e43ed63a9da3e39f55fc29d1e7160d1d06d2e`. Earlier local-delivery and missing-document
claims above describe their dated baseline, not current delivery status.

The [live assessment guide](../../../docs/pilot/live-assessment.md) defines the
private operator decisions, frozen documentation-only manifest, rubric and per-task
closure evidence. The chosen lane, cohort, independent truth minimum/rubric values,
consent and separate evaluation/source/complete-measurement/publication approvals
remain pending. Source approval cannot confer measurement or evaluation authority.
The finite Codex admission is not complete Change/Run/child truth. The existing
economic and demand coverage policies and evaluator accept synthetic evidence only.
A separately authorized real-evidence boundary remains unimplemented even if a
permitted complete dataset becomes available. No new schema, live endpoint, code
flag, provider admission or collection is introduced by this preparation.

Freeze registration before target outcomes, disclose prior exposure, and preserve
original-store authority and destination availability. Use separate forecast/truth
cutoffs, one initial forecast per Change, target/attempt/revision exclusion and
repeat-task dependence. Preserve economic min-20 matched identity/population/
availability and separate adaptive observed/quantile/scenario denominators.
Unknown truth is not zero. All retries and abandonment remain visible; overhead
net benefit needs compatible units. Stop on failed authority, chronology or privacy
checks. A failed rubric produces no passing receipt.

Fresh prerequisite inspection confirms #11, #12, #15, #16 and #35 closed. This is
current readiness evidence only. It does not retroactively satisfy task 1.2's
before-behavior chronology or tasks 2.3-2.6's missing historical prior-RED evidence.
All existing unchecked compound and live tasks remain unchecked. Full integration
and archival remain conditional on actual acceptance; #17 remains active.

Planning rollback reverts this prepared diff. No paid infrastructure, automatic
collection, live dataset inspection or outcome claim is authorized. Relevant checks
are strict OpenSpec, documentation ownership/links, generated index and metadata;
aggregate assurance belongs to verification. Confidence is high for the shipped
synthetic boundary, medium for future readiness pending operator decisions.

## Accepted synthetic contract reconciliation, 2026-10-29 Europe/Berlin

The maintainer requested archival of implemented contracts while retaining genuine
future work. The reconciliation change records the shipped PR #48 synthetic
evaluator in main through native OpenSpec archival. This note is applied only after
that CLI archive and exact main-spec readback succeed. It does not archive or close
#17. The accepted seven requirement identities and 22 synthetic scenarios are
recorded in the reconciliation design. Main now owns their delivered clauses.
The active delta contains full MODIFIED blocks only for complete truth, honest
conclusion and scoped adaptive promotion, plus the unchanged ADDED separate live
authority requirement. The MODIFIED blocks preserve every accepted synthetic
clause and scenario while adding the explicitly future live duties. Other accepted
requirements are referenced in main rather than repeated as ADDED here.

The original delta at source HEAD `5cbe58a892f27c78088a82d95219a0cb57f922df` has
SHA256 `418a7f8d737058b5b011eba0c6b11b0298d82c9bf4c48c5850663d1ca4ffb6d0`. Its original 19 task lines and checkbox bytes are preserved.
Historical task 1.2 chronology and compound prior-RED duties 2.3 through 2.6 remain
incomplete. Current passing synthetic behavior cannot recreate that history.
Live tasks 3.0 through 3.6 and conditional integration 4.1 through 4.3 remain open.
The synthetic entrypoint rejects native usage and non-synthetic providers outright.
It does not ingest real Codex or Cursor records to produce native exclusion reports.
No real-outcome inspection, collection, runtime implementation, passing live receipt,
provider approval or aggregate publication is authorized by this reconciliation.

See the accepted [pilot-evaluation main contract](../../specs/pilot-evaluation/spec.md)
and [live assessment guide](../../../docs/pilot/live-assessment.md). All original
TDD evidence and unchecked historical obligations remain unchanged.
