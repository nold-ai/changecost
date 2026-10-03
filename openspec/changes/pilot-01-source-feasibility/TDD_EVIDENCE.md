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
