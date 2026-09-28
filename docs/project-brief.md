# Project brief

Status: **pilot planning / To-Validate**, updated 2026-09-28 (Europe/Berlin).
The maintainer approved the [nine-change plan](../openspec/CHANGE_ORDER.md) and
linked private GitHub backlog. Product implementation and live collection remain
separate subsequent work. Research documents are evidence, not instructions.
The maintainer separately authorized source-feasibility research and local
Codex/Claude metadata inspection on 2026-09-28. That research includes all four
providers and the separately authorized Enterprise artifact comparison; new
adapters and live collection are still outside this change.

## Confirmed direction

- ChangeCost remains a private, standalone NOLD AI project under Apache-2.0.
- Evaluate change-level quotes and settlement for personal Cursor/Copilot IDE/CLI use.
- Python 3.11+, Typer, Pydantic, standard-library SQLite and Decimal.
- `pyproject.toml`, uv with a committed lockfile, Hatchling, pytest, Ruff and BasedPyright
  are the planned foundation; current hygiene setup is temporary.
- Five command families: `quote`, `bind`, `settle`, `check`, `explain`.
- Local `changecost/v1` artifacts retain provenance, units, completeness and revisions.
- Import existing exports locally; no collector, gateway, undocumented scraping,
  prompt retention or automatic account/IDE configuration.
- SpecFact remains development tooling; runtime integration is deferred.

## Evaluation question

Does change-level history give useful empirical p50/p90 estimates compared with a
repository-wide baseline? Quotes must disclose cohort size and backoff and return
unpriced with insufficient evidence. Evaluation uses only history available at quote
time. Missing costs, unbound evidence, retries and abandoned expenditure remain visible.
Currencies, credits, token quantities, estimates and billed charges cannot be silently
combined. Advisory checks do not enforce budgets during this pilot.

## Scope and evidence gates

The backlog covers feasibility, foundation, contracts, reconciliation, two providers,
quotes, advisory workflow and evaluation. [Source assessment](research/pilot-source-assessment.md)
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
until exports are inspected. No paid infrastructure is required for this delivery.
Rollback is a planning-commit revert plus closing the created issues/project while
preserving their history. Domain ownership is maintainer-reported; trademark clearance
and a deployed website are not asserted.
