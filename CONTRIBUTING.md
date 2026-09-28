# Contributing to ChangeCost

ChangeCost has an unreleased CLI foundation; economic operations remain in the
[approved backlog](openspec/CHANGE_ORDER.md). The maintainer authorized foundation
implementation on 2026-09-28. Other product work and live collection require a
subsequent request; research does not expand that authorization.

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

Follow [README setup](README.md#work-on-the-repository). Install actionlint 1.7.12
(for example `go install github.com/rhysd/actionlint/cmd/actionlint@v1.7.12`) and
put its binary on PATH. Install separate review tooling with
`uv tool install specfact-cli==0.55.4`, then
`specfact module install nold-ai/specfact-code-review --version 0.50.1`.
SpecFact remains outside package/runtime dependencies. Linux x86-64 is required
by its current analyzer capsules; missing coverage blocks full validation.

Use `BASE_REF=<resolved comparison commit> make check`. The base must cover the
whole proposed change: normally the merge-base with fresh main; CI resolves the
PR head/base or the main push event's `before` SHA. Never use an arbitrary last
commit as a substitute. Before staging new files, create and review an explicit
newline-delimited path manifest and pass `MANIFEST=<file>`; keep it under ignored
`.changecost/`. The manifest adds intended new files to tracked inputs, not private
artifacts. Commit hooks read the complete Git index in a temporary directory,
so unstaged corrections cannot pass for different staged contents.

`make format` writes formatting; `make generate` regenerates llms/CLI references.
`make lint`, `make types`, `make test`, `make docs`, `make index`, `make metadata`,
`make workflow`, `make build`, `make audit` and `make review` expose the same leaf
validators as CI. Diff-sensitive leaf targets require BASE_REF and any manifest.
`make check` also checks formatting, hygiene and all OpenSpec changes. An advisory
service failure is incomplete evidence, not a clean vulnerability result.

Update dependencies deliberately with `uv lock`; verification uses locked commands
and never refreshes the lock silently. Build constraints are generated from the
locked build group into a temporary file. Do not maintain requirements-dev.txt
or a second environment authority. See the [gate guide](docs/development/quality-gates.md)
for ownership, rationale formats, generated artifacts and review evidence.

## Contributions and data

Contributions are provided under the repository's Apache-2.0 license.
Preserve applicable upstream notices and attribution. Review dependency licenses
before adoption; avoid dependencies for behavior the standard library clearly
expresses. No contributor agreement or sign-off requirement is added here.

Use synthetic examples. Do not commit credentials, prompts, source transcripts,
real billing exports, or identifiable session data. Report vulnerabilities through
[SECURITY.md](SECURITY.md), not issues or pull requests.
