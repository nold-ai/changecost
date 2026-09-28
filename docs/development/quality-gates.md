# Repository quality gates

The foundation implements shared local, staged and CI validators in `quality/`.
They are development tooling and are excluded from distributions. `make check`
returns nonzero if any required child fails or cannot run. Python 3.11.15 and
3.13.14 use the same targets; OpenSpec 1.13.2, uv 0.12.19 and actionlint 1.7.12
are bootstrap pins. The actionlint version check accepts the release/Homebrew
`1.7.12` and Go-module `v1.7.12` spellings only. The lock resolves Python runtime, dev and build dependencies.
The dev group also pins uv so isolated repository tests can invoke it. BasedPyright
1.39.10 and its Node wheel 24.16.0 are constrained to the signed SpecFact 0.50.1
composition: newer project versions caused required analyzer evidence to be UNKNOWN.
These are development dependencies; analyzer coverage and type-checking rules remain intact. Pytest
explicitly imports repository helpers from the checkout root; they stay outside
the distributed package. CLI tests resolve the active environment’s console script
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

## Review and limitations

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
outstanding dispute. The [record for reviewed commit d48b830](../../openspec/changes/core-01-python-foundation/ADVISORY_DISPOSITIONS.json)
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
