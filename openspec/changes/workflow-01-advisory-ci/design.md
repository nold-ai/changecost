# Design: Advisory CLI checks and GitHub summaries

## Context and delivered boundaries

See [proposal](proposal.md), [acceptance scenarios](specs/advisory-workflow/spec.md)
and [preparation evidence](PREPARATION_EVIDENCE.md).
The Python foundation, four current command families, registration/binding, lifecycle
outcomes, normalized evidence import, computed Settlement and synthetic Quote are
delivered. The authorized implementation now adds `check`, human formatting and structured CLI errors; current-head verification and published acceptance remain pending.
Existing Quote inspection can reproduce supported historical parameters/results;
Settlement inspection currently checks receipt/input availability, not full result
reproduction. Availability alone cannot justify complete budget advice.

## Goals and non-goals

Add readable presentation, truthful offline budget advice and an opt-in safe CI
summary. Reuse delivered contracts, selectors, snapshots, provenance and gates.
No persisted budget, migration, new source policy, provider parser, new coverage
creation command, enforcement, price conversion or competing quality pipeline.

## Presentation and error contract

Global `--format json|human` appears before the command, like `--db`; default json.
Preserve successful JSON payloads for bind, quote, settle and explain, including
portable record schemas and amount strings. Do not add a universal wrapper or
require economic fields on identity-only results. New check output has an internal
version tag; new JSON errors have a version tag, stable code and safe message.
These tags are internal preview contracts, not a product release or artifact v2.
Human output renders the same underlying result and uncertainty; formatting does
not affect selection, persistence or idempotency. Escape terminal control characters
in display values rather than emitting them as terminal commands.

Successful JSON stdout contains exactly one result, human stdout one readable
result. Diagnostics use stderr. Invalid arguments/modes, malformed or unsupported
artifact schemas, missing records/stores and database/filesystem failures exit 2;
JSON mode returns one structured safe error on stderr and no successful stdout.
Argument-parser failures obey the same rule, including invalid format values (safe
JSON error fallback). Do not expose input values, private paths, SQL or tracebacks.
Help and version retain their offline text behavior and exit zero; bare/unknown
commands remain invalid and do not create stores.

## Explicit check source and budget

`check` requires `--record-kind quote|computed_settlement|settlement` and
`--record-id ID`. It never silently selects a latest revision, sums multiple
records or opens another store based on artifact contents. Without `--artifact`,
read the selected immutable record from global `--db` in a read-only snapshot.
With `--artifact PATH`, strictly load an existing changecost/v1 bundle and select
that record there; do not import, create/open a database, or establish local authority.
Reject malformed graphs, missing selection or another record kind as technical errors.
A well-formed unsupported computation version remains inspectable unknown advice;
an unsupported portable schema is a technical failure.

Require `--budget AMOUNT` as a finite, nonnegative Decimal string, and explicit
`--economic-kind`, `--unit`, `--basis`, plus `--currency` for monetary budgets.
Reuse the existing economic identity and amount validators; currency is absent/null
for nonmonetary values. Reject negative/nonfinite/malformed budgets before store
access. Compare kind, unit, basis and currency exactly; no conversion or rounding.
`--quantile p50|p90` applies only to Quotes; absence selects p90 for Quotes. An
explicit quantile with a Settlement is invalid. Comparison is strictly greater for
over_budget; equality, including observed zero, is within_budget.

## Authority, cutoff and completeness

Every result separates declared/claimed values from a verified comparison value,
names the record, budget identity, source, scope/cutoff, completeness/provenance,
sample count when relevant and explicit reasons. Unknown results retain available
claimed amounts/known subtotals but have no verified comparison value.

For a priced Quote, numeric advice requires matching supported computation metadata,
a valid local typed receipt and supported reproduction of the exact stored result
at its original store-local cutoff. Use one read snapshot and the existing historical
selection/replay boundary; a future/foreign cutoff, missing inputs, unsupported
version or result mismatch produces unknown. Legacy/imported Quotes remain claims.
Do not recompute a new Quote against current history or change its original cutoff.

