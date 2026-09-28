# Personal-account source feasibility

Assessment: **2026-09-28 (Europe/Berlin), To-Validate**.
This is the research deliverable for
[pilot-01-source-feasibility](../../openspec/changes/pilot-01-source-feasibility/proposal.md).
No Copilot OTel or Cursor CSV export has been inspected. Authorized local Codex/Claude
metadata inspection found partial usage evidence, described in
[their assessment](codex-claude-metrics.md#observed-local-artifacts).
Scope covers Copilot, Cursor, Codex and
Claude Code, including their separately assessed CLI/IDE surfaces. A subsequently
installed VS Code supplied [hosted Copilot evidence](copilot-local-metrics.md);
other Copilot surfaces remain unverified. A reinstalled Cursor
3.22.7 Basic account supplied [local context evidence](cursor-local-metrics.md);
its usage CSV remains uninspected. The supplied [Enterprise schema bundles](enterprise-schema-review.md)
add local projection evidence for both products; they do not include actual OTel/CSV usage.
The [v2 review](enterprise-v2-schema-review.md) adds reported VS Code message counters
and checks synthetic arithmetic, with encoding and fixture-admission findings.
The maintainer reports work OTel globally disabled and a custom hook that appears
to parse session logs, convert fields and upload to a custom receiver; no Admin API
is called. The [reported source path](enterprise-schema-review.md#reported-work-collection-path)
takes priority over OTel requests; native input and transformed output remain uninspected.
No account settings, telemetry collection, paid services or adapters were enabled.

## Evidence and status rules

Keep **documented availability** and **observed personal-account support** separate.
For each capability, use these dispositions:

- **Supported:** an inspected, versioned source and its semantics satisfy the capability.
- **Partial:** inspected evidence supports a named subset with explicit exclusions.
- **Unavailable:** an established restriction or inspected source prevents that capability.
- **Unverified:** missing samples, versions, account access or conflicting evidence prevent a finding.

Documentation alone cannot establish observed support. Unverified is not unavailable,
and neither means zero usage or zero cost. A missing field in one profile does not
prove the provider never exposes it. Partial local evidence does not approve an
import mapping; there are **no approved adapter profiles**.

## Dated source inventory

All links below were accessed on 2026-09-28. Documentation is rolling, not a pinned
export schema. Installed `copilot`, `code` and `cursor` commands were not found on
the current shell's PATH; this does not prove the applications are absent elsewhere.
The inspected hosted Copilot tier is Personal Free, maintainer-confirmed; export
format versions remain unverified. Cursor Basic is maintainer-reported. Codex and Claude Code CLI
versions were inspected separately; see [their metric assessment](codex-claude-metrics.md).

| Surface / candidate format | Documented availability | Observed status / evidence required |
| --- | --- | --- |
| Copilot CLI / local JSON-lines | File export and billing attributes are described in [GitHub's CLI reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#opentelemetry-monitoring). | Unverified. Need CLI version, personal tier/billing basis, sanitized envelope, root/child samples and export boundary. |
| Copilot IDE / VS Code Copilot Chat JSON-lines | [VS Code monitoring](https://code.visualstudio.com/docs/agents/guides/monitoring-agents) describes local file export and token/session attributes. Other IDEs are not established by this source. | Unverified. Need actual IDE and extension versions, harness/surface, tier, envelope, window and conversation samples. |
| VS Code Agent Host / hosted Copilot SDK | [SDK events](https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/streaming-events) distinguish ephemeral usage and durable checkpoints. | Partial explicit host/SDK ID link, persisted token totals and nano AIU at VS Code 1.139.1, Personal Free (maintainer-confirmed); settlement and OTel unverified. See [local assessment](copilot-local-metrics.md). |
| Personal Cursor / usage CSV | Vendor forum reports conflict; see the chronology below. | Unverified. Need current headers, representative rows, account tier, app version, export date/range/timezone and basis of any cost-like value. |
| Cursor macOS / internal local store | [Context ring documentation](https://prod.cursor.com/docs/agent/prompting) describes occupancy, not a SQLite export contract. | Partial local identity/context evidence at 3.22.7, Basic (maintainer-reported). Empty usage data and zero counters do not establish consumption or money; see [local assessment](cursor-local-metrics.md). |
| Codex CLI / app / IDE | [Metric assessment](codex-claude-metrics.md#codex): CLI JSONL, app-server usage notifications and optional OTel. | Partial local Desktop usage evidence at runtime 0.158.0-alpha.2.1; standalone CLI 0.139.0 differs. Aggregation, billing regime and other surfaces unverified. |
| Claude Code CLI / IDE | [Metric assessment](codex-claude-metrics.md#claude-code): token and estimated-cost metrics. | Partial local usage at versions 2.1.275/2.1.215; standalone CLI 2.1.257 differs. Finality, entrypoint, tier and OTel unverified. |
| Cursor/Copilot Enterprise / supplied local projections | [Enterprise review](enterprise-schema-review.md) compares reported shapes with current official contracts. | Enterprise confirmed by maintainer. Partial local Cursor relationships and producer-reported VS Code message counters in [v2](enterprise-v2-schema-review.md); billing, complete usage and joins unverified. Synthetic examples do not establish native compatibility. |
| Work custom session-log hook | Maintainer reports log parsing and field conversion before upload to a custom receiver; no Admin API call. | Source log format, transformed payload, classifier provenance, units and binding unverified; inspect paired input/output independently of native OTel. |
| Cursor Enterprise / OpenTelemetry (OTel) | [Cursor documentation](https://prod.cursor.com/docs/enterprise/opentelemetry-export) requires Enterprise and a collector. | Unavailable to the personal tier; globally disabled in the work environment per maintainer. Native wire compatibility unverified. No enablement required for custom-hook assessment. |

### Cursor evidence correction

The [2026-07-31 vendor post](https://forum.cursor.com/t/usage-page-to-token-amount-what/167153/16)
reported removal of dollar costs from self-serve CSVs. The same author's
[2026-08-03 update](https://forum.cursor.com/t/usage-page-to-token-amount-what/167153/79)
reported restored CSV dollar values and distinguished on-demand charges from
included usage. A later [2026-09-02 support reply](https://forum.cursor.com/t/measuring-a-quota-through-a-gauge-that-only-shows-tenths-of-a-percent/170206/4)
again stated that CSV costs were removed. These accounts conflict.

**I don't know yet whether the maintainer's current personal CSV exposes monetary
values or what their basis is.** Evidence needed: dated sanitized headers/rows and
the account's explanation of included versus on-demand usage. Next step: perform
the work-side inspection below. Neither an all-cash nor a tokens-only profile is
approved from these posts. Do not enable paid overages merely to create a sample.

## Acquisition paths for later verification

These are documentation-based paths for any authorized existing source, not commands
executed here or authorization to start collection. Work OTel is reported disabled;
use the [custom log-hook evidence checklist](enterprise-schema-review.md#disposition-and-smallest-next-evidence)
there. OTel paths below are conditional references, not required work-side actions.

1. **CLI:** record its version and personal tier; locate an existing file previously
   selected by `COPILOT_OTEL_FILE_EXPORTER_PATH`. That variable enables collection,
   so do not set it merely to inspect old data. Record the exporter configuration
   without credentials. [CLI reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#opentelemetry-monitoring).
2. **VS Code:** record editor and Copilot Chat versions and the agent harness.
   In Settings, search `copilot otel`; record existing `exporterType` and `outfile`
   under `github.copilot.chat.otel`. The documented file path uses enabled OTel,
   exporter type `file` and a JSON-lines outfile. Inspect an existing authorized
   file; keep content capture disabled. If collection is off, stop and record the
   gap. [VS Code monitoring](https://code.visualstudio.com/docs/agents/guides/monitoring-agents).
3. **Cursor:** inspect an existing personal usage CSV and record how it was obtained.
   For a later authorized export, inspect the account's Usage page and chosen date
   range; confirm the actual export control and labels before recording exact UI
   steps. The [vendor update](https://forum.cursor.com/t/usage-page-to-token-amount-what/167153/79)
   describes CSV export, but this account's UI has not been inspected.
4. Review locally using the [fixture contract](fixtures.md). Supply only an allowlisted,
   sanitized sample and its manifest, never a raw billing export or transcript.
   An unavailable export/control is evidence to record, not a reason to scrape.

For the inspected VS Code Agent Host session, use the [local acquisition record](copilot-local-metrics.md).
For Codex and Claude Code, use the separate [acquisition/evidence checklist](codex-claude-metrics.md).

## Economic and attribution assessment

The following names are documentation candidates, not implemented field mappings.

**CLI:** the reference identifies `gen_ai.conversation.id`, input/output and cache
token attributes, `github.copilot.nano_aiu` (1 AIU = 1,000,000,000 nano AIU), and
`github.copilot.cost` as a multiplier. It instructs readers to use root
`invoke_agent` billing rather than sum repeated child values.
[CLI reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#opentelemetry-monitoring).
These OTel semantics have not been validated by the separately inspected
[hosted SDK logs](copilot-local-metrics.md). Actual span presence, missing-root behavior, nested invocation ownership, replay identity,
completeness and corrections still require inspection. No cash conversion is approved.

**IDE:** VS Code documents `gen_ai.conversation.id`, token attributes,
`service.version` and a resource `session.id` scoped to a window.
[VS Code monitoring](https://code.visualstudio.com/docs/agents/guides/monitoring-agents).
Do not equate a window with a conversation or copy CLI billing rules to every IDE
span. Actual billing units, revisions, duplicate identity and complete coverage
are unknown. Keep embedded CLI and extension evidence distinct until joins are verified.

**Cursor CSV:** headers, row identifiers, units, cash basis, revision signals and overlap
identity are all unverified. The separately inspected [local store](cursor-local-metrics.md)
provides context occupancy and one identity match; it does not resolve these CSV gates. Require separate input/output/cache quantities where
present. An unlabeled cost-looking column is not proof of billed currency. A token
sample without money makes cash unavailable **for that sample**, not for all Cursor
accounts. A missing session ID needs explicit manual mapping or unbound evidence;
time proximity cannot establish provider authority.

| Capability | Copilot CLI | Copilot IDE | Personal Cursor | Admission evidence |
| --- | --- | --- | --- | --- |
| Offline usage import | Unverified standalone/OTel | Partial hosted SDK fields; extension OTel unverified | Unverified | Observed format/version, exact fields/types and units, missing-field examples. |
| Provider session joins | Unverified standalone/OTel | Partial explicit host/SDK link | Partial local ID match; CSV/cross-session joins unverified | Stable source IDs, scope and cardinality across independent sessions. |
| Change attribution | Unverified | Unverified | Unverified | Verified session/run binding or explicitly manual evidence mapping; no timestamp inference. |
| Billing units / cash | Unverified / unverified | Partial hosted nano AIU / cash unverified | Unverified / unverified | Units, currency and billing basis; distinguish included usage, estimates and charged amounts. |
| Duplicate / overlap handling | Unverified | Unverified | Unverified | Repeated records/files and stable identities; ambiguous overlaps cannot be additive totals. |
| Completeness / corrections | Unverified | Unverified | Unverified | Coverage window, truncation/loss behavior and correction identity, or explicit partial/unknown findings. |

Missing monetary values stay unknown. Preserve decimal text and original units;
this research introduces no rounding policy, exchange rates or pricing database.
Do not sum root totals with their constituent child totals, or cumulative snapshots
with deltas, until the profile defines an authoritative boundary.
Codex and Claude Code have partial observed metadata support, with their specific
usage/estimate, repetition and snapshot issues recorded in [their dispositions](codex-claude-metrics.md#dispositions-and-next-evidence).

## Work-side evidence checklist and adapter gate

For each selected surface across Copilot, Cursor, Codex and Claude Code, record:

1. Observation date/timezone; product/extension/export version; personal account tier
   and billing regime (no account identifiers); actual acquisition steps and filters.
2. Exact sanitized headers/envelope and field types; one ordinary record, missing
   fields, repeated root/child attributes where applicable, and session boundaries.
3. Coverage start/end, timezone and known gaps; re-export/overlap behavior; stable
   event IDs; a correction example if accessible. If unavailable, record that fact.
4. Unit and billing-basis evidence. Absence of an on-demand row is not proof of zero
   cost or a reason to incur charges. Never derive cash from multipliers or tokens.
5. The [redaction manifest](fixtures.md#redaction-and-provenance-manifest), including
   transformed relationships, omitted fields and limitations. Keep raw input local.

Then update each matrix cell and the linked task with the inspected evidence and
its limits. A profile needs observed shape, version, safe fixtures and an explicit
per-capability decision before it can authorize mappings. Documentation-only and
synthetic examples cannot pass that gate. Unsupported capabilities remain excluded;
a wholly unavailable source needs a maintainer scope decision before its adapter.

[Copilot #13](https://github.com/nold-ai/changecost/issues/13) and
[Cursor #14](https://github.com/nold-ai/changecost/issues/14) remain blocked by
[feasibility #9](https://github.com/nold-ai/changecost/issues/9) and reconciliation
#12. The [change order](../../openspec/CHANGE_ORDER.md) is unchanged. Do not close
#9, archive this change, or claim provider compatibility while task 2.2 is pending.

## Limits, risk and rollback

Confidence: high in the recorded documentation findings; low in account-specific
compatibility. Different tiers, installed versions or export shapes could change
the conclusions. No paid infrastructure is needed; the remaining work is a bounded
manual inspection, with duration unknown until the exports are available.

| Failure mode | Mitigation |
| --- | --- |
| Stale or conflicting provider claims | Dated citations and observed versioned samples; no inferred support. |
| Double counting or false attribution | Preserve graph/identity evidence; keep ambiguous values unbound or partial. |
| Sensitive content in telemetry | Allowlist metadata, replace identifiers, and review the entire sanitized artifact. |

Rollback: remove/revert this research-and-fixture diff. No runtime, database,
account configuration or collected data is changed. Verification is recorded in
[RESEARCH_EVIDENCE.md](../../openspec/changes/pilot-01-source-feasibility/RESEARCH_EVIDENCE.md).
