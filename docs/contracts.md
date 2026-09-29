# Offline contracts v1

ChangeCost's unreleased `changecost/v1` transport uses Pydantic 2 and SQLite schema
1. The executable field definitions are in [models.py](../src/changecost/models.py).
This is a local record contract, not provider verification or a financial algorithm.
See [CLI examples](cli.md) and [implementation evidence](../openspec/changes/core-02-change-run-contracts/TDD_EVIDENCE.md).

## Wire format

A bundle contains `schema`, `source` (store_id, aware UTC at, committed sequence),
`records` and optional `observations` (default empty). Every record explicitly names
`schema: changecost/v1`, `kind`, `record_id`, `origin_store_id`, `recorded_at` and
`effective_at`. Unknown members, kinds and versions, duplicate JSON keys, numeric
or naive timestamps and NaN/Infinity reject the entire import. RFC3339 offsets are
normalized to UTC; timestamp precision is at most six fractional digits.
Identifiers are nonblank exact strings; case and surrounding whitespace are not
silently changed. `RecordRef` is `{kind, record_id}` and resolves to one immutable
record. Run domain selectors always use all four RunRef fields:
`repository_id`, `provider`, `surface`, `run_id`. A Run RecordRef resolves to that
complete tuple; bare provider run IDs never resolve a reference.

| kind | Fields beyond the common envelope |
| --- | --- |
| change | repository_id, change_id, features; optional commit_ref, pr_ref |
| run | ref (RunRef); optional observed_start, provider_session_id, trace_id |
| evidence | provider, surface, profile, identity_scope; source_key for namespaced identity, or file_digest (64 lowercase hex digits) and ordinal (nonnegative integer) for file scope |
| run_binding | run (RunRef), change (RecordRef), method, source_refs |
| evidence_binding | evidence (RecordRef), run (RunRef), method, source_refs |
| outcome | subject (Change/Run RecordRef), outcome; optional previous (Outcome RecordRef), reason |
| interval | run (RunRef), nullable start/end, method, source_refs; optional previous (Interval RecordRef), reason |
| quote | change, state, p50, p90, sample_count, cohort, algorithm_version, cutoff, inputs; optional reason, features |
| settlement | change, components, completeness, scope, coverage, inputs, unknown_reasons; optional previous (Settlement RecordRef) |

`method` defaults to `manual`; imported `verified_provider` remains a producer's
assertion. `source_refs` defaults to empty. No provider profile is approved by import.
Outcomes are accepted/abandoned for Changes and succeeded/failed/cancelled for Runs.
An absent outcome means open; a terminal outcome does not imply known cost.
Each coverage entry names a complete RunRef, an outcome revision, an interval
revision and evidence references. Coverage requires each Run to be bound to its
Settlement Change and each evidence record to that Run; these mappings participate
in historical dependency checks. Import validates graph integrity, not economic
completeness. Quotes and Settlements can be inspected and replayed as records;
no estimator or reconciler runs in this capability.

Features have `version: features/v1`, captured_at/recorded_at equal to Change
registration, and three nullable fields. ASCII whitespace is stripped and ASCII
letters lowercased only for these fields; blank becomes null.

| Field | Allowed nonnull values |
| --- | --- |
| change_shape | bugfix, feature, refactor, docs, maintenance, other |
| trajectory | single-pass, iterative, investigative |
| execution_profile | copilot-cli, copilot-ide, cursor-cli, cursor-ide, mixed |

## Exact components and unknowns

Every component requires economic_kind (`monetary` or `nonmonetary`), unit, basis
and amount. Amount is a finite decimal **string** or null, retained exactly,
including trailing zeros and exponent notation. Currency is a three-uppercase-letter
code for known monetary amounts; it must be null for nonmonetary quantities.
Codes are syntactically checked, not verified against a currency registry.
Units/bases are opaque explicit strings, with no conversion or inference.

```json
{"economic_kind":"monetary","unit":"USD","basis":"billed","currency":"USD","amount":"0.100000100"}
```

```json
{"economic_kind":"nonmonetary","unit":"provider_credit","basis":"reported","currency":null,"amount":null}
```

Known nonmonetary quantities use strings such as `"100"`, `"2"` or `"50"`, not
JSON numbers. Null is unknown, never zero. Quotes require matching p50/p90 component
identities; priced quotes require samples and ordered known quantiles; unpriced
quotes require null quantiles and an explicit reason. Settlement completeness
(`provisional`/`reconciled`) is retained as an origin claim.

## Transactions, revisions and historical limits

The operator owns the local database. Each connection enables foreign keys and uses
explicit transactions; writes use BEGIN IMMEDIATE and a five-second busy timeout.
Records are stored as JSON TEXT, never SQLite numeric amounts. New stores are
built in memory and published without overwriting an existing file. An import
validates the whole combined graph before committing. References may be in any
bundle order; missing references, cycles, forks, changed subjects and conflicting
identities reject the operation. Identical replay preserves original records and
first local availability. An identical Run registration remains a no-op after its
Change becomes terminal; genuinely new Runs require an open Change.

Known interval bounds satisfy start <= end and cannot postdate declaration.
Inspection groups revision chains by kind and follows their predecessor references
from the original declaration to the latest revision; record-ID or timestamp sorting
does not establish correction order.

Outcome/interval changes append revisions; changing an existing outcome or known
bound requires a correction flag and reason through the CLI. Filling a missing
bound requires no correction. Outcomes never synthesize work times.

Python callers submit these fields as one immutable `LifecycleDeclaration` to
`operations.declare(store, target, declaration)`. The request groups the paired
outcome and interval updates inside the same transaction. Identical retries append
no revisions; a rejected correction preserves both histories. This request is an
internal operation input, not another portable record or wire schema.

Each committed record has destination-local `available_at` and transaction
`sequence`, separate from imported origin observations. A captured cutoff includes
store_id, time and committed sequence. Eligibility checks every referenced dependency
against sequence and availability/recorded/effective times. A writer begun before
but committed after the captured snapshot is excluded. This is a snapshot boundary,
not a claim of an exact physical commit timestamp. Clock regression fails writes
and snapshot capture; it cannot detect arbitrary external tampering or clock jumps.
Foreign, time-only or future cutoffs cannot prove local replay. A cutoff time must
not exceed the current committed snapshot's time, even when its store ID and
sequence are otherwise valid. Importing old evidence now
never reconstructs earlier destination knowledge.

`Store.backup(new_path)` uses SQLite's consistent backup API and preserves identity,
sequence and local history. Recover into a separate path with no active writer;
keep the original until the restored copy is checked. Portable import creates a
distinct destination history and cannot substitute for backup. Only schema 1 is
supported; newer schemas are rejected without mutation, with no automatic downgrade.
No upgrade from an older product schema exists yet.

## Privacy and compatibility

Use synthetic, minimal identifiers/reasons; do not put secrets into allowed strings.
Prompt/transcript/raw-payload fields are absent and rejected. Diagnostics suppress
untrusted field names as well as values, because either can contain private text.
This is an allowlist, not a content classifier. Imported data never executes URLs,
paths or instructions. Databases, exports and review artifacts stay outside packages.
Keep package version `0.1.0.dev0`; contract versioning is independent. An incompatible
wire change requires a new schema and an explicit migration policy.
