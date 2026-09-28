# Change workflow: shared state and freshness

The four skills are repository-owned instructions, with no harness dependency:
[prepare](../../.agents/skills/changecost-prepare/SKILL.md),
[implement](../../.agents/skills/changecost-implement/SKILL.md),
[verify](../../.agents/skills/changecost-verify/SKILL.md), and
[promote](../../.agents/skills/changecost-promote/SKILL.md).
They use existing OpenSpec/Git/GitHub tools and the rules in this directory.

## Stage boundaries

Installing or reviewing skills does not execute their workflows. Read the actual
user request and existing session authorization. Prepare selects and reconciles
planning artifacts and the correlated issue; it asks for the requested planning
PR versus stash choice after the result is reviewable. Implement authorizes the
selected change's implementation, not live collection, unrelated changes or a
release. Verify persists work when commit/push is requested; a read-only review
stops at findings. Promote creates/reuses its PR and handles its review comments
and verified fixes when that workflow is requested. No stage merges or deploys.

These are separate stages, not a command that runs the entire backlog. A named
change carries across stages; a generic request to select a change does not pick
one by recency. Ask only for the material choices requested by the workflow or
needed to resolve real ambiguity. Do not repeat already answered choices.

## Refresh main without losing work

1. Read root/branch/status (including staged and untracked files), remotes,
   upstreams and `git worktree list`. Establish ownership before switching or
   integrating. Use the verified repository remote, normally `origin`; confirm
   that its main branch is the intended PR destination.
2. Fetch that remote's `main`; record the successfully fetched SHA and timestamp.
   A failed fetch is not evidence of freshness. Read-only exploration can continue
   with the limitation, but don't certify readiness, commit/push or promote on a
   falsely fresh baseline.
3. On an owned clean `main` checkout, run `git pull --ff-only origin main` (adjust
   the verified remote) and confirm HEAD equals the fetched remote tip. If safe
   to switch to an unused clean local main, do so first. Never pull main into the
   current feature branch as an implicit substitute for this step.
4. If main has local-only/divergent commits, is dirty or is in use in another
   checkout, preserve it. Use a suitable clean checkout or a managed worktree
   based on the fetched main SHA; report that the remote baseline was refreshed
   while local main was left intact. Inspect existing managed worktrees before
   creating one. Do not stash all user work, reset main or move another session's
   branch to satisfy the freshness step.
5. Create new preparation/feature branches from this baseline. For an existing
   owned feature branch, inspect its commits and remote state; merge fresh main
   when integration is needed, with a clean tree and conflict review. Preserve
   published history; no automatic reset, rebase or force-push. If a branch is
   already in use, coordinate or isolate rather than checking it out twice.

Freshness expires when relevant main, issue, code or external facts change, not
at an arbitrary timer. Compare the fetched baseline and dependencies again at
implementation and before verification/promotion. Semantic revalidation is
required even if a merge or stash application has no textual conflicts.

## Prepared artifacts and scoped stash

Keep one small ignored receipt per preparation under
`.changecost/workflow/<change-id>/prepare.md`. Write it in a checkout that the next
stage can locate, and report its absolute path. It records repository identity,
change ID and issue URL, source worktree/branch/HEAD, fetched main SHA/time, reviewed
paths, unresolved decisions, research/check evidence, issue sync state, chosen
delivery, and (if created) the immutable stash commit OID. This is a recovery
pointer, not a second plan, proof of authorization, or automatically trusted input.
No private exports/prompts or transcripts belong in it. Other machines/checkouts
do not automatically share ignored receipts.

For the stash choice:

- Inspect the final diff and own every selected hunk. Include exact changed
  artifact, research and correlated documentation paths, including new files.
  If any selected file also contains unrelated edits, isolate the preparation
  first; a path-scoped stash cannot separate ownership within that file. Also
  require an index with no unrelated staged changes, even outside those paths:
  Git can include the entire index in a path-scoped stash. Use an isolated clean
  preparation checkout rather than unstaging someone else's work. Transfer only
  the reviewed preparation content and report if its original edits remain in
  the first checkout; isolation itself does not remove or stash those duplicates.
