# Pilot source assessment

Evidence accessed **2026-09-28 (Europe/Berlin)**. These observations correct
assumptions in the original research without modifying its preserved bytes.
The [source-feasibility report](../providers/source-feasibility.md) is the current
capability assessment. Authorized Codex/Claude local metadata has been inspected;
Cursor Basic local identity/context evidence is also recorded in its
[assessment](../providers/cursor-local-metrics.md). Copilot/Cursor usage exports
remain pending and no live pilot has run. The [VS Code hosted Copilot assessment](../providers/copilot-local-metrics.md)
now adds an explicit host/SDK identity link and partial local usage evidence.
The separate [Enterprise review](../providers/enterprise-schema-review.md) confirms
local projection relationships while leaving Enterprise consumption unverified.
The [v2 comparison](../providers/enterprise-v2-schema-review.md) adds reported message
counters and synthetic arithmetic, with an OTLP enum mismatch and admission limits.
Work OTel is subsequently reported disabled; existing custom session-log hook output
is the relevant next source, with vendor and derived fields assessed separately.

| Surface | Verified documentation | Pilot implication / evidence still needed |
| --- | --- | --- |
| Cursor Enterprise | OTel export requires Enterprise and sends data to an external collector. | Excluded from this personal-account pilot; its schema is not a personal export contract. |
| Cursor personal usage export | The 2026-07-31 removal report conflicts with an August restoration update and later support advice. | Current cash fields/basis are unverified. Inspect the actual account's CSV; do not assume either universal monetary support or universal removal. |
| Copilot CLI | Local JSON-lines export is documented through `COPILOT_OTEL_FILE_EXPORTER_PATH`. Billing attributes repeat across root and child spans. | Verify installed version and fixture shape; count authoritative billing units once and do not interpret a multiplier as cash. |
| Copilot IDE | VS Code documents a file exporter; resource/session semantics require care. | Confirm actual IDE/version and local format independently of CLI; do not assume a window identifies a change. |
| Codex CLI/app/IDE | Usage interfaces are documented; local Desktop rollout 0.158.0-alpha.2.1 differs from installed CLI 0.139.0. | Partial local token metadata evidence, including cache-write fields and repeated totals. No approved aggregation or billed-cash mapping. |
| Claude Code CLI/IDE | Token and estimated-cost metrics are documented; local records contain repeated request/message usage. | Partial identity/usage evidence at 2.1.275/2.1.215; repeated records can change usage. Finality and cash remain unverified. |

Sources: [Cursor OTel](https://prod.cursor.com/docs/enterprise/opentelemetry-export),
[dated Cursor support post](https://forum.cursor.com/t/usage-page-to-token-amount-what/167153/16),
[Copilot CLI reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference),
[VS Code agent monitoring](https://code.visualstudio.com/docs/agents/guides/monitoring-agents).
All accessed 2026-09-28. Recheck before relying on a specific installed version.
See the [Cursor chronology](../providers/source-feasibility.md#cursor-evidence-correction)
for conflicting updates and the [Codex/Claude assessment](../providers/codex-claude-metrics.md)
for primary citations, observed shapes, versions and their limits.

## Evidence gate

The [source feasibility change](../../openspec/changes/pilot-01-source-feasibility/proposal.md)
requires a per-surface matrix of access, identifiers, economic units, billing basis,
completeness, correction semantics and safe fixture provenance. Documented support
and observed personal-account support must be separate fields. Provider-backed
joins, explicit manual mappings and unbound records remain distinct.

A tokens-only source can support token analysis without supporting monetary
settlement. A missing session identifier cannot be reconstructed from time proximity
with claimed provider authority. Unknown is not zero. An unavailable capability
must narrow the support statement; a wholly unavailable source blocks its adapter
until the maintainer explicitly revises scope.

The planned CLI imports existing local exports. It neither collects telemetry nor
changes IDE/account settings. Synthetic fixtures verify behavior; they do not prove
account access, provider compatibility, cost calibration or actual billing accuracy.

## Planning choices and confidence

The maintainer approved Python 3.11+, Typer/Pydantic, SQLite/Decimal, and
uv/Hatchling. These are design choices, not claims that code exists. uv owns
resolution/environments; Hatchling builds packages through `pyproject.toml`.
See [uv project configuration](https://docs.astral.sh/uv/concepts/projects/config/)
(accessed 2026-09-28). The foundation change will replace the temporary bootstrap
dependency setup with a committed lockfile and modern project workflow.

Confidence: high in the bounded research and recorded observations; low in complete
personal-account reconciliation until source semantics and billing bases are verified. Main failure modes are
unavailable evidence, double counting and misleading calibration. Mitigate with
the feasibility gate, source-aware dedupe and chronological baseline evaluation.
No paid infrastructure is required. Rollback is a planning-commit revert and
closing linked issues/project, retaining their history.
