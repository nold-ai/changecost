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
