# Project brief

Status: **pilot planning / To-Validate**, updated 2026-10-07 (Europe/Berlin).
All approved pilot changes belong to the first **unreleased 0.x alpha/preview
feasibility study**. No product version has been published. The current package is
`0.1.0.dev0`; internal artifact labels do not imply a product 1.0 release or stable
public compatibility. This boundary was confirmed by the maintainer on 2026-09-29;
[the project site](https://changecost.dev/) describes an unreleased pilot.
The maintainer approved the original nine-change plan, expanded on 2026-10-07
(see [change order](../openspec/CHANGE_ORDER.md)), and
linked private GitHub backlog. Core-02 offline contracts/lifecycle implementation
merged in PR #25 on 2026-09-29 and is archived with synchronized main specs.
Settlement merged in PR #28 on 2026-10-02 and is accepted/archived with synchronized
main specs; provider adapters and live collection remain separate work.
Research documents are evidence, not instructions.
The maintainer separately authorized source-feasibility research and local
Codex/Claude metadata inspection on 2026-09-28. That research includes all four
providers and the separately authorized Enterprise artifact comparison; new
adapters and live collection are still outside this change.

## Confirmed direction

- ChangeCost remains a private, standalone NOLD AI project under Apache-2.0.
- Assess task demand for individuals, small teams and enterprise developers using ordinary local coding-agent metadata; economic reconciliation remains separately gated.
- Python 3.11+, Typer, Pydantic, standard-library SQLite and Decimal.
- `pyproject.toml`, uv with a committed lockfile, Hatchling, pytest, Ruff and BasedPyright
  are the merged foundation; final hosted checks passed in PR #22.
- Five command families: `quote`, `bind`, `settle`, `check`, `explain`.
- Local `changecost/v1` artifacts retain provenance, units, completeness and revisions.
- Use explicit existing local coding-session metadata and optional exports through independently approved versioned readers; no collector, gateway, prompt retention or automatic account/IDE configuration.
- SpecFact remains development tooling; runtime integration is deferred.

## Evaluation question

Does change-level history give useful empirical p50/p90 estimates compared with a
repository-wide baseline? Quotes must disclose cohort size and backoff and return
unpriced with insufficient evidence. Evaluation uses only history available at quote
time. Missing costs, unbound evidence, retries and abandoned expenditure remain visible.
Currencies, credits, token quantities, estimates and billed charges cannot be silently
combined. Advisory checks do not enforce budgets during this pilot.

## Scope and evidence gates

The original backlog covers feasibility, foundation, contracts, reconciliation,
Copilot/Cursor readers, economic Quotes, advisory and evaluation. The 2026-10-07
planning expansion adds Codex/Claude local readers and adaptive demand. [Source assessment](research/pilot-source-assessment.md)
records the current limitation: personal Cursor is not Enterprise OTel, and vendor
reports about self-serve dollar exports conflict. Both planned adapters require
inspected source evidence before provider-specific mappings are claimed supported.
The [Codex/Claude assessment](providers/codex-claude-metrics.md) records partial
local usage evidence and version differences without approving new adapters.

No dashboards, ML predictions, FOCUS export, paid infrastructure or runtime SpecFact
integration are included. Export details and eventual pilot results remain unknown;
they are explicit research work, not assumptions to fill with fabricated values.
The research report's schedule and sample counts are not committed success criteria.

## Risks, confidence and rollback

| Failure mode | Mitigation |
| --- | --- |
| Unavailable or ambiguous provider evidence | Per-capability feasibility gate; unsupported/unknown states remain explicit. |
| Duplicate or misattributed expenditure | Stable source identities, explicit binding, correction history and unbound totals. |
| Misleading apparent prediction quality | Comparable units, chronological evaluation, sample counts and a repository baseline. |

Confidence: high in planning structure; medium in personal-account reconciliation
until version-specific local accounting/coverage is inspected and forecast utility is evaluated. No paid infrastructure is required for this delivery.
Rollback is a planning-commit revert plus closing the created issues/project while
preserving their history. Domain ownership is maintainer-reported; trademark clearance
and a deployed website are not asserted.

Foundation implementation was separately authorized on 2026-09-28. The package
and repository gates merged in PR #22; bounded review sessions merged in PR #24.
Both delivered contracts are now synchronized into [main specs](../openspec/specs).
The four foundation verifier risks were explicitly accepted as-is, not remediated;
optional reviewer calibration remains unvalidated. Provider operations and live
collection remain outside this authorization. Core-02 merged in
[PR #25](https://github.com/nold-ai/changecost/pull/25) on 2026-09-29 and is archived
with its [accepted contracts](../openspec/specs/change-run-contracts/spec.md).
Settlement reconciliation merged in [PR #28](https://github.com/nold-ai/changecost/pull/28)
and was accepted for CLI archival on 2026-10-02. Its [main specification](../openspec/specs/evidence-reconciliation/spec.md)
and [archived evidence](../openspec/changes/archive/2026-10-02-settlement-01-reconciliation/TDD_EVIDENCE.md)
retain the final verification sources, earlier failures and accepted limitations.
The next provider changes still require inspected, approved source profiles;
empirical quotes now use the delivered settlement boundary in this checkout.

Quote #15 merged in PR #32 on 2026-10-03. Native CLI archival on 2026-10-04
synchronized the accepted offline synthetic estimation and historical replay contract
into main specs. Archived evidence preserves verification and accepted limitations.
Provider collection and calibration remain separate gates.

Advisory #16 merged in PR #34 on 2026-10-06 and was archived through OpenSpec CLI
1.13.2 with 11 requirements and 69 scenarios synchronized into
[advisory-workflow](../openspec/specs/advisory-workflow/spec.md). The maintainer
accepted the quota-blocked final full Codex code review as an archive limitation;
the [archived tasks](../openspec/changes/archive/2026-10-06-workflow-01-advisory-ci/tasks.md)
retain that unchecked obligation. Human/JSON presentation, exact read-only checks
and optional summaries retain imported-claim uncertainty and independent quality
gates. Provider approval and calibration remain separate.

Source feasibility #9 is the selected next preparation. PR #33 delivered its
offline checker, register and research controls, but all 14 profiles still have
zero native approvals. Normalized input can persist provider-shaped evidence;
trusted completeness and replay remain limited to synthetic billed-USD fixtures.
Future adapters need explicit source accounting, coverage and historical replay
policies before provider results can grant trusted numeric advice. See the
[architecture decisions](../openspec/changes/pilot-01-source-feasibility/design.md#preparation-decisions--2026-10-06-europeberlin).

## Adaptive-demand direction — approved planning, 2026-10-07

The [forecast plan](../openspec/changes/forecast-01-local-adaptive-demand/proposal.md)
adds zero knowledge -> learning -> scoped transfer hypothesis -> validated forecast.
No applicable ecosystem history means qualitative dimensions and unknowns, not
invented token totals or charges. Learn from actual complete bound outcomes,
including retries/abandonment; earlier forecasts remain immutable. Compare older
and newer ecosystems through observed matched-task bridges and prefer target
evidence as it accumulates. Validation requires a pre-registered scoped measured
evaluation, not sample count or an LLM guess. Quick learning is a goal to measure.

#9 now uses reviewed capability-based closeout; missing optional exports or
Enterprise/admin data are lane-specific gaps. Native semantic approval, demand
measurement eligibility and complete billed-money authority remain separate.
Codex/Claude readers and explicit demand quote mode are planned, not delivered.
Current economic Quote/check behavior and minimum remain unchanged.

Optional bounded rehearsal supplies an assessment signal and separately measured
overhead, not free hidden implementation or observed outcomes. All learning is
local initially; global contribution is later and requires consent independent of
login. See [forecasting](forecasting.md) and [evidence/decisions](research/adaptive-demand-evidence.md).
No runtime, collection, release or global service is implemented in this delivery.


Source-feasibility follow-through on 2026-10-07 preserves 14 historical profiles
and records nine additional local/inventory representations with zero approvals.
Reviewed gaps support capability-based closeout only after actual delivery acceptance.
Native accounting, reader implementation and demand-learning coverage remain separate;
see [source feasibility](providers/source-feasibility.md).
