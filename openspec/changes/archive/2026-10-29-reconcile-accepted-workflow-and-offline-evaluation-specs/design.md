# Record accepted contracts without completing future work

## Context and authority

The maintainer's 2026-10-29 Europe/Berlin request requires implemented contracts to
be archived and main specs to be current before Claude-reader archival. The earlier
2026-10-27 decision keeps #17 active for live preparation. #40 also retains its
separate bounded trial. One document-only reconciliation change satisfies both
boundaries without inventing a feature, capability split or product backlog item.

The inspected merged source is `5cbe58a892f27c78088a82d95219a0cb57f922df`.
[PR #42](https://github.com/nold-ai/changecost/pull/42) merged at
`5fe5e2e8f63dbf49eeeb77115ba19c67e063c21e` with reviewed head
`2ddbabb6e94c185dd3c42da5a548510fb1e427b0`.
[PR #48](https://github.com/nold-ai/changecost/pull/48) merged at
`401e43ed63a9da3e39f55fc29d1e7160d1d06d2e`.
Repository source and saved fresh PR metadata were inspected on 2026-10-29.
These are existing implementation receipts, not new assurance for this prose diff.

The independent lifecycle audit found all 13 prior archives synchronized, with 141
current requirement blocks and 540 scenarios matching main after whitespace
normalization. The separately accepted diagnostic repair has its own native CLI
archive. This change neither rewrites those archives nor replays their deltas.

## Scope and exact mapping

The source deltas were discovered from the actual CLI status response's
`artifactPaths.specs.existingOutputPaths`. The two paths are
`openspec/changes/dev-workflow-03-risk-first-execution/specs/bounded-review-session/spec.md`
and `openspec/changes/pilot-02-calibration-evaluation/specs/pilot-evaluation/spec.md`.
Original source hashes and task/evidence snapshots are retained in ignored local
reconciliation evidence. The final published diff must preserve their history.

### Accepted workflow guidance

The first four requirement blocks transfer unchanged. The canonical implementation
is [the shared workflow](../../../../docs/agent-rules/30-change-workflow.md#risk-first-execution-checkpoint)
and its four stage-skill references. PR #42's final receipt supplies current
publication and assurance evidence while retaining its original task snapshot.

| Requirement identity | Accepted scenarios |
| --- | ---: |
| Critical safety assumptions receive early observable proof | 4 |
| Existing review slots consume a compact execution checkpoint | 2 |
| Finding triage distinguishes defects from preferences using evidence | 3 |
| Risk-first execution preserves all existing completion controls | 2 |

The fifth requirement, `Bounded adoption assessment retains full delivery
boundaries`, and its two scenarios stay ADDED in #40. No trial has been selected,
authorized or executed by this reconciliation. Existing usage/performance evidence
from PR #50 cannot retrospectively supply its preparation, stable-candidate and
handoff observations. Tasks 5.1 through 5.3 remain pending. Original unchecked tasks
4.1 and 4.2 remain historical snapshots with a dated note that PR #42's exact final
receipt now satisfies their current publication and assurance duties.

### Accepted synthetic evaluator

The implementation is `src/changecost/evaluation.py`, `evaluation_models.py` and
`evaluation_metrics.py`, with documented use in
[offline evaluation](../../../../docs/pilot/evaluation.md). Existing
`tests/test_evaluation.py` and `tests/test_evaluation_cli.py` substantiate the
reported protections. This reconciliation inspects those existing artifacts and
does not rerun runtime assurance or claim new failing-before proof.

| Requirement identity | Accepted scenarios | Implementation evidence and limits |
| --- | ---: | --- |
| Leakage-free baseline comparison | 5 | `Experiment.forecast`, `economic_status` and `economic_comparison` preserve one initial forecast, shared min-20 fallback, foreign replay refusal and suppression of all accuracy on one-sided availability. Existing fallback, unpriced, correction and asymmetry tests cover these paths. All inputs are synthetic. |
| Complete reproducible evaluation truth | 2 | `economic_truth`, `truth_view` and `Experiment.score` freeze all-attempt settlement/coverage truth at its own checkpoint. Partial truth stays omitted. Economic and adaptive correction tests preserve frozen truth. The real Codex scenario remains future work. |
| Deterministic offline evaluation report | 2 | `run_history`, strict versioned input models and `evaluate_synthetic` preserve deterministic core content and separate later updates. Existing repeat-command and target-exclusion tests support the unchanged block. |
| Explicit metric denominators | 3 | `coverage`, `economic_metrics`, `attribution` and `abandoned_share` retain original units, Wilson uncertainty, raw provider/manual/unbound denominators and undefined zero/unknown shares. Existing six/two/two, retries and denominator tests apply to synthetic records. |
| Reproducible honest conclusion | 1 | `run_history` always emits `synthetic_only_not_yet_validated` and the registered `source_gaps`. `evaluate_synthetic` keeps optional elapsed milliseconds, bytes and environment in `measurements`, outside the deterministic core. No real-provider ingestion or live evidence conclusion is implemented. |
| Chronological adaptive evaluation and scoped promotion | 4 | Registration, target exclusion, frozen truth, `observed_metrics`, `scenario_metrics` and `adaptive_summary` retain separate availability, shared complete synthetic truth and scoped rubric diagnostics. `synthetic_rubric_passed` is a diagnostic. It creates no passing live receipt or native promotion authority. |
| Safe synthetic experiment boundary | 5 | Disposable stores, strict input/provenance models, safe errors, numeric/identifier bounds and allowlisted projections preserve the original block unchanged. Existing privacy, numeric, nested-component, repeated-run and unchanged-runtime-store tests support it. |

The seven blocks contain 22 scenarios in total. Original scenario identities remain
except that the `Failure to improve` and `Small sample` bodies state actual
synthetic-only behavior. The original deterministic-report and safe-boundary blocks
are unchanged. The first, truth and metric blocks gain explicit synthetic subjects.

`validate_evaluation_record` in evaluation.py rejects `native_usage` and any
provider other than `synthetic` before execution. Therefore these three original
scenarios are excluded from accepted main scope and retained in future deltas:

- `Provisional Codex counters are not complete truth`.
- `Unavailable personal cash`, concerning actual Cursor exports.
- `Partial native truth`.

Native refusal remains an accepted protection in the safe-boundary requirement.
The report does not ingest real Codex counters or Cursor money and then classify
those records into exclusion counts. Registered source-gap labels are protocol
inputs. They are not observed provider or measurement approvals.

Actual adaptive failure is a reported false `synthetic_rubric_passed` result. The
evaluator does not create or withdraw an actual live validation receipt. Existing
synthetic fixture tests of demand validation exercise the prior demand contract.
They do not turn this evaluator into a live promotion boundary.

## Native synchronization and future rebasing

Only `openspec archive reconcile-accepted-workflow-and-offline-evaluation-specs --yes`
may synchronize this change into main and create its archive. No main-spec edits,
manual archive moves, `openspec-sync-specs`, `--skip-specs` or `--no-validate` apply.
Independent review of the accepted/future boundary precedes execution. A CLI
failure requires inspection of actual partial state rather than bypass or replay.

After successful CLI readback, rebase #17 and #40 as one reviewed reconciliation:

1. Keep all original proposal/design/task history and append dated mapping notes.
2. Keep all original 19 #17 task lines and all original 15 #40 task lines byte for
   byte, including unchecked states. Keep both TDD evidence files unchanged.
3. In #17, retain full MODIFIED requirement blocks for complete truth, honest
   conclusion and scoped adaptive promotion. Each contains every accepted synthetic
   clause and scenario plus its future live extension and excluded native/provider
   scenario. Keep `Separate prospective live authority and execution` ADDED,
   unchanged with all three scenarios. The future delta has four identities and
   13 scenarios. Reference other transferred requirements in main instead of
   repeating them as ADDED.
4. In #40, retain only the fifth ADDED requirement and its two trial scenarios.
5. Read back accepted clauses, future blocks, original task bytes and strict all
   validation together. Nothing is final until both current main and active future
   deltas are coherent.

No #17 unchecked task becomes complete from extraction. Historical 1.2 and 2.3
through 2.6 proof remains incomplete. Live 3.0 through 3.6 and conditional 4.1
through 4.3 retain their actual authorization, implementation and acceptance duties.
See [live assessment](../../../../docs/pilot/live-assessment.md). Neither original
change is closed or archived by this reconciliation.

## Verification, risks and rollback

Documentation-only scope changes no runtime boundary, so no runtime probe or
invented TDD applies. Verify exact source extraction, 4/11 and 7/22 counts, future
4/13 and 1/2 blocks, strict selected/all OpenSpec and relevant documentation/index
checks. Preserve the exact original checksums and task lines. The parent owns
independent review, native archival, lifecycle documentation and final checks.

The main failure risks are synthetic results being presented as native ingestion,
a pending trial being presented as completed, and future MODIFIED blocks dropping
accepted protections. Explicit rejection language, unchanged task snapshots and
full-block comparison address those risks. Confidence is high for source boundaries
and medium for wording until independent review. The material assumption is that
the user's current all-delivered-contract request permits this separate document-only
reconciliation while original future changes stay active.

No paid infrastructure, data collection or user-store migration is needed. Historical
cost and future effort remain unknown. Rollback is a scoped normal-history revert
of the final reconciliation and lifecycle diff, preserving runtime, source approvals,
older archives and all original evidence. CLI partial failures require inspection.
