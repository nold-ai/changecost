# Foundation implementation evidence

Date: 2026-09-28 (Europe/Berlin). Implementation authorized by the maintainer;
no provider collection, publication, commit or PR is part of this stage.
Fresh main `141b9b3ea5226dad672b0910e6ccf79f2403f8b7` fetched at 13:55:33 +02:00.
Branch: `codex/core-01-python-foundation`. The eight reviewed preparation files
were retained in the same owned worktree; no stash or planning PR was applied.
The original main checkout retains its duplicate artifact-ignore change.

## Actual failing-before and passing-after evidence

Times below are local log completion times, not inferred command-start times.
Logs are local-only under `.changecost/evidence/`.

| Time | Command | Actual outcome |
| --- | --- | --- |
| 2026-09-28T13:57:09+02:00 | `python3 -m unittest discover -s tests -v` | 2 expected assertions: package absent; ignored log `01-cli-red.log` |
| 2026-09-28T13:59:30+02:00 | `uv run --locked python -m pytest tests/test_repository_gates.py -q` | 9 missing-validator assertions; earlier path-setup error excluded; ignored log `02-gates-red.log` |
| 2026-09-28T14:02:36+02:00 | `uv run --locked python -m pytest tests/test_build_and_snapshots.py -q` | 1 expected missing-build-gate assertion; 3 passes; ignored log `03-build-red.log` |
| 2026-09-28T14:16:21+02:00 | `uv run --locked python -m pytest tests/test_repository_gates.py -q` | 2 failures: date-only docs/changelog freshness was incorrectly accepted; ignored log `06-drift-red.log` |
| 2026-09-28T14:07:42+02:00 | `uv run --locked python -m quality build --base 141b9b3` | constrained sdist/wheel build, isolated install and CLI tests passed; ignored log `04-build.log` |
| 2026-09-28T14:14:50+02:00 | `uv run --locked python -m quality audit --base 141b9b3 --manifest .changecost/intended-files.txt` | 52 locked dependency license records; full lock advisory coverage; no known vulnerabilities; ignored log `05-audit.log` |

After fixes, `uv run --locked python -m pytest -q` passed 24 tests and 4 CLI
subtests. Ruff check/format and BasedPyright passed on the same slice. Final
integration/matrix results below supersede these iteration results when available.

## Scenario coverage

- `tests/test_cli.py`: absent package red proof; offline help/version, metadata
  agreement, bare/unknown invocation and unchanged home/work directories.
- `tests/test_build_and_snapshots.py`: stale/missing locks unchanged; missing base;
  actual staged blobs versus unstaged fixes and untracked reference targets.
- `tests/test_repository_gates.py`: owner/source/link/anchor failures and repairs,
  content-bound rationales, immutable byte checks, date-only drift, changelog and
  version conflicts, missing/stale generated output, skill drift/duplicates,
  explicit manifests, complete/missing review profiles, aggregate child failure,
  malformed workflow references and archive privacy checks.
- `quality.build` exercises the installed wheel outside source with runtime-only
  dependencies, version/license/archive checks and rejected backend constraints.
  Build/installation can fetch dependencies; execution tests prohibit sockets.

## Review/runtime evidence

Installed SpecFact CLI 0.55.4 and review module 0.50.1 were invoked with
`code review run --scope full --include-tests --enforcement full --json`.
The macOS controller returned UNKNOWN for all required analyzers with
`unsupported_controller_platform`. No analyzer pass is claimed.

An existing local amd64 development image provided SpecFact 0.55.4. The pinned
0.50.1 module was installed and run against a temporary Git snapshot containing
only tracked/intended files, without local artifacts. Linux execution progressed
but returned UNKNOWN: `capsule_materialization_failed:namespace_unavailable`
because bubblewrap could not create unprivileged namespaces. No container/host
security controls were relaxed. This is a real unresolved review-environment
blocker; full `make check` must remain nonzero until it is resolved.

## Dependencies and source evidence

uv 0.12.19 resolved the committed lock. Runtime consists of Typer 0.27.2 and its
transitives; Pydantic remains selected for the next contract change, not needed
for help/version. Main development pins resolve Ruff 0.16.9, BasedPyright 1.40.1,
pytest 9.1.1, Hatchling 1.32.4 and pip-audit 2.10.1. The recorded license metadata
contains MIT/BSD/ISC/Apache, PSF and MPL declarations; retain their notices and
review updated package metadata before dependency changes. Reports cover 52
locked dependencies, including colorama/typing-extensions absent on this host.
No legal compatibility or absence of undisclosed vulnerabilities is claimed.

