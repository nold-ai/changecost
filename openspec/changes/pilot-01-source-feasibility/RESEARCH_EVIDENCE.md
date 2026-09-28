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
[capability matrix](../../../docs/providers/source-feasibility.md) and
[Codex/Claude comparison](../../../docs/providers/codex-claude-metrics.md), plus the
[Cursor local assessment](../../../docs/providers/cursor-local-metrics.md) and
[hosted Copilot assessment](../../../docs/providers/copilot-local-metrics.md), plus the
[Enterprise projection review](../../../docs/providers/enterprise-schema-review.md).
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
`66897c380da1b70f74c877e219f70bf6f693fead623e80217a5bc8d9cbd1f7dd`.
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

The [v2 review](../../../docs/providers/enterprise-v2-schema-review.md) records two
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

## Remaining work and rollback

Tasks 2.1/2.2 retain exact account acquisition, Copilot/Cursor usage exports and
unresolved profile semantics. Task 4.3 remains a later PR action. The existing
issue tracks the same change; locally authored work is unpublished until a real
branch/PR is pushed. No adapter is declared ready and the change is not archived.

Confidence: high in the narrow documented/local findings, low in complete
reconciliation. Failures to guard against are stale version assumptions,
duplicate/revised usage, and content leakage; mitigate with versioned profiles,
explicit finality/identity evidence and metadata-only synthetic projections.
No paid infrastructure or inference was required. Rollback is the scoped file
diff revert and restoration of the selected issue's prior body if necessary;
raw source data and account settings are unchanged.
