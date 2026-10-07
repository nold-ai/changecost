# Import existing local Codex coding-session metadata

## Why

Ordinary local Codex coding sessions contain candidate usage evidence without
Enterprise exports. Safe local learning requires verified version-specific identity
and accounting rather than assumptions from file presence.

## What Changes

- Accept explicitly selected existing local coding-session files under independently approved source profiles.
- Normalize allowlisted usage/model/identity/interval metadata with versioned deduplication, correction and ownership policy.
- Bind evidence manually to existing Changes/Runs; expose incomplete, unsupported and conflicting observations.
- Keep demand eligibility and billed settlement authority separate.

## Capabilities

### New Capabilities

- `codex-local-import`: Offline approved Codex local coding metadata import.

### Modified Capabilities

None; native accounting policies must be prepared explicitly and do not grant
financial authority merely by importing records.

## Impact

Future reader/normalization and source-specific policy tests, using the existing
settle file workflow and core store. Documentation: provider feasibility, the
Codex/Claude metrics guide, CLI/settlement and [forecasting](../../../docs/forecasting.md).
This delivery adds plans only, no runtime reader or collection.

## Non-goals

No automatic scanning/watch service, ordinary chat import, account settings,
new telemetry, provider API, paid model request, prompt retention or inferred subscription charges.

## Dependencies

[Source feasibility #9](../pilot-01-source-feasibility/proposal.md) and delivered
[reconciliation #12](../archive/2026-10-02-settlement-01-reconciliation/proposal.md).
Demand use additionally requires its own policy under
[adaptive demand](../forecast-01-local-adaptive-demand/proposal.md); that feature
does not depend on this reader for its offline/synthetic implementation.
Reader delivery/archive depends on #9/#12 and its approved source policy, not #35.
Adaptive-demand integration is conditional on #35 delivery and a separately
approved demand policy; otherwise it is recorded as deferred follow-up.

## Risks and rollback

Duplicate/corrected counters, partial lineage and private content -> approved
accounting policy, safe allowlists and conservative gaps. Scoped revert preserves
originals and imported history; any later migration needs backup/recovery tests.

## Source Tracking

Planning approved 2026-10-07; native User Story under Attribution and settlement
#7 / Epic #4. GitHub issue: [#36](https://github.com/nold-ai/changecost/issues/36). Todo, unassigned,
undated; the user requested publication of these plans in a planning-only PR.
Implementation remains unstarted.

Native type/parent/dependencies/private-project Todo read back on 2026-10-07.
