# Major producer compatibility evidence

## Identity and scope

Change `provider-major-version-compatibility`, issue #52, branch
`codex/provider-major-version-compatibility`, unchanged HEAD/base
`7df8be778f7c4a40992a4c048c77b6599fe4859c`. Implementation authorized on
2026-10-31 Europe/Berlin. Original role estimate UNKNOWN. Sole implementation
writer owns the diff. Parent owns independent closure and the authorized selected-file
run. No private raw source, new model call, telemetry or collection was used here.
No commit, push, PR, merge or archive was performed.

The selected design preserves immutable baseline envelopes and historical identities.
Model the Domain puts complete actual producer data on events. Boundary Discipline
shares strict version parsing at source and portable boundaries. Laziness Protocol
keeps the existing profile and target identities instead of adding migrations.

## Existing-system proof and fixed legacy bytes

The parent's `baseline-probes.json` records four existing-system tests passing at
this base, exit 0, in 1.16 seconds. They cover Code refinement/recovery, Desktop CLI
recovery, Codex frozen retry and finite replay. This is baseline evidence only.

Before runtime source edits, the implementation owner executed
`PYTHONPATH=.:src .venv/bin/python /tmp/capture-major-legacy.py` using the unchanged
binary. Nine fixed synthetic data files are retained in
`tests/fixtures/provider_major_legacy`; `sha256.json` records their exact SHA256.
Code partial/final exports preserve original IDs, timestamps, producer, first
provenance and predecessor links. Desktop has a fixed export. Codex has a fixed SQL
dump, capture input and frozen forecast. The ignored workflow retains the capture
script. These bytes were not regenerated after runtime edits.

The first capture attempt used an unresolved macOS temporary path and safely failed
`unsafe_source`. Resolving that temporary path made the acquisition succeed without
changing product code. SQL `iterdump()` omits application/schema pragmas. Initial
Codex restore tests therefore failed `session_store_unrecognized`; those are setup
errors and not RED. Restore now adds literal application_id 0x43435331 and
user_version 3 from the actual baseline sessions.py. They were not captured earlier.
The fixed SQL bytes and original hash remain unchanged.

## Meaningful RED

On 2026-10-31 at 23:42 Europe/Berlin,
`.venv/bin/python -m pytest -q -n 0 tests/test_provider_major_versions.py`
ran against unchanged runtime behavior after the specs and tests were written.
The log is `.changecost/workflow/provider-major-version-compatibility/red.log`.
It reported 30 failed and 104 passed, exit 1. Twenty-eight failures establish
exact-version/alias rejection or Code present-entrypoint acceptance. Two Codex
restore failures are explicitly excluded from RED. The Code cases include
Desktop-marked root-terminal, partial and child after a valid event. Producer
projection/recovery positives were blocked at the old exact admission boundary,
so no independent projection-only RED is claimed.

A separate controlled RED loads the complete original counter reader module from
`git show 7df8be778f7c4a40992a4c048c77b6599fe4859c:src/changecost/codex_session_counter.py`,
with its own globals and dataclass registration, and wires the real public capture
path to that module. The command is
`PYTHONPATH=.:src .venv/bin/python .changecost/workflow/provider-major-version-compatibility/codex-full-baseline-red.py`.
At 23:45 Europe/Berlin it reported three expected failures for 0.163.1,
0.164.0-alpha.10.2 and 0.165.1+build.001. The fixed old store and replay succeeded
before new-version capture returned `unsupported_source_header`. A separate
negative control verified unchanged database and source bytes. This post-edit
re-execution uses exact baseline module bytes, not a pre-edit whole-tree run.
`codex-full-red-final.log` retains the actual output. The earlier header-only probe
is supplemental and not the principal Codex RED evidence.

## Focused GREEN and limits

The first compatibility-only GREEN was 134 passed. The affected-suite command was
`.venv/bin/python -m pytest -q -n 0 tests/test_provider_major_versions.py tests/test_claude_local.py tests/test_claude_desktop308.py tests/test_claude_admission.py tests/test_codex_provisional_sessions.py tests/test_codex_local.py`.
The intermediate run at 23:44 Europe/Berlin reported 573 passed in 5.24 seconds.
The final pre-HOLD bound run reported 574 passed in 5.49 seconds, exit 0, after
adding the fresh same-minor 0.163.1 patch case. Its log is focused-final.log.
The prior affected run had one old Desktop negative expecting another major-2
patch to reject. That control now uses major 3. Existing single-producer cohort
corruption tests remain unchanged. The focused BasedPyright command for changed
runtime/test files reported zero errors, warnings or notes. Strict native OpenSpec
validation reported the selected change valid.

