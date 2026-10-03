# Quote implementation evidence

Selected change: quote-01-empirical-estimation / issue #15. Maintainer explicitly
requested runtime implementation, verification, local CodeRabbit and scoped PR
review/fix delivery on 2026-10-03 (Europe/Berlin). No merge, deployment, provider
collection or archive is authorized. Package remains 0.1.0.dev0; SQLite layout 2
and changecost/v1 are retained.

## Baseline and recovery

Fetched origin/main 3009b351d5108b60e9ba8649a9ef4aa0c0feb9f9; feature branch
codex/quote-01-empirical-estimation in isolated preparation worktree. Verified all
13 prepared tracked/untracked SHA256 fingerprints and applied immutable stash
be9e9d6613b03e83dd05de0033abb2b34ce04a89 without --index; stash retained.
Existing bounded review session retained 1 batch and 13.251394305550154 active
minutes. Explicit runtime scope adoption preserves that original history/allowance.

Independent upfront obligation review found no architectural blockers; it required
typed receipt identity across Quote/settlement retry, predecessor, import-ledger and
explain paths. The implementation covers these boundaries without a schema migration.

## Spec-derived failing-before evidence — 2026-10-03 Europe/Berlin

- `.venv/bin/python -m pytest tests/test_quotes.py -q`: four tests failed because
  changecost.quotes was absent. Existing test infrastructure ran; failure established
  missing runtime computation/replay behavior. Log: ignored tdd-quotes-red.log.
- `.venv/bin/python -m pytest tests/test_quote_cli.py -q`: expected valid quote
  invocation failed with no quote command. Invalid minimum/no-store test already
  passed; it is not credited as missing-behavior failure. Log: tdd-cli-red.log.
- Feature-exclusion regression failed because narrow-filter exclusion provenance
  was missing. Corrected setup-only Bundle errors are not behavioral evidence.
  Log: tdd-features-red.log.
- Malformed metadata imported a peer reference not present in declared inputs;
  expected atomic rejection failed. Strict allowlisted metadata/reference validation
  now rejects it. Fixture-only outcome errors are not credited as red behavior.
  Log: tdd-metadata-red.log.

## Passing slice evidence — 2026-10-03 Europe/Berlin

- Quote/CLI slice passes exact ranks, ordered/permuted inputs, signed values/zero,
  complete/partial cohorts, target exclusion, strict minimum, unsupported identities,
  supported feature/backoff and late-feature provenance, abandoned retries, new gaps
  invalidating prior completeness, sequence-bound immutable replay, response-loss
  retry, portable/backup authority, both operation-kind collisions, both typed-ID
  authority collisions, privacy, legacy/unsupported metadata and atomic rollback.
- `.venv/bin/python -m pytest tests/test_quotes.py tests/test_quote_cli.py tests/test_reconciliation.py tests/test_store.py tests/test_contracts.py tests/test_contract_cli.py -q`
  passed 230 tests in the final scoped run (see ignored tdd-runtime-final-green.log).
  Independent verification will cover the complete final prospective tree.
- Ruff format/check and BasedPyright scoped source/new tests passed. Python host
  3.13.14; tests run against the existing installed editable package.

## Verification and acceptance status

Full independent quality/defect/docs review and explicit-base make check are pending
for the final frozen inputs. This macOS controller cannot run required native
SpecFact capsules; applicable supported-Linux assurance and exact-head external
reviews remain required. Missing analyzer evidence is incomplete, not passing.
No verified feature commit/push or PR acceptance is claimed here.

Provider support/calibration remains To-Validate. Rollback is a scoped follow-up
revert and separate compatible backup restore; retain the original store and stash.

## Independent correction batch 2 — 2026-10-03 Europe/Berlin

The first independent quality lane passed 1,095 runtime/repository tests and all
applicable local mechanical leaves; native SpecFact assurance remained unsupported
on macOS. Independent runtime/docs review identified three P2 findings: earlier
normalized work omitted from feature timing, stale generated/current Quote capability
claims, and missing installed-wheel successful Quote proof. This collected finding
set consumes batch 2, retaining original history and allowance.

The feature invariant now considers all cutoff-visible attributed normalized source
work across direct bindings, retries and correction-connected inputs, for target and
peers. A valid pre-work target selected profile before late evidence; once earlier
work became visible, it correctly fell back to repository. Historical replay keeps
the original profile result. A dedicated correction proof recomputes current amount
from 2 to 4 while original replay retains 2.

Installed public CLI proof constructs synthetic normalized evidence and portable
coverage without source imports or network, prices 0.25 USD, repeats the operation
identically, and explains local authority/reproduced economics. The existing build
gate invokes that proof in a clean locked sdist/wheel installation. Default uv-cache
sandbox and fresh-cache DNS failures are tooling failures, not TDD red evidence;
explicit authorized dependency-registry execution supplies the final build proof.

