# Quote preparation evidence

Reviewed 2026-10-03 (Europe/Berlin). This is planning evidence, not runtime TDD,
provider approval, statistical calibration, or implementation acceptance.

## Baseline and authorization

- Repository: nold-ai/changecost; issue [#15](https://github.com/nold-ai/changecost/issues/15).
- Successfully fetched main: `3009b351d5108b60e9ba8649a9ef4aa0c0feb9f9`
  at 2026-10-03 01:06:51 Europe/Berlin (2026-10-02T23:06:51Z).
- Branch: `codex/prepare-quote-01-empirical-estimation`, isolated clean worktree.
- Maintainer authorized this preparation reconciliation and selected scoped stash.
  Runtime implementation, live collection and publication remain separate requests.
- Settlement delivered in [PR #28](https://github.com/nold-ai/changecost/pull/28),
  accepted/archived by [PR #31](https://github.com/nold-ai/changecost/pull/31).

## State-of-truth reconciliation

| Claim | Status and inspected evidence | Planning consequence |
| --- | --- | --- |
| No runtime or main specs | Outdated: src/changecost, four main specs and installed-command tests exist. | Reuse delivered boundaries and current main-spec links. |
| Quote calculation delivered | False: models.py contains portable Quote, cli.py only inspects imported Quotes. | Keep computation planned; extend the existing record rather than inventing another contract. |
| Full-change amounts follow saved settlement flags | Unsafe: coverage.py and reconciliation.py evaluate one cutoff; saved full_change is snapshot_only. | Derive each peer through pure cutoff selection/coverage without settlement writes. |
| Arbitrary provider/unit coverage is supported | False: coverage.py closes support to synthetic billed USD; docs/settlement.md names its full tuple. | Preserve synthetic provenance and unpriced unsupported scopes; add no policy. |
| Portable import establishes computation authority | False: store.py and inspect_computation retain local receipts separately. | Keep imported claims inspectable; require local authority and same-snapshot replay checks. |
| Source inspection blocks this estimator | Not a dependency: native blocked-by #12 is delivered; provider stories separately require source profiles. | Synthetic verification can proceed after separate implementation authorization. |
| Default 20 or p90 is calibrated | Unknown; these are approved pilot design defaults, not empirical success claims. | Retain defaults and explicit To-Validate limits. |

Inspected models.py Quote/Features/Cutoff, store.py availability/graph/receipts/layout,
reconciliation.py snapshot_records/computation_details/inspect_computation, coverage.py
policy_identity/supports/assess_coverage and economic_graph.py reference-role validation.
Reviewed public offline CLI/docs and tests/test_reconciliation.py for late coverage,
operation retries, imported authority and consistent backup behavior. No runtime
source/test/config behavior is changed by this preparation.

## Workflow and verification

OpenSpec CLI 1.13.2 reports the repo-local spec-driven store and complete planning
artifacts, not completed implementation. Existing quote tasks were 0/11. The revised
implementation tasks remain entirely unchecked. Main specs remain unchanged.
The canonical workflow requires an upfront independent obligation review and affected
closure, exact-head Codex, additional CodeRabbit for persistence/import trust, and
mandatory mechanical/Linux assurance. Existing session allowances cannot reset.
No matching quote session or stash was found across inspected worktrees; a new
three-batch/90-active-minute preparation contract was initialized. Runtime expansion
must use explicit authorized scope adoption and retain preparation history.

Checks and issue readback are recorded below. Final content-bound gate outcomes
are retained in the ignored prepare.md receipt and logs rather than predicted here. No new vendor or
statistical capability claim was introduced, so no external research was needed;
repository code, CLI and native GitHub evidence are the sources, accessed 2026-10-03.

## Risks, limitations and rollback

Confidence: high in corrected local contract facts; implementation/calibration remain
To-Validate. Stale completeness, leakage and lost artifacts are mitigated by cutoff
re-evaluation, immutable availability and verified scoped-stash contents. No paid
infrastructure or runtime migration is part of preparation. Restore only owned
planning paths or revert a later plan commit and reconcile issue text without deleting
history. A local stash is recovery evidence, not remote backup. The ignored preparation
receipt records the immutable OID and exact checks; the next stage must revalidate
fresh main and inputs before implementation.

## Actual preparation checks and readback

- OpenSpec CLI 1.13.2 selected strict validation: passed before and after reconciliation.
- Initial aggregate make check: failed. All 1,075 existing tests passed (92.32 seconds),
  formatting/lint/type/build/index/metadata/workflow and all 11 OpenSpec items passed.
  Documentation found a removed stable feature-section anchor and an outdated
  content-bound generated-command rationale; both were corrected and the docs leaf passed.
- The host make-test fixture inherited command-line BASE_REF/MANIFEST through
  MAKEFLAGS, selecting a commit unavailable in its disposable fixture. The final
  invocation supplies explicit inputs through environment variables and clears Make
  flags; fixture behavior is not changed or waived.
- SpecFact CLI 0.55.4 capsule assurance remains incomplete on this macOS controller:
  all ten required analyzers reported unsupported_controller_platform. Metadata under
  quality/ triggers the existing review gate even for this planning-only diff. No
  policy bypass or analyzer pass is claimed. Supported-Linux assurance remains To-Validate.
- Independent read-only planning review found two concrete retained-scenario conflicts:
  settlement-revision selection versus cutoff-derived normalized inputs, and fallback
  for unsupported feature versions rejected by the existing contract. Both were fixed
  in one correction batch; affected-scope closure verified no remaining actionable
  defects and matching fingerprints. No runtime TDD was invented.
- Issue #15 body synchronization was read back exactly. User Story, parent #8,
  native blocked-by #12 CLOSED, Open/Todo status, empty assignees, labels and existing
  project membership remain unchanged. Revised artifacts are locally unpublished;
  issue links identify the real published baseline, not a nonexistent planning branch.
- The canonical index now includes this preparation evidence; regeneration changes
  llms.txt by one navigation entry. docs/commands.md is byte-identical because no CLI
  source/options or skill metadata changed; its content-bound rationale was refreshed.

The final aggregate is required and its actual result is recorded in the recovery
receipt. Preparation is not certified fully green while Linux assurance is missing.
