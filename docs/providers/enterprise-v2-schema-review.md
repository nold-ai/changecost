# Enterprise v2 schema review

Reviewed **2026-09-28 (Europe/Berlin)**. Enterprise tiers are maintainer-confirmed;
this does not verify billing or exporter configuration. Read the
[original review and reported work flow](enterprise-schema-review.md#reported-work-collection-path)
for context: OTel is disabled, no Admin API is called, and a custom hook reportedly
parses session logs before uploading converted fields. Neither v2 bundle includes
that script or a paired native-log/upload sample.

V2 adds **partial VS Code message-counter evidence and useful synthetic examples**.
It does not establish an Enterprise consumption ledger or approve an adapter.
Received files remain unchanged, including their manifests and line endings.

Received `artifacts/` bundles are local-only review inputs and are not included
in the repository or PR. Paths below identify those inputs, not portable links.
Only the authored synthetic cases and findings are published; local hash receipts
preserve which supplied bytes were reviewed.

## What changed

| Bundle | New evidence | Limits |
| --- | --- | --- |
| `artifacts/changecost_evidence_vscode_v2/README.md` | Producer reports integer `$.v.metadata.promptTokens` and `$.v.metadata.outputTokens` in selected host-session records; adds a synthetic projection, mappings and two documented-format Cursor examples. | Values are invented; versions, event envelope, identities, order and accounting boundary are withheld. This is producer-reported field evidence, not direct inspection of original logs. |
| `artifacts/cursor-copilot-schema-evidence-v2/README.md` | Seven reference files add positive token/cost arithmetic, repeated delivery, correction relationships, normalized Cursor/Copilot objects and candidate CSV. | All eight local sample files and the local schema are byte-identical to v1. Positive usage is synthetic, not newly observed local consumption. |

The first bundle reports identity fields alongside counters but omits their values
from the projection. A host ID found inside free text does not verify a structured
host/SDK link. Repeated message counters could be revisions or summaries; summing
them is not justified. Cache/reasoning inclusion, turn completeness and pricing
remain unknown. Do not transfer the second bundle's version numbers to this one.
The independent Personal Free hosted-SDK findings remain a separate profile.

## Integrity and arithmetic

All **28 manifest-listed hashes** match across the two v2 bundles, and the second
bundle's manifest sidecar matches. All 31 supplied files were hashed. Twenty-two
JSON documents, two JSONL records and one CSV parse. Ordinary JSON parsing permits
the repeated members described below; this is not a strict-schema validation pass.
The `schema.json` files are descriptive inventories, not executable JSON Schemas.

| Synthetic check | Result |
| --- | --- |
| First bundle Cursor metrics and request log | Category values agree: 120 input, 32 output, 24 cache-read and 0 cache-creation tokens; three distinct event IDs; error/correction share a usage-event ID. |
| Second bundle Cursor requests after event-ID dedupe | Two requests sum by category to 1,200 input, 240 output, 800 cache-read and 100 cache-creation tokens, matching its metric and normalized projections. Five delivered log records have four distinct event IDs. |
| Candidate CSV and normalized estimate | USD 0.01875 + USD 0.01250 + USD 0.00000 = USD 0.03125 using decimal arithmetic. This equality does not verify pricing. |
| Copilot normalized totals | 125,000,000 + 75,000,000 = 200,000,000 nano-AIU, equal to the invented checkpoint; direct totals sum to 170,000,000 nano-AIU and overlap the aggregate. |

These checks preserve separate categories; they do not prove cache inclusion or a
grand token total. The replayed log keeps event identity and token attributes but
changes its timestamp: it exercises identity-based dedupe, not byte-exact replay.
The correction targets a separate error group with no positive token/cost amount;
it does not test reversing a previously positive charge. Metrics lack request IDs,
so matching invented totals does not establish a real per-session metric/log join.

## Official-schema comparison and admission findings

Sources below were accessed on **2026-09-28**. No provider endpoint was called.

1. **OTLP enum mismatch:** the second bundle's
   `artifacts/cursor-copilot-schema-evidence-v2/reference-fixtures/cursor-otlp-metrics.synthetic.json`
   uses `"AGGREGATION_TEMPORALITY_DELTA"` in both sums. OTLP JSON requires integer
   enums; delta uses `1`, as in the first bundle. Decimal strings for int64
   `asInt`/`intValue` are appropriate. Preserve this received example as a known
   mismatch; use a separately reviewed derivative before treating it as a positive
   OTLP JSON fixture. Ordinary ProtoJSON acceptance would not prove OTLP JSON
   compliance. [OTLP specification 1.11.0](https://opentelemetry.io/docs/specs/otlp/#json-protobuf-encoding).
2. **Cursor semantic matches:** the synthetic examples retain documented token
   categories, delta sums, estimated USD, log identities and correction targets.
   JSON illustrations do not validate Cursor's documented binary-protobuf transport.
   A correction removes its usage group from billing; it is not another charge.
   [Cursor wire reference, scope 0.1.0](https://prod.cursor.com/docs/enterprise/opentelemetry-export/wire).
3. **Candidate CSV ambiguity:** its corrected row retains `billable=true` with
   `not_billed_errored`. The normalized companion excludes that group. A future
   internal format needs explicit correction precedence; filtering only the
   boolean would misclassify it. Its headers remain analyst-created, not vendor
   headers. Per-request costs and conversation allocation are synthetic.
4. **Copilot normalized shape is not a runtime envelope:** objects named
   `session_usage_checkpoint` and `session_shutdown`, plus snake-case token keys,
   are analyst representations. The SDK documents checkpoint data under an event
   envelope; its shutdown field list does not establish the example's
   `session_shutdown.totalNanoAiu`. Neither this naming nor an equal invented total
   proves native finality. [SDK event reference](https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/streaming-events).
5. **Stale documentation lookup remains:** the second bundle still says
   `github.copilot.nano_aiu` and `github.copilot.cost` were not confirmed in docs.
   The current CLI reference documents both, with the latter a multiplier, not
   money. Their absence in inspected local stores remains a separate finding.
   [Copilot CLI reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference).
6. **Duplicate JSON members remain:** the second bundle's unchanged
   `artifacts/cursor-copilot-schema-evidence-v2/samples/copilot-session-store-identity.json`
   repeats `absolute_timestamps` and `unprojected_sessions` with equal values.
   Preserve the original; any strict fixture admission needs a reviewed derivative.

The source bundles' requests for OTel exports are superseded for this workplace by
the maintainer's disabled-OTel clarification. Documentation-derived examples do not
change that configuration or establish what the custom log parser uploads.

## Updated decision

- **Partial:** producer-reported VS Code message counter paths/types.
- **Useful for research:** positive arithmetic and synthetic dedupe/correction cases,
  subject to the encoding and provenance findings above.
- **Unverified:** actual hook mapping, native export compatibility, complete session
  usage, cache boundaries, classifier provenance, cash basis and settlement.

The smallest next evidence remains sanitized parser mapping code or one matched
native log record and upload payload, with stable replacement identities and field
units. Include receiver output only if it transforms the upload. Existing version,
coverage, retry and correction details would resolve the remaining boundaries;
no telemetry enablement or new paid request is needed for this review.

Confidence: high in byte integrity, synthetic arithmetic and the cited encoding
mismatch; medium in producer-reported local paths; actual accounting remains
unverified. Main failure modes are synthetic examples mistaken for observations,
repeated counters added twice, and normalized keys mistaken for vendor fields.
Keep provenance, identity and source versions explicit to mitigate them. No runtime
collector or adapter changed. Rollback reverts the authored research diff while
preserving all received artifacts.
