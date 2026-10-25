# Provisional Codex implementation evidence

Implementation on 2026-10-25 Europe/Berlin in the exclusive local-session-dogfood worktree, branch codex/local-session-dogfood, retained HEAD de2c42bd1d303dd4cfd080d3effa9f8d77cd59da plus dogfood-01/02. Parent supplied selected design, independent upfront review, safe source shape and actual producer preflight. No raw private source was read by this implementation agent.

## Red before implementation
Specs preceded tests and production. Native OpenSpec status/instructions reported the selected change ready with twelve tasks and four returned context artifacts, all read. `PATH="$PWD/.venv/bin:$PATH" .venv/bin/python -m pytest -o addopts='' tests/test_codex_provisional_sessions.py -q` exited 1 with one failure. The actual CLI start with --source codex returned exit 2 and a fixed invalid_request diagnostic because the selector was missing. Retained raw output is `.changecost/codex-live/red.log`.

## Focused working result
The new actual CLI loop starts a Codex attempt with guess 100, captures repeated cumulative totals 150, 200 and 200 as reported 200 exactly once, shows signed error -100 and 50% absolute relative error, and freezes the next comparable forecast at 200 with one sample. It keeps manual false, unknown coverage/completeness/finality/subagent inclusion, unverified producer and false core/billing/calibration authority.

The expanded focused run passed 94 tests in 3.80 seconds, including existing manual and finite suites. Raw output is `.changecost/codex-live/focused.log`. Further final focused/check results are recorded below after documentation and formatting are complete. Full supported Linux/Python, provider review, actual private-source proof and PR acceptance remain unchecked. No aggregate make check or full native review is claimed.

## Boundaries and rollback
Synthetic sources only. One explicit bounded streamed local-file read and short SQLite transaction, without paid service or timing promise. The selected counter is lifetime cumulative and can include work before start. Omitted work, invisible resets and subagent coverage remain unknown. Use fresh Codex threads where possible, consistent cohort labels and provisional claims. Back up the local session store before v3. Old binaries reject v3; restore the pre-upgrade backup to roll back, preserving the upgraded file separately if later writes matter. Manual/finite plans and historical TDD remain unchanged. The parent owns independent review and final actual-source proof after source freeze.

## Final focused checks

All final commands below ran with the existing worktree `.venv/bin` first on PATH. Tool versions were Python 3.13.14, Ruff 0.16.9, BasedPyright 1.40.1 with Pyright 1.1.414, and OpenSpec 1.13.2. No tool repair or dependency change was performed.

- `.venv/bin/python -m pytest -o addopts='' tests/test_codex_provisional_sessions.py tests/test_sessions_cli.py tests/test_codex_session_observations.py tests/test_codex_local.py tests/test_native_usage.py tests/test_presentation.py tests/test_cli.py tests/test_repository_gates.py -q` exited 0. Result 367 passed and 4 subtests passed in 11.78 seconds. Raw output `.changecost/codex-live/final-focused.log`.
- `.venv/bin/ruff check --no-cache src/changecost/codex_session_counter.py src/changecost/sessions.py src/changecost/cli.py src/changecost/presentation.py tests/test_codex_provisional_sessions.py tests/test_sessions_cli.py tests/test_codex_session_observations.py` exited 0. `.changecost/codex-live/lint.log`.
- `.venv/bin/ruff format --check --no-cache` over those same seven paths exited 0 with seven files already formatted. `.changecost/codex-live/format.log`.
- `.venv/bin/basedpyright` over those same seven paths exited 0 with zero errors, warnings or notes. `.changecost/codex-live/types.log`.
- `.venv/bin/ruff check --no-cache --select C90 src/changecost/codex_session_counter.py src/changecost/sessions.py src/changecost/cli.py src/changecost/presentation.py` exited 0. This checks actual changed-function complexity against configured maximum 10; no unmeasured per-function scores are claimed. `.changecost/codex-live/complexity.log`.
- `.venv/bin/python -m quality docs --base de2c42bd1d303dd4cfd080d3effa9f8d77cd59da --manifest .changecost/codex-live/manifest.txt` exited 0 after source-bound rationale refresh for nine retained core/contributor/historical guides. The initial stale-documentation result was not a passing check. `.changecost/codex-live/docs.log`.
- `.venv/bin/python -m quality index --write` regenerated current command/navigation output. The canonical packaged admission remained byte-identical. The same docs-base/manifest invocation with `index` and `metadata` each exited 0. `.changecost/codex-live/index.log` and `metadata.log`.
- `OPENSPEC_TELEMETRY=0 openspec validate dogfood-03-codex-provisional-loop --strict --no-interactive` exited 0 and reported the change valid. `.changecost/codex-live/spec.log`.

