# Source-feasibility research evidence

Date: **2026-09-28 (Europe/Berlin)**. Status: **partial research delivery;
personal-source/profile verification pending**. This is documentation and synthetic
fixture work, not runtime behavior. TDD and SpecFact product analysis are not
applicable; no runtime test/analyzer pass is claimed.

## Reviewed inputs and scope

- Fresh main: `06736cbdb268c62b834ceac6448a923215f071a6`, fetched and
  fast-forward checked at 2026-09-28 09:43:07 +02:00; clean starting tree.
- Branch: `codex/pilot-01-source-feasibility`. No matching prepared receipt,
  stash or open planning PR existed. Artifacts came directly from fresh main.
- OpenSpec 1.13.2: `spec-driven`, apply state `ready`, initially 0/11 tasks.
- Issue [#9](https://github.com/nold-ai/changecost/issues/9) was open, Todo, with
  no native blocked-by issues. Both planned provider adapters still depend on
  feasibility and reconciliation; no dependency changes are required.
- The maintainer authorized research implementation, extended research to Codex
  and Claude Code, then explicitly authorized inspection of existing local artifacts.
  No model request, new telemetry collection or account configuration was performed.

## Evidence review

Primary citations and their access dates are in the
[capability matrix](../../../../docs/providers/source-feasibility.md) and
[Codex/Claude comparison](../../../../docs/providers/codex-claude-metrics.md), plus the
[Cursor local assessment](../../../../docs/providers/cursor-local-metrics.md) and
[hosted Copilot assessment](../../../../docs/providers/copilot-local-metrics.md), plus the
[Enterprise projection review](../../../../docs/providers/enterprise-schema-review.md).
Rolling documentation is not a guarantee about installed versions or account tiers.

The local review inspected three recent JSONL files per tool, projecting metadata
only. Its 2026-09-28 09:52 Europe/Berlin snapshot records versions, field shapes,
identity/repetition counts and source-byte hashes in ignored local receipts.
Active source files may change; the receipt identifies the inspected byte snapshot,
not an assertion that a later full-file hash is unchanged. Raw inputs remain in
their original stores; no transcripts or original identifiers/quantities were copied
to the repository. Original-to-synthetic identifier mappings are not published.

A subsequent maintainer-authorized Cursor 3.22.7 Basic-account inspection selected
one supplied session from the existing local SQLite store. Two read-only snapshots
at 10:04:52 and 10:07:59 +02:00 showed populated context occupancy, empty usage data
and zero input/output counters in 22 bubble records. The Basic tier is reported by
the maintainer. Private receipts retain hashes and actual quantities; the shared
fixture uses invented quantities and identifiers. Context values agreed with their
breakdown sum and percentage formula. Source hashes changed between snapshots;
no final consumption or billed total was established.

A further authorized VS Code hosted Copilot inspection at 10:17 +02:00 found an
explicit host-to-SDK identity link, one persisted turn-usage row and one durable
SDK usage checkpoint. Turn/direct token totals agree, while top-level token fields
have a different scope. A session-named nano-AIU value is lower than the turn/direct
and checkpoint values. The 366-event snapshot has no ephemeral `assistant.usage`
or `session.shutdown`; this does not establish zero usage or final completeness.
The maintainer confirmed Personal Free for this session. Installed versus recorded
runtime versions remain distinct. Metadata projections
and source hashes are in ignored local receipts; shared values/IDs are synthetic.

Confirmed findings:

- Cursor export claims conflict across dated vendor posts; replace the blanket
  removal assumption with an explicit inspection gap.
- Codex Desktop rollout runtime and envelope differ from installed CLI/protocol
  metadata. Cache-write token fields and repeated cumulative values exist locally.
- Claude local records repeat request/message identity across distinct record IDs;
  older samples change output-token usage within those groups. Per-record summation
  and first-record selection cannot establish correct totals.
- Cursor local context fields match the documented context-window concept; zero
  message counters do not establish zero usage or charges.
- Local token metadata is partial evidence. Billed charges, other account tiers,
  completeness, correction precedence and automatic change attribution are not proven.

The supplied Enterprise bundles were reviewed separately on 2026-09-28. All 17
manifest entries and the supplied manifest sidecar match. Thirteen JSON documents
and two JSONL illustrations parse, but one JSON document repeats two equal-valued
members; strict fixture admission remains blocked for that sample. Three synthetic
Cursor occupancy examples pass arithmetic and projected bubble joins. Independent
session clocks, omitted groups, schema-only illustrations and uninspected stores
prevent stronger conclusions. Originals were preserved, not reformatted or promoted
to native fixtures. Private hashes/check details are in `enterprise-artifact-review.json`.

## Scenario review

| Spec scenario | Evidence / disposition |
| --- | --- |
| No inspected export | Copilot OTel/Cursor CSV and uninspected stdout/OTel profiles remain unverified with explicit evidence requests. |
| Enterprise-only capability | Official Cursor Enterprise prerequisite recorded; excluded for personal pilot. |
| Tokens without money | `tokens-only`: distinct 100 input/20 output tokens, monetary value absent. |
| Missing session identifier | `timestamp-only` and `ide-window-only`: no provider-backed change join. |
| Codex usage without billed cost | Installed interface evidence separated from inspected Desktop rollouts; cash unknown. |
| Claude Code cost estimate | `claude-estimated-cost`: 0.03 USD is an estimate, not a bill. |
| Repeated cumulative metrics | Copilot repeated root/child case, Codex snapshots and Claude cumulative metric example preserve non-additive boundaries. |
| Installed CLI differs from recorded runtime | Local version comparison and `codex-rollout-cache-write`; extra field preserved without conversion. |
| Repeated messages with changing usage | Local Claude identity/usage review and `claude-message-revisions`; finality remains unverified. |
| Cursor context with empty usage counters | Two local snapshots and `cursor-context-not-consumption`; occupancy stays separate from consumption and completion does not settle finality. |
| Hosted Copilot identity and usage projections | Explicit host/SDK linkage, inspected turn usage/checkpoint, SDK event documentation and `copilot-hosted-usage-boundaries`; finality remains unknown. |
| Enterprise projections with withheld evidence | Supplied schema-only and transformed projections; native types distinguished from output types, no cross-session timing claim. |
| Absence in a different source container | Narrative checkpoints/catalogs do not establish SDK/per-session usage absence. |
| Custom session-log hook with disabled OTel | Maintainer reports no Admin API call; tentative log parsing/conversion/upload path recorded separately from uninspected native input, mapping and receiver output. No OTel enablement required. |
| Positive message counters without accounting boundaries | `enterprise-message-counter-boundary` plus v2 producer-reported field review; no assumed repeat or billing semantics. |
| Documentation-derived examples with encoding discrepancies | `documented-example-not-wire-evidence` and received-v2 hash/arithmetic audit; OTLP enum and normalized-envelope findings recorded separately. |
| Reviewable fixture | Eighteen synthetic cases with provenance, allowlisted fields and explicit fictional versus observed-shape distinctions. |

Additional cases cover missing root billing, multipliers, overlapping files and
fictional replacement corrections. The correction example does not establish any
provider's native correction contract. These are reviewed research examples for
later test design, not an implemented normalizer.

## Verification results

Executed on 2026-09-28 (Europe/Berlin), using pre-commit 4.6.2 and OpenSpec 1.13.2:

| Check | Actual result |
| --- | --- |
| `openspec validate pilot-01-source-feasibility --strict --no-interactive` with `OPENSPEC_TELEMETRY=0` | Passed. |
| `make check` | Passed repository hygiene and all nine strict OpenSpec changes after resolving sandbox access. Initial attempt failed because the EOF hook opened protected tracked skill files; it was not a content/test failure. |
| `pre-commit run --files` with all nine authored new file paths (received artifacts excluded) | Passed applicable hooks, including JSON. The all-tracked-files run alone skipped JSON because the fixture was untracked. |
| Fixture relationship assertions | Passed all eighteen cases (including v2 message-counter and encoding boundaries): root/child/replay identity, missing fields, revision history, cumulative repeats, changed message usage, context versus consumption, and hosted Copilot identity/usage boundaries. |
| Relative Markdown link/anchor assertions | Passed across changed/new docs and `llms.txt`. Manual index review confirmed unchanged skill inventory and no implemented product command claims. |
| Original research SHA-256 comparison | Both immutable exports match the hashes in `docs/research/README.md`. |
| Fixture privacy review | All values authored synthetically; inspected key set and relationships, no copied content/credentials/identifiers. Automated key/private-key checks supplement this manual review. |

Fixture SHA-256:
`cd40d19f56709dc97cbe4b5e0b30205d543f68bd5c23fa1dfea79dc9f38f512e`.
The local check script and schema artifacts are ignored workflow evidence, not new
runtime tools or repository quality gates. No behavior tests, SpecFact analyzers,
dependency audits or release/version bump were applicable to this docs/fixture diff.

Issue #9 was re-read immediately before its body update and read back afterwards
at 2026-09-28 10:00 Europe/Berlin, then updated and verified again with the Cursor
findings at 2026-09-28T10:12:41+02:00. It records expanded scope, partial findings,
remaining evidence and locally implemented/unpublished status. Native User Story
type, parent #5, labels, assignees (none), no blocked-by issues, private ChangeCost
project membership and Todo status were verified. Provider #13/#14 blockers remain
#9/#12. No new issue, dependency edge, remote branch or PR was created.

The hosted Copilot update was synchronized and read back at 2026-09-28T10:32:19+02:00.
Issue type, parent, blockers, labels, assignees and project status were preserved.
The full repository check initially encountered an automatic approval-review timeout;
the permitted retry passed. No content failure or unresolved approval remains.

Enterprise comparison findings were added to issue #9 and read back at
2026-09-28T12:20:16+02:00; open/Todo status, type, parent, blockers, labels and
assignees remain unchanged. No artifact contents or identities were uploaded.

The maintainer subsequently reported work OTel globally disabled. The latest
clarification supersedes the earlier Admin API hypothesis: no Admin API is called;
the hook appears to parse session logs, convert fields and upload to a custom
HTTP receiver. This remains a reported flow, not an inspected implementation.
The deployment hostname is excluded and no receiver request was made. Current
Admin API docs were researched before this correction but do not describe this
integration; they are not used to validate its payload. Native log records,
mapping code or paired input/upload output are the next evidence, without OTel
enablement. Classifier provenance, amount units, log coverage, retries and session
binding remain open. No provider API was called or collector enabled.

## Enterprise v2 follow-up — 2026-09-28

The [v2 review](../../../../docs/providers/enterprise-v2-schema-review.md) records two
regenerated bundles. All 28 manifest-listed hashes and the manifest sidecar match;
31 received files were hashed unchanged. Twenty-two JSON documents, two JSONL
records and a CSV parse. Synthetic category sums, event-ID dedupe, correction
identity and decimal arithmetic pass. Strict native compatibility is not claimed:
one metrics example uses string enums, the original duplicate JSON members remain,
and normalized Copilot objects/candidate CSV are not observed native envelopes.
The second bundle's eight local samples and local schema are byte-identical to v1.

V2 reports VS Code integer message-token paths but supplies only synthetic values.
Cache inclusion, stable binding, repeat semantics and complete usage remain unknown.
No hook code or paired log/upload payload was supplied. OTel stays disabled and no
Admin API call is reported; examples do not change those evidence boundaries.
Two authored research cases raise the total to 18. Received artifacts are excluded
from auto-fix and staging manifests; local audit/check scripts are review aids,
not implemented adapters, sanitizers, native decoders or permanent quality gates.

## PR review follow-up — 2026-09-28

Research was verified, committed and pushed in
[PR #21](https://github.com/nold-ai/changecost/pull/21); the earlier local/unpublished
entries above describe their recorded stage. Issue #9 now links that PR and the
published branch, with its open/Todo state and native relationships preserved.
The received source bundles remain local-only and excluded from Git.

Codex review identified two evidence-contract inconsistencies. The Enterprise
message-counter case now uses `hand-authored-synthetic`: its paths were reported
by the producer, and the original logs were not inspected. Its existing
`field_type_evidence` retains that reported provenance. The change-order gate now
requires accurate task status with unfinished work unchecked, allowing verified
research tasks to remain checked. These are documentation/fixture corrections,
not new runtime behavior; final checks and independent review are retained in
the verification handoff and PR.

## Remaining work and rollback

Tasks 2.1/2.2 retain exact account acquisition, Copilot/Cursor usage exports and
unresolved profile semantics. Task 4.3 remains pending through PR review/acceptance.
The existing issue tracks the same change and remains open; no adapter is declared
ready and the change is not archived.

Confidence: high in the narrow documented/local findings, low in complete
reconciliation. Failures to guard against are stale version assumptions,
duplicate/revised usage, and content leakage; mitigate with versioned profiles,
explicit finality/identity evidence and metadata-only synthetic projections.
No paid infrastructure or inference was required. Rollback is the scoped file
diff revert and restoration of the selected issue's prior body if necessary;
raw source data and account settings are unchanged.


## Preparation research — 2026-10-06 (Europe/Berlin)

Fresh main was fetched at 10:09:51 Europe/Berlin, SHA
`ee424b5cf3c116b18515cec1ee086e1a6de223a0`. The PR #34 source and merged
Git trees match. The maintainer selected #9 and retained its existing native-profile
completion criterion. This preparation is locally unpublished; no exports were
acquired, collection enabled or provider settings changed. Historical observations
and private originals remain unchanged. PR #33 delivered the checker and semantic
tooling; that delivery is not approval of intended sources.

### Current primary evidence

All sources in this table were opened on **2026-10-06**. Rolling documentation
establishes a candidate interface, not compatibility of an installed profile.

| Source | Confirmed documentation | Impact / remaining uncertainty |
| --- | --- | --- |
| [Copilot CLI monitoring](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#opentelemetry-monitoring) | File export writes JSON-lines and enables OTel. Nano-AIU repeats across root/child spans; cost is a multiplier. Top-level and subagent invocation spans both exist. | Inspect existing authorized exports. Root-versus-child selection is insufficient without subagent inclusion and interval boundaries; no cash conversion or additive policy is approved. |
| [VS Code monitoring](https://code.visualstudio.com/docs/agents/guides/monitoring-agents) | File JSON-lines and optional SQLite trace export are documented. Content and identity capture are separate settings; Local and Agent Host identity behavior differs. | Record editor/extension/harness and effective existing configuration. CLI or hosted SDK evidence cannot approve Local IDE imports. SQLite is a candidate acquisition format outside the current JSON/JSONL/CSV inspector; support/projection needs a separate decision if necessary. |
| [Copilot SDK events](https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/streaming-events) | Usage info is ephemeral context occupancy; usage checkpoints are durable accumulated nano-AIU snapshots for resumed accounting. | Context occupancy is not consumption. Preserve host/SDK namespaces and overlapping turn/session/checkpoint scopes; require replay/reset/correction/finality evidence. |
| [Cursor August update](https://forum.cursor.com/t/usage-page-to-token-amount-what/167153/79), [September conflicting reply](https://forum.cursor.com/t/measuring-a-quota-through-a-gauge-that-only-shows-tenths-of-a-percent/170206/4), [September team export reply](https://forum.cursor.com/t/cost-column-in-webpage-usage-hidden-behind-scrollbar/173244) | Dated vendor replies disagree about self-serve cost availability; the 2026-09-28 reply describes team CSV cost rows. The August reply distinguishes covered usage value from amounts owed. | Do not extrapolate team support to a personal account or treat any cost column as billed cash. Actual personal headers/rows and account economics remain unknown. |
| [Cursor usage and limits](https://prod.cursor.com/help/models-and-usage/usage-limits) | Included pools, on-demand charges and billing-cycle resets are distinct. | Verify tier, pool/range/timezone and included/on-demand semantics; percentages or external list prices cannot establish billed money. |
| [Codex App Server](https://learn.chatgpt.com/docs/app-server) | Thread token-usage updates are documented. | Current documentation does not certify recorded CLI/Desktop versions, finality or account billing. Keep snapshots/versioned entrypoints separate; no new adapter is authorized. |
| [Claude monitoring](https://code.claude.com/docs/en/monitoring-usage) | Cost metrics are approximations; official billing comes from the API provider. The page documents a streaming usage correction before version 2.1.214. | Date/version the observation, keep estimated versus billed bases distinct, and verify native record repetition/finality. The documented metric fix does not approve repeated assistant-log rows at other versions. |

### Local architecture evidence and decisions requiring attention

Independent read-only obligation review found that provider designs still described
an absent runtime and that the source assessment called the foundation future work.
Those statements are corrected here without introducing provider behavior.
`quality.source_feasibility` checks native evidence/profile digests and named semantic
attestations; it does not authenticate the reviewer. The register still has 14
profiles, zero approvals and unchanged canonical synthetic evidence references.

`src/changecost/normalized.py` already imports strict normalized records with
stable source/component identity and atomic conflict rejection.
`src/changecost/coverage.py` and `src/changecost/reconciliation.py` limit trusted
accounting to synthetic fixture billed USD; `quotes.py` and `advisory.py` reproduce
supported historical policy before numeric authority. Source approval alone cannot
make provider settlements complete or grant priced Quotes/numeric advice.

Before #13/#14 implementation, evidence must settle authoritative quantity lanes,
subagent inclusion, stable identity and binding, replay/reset/correction, cache
categories, accounting interval and finality. Adapter preparation must then define
versioned accounting/coverage policy and historical replay under the current contracts.
The [decision register](design.md#preparation-decisions--2026-10-06-europeberlin)
records required proof and conservative defaults. This preparation neither chooses
unsupported semantics nor changes runtime policy, schemas or dependency edges.

### Exact evidence requests and scope gates

1. Existing native Copilot CLI export: CLI/export version, account tier, exporter
   format/configuration without credentials, root/child/subagent and session/event
   identities, repeated/resumed examples, cache categories, accounting range,
   reset/correction behavior and terminal coverage.
2. Existing native Copilot IDE export: editor/extension/harness versions, tier,
   native format and acquisition route, conversation/trace boundaries and the same
   accounting proof. Hosted SDK logs remain a separate partial profile.
3. Actual personal Cursor CSV: sanitized exact headers/representative rows, app/export
   version and tier, range/timezone/pool, included/on-demand meanings, units/cost basis,
   stable row identity, overlapping exports and correction behavior. Preserve missing
   versus zero; do not enable paid overages to manufacture evidence.
4. Custom hook: sanitized mapping code or paired native log/upload records with
   trigger/version, classifier/units, log coverage, identity and retries/corrections;
   inspect receiver transformations separately. Work OTel need not be enabled.
5. Codex/Claude research: versioned authorized metadata with snapshot/repetition,
   identity/account regime, interval/reset/finality and billing basis; no new adapters.

Evidence may stay private in ignored storage with safe opaque IDs/hashes; publish
synthetic relationships and reviewed provenance, not original identifiers/content.
The inspector's structural success remains separate from semantic approval. Missing
required inputs leave tasks 2.1/2.2, 6.2/6.3 and closeout open. A wholly unavailable
intended source or changed target profile needs an explicit scope revision.

### Preparation checks, limitations and rollback

Baseline default checker returned `errors: []`, `semantic_approval: false`; the
baseline strict OpenSpec run passed all 11 items before the advisory archive.
Final preparation checks and issue readback are recorded in the local receipt and
appended below when observed. Historical PR #33 native assurance is not a current
preparation pass. The old ignored review-session receipt is absent in this worktree;
no new session or reset allowance is fabricated. Recover it before any publication
requiring the bounded session. Current planning remains unpublished.

Confidence: high in code/documentation boundaries, medium in provider feasibility.
Native sources, finality or billing evidence could change capability findings. Risks
are duplicate accounting, premature support claims and unsupported runtime authority;
separate lane/semantic/policy gates mitigate them. No paid infrastructure or inference
is needed for source inspection; artifact availability determines closeout timing.
Rollback reverts this scoped planning diff and restores issue text from its fresh
readback, preserving archives, private originals and historical review evidence.


### Observed preparation verification — 2026-10-06

The first `make check BASE_REF=ee424b5... MANIFEST=...` invocation passed 3,030
repository tests in 35.99 seconds but failed its temporary Make fixture because
inherited command-line Make overrides referenced the outer commit/manifest. This
is an invocation limitation; no test, gate or runtime source was changed to fix it.

The corrected invocation passed both inputs through the environment:
`BASE_REF=ee424b5cf3c116b18515cec1ee086e1a6de223a0 MANIFEST=.changecost/workflow/pilot-01-source-feasibility/manifest.txt make check`.
Both host lock and Make failure/repaired fixture proofs passed. All 3,030 tests
passed in 32.62 seconds; host hygiene, lint/format, types, docs, generated references,
metadata, workflow, package/build proofs and strict OpenSpec 11/11 passed. Dependency
audit correctly reported not applicable for unchanged locked inputs.

Full `make check` remains nonzero: all ten required SpecFact analyzers report
`native_capsule_artifact_not_admitted:darwin-arm64-cp312`. Unsupported Mac execution
is incomplete, not passing supported-Linux assurance. No analyzer waiver, skipped
analysis relabeling or inherited Linux pass is used. Supported-Linux/current
publication evidence and prior bounded-session recovery remain outstanding.
Independent affected-scope review returned no unresolved findings after two active
calibration links were repaired. Issue #9 body readback matches the applied batch;
Open/In Progress, User Story, parent #5, labels/project and #13/#14 edges [9,12]
are preserved. Preparation remains local; PR/stash disposition is pending.

## Adaptive-demand scope reconciliation — 2026-10-07 (Europe/Berlin)

The maintainer selected capability-based closeout in place of the prior universal
Copilot-export/Cursor-CSV requirement. Missing exports/admin/Enterprise data now
remain lane-specific gaps. No native approvals, measurements or fixture answers
are added. Independent source semantics, demand eligibility and complete billed
authority remain separate gates. Newer local producer versions need separate profiles.

The authorized 2026-10-06 metadata-only discovery inspected existing local stores
without settings changes or billable requests: newer Codex request/turn/root-turn
records overlap legacy counters; Claude coding logs contain repeated/revised usage
and overlapping result estimates; Copilot host/checkpoint/session totals have
different scopes; Cursor has context data but unusable empty/zero consumption
counters. Seven selected JSONL inputs passed structural inspection only. The local
private report/hashes are ignored recovery evidence, not semantic attestations.

[Adaptive research](../../../../docs/research/adaptive-demand-evidence.md) records
primary studies, access dates, limits and concrete remaining evidence requests.
The existing 14 canonical profiles and zero approvals remain unchanged. These
planning findings neither certify native finality nor claim complete new inventory
tasks. Historical failures, delivery checks and accepted review limits are retained.


## Publication disposition — 2026-10-07 (Europe/Berlin)

The maintainer superseded local-only retention with the published planning-only
[PR #38](https://github.com/nold-ai/changecost/pull/38). Both scoped stashes remain
recovery points. Earlier dated local/unpublished statements describe their
historical preparation state; this is the current delivery disposition.
Publication does not imply merge, implementation completion or native approval.
Recorded review limits and all 14 source profiles with zero approvals remain
unchanged.


## Merged planning checkpoint — 2026-10-07 (Europe/Berlin)

Planning [PR #38](https://github.com/nold-ai/changecost/pull/38) merged at
21:25:35 Europe/Berlin, commit `dc26715d2b583a31050c1cf7fda8ed0e9a9d5507`,
reviewed head `b6a03b38d160cf784ef8f8735ce3384164980f84`.
Both Python 3.11.15/3.13.14 jobs passed in
[Linux run 37670722956](https://github.com/nold-ai/changecost/actions/runs/37670722956).
These are actual PR #38 delivery checks, not verification of this later diff or
native semantic approval. Earlier publication/local-stash statements remain dated
history; neither recovery stash is reapplied.

## Native reconciliation — 2026-10-07 (Europe/Berlin)

Fresh main is `dc26715d2b583a31050c1cf7fda8ed0e9a9d5507`. This follow-through
reuses the existing discovery inputs and delivered checker; no model request,
account/API call, collector, setting change or runtime adapter is executed.
All 14 historical profile objects and the original synthetic fixture bytes remain
unchanged. Nine separately scoped profiles bring the inventory to **23 profiles,
zero approvals**. The current assessment date is distinct from observation dates.

Seven selected native JSONL originals were rehashed using the bounded regular-file
reader; all match their 2026-10-06 digests. Eight canonical profile/input bindings
pass structural inspection because the mixed-version Claude input is bound to two
version-scoped profiles. Hashing the entire file does not assign every row to either
version. Private manifests, identity comparisons and structural receipts remain
ignored; public findings disclose no source paths, identities or actual quantities.

| Profile group | Observed evidence and disposition | Exact decision still required |
| --- | --- | --- |
| Codex Desktop 0.159.0-alpha.12.1 | Partial request usage/identity; request records and legacy snapshots coexist, with cache-write categories and root-turn fields. | Establish non-overlapping request/snapshot authority, response identity, root/subagent ownership, category inclusion, replay/reset/correction and complete terminal/all-attempt coverage. No adjacency join or cumulative sum is selected. |
| Claude project 2.1.275, new selected inputs | Partial assistant usage/identity; repeated message groups change usage. Distinct observation from the historical profile. | Establish version-scoped request/message revision precedence and complete ownership; first, last and maximum are not universal policies. |
| Claude Desktop 2.1.221/234 | Partial transcript usage/identity for rows with each exact version in one mixed input. | Resolve replay/revisions, cache inclusion, subagent coverage, terminal scope and joins to SDK results without borrowing another version's authority. |
| Claude Desktop SDK/result, mixed runtime headers 2.1.221/234 | Partial usage and identity; assistant records overlap aggregate `usage`/`modelUsage`; numeric `total_cost_usd` is an estimate without billing provenance. | Prove per-result version association and request/result/transcript boundaries; estimated USD never establishes Pro subscription charges. |
| Claude Desktop 2.1.202/205 inventory | All capabilities unverified; documentation-provenance discovery receipt records header versions but no selected native accounting input for them. | Bind exact-version native input before field/accounting claims. The pre-2.1.214 monitoring defect does not prove local transcript behavior. |
| Copilot hosted local observation | Partial usage/identity; native checkpoint and shutdown overlap, while separate host session totals disagree. Ephemeral usage is absent from this selected stream. | Establish root/direct/turn/session ownership, cache inclusion, identity, replay/reset/correction and final coverage. Host SQLite comparisons are non-atomic. Keep CLI and Local IDE separate. |
| Cursor Free local observation | Partial identity, usage unverified; selected stored-row hashes bind bounded read-only SQLite findings, not full DB/WAL snapshots. Empty objects and zero placeholders do not measure consumption. | No usable consumption lane demonstrated. Optional personal CSV needs actual headers/rows, range/timezone, tier/basis, identity and correction evidence; provider-wide absence is not established. |

All billed-money and finality capabilities remain unverified. Current maintainer-
confirmed Free/Pro context does not retroactively prove every stored session's
authentication or billing. Optional Enterprise/custom hooks retain the previously
documented paired native/upload or sanitized mapping requirement, with receiver
transformations inspected separately. No such new input was supplied.

### Current primary-source recheck

Accessed **2026-10-07**: [Codex app-server](https://learn.chatgpt.com/docs/app-server)
documents thread usage notifications and authenticated account summary/daily buckets;
the account interface is optional online/account scope, not a task-level offline
source. [Claude monitoring](https://code.claude.com/docs/en/monitoring-usage)
documents approximate cost, the pre-2.1.214 streaming correction and cache-category
differences. None certifies the persisted samples or a universal revision policy.

[Copilot CLI monitoring](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#opentelemetry-monitoring)
warns against adding repeated child nano-AIU and distinguishes multipliers from
currency. [SDK events](https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/streaming-events)
distinguish ephemeral per-call usage, context occupancy and durable checkpoints.
[VS Code monitoring](https://code.visualstudio.com/docs/agents/guides/monitoring-agents)
describes harness-specific traces and a debug panel available without export;
that does not establish a durable local import contract or authorize enabling OTel.

[Cursor analytics](https://cursor.com/docs/account/teams/analytics) describes
Team/Enterprise access; [usage and limits](https://prod.cursor.com/help/models-and-usage/usage-limits)
separates included pools and on-demand charges. These do not approve personal Free
CSV availability or make context occupancy a consumed-token measurement.

### Delivery and recovery boundary

Reviewed dispositions and exact gaps can satisfy the accepted feasibility criterion
without one supported profile or every optional export. Native support, demand
eligibility and billed-money authority remain independent gates. Actual closeout
requires independent review and current-diff delivery checks, not the checker exit.
The original source review-session receipt is absent from known checkouts/worktrees
and scoped stash trees. No replacement session, inferred counters or approval is
created. Publication, issue closure and archival stay incomplete pending recovery
and applicable assurance; #35's offline synthetic phase has no #9 prerequisite.


### Reviewed disposition and actual local verification

Independent native-disposition review and documentation/metadata review found no
remaining introduced defects after correcting the SDK/result stream's mixed
2.1.221/234 system headers. Result-level version association remains unresolved;
no native support attestations are added. Inventory tasks are reconciled under
capability-based closeout, not the superseded universal-export condition.

The source suite passed 644; all 18 original cases/register/matrix return errors
empty and semantic approval false. All 14 historical profiles and three protected
fixture hashes remain unchanged. Selected/all strict OpenSpec passed 14/14.
Mechanical quality leaves, 3,030 repository tests, build and independent inventory
review passed; original environment failures and affected passing reruns remain
recorded in the ignored reconciliation receipt. Full native assurance remains
FAIL/UNKNOWN on Darwin. Cached Linux cannot provide the required capsule/module
environment; prior PR #38 checks apply only to its merged tree.

Current disposition is local/unpublished on
`codex/reconcile-source-feasibility-20261007`; the original source review receipt
is still missing. No replacement allowance, focused PR, issue closure or archive
is created. The delivery/acceptance tasks remain open until recovery and applicable
current-diff assurance. The original scoped stashes and accepted archives remain
untouched. Rollback reverts only the scoped diff and restores the saved issue body.


Issue #9 synchronization was read back with unchanged native User Story type,
labels, private-project In Progress status and parent #5. #9 has no prerequisites;
#13/#14/#36/#37 retain [#9,#12]. The issue explicitly distinguishes merged PR #38
from this local/unpublished 23-profile reconciliation and records the publication
blockers. No issue state or dependency is changed.

### Maintainer-authorized post-merge review — 2026-10-07 (Europe/Berlin)

The maintainer selected a fresh review for the current uncommitted reconciliation
after the prior PR merged. The new bounded session is
`pilot-01-source-feasibility-reconcile-20261007`, explicitly associated with #9
and its existing OpenSpec change. It reviews the prospective diff against
`dc26715d2b583a31050c1cf7fda8ed0e9a9d5507`; it does not resume or certify PR #33's
implementation review. Main was fetched again and still identifies that commit.

Local execution history proves that the older schema-8 receipt was initialized
on 2026-10-03 in a now-absent temporary worktree and subsequently read successfully.
Six original tool-call/result records were copied into the ignored recovery
directory with source locations and hashes. Saved full-state output is truncated;
no complete historical receipt, missing counters or events are reconstructed.
The original evidence, known findings and earlier limitations remain preserved.

The earlier requirement to recover that receipt before publishing this new scope
is superseded by the maintainer's review choice. This grants no source approval,
passing check or publication acceptance. Fresh verification binds to the current
contents; supported-Linux evidence and the focused PR remain pending.
