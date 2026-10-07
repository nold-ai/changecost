# VS Code hosted Copilot metadata assessment

Assessment: **2026-09-28 10:17 +02:00 (Europe/Berlin), partial observed evidence**.
The maintainer supplied an Agent Host session URL and authorized inspection of its
existing logs. Installed VS Code is **1.139.1**; its bundled `copilot-chat` package
is **0.67.0**, with bundled `@github/copilot` **1.0.73**. The session's start event
instead records `version: 1`, `producer: copilot-agent`, `copilotVersion: 0.0.0`.
Do not replace that recorded version with the installed package version. Account
tier is **Personal Free, maintainer-confirmed**; billing/credit treatment remains
unverified. This tier is recorded independently of the Cursor Basic account.

The separate [Enterprise v2 review](enterprise-v2-schema-review.md) reports
message-counter paths with synthetic values and no verified host/SDK link. It does
not inherit this Personal Free profile's identity or accounting evidence.

## Acquisition and identity

The supplied URI identifies a `copilotcli` provider in the VS Code Agent Host.
The existing `agenthost.log` explicitly connects that host session with a different
SDK session ID during session creation. Its backing `session.start.sessionId`
matches the SDK ID. The link is established by metadata, not timestamp proximity.
Both actual IDs and the original URL remain outside shared fixtures and docs.

Read-only inspection used:

- `~/Library/Application Support/Code/User/globalStorage/agent-host.db`: matched
  session/provider catalog metadata, excluding titles, workspaces and Git bindings.
- `~/Library/Application Support/Code/agentSessionData/<host-id>/session.db`:
  one `turn_usage` row, whose `turn_id` matches the `turns` table. The corresponding
  SDK-ID database contains no `turn_usage` rows in this snapshot.
- `~/.copilot/session-state/<sdk-id>/events.jsonl`: event envelopes and allowlisted
  usage/version fields; raw messages, tool payloads and cache internals excluded.

SQLite connections used read-only transactions. Source snapshots were not atomic
across the log and databases, so cross-source finality is not established. Private
receipts retain projected numbers, structural counts and source-byte hashes. No
model request, telemetry configuration or collection process was started.

## Observed metrics and boundaries

| Evidence | Finding / interpretation limit |
| --- | --- |
| `turn_usage.usage` | Nonzero `inputTokens`, `outputTokens`, `cacheReadTokens`; these differ from the larger turn totals in `_meta`. Do not present top-level fields as complete session totals. |
| `_meta.turnTokenTotals` | One per-model entry with `inputTokens`, `cachedTokens`, `outputTokens`; identical to `directTurnTokenTotals` in this observation. Preserve both boundaries, never add them together. |
| `_meta.copilotUsage.totalNanoAiu` | Matches `directCopilotUsage.totalNanoAiu` and the persisted SDK checkpoint value. They are overlapping observations, not three separate charges. |
| `_meta.copilotUsage.sessionTotalNanoAiu` | Lower than the other nano-AIU values in this snapshot. Cause/freshness unknown; field naming cannot decide which value is final. |
| `_meta.cost` | Numeric with no currency unit. The documented SDK usage `cost` field is a multiplier; this wrapper field is not proof of cash. |
| `session.usage_checkpoint` | One event containing nonzero `totalNanoAiu` and `totalPremiumRequests`. Preserve units separately; do not convert premium requests to tokens or currency. |
| Persisted event lifecycle | 15 assistant turn starts/ends, 23 assistant message events and 18 model-call failure events. No `assistant.usage` or `session.shutdown` event in the inspected file. Counts do not establish billable requests or successful-call totals. |

A focused read of the installed Agent Host JavaScript confirms that its usage
merge code adds per-model turn totals while retaining top-level usage fields, and
that `_parentCopilotUsageMeta` obtains turn and session nano-AIU values from
separate state. This supports keeping their boundaries separate, but does not
explain the observed disagreement or certify complete coverage. The installed
source hash is retained locally; this is version-specific implementation evidence.

## Documentation compared with actuals

All sources accessed **2026-09-28**:

- [VS Code Agent Host](https://code.visualstudio.com/docs/agents/concepts/agent-host)
  describes a dedicated process that owns provider sessions independently of UI
  clients. It distinguishes Agent Host sessions from extension-host sessions.
- [GitHub SDK streaming events](https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/streaming-events)
  describes `assistant.usage` as ephemeral and `session.usage_checkpoint` as durable,
  accumulated usage at checkpoint time. Its absence from the persisted transcript
  is consistent with that contract and does not mean token data was never emitted.
- [GitHub SDK usage and billing](https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/usage-and-billing)
  documents accumulated runtime metrics and per-model usage. No SDK call was made;
  documented runtime access is distinct from the inspected offline files.
- [GitHub CLI reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#opentelemetry-monitoring)
  defines nano AI units and separates multipliers from money. Its root-span rule
  applies to OTel spans; it does not turn a local usage checkpoint into a root span.

No OTel export was inspected. This observation does not establish behavior for a
standalone terminal CLI, foreground extension-host chat, or another IDE.

## Disposition and next evidence

**Partial:** explicit host-to-SDK identity, nonzero persisted turn token metadata
and durable accumulated nano-AIU evidence for this session. **Unverified:** cash,
full request coverage, resets/revisions, cross-session uniqueness,
final checkpoint authority and a supported stable offline import contract.

Next, compare an authorized finalized usage source with these projections and
resolve the disagreeing nano-AIU fields. Inspect any already-collected OTel source
separately; do not enable collection just to fill this research gap. Keep manual
change binding distinct from the verified link between provider session IDs.

The [fixture contract](fixtures.md) includes `copilot-hosted-usage-boundaries`,
using synthetic quantities and two distinct linked identity namespaces.
Confidence: high in the inspected shapes and link, medium in the narrow usage
interpretation, low in final settlement. Tier, version and snapshot timing could
change the conclusion. Failure modes are counting overlapping totals, conflating
host/SDK IDs and treating partial counters as final; the fixture preserves all
three distinctions. No inference cost was incurred. Rollback removes the research
diff; source files, databases and account settings are unchanged.


## Closeout assessment (2026-10-03)

Read-only reinspection of the same authorized source on 2026-10-03 found 367 persisted events and changed raw bytes. The selected checkpoint and turn-usage projections remained unchanged. The current event digest is in the profile register; old receipts remain private and preserved. Host and SDK identities remain distinct. No CLI/IDE native export, authoritative accounting interval, cache inclusion, reset/correction policy or terminal completeness was established. SDK documentation was rechecked on 2026-10-03; interface descriptions do not approve this installed version.

See the canonical [profile register](source-profiles.json) and [current evidence gate](source-feasibility.md#reinspection-and-current-blockers).

## Later local discovery and adaptive-demand scope — 2026-10-07

The earlier observations above remain historical. The authorized 2026-10-06
Copilot discovery and newer representation/version limits are summarized in
[adaptive evidence](../research/adaptive-demand-evidence.md#authorized-local-discovery--2026-10-06).
No new native approval is inferred. #9 now uses capability-based closeout; missing
optional exports do not block all lanes, but usage/identity/correction/finality
proof remains required for supported mappings. Source support, demand-learning
coverage and billed-money authority remain independently gated.


## Reconciled hosted checkpoint — 2026-10-07

`copilot-hosted-local-discovery` in the [register](source-profiles.json) binds the
selected 2026-10-06 native SDK stream with checkpoint and shutdown. Recorded
`copilotVersion: 0.0.0` and event schema 1 remain distinct from installed package
versions. Equal checkpoint/shutdown nano-AIU values are overlapping observations,
not two charges or proof of complete session coverage. Ephemeral `assistant.usage`
is absent in this selected stream; missing does not mean zero. Separate read-only
host SQLite comparisons are not an atomic cross-store snapshot and retain their
disagreeing session-total scope.

[SDK events](https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/streaming-events)
and [VS Code monitoring](https://code.visualstudio.com/docs/agents/guides/monitoring-agents),
accessed 2026-10-07, distinguish durable checkpoints and different harness/export
interfaces. A debug panel working without OTel does not establish a durable import
contract. Preserve CLI, Local IDE and hosted SDK lanes; require identity, ownership,
cache inclusion, replay/reset/correction and finality before aggregation approval.
No telemetry setting or account configuration is changed.
