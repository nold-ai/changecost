# Advisory #16 implementation evidence

Implementation authorized 2026-10-05 (Europe/Berlin), against freshly fetched
main/HEAD `340668e6b74bfb7ccab15efe13830555bc6dd7ef`. The owned combined branch
preserves the native Quote archive. Historical [preparation](PREPARATION_EVIDENCE.md)
is not current runtime certification. No provider collection, persisted budget,
schema migration, product version bump or paid infrastructure was introduced.

## Obligation review and bounded inputs

One read-only upfront reviewer inspected the planning artifacts, CLI/contracts,
Quote/reconciliation/store replay and behavioral guide. Obligations included one
local read snapshot, local typed authority, full material Settlement replay,
strict portable graph/observation checks, budget currency validation, parser errors,
zero/completeness and data-only summaries. That reviewer subsequently became the
sole implementation writer; oracle helper independence is not independent human
authorship. Independent closure and Codex/CodeRabbit reviews remain required.

The existing schema-8 session was recovered with 7.410640516666667 active minutes,
zero correction batches and the original 90-minute/three-batch allowance. Approved
scope manifests retain the combined archive/preparation inputs plus runtime,
absence-bound additions and specification/oracle/generator/configuration dependencies.
Counters were not reset. Bindings were captured before retained red/green runs;
actual JSON bindings and report bytes remain ignored under
`.changecost/workflow/workflow-01-advisory-ci/`. Publication and native acceptance
cannot be inferred from a packet or these implementation tests.

## Observed red/green slices

Environment: Python 3.13.14, locked editable package 0.1.0.dev0; pytest 9.1.1. Commands below use `.venv/bin/python -m pytest`.

| Slice | Command selection | Observed outcome |
| --- | --- | --- |
| Initial missing behavior | tests/test_presentation.py tests/test_advisory.py tests/test_summary.py -q | 22 failed, 7 passed; missing format/check/parser/error/summary behavior |
| First implementation | same selection | 29 passed |
| Missing scope/strict summary boundary | tests/test_advisory.py tests/test_summary.py -q | 5 failed, 50 passed; Quote scope absent and invalid metadata/numeric claims accepted |
| Repaired scope/summary plus controls | tests/test_advisory.py tests/test_advisory_controls.py tests/test_presentation.py tests/test_summary.py -q | 71 passed |

An initial test-author fixture-signature mistake was corrected before the retained
missing-behavior red run. Intermediate unsuccessful implementation runs are retained,
including Typer's vendored Click adaptation; those tooling/API errors are not counted
as product red evidence. An expanded runtime run initially had 108 passes and two
failures: the demo registered retrospective immutable work-start metadata, correctly
excluding its peers, and the console script was missing from the test process PATH.
The demo uses the existing interval declaration instead. Its first subsequent run
correctly exposed an unsupported synthetic namespace; it now uses the delivered
closed policy's opaque namespace rather than extending source support. Final checks
use the installed environment PATH. Those negative outcomes remain retained and
authorize no weaker policy.

## Independent oracle, controls and limits

`tests/advisory_oracle.py` imports only standard-library Decimal and derives its
truth table from the accepted scenarios. Numeric comparison requires local authority,
reproduction, completeness and exact economic compatibility; equality/zero are within.
The deterministic generator exercises 18 combinations: three literal values, two
completeness states and three budgets. Named real-store scenarios additionally cover
p50/p90, exact values beyond float precision, imported/legacy/unpriced claims,
unsupported/future/foreign cutoffs, missing receipts/inputs, material mismatch,
later history and retained narrowed-scope reasons. No-write checks compare durable
bytes/exports and identical computation retries. Artifact mode tests fail any database
connection and reject malformed schemas, graphs, conflicts and observation references.

Six seeded controls modify the exercised target while retaining the detector:
receipt authority, historical result mismatch, completeness, float conversion,
zero truthiness and current-history cutoff substitution. Each requires the faulty
target to fail and the repaired target to pass on the same fixture. Fault injection
alters existing valid records only to exercise corruption/replay boundaries; runnable
demos create no handwritten database rows. Arbitrary concurrent writers, provider
approval, prediction calibration and exhaustive graph/input domains remain outside
this bounded evidence.

