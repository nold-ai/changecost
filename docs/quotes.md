# Offline empirical Quotes

Quotes estimate a registered target Change using complete historical peer Changes in
one repository and economic identity (kind, unit, currency, basis). The pilot is
unreleased; synthetic validation does not establish provider support or calibration.

## Population and source boundary

Each accepted or abandoned peer contributes one exact aggregate including all linked
terminal attempts, including failed/cancelled retries. The target is excluded. Selection
reuses normalized reconciliation and full-interval coverage at one committed cutoff;
old settlements and imported completeness claims are not eligibility caches. Open or
zero-run Changes, unknown amounts, missing/unsupported coverage, unresolved corrections,
ambiguous overlap and potentially relevant unbound evidence are excluded with reasons.
Supported observed zero counts; absent evidence does not imply free work.

The only complete source policy is synthetic/fixture, profile/policy synthetic/v1,
namespace opaque, usage series, charge component and billed monetary USD. Unsupported
identities remain separately representable and unpriced; there is no conversion or
new provider mapping. Quotes create no settlement revisions.

## Exact ranks and cohort backoff

For n exact Decimal amounts sorted ascending, nearest-rank p50 selects ceil(50*n/100)
and p90 selects ceil(90*n/100), using one-based ranks. Integer arithmetic selects the
rank without floating conversion, interpolation or intermediate rounding. For values
1 through 20 USD, p50 is 10 USD and p90 is 18 USD. Signed totals and zero are retained.

The recorded default minimum is 20 peer Changes; a strict positive integer override
is supported. The first qualifying cohort is selected in this fixed order:

1. Repository, change_shape, trajectory and execution_profile.
2. Repository, change_shape and trajectory.
3. Repository-wide.

All levels retain the same population and economic identity. Counts and rejection
reasons are stored. If none qualifies, both quantiles are null and the result is
unpriced. Empirical p90 is a pilot default, not a calibrated confidence bound or budget guarantee.

Features are immutable normalized features/v1 registration snapshots. Narrow matching
requires all relevant fields and capture/local availability before first Run registration
and known work, including cutoff-visible normalized economics attributed to any
linked attempt and its correction-connected inputs. Late or missing features skip narrow membership with reasons while
repository fallback can still use otherwise complete peers. No trajectory is inferred
from retries, outcomes or post-work reconstruction.

## Atomic operation and historical explanation

See [CLI examples](cli.md#empirical-quote-computation). Required selectors are target,
repository, economic identity and caller operation ID. A single writer transaction
captures the committed cutoff and writes the Quote and local receipt. Response-loss
retry returns the original result without adding history; conflicting request/kind reuse
fails unchanged. Invalid inputs or failure before commit leave no partial Quote/receipt.

Stored metadata retains target features, parameters, selected exact peer totals/support,
ordered cohorts, exclusions and synthetic provenance. Inputs retain consulted normalized
and lifecycle dependencies. Explain verifies the exact stored payload and recomputes
supported versions at its original time/sequence cutoff in one read snapshot. Later
imports, bindings or corrections do not leak into the historical result.

Portable claims remain distinct from local receipts. Older Quotes without metadata
are not_computed; foreign/future/unavailable cutoffs or unsupported versions cannot
certify replay. A consistent [backup](contracts.md#transactions-revisions-and-historical-limits)
preserves local receipts; portable import establishes destination availability when it
arrives. Keep records private and use allowlisted normalized data, never prompts or transcripts.

No package version or SQLite layout migration is introduced. Back up before changing
checkouts; rollback uses a follow-up code revert and separate compatible backup restore,
retaining original records. Advisory CI, provider adapters and calibration remain pending.
