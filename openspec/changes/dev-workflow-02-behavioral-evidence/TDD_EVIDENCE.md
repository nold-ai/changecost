# Behavioral evidence implementation evidence

2026-09-29 (Europe/Berlin), base `999cb8f960785fe4ac0434d41a0892beca933191`.
Contributor tooling/test scope only; runtime behavior unchanged. Final review pending.

## Observed red / green

- `pytest tests/test_behavioral_evidence.py -q`: 14 failures at the explicit
  missing-validator assertion before implementation (exit 1). This is interface-absence
  proof, not 14 independent discovered defects; output: ignored
  `.changecost/behavioral-evidence/packet-red.txt`.
- Same command after implementation: 14 passed (exit 0), covering same-head source
  changes, replaced/missing reports, missing oracle role, unmapped dependencies,
  skipped/unbound/non-applicable required evidence, malformed input and impact mapping.
- `pytest tests/test_lifecycle_stateful.py -q`: 13 passed (exit 0). Four selected
  faulty targets raise the named invariant assertion inside sensitivity controls;
  repaired targets run the identical trace/model/projection successfully. The generator
  uses seeds 0–7, 24 operations plus two setup operations each, and an explicit 12-step trace.
- Ruff formatting/import cleanup then scoped lint passed. First type check reported
  nullable cutoff handling in the faulty test subclass; adding the explicit None path
  yielded zero errors/warnings. This is implementation feedback, not a review finding.

No production transition/graph/revision helper is imported by the oracle. Writer
inspection of public APIs also exposed implementation bodies; independent human
review is still required to assess correlated assumptions. Native failure reports,
command timestamps and follow-up verification are retained locally; later sections
record final gate evidence rather than assuming these early checks cover edits.

## Tool experiments and current limitations

See [pilot report](../../../docs/lessons-learned/behavioral-evidence-pilot.md) and its
sanitized JSON ledger for actual SpecFact attempts, exits, elapsed seconds, failed
setup, unbound analysis and the distinct CrossHair/security-scanner controls.
Native reports and copied-input fingerprints are ignored under `.specfact/behavioral-pilot/`.
The exact original collection binding is retained; it is never replaced with a later
binding. Generic scanners and import/drift are not claimed to prove lifecycle behavior.

The genuinely new schema-8 session began at revision 0 with 0 batches/0 measured
minutes and the normal 3-batch/90-minute allowance. Required documentation ownership
paths were added by an explicit approved scope decision and head refresh; history
was preserved. Strict OpenSpec, aggregate checks, staged checks and final independent/
external current-head review remain pending until their actual results are appended.

## Pre-review integration (2026-09-29)

The timed check ledger `.changecost/behavioral-evidence/checks.jsonl` records:
27 targeted tests passing; full BasedPyright zero errors; selected strict OpenSpec
exit 0; full `make check BASE_REF=999cb8f960785fe4ac0434d41a0892beca933191
MANIFEST=.changecost/behavioral-evidence/manifest.txt` exit 2 in 75.37 seconds.
All 833 tests passed in 66.68 seconds. Hygiene, lock (including host missing/stale/
repaired proof), lint, types, index, metadata, workflow, build and all 11 strict
OpenSpec items passed; audit was explicitly not applicable because locked inputs
were unchanged. Documentation initially required a refreshed content-bound rationale
for the unchanged generated command reference; that rationale was repaired and
rechecked separately. Required capsule members reported `unsupported_controller_platform`
on macOS: the aggregate gate is incomplete, not passed; Linux remains required.

The documented packet example was executed on actual passing lifecycle output. It
validated current, became incomplete when the report bytes were replaced at the same
path, and returned current only after exact original bytes were restored. This is
actual evidence freshness control, separate from the initial interface-absence red.

## Review round 1 and repaired regressions

Frozen input digest `6df0fbce679c10bd3afb0ea9431f529c7d992a4195381df4986d8e250906c3dc`,
epoch input-generation:5, was independently reviewed and checked unchanged across
29 files. Three unique P2 findings were accepted (two packet-binding, one retry-history);
CodeRabbit's two comments duplicate the ignored-input finding. Review elapsed
21:18:14.846656Z–21:22:54.296469Z (4.6574968833 minutes) is recorded conservatively as
a wall upper bound, with no overlapping lane time added. Batch/history were preserved.

