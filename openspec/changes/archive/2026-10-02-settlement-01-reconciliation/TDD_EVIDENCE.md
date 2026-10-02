# Settlement implementation evidence

Status: implementation complete locally / verification To-Validate. Unreleased `0.1.0.dev0`.
Authorized by the maintainer on 2026-09-29 (Europe/Berlin).

## Inputs and recovery

Fresh fetched main and HEAD: `999cb8f960785fe4ac0434d41a0892beca933191`, checked
2026-09-29 at 22:01 +02:00. PR #25 is merged; #11's open administrative state
remains a tracking discrepancy. Prepared artifacts were carried directly into the
implementation, without a stash or planning PR. Archive-skill correction and the
full-CLI Core-02 archive remain included. No main spec was manually synchronized.

Active checkout: `/Users/dom/.codex/worktrees/settlement-implementation/changecost`,
branch `codex/settlement-reconciliation`. Work moved here after unrelated retrospective
files appeared in the primary checkout. Only the owned reviewed scope was copied;
unrelated work is untouched. The original dirty implementation is a stale recovery
copy and must not be mistaken for the active tree. The bounded review receipt was
copied intact, retaining preparation time and both correction batches, not reset.

## Actual failing and passing evidence

Logs remain ignored under `.changecost/workflow/settlement-01-reconciliation/`.
Times below are recorded log completion times in Europe/Berlin.

| Timestamp | Log | Outcome |
| --- | --- | --- |
| 2026-09-29T22:03:25+02:00 | `red-contracts.log` | 2 failed in 0.05s |
| 2026-09-29T22:05:39+02:00 | `green-contracts.log` | 94 passed in 0.24s |
| 2026-09-29T22:06:44+02:00 | `red-computation.log` | 4 failed, 4 passed in 1.39s |
| 2026-09-29T22:09:25+02:00 | `red-coverage.log` | 14 failed, 6 passed in 0.28s |
| 2026-09-29T22:11:13+02:00 | `red-cli.log` | 1 failed, 1 passed in 0.11s |
| 2026-09-29T22:12:12+02:00 | `green-cli.log` | 133 passed in 0.49s |
| 2026-09-29T22:16:30+02:00 | `red-review1.log` | 6 failed, 28 passed in 0.31s |
| 2026-09-29T22:17:23+02:00 | `green-review1.log` | 147 passed in 0.52s |
| 2026-09-29T22:23:10+02:00 | `red-review2.log` | 4 failed, 40 passed in 0.35s |
| 2026-09-29T22:24:33+02:00 | `green-review2.log` | 159 passed, 4 subtests passed in 2.31s |

Initial contract tests reached the existing adapter and rejected the newly specified
record kind. The normalized/computation API tests initially failed at their absent
entrypoints; those establish missing capability, not algorithm correctness. The CLI
red proof reached Typer and rejected `--import-evidence`. Subsequent regression reds
exercise implemented behavior and establish the concrete defects described below.
Tests were written before their corresponding implementation/fix. Tooling/typing
failures are not represented as behavioral red evidence.

Commands: `.venv/bin/python -m pytest tests/test_reconciliation.py -q` for scenario
slices; add `tests/test_settlement_cli.py tests/test_store.py tests/test_contracts.py
 tests/test_contract_cli.py tests/test_cli.py` for the combined regression run.
The CLI installation checks require `.venv/bin` on PATH. One direct run without it
failed the installed-script precondition; correcting PATH passed, and this is not
product TDD. Ruff and BasedPyright passed on the scoped runtime/tests after batch2.

## Independent review and correction history

Two read-only agents reviewed the runtime against the selected specifications.
Batch1 fixed scope/lane exclusions hiding contradictory work bounds, portable
successors blocking locally receipted ledgers, transitive correction binding conflicts,
resolved currency leaking into other scopes and report/computation cutoff mismatch.
Six failing regressions became passing; 147 scoped tests passed at that checkpoint.

Batch2 fixed missing portable dependency-role validation, supplied model IDs receiving
inspection authority without matching immutable payloads, profile-only snapshot
precedence and normalization of new components after portable core-ID preservation.
Source-coverage evidence is also checked against the declared Run. Four failing test
functions became passing; 159 scoped tests and 4 installed-CLI subtests passed.
These are distinct invariants, not resets of the prior finding history. Final independent
fix verification is recorded below when complete.

