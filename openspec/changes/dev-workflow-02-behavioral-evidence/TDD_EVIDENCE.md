# Behavioral evidence implementation evidence

2026-09-29 (Europe/Berlin), base `999cb8f960785fe4ac0434d41a0892beca933191`.
Contributor tooling/test scope only; runtime behavior unchanged. Final review pending.

## Observed red / green

- `pytest tests/test_behavioral_evidence.py -q`: 14 failures at the explicit
  missing-validator assertion before implementation (exit 1). This is interface-absence
  proof, not 14 independent discovered defects; output: ignored
  `.changecost/behavioral-evidence/packet-red.txt`.
- Same command after implementation: 14 passed (exit 0), covering same-head source
  changes, replaced/missing reports, missing oracle role, unmapped dependencies,
  skipped/unbound/non-applicable required evidence, malformed input and impact mapping.
- `pytest tests/test_lifecycle_stateful.py -q`: 13 passed (exit 0). Four selected
  faulty targets raise the named invariant assertion inside sensitivity controls;
  repaired targets run the identical trace/model/projection successfully. The generator
  uses seeds 0–7, 24 operations plus two setup operations each, and an explicit 12-step trace.
- Ruff formatting/import cleanup then scoped lint passed. First type check reported
  nullable cutoff handling in the faulty test subclass; adding the explicit None path
  yielded zero errors/warnings. This is implementation feedback, not a review finding.

No production transition/graph/revision helper is imported by the oracle. Writer
inspection of public APIs also exposed implementation bodies; independent human
review is still required to assess correlated assumptions. Native failure reports,
command timestamps and follow-up verification are retained locally; later sections
record final gate evidence rather than assuming these early checks cover edits.

## Tool experiments and current limitations

See [pilot report](../../../docs/lessons-learned/behavioral-evidence-pilot.md) and its
sanitized JSON ledger for actual SpecFact attempts, exits, elapsed seconds, failed
setup, unbound analysis and the distinct CrossHair/security-scanner controls.
Native reports and copied-input fingerprints are ignored under `.specfact/behavioral-pilot/`.
The exact original collection binding is retained; it is never replaced with a later
binding. Generic scanners and import/drift are not claimed to prove lifecycle behavior.

The genuinely new schema-8 session began at revision 0 with 0 batches/0 measured
minutes and the normal 3-batch/90-minute allowance. Required documentation ownership
paths were added by an explicit approved scope decision and head refresh; history
was preserved. Strict OpenSpec, aggregate checks, staged checks and final independent/
external current-head review remain pending until their actual results are appended.

## Pre-review integration (2026-09-29)

The timed check ledger `.changecost/behavioral-evidence/checks.jsonl` records:
27 targeted tests passing; full BasedPyright zero errors; selected strict OpenSpec
exit 0; full `make check BASE_REF=999cb8f960785fe4ac0434d41a0892beca933191
MANIFEST=.changecost/behavioral-evidence/manifest.txt` exit 2 in 75.37 seconds.
All 833 tests passed in 66.68 seconds. Hygiene, lock (including host missing/stale/
repaired proof), lint, types, index, metadata, workflow, build and all 11 strict
OpenSpec items passed; audit was explicitly not applicable because locked inputs
were unchanged. Documentation initially required a refreshed content-bound rationale
for the unchanged generated command reference; that rationale was repaired and
rechecked separately. Required capsule members reported `unsupported_controller_platform`
on macOS: the aggregate gate is incomplete, not passed; Linux remains required.

The documented packet example was executed on actual passing lifecycle output. It
validated current, became incomplete when the report bytes were replaced at the same
path, and returned current only after exact original bytes were restored. This is
actual evidence freshness control, separate from the initial interface-absence red.

## Review round 1 and repaired regressions

Frozen input digest `6df0fbce679c10bd3afb0ea9431f529c7d992a4195381df4986d8e250906c3dc`,
epoch input-generation:5, was independently reviewed and checked unchanged across
29 files. Three unique P2 findings were accepted (two packet-binding, one retry-history);
CodeRabbit's two comments duplicate the ignored-input finding. Review elapsed
21:18:14.846656Z–21:22:54.296469Z (4.6574968833 minutes) is recorded conservatively as
a wall upper bound, with no overlapping lane time added. Batch/history were preserved.

The exact staged-only omission and ignored oracle rehash regressions returned current
before repair. Real SQLite sequence-only and availability-only retry mutations failed
to raise their detector. `pytest tests/test_behavioral_evidence.py
tests/test_lifecycle_stateful.py -q` therefore yielded **4 failed, 27 passed** (exit 1).
After including index diffs, requiring authoritative input membership, and comparing
complete exports for accepted model no-ops, the same suite yielded **31 passed**
(exit 0). Logs: `round-1-regression-red.txt` and `round-1-regression-green.txt` under
ignored `.changecost/behavioral-evidence/`. One intermediate run exposed the older
retry control's assertion-label mismatch after stronger detection; its expected named
detector was aligned, without changing the faulty/repaired input trace.