- Preview `git diff`, `git diff --cached` and selected untracked contents. Record
  the intended path manifest and a unique message containing the change ID, source
  base and preparation timestamp. Stage neither private state nor unrelated files.
- Use `git stash push --include-untracked -m <message> -- <explicit paths>`;
  pass paths as arguments, safely quoted, not untrusted shell text. Avoid `--all`.
  After success, compare old/new stash refs and resolve the new stash commit OID.
  Inspect both its tracked diff and untracked tree (`OID^3` when present) and
  confirm the saved contents match the reviewed manifest. Verify unrelated work
  is unchanged, then atomically save the receipt with that OID. If interrupted
  before the receipt update, recover by inspecting the unique message, OID and
  contents; do not guess the newest stash. A no-op produces no new stash: record
  `no artifact changes`, never reuse a previous stash's OID.
- GitHub changes are not stashed. The linked issue must distinguish locally
  prepared/unpublished requirements from merged implementation. Record the actual
  issue readback and any failed synchronization; a local stash is not remote backup.

For restoration:

1. Match receipt, repository, selected change and issue, then inspect the stash's
   base and full tracked/untracked contents. If there are several plausible
   receipts/stashes, ask which one; don't infer from stash order. If already
   consumed, or equivalent artifacts arrived through a merged planning PR, use
   current artifacts without reapplying them. Verify equivalence, not filenames.
2. Establish the intended clean feature branch from fresh main, or reconcile the
   existing branch first. Apply using `git stash apply <immutable-OID>` without
   `--index`; do not use blind `pop` or `stash branch` (the latter starts at the
   saved old base). The original stash remains a recovery point.
3. Inspect conflicts and semantic drift against current code/specs and issue
   requirements. Never discard untracked collisions or choose all-ours/all-theirs
   blindly. On interruption/conflict, record applied/partial state and inspect
   the current tree before retrying; do not reapply an already applied stash.
4. Rerun selected strict OpenSpec validation and readiness checks; record applied
   OID, destination branch/base and changed paths. Retain the stash through
   successful verification and commit. If dropping it afterwards, find the current
   reflog entry resolving to that OID and recheck immediately before dropping;
   never drop a cached `stash@{n}`. Keeping it for deliberate later cleanup is safe.

## Verification and compact delegation

The parent owns the selected objective and scope. Workers receive only the needed
paths, immutable baseline/head, task, rules and output contract. One named writer
owns edits and Git/PR mutations; readers/checkers run on a stable tree. Reuse workers
within available slots. Store lengthy logs in ignored `.changecost/` or `.specfact/`
and return concise results with evidence paths and reviewed state. Do not mistake
a worker summary or successful tool exit for actual analyzer coverage.

Review and gate evidence is tied to file contents, not just HEAD when the tree is
dirty. Substantive changes invalidate affected results. Missing required tools or
reviewers are blockers; not-applicable checks need a reason. A workflow receipt
can retain the exact verified tree/commit and evidence paths for the next stage,
but the next stage must check that they still match. Receipts never replace
`TDD_EVIDENCE.md`, specs/tasks, PR evidence or native GitHub relationships.

## Documentation, versions and llms.txt

Compare changed behavior to requirements and docs/examples, then inspect linked
entry points. Update `CHANGELOG.md` under Unreleased for meaningful changes. No
version bump, release tag or published package is needed for planning/scaffold
edits; synchronize real package versions only when an applicable policy requires it.

`llms.txt` is currently a small manual index. Check its skill inventory, links,
phase and capability descriptions against canonical files; do not label future
commands as implemented. Link checking alone does not prove semantic freshness.
When a CLI/command generator is actually introduced, generate from its canonical
inputs and run its check mode against committed output. Do not copy SpecFact's
release/signature/registry machinery or make a sibling checkout a prerequisite.

Pattern inspected on 2026-09-28 (Europe/Berlin): `specfact-cli-modules` at
`bdaab8a3fc48c7321d21127e2b0042946cd90bfa`,
`scripts/generate-command-overview.py` (render/check comparison),
`tests/unit/docs/test_llms_overview_freshness.py` (freshness guard), and
`docs/agent-rules/70-release-commit-and-docs.md` (metadata consistency).
ChangeCost currently has no implemented product command tree to generate from.
