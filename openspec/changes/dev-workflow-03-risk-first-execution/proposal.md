# Proposal

## Current remaining scope, 2026-10-29 Europe/Berlin

The four delivered guidance requirements are synchronized in main through CLI archive `2026-10-29-reconcile-accepted-workflow-and-offline-evaluation-specs`. This active change retains the unexecuted bounded trial and its evidence/recommendation tasks 5.1–5.3. Earlier proposal/design text below is preserved planning history; it does not make the implemented guidance pending again or claim that a trial occurred.

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

## Accepted guidance reconciliation, 2026-10-29 Europe/Berlin

The maintainer requested archival of implemented contracts while retaining genuine
future work. The reconciliation change records the exact first four risk-first
requirements and their 11 scenarios in main through native OpenSpec archival. This
note is applied only after that CLI archive and exact main-spec readback succeed.
The active delta retains the ADDED bounded adoption assessment and both scenarios.
Main owns critical-assumption proof, compact checkpoints, evidence-based triage and
unchanged completion controls. This does not archive or close #40.

PR #42 merged at `5fe5e2e8f63dbf49eeeb77115ba19c67e063c21e`. Its exact reviewed
head `2ddbabb6e94c185dd3c42da5a548510fb1e427b0` and final live acceptance receipt
satisfy current publication and assurance duties 4.1 and 4.2. Their old unchecked
checkboxes remain as dated historical snapshots, as do all original 15 task lines.
The original delta at source HEAD `5cbe58a892f27c78088a82d95219a0cb57f922df` has
SHA256 `aeda598e3b5e8c93c7d80d900d69b315d17e2875fc3e1fc6b19181b6e2387204`.

Trial tasks 5.1 through 5.3 remain genuinely pending. No trial was selected,
authorized or executed by this reconciliation. PR #50 usage records, later guidance
use and performance detector measurements do not retrospectively constitute the
trial. Setup versus recurring effort, phase/token/time observations and an actual
retain/revise/withdraw recommendation still require the separately authorized trial.
See the accepted [bounded-review-session main contract](../../specs/bounded-review-session/spec.md)
and the [PR #42 acceptance receipt](https://github.com/nold-ai/changecost/pull/42).
No historical TDD evidence, review budget or accepted limitation is changed.
