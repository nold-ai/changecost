# Offline evaluation findings

The implemented experiment reproduces synthetic economic and adaptive reports.
It does not validate native accuracy or complete the live pilot. The decision
remains **not yet validated**.

The committed economic case demonstrates the existing nearest-rank calculation.
Twenty peers with billed USD amounts 1 through 20 produce p50 USD 10 and p90 USD 18
for both repository fallback and baseline. Against USD 15 truth, p50 coverage is
0/1, p90 coverage is 1/1, signed p50 error is USD -5 and width is USD 8. One synthetic
observation cannot establish calibration or independent sampling.

Separate adaptive cases demonstrate cold start, observed summaries, additional
transfer-only scenario availability and a costly rehearsal. Their token observations
remain separate from billed money. An expensive rehearsal fails the scoped overhead
criterion despite available observed samples. Scenario diagnostics do not create
validation receipts. Tests also exercise useful/harmful transfer and scoped local
receipt withdrawal with an observable effect on a future forecast.

Attribution tests preserve all ten records in the six-provider, two-manual,
two-unbound example. Correction tests freeze forecast inputs and truth independently.
Foreign imported forecasts retain replay-unavailable status. Terminal updates and
all retries remain visible without enlarging the initial accuracy denominator.

The source gaps remain material. Cursor monetary reconciliation has no verified
money in this evaluation. Complete native token, time and effort truth are not
approved by this synthetic experiment. The finite Codex reader and provisional
thread totals confer neither demand nor billing authority.

Next evidence requires explicit authorization for a selected live lane, an approved
measurement policy with complete all-attempts truth, a genuinely pre-registered
rubric and enough independent cases to distinguish improvement from the baseline.
No universal provider-readiness or accuracy claim follows from this implementation.

Focused executable checks and real failing/passing evidence are recorded in the
[selected change](../../openspec/changes/pilot-02-calibration-evaluation/TDD_EVIDENCE.md).
Aggregate assurance and independent reviews belong to the verification stage.
Unchecked chronological TDD obligations are retained where later regression
variants lack a separately recorded pre-implementation failure. This is a stated
limit, not a passing check or future waiver.

## Current checkpoint, 2026-10-27 Europe/Berlin

The offline implementation merged in [PR #48](https://github.com/nold-ai/changecost/pull/48)
at `401e43ed63a9da3e39f55fc29d1e7160d1d06d2e`, with the verified source tree
`2df0883b75cb3b78503fd358550255c01c854405`. Post-merge
[main assurance run, attempt 2](https://github.com/nold-ai/changecost/actions/runs/40563257194/attempts/2)
passed both supported host matrix jobs. Each native report records all ten required
members executed and passed, no UNKNOWN evidence, and `PASS_WITH_ADVISORY`.
The source inventory has 303 members and digest
`dba3a52fe4bc8c57ef90a1e8b97a614a71675ad6a279471a7d572d3f84aa8fbc`.
This is assurance of that merged source, not live calibration evidence or assurance
of future preparation edits. Earlier PR timeout reports and the separate initial
main billing/pre-start block remain historical evidence. No root cause is inferred.

The maintainer selected preparation while keeping #17 active. The
[live guide](live-assessment.md) records pending lane/cohort/operator decisions,
separate approvals, private manifest, chronology and rubric fields. No real dataset
or live outcomes were inspected during this preparation. A real-evidence runtime
boundary remains unimplemented independently of dataset availability. Synthetic
coverage policies cannot confer native demand or economic authority. Tasks 3.0-3.6,
historical prior-RED obligations and conditional full-story integration remain open.
The conclusion remains not yet validated, with no passing live receipt.


## Accepted synthetic specification, 2026-10-29 Europe/Berlin

Native CLI archival synchronized seven accepted synthetic requirements and
22 scenarios into the [main evaluation specification](../../openspec/specs/pilot-evaluation/spec.md).
The [reconciliation archive](../../openspec/changes/archive/2026-10-29-reconcile-accepted-workflow-and-offline-evaluation-specs/proposal.md)
records the already merged PR #48 contract. This supplies no new experiment,
live receipt or prior-RED evidence. Original #17 task history remains intact;
its active delta now describes the separate future live assessment.
