# Native session observation implementation evidence

Local implementation on 2026-10-25 Europe/Berlin. Branch `codex/local-session-dogfood`, base/HEAD `de2c42bd1d303dd4cfd080d3effa9f8d77cd59da`. Parent owns freshness, review ledger and independent acceptance. Existing manual-session edits and prior TDD histories are preserved. No commit, push, merge or release was performed.

## Scope and critical assumptions

Runnable outcome: `changecost session observe-codex SESSION_ID --file SELECTED_FILE --repository-id REPO` attaches only safe partial diagnostics from the existing exact approved mapping beside an unchanged manual forecast. The packaged selector grants no new admission. Native session totals/errors stay unknown and native learning remains excluded. This does not fulfill arbitrary ongoing session totals or learning.

One canonical reader result shares acquisition, strict parse, exact source/producer/projection checks and safe fact projection with the existing core importer. Sessions owns one database transaction, one source snapshot and explicit immutable links. Pending core record templates remain private. Native quantities use safe JSON, including 4096-digit integers, rather than SQLite INTEGER.

Projection drift and migration damage are the critical assumptions. Existing native tests cover core receipt/serialization/replay/first provenance. New authored fixtures cover native privacy/authority, v1 read-only preservation, migration rollback, conflicts and concurrent migration. Parent reports actual approved-source preflight of 16 requests/96 facts; that report is not independent implementation proof. Parent will demonstrate the real selected source after source freeze.

## Actual red and green

- Initial test harness collection failed because the authored fixture import omitted the `tests` package. Corrected before implementation. This is not behavior-red evidence.
- 2026-10-25T20:56:00+01:00. `.venv/bin/python -m pytest -q tests/test_codex_session_observations.py` exited 1. The existing app imported and start succeeded; invoking the missing `session observe-codex` exited 2 instead of 0. One assertion failed. Raw output is ignored `.changecost/codex-dogfood/native-red.txt`.
- 2026-10-25T20:56:38+01:00. `.venv/bin/python -m pytest -q tests/test_codex_session_observations.py tests/test_sessions_cli.py tests/test_codex_local.py tests/test_native_usage.py` exited 0, 96 passed. Raw output is ignored `.changecost/codex-dogfood/native-first-green.txt`.
- 2026-10-25T20:57:33+01:00. The expanded bridge-only suite exited 0, 27 passed. Authored positives substitute packaged admission only inside tests and are not native approval. Raw output is ignored `.changecost/codex-dogfood/native-focused.txt`.

The expanded cases cover exact replay without writes/events, one source linked twice without duplicated facts, unchanged frozen estimates, native-only exclusion, independent manual-total/error/learning coexistence, changed/unsafe sources without migration, missing/unfamiliar stores, populated-v1 read-only/manual compatibility, complete rollback after migration/attachment failure, repository/provenance/source/semantic conflicts, saved reports without source access, source privacy and concurrent attachment/replay.

## Analyzer evidence and limits

Python 3.13.14 locally. Scoped BasedPyright exited 0 with no errors or warnings after the first expanded suite. Scoped Ruff check and format passed after formatting. Actual Radon 6.0.1 `radon.complexity.cc_visit` ran from its existing cached package. All new/changed runtime functions and new tests are at most complexity 10. Existing untouched reader helpers retain complexity 14/13/11 and untouched CLI helpers retain 12/11; these are not represented as passing the whole-file threshold. Raw result is ignored `.changecost/codex-dogfood/native-radon.txt`. A direct Radon CLI launch failed because its cached CLI dependency `mando` is absent; the actual library analyzer ran successfully. No review-tool repair or dependency change was made.

## Remaining assurance and rollback

Final scoped check outcomes are appended below. Supported Linux/Python matrix, aggregate gates, required native/provider review and maintainer acceptance remain pending. No full native capsule, full make check, CI or publication completion is claimed. Prior manual/reader review histories and limitations remain unchanged.

