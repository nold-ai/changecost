# Preparation evidence

Prepared 2026-09-29 (Europe/Berlin). Decision: implementation-ready within this bounded
scope; empirical effectiveness and required implementation gates remain To-Validate.

## Baseline and ownership

- Repository: private `nold-ai/changecost`, target `main`.
- Successful fetch recorded at 2026-09-29T22:45:32+02:00; base and initial HEAD:
  `999cb8f960785fe4ac0434d41a0892beca933191` (merged PR #25, 2026-09-29T17:35:39Z).
- Dedicated worktree: `/Users/dom/.codex/worktrees/behavioral-evidence/changecost`;
  branch `codex/dev-workflow-02-behavioral-evidence`.
- Primary settlement branch and two pre-existing worktrees were inspected read-only.
  Their uncommitted runtime, archive and retrospective report edits were not imported.
- The maintainer explicitly requested propose, issue synchronization, prepare and
  implementation in sequence. Artifacts remain locally prepared/unpublished; no
  planning-only PR/stash detour is required. No merge or deployment is authorized.

## Observed scope and independent review

Read the root instructions, rule index/non-negotiable checklist, shared workflow,
OpenSpec/TDD, quality and GitHub governance; applicable propose/prepare skill rules;
actual OpenSpec 1.13.2 context/status/instructions; existing bounded-review spec,
Core-02 delta, public lifecycle/store code, focused store tests, quality runner,
repository digest helpers, development gate guide and documentation inventory.

The current main lifecycle docs still describe Core-02 as under verification and
its story #11 remains open. Merged PR #25 and the base's complete Core-02 tasks/code
establish delivered implementation. This preparation records that administrative
mismatch without absorbing separate settlement/archive reconciliation.

Independent architecture review identified two acceptance gaps, repaired before
handoff: bind actual report bytes plus spec/oracle/generator/config inputs, and require
faults at the real behavior/persistence boundary with unchanged oracle/projection/trace.
No broader engine or second review ledger is required. The selected pilot has four
fault families and bounded deterministic sequences; concurrency, economic contracts,
exhaustive graph/filesystem/representation domains remain explicitly excluded.

## SpecFact evidence checked

Inspected both saved current GitHub command inventories and the installed-generator
probe at `/tmp/specfact-sidecar-assessment/probe/results.json` (2026-09-29): pure-Python
extractor `None`, no harness for empty default contract, OpenAPI harness uses adapter
dispatch and does not import the example domain function. Installed CLI 0.55.4,
codebase 0.41.16/project 0.41.27; inspected modules main
`b3ca3014c8d0e064b860856d4b560a2591999532`.

Primary source entrypoints, accessed 2026-09-29 (Europe/Berlin):
[core llms.txt](https://github.com/nold-ai/specfact-cli/blob/main/llms.txt) and
[modules llms.txt](https://github.com/nold-ai/specfact-cli-modules/blob/main/llms.txt).
These observations justify a small independent lifecycle oracle, not a claim that
non-capsule analyzers or required Linux capsule review have already run for this change.

## GitHub reconciliation

[Story #26](https://github.com/nold-ai/changecost/issues/26) was created after searching
all open/closed issues and the selected stable marker for duplicates. Readback verified:
native User Story, parent Feature #6 and reciprocal #6 body link, native blocked-by
#23 and #11, labels `enhancement`, `openspec`, `change-proposal`, `architecture`, `QA`,
no assignees, no milestone/delivery dates, private ChangeCost Project 3 membership
and Todo status. Parent #6 belongs to Epic #4. No existing issue was closed.
`CHANGE_ORDER.md` includes the supplemental story and remains acyclic; product order
and unrelated parent content are preserved. Repository privacy/topics were unchanged.

## Checks, limits and next stage

- `openspec validate dev-workflow-02-behavioral-evidence --strict --no-interactive`:
  exit 0, complete schema artifacts valid (2026-09-29).
- `openspec status --change dev-workflow-02-behavioral-evidence --json`: all four
  required planning artifacts exist; unfinished implementation tasks remain unchecked.
- `git diff --check`: exit 0.
- Full `make check`, behavioral red/green evidence, actual pilot telemetry and fresh
  review are implementation-stage obligations; no passing claim is made here.

The coordinator will initialize the genuinely new existing review-session contract
with the complete implementation manifest before review, including current planning
files. The implementation writer owns code/test/docs/index changes after handoff.
No new runtime dependency is planned. Confidence: high in bounded implementation
readiness; medium in defect yield; billing benefit unknown. Rollback reverts this
contributor change and preserves ignored receipts/evidence and existing stores.


## Authorized in-place post-replan preparation (2026-09-30)

Starting owned feature head is f6ddbe48db1df36d1054feed2cf8ae413b007ce6, clean before
this phase. Fetch succeeded before 2026-09-30T11:14:23Z (13:14:23 Europe/Berlin),
origin/main unchanged999cb8f960785fe4ac0434d41a0892beca933191. The initial sandbox
fetch failed writing FETCH_HEAD; the authorized host-context retry succeeded. Primary
settlement checkout and other worktrees remain untouched; no new branch/PR is needed.

Current GitHub readback: issue26 open, User Story, parent Feature6, blocked by23closed
and11open; PR24 merged at2026-09-29T05:40:30Z and PR25 at17:35:39Z satisfy delivered
code prerequisites. Labels enhancement/openspec/change-proposal/architecture/QA,
no assignees, project ChangeCost Todo retained. PR27 is open to main at f6ddbe48.
The administrative issue11 discrepancy remains unrelated to this replan.

The maintainer explicitly approved the same change's replan and implementation.
Existing session revision104 records authorized13/105.67495325 ceilings with10batch
history and15.67495325partialhistoricalminutes preserved; no family closure is asserted.
Original final-effort.md/json and final-verification.json were copied byte-identically
under ignored post-replan/original-f6dd with digests in authorization-baseline.json.
New preparation/implementation measurements use a distinct post-replan phase.

Applicable update/prepare rules and actual schema status/instructions were read.
The existing bounded-review-session capability needs a modified delta for the changed
family/budget/watch contract; it introduces no new capability or runtime framework.
Architecture matrix O1-O8 must be reviewed before code. Task5.3 is deliberately still
unchecked: actual live acceptance requires the repaired ledger and exact-head PR proof.
