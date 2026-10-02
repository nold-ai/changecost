# Settlement preparation evidence

Status: **locally prepared / unpublished; implementation not started**.
Preparation date: 2026-09-29 (Europe/Berlin). Base and HEAD:
`999cb8f960785fe4ac0434d41a0892beca933191`, refreshed from `origin/main` and
verified on 2026-09-29 at 20:25:44 +02:00. The preparation branch is
`codex/prepare-settlement-01-reconciliation`. It carries the maintainer-approved
archive-skill correction and Core-02 CLI archive from the same base; no unrelated
work was present. Local main and origin/main have the same recorded SHA.

## Selection and prerequisite

Settlement reconciliation (#12) is the next change previously identified with the
maintainer, following accepted Core-02 in [PR #25](https://github.com/nold-ai/changecost/pull/25).
Its only implementation prerequisite is Core-02 (#11), delivered at the base above.
The archive used `openspec archive core-02-change-run-contracts --yes` in this
checkout. The CLI synchronized 18 requirements and archived all artifacts;
readback compared the full requirement blocks and metadata. Strict validation
passed all ten active-change/main-spec items. No manual spec merge or folder move
was used. The old Core-02 review receipt remains intact.

| Alternative | Prerequisites and evidence | Scope / disposition |
| --- | --- | --- |
| Settlement reconciliation | Core-02 delivered; generic economic semantics need preparation | Selected: normalized evidence, settlement records, persistence, CLI and synthetic tests. |
| Source feasibility | Three tasks still unchecked; provider exports/custom-hook evidence missing | Remains active; no new live collection is authorized here. |
| Copilot/Cursor adapters | Reconciliation plus inspected per-source feasibility missing | Remain blocked; no provider parser or claimed mapping is added. |
| Empirical quotes | Reconciliation absent | Can be planned later; no estimator work in this preparation. |

## Code findings at the recorded base

| Claim | Finding | Planning consequence |
| --- | --- | --- |
| No runtime/package exists | Outdated: models, SQLite storage, bind, lifecycle-only settle and explain are merged. | Reuse these boundaries and keep their tests. |
| Evidence is ready for arithmetic | Incomplete: `Evidence` stores identity/profile only, no component, event interval, temporal lane or correction payload. | Specify a strict economic evidence contract, retaining stable core references. |
| Settlements have a replay cutoff | Absent: the current record has scope text, components, coverage and references but no captured cutoff, algorithm version or complete membership declaration. | Persist structured computation and coverage provenance. |
| Portable missing correction references can be retained | False for `RecordRef`: `validate_graph` rejects absent references. | A pending correction uses a typed source locator, not a dangling core reference. |
| Reimport deduplication is already economic deduplication | False: `Store.identity` rejects identical source identity under a second record ID. | Normalize stable event identities before core insertion; separate semantic conflict from retry. |
| Settlement history supports arbitrary parallel scopes | False: current predecessor chains have one root/successor per Change. | Define one local computed ledger with scope recorded per revision; preserve imported claim chains separately. |
| Imported `verified_provider` or `reconciled` is trusted | False: current docs explicitly retain producer assertions only. | Source policy is a local, versioned implementation decision; portable labels cannot certify support. |

Read: `src/changecost/models.py`, `store.py`, `operations.py`, `serialization.py`,
`cli.py`; tests for contracts, store and offline commands; [delivered contracts](../../specs/change-run-contracts/spec.md)
and [runtime documentation](../../../docs/contracts.md). The source feasibility
matrix still marks actual monetary/completeness profiles unverified. No provider
sample or account configuration was read or changed by this preparation.

## Primary-source research

Accessed **2026-09-29 (Europe/Berlin)**. These sources constrain generic semantics;
they do not establish Copilot/Cursor support.

| Source and version | Confirmed fact and impact |
| --- | --- |
| [Python decimal documentation, 3.11](https://docs.python.org/3.11/library/decimal.html) (served as 3.11.16) | Input construction retains digits, while arithmetic uses context precision, normally 28. Use explicit exact arithmetic and detect inexact results; merely using Decimal is insufficient. |
| [SQLite aggregate functions](https://www.sqlite.org/lang_aggfunc.html) | Noninteger `sum()` uses approximate floating arithmetic; `total()` is floating. Do not aggregate financial TEXT through SQL sum/total or infer missing values from their null/zero behavior. |
| [SQLite isolation](https://www.sqlite.org/isolation.html) | A write transaction can reserve the writer before reading. Capture computation inputs and persist the revision consistently, with explicit busy/failure handling. |
| [SQLite backup API](https://www.sqlite.org/backup.html) | The backup interface is appropriate for a consistent database copy. Keep rollback separate from portable import, which changes destination availability. |
| [Pydantic model documentation, current v2](https://pydantic.dev/docs/validation/latest/concepts/models/) | Copied/constructed models cannot be assumed validated. Preserve strict revalidation and sanitized diagnostics at public write boundaries. |
| [OpenTelemetry metrics data model](https://opentelemetry.io/docs/specs/otel/metrics/data-model/) | Delta/cumulative identity, reset timing and gaps matter. Overlap guidance is marked Development; it does not prove which provider lane is authoritative. Treat ambiguous overlap/reset data as unresolved rather than infer billable amounts or interpolate. |

## Local preparation probes

Actual environment: Python **3.13.14**, SQLite **3.53.1**, Pydantic **2.13.5**,
Typer **0.27.2**. The project's required later behavior matrix remains Python
3.11.15 and 3.13.14. A primary source's served patch version is not a claim that
that patch version is installed here.

Command: `.venv/bin/python` with a disposable stdlib/model-inspection script.
Output: ignored `.changecost/workflow/settlement-01-reconciliation/preparation-probes.json`.

- Precision-28 Decimal addition of `10000000000000000000000000000 + 1` lost the unit;
  enabling the `Inexact` trap detected it. This is a decimal-digit boundary, not a
  measured provider amount.
- SQLite `sum()` over TEXT `0.1` and `0.2` returned `0.30000000000000004`.
- Two otherwise identical Evidence identities with record IDs `one` and `two`
  raised `conflicting stable identity or binding`.
- Model-field inspection confirmed the missing economic payload/cutoff fields above.

These are preparation probes, **not product failing/passing TDD**. Implementation
must derive meaningful tests from the updated scenarios and observe real failures
before changing behavior.

## Tracking, review and disposition

Initial live readback: #12 was CLOSED and its private ChangeCost project item Done,
while all eleven original implementation tasks were unchecked. #11 remained OPEN,
with PR #25 merged; the native #12 blocked-by #11 edge was present. The selected
issue was updated with the scoped plan, reopened and restored to Todo; final
state/project/labels/assignees readback succeeded. #11 remains administratively open.
No dependency or parent edge is intentionally changed.

A genuinely new bounded preparation/review session was initialized under
`.changecost/workflow/settlement-01-reconciliation/`; previous change receipts were
not reset. Its scope includes the approved skill fix, CLI archive/link maintenance
and this planning work. Remote reviewer identities are the actual REST logins
`chatgpt-codex-connector[bot]` and `coderabbitai[bot]`; required checks are
`quality (3.11.15)`, `quality (3.13.14)` and the `CodeRabbit` status context.
No remote plan branch or PR exists yet. The maintainer resolved the development
boundary on 2026-09-29: all planned changes remain in the first unreleased 0.x
alpha/preview feasibility study. The concrete plan now evolves the current internal
artifact schema, retaining strict unknown-input rejection and data-preserving store
failure handling. No public v2, dual-format compatibility layer or migration
programme is planned. Work remains intact/uncommitted pending the required
planning-PR versus scoped-stash delivery choice.

## Limits and rollback

Confidence: high in code/interface findings and observed probes; provider completeness
remains unknown. No paid infrastructure is needed. Implementation size is larger
than an arithmetic helper because it includes portable evidence, local history,
coverage and failure recovery; no delivery-time estimate is asserted.

- False completeness: separate source claims from local policy and require full Run coverage.
- Duplicate/corrected cost: deterministic identity, pending-target diagnostics and immutable revisions.
- Lost precision/history: checked exact aggregation, committed cutoffs and backup/non-mutation tests.

Rollback this preparation through its eventual planning commit or scoped stash;
restore only owned changes. Do not delete runtime databases or historical receipts.
Implementation rollback must preserve a consistent backup and the matching checkout,
and avoid an older reader writing an incompatible internal store. Planning acceptance authorizes no product
implementation, release or live collection.

## Draft verification checkpoint — 2026-09-29

- `openspec validate settlement-01-reconciliation --strict --no-interactive`: pass.
- `openspec validate --all --strict --no-interactive`: 10 items passed, 0 failed.
- `BASE_REF=999cb8f960785fe4ac0434d41a0892beca933191 MANIFEST=.changecost/workflow/settlement-01-reconciliation/intended-files.txt make check`: exit 1, **incomplete** solely because all ten required SpecFact analyzers report `unsupported_controller_platform` on macOS. This is not full assurance.
- Lock resolution and host guard probes, hygiene, Ruff/format, BasedPyright,
  documentation/index, metadata, workflow, package build and OpenSpec leaves passed.
  Tests: **806 passed in 64.18 seconds**, Python 3.13.14. Dependency audit was
  correctly not applicable because locked dependency/audit inputs did not change.
- Primary-source and preparation probes are evidence for planning decisions only.
  No implementation tests were added; the full existing suite is regression evidence.
- `git diff -- src tests pyproject.toml uv.lock` is empty. Product code, dependency
  versions and runtime behavior are unchanged by preparation.
- Documentation-only checkpoint/readback additions after the aggregate are covered
  by a final docs/index/metadata validation; they do not establish native review.

The full gate log is ignored at
`.changecost/workflow/settlement-01-reconciliation/make-check.log`.
The compatibility scope decision is resolved and the portable delta is now present.
Verification remains **To-Validate**: supported-Linux native assurance is still required. #11's open issue
state remains a tracking discrepancy despite merged implementation evidence.
No plan commit, remote branch, PR, stash, product implementation or release has been created.

## Maintainer clarification and site readback — 2026-09-29

The maintainer explicitly confirmed that nothing has been published and all planned
changes are part of the first pre-v1 0.x alpha/preview feasibility study. Local
`pyproject.toml` confirms `0.1.0.dev0`. The [project home page](https://changecost.dev/)
was fetched successfully with curl after the browser fetch was unavailable; it
labels the project an unreleased pilot and treats provider compatibility and
prediction quality as unvalidated. The page does not establish a public artifact
version or a cross-release migration requirement. No website changes were made.

The earlier v2 choice was unnecessary and is withdrawn. The issue, plan, shared
phase guidance and review-session decision are reconciled with this clarification.
Previous test counts above remain scoped to their recorded run; the final
planning-only refinements receive fresh OpenSpec/docs/index/metadata validation.

Final preview-scope checks: selected/all strict OpenSpec, documentation links and
ownership, generated index, metadata and diff whitespace checks passed after the
new portable delta was added. The selected issue was re-read after its scope update:
OPEN/Todo, User Story, parent #7, prerequisite #11 and original labels/unassigned
state are preserved. Runtime and dependency diffs remain empty. No additional
runtime test run is claimed for these planning-only edits.


## Subsequent implementation handoff

The maintainer subsequently invoked `$changecost-implement settlement-01-reconciliation`
on 2026-09-29. The prepared files were carried directly, without a stash or planning
PR, into the implementation now at `/Users/dom/.codex/worktrees/settlement-implementation/changecost`
on `codex/settlement-reconciliation`. See [TDD evidence](TDD_EVIDENCE.md) for actual
behavior, reviews, both interpreter suites and the remaining native assurance gate.
Earlier preparation-only/no-implementation statements above describe that prior stage.
