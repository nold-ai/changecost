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

## Bounded review contract

Only a genuinely new session uses
`python -m quality.review_session init <change-id> --json <contract.json>`.
Existing sessions use `status`, then `packet` when recovery or replanning is
required. A missing or incompatible receipt must not reset counters, including
after moving to another worktree. Preserve schema-1 history as recovery evidence;
do not synthesize prior measurements into a new schema-8 allowance. Schema-1/2/3/4/5/6/7
receipts remain recovery evidence; new required initial-scope facts are not invented.

The complete JSON contract has this shape (replace example SHAs, file fingerprint,
requirements, gates and exact provider identities with inspected values):

```json
{
  "repository": "nold-ai/changecost",
  "requirements": ["Preserve bounded review history"],
  "acceptance_criteria": ["Applicable checks and reviewers complete"],
  "non_goals": ["Hostile-runner integrity"],
  "trust_boundary": "Existing contributor workflow boundary",
  "intended_files": {"quality/review_session.py": "<sha256>"},
  "base": "<full-base-sha>",
  "pr_base": {"ref": "main", "sha": "<full-target-tip-sha>"},
  "head": "<full-head-sha>",
  "required_reviewers": ["<exact-reviewer-login>"],
  "required_checks": ["<required-check-name>"],
  "required_statuses": []
}
```

Requirements and acceptance criteria are nonempty lists of nonblank strings;
non-goals may be an explicit empty list. Trust boundary is nonblank text. Supply
full existing commit IDs, normalized repository-relative file paths and actual
initial SHA256 values. Use `<absent>` for an intended path not created yet. All
initial changed, staged and untracked paths must be covered; unchanged planned
files are allowed. Initialization verifies those facts once and captures them in
genesis. Later replay uses captured facts, and `init` with the same original
contract remains idempotent after `advance_head`.
Full commit IDs use the same 40/64-character hexadecimal rule at initialization,
head refresh and replay; the declared head must still match actual Git HEAD.
Tracked `assume-unchanged` or `skip-worktree` flags are unsupported because they
can hide changes from Git inspection. The helper rejects them at every input
capture; it never clears or mutates the user's index flags.

Minute extensions and measured time/usage use finite canonical sums of original
event components, preserving exact budget boundaries across retries and restarts.
Overflow fails closed; do not round limits or reset history to recover.

Remote collection makes exactly two complete paginated passes under one deadline
and accepts only matching meaningful evidence, returning the second observation.
Drift or second-pass failure invalidates prior green monitoring. This bounded check
is not an atomic API snapshot and cannot detect reverted or post-final-read changes.
Contract-required completed checks must conclude `success`; `neutral` cannot prove
required validation ran. Optional neutral checks retain their nonblocking policy.
This repository assurance rule is stricter than GitHub's native merge eligibility.
Local reviewer coverage includes every fetched thread, review body and PR comment,
including historical and informational reports. Namespaced thread/review/comment IDs
bind exact content without metadata noise; new, edited or removed reports require
explicit revalidation. Bot-summary churn can therefore require another local
attestation. Empty bodies are valid; missing or malformed identities/bodies and duplicate identities
invalidate monitoring. Coverage never clears objections or unresolved findings.
Input binding includes every declared path, even ignored files or explicit absence.
Existing declared content outside the index prevents clean completion; unrelated
ignored artifacts remain excluded. Remote positive evidence must also postdate
initialization, because its earlier base context cannot be attested. This may
require rerunning valid same-base checks; exact timestamp comparison has no rounding
allowance for coarse provider timestamps. Objections remain blocking regardless of age.
Integer counters retain exact nonnegative values without floating conversion;
unrepresentable floating measurements reject atomically with controlled recovery
for malformed persisted history.

Each `advance_head` recaptures a `reviewed_manifest` and complete changed/staged/
untracked path coverage against the effective comparison base. Normal refreshes
retain authorized keys. To change them, first record a `scope_decision` with
`decision: "approved"` and the complete `intended_files` mapping, then explicitly
reference its ID in `advance_head.scope_decision_id`. Approval fingerprints retain
intent; current fingerprints are recaptured, so planned-absent files may materialize
and authorized content may change. No approval is adopted implicitly; explicitly
selecting an earlier approval is permitted. The packet exposes the current manifest
separately from the immutable original contract. Fresh review evidence is still
required after every refresh; incompatible receipts require recovery without reset.

