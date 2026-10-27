# Local manual session implementation evidence

Implementation on 2026-10-25 Europe/Berlin. Branch `codex/local-session-dogfood`,
HEAD `de2c42bd1d303dd4cfd080d3effa9f8d77cd59da`. Parent verified remote main `4fcc9432ef46252470dfa9390bdb4ff31247dd43`
and reader `dfb1d84cd36125ed3bd2580631257054d0a19141` before this stage.
The parent owns the genuinely new bounded-review session. Older ledgers are preserved.

## Red before behavior

Observed at 2026-10-25T20:23:39.027211+01:00 Europe/Berlin.

After CLI-created OpenSpec artifacts and before session source changes,
`uv run --locked pytest -n 0 tests/test_sessions_cli.py -x -q` exited 1.
The existing application imported successfully. The first real `session start`
request returned exit 2 with sanitized invalid_request because the command did
not exist. One test failed in 0.36 seconds. Actual output is retained locally in
`/private/tmp/changecost-session-red.log`.

## Focused implementation results

The first coherent slice passed 23 CLI tests in 0.57 seconds. Expanded coverage
passed 27 tests in 1.62 seconds. Frozen estimates 100, 200, 200 versus actuals
200, 200, 1000 produced absolute errors 100, 0, 800 tokens. Focused tests also
exercise immutable revision inputs, latest-revision learning, partial exclusion,
unknown and zero actual, exact cohort separation, failed and abandoned totals,
retries/stale conflicts, real subprocess restart/concurrency, safe help/invalid
input/missing reads, unfamiliar-file rejection and safe human rendering.

Scoped Ruff and BasedPyright passed after normal formatting and annotations.
Early `PYENV_VERSION=3.12.13 radon cc src/changecost/sessions.py -s` reported a
maximum cyclomatic complexity of 10 for connection ownership; all other blocks
were below 10. Configured complexity threshold remains 10.

## Final scoped evidence

The final affected-scope regression result was observed at 2026-10-25T20:27:23.244067+01:00 Europe/Berlin.
Environment is the isolated worktree's Python 3.13.14 and uv 0.12.19. All commands
below ran against this working content, with no Git commit or publication.

- `uv run --locked pytest -n 0 tests/test_sessions_cli.py tests/test_cli.py tests/test_presentation.py tests/test_demand_cli.py tests/test_contract_cli.py -q` exited 0, with 114 tests and four subtests passing in 7.51 seconds. Actual output is retained in `/private/tmp/changecost-session-regression.log`.
- `uv run --locked ruff format --check src/changecost/sessions.py src/changecost/session_demo.py src/changecost/cli.py tests/test_sessions_cli.py` exited 0, with four files formatted.
- `uv run --locked ruff check src/changecost/sessions.py src/changecost/session_demo.py src/changecost/cli.py tests/test_sessions_cli.py` exited 0.
- `uv run --locked basedpyright src/changecost/sessions.py src/changecost/session_demo.py src/changecost/cli.py tests/test_sessions_cli.py` exited 0, with zero errors, warnings or notes.
- `make generate` exited 0 using the existing renderer. `make docs BASE_REF=HEAD MANIFEST=.changecost/dogfood/manifest.txt` and the corresponding `make index` exited 0. The docs check initially identified eight unchanged manual contracts. Existing content-bound rationale records now explain why their core, demand, contributor and accepted historical contracts remain accurate; no generated exception was added. `/private/tmp/changecost-session-docs-green.log` retains the passing docs result.
- `OPENSPEC_TELEMETRY=0 openspec validate dogfood-01-local-sessions --strict --no-interactive` exited 0.
- `PYENV_VERSION=3.12.13 radon cc src/changecost/sessions.py src/changecost/session_demo.py -s` exited 0. Maximum complexity is 10, matching the existing configured limit. Demo functions are at most 4.

`uv run --locked python -m changecost.session_demo .changecost/session-demo-implementation-01`
exited 0 through eight actual subprocess CLI operations. Its retained
`.changecost/session-demo-implementation-01/transcript.json` records all inputs
and outputs. Forecasts were 100, 200 and 200 tokens against 200, 200 and 1000.
Signed errors were -100, 0 and -800. Absolute errors were 100, 0 and 800.
The next forecast was 200 from three samples. Cumulative MAE was 900/3 =
300.000000 tokens, with one pending session excluded. The fresh-directory and
no-core-store assertions also passed in the focused demo test. No default real
session database was created by this demonstration.