Actual completion timestamps from retained local logs (Europe/Berlin):

| Command / retained log | Result | Completed |
| --- | --- | --- |
| `.venv/bin/python -m pytest tests/test_quotes.py -q` / tdd-quotes-red.log | exit 1; 4 missing-behavior failures | 2026-10-03T01:24:40.317296+02:00 |
| `.venv/bin/python -m pytest tests/test_quote_cli.py -q` / tdd-cli-red.log | exit 1; missing valid Quote command | 2026-10-03T01:27:18.162510+02:00 |
| `.venv/bin/python -m pytest tests/test_quotes.py -q` / tdd-features-red.log | exit 1; missing feature exclusion; fixture-only errors excluded | 2026-10-03T01:28:12.402141+02:00 |
| `.venv/bin/python -m pytest tests/test_quotes.py -q` / tdd-metadata-red.log | exit 1; malformed metadata unexpectedly accepted; fixture errors excluded | 2026-10-03T01:29:44.515661+02:00 |
| `.venv/bin/python -m pytest tests/test_quotes.py -q` / batch2-feature-red.log | exit 1; earlier normalized work incorrectly selected profile | 2026-10-03T01:47:54.769835+02:00 |
| `.venv/bin/python -m pytest tests/test_quotes.py tests/test_quote_cli.py -q` / batch2-runtime-green.log | exit 0; 24 passed | 2026-10-03T01:51:03.928564+02:00 |

Final Ruff/type/generation/docs/build and independent current-input evidence follows in the verification handoff. No native pass, CodeRabbit upload or PR acceptance is inferred.

Final scoped checks (retained batch2-checks.json binds exact arguments/start/end/exit):

| Command | Exit | Completed Europe/Berlin |
| --- | --- | --- |
| `.venv/bin/ruff format --check src/changecost quality/index.py tests/test_quotes.py tests/test_quote_cli.py tests/test_cli.py` | 0 | 2026-10-03T01:53:41.585207+02:00 |
| `.venv/bin/ruff check src/changecost quality/index.py tests/test_quotes.py tests/test_quote_cli.py tests/test_cli.py` | 0 | 2026-10-03T01:53:41.595316+02:00 |
| `.venv/bin/basedpyright src/changecost quality/index.py tests/test_quotes.py tests/test_quote_cli.py tests/test_cli.py` | 0 | 2026-10-03T01:53:42.457373+02:00 |
| `.venv/bin/python -m pytest tests/test_quotes.py tests/test_quote_cli.py tests/test_reconciliation.py tests/test_store.py tests/test_contracts.py tests/test_contract_cli.py tests/test_cli.py -q` | 0 | 2026-10-03T01:53:47.208455+02:00 |

`UV_CACHE_DIR=/private/tmp/changecost-uv-cache .venv/bin/python -m quality build --base 3009b351d5108b60e9ba8649a9ef4aa0c0feb9f9 --manifest .changecost/workflow/quote-01-empirical-estimation/manifest.txt` completed exit 0; clean installed wheel ran both offline contract test methods, including priced Quote/retry/explain, in 5.787 seconds on Python 3.13.14. Timestamp: 2026-10-03T01:52:23.268767+02:00.

## Collected correction batch 3 — 2026-10-03 Europe/Berlin

After explicit private-diff upload approval, the single authenticated local CodeRabbit
review completed with two major findings; its NDJSON is retained locally (SHA256
aed431e8f244674fedbcc5d046f228afccf5955b4eb322403d5fec99aa43c934).
Independent triage confirmed broad unrelated dependency disclosure and unrelated
closure-import failure. A historical result leak was not demonstrated. Repeated
global-index cost was inspected but no additional performance scope was approved.

The first genuine current-capability documentation escape after batch 2 underwent
independent family-wide invariant review before patching. Current contracts,
settlement and proposal claims now distinguish the implemented estimator from
provider/collection/budget capabilities; explicitly historical preparation/reviewed
baseline evidence remains intact.

Real red: `.venv/bin/python -m pytest tests/test_quotes.py -q` returned exit 1
because a Quote included an unrelated private repository Change reference.
The regression verifies foreign Change/Run/normalized-economics omission and
successful target-only dependency-closure portable import. Existing source
selection/economic replay semantics are retained. Quote dependencies now start
from its target and actually evaluated peer Changes, reconciliation inputs and
exclusions, and consulted feature-timing proofs; canonical typed graph closure
adds transitive records. Relevant unbound economics and unattributed core Evidence
remain explicit, without guessing a missing repository. Target timing proofs
retain linked Run/Interval/EvidenceBinding and correction-connected economics.