The first `watch <change-id> --repo <owner/repo> --pr <number>` binds the PR.
That source remains fixed across input refreshes. `advance_head` captures a new
input epoch and invalidates prior completion evidence while retaining counters.
Epoch strings derive from refresh generations independently of caller event IDs.
Automatic binding chooses a deterministic unused ID under the session lock;
existing finding and scope identities remain unchanged.
Required event strings and supplied `supersedes` references must contain non-whitespace
text. Preserve exact nonblank bytes; do not trim identifiers or alias family labels.
Handoff status and contents derive from one receipt revision, with actual-input drift
still checked; changed watcher output uses that packet's status and observation.
Passing reviewer evidence acknowledges the packet's current `report_receipts` in
`reviewed_reports` after explicit local triage. Remote resolution cannot substitute
for this coverage or for dispositions of known local findings. Changed report content
requires revalidation; exhaustion overrides any remaining family investigation.
Every positive observation retains `_input_epoch` captured before collection.
Ingestion must not attach the current epoch to an unbound old snapshot. Missing,
malformed and stale epochs replace prior green monitoring with incomplete evidence.
The initial comparison `base` and target `pr_base` remain immutable history. To
adopt changed target context, supply both `comparison_base` and `pr_base` on an
`advance_head` event; the packet exposes the current binding. Capture that full
`binding` before each local review/check and supply it explicitly on its evidence
event. Never copy a fresh binding onto an old result. After adoption, required remote
positive results need timestamps at or after adoption; old objections still block.
The final published inputs must be clean. Snapshots retain validated requested-user
metadata. A renewed request to a required exact login blocks completion until absent;
cancellation cannot create approval or override other gates. Full receipts retain canonical
events and separate generated provenance; cached counters, decisions and monitor
summaries must agree with replay. The genesis marker detects a lost state file,
not deletion of the entire ignored directory or hostile tampering.

Investigate the first genuine family escape after correction. A further escape
after that investigation requires replanning. Final non-findings are excluded;
fixing a genuine escape does not erase its chronology. Independent scope work may
continue, but dependent work awaits an explicitly identified scope resolution.

### Review selection and live acceptance

Use one independent high-effort obligation/architecture review before implementation;
then close only affected obligations and dependencies after corrections. Stabilize
mechanical gates before requesting one full Codex review. Codex is required for every
normal PR. Also require CodeRabbit for security/trust boundaries, persistence/data-loss,
assurance or gate changes, and contradictory evidence. This behavioral-evidence replan
requires both providers. Explicit user review requests override the default. Do not add
a generic full local review or CodeRabbit CLI scan by default. All mechanical gates,
the supported-Linux capsule and the existing Python matrix remain mandatory.

