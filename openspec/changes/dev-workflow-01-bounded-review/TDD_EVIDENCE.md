# TDD evidence: bounded review sessions

Date: 2026-09-28 (Europe/Berlin)

## Failing before implementation

`uv run --locked pytest tests/test_review_session.py` failed during collection:
`ImportError: cannot import name 'review_session' from 'quality'`.

## Passing implementation evidence

- `uv run --locked pytest tests/test_review_session.py` — 19 passed, including
  synthetic multi-page GraphQL `reviewThreads` and nested comment pagination.
- `uv run --locked ruff check quality/review_session.py tests/test_review_session.py` — passed.
- `uv run --locked ruff format --check quality/review_session.py tests/test_review_session.py` — passed.
- `uv run --locked basedpyright` — 0 errors, 0 warnings, 0 notes.
- `gh api graphql` against merged PR #22 — confirmed the production schema accepts
  both `PullRequest.reviewThreads` and `PullRequestReviewThread.comments` paging
  queries on 2026-09-28 (Europe/Berlin).
- `openspec validate dev-workflow-01-bounded-review --strict --no-interactive` — valid.
- `BASE_REF=origin/main MANIFEST=/private/tmp/bounded-review-manifest make docs` — passed.
- `BASE_REF=origin/main MANIFEST=/private/tmp/bounded-review-manifest make check` —
  all gates through build passed, including 187 tests; review failed closed because
  every required SpecFact analyzer reported `unsupported_controller_platform` on macOS.

The local macOS controller cannot establish a supported SpecFact capsule review.
The supported-Linux preflight remains pending on PR #24 for its current head;
this document does not claim it completed.

The ignored receipt for `dev-workflow-01-bounded-review` was initialized against
the current intended-file aggregate and returned `continue` with zero batches and
the default 3/90 budget. Cross-family calibration remains pending: an installed
model is only a candidate until the documented concealed-case protocol completes.

## Consolidated PR correction evidence

On 2026-09-28 (Europe/Berlin), the collected PR findings were repaired together.
Before implementation, the added lifecycle and REST regression scenarios produced
14 failures and 20 passes; the actual output is retained locally in
`.changecost/repair-red.txt`. Those failures cover evidence dispatch, nested state,
conflicting event identity, actual REST values, explicit scope resolution and
durable family history.

After correction, 60 focused tests passed with real temporary Git repositories;
targeted helper statement coverage measured 91% using installed coverage 7.16.2.
Dirty tracked files, deletions and untracked additions invalidate reviewed inputs.
CLI ingestion, missing sources, outdated unresolved threads, malformed cursors,
API timeouts and invalid events are included. Radon reports maximum cyclomatic
complexity 9; the installed native KISS metric check returns no findings.

`BASE_REF=origin/main make check` passed lock, hygiene, lint, types, docs, index,
metadata, workflow, build, all 228 tests and all ten strict OpenSpec validations.
The required capsule review remained unavailable on the macOS controller and
returned `unsupported_controller_platform`. The retained local log is
`.changecost/repair-check.txt`; this is not a substitute for fresh Linux evidence.
The previously failed Linux run's helper coverage/complexity/nesting issues are
addressed locally, but its successor must establish the actual runner result.

The original pilot receipt omitted historical activity and is retained as evidence,
not used to claim a fresh allowance or measured savings. The maintainer's explicit
resumed correction request and retained counters are documented in the ignored
resumption handoff. Cross-family model calibration remains pending.

Fresh independent review of that unpublished batch identified four additional
completion/input invariants. Before repair, their regressions produced five
failures and 60 passes (`.changecost/repair-input-red.txt`). The same batch now
invalidates prior evidence on every binding refresh, fingerprints staged blob IDs
and modes, requires explicit expected check/status identities, and reconciles
persisted dispositions with their event history.

Final frozen-source validation: all 70 focused tests passed; helper statement
coverage was 92% (530 of 578 statements), maximum Radon complexity remained 9,
and native KISS metrics returned no findings. Ruff passed and BasedPyright reported
zero errors/warnings. The complete repository suite passed all 238 tests, and the
strict OpenSpec change validation passed. Fresh supported-Linux capsule evidence
remains required; no macOS limitation was treated as a pass.

## Explicitly authorized three-finding extension

