# Codex and Claude Code metric feasibility

Added to `pilot-01-source-feasibility` at the maintainer's request on
**2026-09-28 (Europe/Berlin)**. This extends research and synthetic fixtures only;
it creates no collector, adapter, new backlog change or paid model invocation.
The [common evidence gate](source-feasibility.md) applies to both providers.

## Codex

Local metadata inspection found **codex-cli 0.139.0**. `codex exec --help` confirms
`--json` emits JSONL. A locally generated app-server schema confirms
`ThreadTokenUsageUpdatedNotification` with `threadId`, `turnId` and `tokenUsage`.
The latter separates `last` and `total`, each with `inputTokens`,
`cachedInputTokens`, `outputTokens`, `reasoningOutputTokens` and `totalTokens`.
Schema generation reads no session transcript and proves interface shape, not
observed usage. The CLI emitted a PATH-alias permission warning but exited 0.

| Candidate | Documentation / local evidence | What remains unverified |
| --- | --- | --- |
| CLI JSONL | Official [non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode) documents `thread.started` and `turn.completed.usage`, including input, cached-input, output and reasoning-output token fields. | Existing sanitized stream, version-specific emitted fields, interruption/retry/subagent coverage and replay identity. |
| App / IDE protocol | Official [app-server reference](https://learn.chatgpt.com/docs/app-server) documents `thread/tokenUsage/updated`; installed schema exposes thread/turn IDs and usage breakdowns. | Client/version, accessible authorized capture, snapshot/reset behavior, and relationship to CLI evidence. |
| OTel | Official [advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced#observability-and-telemetry) documents optional log export, conversation metadata and completion token counts. | A suitable existing local export; no collector is introduced to obtain one. |

All three official sources were accessed on 2026-09-28. Record the authentication
and billing regime (ChatGPT plan, API or another configured provider) without
credentials. Token evidence and account quota percentages do not establish a
per-change invoice. Cash, corrections, loss/completeness and automatic change
attribution remain unverified. Do not combine CLI, protocol and OTel observations
of the same work without proven identities and coverage. Preserve category names;
do not add cached or reasoning subsets to totals without verified semantics.

For further inspection, provide an existing, authorized JSONL/protocol capture after
allowlisting only usage events and synthetic thread/turn IDs. Full streams can
contain commands, messages, code and tool outputs. Inspect local stores only with
explicit authorization and project only allowlisted metadata; do not run a new model request merely to produce metrics. An IDE
installation does not establish that its telemetry matches this CLI version.

## Claude Code

Local `claude --version` reported **2.1.257**. Its help confirms `--output-format`
supports `json` and `stream-json`; no request was run, so the result envelope is
not approved as a source profile. IDE version and account tier remain unknown.

The official [monitoring reference](https://code.claude.com/docs/en/monitoring-usage)
(accessed 2026-09-28) documents `claude_code.token.usage` with input/output/cacheRead/
cacheCreation categories and `claude_code.cost.usage` in USD. Costs are approximate.
`session.id`, optional version/entrypoint attributes and configurable delta versus
cumulative temporality matter for attribution and replay. The documented local
console route requires `CLAUDE_CODE_ENABLE_TELEMETRY=1` and
`OTEL_METRICS_EXPORTER=console`; it is a future acquisition option, not enabled here.

The official [cost guide](https://code.claude.com/docs/en/costs) (accessed 2026-09-28)
describes `/usage` session cost as an estimate; it does not represent Pro/Max
subscription billing. Preserve a reported estimate separately from actual charges.
Do not infer a universal cash price from plan limits or token counts.

For later inspection, supply an existing authorized metric export with source
version, entrypoint (`cli` versus an IDE), temporality, interval boundaries and
synthetic session identity. Remove all user/account/organization identifiers,
content and arbitrary resource attributes before sharing. A missing session label
leaves usage unbound; do not recover it from nearby timestamps. Inspect actual
counter resets, resumed sessions, repeated exports and main/subagent/auxiliary
coverage before defining totals. Console output is not assumed to be JSONL.

## Dispositions and next evidence

After the documentation review, the maintainer explicitly authorized local artifact
inspection. The following observations supersede the initial no-sample state for
local Codex/Claude stores only; OTel and CLI stdout profiles remain unverified.

### Observed local artifacts

Inspection at **2026-09-28 09:52 Europe/Berlin** read three recent JSONL files per
tool in memory and emitted only field shapes, versions and relationship counts.
Raw bytes, prompts, responses, tool payloads, paths and identifiers were not copied
into fixtures. Private path pointers and snapshot hashes are retained in the ignored
workflow receipt directory; active files can grow after the recorded snapshot.

**Codex Desktop local rollouts:** all three reported runtime
`0.158.0-alpha.2.1` and originator `Codex Desktop`, distinct from PATH CLI 0.139.0.
The first/third used source `vscode`; one carried subagent metadata. This is an
observed label, not proof those records came from the VS Code extension.
`event_msg.payload.type=token_count` carried `info.total_token_usage` and
`info.last_token_usage`. Both included `cache_write_input_tokens` in addition to
input, cached-input, output, reasoning-output and total token counts. The third
snapshot had 91 usage records, including four consecutive equal total snapshots.
The token events had no turn ID; separate `turn_context` records did. Inferring
their association solely from adjacency is not yet an approved provider join.

**Docs versus actuals:** these are persisted rollout envelopes, not the documented
`codex exec --json` or app-server protocol. Shared token concepts match, but snake
case fields and the cache-write category differ from the generated 0.139.0 schema.
Do not treat the older installed schema as an exhaustive Desktop contract. Preserve
the additional category without guessing whether it is included in other totals.

**Claude Code local records:** the three snapshots reported versions 2.1.275,
2.1.215 and 2.1.215, distinct from PATH CLI 2.1.257. They contained 89, 28 and 23
assistant usage records respectively, representing 39, 6 and 7 distinct message
IDs. All had input/output/cache-read/cache-creation integer fields. No `cost`,
`cost_usd`, `billed_cost` or `total_cost_usd` field appeared in these usage objects;
this does not establish absence from every other artifact.

Different record UUIDs repeated the same request/message IDs. In the newest sample,
all 33 repeated-message groups had identical usage. In both older samples, repeated
groups changed `output_tokens` and some auxiliary usage fields. Neither summing
each record nor blindly taking the first record is defensible. Request/message
identity is promising; finality and revision precedence remain unverified.

**Docs versus actuals:** the [directory reference](https://code.claude.com/docs/en/claude-directory)
identifies local transcript files, while the [monitoring reference](https://code.claude.com/docs/en/monitoring-usage)
describes multiple persisted content-block entries per API response (both accessed
2026-09-28). The observed repetition is consistent with that distinction. It does
not prove that local transcript usage is an OTel counter or that every request is
complete. The [programmatic guide](https://code.claude.com/docs/en/headless) separately
documents estimated `total_cost_usd` in JSON results; no such stdout result was
inspected. IDE entrypoint and account tier cannot be inferred from these samples.

### Capability outcomes

| Capability | Codex CLI / app / IDE | Claude Code CLI / IDE |
| --- | --- | --- |
| Local usage evidence | Partial for inspected Desktop rollout metadata; stdout/OTel/IDE profiles unverified. | Partial for inspected local assistant usage; stdout/OTel/IDE profiles unverified. |
| Session/turn joins and change binding | Partial session identity; turn association and change binding unverified. | Partial session/request/message identity; finality and change binding unverified. |
| Monetary settlement | Unverified; no billed-cost source established. | Unverified; documented estimates are not billed charges. |
| Replay, corrections and completeness | Partial duplicate observation; resets, correction rules, subagent accounting and coverage unverified. | Partial repeated/changed usage observation; finality, counter resets and coverage unverified. |

No import profile is approved: partial evidence is not a verified aggregation rule
or stable source contract. Collecting a new sample still requires separate
authorization. Observed shapes guide the [synthetic examples](fixtures.md), while
task 2.2 stays pending for Copilot/Cursor and the unresolved profile semantics.
Future adapters need
separate scoped changes after this evidence gate and the core reconciliation
prerequisites; existing Copilot/Cursor adapter stories are not relabeled.


## Closeout assessment (2026-10-03)

Installed metadata was rechecked on 2026-10-03: codex-cli 0.139.0 and Claude Code 2.1.257 remain distinct from historical Desktop 0.158.0-alpha.2.1 and stored Claude 2.1.275/2.1.215 records. Each version has a separate register profile. The executable detector checks synthetic snapshots and message variants; it cannot establish native finality, reset/interval authority or account billing. Claude monitoring was rechecked on 2026-10-03; its metric interface remains separate from billed money.

See the canonical [profile register](source-profiles.json) and [current evidence gate](source-feasibility.md#reinspection-and-current-blockers).

## Later local discovery and adaptive-demand scope — 2026-10-07

The earlier observations above remain historical. The authorized 2026-10-06
Codex/Claude discovery and newer representation/version limits are summarized in
[adaptive evidence](../research/adaptive-demand-evidence.md#authorized-local-discovery--2026-10-06).
No new native approval is inferred. #9 now uses capability-based closeout; missing
optional exports do not block all lanes, but usage/identity/correction/finality
proof remains required for supported mappings. Source support, demand-learning
coverage and billed-money authority remain independently gated.


## Separate current observations — 2026-10-07

The [canonical register](source-profiles.json) now binds selected Codex Desktop
0.159.0-alpha.12.1 request/snapshot bytes independently of the older 0.158 profile.
`response_id`, session/thread/turn/root-turn fields and six token categories are
observed; request, turn/thread and legacy snapshots overlap. Complete root/subagent
ownership, cache inclusion, replay/reset/correction and terminal coverage remain
unverified. [Current app-server documentation](https://learn.chatgpt.com/docs/app-server),
accessed 2026-10-07, also documents authenticated account token summaries/daily
buckets. They are an optional online/account scope, not offline task evidence or
authorization to call that endpoint.

Claude project 2.1.275 inputs with revised message usage are a separate observation
from the earlier profiles. Desktop coding transcripts contain 2.1.221 and 2.1.234
rows in one selected native input; each profile is limited to its exact-version
rows. Another selected SDK assistant/result stream reports 2.1.221/2.1.234 in system
headers, while result rows lack a version. Per-result association is unverified;
its `usage`, `modelUsage` and `total_cost_usd` cannot inherit transcript authority.
Desktop 2.1.202/205 remains header-only inventory with no selected native accounting
binding. Current Pro plans are maintainer-reported context, not proof of historical
authentication for every log. Ordinary Desktop chat remains a separate unverified
surface outside these coding-reader plans.

[Claude monitoring](https://code.claude.com/docs/en/monitoring-usage), accessed
2026-10-07, documents approximate costs and version-sensitive streaming behavior
before 2.1.214. Its input category excludes cache reads/writes; total input under
GenAI conventions includes those categories. This documentation cannot approve
local transcript precedence or equate the monitoring defect with every repeated
message. No universally additive token or estimated-USD rule is approved.

## Codex reader preparation refresh, 2026-10-23 Europe/Berlin

The selected [Codex reader plan](../../openspec/changes/archive/2026-10-26-provider-03-codex-local-import/proposal.md)
remains unimplemented. Installed `codex-cli 0.139.0` again generated its app-server
JSON Schema without opening session data or invoking a model. Required thread/turn
IDs, last/total breakdowns and input/cached-input/output/reasoning/total fields
match the earlier installed interface description. This establishes protocol shape
only, not stored-file accounting or compatibility with a Desktop producer.

The [official App Server reference](https://learn.chatgpt.com/docs/app-server),
accessed 2026-10-23, documents usage notifications and persisted JSONL history.
Those descriptions do not approve the reader's accounting/identity/finality policy.
Remote thread APIs and acquisition are outside the selected existing-file scope.
At initial preparation the source register contained 23 profiles and zero approvals. Earlier dated
native observations remain historical; the initial preparation inspected no real
native file. The subsequent authorized investigation below supersedes that state.
See [preparation evidence](../../openspec/changes/archive/2026-10-26-provider-03-codex-local-import/PREPARATION_EVIDENCE.md)
for the storage mismatch, proposed portable NativeUsage record and implementation
gates. Import, demand eligibility and billed-money authority remain independent.

## Restored reader and native accounting investigation, 2026-10-23

The maintainer requested restoration of the scoped preparation and work through
native accounting approval blockers before implementation. Four existing snapshots
were inspected read-only, with 85 request usage records. Their headers declare
0.163.0-alpha.10.2 under separate Desktop and Work originators. Work is not thereby
classified as a coding-session source. At that stage the 23 canonical profiles had
zero approvals. The newer observations did not replace historical profile bindings.

The [native accounting matrix](../../openspec/changes/archive/2026-10-26-provider-03-codex-local-import/NATIVE_ACCOUNTING_EVIDENCE.md)
records exact snapshot hashes, pinned primary sources accessed 2026-10-23 and
remaining gates. Creation headers survive resumed appends. Request, turn and thread
quantities overlap. Legacy snapshots can contain estimates or inherited counters,
optional backend details can default to zero, and usage records are best effort.
No full-task, successful-finality or billed-money authority follows from these rows.

The initial independent semantic review approved no capability. It requested a reliable
record-to-producing-build/client binding, followed by native replay/reset/correction
and category reconciliation with an explicitly accepted partial lineage/finality
scope. No runtime implementation, model request or collection was started.

Further existing-data inspection found historical engine handshakes and selected
thread/turn joins, plus native turn resets, compaction-associated snapshot changes
and repeated legacy counters. The current bundled engine differs from the historical
reported build. Logical session identity survives resume and is not process identity.
See the [follow-up evidence](../../openspec/changes/archive/2026-10-26-provider-03-codex-local-import/NATIVE_ACCOUNTING_EVIDENCE.md#existing-provenance-and-native-edge-case-follow-up)
for exact observed counts, research-only oversized parent files and remaining producer,
replay/correction and approval limits. Profile approvals were empty at that stage.

### Planned finite Codex diagnostics

The 2026-10-23 [producer-binding plan](../../openspec/changes/archive/2026-10-26-provider-03-codex-local-import/PRODUCER_BINDING_POLICY.md)
proposes independently adjudicated immutable snapshots instead of inferring writer
identity from retained headers across resume. Its proposed diagnostic mapping
preserves serialized request categories with unknown backend presence, served
model/time, completeness and finality. Byte-identical copies share admission;
appended, reformatted or other changed files require fresh independent admission.
That planning stage activated no profile and retained zero approvals across the 23
profiles. Subsequent canonical activation is recorded below; reader and
demand/financial authority remain separate gates.

### Canonical activation — 2026-10-23

The maintainer subsequently authorized canonical adoption of the exact finite
diagnostic profile/proof. The register now has 24 profiles and one usage approval;
the original 23 remain unchanged and unapproved. Earlier zero-total-approval
statements describe the investigation before this activation. Contributor admission
checks and [activation evidence](../../openspec/changes/archive/2026-10-26-provider-03-codex-local-import/TDD_EVIDENCE.md)
keep that scope explicit. Reader implementation remains blocked; no broader source
compatibility, complete-task accounting, demand learning or billing follows.

## Finite runtime implementation, 2026-10-24

The exact approved Desktop snapshot now has a separately authorized local reader.
Its finite mapping retains 16 response events and 96 serialized category facts.
The [command boundary](../settlement.md#import-the-approved-finite-codex-diagnostics)
rejects every other digest before persistence. Unknown served model, time, backend
presence and finality remain explicit. Partial reported parent lineage does not
prove full descendant or task coverage. Historical observations above retain their
original scopes. Claude and broader Codex compatibility remain unimplemented.

## Claude project-reader preparation, 2026-10-27 Europe/Berlin

The maintainer selected existing Claude Code project JSONL as the first lane for
[Claude #37](../../openspec/changes/provider-04-claude-local-import/proposal.md).
The intended outcome is a reusable approved-profile reader with version-specific
accounting, immutable corrections, exact replay and separate manual binding.
It has not been narrowed to a finite diagnostic snapshot. Desktop coding
transcripts, IDE, SDK/result streams, JSON containers and SQLite/index acquisition
remain deferred; ordinary chat remains excluded. All ten implementation tasks
remain unchecked and every Claude source profile remains unapproved.

Existing Store and binding APIs are reusable infrastructure. Native graph validation
still requires Codex evidence, while NativeUsage has closed category/scope/ownership
constraints. The [design checkpoint](../../openspec/changes/provider-04-claude-local-import/design.md#approval-to-contract-execution-checkpoint)
requires independent Claude accounting approval and demonstrated contract fit
before implementation. Codex's finite replay algorithm is not a correction policy
for revised Claude project messages. No approval transfers between these providers.

The [SDK cost guide](https://code.claude.com/docs/en/agent-sdk/cost-tracking) and
[monitoring reference](https://code.claude.com/docs/en/monitoring-usage), accessed
2026-10-27, describe stream accounting and estimated costs. They do not establish
the installed producer's persisted project-log contract. The current `claude`
symlink points to a 2.1.257 binary path; this preparation did not execute it or
inspect private source files. Installation does not establish a historical
record's producer, account regime or accounting semantics.

No source-register approval, collector, runtime command or financial/native-demand
authority is added. Delivered #35 removes only its delivery dependency; a Claude
measurement/coverage policy remains separate. Evaluation #17's live boundary,
historical evidence gaps and integration obligations remain open.

## Approved Claude project reader, 2026-10-28 Europe/Berlin

The canonical `claude-project-2-1-215-request-stages` profile now carries independent
usage approval for mapping `claude-project-request-stage-r4`. The explicit
[project JSONL reader](../settlement.md#import-approved-claude-project-diagnostics)
implements its closed grammar, four nullable categories, partial/terminal history
and replay. The [minimized native observations](evidence/claude-project-2-1-215-native-observations.md)
and [producer controls](evidence/claude-project-2-1-215-producer-controls.md) retain
exact evidence boundaries. No source was reinspected during reader completion.

A current-time initial A+B imports both observed stages atomically. A later B
requires retained accepted A. Terminal-only first import cannot admit unseen A.
Backend finality, full lineage and complete coverage remain unknown. Approval does
not transfer to other versions or surfaces, nor confer demand, financial or
calibration authority. Focused implementation evidence is recorded in the
[active change](../../openspec/changes/provider-04-claude-local-import/TDD_EVIDENCE.md);
aggregate and supported-Linux assurance remain pending.

## Approved Desktop root terminal reader, 2026-10-28 Europe/Berlin

The exact `claude-desktop-2-1-308-root-terminal` profile has independent usage
approval and local reader support through the existing project import operation.
Its [native statement](evidence/claude-desktop-2-1-308-native-observations.md) and
[producer statement](evidence/claude-desktop-2-1-308-producer-binding.md) are immutable.
Their draft headers describe the frozen review input, not current approval status.
Producer evidence is external Desktop metadata association, not a controlled probe.
Every contributor requires exact engine and entrypoint; Desktop build is not checked.

Four present exact nonnegative integer categories preserve literal zero without
claiming native zero was observed. Missing/null, partial stages, children and changed
quantities reject. Closed metadata and opaque API blob exclusions grant no nested
accounting or complete-coverage authority. Global event identities prevent cross-profile
duplicates; replay retains original provenance after reopen/recovery. Exact 2.1.215
correction support and finite Codex remain intact. Broader versions/lifecycle, billing,
demand, backend finality, served model and #17 calibration remain separate.

The later independently approved q4 revision uses mapping
`claude-desktop-root-terminal-r2`. It adds closed `cost-state` and `mode` metadata
exclusions while retaining every contributor and accounting constraint. Opaque
`modelUsage`, costs, duration, line counts and mode values grant no native facts,
billing or demand authority. Unexpected keys or present message/direct usage still
reject. This replaces the unpublished q3 candidate; its canonical profile, proof,
asset and source statements remain frozen in local history. No real q3 Desktop
facts were stored. Authored prototype bundles have no compatibility promise.