Presentation tests exercise all five families, human/JSON parser diagnostics,
existing JSON payloads, offline help/version and terminal controls. Existing installed
wheel/fresh-store proofs are extended rather than duplicating registration/outcomes.
Summary tests cover malicious shell/HTML/Markdown/control labels, Unicode, valid
escape/UTF-8 truncation at 65,536 bytes including notice, strict version/semantics,
write failures and nonzero subprocess errors. The optional workflow uses pinned setup,
manual invocation and read-only permissions; seeded writable-token configuration is
rejected while valid advice still renders, then the repaired configuration passes.

## Verification and delivery boundary

Early Ruff checks pass and BasedPyright reports zero errors after focused repair.
Final selected/all strict OpenSpec, documentation/generated references, explicit-base
manifest aggregate, staged checks, clean wheel proofs and supported-Linux Python
matrix/native analyzer results will be recorded by verification. macOS native capsule
execution is unsupported; Linux evidence stays pending, never relabeled pass.
Current-head independent defect/security/documentation and required external reviews
remain pending. Issue #16 stays open until accepted; #16 is not archived here.

Rollback reverts this change's runtime/examples/docs while preserving the accepted
Quote archive, historical evidence and existing user stores/backups. The demo can be
removed by deleting only its synthetic directory and generated summary.

## Focused implementation closeout

The expanded targeted suite reports **116 passed, four subtests passed** with the
installed environment PATH. A final source-bound rerun below retains the same command
selection after documentation/task finalization. Ruff passes; BasedPyright reports
zero errors. Explicit-base documentation ownership/links and generated references
pass. Full aggregate, clean wheel rebuild and native hosted matrix remain subsequent
verification obligations, not implied by the focused run.

```sh
PATH="$PWD/.venv/bin:$PATH" .venv/bin/python -m pytest tests/test_advisory.py tests/test_advisory_controls.py tests/test_presentation.py tests/test_summary.py tests/test_quote_cli.py tests/test_settlement_cli.py tests/test_contract_cli.py tests/test_cli.py -q
.venv/bin/ruff check src/changecost tests/test_advisory.py tests/test_advisory_controls.py tests/test_presentation.py tests/test_summary.py tests/advisory_oracle.py tests/test_cli.py tests/test_contract_cli.py
.venv/bin/basedpyright
```

Bindings capture original head/base plus full working/index input digest; retained
red/green snapshots carry their original epoch rather than a later binding.

- `red.txt` SHA256 `516772c4f378357e6c340812e34dfc8785d152ea879b33b25bc04f93076d5330`.

- `first-green-v3.txt` SHA256 `b7c9ab21c03d028b9db789c489cb31ef8520f5a0505b5b81d01d6f94d93dd7a4`.

- `edge-red.txt` SHA256 `062995aecf7002e855909cbc7e32c8f8dad1f9e8448c022c06206830eeca8bda`.

- `edge-green.txt` SHA256 `4b172023c8fcfe0e2094292649665bff30ee9b06e0565f472c9897f3a9bd459e`.

- `final-runtime.txt` SHA256 `56917a5184df57ce782edebc13d255e416bca67bdc449e32dc23b8b255f02dda`.

Selected strict OpenSpec and all 11 strict items pass. Intended-file hygiene passed
all eight hooks with permissions that allow the EOF checker to open unchanged
repository skill files. The sandbox-only EOF permission failure is retained separately.
Full-source/quality/tests Ruff and formatting checks pass; BasedPyright reports zero
errors. Current documentation rationale digests preserve the unchanged contributor,
gate-policy and historical Settlement evidence rather than rewriting their histories.

## Independent correction batch 1

The independent defect/security lane found effective global-format parsing and
missing metadata diagnostics; the independent documentation lane found stale delivery
claims. The initial local CodeRabbit CLI review reported zero findings and did not
detect those defects. Its clean result is not substituted for independent obligation
closure. The existing session retained counters and collected these findings as one
correction batch; no reset or generic second scope was introduced.

Before changing production behavior, 40 regression cases were run against the frozen
correction-test input: **37 failed, three passed**. Repeated scalar formats must use
the parser's last value; database values resembling commands or options remain option
values. Cases cover root/subcommand parsing and actual console invocation. Metadata
cases exercise missing/multiple rows, strict sequence/type/range, store identity and
dates, both numeric local records and claims lacking receipts. They require safe
stderr-only exit 2, no private values/tracebacks and unchanged stores.