The maintainer authorized one further collected batch with 30 active minutes on
2026-09-28 (Europe/Berlin), retaining prior counters and unknown historical timing.
Scope is missing elapsed measurement, latest reviewer rejection, and complete
paginated REST JSON parsing. The ignored extension receipt records authorization;
it does not replace or reset the historical session.

New spec-first regressions produced eight failures and 71 passes before repair
(`.changecost/extension-red.txt`). The repaired source passes 85 focused tests and
all 253 repository tests. Measured helper coverage is 563/608 statements (93%
rounded), maximum Radon complexity 10, and native KISS metrics report no findings.
Ruff and BasedPyright pass; strict OpenSpec validation passes.

Tests cover explicit zero versus missing minutes, UTC measurement provenance,
restart/idempotent replay, head-refresh invalidation, current-head reviewer state
supersession across pages, top-level human rejections, complete pretty-printed
REST documents, API errors and CLI incomplete handoffs. Recording timestamps do
not infer active time from wall time. This extension still requires fresh remote
Linux and bot review evidence after publication.

Independent review found fractional accumulation drift within this timing repair.
A further regression failed before the final correction
(`.changecost/extension-fractional-red.txt`). Canonical `math.fsum` now computes both
stored and validated totals over all recorded measurements; 900 measurements of
0.1 minute retain exactly 90 minutes across restart and reach the budget boundary.
This remained within the same unpublished, authorized correction batch.

## Family-wide state, identity and workflow reconciliation

The maintainer subsequently authorized continued collected review/fix work until
green, preserving prior counters and unknown historical timing. This batch repairs
the common event/state and monitor-identity invariants rather than only the five
reported symptoms. No new allowance or token saving is inferred from that request.

Spec-first family regressions produced 11 failures and 94 passes before the
implementation (`.changecost/family-red.txt`). Final verification on the unpublished
repair tree: 119 focused tests and all 287 repository tests pass; helper coverage
is 655/713 statements (92% rounded), maximum Radon complexity is 10, and native
KISS metrics report no findings. Ruff and BasedPyright pass. Documentation checks
pass against both the prior head and main; strict OpenSpec, generated index and
hygiene checks pass. Hygiene required normal filesystem access to skill files;
the initial sandbox permission failure was rerun successfully, not waived.

The matrix covers all derived-cache reconciliation, strict discrete types,
genesis recovery, dirty published inputs, same-SHA source/input epochs, exact
human/bot identities, final non-findings versus genuine corrected recurrences,
premature investigations, retry provenance, malformed pagination and collection
errors, metadata noise, and remaining request/sleep deadlines. Logs remain under
ignored `.changecost/family-*.txt`; earlier historical measurements are unchanged.

Schema 2 requires explicit recovery of incompatible prior receipts, retaining
their original history and unknown measurements. Its local genesis marker is not
a backup or hostile-tamper guarantee. REST-only monitoring remains pending if a
provider emits a clean summary without a current-head REST review; coordinator
evidence must disclose that limitation. Fresh supported-Linux and remote review
evidence remain required for the next published head. Calibration remains pending.

Independent review of that unpublished tree identified four transaction-boundary
variants in the same families. Fourteen parameterized tests failed before repair
(`.changecost/family-boundary-red.txt`): concurrent input refresh during collection,
missing typed nested comment/thread fields, malformed optional scope references,
and optimistic retry after a successful write. The corrected tree passes 133
focused tests and all 301 repository tests; coverage is 670/727 statements (92%
rounded), maximum complexity 10, and native KISS findings remain empty. Ruff,
types, documentation against both bases and strict OpenSpec checks pass.

An initial full-test invocation omitted the virtual environment's console-script
PATH and failed the existing entrypoint-discovery test (300 passed). Repeating
with the configured PATH passed all 301; no source repair or test weakening was
needed. Final logs are `.changecost/family-boundary-coverage.txt` and
`.changecost/family-boundary-full-configured.txt`. The historical live receipt still
requires recovery because it predates genesis; the maintainer's continuous-review
authorization permits this work without fabricating a passing helper receipt.

The next independent pass found an adjacent malformed-review-state variant in the
same unpublished batch. The 21-case matrix covers required and other reviewers,
unknown/case/type values, and all five documented GitHub review states. It produced
six failures before repair (`.changecost/family-review-enum-red.txt`), then all 21
passed. The full suite now passes 322 tests. Unknown review states persist
incomplete evidence instead of erasing a preceding rejection; documented pending
and dismissed behavior is unchanged. Ruff, types, docs against both bases,
OpenSpec and hygiene pass; maximum complexity remains 10 with no KISS findings.
Final instrumented focused verification passes 154 tests and measures 672/729
helper statements (92% rounded). Exact final logs are
`.changecost/family-enum-full.txt` and `.changecost/family-enum-coverage.txt`.

