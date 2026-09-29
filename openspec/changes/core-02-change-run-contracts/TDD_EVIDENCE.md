# Core-02 implementation evidence

Working implementation, 2026-09-29 (Europe/Berlin), not yet certified or published.
Branch `codex/core-02-change-run-contracts`; comparison/main/merge-base
`cb6ff3b2e218466c8633463928e7c94b1cf31b22`. Fresh main was fetched again before
verification with no base advancement. The selected prepared artifacts and explicitly
requested archives were retained on this branch, without applying a stash.

## Failing before and passing after

Logs are local ignored files in `.changecost/workflow/core-02-change-run-contracts/`.
Tests use synthetic data and temporary stores. The first missing-module failures
below assert intentionally new product entry points, not missing development tools.

| Slice | Failing command/evidence | Passing evidence |
| --- | --- | --- |
| Strict contracts | `pytest -q tests/test_contracts.py`: models missing (`contracts-red.log`) | 27 tests (`contracts-green.log`) after models/codec |
| Persistence/lifecycle | `pytest -q tests/test_store.py`: operations missing (`store-red.log`) | combined contracts/store 36 tests (`store-first-pass.log`) |
| Offline CLI | `pytest -q tests/test_contract_cli.py`: 4 failures for missing --db/operations, 10 existing error probes pass (`cli-red.log`) | combined three modules 50 tests (`cli-first-pass.log`) |
| Additional boundaries | `pytest -q tests/test_contracts.py tests/test_store.py`: explicit bundle/record schema omission and future observed start accepted, 3 failures/41 passes (`boundary-red.log`) | focused suite plus foundation CLI 60 tests/4 subtests (`core-green.log`) |

The first expanded boundary run also exposed two test-import NameErrors. Those were
repaired and the 3 genuine missing-behavior failures reproduced before product fixes;
harness errors are not counted as behavioral red evidence. Later graph, delayed-commit,
file-evidence and quote replay probes passed when first introduced; they are additional
regression evidence, not fabricated red/green pairs.

## Scenario coverage

| Requirements | Test entry points |
| --- | --- |
| Explicit record lifecycle, registration replay/terminal retries | test_registration_replay_and_terminal_retry; test_fresh_cli_registration_outcome_and_export |
| Revisioned work intervals and correction atomicity | test_revision_corrections_are_atomic; observed-start validation |
| Store-local historical availability | destination import/reimport and cutoff tests in test_store.py |
| Versioned registration features | feature normalization/domain tests in test_contracts.py; registration conflict in test_store.py |
| Stable binding, complete RunRefs, source-evidence mapping | namespace/repository tests and test_file_evidence_binding_and_origin_claim in test_store.py |
| Economic kind/currency and exact portable contracts | parameterized amounts/currency/round-trip tests in test_contracts.py |
| Transactional persistence | busy writer, commit failure, invalid import and graph tests in test_store.py |
| Strict input/private data | duplicate keys, coercions, unknown fields, schemas, timestamps; test_private_invalid_import_has_no_payload_diagnostic |
| Offline portable operations | test_contract_cli.py and installed distribution test_cli.py |
| Lifecycle/algorithm separation | unsupported commands and imported quote replay tests |
| Atomic reference/revision integrity | test_import_rejects_cyclic_wrong_subject_and_forked_revisions and terminal retry |
| Committed/local visibility | test_delayed_commit_is_not_admitted_to_captured_snapshot and backward clock |
| Persistence recovery | failed initial schema, future schema, backup and commit retry tests |

The detailed scenario map below reconciles each scenario to regression coverage.
Initial gaps found by independent review were filled during correction batch 1.

## Environment and current checks

Runtime lock: Python >=3.11, Pydantic 2.13.5/core 2.46.5, Typer 0.27.2.
The package remains `0.1.0.dev0`, unreleased; no release/tag is created.
Ruff formatting/lint and BasedPyright passed for the implementation before the
independent review freeze. Full aggregate, both supported interpreter results,
installed package proof, advisory/license evidence and independent reviews are
recorded as they complete; pending work is not a pass.

Required SpecFact CLI 0.55.4/module 0.50.1 reports
`unsupported_controller_platform` on macOS. The existing Linux image
`specfact-478-linux-dev:latest` starts but `unshare --user --map-root-user true`
fails with Operation not permitted. No isolation controls were relaxed. Thus no
current full Linux analyzer assurance exists. The maintainer clarified that this
assurance runs in GitHub CI/CD, so it follows a locally checked feature-branch push. Historical green runs for PRs #22/#24 do not certify this change.

## Safety, limits and rollback

