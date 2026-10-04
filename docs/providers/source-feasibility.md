# Personal-account source feasibility

Assessment: **2026-10-03 (Europe/Berlin), To-Validate**.
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

## Profile register and derived matrix

The [structured register](source-profiles.json) is the canonical per-version inventory.
The table below is derived by `python -m quality.source_feasibility --matrix`;
its checked-in boundaries are verified by the default checker. Specialist documents
retain interpretation and historical observations. Documentation is rolling, not a pinned
export schema. Historical links retain their original 2026-09-28 access date. Installed `copilot`, `code` and `cursor` commands were not found on
the current shell's PATH; this does not prove the applications are absent elsewhere.
The inspected hosted Copilot tier is Personal Free, maintainer-confirmed; export
format versions remain unverified. Cursor Basic is maintainer-reported. Codex and Claude Code CLI
versions were inspected separately; see [their metric assessment](codex-claude-metrics.md).

<!-- source-profile-matrix:start -->
| Profile / version / tier | Usage | Attribution | Billed money | Finality |
| --- | --- | --- | --- | --- |
| copilot-hosted / VS Code 1.139.1; Chat 0.67.0; SDK 1.0.73; recorded 0.0.0 / historical Personal Free (maintainer-confirmed) | partial | partial | unverified | unverified |
| copilot-cli / uninspected / personal tier unverified | unverified | unverified | unverified | unverified |
| copilot-ide / uninspected / personal tier unverified | unverified | unverified | unverified | unverified |
| cursor-local / 3.22.7; internal _v 18 / historical Basic (maintainer-reported) | partial | partial | unverified | unverified |
| cursor-personal-csv / uninspected / personal tier unverified | unverified | unverified | unverified | unverified |
| codex-app-server / 0.139.0 / unverified | unverified | unverified | unverified | unverified |
| codex-desktop / 0.158.0-alpha.2.1 / unverified | partial | unverified | unverified | unverified |
| claude-2-1-275 / 2.1.275 / unverified | partial | unverified | unverified | unverified |
| claude-2-1-215 / 2.1.215 / unverified | partial | unverified | unverified | unverified |
| claude-2-1-257 / 2.1.257 / unverified | unverified | unverified | unverified | unverified |
| enterprise-copilot-projections / bundle v1/v2; native versions unverified / Enterprise (maintainer-reported) | partial | unverified | unverified | unverified |
| enterprise-cursor-projections / bundle v1/v2; native versions unverified / Enterprise (maintainer-reported) | partial | unverified | unverified | unverified |
| codex-ide / uninspected / unverified | unverified | unverified | unverified | unverified |
| claude-ide / uninspected / unverified | unverified | unverified | unverified | unverified |
<!-- source-profile-matrix:end -->

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
[feasibility #9](https://github.com/nold-ai/changecost/issues/9)'s incomplete source
inspection. Settlement #12 merged in [PR #28](https://github.com/nold-ai/changecost/pull/28)
on 2026-10-02 and is accepted/archived; its implementation prerequisite is delivered.
The [change order](../../openspec/CHANGE_ORDER.md) is unchanged. Open #9 does not
waive task 2.2: do not archive this research change or claim provider compatibility
until the source-profile evidence gate is satisfied.

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


## Executable closeout checks (2026-10-03)

The development-only `quality.source_feasibility` module checks the register, derived
matrix and all 18 original synthetic cases. It computes conclusions from record
identities, values, units and revision links; expected answers are used only for
comparison. Those detector tests cannot approve provider semantics. No public
ChangeCost command, runtime policy, portable schema or migration changes.

```sh
uv run --locked python -m quality.source_feasibility
uv run --locked pytest tests/test_source_feasibility.py
uv run --locked python -m quality.source_feasibility --manifest .changecost/source-manifest.json
```

Store manifests and native input only in ignored local locations. Manifest format:
`source-inspection/v1`, with `entries` containing registered `profile`, `evidence_id`,
private `path`, byte `sha256`, `format` (`json`, `jsonl` or `csv`), and `fields` (lists
of key components). The registered evidence hash must match the received original.
Do not overwrite originals to make a check pass. Supply sanitized copies as separate
evidence entries, retaining the original digest and transformation receipt privately.

The inspector opens regular files without following links in any path component,
reads at most 10 MiB per file and hashes/parses those same bytes. It rejects duplicate
JSON members, nonfinite numbers, invalid UTF-8, malformed CSV, duplicate headers,
row-width mismatches, depth above 32 and record/container counts above 10,000.
Register and manifest documents use the same bounds. Reports contain validated registered opaque profile/evidence keys, ordinal entry/field
references, checked hashes, byte/record counts and type/missing counts. Failures after
reference validation contain a JSON fixed error code plus that safe registered pair;
unknown, unsafe or ambiguous references produce a redacted fixed code. No payload
values, source paths, native identifiers, caller labels or field names are reported.
CSV cells remain strings: passing structure establishes no numeric/unit interpretation.

The test suite exercises both subprocess diagnostics and the same CLI entry point
in process: default checks, derived matrix output, private-manifest reports, hash
rejection, matrix drift/repair and safe malformed-input failures. These controls
cover the publishing boundary without changing the inspection or approval contract.

Synthetic checkpoint controls group totals by explicit SDK session scope and event
identity. Distinct events can show cumulative progress; identical replay is not a
conflict. Different totals for the same session/event identity are conflicting;
missing identity leaves that assessment unresolved. The fixture container's
`identity_evidence.sdk_session_id` supplies scope. Optional per-record
`synthetic_context.sdk_session_id` is authored test context, not a native wire field.
These controls neither add totals nor establish session finality or native approval.

An approval requires a reviewed native evidence digest bound to the exact profile
fingerprint, capability and independent reviewer, plus authority, accounting interval,
replay, reset, correction and exclusion decisions. This validates consistency of a
contributor attestation; it does not authenticate the reviewer or provider. No current
profile has an approval. A structural pass is never a semantic approval.

### Reinspection and current blockers

On 2026-10-03, read-only reinspection of the previously selected hosted Copilot and
Cursor metadata found changed source bytes; historical originals and receipts remain
preserved. Copilot had 367 persisted events; checkpoint and selected turn-usage
projections remained unchanged. Cursor had 23 selected records with empty usage data
and zero bubble counters. These counts describe inspected records, not complete usage.
Current hashes are in the register; private pointers and earlier receipts are ignored.
Installed CLI metadata still reported Codex 0.139.0 and Claude Code 2.1.257, separate
from recorded Desktop and transcript versions. No new native export or hook mapping
was supplied. #9 remains open; #13/#14 remain blocked by source approval.

| Required artifact | Blocked capability |
| --- | --- |
| Native Copilot CLI and IDE exports with versions/tier, identities, replay and coverage/finality boundaries | Per-surface aggregation authority and complete attribution |
| Actual personal Cursor CSV with exact headers, version/tier, acquisition, range/timezone, stable identity and overlap/correction samples | Consumption, included usage, estimates versus billed charges and reliable attribution |
| Hosted Copilot authority/interval/cache/reset/correction/finality evidence | Additive usage and terminal nano-AIU accounting |
| Sanitized custom-hook mapping code or paired native input/upload output; receiver transformations separately | Enterprise producer-to-upload semantics and receiver effects |

Fresh primary-source checks on 2026-10-03 retain the documented boundaries:
[SDK events](https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/streaming-events)
distinguish ephemeral per-call usage and persisted checkpoints;
[CLI reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference)
and [VS Code monitoring](https://code.visualstudio.com/docs/agents/guides/monitoring-agents)
describe optional OTel routes, without proving this account's exports.
[Cursor usage](https://prod.cursor.com/help/models-and-usage/usage-limits) does not
establish the personal CSV's headers or accounting basis.
[Claude monitoring](https://code.claude.com/docs/en/monitoring-usage) documents usage
metrics separately from account billing. Missing native evidence remains To-Validate.

Confidence: high in bounded offline detector behavior after the recorded controls;
low in uninspected profile semantics. Different versions, tiers, receiver mappings or
export intervals could change findings. No paid infrastructure is used. Remaining
inspection duration depends on supplied artifacts. Rollback reverts code/docs while
preserving original evidence, stash recovery and truthful issue state.

### Reviewed detector boundary corrections — 2026-10-03

Replacement references use exact nonnegative integer types, excluding boolean values.
Cumulative estimates require parseable timezone-aware timestamps with ordered bounds;
comparison uses UTC instants, including equivalent start/end offsets and replay conflicts.
Missing or invalid intervals remain unresolved. No checkpoint records or incomplete
checkpoint identity/amount remain unresolved unless a known same-session/event conflict
is demonstrated. These are synthetic detector controls; final usage and provider
approval remain unverified.

### Scoped identity and correction invariant replan — 2026-10-03

Every existing affirmative identity consumer requires exact nonblank strings:
root conversation/span, snapshot thread/turn, rollout session/version, and hosted
namespace/checkpoint scope. Missing, null, Unicode-whitespace or nonstring labels
cannot establish a total or positive scope claim. Valid labels retain their exact
bytes; trimming cannot conflate different identities. Synthetic replacement chains
require a complete stable event/currency/billing-basis key and present nonnegative
integer revision/reference identities, excluding booleans, nulls and coercion.
Missing or mixed economic bases remain unresolved. Quantities, precise Decimal
amounts, finality and native-profile approval policies remain unchanged.

### Quantity and message correlation repair — 2026-10-04

Snapshot and rollout detectors validate every quantity before collapsing replayed
totals. Boolean, floating-point and negative values cannot hide behind an equal
integer in a set. Zero remains zero, missing values remain unknown, and unequal
valid totals remain unresolved. Rollout metadata scope is checked separately from
quantity selection to keep functions focused.

Claude request/message counts require complete nonblank record, request and message
identities for every row and a stable record-to-request/message mapping. A missing
identity in one row or conflicting links for one record leaves those counts
unresolved. Exact replay preserves correlation counts. Physical record count remains
the observed row count; usage-variant count remains a structural observation. Neither
establishes unique requests, additive consumption or finality. Native profile
approval remains pending the artifacts listed above.

### Registered report provenance repair — 2026-10-04

A report's provenance is the registered opaque profile/evidence pair and checked byte
hash. Evidence labels are scoped to their profile; distinct references can share
bytes. Reordering or replaying manifest entries preserves those references independently
of caller-order ordinals. Only matched registered keys in the bounded lowercase ASCII
letter/digit/hyphen grammar (1–80 characters) are publishable; register authors must
use opaque public references rather than private identifiers. This validates reference
shape and binding, not the truth of native claims.

The direct inspection function checks safe-key grammar and duplicate reference
ambiguity before publishing. Caller labels, evidence origin text, private paths, native
identifiers, selectors and payloads are excluded. After a reference is validated,
malformed-input, hash and selector failures retain the safe pair with a fixed code.
A failed inspection emits no partial success report or unverified success hash.
Structural success remains separate from semantic approval, accounting authority and
finality; missing native source artifacts still block issue #9 completion.

### Complete existing-conclusion inventory repair — 2026-10-04

Cumulative metric labels must be exact nonblank strings before accounting series
keys are grouped. Missing, whitespace-only, nonstring or mixed exact labels leave
estimates unresolved; Boolean/integer aliases cannot collapse identity keys. Valid
strings retain their original bytes. Existing Decimal validation and UTC ordering,
reset and equal-endpoint conflict checks keep their precedence and meaning.

Retained revision count requires a complete single event/currency/billing-basis
scope. Mixed or incomplete scopes leave both the current amount and that history
count unresolved. Within one complete scope, replay preserves distinct revision
count even when conflicting amounts make the current amount unavailable. This
does not add a physical-row count or a cross-event accounting policy.

Unsupported Enterprise projection reference fields, including positive-looking
amounts or correction keys, cannot demonstrate a billing correction. The existing
not-demonstrated correction outcome, unknown consumption/money and false native
compatibility remain conservative. Observed multipliers, unit labels, integer field
types and cache/turn metadata presence remain observations; they do not establish
ledger quantities, attribution, cash, finality or native source support.

### Token record completeness and partial profile details — 2026-10-04

The `tokens-only` research case selects an explicit single-record strategy. Extra
records, including identical replays and malformed trailing quantities, reject the
case rather than hiding evidence behind the first row. The shared timestamp and
overlap strategies retain their multi-record boundary observations; no token
aggregation policy is introduced. One record still distinguishes missing from zero.

Any partial capability requires nonempty valid field meanings and unresolved
requirements in the register. Empty, whitespace-only or malformed details cannot
sustain a partial claim. Profiles without partial capabilities do not acquire a
new unresolved-requirements obligation. Existing native approval bindings and
missing Copilot/Cursor/hook artifacts remain unchanged.

### Register disposition truth table — 2026-10-04

Evidence detail requirements apply independently across all four capabilities.
Any supported or partial disposition requires nonempty valid verified field
meanings; any partial or unverified disposition requires nonempty valid unresolved
requirements. Entirely unavailable profiles may leave both empty. Fully resolved
supported profiles may leave requirements empty, retaining verified meanings and
all existing independently reviewed native approval bindings. This corrects the
partial-only guard above; loading and matrix rendering enforce the same validator.
Malformed containers, keys or entries remain invalid even when details are optional.
This is register completeness validation, not proof that contributor review claims
are authentic or that missing native sources are supported.

### Existing input boundary corrections — 2026-10-04

UTC normalization can overflow even after timezone-aware parsing succeeds near
years1and9999. These endpoints leave cumulative intervals unresolved, preserving
representable timestamps, Decimal precedence and reset/conflict behavior. Wrong
nested record containers use fixed case-shape/case-invalid diagnostics rather than
tracebacks; repaired originals and deliberately missing evidence retain their
existing conclusions. This does not introduce a new record schema.

CSV parsing temporarily uses the existing10MiB byte bound as its field-size limit,
then restores the previous process limit on success or failure. Valid wide headers,
UTF8cells and quoted multiline cells within the received byte bound are accepted;
the default Python131,072field limit is not a separate supported-export policy.
Existing total-byte, record-count, width, duplicate-header and private diagnostic
guards remain. This development-only inspector processes inputs serially; the
parser wrapper does not enable collection or native-profile support.

### Hosted research bundle obligation — 2026-10-04

The hosted strategy must compute `checkpoint_conflict` as exactly false for a
research bundle to pass. A known conflict or unresolved checkpoint identity/amount
uses the fixed conclusion-mismatch diagnostic even when that output was absent
from historical fixture expectations. This is an independent strategy obligation;
the immutable original fixture bytes and declared answers remain unchanged. Exact
replay, distinct identified progression and explicitly synthetic separate SDK
namespaces stay conflict-free; a known conflict retains precedence over incomplete
records. Finality remains unknown, totals remain non-additive and source approval
remains false. This research-case obligation establishes no new native policy.

### Fixture expectation shape

Research fixture expectations must be mappings before key coverage or value iteration. Lists (even all required names), strings, scalars and null reject with `case-invalid`; valid mappings retain exact key coverage and value type checks. This fixture metadata guard does not change source conclusions or native approvals.

### Evidence scope notes

Every existing evidence origin requires a nonblank string `scope` note describing provenance or coverage. Unknown completeness is a valid note, not verified native authority. Missing or malformed notes reject even with newly bound approvals. Profile digests already cover scope changes: changing a valid note requires rebinding the reviewed profile. Structural reports and public diagnostics expose opaque references, never scope text.

### Multiplier cardinality and metadata precedence

The multiplier-only research strategy observes one record and rejects any additional row, including replay or missing/conflicting/malformed multiplier values in either order. Other multi-span strategies retain their existing behavior; no consensus, averaging or cash conversion is inferred. Fixture expectation mapping shape and exact key coverage precede detector evaluation: compound structural faults remain `case-invalid`, and wrong keys remain `oracle-coverage`. Valid mappings still require exact conclusion types and the independent hosted checkpoint obligation.

### Citation destination structure

Reference URLs must be strings parsed with HTTPS scheme and a nonblank hostname. Hostless paths/queries/fragments, malformed brackets, nonstrings and other schemes reject safely in register/loader/matrix validation. Kind/access-date checks and exact profile approval binding remain required. This is syntax validation only: no DNS, reachability, provider authority or domain allowlist is inferred.

### Canonical research byte provenance

The default checker requires the existing twelve canonical profile/evidence aliases to retain synthetic origin and agree on one SHA-256. It reads bounded fixture bytes once, checks their hash before parsing and parses those same bytes; any reserialization, changed records/answers or missing/stale/conflicting alias rejects through fixed safe diagnostics. Matching any unrelated evidence hash is insufficient. Original fixture bytes and registered references remain unchanged. `check_cases(bundle)` is an explicit in-memory semantic API with no file-provenance claim; matrix-only mode validates the register without reading the fixture. No native approval is inferred.