The first compatibility run passed 59 and failed one old human-format literal assertion. The requested concise renderer intentionally changed that literal; the test now asserts manual identity, actual measured total and retained escaping. Final semantic assertions pass. Earlier source formatting/type findings were fixed before the final checks. No failing check is relabeled green.

## Actual CLI and retained contracts

Four real-process `.venv/bin/python -m changecost --db UNUSED --format human session --session-db ISOLATED` operations ran with synthetic inputs only. Start synthetic-01 with source codex and guess 100; capture its explicit file/repository/outcome; start synthetic-02; request exact-cohort Codex history. Every process exited 0. Capture reported 200, absolute error 100 and 50.00%; next forecast was 200 from one sample. History disclosed evaluated 1 and learning 1 separately. The unused core store was not created. Exact operation argv and output are retained in `.changecost/codex-live/synthetic-cli.json`.

Boundary tests include a synthetic source over 34 MiB, exactly 100,000 rows, safe row ordinal 10,003, unsupported producer/source shapes, signed 64-bit integer bounds, duplicate JSON members, depth/numeric limits, symlinks, unstable acquisition, null counter events, reset rejection, explicit prefix continuity, historical retry after later revisions, global identity deduplication, manual/native exclusion, zero/half-token arithmetic, atomic migration/insertion failure and concurrent identical/conflicting captures. Existing finite observation remains usable on v3 without downgrade. Human summaries retain control escaping and concise finite diagnostic exclusion without expanding all category facts.

Sixteen retained dogfood-01/02 planning/TDD and finite helper/demo/test paths matched their handoff baseline hashes. `docs/providers/source-profiles.json` and `src/changecost/codex_admission.json` matched HEAD byte-for-byte. The exact reader `src/changecost/codex_local.py` matched its retained handoff baseline. No canonical profile, approval count, old evidence or ledger was rewritten.

## Design reconciliation and handoff

The selected B architecture is implemented. Its four independent clarifications are present: manual membership exclusions, supplied-predecessor prefix acquisition plus exact retry before newest checks, strict signed 64-bit counter domain, and one latest learning attempt versus evaluated-error count. Parent safe evidence added observed version 11.2 before production; it shares mapping/quantity/family with 10.2 while each capture/input discloses actual version. Only vscode and subagent.thread_spawn are recognized. Other subagent variants remain unsupported. Frozen forecast inputs additionally retain immutable repository association and start sequence. These are provenance details within the selected contract, not another helper or architecture.

Model the Domain shaped the frozen snapshot and explicit capture operation. Make Operations Idempotent shaped transaction-time saved retries and predecessor checks. Experience First shaped one capture command and compact history rows with shared unknowns. All cited leaf skills were read. The existing chosen design records the same contract. No new review/evidence schema or ledger machinery was added.

The next stage is parent actual-source proof after source freeze and independent affected-scope review, followed by applicable aggregate verification. Full Linux/Python/provider/PR acceptance remains unchecked. There is no commit, push, PR, merge, external collection or publication from this implementation stage.

## Retained log write timestamps

These are retained artifact modification times in Europe/Berlin, not invented process start times.