Trust boundary: an operator-owned local store and untrusted portable input.
Imported reconciled/verified_provider labels remain producer assertions. No real
provider collection, financial computation or model API operation was implemented.
Whole-graph validation favors simple correctness over large-dataset performance;
this initial local contract has no claimed capacity benchmark. Invalid imports,
conflicting attribution and failed writes roll back; export never overwrites a
final artifact. Keep a consistent SQLite backup for runtime rollback: portable
reimport cannot recreate earlier destination knowledge. Revert the eventual code
commit only after preserving compatible data. Until committed, retain this owned
working tree and local evidence directory; do not discard unrelated future work.

## Correction batch 1 and full scenario map

Independent quality, defect and documentation lanes reviewed canonical manifest
`9fa453638b4b87009864a2c8e2ceca7b62c31c13fe0d9bf545efa2c6c3917a3b`.
CodeRabbit CLI 0.8.1 completed the same complete scope, including untracked files,
with zero findings (`coderabbit-1.ndjson`). The independent defect lane found three
P2 defects and one P3 diagnostic issue; docs/quality identified coverage/status gaps.
These are retained in the bounded session and lane reports, not erased by fixes.

Before correction, `pytest -q tests/test_contracts.py tests/test_store.py
tests/test_contract_cli.py` produced **11 failures / 59 passes** (`review-red.log`):
wrong Settlement attribution/dependencies, empty mode bypass, invalid offsets/UTC
overflow and collapsed schema diagnostics. After correction and additional scenario
coverage, the focused suite plus foundation CLI passes **76 tests / 4 subtests**
(`review-green.log`). Exact amount, origin-claim, revision replay, delayed-outcome,
namespace and competing-writer additions passed on first introduction; they are
regression coverage, not claimed red/green proof.

| Capability scenario | Test (under tests/) |
| --- | --- |
| Register from an empty store | `test_contract_cli.py::test_fresh_cli_registration_outcome_and_export` |
| Registration replay and conflict | `test_store.py::test_registration_replay_and_terminal_retry` |
| Record outcome without monetary evidence | `test_store.py::test_delayed_outcomes_keep_work_bounds_and_retry_history` |
| Correct a terminal outcome explicitly | `test_store.py::test_revision_corrections_are_atomic` |
| Refuse new runs after termination | `test_store.py::test_registration_replay_and_terminal_retry` |
| Delayed outcome does not extend work | `test_store.py::test_delayed_outcomes_keep_work_bounds_and_retry_history` |
| Missing end and invalid correction | `test_store.py::test_revision_corrections_are_atomic` |
| Correct an interval explicitly | `test_store.py::test_revision_corrections_are_atomic` |
| Backdated portable evidence | `test_store.py::test_import_roundtrip_preserves_origin_and_destination_history` |
| Imported quote cannot recreate unavailable history | `test_store.py::test_quote_preserves_structure_but_foreign_replay_is_unavailable` |
| Normalize and preserve feature inputs | `test_contracts.py::test_normalized_feature_domain_and_identity` |
| Reject invalid or revised features | `test_store.py::test_registration_replay_and_terminal_retry` |
| Repeated binding | `test_store.py::test_registration_replay_and_terminal_retry` |
| Conflicting binding | `test_store.py::test_bind_conflict_and_namespaces` |
| Ambiguous run | `test_store.py::test_unbound_and_all_run_namespaces_survive_arbitrary_order` |
| Replay colliding raw run identifiers | `test_store.py::test_unbound_and_all_run_namespaces_survive_arbitrary_order` |
| Reject an incomplete run selector | `test_contract_cli.py::test_read_only_invalid_and_help` |
| Preserve an explicit mapping target namespace | `test_store.py::test_file_evidence_binding_and_origin_claim` |
| Map a source row without a session | `test_store.py::test_file_evidence_binding_and_origin_claim` |
| Replay a manual mapping | `test_store.py::test_file_evidence_binding_and_origin_claim` |
| Reject an unknown evidence selector | `test_store.py::test_bind_conflict_and_namespaces` |
| Reject conflicting record attribution | `test_store.py::test_file_evidence_binding_and_origin_claim` |
| Round-trip known nonmonetary quantities | `test_store.py::test_settlement_exact_storage_restart_and_claim_roundtrip` |
| Reject known money without currency | `test_contracts.py::test_currency_invariants` |
| Reject currency on a nonmonetary quantity | `test_contracts.py::test_currency_invariants` |
| Decimal round trip | `test_store.py::test_settlement_exact_storage_restart_and_claim_roundtrip` |
| Unsupported version | `test_contracts.py::test_unsupported_schema_has_safe_specific_diagnostic` |
| Partial failure | `test_store.py::test_atomic_import_and_missing_reference` |
| Concurrent binding | `test_store.py::test_competing_attribution_retries_observe_winner` |
| Duplicate and coercible input | `test_contracts.py::test_reject_nested_extra_and_duplicate_members` |
| Exact storage beyond floating precision | `test_store.py::test_settlement_exact_storage_restart_and_claim_roundtrip` |
| Preserve opaque identities | `test_contracts.py::test_normalized_feature_domain_and_identity` |
| Import and inspect without a provider | `test_contract_cli.py::test_fresh_cli_registration_outcome_and_export` |
| Invalid operation is read-only | `test_contract_cli.py::test_read_only_invalid_and_help` |
| Export failure preserves data | `test_contract_cli.py::test_export_failure_never_exposes_partial_file` |
| Outcome-only settlement command | `test_contract_cli.py::test_fresh_cli_registration_outcome_and_export` |
| Imported claims retain their provenance | `test_store.py::test_settlement_exact_storage_restart_and_claim_roundtrip` |
| Invalid revision graph | `test_store.py::test_import_rejects_cyclic_wrong_subject_and_forked_revisions` |
| Replay after response loss and terminal outcome | `test_store.py::test_registration_replay_and_terminal_retry` |
| Cross-repository binding | `test_store.py::test_bind_conflict_and_namespaces` |
| Transaction spans a cutoff | `test_store.py::test_delayed_commit_is_not_admitted_to_captured_snapshot` |
| Clock moves backwards | `test_store.py::test_clock_regression_fails_without_mutation` |
| Commit and migration failure | `test_store.py::test_busy_and_failed_commit_are_recoverable` |
| Future schema and backup recovery | `test_store.py::test_newer_schema_and_consistent_backup` |
| Sensitive unknown field | `test_contract_cli.py::test_private_invalid_import_has_no_payload_diagnostic` |

