# Prepare a live assessment

Issue [#17](https://github.com/nold-ai/changecost/issues/17) remains active.
The maintainer selected preparation on 2026-10-27 Europe/Berlin. This guide prepares
an operator record and future execution checks. It authorizes no collection,
inspection of real outcomes, runtime implementation, source admission, or publication
of private data. No live assessment has run through this procedure.

The offline evaluator merged in [PR #48](https://github.com/nold-ai/changecost/pull/48).
Its [reproduction command](evaluation.md) accepts synthetic providers and always
concludes `synthetic_only_not_yet_validated`. Even a complete dataset cannot make
that command a live evaluator. A safe real-evidence entrypoint and its source and
measurement authority remain missing. Never relabel real records as synthetic or
rename a flag to bypass this boundary. Do not enable paid infrastructure or automatic
collection to prepare this assessment.

## Record decisions before target outcomes

Create a private operator record outside Git. Keep each pending field explicitly
`pending`; no default implies approval. Preserve the original record and version
every amendment. Register the protocol before target outcomes and freeze initial
forecasts before assessed work. Record any prior analyst exposure to target outcomes.
Prior exposure makes those cases historical or exploratory, rather than prospectively
registered. A retrospective timestamp cannot repair that exposure.

Complete these fields with the responsible people before live work:

| Field | Current value | Required decision or evidence |
| --- | --- | --- |
| Sponsor, operator, analysis owner, independent reviewer | pending | Name roles and who accepts the protocol and evidence. |
| Lane and prospective or historical design | pending | Select one provider and source snapshot. Record excluded lanes and prior target exposure. |
| Evaluation, collection, source, measurement, publication approvals | pending | Retain separate dated references and exact permitted scope. One grant cannot replace another. |
| Reader and measurement policy | pending | Record versions, profile and evidence digests, acquisition filters, complete coverage and settlement/finality rules. |
| Cohort and independent sampling unit | pending | Freeze eligible Change IDs or an outcome-independent enrollment rule, repository, task kind/context dimensions and ecosystem. |
| Attempt coverage and dependence | pending | Link every Run, retry, child attempt, failure and abandonment. Group dependent repeat-task Changes. Attempts are not independent Changes. |
| Private custodian, consent and access | pending | Record dataset location, permitted fields/purpose, consent, retention, withdrawal and aggregate disclosure permission. |
| Forecast and truth cutoffs | pending | Record separate cutoffs, local availability ordering, selected revisions and complete dependency references. |
| Methods and decision rubric | pending | Freeze the values below with rationale and independent review before outcomes. |
| Real-evidence entrypoint | unimplemented | Specify and separately authorize accepted inputs, authority checks, safe output, deterministic replay and isolated store behavior. |

Keep raw billing, prompts, transcripts and identifiable bindings outside Git.
The repository is public as confirmed on 2026-10-27; its private project does not
protect committed data. Record a publication review against the actual proposed
aggregates, even if collection and analysis are already permitted.

## Freeze the private manifest

Use this documentation-only checklist for the operator record. It is not an accepted
runtime schema, admission payload or authorization token. References point to private
original evidence held by its custodian; copying a reference grants no authority.

- Protocol ID/version, original registration time/digest, reviewer, registration
  receipt, prior outcome exposure and amendments.
- Separate evaluation, collection, reader/source, complete measurement, consent and
  publication references; exact source profile/version/digest and permitted fields.
- Cohort ID, enrollment rule, independent unit, dependent groups, Change/Run/attempt
  references, outcome provenance, ecosystem/component/unit/basis and model/harness versions.
- Source snapshot digests, private manifest digest, origin timestamps and destination
  availability, forecast cutoffs, truth cutoffs, selected revisions, correction,
  overlap/deduplication and full-coverage dependencies.
- Registered methods, rubric/formula versions, minimum independent truth count,
  coverage target/tolerance, uncertainty method, signed underestimation and width
  limits, paired baseline rule, overhead budget/units, exclusions and withdrawal rules.
- Code/environment/lock fingerprints, approved invocation, input/store byte counts,
  timing scope/repetitions, report digest, unknown/excluded counts and disclosure review.
- Continue/pivot/not-yet-validated decision, rubric outcomes, counts/units, next evidence
  and scoped receipt reference or explicit reason no receipt exists.

Freeze one initial forecast per Change. Preserve later forecasts separately.
Exclude the target Change and every linked attempt and revision from its peers,
transfer calibration and validation inputs. Keep truth corrections known by the truth
cutoff without leaking them into forecast history. Origin timestamps do not establish
when a destination learned the evidence. Retain all enrolled cases and reasons for
missing, excluded, failed and abandoned outcomes.

## Set the rubric and denominators

Use broad same-ecosystem history, dimension-profile analogy and directional
matched-pair transfer. Treat rehearsal as an optional separately budgeted method.
Do not select pairs or policies after seeing outcomes. Freeze these live rubric
values before outcomes; their current values are pending, not inferred from examples:

| Rubric field | Current value or fixed contract |
| --- | --- |
| Economic comparable-history minimum | Fixed 20, same identity, population, eligibility, cutoff and quantile method for candidate and baseline. |
| Economic availability | Both priced or both unpriced under shared repository fallback. A mismatch stops accuracy reporting. |
| Independent complete truth minimum and rationale | pending; disclose dependence and uncertainty. No count is proven sufficient for calibration. |
| Coverage target, tolerance and uncertainty method | pending; report numerator/denominator and supported quantities only. |
| Signed underestimation, width and paired baseline limits | pending, in registered component units. |
| Rehearsal overhead budget and net-benefit decision | pending; measure overhead separately and subtract only compatible units. |
| Missingness/exclusion and drift withdrawal rules | pending; freeze before outcomes and retain amendments. |

Score economic accuracy only on paired priced cases with complete eligible truth.
Count jointly unpriced and unknown/partial/provisional truth outside that denominator.
A token counter cannot establish billing. Finite Codex diagnostics cannot establish
complete Change/Run/child demand or money. Treat adaptive observed summaries,
supported empirical quantiles and transfer scenarios separately. Compare errors on
shared complete truth and report additional adaptive availability independently.
Scenario arrays and observed ranges do not become calibrated quantiles.

Count all eligible observed records for attribution, including unbound and unknown
money. Count linked retries once in their applicable totals. Divide abandoned terminal
spend by all terminal spend in the same unit and basis. If any whole-population
amount is unknown, or the denominator is zero, report an undefined share with reasons.
Never substitute zero for unknown truth. Report rehearsal net benefit as paired
absolute-error reduction minus measured overhead only when component units match.
Otherwise report it as undefined. Record input/store bytes, environment and repeated
wall time with an explicit timing boundary; no runtime cost or duration is known yet.

## Close the live tasks with actual evidence

Follow these gates in order. Leave each task unchecked until its own evidence exists.
The existing [task list](../../openspec/changes/pilot-02-calibration-evaluation/tasks.md)
also retains historical TDD and full-story integration obligations.

| Task | Evidence needed to close it | Current state |
| --- | --- | --- |
| 3.0 | Separately authorized implementation and reviewed runnable real-evidence boundary, with safe inputs, authority validation, isolated storage and replay proof. | Unstarted. Synthetic CLI/API cannot supply it. |
| 3.1 | Current prerequisite evidence, selected lane authorization, exact reader/source approval, complete measurement policy and permitted cohort/consent. | Pending operator and authority decisions. |
| 3.2 | Real replay through the approved boundary with frozen manifest, registration, actual report, environment, input/store bytes and separately measured wall time. | Blocked by 3.0 and 3.1. No live command is supplied here. |
| 3.3 | Shared eligible truth, independent/dependent counts, additional availability, uncertainty, all-outcome denominators and compatible-unit rehearsal benefit. | Pending authorized execution and sufficient truth. |
| 3.4 | Reviewed publishable aggregate calibration/width where supported, attribution, abandoned share, unknowns and baseline, with every count/unit/denominator. | Pending results and disclosure permission. |
| 3.5 | Actual rubric outcome and continue/pivot/not-yet-validated rationale in findings.md, with gaps and next evidence. | Pending results. |
| 3.6 | If criteria pass, genuine supported measured receipt bound to exact ecosystem/component/population/input/policy versions and review/withdrawal evidence. Otherwise record no-receipt reason. | Pending supported receipt path and passing evidence. |

## Stop or withdraw when evidence fails

Stop the affected lane on absent authorization/consent, unsupported source bytes or
versions, missing complete-coverage policy, privacy breach, chronology mismatch,
unreviewed changed inputs or an unimplemented capability. Preserve safe private
evidence and record the gap. An unavailable lane does not block a separately ready lane.

An economic availability mismatch stops accuracy reporting for that comparison.
Inadequate independent truth, wide uncertainty, non-improvement or excessive overhead
leaves the conclusion not yet validated. Prior exposure prevents a prospective claim.
A failed rubric produces no passing validation receipt. Drift requires scoped
withdrawal; a sample count or synthetic pass cannot override these decisions.

Confidence is high for the current synthetic boundary and medium for live readiness,
because the operator, lane and dataset remain undecided. The main failure modes are
leakage, selection bias and inflated authority. Separate immutable cutoffs, complete
denominators and explicit approvals address them. A ready non-native lane may remove
some source blockers but still needs a real-evidence entrypoint. Runtime cost and time
remain unknown. Preparation rollback reverts the planning diff. Future runtime rollback
must preserve private evidence and compatible backups without deleting financial history.

Next, complete the private operator decisions and separately specify/authorize task
3.0. Keep #17 open and active until its actual acceptance and historical obligations
are resolved. This preparation cannot close or archive the change.