The exact staged-only omission and ignored oracle rehash regressions returned current
before repair. Real SQLite sequence-only and availability-only retry mutations failed
to raise their detector. `pytest tests/test_behavioral_evidence.py
tests/test_lifecycle_stateful.py -q` therefore yielded **4 failed, 27 passed** (exit 1).
After including index diffs, requiring authoritative input membership, and comparing
complete exports for accepted model no-ops, the same suite yielded **31 passed**
(exit 0). Logs: `round-1-regression-red.txt` and `round-1-regression-green.txt` under
ignored `.changecost/behavioral-evidence/`. One intermediate run exposed the older
retry control's assertion-label mismatch after stronger detection; its expected named
detector was aligned, without changing the faulty/repaired input trace.

## Targeted closure and publication boundary

Round 2 reviewed the exact seven-file delta, digest
`bf225cc54135daa44b6d1d3c73fe978c63bc9fa945317f62cb6cb463bb281293`, input-generation:7.
Both independent lanes returned no findings; the model reviewer repeated both SQLite
metadata faults and the repaired trace. Interval 21:30:08.165861Z–21:31:13.813836Z
adds 1.0941329167 conservative wall minutes, preserving two batches and 5.7516298
recorded minutes. CodeRabbit's full first-round review covered 29 files; its two
comments were duplicates of one accepted finding, not two additional defects.

After repair, all 837 tests passed in 66.46 seconds; full types, docs, index, metadata,
workflow, build and all 11 strict OpenSpec items passed. Aggregate exit 2 was solely
unsupported macOS capsule execution. The revised guide example ran on the complete
authoritative manifest, validated current, rejected replaced report bytes and returned
current after restoration. Native reports remain tied to their original collection
bindings; no old run is relabeled with a newer binding.

The maintainer's end-to-end request explicitly authorizes committing/pushing this
reviewed candidate to obtain the mandatory supported-Linux/current-head remote gates.
Publication is validation in progress, not a full-gate pass or merge authorization.
The pilot telemetry is frozen at 2026-09-29T21:32:11.834840Z, excluding later report
finalization, commits, pushes and remote review; later measurements remain separate.
Main was refreshed before publication and remains the recorded base. Final task 5
items stay unchecked until the remote/staged obligations actually complete.

## Native baseline provenance and Linux quality correction

Native Codex findings `4138609283` and `4138609294` were independently reproduced
and accepted. New spec scenarios precede the implementation: missing prior requires
broad review; foreign change identity returns controlled incomplete; valid same-change
comparison remains current/narrow. Packet regression command
`uv run --locked pytest tests/test_behavioral_evidence.py -q` produced **2 failed,
17 passed** before repair; combined packet/lifecycle suite produced **34 passed**
afterward. Native logs are `native-baseline-red.txt`, `native-baseline-green.txt` and
`native-refactor-green.txt` in ignored `.changecost/behavioral-evidence/`.

Both Linux quality jobs on a664117 failed with three blocking findings in the new
tests: Radon projection CC18; radon-kiss dispatcher nesting7; Pylint E0401 unresolved
behavioral_model. Minimal extraction/named callables/explicit test package retain the
same oracle, mutation IDs, predecessor assertions and full-history comparisons.
Affected files now have maximum Radon CC14 and CC6; the exact installed Radon mapper
reports no errors. Pylint4.0.7 reports no errors with project/test dependencies present
in the isolated local tool environment. Its initial missing pytest result is setup
feedback, not a project defect. Full types pass. No waiver or runtime edit is used.

All counters/history remain: three recorded batches overcount two actual correction
sets because orchestration counted review phases. The bounded extension to four
recorded batches retains the original 90-minute allowance. Targeted independent
closure and final committed-head Linux/native reviews remain mandatory.

## Recurring accepted-append history investigation

Native P2 4138783179 triggered independent family investigation and spec-first
complete bounded transition obligations. Six actual SQLite append faults were
undetected before repair: `uv run --locked pytest tests/test_lifecycle_stateful.py
-k append_history -q` returned **6 failed, 15 deselected** (exit1). They alter old
observation time/sequence, source identity/boundary, or new observation time/boundary.
The repaired checks preserve all old observations, stable source identity/schema,
fixed source clock and coherent unique complete local observations at a strictly
later shared boundary. No contiguous +1 rule is assumed. Two fresh-import controls
corrupt actual foreign observations/local availability, then verify repaired targets.
An explicit rejected fresh-store case preserves absence. Existing no-op and identical
reimport full-export controls remain. Logs are `history-matrix-red.txt` and
`history-matrix-green.txt` under ignored `.changecost/behavioral-evidence/`.

