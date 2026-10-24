# Forecast task demand from local evidence and explicit transfer hypotheses

## Why

The delivered economic Quote cannot forecast native token demand and a new model or
harness has no demonstrated relationship to earlier consumption. Developers need a
useful zero-knowledge assessment that learns from actual work without presenting
assumptions as calibrated cost predictions.

## What Changes

- Add a separate local demand forecast with zero_knowledge, learning,
  transfer_hypothesis and validated_forecast evidence states.
- Freeze multidimensional task and ecosystem snapshots, then learn from eligible
  bound outcomes with immutable cutoffs and versioned measurement policies.
- Test transfer using matched ecosystem comparisons; prefer applicable target
  evidence and expose confounding, residuals and missing measurements.
- Add an explicit demand mode to quote and explanatory support in explain.
- Accept optional user-invoked rehearsal assessments and explicit estimated-price
  scenarios without converting them into measured outcomes or billed money.

## Capabilities

### New Capabilities

- `adaptive-demand`: Local demand assessment, learning and auditable transfer.

### Modified Capabilities

None. Existing economic Quote, Features/v1, settlement and advisory requirements
remain intact; additive demand contracts do not mint their authority.

## Impact

Offline implementation was authorized on 2026-10-11 and is locally implemented
on the feature branch, with acceptance pending. It extends models, portable records,
quote/explain and deterministic learning/transfer while reusing SQLite layout 2.
Native readers and measured pilot evaluation remain separate. Documentation: docs/forecasting.md and the
CLI/contracts guides. See [design](design.md), [requirements](specs/adaptive-demand/spec.md)
and [change order](../../../CHANGE_ORDER.md).

## Non-goals

No paid probes, automatic LLM invocation, provider collection, automatic account
configuration, global service, ML platform, employee ranking, prompts/transcripts,
guaranteed accuracy, invented model multipliers or billed charges from list prices.

## Dependencies

Delivered core-02 #11, settlement #12, Quote #15 and advisory #16 are the core
prerequisites. Source feasibility #9 and an approved reader/policy are prerequisites
for that source's native learning lane, not for zero-knowledge or synthetic behavior.
One unavailable provider does not block other approved lanes.

## Decisions and uncertainty

Local-first and the four evidence states are maintainer-approved on 2026-10-07.
Analogy, transfer and rehearsal improving unseen-task accuracy remain hypotheses.
Policies must be registered before evaluating outcomes. See
[research](../../../../docs/research/adaptive-demand-evidence.md).

## Risks and rollback

Confounded transfer, duplicate accounting and future-information leakage require
matched comparisons, independent accounting approval and cutoff-bound replay.
Rollback planning by scoped revert; future migrations must preserve old records,
export/backup and tested recovery. No release or version bump is planned.

## Source Tracking

Planning approved 2026-10-07; native User Story under Quotes and developer workflow
#8 / Epic #4. GitHub issue: [#35](https://github.com/nold-ai/changecost/issues/35).
Preparation was published in merged PR #38. Offline implementation was authorized
on 2026-10-11 and is local; verification and acceptance remain pending.
The 2026-10-07 project assignment/date snapshot below is historical.

Native type/parent/dependencies/private-project Todo read back on 2026-10-07.
