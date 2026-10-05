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
local reproduction requires a computation kind and a cutoff. Quote and computed
Settlement results require an EconomicScope mapping; numeric comparison identity
must match that scope and the selected declared amount using exact Decimal equality.
Quotes carry exactly two ordered p50/p90 declarations with matching scope identity,
paired null or finite amounts and p50 <= p90. Numeric advice requires positive
samples (minimum one is supported) and the selected quantile's amount. Computed
Settlements require exactly one scope-matching subtotal with explicit unknown_count
zero and a nonnull matching amount; observed zero remains valid. Missing, duplicate,
incomplete or contradictory declarations fail before opening the destination.
Quotes require p50/p90 and a nonnegative integer sample count;
computed and legacy Settlements carry null quantile/sample count. Legacy advice
also requires a null cutoff. Valid unknown advice
must give nonempty reasons. It may retain complete local reproduction only with
a nonnull selected complete declaration, an actually incompatible budget identity
and the incompatible_economic_identity reason. Complete compatible advice cannot
be concealed as unknown. Locally reproduced Quote completeness follows its paired
finite or null declarations. Locally incomplete Settlement advice may retain known
subtotals; imported and unpriced unknown claims remain valid.
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

Summary record IDs, each reason and legacy Settlement scope use the producer's
existing nonblank Identifier contract. Missing, null, empty or whitespace-only
identifiers fail before output access with the fixed safe technical error. Numeric
advice still permits an empty reasons list. Valid nonblank Unicode, padded, long
and control-containing labels are preserved as data and escaped within the existing
64 KiB output bound; no new taxonomy, normalization or identifier length limit applies.

Local computed Settlement declarations retain unique economic identity groups,
explicit nonnegative integer unknown counts and exactly one scope subtotal even
when completeness is unknown. Null amounts and positive unknown counts remain
valid incomplete advice. Summary validation checks structure without store access;
JSON alone cannot authenticate a declared historical amount.
 Complete local advice requires known amounts and zero unknown counts in every group; only the scope group may be empty with null amount and zero unknown count.

Every computed Settlement declaration requires typed nonnegative unknown_count
metadata, including portable unverified claims. Such claims may retain empty,
duplicate or unmatched groups accepted by the record model and remain unknown.
Only locally reproduced results apply scope/grouping/completeness invariants.
Human and summary rendering escape U+2028/U+2029 mandatory text separators;
other Unicode and exact JSON record values remain intact.
