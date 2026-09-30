# Settlement implementation evidence

Status: implementation complete locally / verification To-Validate. Unreleased `0.1.0.dev0`.
Authorized by the maintainer on 2026-09-29 (Europe/Berlin).

## Inputs and recovery

Fresh fetched main and HEAD: `999cb8f960785fe4ac0434d41a0892beca933191`, checked
2026-09-29 at 22:01 +02:00. PR #25 is merged; #11's open administrative state
remains a tracking discrepancy. Prepared artifacts were carried directly into the
implementation, without a stash or planning PR. Archive-skill correction and the
full-CLI Core-02 archive remain included. No main spec was manually synchronized.

Active checkout: `/Users/dom/.codex/worktrees/settlement-implementation/changecost`,
branch `codex/settlement-reconciliation`. Work moved here after unrelated retrospective
files appeared in the primary checkout. Only the owned reviewed scope was copied;
unrelated work is untouched. The original dirty implementation is a stale recovery
copy and must not be mistaken for the active tree. The bounded review receipt was
copied intact, retaining preparation time and both correction batches, not reset.

## Actual failing and passing evidence

Logs remain ignored under `.changecost/workflow/settlement-01-reconciliation/`.
Times below are recorded log completion times in Europe/Berlin.

| Timestamp | Log | Outcome |
| --- | --- | --- |
| 2026-09-29T22:03:25+02:00 | `red-contracts.log` | 2 failed in 0.05s |
| 2026-09-29T22:05:39+02:00 | `green-contracts.log` | 94 passed in 0.24s |
| 2026-09-29T22:06:44+02:00 | `red-computation.log` | 4 failed, 4 passed in 1.39s |
| 2026-09-29T22:09:25+02:00 | `red-coverage.log` | 14 failed, 6 passed in 0.28s |
| 2026-09-29T22:11:13+02:00 | `red-cli.log` | 1 failed, 1 passed in 0.11s |
| 2026-09-29T22:12:12+02:00 | `green-cli.log` | 133 passed in 0.49s |
| 2026-09-29T22:16:30+02:00 | `red-review1.log` | 6 failed, 28 passed in 0.31s |
| 2026-09-29T22:17:23+02:00 | `green-review1.log` | 147 passed in 0.52s |
| 2026-09-29T22:23:10+02:00 | `red-review2.log` | 4 failed, 40 passed in 0.35s |
| 2026-09-29T22:24:33+02:00 | `green-review2.log` | 159 passed, 4 subtests passed in 2.31s |

Initial contract tests reached the existing adapter and rejected the newly specified
record kind. The normalized/computation API tests initially failed at their absent
entrypoints; those establish missing capability, not algorithm correctness. The CLI
red proof reached Typer and rejected `--import-evidence`. Subsequent regression reds
exercise implemented behavior and establish the concrete defects described below.
Tests were written before their corresponding implementation/fix. Tooling/typing
failures are not represented as behavioral red evidence.

Commands: `.venv/bin/python -m pytest tests/test_reconciliation.py -q` for scenario
slices; add `tests/test_settlement_cli.py tests/test_store.py tests/test_contracts.py
 tests/test_contract_cli.py tests/test_cli.py` for the combined regression run.
The CLI installation checks require `.venv/bin` on PATH. One direct run without it
failed the installed-script precondition; correcting PATH passed, and this is not
product TDD. Ruff and BasedPyright passed on the scoped runtime/tests after batch2.

## Independent review and correction history

Two read-only agents reviewed the runtime against the selected specifications.
Batch1 fixed scope/lane exclusions hiding contradictory work bounds, portable
successors blocking locally receipted ledgers, transitive correction binding conflicts,
resolved currency leaking into other scopes and report/computation cutoff mismatch.
Six failing regressions became passing; 147 scoped tests passed at that checkpoint.

Batch2 fixed missing portable dependency-role validation, supplied model IDs receiving
inspection authority without matching immutable payloads, profile-only snapshot
precedence and normalization of new components after portable core-ID preservation.
Source-coverage evidence is also checked against the declared Run. Four failing test
functions became passing; 159 scoped tests and 4 installed-CLI subtests passed.
These are distinct invariants, not resets of the prior finding history. Final independent
fix verification is recorded below when complete.

## Implemented boundary

