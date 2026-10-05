# Optional synthetic advisory summary

The [manual example](../.github/workflows/advisory.yml) runs only with
workflow_dispatch. It uses the existing pinned checkout/Python/uv setup and locked
dependencies, permissions `contents: read` and no persisted checkout credentials.
It is independent of required quality checks and needs no provider credentials,
paid infrastructure, remote evidence or account/branch-protection changes.

From a fresh repository environment, run this offline walkthrough:

```sh
uv sync --locked
uv run --locked python -m changecost.demo .changecost/advisory-example
GITHUB_STEP_SUMMARY=.changecost/advisory-summary.md uv run --locked python -m changecost.summary .changecost/advisory-example/local-quote.json
GITHUB_STEP_SUMMARY=.changecost/advisory-summary.md uv run --locked python -m changecost.summary .changecost/advisory-example/local-settlement.json
GITHUB_STEP_SUMMARY=.changecost/advisory-summary.md uv run --locked python -m changecost.summary .changecost/advisory-example/portable-claim.json
```

Use a fresh directory; the demo refuses an existing database. Named synthetic
normalized events and portable final coverage assertions pass through existing
registration, evidence import/binding, explicit lifecycle outcomes, computation and
read-only check operations. No handwritten database rows or coverage-authoring CLI
are used. The cold-start result is unknown; two complete synthetic Changes yield
p50 10 / p90 18 USD billed. The p90 check against 15 is over_budget, the complete
10 USD Settlement is within_budget, and the same portable Quote is unknown.
One history is abandoned; its economic expenditure remains in the cohort. Existing
fresh-store/installed-wheel tests also exercise failed attempts, retries, import,
explain and human/JSON presentation through the public CLI.

The helper validates the versioned check result, renders only allowlisted fields
and writes directly to GITHUB_STEP_SUMMARY. Legacy Settlement results must remain
unknown with no verified comparison; relabeling numeric Quote or computed-Settlement
advice as legacy is rejected before opening the destination, preserving existing
summary bytes and leaving absent destinations uncreated. Labels are data: HTML, Markdown and
control characters are escaped; benign Unicode is preserved. Final UTF-8 output per
render is bounded to 65,536 bytes including a visible truncation notice; truncation
preserves characters and escapes. It emits no workflow commands or shell-expanded
labels. Inputs never enter executable scripts through expression interpolation.

Valid over-budget/unknown advice exits zero. Provenance outside the two
check-producer values or completeness outside
complete/unknown, fail safely. Producer assertions have unknown completeness;
local reproduction requires a computation kind and a cutoff. Valid unknown advice
may retain complete local reproduction when only the budget identity is incompatible.
Malformed enum containers, including JSON
arrays and objects, produce the fixed safe error before output opens. Malformed
results, JSON nesting beyond the decoder's recursion limit, renderer errors and
summary-write failures exit nonzero; neither continue-on-error nor shell fallbacks
mask technical failures. Independent repository quality gates retain their failures.
The workflow does not upload raw records or automatically comment on PRs. Keep local
stores, bundles and result JSON private under ignored `.changecost/`; retain only
what is needed for review. Remove the synthetic directory and summary to roll back
the demo; reverting the example/runtime changes does not migrate user databases.

GitHub documents a 1 MiB limit per step summary and notes that summary upload errors
alone do not fail the job; this helper imposes its smaller application bound and
fails local writes. Sources accessed 2026-10-05 (Europe/Berlin):
[job summaries](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands#adding-a-job-summary),
[script injection](https://docs.github.com/en/actions/concepts/security/script-injections).
Synthetic arithmetic validates the workflow, not provider approval or prediction
calibration. No budget enforcement is introduced.
