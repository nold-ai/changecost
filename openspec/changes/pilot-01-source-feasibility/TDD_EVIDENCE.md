# Source feasibility implementation evidence

## Scope and status (2026-10-03, Europe/Berlin)

Accepted plan: complete existing research/tooling while retaining the native-profile
gate. Fresh main and implementation base: `5f43c32d09e6d1b167c352ad16cabea555d84ec2`.
Preparation stash `fbc49fef8027a790c68cd4785d76f764ca6f29e8` was inspected and applied
once on `codex/pilot-01-source-feasibility-closeout`; it remains available for recovery.
The separate unpublished Quote archive checkout is preserved.

#9 was reopened and read back as Open/Todo during preparation, then moved to
In Progress for implementation. Native User Story type, parent #5 and #13/#14
source dependencies remain intact. PR #21 delivered historical partial research;
PR #32 delivered Quotes. No source profile is approved and this change is not archived.

## Actual red / green evidence

Specs and tests preceded the new implementation. At the first red run,
`pytest tests/test_source_feasibility.py -q` failed collection because the requested
`quality.source_feasibility` module did not exist (pytest exit 2, one error).
After implementation, the same suite exposed a real matrix mismatch-path failure:
51 passed, one failed. The matrix now returns mismatch for an invalid approval.
A later spec-derived checkpoint conflict test failed with missing computed
`checkpoint_conflict`; after computing distinct checkpoint values, 77 tests passed after additional missing-parent/orphaned-correction/interval controls.
Commands used the locked Python 3.13.14 environment and pytest 9.1.1.
Private logs: `red.log`, `green-initial.log`, `checkpoint-red.log`, `identity-red.log`, `green.log` in the
ignored change workflow directory. Additional behavior tests cover all 18 original
cases plus faulty/repaired expectation controls, independently changed inputs,
root/child identity, replay/conflicts, snapshots, reset/unit boundaries, exact
Decimal corrections, missing/null/zero, JSON/JSONL/CSV rejection, input limits,
changed hashes, link rejection and private diagnostic sentinels.

The existing fixture file remains byte-for-byte unchanged. Tests compare computed
results with the historical expected values; evaluators never read those answers
or dispatch on a case ID. Synthetic authority rules remain detector hypotheses.
Neither those cases nor structural inspector output establish native provider support.

## Source reinspection and limits

Selected existing Copilot/Cursor metadata was reinspected read-only on 2026-10-03.
Source bytes changed; original receipts remain preserved. The canonical register
records current opaque digests and separate source/version/tier profiles. Selected
Copilot checkpoint/turn usage projections remained unchanged; Cursor usageData
remained empty with zero bubble counters. These are not final consumption records.
Installed Codex 0.139.0 and Claude 2.1.257 metadata was refreshed separately from
Desktop/transcript versions. Supplied bundle integrity was rechecked against prior
receipts: 51 files across four bundles remained unchanged; original bytes were preserved.
The new inspector also checked 1,050,015 bytes / 367 native hosted event records,
reporting ordinal type/missing counts without private values or semantic approval. Current primary documentation checks,
interpretation and exact missing artifacts are in the source-feasibility guide.

Native CLI/IDE exports, personal Cursor CSV and paired hook/upload/receiver mapping
remain missing. #9 stays open; tasks 2.1/2.2, 6.2/6.3 and acceptance remain pending.
No account settings, live collection, paid requests, adapters, portable schemas,
database migrations, settlement policy or Quote coverage policy changed.

## Verification and review

Independent upfront obligation review identified native attestation binding,
version separation, bounded file descriptors, duplicate handling and safe diagnostic
obligations. Local mechanical checks, independent affected-scope closure and fresh
Linux/provider reviews are recorded here as they finish; missing evidence is pending,
never a pass. A genuinely new schema-8 bounded session preserves its immutable
contract, binding, review counters and logs; recovered historical receipts are retained.

## Supported native failure and bounded correction (2026-10-03)