Strict internal economic/coverage/computed records, atomic normalized import,
stable source/component identities, typed pending replacement locators, nonbranching
correction history, bounded exact arithmetic, explicit supported temporal lanes,
local snapshot/operation receipts, policy-bound synthetic coverage and read-only
repository remainder are implemented. Source/record history, failed/cancelled retries
and abandoned Change expenditure are retained. Product version remains unchanged;
provider adapters, quote/check algorithms and live collection remain outside scope.

Local SQLite layout 2 rejects incompatible layouts unchanged; no automatic migration
or public v2 was added. A consistent backup preserves receipts and original local
history. Portable reimport creates destination availability and imported claims,
not local computation authority. Roll back using the compatible checkout and a
consistent backup into a distinct path; never erase a runtime store to downgrade.

## Limits and remaining verification

No provider profile is certified. Only the closed synthetic policy can produce
synthetic full-change coverage. Exact computations enforce 100000 repository
records and 4096 aligned digits; normalized CLI input is limited to 32 MiB.
Native SpecFact analyzer assurance cannot run on this macOS controller and requires
supported Linux. No native pass, commit, push, PR, release, deployment or completed
verification stage is claimed. Full matrix/build/docs gate outcomes follow when run.


## Final implementation handoff — 2026-09-29

- Aggregate command: `BASE_REF=999cb8f960785fe4ac0434d41a0892beca933191 MANIFEST=.changecost/workflow/settlement-01-reconciliation/intended-files.txt make check`.
  Python 3.13.14 suite: **852 passed in 71.27 seconds**. Lock and host guard probes,
  hygiene, Ruff/format, BasedPyright, docs, generated references, metadata, workflow
  and distribution build passed. Dependency audit was not applicable because locked
  dependency/audit inputs did not change. Log: `implementation-make-check.log`.
- Python 3.11.15 used a separate locked environment via
  `UV_PROJECT_ENVIRONMENT=/tmp/changecost-settlement-python311 uv sync --locked --group build --python 3.11.15`,
  then `PATH=/tmp/changecost-settlement-python311/bin:$PATH /tmp/changecost-settlement-python311/bin/python -m pytest -q`:
  **852 passed, 4 subtests passed in 72.43 seconds** (`python311-tests.log`).
- Distribution build rebuilt the wheel from the sdist, installed only locked runtime
  dependencies into a clean environment outside the checkout, checked archive privacy
  and absence of SpecFact, and ran `tests/test_cli.py`. Its subprocess socket guard
  blocked network while exercising duplicate/retry/replacement import, explicit bind,
  exact `0.45` computation, operation retry, explain and twice-imported portable output.
  All passed. The documented nine-command example also passed independent execution,
  producing `0.25` with correctly provisional coverage.
- Full aggregate exit was **1**, not a pass. Its native-review leaf reported all ten
  analyzers `unsupported_controller_platform` on macOS. The initial spec leaf also
  detected an empty Core-02 active directory left by transferring deleted files into
  the worktree. Verified it contained no files, removed only empty directories, then
  reran all strict specs: **10 passed, 0 failed**. This was transfer cleanup, not an
  archive substitute; the archive itself had already been executed by the full CLI.
- Two independent runtime lanes verified final fixes, with **46 settlement tests**
  passing in their read-only review runs and no remaining concrete findings. An
  additional three-Run nonzero probe preserved `0.60` through accepted/abandoned
  outcomes and reporting. The documentation lane verified its corrected generator
  and `economic_kind`/legacy coverage wording, with no remaining scoped findings.
- The final reference-description edits alter documentation strings only. Fresh
  docs/index, Ruff, whole-repository BasedPyright, metadata, strict specs and whitespace
  checks cover those refinements; no extra runtime suite is claimed for them.
- Issue #12 body was reconciled and moved to In Progress, remaining OPEN. Native
  User Story, parent #7, prerequisite #11, labels and unassigned state are retained.
  Prepared work is local/unpublished. Original preparation checkpoints in the issue
  are historical; no remote implementation link is invented.

Confidence: high in the observed offline behavior and scoped fixes; native analyzer
assurance remains unknown until supported-Linux verification. No provider economic
completeness or historical destination replay is inferred from portable claims.
False finality, double-counting and history loss are guarded by explicit coverage,
validated replacement chains and immutable transactional receipts plus backup tests.
No paid infrastructure is needed; no implementation-time estimate is asserted.

