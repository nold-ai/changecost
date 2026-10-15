# Optional synthetic advisory summary

Required repository quality remains independent of this example. Its current
coverage timeout investigation adds slowest-test durations to the existing full
host suite and fixed, bounded CPU/resource context before the gate. See
[quality gates](development/quality-gates.md#privacy-safe-runtime-timeout-diagnostics)
for scope and limitations. Host observations never replace signed native acceptance.

Native pytest coverage explicitly measures the installed `changecost` package and
repository `quality` tooling. The reviewer still collects and executes every test
with four workers under load scheduling and dispatches at most one pending test per
scheduling step. The installed CLI proof uses separate isolated cases so the
scheduler can place its smoke, portable lifecycle, economic and Quote work on
different workers without dropping assertions. Only complete signed Linux reports
on both matrix legs can accept this correction. It applies the
unchanged production-source coverage threshold and runs the full analyzer set under
the existing limits. Test modules
remain execution evidence rather than coverage targets; tracing their implementation
previously added work without adding a production-source coverage obligation.

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

Use a fresh directory; the demo preflights its database, bundle and four named
result paths before opening the store. Existing files, directories and symlinks,
including dangling links, cause safe exit two without modifying those paths or
creating a database; unrelated files are permitted. JSON outputs use exclusive
creation, preserving files that appear after preflight. A late failure may retain
newly generated demo files; remove only the owned example output before retrying.
This does not provide atomic directory publication or racing SQLite protection.
Named synthetic
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

Locally reproduced unpriced Quotes have paired null quantiles and zero samples.
A positive sample count contradicts that producer result and fails with the fixed
safe technical error before creating or appending to the summary destination.
Imported assertions may retain positive declared counts and remain unverified;
valid priced local results, including observed-zero amounts, retain their counts.

Quote check projections have null time-window bounds, including imported claims.
The summary rejects windowed Quote projections before writing; omitted bounds
retain their null defaults. Computed Settlement summaries retain supported
windows from their computation scope.

Native execution diagnostics retain a fresh `.specfact/native-process-*.json`
artifact alongside the unchanged native reports, including on failure. A five-second
observer samples numeric descendant process stat fields during the canonical review
command, excluding preexisting descendants and the controller. Exact PID/start-tick
parent chains, fresh invocation ID and input digest bind the observations. No process
names, command lines, environment, file paths or runtime payloads are exported.
The 64 KiB projection retains first/latest bounded trees and the latest 120 aggregate
samples, including a final observation. Missing links, incomplete baseline, process
limits, departures and truncation are disclosed. CPU ticks and resident pages are sums
of observed live processes, with units supplied when available; they do not represent
cumulative CPU or unique memory. Unsupported or unwritable diagnostics cannot change
native exits, report validation, test selection, analyzer limits or provider requirements.
Activity observations do not identify pytest phases or prove timeout causality.

If the initial descendant scan is incomplete, process diagnostics remain
unavailable for that invocation: later scans cannot safely classify unseen
preexisting work. Empty trees and samples retain the fresh binding and terminal
elapsed time; native execution, exits and acceptance checks continue unchanged.

A failed complete repository check also runs the pinned native CLI with explicit
`tests/test_review_session.py` selection, saving
`.specfact/selected-review-session-diagnostic.json`. This diagnostic retains the
original project configuration and signed runtime, with normal technical exits.
The required full-suite failure and canonical reports remain intact. Inspect actual
selected/observed test IDs and bindings before using the report to bound this family;
a subset success cannot certify the full suite or establish timeout causality.

Historical Settlement checks fail closed on uncertain prior local authority.
Predecessor candidates use destination time/sequence availability before dependency
pruning or receipt filtering; missing, invalid or ambiguous receipts and unsupported
anchors/versions cannot manufacture a first result. A unique historical tip is
required. Surviving local origin/cutoff declarations or raw computation record IDs
retain candidates after combined corruption; those claims deny verification only.
Foreign claims, unrelated Changes and genuinely later results keep their separate
treatment. These consistency checks do not authenticate coordinated removal or
rewriting of every unauthenticated origin, cutoff and receipt marker; availability
alone cannot distinguish that history from a foreign import.

Budget checks preserve surviving request selectors as negative historical evidence
when a predecessor changes its declared Change. A uniquely validated Quote-only
receipt sharing an imported Settlement ID does not confer Settlement authority or
suppress legitimate local advice. Both formats retain the same no-write boundary;
summary rendering cannot authenticate a producer claim.