## Implemented boundary

Strict internal economic/coverage/computed records, atomic normalized import,
stable source/component identities, typed pending replacement locators, nonbranching
correction history, bounded exact arithmetic, explicit supported temporal lanes,
local snapshot/operation receipts, policy-bound synthetic coverage and read-only
repository remainder are implemented. Source/record history, failed/cancelled retries
and abandoned Change expenditure are retained. Product version remains unchanged;
provider adapters, quote/check algorithms and live collection remain outside scope.

Local SQLite layout 2 rejects incompatible layouts unchanged; no automatic migration
or public v2 was added. A consistent backup preserves receipts and original local
history. Portable reimport creates destination availability and imported claims,
not local computation authority. Roll back using the compatible checkout and a
consistent backup into a distinct path; never erase a runtime store to downgrade.

## Limits and remaining verification

No provider profile is certified. Only the closed synthetic policy can produce
synthetic full-change coverage. Exact computations enforce 100000 repository
records and 4096 aligned digits; normalized CLI input is limited to 32 MiB.
Native SpecFact analyzer assurance cannot run on this macOS controller and requires
supported Linux. No native pass, commit, push, PR, release, deployment or completed
verification stage is claimed. Full matrix/build/docs gate outcomes follow when run.


## Final implementation handoff — 2026-09-29

- Aggregate command: `BASE_REF=999cb8f960785fe4ac0434d41a0892beca933191 MANIFEST=.changecost/workflow/settlement-01-reconciliation/intended-files.txt make check`.
  Python 3.13.14 suite: **852 passed in 71.27 seconds**. Lock and host guard probes,
  hygiene, Ruff/format, BasedPyright, docs, generated references, metadata, workflow
  and distribution build passed. Dependency audit was not applicable because locked
  dependency/audit inputs did not change. Log: `implementation-make-check.log`.
- Python 3.11.15 used a separate locked environment via
  `UV_PROJECT_ENVIRONMENT=/tmp/changecost-settlement-python311 uv sync --locked --group build --python 3.11.15`,
  then `PATH=/tmp/changecost-settlement-python311/bin:$PATH /tmp/changecost-settlement-python311/bin/python -m pytest -q`:
  **852 passed, 4 subtests passed in 72.43 seconds** (`python311-tests.log`).
- Distribution build rebuilt the wheel from the sdist, installed only locked runtime
  dependencies into a clean environment outside the checkout, checked archive privacy
  and absence of SpecFact, and ran `tests/test_cli.py`. Its subprocess socket guard
  blocked network while exercising duplicate/retry/replacement import, explicit bind,
  exact `0.45` computation, operation retry, explain and twice-imported portable output.
  All passed. The documented nine-command example also passed independent execution,
  producing `0.25` with correctly provisional coverage.
- Full aggregate exit was **1**, not a pass. Its native-review leaf reported all ten
  analyzers `unsupported_controller_platform` on macOS. The initial spec leaf also
  detected an empty Core-02 active directory left by transferring deleted files into
  the worktree. Verified it contained no files, removed only empty directories, then
  reran all strict specs: **10 passed, 0 failed**. This was transfer cleanup, not an
  archive substitute; the archive itself had already been executed by the full CLI.
- Two independent runtime lanes verified final fixes, with **46 settlement tests**
  passing in their read-only review runs and no remaining concrete findings. An
  additional three-Run nonzero probe preserved `0.60` through accepted/abandoned
  outcomes and reporting. The documentation lane verified its corrected generator
  and `economic_kind`/legacy coverage wording, with no remaining scoped findings.
- The final reference-description edits alter documentation strings only. Fresh
  docs/index, Ruff, whole-repository BasedPyright, metadata, strict specs and whitespace
  checks cover those refinements; no extra runtime suite is claimed for them.
- Issue #12 body was reconciled and moved to In Progress, remaining OPEN. Native
  User Story, parent #7, prerequisite #11, labels and unassigned state are retained.
  Prepared work is local/unpublished. Original preparation checkpoints in the issue
  are historical; no remote implementation link is invented.