The fix uses the installed root parser's resilient option parsing without callbacks,
not a competing token grammar. Local check validates exactly one metadata row and
existing Cutoff integer/identity/timestamp rules inside the same read transaction,
before authority/claim decisions. Known corruption becomes a controlled technical
error; unexpected programming exceptions are not broadly swallowed. Historical
archive bytes, portable contracts and persistence layout remain unchanged.

The full initial frozen local aggregate passed **1,882 tests in 101.85 seconds** and
two clean installed-wheel tests in 6.508 seconds. Lock/host negative-repair proofs,
hygiene, lint/format, types, docs/index, metadata/workflow, build and all 11 strict
OpenSpec items passed; dependency audit was not applicable to unchanged locked inputs.
Aggregate exit 2 preserves incomplete macOS native assurance: all ten required
analyzers returned unsupported_controller_platform (FAIL/UNKNOWN), not execution.
SpecFact CLI 0.55.4 raw report SHA256
`e8183dc7d168f197558eb5e8fca65e0426dd56ad03550b3b7430562aafb15c02`;
full original receipt remains `.changecost/workflow/workflow-01-advisory-ci/verify-quality-result.json`.
Those results describe the original frozen generation; corrected inputs still need
fresh verification and supported-Linux/current-head review before acceptance.

Correction red report SHA256 `aa6c39873417cd21b97797781713bdd8861d2faa0dae6402e07e63b112e0ab6e`.

Correction batch 1 green, captured before execution at `input-generation:17`
(input digest `dbe817fb8ac316852b803685cc4c57461062f62dd8a0aacea4157b50a433fd85`):
40 named regressions passed in 2.32 seconds; the full focused runtime suite passed
**156 tests and four subtests in 6.31 seconds**. Both commands used the installed
`.venv` PATH and retained their original bindings. Full Ruff/format, types (zero
errors) and all eight hygiene hooks passed during correction finalization.

```sh
PATH="$PWD/.venv/bin:$PATH" .venv/bin/python -m pytest tests/test_presentation.py::test_effective_global_format_parser_failures tests/test_presentation.py::test_effective_format_console tests/test_advisory.py::test_corrupt_metadata_safe_error_no_write -q
```

This resolves the demonstrated behavior locally. Independent affected-obligation
closure, fresh aggregate/current-head native Linux assurance and external published
reviews remain separate gates; task 5 remains pending until those actual outcomes.

- `correction-1-green.txt` SHA256 `55394105265b931c2956a750e5c902ca0f3a9d224b6ed5123512af19d4f15d11`.

- `correction-1-targeted.txt` SHA256 `2978ba2440d63c88871ba86c8b2f2f3d5929dd0f04e4b48be57a46450c8247ed`.

## Reviewed transport publication milestone — 2026-10-05 (Europe/Berlin)

The corrected runtime freeze (`input-generation:18`) passed all applicable local
leaves: 1,922 tests in 103.43 seconds, two clean installed-wheel proofs in 6.508
seconds, lock/host negative-repaired proofs, hygiene, Ruff/format, typing, docs/index,
metadata/workflow, build and all 11 strict OpenSpec items. Dependency audit is not
applicable because its locked inputs are unchanged. The aggregate still exits 2
solely because all ten required native analyzers report
`unsupported_controller_platform`; native verdict FAIL/UNKNOWN, exit 1.
The actual native report SHA256 is
`f0b7b8493a73d5ddebc384d6161cd4c203ed9c2658dfabd5b5166d6f50a72a1d`;
its preserved copy is `.specfact/verification/workflow-01-advisory-ci/native-epoch18.json`.
Earlier generation-15 native evidence is preserved separately, without relabeling
it as current evidence.

Independent read-only defect/security closure reran all 40 correction cases and
verified both parser and store-error findings fixed, with no new findings. A
separate documentation reviewer verified the status/rationale corrections and
current docs/index/metadata. Both local CodeRabbit CLI 0.8.2 runs completed
`review_completed`, each covering the complete combined diff including intended
untracked files and returning zero findings. The independent reviewer, rather
than CodeRabbit, identified the corrected defects. Actual reports remain under
`.changecost/workflow/workflow-01-advisory-ci/`; each retains its original binding.

