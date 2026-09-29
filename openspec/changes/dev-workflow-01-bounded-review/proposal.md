# Proposal

## Why

Small changes can enter expensive, self-expanding review loops when each new
finding is fixed in isolation and prior evidence disappears from the active
context. The first Python foundation exposed this risk in practice.

## What Changes

- Add a local, versioned review-session record with explicit scope, budgets,
  findings, review evidence and compact handoff output.
- Add deterministic status decisions for review batches, repeated finding
  families, scope expansion, incomplete evidence and no-progress waits.
- Add read-only GitHub review monitoring and documented pre-PR Linux preflight.
- Update all four ChangeCost workflow skills to use the shared review contract.
- Calibrate, but do not yet require, an available cross-family local reviewer.

## Capabilities

### New Capabilities

- `bounded-review-session`: Persisted contributor-workflow decisions that bound
  a review/fix session while retaining its evidence and context.

### Modified Capabilities

- None.

## Impact

Changes development-only `quality/` tooling, workflow skills and their
documentation. No package runtime dependency, provider integration, hosted
service, deployment, or branch-protection policy is added.

Tracking: [#23](https://github.com/nold-ai/changecost/issues/23) is a User Story
under Feature [#6](https://github.com/nold-ai/changecost/issues/6), in the
ChangeCost project with status Todo.

## Non-goals

This does not authenticate PR-controlled code, intercept arbitrary model calls,
guarantee lower token cost, or make a calibrated reviewer mandatory.
