# Offline settlement preview

This checkout implements normalized import and economic computation for the unreleased
`0.1.0.dev0` feasibility study. Verification and accepted limitations are recorded in
[the change evidence](../openspec/changes/archive/2026-10-02-settlement-01-reconciliation/TDD_EVIDENCE.md).
The separately authorized finite Codex diagnostic reader is available below. Collection and budget enforcement remain unavailable. The separate
[empirical Quote operation](quotes.md) computes offline synthetic estimates.

## Import, bind, compute and explain

Save this synthetic fixture as `normalized.json`. It is the strict
`changecost/normalized-v1` input format, not a native provider export:

```json
{
  "schema": "changecost/normalized-v1",
  "repository_id": "demo",
  "batch_id": "example",
  "events": [{
    "source": {
      "repository_id": "demo", "provider": "synthetic", "surface": "fixture",
      "profile": "synthetic/v1", "namespace": "opaque", "identity_scope": "namespaced",
      "source_key": "event-a"
    },
    "component_key": "charge",
    "component": {"economic_kind": "monetary", "unit": "USD", "currency": "USD", "basis": "billed", "amount": "0.25"},
    "series": "usage", "lane": "delta",
    "start": "2026-09-29T08:00:00Z", "end": "2026-09-29T08:00:00Z"
  }]
}
```

```sh
changecost --db demo.sqlite bind --register-change --repository-id demo --change-id C1
changecost --db demo.sqlite bind --register-run --repository-id demo --change-id C1 --provider synthetic --surface fixture --run-id R1
changecost --db demo.sqlite settle --import-evidence normalized.json --repository-id demo
```

Use the returned `evidence_ids` selector as `EVIDENCE_ID` below. Every component of
the same source event shares that selector; bind it once. No time-based attribution
is performed.

```sh
changecost --db demo.sqlite bind --repository-id demo --provider synthetic --surface fixture --run-id R1 --evidence-id EVIDENCE_ID
changecost --db demo.sqlite settle --compute --repository-id demo --change-id C1 --operation-id calculation-1 --economic-kind monetary --unit USD --currency USD --basis billed
changecost --db demo.sqlite explain --record-kind computed_settlement --record-id RESULT_ID
changecost --db demo.sqlite explain --repository-remainder --repository-id demo --economic-kind monetary --unit USD --currency USD --basis billed
changecost --db demo.sqlite explain --export-artifact evidence.json
changecost --db imported.sqlite bind --import-artifact evidence.json
```

`RESULT_ID` is the computation's returned record_id. The example subtotal is `0.25`,
with provisional coverage: no terminal outcomes, work bounds or supported coverage
have been declared. Missing observations yield null, not zero. Distinct currencies,
units and billed/estimated bases require separate explicit scopes; no grand total is
created. Repository reports name `unknown_amount` when either bucket includes
unknown values. Identity-only Evidence without normalized economics is listed as
unresolved `missing_economic_evidence`: unbound identities are conservatively
potentially relevant, and bound identities are scoped by their Run repository.
They contribute no fabricated economic amount. Optional `--source-start` and `--source-end` must both be present and use
aware RFC3339 times. Source windows are start-inclusive/end-exclusive.

## Normalization and corrections

The input envelope requires schema, repository_id, batch_id and events. Unknown
nested fields and coercible amounts reject the entire batch without publication.
Amounts are exact signed decimal strings or null. `batch_id` identifies transport;
it does not affect duplicate detection. No arbitrary input metadata is retained.

Each event requires source, component_key, component, series, lane, start and end.
`baseline_zero` defaults false. A replacement additionally supplies `replaces`
(a complete SourceLocator) and `correction_reason`; both are required together.
Only replacements are supported: replacement `0` is a documented reversal, not a
negative adjustment added to the original. Known currency cannot change; a null
currency with unknown amount may be explicitly resolved by a later replacement.

