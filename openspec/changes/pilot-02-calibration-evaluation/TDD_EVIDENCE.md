# Offline evaluation implementation evidence

## Scope and ownership

Implementation began on `codex/pilot-02-calibration-evaluation` at main base
`ffd8dff568f11e6e9283b00badbce6c98a0b5580`, refreshed by the integration owner.
The matching prepared stash was already restored. Existing archive/planning
changes, twelve unchecked historical tasks and source-approval hashes were
preserved. This stage made no Git, ledger, issue, provider or approval mutations.
The integration owner owns aggregate assurance and publication after handoff.

Input is declared portable synthetic history plus a versioned pre-registered
protocol. The user-visible result is a deterministic JSON report through
`changecost evaluate-synthetic`. A disposable Store computes local forecasts;
foreign receipts are never reconstructed. No normal runtime database is opened.
The repository-only selector reuses existing economic peers and quantiles. New
demand measurement explicitly selects observed-summary/v4 without changing old
receipt defaults. Synthetic conclusions never establish native calibration.

## Actual failing and passing evidence

All timestamps below are Europe/Berlin on 2026-10-26. The interpreter is the
installed `.venv/bin/python`, Python 3.13.14. The normal pytest configuration used
four workers. Logs are ignored local evidence under
`.changecost/workflow/pilot-02-calibration-evaluation/runtime-20261026/`.

| Time | Command | Observed result |
| --- | --- | --- |
| 23:36:26 | `.venv/bin/python -m pytest -q tests/test_evaluation_cli.py` | One meaningful RED. A valid 20-peer experiment expected exit 0 but the missing command returned 2. `red-cli.log`. |
| Following first implementation | Same command | One GREEN. Exact p50 10, p90 18, truth 15, width 8 and signed p50 error -5; unchanged ordinary database; repeated stdout equality. |
| 23:40:06 | `.venv/bin/python -m pytest -q tests/test_evaluation.py` | 16 passed, one fixture construction failure from incorrect Rehearsal fields. This was not product RED. Corrected the fixture to the existing model. `adaptive-first.log`. |
| 23:43:25 | `.venv/bin/python -m pytest -q tests/test_evaluation.py -k 'aggregate_has or unsafe_scope'` | Two meaningful REDs. Shared adaptive aggregate absent; unsafe economic unit accepted and emitted. `red-aggregate.log`. |
| 23:43:55 | `.venv/bin/python -m pytest -q tests/test_evaluation.py tests/test_evaluation_cli.py` | 33 GREEN after grouped observed metrics and boundary validation. `green-aggregate.log`. |
| 23:44:26 | `.venv/bin/python -m pytest -q tests/test_evaluation.py -k 'earlier_economic or late_policy'` | Late scoped policy incorrectly accepted in cold start. The economic fixture initially expected complete truth despite contradictory work bounds; that assertion was corrected, not counted as product RED. `red-timing.log`. |
| 23:44:41 | `.venv/bin/python -m pytest -q tests/test_evaluation.py -k earlier_economic` | Meaningful RED after the oracle correction. Earlier economic work was labeled missing truth instead of non-initial. `red-timing-corrected.log`. |
| 23:44:56 | `.venv/bin/python -m pytest -q tests/test_evaluation.py tests/test_evaluation_cli.py tests/test_quotes.py tests/test_demand.py tests/test_demand_revision.py` | 192 GREEN, including existing nested target-exclusion and historical replay regressions. `green-focused.log`. |
| 23:47:09 | `.venv/bin/python -m pytest -q tests/test_evaluation_cli.py -k extreme` | Meaningful RED. `1e1000` accepted rather than rejected at the bounded evaluation input. `red-numeric.log`. |
| 23:48:11 | `.venv/bin/python -m pytest -q tests/test_evaluation.py tests/test_evaluation_cli.py` | 38 GREEN including bounded numbers, separate rehearsal comparison, cleanup and measurement-envelope equality. `green-final-evaluation.log`. |

Some later acceptance variants first passed against reused existing Quote/demand
behavior. They are regression/acceptance evidence, not separately observed
pre-implementation RED. In particular, the complete compound chronology required
by tasks 2.3 through 2.5 is not claimed. Those boxes remain unchecked. The first
missing-command test establishes a real new public outcome failure, but does not
retroactively establish every later scenario's TDD order. No old accepted exception
is inherited.

## Acceptance coverage

The focused tests exercise fixed min20 fallback, min19 joint unpriced, run-wide
asymmetric suppression and exit 2, partial truth, imported Quote refusal,
independent corrected truth and terminal updates. Source/provider and unsafe-field
controls reject native input, missing paths, duplicate JSON members, nonfinite
JSON and unsupported magnitude without echoing private values.

