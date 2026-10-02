# Design: Import native Copilot IDE and CLI evidence

## Context

See [proposal](proposal.md) and [capability spec](specs/copilot-import/spec.md).
The current repository contains documentation and hygiene gates, with no product
package or runtime. This design describes later implementation, not delivered behavior.

## Goals / Non-Goals

**Goals:** Make the specified capability local, reproducible and explicit about missing evidence.

**Non-Goals:** No SDK wrapper requirement, telemetry collector, automatic environment/IDE configuration, prompt storage, account API scraping, or dollars inferred from multipliers.

## Decisions

1. Use local file inputs to settle, with an explicit provider/surface profile, not a new import command family. CLI candidate configuration is COPILOT_OTEL_FILE_EXPORTER_PATH; describe optional manual setup only after feasibility confirms the installed version. No setting is changed by ChangeCost.

2. Keep IDE and CLI source profiles distinct. Feasibility must verify actual file shape, event keys, session/trace relationships and repeated attributes for each supported version. A resource window session is not automatically a change run. Unsupported profiles fail clearly before persistence.

3. For the documented CLI profile, root invoke_agent carries github.copilot.nano_aiu; corresponding child chat spans repeat that billing amount and must not add it again. github.copilot.cost is a multiplier, not cash. Preserve nano_aiu as a distinct unit and any cumulative source as a separate lane. Only verified semantics permit a transform, with provenance retained.

4. Normalize allowlisted identifiers, times, model and economic fields only. Strip content fields before persistence or logging, including unexpected nested payloads. Provider-backed joins require verified stable identities and explicit run binding; manual maps use a different provenance method and ambiguous records remain unbound.

5. Reject malformed files atomically with record location and safe diagnostics. Process bounded input sizes with explicit limits. No network is needed. An unavailable IDE format remains documented unsupported even if the CLI profile is implemented.

## Dependencies and evidence

- [pilot-01-source-feasibility](../pilot-01-source-feasibility/proposal.md)
- [settlement-01-reconciliation](../archive/2026-10-02-settlement-01-reconciliation/proposal.md)

Shared boundaries and current provider evidence are recorded in the
[source assessment](../../../docs/research/pilot-source-assessment.md).
No provider-specific mapping becomes supported merely by appearing in this plan.

## Risks / Trade-offs

- Repeated billing attributes → fixture-tested authoritative root selection.
- Session ambiguity → verified joins or manual/unbound status.
- Content leakage → allowlist normalization and negative log/storage tests.

## Migration Plan

After separate implementation authorization, land this change in dependency order
with spec-derived failing and passing evidence. Update docs/providers/copilot.md, docs/providers/source-feasibility.md, and docs/cli.md.
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
