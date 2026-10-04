# Advisory workflow preparation — 2026-10-05 (Europe/Berlin)

## Scope, freshness and disposition

Selected change: workflow-01-advisory-ci, issue [#16](https://github.com/nold-ai/changecost/issues/16).
Fresh main fetched successfully at approximately 00:09 Europe/Berlin on 2026-10-05:
`340668e6b74bfb7ccab15efe13830555bc6dd7ef`, including merged PR #32 Quotes and
PR #33 source-feasibility checks. HEAD matches the fetched SHA; owned branch
`codex/archive-quote-and-prepare-next`, worktree 7808. Prior clean-main fast-forward
was performed before creating this branch; current dirty archive work is preserved.
The user explicitly requested this same worktree and later combined delivery,
overriding the default separate clean preparation branch and PR/stash disposition.
Preparation is local/unpublished, without runtime changes, stash, commit, push or PR.

Fresh issue readback: #16 Open/Todo, parent #8, sole native blocked-by prerequisite
#15 closed. No new dependency or provider approval follows from this reconciliation.
After the authorized issue-body synchronization, exact body readback matches; native
User Story type, labels, parent #8, sole closed prerequisite #15 and private project
#3 Todo were read back unchanged. The ignored receipt retains source fields.

## Confirmed, outdated and unknown claims

| Prior claim or ambiguity | Disposition and inspected evidence |
| --- | --- |
| No runtime package or main specs exist | Outdated: pyproject.toml, installed CLI help and accepted contracts/reconciliation/Quote main specs are present. |
| Registration/outcome operations need implementation | Delivered: src/changecost/cli.py bind/settle and existing installed-wheel/lifecycle tests. Keep regression coverage, not duplicate implementation tasks. |
| Every result needs versioned economics fields | Over-specified: identity registration and export acknowledgements are not economic results; preserve existing JSON success payloads. Version new check/error outputs only. |
| CLI human format and structured parser/errors already exist | Not delivered: cli.execute emits existing JSON and plain safe error strings; help shows four command families and no format/check options. |
| Settlement inputs_available proves full reproduction | False: reconciliation.inspect_computation checks local receipt/cutoff/input availability, not complete material result equality. Numeric advice needs read-only cutoff reproduction. |
| Imported complete/priced claims may receive numeric advice | Resolved by maintainer: unknown with displayed declared amounts/provenance unless supported local computation verifies values/completeness. Artifact-only mode therefore remains unknown. |
| Portable artifact checking needs import or store mutation | Unnecessary: strictly read/validate existing bundle and selected claim without opening a database; no portable receipt or stateless certification is added. |
| Scope/quantile/Decimal/exit behavior is unspecified | Resolved: explicit record ID/kind, budget identity, exact nonnegative Decimal; p90 default/p50 option, declared historical scope, valid statuses exit 0 and technical failures exit 2. |
| Summary limits and shell safety | Confirmed from current GitHub primary docs; fixed 65,536-byte UTF-8 application limit is an approved pilot default, not a vendor guarantee. |
| Provider compatibility/calibration | To-Validate: source-profiles register approves no provider mappings, #9 remains separate; this workflow uses controlled synthetic fixtures. |

Local interfaces inspected: src/changecost/cli.py, models.py, quotes.inspect_quote,
reconciliation.inspect_computation/computation_details/snapshot_records, the accepted
main specs, docs/cli.md and docs/settlement.md, existing CLI/installed-wheel proofs,
quality workflow/docs/index and bounded-session input rules. Tool evidence: OpenSpec
1.13.2; Python 3.13.14 environment; package remains 0.1.0.dev0. No product TDD is claimed
for this planning-only diff. New runtime scenarios require genuine red/green later.

## External sources and versions

GitHub primary documentation rechecked on 2026-10-05 (Europe/Berlin):
- [Job summaries](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands#adding-a-job-summary): per-step summary file, 1 MiB upload limit, upload failures alone do not fail the job. Enforce a smaller explicit application bound and preserve write errors.
- [Script injections](https://docs.github.com/en/actions/concepts/security/script-injections): context/artifact values are data and cannot flow into executable interpolation. Use Python rendering and data arguments.
- [Workflow permissions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions): explicit read-only repository permissions; reuse reviewed pinned local setup.

The prior access date 2026-10-04 remains historical in the approved conversation plan;
this preparation records its own 2026-10-05 readback. No provider capability is inferred
from GitHub documentation.

## Obligations and review boundaries

Stable intent: readable presentation and honest budget advice, with no enforcement,
provider policy, conversion, persistence change or collection. Invariant/dependency
mapping proposed here requires an independent upfront review before runtime work:
- Presentation/parser → existing JSON/exit/privacy contract and no-store help/error behavior.
- Numeric advice → typed receipt, supported metadata, immutable historical snapshot,
  economic identity, exact comparison and requested-scope completeness reproduction.
- Unknown claims → portable schema validation/provenance without manufactured authority.
- Summary → allowlisted versioned check result, data-only escaped UTF-8 bounded output,
  independent technical/quality failure handling.

Independent preparation review also inspected coverage.py: narrowed Run windows
retain partial_change_scope in the delivered evaluator. Artifacts explicitly preserve
that reason/unknown advice instead of inventing narrower completeness or filtering
unknown reasons. This removes an over-promise without changing approved budget trust.

Use the existing behavioral evidence packet for specification/oracle/generator/config
fingerprints and actual native report digests. A new bounded session is initialized
only after checking known worktrees for prior #16 receipts; three correction batches
and 90 active minutes are the default, never a reset of Quote counters. Bind the full
combined archive/preparation manifest. Later runtime scope requires an explicit bound
scope adoption; independent review and current-head Codex/CodeRabbit remain required.
There is no runtime oracle/generator/native success for this new capability yet.

## Checks, issue sync and limits

Selected/all strict validation and the explicit-base make check were executed;
the actual results are recorded below. Existing macOS unsupported native analyzers stay incomplete; earlier
Quote/archival assurance cannot certify new inputs. No current runtime or external
review completion is inferred from schema validation or planning review.

## Risks, confidence and rollback

Confidence: high in scope reconciliation and observed interfaces; runtime reproduction
and CI execution remain unimplemented/To-Validate. Misleading imported completeness is
mitigated by unknown provenance; historical leakage by original cutoff reproduction;
script/markup injection by data-only escaped bounded output. No paid infrastructure.
Preserve archive artifacts/spec and unrelated work. Restore/revert only preparation
artifacts/correlated docs to roll back; retain recovery evidence and future stores/backups.

## Independent preparation review

One read-only independent Codex subagent reviewed the complete updated artifact
packet against CLI/models, Quote replay, Settlement evaluator and coverage policy.
It found the narrowed-scope completeness over-promise; affected readback verified
the corrected partial_change_scope scenario/design and retained unknown behavior.
No other actionable preparation findings remain. This is planning/code-boundary
review, not the future upfront runtime architecture review, product TDD, hosted
Codex/CodeRabbit review or native analyzer assurance.

## Actual preparation checks — 2026-10-05 (Europe/Berlin)

`BASE_REF=340668e6b74bfb7ccab15efe13830555bc6dd7ef
MANIFEST=.changecost/workflow/workflow-01-advisory-ci/manifest.txt
PATH="$PWD/.venv/bin:$PATH" make check` ran all leaves against the captured
pre-check session binding. Environment assignments avoid the earlier archive
invocation's inherited GNU make fixture override; both host lock and make-test
missing/stale/failure/repair/input proofs pass without changes or bypasses.

- Python 3.13.14 / pytest 9.1.1: 1,791 existing tests passed in 129.41 seconds.
- Two clean installed-wheel offline proofs passed in 6.876 seconds.
- Hygiene, lint/format, types (zero errors), docs ownership/links, generated index,
  metadata and workflow checks passed. Dependency audit is not applicable because
  locked dependency/audit inputs are unchanged.
- Selected change validation passed; strict all-item validation passed 11 items.
- The aggregate exited nonzero: SpecFact CLI 0.55.4 reports FAIL/UNKNOWN with all
  ten required analyzers unsupported_controller_platform on macOS. This is not
  passing native assurance, and no fresh Linux/public review is claimed.

Native report/log digests and original binding are retained under ignored
`.changecost/workflow/workflow-01-advisory-ci/`; generated-reference source rationale
for unchanged docs/commands.md was refreshed after navigation changes. The initial
preliminary docs check caught that stale rationale; final aggregate docs/index pass.
No runtime code/tests/dependencies/active workflow changed, so these existing-suite
results are regression evidence, not new-capability TDD. The final result-recording
doc edit receives a new binding and scoped docs/index/spec/diff readback; prior
aggregate evidence retains its original binding instead of being rebound as current.
Future runtime oracle/generator remain not authored, explicitly incomplete in the
obligation map; no complete behavioral packet or product test proof is fabricated.

Issue #16 body, type/labels/hierarchy/dependency and private Todo status were read
back after synchronization. Its historical published artifact links are preserved
and labeled historical; the new revision is explicitly local/unpublished with no
invented remote link. Quote archive hashes are unchanged byte-for-byte. Runtime
source/tests, dependency manifests and active workflows remain unchanged.
Confidence is high in planning consistency; native assurance and all runtime
capability/public-review obligations remain incomplete. The reviewed local diff is
retained for the requested later combined delivery, with no stash/commit/push/PR.
