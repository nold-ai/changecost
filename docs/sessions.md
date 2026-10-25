# Record and compare your sessions

Before work, start a new session with a stable task kind and context. Use the same
labels only for work you judge comparable. This local experiment has separate manual and Codex provisional targets.
Selected finite native diagnostics can also be attached separately. None calculates billing.

```sh
uv run --locked changecost --format human session start work-01 --task-kind bug-fix --context changecost/python --guess 12000
```

Read `forecast.amount`, `source`, `sample_count`, `summary` and `inputs` before
starting the work. With no comparable history, `--guess` supplies a cold-start
estimate. Without a guess, the estimate is unknown. With history, its median
replaces the fallback guess. The original guess remains in the saved forecast.

After work, replace the example quantity below with your measured session total:

```sh
uv run --locked changecost --format human session finish work-01 --tokens 10000 --outcome completed
uv run --locked changecost --format human session show work-01
```

Use `--outcome failed` or `--outcome abandoned` for those measured attempts.
Their totals train later comparable sessions and their outcome counts are disclosed.
If the quantity covers only part of the session, add `--coverage partial`.
Partial measurements remain inspectable but do not train or receive full-total errors.
A declared session total is your assertion of coverage, not independently verified truth.

## Capture a new Codex session without typing totals

Use a fresh Codex thread for each attempt when possible. The target is the selected
thread's source-reported lifetime cumulative counter. A long-running thread includes
work before the ChangeCost start. No baseline is subtracted, and the counter is not
verified actual task or change usage. Keep task kind and context consistent only
for work you judge comparable. Heterogeneous cohorts can worsen forecasts.

Before work, explicitly select the Codex target:

```sh
uv run --locked changecost --format human session start native-01 --source codex --task-kind bug-fix --context changecost/python --guess 12000
```

After work, select that thread's local file and its repository. Mark the attempt's
outcome yourself. This does not establish provider finality:

```sh
uv run --locked changecost --format human session capture-codex native-01 --file /selected/new-codex-session.jsonl --repository-id my-repository --outcome completed
uv run --locked changecost --format human session show native-01
uv run --locked changecost --format human session start native-02 --source codex --task-kind bug-fix --context changecost/python
uv run --locked changecost --format human session history --source codex --task-kind bug-fix --context changecost/python
```

The human summary shows the estimate, its guess or cohort source, sample count,
reported lifetime counter, whether the estimate was high or low, absolute error,
relative error, capture revision and explicit outcome. Coverage, completeness,
finality and subagent inclusion remain UNKNOWN. Producer claims are unverified.
Remove `--format human` for full safe JSON, exact ratios, source hashes, target
semantics, immutable capture revisions and frozen forecast inputs.

The separate `codex-desktop-session-counter/v1` mapping supports observed
`Codex Desktop` producer versions `0.163.0-alpha.10.2` and `0.163.0-alpha.11.2`,
with `vscode` or `subagent.thread_spawn` source metadata. The versions share one
provisional target family, while captures and forecast inputs retain the actual
version and source kind. Unsupported producers or shapes reject. These local
observations do not authenticate a producer or approve its accounting semantics.

The reader streams only the explicit stable regular file through no-follow path
traversal. Its separate limits are 128 MiB, 100,000 JSONL rows and JSON depth 32.
Duplicate members, nonfinite numbers, excessive numeric lexemes, malformed counters,
missing identity and decreasing counters reject. Only the latest cumulative
`total_token_usage.total_tokens` supplies the quantity. Repeated snapshots,
overlapping categories, `last_token_usage` and request/response records are never
added. All category values must be nonnegative signed 64-bit integers, excluding
booleans. No raw IDs, paths, filenames, prompts or source text are saved.

Each provider session identity binds to one local attempt globally. A renamed copy,
changed repository label or supported producer version cannot create a duplicate
training attempt. Repository association binds on first capture. Retrying identical
selected bytes and the same operation payload creates no new event. A source file
that has grown is a new payload, even at the same path.

