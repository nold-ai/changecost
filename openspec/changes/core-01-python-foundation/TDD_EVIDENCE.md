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
