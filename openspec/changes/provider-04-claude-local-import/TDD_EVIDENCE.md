# Claude project reader implementation evidence

## Synthetic tests before runtime, 2026-10-28 Europe/Berlin

The parent authorized focused synthetic test drafting while exact profile approval
remains pending. No runtime, source admission, portable graph or canonical register
code changed. All ten existing implementation tasks remain unchecked. The original
forecast for `claude37/implement/reader-owner-2` is UNKNOWN, recorded before
substantive review in ignored workflow history. No later estimate replaces it.

The input is authored project JSONL with the observed repeated-block and retained
partial-to-terminal relationships. All quantities and identities are synthetic.
Tests exercise the intended `import_claude_project` API and explicit CLI mode,
immutable four-category stage refinement, accepted-stage replay and recovery,
normalized supported terminal reasons, strict identity/producer/quantity rules,
whole-batch rejection, cache exclusions, manual binding and acquisition/privacy
bounds. The fixture substitutes an admission envelope for unit testing. It grants
no native approval. Unknown noncontributing row types are not guessed or tested.

This worktree has its own `.venv`, created by
`UV_PYTHON=/Users/dom/.local/bin/python3.13 uv sync --locked --offline`. It uses
Python 3.13.14 and the unchanged lockfile. Existing native roundtrip and finite
Codex replay controls both pass, establishing a working focused test environment.
They do not verify new Claude behavior or supported-host aggregate assurance.

`tests/test_claude_local.py` collects 48 cases. Ruff formatting/lint and scoped
BasedPyright pass. The frozen draft test file SHA-256 is
`36ab03ccf2b04ae6a1bf91de93ebf5d99cfba5f99324fb8df8a1e72b81df7b35`.

| Check | Time, Europe/Berlin | Exit | Actual result |
| --- | --- | ---: | --- |
| `.venv/bin/python -m pytest -n 0 tests/test_native_usage.py::test_old_bundle_still_reads tests/test_codex_local.py::test_finite_replay_and_private_projection -q` | 2026-10-28T01:49:50.051711+01:00 to 2026-10-28T01:49:50.807819+01:00 | 0 | Two existing controls pass. |
| `.venv/bin/python -m pytest -n 0 tests/test_claude_local.py::test_partial_refinement_both_replays_and_actual_recovery -q` | 2026-10-28T01:49:50.808111+01:00 to 2026-10-28T01:49:50.962298+01:00 | 1 | Expected missing behavior: `ModuleNotFoundError: No module named 'changecost.claude_local'`. This is a setup failure for the missing product module; the detailed new scenarios have not executed. |
| `.venv/bin/python -m pytest -n 0 tests/test_claude_local.py::test_cli_help_exposes_selected_claude_project_mode -q` | 2026-10-28T01:49:50.962602+01:00 to 2026-10-28T01:49:51.213408+01:00 | 1 | Expected CLI assertion mismatch: successful settle help does not contain `--import-claude-project`. |

Exact command/timestamp/exit-code records and complete logs are in ignored
`.changecost/workflow/provider-04-claude-local-import/reader-owner-2-red-results.json`
and its named log files. No passing-after evidence exists yet. The missing-module
RED establishes the absent reader entry point only. It does not independently
prove each future accounting assertion would catch a defect. Those cases require
execution and green evidence after implementation.

Candidate 2, both public evidence artifacts and the four original planning files
remain frozen for independent review. Native policy approval and parent GO still
precede dependent runtime work. No aggregate `make check`, native assurance suite,
commit, push, PR, merge, release, live collection or provider call occurred.
Rollback removes only owned uncommitted test/implementation additions while
preserving source proof, frozen candidates, original forecasts and the PR #50
review-session history and allowance.

## Reader completion, 2026-10-28 Europe/Berlin

The maintainer explicitly approved exact candidate-4 activation and completion/testing
of the reader. Fresh escalation accepted the activation command. The prior denial,
blocked handoff and original UNKNOWN forecasts remain preserved. This owner's original
forecast is also UNKNOWN, recorded before substantive edits. Main was fetched and
read back as `c424eb8ac67b51af087dbe71a1516a24281c90a1`; this separate branch remains
at `83449d93f8439fa6604c1fb65c0bdb5f273b7261` with uncommitted implementation.

