# Optional runtime diagnostic applicability

## Why

PR #50's documentation-only checks passed, but CI failed when the diagnostic
collector tried to read a native report that the dispatcher correctly did not
produce. The maintainer separately authorized the scoped CI repair in PR #50.

## What Changes

Collect runtime metadata only when the native report exists, including after a
failed review. Preserve mandatory review failure and malformed-report errors.

## Capabilities

- `python-foundation`: clarify optional diagnostic applicability alongside the
  existing consistent local and CI gate contract.

## Impact

One workflow condition, focused synthetic regressions, the existing gate guide,
and an Unreleased changelog entry. Track this contributor correction in
[PR #50](https://github.com/nold-ai/changecost/pull/50), separately from
[Claude reader planning](../provider-04-claude-local-import/proposal.md).
Verify locally and on the supported Ubuntu/Python matrix with both required
providers. Revert the repair commit to roll back; retain historical evidence.

## Non-goals

No reader implementation, private source inspection, activation, live assessment,
review-tool repair, analyzer waiver, dependency/configuration policy changes,
merge, deployment or release.
