# Proposal

## Why

The foundation and behavioral-evidence retrospectives record repeated late corrections and substantial assurance-tooling overhead without demonstrated billing or delivery savings. Move critical-assumption proof and finding adjudication earlier in the existing workflow so more effort produces useful, verified changes.

## What Changes

- Select one or two critical safety assumptions for each nontrivial behavior change and prove them through the smallest relevant existing CLI, API or dependency probe before dependent implementation.
- Feed those assumptions, observable evidence, affected obligations and exclusions into the existing upfront independent review; reuse applicable behavioral packets.
- Require actionable findings to identify a violated obligation, reachable failure path and evidence. Record preferences, non-findings and uncertainty explicitly without dismissing confirmed defects.
- Keep one writer, batch compatible corrections and provide compact delta/assumption handoffs through existing review slots.
- Run one bounded trial on a subsequently authorized change, reporting full delivery overhead, early discoveries and later escapes with unknown costs preserved.

## Capabilities

### New Capabilities

None. Reuse the existing contributor review capability and records.

### Modified Capabilities

- `bounded-review-session`: add critical-assumption proof, evidence-based triage, compact execution checkpoints and a bounded adoption assessment to the contributor workflow. Existing ledger schema, interfaces, budget rules and completion semantics remain unchanged.

## Impact

Implementation will update the four repository-owned ChangeCost workflow skills, canonical shared workflow guidance and correlated development/contribution documentation. Documentation ownership, generated references and the Unreleased changelog must remain consistent. No product-runtime or executable quality-tool change is planned.

The maintainer authorized implementation followed by verification on 2026-10-08. Guidance and planning artifacts are locally implemented and unpublished on `codex/dev-workflow-03-risk-first-execution`; final assurance/publication and the separately authorized trial remain pending. Tracking story: [#40](https://github.com/nold-ai/changecost/issues/40), with native User Story type, parent #6, prerequisite #26 and private ChangeCost project In Progress state.

Parent feature: [Local core and contracts #6](https://github.com/nold-ai/changecost/issues/6), under [Epic #4](https://github.com/nold-ai/changecost/issues/4). Sole native prerequisite: [behavioral evidence #26](https://github.com/nold-ai/changecost/issues/26), closed and delivered through PR #27. Its retained negative pilot outcome and acceptance limitations are not rewritten. No product-delivery dependency is added.

Verification covers strict selected/all OpenSpec validation and applicable documentation, ownership, metadata and index checks now. Later implementation preserves mechanical gates, supported-Linux/Python assurance, Codex and risk-triggered CodeRabbit, current-input evidence and bounded review history. This assurance-guidance change requires both review providers when promoted.

## Non-goals

No Pstack installation, Cursor migration, default design competition or additional review lane; no new ledger, packet format, receipt schema, runtime command, provider reader, automatic collection or LLM invocation. No gate reduction, merge, release, deployment or PR creation is authorized in the implementation/verification stage. The invoked verify skill authorizes commit/push only after required checks and independent closure pass. No guaranteed reduction in defect count, tokens, billed cost or delivery time is claimed.

## Evidence, assumptions and rollback

Confirmed direction: preserve assurance and lower avoidable overhead. The [foundation retrospective](../../../docs/lessons-learned/token-economics-first-foundation.md) and [behavioral-evidence retrospective](../../../docs/lessons-learned/behavioral-evidence-pilot.md) motivate earlier proof; neither establishes a causal savings baseline. The improvement remains a hypothesis for the bounded trial.

Pstack's [blast-radius practice](https://github.com/cursor/plugins/blob/main/pstack/skills/blast-radius/SKILL.md) and [lead-judgment guidance](https://github.com/cursor/plugins/blob/main/pstack/skills/interrogate/references/lead-judgment.md), accessed 2026-10-08 (Europe/Berlin), inform selective practices rather than authorize installing or executing upstream workflows.

Added ceremony, weak probes and mistaken dismissal are mitigated by limited assumptions, explicit evidence boundaries and preserved defect/completion obligations. Confidence: high in feasibility, medium in defect-reduction benefit; billing savings remain unknown. Rollback removes the eventual guidance changes while retaining evidence and review history; abandoning this local proposal removes only its owned uncommitted files and closes tracking without deleting records. No user-store migration is required.
