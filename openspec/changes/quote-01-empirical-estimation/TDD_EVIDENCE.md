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
