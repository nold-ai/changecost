# Design: Verify personal-account source feasibility

## Context

See [proposal](proposal.md) and [capability spec](specs/source-feasibility/spec.md).
The current repository contains documentation and hygiene gates, with no product
package or runtime. This design describes later implementation, not delivered behavior.

## Goals / Non-Goals

**Goals:** Make the specified capability local, reproducible and explicit about missing evidence.

**Non-Goals:** No account changes, paid plans, live collection in this planning delivery, Enterprise collector, undocumented scraping, or adapter implementation.

## Decisions

1. Use a documentation-and-fixture evidence gate, not assumptions from the research report. For each source record product/version, account tier, acquisition steps, format/version, sample provenance, identifiers, units, repeated/cumulative fields, corrections and retention risks. An unavailable capability is a valid finding, not a successful reconciliation.

2. Inspect only maintainer-provided, locally held exports after collection is separately authorized. Publish synthetic equivalents and a redaction manifest; never commit original exports. The manifest must preserve cardinality and join relationships while replacing IDs and removing content.

3. Copilot CLI local JSON-lines is a candidate source; IDE formats need independent confirmation. Cursor Enterprise OTel is excluded. The dated self-serve export report motivates a tokens-only fallback. Source-specific field mappings remain blocked until inspected evidence supports them.

4. Gate outcomes are per capability, not one provider-wide boolean. A source may permit usage import but not automatic attribution or cash settlement. A completely unavailable source blocks that adapter implementation until scope is explicitly revised; do not fabricate an empty adapter to close its story.

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

After separate implementation authorization, land this change in dependency order
with spec-derived failing and passing evidence. Update docs/providers/source-feasibility.md, docs/providers/fixtures.md, and docs/research/pilot-source-assessment.md.
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