The earlier head3258615 passed both Linux quality jobs (run36636593121); later inputs
remain unverified by that result. Independent closure/new-head gates are pending.
This is the third actual correction set/fourth recorded batch, with authorized
max5/90minutes retaining all earlier history and orchestration accounting error.

The first family closure exposed a remaining conditional bypass: absent storage after
a successful append skipped persistence checks. Fresh/existing-store real-operation
then-delete variants both failed the detector before the guard (**2 failed**). The
accepted-append branch now unconditionally requires a persisted export before checking
its relations. Both faulty targets are rejected and repaired traces pass. This is an
additional variant of the still-open history finding/correction set, not a new runtime
defect or review batch. `history-absence-red.txt` retains the red proof.

## Packet review-context family investigation

Native4138893867 advisory-context deletion and the independently reproduced adjacent
evidence-definition drift prompted a fourth actual correction set. Spec-first tests
for findings deletion/replacement, seven definition fields and required/optional
removals returned **11 failed, 19 deselected** before repair (`context-red.txt`).
Minimal stateless old/new deltas now broaden semantic changes without interpreting
advisory strings as authoritative dispositions. Execution refresh/order changes remain
narrow-eligible; required nonpass remains incomplete; session findings remain intact.
`context-green.txt` retains affected-suite results, with pinned Pylint4.0.7/Radon6.0.1
error checks and full types separately retained. No second ledger or runtime edit.

Prior cbce547 Linux jobs both passed; this later input needs independent family closure
and fresh committed-head checks. Five recorded batches/max6 retain the earlier
administrative overcount, four actual correction sets and unchanged90minute allowance.

## Shared input identity and pre-call complete payloads

Native4138995957/4138995965 prompted two independent family investigations and a
combined fifth actual correction set. Dirty-baseline chmod failed the new stale-input
regression before implementation (`input-identity-red.txt`). Mode/index-only deltas,
unsupported index types/conflicts, mtime/no-op behavior and raw report hashes are
covered. The first full review-session/packet run passed569tests; index parsing was
then shared per capture to avoid per-file Git subprocess overhead. Historical event
replay still uses captured provenance rather than recapturing old files.

Ten actual SQL payload mutation/extra-record variants produced **10failed** before
the exact oracle (`payload-red.txt`). The new plain accumulator constructs complete
expected payloads before public calls using copied model/action values, finite literal
IDs and deterministic UUID allocation fixtures. No observed payload/return or production
decision helper constructs the expectation. All five record kinds and full cardinality
are checked. Combined packet/lifecycle tests pass74cases (`combined-identity-green.txt`).
One local Radon run flagged apply_checked CC16; extracting operation acceptance reduced
its complexity without changing assertions. Full integration/pinned analyzers are
recorded separately; final committed-head Linux/native evidence remains required.

Combined full local gate ran2026-09-29T22:46:19.074517Z–22:47:39.464493Z
(80.38991seconds, exit2): **884tests passed in71.92seconds**, full types zero errors,
lock/hygiene/lint/docs/index/metadata/workflow/build and all11strict OpenSpec items
passed. Audit was not applicable to unchanged locked dependencies. The only aggregate
limitation was required capsule analysis unsupported on this macOS controller. Pinned
local Pylint/Radon error checks passed after complexity extraction; they do not replace
the mandatory current-head Linux capsule.

## Exact foreign observation/source partition

Native4139150511 family investigation reproduced invented foreign observations on
append and fresh import, plus first-source substitution. Spec-first fault controls
returned **3failed** before repair (`partition-red.txt`); exact partition/source checks
then passed77combined cases (`partition-green.txt`). Canonical sorted lists preserve
all observation fields/multiplicity; fresh import foreign evidence equals original
input exactly and local obligations remain. Fixed source identity is fixture consistency,
not a claim about UUID generation. A local RadonCC16 result on assert_append prompted
extracting unchanged prior-history assertions; pinned error checks then passed.
No new runtime behavior, generalized import scope, ledger or correction batch was added.
This sixth actual correction set is seventh recorded event/max8 with history retained.

## Independent export envelope/scalar anchors

