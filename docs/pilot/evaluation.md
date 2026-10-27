# Reproduce an offline synthetic evaluation

Run the declared synthetic experiment from the repository root with the installed
ChangeCost development environment. This command prints JSON and uses disposable
SQLite stores. It does not open the database selected by the global `--db` option.

```sh
uv run --locked changecost evaluate-synthetic \
  --history examples/evaluation/history.json \
  --protocol examples/evaluation/protocol.json
```

The Python API is `changecost.evaluation.evaluate_synthetic(history, protocol)`.
Both arguments are paths. Its return value has deterministic `core` content and
an optional `measurements` envelope. The committed example contains one economic
case and four adaptive cases, including cold start, learning, transfer-only
availability and costly rehearsal. The first economic case has 20 complete peers
with billed USD amounts 1 through 20 and USD 15 truth. Its candidate and broad
baseline both return p50 USD 10 and p90 USD 18. The width is USD 8 and signed p50
error is USD -5. Adaptive cases without complete money remain outside economic
accuracy counts even when complete token truth is available.

To record overhead for five independent disposable runs, add `--measure-runs 5`.
The envelope records elapsed milliseconds, input bytes, store bytes, Python version,
platform and timer. It times import, computation and report construction, excluding
initial JSON parsing, final output serialization and temporary-directory cleanup.
It does not claim a speedup, a production latency estimate or live collection cost.
Timing never enters the deterministic core. A failed repetition produces a safe
error instead of a partial success report.

## Input contract

The history uses `changecost/synthetic-evaluation-history-v1`, asserted provenance
`synthetic_fixture_only`, a normal portable `changecost/v1` Bundle and an ordered
list of deliveries. Each record appears in exactly one delivery. The destination
learns those records at the declared delivery time. Existing origin observations
remain foreign observations and confer no local computation authority.

The protocol uses `changecost/evaluation-protocol-v1`. It declares its version,
registration time, full-change economic identity, fixed minimum 20, minimum independent truth count, formula version,
all four methods, cases, observation cutoff and source gaps. Each case specifies
one Change, an initial forecast time, independent truth time and optional diagnostic
update times. Adaptive cases select a pre-registered ValidationPolicy, ecosystem
and assessment. An optional rehearsal assessment gets its own broad comparator.
A case can instead select an imported historical forecast to test replay refusal.

Registration must precede evaluated assessments. Their scoped policy must also
precede each assessment. Deliveries at equal times retain their listed order.
At a shared timestamp, deliveries precede forecasts, truth scoring and updates.
A selected target or adaptive selector must arrive strictly before its forecast.
The synthetic timestamps model an experiment. They do not prove that a live
protocol was historically registered.

The command rejects unknown fields, duplicate JSON members, nonfinite or floating
JSON numbers, unsupported native usage and non-synthetic providers. Each input is
limited to 16 MiB. Numeric strings have at most 256 characters and decimal
exponents have magnitude at most 256, including Unicode decimal digits accepted
by the existing numeric contracts. Component unit and basis identifiers, including
policy and rehearsal budget/overhead components, are checked before computation.
Report identifiers use at most 200 ASCII
letters, digits, underscores, periods, colons and hyphens, beginning with a letter
or digit. Errors omit rejected fields, values and filesystem paths. Synthetic
provenance is a caller assertion, not an automatic real-data detector. Do not put
real customer records, prompts or secrets in these files.

## Metric definitions

All amounts and errors use exact rational arithmetic. A fraction such as `3/5`
is an exact value, not rounded decimal output. Signed error is prediction minus
actual; a negative error means underestimation. Empty denominators produce null
values with reasons. Coverage uncertainty is a Wilson 95% interval with
z = 1.959963984540054, rounded to six decimal places.

Economic candidate and baseline use the same exact cutoff, eligible peer history,
economic identity and fixed minimum 20. The baseline is a report-only repository
estimate, not an invented stored Quote. The default Quote algorithm is unchanged.
One-sided availability sets `comparison_error`, suppresses both aggregate accuracy
objects and exits with code 2. Jointly unpriced, non-initial, replay-unavailable
and incomplete-truth cases retain their counts outside accuracy denominators.
Economic accuracy includes p50 and p90 coverage, mean signed and absolute p50
error, and mean p90-minus-p50 width in the original identity.

Adaptive measurements explicitly use `observed-summary/v4`. Repository and
dimensional errors are compared on shared eligible complete truth and grouped by
registered policy. Available and scored counts remain separate. Observed median,
minimum and maximum are not empirical quantiles. Transfer diagnostics use the
median, minimum and maximum of the existing scenario array. Support-pair, donor
and complete-truth counts remain separate. Scenario point error does not enter
observed-range coverage or create a measured validation receipt.

Rehearsal overhead is reported in its own component. Net benefit is broad
absolute error minus assessed absolute error minus overhead, only for compatible
units and the same assessment. Otherwise it remains undefined. The underlying
registered rubric checks coverage, underestimation, width, overhead and baseline
error. A per-case `synthetic_rubric_passed` value is only a synthetic diagnostic.
Distinct scope groups disclose repeat-task dependence; they do not establish
independent sampling. No sample count or effort establishes calibration.

Truth is scored at its checkpoint and retained before later deliveries. Economic
truth records all linked attempts and settlement/coverage dependency references.
Demand truth records selected observation revisions. Later updates never enlarge
primary case counts. Generated destination IDs are normalized; portable revision
and dependency IDs remain intact. Existing demand selection and validation enforce
target exclusion, including nested validation support and bridge participation.

Attribution counts raw eligible economic records at the observation cutoff. Its
provider/manual/unbound categories are mutually exclusive and include unknown
money. Provider means asserted `verified_provider` binding provenance, not new
provider approval. The report separately displays effective selected event counts,
known amounts, unknown-money counts and reconciliation diagnostics. Conflicting
portable identities reject import; successful experiments cannot retain such
conflicts as financial truth. Duplicate delivery/record IDs reject rather than
inflate the raw denominator. Pending corrections remain diagnostic exclusions.

Abandoned share divides complete abandoned spend by complete accepted-plus-abandoned
spend for the same identity. Each linked retry contributes once. Any unknown
terminal amount makes the whole-population share undefined. A zero denominator
is also undefined. The report retains known subtotals and unknown counts.

## Limits and recovery

The conclusion is always `synthetic_only_not_yet_validated`. Complete token truth
does not establish money. Provisional Codex counters and source approval do not
establish complete evaluation truth. Live pilot assessment, calibration, provider
admission and publication need their own authorization and evidence.

No user-store migration or rollback is needed. Temporary stores are removed on
normal completion and handled failures. Removing the additive command/evaluator
and the default-preserving baseline selector rolls back this feature. Review
current [findings](findings.md) and the selected change's
[TDD evidence](../../openspec/changes/pilot-02-calibration-evaluation/TDD_EVIDENCE.md)
before relying on its assurance status.

## Prepare the separate live lane

The offline implementation merged in [PR #48](https://github.com/nold-ai/changecost/pull/48)
on 2026-10-27. Follow the [live assessment preparation guide](live-assessment.md)
for pending operator decisions and future closure checks. Its private manifest is
documentation only. The real-evidence entrypoint and source/complete-measurement
approvals remain missing; the command above remains synthetic only. Preparation
keeps #17 active and authorizes no live collection or outcome inspection.