SourceLocator names repository_id, provider, surface, profile, namespace and
identity_scope. A namespaced identity requires source_key; a file identity instead
requires a lowercase SHA256 file_digest and nonnegative integer ordinal. Use opaque
namespaces to separate accounts/streams without retaining raw account identifiers.
Core binding identities use a deterministic hash of this full locator; economic
records retain the locator and separately identify component_key. Exact replay of
file/row identities does not deduplicate ambiguous overlap between different files.
Such overlapping partitions are excluded and reported as unresolved.

Semantic repeats ignore batch identity/order and preserve the first record and
availability. Conflicting payloads fail atomically. Replacement chains retain every
original value; missing targets stay pending until their source locator arrives.
Cycles, forks, incompatible economic/window/source identity and conflicting explicit
bindings reject rather than choosing by arrival order. A chain can use its existing
explicit binding; it cannot move a charge to a different Run.

A Change computation excludes correction chains explicitly attributed to other
Runs before applying correction and temporal-lane policy. All Runs belonging to
the requested Change remain in scope, so mixed attribution within that Change
still blocks unsupported snapshot selection. Chains without an explicit binding
remain potentially relevant. Foreign chains contribute neither inputs nor exclusions.
Retained chains record consulted explicit bindings even while a correction target
is missing. Repository reports continue to consider all Runs.

Normalized import indexes existing Evidence identities once per transaction,
preserving the first matching core record and updating the index for new records.
Economic graph validation similarly indexes Evidence and Run bindings once per
validation and declared Run membership once per computed result. Coverage and
computed membership validation reuse those indexes.
Correction subject validation visits each present chain node once, including
inherited bindings and pending predecessors. File-overlap detection sorts windows
and tracks the furthest endpoints for two distinct digests, preserving inclusive
point boundaries and namespaced/file ambiguity. Computation builds full-reference
Run, lifecycle-leaf, coverage and event indexes once per snapshot. Cutoff pruning
propagates unavailable dependencies through a reverse index once per edge.
Coverage summarizes distinct Evidence references and point extrema once per Run;
each assertion separately checks its own declared evidence and point boundaries.
Assertions are not combined to manufacture complete coverage. Per-assertion work
is bounded by that assertion's declared references, including shared-Evidence
components.
These bounds apply to these steps, not to total pipeline complexity.

## Temporal and coverage policy

Deltas and cumulative snapshots are never added together. Supported synthetic
snapshots require one exact Run window, an explicit zero baseline and consistent
attribution. Unknown reset/baseline, overlapping snapshots, partial windows and
unsupported mixed lanes stay unresolved. No subtraction, interpolation or proration
manufactures a narrower amount.

Only the closed synthetic fixture policy can establish full-change eligibility:
provider `synthetic`, surface `fixture`, profile/policy `synthetic/v1`, namespace
`opaque`, series `usage`, component_key `charge`, billed monetary USD. Every linked
Run must have a terminal outcome and known work bounds, supported SourceCoverage
with explicit evidence and finality, and known economics covering its source scope.
The Change must be terminal and its Run set nonempty. Relevant unbound evidence,
unknown amounts/applicability, missing intervals or contradictory work events block
full-change status. Even zero-duration work needs affirmative coverage and evidence.
A `source_coverage` record enters via strict portable import, with the fields in
[contracts](contracts.md); labels alone never approve a real source.

The synthetic result remains explicitly synthetic. Other profiles may contribute
provisional known amounts but never acquire provider verification from a label,
policy file or CLI flag. Accepted and abandoned Changes and failed/cancelled retries
retain their expenditure.

## Revisions, limits and recovery

Computation holds a SQLite writer transaction, captures one committed input cutoff,
and atomically writes the result and local operation receipt. Retry an identical
operation_id after a lost response: the original result and cutoff return even if
new evidence has arrived. Reusing it with different selectors fails; a new operation_id
captures a new revision. Imported computed results remain producer claims. Inspection
always labels completeness as `snapshot_only`, never current eligibility. It checks
the exact immutable payload, local operation receipt, cutoff bounds and all input
dependencies in one read transaction with one graph validation.
The result's insertion sequence must equal cutoff sequence plus one and its local
availability time must equal cutoff time, matching the atomic supported producer.
Later unrelated history cannot authorize a replacement cutoff.