## Effective objections, initial contracts and bounded timing fixture

On 2026-09-29 (Europe/Berlin), the next collected batch addresses effective review
objections, usable initial scope and the supported-Linux targeted-coverage timeout.
New specification-first contract/history tests produced 32 failures and three
passes before implementation (`.changecost/batch7-red.txt`). Schema 3 verifies
initial real Git/file facts and preserves them for pure replay; incompatible
receipts require explicit recovery without invented provenance or budget resets.
Current-head changes-requested objections survive later comments/pending reviews
and dismissal of another review, while later approval or dismissal of the original
rejecting review is recognized from the complete fresh snapshot.

The 900-measurement timing fixture was replaced with 89 minutes plus ten 0.1-minute
measurements. An actual incremental-addition mutant fails at
89.99999999999994 instead of 90 (`.changecost/batch7-timing-mutant-red.txt`), so the
smaller fixture retains the arithmetic, restart, final-completion and next-batch
boundary proof. No production timeout, analyzer enforcement or accumulation logic
was weakened. This reduces test input volume; fresh Linux evidence must confirm
the timeout repair rather than inferring it from local timing.

Final local verification: 202 focused tests pass in 18.25 seconds under coverage,
370 full tests pass in 19.58 seconds, and helper coverage is 736/794 statements
(93% rounded). Ruff, BasedPyright, docs against HEAD/main and strict OpenSpec pass;
maximum complexity remains 10 and native KISS reports no findings. Logs are
`.changecost/batch7-focused.txt`, `.changecost/batch7-coverage.txt` and
`.changecost/batch7-full.txt`. These local durations are test observations, not
review-token or cost savings.

The watcher documentation now explicitly distinguishes read-only GitHub operations
from local code isolation: checkout Python executes with operator privileges and
credentials. The existing trusted-contributor boundary remains unchanged; hostile
PR isolation needs a separate architecture decision and is not claimed fixed.

Independent review found that assume-unchanged/skip-worktree flags could hide a
tracked edit from the initial Git change set. Six real-Git scenarios failed before
repair (`.changecost/batch7-index-flags-red.txt`), covering both flags during
initialization, input refresh and final completion. Shared input capture now
rejects these unsupported flags without mutating the index. All six pass; the
final tree passes 208 focused tests and 376 full tests. Final logs are
`.changecost/batch7-final-coverage.txt` and `.changecost/batch7-final-full.txt`.
Types, Ruff, docs against both bases and OpenSpec pass, with maximum complexity10
and no native KISS findings. Helper coverage measures 741/799 statements (93%
rounded). This stayed within the same unpublished batch.

## Visible watcher decisions and shared commit-ID validation

On 2026-09-29 (Europe/Berlin), the next collected batch repairs silent local terminal
decisions during unchanged polling, stale wait output at the final sleep boundary,
and inconsistent SHA-1/SHA-256 head validation. Specification-first regressions
produced five failures and two passes before implementation
(`.changecost/batch8-red.txt`). Terminal output is emitted once, changed packets
are not duplicated, and the deadline rereads local state before reporting wait.
Incomplete retains exit status 1; other terminal/wait results retain 0.

Real SHA-1 and SHA-256 Git fixtures initialize, record a batch, commit, advance and
reload while preserving their initial contracts and counters. Additional variants
reject malformed/short/nonhex/type-invalid identities in contract, recording and
pure replay, and reject valid-format heads that differ from actual Git HEAD.

Final local verification passes 227 focused tests and 395 full repository tests;
helper coverage measures 756/809 statements (93% rounded).
Ruff, BasedPyright, docs against HEAD/main and strict OpenSpec pass; maximum
complexity remains 10 with no native KISS findings. Logs are
`.changecost/batch8-focused.txt`, `.changecost/batch8-coverage.txt` and
`.changecost/batch8-full.txt`. Fresh supported-Linux and current-head provider
results remain required after publication; historical receipt recovery and
calibration limitations remain unchanged.

## Explicit comparison and PR target context