The existing macOS handoff in the [gate guide](../../../docs/development/quality-gates.md)
permits transport of the reviewed feature to GitHub's supported Linux verifier
after local/staged checks. This specific bootstrap route is applied under the
maintainer's explicit implementation/verification/push/PR authorization despite
the verify skill's generic unresolved-gate publication prohibition. It grants no
native waiver or acceptance: both current-head Ubuntu Python jobs, complete native
reports and current-head Codex plus CodeRabbit remain required. This paragraph
records a publication milestone, not later live acceptance. Stage-5 acceptance
checkboxes remain pending; the future live PR receipt and bounded ledger carry
exact-head results without a receipt-only source commit.

Package remains 0.1.0.dev0. Rollback is a scoped follow-up revert retaining the
accepted Quote archive, original stores/backups and historical evidence. No paid
infrastructure, provider collection, merge, release or deployment is included.

## PR #34 cutoff authority and diagnostic helper correction — 2026-10-05

The actual current-head provider review identified a missing committed-timestamp
authority bound: a locally receipted Quote or computed Settlement could claim a
cutoff later than metadata.last_at but before an advanced wall clock. Independent
reproduction confirmed numeric advice for both record families; the separate
portable-graph report was rejected as a false positive using existing complete
RunRef validation. Upfront review traced the same timestamp assumption through
check, Quote inspection and computed Settlement inspection. The maintainer
explicitly extended the existing bounded session by 60 active minutes and two
correction batches before this work; previous counters and failures remain intact.

New specification and 18 regression cases were written before runtime edits.
Root captured `pr34-correction-red-packet.json` before execution. The actual red
selection returned **10 failed, eight passed, 69 deselected in 0.49 seconds**:
future committed cutoffs failed both direct paths and JSON/human CLI cases, and
populated stores with missing committed timestamps wrongly retained authority.
Equality and genuinely older cutoffs already passed. This red evidence is bound
to its original source/test inputs and is not reused as final certification.

The minimum correction keeps all existing store identity, sequence, receipt,
wall-clock and original historical replay guards and adds the committed metadata
timestamp upper bound across all three authority entrypoints. Missing timestamps
cannot certify inspection; a populated store without one returns check's existing
safe technical error. It changes no database layout, receipts, success schema,
comparison arithmetic or accepted Quote archive. Each new case checks unchanged
store bytes; the existing claim/artifact and real-target historical/oracle controls
remain part of the affected regression selection.

