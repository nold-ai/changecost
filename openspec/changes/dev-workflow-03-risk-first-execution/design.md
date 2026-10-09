# Design

## Context

See [the proposal](proposal.md) for motivation and [the delta](specs/bounded-review-session/spec.md) for the five added workflow requirements. The current shared policy already selects one upfront independent obligation review, affected-scope closure, Codex and risk-triggered CodeRabbit. The existing schema-8 session owns scope, findings, budgets and acceptance; behavioral packets summarize mapped evidence without granting completion.

This is a cross-cutting guidance change across the four workflow stages, so a design artifact is applicable. Current runtime, quality-tool code, receipt schemas and installed integrations remain unchanged. The closed #26 prerequisite supplies delivered mechanisms while its active OpenSpec history still retains incomplete acceptance milestones; this change does not resolve or archive those milestones.

## Goals / Non-Goals

**Goals:** put critical proof before dependent work, make reviewer requests easier to adjudicate, and evaluate marginal benefit through existing records.

**Non-goals:** add machine-enforced receipt fields, a new orchestration layer, mandatory multi-model competitions, a telemetry reader, or assurance-policy exceptions. The selected change remains instruction/documentation work; if executable tooling later proves necessary, return that additional scope for an explicit decision.

## Decisions

### 1. One compact checkpoint inside existing artifacts

Preparation records a small table in the existing design or preparation evidence: critical assumption, affected obligation, observable check and expected result, actual evidence reference, and limits. Limit selection to one or two assumptions for nontrivial behavior; existing obligation matrices still cover their full selected scope. Classify routine versus the current listed risk classes without creating another risk taxonomy.

Use synthetic fixtures and read-only or isolated probes through the relevant existing CLI/API/dependency. Record exact commands, input identity, outcomes and tool versions where relevant. Existing-system contradictions require revising the dependent approach; unavailable evidence names the supported next check and cannot be called proven. Expected red tests for new behavior retain the normal TDD meaning. Documentation-only work records applicability and uses document checks.

An upfront reviewer assesses the checkpoint alongside the existing obligation review. There is no extra reviewer. A standalone checklist, new packet schema or assurance validator was rejected because it would expand the machinery whose overhead motivated this change.

### 2. Stage integration follows the canonical shared policy

- **Prepare:** select and probe assumptions, reconcile scope, record relevant exclusions, and hand the checkpoint to the existing reviewer.
- **Implement:** confirm current evidence and settle critical contradictions before dependent work; name the sole writer and any independent read-only work. Preserve failing-before/passing-after behavior evidence.
- **Verify:** freeze the intended result and close affected obligations using the checkpoint, actual delta and current binding. Keep all mechanical and independent obligations.
- **Promote:** collect compatible findings, adjudicate them and obtain the required current-head provider evidence. Publish live acceptance in the existing PR receipt rather than a tracked receipt-only commit.

The shared workflow document owns the rule. The four skills reference it and add only their stage-specific action, avoiding four copies of the same policy. Update the relevant contribution/development guide, docs ownership, generated references and changelog during implementation.

Full Pstack routing was rejected: its design competitions and harness-specific delivery rules would add integration effort. No new standing agents, default fan-out, account settings or model changes are required. Parallel work is justified only for independent read-only obligations already selected by the workflow; shared writes remain serialized.

### 3. Findings retain evidence and authoritative dispositions

Triage summaries identify the accepted requirement, concrete path, evidence and proposed resolution. Record duplicate source identities against the same root finding; preserve distinct variants that alter failure coverage. A confirmed defect stays blocking regardless of how many reviewers reported it. A preference can be nonblocking only with an explicit explanation of why it violates no accepted obligation.

Use existing legal ledger dispositions. A credible unverified defect remains pending; a real defect requiring new scope goes through the existing scope decision. A genuine defect cannot be renamed a preference or non-finding to save effort. Existing exception approval, family investigation, counter retention and replan rules govern resolution. Do not introduce Pstack verdict labels as new event values.

Follow-up handoffs carry selected change, comparison/head/input binding, affected delta and assumptions, unresolved findings and necessary report references. Reuse applicable existing behavioral packets, without requiring lifecycle-model packets for unrelated documentation work. Keep verbose logs in ignored local output and preserve required complete source evidence there.

### 4. One bounded descriptive adoption trial

