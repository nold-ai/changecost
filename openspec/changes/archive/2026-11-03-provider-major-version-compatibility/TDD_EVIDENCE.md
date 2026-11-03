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

## Task 4.3 completed before archival, 2026-11-03 Europe/Berlin

This dated record supersedes the earlier pending-assurance statements for the
accepted implementation. It does not rewrite their original observations or
create missing historical RED evidence. The maintainer requested actual completion
of task 4.3 before native CLI archival and a delivery PR.

[PR #53](https://github.com/nold-ai/changecost/pull/53) merged at
`584ed7a17e4222610608440171de1f0774399dee` on 2026-11-03 at 21:24:38
Europe/Berlin. Its final source `71f0828ad4793f39b5430016ca42b1cc3f8b50c7`
has the identical tree `3be93f23e250a764e1019ca59db4c1ca63d4d0c3`.
The final comparison base is `3a6acb4574047edcd6c9aaadc24c6143e49829c0`.
The integration changed five documentation files relative to the original
reviewed implementation; runtime, tests and quality code remained byte-identical.
Independent affected closure inspected the final documentation resolution and
returned no findings. Its 177 compatibility tests and staged contract, hygiene,
documentation, generated-reference and metadata checks passed before publication.

### Supported host and native report readback

[Run 41710744495](https://github.com/nold-ai/changecost/actions/runs/41710744495)
passed both supported Ubuntu jobs, Python 3.11.15 and 3.13.14, for the exact final
source. An independent audit downloaded both actual reports and run logs rather
than accepting the green summary alone. Each host passed 4,063 tests and five
installed-package checks. All thirteen aggregate leaves ran; dependency audit was
explicitly inapplicable because locked audit inputs were unchanged.

Both native reports concluded PASS_WITH_ADVISORY with assurance PASS, exit 0,
unknown-required-evidence false and all ten required members ran/PASS. The existing
evidence validator returned no errors. Both sidecars match the independently
recomputed 352-file source digest
`aa1866cdb3032cba22990cf558e7ce5123f04624fd717677da07e0b8c5a9d348`.

| Python host | Final native report SHA256 |
| --- | --- |
| 3.11.15 | `1396e8ab44cad198d60b922874686539d8234523b49dae4a7c5cc6562b5a9a17` |
| 3.13.14 | `889510f2e43c84ef454c222eadc14b0b137a560509a2bfe170d648e224b7213c` |

Each report retains 3,797 nonblocking advisories. The independent audit verified
every finding field and prior per-occurrence disposition, including report/index
and source-context hashes. All 88 containing source files are byte-identical to
the original reviewed implementation. The corresponding earlier disposition
files have SHA256 `4ed906071fe7a47a23e7f89ca1f4b1024ea9dbfec30020342bf953bedd99b4b9`
for Python 3.11 and `4f1b3745cf3861aed9a74dd06e075729d736aa774342646d705a2f0b5fe69dd0`
for Python 3.13. Their applicability to the new report hashes was established by
that exact comparison, not inferred from finding counts.

### Final-source provider reviews

The [Codex code-review summary](https://github.com/nold-ai/changecost/pull/53#issuecomment-6550540522)
binds the full final source SHA and records completion at 21:15:50 Europe/Berlin
with no findings or unresolved findings. This is code review, distinct from the
older security-review metadata.

The hosted CodeRabbit check remained SKIPPED after the documentation integration.
One [incremental request](https://github.com/nold-ai/changecost/pull/53#issuecomment-6614694727)
on the merged PR did not start a visible review. The missing source review was
therefore completed using the existing authenticated CodeRabbit CLI 0.9.2 in a
clean detached checkout of the exact final source. No paid override, account
setting change or duplicate running review was introduced.

```sh
/Users/dom/.local/bin/coderabbit review --agent --committed --base-commit 3a6acb4574047edcd6c9aaadc24c6143e49829c0
```

The run started at 21:31:26 and completed by 21:36:16 Europe/Berlin. Exit was 0;
the final event was `type: complete`, `status: review_completed`,
`outcome: completed`, with zero findings. Its 43 reviewed paths exactly equal the
final PR diff. The raw NDJSON SHA256 is
`4888ab949e4aea9535780b284e9453c6999338059aa5ef23bae64911d8585eda`.
The checkout remained clean and on the bound source throughout. This is an actual
CLI provider review, not a claimed hosted review or a fabricated check status.

The source reports, execution facts and independent audit are retained in ignored
`.changecost/workflow/provider-major-version-compatibility-closeout/`. The existing
review session and its original counters/history remain preserved; its historical
COMPLETE result is not rebound to a later stage without the supported transition.

The later [supported full-review request](https://github.com/nold-ai/changecost/pull/53#issuecomment-6615010777)
was explicitly [refused because the PR is closed](https://github.com/nold-ai/changecost/pull/53#issuecomment-6615013346).
Its hosted check concluded CANCELLED; the earlier SKIPPED check remains historical.
The existing ledger's supported merged-stage retirement rejected the source
check state without changing its binding or counters. Its historical receipt is
preserved at revision 23 after the approved scope decision, with zero correction
batches and the original measured time. No fresh session, fabricated provider
completion or passing retirement is claimed. The archival delivery PR can collect
its own actual checks/reviews, but these cannot retrospectively change the closed
source PR's hosted outcome. This administrative acceptance limitation remains
explicit and is not a runtime or review-tool repair in this change.

Task 4.3 is now complete. This assurance covers the accepted implementation and
its final documentation integration. The archival delivery has its own changed
specification/documentation scope and requires current-head checks and reviews.
Native Code entrypoint absence remains unverified beyond the recorded grammar
controls; no new source approval, demand, billing or calibration authority follows.

### Strict archival tooling

The repository pins OpenSpec 1.13.2 in contributor setup and CI. The installed
global 1.15.0 preflight failed thirteen existing items because long-requirement
information became strict warnings. No specification was rewritten to satisfy a
different tool version. The pinned 1.13.2 strict preflight passed all 19 items,
including this change. Archival uses the pinned CLI with normal validation and
spec synchronization, followed by exact requirement/scenario readback and all-item
strict validation. Rollback reverts the eventual archive/documentation commit as
a unit while preserving source records, original evidence and review history.
