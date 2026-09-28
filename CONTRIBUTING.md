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


The staged commit hook compares to HEAD when BASE_REF is unset; explicitly supplied
comparison bases remain authoritative. The lock leaf includes the real external uv
probe on the host; capsule unit tests verify its failure propagation. Local aggregate checks still require an
explicit base. Keep the locked development analyzer versions aligned with the
signed review capsule; see the [gate guide](docs/development/quality-gates.md).
When editing CI, preserve `contents: read` both at workflow level and in any
job permission override, including sibling jobs and additional workflow files.
Every `.yml`/`.yaml` workflow must declare this root policy and must not use
`pull_request_target`; legitimate read-only siblings need no quality-job matrix
or comparison resolver. Keep the canonical initial
checkout tied to the event head; CI checks actual HEAD before resolving its base.

Inspect and disposition nonblocking native review advisories even when full
assurance passes. `PASS_WITH_ADVISORY` is a supported successful native verdict,
not permission to ignore failed, unknown, stale or missing analyzer evidence.

Changes to `openspec/config.yaml` require full review even when no Python source
changes; this configuration influences the specification workflow and is not a
docs-only applicability exemption.

CI invokes the aggregate with `MAKEFLAGS`, `GNUMAKEFLAGS` and `MFLAGS` removed
from its environment so inherited ignore-errors options cannot turn gate failures
into success. Preserve this canonical command when editing the workflow; local
contributor commands remain `make check` with the explicit comparison base.

Root-relative input paths beginning with `-` are unsupported: pre-commit and its
hooks can interpret them as options. Rename these inputs before staging; deleting
one remains allowed. Nested paths such as `fixtures/--help` and root names such
as `.--help` are valid. The inventory, staged snapshot and direct hygiene leaf
reject unsafe current inputs with an explicit filename diagnostic.

The quality job explicitly defaults every run step to
`/bin/bash --noprofile --norc -p -e -o pipefail {0}` in the repository root
(`working-directory: .`). Preserve the exact template in defaults and any explicit
step shell. It ignores inherited Bash startup hooks/options/functions while
retaining fail-fast behavior. Bash's `-p` startup mode grants no OS privilege on
the ordinary equal-UID runner; it does not authenticate child tools or outputs.

Manual CI requires a resolved comparison base different from the tested head;
HEAD or an alias resolving to that head is rejected before export. PR and push
comparison rules and the ordinary staged-hook HEAD default are unchanged.

Keep the quality job's `UV_PYTHON` and every run step's explicit binding set exactly
to `${{ matrix.python }}`. Step bindings take precedence over earlier inherited
GITHUB_ENV values; action steps may omit the variable or use the exact expression.
The workflow gate requires the exact two-version Python matrix mapping, without
include/exclude entries or extra axes. Matrix labels alone do not prove the
intended jobs ran with their intended interpreters.

CI uses the pinned Ubuntu runner's `/usr/bin/env` and `/usr/bin/make` for the
aggregate. Do not set PATH directly in workflow, quality-job or quality-step
environments; the gate rejects those overrides. Normal bootstrap GITHUB_PATH
additions remain supported. Absolute launcher selection does not authenticate
a mutable host or its reports.

A manual comparison is operator-selected and controls changed-input applicability.
A distinct identical-tree base or docs-only interval may legitimately make behavior
checks not applicable. Such results are scoped evidence, not full ten-analyzer
assurance, and cannot replace a PR/promotion's required behavior review.
