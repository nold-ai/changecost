# Behavioral evidence pilot

**Status: local review complete; remote validation pending, 2026-09-29 (Europe/Berlin).** The bounded model
and packet checks run, and all four selected faulty/repaired controls detect their
intended violation. Initial and targeted independent review are complete; external current-head review
and supported-Linux gates remain pending. This snapshot establishes detector sensitivity, not general cost savings.

## Observed behavior and scope

The first candidate passed 27 tests: 14 packet scenarios and 13 lifecycle cases.
The reviewed repair passes 31 after adding two packet regressions and two retry
metadata variants within the existing four fault families. Eight fixed
seeds each execute 24 generated operations after two setup operations; one explicit
12-operation trace covers meaningful replay, conflicts, corrections and rollback.
Chronology/import tests and four controls complement those traces. No production
runtime files changed. No genuine runtime defect was found in this bounded sample.
The two accepted architecture findings were design ambiguities repaired before code:
report/spec/oracle/config byte binding, and fault injection at the real exercised boundary.
They are neither runtime bugs nor seeded detections.

The oracle imports no production decision helpers, but its writer inspected APIs and
implementation code beforehand. Independent review must inspect its scenario mapping;
helper independence alone cannot eliminate shared assumptions. Controls use real SQLite,
public operations or the real eligibility path, with identical expectations/projection.
See the [guide](../development/behavioral-evidence.md) for exact bounds and exclusions.

## Actual non-capsule tool comparison

Installed SpecFact CLI 0.55.4, codebase module 0.41.16 and project module 0.41.27
were used against an isolated ignored copy. Original input fingerprints and collection
binding are retained locally. The [sanitized ledger](behavioral-evidence-pilot.json)
records each actual argv, exit, duration and native-output digest. Local raw reports
remain ignored; they are not copied into this document.

| Experiment | Observed outcome | What it establishes |
| --- | --- | --- |
| SpecFact code import | Three bounded invocation forms rejected option ordering (exits 1/2), including the displayed explicit and canonical forms | Import unavailable for this run; no valid inventory baseline |
| Contract inventory | Missing bundle, exit 1 | No inspected contract coverage; not a code defect |
| Drift baseline/fault/repaired | Exit 0 and empty drift output without a valid imported baseline | Unbound status only; cannot evaluate fault sensitivity |
| Pure-Python sidecar | Exit 0; zero routes, zero contracts, no generated harness | No bound lifecycle analysis |
| Repro | Initial output-path setup failure; corrected run failed host tools; explicit PATH ran Ruff but type checking lacked snapshot dependencies and CrossHair launch failed | Incomplete environment/integration evidence; no lifecycle pytest assurance |
| Explicit CrossHair 0.0.107 wrapper | Actual `store.available` fault produced `observed_by(1, 0)` counterexample; repaired predicate confirmed all paths | Selected pure sequence predicate, with both integers constrained to 0–100; no SQLite/public lifecycle coverage |
| Semgrep 1.176.0 | One local eval rule, three actual lifecycle files, zero findings; sentinel one finding then zero repaired | Scanner health and this rule only; no general lifecycle claim |
| Bandit 1.9.4 | Three actual lifecycle files, zero findings; eval sentinel one finding then zero repaired | Generic security scan plus scanner health; no lifecycle fault sensitivity claim |

The original import failure was an invocation issue. The next two commands followed
the native migration hint/canonical form but also failed. Investigation of the installed
parser informed stopping, not an upstream change or compatibility guarantee. All subsequent
empty drift outputs remain unbound; calling them semantic false negatives would overclaim.
Semgrep initially failed host certificate initialization; setting its process-local
`SSL_CERT_FILE` to the existing certificate file enabled the local-rule experiment.
CrossHair/Bandit ran in a disposable temporary environment without changing project locks.
Semgrep reports findings with exit 0 by default; native result counts, not exit alone,
establish sentinel detection. Bandit's sentinel returned exit 1 as expected.

The useful division here is concrete: the independent model exercises four domain
families, a bound CrossHair contract checks one pure predicate, and security rules inspect
selected generic patterns. Inventory/drift/sidecar cannot substitute for a domain oracle.
None of these experiments waives the separate required Linux capsule review.

## Usage snapshot and historical comparison

The experiment begins at **2026-09-29 22:44:09.656 Europe/Berlin**, excluding earlier
retrospective and feasibility discussion in the same chat. Per-response usage is
deduplicated by response identity and accepted only from its containing session;
cumulative counters are not summed. Reasoning is already included in output.
The fixed snapshot below includes both local review rounds, but excludes later
finalization, commit/push and remote validation; it is not total delivery cost. Model labels are observed session metadata, not a billing basis.

