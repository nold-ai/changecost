# Offline lifecycle and settlement CLI

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
other records use `--record-kind KIND --record-id ID`. Quote inspection reports input
eligibility, never validates the producer's economic calculation. A future cutoff
cannot establish observed history and returns replay_unavailable. Export is a
consistent full bundle; it refuses an existing path and cleans up temporary output
on a handled failure. Hard process termination may leave an unreferenced temporary
file, but never a partial final artifact. Keep exports private.

Portable import/export modes cannot be combined with selectors or other operation modes.
`quote`, `check`, native provider imports, collection and money estimation remain
unavailable. Computed record inspection includes local receipt status, input replay
eligibility and `snapshot_only` completeness. Repository remainder reports are read-only.
A busy store reports a retryable error; wait for the other writer and repeat the
same request. Conflicting attribution must be resolved explicitly, not retried with
guessed identities. For recovery, use the consistent backup procedure in
[contracts](contracts.md#transactions-revisions-and-historical-limits).

Oversized observation or cutoff sequences are invalid portable input: imports exit
2 without a traceback or rejected payload values, and preserve existing stores.
Local transaction-sequence exhaustion also fails before new records are inserted;
retrying an already committed operation remains valid.