Native4139247160 and adjacent copied-export probes produced **5failed** controls
before repair (`envelope-red.txt`): wrong schema, source boolean/float, observation
boolean/float. The independent envelope guard anchors schema and exact sequence
integer/ranges before history/partition/payload relations, including fresh import and
reimport. Valid endpoints and invalid adjacent range values complement those faults.
The affected suites pass88tests (`envelope-green.txt`); full types, pinned Pylint/Radon
error checks and scoped style/docs/staged checks are retained separately. No production
schema validator supplies the expected result. This is seventh actual correction set,
eighth recorded batch/max9, preserving sticky REPLAN and all previous evidence.

## Finite documentation closeout

Verified code SHA `6c97e45bfa06647ab3adbb3b31cc4b41bc2061ba` passed both required Linux jobs in
run36645470663 (898 tests each, all11 strict OpenSpec items); Codex completed clean
at2026-09-29T23:34:34.935845Z and CodeRabbit explicitly covered this SHA with no
actionable comments at23:43:04Z. Fresh origin/main remained999cb8f after fetch.
The current documentation commit still requires its own native/Linux proof, retained
in the final ignored receipt without another tracked status update.

Task5.2 records completed execution/manual assessment. The separate open task5.3
preserves unmet automatic coordinator completion: historical family-escape REPLAN
and the native-summary/REST-review mismatch are accepted negative pilot results,
not waivers or fabricated passing checks. Full source evidence is retained in the
ignored input-identity closure and remote snapshots. PR27 remains open/unmerged;
issue26 metadata/parent/dependencies remain governed and unchanged.

The pilot report corrects the later successful minimal SpecFact import and valid but
non-selective drift comparison while preserving failed invocation history and immutable
initial telemetry. API return values remain outside this persisted-state oracle;
existing store API tests remain complementary. Final effort capture occurs after
final-head validation and explicitly excludes its own unfinished response.

## Late applicability consistency repair

Native4139466668 at d7b799e was independently reproduced. Spec preceded tests:
true/false applicability × missing/empty/whitespace/nonblank rationale gave4failed,
4passed before guard (`applicability-red.txt`). The minimal existing check now requires
rationale for either non-applicability signal and rejects true/not_applicable;55packet
tests pass (`applicability-green.txt`), including required nonpass and optional advisory
positives. Existing false/pass+rationale semantics remain unchanged. This is recorded
batch9/max9, actual correction set8, semantic record13. Earlier closeout proof is not
relabelled as this new head; exact-head final evidence is retained separately.

## Prior/current changed-input impact

Native4139520443 was independently confirmed as missing impact context, not a broad
review bypass. Spec-first tests produced3failed/1passed before repair;59packet cases
pass after the small mapping-union helper. Removed old-only labels, added current labels,
remapped unions and unchanged unrelated exclusion are covered, including a real
validated-packet removal and existing initial/narrow controls. Reports:
`removed-impact-red.txt`, `removed-impact-green.txt`. Explicit one-batch extension
preserves recorded9/9 exhaustion; now10events/max10,9actualsets,14semanticrecords.

Pinned Radon initially reported impactCC17; extracting unchanged affected-dependency
collection restored the existing complexity gate without a waiver. Redundant test
membership assertions produced type feedback and were removed because exact array
equality already proves exclusion; these are implementation feedback, not new semantic
findings.


## Post-replan phase: preparation only, 2026-09-30

The maintainer authorized revising this same change/issue26/PR27. Everything above is
historical evidence; the f6ddbe48 original pilot report/receipt/measurement remains
unchanged. New behavioral obligations are O1-O8 in design.md and the bounded-review
session delta. No post-replan red/green implementation result is claimed yet.

Observed starting session: revision103, 10 recorded batch events (9 actual sets),
15.67495325 partial recorded active minutes, budget10/90. Authorized ceilings are
13 batches and105.67495325 active minutes, preserving history. Runtime/coordinator
implementation follows independent architecture review of the selected matrix.

Final live acceptance belongs in the existing ledger and canonical PR-body exact-head
receipt. Task5.3 is a publication-time unchecked snapshot until that external acceptance
is actually recorded; its final live satisfaction must name the verified SHA and must
not be confused with a completed tracked OpenSpec checkbox count. No tracked update is
required solely to copy remote receipts into this milestone.

## Post-replan coordinator implementation controls

Upfront O1–O8 architecture approval completed 2026-09-30T11:23:44.258624Z;
planning handoff completed 11:24:47.427530Z. The original f6dd final-effort and
verification bytes are preserved in ignored post-replan/original-f6dd with baseline
SHA256 receipt. Post-replan measurement starts at the separate human implementation
task 11:12:35.448Z, with fixed preparation capture at approval; it does not overwrite
the original pilot report or claim savings.

