# Design: Verify personal-account source feasibility

## Context

See [proposal](proposal.md) and [capability spec](specs/source-feasibility/spec.md).
The Python foundation, contracts, normalized settlement and empirical Quotes are
delivered in PRs #22/#25/#28/#32. Source-feasibility closeout was authorized on
2026-10-03; provider support remains unverified until native evidence is inspected. See the [assessment](../../../docs/providers/source-feasibility.md).

## Goals / Non-Goals

**Goals:** Make the specified capability local, reproducible and explicit about missing evidence.

**Non-Goals:** No account changes, paid plans, live collection in this planning delivery, Enterprise collector, undocumented scraping, or adapter implementation.

## Decisions

1. Use a documentation-and-fixture evidence gate, not assumptions from the research report. For each source record product/version, account tier, acquisition steps, format/version, sample provenance, identifiers, units, repeated/cumulative fields, corrections and retention risks. An unavailable capability is a valid finding, not a successful reconciliation.

2. Inspect maintainer-provided sanitized exports or explicitly authorized metadata
   projections from existing local artifacts. Starting new collection requires
   separate authorization. Publish synthetic equivalents and a redaction manifest;
   never commit original exports. Preserve cardinality and join relationships while
   replacing IDs/quantities and excluding content. The maintainer authorized local
   Codex/Claude artifact inspection and one Cursor Basic session inspection on
   2026-09-28, then a VS Code hosted Copilot session. Preserve its explicit host/SDK
   identity link, turn-versus-session counters and ephemeral-versus-durable events.
   Cursor local context occupancy is not consumed-token evidence;
   internal store inspection does not authorize an undocumented runtime adapter.

3. Copilot CLI local JSON-lines is a candidate source; IDE formats need independent confirmation. Cursor Enterprise OTel is excluded. Conflicting dated Cursor export reports require inspecting both token fields and any cost-like columns; do not assume cash is always absent. Source-specific field mappings remain blocked until inspected evidence supports them.

4. Gate outcomes are per capability, not one provider-wide boolean. A source may permit usage import but not automatic attribution or cash settlement. A completely unavailable source blocks that adapter implementation until scope is explicitly revised; do not fabricate an empty adapter to close its story.

5. The maintainer added Codex and Claude Code metrics research on 2026-09-28.
   Assess CLI and IDE/app entrypoints separately, preserving usage snapshots,
   counter temporality and estimate-versus-billed distinctions. Local CLI help and
   generated protocol schemas establish interfaces, not observed account support.
   Inspect only authorized metadata projections, excluding transcript content;
   do not start collection. Future adapters are separate scope.

6. Compare the supplied Enterprise projections as separate evidence profiles.
   Preserve original artifact bytes and distinguish native fields from transformed
   clocks, synthetic quantities, withheld values and uninspected containers. Neither
   an Enterprise tier nor a schema inventory certifies an OTel or billing source.
   Work OTel is reported disabled; inspect the reported session-log parser and custom upload
   separately, preserving native fields versus converted/derived labels, units and
   joins. No Admin API is called per the latest clarification; mapping is uninspected.
   V2 message-counter paths support partial field evidence only. Check synthetic
   arithmetic separately from encoding fidelity and preserve received discrepancies;
   normalized keys, invented CSV headers and joins cannot approve native adapters.

## Dependencies and evidence

None.

Shared boundaries and current provider evidence are recorded in the
[source assessment](../../../docs/research/pilot-source-assessment.md).
No provider-specific mapping becomes supported merely by appearing in this plan.

## Risks / Trade-offs

- Provider access changes → date/version every observation and recheck before implementation.
- Redaction destroys join evidence → retain synthetic relationships and review the manifest.
- Unavailable exports → narrow documented support; leave dependent implementation blocked where no feasible path exists.

## Migration Plan

Land the authorized research with scenario-by-scenario evidence review, then finish
personal-source inspection when sanitized exports are available. Research-only work
does not invent runtime TDD. Update docs/providers/source-feasibility.md,
docs/providers/fixtures.md, docs/providers/codex-claude-metrics.md,
docs/providers/cursor-local-metrics.md, docs/providers/copilot-local-metrics.md and
docs/research/pilot-source-assessment.md.
Use synthetic fixtures before any authorized real-data evaluation. This is unreleased;
there is no deployed service to migrate. For local schema changes, export/backup
before migration and validate recovery without deleting the previous data.