The exact r4 profile digest is
`b79d44303e6b73075ea8f1ca2d8d26bc8153e8a19d39f0766b63b2c4aaafd16c`.
Independent approval came from `claude37/implement/exact-profile-4-delta-review`.
Its frozen attestation file SHA-256 is
`56255c8b8016539087620a6d9a66e3b3a0073366d995cf052fc98ac5c1739baa`.
The packaged canonical approval digest is
`18b331902d03497bdbd3503f092d59b4644ac7110868a227e73d4e68530979a5`.
The exact reviewed candidate and previous r3 register/package are preserved in
ignored `canonical-candidate-4/reviewed-snapshot`. Original 24 profile objects and
the finite Codex package remain unchanged. No private source was reinspected.

### Actual focused evidence

Logs below are relative to ignored
`.changecost/workflow/provider-04-claude-local-import/`. They retain failures as well
as passing results. Counts are overlapping runs and must not be added together.
The final command timestamps and exit codes are in `owner3-final-checks.json`.

| Check | Actual result | Log |
| --- | --- | --- |
| Initial combined A+B test before persistence implementation | One expected failure at `_persist` with `NotImplementedError`; this test reached the absent behavior. | `owner3-combined-red.log` |
| First full Claude runtime/admission run | 69 runtime cases passed; one obsolete expected reviewer-name assertion failed after exact r4 activation. Updated it to the actual independent reviewer. | `owner3-green-1.log` |
| Portable provider corruption | Actual `DID NOT RAISE` on Claude Evidence relabeled as Codex. Fixed Claude validation selection for project surface and required Claude provider. | `owner3-green-2.log` |
| Coherent provider/surface corruption variant | Initial test rejected on an unrelated observation reference; a fixture-edit attempt then had `KeyError`. After repairing all references, actual `DID NOT RAISE` reproduced the bypass. Reserved r4 mapping now also selects Claude validation. | `owner3-provider-variant-red.log`, `owner3-provider-variant-red-2.log`, `owner3-provider-variant-red-3.log` |
| Final six-suite focused regression run | 889 passed on Python 3.13.14. Claude runtime/admission plus existing source-admission, source-feasibility, finite Codex and NativeUsage suites. | `owner3-final-focused-regressions.log` |
| Scoped Ruff and format | All checks passed; ten touched Python files formatted. | `owner3-final-lint.log`, `owner3-final-format.log` |
| Scoped BasedPyright | Zero errors, warnings or notes on those ten files. | `owner3-final-types.log` |
| Selected strict OpenSpec | Passed. | `owner3-final-openspec.log` |

The four-state history reducer preserves accepted partial, terminal-only and refined
histories. Tests exercise initial combined A+B and equal-quantity A+B after reopen
and actual bundle recovery, retained-A advancement, A/B replay, strict unseen-partial
rejection with otherwise valid new events, coherent provider forgery, category/cohort,
first provenance, stale predecessor, fork, cycle and backdated-history rejection.
The portable model and serializer were not changed.

### Runnable product proof

`owner3-cli-demo-2/receipts.json` records actual subprocess `.venv/bin/changecost`
commands using the canonical packaged profile, not the unit-test monkeypatch.
Sources are authored synthetic project JSONL with the approved relationships.
A first attempt omitted required `isSidechain` and correctly rejected with
`invalid_source_lineage`; `owner3-cli-demo.log` preserves that failed input attempt.
The corrected source imported A, refined with A+B, then replayed A, B and A+B.
The first two calls each inserted four NativeUsage records, and the second reported
four corrections. All later calls inserted zero and replayed four categories.
The store contains eight history records and one stable Evidence reference. Export
and import into a new Store preserved every record. Source files and receipts remain
in `owner3-cli-demo-2`, with `owner3-cli-demo-2.log` retaining output. No collection,
provider API, paid model invocation or native billing/demand claim occurred.

### Limits and rollback

This implementation stage ran focused checks only. Aggregate make check, full
supported-Linux/SpecFact assurance, provider review and final independent affected
review remain pending. Earlier missing-module RED proves only absent entrypoints;
it is not retrospective failing evidence for every detailed assertion. Compound
historical TDD/review/publication tasks remain unchecked where their full criteria
are incomplete. Docs/index checks and final frozen manifest are recorded in the
owner handoff. The first index invocation lacked its required base and rejected;
whitespace checking also reported extra EOF lines, subsequently removed.

Rollback preserves exported bundles, source evidence, approvals, original forecasts
and PR #50's review ledger. Remove only this branch's owned uncommitted changes
when deliberately abandoning the reader. Do not load new Claude records into an
older binary and assume compatibility. No aggregate or archive acceptance follows
from focused green evidence.