Before implementation, `pytest tests/test_review_session.py -q -k
'named_family_resolution or native_completion or exhaustion_blocks_new or
watch_default_is_absolute'` produced 18 failed/531 deselected. Seventeen failures
were missing behavioral acceptance/rejection; omitted watch timeout initially failed
at the absent interface. After implementation the same selection passed18/531 in
2.41s. These are planned controls, not new independent review findings.

Existing compatibility initially passed547/549: two watcher fixtures expected continued
waiting after reports were ready for adjudication. Their pending/deadline setup was
updated to retain the original intended assertions under the explicit new handoff.
The full coordinator suite then passed568 in74.92s. Additional negative controls
cover provider author/content changes, absent sources, check failure/pending/missing,
requested/negative review, unresolved thread/local finding, input drift, retained-source
replay and simultaneous budget/family escalation. An author-change control caught
incidental-metadata normalization during implementation; only explicitly adjudicated
native sources now add author identity to meaningful progress, preserving old receipt
replay. Further durable-claim controls produced2failed before insertion-time actual
input validation, then passed with the selected native/deadline cases (14passed).

Pinned Pylint4.0.7 reported no errors. Early type checking found two optional-receipt
accesses, repaired by explicit validation. Installed SpecFact Radon6.0.1 mapping found
a nested test mutation dispatcher; named data-driven mutations retained every label
and repaired it. The selected mapper then reported no errors (advisory complexity
warnings remain). No threshold/waiver or CI matrix was changed. Ruff and types pass.
Exact logs are ignored `.changecost/behavioral-evidence/post-replan/`; subsequent
aggregate, immutable closure and live exact-head results are separate receipts.
Initial implementation is not a correction batch. Historical10events and partial
15.67495325 recorded minutes remain, with authorized cumulative ceilings13 and
105.67495325; old family obligations are not resolved until independent verified closure.


The integrated local candidate `make check BASE_REF=999cb8f960785fe4ac0434d41a0892beca933191
MANIFEST=.changecost/behavioral-evidence/post-replan/manifest.txt` ran at
11:50:01.099643–11:51:41.671661Z (100.5715 seconds). It passed958 tests in91.26s,
all11 strict OpenSpec items and the other local leaves. Aggregate exit2 remains
**incomplete** because every required signed capsule analyzer reports
`unsupported_controller_platform` on this macOS host. Supported current-head Linux
is still required. This is not a full assurance pass. Later small handoff-label and
documentation consistency edits receive affected checks and staged verification;
the exact frozen receipt records final bytes. Task7.2/7.3 and live5.3 remain open.


A final watch compatibility control observed a false repeated handoff for an already
adjudicated incomplete native source (1failed); unchanged covered reports now remain
pending until their source changes. This retains human code-review adjudication and
avoids inferring completion/readiness from an old provider author's mere presence.
No new review finding or correction set is counted. The final focused/staged receipts
include this control; the earlier958-test aggregate describes its actual earlier input.


## Post-replan correction set 1: native fallback / REST precedence

Independent O1–O8 closure (11:57:29.908295–12:00:35.357427Z, conservative185.449132s)
collected one P2: native completion overrode present current-head REST PENDING or
DISMISSED. Both real temporary-session controls acknowledged every current report
and incorrectly reached COMPLETE before repair (2failed,571deselected). The minimal
repair permits fallback only when that provider has no current-head REST result;
normal REST state and freshness, negative reviews, requests and all other gates remain.
The selected native/REST suite passed61 before adding the explicit stale/fresh REST
positive boundary. Types and pinned Pylint pass. Exact command receipts/logs are
`post-replan/rest-precedence-*`; final staged/freeze receipts bind the final controls.

This is one new independent post-replan finding and one actual correction set, now
11 retained recorded events out of13. Scoped historical closure evidence was captured
at epoch31 before edits; it is not reused to resolve obligations on the revised input.
Current-binding targeted closure is still required. No budget reset, runtime change,
new review framework or broad repeat review was introduced.


## Post-replan correction set 2: causal closure and provider policy

Both b350 Linux jobs passed963 tests and11 OpenSpec items. Native reviews completed:
Codex code summary5899441830 at12:18:24.167388Z with P2 comment5911145441;
CodeRabbit COMMENTED review5366054363 at12:19:01Z with one outside-diff Major.
Neither is described as clean. The watcher rejected one between-pass evidence change;
a deliberate single fresh snapshot recovered stable current-head facts. This was
collection friction, not a review finding or a passing receipt. The actual queued
CodeRabbit review was reused without a duplicate manual request, although the published
feature YAML disabled automatic review; effective service behavior remains separately
observed. Original reports and first-publication telemetry remain immutable.

