# Offline adaptive demand implementation evidence

Status: locally implemented, not committed/pushed/accepted. Recorded **2026-10-11,
Europe/Berlin**. Package `0.1.0.dev0`, portable envelope `changecost/v1`, SQLite layout 2.
No native reader approval, actual pilot accuracy or release is established.

## Inputs, scope and recovery

Fresh remote main: `5fe5e2e8f63dbf49eeeb77115ba19c67e063c21e` (PR #42 included).
Branch: `codex/forecast-01-local-adaptive-demand`. #35 implementation was explicitly
authorized; #36, #17 runtime and publication remain separate. #11/#12/#15/#16
prerequisites were closed in the verified issue state on 2026-10-11. The matching
preparation stash `f030458fecebd054fc0e3c6c2119972a7769dd8f` was inspected and is
superseded by merged PR #38 (`dc26715`); it was retained and not reapplied.
The existing planning history and unavailable preparation review remain preserved.

Root is the sole writer. One independent read-only obligation reviewer inspected
contracts/authority before implementation, then reviewed affected runtime obligations
and correction deltas. The original critical checkpoints used three existing tests:
portable import/local authority and backup, backdated input cutoff and receipt
fault controls; all three passed before dependent implementation. These prove only
those existing boundaries, not new demand accuracy. Exact initialized inputs and
review-session binding are retained under ignored `.changecost/workflow/forecast-01-local-adaptive-demand/`.

## Red and green proof

Environment: Python 3.13.14, uv 0.12.19, pytest 9.1.1, Ruff 0.16.9,
BasedPyright 1.40.1; OpenSpec CLI 1.13.2. Commands run in the repository virtualenv.
Report timestamps below are completion times from retained local files, in Berlin.

| Command / behavior | Failing evidence | Passing evidence |
| --- | --- | --- |
| `pytest -o addopts='' tests/test_demand.py -q` | 22:58, `red.txt`: missing demand module before implementation | Synthetic demand scenarios pass after implementation |
| `pytest -o addopts='' tests/test_demand_cli.py -q` | 22:59, `red-cli.txt`: absent explicit demand option, 1 failure / 1 pass | Demand parser tests pass |
| Demand initial/diagnostic property | 23:05, `red-validation-ready.txt`: missing initial marker; its second failure was an overbroad imported-history expectation | Initial pre-work marker and conservative import expectation verified |
| `pytest -o addopts='' tests/test_demand.py -k 'laundered or overlapping or advancing' -q` | 23:11, `red-closure.txt`: all 3 fail for reproduced authority, rubric drift and clock defects | 23:11, `green-closure.txt`: 26 demand tests pass |
| `pytest -o addopts='' tests/test_demand_controls.py -k explicit_economic -q` | 23:13, `red-minimum.txt`: explicitly supplied economic minimum accepted | Explicit minimum rejects before demand persistence |
| `pytest -o addopts='' tests/test_demand.py -k 'same_transaction or maps_donor' -q` | 23:14, `red-second-closure.txt`: 2 fail for tied rubric and omitted donor history | 23:15, `green-second-closure.txt`: 29 demand tests pass |

Earlier `red-validation.txt` and `red-validation-fixed-fixture.txt` contain missing
fixture-import NameErrors and are **not** behavioral red proof. The original import
failure is proof only of absent demand functionality; individual scenarios were not
all separately executed red before code existed. Task completion below retains that
TDD granularity limitation rather than claiming per-scenario red execution.

A compatibility run of demand, economic quote, CLI and advisory tests passed
**701 tests** before later closure changes. Final full-suite/gate outcomes are recorded
below after execution; that earlier result alone is not final-current-input assurance.

## Invariants and corrections

- Separate demand records and exact typed requests retain local computation authority;
  portable claims cannot manufacture receipts. Backup preserves receipts and replay.
- Full terminal Change aggregates include all attempts, zeros and abandonment.
  Native Run identities, unsupported semantics, mixed models, incomplete coverage
  and late assessment/ecosystem snapshots remain excluded.
- Target/self and future bridge history are excluded; historical cutoff replay is
  immutable. Complete dimension matches precede broad known-ecosystem history.
- Exact median-ratio calibration and matched-pair residuals stay separate from
  mapped eligible donor aggregates/counts. Donors do not become target observations.
- Validation requires an explicitly pre-registered scoped rubric and reproduced local
  initial predictions with complete truth. New failure/drift withdraws later support.
  Latest overlapping policy ties fail closed; baseline evidence references must match
  exactly, while separate capture timestamps may differ. #17 owns pilot thresholds.
- Optional rates remain estimated authority; rehearsal is supplied/minimized with
  separate bounded overhead. No reader, telemetry, model request or sharing runs.

Independent review found three first-batch defects. Their meaningful regressions
failed before fixes. Follow-up closed native identity and clock handling, exposed
an availability-tie escape in the validation family, and identified incomplete donor
mapping. Before batch 2 the validation invariant was investigated across multi-record
imports, snapshot iteration, compute/replay callers, policy drift and failed heads.
Two-batch history and remaining findings are retained in the existing review session;
its allowance was not reset. Provider Codex and CodeRabbit reviews remain required
at the subsequent stages because authority and persistence changed.

## Remaining gates and rollback

Final local results and affected-scope closure are appended below. Fresh supported
Linux x86-64 SpecFact assurance and the Python 3.11/3.13 CI matrix remain acceptance
requirements. macOS tests or unavailable analyzers do not establish those results.
No provider review was requested by this implementation-only stage; no PR exists.

Rollback the uncommitted branch diff while retaining exports and a compatible SQLite
backup. There is no schema-layout migration. A prior checkout can reject additive
record kinds, so use its corresponding backup rather than deleting new records.
No paid infrastructure or package publication was introduced. Delivery duration
for the native pilot remains unknown until #36 accounting is approved.

## Final local verification — 2026-10-11

- `BASE_REF=origin/main MANIFEST=.changecost/workflow/forecast-01-local-adaptive-demand/manifest.txt make check`:
  **3,083 tests passed in 28.83 seconds** on Python 3.13.14, four workers.
  Lock probes, hygiene, Ruff lint/format, full BasedPyright (zero errors), docs,
  generated index, metadata, workflow validation and isolated wheel/sdist build
  with fresh-environment smoke installation passed. Dependency audit was explicitly
  not applicable because locked dependency/audit inputs did not change.
  All **15 OpenSpec items** passed strict validation.
- The aggregate command exited 1 (make exits 2) solely because SpecFact CLI 0.55.4
  lacked its `nold-ai/specfact-codebase` module and produced no review report.
  Supported-Linux full enforcement, required analyzers and Python 3.11 CI remain
  **incomplete**, alongside subsequent provider reviews. No assurance waiver exists.
- The earlier gate attempt exposed inherited command-line make variables in its
  isolated fixture and a negative-test constructor typing error. The final invocation
  supplies BASE_REF/MANIFEST as environment variables so the fixture can remove them;
  this changes no validator. Boolean untrusted-input rejection now uses model_validate
  rather than an intentionally ill-typed constructor; the independent reviewer
  accepted this test-only delta and its targeted test passed.
- Independent final affected-scope closure: no remaining findings. **29 demand tests**
  passed in 0.93 seconds; separate temporary-store probes confirmed that earlier
  validated and bridge-bearing forecasts replay after later ties/donor history.
- Final documentation ownership validation and `git diff --check` passed after
  aligning proposal/agent/config status. Runtime inputs did not change after full tests.

Native issue relationships and acceptance are unchanged; #35 remains open. No
commit, push, PR, archive or release was performed. Next stage:
`$changecost-verify forecast-01-local-adaptive-demand` with the existing review
session and retained pending assurance; do not initialize a new allowance.

Retained report SHA-256 values:

- `red.txt`: `a57b4500eb863cb24e6174edd938ddb5703b9bde6647260931f78e213c99c881`
- `red-cli.txt`: `d33b5688f7b0fa68302f404dc295048514ab2a3be68574a657757677bfbaa569`
- `red-closure.txt`: `2860b77b334c73c7f88f658c59b3590e22360a346992a39eab3a9394d0a03a5d`
- `red-minimum.txt`: `3440792cf76fc00f6c39cae8559ee7c3c6c7a14c684950cd988b3ef0ab0e6281`
- `red-second-closure.txt`: `abce20afbcf558ca2e3179cfd8c6fdfbcb37379fd40fe6d40d775543e8cb6d8e`
- `green-second-closure.txt`: `2ef4a1f36ea091aa55cf2a37260a8169fbbc40db5d212fadb948518ff5513e41`
- `demand-final.txt`: `f0e4d7e201812f3b10eb439b3ebed9241f6002ca1f0b2a2df181607f186efbfa`
- `make-check-final.txt`: `50bcc1f0c47e54be2755b88a0f838e9cf4f1f27d4bdce85c9c0931ad92ffb31d`

## Verification continuation — 2026-10-11, Europe/Berlin

The maintainer explicitly accepted the documented grouped-red granularity limitation
and authorized three additional correction batches / 60 active minutes. The original
session, findings and counters are retained; this is not Linux assurance or defect waiver.
Tasks whose behavior is implemented and passing can now close with this narrow accepted
historical-proof limitation. Do not claim retrospective per-scenario red execution.

Three independent verification lanes confirmed exact current inputs. A grouped semantic
freshness finding corrected stale planned/unimplemented claims in CLI, proposal, design,
index and generated llms; affected-document closure passed. No new runtime/quality
findings were reported. The same runtime/test hashes retain prior defect closure.

`BASE_REF=origin/main MANIFEST=.changecost/workflow/forecast-01-local-adaptive-demand/verify/manifest.txt make check`
passed 3,083 tests in27.90 seconds, all applicable local mechanical leaves and15 strict
OpenSpec items. Independent demand run passed29 tests in0.97 seconds. Dependency audit
remains not applicable (dependency/audit inputs unchanged).

The repository-pinned signed `nold-ai/specfact-code-review`0.50.1 module was installed
through SpecFact0.55.4's native verified official installer with the configured immutable
registry. Its actual native report now exists: overall FAIL, assurance UNKNOWN, exit1,
all10 required members UNKNOWN/error with `unsupported_controller_platform`.
Report SHA256:`1bf0ced79c8fe00330792a528eac19a216893aff259a50d31ae43f49b6b6ea4a`;
sidecar binds246 inventory files with digest
`148b2398cd91b4171cb2db87d24391e1e549e9795594a9467eb32693d5414cb5`.

Per the repository's explicit macOS procedure (gate guide, hosted assurance), the
reviewed feature commit/push bootstraps a manually dispatched Ubuntu quality matrix.
Full verification stays pending until both3.11.15/3.13.14 jobs and all native required
analyzers pass. This preliminary publication is neither accepted implementation nor
a verified Linux result. The user's subsequent full local CodeRabbit/review-agent scans
remain to be performed after this verification. No PR, merge, archive or release is
part of this verification request.


## Supported-Linux maintainability correction — 2026-10-11, Europe/Berlin

Commit `570a5253ff36ec017c01adbcfc79c5862a590b6a` was pushed using the documented
macOS bootstrap procedure. Repository quality run `38176917319`, Python 3.11.15,
executed all ten required native analyzers: nine passed; Radon failed with twelve
blocking complexity/parameter findings. Required evidence was complete, not UNKNOWN.
The complete native test collection contained 3,083 tests. Report SHA-256:
`3a370434fe3c8a069f1e77b2554966c836854019372787485f2442c8a9937bba`;
full input sidecar digest:
`3c79d0712c0dfd4582011c118a53215044bdccbd170b38b2b7f66e745fda00d8`.
The Python 3.13.14 leg failed during a Go toolchain download before project checks;
only that setup failure was retried. Neither failed run grants acceptance.

Correction batch 4 groups explicit request selectors and captured forecast inputs,
extracts observed-summary checks, latest rubric selection/receipt heads, per-case
measurement and transfer mapping, and groups synthetic peer options. Exact request
identity, cutoff/replay, validation withdrawal, terminal all-attempt truth, donor
cohort separation, serialized records and CLI option semantics remain unchanged.
Local Radon 6.0.1 now reports the affected functions/classes below blocking limits;
29 demand tests pass and basedpyright reports zero errors. Native thresholds,
suppressions and analyzer requirements were not altered. Fresh complete local and
supported-Linux gates plus independent affected closure remain required for this delta.

Nonblocking native advisories are reviewed separately: explicit schema/test names
retain their existing concise documentation; local imports retain dependency boundaries;
fixture naming/setup order, exact-type guards and immutable transaction callbacks are
intentional. Complexity/parameter advisories are rechecked after decomposition; unrelated
pre-existing warnings remain outside this change. No native defect waiver follows.


The corrected local aggregate passed 3,083 tests in 35.79 seconds, package build/install
smokes and 15 strict OpenSpec items. The native local leaf produced no report because
the host's previously installed review module was no longer available; its result stays
incomplete. The earlier unsupported report remains historical evidence only. Required
native assurance runs in the supported Ubuntu matrix; no repeated local capsule attempt
or accepted native exception is implied.

Independent quality, runtime and documentation lanes found no issues in the frozen
refactor. All 32 path fingerprints matched. Runtime closure passed 29 tests in 2.91
seconds and reproduced original pre-refactor transfer forecasts and measured validation
receipts under the corrected runtime. Current blocking metrics are CC7/10/13/8 for
validation selection, estimate, measurement and computation; Run truth CC11; transfer
CC9; DemandResult/state validator CC11/10. Request/estimate/CLI helpers each take two
parameters; the peer helper takes four. Fresh exact-commit hosted acceptance remains
pending and is not inferred from these local measurements.


## Explicit price-selector correction — 2026-10-12, Europe/Berlin

An independent temporary-store probe at `2fda36b2350a29d61a89d8ed337f8f54b7c0d2fc`
confirmed `--price-id ""` exited zero, inserted an unpriced forecast and changed sequence
12 to 13, silently replacing the supplied selector with omission in the receipt. This
violated the documented incomplete-request boundary. Correction batch 5 adds an explicit
specification scenario, API/CLI controls for empty/ASCII/Unicode-whitespace identifiers
and identifier validation before transaction opening. Omitted `None` and valid scenario
selectors retain their behavior; rejected requests leave the operation ID reusable.

Before the guard, three API regression cases failed; three fresh-store CLI controls
already passed because the Change was absent. The final CLI controls additionally cover
an existing registered store, matching the independently reproduced defective call path.
No claim is made that those later added assertions ran red before implementation.
All 35 demand tests pass after the guard. Red report SHA-256: `7c169c30737f4c35d580fd08bb0f88cde9ea561ed31ea40ce58f175b1ed545c7`;
green report SHA-256: `7c40f5592bf6f725d2765ba69efed68de76037f254a07b6f3737ab4e51613458`. Fresh complete gates, independent affected closure
and supported-Linux assurance remain pending for this new delta. The previous Linux
matrix covers the pre-selector-fix commit only.


## Styled help assurance correction — 2026-10-12, Europe/Berlin

Run `38178551294` at `2fda36b2350a29d61a89d8ed337f8f54b7c0d2fc`, Python 3.13.14,
produced complete native PASS assurance / PASS_WITH_ADVISORY, exit zero, no unknown
required evidence and all ten analyzers ran PASS. Native report SHA-256:
`377b74bb52b2f6b36da839645f48185939fd5f638cf3a7d4107d83c8645a83bd`.
The host pytest gate failed one help assertion (3,082 passed): ANSI styling split
`--demand` in captured output. The passing native report does not waive that failed
host gate or certify the later blank-selector/current input delta.

Correction batch 6 changes only the help test oracle: explicit plain/styled controls
retain zero exit and complete demand/assessment flag assertions, normalizing SGR color
sequences before matching text. The styled case verifies ANSI output is present.
Actual pre-normalization control: one failed styled case, one passing plain case.
After normalization all 36 demand cases pass. Runtime CLI rendering is unchanged.
Red report SHA-256: `61b3a92dacef003e86f32b7719aeb501c3db78e5317c65dd81c94be7a927a84d`; green SHA-256: `d765413853f65a735dc2abe8a1297db96bb0c192e48883a7f5988944264fa2ad`.
Fresh staged/full gates and independent affected closure remain required; final exact-head
Ubuntu matrix/native assurance and the explicitly requested later full scans remain pending.


## Full-scan chronology correction — 2026-10-12, Europe/Berlin

Commit `0dab2b12ba218f3a1c301ed4b0435970c4465e09` passed Repository quality
run `38180838215` on Ubuntu 24.04 / Python 3.11.15 and 3.13.14. Each native report
ran all ten required analyzers PASS, exit zero, no unknown required evidence, no
blockers and PASS_WITH_ADVISORY. Both sidecars matched the actual 246-file digest
`ee12f217c943a5dfc9c69ac5f7244fe54cbb85ff1bfd24594543f62454db5b38`.
Report SHA-256 values: Python 3.11 `6eecd3cfadc404484c2bb2af079565e7292cd8abb93f9a297e82aaed4e4098c5`;
Python 3.13 `3e8845e7cd869653534d13478cc73c20a0539af84acd7a79b90ed77e534cbd7a`.

The maintainer extended the preserved session from six to eight correction batches,
retaining its 150-minute limit. CodeRabbit CLI 0.9.0 completed the full 31-path
committed diff review with zero findings (`review_completed`, not skipped). A fresh
independent full review-agent scan covered the complete diff and surrounding code,
reporting one P2 chronology defect and no additional security/code defects: a forecast
or baseline captured after actual work starts was admitted when Run registration
occurred later. The stored initial flag correctly described its own earlier visible
snapshot, but could not prove chronology against subsequent complete truth.

This genuine evaluation-cutoff-family escape received a family-wide invariant review
before correction; prior findings and investigation history remain retained. Batch 7
reuses truth work-bound derivation to check each prediction's own cutoff before
measurement. Original forecast snapshot replay and the accepted distinct-clock,
identical-input baseline behavior remain unchanged. No provider collection or new
accuracy claim is introduced.

Five specification-derived controls cover candidate before/equal/after work, baseline
equal/after work and legitimately future work registered later. Before the guards,
four invalid cases failed and the legitimate case passed. Afterward all 41 demand
cases pass; invalid receipt creation preserves the store and does not promote later
forecasts. Both original candidate/baseline forecasts still reproduce.
Red report SHA-256: `907f8a46f1fba7900ee0db7adcb3b8d52000a4bc7fc140935369c914a299d370`; green: `77dbf277dfd95d88b958c973337d4d9d7531a6bc5341060a344b53c4876b9c96`.
Fresh affected closure, complete local/staged checks, exact-head Ubuntu assurance and
CodeRabbit verification remain required for this new correction; earlier reports
certify only their original commit.


## Current-capability documentation correction — 2026-10-12, Europe/Berlin

The fresh CodeRabbit review at `c6ff024c814e54bc2e5e6a571456ca74d961b3f7`
completed all 31 changed paths and returned one `minor` finding: the README's
retained planning summary contradicted the implemented demand CLI. No further
runtime issue was reported. The first documentation-freshness-family escape
received an independent complete current-summary investigation before correction.

The final authorized correction set reconciles that README section, the project
brief's unqualified no-runtime statement, financial-versus-demand replay qualifiers,
the OpenSpec context's original pilot/planned command descriptions and current #9
status summaries. GitHub read-only evidence on 2026-10-12 confirmed #9 closed and
PR #39 merged; all 23 native profiles remain unapproved. Current Codex reader and
native/evaluation/publication gates remain separate. Dated research/archives and
historical change-order entries remain unchanged. An inherited advisory-status line
in untouched docs/quotes.md predates #35 and is outside this introduced-change scope.

Runtime and tests are unchanged from the independently closed chronology fix.
The preserved session permits eight correction batches / 150 active minutes;
this last documentation batch includes its closure and final exact-head checks.
Its completed consumption will be recorded without resetting history or allowance.
Current Linux and CodeRabbit results must cover the final committed contents;
earlier reports remain bound only to their original inputs.


## PR #43 coverage and replay corrections — 2026-10-12, Europe/Berlin

Both current-head providers completed code review at `0e32a9a298fc3229d916a635cd68d28484032cd2`. Codex review 5494547632 reported a P1 unknown-transfer allegation and a P2 incomplete Run-start coverage defect; CodeRabbit review 5494582211 reported one Major repeated-replay performance defect. The P1 allegation was independently disproved: a known bridge control works, while 24 source/target/both unknown-field controls either reject typed provider/surface omissions or produce no transfer through the existing observation identity guard. The scoped reply and resolved thread retain that concrete non-finding; no defensive preference change is made.

The P2 is reproducible through supported interval/observation corrections: an immutable Run start at 10:00:02, with both current interval and observation moved to 10:00:02.500000, previously admitted a partial quantity as learning truth. Coverage eligibility is distinct from the earlier forecast-capture chronology family. Run has no observed-end field: the latest interval supplies end. The correction requires coverage of the known immutable start as well as the latest interval, while absent starts retain current-interval semantics. Registration time and superseded interval bounds are not new measurement boundaries.

The Major performance defect is independently demonstrated with six public validation generations under BEGIN IMMEDIATE: forecast replay calls grow 2, 6, 14, 30, 62, 126 for only 2, 4, 6, 8, 10, 12 distinct forecasts; validation replay calls grow 0, 2, 6, 14, 30, 62 for zero through five distinct receipts. The new repeated-replay family does not reinterpret rubric applicability or capture authority. One ephemeral ReplayContext per public operation now reuses only completed results, binding the actual record serialization/cutoff and visible revision identities. Original local cutoff authority and required-input availability are checked before cache use. No global or persisted cache, provisional cycle sentinel, provider admission or package/version change is introduced.

Specifications preceded tests and implementation. The first selected run reported three failures and five passing controls: the learning-coverage and 31-versus-five replay-count assertions failed on the intended behavior; the initial validation fixture separately failed because its observed start postdated registration. That fixture failure is not product red evidence. The corrected fixture uses a valid later work start, and an isolated detector control restoring the exact pre-fix complete_run function subsequently fails because partial truth is accepted. This is a post-implementation old-behavior detector control, not a claim of earlier per-scenario red execution.

After correction, all 49 demand cases pass (1.00 seconds). Six before/equal/after controls cover known and absent start bounds, preserving original forecast replay. Validation excludes partial truth without persistence. A five-generation call-count detector measures each validation result once per operation, checks two independent cold inspections, read-only exports, foreign imported authority, a new failed rubric withdrawing validation, and preserved older replay. Ruff and BasedPyright report no errors.

batch9-red.txt SHA-256: `a93674b30f46f3c1849a47ddde941b1fd352f5b65e4cc62dea7da6c80fa584df`.
batch9-corrected-validation-old-guard-control.txt SHA-256: `8c82c11ab30d78f5df27de070bd7539e3502d772a1d8f0a612f8d386aae50423`.
batch9-green-corrected.txt SHA-256: `69ca42c31df6b9f86a3574e230b22b236b66613020d5d8431960392ba91e53e5`.

The maintainer explicitly extended the preserved review session to eleven correction batches and 240 active minutes and approved the private diff's CodeRabbit review. This is the ninth collected correction batch; the final current-input independent closure, complete applicable checks, supported-Linux matrix and fresh PR-provider results remain required before acceptance. No historical counters, prior findings or accepted initial TDD limitation are reset. The PR live verification index and ignored receipt will carry exact-head completion without a receipt-only source commit.


## Target-repeat disclosure and historical policy compatibility — 2026-10-12, Europe/Berlin

At PR head `702018bc0f22985a76ea4103cea85b69f01ea7bf`, both required Ubuntu jobs in run 38292161369 passed; independent native report inspection found all ten analyzers ran/PASS, no UNKNOWN evidence, zero blockers and the exact committed 246-file digest `084421e762f219e349d901ffd35bd3bfe830ae227e4ef99a58ef935d1fcc7786`. These results certify that head only. The fresh Codex code review 5494760746 then reported two P2 allegations.

The self-baseline allegation was independently reconsidered against the accepted numerical contract. Zero comparative improvement is permitted by the non-worse criterion; no distinct-artifact/algorithm or positive-improvement requirement exists. Same-artifact cases report equal candidate/baseline errors honestly. Truth outside coverage or exceeding underestimation limits produces failed receipts; distinct normal-candidate/broad-baseline records may legitimately have equal errors. The unsupported minimum_improvement field rejects. The original inference and contrary controls remain retained, with a reasoned non-finding reply/resolution. No stronger #17 methodology or new baseline restriction is invented.

A single eligible peer sharing the target task scope did omit the documented repeat-task dependence warning. This genuine analogue-disclosure defect is corrected without changing target exclusion, eligible counts, quantities, validation metrics or donor hypotheses. Six specification-derived controls ran before runtime edits: three failed (target-repeat single/mixed peers and missing v2 default) and three unrelated/duplicate-peer controls passed.

The correction uses the existing versioned algorithm field: new forecasts default to observed-summary/v2, while v1 replay explicitly keeps its original disclosure. Both labels decode through the additive enum. Request/retry authority, database schema 2 and package 0.1.0.dev0 remain unchanged; no public selector or automatic collection is added. Replay still compares the full payload, and operation-local cache keys include the actual serialized algorithm identity.

All 56 demand cases pass (2.49 seconds). New controls cover v2 target/peer repetition, unique task scopes, unchanged quantities/counts and target exclusion; synthetic v1 forecasts/receipts, exact retries, v1/v2 cold/warm replay isolation, unsupported v3 rejection, foreign-import producer claims and mixed-version backup recovery. A real pre-edit v1 database captured from the 702018b implementation separately preserves four forecast payloads and a passing local receipt, including a single-peer forecast without the new warning. All four forecasts and that receipt reproduce under the corrected code; same-operation retry leaves its export unchanged, and a new v2 result equals the earlier validated numeric result. The original database hash remains `faa876f38f0eec8d363c53e77c8e3116f81aea40085ecc91ed2536ee1ac9e238`. An initial ad-hoc probe selected a different target from the sorted forecast list and its cross-target comparison failed; the corrected probe selects the explicit saved target identity. That fixture selection failure is not product red evidence.

batch10-red.txt SHA-256: `3d1d928ea9813c48e7165f55f5b9d99b2ca474978a1d01e31cf0ee864d8bb62c`.
batch10-green-final.txt SHA-256: `e611d9111d18baf9e6d54ed9fc71e3667e2b533425a40d843d08f7b7b2288070`.
batch10-actual-v1-replay.txt SHA-256: `14ccc04d696f0b4e5e67b1d00d8616bca44a96c607676dd3a641b1719c719093`.

Rollback of the new default must retain v2 decoding/replay for already persisted or exported v2 records. Restoring full older code requires the pre-v2 compatible database backup. No historical record is rewritten. The preserved eleven-batch/240-minute allowance applies; final broadened algorithm/model/serialization/replay/validation/import/recovery closure and exact-head quality/provider gates remain pending for this tenth collected batch.


## Complete-window and imported-lineage corrections — 2026-10-12, Europe/Berlin

Codex review 5494966830 at 74fcfdf identified two reproduced P2 defects: a corrected observation ending before the immutable known Run start still supplied complete truth, and imported validation predecessors were hidden from new local receipt construction, producing a revision-history fork. The first coverage-family escape received a complete point/window/current-revision/attempt/validation/replay investigation before correction. Structural receipt lineage is separate from local promotion authority.

Specifications and fifteen focused controls preceded runtime edits: five failed on the expected coverage, validation-truth, imported continuation and cutoff-unavailable head behavior; ten controls passed. The minimum coverage guard now includes both observation endpoints. Receipt predecessor selection uses the unique structural history head, rejects a cutoff-unavailable head before persistence, and permits promotion only through an applicable current head with its own passing local computation receipt. Imported claims never inherit authority. Old snapshots, exact retry, reimport and foreign claims remain unchanged.

After correction, 67 cases across tests/test_demand.py and tests/test_demand_controls.py pass in 1.09 seconds, including added zero-width coverage and local→foreign-claim→local lineage controls. The latter proves current authority withdrawal, preserved earlier replay, fresh local metric computation and existing-local reimport preservation. Additional compatibility and independent closure remain required. Red SHA-256: `79a7214b1e12181cf35d9a6e0ca516d6e137afa50147aa30b46632ef039b5fc1`; green SHA-256: `eeac7fe4050bba35fa556a2569a8a46170516cbd172795dfc599a21d58c34dee`.

The old 74fcfdf Ubuntu run 38294888318 failed both native jobs: Radon 6.0.1 actually ran and reported CC21 for the mixed v1/v2 compatibility test; the other nine analyzers ran/PASS, UNKNOWN was false, and all 3,110 ordinary tests passed. This is a concrete native maintainability failure, not missing infrastructure or an assurance pass. Its immutable 246-file digest is 5366c0617aa7b4d7bca90ed2237a42791e21caf2ac49d4d578878bfb772da28f. Final current-head gates and provider reviews remain mandatory within the preserved eleven-batch/240-minute allowance. No schema, package or demand algorithm change is introduced by this batch.

The first demand-maintainability escape was investigated across every changed runtime and test function before correction. The pinned Radon 6.0.1 detector reproduces CC21 on the original compound compatibility test. Extracting cohesive replay-cache and backup/import assertion helpers retains every original arrangement and assertion; all declared Python functions now satisfy CC≤20 without a suppression or policy change. This test-only decomposition introduces no runtime behavior. The final native matrix still must certify the eventual commit.


## Approved numeric-resource correction batch 12 — 2026-10-12, Europe/Berlin

Codex review 5495167907 at 29a5378 reported P1 resource exhaustion: compact extreme decimal exponents admitted by new demand primitives can cause unbounded downstream Fraction expansion. Independent public DemandObservation and PriceScenario Bundle import controls confirmed admission without executing the dangerous operand. Economic exact_sum already rejects the same unsupported span through its existing 4096-digit budget. The maintainer explicitly approved one additional distinct correction batch and 60 active minutes (12/300), preserving the previous history and inactive approval gap. This correction is not folded into batch eleven.

Specification-first tests ran before runtime changes: twenty intended numeric guards failed, fourteen ordinary/boundary controls passed, and two import fixtures separately failed because export was attempted on an uninitialized target store. Those fixture failures are not product red evidence. Correcting the target fixture then applying the exact old primitive callback in an isolated serial process causes both public import rejection assertions to fail. This is a postimplementation old-behavior detector, not an earlier TDD claim. An initial detector incorrectly used fresh xdist workers and passed against the current code; that ineffective run remains retained. No huge Fraction was executed and interpreter limits were not changed.

The minimum new-demand-only guard bounds aligned decimal integer/fractional span, coefficient and both exponent directions to 4096 digits, including zero. Rational numerator and denominator components are each bounded before Fraction conversion. Original supported decimal representations and rational normalization remain unchanged; legacy Amount and economic accounting remain unchanged. All 156 focused demand/CLI/contracts cases pass in 1.35 seconds, including 4096-digit positive/negative exponent learning and backup replay, rational boundaries, atomic portable import rejection and legacy economic admission. Ordinary v1/v2 historical records remain supported; previously admitted out-of-budget demand records now reject typed decoding and are not silently rewritten. Preserve their original exports/backups for diagnosis. No database schema, package, algorithm label or public selector changes.

Red SHA-256 `91de49f9b14cd0d1cb6663b971204abce066fd49b33b4911a98d5577703708b8`; focused green `b8639ce27b80618c748a990ad0ee8975d8e09d0410931c53ae2523bba00ca213`; corrected serial old-guard detector `1958e9804110fd800ca89afcf10a3f15653c19eddd6fc783006e65a0faa0f53e`.

The preceding 29a5378 Linux run 38297515631 passed Python3.13 with all ten native analyzers; Python3.11 failed Pylint4.0.7 after the signed 30-second full-source/tests timeout, leaving UNKNOWN assurance while the other nine analyzers passed. All 3,127 ordinary tests passed. Signed module0.50.1 operating code and signature were independently inspected; jobs2 is supported and already configured, but no project deadline override or proven remedy was identified. No vendor patch, analyzer/file reduction, timeout change or selected-diagnostic substitution is authorized. Fresh final-head full native matrix and both provider reviews remain mandatory.

## PR batch13: current temporal revisions and target validation support (2026-10-12 Europe/Berlin)
Maintainer approved scoped replanning and one correction batch plus60 active minutes,
retaining prior counters. Specs precede tests and runtime. Initial four-test red run
recorded three expected behavioral failures (own support, corrected Interval, v3
selection) and one invalid Observation fixture. Its corrected fixture was still
invalid because graph admission requires producer assessment time before observation
start; neither fixture error counts as behavioral red. A public valid Observation
correction uses a start after assessment but before an advanced baseline cutoff.
An immutable8e source snapshot detector after implementation fails precisely with
`baseline was not captured before truth work`; this is post-implementation detector
evidence, not pre-implementation red. Actual logs remain ignored in promote/batch13-*.
The expanded current suite passes18 tests, including selected nested receipt evidence,
metadata contrary controls, corrected Interval/Observation, old algorithms, private
request generations and exact legacy retry. Additional closure/check results follow.
Internal algorithmv3 and local requestv2 are additive decoder/provenance choices;
package0.1.0.dev0, database schema2 and exact payload comparison are unchanged.

First frozen snapshot42: full3184 tests passed27.06s and15 strict items passed.
Independent broad review found no runtime defect, but signed native parameter analysis
found three eight-parameter helpers above its seven-parameter limit. The type checker
also found optional-generation narrowing and a missing baseline assertion. These draft
mechanical failures are retained; cohort options and hypothesis-owned component
selection remove redundant arguments without suppressions or threshold changes.
The initial sandbox aggregate also could not open protected skill files for hygiene
and could not reach pinned build dependencies; it is not a passing aggregate.
Independent actual legacy v1/v2 databases reproduced exactly, including receipts,
retries, new-generation validation of old cases, backup/reimport and foreign claims.
Selected transfer/nested support and diagnostic/structural-predecessor contrary probes
passed; final corrected snapshot evidence follows.

After mechanical stabilization,124 demand/CLI/revision tests passed4.90s and
basedpyright reported zero errors/warnings. The earlier invalid fixtures and failing
mechanical/native parameter evidence remain recorded. No signed analyzer limit,
coverage obligation, checker, source file or deadline was changed. Full Linux timeout
cause remains unknown; diagnostic facts/proposed complete-scope profiling are retained,
and fresh native assurance on both matrix legs is still required for acceptance.

## PR #43 separately approved tooling correction batch 14

The maintainer approved14 correction batches/450 active minutes on2026-10-13,
retaining prior counters, checks and negative history. The bounded correction adopts
the already published, strictly signed review module0.51.2 through its immutable
registry209b4ed835187ea857d1fa847abdd351f6f6232a. It keeps CLI0.55.4,
all67 Python inputs, all10 analyzers, four pytest workers, coverage policy and the
native Pylint30-second/member300-second limits. No supplier patch, signature
bypass, runtime dependency, portable field or product/schema version is introduced.

Original71518ca assurance failures remain negative evidence. The initial signed
candidate matrix38438791168 had nine passing analyzers including Pylint on both
legs, but complete coverage remained UNKNOWN at300seconds. The existing upstream
bounded similarity-window cache passed16 actual supplier controls: cold/warm output,
minimum/ignore settings,256-entry bound and eviction, restoration on error/SystemExit,
message/statistic/exit parity. These functional controls are not native timing proof.

A separately reviewed, read-only live metadata diagnostic38442321709 checked frozen
71518ca with unchanged pins/configuration and deadlines. Its original full check
returned0. The actual report has all10 unique analyzers ran/PASS, no UNKNOWN and
PASS_WITH_ADVISORY. It collected/called all3184 unique cases (3188 passing call
records), matching the prior complete71518ca inventory; coverage is17119/17558lines
(97.499715%). Actual namespace adapter SHA256
62f4855a347c857039b7741448a770f7a7aa063dfca52417c552d662c2984c90 was joined to
owned Pylint/coverage request identities; both requests retain all67 Python files.
The observer returned the original checker exit and never changed analysis inputs,
bootstrap, isolation or deadlines. It establishes loaded-byte and full-scope proof,
not repeatability or primary-PR acceptance. Earlier slower host/native outcomes
remain retained; setup versus test versus export timing is only coarsely observed.

This is a contributor-tool pin correction, not new product behavior. The supplier's
actual controls and original failed/current positive native reports are its proof;
no fabricated product TDD or timeout waiver is claimed. Consumer pin/docs checks,
affected independent closure, and fresh full assurance on both primary matrix legs
plus both current-head code providers remain required after publication. Rollback
restores the prior signed module/registry pins; retained exports and demand v3/private
request-v2 replay requirements are unchanged. Package0.1.0.dev0/database2 remain.

## PR #43 production coverage scope correction — 2026-10-15 Europe/Berlin

The original current-head quality run38445397034 and its failed-job rerun reproduced
the same bounded Linux failure: full pytest execution reached the signed
`targeted-pytest-coverage` member's300-second limit. The passing peer report and the
failed report used the same project runtime family and test inventory. The passing
report measured21 installed `changecost` files plus46 snapshot files from `quality/`
and `tests/`; reviewer evaluation already excludes collected test files from its
production-source coverage obligation. The excess test-body tracing therefore added
execution work without covering an accepted runtime source.

A repository contract test preceded configuration. It failed with missing
`tool.coverage` and SHA256
`98de608e88241174ad96633e701ad1ed270fc8f0f830e86bf15ead8d5f961141`, then passed
after `source_pkgs = ["changecost", "quality"]` with SHA256
`4bcefcc9f6c645923b9993ccf73ad92e6b400ca25458ea14e095857fc2131342`.
The exact coverage7.15.4/pytest-cov7.1.0 stack measured both source families in a
focused control and no `tests/` files. Its full local macOS run kept the canonical
four workers and complete inventory:3185 passed in32.48seconds, measuring21 product
and17 quality files, zero test files and94.837534% aggregate line coverage. Report
SHA256 is `521629a930fc14d9342b18a66c3088417f3a916efb01997f75fe84beb1145baf`.

This first correction changed neither test selection nor the analyzer, threshold,
worker or deadline policy. Fresh supported-Linux matrix evidence remained blocking
because local macOS timing did not prove that the hosted capsule would finish.

## PR #43 two-CPU worker correction, 2026-10-15 Europe/Berlin

The signed `b6bda8f` matrix records reported two available CPUs on both legs. A
rerunnable census over the native process records found 12 to 16 live processes
during each high-process phase. The passing leg had a median of three runnable
processes and a peak of four. The failed leg had a median of three and a peak of
five. Both records used input digest
`68c556c240eb94b128dd31f1fd3d721711ffb658eb2e760e64d37a5802af9aed`.
One coverage member completed in about 246 seconds and the other reached its
unchanged 300-second limit. The runnable-process excess motivated a two-worker
candidate; it did not establish timeout causality.

The repository contract test was changed first to require two workers. It failed
only on the expected `-n 4` versus `-n 2` mismatch with log SHA256
`1e55e47e4ad95e58e0469da1d6678b2a67c47dbd8e60df56f75b47301cef8ada`.
It passed after the configuration change with log SHA256
`688435415686b91f3034ff8352c8583f9cfe74b651dec3adfba0532d844d495b`.
Three independent reviewers challenged the plan. Two returned no findings. The
third required both exact-head signed Linux legs to pass before acceptance.

The corrected local coverage run placed the installed console script on `PATH` and
passed all 3,185 tests in 55.41 seconds with two workers. It measured 21 product
files and 17 quality files, no test files, and 94.837534% aggregate line coverage.
The log SHA256 is
`54bc2d7f56f0e2e23d1ce732d8878e4079a07b085a0180a90f28f9ed9194c1d4`.
The coverage JSON SHA256 is
`3c4eda311c78bb84a8e2d514b8ce5d3d5c5aca3c029826d04fc8806121fcad94`.
An earlier invocation omitted `.venv/bin` from `PATH`; only the installed-console
script contract failed, so that run is retained as invalid runner setup evidence.

The correction changes only pytest worker concurrency. Test selection, coverage
sources and thresholds, analyzers, signatures, execution identity and deadlines
remain unchanged. Fresh supported-Linux reports on both exact-head matrix legs are
still blocking. Rollback restores four workers and the matching contract and docs;
all historical reports remain retained.

## PR #43 worker-candidate correction, 2026-10-15 Europe/Berlin

The exact `4938623` Linux matrix disproved the preceding two-worker acceptance
hypothesis. Python3.13 completed all ten analyzers, but its complete native review
increased from 376.947 seconds with four workers to 450.372 seconds with two.
Python3.11 remained incomplete at 485.800 seconds: targeted coverage reached the
same signed 300-second member limit and Pylint separately reported incomplete
execution. The complete passing reports collected the same 3,185 tests and covered
the same 6,246 of 6,586 statements. Individual runs do not prove the worker count
caused every timing difference, but two workers did not meet the required outcome.

Three alternating four-worker coverage runs using `load` had a 33-second median
and 33 to 34-second range. Three `worksteal` runs had a 34-second median and 31 to
35-second range, so the scheduler comparison was inconclusive. Two complete runs
per worker count finished in 33 to 34 seconds with four workers, 28 seconds with
six, and 25 seconds with eight. Every run executed all 3,185 tests with unchanged
coverage. A separate per-file census ranked `tests/test_review_session.py` highest,
but it summed overlapping pytest phase elapsed durations and did not identify CPU
work or a removable fixture cost. Its session-scoped committed and initialized
seeds already preserve isolated test arrangements.

Three independent reviewers rejected the two-worker rationale and found no measured
basis for a scheduler or fixture change. Two selected eight workers as the strongest
single-variable candidate; one preferred six as a conservative intermediate. The
repository contract was changed first to require eight workers and failed only on
the expected `-n 2` versus `-n 8` mismatch. Red log SHA256 is
`117226aa855506b97b4870c6f989fe35c88b1f4333f2d83cbe73391574ec32b1`;
focused green SHA256 is
`98c0a39709e4b38f8123f83b5c05a726dac4052cf2e9f8c3577b5252a69e98cc`.
The canonical eight-worker coverage run passed all 3,185 tests in 24.23 seconds,
measured the same 21 product and 17 quality files with zero test files, and retained
94.837534% aggregate line coverage. Its log SHA256 is
`f7ae2c7048b894d4383891584df45efbcf046c8267108db008df3a5cda11e7c9`;
coverage JSON SHA256 is
`9be8ca68916cf8c201ee285dcc399c9b874878e37e45d8f746e28e2badcae15f`.
The aggregate local gate passed lock, hygiene, lint, typing, documentation, index,
metadata, workflow, all 3,185 tests in 19.59 seconds, build, dependency audit and
15 strict OpenSpec items. Native review remained incomplete because the signed
codebase module is unavailable on macOS. Log SHA256 is
`ba359f45aafd80675af5dfdd43bd0ca5d4939398a603772458a05a0ce458a2d1`.

Eight workers with the existing load scheduler are an unaccepted Linux candidate,
not a demonstrated root cause. Test selection, isolated fixtures, coverage sources
and thresholds, analyzers, signatures, execution identity and 30/300-second limits
remain unchanged. Both exact-head signed Linux legs must complete before acceptance.
Rollback restores four workers and matching contract/docs; every failed and passing
report remains retained.

## PR #43 bounded CLI-tail scheduling correction, 2026-10-15 Europe/Berlin

Exact-head run 38788058844 disproved the eight-worker candidate. Python 3.11 passed
all ten signed analyzers, collected all 3,185 tests and measured the expected 38
runtime files at 94.837534% coverage. Python 3.13 passed the other nine analyzers but
its complete coverage member reached the unchanged 300-second limit. Its ordinary
suite passed all 3,185 tests in 137.86 seconds, while the single installed CLI proof
consumed 78.62 seconds. The same proof had consumed 14.34 to 30.63 seconds in the prior
four-worker matrix and 17.85 to 18.73 seconds with two workers. This establishes an
eight-worker regression for the serial subprocess proof; it does not attribute all
native coverage time to that case.

An independent plan review rejected a split-only correction. With 3,185 collected
tests, xdist 3.8.0 load scheduling initially assigns 199 consecutive cases to each of
four workers; the installed CLI case at collection index 684 and adjacent split
cases would remain on one worker. The bounded correction therefore restores four
workers, retains `load`, and adds `--maxschedchunk=1` so slow split cases are
dispatched independently in the observed collection. Xdist still sends two tests
per worker at startup and may send two to an empty worker; it replenishes a worker
that retains pending work one test at a time. One installed proof became four cases with fresh
temporary HOME/work/database state: read-only invocation, portable lifecycle,
economic settlement/replay and Quote/budget presentation. The shared economic seed
recreates the original Change, Run and failed outcome. All original console-script,
network guard, duplicate-import, retry/correction, replay, human-output and
idempotency assertions remain.

A complete verbose local run placed the four cases on `gw3`, `gw2`, `gw1` and
`gw0`, respectively, and passed 3,188 tests plus four subtests in 27.08 seconds. Its
log SHA256 is
`e6f7b8c37cbff2793b12208f096f8305bc4a2d42316ff16d205046b54bfd5bc1`.
The exact combined coverage run passed 3,188 tests with 93 warnings in 32.34 seconds,
retaining 6,246 of 6,586 statements (94.837534%). Its log SHA256 is
`aa4058efaa1fb6638ec4e4497dd8be189dcb6a48a1caec292685a3b9b768f676`;
coverage JSON SHA256 is
`6e777f1615784efc347e6dd2ebfc9b6100f858ff1b5e39d595ec9ca80b84cbd4`.
The isolated wheel proof also passed all five unittest methods against the built
distribution. These local results establish collection, dispatch and preserved
behavior only. Both exact-head signed Linux reports, all analyzers and current-head
provider reviews remain blocking. Rollback restores the preceding worker/scheduler
configuration and monolithic test while retaining every historical report.

## PR #43 estimated-price provenance correction, 2026-10-15 Europe/Berlin

The exact-head Codex review identified that portable `DemandForecast` graph
validation checked only `price_request`. An imported estimated price could therefore
name another price scenario, or retain a price with no declared request, without
that claimed source becoming a validated graph dependency.

The specification and two adversarial import cases were added before the graph
correction. With the guard removed, both cases failed for the expected reason:
`ContractError` was not raised for the missing and mismatched request variants.
The red log SHA256 is
`ddecd616af361ee146251865dd3bbfe27d9edff25913eaa505209fbbbb6674e0`.
Command: `pytest -q tests/test_demand_controls.py::test_imported_forecast_binds_estimated_price_to_declared_request`.

The correction requires price and request presence to agree, requires the price
source to equal the declared request, resolves that exact source as a `demand_price`
record and adds it to the dependency graph. The focused demand, CLI and compatibility
run passed 65 tests. The two corrected import cases passed with log SHA256
`b55e4ead9357609b648f5af68386cc08ab2254c4bb4db78e61a6d89e782cffcf`.
The complete local suite, with the installed console script on `PATH`, passed 3,190
tests and four subtests in 30.56 seconds; its log SHA256 is
`e1d5c868283310d2ae9ac0a2b524a6d9c502d5f53b7addd5593d7c251a0451a9`.
Ruff, formatting,
BasedPyright and strict OpenSpec validation also passed. Fresh exact-head Linux
assurance and provider review remain required after publication. Rollback reverts
this graph guard, its two controls, and the additive specification scenario; all
portable records remain unchanged.


## Issue 44 intrinsic rubric preregistration correction (2026-10-15, Europe/Berlin)

The active specification, design and section 5 tasks were revised before regression
tests and runtime changes on branch `codex/fix-demand-policy-preregistration-44`,
based on main `ac2e8519`. Issue #44 demonstrated an imported future-declared rubric
arriving before evaluation and becoming authoritative when the clock caught up.

Red command: `.venv/bin/python -m pytest tests/test_demand_revision.py -k
'intrinsic_rubric' -n 0`. Four separate future/equality recorded_at/effective_at
cases failed with `Failed: DID NOT RAISE <class 'changecost.serialization.ContractError'>`;
two strictly earlier controls passed. An initial test fixture imported seed history
after its work and failed for unrelated forecast incompatibility; it was corrected
to create local seed history before capturing this red evidence. No runtime edits
preceded the corrected red execution.

A shared predicate requires local rubric availability to precede assessment
availability and both rubric timestamps to precede all intrinsic/local assessment
times. New receipt request v3 enables strict registration separately from v3
measurement semantics; forecast v4 inherits v3 temporal/support behavior and checks
all selected receipt cases. An iterative traversal with payload/visible-snapshot
visited identities checks nested candidate/baseline authority without recursively
revisiting shared branches. Exact v1/v2 receipt requests and v1/v2/v3 forecast replay
retain their original semantics. Valid legacy receipts remain eligible for v4.

Green command: `.venv/bin/python -m pytest tests/test_demand_revision.py
tests/test_demand.py tests/test_demand_controls.py tests/test_demand_cli.py -n 0`.
All 145 tests passed. Added controls include both intrinsic assessment timestamps,
valid earlier policy timestamps, same local capture time with earlier sequence,
atomic records/computation preservation, both legacy receipt generations, historical
forecast retries/replay, and nested invalid legacy authority rejection. Existing
late-local-rubric and operation-conflict controls remain enabled. Legacy-generation
test construction explicitly selects historical request, measurement and forecast
applicability behavior; it does not claim to replace archived baseline databases.

Ruff check, Ruff format check and BasedPyright passed for demand.py, demand_history.py,
models.py, test_demand.py and test_demand_revision.py. Strict OpenSpec validation
passed for this active change. Full repository gates, supported-Linux assurance and
independent/provider review remain parent-owned pending obligations. This is offline
synthetic evidence; native calibration, release and archival acceptance are unclaimed.
No package version, database schema or portable receipt field changed. Rollback must
retain v4 and receipt-v3 replay or use a compatible pre-change backup; do not rewrite
saved records or delete historical computation markers.

Actual ignored log timestamps (UTC) and SHA256 digests follow. Timestamps are file
completion times, retained as chronological execution evidence.

- `red.log` completed 2026-10-15T21:07:22.132275+00:00; SHA256 `5e3648e526265fab6567a87f3e564a9b6df8ece131fa123da59bdb48172c5074`.
- `green.log` completed 2026-10-15T21:13:15.096858+00:00; SHA256 `37ba983745ebc29226e58c90c14c9d2c8fd9450c754fa17f3ecc87b16eca23ea`.
- `lint.log` completed 2026-10-15T21:12:20.893130+00:00; SHA256 `82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18`.
- `format.log` completed 2026-10-15T21:13:15.128919+00:00; SHA256 `f114d83b30c5c657ee43a847a45bafccaea255d82673feb87c26d252c61e29c1`.
- `types.log` completed 2026-10-15T21:12:21.791933+00:00; SHA256 `56882e01cb80173ef053c4096e4ee43e3123a15f5c0a06715f96988d48fbd91c`.
- `openspec.log` completed 2026-10-15T21:12:22.006166+00:00; SHA256 `bed60daa235141d2ac2839556d4e1dc045bcb94c4f6302c0d61a8c613498f483`.

The coordinator also replayed an actual pre-edit database captured from merged main.
Its saved receipt-v2 and forecast-v3 payloads reproduce and retry exactly after the
correction. A new receipt rejects the invalid policy atomically, and a new v4
forecast remains learning. The original synthetic database remains unchanged at
SHA256 `70b3a5d58a953c634f6b01111097dd48e6fa92832d9697c927ea5e67b56c3a74`.
Eight retained documentation-source rationales were refreshed after the docs gate
identified their stale source digests; retained document bytes and gates are unchanged.