Tasks 1.1–6.2 are complete (17 tasks); 6.3–6.4 remain pending for full assurance,
staged checks, acceptance and any later authorized publication. Next invocation:
`$changecost-verify settlement-01-reconciliation`. No commit/push, PR, settlement
archive, release or deployment was performed. Preserve the active managed worktree
and its ignored review history; the original checkout is only a stale recovery copy.


## Local verification milestone — 2026-09-30

The maintainer authorized verification, scoped CodeRabbit review and later promotion.
The implementation was refreshed onto PR #27 at main/HEAD
`131799f640caac6c2ee68dc6904d331a4203f825`; the ten owned runtime/test files
remained byte-identical. The strengthened review process is now applicable.

Frozen generation 7 (`e16b726c0265ee25a5394794c18abba0917941481c0ad957a0f6c663bc7c1e6b`)
received independent quality, security/defect and documentation review. The current
Python 3.13.14 suite passed 1,020 tests in 93.12 seconds; fresh Python 3.11.15
passed 1,020 tests in 95.46 seconds. The distribution build and installed offline
CLI proof passed. Lint/format, typing, docs/index, metadata, workflow, lock and
hygiene passed; hygiene included all intended new files. Dependency audit was
not applicable because its locked inputs were unchanged. Strict OpenSpec passed
all 11 items. Full commands and native logs are retained in the ignored workflow
receipts; initial PATH-related test/lint/type failures and corrected reruns remain
visible in the refresh history.

CodeRabbit CLI 0.8.2 completed one authenticated full-diff review including all
54 changed paths and untracked additions, with zero findings. The independent
review-agent security/defect inspection also found no actionable defect and ran
46 reconciliation/CLI regressions successfully. This does not certify a later PR
head or replace hosted provider reviews. Documentation review identified one mode
wording ambiguity: selector exclusion applies to portable import/export, while
normalized import requires a repository selector. That wording is corrected.

This is a local verification milestone, not final acceptance. The macOS native
report is historical UNKNOWN, all ten analyzers unsupported with a stale binding;
no full aggregate or native pass is claimed. Final staged checks, supported-Linux
matrix/analyzer assurance and hosted exact-head reviews remain pending. Their
live evidence belongs in the PR body and existing review ledger, without a
receipt-only source commit. Tasks 6.3 and 6.4 remain unchecked until their full
acceptance obligations are established. Version remains unpublished 0.1.0.dev0.

## Hosted static-quality correction — 2026-10-01

The first supported-Linux matrix at commit `822243c133ecaa2c0b4c78f033ed7edeb788d6a3`
([run 36783132528](https://github.com/nold-ai/changecost/actions/runs/36783132528))
ran all ten required analyzers on both Python versions. Eight passed; Radon and
Pylint failed with the same nine blocking findings. This is actual failing static
analysis evidence, not a behavioral TDD failure or accepted native pass.

Correction batch 4 separates source-chain selection, file overlap, snapshot/window
validation, coverage membership, portable-ledger ownership and immutable result
construction into focused functions. The source input comparison iterates the
already-validated input object's fields rather than Pydantic class metadata. The
coverage test cases retain their scenarios with fixture construction separated.
The internal schemas, transaction boundaries, CLI, exact amounts and thresholds
are unchanged. No analyzer suppressions or gate-policy changes were added.

Pinned local Radon 6.0.1 reports no complexity above the configured blocking
threshold of 15, and the affected functions have no more than seven parameters;
immutable-result construction now uses five. Pylint 4.0.7 with strict None/opaque
inference and pinned runtime imports reports no E/F findings in the six changed
files. This local diagnostic run is not sealed-capsule assurance: translating the
native blank decorator settings literally produced baseline-only context-manager
errors absent from the hosted report, so the local run retains Pylint's standard
context-manager recognition. Fresh hosted native results remain mandatory.

After the final refactor, 159 relevant tests and four installed-CLI subtests passed
in 4.06 seconds; Ruff/format and BasedPyright passed. Local diagnostic syntax and
intermediate type/inference failures were corrected and are not product TDD proof.
Full post-refactor matrix, independent affected-scope closure and exact-head hosted
analysis are recorded in the live PR/ledger once observed. Original failed native
reports remain in the run artifacts and ignored workflow receipts.