Rollback the implementation commit if its checks fail; restore a compatible local
backup rather than forcing an older program to write a newer database. Planning
rollback is a commit revert plus closing the associated issue, preserving history.

## Verification

Each requirement has Given/When/Then scenarios. Exercise negative paths and privacy
boundaries alongside the success cases. Run strict OpenSpec validation and applicable
repository gates; record actual results, not anticipated test or review outcomes.

## Authorized closeout — 2026-10-03 (Europe/Berlin)

Maintain one versioned profile register at `docs/providers/source-profiles.json`.
Each profile names its provider/surface, version/tier, acquisition route, primary
citations/access dates, opaque evidence references/hashes, per-capability disposition,
field semantics and specific unresolved requirements. Derived compact Markdown is
checked against this register; specialist reports preserve dated interpretation.

Add development-only `quality.source_feasibility` tooling and independent semantic
case evaluation under the existing pytest suite. Use existing dependencies only.
The command validates the register/fixture bundle and accepts an optional ignored
local evidence manifest with explicit profile, format, file, SHA-256, provenance
and allowlisted field paths. JSON/JSONL/CSV reads are bounded to 10 MiB/file,
10,000 records and depth 32; invalid UTF-8, duplicate members/headers, symlinks,
unknown profiles/formats and non-finite values fail with safe location-only codes.
Reports retain opaque evidence IDs, hashes, counts and value types, not payloads,
identifiers, raw paths, column names, arbitrary field names or exception text.
Inspection cannot establish semantic finality or automatically approve a profile.

Historical synthetic case inputs are evaluated independently from declared expected
results. Preserve exact Decimal arithmetic and separate unknown/zero, economic
units, cumulative/replacement evidence and identity scopes. Detector controls
mutate inputs or expected claims and must fail before passing when repaired.

Registry approvals require independently reviewed native evidence for the named
capability. Synthetic, reported, documentation-only and historical partial evidence
cannot supply approval. Even a valid native shape/manifest is only structural
evidence; the named human review must confirm version, authority, accounting
interval, replay/reset/correction semantics and declared exclusions. No provider
policy, adapter, public command, portable schema or database migration is added.

Historical 2026-10-03 completion rule (superseded on 2026-10-07): required verified intended Copilot/Cursor profiles.
Missing exports/finality or custom-hook input/output leave tasks and #9 open;
complete tooling and documents may be delivered while those evidence gates remain
blocked. Reopen #9/Todo for preparation and use In Progress during implementation.
Preserve historical PR #21 acceptance and native parent/dependency relationships.

## Preparation decisions — 2026-10-06 (Europe/Berlin)

PR #33 delivered the register, bounded inspector and all 18 research controls;
PR #34 delivered advisory behavior. This preparation changes planning and evidence
documentation only. Intended native profiles still need inspection and independent
semantic approval. All 14 profiles have zero approvals. Preserve completed work,
retained failures and the current completion criterion; documentation is not a sample.

### Acquisition and accounting decisions

Keep Copilot CLI OTel, Local IDE OTel, hosted SDK logs, personal Cursor CSV and
Enterprise/custom-hook projections as separate source/version/harness profiles.
Prefer existing authorized JSON/JSONL/CSV input supported by the bounded inspector.
VS Code also documents SQLite trace export: that is an acquisition candidate, not
a supported inspector format. If only a database exists, resolve an explicit
offline projection/support decision before extending tooling. A transformed
derivative is not native wire evidence. Do not enable collection to fill a gap.