PR head `2009a11831c7b2a83b659d44470c2a771fb2134a` additionally ran
[Repository quality #37248663915](https://github.com/nold-ai/changecost/actions/runs/37248663915).
Both host suites passed 1,943 tests and two installed-wheel proofs; both native
coverage analyzers executed successfully with no UNKNOWN rows. The sole native
blocker on each job was the diagnostic fault helper's nine-level `elif` AST nesting.
Both privacy-safe metadata collectors succeeded. This does not make the failed
native reports passing, and does not establish the earlier timeout's cause.

The diagnostic helper refactor retains all nine file faults and four metadata
faults, using flat guards with returns. The installed signed 0.50.1 analyzer's
actual AST nesting functions measure depths nine/four before and one/one after;
its source digest and exact measured inputs are preserved in ignored
`pr34-native-ast-metrics.json`. These local metrics supplement the required fresh
supported-Linux native execution; no thresholds, test selection, vendor code or
deadlines were changed. Root captured `pr34-correction-green-packet.json` before
executing the repaired regression selection: all 18 new cases passed in 0.86
seconds. The broader affected selection passed 364 tests and four subtests in
13.35 seconds, including all 21 diagnostic controls and the existing Quote,
reconciliation, presentation, summary, fresh-store and installed-package tests.
Writer formatting/lint pass and BasedPyright reports zero errors. These results
retain their original green binding; later evidence/rationale text changes do not
rebind the prior reports. Independent affected closure, refreshed complete local/
staged checks and actual current-head Linux/native/provider acceptance remain
required. Rollback reverts only the correction diff; archived Quote evidence,
original stores and previous reports are preserved.

## Supported-Linux findings and maintainability correction — 2026-10-05

The reviewed transport head `3b46f92482d0c9ac60b9d38684310e30b56fd399` ran
[Repository quality #37243614107](https://github.com/nold-ai/changecost/actions/runs/37243614107)
on both supported Python versions. Both native reports contain four blocking
maintainability findings: `result_for` complexity 19, `check_record` ten parameters,
and the fresh-store integration test complexity 19/138 lines. Each scoped report also
retains 257 nonblocking warnings and nine informational findings, including
complexity/KISS, naming and Pylint/style advisories. These are actual native
outcomes, not macOS execution or a passing assurance claim. Each full report
contains 1,969 warnings, 36 informational findings and the same four errors.
Python 3.11 completed all ten native analyzers; Python 3.13 targeted coverage
remains UNKNOWN because the sealed launch timed out. The unchanged-config retry
still requires a fresh supported-Linux pass. Root retained the
reports and recorded correction batch two without resetting the existing session.

The correction groups the already validated RecordRef and Component inputs,
separates exact comparison from record context/presentation, and splits the same
fresh-store fixture into lifecycle, advisory and portable-roundtrip phases.
Registration, outcomes, every existing assertion and serialized result field/order
are preserved. No analyzer thresholds, dependency lock, persistence policy,
accepted Quote archive or portable/CLI contract changed.

Focused writer diagnostics after this refactor: 152 tests and four subtests pass;
Ruff passes and BasedPyright reports zero errors. A direct comparison against the
previous committed implementation confirms identical serialized result bytes for
24 Quote/complete-Settlement/incomplete-Settlement combinations across quantiles,
authority and economic compatibility. This supplements the independent contract
oracle rather than substituting previous behavior for the specification.

An isolated Radon 6.0.1 tool reports `result_for` complexity six/five parameters,
`check_record` complexity seven/five parameters, and the coordinator integration
test complexity one/four lines. Its phase helpers have complexity ten/five/six and
77/52/11 lines respectively. Exact executable/module provenance and AST parameter/
line measurements remain in ignored `native-correction-local-metrics.json`.
The isolated tool changes no repository dependencies and is only a local diagnostic;
it cannot replace the signed supported-Linux native gate.

These writer checks are diagnostic outcomes, not rebound certification of the old
head. Independent affected closure, refreshed complete local/staged checks and a
new current-head supported-Linux matrix/native report remain required before
publication acceptance and provider review. No PR was created while these native
findings remained unresolved.

## Runtime metadata diagnostic boundary — 2026-10-05

The corrected supported-Linux run #37245363690 removed all four blocking
maintainability findings. Python 3.11 completed all ten native members; Python 3.13
again reached the unchanged sealed coverage launch deadline. Both host suites,
wheel proofs and strict specs pass; this mixed result remains incomplete native
assurance. A renewed independent obligation review authorized a bounded metadata
collector before retrying that boundary, not a signed-vendor patch or timeout/
test-selection/quality waiver.

The development-only collector matches the report runtime identity to exactly one
canonical-hash/context-verified cache descriptor through no-follow directory/file
descriptors. It uploads only bounded allowlisted package/version/requested facts,
fixed Python markers and pytest-observe dependency names, excluding URLs, raw
requirements, project/payload/source data, arguments, logs and executable bytes.
Always-run diagnostic/upload steps preserve the original gate failure; collector
errors remain nonzero. Its detailed limits and rollback are in the gate guide.

Initial 16 missing-capability cases failed before implementation and then passed.
Those writer reports ran before the new input binding was captured and are retained
explicitly **unbound**; they are diagnostic chronology, not current-head acceptance.
Expanded meaningful tests cover privacy canaries, canonical/context mismatches,
duplicate/nonfinite JSON, linked/oversized/nonregular metadata, cache ambiguity,
parent replacement, byte bounds and exclusive/write-error output. A real-target
canonical-identity bypass must fail the same detector while the repaired boundary
passes. Fresh binding, independent closure and supported-Linux execution remain
required; successful collection alone cannot establish native assurance.


## PR #34 legacy-kind summary authority — 2026-10-05

An independent provider finding and upfront obligation review confirmed that the
summary validator accepted otherwise valid numeric Quote/computed-Settlement
advice after only its record kind was changed to legacy Settlement. That kind has
no local numeric authority. Correction batch four preserves the prior successful
head's supported-Linux evidence as history rather than rebinding it to this change.

The active specification was revised before production. Under the root's captured
red binding (input generation 36), the 13-case regression selection produced
12 failures and one pass in 0.70 seconds: all four producer-kind/status mutations
were accepted incorrectly, as were eight CLI mutations covering absent/existing
destinations. Valid legacy unknown advice already passed. Each direct mutation
first confirms the unmodified numeric producer result is accepted. The CLI checks
require exit 2, empty stdout, the fixed safe diagnostic, and unchanged existing
bytes or an absent destination remaining absent.

The minimal validator guard rejects numeric legacy status after record-kind
validation, before formatting or opening output. No producer, persistence,
economic arithmetic, accepted archive or native policy changes. Green execution,
independent affected review and fresh current-head gates remain pending at this
point; no unexecuted result is claimed.


Root captured green input generation 37 before execution. All 13 regressions pass
in 0.71 seconds; the full affected summary/advisory/control/public-CLI suite,
including the synthetic demo, passes 121 tests and four subtests in 7.13 seconds.
The first affected-suite command referenced nonexistent test_demo.py and collected
no tests; the corrected selection above provides the actual passing evidence.
Ruff passes. Both HEAD and explicit-main documentation gates pass after retaining
historical reasons and refreshing only ten actual stale source-bound rationales.
The installed signed 0.50.1 AST nesting function measures the added helper/tests
at depths zero through one; the amended validator remains depth one. Exact tool
and file metrics are retained in ignored pr34-summary-ast-metrics.json. These
writer diagnostics do not replace independent closure or fresh native assurance.
Rollback reverts this scoped validator/spec/test/documentation diff; persisted
stores and accepted Quote archive require no migration or modification.


The same batch's independent affected review found malformed status, record-kind
and quantile arrays/objects could trigger an unhashable-value traceback. Under
captured red generation 39, the 16-case CLI matrix produced 12 failures and four
passes in 1.23 seconds; completeness arrays/objects were already handled safely.
Every case checks the fixed diagnostic, exit 2, no private-canary disclosure, empty
stdout and destination integrity. Three enum allowlists now use tuples so all JSON
value types can be rejected through the existing validation error path without
adding branches. Null/bool/number rejection controls were added after that red run;
no failing evidence is claimed for those additions. Existing accepted unknown
legacy advice with a null quantile remains a positive control. Green validation
and fresh independent/native assurance are pending for these additional bytes.


Under captured green generation 40, all 38 expanded malformed-enum CLI cases pass
in 2.97 seconds, and the full affected suite (including the 13 legacy-authority
regressions and synthetic demo) passes 159 tests and four subtests in 10.12 seconds.
The three tuple replacements preserve validator complexity and nesting. Current
source-bound rationale fingerprints are refreshed for the same ten owned documents;
accepted archive bytes and prior failed/successful native reports remain unchanged.
Independent closure and fresh current-head gates remain required.

## PR #34 JSON decoder recursion — 2026-10-05

Direct review reproduced a 24,001-byte, 12,000-level JSON array causing an
uncaught RecursionError before summary validation. Under captured input generation
44, two console regressions failed in 0.21 seconds, covering absent and existing
summary destinations. Both require exit 2, empty stdout, the fixed safe diagnostic
and preserved destination state. The active specification was clarified before
production; the decoder boundary now catches RecursionError explicitly.

Under captured green generation 45, all 66 summary tests pass in 4.40 seconds.
This includes the two new regressions and prior authority, malformed-value,
Unicode, escaping, truncation and write-failure controls. No arbitrary exception
handler, store change or native-gate waiver is introduced. Independent closure
and fresh exact-head hosted assurance remain required. Rollback reverts only this
handler and its correlated tests/spec/docs; accepted Quote archive stays intact.

## Native coverage startup investigation — 2026-10-05

The current-head Python 3.11 job timed out twice in the signed native coverage
launcher; the Python 3.13 job passed. The launcher kills and discards timed-out
worker output, so a particular slow test and the complete cause remain unknown.
No analyzer, deadline, selection or enforcement setting is changed.

A read-only host profile found four Git setup commands for each review-session
case; the native capsule also starts a Python launcher for every Git invocation.
All 586 module tests passed in 88.45 seconds. An isolated experiment replaced only
the setup fixture with a once-committed seed copied into each fresh test directory;
all 586 tests passed in 71.49 seconds. AST comparison confirms 199 existing
functions/classes remain unchanged apart from that fixture. The tracked fixture
now uses those separate filesystem copies, including independent Git metadata,
without shared mutable repositories, mocked Git or reduced assertions. These
host measurements justify reducing repeated setup work, but do not establish
that the native timeout is fixed. Fresh full-suite, independent isolation review
and exact-head hosted assurance remain required. Rollback restores this fixture.

The tracked combined source passed all 2,014 tests in 101.55 seconds, both wheel
proof tests and all 11 strict OpenSpec items. The full explicit-base check also
identified the unchanged behavioral-evidence guide as stale; it now documents the
seed isolation mechanism and is rechecked independently. The ten native analyzers
remain unsupported on macOS; this local result does not certify Linux assurance.

## Original-cutoff and summary authority review — 2026-10-05

Fresh Codex review of 6a7d6ee identified cutoff and summary authority defects;
independent whole-family triage reproduced both. The cutoff could advance to its
own result insertion or later unrelated history without changing replay values.
Unknown summary advice accepted unsupported provenance/completeness strings.
Both supported local producers atomically capture sequence N and time T, then
insert their one result at N+1 and T. The shared original-cutoff predicate now
checks those anchors in advice and both inspectors, retaining existing receipt,
version, metadata/clock and replay requirements without a receipt/schema change.

Under captured input generation 51, the 20-case initial selection produced 16
failures and four passes in 0.64 seconds: 12 cutoff mutations and four summary
string claims were accepted; earlier-cutoff controls already rejected mismatches.
The broader consumer authority matrix under generation 52 produced 22 failures
and four passes in 1.18 seconds. Six additional cases covered impossible producer
completeness and local claims with missing cutoff or legacy kind. The legacy case
was subsequently strengthened to include a valid cutoff, isolating the kind
condition; no initial red result is claimed for that stronger control.

The consumer accepts only the two actual producer provenance strings and
complete/unknown completeness. Producer assertions cannot claim complete local
validation; local authority requires a computation kind and cutoff. Actual
incompatible-budget, incomplete and unpriced producer outputs remain positive
controls. The old abbreviated test provenance was corrected to actual output.

The first two-worker affected run under generation 53 passed 416 tests in 14.06
seconds. It covers original cutoffs, no-write behavior, summary controls, historical
Quote/Settlement replay and behavioral packets. Full-suite and final independent
closure remain required; subsequent documentation/stronger-control edits need
fresh binding rather than retroactively changing that report.

## Full-suite parallel execution — 2026-10-05

The 6a7d6ee Linux run passed all ten analyzers on Python 3.11 but timed out in
coverage on Python 3.13; all 2,014 host tests passed in 100.59 and 153.39 seconds
respectively, with nine other native analyzers passing and zero blocking findings.
The signed 0.50.1 source explicitly supports xdist collection and terminal reports,
rejects worker errors/incomplete targets, and combines controller coverage.
Pytest-xdist 3.8.0 and execnet 2.1.2 are locked test tooling, outside runtime package
dependencies. Pytest config now runs two local workers with load distribution.
No test selection, required analyzer, enforcement or deadline changes. Host success
cannot prove native subprocess/plugin compatibility or timeout resolution; fresh
complete distributed target execution and combined native coverage must pass on
both Linux jobs. The prepared 59-test packet-seed experiment remains ignored
investigation evidence and was not adopted. Rollback restores this scoped code,
test/config and documentation diff; accepted archives and stores remain unchanged.

Final initial parallel verification at generation 54 passed all 2,043 tests in
53.91 seconds, both wheel proofs and 11 strict OpenSpec items; the fresh dependency
audit found no known vulnerabilities. Independent review nevertheless found the
new availability predicate performed arithmetic on an unvalidated SQLite field.
This was corrected within the same unpublished batch. Under captured generation
55, 32 human/JSON check/explain controls produced 18 failures and 14 passes in
0.48 seconds, covering text/fractional/nonpositive sequence and invalid time.
No passing-before behavior is misreported as a new defect.

The existing Observation validator now checks the selected row's strict integer
sequence (1..MAX_SEQUENCE), typed reference and timestamp before cutoff arithmetic.
Under generation 56, all 448 affected tests pass in 15.20 seconds, including all
32 error/no-write/private-canary controls, original anchors and supported summary
combinations. A subsequent test-only edit uses fixed SQL statements for each
allowlisted fault column; final full checks and independent closure use its new
fingerprint. Native macOS evidence remains incomplete; final Linux execution and
all current-head provider reviews remain pending.

Final frozen generation 57 passed all 2,075 tests in 52.94 seconds, both wheel
proofs, dependency audit (no known vulnerabilities) and all 11 strict OpenSpec
items. Independent defect/security closure passed 214 affected tests in 4.82
seconds, eight documentation/navigation/metadata/workflow checks and actual
omission controls for each repaired boundary. All accepted archive bytes were
conserved. Independent config adoption confirmed 2,075 unique collected IDs,
unchanged runtime dependencies and original signed adapter fault controls. These
are host/local proofs: all ten native analyzers remain unsupported on macOS and
fresh exact-head Linux coverage/provider completion remains required. This final
evidence-only paragraph is separately checked before staging; source proofs retain
their generation 57 binding rather than claiming tests were rerun after prose.


## Operation receipt and summary scope correction — 2026-10-05

Current-head CODE review `5413700381` identified two genuine P2 defects on
`4535f4e`: Settlement receipt resolution omitted the persisted operation primary
key, and the summary accepted missing/legacy scopes for numeric computation advice.
Independent family review additionally reproduced contradictory USD/EUR scope and
an original-ID retry authorized by a cloned receipt. The maintainer's explicit
until-fixed approval authorizes this renewed family plan; prior counters and escapes
remain retained.

Before implementation, the new 26-case receipt/scope selection ran serially:
22 failed and four passed in 1.84 seconds. The four already-passing cases reject
missing numeric cutoffs, so they are controls rather than new red evidence. Changes
bind computed payload operation IDs to receipt keys and directly to retry requests;
Quotes retain their existing request binding without inventing an operation field.
Computation summaries require typed scope/cutoff and operation-appropriate
quantile/sample fields; numeric scope economic identity must match comparison.
The summary fixture now reflects real producer scope/cutoff/sample shape; its
existing missing-cutoff negative sets absence explicitly. An initial green run
caught that fixture assumption (407 passes/two failures), retained as test-author
correction evidence rather than a product defect.

The previous head's Linux run `37301916602` passed both Python jobs and all ten
native analyzers with exactly 2,075 unique complete test cases in each artifact.
Those results demonstrate the parallel full-suite timeout fix, not acceptance of
this new source diff. Fresh full gates, independent closure and current-head Linux
and required provider reviews remain necessary. No schema migration, analyzer,
test-selection/deadline waiver, provider collection or paid infrastructure is added.


Independent closure of the operation-specific validator caught a new legacy-cutoff
regression before publication: unlike actual legacy producer output (null cutoff),
non-null mappings passed and scalar/container values escaped via AttributeError.
A ten-case real console regression first produced eight failures/two valid-null
passes in 0.80 seconds. Legacy cutoff now requires null before any rendering or
summary destination access. This remains a recorded family escape in batch eight;
no prior investigation or counter is erased. The first full local run passed
2,101 tests in 53.72 seconds, wheel checks, dependency audit and strict validation;
all macOS native analyzers remained unsupported/incomplete. These pre-repair
results are retained, and final post-repair checks are required.


The post-legacy-repair full local suite passed 2,111 tests (all selected), wheel,
dependency audit and strict validation. Independent exact-tool Radon 6.0.1
inspection then measured compute_settlement at CC16, above signed module 0.50.1's
error boundary (>15). Before publication the retry validation was extracted into
one focused helper retaining the same transaction, request, typed record, operation
ID and receipt-membership checks. This is a recorded native-maintainability finding,
not a threshold waiver; extracted-helper controls and fresh full gates are required.


Final extracted-helper verification passed all 2,111 tests in 55.93 seconds, wheel
checks, dependency audit (no known vulnerabilities), all eleven strict OpenSpec
items. An overlong SQL test literal still failed lint in the full and staged gates;
its adjacent-string wrap preserves the same SQL and is checked before publication.
Independent closure passed 250 affected
tests, eight documentation/generated-index/metadata/workflow checks across both
explicit bases, actual omission controls and unchanged archive fingerprints. Exact
Radon 6.0.1 measurements are computation CC13 and retry helper CC6; signed native
Linux execution and fresh provider reviews remain pending. All ten macOS native
analyzers remain unsupported/incomplete; publication is needed to obtain supported
Linux evidence under the maintainer's explicit until-fixed authorization.

The retained full/staged lint failures are not passing gates. Final reruns after
the test-literal wrap must confirm lint and exact staged contents; no line-limit
exception or analyzer waiver was introduced.

After the literal wrap, the final explicit-base make check passed lint, hygiene,
types, docs/index/metadata/workflow, all 2,111 tests in 54.28 seconds, both wheel
checks, dependency audit and all eleven strict OpenSpec items. Its aggregate exit
remains two solely for the ten unsupported macOS native analyzers. Supported Linux
and required provider reviews remain mandatory after publication.