- `red.log` 2026-10-25T21:18:50+01:00.
- `final-focused.log` 2026-10-25T21:25:39+01:00.
- `lint.log` 2026-10-25T21:26:34+01:00.
- `format.log` 2026-10-25T21:26:34+01:00.
- `types.log` 2026-10-25T21:26:35+01:00.
- `docs.log` 2026-10-25T21:26:36+01:00.
- `index.log` 2026-10-25T21:26:36+01:00.
- `metadata.log` 2026-10-25T21:27:49+01:00.
- `complexity.log` 2026-10-25T21:27:50+01:00.
- `spec.log` 2026-10-25T21:26:34+01:00.
- `synthetic-cli.json` 2026-10-25T21:27:04+01:00.

## Focused producer identity correction on 2026-10-25

The parent actual-source attempt failed at ordinal 0 with `source_identity_mismatch`; its safe retained report is `.changecost/codex-live/actual-01/failed-first-capture.json`. Parent source-shape inspection established separate thread `id` and runtime `session_id` roles. This writer used only that safe evidence and authored synthetic inputs, and did not read private actual files. The first implementation had incorrectly required equality. Existing finite request validation already distinguishes the roles. Specification clarification preceded the focused test and production correction.

The data shape is unchanged: header `id` supplies the existing domain-separated deduplication hash, while optional `session_id` is independently validated as a nonblank string of at most 512 characters. No persistence, format version, counter mapping, authority, or approval changes were made. The default positive fixture now includes a distinct runtime identity. The redundant comment identified by comment review was removed.

All commands ran from the owned worktree with its `.venv/bin` first on PATH. Retained logs use the `.changecost/codex-live/identity-fix-` prefix.

- Red: `.venv/bin/python -m pytest -o addopts='' tests/test_codex_provisional_sessions.py -k distinct_runtime_identity -q` exited 1 before production changes. Both admitted versions failed with `{"schema": "changecost/error-v1", "code": "source_identity_mismatch", "message": "provisional Codex source rejected", "ordinal": 0}`. Result: 2 failed, 49 deselected. Log `identity-fix-red.log`.
- Green: `.venv/bin/python -m pytest -o addopts='' tests/test_codex_provisional_sessions.py -k runtime_identity -q` exited 0 with 13 passed, 38 deselected. The actual CLI capture/next forecast admits distinct IDs for both versions; changing only the runtime identity and path cannot duplicate a thread's training. Database bytes remain unchanged on duplicate and malformed identity rejection. Tests retain absent/equal runtime ID compatibility, the 512-character bound, and reject null, nonstring, blank and overlong values. Log `identity-fix-green.log`.
- Compatibility: `.venv/bin/python -m pytest -o addopts='' tests/test_codex_provisional_sessions.py tests/test_sessions_cli.py tests/test_codex_session_observations.py tests/test_codex_local.py -q` exited 0 with 158 passed in 5.49 seconds. Log `identity-fix-focused.log`. This includes all provisional cases with the more realistic positive fixture and nearby manual/finite contracts.
- `.venv/bin/ruff check --no-cache src/changecost/codex_session_counter.py tests/test_codex_provisional_sessions.py` exited 0, including configured complexity checks. Log `identity-fix-lint.log`.
- `.venv/bin/ruff format --check --no-cache src/changecost/codex_session_counter.py tests/test_codex_provisional_sessions.py` exited 0 with two files already formatted. Log `identity-fix-format.log`.
- `.venv/bin/basedpyright src/changecost/codex_session_counter.py tests/test_codex_provisional_sessions.py` exited 0 with zero errors, warnings or notes. Log `identity-fix-types.log`.
- `OPENSPEC_TELEMETRY=0 openspec validate dogfood-03-codex-provisional-loop --strict --no-interactive` exited 0. Log `identity-fix-spec.log`.