No aggregate make check, supported Linux capsule, full Python matrix, provider
review, publication or acceptance is claimed. This implementation stage owns
focused checks. Verification owns missing aggregate assurance and independent
closure.

## Limits and rollback

Manual totals and exact cohort labels are user assertions. All forecasts remain
provisional and uncalibrated. Partial totals cannot establish full-session errors.
The database is local only, with normal SQLite transactions and no cross-file merge.
No native collection, source approval, core Store, economic or billing policy changes.
Rollback removes command wiring and preserves the separate session SQLite file.


## First-creation correction, 2026-10-25 Europe/Berlin

The three independent local reviews identified one bootstrap defect,
`dogfood-bootstrap-1`. The final database path became visible before schema
commit. A second first start or a retry after interruption rejected that file.
The correction prepares and commits a private database on the same filesystem,
closes it, then publishes a hard link without replacing any existing path.
A competing creator recognizes the published winner before normal transactions.
The schema, forecasts, revisions, core store and native/economic authority remain
unchanged. The redundant test-module docstring was removed as reviewed.

Before implementation, the updated specification and five deterministic tests
were in place. At 2026-10-25T20:33:14+01:00,
`uv run --locked pytest -n 0 tests/test_sessions_cli.py -k 'first_creation' -q`
exited 1 with 5 failed and 27 deselected in 0.62 seconds. Real subprocess exits
before and after schema initialization both made the normal CLI retry fail with
`session_store_unrecognized` and `assert 2 == 0`. A paused initial creator caused
the concurrent CLI start to fail the same way. A normal initialization exception
left `sessions.sqlite3` behind. The foreign-publication collision returned success
instead of rejection, producing `assert 0 == 2`. The actual output is retained in
`/private/tmp/changecost-session-bootstrap-red.log`.

At 2026-10-25T20:33:41+01:00, the same focused command exited 0 with 5 passed and
27 deselected in 0.39 seconds. The tests use events to force the first-use race,
not timing loops. Real process interruption covers both sides of schema creation.
Normal exceptions leave no preparation files, and a foreign publication collision
preserves the exact foreign bytes. Existing empty, foreign, text and core-file
rejection cases remain in the regression set. The passing focused output is in
`/private/tmp/changecost-session-bootstrap-green.log`.

Final scoped checks after the lint correction:

- `uv run --locked pytest -n 0 tests/test_sessions_cli.py tests/test_cli.py tests/test_presentation.py tests/test_demand_cli.py tests/test_contract_cli.py -q` exited 0 at 2026-10-25T20:34:43+01:00, with 119 tests and four subtests passing in 9.76 seconds. Output is retained in `/private/tmp/changecost-session-bootstrap-regression-final.log`.
- `uv run --locked ruff format --check src/changecost/sessions.py src/changecost/session_demo.py src/changecost/cli.py tests/test_sessions_cli.py` exited 0 with four files already formatted.
- `uv run --locked ruff check src/changecost/sessions.py src/changecost/session_demo.py src/changecost/cli.py tests/test_sessions_cli.py` exited 0. The initial SIM105 finding was fixed with `suppress(FileExistsError)` around only the hard-link publication.
- `uv run --locked basedpyright src/changecost/sessions.py src/changecost/session_demo.py src/changecost/cli.py tests/test_sessions_cli.py` exited 0 with zero errors, warnings or notes.
- `PYENV_VERSION=3.12.13 radon cc src/changecost/sessions.py src/changecost/session_demo.py -s` exited 0. Maximum complexity is 9 against the existing limit of 10. Connection complexity is 7 and creation complexity is 1. Output is retained in `/private/tmp/changecost-session-bootstrap-radon.log`.
- `OPENSPEC_TELEMETRY=0 openspec validate dogfood-01-local-sessions --strict --no-interactive` exited 0.

`uv run --locked python -m changecost.session_demo .changecost/session-demo-bootstrap-01`
exited 0 at 2026-10-25T20:34:20+01:00. The fresh directory's `transcript.json`
retains the eight real CLI operations. Forecasts 100, 200 and 200 tokens against
actuals 200, 200 and 1000 produced absolute errors 100, 0 and 800 tokens. The next
forecast was 200 from three samples. MAE remained 900/3 = 300.000000 tokens with
one pending exclusion. Output is in `/private/tmp/changecost-session-bootstrap-demo.log`.

