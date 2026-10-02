# Core-02 preparation evidence

Date: **2026-09-29 (Europe/Berlin)**. Status: **locally prepared / unpublished**.
This is planning/research evidence, not implementation or product TDD.

## Baseline and archive-first review

Fresh main was fetched and fast-forwarded at **08:42:06 +02:00**, SHA
`cb6ff3b2e218466c8633463928e7c94b1cf31b22`. The preparation branch is
`codex/prepare-core-02-change-run-contracts`. No concurrent worktree or unrelated
working-tree edits were present. Issue [#11](https://github.com/nold-ai/changecost/issues/11)
remains the selected identity; no competing change or issue is introduced.

Before contract research, OpenSpec CLI **1.13.2** archived:

| Delivered change | Delivery evidence | Archive/spec result |
| --- | --- | --- |
| core-01-python-foundation | [PR #22](https://github.com/nold-ai/changecost/pull/22), merged 2026-09-28; final head c70ebcf; [Linux run 36462266628](https://github.com/nold-ai/changecost/actions/runs/36462266628) | [Archived record](../2026-09-29-core-01-python-foundation/tasks.md); seven requirements in [main spec](../../../specs/python-foundation/spec.md) |
| dev-workflow-01-bounded-review | [PR #24](https://github.com/nold-ai/changecost/pull/24), merged 2026-09-29; final head 7af6666; [Linux run 36517806157](https://github.com/nold-ai/changecost/actions/runs/36517806157) | [Archived record](../2026-09-29-dev-workflow-01-bounded-review/tasks.md); 25 requirements in [main spec](../../../specs/bounded-review-session/spec.md) |

Both archives used `openspec archive <id> --yes --json`, with validation and spec
updates enabled. All artifacts existed; task closure was reconciled against final
checks, acceptance and limitations first. The foundation's four host/controller/
loader findings have explicit maintainer accepted-risk dispositions linked in its
archived tasks. They were not fixed or withdrawn. Bounded-review task 4.3 uses its
explicit limitation-recording alternative: concealed-case calibration is unavailable,
the advisory model lane was not adopted, and no savings are claimed. Its legacy
receipt remains recovery-required; no allowance was reset.

All archived requirement/scenario text matches its main spec after whitespace
normalization. OpenSpec inserted one separating blank line in the review spec.
Purpose sections are populated; no generated TBD placeholders remain. Relative
links and ownership/index paths were repaired after the moves. Source feasibility
is deliberately **not archived**: tasks 2.1/2.2 still lack inspected provider evidence,
despite closed #9 and merged research PR #21. Eight active changes remain.

## Requirement review against current code

`src/changecost` contains only the existing CLI help/version entry point, not models,
SQLite storage, provider parsers or economic operations. The Pydantic dependency
selected by planning is absent from both project metadata/lock and the project
runtime. Typer is locked/installed at **0.27.2**, uv at **0.12.19**; the project
version remains **0.1.0.dev0**. No version bump or dependency installation was made.

| Requirement group | Evidence/assessment | Reconciliation |
| --- | --- | --- |
| Foundation prerequisite | Confirmed: #10 closed, PR #22 merged, native #11 blocked-by edge names #10 | Replace obsolete no-runtime assumption; retain delivered foundation guarantees |
| Lifecycle and stable bindings | Specified, unimplemented | Distinguish new Run rejection from identical retry after terminal outcome; require same-repository Change binding |
| Full RunRef and evidence mappings | Specified, unimplemented | Preserve exact identities and file-scoped limits; use synthetic portable records before native adapters |
| Features and work intervals | Specified, unimplemented | Preserve immutable normalization and reasoned corrections; core emits revisions, later reconciliation evaluates coverage |
| Store-local history | Specified, with timestamp/commit race gap | Add committed snapshot boundary and explicit unavailable replay; preserve destination-local availability |
| Economic values | Specified, but storage/coercion failure cases missing | Require finite decimal strings, TEXT persistence, null/unit/currency separation and no arithmetic during serialization |
| Portable records | Round trip specified, CLI and strict input boundary incomplete | Define bind import, explain inspection/export, forbidden extras/duplicates, acyclic references and private diagnostic handling |
| Transactions | Atomicity specified, failure paths incomplete | Define busy/commit rollback, migration/newer-schema rejection, restart retry and backup distinction |
| Quote/Settlement contracts | Records overlap with later algorithms | Core validates/preserves structure and provenance; #12 computes reconciliation, #15 produces quotes, #16 adds budget checks |
| CLI/regression surface | Existing test asserts settle absent from help | Replace that assertion only when settle is delivered; retain read-only help/version/errors, offline installed-wheel and unimplemented quote/check tests |

No existing main requirement needs a MODIFIED delta: the new operations preserve
foundation behavior for help, version and invalid invocation, and use the current
review workflow. The change adds `change-run-contracts` only. All implementation
tasks remain unchecked, split into scenario-derived tests, implementation and
adjacent documentation rather than claiming preparation completes behavior.

## Primary-source research and impact

All sources below were accessed **2026-09-29 (Europe/Berlin)**. These are
implementation decisions derived from documentation, not provider capability claims.

- [Pydantic standard types](https://docs.pydantic.dev/latest/api/standard_library_types/)
  and [model configuration](https://docs.pydantic.dev/latest/api/config/): Decimal
  serializes to JSON strings, but JSON strict mode alone does not enforce the
  desired decimal input shape; datetime parsing permits more forms than this
  contract. Unknown fields need explicit rejection. Use v2 models with field
  allowlists and prevalidation, not default coercion. Exact compatible lock and
  matrix proof belong to implementation; latest documentation does not establish
  installed compatibility.
- [Python 3.11 sqlite3](https://docs.python.org/3.11/library/sqlite3.html): use
  explicit SQL transactions with isolation_level=None for the minimum supported
  Python. Avoid relying on newer Connection.autocommit APIs. `executescript`
  can commit an existing transaction before its script; migration execution must
  preserve the intended atomic boundary. Connection backup supports a consistent
  store copy; portable import has different history semantics.
- [SQLite transactions](https://www.sqlite.org/lang_transaction.html) and
  [isolation](https://www.sqlite.org/isolation.html): writes serialize and
  BEGIN IMMEDIATE can return SQLITE_BUSY; another connection cannot see uncommitted
  records. The application must handle contention/failed commits and pin historical
  read membership, rather than equating an in-transaction timestamp with visibility.
- [SQLite type affinity](https://www.sqlite.org/datatype3.html): numeric affinity
  can coerce a numeric string to REAL. Store exact decimal text as TEXT and retain
  explicit economic identity; do not sum different units in storage/serialization.
- [SQLite foreign keys](https://www.sqlite.org/foreignkeys.html): enable and verify
  enforcement per connection before a transaction. A schema declaration alone is
  insufficient proof that broken references are rejected.
- [Python JSON](https://docs.python.org/3.11/library/json.html): default decoding
  accepts repeated names and nonfinite values. Reject duplicates using an object
  pairs hook and nonfinite constants before model validation; use allowlisted
  diagnostics rather than echoing potentially private invalid values.
- [Python Decimal](https://docs.python.org/3.11/library/decimal.html): constructing
  from a binary float preserves that float's approximation. Parse wire decimal
  strings directly, preserve stored scale and defer any explicit display rounding.
- [Typer callbacks](https://typer.tiangolo.com/tutorial/commands/callback/): the
  existing root callback must continue through subcommand dispatch while preserving
  root help/version/bare-invocation behavior. Prove installed command behavior when
  bind/settle/explain become real commands; do not add successful placeholders.

The scope needs no renewed provider-interface research or private export inspection:
it consumes synthetic portable reference contracts, and no provider profile is
promoted to supported. Native adapters retain their separate feasibility gate.

## Local research probes

A disposable standard-library probe ran with installed **Python 3.11.15** and
**3.13.14**, both reporting **SQLite 3.53.1**. Both runs passed committed-read
visibility, writer contention, rollback and enabled foreign-key rejection checks.
A NUMERIC column converted `0.12345678901234567890123456789` to
`0.12345678901234568`; a TEXT column retained the input exactly. Default JSON
kept the last duplicate member and accepted NaN. Decimal-from-float differed from
Decimal-from-string. These observations substantiate the design's failure cases;
they are not tests of the unimplemented product or Pydantic.

Reproduction script and outputs are retained locally under
`.changecost/workflow/core-02-change-run-contracts/stdlib-probe.py`,
`probe-3.11.log` and `probe-3.13.log`. They use only synthetic values and temporary
SQLite stores. No real billing data, telemetry or model request was made.

## Checks, issue alignment and limitations

Preparation strict validation passed for all 8 active changes and 2 main specs.
The preparation aggregate passed 12 leaves and 695 tests plus 4 subtests; its
required review leaf remained incomplete because all 10 analyzers reported an
unsupported macOS controller. Issue #11 was updated and read back; native parent,
dependency and private-project relationships were preserved. A strict
schema pass does not establish product correctness, and local unavailable capsule
analysis cannot be described as full assurance. Remote links remain on the actual
published baseline until a preparation branch/PR is published.

Confidence: high in the dependency and archive evidence; medium in the unimplemented
contract design until scenario-derived tests and the supported Linux matrix run.
No paid infrastructure or live collection is required. The largest implementation
risk is historical cutoff/revision correctness; delayed-commit, restart and clock
cases must pass before it is claimed. Strict decoding prevents value/privacy loss;
transaction failure probes protect partial-state recovery. Pydantic lock selection
and real installed-wheel operations remain implementation gates.

Rollback this planning diff to restore prior plans/archive locations without touching
runtime data. The archive directories retain original implementation/review evidence.
Later runtime rollback must use a compatible consistent database backup; portable
reimport cannot recreate another store's historical knowledge. The maintainer subsequently authorized implementation and verification on
2026-09-29. The preparation was carried directly into the feature branch; no
plan-only PR or stash was created. See [implementation evidence](TDD_EVIDENCE.md).