The original 39-path source freeze and failed actual proof remain immutable. The correction uses the same 39 paths in `.changecost/codex-live/identity-fix-manifest.json`. Parent owns actual selected-source CLI proof, affected independent closure and affected documentation provenance checks after release. Full supported Linux/Python, aggregate assurance, provider review and PR acceptance remain pending. No full make/native/CI/provider checks were rerun and no commit, push or merge occurred. This correction changes no stored identity or schema, so rollback is limited to the focused source/test/spec correction; it restores the demonstrated rejection defect. Existing store backup guidance remains applicable.


## Parent actual-source acceptance and affected closure, 2026-10-25 Europe/Berlin

The first actual-source attempt rejected a valid supported 11.2 header because
thread and runtime session identities differ. Both selected real headers have
distinct identities. The original failed capture and
unchanged database are retained in ignored `actual-01/failed-first-capture.json`.
The existing core reader treats those identity roles separately; metadata-only
inspection of 48 and 49 request records corroborated their respective header joins.
The original independent review reproduced that defect and found no others.
One correction batch preserved this history. The focused red/green and 158-case
compatibility rerun above retain their actual scope; the earlier 367-case result
is not relabeled as a new all-suite run after correction.

After correction, the installed CLI used two real, explicitly selected 11.2 local
sessions with the ordinary packaged code and no substituted admission or typed
post-work total. Reported lifetime counters were 4,973,643 and 6,533,098 tokens.
A retrospective illustrative guess of 5,000,000 had absolute error 26,357. The next
frozen estimate was 4,973,643 and had absolute error 1,559,455. The next pending
estimate was 5,753,370.5 from two samples. Descriptive MAE was
1,585,812 / 2 = 792,906 tokens. These heterogeneous historical replays demonstrate
calculation and worsening as well as changing error; they do not validate
prospective accuracy or calibrated improvement.

Exact repeat capture left database bytes unchanged. A second attempt selecting the
same source and a symlink source both rejected without writes. Both real source
files were unchanged. No manual measurements or core store were created. Coverage,
completeness, finality and subagent inclusion remained unknown, producer claims
unverified and core/billing/calibration authority false. Safe receipts and redacted
CLI output are ignored `.changecost/codex-live/actual-02/proof.json`, `transcript.json`,
`history.txt` and `show.txt`. Human history was 713 bytes and the session report
456 bytes. Those are output sizes, not runtime performance measurements.

A separate real current 10.2 thread of 35,827,520 bytes and 11,901 rows was accepted
without widening the finite core reader limits. Its reported counter was
224,724,043. An explicit subsequent append capture accepted the identical old
prefix at 35,846,707 bytes and revised the counter to 224,960,717. The preceding
forecast stayed frozen; a later forecast used the revised quantity with sample
count one. The unestimated original capture trained but remained excluded from
MAE. The existing long thread includes earlier work, so it is a functional
lifetime-counter check, not measurement of this change. Safe receipts are
`actual-02/long-thread-first.json` and `long-thread-refresh.json`.

An actual stored finite diagnostic report remained schema v2 and byte-identical
on read. Its human summary was 320 bytes and did not expand its 96 fact records.
The canonical register, packaged finite admission and finite reader remain
unchanged. Old plan/TDD and review-session histories remain preserved.

Fresh independent correction closure by gpt-6-astra verified all 39 corrected
hashes, exactly five changed paths and the header guard as the only runtime delta
from the original reviewed feature. It independently ran 16 identity, dedup,
retry and prefix cases, all passing, and closed `thread-runtime-identity-finding`
with no new findings. It did not inspect private source files or claim full
Linux/provider assurance. Original review, comment review and closure reports are
retained locally in `.changecost/codex-live/review/`. One redundant test comment
was deleted; public contract docstrings and all analyzer protections were retained.

Local runnable implementation, actual-source demonstration and affected review are
complete. Full Linux/Python, required provider reviews and PR acceptance remain
pending. There was no commit, push, PR, merge, release or provider invocation by
the runtime. Rollback after schema v3 needs the pre-upgrade session-store backup.