## Independent final review correction, 2026-10-28 Europe/Berlin

Independent code review found two P2 defects in the frozen implementation. Retaining
the recognized Claude profile or admission digests while coherently renaming provider,
surface and mapping could evade exact Claude validation. Separately, a portable
bundle could coherently rename its Evidence ID and import successfully, although
identical reader replay would then fail. Documentation review also found stale current
README claims of 24 profiles and only one usage approval.

The first defect escaped the earlier provider/surface/mapping repairs. Before this
batch, the owner explicitly replanned the entire dispatch invariant in the ignored
implementation todo. One recognizer now treats each recognized packaged Claude claim
as sufficient to require full exact association validation. Its finite test matrix
retains provider, Evidence surface, producer surface, mapping, profile ID, profile
digest and approval digest independently, coherently changing all other claims and
rehashing records plus predecessor/observation references. Entirely new claims do not
authenticate Claude provenance. Existing finite Codex behavior remains unchanged.

The new eight-case run before the patch produced five failures and three passes.
Profile ID, profile digest, approval digest and Evidence alias cases reached actual
`DID NOT RAISE` failures. Evidence-surface-only already rejected through generic
association validation, but failed the expected exact Claude diagnostic. This is
not claimed as an accepted malformed bundle. The other recognized claims already
selected exact validation. `owner3-review-batch-red.log` preserves these distinctions.
After the patch all eight cases passed in `owner3-review-batch-green.log`.

Evidence aliases now reject at the Claude graph boundary because the canonical writer
uses event identity as Evidence ID. This preserves the approved identity contract
without adding an alternate replay-resolution policy. The alias test coherently
updates every Evidence reference and observation, asserts atomic rejection with no
database, and verifies original-store replay preserves exact references and records.
The README current inventory now states 25 profiles and two usage approvals, while
dated historical checkpoints remain unchanged.

This was a family-wide invariant replan, not a fresh review allowance or PR #50
ledger reset. Further escapes after this replan require renewed scope judgment.
The final corrected focused run passed 897 cases across the same six suites.
Scoped Ruff, format and BasedPyright passed, selected strict OpenSpec passed, and
explicit-base docs/index plus diff whitespace checks passed. These overlapping
runs do not add to earlier test counts. Final corrected logs and timestamps use
the `owner3-review-` prefix.
Parent-coordinated independent affected closure remains pending at this checkpoint.

## Desktop 2.1.308 additive implementation, 2026-10-28 Europe/Berlin

Independent q3 approval binds profile digest
`d942dcb33a80294a7f25d4d4c9f31523e1e5338b02e84efd715a32aaa86f1708`.
The original candidate and bound statements were frozen before appending approval.
The original 25 profile objects, 2.1.215 admission bytes, finite Codex reader/asset,
NativeUsage model and serializer are unchanged. The register now has 26 profiles
and three usage approvals. The frozen public statements retain draft wording as
historical review inputs; canonical approval records the current status.

Specs preceded the new Desktop test. `.venv/bin/python -m pytest
 tests/test_claude_desktop308.py -n 0 -q` failed with `unsupported_profile` before
activation or reader changes, one expected failure. This proves the missing public
import capability. Rejection matrix tests were subsequently authored before the
Desktop runtime changes, but their individual missing-behavior RED was not captured.
Passing rejection tests do not retroactively supply that historical RED evidence.

The first focused run had 980 passes and eight failures. The new CLI fixture used
`--store` instead of `--db`, two assertions compared time-stamped Bundle exports,
and the source matrix still needed regeneration. These were test/development
integration corrections. The second run had 1,011 passes and one fixture failure;
its reason-only forged record was rejected by Pydantic before the intended graph
check. The fixture now carries predecessor and reason. No correction batch or
production defect finding is inferred from expected development failures.

The focused passing command was:

```sh
.venv/bin/python -m pytest tests/test_claude_desktop308.py tests/test_claude_local.py tests/test_claude_admission.py tests/test_source_admission.py tests/test_source_feasibility.py tests/test_codex_local.py tests/test_codex_session_observations.py tests/test_codex_provisional_sessions.py -n 0 -q
```

It passed 1,090 tests with exit 0. Actual run start was `2026-10-28T22:17:21.797599+00:00` and
finish was `2026-10-28T22:17:27.278522+00:00`. Logs and the pre-execution binding are in the ignored
`desktop308-implementation/reader-owner/green3` artifacts. This is focused evidence,
not full aggregate or supported-Linux native assurance.

