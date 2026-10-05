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
and known work. Every non-null start or end across all cutoff-visible Interval
revisions and linked attempts constrains that timing, even an older end-only
revision later replaced by complete bounds. Equal endpoints are allowed. This also
includes cutoff-visible normalized economics attributed to any
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
supported versions at its original time/sequence cutoff in one read snapshot. The
result's own insertion sequence must equal cutoff sequence plus one, and its local
availability time must equal cutoff time, preserving the supported producer's
original snapshot even after unrelated history advances metadata. The cutoff
time must not exceed the latest committed metadata timestamp; an advanced wall clock
does not authorize a future committed cutoff. Equality and older historical cutoffs
remain eligible, while a missing committed timestamp cannot certify replay. Later
imports, bindings or corrections do not leak into the historical result. Explain reads
the local clock once in that transaction and rejects a clock earlier than the latest
committed local availability, including for imported or unsupported claims. Equality
with the latest availability is allowed. Restore the clock before inspecting history;
an identical durable computation retry still returns its original result unchanged.

Portable claims remain distinct from local receipts. Older Quotes without metadata
are not_computed; foreign/future/unavailable cutoffs or unsupported versions cannot
certify replay. A consistent [backup](contracts.md#transactions-revisions-and-historical-limits)
preserves local receipts; portable import establishes destination availability when it
arrives. Keep records private and use allowlisted normalized data, never prompts or transcripts.

One committed Quote snapshot builds lifecycle, correction-chain, raw evidence and
feature-timing lookups once. Linked peers consult their own attempts and genuinely
shared uncertainty. Zero-attempt peers also share open/terminal diagnostics. Each
peer retains its own references and reasons; unbound evidence and pending corrections
remain auditable. Shared normalized chains, fixed-window series summaries and raw
uncertainty are prepared once, and aggregate Quote dependencies retain their roots
once. Member filtering precedes economic series/lane selection; shared file-overlap
and snapshot decisions still include each member's source interactions. Exact
historical output is preserved, including repeated pending-correction exclusions
when those are required by the audit output. No cohort count cap is added.

No package version or SQLite layout migration is introduced. Back up before changing
checkouts; rollback uses a follow-up code revert and separate compatible backup restore,
retaining original records. Advisory checks and optional CI summaries are implemented
locally, pending current-head verification/acceptance. Provider adapters and calibration
remain pending.

## Budget advice

Read-only check defaults to p90, permits explicit p50 and requires a local typed receipt plus supported historical reproduction before numeric advice. Imported/unpriced Quotes remain unknown with declared values and provenance; see [CLI advice](cli.md#presentation-errors-and-advisory-budgets).

Selected local Quote availability is validated as a typed Observation before
unsupported-version or receipt trust shortcuts. Malformed sequence/timestamp rows
fail with safe technical diagnostics rather than leaking raw row values or
returning a successful unknown claim. Check and explain remain read-only; portable
artifact advice never accesses the local database.