At 2026-09-29T21:32:11.834840+00:00, the observed tree consumed
**32,307,872 tokens**: 31,628,800 cached input,
577,823 uncached input and 101,249 output,
across 337 provider responses. There were
1 root task turns and 15 worker task turns.
Elapsed wall time was 48.04 minutes, including parallel work and waits.
Measurement setup accounts for 604,148 tokens;
that worker's later implementation work remains in delivery totals.

| Observed interval | Request tokens | Elapsed minutes |
| --- | ---: | ---: |
| planning readiness | 7,885,602 | 11.43 |
| implementation experiments | 13,028,065 | 22.66 |
| review round 1 | 4,848,244 | 4.66 |
| repair verification | 4,182,113 | 7.23 |
| review round 2 | 1,488,286 | 1.09 |
| finalization | 875,562 | 0.97 |

Intervals use observed handoff/review boundaries and include all concurrent agent
responses, so they are chronological slices rather than exclusive task-cost attribution.

Actual billed cost is **unknown**. External bot inference, host compute and any
unrecorded tool inference are not priced. Two local review rounds found and closed three defects; final native review and
savings conclusions remain pending. The session counters remain authoritative.

Historical completed totals reconstructed on 2026-09-29 were 302,957,968 tokens for
foundation PR #22, 426,090,919 for bounded-review PR #24 and 148,246,933 for Core-02
PR #25. Their pre-PR totals were 23,050,831; 27,399,003; and 45,957,016 respectively.
These are different changes with different scopes and completion boundaries, not
matched trials. This incomplete pre-PR observation cannot establish causal savings,
statistical significance or a billed-cost reduction. Historical methodology and original
cutoff context are described in the committed
[first-foundation analysis](token-economics-first-foundation.md); later reconstructed
aggregates were read from the maintainer's local retrospective, not imported wholesale.

## Limits, confidence and rollback

Confidence is high in the observed native outputs and selected fault assertions;
medium in practical review benefit; unknown in billing savings. Missing dependency
coverage, a correlated oracle error or later report replacement could invalidate a
claim: retain explicit mappings, independent review and byte-bound current evidence.
One selected representation fault does not cover the full portable input domain.
Rollback reverts the contributor tooling/tests/docs while retaining ignored evidence
and existing review-session history. Existing user stores require no migration.

Next: obtain committed-head Linux gates and native external review, retain actual
findings/corrections, then take a separate final measurement snapshot. Do not mark
pending work complete based on this document.

Pre-review integration subsequently ran all 833 tests successfully (66.68 seconds),
full types and all 11 strict OpenSpec items. The aggregate command returned exit 2:
a generated-reference rationale needed refresh, and required capsule analysis is
unsupported on this macOS controller. The former was repaired; the latter requires
current-input supported Linux evidence. No full aggregate pass is claimed.

## First review findings and bounded repair

The first frozen candidate review found three unique P2 contributor defects: staged-only
paths could escape packet impact coverage; ignored packet-only oracle/config inputs
could be rehashed onto old session evidence; and accepted model no-ops did not compare
the complete persisted export, missing sequence/availability mutation. CodeRabbit's
two major comments duplicate the second finding and are counted once. These are
actual defects in this new assurance tooling, separate from the two prevented design
ambiguities and the seeded production-boundary controls. No runtime defect is claimed.

Four new regression cases failed before repair (the retry family has two metadata
variants); all 31 targeted tests passed afterward. The validator now includes staged
diff paths and requires every packet input in the authoritative pre-execution session
manifest. The harness requires exact full-export equality on accepted independent-model
no-ops. The guide binds unchanged runtime/spec/config dependencies before execution.
The existing session retains two review batches and 5.7516 minutes recorded as a
conservative elapsed upper bound for the parallel review intervals, not measured active
human/model effort. Both targeted independent closures passed without new findings; mandatory remote
gates and native review remain.

This negative result matters: adding assurance introduced its own assurance gaps.
Early mechanical controls were useful, but did not eliminate independent review or
prove a lower overall review bill. The fixed usage snapshot above includes this local review/repair interval; final
ignored capture and handoff will report later remote-validation totals.

Targeted closure verified all repaired logic against the frozen delta. The final local
run passed 837 tests in 66.46 seconds and normal applicable gates; aggregate exit 2
was solely the unsupported macOS capsule. The current 32.308 million request tokens
already exceed the historical foundation and bounded-workflow pre-PR observations,
while remaining below Core-02's pre-PR total. Scope and timing differ, so this neither
proves failure nor demonstrates savings. The evidence supports useful bounded defect
detection with material setup/review overhead, not replacing independent review.

## Native review and Linux feedback after the fixed usage cutoff

Published head `a6641177e113fb46c4eb14631dbfee45031d3803` received two further
Codex P2 findings: a packet without a previous packet incorrectly permitted narrow
review, and a previous packet for a different change could supply the comparison
baseline. Both are accepted tooling defects in review-baseline provenance. The first
local review covered current input binding but missed baseline existence and identity.
The revised spec requires broad review without a baseline, rejects a foreign change ID
exactly, and preserves a valid same-change delta. Two regression cases failed before
repair; the matching-baseline positive case passed. The repaired combined suite passes
34 tests. This brings actual unique semantic findings to five, across two correction
sets; no production runtime defect was found. CodeRabbit's native current-head summary
was clean; its missing REST review record is a status-adapter limitation, not evidence
that the native review did not run.

