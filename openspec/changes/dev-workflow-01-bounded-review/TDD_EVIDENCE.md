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