| Decision | Required native evidence | Default while evidence is missing |
| --- | --- | --- |
| Authoritative Copilot quantity | Root/child/subagent identities and inclusion boundaries; durable checkpoints versus invocation data in the same interval. | Keep overlapping lanes separate. Do not add roots, children and cumulative checkpoints. Nano-AIU, multipliers, tokens and currency stay distinct. |
| Replay, corrections and finality | Stable record/revision identity, resume/replay examples, interval/timezone, reset/corrections, cache categories and terminal coverage. | Retain partial/unverified status. Completion flags or absent events do not prove a complete ledger. |
| Provider-to-change attribution | Exact namespaces/session joins and explicit binding, including manual provenance and ambiguous/unbound records. | No provider-authoritative join inferred from time proximity, repository labels or IDE windows. |
| Cursor economics | Actual personal CSV headers/rows, tier/export version/range, included/on-demand/pool meanings, quantity units, stable row identity and corrections. | Displayed dollars and included usage are not automatically billed cash. No conversion from quota percentages or list prices. |
| Hook transformation | Sanitized mapping code or paired native input/upload; receiver changes inspected separately, including retry/correction/classifier provenance. | Keep native, converted and receiver claims separate. Disabled work OTel stays disabled. |

Historical 2026-10-06 disposition: native evidence determined approval and this
preparation retained intended profiles/dependencies. The explicit 2026-10-07 scope
revision below supersedes that universal closeout condition. Codex/Claude reader
plans are now authorized planning only; runtime adapters remain unimplemented.

### Source approval and runtime authority

The contributor attestation binds profile digest, capability, native evidence hash
and named semantic review. It does not authenticate the reviewer, mint a computation
receipt or change runtime policy. Normalized imports already persist provider-shaped
economic records, while trusted coverage, settlement, Quote replay and advisory
reproduction authorize synthetic fixture billed-USD accounting only. A supported
register cell cannot make provider results complete, priced or eligible for advice.

Later #13/#14 preparation must explicitly map supported versioned source/component
and economic semantics into an accounting/coverage policy and bind its version to
historical settlement, Quote and advisory replay. Reuse current contracts where
they suffice; this preparation introduces no plugin framework, public command,
schema migration or runtime policy extension.

### Acceptance and recovery

Refresh citations without replacing historical observations, original evidence or
canonical fixture bytes. Verify register/matrix consistency, all 18 cases, links
and applicable quality gates. Keep #9 Open/In Progress with zero approvals and exact
native evidence requests; #13/#14 retain blocked-by #9/#12. Remain locally unpublished
pending the reviewed-diff PR/stash choice. A missing earlier local review receipt
requires recovery, not a new correction allowance.

Confidence is high in code boundaries and medium in provider feasibility. Duplicate
accounting, premature approval and unsupported numeric authority are mitigated by
separate lanes, semantic attestations and later policy-specific replay. No paid
infrastructure is needed; native artifact availability controls timing. Rollback
reverts the scoped planning diff and restores issue text from readback while
preserving source originals, archives and review history.

## Current decisions — capability closeout, 2026-10-07

1. Assess accessible regular local metadata without requiring new exports,
   Enterprise plans, administrator data or collection. Record unsupported/partial/
   unverified capabilities and bounded acquisition evidence. Custom hooks and
   optional OTel/CSV profiles remain separate unresolved lanes, not universal gates.
2. A reviewed capability inventory with exact gaps can complete feasibility; it
   cannot approve a missing mapping. The current 14-profile register has zero native
   approvals. New observed Codex/Claude producer versions need separate profile
   reconciliation; do not relabel old evidence or infer support from installed apps.
3. Native source semantics, demand-measurement eligibility and full billed-money
   authority are independent. Preserve exact profile/capability/evidence/reviewer
   attestations and policy-specific replay. This change creates no runtime policy.
4. Existing local session JSON/JSONL is a candidate acquisition route. SQLite
   databases require an explicitly reviewed read-only snapshot/projection policy,
   including live-file/WAL limits; no write-capable open, checkpoint or bypass.
5. Codex request records overlap legacy snapshots; Claude repeated/revised usage
   overlaps result streams; Copilot root/direct/checkpoint/session totals can overlap.
   Cursor empty counters/context occupancy cannot provide measured token outcomes.
   Preserve identities, representations, cache categories, reset/correction/finality
   and root/subagent gaps. Explicit manual Run/Change binding stays the default.
6. Dated metadata-only discovery findings are incorporated without native approvals;
   original private source pointers/hashes remain ignored. Public summaries exclude
   prompts, paths, identifiers and actual account quantities. See the
   [research evidence](../../../docs/research/adaptive-demand-evidence.md).