The local computed ledger is separate from legacy Settlement claims. Its ledger_id
is an opaque local chain identity; a portable origin ID cannot create a local receipt.
Backups preserve receipts and original cutoff history. Portable imports establish
new destination availability and cannot reproduce the original local computation.

Input is limited to 32 MiB and 100000 economic rows; computation accepts at most
100000 economic records per repository snapshot and 4096 aligned decimal digits.
A result exceeding a bound fails without publishing a revision. Arithmetic uses
integer coefficients and decimal exponents, independent of ambient Decimal precision,
with no float, SQL sum, display rounding or silent truncation. Source strings remain
unchanged; result scale reflects the selected exact inputs.

The internal SQLite layout is 2, independent of package `0.1.0.dev0` and the evolving
`changecost/v1` artifact label. Layout 1 is rejected unchanged. Keep a consistent
backup and matching earlier checkout; export there and import into a separate fresh
store for preview experimentation. This creates new destination history. Retain the
old backup/checkout for original cutoff replay. No automatic migration, downgrade,
release or cross-checkout compatibility promise is provided.

## Historical budget advice

Check additionally reproduces all material reconciliation fields at the original cutoff.
Both check and computation inspection require its time to be no later than the latest
committed metadata timestamp; an advanced wall clock cannot grant authority. Equality
and older historical cutoffs remain eligible. Missing timestamps cannot certify replay,
and a populated store with no committed timestamp returns check's safe technical error.
Input availability alone is insufficient. Incomplete known subtotals above or below budget
and narrowed partial_change_scope results remain unknown; see [CLI advice](cli.md#presentation-errors-and-advisory-budgets).

Selected local result availability must not exceed the committed metadata sequence.
Check and both computation inspectors validate that strict integer bound before
receipt/version trust decisions, returning safe technical errors for unavailable
selected records and preserving store bytes. The original cutoff-to-insertion
anchor remains separate: its valid N→N+1 relation cannot authorize a result beyond
the committed snapshot. Equality and later committed appends remain supported;
portable artifact advice never consults the local store.

## Import the approved finite Codex diagnostics

```sh
changecost settle --repository-id repo --import-codex selected.jsonl \
  --source-profile codex-desktop-0163-finite-diagnostics \
  --source-sha256 550db3df1e6f13f55744965c24db1825f4abd59443d9bd88600350ee25ba1a1f
```

Only the independently approved exact snapshot is eligible. This command imports
16 response Evidence events and 96 separate category facts. Other files, appends,
formatting changes, Work exports and unreviewed resumes reject. A byte-identical
regular copy replays the same events. The receipt returns local Evidence selectors,
counts and diagnostic codes without source paths or private identities. Use the
existing exact `bind --evidence-id` operation later; import never infers a Run.

The native mode requires all four selectors shown above and excludes normalized
import, computation, Change, Run and lifecycle selectors. Mode validation precedes
source acquisition and persistence. Sources are read-only regular files with no
symlink in any traversed component. One descriptor supplies bounded hashed and
parsed bytes. Limits are 10 MiB, 10,000 records, depth 32 and 4096 token digits.
Duplicate keys, nonfinite numbers and malformed records reject atomically. Pre/post
file metadata detects ordinary changes; it cannot prove absence of an adversarial
concurrent rewrite. Select a stable snapshot. No source is collected or modified.

These are partial serialized diagnostics. Served model, request time, backend
presence, completeness and finality remain unknown, including serialized zeros.
Legacy snapshots and request categories are never added together. Manual binding
creates no EconomicEvidence, SourceCoverage, demand observation or policy. Numeric
financial and demand eligibility retain their existing synthetic-only guards.

## Import approved Claude project diagnostics

The explicit offline reader supports the approved Claude Code 2.1.215 project
JSONL grammar. Choose one existing file and its SHA-256; no scanning or collection
occurs. Source version declarations do not authenticate arbitrary files.

```sh
changecost settle --repository-id repo --import-claude-project selected.jsonl \
  --source-profile claude-project-2-1-215-request-stages \
  --source-sha256 SHA256_OF_SELECTED_FILE
```

The result returns exact `evidence_refs` for later manual Evidence-to-Run-to-Change
binding. Import cannot be combined with binding or other settlement modes. The
four distinct nullable categories are input, output, cache creation and cache read.
Missing remains null; zero remains zero. They are not summed into a total.

An initial partial A stores four NativeUsage records. A later snapshot retaining A
and containing terminal B appends four corrections. An initial A+B snapshot stores
both cohorts at the current import time, eight records with four predecessors;
only B is current. Terminal-only first import stores four originals and rejects
any later unseen partial, even beside known B. Accepted A-only, B-only and A+B replay
without writes after refinement, including after reopen and current-version recovery.
Changed quantities, absent retained A, forks or conflicting identities reject the
whole batch. Supported terminal reasons normalize only after snapshot validation.

`fact_count` counts four selected categories per event. `inserted_fact_count`
counts newly stored history records, including corrections. `corrected_fact_count`
counts those new records with predecessors. `replayed_fact_count` counts categories
of fully replayed events. None of these counters measures tokens or billed money.

Only allowlisted metadata persists. Paths, raw source identifiers, content and stop
reasons do not. Reads reject symlinks, nonregular files, changed acquisition metadata,
wrong hashes, more than 10 MiB, 10,000 records or nesting depth 32. Stable-read checks
are not protection against every adversarial writer. Diagnostics use closed codes
and optional record ordinals.

Coverage, backend finality, lineage and interval remain unknown. No demand learning,
economic settlement, calibration or compatibility with 2.1.257, 2.1.275, other Desktop versions,
IDE or SDK streams follows. Preserve an exported bundle before rollback; older
binaries need not accept the added provider association. Current-version recovery
preserves first acquisition/admission and correction history.

### Desktop 2.1.308 root terminal diagnostics

Select `claude-desktop-2-1-308-root-terminal` with the same command and source hash.
Every contributor must declare version `2.1.308`, entrypoint `claude-desktop` and
`isSidechain=false`, with no `agentId` member. Only `end_turn` and `tool_use` are
supported. Each of the four categories must be present as an exact nonnegative
integer. Literal zero remains zero; missing, null, bool and negative values reject.
Cache creation duration components are not added to the aggregate category.

Desktop imports four final serialized-source facts per event. Partial stages,
children, quantity changes and corrections are unsupported. Unknown row types or
keys and malformed user/metadata/API blob shapes reject the whole batch. API blob
messages are opaque JSON values with no immediate `usage` member when an object;
no recursive counter extraction occurs. All records are validated before writes.

Semantic replay from another path or hash preserves the first Evidence, acquisition,
admission and timestamps, including after reopen and bundle recovery. Event identity
excludes version and profile. Same-event observations under different profiles reject
even when all quantities agree. This prevents a second contribution from inheriting
another profile's approval. Existing 2.1.215 correction support is unchanged.

The approval binds [native observations](providers/evidence/claude-desktop-2-1-308-native-observations.md)
and [external producer association](providers/evidence/claude-desktop-2-1-308-producer-binding.md).
Their frozen draft headers record their original stage; the canonical register now
contains independent approval. External Desktop build metadata is not a runtime
build check. Broader Desktop lifecycle, complete coverage, served model, backend
finality, ownership, demand, money and calibration remain unproved.

Claude project import accepts UTF-8 JSONL, with an optional UTF-8 BOM per line
as a compatibility extension.
UTF-16/32 and malformed UTF-8 reject before persistence. Byte-delimited JSONL
lines retain valid Unicode line characters inside strings; escaped quotes do not
waive the depth-32 bound. This applies to both approved Claude profiles.

The later independently approved q4 revision uses mapping
`claude-desktop-root-terminal-r2`. It adds closed `cost-state` and `mode` metadata
exclusions while retaining every contributor and accounting constraint. Opaque
`modelUsage`, costs, duration, line counts and mode values grant no native facts,
billing or demand authority. Unexpected keys or present message/direct usage still
reject. This replaces the unpublished q3 candidate; its canonical profile, proof,
asset and source statements remain frozen in local history. No real q3 Desktop
facts were stored. Authored prototype bundles have no compatibility promise.
