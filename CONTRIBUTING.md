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

For implementation/review work, initialize the bounded local review receipt with
`python -m quality.review_session init <change-id> --json <contract.json>`. It
keeps the complete scope, finding families and counters across chats and commits.
Use initialization only for a genuinely new session; recover lost or incompatible
receipts. Schema 8 replays original events with separately captured timestamps and
Git inputs, checking all cached decisions against that history. A durable genesis
marker detects a missing state file; preserve the entire ignored directory because
this local recovery guard is not a backup or a tamper-proof store.
The contract must name `required_checks` (nonempty), `required_statuses` (explicit,
possibly empty), and required reviewers. Missing declared results block completion.
It also names the exact repository; the first PR selection is retained. Reviewer
logins match REST identities exactly, including `[bot]`. See the complete
[contract example](docs/agent-rules/30-change-workflow.md#bounded-review-contract).
An `advance_head` event refreshes the Git HEAD, working-content and staged-index
binding. Supply both `comparison_base` and `pr_base` to explicitly adopt a changed
PR target. Schema-8 evidence events include the full binding captured before the
check; remote positive results must postdate base adoption. This retains history
and does not establish hostile-runner authenticity. The refresh preserves counters;
passing evidence from before that refresh
remains historical and cannot establish completion of the new inputs.
Record measured `active_minutes` explicitly after each input refresh, including an
actual measured zero when appropriate. The helper retains UTC receipt timestamps
without estimating activity from elapsed wall time. Latest current-head reviewer
rejections block completion; pending/dismissed results cannot reuse old approvals.
An effective changes-requested objection survives later comments, pending reviews
and dismissal of a different review. A later approval clears it; dismissal of the
original rejection is recognized from the complete fresh snapshot.
An outstanding request to a required reviewer keeps completion pending despite a
prior approval. Request metadata is validated at both collection reads; cancellation
does not replace approval or other current-context evidence.
Epochs derive from the count of recorded refreshes, not caller IDs. Automatic PR
binding selects an unused identity under the session lock. Preserve original IDs;
incompatible prior receipts require recovery without restarting the allowance.
Packets derive status and contents from one loaded receipt while still checking
actual input drift. Changed watcher output and exit decisions use that same packet.
Required event text, including extension approval identity, must contain non-whitespace
text; valid exact IDs and references are never trimmed or normalized.
Before recording passing reviewer evidence, explicitly adjudicate all current fetched
reports and supply their packet `report_receipts` mapping as `reviewed_reports`.
New or edited report content invalidates coverage; unresolved threads and local
findings still block independently. This is a trusted operator assertion, not
verification of GitHub resolver permissions. An exhausted budget permits exact-limit
completion only when no remaining family investigation is required. Minute grants,
active time and measured usage sum original components canonically; overflow rejects
the update atomically. Unmeasured usage remains unknown and batch counts stay integers.
Every refresh validates current changed-path coverage. Changing authorized paths
requires an explicitly referenced approved scope manifest; packets retain both
the original contract and recaptured current manifest.
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
Keep each observation's explicit `_input_epoch` captured before collection. Direct
ingestion never supplies the current generation for missing metadata; absent,
malformed or stale epochs persist as incomplete evidence, including the first generation.
Initialization verifies typed scope, full commit IDs and a path/SHA256 manifest
against actual initial inputs; `<absent>` represents an intended future file.
Changed, staged and untracked paths must be included. Captured initial facts remain
immutable through head refreshes; incompatible older schemas require recovery.
The same full hexadecimal commit-ID rule covers SHA-1 and SHA-256 repositories
through initialization, refresh and replay. Watcher terminal decisions are emitted
even when GitHub data is unchanged; the timeout boundary rechecks local budget
and scope before reporting a wait.
Dirty inputs may be reviewed locally but cannot establish published completion.
Non-findings do not seed family escalation; genuine fixed recurrences remain in
history. Investigate the first escape after correction and replan after a further
escape following that investigation.
At three correction batches, 90 active minutes, or an escaping investigated family,
create a packet and replan rather than continue a narrow fix loop.

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

The required tests leaf ignores inherited `PYTEST_ADDOPTS` so local or CI selection
flags cannot narrow the repository suite. It removes only that variable from a
copy of the pytest child environment. Repository pytest configuration, other
variables and the caller's environment remain intact; direct developer pytest
invocations may still use their usual filters. The required invocation explicitly
selects `pyproject.toml` with `-c`, so alternate root pytest configuration cannot
replace the canonical settings. Root `conftest.py` is still a supported Python
collection hook, and its changed content requires full review.


`make test` invokes the shared required tests leaf, including canonical
`pyproject.toml` selection and inherited `PYTEST_ADDOPTS` removal. This non-diff
leaf defaults its inventory baseline to HEAD; explicit `BASE_REF` and `MANIFEST`
are honored and validated. The aggregate still requires its explicit comparison
base. Use direct `uv run --locked pytest ...` for optional developer filtering.