Green: `.venv/bin/python -m pytest tests/test_quotes.py tests/test_quote_cli.py tests/test_reconciliation.py tests/test_store.py tests/test_contracts.py tests/test_contract_cli.py -q`
returned exit 0, 237 passed in 2.06 seconds. Ruff format/check and scoped BasedPyright
returned exit 0 (zero errors/warnings). Retained logs: batch3-inputs-red.log and
batch3-scope-green.log.

This collected batch reaches the original three-correction allowance. The session
requires explicit maintainer extension/replanning before additional independent
review/publication; none is inferred. Local correction proof is not final current
full assurance, remote review, supported-Linux native evidence or PR acceptance.

batch3-inputs-red.log completion: 2026-10-03T10:42:26.933373+02:00.

batch3-scope-green.log completion: 2026-10-03T10:45:35.528632+02:00.

## Native maintainability correction — 2026-10-03 Europe/Berlin

The first supported Ubuntu native run on commit
`eab1201f26f0617da3700e7f493deb3e3c0f93ea` failed Radon full enforcement:
[run 37117591704](https://github.com/nold-ai/changecost/actions/runs/37117591704).
Both matrix jobs reported the same six blockers: `estimation_inputs` complexity
17, `estimate` 34, `feature_valid` 20, `feature_inputs` 16, `inspect_quote` 19,
and installed CLI `prove_quote_roundtrip` length 146 lines. Nine other required
analyzers passed; none was unknown. This is genuine failing gate evidence for a
behavior-preserving refactor, rather than an invented failing behavior test.

The maintainer's renewed instruction to fix identified defective classes and PR
annotations authorized one additional collected correction batch for these six
blockers. Existing history and the original 90-active-minute budget are retained.
Old-head Codex code/security and CodeRabbit reviews completed without actionable
annotations; their acceptance does not cover the refactored head.

The refactor separates peer evaluation, ordered cohort selection, Quote creation,
feature timing/evidence selection, metadata validation, and replay rendering.
Quote explanation retains one read connection and transaction throughout replay.
The installed-wheel fixture separates public CLI lifecycle, economics, coverage,
and assertion stages; it still uses no source imports and blocks network access.

Early feedback uses isolated pinned Radon 6.0.1 without dependency/lock changes:
`UV_CACHE_DIR=/private/tmp/changecost-uv-cache uv run --with radon==6.0.1 --no-project radon cc -j src/changecost/quotes.py src/changecost/models.py`.
The six named functions now have complexities 2/1/7/3/5 respectively and CLI
roundtrip length 6 lines; extracted helpers remain below the blocking complexity
threshold and under 80 lines. Ruff format/check and scoped BasedPyright passed.

Behavior preservation proof:
`.venv/bin/python -m pytest tests/test_quotes.py tests/test_quote_cli.py tests/test_contracts.py tests/test_reconciliation.py tests/test_store.py tests/test_cli.py -q`
returned exit 0: 220 tests and 4 subtests passed in 4.60 seconds, including the
clean installed offline Quote/retry/explanation proofs. This early local feedback
is not supported-Linux native acceptance; exact-head CI and fresh independent and
remote review remain required after the refactor.

## Native-family first-escape closure — 2026-10-03 Europe/Berlin

The broader canonical Radon/KISS investigation identified two remaining arity
errors after the complexity extraction: `quote_result` accepted 10 parameters
and `quote_coverage_fixture` accepted 8 including `self`. This investigation was
recorded before edits. The maintainer's renewed fix instruction authorized the
minimum additional collected batch for these two identified native-family
findings; five total batches and the original 90-minute allowance are retained.
No counter reset or blanket allowance was inferred.

Local red/green feedback invokes the pure canonical `_kiss_metric_findings` and
`_map_radon_complexity_findings` functions from the installed native runner,
SHA256 `4a15673a9ff26c34a4a9becad794ce450dbf6e2b6e2549bf230946c4d4ac7101`,
with fresh pinned Radon 6.0.1 complexity output over all 11 intended Python paths.
The red report contained exactly the two arity errors. Quote construction now
remains inside the six-parameter `estimate`, retaining extracted peer/cohort
stages. The installed fixture passes related run/window and evidence/economic
values as existing tuples, reducing the coverage helper to five parameters;
no general context abstraction was added.

The same complete four-rule oracle now exits 0 with no errors: complexity,
function length, control-flow nesting and total parameter count were checked.
Its 18 warnings remain advisory under the canonical thresholds; reviewed
examples include six-parameter Quote helpers, existing economic-work complexity
13, and existing installed economic proof length 120. They do not weaken or
waive the full native gate. The oracle retains input hashes and the canonical
source digest in ignored workflow evidence, and is preparatory feedback rather
than sealed native assurance.

Ruff format/check and scoped BasedPyright passed. The existing 220-test behavior
suite plus four subtests passed, including both installed offline public CLI
proofs; no behavior red was invented for this pure refactor. Supported-Linux
native assurance, independent final verification, and fresh remote review remain
pending for the final committed head.
