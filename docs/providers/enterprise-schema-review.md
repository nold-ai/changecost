# Enterprise artifact schema review

Review: **2026-09-28 (Europe/Berlin)**. Both products use Enterprise tiers,
**confirmed by the maintainer**. This updates the tier context withheld in one
bundle; it does not retroactively verify exporter configuration or billing.

The artifacts corroborate local identity/context shapes. They do **not** contain
Cursor or Copilot OTel exports, usage CSVs, or an Enterprise consumption ledger.
No native import profile is approved. Earlier Basic/Personal Free observations
remain separate source profiles; plan tier alone does not explain differences.

The [v2 review](enterprise-v2-schema-review.md) adds producer-reported VS Code
message counters and evaluates synthetic OTLP/normalized examples. Integrity and
local-projection counts below refer to the original bundles; v2 findings are separate.

## Reported work collection path

The maintainer reports that **OpenTelemetry is globally disabled at work**.
OTel is unavailable in that reported configuration; missing files are expected,
not a collection defect. The official OTel comparison below remains reference-only
and does not require enabling export.

The latest clarification supersedes the earlier Admin API assumption: **no Admin
API is called**. The reported flow is **session logs → custom hook parsing and
field conversion → organization-specific HTTP receiver** at `/api/hooks/events`.
The deployment hostname is intentionally excluded. No request was sent to it.
The log-parsing description is maintainer-reported and tentative; neither the
script nor a matched input/output sample has been inspected.

Assess three separate contracts: the original log record, the hook's transformed
upload payload, and any receiver-side stored record. Official documentation can
support a native field only after its product, version, container and semantics
match the source. A custom upload does not inherit an Admin API or OTel contract.
Admin API endpoint schemas are therefore not evidence for this integration.

Hook version/trigger, exact log location and format, field mapping, classifier
meaning/origin, amount units, coverage and session binding remain unverified.
I don't know yet whether classifier/cost fields are copied from logs, calculated
by the script, or added by the receiver. Sanitized mapping code or paired native
input and uploaded output would resolve the first boundary; a stored output would
resolve any receiver changes. Do not infer billed cash from a field named `cost`,
or infer consumption from context occupancy. Verify the Copilot path separately;
the reported Cursor hook does not establish its source or transformations.