The commit/migration failure scenario also uses
`test_failed_initial_schema_has_no_published_store`: schema 1 creation is the only
implemented migration. No older production schema exists to upgrade. The private
input scenario also relies on the distribution build gate exclusion sentinels.
Coverage is structural/offline; financial correctness and provider capabilities
remain outside this change.

The first full aggregate passed all non-review leaves and 753 tests on Python
3.13.14; independent Python 3.11.15 ran 753 tests plus 4 subtests. The installed
sdist-to-wheel proof passed outside the checkout with socket creation blocked.
Advisory/license artifacts cover all 57 locked registry dependencies; no known
vulnerabilities or missing license metadata were reported. This evidence is
historical to the first freeze; corrected-tree checks/review are required next.

## Corrected-tree verification

Correction batch 1 full suites pass **769 tests** on Python **3.13.14** and
**769 tests plus 4 subtests** on Python **3.11.15** (`corrected-check.log`,
`corrected-py311.log`). Format, lint, types, docs/index, metadata, workflow,
locked dependencies, package proof and strict OpenSpec pass. Hygiene initially
removed one extra final blank line from openspec/config.yaml; its scoped rerun
is recorded separately. All 10 active/main spec items validate strictly.
The full aggregate remains nonzero for the required unsupported SpecFact review;
all ten native analyzers still report unavailable, without any waiver.
Final independent bug/security re-review found no remaining defects. The quality
and documentation lanes confirmed the corrected tests and evidence. CodeRabbit
completed its second full review with one minor finding: stale implementation
status and portable-backup wording in proposal.md. Both were corrected in the
final documentation batch; affected checks and independent delta review follow.


## GitHub-only capsule verification route

On 2026-09-29 the maintainer clarified that SpecFact capsules run in GitHub CI/CD,
not local macOS. Local unsupported reports describe platform applicability and do
not prove native assurance. Complete local checks and the staged commit hooks,
then push this feature branch and dispatch Repository quality with comparison_base
`cb6ff3b2e218466c8633463928e7c94b1cf31b22`. The workflow supports manual dispatch;
a PR is not required. Its Ubuntu matrix runs the actual ten native analyzers.
Full verification stays incomplete until current-head CI and native report contents
establish passing evidence. No gates, hooks or capsule isolation controls are bypassed.

The prior bounded-review replan signal remains in the receipt, with three correction
batches and all findings retained. The coordinator interprets the maintainer's CI
clarification together with the existing instruction to fix findings as continuation
of the final documentation correction and CI verification route. This does not
reset history or certify the helper's published-completion state. Actual remote
commit/run/report identities belong in the local handoff and issue after dispatch.

## Authorized lifecycle complexity correction