The tests cover complete version syntax, bounded major digit-string comparison,
actual producer in four categories and Code stages, aliases before persistence,
exact replay/recovery, both-order version/profile conflicts, mixed-version distinct
events, safe atomic malformed versions, rehashed portable policy negatives including
non-version metadata, Code marker separation, fixed legacy exports, frozen Codex
forecasts, future cross-minor cohorts, true append and rewritten-header refusal.
Affected existing suites retain shape, quantity, six-category, decrease, identity,
finite modified/appended-byte and admission mutation controls.

Canonical session initialization used the actual helper schema with complete initial
scope hashes and planned absences. It created a new identity without resetting old
Claude #37 history. Defaults remain three batches and 90 active minutes. No measured
usage or historical success was invented. A pre-RED packet was captured. Intermediate
GREEN logs were diagnostic outputs before a refreshed binding and are not canonical
final assurance. Final bound focused checks and current content manifests are retained
in the ignored workflow handoff. Aggregate evidence remains incomplete.

## Native outcome and remaining obligations

The parent ran the existing authorized selected Desktop 2.1.309 session against
the frozen runtime after focused checks. The real CLI import succeeded with eight
category facts across four separate categories, all preserving engine_version
2.1.309. Exact replay inserted zero facts and preserved records, observations and
sequence. Portable export/recovery and replay passed. No demand or economic records
were created. The original forecast remains UNKNOWN. No total, billing, native
completeness or calibrated accuracy claim follows. The parent retains the private
selection and safe local proof; none of its path, UUID, source hash, quantities or
portable bundle is copied here. No new model call or source activation occurred.
This establishes the selected Desktop shape only. Native Code baseline entrypoint
absence remains unverified by public evidence.
No new observed-release proof, profile or approval is created by this policy.

Parent independent affected-obligation closure, aggregate supported-Linux/Python
matrix and native SpecFact assurance,
risk-selected Codex/CodeRabbit reviews and PR publication remain pending. This
macOS implementation stage does not waive unsupported native checks or historical
gaps. Historical archives, original #17/#40 tasks and TDD remain unchanged.

## Rollback and risks

Exact producer retention prevents baseline substitution. Code marker absence and
Desktop root-terminal checks prevent the known family crossover. Fixed records and
unchanged Codex TARGET prevent historical rewrites and accidental cohort splitting.
Same-major future format changes can still reject safely. Declarations cannot
authenticate a deliberately forged producer. Compatible major 0 intentionally spans
minors under the existing provisional measurement contract.

No dependency, schema migration or product version bump is needed. Time estimate
remains UNKNOWN and no paid calls were made. Keep a pre-change store backup and
updated-reader access for newly admitted versions. An older binary may reject new
records. Never erase accepted facts or frozen forecasts to downgrade.


## Documentation reconciliation and tools

The parent authorized current CLI/contracts documentation updates and existing
content-bound rationale refreshes for unchanged contributor/gate policy and immutable
historical snapshots. The canonical session records that scope extension. This does
not change gate code, thresholds, requirements or historical archive bytes. The old
Desktop guide anchor is retained. Generated index/help text uses the real selectors.

Executed tools report Python 3.13.14, Ruff 0.16.9, BasedPyright 1.40.1 with Pyright
1.1.414, and OpenSpec 1.15.0. This version report describes execution, not an upgrade
of repository requirements. Final current documentation checks are recorded in the
ignored implementation handoff. No aggregate/native run was used to end this stage.


Final document reconciliation passed `python -m quality docs` with the explicit
base and intended-file manifest. Index and metadata checks passed. Full existing
hygiene initially failed under restricted access to the global cache and protected
`.agents` paths. A task-local copy of the exact pinned official hook repository
removed network/cache dependency; focused hooks passed. The supported escalated
full hygiene run then exited zero with all eight hooks passing. No hook configuration,
gate implementation or protected `.agents` content changed. Fixed legacy asset
hashes, canonical profiles, packaged approvals, finite reader, all archives, main
specs and original #17/#40 artifacts remained unchanged. Runtime, test and generator
bytes remained identical to the bound pre-native focused state.

Final verification evidence is limited to the implemented slice. The canonical
session remains incomplete until independent closure and aggregate/native/provider
assurance complete. No passing local check is represented as full acceptance.
