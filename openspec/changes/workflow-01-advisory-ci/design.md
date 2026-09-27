# Design: Expose advisory CLI checks and GitHub summaries

## Context

See [proposal](proposal.md) and [capability spec](specs/advisory-workflow/spec.md).
The current repository contains documentation and hygiene gates, with no product
package or runtime. This design describes later implementation, not delivered behavior.

## Goals / Non-Goals

**Goals:** Make the specified capability local, reproducible and explicit about missing evidence.

**Non-Goals:** No required status enforcement, PR comment bot, hosted service, dashboard, provider account setup or SpecFact runtime integration.

## Decisions

1. Keep only five public command families. quote creates the economic record; bind records explicit association; settle accepts local evidence/artifact paths; check compares a quote/settlement to a compatible budget; explain traces a selected record. All support structured JSON as appropriate; diagnostics go to stderr, not mixed into JSON stdout.

2. For successful check evaluation return advisory status within_budget, over_budget or unknown. All three exit zero during the pilot; invalid input, unsupported schema, database failure or malformed evidence returns nonzero with a structured error. Never suppress technical failures as budget advice.

3. Budgets must match economic kind, unit and basis, plus currency for money;
   nonmonetary budgets use currency=null. Incompatible or unpriced comparisons return
   unknown with a reason; no implicit FX or credit-to-cash conversion. For settlements,
   evaluate completeness for the exact requested source/interval/unit scope before
   comparing amounts. A provisional total, missing same-unit charge, unresolved
   correction or overlap affecting that scope returns unknown, whether the known
   subtotal is below or above budget. Show that subtotal and the missing evidence,
   but do not claim a complete budget result. The pilot does not infer lower-bound
   over_budget semantics from provisional records. Complete compatible settlements
   and priced quotes compare their selected value (quote p90 by default) to budget:
   greater means over_budget, otherwise within_budget. Human and JSON output name the
   scope, comparison value, basis, completeness, n when applicable and reasons.

4. Use GitHub Actions job summaries with read-only repository permission and sanitized local artifacts. The example invokes the standalone CLI, never interpolates issue titles or artifact values into shell code, escapes Markdown/HTML and controls summary size. No account tokens or live provider calls are needed.

5. CI example must remain opt-in and advisory; do not add a required budget check or automatic mutation of branch protection. Document integration with whatever developer workflow already exports local evidence.

## Dependencies and evidence

- [quote-01-empirical-estimation](../quote-01-empirical-estimation/proposal.md)

Shared boundaries and current provider evidence are recorded in the
[source assessment](../../../docs/research/pilot-source-assessment.md).
No provider-specific mapping becomes supported merely by appearing in this plan.

## Risks / Trade-offs

- Advice becomes enforcement → explicit exit semantics and opt-in workflow.
- Untrusted labels execute or misrender → safe argument handling and escaped bounded summaries.
- JSON hides uncertainty → required completeness and structured unknown reasons.

## Migration Plan

After separate implementation authorization, land this change in dependency order
with spec-derived failing and passing evidence. Update docs/cli.md, docs/ci.md, and README.md.
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