Independent triage (12:21:27.851750–12:22:46.887741Z) accepted two first findings in
one collected set: closure causal coverage and promotion-policy consistency. A blanket
requirement for fixed flags before review was rejected: known corrected input may be
reviewed before the administrative disposition. The approved causal matrix instead
produced5failed/2passed before repair: future finding coverage, later accepted-exception
or non-finding disposition, and scoped failing/incomplete review invalidate the old
closure; both legitimate administrative orders already passed. Resolution now inspects
existing ordered events, preserving binding checks and old informational history.
Fresh closure after contradiction restores validity; unrelated events do not invalidate.
The selected family/closure suite passed32 in4.75s. Types and pinned Pylint/Radon report
no errors. The promotion skill now requires the same risk-selected providers as the
canonical workflow; a limited wording consistency check found no residual unconditional
two-bot completion rule. No new ledger, runtime behavior or provider parser was added.

This is post-replan actual set2, cumulative recorded event12/13 with no extension;
the two findings retain separate identities and original severities. Multiple negative
controls are not multiple findings or a recurring family. Final staged evidence and
independent targeted closure are required before another publication. Prior b350 checks
remain historical; new-head full Linux/provider proof and live task5.3 remain pending.

The HEAD-relative staged gate initially rejected three stale documentation fingerprints
(quality rules, generated llms index and behavioral guide). Their existing canonical
workflow links and scope remain accurate; content-bound rationales were refreshed after
inspection. This is documentation-gate feedback, not another semantic review finding.


## Post-replan final collected correction set3

Head14b3a2e passed970 tests and11 spec items in each supported Linux job
(run36716259084). Codex completed12:52:25.450630Z and reported the first O6 P2
(PRRT_kwDOUu9-oc6niTOw): new top-level review feedback was delayed by pending CI.
Independent triage12:54:03.496536–12:54:47.182715Z confirmed the actual simulated
three-poll/60-second delay. New pending/missing-gate controls produced2failed/2passed
before repair; the affected watcher/deadline/exhaustion suite now passes21. The minimal
repair removes only the pending-gate filter from report handoff. CI still blocks
completion; error/negative/budget precedence and exact receipt novelty remain. Existing
steady-poll and deadline fixtures now explicitly acknowledge their baseline reports;
the deadline control varies actual queued/in-progress status instead of report prose
or ignored details URLs. The initial broader run exposed these three fixture
assumptions; saved reruns retain that implementation feedback.

CodeRabbit did not cover14b: at12:40:23Z it attempted the8-file increment and returned
its included-review limit with29minutes until normal availability. No paid request
was made. Configuration response5911495348 at12:40:43Z confirmed enabled=false but
auto_incremental_review=true. This is the first O7 recurrence/acceptance gap; queue
causation is unknown. The approved empirical plan adjustment additionally disables
auto_incremental_review, preserving all other configuration. The bounded trigger matrix
covers open/reopen, push, explicit required manual review and config-versus-coverage
distinctions. Local YAML/config checks are not proof of hosted scheduling; actual
final-head readback and required manual completion remain necessary. No permanent
literal-boolean test or test-only publication was added.

This is final post-replan actual correction set3, retained recorded event13/13; no
extension or reset. Original pilot reports and first-publication telemetry are unchanged.
Focused static/spec and staged checks precede one independent affected-scope closure.
Main-relative gates cover the whole feature; HEAD-relative gates cover this correction
and its source-bound documentation metadata independently. Subsequent current-head
Linux/native coverage and actual ledger completion remain pending, not preclaimed.


The first final-set closure (13:02:54.985956–13:06:17.184614Z) was not passing:
its independent14-control selection found one budget-only observation fixture with an
unacknowledged baseline REST report. The new handoff was correct; the fixture did not
isolate budget-only waiting. Root authorized only acknowledging that unchanged
baseline before exercising the existing six blocker variants. No production change,
new finding family or correction event was introduced. The complete coordinator suite
then passed586 tests at13:06:41.517092–13:07:53.883753Z (72.37 seconds command wall),
including all existing watcher, deadline, budget, negative-gate and history controls.
The revised staged snapshot still requires targeted independent closure.
