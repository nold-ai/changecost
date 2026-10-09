---
name: changecost-prepare
description: Interactively select and review the next pending ChangeCost change against fresh main, code and current external evidence; reconcile its plan and GitHub issue, then offer a planning PR or scoped stash.
---

# Prepare the next change

Read `AGENTS.md`, `openspec/config.yaml`, the project brief and
`openspec/CHANGE_ORDER.md`, then the
[shared workflow](../../../docs/agent-rules/30-change-workflow.md) and
[GitHub governance](../../../docs/agent-rules/60-github-change-governance.md).
This stage changes planning/docs and the selected issue, not product behavior.

Follow the canonical [review selection and live acceptance policy](../../../docs/agent-rules/30-change-workflow.md#review-selection-and-live-acceptance):
one upfront obligation review, affected-scope closure, Codex by default and additional
CodeRabbit for listed risks. Preserve mechanical gates and exact-head evidence; do not
add a generic full local/CLI review or a receipt-only commit by default.

## Bounded review-session contract

For a change expected to reach implementation, prepare a compact review contract
under `.changecost/workflow/<change-id>/` with `python -m quality.review_session
init <change-id> --json <contract.json>` only for a genuinely new session. Follow
the complete shared-workflow contract example. Recover lost/incompatible existing
receipts rather than initialize another allowance, including in another worktree.
It names the requirements, acceptance criteria, non-goals, trust boundary,
complete intended input fingerprint, base, head and required GitHub reviewer
logins (exact REST identities), repository, required checks and status contexts.
Default allowance is three
correction batches or 90 active minutes; an explicit maintainer extension retains
prior counters. This is local recovery evidence, not authorization to expand scope.

## Refresh and select interactively

1. Refresh main by the shared protocol before judging what is pending. Preserve
   unrelated edits and in-use branches; use a clean owned preparation branch
   `codex/prepare-<change-id>` after selection, based on the recorded fresh main.
2. Run `openspec list --json`, inspect the change order, tasks, linked GitHub issue
   state, native blocked-by relationships and relevant merged PRs/code. Unchecked
   tasks, an open issue or a recent modification date alone do not prove readiness.
3. If the user already named a change, verify it. Otherwise present a compact
   shortlist of pending changes with prerequisite status, evidence gaps, likely
   touched scope and a recommendation with reasons. Ask the user to select one;
   do not select solely by recency. Wait for selection before change-specific
   edits; general freshness/read-only inspection can continue while waiting.
   Blocked work can be prepared, but name unmet implementation prerequisites.

## Review against code and reality

Get `openspec status --change <id> --json` and the applicable
`openspec instructions <artifact-id> --change <id> --json`. Read the schema's
actual artifact paths, existing specs, implementation, tests, relevant docs and
the issue. Preserve any explicitly selected OpenSpec store in subsequent commands.

Check each requirement for existing implementation, changed interfaces, conflicting
assumptions, testable acceptance criteria, missing failure cases, dependencies and
scope. Mark claims confirmed, outdated or unknown with evidence. For time-sensitive
or uncertain external claims, research current primary sources; record access
dates, versions and their impact. Local code/CLI evidence is preferable for what
is installed. Provider capabilities need inspected evidence, not guessed mappings.

Ask for material unresolved decisions when evidence cannot determine the intended
behavior. Do independent work while waiting; do not replace a required answer with
elapsed time. Resolve ordinary implementation details using existing scope. If the
change is already delivered or its purpose is obsolete, explain that and return
to selection instead of forcing new implementation work.

## Prepare the execution checkpoint

Apply the [canonical checkpoint](../../../docs/agent-rules/30-change-workflow.md#risk-first-execution-checkpoint)
to the selected change: record the critical assumptions, observed boundary proof,
affected obligations and exclusions in its existing design/preparation evidence.
Name dependent blockers and the sole writer; pass this evidence to the existing
upfront reviewer. For documentation-only scope, record applicability and relevant
checks without requiring an unrelated lifecycle packet. Resolve material contrary
or unavailable evidence before representing the dependent approach as ready.

## Reconcile the plan and correlated issue

Apply evidence-backed updates coherently across proposal/design/specs/tasks and
affected docs, retaining the selected change identity and uncompleted task state.
Use schema instructions for missing artifacts. Preserve completed historical work;
new follow-up work needs explicit scope and accurate task state. The selected
prepare request authorizes this batch reconciliation; do not insert per-artifact
confirmation loops from the generic update skill. A material scope decision still
needs the user's answer. Do not create a competing plan or new issue for the same
change, and do not silently expand product scope.

Read the linked GitHub issue immediately before editing; preserve unrelated body
content and discussion. Update acceptance criteria, scope/non-goals, evidence,
dependencies and OpenSpec links affected by the reconciliation. Reuse stable IDs;
if dependency/hierarchy changes are necessary, keep native relationships and
`CHANGE_ORDER.md` coherent and acyclic. Read back affected issue fields and project
relationships per governance. Mark the plan as locally prepared/unpublished until
there is a real remote branch/PR; never invent a published link or imply delivery.
On concurrent edits or failed writes, read back the current issue before retrying:
a timeout may have followed a successful write. Apply only still-missing changes
and preserve concurrent edits. Report any unsynced state honestly.

Run selected strict validation and `make check`; inspect documentation links and
`llms.txt` applicability. Present the concrete reviewed diff, what changed and why,
fresh main SHA/time, issue sync result, remaining ambiguity/prerequisites and checks.
If required evidence is unavailable, label it To-Validate; don't claim ready.

## Offer and execute the disposition

If no file changes remain, report that the plan is already current and record any
issue-only update. Do not manufacture a commit, stash or empty PR. Otherwise:

After the result is reviewable, ask whether to **create a plan-only PR to main** or
**save the prepared artifacts in a scoped stash for implementation**. This is the
requested delivery choice, not permission to implement. Reuse an earlier explicit
choice. No answer is not a choice; keep the work intact while waiting.

- **Planning PR:** use `$changecost-verify` in planning-only scope to run applicable
  review/checks and commit/push the preparation branch. Create/reuse a focused PR
  to `main`, follow the repository template, attach the PR artifact where available,
  and update/read back the issue's real plan link. Use linking language rather
  than closing an unfinished implementation issue. Hand off the PR URL/head and
  remaining prerequisites; promotion's monitoring loop is a separate request.
- **Stash:** follow the shared scoped tracked/untracked stash procedure and write
  the receipt with its immutable OID. Include correlated doc/research changes,
  preserve unrelated work, record the actual issue sync state and report the local
  recovery location. With no artifact changes, record that fact; do not stash or
  label an old entry as this preparation.

Finish with selected change, disposition, evidence/limits and the exact next
invocation: `$changecost-implement <id>` only when implementation is desired and
its prerequisites are met. This preparation does not start that stage.

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