Primary documentation accessed 2026-09-28:
[uv builds](https://docs.astral.sh/uv/concepts/projects/build/),
[BasedPyright configuration](https://docs.basedpyright.com/latest/configuration/config-files/),
[actionlint installation](https://github.com/rhysd/actionlint/blob/main/docs/install.md),
[pip-audit](https://github.com/pypa/pip-audit), and
[PyPI release metadata](https://docs.pypi.org/api/json/).
Local SpecFact help and the actual reports establish the installed interfaces and
runtime limitations. See the design's preparation evidence for prior decisions.

## Handoff and rollback

Package/repository code is unreleased. No runtime cost command, database, adapter,
collector or provider call was added. Revert this scoped change and recreate the
prior contributor environment to roll back; preserve provider evidence. Required
review and final PR tasks remain pending until their actual subsequent stages.

## Final local integration

- `BASE_REF=141b9b3 MANIFEST=.changecost/intended-files.txt make check` on
  Python 3.13.14: 29 tests plus CLI subtests, format/lint, typing, hygiene,
  docs/index/metadata/workflow, constrained build/install, dependency audit and
  all nine strict OpenSpec changes passed. SpecFact returned UNKNOWN; aggregate
  exit 2 is intentionally non-success. Log: `14-final313.log`.
- The same command with `UV_PROJECT_ENVIRONMENT=.changecost/venv311` and
  `UV_PYTHON=3.11.15` produced the same result. Log: `15-final311.log`.
- A fresh temporary checkout ran `uv sync --locked --group build`, then
  `BASE_REF=HEAD uv run --locked python -m quality staged`: all staged snapshot
  gates passed, without altering the implementation index or original checkout.
- Type and lint probes rejected an int assigned a string and an undefined name;
  logs `13-type-probe.log` and `13-lint-probe.log`. Probes were temporary files.
- A valid workflow that restricted checks to manual runs first passed incorrectly;
  `10-workflow-red.log` records the failing acceptance test. The wiring gate now
  rejects conditional/ignored aggregate steps and verifies the full Python matrix.
- A subcommand/option fixture first exposed missing generated CLI-tree coverage
  (`12-command-tree-red.log`); the renderer now walks the registered tree. The
  production CLI still implements only help/version.
- Synthetic private-file sentinels beside build inputs were absent from both
  distributions; the installed console script (not source imports) passed the
  offline/read-only tests. Log: `08-build-sentinels.log`.

These commands cover the implementation contents before final evidence/task prose
updates. Documentation/index/strict validation are rerun after those prose edits.
Remote CI has not run. Independent verification is recorded below. Eleven of sixteen tasks
have local completion evidence; unresolved review/remote-CI/PR work stays unchecked.


## Independent verification and corrections

Verification started 2026-09-28 after refreshing origin/main at 14:31:29 +02:00;
base and HEAD remained `141b9b3ea5226dad672b0910e6ccf79f2403f8b7`.
Three read-only lanes inspected all 45 intended files, including additions and
the deleted requirements file. Initial content-manifest fingerprint:
`936b98cb0b32111e24603f2a4adf9ae1abcb83d6e1e1254877b77b5d48e65b29`.
The quality lane ran the full aggregate in a complete staged temporary snapshot
on Python 3.13.14 and 3.11.15. Both passed all non-review leaves and 29 tests plus
four CLI subtests; both aggregates exited 2 because all ten SpecFact analyzers
reported UNKNOWN/error (`unsupported_controller_platform`). Native reports were
created at 14:35:37 and 14:36:27 +02:00. No frozen files changed during review.

The lanes found four code/test defects and one stale proposal status sentence:

- The full-review command did not activate its required semgrep-bugs analyzer.
  A regression using the pinned module's conditional-member semantics failed
  before adding `--bug-hunt` (`17-review-activation-red.log`) and then passed.
- Plain pytest could not import repository helpers. Its reproduced collection
  failure is fixed by explicit pytest `pythonpath`, also consumed by the review
  runtime. The helper package remains excluded from product distributions.
- Isolated tests needed native Git and uv. Git is now declared as a review native
  tool; uv 0.12.19 is locked in the development group. Actionlint process-boundary
  unit tests run without a host Go executable. Real syntax validation remains a
  required aggregate leaf; the separate actual malformed/repaired probe passed
  (`19-actionlint-real-probe.log`). No required check was waived.
- CLI tests assumed console scripts lived beside the analyzer's interpreter.
  They now use PATH; the wheel proof explicitly prioritizes its clean venv bin.
- Proposal tracking now distinguishes GitHub Todo from local implementation.

After corrections, plain `uv run --locked pytest -q` passed 30 tests and four CLI
subtests (`20-review-fixes-green.log`); Ruff and BasedPyright passed. Runtime
inspection now records the repository source root and native Git; inspection is
not execution assurance. Adding dev-only uv increases the lock from 52 to 53
third-party packages. Historical audit counts above refer to their original lock.
Final fingerprint, independent rechecks and audit outcomes belong in the ignored
verification receipt `.changecost/workflow/core-01-python-foundation/verify.md`.
The initial unreleased version remains 0.1.0.dev0. No release/tag is warranted.

Supported Linux capsule execution, its coverage requirements, hosted CI namespace
behavior and the final PR remain unverified. The earlier Docker namespace failure
was not retried and no host/container protection was changed. Keep the required
review gate incomplete until an approved supported runner returns actual evidence.


## Maintainer decision: local capsule limitation

On 2026-09-28 the maintainer confirmed that capsule execution on this Mac is a
known limitation and assigned that assurance to GitHub CI. This explicitly permits
committing and pushing this change after the passing local checks and independent
reviews, with capsule assurance pending. The prior UNKNOWN results remain actual
failed/incomplete execution evidence; they are not relabeled as passes. No capsule
retry, local security-policy change or CI bypass is required for this handoff.

The full review gate remains enabled in GitHub CI. Its successful execution and
any resulting findings must be checked during PR promotion before merge readiness
can be claimed. Hosted execution is expected to provide the supported environment,
but has not yet been observed for this change. Prepared artifacts, implementation
and the artifacts-ignore rule belong to the same eventual PR.


## PR 22 review and hosted-runner corrections

On 2026-09-28, CI run [36424984547](https://github.com/nold-ai/changecost/actions/runs/36424984547)
at head `50761043cfebd1894ca8617e971930884054de7d` failed on both Python matrix
jobs. All ten required review analyzers were UNKNOWN because signed capsule
materialization failed at offline-install with `bwrap: loopback: Failed RTM_NEWADDR:
Operation not permitted`; `make check` exited 2. The workflow leaf also failed:
the Go-installed validator reported `v1.7.12`, which the exact-version check rejected.
A full log audit identified these two failing leaves; other leaves reported no
errors. This supersedes the earlier statement that remote CI had not run.

Comparison with `specfact-cli-modules` public main `b3ca3014c8d0e064b860856d4b560a2591999532`
found a missing prerequisite: its customer workflow pins Ubuntu 24.04, sets a
job-local `SPECFACT_CODE_REVIEW_CAPSULE_CACHE`, and loads a narrowly attached
AppArmor `userns` profile before ordinary-user capsule execution. Upstream run
[35158056310](https://github.com/nold-ai/specfact-cli-modules/actions/runs/35158056310)
shows PASS for clean cold/warm/alternate/targeted fixtures after that setup. The
upstream run overall failed separate composition-identity checks; it is not
reported as a fully passing reference run. The adapted ChangeCost setup preserves
global restrictions, signed capsule validation, all required analyzers and ordinary
user execution. The next hosted run must establish whether it resolves this failure.

Codex review comments 4122414070 and 4122414083 identified two reproducible gate
omissions. New OpenSpec scenarios preceded changes. The focused command
`uv run --locked pytest -q tests/test_repository_gates.py -k 'hygiene_policy_change or manifest_rejects or workflow_requires_scoped'`
initially failed all four cases: hygiene-only edits skipped review, missing file
and directory manifest entries were silently omitted, and missing capsule setup
was accepted. After the minimum corrections the same command passed all four.
Ignored logs: `promotion/fixes-red.log` and `promotion/fixes-green.log` under the
change's `.changecost/workflow/` receipt directory.

Real actionlint 1.7.12 caught an invalid runner context in job-level environment
configuration while preparing the fix. Moving that value to the setup step's
environment and exporting it for subsequent steps repaired the syntax;
`uv run --locked python -m quality workflow --base 141b9b3` then passed. This
checks configuration and regressions, not actual AppArmor or capsule execution.
The full Linux review and fresh current-head bot reviews remain required after push.


CodeRabbit comment 4122475797 identified the additional actionlint version defect.
Both hosted job logs contain `actionlint 1.7.12 is required` (lines 41 and 223 of
the saved combined failed-step log). The pinned upstream
[command.go](https://github.com/rhysd/actionlint/blob/v1.7.12/command.go#L64)
returns the Go module version when no release ldflag sets the version, explaining
`v1.7.12` versus the local Homebrew binary's `1.7.12` (checked 2026-09-28).
An initial claim that all non-review CI leaves passed was incorrect; the complete
stage/error audit is saved in `promotion/ci-error-audit.txt` and the narrative above
is corrected. No actual Go installation ran locally because Go is unavailable.

The new version scenario and parameterized regression preceded the validator fix.
`uv run --locked pytest -q tests/test_repository_gates.py -k workflow_validator_accepts`
failed the supported `v1.7.12` case before correction and passed afterward. Only
`1.7.12` and `v1.7.12` are accepted; empty output, malformed/unknown and different
versions are rejected before syntax execution. Accepted versions still invoke the
syntax validator. Logs: `promotion/actionlint-red.log` and `promotion/actionlint-green.log`.


## Native capsule findings at 086e8fd

On 2026-09-28, hosted run [36427023807](https://github.com/nold-ai/changecost/actions/runs/36427023807)
confirmed the AppArmor prerequisite and actionlint spelling fix: both Python jobs
passed workflow validation and executed the capsules. Full review still failed.
Seven analyzers passed; BasedPyright was UNKNOWN because project versions
1.40.1/Node wheel 24.19.0 differed from sealed 1.39.10/24.16.0. Radon reported
three blocking functions (licenses CC24, build run CC16, workflow wiring CC16).
Pytest reported one capsule-only uv lock-fixture failure and five files below the
required 80% coverage. The native report contains 169 findings: nine blocking and
160 nonblocking. Native JSON artifacts remain in ignored local evidence.

The corrected development lock now uses BasedPyright 1.39.10 and a Node wheel
24.16.0 constraint to match the signed module 0.50.1 composition. Runtime package
dependencies and required analyzers are unchanged. `uv sync --locked --group build`,
BasedPyright, the actual locked dependency audit and license metadata check passed;
all 53 third-party lock entries were audited with no reported advisories.

The three complex routines were split by existing responsibility (license record,
source/archive/install proof, capsule setup wiring) without removing validators.
Radon 6.0.1 now reports no function above the blocking complexity threshold of 15.
Offline tests exercise license fallbacks/outages/mismatch, archive privacy/version/
runtime dependency errors, build failure propagation, aggregate diagnostic paths
and actual in-process help/version/error/module invocation. Subprocess doubles
exercise error branches without a network dependency; the unchanged real build,
audit, actionlint and isolated installed-wheel proofs remain required and passed
locally. These unit tests are not a substitute for real tool execution.

A local coverage run before correction reproduced the low files (main 65.4%, audit
36.1%, build 26.5%, module entrypoint 0%, CLI 53.3%; this run also contained the new
failing hook regression). After correction, `uv run --locked --with pytest-cov==7.1.0 pytest -q --cov=quality --cov=changecost --cov-report=json:...`
passed 48 tests plus four subtests. Every measured source/validator file exceeded
80%: main 86.9%, audit/build 98.7%, CLI and module entrypoint 100%. No coverage
threshold, source scope or analyzer policy was weakened. Capsule attribution must
still be confirmed by hosted review. Logs/reports: `promotion/coverage-before.*`,
`promotion/coverage-after.*`, `promotion/complexity-after.json`,
`promotion/capsule-pin-audit.log`, `promotion/refactor-build.log`.

Codex comment 4122587726 correctly identified that ordinary hooks forwarded an
empty comparison base. A new scenario and regression failed before the fix;
only the staged hook now defaults an unset base to HEAD, preserving an explicit
override. The actual configured `pre-commit run repository-contracts --all-files`
also passed with BASE_REF absent in an isolated clone containing the full staged
fixes (`promotion/ordinary-hook.log`); the working index was not touched.
Aggregate/CI base requirements remain explicit.

The 160 nonblocking findings have per-finding dispositions in the ignored
`promotion/nonblocking-dispositions.json`: descriptive test/helper docstrings,
pytest fixture-name injection and local imports, exact empty-list assertions,
required callback/test-double parameters, intentional validator CLI output, and
bounded dispatch/validation complexity retain documented narrow exceptions.
Build/audit structure and explicit subprocess/UTF-8 fixture handling were repaired.
These are scoped review dispositions, not suppressions or changes to analyzer rules.

Codex 4122587708 and CodeRabbit 4122599241 correctly note that the AppArmor cache
attachment is path-based, not bound to a binary signature. The gate guide now
states this limitation. The proposed new host-privilege gain is not established
on this disposable hosted VM: GitHub documents passwordless sudo for its runner
user, and repository-controlled uv/build/tests already execute host-side. SpecFact's
signed digest/same-descriptor checks protect its own launcher invocation, not
arbitrary host executions; candidate capsules do not mount the host cache writable.
Module 0.50.1 has no supported immutable external launcher setting; changing signed
module internals or copying a different bwrap is not an authorized compatibility fix.
The current disposition is a documented host trust boundary, pending reviewer reply.

The capsule-only uv fixture failure remains unresolved: its native traceback only
contained CalledProcessError, without stderr. Local offline execution passes. The
fixture now asserts its return code with captured stderr so the next hosted report
can identify the exact cause. No fixture was skipped or made permissive. Hosted
full assurance and current-head reviews remain required; this batch does not claim
the required CI gate has passed.


Independent review of that local batch found a marker-split license regression
introduced by the helper extraction: two locked versions of one package incorrectly
reused the single installed version's metadata. A synthetic two-version lock test
failed before correction (`promotion/license-split-red.log`). The collector now
uses installed metadata only for its exact locked version, fetches exact-release
metadata for other versions, and separately rejects an installed version outside
all locked alternatives. The same fixture verifies both distinct evidence rows and
the out-of-lock failure. All focused license tests pass after correction; the new
fixture is part of the final 49-test suite. No package/audit scope was narrowed.


## Supported external-tool boundary and CI comparison base

Hosted run [36429886815](https://github.com/nold-ai/changecost/actions/runs/36429886815)
at `ba7221d506281c9d74fac342ecef10ada17b984d` passed every non-review leaf and nine
review analyzers on both Python versions. Complexity, coverage and type-checker
compatibility were repaired. The sole blocking native finding retained stderr:
uv invokes the selected Python with `-I`; the signed project-runtime wrapper
rejects this as `project_python_option_unsupported:-I` because it disables required
runtime attachment. This is genuine hosted failing evidence, not a locally inferred
failure. Native reports contain 179 findings, one blocking and 178 nonblocking;
updated individual dispositions are in ignored
`promotion/nonblocking-dispositions-ba7221d.json` (local test-double names and
ASCII-only fixture encodings are scoped exceptions, not new suppression rules).

The real offline missing/stale/repaired lock fixture now lives in the standalone
`tests/tool_probes.py` and runs unconditionally from the required host lock leaf
alongside `uv lock --check`. It uses host uv/Python, asserts failures and immutable
lock bytes, and verifies the repaired configuration. Therefore local aggregates,
CI and staged hooks still execute the actual external-tool proof. Capsule pytest
checks that failures from either command propagate; no skip/xfail, runtime override,
analyzer omission or relaxed assertion was introduced. The host command passed:
`uv run --locked python -m quality lock --base HEAD --manifest .changecost/intended-files.txt`
(`promotion/host-lock-proof.log`). The manifest lists the intended new probe and external-tool resolver files.

Codex comment 4122823910 identified an accepted workflow BASE_REF override that
could hide change-sensitive gates. The validator now checks the current reviewed
resolver script and event inputs, its required order/unconditional execution, and
rejects workflow/job/step BASE_REF overrides and other explicit exports. It does
not attempt arbitrary shell static analysis; staged-hook HEAD defaults are unchanged.
New OpenSpec scenarios and ten regression cases preceded implementation. All ten
failed before correction and pass afterward, covering both required lock commands
and eight comparison-wiring mutations (`promotion/host-lock-base-red.log`,
`promotion/host-lock-base-green.log`). Real actionlint and BasedPyright passed;
Radon reports maximum complexity 13 in the affected workflow validator (threshold15).

The new controller-PATH finding notes a genuine limitation of same-head quality
checks: malicious PR code could replace validators or reports. This workflow also
executes the PR's own checker, digest binding and workflow code on a sudo-capable
host, so absolute paths alone cannot establish tamper-proof attestation. The gate
guide states the actual trust boundary and does not claim malicious-PR attestation.
No out-of-band verification framework or signed module modifications were introduced.
Fresh hosted full assurance and bot reviews remain required for the corrected head.


The narrow mitigation for Codex security comment 4122885936 rejects external
validator paths inside the repository or active project environment after symlink
resolution and invokes the accepted absolute path. Three real fake-PASS console
scripts (repository, custom environment and symlink) were accepted before the fix
and rejected afterward (`promotion/validator-shadow-red.log` and
`promotion/validator-shadow-green.log`). Tests also exercise missing validators,
explicit repair without silent PATH fallback, allowed external symlinks and the
OpenSpec caller. Controller unit tests inject external resolution so native tools
are not recursively required inside capsule pytest. This is collision prevention,
not an authentication or malicious-PR attestation claim.

On 2026-09-28 the final local controller suite passed 65 tests and four subtests;
measured source-file line coverage ranged from 87.3% to 100%, with 100% for the new
resolver. Ruff, format, BasedPyright, actual actionlint/OpenSpec, the real host lock
proof and docs/index/metadata checks passed. Coverage and complexity receipts are
`promotion/controller-coverage.json` and `promotion/controller-complexity.json`.
These local results do not replace the pending corrected-head hosted capsule run.


## Native nesting and job token permissions

Hosted run [36433228924](https://github.com/nold-ai/changecost/actions/runs/36433228924)
at `9bf9ad6159300f9adaf0acbd8d8b68b9ada8ae4b` passed the host missing/stale/repaired
uv proof, every non-review leaf and nine analyzers, including targeted pytest and
coverage, on both Python versions. The sole blocking finding was native KISS
nesting depth seven in the workflow mutation test's elif dispatch. The signed
module counts nested AST If nodes, so passing Radon cyclomatic checks did not
cover that independent rule. The unchanged installed nesting metric reproduces
seven before and two after replacing six scalar branches with an explicit
mutation table; all eight negative cases and repaired workflow checks pass. No
nesting threshold, test scope or analyzer was changed. Actual metric evidence is
`promotion/nesting-red-green.json`; the current native report's 194 nonblocking
findings have scoped dispositions in `promotion/nonblocking-dispositions-9bf9ad6.json`.

Codex comment 4123113287 then identified that quality-job permissions could
override root read-only permissions. Three new cases (contents write, write-all,
and issues write) failed before the guard and pass after it. The job may inherit
the root permissions or repeat exactly contents read. Each negative case verifies
the repaired explicit read map, preserving the current hosted runner setup.
Receipts: `promotion/job-permissions-red.log` and `promotion/job-permissions-green.log`.
Fresh corrected-head full hosted assurance remains required.

Local verification after these corrections passed 68 tests and four subtests,
including all eleven targeted nesting/permission cases. Source coverage remains
at least 87.27%; maximum measured cyclomatic complexity across source and tests
is 13. Ruff/format, BasedPyright, actual actionlint, strict OpenSpec, docs/metadata
and hygiene passed. Evidence is in `promotion/nesting-coverage.json`,
`promotion/nesting-complexity.json` and the corresponding local logs.


CodeRabbit comment 4123160190 identified an ambiguous stale-lock negative: the
nonexistent dependency could fail resolution even without `--check`. Removing
only that flag from the old probe confirmed the defect: it still exited zero.
The fixture now drifts the project's own version from 0.1.0 to 0.2.0 with no
dependencies. Check failure preserves exact lock bytes; restoring metadata passes
without a rewrite. Reapplying the same drift then succeeds with ordinary offline
locking, changes the lock bytes, and passes the subsequent check. The same flag
removal mutant now exits one at the stale-check assertion, while the required host
lock leaf passes unchanged. Receipts: `promotion/stale-check-bypass-before.log`,
`promotion/stale-check-bypass-after.log`, `promotion/stale-lock-host-green.log`.
No test skip or weaker resolution assertion is involved.


## Native advisory-success verdict

Hosted run [36435919187](https://github.com/nold-ai/changecost/actions/runs/36435919187)
at `0f0f6a866959fb2110a9f1829eacac5b0644d81a` reports all ten required analyzers ran
with PASS evidence on both Python versions: assurance PASS, unknown evidence false,
full enforcement, exit code zero, 200 nonblocking findings and no blocking findings.
The aggregate still failed because this repository accepted only the literal PASS
verdict. Installed signed module 0.50.1 `run/findings.py:553` declares the three
verdict literals; lines 645–670 derive PASS_WITH_ADVISORY from passing assurance
when findings remain. This is a supported native success form, not a waived check.

The parameterized complete-report regression passed for PASS and failed for
PASS_WITH_ADVISORY before the correction; both pass afterward. For each form it
also rejects stale digests, UNKNOWN assurance/evidence, nonzero exit, FAIL verdict,
missing analyzers, unknown analyzer outcome and failed execution. The wrapper now
accepts exactly the two successful verdicts while retaining every existing check.
The actual native JSON reproduces the wrapper-only error before and no adapter
error afterward using a synthetic matching digest strictly for this function-level
probe, not as new native assurance. Receipts: `promotion/advisory-verdict-red.log`,
`promotion/advisory-verdict-green.log`, `promotion/advisory-native-before.json` and
`promotion/advisory-native-after.json`. All 200 advisories retain scoped dispositions
in `promotion/nonblocking-dispositions-0f0f6a8.json`; no analyzer policy changed.
Fresh corrected-head CI and unresolved review scope questions remain outstanding.


## Read-only permissions on sibling jobs

Codex security review 5340246562 of `0f0f6a8` (comment 4123435837) arrived after
the next adapter batch was already being promoted. The finding still applied:
only the named quality job's permission override was checked. Three sibling-job
cases with contents write, write-all and issues write passed incorrectly; the
same quality-job cases already failed correctly. The six-case parameterized
regression recorded three failures and three passes before correction. The guard
now checks all jobs' permission overrides, allowing inherited root read-only
permissions or exactly contents read. Every case verifies inheritance and a
repaired explicit read-only map. No job or GitHub permission was changed; only the
validator's coverage of future workflow edits was corrected. Evidence is in
`promotion/all-jobs-permissions-red.log` and `promotion/all-jobs-permissions-green.log`.

Contributor and gate guidance now name sibling jobs explicitly. README setup,
hook/review semantics and the agent quality procedure remain accurate; narrow
no-prose-change rationales in `quality/exceptions.json` bind those two unchanged
documents to the exact current mapped source digest. They neither suppress
analyzers nor exempt future changed source contents from documentation review.


Codex code review 5340321134 of `d48b830` (comment 4123495762) identified that the
checkout could select the PR base rather than the head without failing wiring
validation. Eight checkout mutations failed their expected-rejection assertions
before correction: ref, history depth, persisted credentials, conditional/ignored
execution, action pin, duplication and order. They now fail validation and pass
after repair. The event-head resolver input is also bound by the existing script
contract. A real host shell probe with a deliberately wrong EXPECTED_HEAD exited
zero before correction; it now exits one without exporting BASE_REF. The matching
head still exits zero and exports the resolved comparison. This probe runs on the
host because it exercises the GitHub shell contract; capsule pytest retains the
YAML mutation tests without requiring an extra native shell tool. Receipts:
`promotion/checkout-red.log`, `promotion/checkout-green.log`,
`promotion/checkout-runtime-before.json`, `promotion/checkout-runtime-after.json`.
The runtime assertion is necessary because a wrong checkout can otherwise load the
base's validator; the source validator additionally checks prospective workflow edits.
It does not establish hostile-controller attestation.

In parallel, hosted run [36437520340](https://github.com/nold-ai/changecost/actions/runs/36437520340)
completed successfully on `d48b830` for both Python versions: every leaf passed and
all ten native analyzers ran with PASS evidence, full assurance, no unknowns, exit
zero and PASS_WITH_ADVISORY. Its 200 advisory findings received recorded
individual dispositions. That confirms the preceding adapter correction; these
additional workflow corrections still require fresh CI on their committed head.

Final local verification of this workflow batch passed 81 tests and four subtests,
Ruff/format, BasedPyright, actual actionlint, HEAD-based docs/index/metadata, strict
OpenSpec and hygiene. Source coverage remains at least 87.27%; maximum measured
complexity across source/tests is 13. Receipts include `promotion/checkout-coverage.json`
and `promotion/checkout-complexity.json`. Current green-head advisory dispositions
are refreshed in `promotion/nonblocking-dispositions-d48b830.json`.


## Reviewable advisory dispositions

CodeRabbit comment 4123577773 identified that the previously recorded individual
advisory dispositions were only in ignored local output. The native adapter's
approved success contract remains unchanged: complete native advisory success
passes the machine gate, while promotion still requires findings to be fixed or
explicitly dispositioned before review completion. The missing reviewable record
is now [ADVISORY_DISPOSITIONS.json](ADVISORY_DISPOSITIONS.json), bound to commit
`d48b830bf4d4e32e94183b05c831ccb4c7fb2c52`, successful CI run 36437520340, both
Python matrix report SHA-256 hashes and 200 individual stable finding identities.
The matrix finding sets are identical. Each entry points to one of 16 scoped
rationales; build and license-fixture sequence warnings have their own explicit
reasons. The record contains no private host paths or raw report dumps and cannot
waive new findings or claim coverage of the next head. Subsequent current-head
triage must be recorded with its report identity, including through reviewable PR
evidence, before promotion is complete. No generic runtime waiver or approval
framework was added, and the two mutable-host scope disputes remain open.


## OpenSpec configuration review applicability

Codex review 5340620250 of `a70f845` (comment 4123744916) identified that an
`openspec/config.yaml`-only edit skipped full review. The spec now explicitly
covers this configuration boundary. The regression changed only its workflow
context and injected incomplete native evidence; before correction the leaf
returned success with “not applicable” instead of propagating UNKNOWN. Adding
this exact path to the existing configuration set makes the regression pass and
leaves unchanged configuration non-applicable. The existing hygiene-policy
regression also passes. Receipts: `promotion/openspec-config-red.log` and
`promotion/openspec-config-green.log`. No analyzer or assurance requirement changed.

Hosted run [36440386931](https://github.com/nold-ai/changecost/actions/runs/36440386931)
passed both Python versions at `a70f845`, including every aggregate leaf and all
ten native analyzers. Its 209 nonblocking findings have a
[report-bound individual disposition delta](https://github.com/nold-ai/changecost/pull/22#issuecomment-5872803533)
against the committed baseline: 187 retained, 22 explicitly reviewed additions
and 13 removals. That evidence covers `a70f845`; this applicability correction
still requires independent verification and fresh hosted CI/reviews. The two
mutable-host integrity scope disputes remain open.


## Shared security policy across workflow files

Codex security review 5340803594 of `a70f845` (comment 4123896111) identified
that actionlint received sibling workflows but the token/event policy inspected
only `quality.yml`. Ten new `.yml`/`.yaml` fixture cases failed before correction:
root write, root write-all, omitted root permissions, a job write override and
`pull_request_target`. They now fail validation with a filename-bound diagnostic.
Each fixture first accepts a read-only push sibling with inherited permissions,
then repairs the violation and explicitly sets the job to `contents: read`.
These siblings have no quality matrix, checkout or resolver, demonstrating that
only shared security invariants apply. Existing quality-job override cases now
exercise the shared policy directly. The combined 17 affected cases pass.
Receipts: `promotion/all-workflow-red.log` and `promotion/all-workflow-green.log`.

This correction enforces the approved read-only CI design across workflow files;
it does not authenticate a hostile PR controller or change the two open integrity
scope disputes. Current-head CI remains green at `a70f845`; the uncommitted
configuration and workflow-policy fixes still require fresh verification and CI.


## Inherited Make flags preserve aggregate failure

Codex code review 5340973177 of `b241407` (comment 4124033798) identified that
`MAKEFLAGS=-i` could suppress gate failures. A real host probe using the workflow's
original `make check` command and a synthetic recipe exiting 23 reproduced the
problem at workflow, job and step scope: wiring validation accepted all three,
and GNU Make returned zero with “Error 23 (ignored)”. Four canonical-command
regressions also failed before correction. CI now clears MAKEFLAGS, GNUMAKEFLAGS
and MFLAGS immediately before Make; the validator requires that exact command.

With all three flag variables set to `-i`, the actual corrected workflow command
now returns two for the failing recipe and zero after repair, at each of the three
inheritance scopes. No failure was ignored. The host proof uses GNU Make 3.81 on
macOS; the inherited MAKEFLAGS bypass is directly reproduced there, while clearing
GNUMAKEFLAGS also protects GNU Make versions supporting that input. Four command
mutation/repair cases plus existing condition/resolver tests pass (14 targeted
cases). The external Make proof runs on the host, while capsule pytest exercises
the workflow contract without adding a native Make dependency. Receipts:
`promotion/makeflags-runtime-red.json`, `promotion/makeflags-test-red.log`,
`promotion/makeflags-runtime-green.json` and `promotion/makeflags-test-green.log`.

Hosted run [36443662510](https://github.com/nold-ai/changecost/actions/runs/36443662510)
passed all gates on both Python versions at `b241407`, including all ten native
analyzers. Its 220 nonblocking findings received an
[individual report-bound disposition](https://github.com/nold-ai/changecost/pull/22#issuecomment-5873326997),
including explicit reassessment of five retained identities with changed source
context. This inherited-flag correction still needs independent verification and
fresh hosted CI/reviews; the two mutable-host scope disputes remain open.


## Hygiene filename argument boundary

Codex security review 5341086436 of `b241407` (comment 4124121693) identified
a tracked root `--help` filename being parsed as a pre-commit option. An isolated
real Git repository with that name and a harmless synthetic private-key header
marker reproduced success and help output without running hooks. A `./` prefix
was also tested and was insufficient: installed pre-commit normalizes paths to
relative names before invoking its hooks; all hooks then reported success despite
the synthetic marker. This downstream failure is preserved in
`promotion/hygiene-prefix-probe.json`, not described as a successful fix.

The shared current-input validator now rejects option-shaped root paths during
working inventory, staged materialization and direct hygiene invocation. Three
failing-before cases cover `--help`, `-h` and normalized `./--help`, then prove
removing the input permits inventory/snapshot/hygiene again without rejecting its
old comparison entry. Three additional cases preserve `fixtures/--help`, `.--help`
and an ordinary filename. All six targeted cases pass. The guard applies only to
current inputs; it does not prohibit repairing an existing unsupported filename.

The actual downstream proof now rejects the unsafe root path. After a safe rename,
detect-private-key fails the harmless synthetic marker as expected; replacing the
marker with ordinary text makes every hook pass. No real key material is used.
Receipts: `promotion/hygiene-option-runtime-red.json`,
`promotion/hygiene-option-test-red.log`, `promotion/hygiene-option-test-green.log`
and `promotion/hygiene-option-runtime-green.json`. This fix and the inherited
Make-flag correction remain pending independent verification and fresh hosted CI.


## Static quality execution context validation

Codex code review 5341369751 of `37cb81d` (comment 4124356205) identified that
matching aggregate command text alone did not constrain its execution shell.
The spec now requires explicit quality-job Bash/root defaults and rejects
conflicting inherited or per-step contexts. Nineteen YAML-only regression cases
failed before correction and pass afterward: changed workflow/job shell/directory,
missing job defaults, and each of the seven quality run steps with altered shell
or directory. Repairs restore canonical or inherited settings. No alternate shell
is executed by these regressions. Actual actionlint also accepts the corrected YAML.
Receipts: `promotion/execution-context-static-red.log` and
`promotion/execution-context-static-green.log`.

An earlier local dynamic attempt was unavailable because the reported executable
path was absent on this Mac; it produced no successful reproduction or saved
runtime evidence. Subsequent work is limited to static YAML validation and normal
quality checks. GitHub's [workflow syntax reference](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_iddefaultsrun)
(accessed 2026-09-28) documents job run defaults and more-specific step settings;
this patch validates the reviewed subset rather than parsing arbitrary shell code.

Hosted run [36447375954](https://github.com/nold-ai/changecost/actions/runs/36447375954)
passed both Python versions at `37cb81d`, with all ten required native analyzers
ran/PASS and 231 nonblocking findings. Its
[report-bound disposition](https://github.com/nold-ai/changecost/pull/22#issuecomment-5873842916)
includes 82 additions, 71 removals and six explicit reassessments among 149
retained identities. That evidence covers the previous head; this static context
correction still requires independent verification and fresh hosted CI/reviews.


## Manual CI comparison interval

Codex security review 5341400576 of `37cb81d` (comment 4124381219) identified
that a manual comparison resolving to the tested head created an empty interval.
The explicit-base design is now clarified for manual CI only: the resolved base
must differ from the expected head. The shared local baseline function and the
staged-hook HEAD default are unchanged; no ancestry restriction was added.

An ordinary resolver fixture using only Git reads and temporary output files
confirmed the previous script accepted both HEAD and its exact SHA and exported
that equal base. After correction those two manual cases exit one without any
BASE_REF export; a distinct explicit base succeeds. PR and push fixtures retain
their previous behavior. A YAML-only guard-removal regression failed before the
change and passes after correction; all 20 combined static execution/manual cases
pass. This uses the normal Bash resolver, with no alternate execution shell.
Receipts: `promotion/manual-base-runtime-red.json`,
`promotion/manual-base-static-red.log`, `promotion/manual-base-runtime-green.json`
and `promotion/execution-manual-green.log`. Independent verification and fresh
hosted CI/reviews remain required for this uncommitted combined correction.


## Static matrix interpreter binding

Codex code review 5341591512 of `f43bf23` (comment 4124542155) identified that
version labels alone did not validate uv's actual interpreter selection. The
current hosted run did use both intended Python versions; this is a prospective
workflow validation gap, not a claim that its matrix evidence was duplicated.
The spec now requires the existing canonical job-level UV_PYTHON matrix binding
and rejects all per-step overrides.

Five YAML-only regression cases failed before correction and now pass: missing
job binding, either fixed interpreter value, and fixed or redundant-expression
step overrides. The latter cases visit every quality step and verify repair each
time. A small matrix validator retains the exact two-version check and applies
the binding rules together. No workflow YAML or runtime tooling changed. Actual
actionlint passes. Receipts: `promotion/matrix-binding-static-red.log` and
`promotion/matrix-binding-static-green.log`.

Hosted run [36449961738](https://github.com/nold-ai/changecost/actions/runs/36449961738)
passed every aggregate leaf at `f43bf23` on both Python versions, including 122
tests plus four subtests and all ten native analyzers. Its 248 nonblocking
findings have an [individual report-bound disposition](https://github.com/nold-ai/changecost/pull/22#issuecomment-5874170166)
covering 20 additions, three removals and 228 unchanged-context retained identities.
This matrix-binding validator correction still requires independent verification
and fresh hosted CI/reviews; the two mutable-host scope disputes remain open.


## Static aggregate launcher selection and manual evidence scope

Security review 5341678338 of `f43bf23` reported direct PATH selection of the
aggregate launcher (comment 4124618208). Five new YAML-only cases failed before
correction: workflow/job/step PATH entries and either noncanonical launcher path.
All 14 focused PATH, existing Make-flag and matrix-binding cases now pass,
including removal/repair checks at every quality step. The canonical Ubuntu
command uses `/usr/bin/env` and `/usr/bin/make`; direct PATH entries are rejected.
Normal GITHUB_PATH bootstrap additions remain intact. Receipts:
`promotion/path-static-red.log` and `promotion/path-matrix-static-green.log`.
No alternative shell or fake launcher was executed; this evidence verifies static
configuration validation and does not authenticate a mutable runner or output.

The same review's comment 4124618186 asks that manually selected bases be trusted.
The original design specifies an explicit manual base and the approved behavior
review scenario uses changed-input applicability. A valid distinct identical-tree
or docs-only interval therefore legitimately has no applicable behavior changes.
Rejecting identical trees alone would not establish trust in other selected
intervals. Documentation now explicitly distinguishes scoped manual results from
full ten-analyzer assurance and required PR/promotion behavior evidence. This is
a non-finding under the declared comparison contract, not a reviewer withdrawal
or permission to substitute not-applicable results for required behavior review.
No additional manual comparison restriction was implemented. The thread remains
open pending a verified reply and observation of any contest.

The combined matrix/PATH correction still needs independent verification and
fresh hosted CI/reviews. The current `f43bf23` run and its published 248 advisory
dispositions remain bound to that earlier head; the two mutable-host scope disputes
remain open.
