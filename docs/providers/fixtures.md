# Source-feasibility fixture contract

Status: **2026-09-28 (Europe/Berlin), synthetic research examples only**.
Read the [source assessment and admission gate](source-feasibility.md) first.
No provider wire profile or adapter is approved by these examples.

## Included artifact

[source-feasibility-cases.json](fixtures/source-feasibility-cases.json) contains
hand-authored cases and expected research dispositions. Its wrapper is an internal
example format, not `changecost/v1`, an OTel wire encoding, or a Cursor CSV schema.
Copilot attribute projections use only the documented names cited in the assessment;
transport ID/parent fields illustrate required joins without claiming an observed
export envelope. Cursor-like cases use explicitly fictional semantic fields because
personal CSV headers have not been inspected. Correction fields are hypothetical.

The bundle has synthetic values throughout. Four cases use field names and repetition
patterns from authorized local metadata inspection; they are minimized projections,
not redacted whole transcripts. All identifiers, dates and quantities were authored here.
The v2 follow-up adds a hand-authored case using producer-reported message
counter paths, plus a hand-authored encoding distinction. The original Enterprise
logs were not inspected, so the message-counter case does not claim observed-shape
provenance. These examples demonstrate
the evidence gate and future test inputs, not passing adapter tests or successful
live reconciliation.

| Case | Expected assessment / invariant |
| --- | --- |
| `cli-repeated-billing` | Root and child repeat 100 nano AIU; replay repeats the same root. Count the authoritative root once: 100, not 200 or 300. Cash stays unknown. |
| `cli-missing-root` | A child alone cannot prove authoritative aggregate billing or completeness. Do not treat it as a zero-cost invocation. |
| `multiplier-only` | A multiplier of 2 is explanatory metadata, not 2 currency units. |
| `ide-window-only` | Two records share a window and lack conversation IDs. Both remain unbound unless explicitly mapped. |
| `tokens-only` | Preserve 100 input and 20 output tokens separately; cash unavailable for this sample, not zero. |
| `timestamp-only` | Identical timestamps do not establish a shared session or change. |
| `ambiguous-overlap` | Two fictional files repeat a row without stable IDs. Do not claim a fully reconciled additive total. |
| `correction` | Fictional replacement revision changes 0.05 USD to 0.03 USD. Retain history; current total is 0.03, not 0.08. Replay adds nothing. This proves no provider supports such a correction. |
| `codex-usage-snapshot` | Preserve last versus total token usage and a repeated snapshot. A total of 120 tokens is not 240 after replay. Cash remains unknown. |
| `claude-estimated-cost` | Preserve 0.03 USD as an estimate, with billed cash unknown. A replayed cumulative point does not add another 0.03 USD. Missing session identity leaves it unbound. |
| `codex-rollout-cache-write` | Preserve observed cache-write field and distinct rollout version. The token event lacks a turn ID; nearby context cannot by itself approve a join. Repeated totals are not additive. |
| `enterprise-projection-boundaries` | Independent zero-based clocks do not establish overlap; synthetic context, local abort and missing usage do not establish consumption or corrections. |
| `copilot-container-absence` | An empty narrative checkpoint table and catalog without usage leave SDK checkpoint availability unknown. |
| `copilot-hosted-usage-boundaries` | Link distinct host/SDK IDs using explicit metadata. Preserve top-level versus turn totals, overlapping direct/aggregate nano AIU, a lower session-named value and a durable checkpoint. Missing ephemeral events is not zero usage; finality/cash stay unknown. |
| `cursor-context-not-consumption` | Nonzero context occupancy with empty usage data and zero token counters does not prove zero consumption or billed cost. A saved completion flag does not settle finality. |
| `enterprise-message-counter-boundary` | Repeated synthetic VS Code message counters have no retained identity/boundary; do not infer additive session tokens or cash. |
| `documented-example-not-wire-evidence` | A string enum is not valid OTLP JSON temporality; a numeric delta enum does not itself verify native exports or the hook mapping. |
| `claude-message-revisions` | Distinct record IDs share request/message identity, with both equal and changed usage. Count neither each record nor a guessed final value; record unresolved finality. |

## Received Enterprise projections

The [Enterprise review](enterprise-schema-review.md) keeps received bundles separate
from this authored fixture contract. They are evidence inputs, not native wire
fixtures: one is schema-only; the other rebases clocks, changes timestamp types,
uses synthetic occupancy and omits groups. A duplicate-member JSON sample also
needs an explicitly normalized derivative before strict fixture admission. Preserve
received bytes and manifests; do not run whitespace auto-fixes on these originals.
Checks on projections cannot certify private originals, cross-session timing or
unsupported provider capabilities. `enterprise-projection-boundaries` and
`copilot-container-absence` below are hand-authored scenarios motivated by this
review, not additional observed Enterprise records.

## Allowlist before inspecting real sources

Default-deny all fields, including arbitrary nested resource attributes. Preserve
the smallest subset needed for a specific capability; presence in an export alone
does not authorize retention.

- **Copilot CLI candidate:** operation kind, synthetic trace/span/parent/conversation
  identities, source version, input/output/cache token quantities and documented
  billing-unit/multiplier attributes referenced in the assessment. Preserve missing
  fields and types. Record any newly needed field before admitting it.
- **Hosted Copilot observation:** synthetic host/SDK/turn/event IDs and explicit
  link evidence; installed/recorded versions; usage input/output/cache fields;
  selected `_meta` turn/direct totals, multiplier and nano-AIU fields; checkpoint
  `totalNanoAiu`/`totalPremiumRequests`. Exclude quota snapshots, model/cache state,
  messages and Git/workspace bindings. See [observed boundaries](copilot-local-metrics.md).