Back up SQLite with no writer before the first native attachment. Reads/manual writes retain v1; accepted attachment migrates transactionally to v2. An old binary refuses v2. Rollback after migration requires restoring the pre-upgrade backup, losing later observations. Removing the command alone does not revert schema. Normal local SQLite filesystem semantics only; no new power-loss or network filesystem guarantee. No paid calls.

## Final scoped checks, 2026-10-25T21:01:40+01:00

- `.venv/bin/python -m pytest -q tests/test_codex_session_observations.py tests/test_sessions_cli.py tests/test_codex_local.py tests/test_native_usage.py tests/test_cli.py tests/test_presentation.py tests/test_repository_gates.py` completed with 325 passed and 4 failed. All four failures were installed console-script lookup assertions because `.venv/bin` was absent from inherited PATH. No behavior failure was reported in the other 325 tests. Raw output is ignored `.changecost/codex-dogfood/native-green.txt`, retaining its actual failed exit.
- With `PATH="$PWD/.venv/bin:$PATH"`, reran only `tests/test_cli.py::CliContract::test_installed_economic_roundtrip`, `test_installed_portable_roundtrip`, `test_installed_quote_roundtrip` and `test_offline_read_only_entrypoint` using the same module prefix. Exit 0, 4 passed and 4 subtests passed. Raw output is ignored `.changecost/codex-dogfood/native-cli-path-retry.txt`. This is an invocation correction, not a source/test or analyzer change. The whole scoped command was not relabeled as a single passing run.
- Scoped `ruff check` passed, `ruff format --check` found all four files formatted, and `basedpyright` reported 0 errors, 0 warnings, 0 notes. Scope was `src/changecost/{codex_local,sessions,cli}.py` and `tests/test_codex_session_observations.py`.
- `make generate`, `python -m quality docs --base HEAD --manifest .changecost/codex-dogfood/native-manifest.txt` and the corresponding `quality index` passed. Generated commands and llms inventory use the existing renderer. Source-bound rationales preserve unchanged core/contributor/historical prose and do not waive assurance.
- `OPENSPEC_TELEMETRY=0 openspec validate dogfood-02-codex-observations --strict --no-interactive` passed.

No prior manual-session spec or TDD history was rewritten. Parent retains sole review-ledger ownership and will run actual-source acceptance and independent boundary review after this handoff. Confidence is high for local fixture behavior and source-boundary reuse, and medium for broader acceptance pending those proofs and supported-platform assurance.


## Actual-source proof and local review closure, 2026-10-25T21:05:45+01:00

The parent ran the installed CLI with the packaged admission against the existing
approved private local source. This was not a synthetic-admission substitution.
The isolated store captured 16 requests and 96 independent category facts, preserving
the exact source/profile/projection digests, unknown coverage/finality labels and
original forecast. No session total, total error, manual measurement or native
learning sample was created. The next comparable session had no forecast and zero
samples. Two explicit session links shared one stored snapshot. Exact retry left
all database bytes and event counts unchanged. A temporary modified copy was
rejected as `unadmitted_source` without changing database bytes; that copy was
removed. The original source bytes were unchanged and no core store was created.
Safe receipts are ignored `.changecost/codex-dogfood/actual-native-01/proof.json`
and `transcript.json`. Source text and private paths are absent from these receipts.

Independent affected-scope review by gpt-6-astra found no findings against all 19
frozen path hashes. It independently ran 59 bridge/manual tests and 63 existing
reader/native-usage tests, with 122 passing in total. It did not read the private
source and did not claim full Linux/provider/PR assurance. Independent comment
review by gpt-6.1-sol also found no findings or needed suppressions. Reports are
retained locally in `.changecost/codex-dogfood/review/` with their original scope.
The source-freeze manifest remains the original reviewed snapshot; this appended
evidence and task checkbox update occurred afterward and changed no runtime code.

Local implementation and actual-source demonstration are complete. General new or
appended local sessions remain unadmitted, and predictive accuracy remains
unmeasured. Linux/Python, required provider reviews and acceptance remain pending.
No commit, push, merge, publication or release was performed for this bridge.