The post-correction documentation check retained its failed result for six unchanged
core/contributor/historical guides until their existing content-bound rationale
digests were revalidated. The correction changes only provisional header identity
validation and its tests/specification; those guides, approval policy and gate
implementation are unchanged. Their existing rationale prose remains applicable.
Only the six source digests are refreshed, without a new exception or waiver.
Final docs/index/metadata/strict/whitespace receipts are retained separately in
`.changecost/codex-live/final-checks.json`; no broad suite rerun is implied.

## Verification and private CI handoff on 2026-10-25

The maintainer authorized `$changecost-verify`, preservation of review history,
reuse of applicable checks, private branch upload and fresh Linux/Python CI. No
merge is authorized. The existing ledger remains in use with its original failure,
correction and timing history. Main and merge base are
`4fcc9432ef46252470dfa9390bdb4ff31247dd43`. The full prospective merge scope has
77 paths, including the inherited finite reader and generated-reference correction.

All 39 final implementation input hashes still matched. Independent composition
review reused exact-content earlier reviews and found no additional defect. The
fresh documentation review found one P3 status-description drift. Current overview
and index descriptions now acknowledge the completed real-source proof and local
closure. Dated implementation evidence remains unchanged.

Fresh non-native aggregate leaves passed against the complete scope, including
lock, hygiene, Ruff lint/format, BasedPyright, docs, generated index, metadata,
workflow, all 3,525 tests, clean package build/install with five tests, and all
18 strict OpenSpec items. Dependency audit was correctly not applicable because
its locked inputs were unchanged. Tool versions and exact commands are retained
in the existing ignored verification directory. Supported native assurance remains
pending fresh Linux/Python 3.11.15 and 3.13.14 CI at upload. This Mac cannot run the
required capsule, so no repeated unsupported native attempt or local aggregate
pass is claimed. Subsequent exact-commit CI/native results belong to the existing
ledger and verification handoff; provider/PR acceptance remains a later stage.

## First supported Linux attempt and test correction

Run `40233108333` on committed head
`451c8aeeef40c9cae8cbdc41a8176c60ae7cc7a9` failed native assurance on both
Python versions. Each ordinary Linux suite passed 3,525 tests and all 18 strict
OpenSpec items passed. The complete native reports and source bindings are retained
in the existing ignored verification directory, including all advisory dispositions.
Seven required analyzers passed. Radon reported six blocking test-structure findings;
Pylint timed out after 30 seconds and targeted coverage remained UNKNOWN after its
300-second timeout. The later selected historical-test diagnostic passed all ten
analyzers, but does not replace the failed full-scope result.

Correction batch 3 changes only the two test modules. Four coherent assertion
helpers retain each end-to-end scenario; three exceptional repository operations
now spell their CLI arguments directly; rejected source preparation is separate
from its transaction/privacy oracle with flat mutually exclusive mutations.
All 238 assertions, test names, decorators and 18 rejection cases are preserved.
Before and after affected runs each passed 83 tests. The retained equivalence proof
compares 108 capture argument combinations and byte-identical rejected source inputs.
Its first execution needed the repository on the script import path; this local
proof harness correction changed no product code.

Actual Radon 6.0.1 removes all four blocking complexity findings. The unchanged
installed KISS metric removes both parameter-count and nesting errors. These local
metrics do not claim a supported native pass. Formatting, lint, targeted types and
whitespace checks passed. Capture's seven explicit parameters and assertion-heavy
scenarios retain disclosed nonblocking warnings rather than new configuration
objects or additional wrappers. Production behavior, analyzer configuration,
source/approval limits, test selection and native deadlines are unchanged.

The timeout investigation found no demonstrated current recovery under unchanged
limits. Existing reports do not retain the inner coverage output needed to identify
a particular failing or slow test. Native assurance remains incomplete until a fresh
full report on the corrected head passes. A required rerun after these legitimate
corrections is not claimed as a proven timeout remedy. Prior failure history and
all independent reviews remain preserved. No merge is authorized.
