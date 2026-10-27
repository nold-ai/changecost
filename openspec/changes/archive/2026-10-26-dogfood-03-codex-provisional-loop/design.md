# Chosen design

The selected B sketch is `/private/tmp/changecost-codex-live-design-b.md`, synthesized with all four judge clarifications from `/private/tmp/changecost-codex-live-verdict.md`. Architecture exploration and upfront independent review occurred before this implementation. The sole writer owns the dedicated dogfood worktree. The parent owns review ledgers and subsequent independent review.

## Caller contract and ownership
`start --source codex` freezes the provisional target and forecast. `capture-codex ID --file PATH --repository-id REPO --outcome completed` atomically binds the source and appends revision 1. A changed capture requires `--revision N --reason TEXT`. `show` infers its saved target. `history --source codex` selects a separate cohort. Manual remains the default.

`codex_session_counter.py` owns bounded source acquisition and mapping through a frozen CodexCounterSnapshot. `sessions.py` owns CaptureOperation, persistence, revisions, cohort selection and exact arithmetic. `cli.py` translates explicit options. `presentation.py` renders concise safe session summaries. Add codex_sessions membership/bound identity/repository and immutable codex_captures tables without altering manual measurement rows. Version recognition explicitly enumerates v1, v2 and v3. Existing finite diagnostics work on v3 without downgrade.

## Counter mapping and privacy
The observed tuple is originator `Codex Desktop`, cli_version `0.163.0-alpha.10.2` or `0.163.0-alpha.11.2`, source `vscode` or the observed subagent.thread_spawn variant. Parent safe preflight established the second version before implementation. Both versions share the observed cumulative-counter shape and one provisional producer family; actual version remains disclosed in each capture and frozen input. Claims are unverified. A domain-separated hash of header `id` (source thread identity) excludes runtime `session_id`, path, repository and mapping. The target is the latest cumulative total_token_usage.total_tokens, never a sum of events, categories, last counts or response records. Counter integers exclude booleans and lie in 0 through 2**63-1. Decreases reject. Coverage, completeness, finality and subagent inclusion remain unknown.

Open only the explicit regular file through no-follow traversal. Stream rows and hashes with bounded bytes, rows, JSON depth, numeric lexemes, finite numbers and duplicate members. Stable descriptor metadata and observed size must agree before/after. Persist only safe projections and hashes. Reject with fixed safe codes and bounded ordinals.

## Retry and history invariants
Read the supplied immutable predecessor before acquisition and hash exactly that many old bytes. Under BEGIN IMMEDIATE, check an identical saved operation before newest-predecessor continuity. A byte-identical retry preserves its operation_revision even after later captures. Changed captures retain identity, repository, target and producer semantics; prefix digest, length and nondecreasing total must match the current predecessor. Concurrent stale writes reject atomically. One provider identity binds to one local attempt globally. One latest capture trains once per attempt. Unestimated captures train but do not enter the MAE denominator. Old forecasts retain earlier immutable capture provenance and quantities.

Manual start retries, finish/correct, forecasts and history all explicitly exclude Codex membership. Native evaluation shares exact arithmetic but never claims declared manual coverage. Human output shows estimate/source/sample count, reported total, direction and absolute/percentage error, revision/outcome, unknowns, and evaluated versus learning count. Full safe JSON retains provenance.

## Throughput checkpoint
- Blocking first steps. Selected design and source-shape proof are complete; specification precedes CLI red test and implementation.
- Independent workstreams. This code-coupled migration, reader and forecast path has one sole writer. No parallel source writes or test runs.
- Shared mutable state. One existing SQLite transaction writer owns membership, identity binding, revisions and migration.
- Smallest safe decomposition. One new reader module and two additive tables isolate provisional authority while reusing exact arithmetic and existing store transactions.

## Risk-first proof
The focused CLI test must fail because --source is missing, then prove start/capture/next forecast on synthetic compatible sources. Existing manual and finite suites prove their contracts remain usable. No raw private sources are read by the implementation agent. Parent performs selected actual-source CLI proof after freeze. Full supported Linux/provider review remains separate.

## Accepted identity correction on 2026-10-25

Parent actual-source proof rejected a valid header at ordinal 0 because the implementation required `session_id == id`. The existing finite request validator already matches request `thread_id` to header `id` and request `session_id` to header `session_id` separately. The provisional reader now validates the optional runtime `session_id` independently as a nonblank string of at most 512 characters. The existing provider-domain-separated hash remains based solely on header `id`, the thread identity. Changing a runtime session ID cannot create a second learning sample for the same thread. No stored metadata, format version, mapping or authority changes are needed. Synthetic regressions cover both admitted producer versions; parent actual-source proof remains separate.