For a computed Settlement, validate its local typed receipt, supported algorithm and
policy, original cutoff and all required historical inputs, then reproduce values
and completeness using the existing reconciliation evaluator at its stored scope.
Compare the reproduced material result with the immutable stored result, including
subtotals, scope, consulted inputs/exclusions, reasons and full-change completeness.
Ignore only nondeterministic record bookkeeping that is not computation evidence.
Receipt/input availability alone is insufficient. Later imports/corrections do not
change advice about the selected historical record. Numeric advice requires the existing evaluator to certify completeness for the
exact stored scope with one matching subtotal and no unresolved reasons. The current
evaluator marks narrowed Run windows partial_change_scope; retain that reason and
return unknown with the declared scope/subtotal. Do not filter scope-only reasons
or invent a new narrower coverage policy. Provisional/missing coverage or unresolved
corrections remain unknown on either side of budget. Incompatible identity remains unknown; do not sum other subtotals.

A valid legacy Settlement or imported/portable computed claim without local
verification returns unknown with its declared values and producer-assertion status.
Even purported completeness or supplied receipt-like fields cannot create authority.
Artifact-only inputs always remain producer claims under the current portable contract;
no stateless historical certification or new portable receipt is introduced.
Malformed input and failed database access are technical failures, not uncertainty.

Check returns within_budget, over_budget or unknown with exit zero for valid advice.
It creates no store, Quote, Settlement, computation receipt, revision or availability
observation. Verify unchanged exports and durable retry behavior around evaluation.

## Fresh-store regression walkthrough

Reuse bind registration, quote, Run registration/binding, normalized settle import,
evidence binding, explicit Run/Change outcomes and settle computation. Use named
controlled synthetic fixtures including existing portable coverage records, not a
real provider export or invented parser. Cold start is a valid unpriced Quote;
complete synthetic history can support a priced Quote and complete Settlement.
Exercise check/explain and both presentation modes after the existing lifecycle.
No hand-written database row or new coverage-authoring API is needed. The fixture
bundle is test/demo input with explicit synthetic provenance, not an approved provider.

## Optional Actions example and summary

Add a workflow_dispatch-only example, independent of required quality jobs, using
local synthetic fixtures and the repository's reviewed pinned checkout/uv/Python
setup. Use permissions contents: read, no persisted checkout credentials, provider
credentials, remote collection or automatic PR commentary. Pass selections/budgets
as data arguments/environment values, never expression interpolation into scripts.
No setup changes to account settings, branch protection or required checks.

Use a Python helper to validate the check-result version and allowlist summary
fields, then write directly to GITHUB_STEP_SUMMARY; do not eval, source, shell-expand
or render raw record dumps. Escape HTML, Markdown delimiters and terminal/control
characters; preserve benign Unicode. Bound final UTF-8 output to 65,536 bytes,
including a visible truncation notice; truncation must preserve UTF-8 validity and
rendering escapes. This fixed pilot limit is not a new configuration framework.
Summary serialization/path/write failures are technical nonzero failures. Valid
unknown/over-budget advice exits zero; do not suppress technical failures with
continue-on-error or shell fallbacks. Raw artifacts remain local; document retention
without automatically uploading sensitive records.