- **VS Code candidate:** operation kind, synthetic trace/span/parent/conversation
  identities, synthetic window identity, editor/extension version and token
  categories. Do not assume the CLI's economic attributes apply to this surface.
- **Personal Cursor:** no native header allowlist is approved yet. First review
  sanitized header names and document their meanings. Candidate semantic categories
  are timestamps, synthetic row/session IDs if present, token categories and a
  verified amount/unit/billing-basis tuple. Do not invent headers for an adapter.
  The separately observed local Cursor projection allows synthetic `composerId`
  and `bubbleId`, app version, internal `_v`, status, empty `usageData`, context
  quantities/percentage and `tokenCount` input/output fields. Keep occupancy separate
  from consumption; no message bodies, model configuration or encryption metadata.
  See the [local observation](cursor-local-metrics.md).
- **Codex candidate:** usage event type, synthetic thread/turn IDs, source version
  and documented token fields; preserve `last`/`total` boundaries. Exclude all item
  messages, commands and outputs. See the [installed-schema evidence](codex-claude-metrics.md#codex).
  The separately observed Desktop projection also allows synthetic session IDs,
  runtime/source metadata, `total_token_usage`/`last_token_usage`, cache-write tokens
  and null rate limits. Actual quota/account metadata is excluded.
- **Claude Code candidate:** token/cost metric name, value/unit, token category,
  temporality, shifted interval, synthetic session identity and source version/
  entrypoint. Retain estimated cost as estimated. No user identity or arbitrary
  resource fields. See the [metric evidence](codex-claude-metrics.md#claude-code).
  The separately observed local projection allows synthetic `sessionId`, `uuid`,
  `parentUuid`, `requestId`, `message.id`, version and four token quantities under
  `message.usage`; it has no message content or other transcript fields.

Do not retain prompts, responses, tool payloads, source snippets, free-text errors,
credentials, endpoints/headers, email, account/user/device identifiers, file paths,
repository names/remotes or branch names. Even pseudonymous provider user IDs are
excluded. Source/format versions may be retained; model names are unnecessary for
these cases. If a forbidden header name contains identifying data, replace it in
the shared sample and note that exact-header approval is still blocked.

## Received v2 examples

The [v2 review](enterprise-v2-schema-review.md) keeps received source bundles separate
from this authored fixture contract. Their synthetic positive values are useful
research inputs; they are not admitted native wire fixtures. The second bundle
retains duplicate JSON members and uses string enums in its OTLP-shaped metrics.
Candidate CSV headers and normalized Copilot keys remain analyst-defined. Preserve
originals and review any corrected derivative separately before future parser tests.

## Deterministic transformation rules

For a later authorized bundle, enumerate each identifier namespace in stable
file/record order. Assign `trace-001`, `span-001`, `conversation-001`, etc. on first
occurrence; reuse the mapping across every file and all references. Parent IDs use
the span namespace. Distinct originals stay distinct; repeated originals stay equal.
Scope namespaces by source unless an inspected cross-source join proves equivalence.
Never create a missing source ID or reconstruct one from time. This is a documented
review procedure, not an implemented sanitizer.

Keep the temporary original-to-synthetic table private and outside Git. Publish
only a count/relationship summary. Do not hash raw IDs as a public substitute.
Use one fixed timestamp offset across the bundle, preserving order, equality,
durations and overlaps. Shift coverage windows too; record units/timezone and the
fact of shifting, not the identifying original timestamp. Preserve field absence,
null and zero distinctly. Replace real financial values with synthetic values
while maintaining duplicates, revision relationships and unit separation; document
the replacement so no one mistakes the fixture for billing evidence.

Reject a transformation that changes join cardinality, merges independent sessions,
removes a needed duplicate or makes a correction look additive. Keep original data
under the maintainer's retention policy; ignored files are not an access-control
boundary. Only reviewed synthetic equivalents belong in the repository.

## Redaction and provenance manifest

Each future source fixture must record:

- Source surface, installed product/extension and export versions, account tier and
  billing regime without identifying the account; observation date/timezone.
- Whether it is synthetic or derived from an authorized observation; documentation
  links/access dates; private evidence reference without a raw file path or payload.
- Verified acquisition route, filters/coverage, envelope/header types and field
  meanings; explicit unknowns, units, billing basis and completeness limitations.
- Field allowlist, dropped categories, timestamp/value transformations, identifier
  namespaces and cardinalities, parent/join/replay/correction relationships.
- Expected per-capability disposition, redaction reviewer/date, fixture SHA-256 and
  limitations. Actual fixture bytes must match the reviewed digest.

For the included bundle, case provenance is `hand-authored-synthetic` or
`synthetic-values-from-observed-local-shape`. Source versions are stated only for
inspected interfaces/local shapes; account tier remains null. No original record
or real quantity was copied. The
[research evidence](../../openspec/changes/pilot-01-source-feasibility/RESEARCH_EVIDENCE.md)
records the reviewed digest and structural checks. Its JSON keys are exactly the
example contract, with no pass-through attributes or content fields. Before sharing
a new fixture, inspect every value in addition to key and credential checks.


## Closeout assessment (2026-10-03)

The development-only inspector and all 18 executable semantic cases are documented in [source feasibility](source-feasibility.md#executable-closeout-checks-2026-10-03). Original research fixture bytes are unchanged. Faulty/repaired controls and additional missing-identity, checkpoint-conflict, reset, correction, unit and privacy cases are in tests/test_source_feasibility.py. Structural inspection reports use ordinal selectors only; private manifests retain paths/field selectors. Passing synthetic tests does not authorize any provider profile.

See the canonical [profile register](source-profiles.json) and [current evidence gate](source-feasibility.md#reinspection-and-current-blockers).