`make docs BASE_REF=HEAD MANIFEST=.changecost/dogfood/manifest.txt` and
`make index BASE_REF=HEAD MANIFEST=.changecost/dogfood/manifest.txt` exited 0.
The initial docs result identified six stale fingerprints. Only those existing
manual-document digests were refreshed through the existing source-selection and
digest functions. Their retained rationales still describe unchanged core,
settlement, contributor and accepted historical contracts. No rationale text,
generated-document exception or gate policy changed. Outputs are retained in
`/private/tmp/changecost-session-bootstrap-docs-green.log` and
`/private/tmp/changecost-session-bootstrap-index-green.log`.

Abrupt process termination can leave a private `.sessions-*` preparation directory,
but it is never adopted as the configured database and cannot block a retry.
Normal exceptions remove it. This local-filesystem implementation relies on
hard-link support. It does not claim power-loss or network-filesystem assurance.
Existing published databases are not migrated or replaced. No aggregate make
check, full Python matrix, supported Linux, provider or publication assurance was
run in this correction. Independent closure remains the parent stage's task.

## Local parent acceptance

Observed 2026-10-25T20:38:56.257290+01:00. The parent reran
`uv run --locked python -m changecost.session_demo .changecost/session-demo-final-parent-01`
through the actual CLI after the bootstrap correction. It exited 0 with forecasts
100/200/200, actuals 200/200/1000, absolute errors 100/0/800, the next median 200
and cumulative MAE 900/3 = 300.000000 tokens. The isolated transcript is retained
in that directory. `uv build --wheel --out-dir .changecost/dogfood/dist` exited 0
and created the local 0.1.0.dev0 wheel. No package was published.

Fresh independent affected-scope review closed `dogfood-bootstrap-1`. It reran all
32 session tests successfully and verified all 19 then-frozen hashes. The report
is `/private/tmp/changecost-dogfood-bootstrap-closure.md`. No additional runtime
finding was established. This closes task 2.1 only; full final/provider, aggregate
Linux/Python and PR acceptance remain pending.

The adopted generated-reference regression initially failed twice with
`FileNotFoundError` for its omitted source-profiles fixture. This was test setup,
not a product TDD failure. Calling its existing `copy_generator_register(tmp_path)`
fixture helper repaired the integration with the reader-based generator. The
parent then ran `uv run --locked pytest -n 0 tests/test_repository_gates.py -q`,
which exited 0 with 145 passed. Before/after outputs are retained in
`.changecost/dogfood/adopted-fixture-red.log` and `adopted-fixture-green.log`.
The manifest now includes that twentieth test path. Runtime source was unchanged
by this fixture correction. Both correction batches remain in the existing ledger.


## Accepted delivery and archival disposition, 2026-10-26 Europe/Berlin

[PR #47](https://github.com/nold-ai/changecost/pull/47) merged at
`ffd8dff568f11e6e9283b00badbce6c98a0b5580`. The accepted reviewed head was
`8cc0c681b71d430fd44b0cc874f4f7585b76d73f`, compared with
`4fcc9432ef46252470dfa9390bdb4ff31247dd43`. GitHub readback on 2026-10-26
confirms the merged PR includes this change, all three session changes and the
finite diagnostic reader. Required current-head Codex and CodeRabbit code reviews
completed without actionable findings; scoped acceptance and publication occurred.

The maintainer accepted the narrow native capsule timeout exception for that
head. Both ordinary host suites passed 3,525 tests. The Python 3.13.14 host's
mandatory check and all ten native analyzers passed with PASS_WITH_ADVISORY. The
Python 3.11.15 host's mandatory check failed because native pytest coverage remained
UNKNOWN after `sandbox_launch_failed:timeout` at the unchanged 300-second deadline.
The two native target runtimes report Linux x86-64 CPython 3.13.11, independently of
the host matrix versions. The canonical helper remains INCOMPLETE under unchanged
gate policy. This exception establishes neither passing full assurance nor a waiver
for future changes. [The final CI run](https://github.com/nold-ai/changecost/actions/runs/40242126948)
preserves both passing and failing results. Historical evidence above remains intact.

The maintainer explicitly requested native CLI archival despite the retained
unchecked compound tasks. Completed provider-review, publication and acceptance
sub-obligations are evidenced by PR #47. Full unqualified supported-Linux assurance
remains incomplete. All three unchecked boxes are preserved rather than relabelled
as passing. Any remaining tracking/readback sub-obligation stays incomplete unless
separately evidenced. Archive synchronization is performed only by `openspec archive`.

No new source approval, complete native demand, billing, calibration, collection,
release or publication authority follows from archival. The canonical register
retains 24 profiles and one finite usage approval. Rollback uses a focused revert
that preserves accepted evidence and any existing local runtime data.
