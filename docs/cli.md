# Offline lifecycle, settlement, Quote and advisory CLI

Install with the [README setup](../README.md#work-on-the-repository). Put the global
`--db PATH` option before the subcommand. Its default is
`.changecost/changecost.sqlite3`. All examples below are synthetic and work offline.
Help and version succeed without creating a store; bare, invalid and unsupported
operations exit nonzero. Read-only inspection of a missing store also fails without
creating it. See the [generated option reference](commands.md) and [contracts](contracts.md).

```sh
changecost --db demo.sqlite bind --register-change --repository-id demo --change-id C1 --change-shape bugfix
changecost --db demo.sqlite bind --register-run --repository-id demo --change-id C1 --provider synthetic --surface cli --run-id R1
changecost --db demo.sqlite settle --repository-id demo --provider synthetic --surface cli --run-id R1 --run-outcome failed
changecost --db demo.sqlite settle --repository-id demo --change-id C1 --outcome accepted
changecost --db demo.sqlite explain --repository-id demo --change-id C1
changecost --db demo.sqlite explain --export-artifact bundle.json
changecost --db imported.sqlite bind --import-artifact bundle.json
```

Registration returns the immutable record as JSON. Repeating identical inputs is a
no-op; conflicting immutable data fails. Register each retry with a different full
RunRef before marking its Change terminal. Features are captured once at Change
registration. Run registration can include `--work-start` with an aware RFC3339 time.
For an already imported unbound Run, omit `--register-run` to bind it to a Change
with the same complete selectors. Evidence mapping uses `--evidence-id RECORD_ID`
plus all Run selectors, with no change-id. Evidence IDs refer to previously imported
v1 evidence records; this command does not parse provider exports.

`settle` has mutually exclusive lifecycle, normalized-import and computation modes.
See [settlement examples](settlement.md) for import/compute selectors. Lifecycle mode
declares outcomes and work bounds. Use `--outcome accepted|abandoned` for a Change,
or `--run-outcome succeeded|failed|cancelled` with all four Run selectors. Work bounds
`--work-start`/`--work-end` can be supplied independently. To change a known outcome
or bound, supply `--correct-outcome` or `--correct-interval` and `--reason TEXT`.
A request combining an outcome and invalid bounds fails atomically. Delayed outcome
entry does not extend work. The result reports `economic_status: not_computed`.

`explain` returns the selected record, revision history, availability and the explicit
producer-assertion status. Revisions are grouped by kind and ordered through their
predecessor links from the original declaration to the latest correction, including
equal timestamps and arbitrary IDs. Change and Run inspection requires domain selectors;
other records use `--record-kind KIND --record-id ID`. Quote inspection verifies stored parameters and replays supported historical inputs
from one read snapshot; older claims without metadata remain not_computed. A future cutoff
cannot establish observed history and returns replay_unavailable. Export is a
consistent full bundle; it refuses an existing path and cleans up temporary output
on a handled failure. Hard process termination may leave an unreferenced temporary
file, but never a partial final artifact. Keep exports private.

Portable import/export modes cannot be combined with selectors or other operation modes.
Native provider imports and live collection remain unavailable. Read-only `check` is described below.
`quote` computes synthetic offline empirical amounts. Computed record inspection includes local receipt status, input replay
eligibility and `snapshot_only` completeness. Repository remainder reports are read-only.
A busy store reports a retryable error; wait for the other writer and repeat the
same request. Conflicting attribution must be resolved explicitly, not retried with
guessed identities. For recovery, use the consistent backup procedure in
[contracts](contracts.md#transactions-revisions-and-historical-limits).

Oversized observation or cutoff sequences are invalid portable input: imports exit
2 without a traceback or rejected payload values, and preserve existing stores.
Local transaction-sequence exhaustion also fails before new records are inserted;
retrying an already committed operation remains valid.

## Empirical Quote computation

Register the target Change before quoting. Explicit repository and economic selectors
and a caller operation ID are required. The minimum is a positive integer, default 20.

```sh
changecost --db demo.sqlite quote --repository-id demo --change-id C1 --operation-id quote-C1 --economic-kind monetary --unit USD --currency USD --basis billed
changecost --db demo.sqlite explain --record-kind quote --record-id QUOTE_ID
```

The first example returns unpriced when demo history is incomplete; missing coverage
is not zero. Supply `--minimum 1` only for a small synthetic demonstration, recording
that override. Identical operation retries preserve the original cutoff/result even
when new evidence arrives; conflicting reuse, including a settlement operation ID,
fails unchanged. See [empirical Quotes](quotes.md) for complete-cohort, feature and
replay semantics. These commands never collect provider data or write settlements.

## Presentation, errors and advisory budgets

Put global `--format human` before the command for readable values; `--format json`
(or no format option) preserves existing bind/quote/settle/explain success payloads.
Human presentation escapes terminal controls. Help/version remain offline text with
exit 0. Technical failures, including argument parsing, emit a safe diagnostic on
stderr, leave stdout empty and exit 2. JSON errors use `changecost/error-v1` with
`code` and `message`; rejected values, paths, SQL and tracebacks are not displayed.
New advice uses `changecost/check-v1`; these are internal preview tags.

```sh
changecost --db demo.sqlite --format human explain --record-kind quote --record-id QUOTE_ID
changecost --db demo.sqlite check --record-kind quote --record-id QUOTE_ID --budget 15 --economic-kind monetary --unit USD --currency USD --basis billed
changecost --db demo.sqlite check --record-kind quote --record-id QUOTE_ID --quantile p50 --budget 15 --economic-kind monetary --unit USD --currency USD --basis billed
changecost --db demo.sqlite check --record-kind computed_settlement --record-id SETTLEMENT_ID --budget 15 --economic-kind monetary --unit USD --currency USD --basis billed
changecost check --artifact bundle.json --record-kind quote --record-id QUOTE_ID --budget 15 --economic-kind monetary --unit USD --currency USD --basis billed
```

Replace the explicit record IDs with the selected immutable result. No implicit
latest selection or aggregation occurs. Budgets are finite nonnegative Decimal
strings with exact kind/unit/basis/currency identity, no rounding or conversion.
Monetary budgets require currency; nonmonetary budgets omit it. Quote p90 is the
default; p50 is explicit. Settlement quantiles are invalid. Equality and observed
zero are within_budget. All valid advice (`within_budget`, `over_budget`, `unknown`)
exits 0; technical failures exit 2.

Numeric advice requires a supported local typed computation receipt and exact
historical reproduction at the original cutoff. Supported local computations insert
their result at cutoff sequence plus one and at the cutoff time; check and both
historical inspectors verify these anchors against the result's own availability.
The generated origin store equals the cutoff store, and both recorded/effective
timestamps equal the cutoff time.
Its time cannot exceed the latest
committed local metadata timestamp, even when the wall clock has advanced; equality
and earlier historical cutoffs remain eligible. The same boundary applies to Quote
and computed Settlement explain. A populated store missing its committed metadata
timestamp is invalid for check even if metadata sequence is corrupted to zero or
no local receipt remains; record checks never substitute the wall clock for a missing
committed timestamp. Inspection cannot certify replay without that timestamp.
Computed Settlement receipts also bind the payload operation ID to the local receipt
primary key. Retrying an operation rejects a mismatched stored operation ID even
if another receipt references that result. Settlement reproduction includes
scope, subtotals, supporting inputs/exclusions, reasons and completeness. It also
reproduces the receipted same-Change predecessor at that cutoff across scopes,
preserving its ledger identity and ignoring later computations. A first ledger ID
remains opaque; this is deterministic replay, not generic payload authentication. Explain's
`inputs_available` alone cannot certify a value. Later evidence never replaces that
cutoff. Imported/legacy/artifact-only results remain unknown producer claims, even
with declared completeness. Unpriced, incomplete, incompatible, unsupported or
unreproducible results remain unknown on both sides of budget. Narrowed Run windows
retain the existing partial_change_scope reason. Results separate `declared` amounts
from verified `comparison`, expose provenance, scope/cutoff and reasons.

Check creates no record, receipt, revision, observation or store. Artifact mode
strictly validates the portable graph and performs no database access or import.
The executable [synthetic CI walkthrough](ci.md) demonstrates complete local values
and portable claims; provider support/calibration remain To-Validate.