Both required Linux jobs on that head failed with the same three additional quality
blockers: projection cyclomatic complexity 18, a test mutation dispatcher nesting
seven levels, and an unresolved test-helper import. The mandatory SpecFact capsule
therefore supplied useful integration/maintainability feedback, distinct from the
non-capsule import invocation failures and empty sidecar evidence above. The repair
extracts predecessor traversal without changing assertions, uses named mutation
parameters, and makes tests an explicit package. Pylint 4.0.7 and Radon 6.0.1 plus the
installed Radon policy mapper report no affected-file error after repair; local
Pylint first lacked pytest in its isolated environment, then passed the error check
after that dependency was supplied. Full Linux capsule verification on the new
committed head is still required; local reproduction is not a capsule pass.

The ledger preserves three recorded batches, but orchestration overcounted review
phases: clean targeted closure and monitoring do not create correction sets. There
are two actual correction sets. A narrow extension to four recorded batches preserves
all prior events and the 90-minute limit, covering these validated native findings
and quality repairs. The earlier recorded 5.7516 minutes is only the two local review
intervals' conservative wall upper bound; native wait time and inference billing are
not silently treated as zero. The usage snapshot remains unchanged and excludes this
appendix's later work. Updated head gates/reviews and final ignored telemetry are pending.

## Recurring history gap and third correction set

The next native Codex review of `3258615fcd21a7a3c149560aa4747f6ba63d0f5d`
found P2 `4138783179`: accepted appends still omitted persisted observation history.
The first no-op repair was too narrow. Independent family investigation demonstrated
six real SQLite faults on the same change/run trace: old availability time, old
sequence, source identity, source-only sequence increment, new availability time,
and new availability sequence. All six passed the old oracle and therefore failed
the sensitivity tests. This is the sixth unique semantic defect in the new assurance
tooling, not six runtime defects. It reinforces the cost of maintaining an oracle.

The bounded repair covers Bundle schema/source/records/observations for rejection,
model no-op, lifecycle append, fresh selected import and identical reimport. It uses
strictly later boundaries and shared new-observation consistency, not an unsupported
contiguous-allocation assumption. Six append variants now reject faulty targets and
accept repaired targets; two selected import variants cover foreign preservation and
local-clock coherence. The four original fault families remain unchanged. An explicit
fresh-store rejection test checks absence preservation. Concurrency, changing clocks
inside a trace, generalized merge imports and observation-only imports remain excluded.

Both required Linux jobs passed on 3258615, demonstrating the earlier three capsule
quality repairs. That prior-head success does not validate the later history repair.
The new candidate requires independent family closure and fresh committed-head gates.
Totals are now six semantic tooling/test defects, three separate quality/integration
blockers, two prevented design ambiguities and three actual correction sets. Four
batch events remain in the ledger; a narrow maximum-five extension preserves the
prior orchestration overcount and the unchanged 90-minute allowance. The recurring
family was explicitly investigated before repair; no history was reset. No runtime
bug discovery, causal efficiency gain or billed savings has been demonstrated.

Family closure also caught an absent-store conditional bypass within that same open
finding: fresh/existing successful-write-then-delete faults skipped append checks.
Both new controls failed before repair; accepted appends now require persisted storage
unconditionally. This additional closure iteration remains in the third correction
set and reinforces the observed maintenance/review overhead.

## Follow-up context preservation investigation

Codex next found P2 `4138893867` on cbce547: a same-change packet could drop prior
advisory findings and still permit narrow review. Independent family investigation
also reproduced evidence-policy drift: removing/demoting an obligation or changing
its analyzer definition remained narrow while current evidence passed. These are
two semantic tooling defects (eight total), not each test row counted separately.
Authoritative review-session dispositions were never bypassed; the defect lost
advisory reviewer context. The fourth actual correction set preserves old/new changed
findings and evidence descriptors in a stateless `context_changes` result and requires
broader review. Definitions include ID, command/tool/version and applicability policy;
execution outcome/report/binding refresh is deliberately separate.

Eleven regressions failed before repair. Positive checks preserve narrow review for
fresh same-policy executions and ordering changes, keep required non-passing evidence
incomplete, expose added definitions and retain unresolved session findings. Both
Linux jobs passed on cbce547 before this later repair; new-head gates remain required.
Five recorded batches include the earlier administrative overcount; max6/90minutes
was explicitly authorized without resetting history. No lower recurring review cost
has been established: this pilot added maintenance work and repeatedly needed both
independent local and native review to discover defects in its own assurance tooling.
