# Expose advisory CLI checks and GitHub summaries

## Why

Developers need readable and machine-consumable results and safe budget advice
without turning an unvalidated empirical quote into budget enforcement. The
foundation, registration/outcomes, normalized settlement and synthetic Quotes are
already delivered; this change completes presentation, checks and CI examples.

## What Changes

- Preserve existing JSON success payloads and add opt-in human presentation through
  global `--format human`; JSON remains the default across the five command families.
- Add safe structured technical errors, including argument-parsing failures.
- Add read-only `check` of an explicitly selected Quote or Settlement against an
  exact compatible Decimal budget, disclosing scope, historical cutoff and provenance.
- Return unknown for unverifiable producer claims and incomplete/unpriced values,
  showing declared amounts or known subtotals without treating them as verified totals.
- Provide a manually invoked, read-only GitHub Actions example and a bounded safe
  summary renderer using local synthetic artifacts without provider credentials.
- Extend existing fresh-store regression examples and foundation documentation,
  generated references and workflow checks rather than rebuilding delivered operations.

## Capabilities

### New Capabilities

- `advisory-workflow`: Human/JSON presentation, provenance-aware advisory budget
  evaluation and safe standalone CI summaries.

### Modified Capabilities

None. This adds an advisory capability using the accepted
[contracts](../../../specs/change-run-contracts/spec.md),
[reconciliation](../../../specs/evidence-reconciliation/spec.md) and
[Quotes](../../../specs/empirical-quotes/spec.md). It does not replace their portable
schemas, computation algorithms or source-coverage policies.

## Impact

The authorized implementation affects CLI presentation, ephemeral budget results, read-only
historical verification and the optional CI example. Documentation will update
`docs/cli.md`, add `docs/ci.md`, and retain current ownership/generated references.
The planned interfaces are defined in [design](design.md); acceptance is defined
by [the delta scenarios](specs/advisory-workflow/spec.md).
Preparation was docs-only. Implementation was separately authorized on 2026-10-05; current runtime changes and optional workflow are pending verification/PR acceptance.

## Non-goals

No budget enforcement, persisted budgets, database-layout migration, automatic
latest-record selection, provider parser/collection, FX or credit-to-cash conversion,
PR comment bot, hosted service, dashboard or SpecFact runtime integration. Blocking
repository quality checks remain independent of advisory statuses. No new CLI mode
for manufacturing coverage assertions is required by this change.

## Dependencies

- [quote-01-empirical-estimation](../2026-10-04-quote-01-empirical-estimation/proposal.md)

#15 is closed after merged PR #32; its accepted Quote specification is synchronized
locally through the native CLI archive. Native prerequisites are unchanged.
See [change order](../../../CHANGE_ORDER.md) and [preparation evidence](PREPARATION_EVIDENCE.md).
Provider approval and calibration remain separate gates; synthetic evidence suffices
for this advisory workflow and approves no provider-specific mapping.

## Decisions and uncertainty

The maintainer selected **unknown with displayed claims** for imported results
without supported local verification. Existing JSON payloads remain intact; only
new check/error results receive new version tags. All three valid advisory statuses
exit zero; technical failures exit 2. Claims, checked values and historical
completeness remain visibly distinct. See [design](design.md).
Prediction accuracy and live source support remain To-Validate. Preparation is
historical preparation was local/unpublished; the subsequent maintainer request authorizes this runtime scope.

## Risks and rollback

- False completeness from imported flags → supported local receipt plus historical
  result/completeness reproduction before numeric budget advice.
- Advice hides technical failure → distinct stderr/error contract and nonzero exits.
- Untrusted labels execute or misrender → data-only rendering with escaped bounded output.

Restore/revert only the preparation diff if abandoned, preserving the accepted Quote
archive and earlier evidence. Later runtime rollback reverts implementation while
retaining stores/backups; no planned persistence change or paid infrastructure is needed.

## Source Tracking

<!-- tracking:start -->
- GitHub issue: [#16](https://github.com/nold-ai/changecost/issues/16) (native type: User Story).
- Parent feature: [#8](https://github.com/nold-ai/changecost/issues/8) — Quotes and developer workflow.
- Parent epic: [#4](https://github.com/nold-ai/changecost/issues/4) — ChangeCost — validate change-level cost estimation and settlement.
- Project: [ChangeCost](https://github.com/orgs/nold-ai/projects/3) — private, status Todo.
- Source: maintainer-approved pilot plan, 2026-09-28 (Europe/Berlin).
- Tracking readback: 2026-10-05; issue Open/Todo, parent #8 and closed prerequisite #15 retained.
- Preparation: local/unpublished history retained. Implementation authorized 2026-10-05, in progress; acceptance and issue closure remain pending.
<!-- tracking:end -->
