# Codex reader preparation evidence

Prepared 2026-10-23 Europe/Berlin in planning mode. This record describes inspected
facts and a proposed architecture. Runtime implementation remains unstarted.

## Baseline and lifecycle

Freshly fetched main is `6b6fab30e8030e04fc1a2d803000c640c9f64479`. The owned
branch is `codex/prepare-provider-03-codex-local-import`. The maintainer selected
#36 and requested architect review. No published preparation branch/PR exists.
Native #36 readback found OPEN, User Story, parent #7, closed blocked-by #9/#12,
and private ChangeCost project #3 status Todo. No dependency or status change is
planned. PR #45 merged on 2026-10-18 at 23:47:47 Europe/Berlin. Its final live
verification index records accepted #35 implementation and correction evidence.

The separately requested actual CLI archive in this checkout succeeded on
2026-10-23. It created the [forecast archive](../2026-10-23-forecast-01-local-adaptive-demand/proposal.md)
and synchronized [adaptive demand](../../../specs/adaptive-demand/spec.md).
Readback preserved all 12 requirements/47 scenarios and the exact original delta
hash `f9e7cac1af7dffb86c15cdc9c64a34932658f52333bb462f20e5405f7b29b03b`.
No main spec was copied or manually merged. The original separate unpublished
2026-10-18 archive worktree remains intact. Accepted grouped-red and historical
review limitations remain recorded; existing review histories are not reset.

## Initial source evidence

`codex --version` reports `codex-cli 0.139.0`. The command
`codex app-server generate-json-schema --out <ignored-output>` succeeded without
starting a session, running a model or reading user logs. Its generated
ThreadTokenUsageUpdatedNotification requires threadId, turnId and tokenUsage.
TokenUsage has last/total breakdowns with inputTokens, cachedInputTokens,
outputTokens, reasoningOutputTokens and totalTokens. This proves installed
interface shape only. It does not prove persisted-file accounting, source
identity/finality, cache inclusion or Desktop producer compatibility.

