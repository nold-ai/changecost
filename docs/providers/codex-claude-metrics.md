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
