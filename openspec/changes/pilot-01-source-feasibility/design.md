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

The selected completion rule requires verified intended Copilot/Cursor profiles.
Missing exports/finality or custom-hook input/output leave tasks and #9 open;
complete tooling and documents may be delivered while those evidence gates remain
blocked. Reopen #9/Todo for preparation and use In Progress during implementation.
Preserve historical PR #21 acceptance and native parent/dependency relationships.