On 2026-09-29 (Europe/Berlin), the collected base/evidence repair began with
seven failing spec-first cases (`.changecost/batch9-red.txt`). Schema 4 separates
the immutable initial comparison and target-base facts from explicitly adopted
current context. Atomic adoption verifies local commits, retains counters, and
invalidates the prior evidence epoch even with unchanged HEAD. Local results
must supply their original full binding; cloning an old pass under a new event ID
does not make it current.

The matrix covers target ref/SHA drift between collection reads, malformed initial
targets, partial adoption, independent comparison versus target-tip commits, pure
replay and original-init retries, and missing/malformed/old remote timestamps in
all three positive evidence lanes. Existing current-head objections still block.
These timestamps bound freshness after adoption; they do not authenticate remote
execution against the new context or replace SpecFact's separate content proof.

Independent review then identified adopted annotated-tag object IDs being peeled
without retaining their exact identity. Four real-Git cases produced two failures
and two passes (`.changecost/batch9-tag-red.txt`). Shared base verification now
rejects tag object IDs for both initial and adopted contexts, while real SHA-1/
SHA-256 commit refresh and filesystem-free replay continue passing.

Final local runs pass 258 focused tests and 426 full tests (plus four subtests).
Coverage measures 827/882 helper statements (94% rounded). Ruff, BasedPyright,
docs against HEAD/main and strict OpenSpec pass; maximum complexity is 10 and
native KISS findings are empty. Logs are `.changecost/batch9-final-focused.txt`,
`.changecost/batch9-final-full.txt`, `.changecost/batch9-coverage.txt` and
`.changecost/batch9-types.txt`. Fresh supported-Linux and provider results remain
pending publication. Historical receipt recovery and calibration remain incomplete;
no reset or token/time savings is inferred from this repair.

## Outstanding requested-reviewer evidence

On 2026-09-29 (Europe/Berlin), fourteen spec-first cases failed before repairing
renewed reviewer requests (`.changecost/batch10-red.txt`). One validated exact-login
extractor now supplies semantic hashing, required-reviewer pending decisions and
both metadata reads. Missing or malformed request arrays invalidate previous green
evidence. Requests added or removed during collection are incomplete; ordering,
duplicate entries and avatar changes remain quiet. Bot suffixes remain distinct.

Regression cases cover previous approval/comment, cancellation with absent or
old-head evidence, preserved objections and exhausted budgets, required versus
nonrequired users, malformed fields and collection races. No team membership is
expanded. Schema 4 remains unchanged; old observations lacking the required source
data become incomplete without a fresh allowance. An explicit list guard also
provides runtime/type narrowing; it does not suppress validation.

Final local verification passes 276 focused tests and 444 full tests plus four
subtests. Coverage measures 846/900 statements (94%). Ruff/formatting, BasedPyright,
docs against HEAD/main, index, metadata and strict OpenSpec pass. Maximum complexity
is 10 with no native KISS findings. Exact-source logs are
`.changecost/batch10-coverage-test.txt`, `.changecost/batch10-full.txt`,
`.changecost/batch10-coverage.txt` and `.changecost/batch10-types.txt`.
Fresh Linux and provider reviews remain required after publication; retained
history, calibration and trust-boundary limitations remain unchanged.

## Caller-independent epochs and atomic automatic binding

On 2026-09-29 (Europe/Berlin), five spec-first cases failed before repairing the
two helper/caller identity collisions (`.changecost/batch11-red.txt`). Schema 5
derives `input-generation:N` from the recorded refresh count rather than caller
event IDs. Automatic PR binding selects a deterministic unused ID under the same
session lock as event persistence. Original caller, finding and scope identities
remain intact; prior incompatible epoch histories require recovery without reset.

The matrix exercises genesis/bind-pr/numeric/generation-like caller IDs, repeated
same-head refresh, stale local and monitor evidence, exact retries, ordinary events,
numeric aliases, multiple occupied bind candidates, and real threaded candidate
and same/conflicting-target races. Same-target retries are idempotent; conflicting
payloads or targets do not overwrite existing records.

Final local verification passes 290 focused tests and 458 full tests plus four
subtests. Coverage measures 857/909 statements (94% rounded); maximum complexity
is 10 with no native KISS findings. Ruff/formatting, BasedPyright, docs against
HEAD/main, index, metadata and strict OpenSpec pass. Logs are
`.changecost/batch11-full.txt`, `.changecost/batch11-coverage-test.txt`,
`.changecost/batch11-coverage.txt` and `.changecost/batch11-types.txt`.
Fresh Linux and provider evidence remain pending publication; no new allowance,
inferred historical timing or review-efficiency claim is introduced.