GitHub's per-step summary limit is 1 MiB and summary upload errors alone do not
fail a job. Application rendering must enforce its own smaller limit and write-error
contract. Sources, accessed 2026-10-05 (Europe/Berlin):
[job summaries](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands#adding-a-job-summary),
[script injections](https://docs.github.com/en/actions/concepts/security/script-injections),
[permissions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions).

## Verification, delivery and rollback

Spec first, real failing tests, implementation, passing evidence. Preserve existing
JSON/idempotency, imported-claim, backup, historical cutoff and trust tests; extend
fresh-store/installed-wheel proofs rather than rebuild delivered operations.
Add exact comparison, authority/replay, no-write, presentation/parser and malicious
summary boundaries from the delta spec. Update docs/cli.md and new docs/ci.md only
when runtime/examples exist, their owner/source mappings and generated references.
Keep package 0.1.0.dev0 and the existing blocking quality/Python-matrix requirements.

Before later implementation obtain one independent obligation review, then close
only affected obligations after corrections. Required published reviews are Codex
and CodeRabbit because claim trust and historical computation are affected. Bind
actual complete inputs and reports in the bounded session; no counter reset or
assurance from an older archive/feature result. Supported-Linux native assurance
remains required; unavailable macOS analyzers are incomplete.

Preparation remains local/unpublished on the owned combined branch in worktree
7808, alongside the existing Quote archive, as explicitly requested. The sole
native prerequisite is closed #15; provider approval/calibration remain separate.
See [archived Quotes](../archive/2026-10-04-quote-01-empirical-estimation/proposal.md),
[change order](../../CHANGE_ORDER.md) and [source assessment](../../../docs/research/pilot-source-assessment.md).
No runtime persistence change or paid infrastructure is planned. Restore only the
preparation diff to undo planning; later revert runtime changes while retaining
original stores/backups, accepted archive and evidence.

## Authorized implementation status

The maintainer requested implementation, independent/local review and combined PR
delivery on 2026-10-05. Historical preparation remains unchanged evidence; current
red/green outcomes are recorded separately in [TDD evidence](TDD_EVIDENCE.md).


## Review correction: producer headers, predecessors and selected values

Supported generated headers bind origin and both generated timestamps to their
original cutoff through the existing shared eligibility guard. Advisory Settlement
replay also reconstructs the receipted same-Change predecessor at that cutoff,
across scopes, retaining its ledger identity without authenticating opaque first IDs.
Summary validation binds numeric comparison to the selected p50/p90 pair or single
complete scope subtotal using exact Decimal equality. Unknown producer results and
minimum-one Quotes remain supported; no persisted schema or budget policy changes.


Local computation authority requires exactly one raw receipt per result ID before
request/payload matching. Identical aliases and conflicting aliases are ambiguous
for both computation kinds, including inspection, retry and historical predecessor
selection. This uses the existing receipt table without a database/schema change.


Selected local availability is a technical input boundary, checked before legacy,
receipt or version trust shortcuts. Quote inspection uses the same typed-row
validation without changing normal serialized availability. Summary unknown status
requires reasons; local completeness follows the Quote pair and selected complete
value. Complete local unknown is possible only for an actually incompatible budget
with its reason. Partial computed scopes can retain a known subtotal while unknown.

Selected local availability must belong to the committed metadata snapshot: its
strict positive sequence cannot exceed the metadata sequence. Check and both
computation inspectors validate this bound before legacy/receipt/version decisions.
A result's original cutoff intentionally precedes its own insertion; validating
that original anchor does not replace the committed-snapshot membership check.

The summary reuses the producer's existing Identifier validator for legacy scope,
record ID and each reason. Missing/null/blank values fail before output access;
valid nonblank labels retain original Unicode, whitespace, controls and length,
with escaping/bounded output unchanged. Numeric advice still permits empty reasons.

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
# Native timeout investigation

Both signed coverage analyzers for commit 95457ed timed out at 300 seconds;
the other nine analyzers passed. Four pytest workers did not establish native
acceptance. The failed reports contain no partial test or coverage observations,
so the cause remains unknown. Preserve these failures and every mandatory gate.

Log the slowest 25 durations from the existing complete host suite, and collect
only bounded Python-version, CPU/affinity counts and numeric/max cgroup limits
before the repository check. Missing or invalid resource values are unavailable;
never print arbitrary input, environment values or runtime payloads. These host
observations cannot replace signed coverage or establish its timeout cause.
No second suite, dependency, runner upgrade, test selection or deadline change
is introduced. Rollback removes only the diagnostic configuration and collector.
