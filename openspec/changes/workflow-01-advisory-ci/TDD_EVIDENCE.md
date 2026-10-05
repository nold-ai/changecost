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