Adaptive cases cover cold start, unknown ecosystems, exact current algorithm,
complete and partial measured truth, high-count failing metrics, future and
confounded pairs, transfer-only availability, useful/harmful scenario errors,
target-only preference and costly rehearsal. Existing demand_revision tests cover
nested selected-validation and bridge target exclusion with all attempts. The
new disposable local receipt test proves success, unrelated-policy noninterference,
later failing overlapping policy and a future learning forecast without validation.
Those local fixture receipts are never exported by the evaluator.

Attribution retains six asserted provider, two manual and two unbound records over
ten, with unknown money separate. Abandoned retry spend totals 4 + 6 = USD 10 once,
over USD 25 known terminal spend. Adding an unknown terminal Change makes the
whole-population share undefined. Normal reconciliation retains pending-correction
and effective-event diagnostics; conflicting identities and duplicate delivery IDs
are input errors rather than accepted scored financial history.

## Runnable committed example and overhead

The exact documented CLI was run twice with `examples/evaluation/history.json`
and `examples/evaluation/protocol.json`. `report-final.json` and
`report-final-repeat.json` matched byte-for-byte using `cmp` with exit 0. There
are five primary cases. The economic summary has one scored case and four missing
full-change money cases. Adaptive availability includes two repository summaries,
two dimensional summaries, one transfer scenario and one rehearsal with its own
broad comparator. Every conclusion remains synthetic-only not-yet-validated.

The same command with `--measure-runs 5` produced `report-measured.json` and a core
identical to the unmeasured result. Five successful repetitions on Darwin/Python
3.13.14 had median 1001.121959 ms, range 997.167334 to 1011.561166 ms, for 395358 input
bytes and 991232 temporary-store bytes per repetition. The timer is
`perf_counter_ns`, covering import/computation/report construction. Parsing,
serialization and cleanup are excluded. Load averages read before measurement were
1.48/1.54/1.72. The host core-count query was denied. This is an observed synthetic
execution cost, not a comparative benchmark, production latency promise or speedup.
No limiter was profiled. There were no paid provider calls or live data collection.

## Checks and remaining assurance

Scoped Ruff formatting/lint and BasedPyright passed after the implementation and
fixture corrections. Selected strict OpenSpec and documentation/index results are
recorded at final handoff. No aggregate `make check`, fresh native Linux assurance,
CodeRabbit, independent defect review, commit or PR publication occurred in this
implementation stage. Those obligations remain with verification/promotion.

The preserved 24-profile source register retains one usage approval. No source
approval or native reader was expanded. Input provenance is caller asserted; the
evaluator cannot detect arbitrary real data mislabeled as synthetic. Opaque safe
IDs and declared dependencies may still be identifying to their author. Use only
synthetic fixtures.

Rollback removes the additive evaluator/command/docs and optional default-preserving
selector. Existing stores have no migration or new persistent record kind. Temporary
stores are cleaned after handled failures. Remaining risks are cutoff mistakes,
misread scenario semantics and small dependent samples; the tests and permanent
synthetic conclusion constrain those risks without proving live accuracy.

## Final focused handoff

The final scoped command over evaluator, Quote, demand and demand_revision tests
passed 199 tests. `green-handoff.log` is the retained output. Scoped Ruff lint/format
and BasedPyright report no errors. The independent truth minimum and explicit
partial/observed/unavailable/imputed denominator fields each have a recorded
meaningful failure before their implementation (`red-independent-minimum.log` and
`red-categories.log`), followed by the final green suite. Imputed values have zero
accepted truth in this closed observed-policy experiment.

Selected strict OpenSpec validation passed. Documentation and generated-index gates
passed against HEAD with the intended untracked-file manifest. Historical unchanged
Settlement/quality prose uses reviewed content-bound rationales; no gate rule was
changed. Final CLI repetitions again matched byte-for-byte and the five-run
measurement envelope had an identical core. Full aggregate/native and provider
review remain unexecuted here.

`red-independent-minimum.log` completed at 2026-10-26T23:53:16.696300+01:00.

`red-categories.log` completed at 2026-10-26T23:54:15.567057+01:00.

`green-handoff.log` completed at 2026-10-26T23:54:31.555489+01:00.


## Independent review and boundary correction, 2026-10-27 Europe/Berlin

