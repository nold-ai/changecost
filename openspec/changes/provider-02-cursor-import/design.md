# Design: Import accessible personal Cursor usage exports

## Context

See [proposal](proposal.md) and [capability spec](specs/cursor-import/spec.md).
The current repository contains documentation and hygiene gates, with no product
package or runtime. This design describes later implementation, not delivered behavior.

## Goals / Non-Goals

**Goals:** Make the specified capability local, reproducible and explicit about missing evidence.

**Non-Goals:** No Enterprise OTel collector, Admin API dependency, undocumented editor database scraping, synthetic invoice pricing, or promised automatic session attribution.

## Decisions

1. Start from inspected personal-account CSV headers and sanitized rows. Do not hard-code Enterprise wire attributes into the personal format. The dated support report of tokens-only exports is a constraint to test, not proof of the exact current user schema. Each accepted profile has a documented version/header signature.

2. Preserve input/output/cache token categories as separate units when available. If money is absent, monetary components are unknown; do not substitute subscription price or model list prices. Any actual monetary field needs verified currency and billing basis before it is aggregated.

3. Use verified stable source event IDs where present. Otherwise exact-file hash plus row index makes repeated identical files idempotent only; overlapping exports remain a documented ambiguity and cannot silently double-count or assume identical rows are one event. Reject ambiguous overlap from final reconciliation pending explicit evidence.

4. Use the [core evidence references and mappings](../core-02-change-run-contracts/design.md)
   for manual attribution. First import the row as unbound and expose its evidence_id;
   bind then maps that exact reference to an existing run, which is explicitly bound
   to a change. A portable artifact may import evidence and its mapping atomically.
   Export/replay retains file-scoped identity and manual provenance; a conflicting
   mapping fails. Timestamp proximity alone never creates a provider-backed join.
   No run/session ID means unbound by default.

5. Import locally, validate the whole file before commit, and allowlist fields. Never retain email, prompt text, raw account identity or arbitrary CSV columns. Preserve safe diagnostics and leave originals under user control.

## Dependencies and evidence

- [pilot-01-source-feasibility](../pilot-01-source-feasibility/proposal.md)
- [settlement-01-reconciliation](../settlement-01-reconciliation/proposal.md)

Shared boundaries and current provider evidence are recorded in the
[source assessment](../../../docs/research/pilot-source-assessment.md).
No provider-specific mapping becomes supported merely by appearing in this plan.

## Risks / Trade-offs

- Personal export changes → explicit profile signature and dated feasibility evidence.
- Overlapping rows lack identity → disclose incomplete dedupe and block false final totals.
- Tokens mistaken for cash → separate units and unknown monetary components.

## Migration Plan

After separate implementation authorization, land this change in dependency order
with spec-derived failing and passing evidence. Update docs/providers/cursor.md, docs/providers/source-feasibility.md, and docs/cli.md.
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