Checks cover root terminal import, literal zero and separate categories, strict
missing/null/bool/negative rejection, closed per-type metadata and opaque API blobs,
producer/lineage/stage refusal, same-event conflicts in both profile import orders,
first provenance after reopen and actual bundle recovery, each of seven retained
association claims for each profile, borrowed proof, canonical Evidence identity,
forged Desktop stages/predecessors, and atomic commit failure with a repaired retry.
The existing 2.1.215 refinement/correction/replay tests and Codex suites still pass.
Catalogue resources remain private and freshly loaded; there is no shared mutable
cache or new public reader API. The fixed resource variants select their own policy.

The real installed command used `UV_PYTHON=/Users/dom/.local/bin/python3.13
UV_OFFLINE=1 uv run --locked changecost --db ... settle --repository-id repo
--import-claude-project ... --source-profile claude-desktop-2-1-308-root-terminal
--source-sha256 ...`. An authored fixture inserted four facts, then replayed four
with no additions. A sandbox cache denial was resolved through approved escalation.
No paid call or producer process ran. Private arguments and receipts stay ignored.

The explicitly selected existing transcript had changed since the frozen source
capture. Its current hash was recorded only in a separate private binding with an
explicit verification revision reason. The original capture remains immutable.
The current-file CLI refused `unsupported_source_shape` at ordinal 163 and wrote no
store. No new-row payload was inspected and no grammar was broadened. Therefore
current-file native success is NOT established. The reusable approved shape is
implemented; additional live-file shapes require their own source adjudication.

Scoped Ruff and BasedPyright checks, selected strict OpenSpec validation and all
intended-file hygiene hooks passed during implementation. Final frozen leaf reports
are retained by the stage owner. Whole-repository aggregate checks, independent
code/docs closure, hosted native/matrix assurance and publication remain pending.
All #17 obligations and previous archive exceptions are unchanged.

Historical uninstrumented implementation/source work remains UNKNOWN. Only measured
prospective intervals are appended to the recovered existing review ledger; its PR
binding, original events and counters are retained. Expected RED is no defect batch.
Rollback reverts the additive Desktop change while preserving source proofs and
exported store bundles. Older binaries may reject Desktop-associated records.

## Collected correction batch 2 and q4 source extension

Independent q3 code review found one P2 defect, recorded as
`desktop308-depth-encoding-bypass` in family `claude-acquisition-depth-encoding`.
The raw-byte depth scanner and json.loads byte auto-detection interpreted different
character streams. Escaped quotes let UTF-16/32 nested payloads bypass depth 32.
The fix decodes each byte-delimited line with `utf-8-sig` before JSON parsing.
Byte `splitlines` remains unchanged, preserving U+2028/U+0085 inside valid strings.
An optional UTF-8 BOM remains a compatibility extension; no strict JSON Lines
conformance claim is made. UTF-16/32 and malformed UTF-8 are unsupported.

Specs and the encoding matrix preceded the fix. The command below failed with
32 accepted unsupported-encoding cases and passed eight UTF-8 controls before
implementation. Both Claude profiles, both byte orders, BOM/no-BOM, shallow/deep
payloads and escaped quotes are represented.

```sh
.venv/bin/python -m pytest tests/test_claude_desktop308.py -k 'wire_encodings or unicode_line_characters' -n 0 -q
```

RED began `2026-10-28T22:33:05.691186+00:00` and ended `2026-10-28T22:33:06.103272+00:00`, exit 1.
After the one-line fix, both reader files passed 264 tests. Scoped Ruff and
BasedPyright passed. The independent reviewer must still adjudicate closure;
implementation has not marked the finding fixed or reset its history.

Independent q4 source approval binds profile digest
`7e3cf00757e1eca8c91782848c59913a9e19bb39b78c7a15edf7be370b906b55` and
mapping `claude-desktop-root-terminal-r2`. Approval file SHA-256 is
`76794b6c09e818bbc97af983af3e10ab0c7a83232c15e07a6f63142182bcb6a5`.
The exact ten-entry candidate manifest and independent report hashes were checked
before activation. The original q3 candidate, canonical profile, asset, approval,
public statement bytes, implementation snapshot and disposable stores remain
frozen locally. The unpublished Desktop entry alone was replaced. The original
25 profiles, 2.1.215 asset, finite Codex reader/asset and NativeUsage serialization
remain unchanged. No q3 prototype-bundle compatibility is promised.

