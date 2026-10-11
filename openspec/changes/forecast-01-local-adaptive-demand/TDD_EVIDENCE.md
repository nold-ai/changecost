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
