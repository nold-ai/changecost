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