Confidence: high in the observed offline behavior and scoped fixes; native analyzer
assurance remains unknown until supported-Linux verification. No provider economic
completeness or historical destination replay is inferred from portable claims.
False finality, double-counting and history loss are guarded by explicit coverage,
validated replacement chains and immutable transactional receipts plus backup tests.
No paid infrastructure is needed; no implementation-time estimate is asserted.

Tasks 1.1–6.2 are complete (17 tasks); 6.3–6.4 remain pending for full assurance,
staged checks, acceptance and any later authorized publication. Next invocation:
`$changecost-verify settlement-01-reconciliation`. No commit/push, PR, settlement
archive, release or deployment was performed. Preserve the active managed worktree
and its ignored review history; the original checkout is only a stale recovery copy.


## Local verification milestone — 2026-09-30

The maintainer authorized verification, scoped CodeRabbit review and later promotion.
The implementation was refreshed onto PR #27 at main/HEAD
`131799f640caac6c2ee68dc6904d331a4203f825`; the ten owned runtime/test files
remained byte-identical. The strengthened review process is now applicable.

Frozen generation 7 (`e16b726c0265ee25a5394794c18abba0917941481c0ad957a0f6c663bc7c1e6b`)
received independent quality, security/defect and documentation review. The current
Python 3.13.14 suite passed 1,020 tests in 93.12 seconds; fresh Python 3.11.15
passed 1,020 tests in 95.46 seconds. The distribution build and installed offline
CLI proof passed. Lint/format, typing, docs/index, metadata, workflow, lock and
hygiene passed; hygiene included all intended new files. Dependency audit was
not applicable because its locked inputs were unchanged. Strict OpenSpec passed
all 11 items. Full commands and native logs are retained in the ignored workflow
receipts; initial PATH-related test/lint/type failures and corrected reruns remain
visible in the refresh history.

CodeRabbit CLI 0.8.2 completed one authenticated full-diff review including all
54 changed paths and untracked additions, with zero findings. The independent
review-agent security/defect inspection also found no actionable defect and ran
46 reconciliation/CLI regressions successfully. This does not certify a later PR
head or replace hosted provider reviews. Documentation review identified one mode
wording ambiguity: selector exclusion applies to portable import/export, while
normalized import requires a repository selector. That wording is corrected.

This is a local verification milestone, not final acceptance. The macOS native
report is historical UNKNOWN, all ten analyzers unsupported with a stale binding;
no full aggregate or native pass is claimed. Final staged checks, supported-Linux
matrix/analyzer assurance and hosted exact-head reviews remain pending. Their
live evidence belongs in the PR body and existing review ledger, without a
receipt-only source commit. Tasks 6.3 and 6.4 remain unchecked until their full
acceptance obligations are established. Version remains unpublished 0.1.0.dev0.

## Hosted static-quality correction — 2026-10-01