## Targeted closure and publication boundary

Round 2 reviewed the exact seven-file delta, digest
`bf225cc54135daa44b6d1d3c73fe978c63bc9fa945317f62cb6cb463bb281293`, input-generation:7.
Both independent lanes returned no findings; the model reviewer repeated both SQLite
metadata faults and the repaired trace. Interval 21:30:08.165861Z–21:31:13.813836Z
adds 1.0941329167 conservative wall minutes, preserving two batches and 5.7516298
recorded minutes. CodeRabbit's full first-round review covered 29 files; its two
comments were duplicates of one accepted finding, not two additional defects.

After repair, all 837 tests passed in 66.46 seconds; full types, docs, index, metadata,
workflow, build and all 11 strict OpenSpec items passed. Aggregate exit 2 was solely
unsupported macOS capsule execution. The revised guide example ran on the complete
authoritative manifest, validated current, rejected replaced report bytes and returned
current after restoration. Native reports remain tied to their original collection
bindings; no old run is relabeled with a newer binding.

The maintainer's end-to-end request explicitly authorizes committing/pushing this
reviewed candidate to obtain the mandatory supported-Linux/current-head remote gates.
Publication is validation in progress, not a full-gate pass or merge authorization.
The pilot telemetry is frozen at 2026-09-29T21:32:11.834840Z, excluding later report
finalization, commits, pushes and remote review; later measurements remain separate.
Main was refreshed before publication and remains the recorded base. Final task 5
items stay unchecked until the remote/staged obligations actually complete.

## Native baseline provenance and Linux quality correction

Native Codex findings `4138609283` and `4138609294` were independently reproduced
and accepted. New spec scenarios precede the implementation: missing prior requires
broad review; foreign change identity returns controlled incomplete; valid same-change
comparison remains current/narrow. Packet regression command
`uv run --locked pytest tests/test_behavioral_evidence.py -q` produced **2 failed,
17 passed** before repair; combined packet/lifecycle suite produced **34 passed**
afterward. Native logs are `native-baseline-red.txt`, `native-baseline-green.txt` and
`native-refactor-green.txt` in ignored `.changecost/behavioral-evidence/`.

Both Linux quality jobs on a664117 failed with three blocking findings in the new
tests: Radon projection CC18; radon-kiss dispatcher nesting7; Pylint E0401 unresolved
behavioral_model. Minimal extraction/named callables/explicit test package retain the
same oracle, mutation IDs, predecessor assertions and full-history comparisons.
Affected files now have maximum Radon CC14 and CC6; the exact installed Radon mapper
reports no errors. Pylint4.0.7 reports no errors with project/test dependencies present
in the isolated local tool environment. Its initial missing pytest result is setup
feedback, not a project defect. Full types pass. No waiver or runtime edit is used.

All counters/history remain: three recorded batches overcount two actual correction
sets because orchestration counted review phases. The bounded extension to four
recorded batches retains the original 90-minute allowance. Targeted independent
closure and final committed-head Linux/native reviews remain mandatory.

## Recurring accepted-append history investigation

Native P2 4138783179 triggered independent family investigation and spec-first
complete bounded transition obligations. Six actual SQLite append faults were
undetected before repair: `uv run --locked pytest tests/test_lifecycle_stateful.py
-k append_history -q` returned **6 failed, 15 deselected** (exit1). They alter old
observation time/sequence, source identity/boundary, or new observation time/boundary.
The repaired checks preserve all old observations, stable source identity/schema,
fixed source clock and coherent unique complete local observations at a strictly
later shared boundary. No contiguous +1 rule is assumed. Two fresh-import controls
corrupt actual foreign observations/local availability, then verify repaired targets.
An explicit rejected fresh-store case preserves absence. Existing no-op and identical
reimport full-export controls remain. Logs are `history-matrix-red.txt` and
`history-matrix-green.txt` under ignored `.changecost/behavioral-evidence/`.

The earlier head3258615 passed both Linux quality jobs (run36636593121); later inputs
remain unverified by that result. Independent closure/new-head gates are pending.
This is the third actual correction set/fourth recorded batch, with authorized
max5/90minutes retaining all earlier history and orchestration accounting error.

The first family closure exposed a remaining conditional bypass: absent storage after
a successful append skipped persistence checks. Fresh/existing-store real-operation
then-delete variants both failed the detector before the guard (**2 failed**). The
accepted-append branch now unconditionally requires a persisted export before checking
its relations. Both faulty targets are rejected and repaired traces pass. This is an
additional variant of the still-open history finding/correction set, not a new runtime
defect or review batch. `history-absence-red.txt` retains the red proof.
