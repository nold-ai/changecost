# Design: Verify personal-account source feasibility

## Context

See [proposal](proposal.md) and [capability spec](specs/source-feasibility/spec.md).
The current repository contains documentation and hygiene gates, with no product
package or runtime. Research implementation is authorized; observed provider support
remains unverified. See the [assessment](../../../docs/providers/source-feasibility.md).

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
