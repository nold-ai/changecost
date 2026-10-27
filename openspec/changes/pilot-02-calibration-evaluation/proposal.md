# Evaluate attribution and chronological quote calibration

## Why

The pilot must test whether local task dimensions, ecosystem comparisons and optional rehearsal improve forecasts over simple historical baselines, including zero knowledge and changed ecosystems. Missing capabilities and small samples remain visible.

## What Changes

- Deliver a deterministic offline report from portable synthetic history and a pre-registered protocol, reusing existing quote replay and demand validation.
- Define a reproducible chronological evaluation protocol and repository-wide baseline, with matched availability and one initial quote per change.
- Report attribution, calibration, quote width, abandoned expenditure and runtime/storage overhead.
- Publish aggregate findings and limitations using safe fixtures; classify unsupported or insufficient evidence explicitly.
- Require full-change truth coverage and freeze truth revisions/cutoff separately from quote-time evidence.

## Capabilities

### New Capabilities

- `pilot-evaluation`: Evaluate attribution and chronological quote calibration.

### Modified Capabilities

None; delivered main capabilities are preserved. New additive requirements are defined in this change; source/policy approval remains separate.

## Impact

The separately authorized offline implementation adds `evaluate-synthetic` to the
standalone Python CLI and a public evaluation API using disposable local stores.
Documentation: docs/pilot/evaluation.md, docs/pilot/findings.md, and docs/providers/source-feasibility.md.
Verification: the scenarios in [the capability spec](specs/pilot-evaluation/spec.md),
strict OpenSpec validation, applicable quality gates and truthful review evidence.
The evaluator, input models, metric helpers, synthetic fixtures and tests are
implemented locally pending complete verification and PR publication. No new
runtime dependencies, normal-store migration or live collection are introduced.

## Non-goals

No fabricated live measurements, collection during planning, product launch claim, employee ranking, opaque ML training, enforcement threshold or paid infrastructure. Deterministic analogy/transfer and optional supplied rehearsal assessments are in scope.

## Dependencies

- [forecast-01-local-adaptive-demand](../archive/2026-10-23-forecast-01-local-adaptive-demand/proposal.md)
- Delivered core-02 #11 and reconciliation #12.
- Approved readers #13/#14 and Codex/Claude are prerequisites only for their respective native evaluation lanes, not universal gates.
- [quote-01-empirical-estimation](../archive/2026-10-04-quote-01-empirical-estimation/proposal.md)
- [workflow-01-advisory-ci](../archive/2026-10-06-workflow-01-advisory-ci/proposal.md)

Dependencies are implementation prerequisites; planning can proceed together.
See [change order](../../CHANGE_ORDER.md) and [source assessment](../../../docs/research/pilot-source-assessment.md).

## Decisions and uncertainty

The Python/local-first scope is confirmed. Provider access and prediction quality
remain To-Validate. See [design](design.md) for decisions and evidence gates.

## Risks and rollback

- Selection bias → report unpriced and unbound cases with full denominators.
- Leakage → chronological revision-aware replay for both methods.
- Small or unavailable evidence → uncertainty and not-yet-validated conclusion, never invented measurements.

Planning rollback: revert the planning commit and close linked tracking items if
abandoned, preserving history. Later runtime rollback must preserve portable
evidence and prior local database versions; do not erase financial history.

## Source Tracking

<!-- tracking:start -->
- GitHub issue: [#17](https://github.com/nold-ai/changecost/issues/17) (native type: User Story).
- Parent feature: [#5](https://github.com/nold-ai/changecost/issues/5) — Pilot evidence.
- Parent epic: [#4](https://github.com/nold-ai/changecost/issues/4) — ChangeCost — validate change-level cost estimation and settlement.
- Project: [ChangeCost](https://github.com/orgs/nold-ai/projects/3) — private, status Todo.
- Source: maintainer-approved pilot plan, 2026-09-28 (Europe/Berlin).
- Tracking verified: 2026-09-28; implementation is unstarted, unassigned and undated.
- Preparation refreshed: 2026-10-26 (Europe/Berlin), against `ffd8dff568f11e6e9283b00badbce6c98a0b5580`. Issue #17 remains User Story under #5 in private Project 3, Todo. Native blockers #11, #12, #15, #16 and #35 are closed.
- Preparation disposition on 2026-10-26: locally prepared and unpublished; preparation alone authorized no runtime.
- Subsequent runtime authorization on 2026-10-26: offline implementation, verification and PR promotion. As of 2026-10-27 the synthetic CLI/API is implemented locally pending complete verification and publication. Live assessment, provider approval, calibration claims and merge remain outside authorization.
<!-- tracking:end -->