## Consistent handoffs and meaningful event text

On 2026-09-29 (Europe/Berlin), the collected handoff/text family matrix produced
19 failures and five passes before implementation (`.changecost/batch12-red.txt`).
Packets now load one state revision and derive both body and status from it,
retaining actual input-drift verification. Changed watcher output uses that same
packet's status for its exit decision and its raw monitor data for the associated
snapshot. Deterministic cases cover both complete/incomplete directions and
replacement observation association; quiet and timeout behavior remains covered.

Required event identities/semantic fields and supplied scope references reject
nonstring, empty and whitespace-only values, including Unicode whitespace. Padded
valid IDs and family labels retain exact bytes; no normalization or extra identity
grammar was added. Recording rejected extensions leaves exhausted budgets and
revision untouched; replay rejects malformed history. Exact finding/disposition,
scope/supersedes and identical-retry cases remain valid. Comment body rules remain
independent and allow legitimate empty bodies.

Final local verification passes 322 focused tests and 490 full tests plus four
subtests. Coverage measures 872/924 statements (94% rounded); maximum complexity
is 10, with no native KISS findings. Ruff/formatting, BasedPyright, docs against
HEAD/main, index, metadata and strict OpenSpec pass. Logs are
`.changecost/batch12-full.txt`, `.changecost/batch12-coverage-test.txt`,
`.changecost/batch12-coverage.txt` and `.changecost/batch12-types.txt`.
Fresh current-head Linux/provider evidence remains required after publication;
legacy receipt recovery, unknown historical measurements and calibration remain
explicit limitations rather than a reset or inferred savings.

## Budget precedence and explicit thread-report adjudication

On 2026-09-29 (Europe/Berlin), the collected budget/thread family regressions
produced five failures before implementation (`.changecost/batch13-red.txt`). An
otherwise complete receipt that still needs family investigation now replans when
either allowance is exhausted. Genuine fully satisfied completion remains permitted
exactly at the limit. Cases cover below/equal/over batch and minute boundaries,
fixed/accepted-exception recurrences, independently insufficient and combined
extensions, and matching status/packet/watch decisions.

Existing reviewer evidence can explicitly acknowledge current remote reports via
`reviewed_threads`, a stable thread ID/content-digest map exposed by the packet.
Resolved flags alone never supply this acknowledgment. Tests cover first-observed
resolved reports, added/edited comments and threads, complete collected comment
content, malformed mappings at ingestion/replay, extra stale IDs, local unresolved
findings, input/base refresh, outdated/reopened blocking, and unchanged reclosure.
Resolution-only flips may reuse actual prior adjudication of unchanged content;
this is trusted local operator evidence, not resolver-role authentication or a
guarantee about unobserved transitions. No new observation-history subsystem is added.

Final local runs pass 351 focused tests and 519 full tests plus four subtests.
Coverage measures 901/954 statements (94% rounded), maximum complexity remains 10,
and native KISS findings are empty. Ruff/formatting, BasedPyright, docs against
HEAD/main, index, metadata and strict OpenSpec pass. Exact logs are
`.changecost/batch13-full.txt`, `.changecost/batch13-coverage-test.txt`,
`.changecost/batch13-coverage.txt` and `.changecost/batch13-types.txt`.
Fresh Linux/provider evidence is still required after publication; historical
recovery, unknown measurements, calibration and trust-boundary limits remain.

## Explicit observation epoch provenance

On 2026-09-29 (Europe/Berlin), the epoch-ingestion matrix produced two failures and
14 passes before implementation (`.changecost/batch14-red.txt`). Ingestion now
preserves the original observation without defaulting its epoch to the current
generation. Missing, null, malformed and stale epochs persist as incomplete,
replacing earlier passing monitoring; error observations without epochs remain
storable and expose no adjudication receipts.

Cases cover generation zero and repeated same-head refresh, direct ingestion,
collection-time concurrent refresh, accepted explicit current epochs, rejected old
epochs, quiet repeated invalid observations, canonical reload and exact event
retries. Existing valid post-refresh fixtures now provide their explicit generation;
the elapsed-time test also checks its intended missing-measurement reason rather
than accidentally passing on an invalid monitor binding.