The official [App Server reference](https://learn.chatgpt.com/docs/app-server),
accessed 2026-10-23, documents usage notifications and persisted JSONL thread
history. It does not establish a versioned offline accounting mapping for these
selected files. Remote API acquisition remains outside this reader scope. The
reference also describes listing that can repair metadata, so a remotely invoked
list/read workflow is not substituted for explicit read-only file acquisition.

The [canonical source register](../../../../docs/providers/source-profiles.json)
at initial preparation contained 23 profiles and zero approvals. Its
historical Desktop producer 0.159.0-alpha.12.1 representation remains partial and
is not relabeled from installed CLI 0.139.0. That initial preparation inspected no
native file. The subsequent authorized investigation inspected four existing native
snapshots. Its [accounting evidence](NATIVE_ACCOUNTING_EVIDENCE.md) supersedes that
initial no-sample state while preserving the zero-approval register. Exact producer
binding, replay/reset/correction and partial ownership/finality remain To-Validate.

## Architecture proof and comparison

The inspected code includes `cli.py`, `models.py`, `normalized.py`, `store.py`,
`economic_graph.py`, `reconciliation.py`, `coverage.py`, `demand_graph.py` and
`demand_history.py`. Grounding established these constraints:

- Evidence retains identity but no quantity/model/lineage/finality.
- Normalized economic input persists typed quantities but cannot preserve all
  required native provenance; its corrections require unchanged time windows.
  Current snapshot reconciliation also rejects nonsynthetic snapshot totals.
- DemandObservation needs prior assessment/ecosystem and exact bound Run context.
  Native policy, Run and Evidence each have separate rejecting demand guards.
- Store.apply already owns transactional graph validation and append-only records.
  Existing manual binding and portable availability remain the owners of those facts.

Three isolated candidates used configured gpt-6-astra, gpt-6.1-sol and gpt-6-luna.
The independent cross-judge selected the portable native fact design. The parent
read every candidate and agrees. Rubric scores are design judgments, not measured
product quality or compatibility:

| Candidate | Authority separation | Existing ownership/API | Safe acquisition | Replay/provenance | Bounded scope/evidence | Total of 10 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Existing normalized economics | 2 | 2 | 2 | 0 | 1 | 7 |
| Portable native fact | 2 | 1 | 2 | 1 | 2 | 8 |
| Alternate native fact | 2 | 1 | 2 | 1 | 1 | 7 |

Existing economics was rejected as a full solution despite its small change size.
The selected design adds one portable NativeUsage record without native demand
projection. Grafts retain explicit native mode, one approval authority, separate
manual binding, safe receipts, source categories including total, unknown states
and semantic replay across changed snapshot digests. No stage-based parser API,
sidecar persistence or optional atomic binding remains. Cross-model diversity was
limited to available GPT variants. See [design](design.md) for the synthesized
caller-first sketch and tradeoffs. No runtime bodies were implemented.

## Checks and limits

Before the selected plan edits, strict OpenSpec validated all 15 items. The actual
post-archive strict run rejected the CLI-generated Purpose placeholder. A descriptive
metadata repair retained every nonblank requirement/scenario line; all 15 items
then passed. Raw command results and the comparison report remain ignored local
evidence. No failing product test or native approval is fabricated for planning.

The first explicit-base/manifest make check ran all 3,209 tests successfully and
passed lock/tool controls, lint/format, typing, hygiene, workflow, build proofs and
strict OpenSpec. It failed documentation freshness for unchanged generated
commands and produced no SpecFact report because the local code-review module
was missing. The missing report remains incomplete assurance. The documentation
rationale and selected final planning checks are recorded at the final checkpoint;
implementation acceptance cannot certify this later lifecycle/planning diff.

## Remaining gates and rollback

Approve one exact source mapping before native implementation. Its evidence must
resolve stable identity, request/snapshot overlap, revisions/reset, cache/reasoning
inclusion, root/subagent ownership and finality. No missing quantity becomes zero.
Native demand requires separately authorized projection and policy work; measured
#17 evaluation still requires preregistration before evaluated outcomes.

Scope is artifacts and correlated issue reconciliation, plus the requested #35
CLI archive and authorized read-only native evidence research. No paid service,
runtime reader, collection, new approval or release
is added. Implementation time remains unknown until native proof exists. Revert
the eventual scoped planning/lifecycle commit to roll back, retaining the separate
archive, source originals and review histories. New portable records would require
preserved backups and an explicit old-reader incompatibility boundary later.

## Issue synchronization and local review checkpoint

Issue #36 was read immediately before its body-only reconciliation and read back
with exact new content. Native readback retained OPEN, User Story, parent #7,
closed prerequisites #9/#12, the same labels, no assignees and private project #3
Todo. No hierarchy, dependency, date or project mutation occurred. The issue
states local/unpublished preparation and the pending delivery disposition.

Selected strict validation and documentation ownership/link checks pass after
binding the unchanged generated command reference to its inspected source digest.
The independent comment review found zero actionable comments in the six selected
planning files. Final whole-diff review and applicable aggregate results remain
bound to the ignored preparation receipt, not a fabricated native report. No
runtime probe or product red/green execution is needed for these artifact-only
edits; actual product TDD remains future unchecked implementation work.

## Restored plan and native accounting investigation

On 2026-10-23 the maintainer requested restoration of the scoped stash and work on
native accounting approval blockers before implementation. Fresh main remained
`6b6fab30e8030e04fc1a2d803000c640c9f64479`. All 38 saved path fingerprints were
restored exactly without restoring index state. The original stash and review
genesis/counters remain intact. The additional evidence document is explicitly
included in the continued local review scope. No new review allowance was created.

The [native evidence matrix](NATIVE_ACCOUNTING_EVIDENCE.md) binds four immutable
acquisitions, 85 request records and exact tagged producer source. Request/turn/thread
overlap is established. Legacy snapshots can contain context estimates and inherited
baselines. Optional backend detail fields can become serialized zero. Best-effort
usage records cannot prove complete attempts or successful finality. A resumed file
retains its creation header, so exact producer compatibility remains unproven.

No source approval is issued by these findings. All ten implementation tasks remain
unchecked. Private paths, identifiers and quantities stay in ignored local receipts.
The restored preparation and additional evidence remain local and unpublished.

## Existing provenance and edge-case search

The subsequent maintainer request authorized finding existing build and native
replay/reset evidence, followed by a fresh independent approval review. Historical
application logs report local engine 0.163.0-alpha.10.2 and correlate three selected
thread/turns. The current executable at the logged path reports 0.163.0-alpha.11.2,
so its hash cannot attest the old process. Retained engine-database evidence covers
only 2026-10-23 in the inspected main image. No telemetry was enabled.

Actual reacquisitions preserve all 85 original request facts. Linked parent histories
add 318 observed turn-scope restarts, 81 compaction-associated last-snapshot changes
and 975 equal legacy total counters. All parent histories exceed the reader's unchanged
10 MiB cap and remain research-only. No copied/appended request replay or native
correction was recovered. The [updated matrix](NATIVE_ACCOUNTING_EVIDENCE.md#existing-provenance-and-native-edge-case-follow-up)
distinguishes those observations from mapping approval and records corrections to
the earlier logical-session and top-level-parent interpretation. Implementation
remains blocked. The fresh exact-candidate adjudication denied runtime approval.
It credits medium-confidence producer corroboration for the selected Desktop segment
and narrowly verified replay/reset/compaction observations. An enforceable producer
binding across resume, explicit partial-policy acceptance and recognizable unsupported
lifecycle boundaries remain the approval gates. Missing historical signing or a log
for every response is not an independent veto under the ordinary local trust model.
At that preceding stage the canonical register remained at 23 profiles and zero
approvals. Subsequent semantic approval and activation are recorded below.

## Finite producer-binding architecture

The 2026-10-23 planning-only follow-up defines the
[producer-binding contract](PRODUCER_BINDING_POLICY.md) and
[retained pre-activation proposal](PROPOSED_PROFILE.json). Three candidates and an
independent cross-judge selected finite exact snapshots over general process
receipts. Supporting drafts, comparison, complete classification, canonical
projection and authored digest controls are retained locally under
`.changecost/workflow/provider-03-codex-local-import/architect-producer-binding-20261023/`.
Controls prove specified hash consequences only, not implemented reader behavior.
Semantic approval, canonical activation and implementation assurance are distinct.
No canonical profile, runtime module or test baseline is edited by this planning task.

The final explicit-base/manifest aggregate run passed 3,209 tests, lint/type checks,
lock/tool probes, hygiene, documentation/index/metadata/workflow, constrained package
build/install and all 15 strict OpenSpec items. Dependency audit was explicitly
not applicable because its locked inputs were unchanged. Aggregate acceptance
remains incomplete: SpecFact CLI 0.55.4 reports missing
`nold-ai/specfact-codebase` and produces no native assurance report. Supported-Linux
and current external-provider assurance remain outstanding. Earlier sandbox cache,
read/write hook and inherited MAKEFLAGS failures are retained in separate logs;
the corrected aggregate used environment base/manifest and normal cache access.

Independent exact-mapping review now approves the finite profile and all six
decisions at digest `8be47bbc66c0b04d61bcc4e646271449b4eb653b460c24322cfd203bc5d2a991`.
See the [bound disposition](NATIVE_ACCOUNTING_EVIDENCE.md#independent-finite-mapping-approval)
for report/projection/decision hashes, native reproduction and limits. No canonical
activation or implementation occurred; all ten implementation tasks remain unchecked.

## Canonical activation follow-up

The maintainer subsequently authorized activating the exact reviewed finite P/R,
contributor admission checks and the historical zero-approval baseline update.
The register now contains 24 profiles and one finite usage approval; the original
23 objects remain unchanged with zero approvals. See [activation evidence](TDD_EVIDENCE.md)
for red/green controls and independent verification. The immutable proposal and
original semantic receipts remain retained. Reader implementation stays blocked.