The first supported-Linux matrix at commit `822243c133ecaa2c0b4c78f033ed7edeb788d6a3`
([run 36783132528](https://github.com/nold-ai/changecost/actions/runs/36783132528))
ran all ten required analyzers on both Python versions. Eight passed; Radon and
Pylint failed with the same nine blocking findings. This is actual failing static
analysis evidence, not a behavioral TDD failure or accepted native pass.

Correction batch 4 separates source-chain selection, file overlap, snapshot/window
validation, coverage membership, portable-ledger ownership and immutable result
construction into focused functions. The source input comparison iterates the
already-validated input object's fields rather than Pydantic class metadata. The
coverage test cases retain their scenarios with fixture construction separated.
The internal schemas, transaction boundaries, CLI, exact amounts and thresholds
are unchanged. No analyzer suppressions or gate-policy changes were added.

Pinned local Radon 6.0.1 reports no complexity above the configured blocking
threshold of 15, and the affected functions have no more than seven parameters;
immutable-result construction now uses five. Pylint 4.0.7 with strict None/opaque
inference and pinned runtime imports reports no E/F findings in the six changed
files. This local diagnostic run is not sealed-capsule assurance: translating the
native blank decorator settings literally produced baseline-only context-manager
errors absent from the hosted report, so the local run retains Pylint's standard
context-manager recognition. Fresh hosted native results remain mandatory.

After the final refactor, 159 relevant tests and four installed-CLI subtests passed
in 4.06 seconds; Ruff/format and BasedPyright passed. Local diagnostic syntax and
intermediate type/inference failures were corrected and are not product TDD proof.
Full post-refactor matrix, independent affected-scope closure and exact-head hosted
analysis are recorded in the live PR/ledger once observed. Original failed native
reports remain in the run artifacts and ignored workflow receipts.


## Hosted Codex correction — 2026-10-01

Codex review 5372816184 of PR #28 at a7dae694 reported target-Change selection
contamination and repeated full-record scans in economic binding validation and
normalized Evidence matching. Independent reproduction confirmed all three.
The prior exact-head Linux runs passed mechanically; this did not establish
absence of the subsequently reported semantic and bounded-work defects.

Before implementation, `pytest -q tests/test_reconciliation.py -k
'foreign_change_does_not or lookup_does_not'` failed all seven selected cases
(0.17 seconds): unrelated snapshot/pending/inherited chains changed the target
result, and counting dictionaries exceeded linear visit bounds at 20 and 40
records. The final type-correct counting fixture bounds entries exposed by mapping values
views. All eight final regressions were additionally run against an isolated exact
a7dae694 source snapshot and failed (0.17 seconds), then passed against the correction.
These deterministic checks measure the two lookup steps, not whole-pipeline
complexity or timing. The ignored batch5-red.log preserves the actual failures.

Selection now resolves inherited chain attribution before lane/correction policy
and excludes explicit non-member chains. All target Runs and genuinely unbound
chains remain eligible for conservative policy. Graph binding and normalized
Evidence identity indexes are rebuilt per operation; matching preserves the first
existing core record and extends the index within a batch. No schema, CLI, runtime
dependency, gate threshold or release version changes are made.

After correction, 146 reconciliation, settlement CLI, store and contract tests
passed in 0.56 seconds, including an additional different-namespace pending-chain
case, existing mixed-attribution, unbound, arbitrary core-ID and multi-component
controls. An intermediate dependency-forwarding typo was corrected; its failing
run remains recorded and is not cited as baseline TDD proof. Final full matrix,
independent closure and current-head hosted review belong in the live PR receipt.


## Family investigation and provenance/index correction — 2026-10-01

Codex review 5372995808 of published 98d6e273 found three remaining defects:
foreign chain inputs survived an early return, explicit EvidenceBinding inputs
were only repository-checked, and SourceCoverage validation rebuilt bindings for
every assertion. Independent family-wide investigation confirmed these and found
two related paths: retained pending corrections omitted consulted mapping inputs,
and computed membership rescanned Run bindings. It also covered repeated declared
Run membership checks, all computed input roles, selection, normalized import and
portable history. Earlier subtotal/exclusion-only regressions missed immutable
provenance; this was reevaluated rather than dismissed as redundant code.

Before runtime edits, the selected new/strengthened tests in
`tests/test_reconciliation.py` produced 10 failures and four passing controls
(0.51 seconds), recorded in batch6-red.log. They assert foreign input isolation,
pending binding provenance, atomic explicit foreign-mapping rejection and bounded
record-map exposure across coverage/computed membership at 10 and 20 Runs. The
controls preserve accepted member mappings, both conflicting-binding input orders,
and historical unbound plain/economic evidence after later foreign binding.

The correction records retained event and mapping references after membership
selection and before pending-chain return. It shares full-reference Evidence/Run
binding indexes once per validation and a declared-Run set once per computed
result. It checks explicit mapping membership without retroactively inferring
historical economic attribution from newer bindings. This is a bound on these
lookup steps, not an assertion of whole-pipeline linear complexity.

After correction, 156 focused reconciliation, CLI, store and contract tests passed
in 0.85 seconds. An intermediate signature-propagation error and local CC16
diagnostic were fixed inside this batch; they are retained as implementation
diagnostics, not baseline behavioral red evidence. No analyzer threshold, schema,
CLI, dependency or unpublished 0.1.0.dev0 version changed. Fresh full matrix,
independent family closure, supported-Linux native assurance and hosted provider
results remain separate live PR/ledger acceptance obligations.


## Outcome lookup replan and correction — 2026-10-01

Independent review of the preceding family correction found a remaining
`members | {change}` copy for every Outcome input: 10 and 20 Run Outcomes copied
100 and 400 member entries. This was retained as a post-investigation escape in
the same bounded-lookup family. The maintainer explicitly approved the concrete
replan and continued verification; budget/history were preserved, not reset.

Before this fix, `pytest -q tests/test_reconciliation.py -k
'outcome_subject_lookup or computed_outcome_subject_membership'` produced two
counted-work failures and three passing subject controls in 0.17 seconds. The
minimal correction checks membership in the existing set or equality with the
Change reference separately. The same Change/Run Outcomes remain accepted and a
foreign Outcome remains rejected. No per-Outcome membership set is allocated.

After the fix, 161 focused reconciliation, CLI, store and contract tests passed
in 2.58 seconds; typing passed with zero errors or warnings. The preceding
mechanical-only matrix (1,038 tests per Python version) did not certify absence
of this defect. Fresh independent closure covering the exact named escape and
all prior related fixes, full quality verification and new-head hosted assurance
remain required before live acceptance. Version stays unpublished 0.1.0.dev0.

## Consolidated seven-path repair — 2026-10-02 (Europe/Berlin)

The maintainer approved correction of findings 11–13 and related findings 14–17
as batch 8. The existing schema-8 session, investigations, active-time history and
extension to 11 batches / 300 active minutes were retained. Replan remains pending
current-binding independent closure and a verified named family resolution.

The four new specification scenarios preceded test and implementation edits.
Before implementation, `.venv/bin/python -m pytest tests/test_reconciliation.py -k
'subject_work_is_linear or disjoint_file_overlap_work or repository_unknown_amount_reason
or repository_plain_evidence_uncertainty or computation_coverage_record_work
or cutoff_pruning_dependency_work or inspection_uses_one' -q` produced **15 failures,
1 passing foreign-repository control and 67 deselections in 2.33 seconds**. The
ignored `batch8-red.log` contains the actual failures: repeated chain binding visits,
ordered overlap comparisons, empty unknown reasons, omitted plain Evidence,
repeated complete-record coverage scans, repeated dependency pruning and multiple
inspection read transactions. These are causal baseline failures, not tool failures.

The correction walks chain leaves once with shared visited state; sorts overlap
windows and retains the furthest endpoints for two distinct digests; indexes
full-reference lifecycle leaves, coverage, bindings and per-Run event groups;
propagates unavailable references through reverse dependencies once per edge; and
checks inspection payload, local receipt authority, cutoff bounds and all inputs
in one transaction with one graph validation. Repository bucket subtotals are
computed once, unknown amounts name unknown_amount, and identity-only Evidence
is explicitly unresolved and scoped by any explicit Run repository binding.
These are bounds for these steps, not a whole-pipeline linear-complexity claim.

After implementation, the original complete settlement file passed **83 tests in
0.98 seconds**. Additional controls cover per-Run global event scan counts,
predecessor-defined leaves in both insertion orders, complete RunRefs with matching
run IDs across repositories, and all four availability inequalities. An initial
new control attempted a future declared work bound and correctly failed contract
validation; it was repaired to a past bound. A CLI test initially lacked the
installed entrypoint in PATH; using the existing `.venv/bin` resolved that test
environment issue. Neither is counted as baseline red evidence.

The final affected command, `PATH="$PWD/.venv/bin:$PATH" .venv/bin/python -m pytest
tests/test_reconciliation.py tests/test_settlement_cli.py tests/test_store.py
tests/test_contracts.py tests/test_cli.py -q`, passed **187 tests and 4 subtests in
3.41 seconds**. Focused Ruff and BasedPyright passed with zero errors/warnings;
`openspec validate settlement-01-reconciliation --strict --no-interactive` passed.
Independent closure, full current-input quality/matrix, staged checks and new-head
Linux native/provider review remain required. Prior native passes do not certify
this new result. No schema, package version, analyzer threshold or source policy
changed; package remains unpublished `0.1.0.dev0`, with offline synthetic scope.

Rollback is a follow-up revert of the scoped repair commit after publication;
no stored payload format or database migration is introduced. Preserve the prior
checkout and database backup for preview rollback and original cutoff inspection.

## Coverage assertion closure and full-test typing — 2026-10-02 (Europe/Berlin)

Generation-21 independent review confirmed the seven direct corrections, including
2,100 overlap sets, eight correction controls, 720 cutoff DAGs, 50 coverage parity
cases and single-transaction inspection controls. Complete family closure failed:
each coverage assertion still rescanned all selected point endpoints and economic
components. Valid graph probes measured 200/800 point-start reads for 10/20 events
and assertions, and 100/400 evidence reads when components shared Evidence. This
is finding `codex-pr28-related-18` in the existing bounded-lookup family, retained
as a post-investigation escape. Both full 3.11.15/3.13.14 suites passed 1,067 tests,
but the full types leaf failed three errors at the new subtotal assertion. The
prior focused runtime typing pass did not cover that test and was not full quality
acceptance. No previous incomplete result is relabeled passed.

Persistent explicit maintainer instructions to continue until the PR is green and
to repair/continue authorize this in-scope follow-up. Batch 9 collects the residual
and full-test type blocker; counters, budget and replan history are preserved.
A new specification scenario preceded regression and implementation edits.
`pytest tests/test_reconciliation.py -k coverage_assertion_work_tracks_declared_inputs
-q` failed **six causal work-count cases with 91 deselections in 0.31 seconds**:
10/20-event endpoint cases and shared-Evidence endpoint/membership cases. Each
fixture passed graph validation and retained expected uncertainty/provenance.

Coverage now summarizes distinct complete Evidence keys, point minimum/maximum
and presence of events once per selected Run group. Each assertion keeps its own
policy, finality, economic identity, full interval and evidence-set requirements.
Cardinality rejection and subset checking use distinct keys; no assertion union
manufactures completeness. Point starts stay inclusive and ends exclusive; no
point events skips only the point predicate. All consulted assertions remain
provenance even when rejected. The unmodified independent probes now measure
10/20 point-start reads and 10/20 shared-Evidence reads for 10/20 events; their
missing-supported/unsupported-source reasons remain unchanged.

The subtotal test uses list/Subtotal runtime guards to narrow actual values. A
new assertion-separation fixture briefly triggered a possibly-unbound local
variable diagnostic; explicit initialization/guard repaired the test, without an
ignore or gate relaxation. The final focused command from batch 8 passed **195
tests and four subtests in 3.38 seconds**; full `make types` against comparison
`131799f640caac6c2ee68dc6904d331a4203f825` passed with zero errors/warnings.
Ruff passed. New independent full-family closure, fresh current-input full quality,
staged checks and native/provider/live acceptance remain required. All earlier
repair controls and offline unpublished `0.1.0.dev0` scope are preserved.

## Native structural correction — 2026-10-02 (Europe/Berlin)

The automatic current-head Linux run
[37058926420](https://github.com/nold-ai/changecost/actions/runs/37058926420)
failed both matrix jobs at `fe18874140c91414841b379181b2ef6c99ef1dce`.
All ten required analyzers actually ran; nine passed and Radon failed with one
blocking finding: `CoverageIndex.add_record` at coverage.py:98 had seven nesting
levels (`radon-kiss` / `kiss.nesting.error`). Neither report had UNKNOWN required
evidence. Both exact report digests and published-scope/blob proofs are retained
in ignored `ci-37058926420/summary.json`. The earlier CC-only local diagnostics
did not cover this separate native nesting rule and did not certify native PASS.

The installed pinned `specfact-code-review` 0.50.1 `radon_runner.py` defines
`_nesting_depth` using control-flow AST children, so the elif chain contributes
nested If nodes. Its warning threshold is 3 and error threshold is 5; the native
message recommends keeping nesting under 3. Executing those exact installed
AST definitions reproduced depth 7 before editing. The detector file SHA256 is
`4a15673a9ff26c34a4a9becad794ce450dbf6e2b6e2549bf230946c4d4ac7101`.
This actual structural gate failure is the RED evidence; no behavior change or
fabricated failing product test is claimed. The native-static-quality finding,
exact-rule investigation and batch 10 preserve the existing history and allowance.

The minimal change replaces mutually exclusive elif dispatch with separate
if guards and early returns. Each selected record role still populates the same
index exactly once; full references, predecessor-defined lifecycle leaves and
bounded scans are preserved. The same pinned detector now measures depth 2 for
add_record and no blocking nesting in coverage.py. No gate threshold, analyzer,
suppression, source policy, version or schema is changed, and no unsupported macOS
capsule or manual CI retry is used.

The existing focused suite passed **195 tests and four subtests in 4.85 seconds**;
full typing passed with zero errors/warnings and Ruff passed. Independent coverage
parity/index closure, fresh frozen local quality, staged verification, new-head
Linux native assurance and provider completion remain required before acceptance.
The CodeRabbit initial full request is held while the known native blocker is
being repaired. Earlier exact-head Codex completion cannot certify the new head.


## Implementation acceptance and archive closeout — 2026-10-02 (Europe/Berlin)

The maintainer accepted settlement closeout after merge and requested the normal
OpenSpec CLI archive with strict validation and main-spec synchronization. Closeout
uses fresh main `175fd4bb3a545d6720cfdcd8e056b01b8a419b3b` in a registered isolated
worktree; the original dirty development checkout is preserved.

[Merged PR #28](https://github.com/nold-ai/changecost/pull/28) is the final
implementation verification index for head
`beedfd16f3af233e2f7ceb8dbcecf5baa2bd7bf1`, merged at
`1f55b767066d9834765f92a427b5eb9dc653a315`. Readback on 2026-10-02 confirms both
`quality (3.11.15)` and `quality (3.13.14)` SUCCESS and CodeRabbit SUCCESS. The PR
records 1,075 tests per Python version, installed-package proof, final staged checks
with both default HEAD and explicit main comparison, independent family closure,
and actual current-head Codex/CodeRabbit completions. These records close tasks
6.3/6.4; the earlier unchecked milestone and failed repair runs remain historical
evidence, not current acceptance failures.

[Linux run 37061421153](https://github.com/nold-ai/changecost/actions/runs/37061421153)
provides the final native assurance: all ten required analyzers ran/PASS,
UNKNOWN=false, zero blocking findings, exit zero and PASS_WITH_ADVISORY with PASS
assurance. The [exact advisory disposition](https://github.com/nold-ai/changecost/pull/28#issuecomment-5961284561)
retains all 1,378 nonblocking entries per report. Native `local_build` authority,
`protected_pr_eligible=false` and simplification-summary inconsistency remain
limitations. No analyzer threshold or trust boundary is changed by closeout.

Fresh [issue #12](https://github.com/nold-ai/changecost/issues/12) readback confirms
CLOSED/Done, User Story type, parent #7, native prerequisite #11 and retained labels.
The issue's older preparation prose and unchecked acceptance criteria need lifecycle
reconciliation; closing an issue alone did not establish implementation correctness.
The maintainer's present acceptance plus the merged verification index establish
that acceptance. Fresh readback on 2026-10-03 confirms Core-02 #11 CLOSED since
2026-10-02 at 23:53:45 Europe/Berlin; no prerequisite issue mutation is needed in
this settlement closeout. Provider profile approval and source-feasibility gaps
remain separate prerequisites.

Before archival, `openspec validate settlement-01-reconciliation --strict
--no-interactive` passed and `openspec validate --all --strict --no-interactive`
passed all 11 active-change/main-spec items. The read-only delta comparison found
three added change-run contract requirements and fourteen added reconciliation
requirements, with no conflicting names, modifications, removals or renames.
OpenSpec CLI 1.13.2 owns spec synchronization and archival; no manual spec merge,
folder move, skip-specs or validation bypass is used.

Closeout changes only lifecycle documentation, CLI-generated specification output
and reference ownership. The implementation verification above remains bound to
the published implementation head; it is not claimed as a fresh analyzer review
of the closeout diff. Runtime code, source policies, database layout and package
`0.1.0.dev0` remain unchanged. Rollback is a scoped closeout-commit revert if
committed, preserving evidence and store files; do not delete or downgrade local
history. No paid infrastructure or live collection is introduced.


### Archive readback and closeout checks — 2026-10-03 (Europe/Berlin)

The actual `openspec archive settlement-01-reconciliation --yes` command exited
zero and reported spec synchronization before archival to
`openspec/changes/archive/2026-10-02-settlement-01-reconciliation`. The CLI's date
prefix is retained; archival ran on 2026-10-02 before this verification crossed
midnight. Schema is `spec-driven`, CLI 1.13.2. The only archive warning was the
nonblocking recommendation to split changes with more than ten deltas.

Readback verified the complete text of all 17 added requirements and 55 scenarios,
all 18 previously accepted contract requirements, unchanged `.openspec.yaml`,
all archived artifacts and absence of the active change. CLI output collapses one
extra blank line; the comparison normalizes repeated blank lines only. No scenario,
requirement text or operation header is lost or retained incorrectly in main specs.
Post-archive strict validation passed all 11 active-change/main-spec items.
Moved relative links, ownership entries and generated llms references are repaired;
the unchanged generated command reference has a reviewed content-bound rationale.
Issue #12's acceptance criteria and stale unpublished implementation prose were
corrected with exact body readback; CLOSED/Done and native relationships are retained.

`make check BASE_REF=175fd4bb3a545d6720cfdcd8e056b01b8a419b3b
MANIFEST=.changecost/closeout/manifest.txt` did not pass as an aggregate. Its runtime
suite passed 1,075 tests on Python 3.13.14 in 102.37 seconds. Hygiene, Ruff
lint/format, BasedPyright (zero errors/warnings), docs, generated index, metadata,
workflow, package build plus two installed CLI tests, and strict OpenSpec passed.
Dependency audit was not applicable because locked dependency/audit inputs are
unchanged. No new Python 3.11 run is claimed for this documentation-only closeout;
the accepted implementation's two-version evidence remains in PR #28.

The lock/tool probe initially failed because outer command-line Make overrides
propagated the repository comparison SHA/manifest into its independent Git fixture.
`make lock MAKEOVERRIDES= BASE_REF=175fd4bb3a545d6720cfdcd8e056b01b8a419b3b
MANIFEST=.changecost/closeout/manifest.txt` passed the same lock and required-test
negative/repaired probes. No gate or probe implementation was changed. The original
aggregate failure remains in the ignored closeout log.

The native review leaf actually attempted SpecFact CLI 0.55.4, but all ten required
analyzers reported `unsupported_controller_platform` on macOS. Closeout metadata
and OpenSpec-context changes trigger this broad repository leaf. Its assurance is
incomplete/failed, never a pass. The previously accepted Linux implementation run
does not certify these later documentation inputs. Native capsule review of the closeout diff belongs exclusively to GitHub CI/CD.
Local Linux runner installation, execution or repair is outside this closeout.
The unsupported capsule attempt does not indicate a failure of the passing macOS
checks and is not a local closeout blocker. Its actual nonzero aggregate outcome
remains recorded. No CI workflow was dispatched against an unrelated main snapshot
and no skip/threshold bypass was introduced.

Actual local logs are retained in `.changecost/closeout/make-check.log`,
`.changecost/closeout/lock-recheck.log` and `.specfact/`; ignored logs are local
recovery evidence, not published artifacts. Archive/spec synchronization and strict
validation are complete; the closeout remains local on
`codex/archive-settlement-01` until publication is separately requested.


### macOS / GitHub CI boundary clarification — 2026-10-03 (Europe/Berlin)

The maintainer reaffirmed that Linux runner work is out of scope locally and may
run only through GitHub CI/CD. The current pinned SpecFact CLI/module composition
still rejects local capsule execution, while the macOS Ruff, BasedPyright,
1,075-test suite, installed-package proof, repaired tool probes and both complete
staged checks passed. The aggregate command's expected capsule rejection was
incorrectly framed in the handoff as a remaining local blocker. It does not undo
settlement acceptance or strict archive/spec verification, and no local Linux
setup, execution or runner repair is required. Preserve the actual failed attempt
above; do not relabel it as passing native evidence. Any future publication uses
the existing GitHub Ubuntu workflow for the CI-only capsule review.