To capture a resumed thread, inspect the latest revision, then provide that
predecessor and a reason:

```sh
uv run --locked changecost --format human session capture-codex native-01 --file /selected/new-codex-session.jsonl --repository-id my-repository --outcome completed --revision 1 --reason "Captured resumed thread"
```

The earlier byte prefix must match exactly. Shrinks, rewrites, counter decreases,
changed identity/repository and stale conflicting predecessors reject atomically.
Captures remain immutable. A retry of an older successful operation with identical
old bytes returns its original `operation_revision`; the report still shows the
latest capture. A correction can change an outcome on identical source bytes or
record appended bytes without a new counter. It still supplies one current sample.

Native forecasts use the latest capture once per attempt in the same exact
context, task kind and provisional target. Failed and abandoned attempts also train.
Unestimated captures train later forecasts but have no retrospective error. History
discloses the learning count separately from evaluated-error count. Corrections
update the attempt's current error and future cohorts without rewriting old
forecasts. Percentage error is unavailable for a zero target. No accuracy
improvement or calibrated accuracy is claimed.

Manual finish/correct cannot measure a Codex target, and capture-codex cannot measure
a manual target. Start retries must retain the original source, labels and guess.
Default history remains manual; use `--source codex` for the separate provisional
history. Core demand, billing, calibration, canonical profiles and approval counts
receive no authority from this experiment. See the
[provisional implementation evidence](../openspec/changes/dogfood-03-codex-provisional-loop/TDD_EVIDENCE.md)
for actual focused checks and remaining acceptance work.

## Attach the approved finite Codex observations

For an existing session, explicitly select the source file and repository:

```sh
uv run --locked changecost --format human session observe-codex work-01 --file /selected/codex-session.jsonl --repository-id my-repository
```

No manual token total is required for this observation. The command resolves the
packaged profile and expected digest, then uses the same acquisition, strict parsing,
producer and exact admission checks as the existing core importer. It admits only
`codex-desktop-0163-finite-diagnostics`, whole-file SHA256
`550db3df1e6f13f55744965c24db1825f4abd59443d9bd88600350ee25ba1a1f`.
This finite approval covers 16 selected requests and 96 category facts. New sources,
format changes, appends and resumed sessions remain unadmitted. There is no file
discovery, watcher or automatic association.

Read `native_diagnostics` separately from the manual forecast, measurement and
error fields. Its `manual` is false and its unit is `source_category_tokens`.
The six independent categories preserve their own request identities, quantities,
source/profile/approval/projection digests, mapping and producer provenance, and
unknown coverage, completeness, finality and backend presence. The snapshot retains
hashed lineage, never raw IDs, paths, filenames, prompts or source text.
The outer `manual_scope` and `unit_scope` identify the manual fields they describe.

Categories overlap. Neither their sum nor a reconstructed session total is allowed.
These finite diagnostics keep `session_total` and `total_error` null, and `learning_eligible` stays false
with `native_partial_diagnostics` as the exclusion reason. A native-only session also
has that reason for its manual total-error exclusion. It contributes no measurement
or future cohort sample. An independently entered manual total keeps its existing
manual authority, error calculation and learning eligibility. Attaching diagnostics
never changes any frozen estimate or core Run/Change record.

Each session has one immutable diagnostic attachment. Exact rereads, including a
byte-identical renamed copy, reuse its snapshot and event. You may explicitly link
the same source to a second session; its facts are stored once. Conflicting sources,
repositories, meanings or provenance reject atomically. There is no correction
operation for the finite attachment. `show` and `history` use stored diagnostics without reopening the source.
Rejected source reads and failed migrations leave database and source bytes unchanged.

## Continue the manual experiment

For the next session, choose a new ID and keep the matching labels:

```sh
uv run --locked changecost --format human session start work-02 --task-kind bug-fix --context changecost/python
uv run --locked changecost --format human session history --task-kind bug-fix --context changecost/python
```

