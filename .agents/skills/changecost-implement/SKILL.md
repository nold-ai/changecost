---
name: changecost-implement
description: Implement a selected ChangeCost OpenSpec change from fresh main, safely reconcile matching prepared artifacts, and deliver minimum sufficient code with TDD, current docs and llms.txt.
---

# Implement the selected change

Read `AGENTS.md`, `openspec/config.yaml`, the project brief, change order and
[shared workflow](../../../docs/agent-rules/30-change-workflow.md). Follow
[OpenSpec/TDD](../../../docs/agent-rules/40-openspec-and-tdd.md) and
[quality rules](../../../docs/agent-rules/50-quality-gates-and-review.md).
An implementation request authorizes the named change, not live provider data
collection, unrelated backlog items, releases or deployment.

Follow the canonical [review selection and live acceptance policy](../../../docs/agent-rules/30-change-workflow.md#review-selection-and-live-acceptance):
one upfront obligation review, affected-scope closure, Codex by default and additional
CodeRabbit for listed risks. Preserve mechanical gates and exact-head evidence; do not
add a generic full local/CLI review or a receipt-only commit by default.

## Establish fresh, matching inputs

1. Confirm the change from the request or preparation receipt. If ambiguous,
   show the relevant pending choices and ask; do not implement the newest stash
   or most recently modified change by default.
2. Refresh main using the shared protocol. Inspect linked issue status,
   prerequisites, recent merged work, existing feature/preparation branches and
   receipts. Recheck that the work is still needed and authorized.
3. Reuse a suitable owned `codex/<change-id>` feature branch, or create one from
   fresh main. Preserve existing commits and unrelated work; integrate updated
   main deliberately on an existing branch. Never implement on main.
4. If a matching prepared stash exists, inspect identity, recorded base, tracked
   and untracked contents, then apply its immutable OID using the shared recovery
   procedure. Keep it until verified/committed. If multiple stashes match, ask;
   if already applied, partially applied, superseded or merged, inspect the tree
   before taking another action. Do not apply a stash for another change.
5. If preparation is in an unmerged planning PR, do not pretend main contains it.
   Read the PR's current remote head SHA, fetch that head from the verified remote,
   and inspect its complete planning diff, including review follow-up commits.
   Record that SHA; fetching main alone does not refresh a local planning branch.
   Bring only
   the selected verified planning commits into the feature branch (merge or
   cherry-pick after ownership/diff inspection), or report a genuine dependency
   blocker. Revalidate the combined diff against fresh main. A merged plan needs
   no second application. Record how the final artifacts were obtained.
6. Recheck artifacts against current code and external evidence affected since
   preparation. Research uncertain/time-sensitive claims and reconcile within
   scope; a clean apply/merge is not semantic readiness. New product decisions or
   unmet prerequisites go back to preparation/clarification. Do not silently
   narrow required behavior to make implementation possible.

## Apply OpenSpec with small, testable steps

For a genuinely new review session, follow the complete contract example in
[the shared workflow](../../../docs/agent-rules/30-change-workflow.md) and run
`python -m quality.review_session init <change-id> --json <contract.json>`.
For an existing session run `python -m quality.review_session status <change-id>`;
missing or incompatible receipts require recovery, never a fresh allowance.
Record the
frozen intended result and collect independent lanes before a correction batch.
Classify each finding with concrete evidence, affected requirement and a family.
On the first genuine escape after a correction, investigate its invariant, variants, callers and
missing tests before another patch; an escape after that investigation requires
replanning. Do not reset counters by restarting a chat or pushing a commit.

Use the schema-aware mechanics of
[openspec-apply-change](../openspec-apply-change/SKILL.md):
`openspec status --change <id> --json`, then
`openspec instructions apply --change <id> --json`. Respect an explicitly selected
store. Read all returned context files plus applicable project `context` and
`operationGuidance`; keep those advisory fields separate from actual task state.
Honor blocked/all-done states and never infer completion from prose guidance.

For each scoped requirement:

1. Map its scenarios to the smallest meaningful tests. Record an expected failure
   caused by missing behavior before implementing; broken tooling is not that
   evidence. Pure docs/scaffold edits need relevant verification, not fake tests.
2. Implement the least code and fewest moving parts that fully satisfy the
   scenarios. Reuse existing contracts. Prefer direct data flow, focused functions,
   clear names and early exits over nested branching. Do not optimize line count
   by compressing readable code or dropping error handling, units or edge cases.
   No speculative framework, generic adapter, factory or dependency without a
   current requirement. Isolate distinct decisions before complexity accumulates.
3. Run the tests and configured format/lint/type checks for that slice. Where
   relevant tooling exists, use early complexity feedback and scoped SpecFact
   review to prevent a late rewrite; thresholds come from actual configuration,
   not invented LOC/cyclomatic limits. Missing tooling remains a limitation.
4. Record actual failing-before/passing-after commands, timestamps, scope and
   results in the change's `TDD_EVIDENCE.md`. Mark a task complete only when its
   full behavior is implemented and verified; keep review/push/PR tasks pending
   until those later stages actually happen. Do not archive unfinished work.

Persist while authorized tasks remain. On a real ambiguity, new scope, external
blocker or conflicting requirements, explain it precisely and continue independent
work where possible. Do not broaden the change to remove an inconvenient gate.

## Keep documentation and handoff current

Update user/developer docs, examples, spec/task descriptions and `CHANGELOG.md`
with behavior changes. Verify `llms.txt` inventory, phase and descriptions against
current files; add product commands only once implemented and verified. Use an
existing generation/check command when available. Apply actual version policy;
planning/scaffold changes do not invent a release or version bump.

Run selected strict OpenSpec validation and applicable `make check` gates. Inspect
the final diff for unnecessary branches, duplicate logic, speculative abstractions
and unrelated work before handing it to verification. Record the selected change,
fresh base, feature branch, prepared-artifact disposition, changed paths, actual
test/review evidence and unresolved limitations in a compact local receipt if the
next stage is in another session. Keep the existing specs/tasks as the work plan.

Finish with `$changecost-verify <id>` as the next stage. Do not commit/push, create
a PR or launch promotion merely because implementation finished unless the user
already requested those subsequent stages as well.

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