Task/source-feasibility scope is current; prior acceptance/failures remain history.
Close/archive still requires separately reviewed actual reconciliation and applicable
delivery checks. This planning update does not close #9 or imply adapter readiness.


## Publication disposition — 2026-10-07 (Europe/Berlin)

The maintainer superseded local-only retention with the published planning-only
[PR #38](https://github.com/nold-ai/changecost/pull/38). Both scoped stashes remain
recovery points. Earlier dated local/unpublished statements describe their
historical preparation state; this is the current delivery disposition.
Publication does not imply merge, implementation completion or native approval.
Recorded review limits and all 14 source profiles with zero approvals remain
unchanged.


## Merged planning checkpoint — 2026-10-07 (Europe/Berlin)

Planning [PR #38](https://github.com/nold-ai/changecost/pull/38) merged at
21:25:35 Europe/Berlin, commit `dc26715d2b583a31050c1cf7fda8ed0e9a9d5507`,
reviewed head `b6a03b38d160cf784ef8f8735ce3384164980f84`.
Both Python 3.11.15/3.13.14 jobs passed in
[Linux run 37670722956](https://github.com/nold-ai/changecost/actions/runs/37670722956).
These are actual PR #38 delivery checks, not verification of this later diff or
native semantic approval. Earlier publication/local-stash statements remain dated
history; neither recovery stash is reapplied.

## Profile reconciliation decisions — 2026-10-07

- Preserve the 14 historical profiles byte-for-byte as JSON objects; add nine
  separate observation/representation profiles and refresh only the current
  assessment date. All 23 profiles retain zero approvals.
- Bind Codex 0.159.0-alpha.12.1 request/snapshot inputs separately from 0.158
  histories. Bind the newly selected Claude 2.1.275 project inputs separately from
  the earlier observation; repeated usage has changed within message groups.
- Scope Claude Desktop 2.1.221/234 profiles to exact-version rows in the same
  mixed-version native input. Keep the SDK/result stream with mixed system-header versions separate;
  per-result version association remains unverified.
  The 2.1.202/205 header inventory has documentation provenance only; no other
  version's hash or monitoring fix grants its accounting semantics.
- Bind the Copilot hosted checkpoint/shutdown observation separately. Equal
  checkpoint/shutdown amounts do not establish full coverage; disagreeing host
  session totals remain unresolved and host SQLite comparisons are non-atomic.
- Record Cursor Free separately from historical Basic. Its native digest binds
  selected stored-row bytes, not a whole DB/WAL snapshot. Usage remains unverified:
  empty objects, zero placeholders and context occupancy are not consumed tokens.
- Support is still conditional on independently reviewed native authority, interval,
  identity, replay/reset/correction, cache inclusion, ownership and finality.
  No sum-all, first/last, largest-value or cross-version aggregation is selected.

The original source review-session receipt remains missing after checking known
checkouts, temporary worktrees and immutable stash trees; partial original
execution records are preserved locally. The maintainer authorized a separate
fresh review for this post-merge reconciliation in session
`pilot-01-source-feasibility-reconcile-20261007`. It neither reconstructs old
counters nor certifies the earlier review. Historical receipt recovery does not
block this new scope; current review, applicable Linux assurance and delivery
acceptance remain required for publication and closeout.

### Contributor gate performance repair — 2026-10-08

The maintainer requested repair of PR #39's native full-suite timeout. The first
test-arrangement optimization passed full native assurance on Python 3.11, while
Python 3.13 still timed out. The same signed native interpreter/dependency versions
and reversed matrix pattern do not identify a host-version defect. Independent
review found avoidable repeated Git acquisition within contributor input capture.

Use one NUL-delimited tagged `git ls-files` result for index flags, stage records
and visible untracked inventory. Distinguish untracked tags before parsing filenames,
strip only tracked tag prefixes and retain stage order/terminal NUL so existing
schema-8 fingerprints remain byte-identical. Reject hidden flags globally, including
undeclared entries. Keep HEAD/status verification, ignored/absent declarations and
both initialization/refresh captures. This consistent index observation does not
make the entire working-tree capture atomic. Real Git parity/race tests and fresh
full native assurance are mandatory; no vendor deadline or product API changes.