If these are Cursor's lifecycle hooks, their documented conversation/generation
IDs are candidate inputs; not every hook has session context. Which event and
identifiers this custom integration uses needs inspection.
[Cursor hooks](https://prod.cursor.com/docs/hooks), accessed 2026-09-28.

Received `artifacts/` bundles are local-only review inputs and are not included
in the repository or PR. Paths below identify those inputs, not portable links.
Only the authored synthetic cases and findings are published; local hash receipts
preserve which supplied bytes were reviewed.

## Evidence boundaries and integrity

| Received bundle | What can actually be reviewed |
| --- | --- |
| `artifacts/changecost_evidence_vscode/README.md` | Field/type inventory, one Cursor presence summary and two Copilot schema illustrations. Original event values, kinds, versions, times and identity relationships were removed. No event-level joins or arithmetic can be verified. |
| `artifacts/cursor-copilot-schema-evidence/README.md` | Four Cursor local-state projections; Copilot session-store identities, empty chat index and Agent Host catalog projection. Synthetic occupancy, replacement IDs and per-session relative clocks. No OTel/CSV or SDK usage stream. |

Recomputed **17/17** manifest-listed file hashes match; the second bundle's
manifest sidecar also matches. All 13 JSON documents and two JSONL illustrations
parse with the standard parser. Hashes verify the received bytes, not authenticity
of private originals, completeness or exporter compatibility.

One JSON document, `samples/copilot-session-store-identity.json`, repeats
`absolute_timestamps` and `unprojected_sessions` at the same object level. Both
repetitions have identical values, so the retained values do not conflict; a strict
no-duplicate-member check still flags the file. It needs a separately labeled,
normalized derivative before fixture admission. The received originals, including
CRLF line endings and manifests, were preserved byte-for-byte.

Collection instants are withheld. The review date must not be substituted for them.
The first bundle reports an unintended Cursor WSL server installation during a
version probe; acquisition was not wholly side-effect-free. Neither that account
nor the reported immutable SQLite read proves a stable snapshot. `immutable=1`
skips locking and change detection and requires an actually unchanging database;
use a consistent snapshot for further row evidence. [SQLite URI reference](https://www.sqlite.org/uri.html),
accessed 2026-09-28.

## Local shape comparison

| Observed or projected evidence | Match / limit |
| --- | --- |
| Cursor 3.22.7, embedded VS Code 1.128.0 | Versions reported by the second bundle; first bundle withholds versions. Do not merge the two into one versioned capture. |
| `composerData.usageData = {}` and zero bubble input/output counters | Same narrow shape as the earlier macOS Basic sample. This does not support attributing that shape to the Basic plan alone. It does not explain why counters are zero. |
| Context used/limit/percent and category estimates | All three included occupancy examples pass category-sum, total/limit and four-decimal percentage checks on synthetic quantities. They cannot reproduce original ratios or actual token volumes. |
| Missing-context composer | The fourth sample omits occupancy fields and bubble bodies. Do not require these fields or substitute zero. Its aggregate bubble claims cannot be independently checked against omitted rows. |
| Bubble-to-composer IDs | Links and uniqueness pass within the projected groups. The completed group has 39 included bubbles and one nonempty request ID; the aborted group has six bubbles. These counts describe selected projections, not store populations. |
| “Multicall” sample | Two distinct request IDs survive, with 105 bubble rows omitted. This proves two projected identifiers, not two successful/billed model calls, cache usage or complete turn coverage. |
| `status = aborted` | Local lifecycle state, not a provider correction or refund. `completed` likewise does not prove final accounting. |
| Copilot Chat 0.67.0 package versus 0.57.0 state | Both retained as reported. The state may be stale or have different scope; it does not establish the runtime that emitted a record. VS Code 1.139.1 and completions state 1.378.1799 remain separate. |
| Copilot session store and chat index | Identity/narrative storage, not the per-session `turn_usage` source inspected at home. Empty chat-index entries do not prove no hosted conversation or no consumption. |
| Agent Host `provider = copilotcli` | Supports the provider label. Payload was withheld; no explicit host-to-SDK link or usage record was shared. A missing standalone CLI executable does not exclude an embedded SDK runtime. |
| Copilot `$.data.id` / `$.data.parentId` inventory | Does not directly match the documented SDK envelope location. A wrapper or another version may explain it; values and event types are withheld, so no unwrapping/mapping is approved. |

The local Cursor occupancy concept agrees with the documented context ring and
category breakdown. The public page does not specify `composerData`, SQLite keys,
bubble enum values or their accounting semantics. This is conceptual agreement,
not an official internal-storage contract. [Cursor context documentation](https://prod.cursor.com/docs/agent/prompting),
accessed 2026-09-28.

## Official export comparison

Sources below were accessed **2026-09-28**; they are rolling documentation.

**Cursor Enterprise:** the wire reference specifies `cursor.telemetry` scope
version `0.1.0`, delta-sum metrics without correlation IDs, and request/error/correction
logs. `cursor.cost.usage` is an estimated USD metric, not an invoice. Log
`cursor.conversation.id` can identify the IDE/CLI composer; `cursor.usage_event.id`
links usage records and corrections. Corrections remove a usage group from billing;
local `aborted` status is not that event. None of these wire records was supplied.
The account tier permits this feature, but the maintainer reports it disabled
globally at work; this wire contract is only a comparison reference. [Cursor wire reference](https://prod.cursor.com/docs/enterprise/opentelemetry-export/wire).

**Copilot SDK:** its documented common event envelope places `id`, `timestamp`
and nullable `parentId` at the top level. `parentId` links the preceding event,
not an OTel parent span. `assistant.usage` is ephemeral; the durable
`session.usage_checkpoint` carries accumulated nano AI units. The first bundle's
nested ID paths are only an unresolved shape difference. The second bundle's
narrative SQLite `checkpoints` table cannot establish presence or absence of that
SDK event. [SDK event reference](https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/streaming-events).

**Copilot OTel:** the current CLI reference explicitly documents
`github.copilot.nano_aiu` and `github.copilot.cost`, despite the second bundle's
reported documentation lookup gap. Nano AI units are billing units; `cost` is a
multiplier. Its root-span aggregation rule is specific to that OTel source.
Neither attribute was supplied as an observed Enterprise span.
[CLI reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#opentelemetry-monitoring).

**VS Code surface:** Agent Host and extension-host sessions have different storage
and lifecycles. Generic VS Code activity reports or legacy cost attributes cannot
certify the supplied local store. [Agent Host architecture](https://code.visualstudio.com/docs/agents/concepts/agent-host)
and [OTel monitoring](https://code.visualstudio.com/docs/agents/guides/monitoring-agents).
The current monitoring page does not list the bundle's cited legacy
`copilot_chat.total_cost_usd` field; its current availability remains unverified.
The bundle's quoted AI-credit price is not enough to convert these projections to
cash: they contain neither such quantities nor a verified invoiced billing basis.

## Assumptions rejected by this review

- A field-name inventory is not an observed event envelope. “Not shared”, “not
  inspected”, “absent from this container” and “unsupported by the product” differ.
- Neither lookup failure nor field names found inside chat text prove a telemetry
  field does or does not exist. Match parsed keys, source, version and semantics.
- The second bundle rebases each session independently. Equal zero timestamps
  cannot establish simultaneity, cross-session ordering or overlap. It also converts
  native Copilot ISO strings into numeric relative offsets; the sample type is not
  the native field type. The more specific README/manifest overrides the broad
  per-file wording in `CLASSIFICATION.md` for interpretation.
- Replacement namespaces do not independently prove original identifier inequality.
  Source non-overlap is a producer assertion; no verified host/SDK join survives.
- No `turn_usage` in the catalog, or no rows in the narrative `checkpoints` table,
  says nothing about separate per-session databases or SDK event files.

## Disposition and smallest next evidence

| Capability | Enterprise result |
| --- | --- |
| Local Cursor context/identity shape | Partial; validated projection relationships and optional fields. |
| Copilot identity/message schema | Partial; v2 adds reported integer message counters. Actual event parent chains, accounting boundaries and host/SDK links remain unverified. |
| Consumed tokens, cash, corrections, finality | Unverified for both Enterprise profiles. |
| Work OTel collection | Unavailable under reported global configuration; no enablement requested. |
| Custom session-log hook import | Log parsing/conversion and custom receiver reported; native input, mapping and output uninspected. No Admin API call reported. |
| Native OTel/CSV compatibility | Unverified; source records not supplied, independent of tier eligibility. |

A useful next bundle needs only one small, complete, already-authorized source
group per surface:

1. **Existing log parser:** hook trigger/version, product/runtime version and exact
   source container, plus a minimized native log record and matching upload payload
   or sanitized mapping code. Mark copied, renamed, converted, aggregated and
   classified fields. Identify classifier provenance and each amount's unit/scope.
   Include a matching saved record only if the receiver changes the payload.
   Exclude credentials, identities and deployment hostnames as before.
2. **Coverage and binding:** document log selection, rotation/truncation, partial
   writes, parser filters, repeated/corrected records and upload retry handling.
   Preserve stable replacement IDs across log input, upload and saved output.
   A hook firing at turn-end does not prove that a log total belongs to that turn
   or is final; timestamp-only association remains insufficient. Use existing
   repeated snapshots if available.
3. **Copilot:** identify its actual custom source separately, or provide an explicit
   host/SDK link with existing per-session `turn_usage`/SDK checkpoint evidence if
   available. Record the exact container; a session catalog is not a substitute.
4. **Unresolved JSONL wrapper:** one minimized native envelope with a safe event
   kind and consistent replacement IDs, preserving nesting and nullable parent
   values. A schema illustration with all values removed cannot resolve this.

Preserve within-group relationships and mark truncation. If policy requires
independent time rebasing, retain it and exclude cross-session temporal checks.
Do not request broader company data or change telemetry settings to fill gaps.

Confidence: high in supplied bytes, projected arithmetic and documented differences;
medium in producer-reported native shapes; no verified Enterprise consumption or
settlement. Versions, omitted stores and sanitization can change conclusions.
Primary risks are mapping projections as wire formats, false absence and broken
joins; mitigate with source-specific profiles and explicit evidence boundaries.
No provider call or cost was incurred by this review. Rollback reverts the authored
research diff; received artifacts remain unchanged and no adapter was implemented.