Final verification passes 371 focused tests and 539 full tests plus four subtests.
Coverage measures 901/954 statements (94% rounded); maximum complexity remains 10
and native KISS findings are empty. Ruff/formatting, BasedPyright, docs against
HEAD/main, index, metadata and strict OpenSpec pass. Final logs are
`.changecost/batch14-coverage-test.txt`, `.changecost/batch14-full.txt`,
`.changecost/batch14-coverage.txt` and `.changecost/batch14-types.txt`.
The earlier batch14-focused.txt records an intermediate fixture-adjustment failure,
not final verification. Current-head Linux/provider evidence remains pending
publication; history and recovery limitations are preserved without a new allowance.

## Finite canonical numeric aggregates

On 2026-09-29 (Europe/Berlin), six failing cases reproduced both fractional
extension rounding directions and overflowing budget, elapsed-time and usage
aggregates (`.changecost/batch15-red.txt`). Minute budgets now sum the default and
all original extension components; active time and measured usage use the same
finite canonical summation guard. Overflow becomes a controlled rejection before
persistence, and malformed replayed history remains recovery-required. Integer
batch counts, unknown usage and exact retry identities are preserved without an
epsilon or synthesized allowance.

The matrix covers exact-limit completion versus further work, below/exact/above
boundaries in active/paused/complete phases, interleaved events, reload, same-head
refresh, zero and batch-only grants, duplicate ingestion with the original
revision, all usage categories, atomic overflow rejection and malformed-history
status. Final verification passes 388 focused tests and 556 full tests plus four
subtests. Coverage measures 909/962 statements (94% rounded); maximum complexity
is 10 and native KISS findings are empty. Ruff/formatting, BasedPyright, docs
against HEAD/main, index, metadata and strict OpenSpec pass. Final logs are
`.changecost/batch15-coverage-test.txt`, `.changecost/batch15-full.txt`,
`.changecost/batch15-coverage.txt` and `.changecost/batch15-types.txt`.
The batch15-focused.txt log predates the final three boundary cases; the coverage
run includes them. Current-head Linux/provider evidence remains required after
publication; the preserved legacy receipt remains recovery-required, and prior
counters and unknown historical measurements are not reset.

## Exact integer validation and floating conversion failures

On 2026-09-29 (Europe/Berlin), thirteen failures reproduced oversized JSON integer
measurement errors and accidental floating-range restrictions on integer batch
counts (`.changecost/batch16-red.txt`). Numeric validation now checks integers by
sign without floating conversion, while floating measurements convert under an
explicit overflow guard. Rejected events preserve the receipt; malformed replay
returns recovery-incomplete instead of an exception traceback.

The matrix covers positive/negative 1001-digit integers in all six measurement
fields, exact large batch grants and retries, negative batches, optimistic revision
conflicts, PR mismatch/malformed identity replacing previous green observations,
observation-revision integer semantics and structured CLI output. Exact integer
counters gain no new numeric bound. The initial focused run had one test-harness
failure from an incorrect CLI flag; the final test uses the actual `--json` option.

Final verification passes 410 focused tests and 578 full tests plus four subtests.
Coverage measures 913/965 statements (95% rounded); maximum complexity is 10 and
native KISS findings are empty. Ruff/formatting, BasedPyright, docs against
HEAD/main, index, metadata and strict OpenSpec pass. Final logs are
`.changecost/batch16-coverage-test.txt`, `.changecost/batch16-full.txt`,
`.changecost/batch16-coverage.txt` and `.changecost/batch16-types.txt`;
batch16-focused.txt is the intermediate CLI-fixture failure, not final evidence.
Fresh supported-Linux and provider results remain required after publication.
The preserved legacy receipt still requires recovery; prior counters and unknown
historical time/usage are retained without a reset or savings claim.

## Explicit refreshed scope coverage

On 2026-09-29 (Europe/Berlin), four failures reproduced undeclared untracked,
staged and committed paths being accepted at refresh, plus the missing current
reviewed manifest (`.changecost/batch17-red.txt`). Schema 6 retains the immutable
initial contract and derives the current reviewed manifest from required captured
scope facts on each advance. Coverage includes changed/index/untracked paths
against the effective comparison base between consistent input reads.

Ordinary refreshes retain authorized keys and recapture fingerprints. Keyset changes
require an explicitly referenced prior approved scope decision with a validated
complete manifest. Approval fingerprints record intent, so planned-absent files
may materialize and authorized content may change; they do not substitute for
fresh review evidence. Historical approvals are never adopted implicitly, while
explicit selection remains allowed under the trusted operator contract.