After guidance implementation, use one subsequently authorized bounded change as the trial. Do not select or implement another product change automatically. At its preparation, first stable candidate and final handoff, retain available measurements in existing receipts/evidence; preserve observation identity and scope. Separate one-time guidance/setup effort from that change's recurring execution.

Report phase boundaries for preparation, implementation, verification, review, rework and orchestration. Parallel intervals are not exclusive cost allocations; wall minutes, measured active reviewer time and measured active maintainer time must stay distinct. Unknown active human time cannot be inferred from waits or elapsed time. Record token categories separately, use deduplicated observed response usage or supported interval deltas, and never add cumulative snapshots together. Retain partial coverage and unknown billing; no rate database or inferred cash price is added.

Count genuine early discoveries and later escapes separately from duplicates, assurance-tool defects, design ambiguities and synthetic controls. Use the existing three-batch/90-active-minute default unless a maintainer explicitly grants an extension; preserve existing sessions and all prior counters. Record limits or incomplete acceptance without converting them into a successful trial.

The final assessment recommends retain, revise or withdraw using observed benefit, effort and limitations. No numeric savings threshold or guaranteed defect reduction is justified. Historical comparisons require comparable scope and acceptance boundaries and remain descriptive. No available authorized trial means the trial task stays pending. Update the established lessons-learned documentation and ownership only when real observations exist; do not create an empty report or another ledger now.

## Risks / Trade-offs

- Added ceremony: reuse existing artifacts/review slots, limit critical assumptions, and assess setup versus recurring effort in the trial.
- False confidence from a narrow probe: name excluded behavior, unavailable evidence and current-input identity; preserve final gates and independent review.
- Incorrect dismissal: require a concrete disposition rationale, keep credible unresolved defects pending and retain native objections/exception policy.

Confidence is high in guidance feasibility and medium in defect-reduction benefit. Actual time and billing savings are unknown. No paid service or new dependency is required; effort follows the existing bounded-review process rather than an unbounded workflow project.

## Migration Plan

1. Create and validate this proposal, unchecked tasks and accurately linked Todo issue; this creation request leaves code, skills and main specs unchanged.
2. On a separate implementation request, update canonical guidance and stage-specific skill references, validate worked scenarios and run applicable repository checks/review.
3. Trial on a separately authorized change, retain real observations, and publish an evidence-based recommendation. Keep acceptance pending until the required implementation/trial evidence exists.

No receipt or user-store migration is needed. Rollback reverts guidance/documentation changes and retains review/trial evidence; historical #26 results are preserved. Abandoned issue tracking is closed with history intact.

## Implementation checkpoint — 2026-10-08 (Europe/Berlin)

Fresh main/HEAD: `dc26715d2b583a31050c1cf7fda8ed0e9a9d5507`; implementation
branch: `codex/dev-workflow-03-risk-first-execution`. Matching local prepared
artifacts were carried forward intact from the planning branch, with no stash or
planning-PR application. Native #26 is closed; its historical limitations remain.
The implementation/verification request authorizes guidance and a verified push,
not a PR or another product change/trial.

Documentation applicability: this change edits instructions and registrations,
not runtime or executable gate code. No runtime safety probe or invented TDD red
is appropriate. Relevant proofs are existing scenario/gate checks and independent
inspection. Two critical planning assumptions were inspected before edits:

| Assumption / obligation | Observable check / expected result | Actual evidence | Limits |
| --- | --- | --- | --- |
| Prose checkpoints fit existing records without schema changes | Inspect existing session dispositions, binding and design/preparation artifacts | Upfront independent reviewer confirmed compatibility; legal dispositions are `fixed`, `non_finding`, `accepted_exception`, with credible findings initially `unresolved` | Prose accuracy still needs affected independent closure; no machine enforcement added |
| Same-head edits cannot reuse stale evidence | Inspect `advance_head` and current binding rules | Upfront review confirmed input/content/index refresh invalidates prior evidence; new native/check reports require current binding | Required native evidence and providers still need actual execution; a checkpoint cannot waive them |

Sole writer: coordinating implementation agent. Independent reviewer/checkers are
read-only. Local container prerequisite checks observed Linux x86_64 execution and
successful `unshare -Ur true` only in a disposable container with its syscall
filter relaxed; no host mount, privilege grant or repository/account configuration
change was used for that probe. This is a launcher prerequisite, not native
assurance. Final commands/outcomes and unsupported evidence belong in
[TDD evidence](TDD_EVIDENCE.md). The subsequently authorized adoption trial remains
pending and cost/defect-reduction benefit remains unvalidated.