Each estimate freezes the earlier committed session IDs, measurement revisions,
values, outcome counts, summary and `manual-session-median/v1` algorithm. Pending
sessions and different exact labels contribute nothing. Later totals or corrections
never change old estimates. Retrying start requires identical original labels and
guess, including whether the guess was omitted.

To repair an incorrect measurement, inspect its current revision with `show`, then
supply that revision and a nonblank reason. This example corrects revision 1:

```sh
uv run --locked changecost --format human session correct work-01 --revision 1 --tokens 11000 --outcome completed --reason "Corrected the measured session total"
```

Finish and correction retries are idempotent only for the same payload. Conflicting
finish requires correction. A correction with a stale predecessor and different
payload rejects. Every measurement remains visible. `operation_revision` identifies
the revision created by the operation, even when retrying after a later correction.
The report's `measurement` and `error` always use the latest revision.

Read `error.signed_tokens` as forecast minus actual. Negative means the estimate
was too low. `absolute_tokens` is the magnitude. Percentage error is unavailable
when actual is zero. History reports the total signed error and mean absolute
error, or MAE, with included counts and exclusions for pending, partial and
unknown-forecast sessions. Ratios retain their exact numerator and denominator;
`rounded_decimal` uses six decimal places and half-even rounding. Error changes
are descriptive. No calibrated accuracy or improvement promise follows.

To choose a separate store, put the option before the session operation:

```sh
uv run --locked changecost session --session-db .changecost/my-sessions.sqlite3 history
```

The default is `.changecost/sessions.sqlite3` relative to your working directory.
Only a valid start creates it. Help, invalid input, history of missing storage and
show of an unknown session create neither the session store nor the core store.
Do not point `--session-db` at a core or unfamiliar database. Such files reject
without adoption. First creation publishes only a committed database and never
replaces an existing file. Retry start after an interrupted first attempt. Keep
the SQLite file on a local filesystem and back it up while
no command is writing. Separate files do not share or merge learning.

For a deterministic example, choose a fresh output directory:

```sh
uv run --locked python -m changecost.session_demo .changecost/session-demo-01
```

The actual CLI records totals of 200, 200 and 1000 after forecasts of 100, 200 and
200. Absolute errors are 100, 0 and 800 tokens. A fourth pending session forecasts
200 from the three-sample median. Cumulative MAE is 900/3 = 300 tokens. The demo
retains a separate SQLite file and `transcript.json`, and refuses an existing output
directory. It never populates the default real store.

Manual totals and cohort choices can be wrong. The finite native bridge provides
partial diagnostics only, without full-Change demand, economic or billing authority.
The separate provisional counter target above does not widen that finite approval. Local focused checks are
recorded in the [implementation evidence](../openspec/changes/dogfood-01-local-sessions/TDD_EVIDENCE.md).
Local persistence/correction review is closed. Aggregate Linux/Python assurance,
final provider review and PR acceptance remain pending. The bridge's local checks
are recorded separately in [native observation evidence](../openspec/changes/dogfood-02-codex-observations/TDD_EVIDENCE.md).

Manual-only databases remain schema v1 and stay readable without migration. Existing
manual start, finish, correction and retry work on v1, v2 and v3. The first accepted
native attachment upgrades v1 to v2 together with snapshot/link/event writes in one
transaction. Source validation happens before any write. Migration is decided after
the write lock, and failures roll it back. Unknown databases reject unchanged.
The first Codex-target start upgrades recognized v1 or v2 storage to additive v3
inside the same transaction as the frozen forecast and session membership. Finite
observations work on v3 without downgrade. Read-only reports never migrate.
The committed bootstrap and no-clobber publication rule remains in effect.

Before upgrading, back up the separate SQLite file while no command is writing.
Old binaries refuse the newer v2 or v3 schemas. Rollback after migration requires restoring the pre-upgrade
backup and loses observations written since that backup. Removing the command alone
does not revert the schema. Keep the database on a normal local filesystem; no new
network filesystem or power-loss durability guarantee is established.