Tests cover declaration omissions, pending/rejected/deferred/missing/unrelated
approvals, planned files, edits/deletes/renames, contraction and explicit reexpansion,
retries, pure replay, forged scope facts, concurrent edits and adopted comparison
bases. An existing rebind test now declares its planned added.py before initialization
so it continues testing evidence invalidation within authorized scope. No prior
measurements or counters are rewritten; schema-5 receipts require explicit recovery.

Final verification passes 426 focused tests and 594 full tests plus four subtests.
Coverage measures 941/994 statements (95% rounded); maximum complexity is 10 and
native KISS findings are empty. Ruff/formatting, BasedPyright, docs against
HEAD/main, index, metadata and strict OpenSpec pass. Final logs are
`.changecost/batch17-coverage-test.txt`, `.changecost/batch17-full.txt`,
`.changecost/batch17-coverage.txt` and `.changecost/batch17-types.txt`.
Fresh supported-Linux and provider checks remain required after publication.
Legacy receipt recovery and unknown historical active-time/usage limits remain;
this change neither grants a new allowance nor claims review savings.

## Declared input binding and initial remote freshness

On 2026-09-29 (Europe/Berlin), three ignored-declared-file regressions failed before
implementation (`.changecost/batch18-red.txt`), and twelve old/missing/malformed
initial positive-timestamp cases failed (`.changecost/batch18-freshness-red.txt`).
A further unreadable-path case failed while dangling-symlink/directory cases already
passed (`.changecost/batch18-readability-red.txt`). The read failure now becomes a
controlled incomplete result rather than an uncaught exception.

Schema 7 requires declared keys at every input capture. Explicit fingerprints or
absence join the Git/index digest; existing declared content outside the index
prevents clean completion even when ignored. Unrelated ignored output remains
excluded. Tests cover creation/edit/deletion, local/global ignore rules, negation,
tracked paths matching ignore, approved new keys, consistency races and nonregular
or unreadable paths. Earlier receipt binding semantics require explicit recovery.

The initial remote freshness floor now derives from validated immutable genesis
time. Ordinary refreshes and retries retain it; explicit base adoption updates it.
Exact timezone-aware comparisons accept equal/new timestamps and reject earlier,
missing, malformed or naive timestamps. Positive fixtures now carry timestamps;
the adoption missing-evidence case explicitly removes them to retain its original
intent. Objections/failures remain independent blockers. Valid pre-init same-base
work and coarse earlier same-second timestamps may conservatively require reruns;
this is contextual evidence, not authenticated runner execution.

Final verification passes 455 focused tests and 623 full tests plus four subtests.
Coverage measures 949/1002 statements (95% rounded); maximum complexity is 10 and
native KISS findings are empty. Ruff/formatting, BasedPyright, docs against
HEAD/main, index, metadata and strict OpenSpec pass. Final logs are
`.changecost/batch18-coverage-test.txt`, `.changecost/batch18-full.txt`,
`.changecost/batch18-coverage.txt` and `.changecost/batch18-types.txt`.
The batch18-focused.txt log precedes the three final path-readability cases;
the coverage run includes them. Supported-Linux/provider evidence remains required
for the published head. Legacy recovery, retained counters and unknown historical
time/usage remain explicit; no fresh allowance or savings claim is introduced.

## All-report adjudication and portable Git fixtures

On 2026-09-29 (Europe/Berlin), the actual empty-Git-template run reproduced three
fixture failures and one passing control (`.changecost/batch19-red.txt`). Both
Linux capsule jobs failed because .git/info was absent, not because of a timeout.
The fixture now creates its intended metadata parent explicitly; no analyzer,
timeout or production Git behavior is weakened. The test audit found no other
optional Git-template-directory write assumption.

Two failing cases showed changed top-level review bodies and PR comments preserving
completion (`.changecost/batch19-reports-red.txt`). Schema 8 generalizes explicit
coverage to packet `report_receipts` and local `reviewed_reports`, namespaced by
thread/review/comment source. All fetched pages and historical reports participate;
exact bodies and stable context are hashed, while transport metadata and lifecycle
flags do not revoke content adjudication. Independent objections, unresolved state,
freshness and input gates remain blocking. Missing or malformed identities/bodies and duplicate identities
invalidate monitoring rather than silently omitting reports.

