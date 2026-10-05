# Repository quality gates

The foundation implements shared local, staged and CI validators in `quality/`.
They are development tooling and are excluded from distributions. `make check`
returns nonzero if any required child fails or cannot run. Python 3.11.15 and
3.13.14 use the same targets; OpenSpec 1.13.2, uv 0.12.19 and actionlint 1.7.12
are bootstrap pins. The actionlint version check accepts the release/Homebrew
`1.7.12` and Go-module `v1.7.12` spellings only. The lock resolves Python runtime, dev and build dependencies.
The dev group includes the test tools and pins uv so isolated repository tests can
invoke it. Host typing uses BasedPyright 1.40.1; its Node wheel remains constrained
to 24.16.0. The separate test group lets SpecFact 0.50.1 retain its signed
BasedPyright 1.39.10 analyzer without a conflicting project copy. These are
development dependencies; analyzer coverage and type-checking rules remain intact. Pytest
explicitly imports repository helpers from the checkout root; they stay outside
the distributed package.
The test group locks pytest-xdist 3.8.0; repository pytest configuration runs the
complete suite with four local workers using load distribution. Each worker retains
its isolated fixtures. The signed native observer supports distributed collection
and terminal reports, while the coverage adapter combines worker coverage and
rejects worker errors or missing coverage. Selection, required analyzers, enforcement
and the native launcher's deadline are unchanged. Fresh Linux reports must show
complete target execution and passing combined coverage; host timing alone does
not establish assurance. Sources accessed 2026-10-05 (Europe/Berlin):
[worker distribution](https://pytest-xdist.readthedocs.io/en/latest/distribution.html),
[combined coverage](https://pytest-cov.readthedocs.io/en/stable/xdist.html).

CLI tests resolve the active environment’s console script
from PATH, and the wheel proof puts its clean installation first.

## Inputs and comparison

Supply `BASE_REF` explicitly for local aggregate/manual review and CI. The staged
commit hook alone defaults an unset base to HEAD and preserves explicit overrides.
A PR checks its head and the merge-base with
the event base; main pushes use the event's before SHA, including all commits in
the push. Manual CI requires a comparison SHA distinct from the tested head. Equal-head
manual bases fail before BASE_REF is exported; PR merge-base, push-before and
staged-hook HEAD semantics are unchanged. The operator-selected manual comparison
controls changed-input applicability. A valid distinct commit with an identical
tree, or a docs-only interval, can legitimately report behavior gates as not
applicable. That result is scoped comparison evidence, not full ten-analyzer
assurance, and cannot replace the required behavior evidence for a PR/promotion.
The manual input is not a trusted-main policy; rejecting only identical trees
would not establish a trusted interval. Missing history fails. Local
`make check` reads tracked working files plus an explicit `MANIFEST` for intended
new files; it refuses implicit omission when untracked files exist. Unrelated
private `artifacts/` directories are ignored at every depth. Every nonempty manifest
entry must name an existing regular file; missing paths and directories are rejected
by name. Valid manifests may intentionally exclude unrelated untracked files.

The commit hook materializes Git index blobs into a temporary directory and runs
the staged validator code there. It checks staged additions, removals, renames and
links without stashing or modifying user files. It cannot read an unstaged fix or
untracked link target as part of the commit. Fast hooks run lock, lint, typing,
docs, generated-index, metadata and workflow checks. The required lock leaf runs both `uv lock --check` and the real offline
missing/stale/repaired lock proof in `tests/tool_probes.py`. That host-side proof
also runs inside staged snapshots. Complete CI runs tests, build proof, dependency
checks and applicable review too. Hygiene hooks have a
separate shared configuration to prevent aggregate recursion.

## Documentation ownership

`quality/docs.json` lists each maintained Markdown document and llms.txt once,
with a logical owner, manual/generated kind and canonical source path/globs.
New pages need an entry; empty/orphaned sources, duplicate owners and broken
local links/anchors fail. OpenSpec and skill documents are included. The two
original research exports have exact path/hash/reason exemptions; their bytes
are checked, not rewritten. License text is shipped verbatim and excluded from
Markdown analysis because it is not a maintained Markdown page.

Changed sources require a changed corresponding document, or a reviewed entry
in `quality/exceptions.json` keyed by document path:

```json
{"docs/example.md": {"reason": "Specific reason the source change needs no prose change", "digest": "sha256 of the complete mapped source contents"}}
```

Use `quality.repository.digest(root, source_paths)` to compute the binding.
Include path identity and deleted source paths; exclude the target document,
the rationale file and generated llms/command output. Rationale wording remains
a review responsibility. A different source digest invalidates the rationale.
The checker proves structural coverage and detectable drift, not prose accuracy.

## Generated references

`quality/index.json` supplies curated documentation entry points. The renderer
reads local skill frontmatter and the real Typer command parameters; it writes
`llms.txt` and `docs/commands.md` deterministically with `make generate`. Checks
are read-only and show a diff for missing/stale output. Duplicate/dangling inputs
fail. Normal tests run integrity checking even if pre-commit is bypassed. Future
cost commands are labeled as planned, never fabricated as working commands.

## Changelog and versions

`pyproject.toml` owns version 0.1.0.dev0. CLI version comes from installed metadata;
checks compare the project entry in uv.lock, built wheel/sdist and installed CLI.
Initial metadata is valid without inventing a prior release. Versions may not
decrease; ordinary unreleased work does not require a bump or PyPI lookup.
Changed behavior/workflow/contracts need a new substantive Unreleased entry.
An editorial/test-only exception uses key `changelog`, a specific `reason` and
the digest of the changed paths excluding CHANGELOG.md and the rationale file.
Old entries or dates alone fail. Human review still judges whether wording is useful.

## Build and dependency proof

The build gate exports hash-pinned build constraints from uv.lock, builds a wheel
through the sdist, checks archive members/version/license, installs in a clean
runtime-only environment, and runs help/version/error tests outside the checkout
with network attempts blocked. It rejects contradictory build constraints.
Package installation/auditing can use the network; CLI execution and generation
are offline. No publication target or deployment job is provided.

The advisory gate audits exported locked runtime/dev/build requirements using
pip-audit and records `.changecost/dependency-audit.json`; missing data fails.
Installed locked license metadata (release-specific PyPI metadata for dependencies
absent on this platform) is recorded in `.changecost/dependency-licenses.json`
and missing evidence fails. Marker-split locks retain one evidence row per package
version: installed metadata is reused only for an exact version match, with other
versions fetched from their exact release metadata. An installed version outside
all locked alternatives still fails. Review the actual license report before accepting new
dependencies; metadata reporting is not legal advice or a compatibility guarantee.

The workflow unit tests isolate the actionlint process boundary and exercise
syntax-failure propagation and conditional-gate rejection. The required workflow
leaf still runs real actionlint; verification also executes a malformed-and-repaired
workflow against that binary. Capsule tests do not depend on a host Go binary. The same boundary applies to uv
interpreter probing: the attached capsule interpreter rejects uv's `-I` probe,
so the real external lock proof runs unconditionally in the host lock leaf. Pytest
checks propagation of both lock-command and probe failures. No test is marked
skipped/xfail and no capsule runtime protection is changed.

## Bounded review sessions

`python -m quality.review_session` is local contributor tooling. It stores a
versioned, atomic session record under `.changecost/workflow/<change-id>/`; that
directory is ignored and is not a substitute for committed specifications or test
evidence. Initialize it with a JSON contract that records requirements, acceptance
criteria, non-goals, trust boundary, complete input fingerprints, base, head and
the required GitHub reviewer logins, nonempty `required_checks` names and explicit
`required_statuses` contexts (which may be an empty list). These identities are
declared review policy; do not infer protected-branch settings from them. Missing
declared checks or statuses leave the session pending even when API pages are empty.
Name the exact repository and REST reviewer logins, including `[bot]`. The first
PR selection becomes immutable. Schema-8 canonical replay reconciles all derived
fields with original events and separately captured time/input facts. Minute budgets,
active time and measured usage use finite canonical sums of their original components;
overflow rejects the update without changing the receipt. Batch counts remain integers,
and unmeasured usage remains unknown. Preserve the
genesis marker and state together; lost or incompatible history requires recovery,
not another allowance. The marker detects state-file loss, not full-directory
deletion or hostile tampering. See the
[complete contract example](../agent-rules/30-change-workflow.md#bounded-review-contract).
Every refresh validates current changed-path coverage. Changing authorized paths
requires an explicitly referenced approved scope manifest; packets retain both
the original contract and recaptured current manifest.
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
Initialization validates nonblank typed scope, full existing commits and safe
path-to-SHA256 fingerprints against actual inputs. `<absent>` explicitly permits
future planned files. Cover all changed, staged and untracked paths while allowing
unchanged intended files. Captured initial scope facts remain immutable through
head refreshes and are validated without filesystem access during replay. Existing
schema-1/2/3/4/5/6/7 receipts require recovery rather than synthesized migration.
Contract and refresh paths use one full hexadecimal commit-ID rule for 40-character
SHA-1 and 64-character SHA-256 repositories. Shape validation does not replace
checking the actual Git head; pure replay retains the same identity rule.
Tracked assume-unchanged and skip-worktree entries are unsupported. Initialization,
head refresh and final input/status checks reject those flags without changing the
index, because Git's reported change set and clean state may conceal file edits.

The helper reports `continue`, `wait`, `investigate`, `replan`, `incomplete` or
`complete`. The defaults are three collected correction batches and 90 active
minutes. A finding arriving after a family's correction requires investigation; an escape after investigation
requires replanning. Budget extensions require an explicit maintainer identity and
do not reset counters. The packet command preserves only compact scope, unresolved
findings, evidence, investigations and separated cached-input, uncached-input,
output and cost measurements. Missing measurements remain unknown.

Initialization captures the real Git HEAD, tracked/untracked input contents and
staged Git blob identities and file modes.
`status` rejects changed inputs. Record an `advance_head` event with the new local
commit to refresh that binding explicitly, preserve history and counters, and clear
the previous monitor and completion phase. Prior passing evidence remains in history
but is invalidated, including on a same-head input refresh. Missing input bindings
or gate-identity configuration require recovery.
Evidence events use `kind: "evidence"` with a separate `evidence_type` of `gate` or
`reviewer`, their `head`, `result` and explicit `binding` copied from the reviewed
packet: head, input digest, epoch, comparison base and PR base. Capture that binding
before running the check, not when ingesting its result. A stale payload with a new
event ID is rejected. The latest result for each category applies.
The contract's `base` is the immutable initial comparison commit; required
`pr_base: {"ref": "main", "sha": "<full target-tip SHA>"}` independently records
the expected PR target. Snapshots check the target ref and SHA before and after
collection. Retargeting or target advancement leaves evidence incomplete.
Explicitly adopt a reviewed context through `advance_head` with both
`comparison_base` and `pr_base`; both referenced commits must exist locally. The
Base IDs must name commit objects exactly; annotated-tag object IDs are rejected
rather than silently peeled into different identities. The atomic update preserves
the original contract and counters, while creating a new
input epoch and invalidating local evidence, timing and monitor completion even
when HEAD is unchanged. Packets expose both original and current context.
After adoption, required checks' `started_at`, statuses' `created_at` and positive
reviews' `submitted_at` must be at or after the separately captured adoption time.
Missing, invalid or older timestamps leave completion pending; existing current-head
objections still block it. Timestamp freshness is a workflow bound, not proof that a
remote runner actually evaluated the new merge context. SpecFact's content digest
remains separate evidence and does not authenticate that context.
A scope resolution names the pending event's identity in `supersedes`.
Completion requires a complete current-head monitor snapshot as well as passing
local evidence. Pending checks, commit statuses, reviewers and unresolved threads
(including outdated threads) block completion. Exhausted budgets take precedence
over waiting; a fully verified final allowed batch may complete.
That exact-limit exception does not permit further family investigation: if an
otherwise complete session still needs investigation, either exhausted budget
requires replanning. Extensions must cover every exhausted budget axis.

Resolved remote threads require explicit local adjudication coverage, rather than
trusting GitHub resolution flags alone. A packet's `report_receipts` maps stable
namespaced `thread:<id>`, `review:<id>` and `comment:<id>` identities to deterministic
SHA256 digests of exact bodies and stable context across every collected page. After actual triage, the trusted coordinator records
that exact map as `reviewed_reports` on its binding-qualified reviewer evidence event.
Known local defects still require their separate finding/disposition records.
New/edited comments, added threads, extra stale coverage IDs or changed input/base
bindings prevent completion until revalidated. Missing coverage cannot cover any
nonempty report set; only the no-report case permits empty coverage.
Malformed/error observations expose no usable packet receipts. Supplied mappings
are validated at ingestion and replay; observations never fabricate acknowledgment.
Unresolved threads, including outdated ones, always block. Resolution/outdated flags
are separate from report content: an unchanged report reopened then reclosed under
the same input binding may reuse its explicit adjudication. Only observed status is
known; no unobserved transition guarantee is made. This is local operator attestation,
not independent verification of resolver permissions or protection from a dishonest
operator. Authorized PR-author resolution remains supported; no role lookup is added.
Completion also requires an `active_minutes` event with explicit finite nonnegative
`minutes` after the latest binding refresh. Missing timing remains unknown; measured
zero is allowed. Separate UTC recording timestamps preserve measurement provenance
and idempotent ingestion, without inferring active time from wall-clock duration.
For each reviewer, the effective current-head objection applies: CHANGES_REQUESTED blocks
even without inline comments; a required reviewer with PENDING or DISMISSED cannot
reuse an older approval. APPROVED and COMMENTED satisfy reviewer completion only.
An earlier rejection survives later COMMENTED/PENDING rows and dismissal of a
different review. A later APPROVED row clears it; a complete fresh snapshot can
also show the original rejecting review itself changed to DISMISSED.
Unknown or malformed review states make the observation incomplete rather than
overwriting a prior rejection, for required and other reviewers alike.
Outstanding requests to required reviewers also leave completion pending, even
after a prior same-head approval or comment. Every snapshot requires a validated
requested-user array with exact logins, including bot suffixes. Collection compares
normalized requested identities at both metadata reads; additions/removals invalidate
the observation. Order, duplicates and avatar changes are semantically quiet.
Nonrequired requests remain informational; team membership is not expanded.
Cancellation only restores still-qualifying evidence and cannot override rejection,
head/base freshness or budget limits. Older snapshots missing request data become
incomplete under schema 8; no new session allowance is created.
Input epochs use `input-generation:N`, starting at zero and advancing only for
recorded `advance_head` events. Caller IDs, ordinary events, monitor revisions and
exact retries cannot change or collide with that generation. Positive monitoring
requires the observation's explicit collection-time `_input_epoch`; direct ingestion
does not fill missing metadata. Missing/null/malformed/stale epochs, including at
generation zero, persist as incomplete observations and replace previous green
evidence. The collector captures its epoch before network calls; a same-head refresh
during collection makes that observation stale. Error observations without an epoch
remain storable incomplete evidence and expose no usable thread receipts.
Automatic PR binding
selects the first unused `bind-pr`/`bind-pr:N` event ID while holding the same session
lock through persistence. Caller IDs are not reserved or rewritten; same-target
binding is idempotent and conflicting targets are rejected. Preserve incompatible
old epoch histories for recovery rather than synthesizing a new allowance.
Packets load one receipt and derive status and body from that state while retaining
the actual Git/input drift check. When the watcher emits a changed packet, its exit
decision and associated snapshot come from that same packet rather than separate
receipt reads. Later concurrent writes remain a later revision, not mixed evidence.
Required event identities and semantic strings must contain non-whitespace text,
including Unicode whitespace handling; supplied `supersedes` references follow the
same rule. Valid padded or internal-space identities stay byte-for-byte exact, with
no trimming or family-label aliasing. Replay enforces the same validation. Free-form
GitHub comment bodies keep their separate rules and may be empty.

The optional watcher uses paginated read-only `gh api --paginate --slurp` requests for current checks,
statuses, reviews and issue comments, plus GraphQL `reviewThreads` and their
comments to retain resolved/outdated thread state. The slurped REST result is parsed
as one complete JSON document, not physical lines. It never pushes, replies,
resolves a thread or requests a review. Unchanged snapshots are suppressed; API
or GraphQL failures make the session incomplete. The helper cannot authenticate a
hostile runner or prevent arbitrary model calls outside this workflow.
"Read-only" describes GitHub operations, not local code isolation: invoking this
helper executes checkout-controlled Python with the operator's privileges and
credentials. This contributor workflow assumes trusted local code; running hostile
PR code safely requires a separate external-verifier architecture decision.
It polls changed nonterminal state with 15/30/60-second backoff and returns a
`wait` handoff after at most 30 minutes without progress; that wait never resets
the correction-batch or active-time budgets.
Local complete/investigate/replan/incomplete decisions are emitted once even when
the remote snapshot is unchanged. At the deadline, the watcher rereads local
status before reporting wait; a budget exhausted during sleep returns replan.
Incomplete retains exit status 1; other documented terminal/wait results retain 0.
Requests and pagination share the remaining deadline; sleep is capped accordingly.
Zero timeout means one collection with a 60-second cap. Progress hashes exclude
incidental avatar metadata. A snapshot binds repository, PR, head, target base and input epoch;
collection errors invalidate previous green evidence. Refreshed inputs
cannot inherit a collection that started before their input refresh. Nested thread
and comment fields are validated before completion; malformed optional event
references are rejected before persistence. An exact successful event retry retains
its result even with the original expected revision; new writes still conflict.
Dirty local review inputs
cannot complete publication. Final non-findings do not seed family escalation,
but fixing a genuine recurrence preserves its escape history.
Some providers publish a clean summary without a REST review: the helper remains
pending. Coordinators may separately verify provider output against the current
head, but must disclose the helper's missing evidence rather than infer approval.

### Cross-family reviewer calibration

`qwen3.8:27b-mlx` is a local candidate, not a validated review lane. Before an
advisory pre-PR use, give it three concealed historical defect cases and repaired
controls in fresh contexts. Record defect detection, actionable false positives,
timeouts, latency and available usage units. Allow 90 seconds per case and ten
minutes total. Adopt it only when it detects at least two defects, produces no
actionable false positives on the repaired controls, and completes within budget.
Failure or unavailable access leaves cross-family review unvalidated; it does not
block promotion or trigger a provider installation campaign.

Full review enables `--bug-hunt`, including the required semgrep-bugs member.
`[tool.specfact.code-review]` declares native Git for index tests; pytest’s
`pythonpath` supplies the repository import root. These declarations repair
known setup defects but do not prove capsule execution on an unsupported host.

SpecFact CLI 0.55.4 and review module 0.50.1 produce the native ignored
`.specfact/code-review.json`. The runner binds its scope to a digest of the complete
input set in a sidecar and checks actual required analyzer states and assurance.
Behavior-affecting source, tests, dependencies, validator or CI edits require review;
changes to `openspec/config.yaml` or either pre-commit configuration, including
the shared hygiene policy, also require review. Docs-only work states non-applicability and still runs its gates. Missing/skipped
analyzers fail. The manual hook alone is not review completion.

The default `dev` dependency group includes `test` and BasedPyright 1.40.1;
locked local and CI typing use that current project tool. SpecFact module 0.50.1
auto-selects the explicit `test` group and syncs it with `--no-default-groups`,
so its project runtime receives all existing test dependencies without installing
a second BasedPyright. The required capsule analyzer remains its signed 1.39.10
version. This separation avoids the module's pinned-analyzer conflict check;
it preserves every required analyzer and full enforcement. Native execution of
this composition must still pass on the current PR head in the Linux CI matrix.

Review capsules currently need a Linux x86-64 controller. Local macOS results
are UNKNOWN, not PASS. The gate must remain nonzero until the supported runtime
produces complete evidence; no fabricated runtime descriptor or bypass is allowed.
No branch-protection, paid infrastructure, provider collection or deployment is
configured by these files. Revert the foundation changes and recreate the prior
development environment to roll back, preserving all local evidence.


For core-01-python-foundation, the maintainer accepted the known Mac capsule
limitation on 2026-09-28 and deferred that assurance to GitHub CI. Local UNKNOWN
reports remain incomplete evidence. Passing local checks and independent reviews
permit this change’s commit/push handoff; the enabled full CI review must still
execute successfully before claiming merge readiness. This decision does not
turn an unavailable analyzer into a pass or disable the CI gate.


## Hosted capsule prerequisite

CI pins Ubuntu 24.04 and assigns a fresh job-local capsule cache under RUNNER_TEMP.
Before review, it loads an AppArmor profile granting `userns` to that cache's
`**/opt/specfact/bin/bwrap-static` launcher. Installation and all analyzers remain
ordinary-user processes; only loading/removing this profile uses administrator
privilege. The global AppArmor user-namespace restriction is checked to remain
enabled. The job removes its profile after checking and retains only native
review JSON plus the content-binding sidecar as a seven-day CI artifact.

This adapts the public SpecFact customer workflow's prerequisite, not its corpus
wrappers or privileged legacy smoke jobs. Ubuntu explains that the default profile
can permit namespace creation while denying later capabilities, so a loopback
`RTM_NEWADDR` permission failure is consistent with this restriction. Sources
checked 2026-09-28: [Ubuntu 24.04 release notes](https://documentation.ubuntu.com/release-notes/24.04/#unprivileged-user-namespace-restrictions)
and [SpecFact customer workflow at b3ca3014](https://github.com/nold-ai/specfact-cli-modules/blob/b3ca3014c8d0e064b860856d4b560a2591999532/.github/workflows/capsule-customer-execution.yml).

The first ChangeCost CI run failed during offline capsule installation and rejected
the Go-build actionlint spelling. Run 36427023807 at `086e8fd` passed workflow
validation and executed capsules on both Python versions, exposing complexity,
coverage, a capsule-only uv fixture failure and an analyzer dependency mismatch.
Full review remains incomplete until those findings pass current-head CI. If namespace setup
still fails, preserve the native report and investigate the runner denial rather
than disabling global restrictions, using root analyzers or skipping review.
Rollback removes the prerequisite step/profile and restores a failing incomplete
review gate; no host policy on the contributor's machine is modified.


The cache attachment is path-based and is not an authentication boundary: another
host process could replace a matching file. This job uses a fresh GitHub-hosted
VM where repository-controlled uv/build/tests already run as a user with
[passwordless sudo](https://docs.github.com/en/actions/reference/runners/github-hosted-runners#administrative-privileges)
(checked 2026-09-28). SpecFact verifies the signed launcher digest and executes the
same open descriptor for its own invocations; that does not authenticate arbitrary
host invocations. Capsule candidates receive read-only source/runtime mounts and
writable output/tmp, not the host cache. The profile therefore supplies the required
namespace prerequisite within this existing disposable-host trust model; it is not
a new isolation boundary against a hostile host process. Do not reuse this setup
on a shared or privileged persistent runner. An immutable external launcher would
require upstream supported configuration absent from module 0.50.1.

Failure-path unit tests use synthetic metadata, archives and injected subprocess
outcomes to exercise diagnostic branches offline. They complement the real build,
audit, actionlint and installed-CLI gates; their coverage percentages do not prove
network service availability or real capsule execution. In-process CLI tests also
cover help/version/errors and the module entrypoint; isolated subprocess proof remains.


CI comparison wiring is checked against the small reviewed event-based resolver
and its exact event inputs. Workflow/job/step BASE_REF overrides, another explicit
BASE_REF export, a conditional or moved resolver, or replacing its script are
rejected. This is a conservative contract for the current workflow, not a general
shell-program verifier. Ordinary staged hooks still accept their HEAD default.

Same-head CI is contributor quality evidence, not a tamper-proof attestation
against malicious pull-request code. The pull request supplies the workflow,
validators, project dependencies and report-binding code on the same host. A
malicious host process could replace PATH tools or forge reports regardless of
using an absolute launcher path. Signed capsule verification protects genuine
SpecFact execution; it does not authenticate an arbitrarily replaced controller.
The current workflow has no protected out-of-band verifier or malicious-PR
attestation claim; repository review remains necessary.


External SpecFact, actionlint and OpenSpec executables are resolved once per gate
invocation to their absolute symlink-resolved paths. A target inside the repository
or active project Python environment (`sys.prefix`, including a custom environment
outside the checkout) fails explicitly; a later PATH entry is not silently used.
Install these external validators outside that environment to repair a collision.
Project-managed uv, Ruff and BasedPyright remain locked project dependencies. This
guard prevents accidental project-environment collisions, not hostile-PR forgery.


Every job in the quality workflow may inherit root `contents: read` permissions
or repeat that exact permission map. This includes newly added sibling jobs.
Job-level write permissions and other overrides are rejected regardless of job
name, because GitHub job permissions replace the workflow-level setting.


The host lock fixture uses a project-version change with no dependencies, so the
stale metadata remains resolvable offline. It verifies that `uv lock --check`
fails without changing lock bytes, restoring metadata passes unchanged, and
ordinary `uv lock` can update that same drift before a subsequent check passes.
This distinguishes lock freshness enforcement from dependency resolution failure.


SpecFact module 0.50.1 declares PASS, PASS_WITH_ADVISORY and FAIL native verdicts.
Its authoritative report projection maps passing assurance with findings to
PASS_WITH_ADVISORY and exit code zero; findings remain in the report. The wrapper
accepts either successful verdict only when the content digest matches, assurance
is PASS, required evidence is not unknown, all required analyzers ran with PASS
outcomes, and the native exit code is zero. Required execution still invokes full
enforcement. Advisory success does not waive those checks or advisory disposition.


The quality workflow must begin with exactly one unconditional, pinned checkout
using the event's pull-request head or event SHA, full history and no persisted
credentials. Its resolver compares actual Git HEAD to that expected event head
before exporting any comparison base. Thus accidentally checking out the base
commit fails at runtime even before the repository validator can run. The
prospective YAML check also rejects checkout drift; this is a contract for the
reviewed workflow, not a verifier for arbitrary shell commands or hostile hosts.


Native analyzer status and promotion review completion are separate contracts.
The automated adapter validates the complete native result and preserves its
findings; it does not manufacture human dispositions or block native advisory
success while a reviewer works. Before the PR review loop is declared complete,
every finding must be fixed or have a reviewable, scoped disposition without an
outstanding dispute. The [record for reviewed commit d48b830](../../openspec/changes/archive/2026-09-29-core-01-python-foundation/ADVISORY_DISPOSITIONS.json)
publishes each advisory's identity, source report hashes and explicit rationale.
It covers only those reports. Later report-bound dispositions or deltas may be
recorded in the PR so recording evidence alone does not require another source
commit. A green native check does not complete this review obligation.

The shared token/event policy applies to every discovered `.yml` and `.yaml`
workflow: explicit root `contents: read`, inherited or identical job permissions,
and no `pull_request_target`. Diagnostics identify the offending workflow.
Quality-specific matrix, checkout and comparison wiring remain requirements of
`quality.yml`; unrelated read-only workflows do not need that foundation schema.

The canonical CI aggregate command is
`/usr/bin/env -u MAKEFLAGS -u GNUMAKEFLAGS -u MFLAGS /usr/bin/make check`. It removes Make flag
variables inherited from workflow, job, step or earlier runner setup before Make
starts. Required wiring validation rejects a bare command or partial removal of
this protection. This preserves failing recipe exit status; it does not attest a
hostile controller or reinterpret arbitrary workflow shell programs. On the
pinned Ubuntu runner, the absolute env/Make paths avoid selecting these launchers
through PATH. The workflow gate also rejects direct PATH entries at workflow,
quality-job or any quality-step scope. Normal bootstrap additions through
GITHUB_PATH remain supported. These are configuration constraints, not an
integrity guarantee for host binaries, downstream tools or reports.

Current root-relative paths beginning with `-` are rejected before input acceptance
or direct hygiene invocation, including a normalized `./--help`. Prefixing alone
is insufficient: pre-commit normalizes filenames again before passing them to
individual hooks. The always-run staged repository-contracts hook rejects these
index entries even if an earlier hygiene hook interprets the name as help.
Rename or delete the input; deletion is a valid repair. Nested `fixtures/--help`
and root `.--help` remain ordinary filenames and are allowed.

The quality job declares `defaults.run` with
`shell: /bin/bash --noprofile --norc -p -e -o pipefail {0}` and
`working-directory: .`. Validation requires this exact job declaration, allows
absent or identical workflow defaults, and checks every quality run step for
conflicting shell/directory overrides. Matching aggregate text alone does not
prove its script will run in the intended context. This is static configuration
validation and does not authenticate a hostile runner or general shell program.

The [GNU Bash manual](https://www.gnu.org/s/bash/manual/html_node/The-Set-Builtin.html)
(accessed 2026-09-28) documents that startup `-p` ignores BASH_ENV/ENV files,
inherited shell functions, and environment SHELLOPTS, BASHOPTS, CDPATH and
GLOBIGNORE. This applies regardless of whether the environment came from a direct
YAML entry or a previous GITHUB_ENV export; no producer script parser is used.
[GitHub's custom-shell contract](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#custom-shell)
(accessed 2026-09-28) supports the command/options/`{0}` template. Explicit `-e`
and `-o pipefail` preserve fail-fast behavior when replacing its built-in Bash
invocation. This shell mode does not acquire operating-system privileges: the
ordinary runner retains its equal real/effective UID. It does not protect child
interpreters' startup, host binaries or report authenticity. GITHUB_PATH and
normal environment values remain available. Static YAML mutation/repair tests
cover the template; no adversarial startup script was executed locally, and fresh
hosted CI must establish normal execution on the pinned Ubuntu runner.

Python matrix validation requires exactly `python: ['3.11.15', '3.13.14']`, with
no include/exclude entries or additional axes that change the expanded jobs. The
quality job and every run step explicitly bind `UV_PYTHON: ${{ matrix.python }}`;
action steps may omit it or use that exact expression. This supersedes the earlier
blanket prohibition on step entries. GitHub's [step environment precedence](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_idstepsenv)
(accessed 2026-09-28) and its [runner implementation](https://github.com/actions/runner/blob/main/src/Runner.Worker/StepsRunner.cs)
show global environment values being merged before evaluated step entries. The
[environment-file handler](https://github.com/actions/runner/blob/main/src/Runner.Worker/FileCommandManager.cs)
places earlier GITHUB_ENV values in that global environment. Explicit step bindings
therefore restore the matrix value without parsing earlier commands. Static tests
check removal, substitution and repair. Fresh CI must prove normal matrix execution;
these constraints do not authenticate arbitrary host code or child tools.


The required `tests` leaf starts pytest with a copied environment excluding only
`PYTEST_ADDOPTS`. The [pytest environment reference](https://docs.pytest.org/en/stable/reference/reference.html#envvar-PYTEST_ADDOPTS)
(accessed 2026-09-28; locked pytest 9.1.1) documents that this variable prepends
command-line options, which can select files or filter tests. Clearing it at the
subprocess boundary handles local, workflow, job and earlier GITHUB_ENV inheritance
without a YAML blacklist. Repository configuration and all other environment
values remain available; the parent environment and non-test gate subprocesses
are unchanged. This preserves the requested full-suite invocation, not a claim
that arbitrary plugins or host code are authenticated. Direct developer pytest
commands can continue to use selection options.


The tests leaf explicitly passes `-c pyproject.toml`. Pytest's
[configuration discovery rules](https://docs.pytest.org/en/stable/reference/customize.html#finding-the-rootdir)
(accessed 2026-09-28; locked pytest 9.1.1) otherwise prioritize root `pytest.toml`
and `pytest.ini` over pyproject settings. Explicit selection prevents these
alternate files from replacing the required gate's canonical configuration, while
preserving its settings. It does not disable Python hooks: a root `conftest.py`
can change collection through a documented
[collection hook](https://docs.pytest.org/en/stable/how-to/writing_hook_functions.html).
Changes to that root hook therefore require full review, like changes under
`tests/`; unchanged content does not. No additional config parser, filename ban or
plugin-authentication guarantee is introduced.


The public `make test` target routes to the same `quality tests` leaf used by
`make check`, without duplicating config or environment handling. It defaults
only this non-diff target's inventory base to HEAD and preserves explicit
BASE_REF/MANIFEST validation. Aggregate comparison semantics are unchanged.
Direct developer `uv run --locked pytest ...` remains available for filtered runs.

The mandatory host probe invoked by the lock leaf also runs the actual copied
Makefile in a disposable Git fixture with two tiny tests. Both inherited filters
and an alternate pytest config must expose the failing required test; repairing
it passes, and invalid explicit base/manifest inputs fail. It uses `UV_NO_SYNC=1`
only inside that fixture to reuse the already synchronized host environment
without modifying dependencies; the required locked-sync gate still runs. This
external uv/Make proof stays outside capsule pytest because the capsule runtime
does not support uv's isolated interpreter probe. It remains mandatory in local
lock/aggregate checks, staged hooks and CI, with failures propagated normally.

The Core-02 installed-package proof also exercises offline registration, lifecycle
declaration and artifact replay outside the checkout. Pydantic 2 is a locked runtime
dependency; SpecFact remains excluded. See [contracts](../contracts.md).

For local macOS work, native SpecFact capsule assurance is performed by GitHub CI/CD.
Run the applicable local leaves and staged commit checks, then push the reviewed
feature branch and manually dispatch Repository quality with its full comparison
base. Feature-branch pushes alone do not trigger this workflow. Keep full assurance
pending until the Ubuntu matrix and native reports pass; a local unsupported report
is neither a native pass nor a reason to attempt local capsule execution repeatedly.

Contributor review can use the [behavioral evidence pilot](behavioral-evidence.md) for bounded
lifecycle controls and content-bound delta review. Final required gates remain mandatory.

## Privacy-safe runtime timeout diagnostics

The existing Repository quality workflow collects a small metadata diagnostic
before its always-run evidence upload, including when native review fails. It
matches the report's supported `project-runtime-layer-v2` identity to one bounded,
one-level cache descriptor and verifies the canonical descriptor digest/context.
The collector reads metadata only, follows no linked ancestors/files, rejects
hardlinked/nonregular/oversized/ambiguous metadata and rejects duplicate/nonfinite
JSON. Descriptor content is not an authenticated host attestation.

The diagnostic allowlists only runtime/project/worker identities, fixed local-build
provenance, bounded ASCII Python markers, package names/versions/requested flags,
and the pytest-observe member graph's package names/versions/dependency names.
It excludes project/payload/source metadata, URLs, raw requirements, environment
variables, arguments, logs, imports and executables. Inputs are capped at 16 MiB,
cache candidates at 256, package/dependency lists at 1,000 and final JSON at 65,536
bytes. Output is exclusive and no-follow. Invalid/unavailable metadata or write
failure emits a safe nonzero diagnostic; evidence upload still runs and cannot
mask the original quality failure. Successful collection certifies only the
metadata match, never native analysis or capsule performance.

This was added after a supported-Python-3.13 capsule coverage timeout persisted
while Python 3.11 completed. It supplies dependency/runtime evidence for diagnosis;
no signed vendor patch, analyzer timeout, test selection, quality threshold or
required member was changed. Native assurance stays incomplete until actual
current-head full reports pass. Revert this collector/workflow addition to roll
back metadata retention, preserving original failure evidence.


Pylint's full source analysis uses two local processes via the supported
`tool.pylint.main.jobs = 2` setting. The installed signed module preserves this
ordinary configuration while enforcing its complete file/checker projection and
30-second Pylint deadline. Pylint 4.0.7 merges worker checker results; aggregation
of duplicate-code messages can differ between worker counts. This setting adds no
ignored files/checkers or deadline exception. The measured host timing is diagnostic;
actual supported-Linux native completion remains required. Official
[parallel execution guidance](https://pylint.readthedocs.io/en/v4.0.7/user_guide/configuration/all-options.html#jobs)
accessed 2026-10-05 (Europe/Berlin); the installed 4.0.7 implementation and signed
module 0.50.1 configuration projection were inspected separately.

The four-worker configuration followed repeated signed coverage timeouts on both
Python matrix legs. A same-source host run passed all 2,657 tests in 34.97 seconds
with four workers versus 63.09 seconds with two. The earlier improperly configured
benchmark remains failed evidence. This host timing does not establish Linux
performance or acceptance; actual fresh signed reports must retain every collected
and called test, combined coverage, controller observations and complete worker
evidence. The repository is private and actual hosted CPU count was not recorded.
No runner upgrade, dependency, selection, threshold or deadline change is made.

Both fresh 95457ed Linux reports still returned coverage UNKNOWN at the signed
300-second launch deadline; all other nine analyzers passed. The host suites
passed 2,685 tests in 148.03 and 148.60 seconds. Four workers therefore remain an
unaccepted native performance hypothesis. No partial target observations survive
the timeout, so startup, tests, workers and coverage export cannot be distinguished.

The existing host pytest run now reports its slowest 25 durations. Before the
aggregate gate, the workflow logs only Python-version integers, logical CPU and
affinity counts, and bounded numeric/max cpu.max and memory.max tokens. Absent,
malformed, oversized or symlinked limit files produce null fields; arbitrary input,
environment variables and runtime payloads are not logged. No duplicate suite or
new dependency is introduced. These observations diagnose the host, not native
coverage; all tests, signed analyzers, worker/controller observations and deadlines
remain mandatory. Rollback removes only the collector and diagnostic configuration.
