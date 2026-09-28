# Contributing to ChangeCost

ChangeCost is in pilot planning. The [approved backlog](openspec/CHANGE_ORDER.md)
authorizes specifications and tracking. Product implementation and live collection
require a subsequent request; research does not expand that authorization.

## Workflow

1. Read [AGENTS.md](AGENTS.md) and the applicable [agent rules](docs/agent-rules/INDEX.md).
2. Check `git status --short --branch`; preserve work belonging to others.
3. Use a focused branch (`codex/<topic>` for coding agents). Use a worktree when
   concurrent work needs isolation; a separate worktree is not mandatory.
4. For product behavior, agree scope, create an OpenSpec change, and follow
   spec → failing tests → implementation → passing tests. Record actual evidence.
5. Run `make check`; run language-appropriate gates and SpecFact review when
   source code exists. See the [quality rules](docs/agent-rules/50-quality-gates-and-review.md).
6. Open a focused pull request with scope, verification, limitations, and rollback.
   Archive completed OpenSpec changes with `openspec archive <change-id>`.

Documentation-only fixes need relevant checks, not artificial runtime tests.
Planning artifacts do not create a product release or prove runtime behavior.
Use conventional commit subjects such as `docs: ...`, `chore: ...`, or `fix: ...`.

## Agent workflow

Use these shared skills in agent chat; they are not terminal commands. Each stage
can run in a new session. Name the OpenSpec change after selection so later stages
resume the same work. Installing these skills does not authorize implementation.

| Stage | Example request | Result |
| --- | --- | --- |
| Prepare | `$changecost-prepare` — help me choose and refresh the next pending change | Reviewed plan and linked issue; asks whether to open a planning PR or save a scoped stash. |
| Implement | `$changecost-implement <change-id>` | Fresh baseline, matching prepared artifacts, minimal implementation, tests and docs. |
| Verify | `$changecost-verify <change-id>` — review, verify, commit and push | Scoped agent checks, local defect review, applicable SpecFact review, then a verified feature-branch push. |
| Promote | `$changecost-promote <change-id>` — create the PR and monitor/fix its reviews | PR to `main`, delegated review/check/fix loop; leaves merge to the maintainer. |

Start with [the shared workflow rules](docs/agent-rules/30-change-workflow.md).
Plans/specs and GitHub remain the work record. Small ignored receipts under
`.changecost/workflow/` record the change, baseline, exact stash ID and verification
state between sessions. A stash is local, not a backup on GitHub. A planning PR
does not close an implementation issue. The promotion stage reports missing bot
reviews or required checks as incomplete, not as a green review.

## Local checks

Follow [README setup](README.md#work-on-the-repository), then run `make check`.
Pre-commit may fix whitespace or final newlines; review the diff and rerun it.
Tool versions are pinned in `requirements-dev.txt`, `.pre-commit-config.yaml`,
and CI. Update pins deliberately and verify local/CI parity.

## Contributions and data

Contributions are provided under the repository's Apache-2.0 license.
Preserve applicable upstream notices and attribution. Review dependency licenses
before adoption; avoid dependencies for behavior the standard library clearly
expresses. No contributor agreement or sign-off requirement is added here.

Use synthetic examples. Do not commit credentials, prompts, source transcripts,
real billing exports, or identifiable session data. Report vulnerabilities through
[SECURITY.md](SECURITY.md), not issues or pull requests.
