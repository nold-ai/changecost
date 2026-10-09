---
name: changecost-verify
description: Verify a ChangeCost change with scoped quality, defect-review, and documentation subagents, then commit and push the verified feature branch. Use after implementation or preparation, before promotion to a PR.
---

# Verify and persist a change

Run this workflow when asked to verify and persist a selected change. A read-only
review request stops at the findings; authoring or discussing this skill does not
execute its commit/push steps.

Read `AGENTS.md`, `openspec/config.yaml`, the selected change artifacts, and
[quality gates](../../../docs/agent-rules/50-quality-gates-and-review.md).
Use the [shared workflow](../../../docs/agent-rules/30-change-workflow.md) for
main freshness, branch ownership, prepared artifacts, and saved-state recovery.
Preserve existing authorization and unrelated work.

Follow the canonical [review selection and live acceptance policy](../../../docs/agent-rules/30-change-workflow.md#review-selection-and-live-acceptance):
one upfront obligation review, affected-scope closure, Codex by default and additional
CodeRabbit for listed risks. Preserve mechanical gates and exact-head evidence; do not
add a generic full local/CLI review or a receipt-only commit by default.

## Freeze the intended result

- Confirm the selected change, owned paths/hunks, feature branch, upstream, and
  remote destination. Refresh main using the shared protocol before verification;
  reconcile relevant drift before certifying results.
- Resolve the comparison ref according to the review-agent contract: use the
  local base branch's upstream if ahead, otherwise the local branch; fall back to
  its configured upstream if the local branch is unavailable. Record the resolved
  SHA and `git merge-base HEAD <comparison-ref>`.
- Define review scope as everything that would merge: the merge-base diff,
  staged and unstaged changes, and intended untracked files. Explicitly inspect
  staged changes that differ from working files; an ordinary tracked diff omits
  untracked files. Exclude unrelated edits from the intended result, not from the
  ownership audit.
- Record HEAD, base SHA, path manifest, and content fingerprints for the intended
  files (including additions and deletions). Checkers must see the prospective
  committed contents. If partial staging or unrelated work would alter their
  inputs, verify an isolated snapshot of that intended result; do not certify a
  commit using tests that depended on excluded edits.
- Finish formatting and other intended edits before freezing. Keep exactly one
  writer. While review lanes run, no agent may edit tracked files, stage, commit,
  switch branches, or push. A gate that fixes files must run before the freeze or
  in an isolated snapshot; any fixes must be inspected, incorporated by the sole
  writer, and checked again against a new fingerprint.

## Close the affected execution obligations

Use the [canonical checkpoint](../../../docs/agent-rules/30-change-workflow.md#risk-first-execution-checkpoint)
with the frozen scope and current input binding. Give the existing closure reviewer
the actual delta, affected assumptions, unresolved findings and proof limits.
Mapped corrections receive affected-scope closure; unknown dependencies or changed
entrypoints/trust boundaries renew broader review. Adjudicate findings using the
canonical evidence/disposition rules. Documentation applicability does not waive
the dispatcher's required native assurance or final mechanical/provider gates.

## Verify selected obligations

Before dispatching another review or correction batch, read
`python -m quality.review_session status <change-id>`. `replan` and `incomplete`
require a compact packet and a maintainer decision; `investigate` requires a
family-wide invariant review before another targeted repair. Record the complete
frozen scope, findings, evidence and active time in the local session record.
One batch is one collected finding set followed by fixes and verification, not one
commit. A fresh conversation or head does not reset its allowance.
Use `init <change-id> --json <contract.json>` only for genuinely new sessions,
following the complete shared-workflow example; lost or incompatible receipts
require recovery. Investigate the first genuine escape after correction; another
escape after that investigation requires replanning. A non-finding is not an
escape, but fixing a genuine recurrence does not erase its history.

When using independent workers for the selected obligations, give each the checkout/snapshot, selected change, complete scope manifest,
base/HEAD SHAs, fingerprints, applicable rules, and a compact output contract:
commands and outcomes, actionable findings with paths/lines, missing evidence,
and the reviewed fingerprint. Store large logs locally in `.changecost/` or
`.specfact/`; return summaries to keep the coordinating context small. Subagents
must not delegate further or perform Git mutations. If delegation is unavailable,
report that limitation; a coordinator's own review is not independent review.

1. **Quality gates.** Run `make check` and applicable checks from repository
   configuration and CI. `pre-commit run --all-files` only covers tracked files:
   include every intended addition explicitly with `pre-commit run --files <paths>`
   in an isolated verification snapshot, or use a snapshot whose index includes
   all intended additions. Review any auto-fixes through the single-writer/freeze
   procedure above; do not certify untracked additions that skipped hygiene.
   For implemented Python behavior, run the configured
   format/lint/type/tests and fresh SpecFact code review covering affected behavior
   and dependencies. Inspect analyzer availability and report contents, not just
   exit status. Record CLI/module versions, commands, timestamp, scope, and actual
   results. Check genuine failing-before/passing-after TDD evidence for behavior
   changes. With no product source, report runtime tests and SpecFact source
   analysis as not applicable, never passed. Missing required tools, skipped
   required analyzers, stale reports, and failing checks block a green result.
2. **Defect review.** Read and use
   `/Users/dom/.codex/skills/.system/review-agent/SKILL.md`. If unavailable, search
   available skill locations once; if still absent, disclose that and use the
   user's supplied review-agent contract below as an explicit fallback. Inspect
   the selected upfront obligation matrix or affected follow-up delta and enough surrounding code, tests, and call sites to
   establish each defect. Remain read-only: no edits, commits, pushes, comments,
   or further delegation. Return every concrete, introduced, actionable defect
   affecting correctness, security, performance, or meaningful maintainability;
   exclude speculation, pre-existing issues, intentional changes, and style nits.
   Use `[P1] Imperative title — path:line` with a short demonstrated scenario,
   smallest changed line range, severity P0 through P3, highest first. If none,
   return `No findings.` Add overall assessment and material test gaps. Do not
   claim the installed skill ran when using the fallback contract.
3. **Documentation and metadata freshness.** Trace each changed behavior or
   workflow to its specs, task status, user/developer docs, examples, changelog,
   and `llms.txt`. Check descriptions and commands against current code/config
   and actual evidence; timestamps alone do not establish freshness. Check links
   and navigation for moved/new pages. Run any repository-owned generation/check
   command in check mode and compare expected contents with checked-in artifacts.
   If no generator exists, inspect the small source-to-document mapping directly;
   do not import a sibling repository's toolchain. Confirm `llms.txt` reflects
   current entry points and capabilities without presenting planned features as
   implemented. For the current manual index, compare its skill inventory,
   project phase, and documentation claims to the canonical files, not merely link
   existence. Record an explicit version decision: keep unreleased planning
   unversioned, update `CHANGELOG.md` under Unreleased as applicable, and only
   synchronize package/version references when the actual change and established
   release policy require it. Do not manufacture a release, tag, or version bump
   to satisfy a checklist.

## Resolve, certify, commit, push

Wait for required checks and selected independent closure. Verify findings against evidence, then let the sole writer
make the smallest sufficient corrections. Preserve clear names and proportionate
complexity; avoid speculative abstractions. Rerun affected checks and review the
changed scope after fixes. Any source/test/config/spec edit invalidates affected
earlier evidence; all final required results must cover the same intended contents.
Record final checks and scope in the change's evidence or appropriate workflow
handoff. If recording evidence changes files, review those additions and rerun
applicable documentation/hygiene checks before final certification.

Do not commit or push while a confirmed actionable defect or required gate remains
unresolved. A documented limitation is not a pass; report the blocker with the
smallest next action. If repeated attempts make no progress, diagnose the missing
prerequisite or decision instead of retrying blindly. Continue independent fixes;
an actual blocker or required user decision must remain explicit and incomplete.

When all applicable gates are genuinely green:

1. Recheck branch, HEAD, base, owned files, and fingerprints. If another writer or
   newly fetched main changes the evaluated result, reconcile and reverify first.
2. Stage explicit owned paths/hunks only. Inspect `git diff --cached`, staged
   secrets/generated files, and the resulting prospective tree. Preserve existing
   unrelated staged work; do not include it in this commit. If it cannot safely
   coexist, isolate the owned change before committing. Never use blanket staging
   to sweep in unrelated files.
3. Confirm the staged contents equal what was verified. Commit with the repository
   convention. Respect signing and hooks; if a hook changes files, inspect and
   reverify them before retrying. Do not bypass failing checks or signing policy.
4. Inspect the resulting commit and confirm its tree matches the verified result.
   Push normally to the identified feature branch, setting its upstream if needed.
   Never push main or force-push as part of this workflow. On remote divergence,
   fetch and reconcile deliberately, then reverify; do not overwrite remote work.
5. Verify the remote branch points at the committed SHA. Report commit, branch,
   actual gates/review results, remaining limitations, and rollback by a follow-up
   revert commit. Hand off to `$changecost-promote`; this phase does not create a PR.

## Behavioral evidence pilot

Use the [behavioral evidence guide](../../../docs/development/behavioral-evidence.md)
for the selected pilot: retain stable intent, independently inspected invariant and
dependency mappings, specification/oracle/generator/configuration fingerprints and
native report digests. Capture the existing review-session binding before executing
checks; provide the first reviewer the complete packet and later reviewers the actual
delta plus affected assumptions and unresolved findings. New/unknown inputs, changed
entrypoints or trust boundaries require renewed broad review. Missing, stale, skipped
or unbound required evidence stays incomplete. Preserve existing counters and final
current-head quality/independent/external-review gates; the packet grants no completion.