Fresh Ubuntu [workflow 37144463158](https://github.com/nold-ai/changecost/actions/runs/37144463158) checked published head
`c91bfe56d186af407563cf0fa372755fefd71a80`. Ordinary 1,234 tests and strict
OpenSpec 11/11 passed in both Python jobs. Eight native analyzer members passed.
Actual native assurance failed: `_profile_valid` complexity 17, `_parse` nesting
depth 6 above 3, and source checker coverage 74.6% below 80% in Python 3.13.14.
Python 3.11.15 targeted capsule coverage additionally timed out (UNKNOWN); its
report contains no partial test output, so the exact cause remains unverified.
Original reports/hashes and full logs are preserved privately. No native pass is claimed.

The maintainer approved extending the same bounded session to five correction
batches / 120 active minutes, preserving prior history and failures. Batch 3
separates profile field-group checks and JSONL/CSV parsing without changing profile
semantics, approval conditions, diagnostics or input limits. Eight additional
meaningful in-process CLI checks exercise default/matrix output, private reports,
hash rejection, matrix drift/repair and safe argument/register failures; subprocess
checks remain. An initial test fixture unpack error failed two tests and was
corrected without changing product behavior. Scoped tests now pass: 95 source
tests, lint and typing. Fresh native assurance on the corrected published head is
still required; thresholds, exclusions, test scope, dependencies and CI are unchanged.
The aggregate staged check passed; the incremental HEAD-baseline check exposed an
unchanged README mapping to the refactored quality sources. Its CLI control summary
was refreshed rather than waiving the documentation freshness gate.

## Checkpoint identity correction (2026-10-03)

Independent review reproduced a P2 semantic defect in the published synthetic
hosted evaluator: any differing checkpoint totals were flagged as a conflict,
including legitimate cumulative progress across distinct event identities.
After the spec scenario was written, nine input-derived controls produced actual
red evidence: 7 failed / 2 passed, retained in `checkpoint-identity-red.log`.
They cover distinct progressing events, identical replay, same-ID conflicts,
missing event/session identities and separate SDK session namespaces.

Batch 4 groups comparisons by explicit SDK session/event identity. Missing identity
leaves the conflict assessment unresolved; no totals are added and final session
consumption remains unknown. Optional per-record `synthetic_context.sdk_session_id`
is authored fixture scope metadata, never a claimed native wire field. The original
18-case fixture file remains unchanged. Scoped green: 104 source tests, lint and
typing; actual log `checkpoint-identity-green.log`. The preceding Linux run for
`08740b9c2ce5856a2de51466bda6cd2a042f8d61` remains historical assurance only,
not defect-free proof of this correction. Fresh corrected-head assurance is required.

## Risk and rollback

Confidence: high in the bounded detector approach; source approval is To-Validate.
Versions, tiers, native accounting intervals or receiver mappings could change findings.
False authority is mitigated by exact reviewed profile bindings; overlap by explicit
unknowns and revision checks; disclosure by fixed-code diagnostics and ordinal reports.
No paid infrastructure is planned. Remaining source inspection duration depends on
artifact availability. Revert this change's code/docs to roll back; preserve original
source bytes, private receipts, stash and truthful issue state.


### Independent correction batch 1

The frozen initial review returned seven code/provenance defects and three
tracking/profile omissions. Actual faulty controls failed before fixes: 10 failed,
77 passed (`review-red.log`). Empty/subset oracles now reject; synthetic shape/export
flags cannot claim native compatibility or inspected payloads; rollout aggregation
requires one explicit versioned session and nonempty token events. Required register
citations/field meanings/requirements are validated. Synthetic derivative hashes are
labeled synthetic, separate IDE profiles exist, and current #9 status is consistent.
After fixes, `review-green.log` records 87 source tests passing. The original 18-case
fixture is unchanged. Missing accounting approval and native evidence remain pending.

Initial local aggregate: 1,224 tests and all 11 strict OpenSpec validations passed;
all non-native leaves passed after using environment-variable Make inputs. The first
invocation retained a Make override contamination failure in a pre-existing probe;
no checker behavior was changed to bypass it. Hygiene repaired CHANGELOG's final
newline, invalidating that frozen binding; the reviewed content was recaptured.
Fresh macOS SpecFact remained UNKNOWN/unsupported for all ten required analyzers.
The repository's documented macOS handoff permits reviewed local commit/push for
fresh Linux CI; no native pass or merge readiness is inferred from local results.
Fresh final scoped/staged checks, affected independent closure and Linux/provider
assurance remain pending until their actual current-input results are available.

Fresh Codex app-server schema generation produced 258 files; 257 were identical to
the prior receipt. Only the combined schema excluded experimental fuzzy-search
methods in the default generation. Individual usage schemas remained unchanged.
This refresh proves an interface shape, not observed account/session finality.


### Tracking-family investigation and current local verification

Affected independent code closure returned No findings for all seven original
families. The documentation follow-up caught a genuine residual tracking escape:
two earlier CHANGE_ORDER summaries still said closed #9. The complete current-status
family was investigated before another correction, with historical references
classified separately. Batch 2 updates the overview/lifecycle summaries together,
including accurate merged Quote PR32 context, while preserving its separate archive.
The original finding, correction, escape and investigation remain in session history.

Final non-native local aggregate on generation 3: all 12 leaves passed, 1,234 tests
passed (87 source tests), strict OpenSpec 11/11 passed, and no input drift occurred.
The later tracking-only correction changes no verified Python behavior. Scoped final
docs/index/hygiene/metadata/staged checks and independent tracking closure are required
for its recaptured binding. Full native Linux/provider results remain pending until
current-head remote assurance completes. See ignored closure receipts for full logs.


### Current-head provider semantic corrections (batch 5) — 2026-10-03

Codex review 5402728822 at dc2641ce4ce39b222720cc51b85a69fd1553582c
reported boolean replacement references, unparsed cumulative interval strings and
absent checkpoints incorrectly certifying conclusions. All three reproduced against
the unchanged historical fixture expectations. Specification scenarios preceded
15 controls: actual red was 11 failed / 4 passed; after minimum detector fixes all
119 source tests pass. Faulty/repaired controls preserve original fixture bytes.
UTC-offset ordering/equal endpoint conflicts, reversed/naive/malformed bounds, missing
quantity and known-conflict precedence are covered. The first checkpoint-family escape
was investigated across absence, incomplete identity/amount, replay/progression and
conflict precedence; any further genuine escape requires replanning.

The prior corrected-head Linux run 37152662363 passed both matrices, 1,251 tests,
strict OpenSpec 11/11 and all ten required native analyzers. It is now historical
mechanical evidence, not acceptance of the next head. CodeRabbit completed full dc264
review with no actionable comments; Codex's three findings remain pending verified
closure. Final scoped/staged checks, independent affected closure and fresh Linux plus
provider evidence are required for this correction. No approval/finality expansion,
quality thresholds/exclusions or original fixture changes were made.


### Maintainer-approved scoped invariant replan (batch 6) — 2026-10-03

At b50551f3f528c709068b6770cd0ed98d9d65a837, Codex review5402803643
reported whitespace snapshot identities and mixed correction billing bases. The
five-batch limit stopped fixes; the issue/PR truthfully retained REPLAN and missing
current-head CodeRabbit acceptance. Supported Linux37154482038 passed all ten native
analyzers and 1,266 tests on both Python versions, but did not close those defects.

The maintainer explicitly approved a same-change invariant replan and seven batches /
150 active minutes, preserving all five prior batches, failures and allowance history.
An independent immutable-head investigation collected related malformed root/rollout/
hosted identity labels, incomplete correction event/currency/basis and null mandatory
revision defects before batch6. Writer investigation covers affirmative identity
consumers and complete correction economic/revision identity; future genuine escape
after investigation requires replanning. No runtime/product scope was expanded.

Specification preceded 76 invariant controls: actual red49failed/27passed. The shared
nonblank-string guard and stable exact correction key plus mandatory integer revision
validation repaired them. Additional missing/list/dict label controls exercise safe
unresolved outcomes. Original 18 fixture bytes and precise Decimal/history/replay
expectations remain unchanged. Scoped/source/full/staged verification, independent
affected closure and fresh Linux/provider acceptance remain required for the next head.
No quantity, native approval, finality, adapter, portable schema, collection, quality
threshold, coverage exclusion or review policy change was introduced.

Final source control matrix: all 228 source tests pass, including the original 18 cases.

### Approved focused postescape replan (batch 7) — 2026-10-04 Europe/Berlin

At 01d2472852d0f695aa29ac708174fa60e48dae62, Codex review 5402909675
exposed numeric equality hiding invalid quantities during deduplication and missing
Claude identities producing positive correlation counts. Independent adjudication
classified the latter as a genuine post-investigation identity-family escape: the
stricter repository REPLAN rule took precedence over the helper's INVESTIGATE result.
The maintainer explicitly approved this focused repair using batch seven and the
existing 150 active-minute allowance; no allowance or history was reset.

Supported Linux run 37156281112 completed both Python versions: 1,375 ordinary
tests and strict OpenSpec 11/11 passed; all ten native analyzers ran. Nine passed;
Radon failed on rollout cyclomatic complexity 17. No native result was UNKNOWN.
This retained failed run is historical evidence, not acceptance of a later head.

Whole-family quantity-before-deduplication and correlation investigation preceded
batch seven. Specification preceded 51 controls: actual red was 36 failed / 15 passed.
Minimum repairs validate each quantity before replay collapse, require complete
stable correlation mappings, and separate rollout metadata scope checking. Three
additional missing-field controls bring the passing source suite to 282 tests.
Fault/repaired controls cover boolean/integer and float/integer aliases in both
orders, zero, unknown and unequal totals, missing/partial/nonstring identities,
replay and conflicting links while preserving physical row counts.

Original 18 fixture bytes, finality and native approval criteria remain unchanged.
No adapters, runtime commands, schema, collection, new source fields, thresholds or
coverage exclusions were added. Affected independent closure, full scoped/staged
checks, fresh supported Linux and current-head provider acceptance remain pending
for the repaired head.

### Approved report provenance repair (batch 8) — 2026-10-04 Europe/Berlin

Published 84f7cb18ecaacac353eaa22fd97278ed9f6cf691 passed supported Linux
37157951153 on both versions: 1,429 tests, strict11/11 and all ten native members
ran/PASS, assurancePASS, exit0, noUNKNOWN (PASS_WITH_ADVISORY). Current Codex
review5403079887 nevertheless identified P2 comment4175142838: public inspection
reports omitted safe registered evidence references. Same-byte distinct-reference
reproduction confirmed the explicit inspection specification violation. CodeRabbit
completed full 5f43→84f7 review across24files with no actionable comments; its
included allowance was zero afterward. Mechanical/provider clean output could not
close the known provenance defect. The eight-batch repair has no prior-head acceptance.

At seven batches /149.226 recorded active minutes, the maintainer explicitly replied
“yes approved” after the coordinator described the minimum provenance/privacy repair
and one additional batch with30active minutes. The same session now allows eight
batches /180minutes, retaining all history and original failures; no reset or quota
bypass. Independent immutable-head provenance investigation and writer consumer
mapping covered success reports, direct inspection and validated-reference errors.

Specification preceded controls: actual provenance red28failed; valid-reference
failure/atomic-output red5failed1passed. Minimum helpers match registered safe
profile/evidence keys, validate grammar and uniqueness before echo, and retain that
pair in success reports and fixed-code diagnostics after validation. Unknown/unsafe
references stay redacted. Repaired controls cover shared bytes/different origins,
cross-profile equal labels, reorder/replay, malformed matched labels, ambiguous and
unknown refs, malformed/hash/selector failures, no partial output and private data
suppression. The final source suite has317passing tests; original18fixture bytes and
all native approval/finality/economic policies remain unchanged.

Current-head independent closure, complete local/staged gates, fresh supported Linux
and required provider completion remain pending. No adapters, public runtime command,
schema, collection, account change, paid request, threshold/exclusion or authenticated
provenance framework was added. The registered keys are intended public opaque
references, not authentication of source claims or human review.

### Approved complete-inventory replan (batch 9) — 2026-10-04 Europe/Berlin

At published18228bbf99740073d70284ac705c421e015f63c1, supported Linux
37160043893 passed both versions:1,464tests,strict11/11,all10native members
ran/PASS,assurancePASS,exit0,noUNKNOWN (PASS_WITH_ADVISORY). Codex5403306710
then reported malformed cumulative metric identity producing an estimate. A retained
full18inventory reproduction confirmed the result without changing fixture oracles;
the earlier reduced one-case inventory failure was preserved, not called a pass.
Independent adjudication classified this as a genuine post-investigation identity
escape, requiring explicit REPLAN. CodeRabbit current-head completion remained
missing; its capacity-only query reported the next availability, without starting
or paying for a review. Earlier full review covered84f7 and was stale.

Before further fixes, independent immutable-head inventory mapped all18cases,
13strategies,123case/outputslots,49outputnames and74historicaloracle slots. It
collected three demonstrated P2s: omitted cumulative metric identity; projection
key presence falsely implying billing correction; and unsupported mixed-event
history deduplicated by bare revision. The maintainer explicitly answered
“Approve the scoped replan” for one ninth batch/+30active minutes (9/210total),
preserving eight used batches,172.689recorded active minutes and every failure.
The writer traced each output's guard/precedence against this inventory before
repair. No new provider fields, supported capabilities or runtime product scope.

Specification preceded30fault/repaired controls: actual red24failed/6passed.
Minimum repair uses the shared exact nonblank metric predicate before grouping,
keeps unsupported projection billing correction not demonstrated, and makes history
count unavailable outside a complete single economic/event scope. Original same-scope
revision counts, conflicts/replay and precise Decimal/UTC behavior remain intact.
Bounded containment controls cover existing context quantities, counter/enum type
observations, rollout field presence and all18fixed native/cash boundaries. These
distinguish structural observations from billing/aggregation claims; they introduce
no provider quantity policy. All380source tests pass, including unchanged18fixtures.

Required affected independent closure, full local/staged checks, fresh supported
Linux and both current-head providers remain pending for the repaired head. Native
Copilot/Cursor/hook samples still block profile approval and issue9completion.
Rollback preserves originals, scoped stash, Quote archive and review history.

## Tenth scoped correction batch — 2026-10-04 Europe/Berlin

Published a2ab025 Linux37162274523 passed both3.11.15/3.13.14 with1,527tests,
strict11/11 and all ten native analyzers ran/PASS. CodeRabbit full native summary
5973457004 and acknowledgement5974725594 completed against that exact head,
independently adjudicated; no normal REST submission was fabricated. Codex
5403510573 then reported two genuine P2 defects:4175449008 ignored additional
token records and4175449009 accepted empty partial-profile evidence details.
Those green mechanical/provider receipts remain historical for the next head.

The maintainer explicitly approved focused batchten/+30active minutes and requested
continued reviewed fixes until green within the preserved10/240allowance. Original
nine batches,197.917conservative active counter, post-investigation escapes and
quota failures remain; no automatic further allowance or gate waiver is inferred.

Spec-first controls produced actual13failures/9passes before code changes. The
minimum repair assigns only tokens-only an explicit single-record strategy; the
shared multi-record timestamp/overlap strategies remain unchanged. Partial
capabilities require nonempty valid fields and requirements; nonpartial controls
retain empty-details validity. Both record orders, identical replay, malformed
trailing rows, zero/missing amounts, each/both empty or malformed detail collection
and repaired valid controls are covered. Source tests now402pass. Original18
fixture bytes, expected conclusions and register approvals remain unchanged.

Independent affected closure, complete stagedmain/priorHEAD checks, fresh supported
Linux and current-head provider acceptance remain pending at this checkpoint. No
source approval, collection, adapter/runtime/schema change or issue closure follows
from passing synthetic controls.

## Full register family continuation — 2026-10-04 Europe/Berlin

Published4c6e5aa native37163878156 first3.11attempt recorded targeted capsule
UNKNOWN/sandbox_launch_failed:timeout; nine other members and ordinary1,549tests
passed. Same-head3.13 passed all10. Pinnedmodule0.50.1 outer launcher uses300seconds
while portable child has1200; timeout discards partialstdout, so precise cause is
unknown. One explicitly authorized unchanged-head failed-job observation passed
all10native members/assurancePASS/noUNKNOWN, preserving originalartifacts. No
timeout, dependency, test selection or gate policy was changed.

Automatic currentCodex5403549513 reported4175488366: supported profile meanings
and entirely unverified unresolved requirements could be empty. A redundant manual
Codex request5975008606 was an administrative mistake after the automatic result
was visible; it remains in history, with no further duplicate trigger. CodeRabbit
capacity-only5974853699 reported40minutes from00:07:18UTC; no fresh full review was
requested against the known defective head.

The actual maintainer request was to keep fixing and monitor PR review, triage,
push and resolve via sub-agents until green. The coordinator explicitly interpreted
that ongoing same-change authorization as a scoped register-family continuation:
one further batch, eleven total, with the active allowance unchanged at240minutes.
No numeric eleven quote or extra active-time approval is attributed to the user;
all prior counters, post-investigation escapes and failures remain.

An independent full register disposition investigation preceded implementation
and admitted the partial-only closure miss. Spec-first controls failed9/passed16
before the minimum guard repair. Finite controls cover256capability combinations
withfourempty/nonemptydetail states, alongside24malformed/load/matrix/fault-repaired
controls. Source tests now427pass. Any supported/partial capability requires valid
meanings; any partial/unverified requires unresolvedrequirements. Allunavailable
mayemptyboth; fullysupportedresolved mayemptyrequirements, preserving mandatory
existing nativeapproval bindings. Original18fixturebytes/registercontents unchanged.

Affected independent closure, complete stagedmain/priorHEAD proofs, fresh supported
native and current providers remain pending for the updated head. No source profile
approval, collection, adapter/runtime/schema or issue closure is introduced.

## Collected input boundary continuation — 2026-10-04 Europe/Berlin

At5a80, active Codex findings included UTC normalization overflow and the default
CSV field cap from delayed manual review comments4175549605/4175549607, whose
original head was4c6e5aa, plus nested-shape comment4175563022 from automatic
review5403624086 at5a80. All three were independently reproduced on immutable5a80
before changes and fixed in d72ac2453973ef1c6ed796f44786d0854938fa6d. The earlier
redundant manual request5975008606 and original/current comment-head metadata remain
preserved. No additional manual request or CodeRabbit full review was started
against known defective5a80; its native outcomes remain historical for later heads.

The actualexisting maintaineruntilgreen request and coordinator's explicit scoped
continuation interpretation authorize batchtwelve withUNCHANGED240active minutes.
No new numeric twelve quote or extra time is attributed to the user; prior
observations, failures, counters and reviewed-boundary escapes remain. Independent
complete affectedinput-family investigation preceded spec/tests/implementation.

Initial control-construction mistakes (manifest tuple/path selection) produced a
24fail/3pass log, retained separately. Corrected behavior controls then reproduced
32fail/10pass before code. Minimum repairs catch UTCnormalizationOverflowError as
unavailabletime, normalize nestedAttributeError at the existingcase dispatcher,
and wrapCSV parsing withMAX_BYTESfieldlimit/restorationfinally. BothUTCbounds and
intervalpositions, plannednestedconsumercontainers, wideUTF8header/cells/quoted
multiline/repeatedparses/malformedfailure/restoration and privateCLI diagnostics
arecovered. Two laterCLI control signature mistakes were retained/corrected using
the actual no-argumententrypoint; final471source tests pass. Original18fixturebytes,
register, numeric meanings, nativeapproval/uncertainty boundaries remain unchanged.

Independent affectedclosure, complete stagedmain/priorHEADproofs, fresh supported
native and currentCodex/CodeRabbit acceptance remain pending. There is no new
format/framework/accountingprofile/runtime/schema/collection capability.

## Hosted semantic oracle continuation — 2026-10-04 Europe/Berlin

At1792469, active reviewthreadPRRT_kwDOUu9-oc6otimC demonstrated that an actual
computed checkpoint conflict was absent from checker obligations: adding the same
SDK/eventidentity with300000001 instead of300000000 yieldedcheckpoint_conflictTrue
butcheck_cases[]. The full inventory had mapped this slot but failed to enforce it;
independent adjudication retained the conclusion-coverage family escape and admitted
the review miss. Source evaluator behavior was already correct.

Actualexisting maintaineruntilgreen authorization and coordinator's explicit scoped
interpretation continuebatchthirteen withUNCHANGED240active minutes, no invented
newreply/numericquote/extratime orhistoryreset. The proposed provider rewrite of
historical expectedfixtures was not a user instruction; all18originalfixturebytes
and declaredexpectation dictionaries remain immutable.

Spec-first checker-level controls reproduced10fail/5pass. The minimum strategy
acceptance guard requires actualcheckpoint_conflict exactlyFalse independent of
fixture-declared answers. Unknown/True/falsy-type substitutions reject safely;
canonical original, exactreplay, identifiedprogression and separate synthetic
namespaces pass. Knownconflict plus incomplete evidence retains conflictprecedence;
missingcheckpoint/amount/SDKscope/eventID and privateCLI diagnostics are covered.
Final486source tests pass. A testconstructor Ruffcomplexity failure was retained
and repaired by separating construction/assertions, without suppressions. Existing
localRadon6.0.1 reports checkerCC13/constructor14/assertiontest9; this is a targeted
local check, not supported native assurance.

Nativeauthority/finality/approval, immutablecases, register and evaluator remain
unchanged. Affected independentclosure, complete stagedmain/priorHEADproofs, fresh
supported native and currentrequiredproviders remain pending for the updated head.

## Fixture metadata shape continuation — 2026-10-04 Europe/Berlin

At85cbabe, threadPRRT_kwDOUu9-oc6otla4 showed an expectation list containing all required conclusion names passes key coverage then raises AttributeError at mapping iteration. Independent full affected fixture metadata investigation retained the existing malformed-case shape post-investigation escape; the prior detector-focused closure missed this consumer.

The actual maintainer until-green request and coordinator scoped interpretation continue batch14 with UNCHANGED240 active minutes, preserving all history and without inventing a numeric human reply or extra time. Spec-first controls failed4/passed15 before repair. The minimum explicit expectation-dict guard precedes set/items; valid mapping key coverage and exact value types remain unchanged. Fault/repaired controls cover all JSON expectation types, bad keys/value types, malformed outer inventories and safe CLI rejection. Original18 fixture bytes/expectation dictionaries, hosted oracle, evaluator, register and native boundaries remain unchanged.

Final505 source tests pass. Independent affected closure, complete staged main/priorHEAD proofs, fresh supported native and current required providers remain pending.

## Evidence provenance scope continuation — 2026-10-04 Europe/Berlin

Current b77e2c0 Codex review5403784599/threadPRRT_kwDOUu9-oc6otyGd demonstrated missing/blank/nonstring evidence scope accepted even with freshly rebound native usage proof. Independent adjudication confirmed existing source-register provenance completeness escape and clarified the already present scope key; this is not a new profile/schema or authentication mechanism.

The coordinator selected a bounded15/270 continuation under the actual maintainer until-green request, preserving14used/235.809active and all failures. Those numeric resource limits are coordinator interpretation, not a fabricated new human quote. Spec-first controls produced38fail/1pass before the minimum nonblank-text guard. Four origins and all malformed JSON scope types, uncertainty repairs, fresh/stale native proof binding, loader/matrix consumers and report/error privacy are covered. Existing profile digest already includes scope; no fingerprint change was required. A documentation edit initially looked for an absent bracketed changelog header; that construction failure was retained and corrected to the actual Unreleased heading.

Final544 source tests pass. Original18fixturebytes/expectations, register content, source evaluators, hosted obligation and native approval criteria remain unchanged. Scope notes record provenance claims, not authenticated truth. Independent affected closure, complete staged main/priorHEAD proofs, fresh supported native and required current-head providers remain pending.

## Multiplier and compound fixture continuation — 2026-10-04 Europe/Berlin

Currentd7b16e4 Codex5403840343/threadsPRRT_kwDOUu9-oc6ot54g/54h demonstrated ignored extra multiplier records and hosted semantic early rejection masking malformed expectation metadata. Independent full affected consumer plans retained existing quantity-completeness and malformed-fixture shape post-investigation escapes. Actual maintainer until-green authorization/coordinator interpretation continue16/270 with no extra minutes/new numeric human quote/history reset.

Initial red26/6 included a faulty nested constructor targeting deliberately uninterpreted host usage. It was corrected before implementation to the actual consumed checkpoint data, producing meaningful red27fail/5pass. Minimum repairs select an explicit single-record multiplier strategy before the shared span detector and validate expectation dict/key coverage before detector evaluation/hosted early continuation. Exact values/types, other multi-span behavior, hosted semantic obligations, billed-money uncertainty and native policy remain unchanged.

Fault/repaired controls cover replay/conflict/malformed/bool/null/missing extra multipliers in both orders, compound missing identity/conflict/nested shapes with malformed or wrong-key expectations, valid expectations with malformed consumed checkpoint data, and CLI privacy. Final576 source tests pass; scoped Ruff format/lint passed. All original18fixturebytes/expectation dictionaries and register contents remain unchanged. Independent affected closure, complete stagedmain/priorHEAD proofs, fresh supported native/current required provider acceptance remain pending.

## Citation destination continuation — 2026-10-04 Europe/Berlin

Current91c3252 Codex5403883235/threadPRRT_kwDOUu9-oc6ot_85 demonstrated hostless HTTPS references accepted by prefix-only validation. Independent register citation-family adjudication retained the provenance completeness escape and prior missed URL-structure coverage. Existing actual maintainer until-green/coordinator interpretation continue17/270 with no extra time/new numeric human quote/history reset.

Spec-first controls produced10fail/11pass. Minimum standard-library parsing requires a string HTTPS URL with nonblank hostname. Hostless path/query/fragment, malformed brackets, other schemes and JSON types reject through existing safe register diagnostics; valid destinations, loader/matrix consumers and fresh/stale native approval bindings are covered. Profile digest already binds URL metadata, so no fingerprint change was needed. No DNS/reachability/provider-authentication/domainallowlist request or policy was added.

Final597 source tests pass, scoped Ruffformat/lint passed. Original18fixturebytes/expectations, register contents, source evaluations and native approval criteria remain unchanged. Independent affected closure, complete stagedmain/priorHEAD proofs, fresh supported native and required current-head providers remain pending.

## Default research byte provenance continuation — 2026-10-04 Europe/Berlin

Currentfb182fc Codex5403919410/threadPRRT_kwDOUu9-oc6ouEvE demonstrated reserialized identical case JSON changes the fixture digest while the default CLI succeeds against stale registered research references. Independent affected provenance investigation retained the existing source-report-provenance consumer escape: earlier manifest-focused closure missed the default research route. Two initial read-only reproductions used a /var symlink path and safely rejected source-unavailable; the corrected /private/tmp reproduction confirmed the defect.

Existing actual maintainer until-green/coordinator interpretation continue18/270 with no additional minutes/new numeric human quote/reset. Spec-first byte/alias controls produced7fail/1pass. Minimum repair requires all twelve exact canonical profile/evidence aliases with synthetic origin and one agreed digest, reads bounded bytes once, hashes before parsing and parses those same bytes. Every alias has stale/missing/wrong-origin fault/repaired controls; hash-before-parse, file replacement after the one read, duplicate keys and malformed UTF-8 preserve input protections. Final644 source tests pass with scoped Ruffformat/lint.

The matrix-drift fixture control now uses original received bytes; synthetic semantic CLI faults are injected at the explicitly in-memory check_cases stage after genuine canonical provenance succeeds. This preserves meaningful privacy/semantic tests without a production hash bypass. Matrix-only mode does not read fixture bytes, and direct check_cases intentionally claims no file provenance. Original18 fixture bytes/expectation dictionaries, register contents, source evaluations and native approval criteria remain unchanged. Independent affected closure, complete stagedmain/priorHEAD proofs, fresh supported native and required current-head providers remain pending.


## Planning reconciliation — 2026-10-06 (Europe/Berlin)

PR #33 delivered the offline tooling at merged `340668e6b74bfb7ccab15efe13830555bc6dd7ef`.
The current preparation is based on fresh main `ee424b5cf3c116b18515cec1ee086e1a6de223a0`.
Only planning, lifecycle and dated documentation references change; native profile
observations, all 18 canonical fixture bytes and approvals remain unchanged. No
behavior was added, so no new runtime red/green result is claimed. The default
checker passes with `errors: []` and `semantic_approval: false`; strict all-spec
validation passes 11/11 after native advisory archival. Full preparation gate and
independent review results are retained in the ignored preparation receipt.
Native evidence/finality and paired hook inspection remain incomplete; prior Linux
assurance is historical and source approvals remain zero. Earlier review-session
receipts are absent from this checkout; no correction allowance is reset.


Preparation quality result: 3,030 existing tests passed in 32.62 seconds, both
host tool-fixture proofs and all applicable host leaves passed, strict OpenSpec
11/11 and independent affected review passed. Full make check remains nonzero only
because all ten native analyzers cannot run on this Darwin controller. The first
invocation's inherited Make-overrides fixture failure and its corrected environment
invocation are retained in research evidence and ignored logs. No new runtime TDD,
source approval, current Linux assurance or publication acceptance is claimed.


## Inventory reconciliation — 2026-10-07 (Europe/Berlin)

Base `dc26715d2b583a31050c1cf7fda8ed0e9a9d5507`; owned branch
`codex/reconcile-source-feasibility-20261007`. This batch updates metadata, specs
and documentation only. No new product or checker behavior is implemented; no
failing-before TDD result is invented. Existing regression tests are applicable
verification of the delivered tool. All 14 historical profiles and original case
bytes remain unchanged; nine separate profiles retain zero approvals.

The seven selected native JSONL digests still match and eight canonical bindings
pass bounded structural inspection with semantic approval false. Header inventory,
mixed-version rows and selected SQLite row digests retain separate scopes. No
whole-database/WAL identity, native aggregation or learning eligibility is asserted.

PR #38 merged at `dc26715`; its Python 3.11.15/3.13.14 Linux jobs passed in run
37670722956. That is historical evidence for the prior planning tree only.
Current-diff checks and independent inventory review are recorded separately in
RESEARCH_EVIDENCE.md and the ignored reconciliation receipts. The original source
review-session state is missing; no allowance is reset. Publication, closeout and
archival remain incomplete until original recovery and applicable assurance.

A cached x86-64 Linux image has SpecFact CLI 0.55.4, but no required code-review
module and denies unprivileged namespace isolation. Its Python 3.12 environment
does not reproduce the required 3.11/3.13 matrix. This inspection is not a passing
Linux assurance run and no tooling/account configuration is changed to imply one.


### Observed reconciliation verification

The corrected 19-file pre-receipt freeze passed the source suite (644), default
register/matrix/all-18-case checker (`errors: []`, `semantic_approval: false`),
selected/all strict OpenSpec (14/14), documentation ownership/links, generated
references and independent source/documentation review with no remaining findings.
All 14 historical objects and three protected fixture digests were unchanged.

`make check` used explicit `BASE_REF=dc26715d2b583a31050c1cf7fda8ed0e9a9d5507`
and an intended 19-file manifest as environment variables. Initial cache permission,
hygiene rb+ access and build-network failures were preserved; targeted authorized
hygiene/build reruns passed. Lock/faulty-repaired host proofs, lint/58-file format,
types (zero errors), docs/index/metadata/workflow, 3,030 tests (42.25 seconds) and
build/two wheel smokes passed. Dependency audit was not applicable: locked inputs
unchanged. Aggregate remains nonzero because fresh SpecFact 0.55.4 full review
reported FAIL/UNKNOWN with all ten analyzers unsupported on darwin-arm64-cp312.
No selected subset, old PR #38 Linux run or independent inventory review substitutes
for current-diff native assurance. No package version change is required.

Final task/evidence receipt updates require affected docs/index/strict readback;
they do not change the tested Python behavior or original fixtures. Missing source
review-session history and supported-Linux evidence block publication and acceptance.
No commit, push, issue closure, CLI archive or #35 runtime implementation occurs.

### Separate post-merge review scope — 2026-10-07 (Europe/Berlin)

The maintainer authorized a fresh bounded review of the current reconciliation,
using session `pilot-01-source-feasibility-reconcile-20261007`. Existing task,
research, native inputs, prior failures and corrected review findings are retained.
The prospective input fingerprint is captured separately after this documentation
update. Earlier checks remain evidence for their recorded fingerprints; no old
passing result is represented as fresh bound review evidence. No runtime change
or failing-before TDD claim is introduced.

Partial original initialization/read/state records were copied from execution
history and verified against their sources. The original PR #33 session is not
restored or reinitialized. The preceding missing-receipt publication block is
historical following this explicit choice; fresh current-scope checks, independent
review and supported-Linux assurance remain incomplete until actually obtained.

### Native coverage timeout repair — 2026-10-08 (Europe/Berlin)

PR #39 at `c01ec1bb94acfff5b8a7f85e268a5ae8eb090f4a` reached genuine hosted
Linux assurance on Python 3.13, but both Python 3.11 job attempts failed native
`targeted-pytest-coverage` with `sandbox_launch_failed:timeout`. Nine other native
analyzers passed; the ordinary 3,030-test suite passed. Both native test runtimes
used Python 3.13.11 with identical package versions. Selected follow-up diagnostics
passed 586 review-session tests (1,758 setup/call/teardown records). The full failed
reports do not identify the precise slow case; active descendants and the signed
300-second limit support a performance/deadline diagnosis, not a proven host-version
defect. Original reports, bindings and the successful 3.13 artifact are retained.

The maintainer requested analysis and repair. The existing bounded session explicitly
expanded its scope for test arrangement and correlated documentation, retaining
previous counters and evidence. No new allowance or replacement receipt was initialized.
Independent review identified 67 ordinary default-arrange functions (198 existing
parameterized cases) eligible to reuse an independently copied pristine receipt.
The helper performs real canonical replay, exact contract comparison and current
Git-input capture before copying. Initialization/race/corruption/replay/loss/index
controls and every original assertion, decorator and parameter ID are unchanged.
Seven additional cases verify binding, inode/event isolation, dirty/tampered clone
detection and rejection before copying. No runtime, analyzer, vendor, lock, test-selection
or deadline change is included; this test scaffold adds no product capability.

The independent ten-arrangement local probe measured 15 Git calls per real initializer
versus five per guarded clone, taking 0.8871 versus 0.3127 seconds. Controlled local
coverage runs used the locked project with temporary `coverage==7.15.4` and
`pytest-cov==7.1.0`, without modifying project dependencies. The original full suite
passed 3,030 cases in 41.58 seconds. The review-session comparison passed 586 cases
in 23.14 seconds before and 593 cases in 19.71 seconds after the repair.
These measurements establish reduced arrangement overhead, not native timeout
resolution. Fresh current-head aggregate, independent closure and supported-Linux
matrix/provider evidence remain necessary. Package version and source approvals
remain unchanged; no runtime failing-before TDD claim is fabricated for this scaffold.