CodeRabbit automatic review is disabled only through `reviews.auto_review.enabled`.
Inspect actual pending/current-head provider state and effective feature-branch config
once before requesting a review; reuse an already-running required review. For a
required provider use its established manual protocol: `@coderabbitai full review` for
the initial stable diff, `@coderabbitai review` for subsequent stable increments.
Never duplicate a running request or bypass quota/purchase credits. Codex app automation
is independent of this YAML. Official [automatic-review configuration](https://docs.coderabbit.ai/configuration/auto-review)
and [commands](https://docs.coderabbit.ai/guides/commands) were checked 2026-09-30.

The PR body is the canonical published live verification index: exact head/base,
current gate links, provider review source identities, independent closure evidence,
and the existing session's actual decision. Tracked tasks/TDD/report record immutable
publication milestones. A live acceptance checkbox may remain unchecked at publication;
record later exact-head acceptance in the ledger and PR receipt without a receipt-only
source commit. Do not claim every tracked checkbox is complete. A subsequent authorized
archival lifecycle may reconcile it using already verified proof. Old-head evidence
cannot certify a new head; negative pilot outcomes remain visible.

### Verified recovery and native provider evidence

An approved `scope_decision` may resolve only named historical escalation instances:
`resolves_findings` is a list of exact existing finding IDs, `binding` is the current
full session binding, and `closure_evidence_id` references prior passing reviewer
evidence. That evidence must explicitly `covers_findings` for every named ID; each must
have a genuine verified fixed disposition. Supply `approved_by`. Unknown, nonfixed,
uncovered or stale claims reject. The insertion-time binding is validated during
historical replay, so accepted closure survives later head adoption. Findings,
dispositions, investigations and counters remain; later or unlisted escapes cannot
inherit closure. Extending allowance alone never resolves a family.
The referenced findings must already exist when that closure is recorded. A later
nonfixed disposition or explicit failing/incomplete reviewer evidence covering the
same ID invalidates that closure for a subsequent resolution until fresh closure
follows. Unrelated events do not invalidate it. A known finding may be reviewed against
the corrected current binding before its administrative fixed flag is recorded;
there is no blanket requirement to record that flag before independent review.

When normal REST review submission is absent, passing existing reviewer evidence may
include `provider_completions`, for example:

```json
{
  "provider_completions": [{
    "reviewer": "chatgpt-codex-connector[bot]",
    "review_kind": "code",
    "source": "comment:123456",
    "report_sha256": "<current report_receipts comment SHA256>",
    "head": "<full independently verified current SHA>",
    "completed_at": "<verified ISO-8601 completion timestamp>"
  }]
}
```

Include this in an ordinary bound `evidence` event with `evidence_type: reviewer`,
`result: pass`, current `head`/`binding` and complete `reviewed_reports`. Independently
inspect the fetched source's code-review kind, full-head association and completion
time; the helper does not parse or authenticate arbitrary prose. A literal full SHA in
prose is unnecessary, but an ambiguous short SHA or unrelated security metadata cannot
establish the association. At recording, the helper retains selected fetched source
identity/author/digest plus the adjudicated head/time/kind in existing provenance.
Replay uses those facts offline; current use requires the fetched source to still
match. Normal REST remains preferred; no synthetic REST review is created. Positive
native evidence satisfies only the named provider's completion/freshness, never a
negative review, requested reviewer, failed/pending/missing check, unresolved thread,
local finding, report-coverage or changed-input obligation. This trusts the independent
adjudicator and existing checkout/GitHub identities, not hostile-source forgery defense.

### Bounded observation

Polling ignores incidental metadata changes. The omitted timeout now means one absolute
45-minute deadline from invocation, including requests/pagination/sleep; progress never
extends it. `--timeout-minutes N` explicitly selects a supported 1–30-minute inactivity
limit within that absolute bound. Zero retains one collection capped at 60 seconds.
Only meaningful changes are emitted. Actionable feedback, evidence ready for independent
adjudication, terminal status or deadline stops observation. Timeout returns pending/wait,
not a passing review or fabricated failure; no automatic requests/retries/extensions.

`watch --observe-only` permits collecting already-running checks at budget-only REPLAN,
while the authoritative status and counters remain unchanged. It does not mask a
simultaneous family escalation, input/evidence error, failed gate or actionable finding.
Exhaustion rejects new correction-batch/investigation records until an explicit allowance
extension; observation and bound adjudication consume no correction batch. Exact-limit
completion still requires every obligation; over-limit completion remains REPLAN.
Existing histories retain their original events, including administrative overcounts.

### Delegation evidence

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

`llms.txt` and the CLI reference are generated from local skill metadata, the
curated `quality/index.json` inventory and the actual CLI tree. Run `make generate`
when these inputs change and `make index BASE_REF=<base>` to check without writing.
Keep phase/capability descriptions current; future economic commands remain planned.
The normal test/CI gate checks output independently of pre-commit. Link checking
alone does not prove semantic freshness. See the [gate guide](../development/quality-gates.md)
for ownership/source mappings and content-bound documentation rationale records.

Pattern inspected on 2026-09-28 (Europe/Berlin): `specfact-cli-modules` at
`bdaab8a3fc48c7321d21127e2b0042946cd90bfa`,
`scripts/generate-command-overview.py` (render/check comparison),
`tests/unit/docs/test_llms_overview_freshness.py` (freshness guard), and
`docs/agent-rules/70-release-commit-and-docs.md` (metadata consistency).
ChangeCost currently generates only its foundation help/version surface; economic
commands remain unimplemented.

## Behavioral evidence and follow-up review

The [behavioral evidence pilot](../development/behavioral-evidence.md) adds a read-only
packet check alongside this existing session. Bind actual reports and the specification,
oracle, generator and configuration to inputs captured before each check. Review stable
intent once, then provide the actual delta, affected invariant/assumption mappings and
unresolved findings. Unknown dependencies, changed scope/entrypoints/trust boundaries
require broader review; an old packet cannot waive current-head final gates or reset
review budgets. Seeded faults are detector controls, not defects found in runtime.