Independent defect review of frozen prospective tree
`81c39ff0ea8447b9b44558cc1917270254d41360` found two reachable boundary defects.
The complete CLI accepted a Unicode decimal exponent outside the bound and emitted
unsafe selected-policy component identifiers. The single correction owner applied
Fix Root Causes by aligning the evaluator's pre-parse numeric grammar with the
existing Amount/Rational Unicode decimal grammar and validating nested component
unit/basis identifiers centrally before computation. Existing numeric models and
exact arithmetic are unchanged. Policy population/category and rehearsal method
are closed literals; record references resolve to the already checked record IDs.
Economic identity and case/protocol IDs retain their existing checks.

The additional boundary scenarios were specified before regression tests and the
production correction. Actual evidence uses Python 3.13.14 and the existing four
pytest workers. Ignored logs and command/timestamp JSON are in the same runtime
folder as the original evidence.

| Completion time | Command / log | Observed result |
| --- | --- | --- |
| 2026-10-27T00:05:04.256949+01:00 | `.venv/bin/python -m pytest -q tests/test_evaluation_cli.py -k 'unicode or nested_component'`; `correction-red.log` | Nine genuine REDs, all `assert 0 == 2` with a successful report. Three cover Unicode exponent/integer/decimal bounds; two cover rational numerator/denominator length; four cover policy and rehearsal unit/basis. Three additional bounded-value controls failed in fixture selection with StopIteration, not a product defect; their selector was corrected. |
| 2026-10-27T00:05:21.868133+01:00 | Same focused command; `correction-green-boundaries.log` | Twelve GREEN, including exact truth 15 from three bounded Unicode numeric spellings and no rejected payload echo. No destructive exponent was constructed; the failing probe used magnitude 1000. |
| 2026-10-27T00:06:15.768829+01:00 | `.venv/bin/python -m pytest -q tests/test_evaluation.py tests/test_evaluation_cli.py tests/test_quotes.py tests/test_demand.py tests/test_demand_revision.py`; `correction-focused.log` | 211 GREEN. Existing Quote/demand replay and evaluation cases preserved. |

Initial correction Ruff found one import-order error, fixed without behavior
changes. Format, type checking, index and selected strict OpenSpec passed. The docs
check identified three stale content-bound rationale hashes after source changes;
those retained quality/Settlement documents were reviewed and their hashes
refreshed without altering historical bytes or gate policy. Final check logs use
`correction-final-*`. Aggregate/native checks are not duplicated in this correction;
the integration owner's original results and remaining UNKNOWN/FAIL limits stand.

Independent `documentation-review.md`, dated 2026-10-27, reviewed the concrete
protocol `synthetic-20261026-v1`, schema `changecost/evaluation-protocol-v1` and
formula `exact-errors-wilson95-scenario-median/v1` at the frozen tree above. It
confirmed four methods, fixed economic minimum 20, scoped rubric thresholds,
registration/arrival ordering, cutoffs and source gaps. This closes task 2.1 only
for the authorized offline protocol. It proves neither live preregistration nor
calibration. Tasks 2.3–2.5 and dependent 2.6 remain unchecked pending the explicit
historical-TDD disposition; every Stage 3 live task remains unchecked.

The no-comments audit's six module docstrings remain. They identify module
contracts, match the surrounding repository convention, and the repository Pylint
configuration sets only jobs, with no missing-module-docstring exemption. Removing
them solely for style risks introducing C0114. The local environment has no pylint
module, so no native Pylint pass is asserted. Both public API/command contract
docstrings remain. The single provenance comment explains why asserted binding
provenance is deliberately distinct from verified provider evidence; it protects
that test's interpretation and is retained as a non-obvious contract rationale.
No suppression, analyzer, gate or unrelated application refactor was introduced.

Current entrypoints now state locally implemented offline runtime pending complete
verification and publication. Dated planning history and all twelve unchecked
archive tasks are preserved. Rollback is removal of the additive evaluator or a
follow-up revert of this boundary correction; no persistent store changes occur.
Remaining failure modes are future projected free-text fields, unsupported numeric
spellings and synthetic results misread as live evidence. Closed report fields,
pre-parse bounds, nested component checks and permanent synthetic conclusions
mitigate these without claiming a general real-data detector or live accuracy.


The same-family output inspection also traced truth attempts to RunBinding.run and
its matching checked Run.ref, peer/dependency/policy ecosystem references to checked
record IDs, and case/protocol/economic identifiers to existing ASCII guards.
Source-gap codes, policy population, component category, rehearsal method and
outcomes are closed literals. Algorithm/formula/status/reason labels are closed or
locally constructed. Namespace/provider/surface strings are not projected by the
report constructors. Four additional public-CLI controls changed every fixture
RunRef run ID consistently, case ID, protocol version and source-gap code to unsafe
text; all four rejected without echo (`correction-projected-identifiers.log`).
These are existing-boundary regression controls, not newly claimed RED evidence.
