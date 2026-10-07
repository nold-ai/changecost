# Cursor local metadata assessment

Assessment: **2026-09-28 (Europe/Berlin), partial observed evidence**.
The maintainer authorized inspection of one identified, reportedly running local
session after reinstalling Cursor. Installed macOS app: **3.22.7**, read from its
bundle metadata. Account: **Basic, maintainer-reported**, not independently checked;
no Pro or Enterprise capability is inferred. The session identifier stays private.

## Acquisition and observation

Two read-only SQLite transactions inspected the existing local store at
`~/Library/Application Support/Cursor/User/globalStorage/state.vscdb` on
2026-09-28 at **10:04:52** and **10:07:59 +02:00**. Rows in `cursorDiskKV` were
selected by the supplied session identifier, then projected onto metadata fields
from `composerData` and `bubbleId` records. No database, journal, transcript or
content payload was copied; no model request or collector was started.

The ignored local evidence records source-byte hashes, field shapes, aggregate
relationships and snapshot times. This is an observed internal storage shape,
not a documented, supported export API or production adapter contract. No ongoing
monitor was installed. Other conversations and account credentials were excluded.

| Observed field / relationship | Finding and limit |
| --- | --- |
| `composerData.composerId` | Matches the maintainer-supplied session ID. One conversation supports a local identity match, not cross-session uniqueness or a CSV join. |
| `composerData._v` | Value 18 in the second snapshot; internal meaning/version compatibility is unverified. |
| `contextTokensUsed`, `contextTokenLimit`, `contextUsagePercent` | Populated, nonzero context occupancy. The percentage equals used / limit × 100; it is not an account quota percentage. |
| `promptTokenBreakdown` | `totalUsedTokens` equals context occupancy; eight category `estimatedTokens` values sum to that total. Values persisted unchanged between snapshots. |
| `usageData` | Empty object in both snapshots. No settled token or money total is established. |
| 22 `bubbleId` records | All inspected `tokenCount.inputTokens` and `outputTokens` values are zero. Nonzero context exists alongside them; do not report zero consumed tokens from these counters. |
| Request identity | Only one of the 22 bubble records has a nonempty `requestId` in the second snapshot. Do not assume every bubble is a distinct provider request. |
| Persisted `status` | `completed` in both snapshots; the second has zero generating bubble IDs. This does not establish that the user has ended the conversation or that billing is final. |
| Snapshot hashes | The selected source-byte hash set changed while the listed context/counter values stayed equal. These are mutable snapshots, not immutable usage events. |

## Documentation compared with actuals

Cursor describes its context ring as the fullness of the model's fixed context
window, with category breakdown and compression of older conversation as it fills.
[Cursor prompting documentation](https://prod.cursor.com/docs/agent/prompting),
accessed 2026-09-28. The local context fields are consistent with that description.
The documentation does not establish this SQLite layout or its billing semantics.

**Inference:** context occupancy cannot serve as cumulative consumed-token or
billed-cost evidence. Reused context and compression prevent interpreting successive
occupancy snapshots as additive usage. Empty usage data and zero counters do not
establish free usage, exhausted quota, a Basic restriction, or a telemetry fault.
I don't know yet why these counters are zero; provider documentation or a matched
completed-session usage export is needed to explain them.

## Disposition and next evidence

- **Partial:** local identity match and context occupancy for this version/session.
- **Unverified:** authoritative input/output/cache consumption, cost/billing basis,
  CSV identity joins, finality, corrections, complete coverage and stable storage API.
- **Excluded:** Enterprise OTel for this Basic-account observation.

The [CSV assessment](source-feasibility.md#cursor-evidence-correction) remains open.
Next, inspect an authorized usage export for the completed session and compare its
fields and coverage with these local observations. If it omits a stable session ID,
retain manual/unbound attribution; do not match by timestamp alone. No upgrade or
paid request is needed merely to fill an evidence gap.

The synthetic `cursor-context-not-consumption` case in the
[fixture contract](fixtures.md) preserves empty/zero/nonzero distinctions using
invented identifiers and quantities. It does not publish this session's usage.

Confidence: high in the inspected metadata, low in consumption/billing feasibility.
Another version, account tier or completed turn may change the fields. Key failure
modes are mistaking occupancy for consumption, treating zeros as free usage, and
prematurely trusting completion; separate metrics and require final export evidence.
Inspection incurred no inference cost. Rollback removes this research diff; source
storage and account settings were unchanged.


## Closeout assessment (2026-10-03)

Read-only reinspection of the same authorized store on 2026-10-03 found changed bytes across 23 selected records, with empty usageData and zero bubble counters. The new digest is recorded separately in the profile register. These observations establish neither zero consumption nor a final charge. No personal usage CSV was supplied; exact headers, app/export version, tier, acquisition, range/timezone, stable identity, overlap and charge basis remain required.

See the canonical [profile register](source-profiles.json) and [current evidence gate](source-feasibility.md#reinspection-and-current-blockers).

## Later local discovery and adaptive-demand scope — 2026-10-07

The earlier observations above remain historical. The authorized 2026-10-06
Cursor discovery and newer representation/version limits are summarized in
[adaptive evidence](../research/adaptive-demand-evidence.md#authorized-local-discovery--2026-10-06).
No new native approval is inferred. #9 now uses capability-based closeout; missing
optional exports do not block all lanes, but usage/identity/correction/finality
proof remains required for supported mappings. Source support, demand-learning
coverage and billed-money authority remain independently gated.