GitHub run [36552094082](https://github.com/nold-ai/changecost/actions/runs/36552094082)
analyzed commit `1d9046a40ba40d48fdccf9355f4ada567d0b89e2` on both Python versions.
All ten analyzers ran. Nine passed; Radon reported three blockers in operations.py:
interval_update complexity 19, and eight parameters on interval_update and declare.
The reports also retain 824 nonblocking warnings and 17 informational findings.
The maintainer explicitly authorized one additional correction batch on 2026-09-29;
the existing bounded-session history, findings and counters remain intact.

The correction groups one atomic lifecycle request into LifecycleDeclaration and
separates bound merging, known-bound change detection and correction authorization.
CLI flags, portable schema and transaction semantics remain unchanged. A new
characterization test proves combined retry idempotency and paired-update rollback.
It passes before and after the refactor; its initial assertion incorrectly assumed
record ordering and was repaired before the baseline pass. That test-writing error
is not product-defect TDD evidence. The actual failing-before evidence for this
maintainability correction is the native Radon report above. All 39 focused store
and CLI tests pass after the refactor. Final matrix tests, independent review and
current-commit native CI evidence are recorded in the workflow handoff and issue.


## Promotion checkpoint — 2026-09-29 (Europe/Berlin)

Implementation commit `fae72f330b2e8187521f2ed176b7bc0118f3575f` passed
[GitHub run 36558317437](https://github.com/nold-ai/changecost/actions/runs/36558317437)
on Python 3.11.15 and 3.13.14. Each native report proves all ten analyzers ran/PASS,
zero blockers, assurance PASS and exit 0 (`PASS_WITH_ADVISORY`). The 823 warnings
and 17 informational findings per report remain disclosed maintenance advisories;
no analyzer threshold or policy was weakened. Both full 154-file digests match
`bcb0320a3d90c2fe8c0c01685e901ed486a74b88982ae026b089c69f8eeb9dba`.
Local full suites passed 770 tests plus four subtests on each interpreter, and
both explicit-base and default-HEAD staged gates passed before the normal commit.
Independent final reviews found no remaining defects; retained workflow evidence
binds the reviewed manifest to that commit.

Fresh main and remote feature reads at promotion still identify main
`cb6ff3b2e218466c8633463928e7c94b1cf31b22` and the implementation commit above.
The maintainer explicitly requested the promotion/review workflow. Ready
[PR #25](https://github.com/nold-ai/changecost/pull/25) was created against main;
its initial head/base/body/draft status were read back. Tasks 5.1 and 5.3 now record
that completed verification/publication checkpoint. This documentation follow-up
requires its own scoped checks and review before commit; earlier CI does not
certify a later head. Current PR-head CI, Codex/CodeRabbit review and implementation
acceptance remain pending. Issue #11 stays open and Core-02 stays unarchived.


## PR #25 historical replay and presentation correction

Codex review 5354702412 reported two reproduced P2 defects in the unchanged runtime
at `42cc2ecafbda568da85b76c40477a3378699eb1b`: a future same-store cutoff could
admit future-effective inputs ([cutoff finding](https://github.com/nold-ai/changecost/pull/25#discussion_r4135200791)),
and arbitrary revision IDs could display a correction before its predecessor
([history finding](https://github.com/nold-ai/changecost/pull/25#discussion_r4135200813)).
The maintainer's promotion request authorizes this collected correction batch;
prior receipt counters and the historical documentation replan signal remain retained.

Spec scenarios were added before tests. The focused regression command
`pytest -q tests/test_store.py -k 'future_cutoff_cannot or inspection_orders_each'`
failed **4 tests** for the actual missing behaviors (`pr25-runtime-red.log`): one
future-cutoff case and predecessor ordering for outcome, interval and settlement.
An earlier uv invocation was blocked by local cache permissions before running
pytest; it is not behavioral red evidence. The project interpreter then reproduced
the four real failures. After the minimal fix, the complete contracts/store/CLI
suite passes **79 tests** (`pr25-runtime-green.log`); Ruff and BasedPyright pass.

Eligibility now rejects times later than the captured current snapshot without
writing. Inspection groups validated chains by kind and follows previous links,
independently of IDs or equal timestamps. Existing foreign/time-only cutoff,
sequence, destination availability, delayed-commit, clock and reference-graph
constraints remain intact. The new tests assert inspection leaves the full bundle
unchanged. No command flags, portable schema or financial algorithms changed.
Both corrections require independent frozen-tree verification and fresh GitHub
native assurance before the PR findings can be resolved; those later run/commit
identities belong in the retained workflow handoff and PR evidence.