The q4 delta excludes only closed cost-state and mode metadata. All contributor,
integer, root, lifecycle, replay and cross-profile conflict rules are unchanged.
Two new positive metadata tests failed with unsupported_source_shape before
activation, then passed. The expanded metadata matrix rejects extra keys and
present-null direct usage/message. Opaque modelUsage, cost and mode values create
no facts or economic/demand authority. This approved source extension is distinct
from the encoding defect and does not invent another runtime finding.

The same eight-file focused command documented above passed **1,140 tests**, exit 0,
from `2026-10-28T22:34:28.619149+00:00` to `2026-10-28T22:34:34.147586+00:00`. Counts overlap prior runs
and are not cumulative. The pre-check binding and exact command/log are retained
in `reader-owner/batch2-q4-green` ignored artifacts.

The real installed CLI, with the same offline Python 3.13 uv invocation, imported
an authored fixture as four facts and replayed four without additions. It then
imported the explicitly selected existing Desktop transcript as 40 facts across
ten events and replayed all 40 without additions. The current source hash matched
the independently approved q4 capture binding. This closes the earlier q3 current-file
refusal for that observed capture, without claiming future shapes or full-session
coverage. The original native file was not changed. No producer process, paid call,
telemetry, unrelated source inspection or new collection ran.

Real q4 native facts exist only in the ignored disposable verification store
`reader-owner/q4-cli/selected-existing.db`. No real q3 native facts were created.
Private native paths, hashes, identities and quantities remain ignored. Final
code/docs review and aggregate/native assurance remain owned by verification.
#17 obligations, archived exceptions, two accumulated correction batches and the
existing PR binding remain intact. Only prospective measured active time is added.

## CI failure repair on 2026-10-29 Europe/Berlin

Supported-Linux run 40782816882 at `10dac19988427d7354bd25acc1a3ffd240439f4f`
failed the ordinary help assertion on both Python 3.11.15 and 3.13.14 hosts.
Each native report ran all ten required analyzers, with nine passing and Radon
failing. Neither native report had UNKNOWN required evidence. These failures
remain historical failures; the local checks below do not replace Linux assurance.

The help failure reproduced before editing with this command, exit 1 and one
failed test. Help itself exited zero. The complete option literal was absent
from raw ANSI-styled output and present after `Text.from_ansi(output).plain`.

```sh
UV_PYTHON=/Users/dom/.local/bin/python3.13 UV_OFFLINE=1 FORCE_COLOR=1 \
TERM=xterm-256color COLUMNS=160 uv run --locked pytest -q \
tests/test_claude_local.py::test_cli_help_exposes_selected_claude_project_mode
```

The assertion now normalizes ANSI presentation and still requires the complete
`--import-claude-project` option. The same command passed one test after editing.
A second invocation with `NO_COLOR=1 TERM=dumb COLUMNS=160` also passed one test.
No product option, CLI parser or help text changed.

The five blocking native findings were cyclomatic complexity 20 in `_contributor`,
24 in `_claude_record_valid`, 16 in `_claude_cohorts`, 28 in the lifecycle/recovery
test, and eight nested control-flow levels in `_corrupt_history`. Cohesive helpers
now separate source lineage and observation grammar, exact admission association,
diagnostic meaning, lifecycle policy, cohort availability and refinement links.
Test helpers preserve provenance, replay and diagnostic assertions. Independent
terminating fault branches retain every corruption case and relationship rehash.
The test file retains all 74 assertions.

A local cached Radon 6.0.1 probe reproduced those four complexity measurements
before editing and measured 6, 6, 8 and 11 afterward. The installed review module's
unchanged AST nesting functions measured the fixture dispatch at three levels
afterward. No new helper exceeds complexity 12. This scoped metric proof does
not claim execution of the supported-Linux native aggregate. Thresholds,
suppressions, tool policy, source admissions and public APIs remain unchanged.

The eight-file Claude/Codex reader, admission and native-usage regression command
passed 509 tests. The complete local suite, using the forced-color environment
above and `uv run --locked pytest -q`, passed 3,875 tests and four subtests in
31.09 seconds on Python 3.13.14 with four workers. Counts overlap and are not
cumulative. Scoped Ruff check/format and BasedPyright passed. Exact commands,
logs, metric script and hashes are saved in the ignored `ci-fix-owner` directory.
Final local leaves, independent closure, supported-Linux assurance and current-head
provider obligations remain under the verification stage owner. No native source
was inspected or collected during this repair. Original estimate remains UNKNOWN.
