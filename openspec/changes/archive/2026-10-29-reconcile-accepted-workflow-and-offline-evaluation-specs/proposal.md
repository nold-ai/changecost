# Reconcile accepted workflow and offline evaluation contracts

## Why

The maintainer requested archival of implemented contracts before the merged Claude
reader is archived. Main specs omit accepted risk-first guidance from
[PR #42](https://github.com/nold-ai/changecost/pull/42) and the synthetic evaluator
from [PR #48](https://github.com/nold-ai/changecost/pull/48). Their original changes
also contain genuine future trial and live-assessment work. Archiving either whole
change would misrepresent that work as delivered.

On 2026-10-29 Europe/Berlin, the maintainer authorized this specification and
lifecycle reconciliation. This change records only shipped behavior through native
OpenSpec archival. It introduces no product behavior or new product issue.

## What changes

- Add the exact first four risk-first workflow requirements and 11 scenarios to the
  existing bounded-review-session capability through the archive CLI.
- Add seven pilot-evaluation requirement identities and 22 scenarios, explicitly
  limited to the shipped synthetic evaluator.
- Preserve the original #17 and #40 changes, all task checkbox states and all TDD
  history. After CLI synchronization and readback, rebase only their future deltas
  against main and append dated mappings to their planning artifacts.
- Keep the adoption trial, real-evidence boundary, live assessment, measurement
  approval and calibration authority pending in their original changes.

## Capabilities

### New capabilities

- `pilot-evaluation` records the already shipped offline synthetic contract. This
  capability exists in #17's active delta and is new only to main specs.

### Modified capabilities

- `bounded-review-session` gains the four already shipped risk-first guidance
  requirements. Existing requirement bodies remain unchanged.

## Impact

Only OpenSpec and correlated lifecycle documentation change. Runtime, tests,
provider admissions, stores and historical evidence remain unchanged. The
[design](design.md) maps every transferred requirement to merged source and records
which real-provider scenarios remain future work. Strict selected and all OpenSpec
validation, relevant documentation/index checks and independent wording review are
required. Runtime TDD would fabricate a behavior change that this work does not make.

The principal risk is claiming native ingestion or live calibration from a synthetic
report. The evaluator rejects native_usage and every non-synthetic provider.
Its conclusion always remains `synthetic_only_not_yet_validated`. Scoped rollback
reverts only the reconciliation and lifecycle diff through ordinary Git history.
No user-store migration, paid service or collection is required. Duration and
historical cost are unknown.

## Non-goals

No #17 or #40 closure or whole-change archival. No retrospective trial from PR #50
usage or detector measurements. No real-outcome inspection, live collection, runtime
implementation, provider approval, measured truth approval, aggregate publication,
merge, release or deployment. Historical missing prior-RED proof remains incomplete.