Valid old fixtures now provide explicit REST identities/bodies and full-report
attestations; rejection tests attest reports before verifying objections still
block. The changed-terminal watcher test changes check metadata rather than adding
an unadjudicated report. Tests cover add/edit/delete, historical pages, empty bodies,
namespace collisions, duplicate IDs, malformed types, metadata/reordering stability,
stale extra coverage and explicit revalidation. Earlier receipt semantics require
recovery, with no synthesized approvals, counter reset or savings claim.

Final verification passes 646 repository tests plus four subtests under an empty
Git template, covering all 478 helper cases; four normal-template ignore-rule
controls also pass. Coverage in that full run measures 971/1022 helper statements
(95% rounded); maximum complexity is 10 and native KISS findings are empty.
Ruff/formatting, BasedPyright, docs against HEAD/main, index, metadata and strict
OpenSpec pass. Final logs are `.changecost/batch19-empty-template-full.txt`,
`.changecost/batch19-normal-controls.txt`, `.changecost/batch19-focused.txt`,
`.changecost/batch19-coverage.txt` and `.changecost/batch19-types.txt`.
The full run used the project interpreter with the existing cached coverage package;
an initial cached-only interpreter lacked typer during collection and ran no tests.
Fresh native Linux and provider evidence remains required after publication;
legacy receipt recovery and unknown historical usage/time remain explicit.

## Required checks need positive success

On 2026-09-29 (Europe/Berlin), two failures reproduced required neutral conclusions
preserving completion, alone and alongside a same-name successful result on a later
page (`.changecost/batch20-red.txt`). Classification now uses exact contract names:
completed required checks must conclude success, while optional neutral results
retain their existing nonblocking behavior. Other failures and pending states are
unchanged; no run-supersession policy or analyzer setting is introduced.

The conclusion matrix covers required/optional success, neutral, skipped, failure,
cancelled, timed-out, action-required, stale, startup-failure, unknown and absent
conclusions. Pending-state variants and existing absent-name/freshness cases remain
covered. This is the repository's executed-positive-assurance policy, not a claim
that GitHub's native merge rules reject neutral checks. The original report's P1
label was triaged as a P2 advisory workflow-policy defect.

Final verification passes 676 repository tests plus four subtests under an empty
Git template, including all 508 helper cases. Coverage in that run measures
974/1025 helper statements (95% rounded); maximum complexity is 10 and native KISS
findings are empty. Ruff/formatting, BasedPyright, docs against HEAD/main, index,
metadata and strict OpenSpec pass. Final logs are `.changecost/batch20-full.txt`,
`.changecost/batch20-focused.txt`, `.changecost/batch20-coverage.txt` and
`.changecost/batch20-types.txt`. Fresh native Linux/provider results remain required
after publication; historical counters, recovery limitations and unknown time/usage
remain retained without a reset or claimed savings.

## Bounded cross-surface collection consistency

On 2026-09-29 (Europe/Berlin), five failures reproduced check/status/review/comment/
thread changes being missed after their first collection (`.changecost/batch21-red.txt`).
The collector now makes exactly two complete passes, validates both and compares
existing meaningful projections before returning the second. Each pass retains
all pagination and initial/final metadata guards; one outer request deadline covers
both passes. No ordering refactor, stabilization retry or schema change is added.

Tests cover surface content and lifecycle changes, freshness timestamps, stable
page regrouping and excluded transport metadata, second-pass API/malformed/timeout
errors replacing prior green, and decreasing request allowance across both passes.
The prior pagination fixture now supplies valid complete shapes and asserts eight
paginated REST reads instead of four; request-order controls supply all four PR
metadata reads. Sequential observations cannot guarantee atomicity, detect unseen
changes that revert between reads, or prevent changes after the last observation.

Final verification passes 695 repository tests plus four subtests under an empty
Git template, including all 527 helper cases. Coverage measures 982/1033 helper
statements (95% rounded); maximum complexity is 10 and native KISS findings are
empty. Ruff/formatting, BasedPyright, docs against HEAD/main, index, metadata and
strict OpenSpec pass. Final logs are `.changecost/batch21-full.txt`,
`.changecost/batch21-focused.txt`, `.changecost/batch21-coverage.txt` and
`.changecost/batch21-types.txt`. Fresh native Linux/provider results remain required
after publication; prior counters, legacy recovery and unknown historical time/usage
remain preserved without a reset or savings claim.
