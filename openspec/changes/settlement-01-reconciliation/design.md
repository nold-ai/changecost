# Design: Reconcile evidence into revisioned settlements

## Context

See [proposal](proposal.md) and [capability spec](specs/evidence-reconciliation/spec.md).
The current repository contains documentation and hygiene gates, with no product
package or runtime. This design describes later implementation, not delivered behavior.

## Goals / Non-Goals

**Goals:** Make the specified capability local, reproducible and explicit about missing evidence.

**Non-Goals:** No inferred cash prices, universal invoice reconciliation guarantee, automatic attribution, provider API calls, or budget enforcement.

## Decisions

1. Normalized evidence carries provider/surface, source schema, source event key, recorded/effective timestamps, run/session IDs when present, unit/basis, amount or null, completeness and correction target. Expose the core evidence_id and identity scope in import results and explain, and consume portable evidence-to-run mappings without weakening their provenance. Store a minimal source fingerprint and provenance, never a raw prompt-bearing payload.

2. Deduplicate by stable source event identity and source namespace. Same key/same normalized payload is idempotent; same key/different payload is a conflict unless a documented correction relationship exists. Without stable cross-export identity, mark dedupe limited; file hash plus row position prevents exact-file reimport only and must not claim overlap dedupe.

3. Treat event deltas and cumulative snapshots as separate evidence lanes. Never add a cumulative total to its constituent deltas. Source adapters choose one documented authoritative lane per series; unsupported ambiguity produces an incomplete settlement. Retries with distinct event identities count as distinct expenditure even if a final patch is accepted.

4. Corrections append revision records linked to original evidence; compute a new aggregate without deleting the previous settlement. Out-of-order corrections remain pending until their target arrives. Explicit not-billed or reversal evidence is distinct from missing money. Each settlement includes an as-of timestamp and recorded-at cutoff.

5. Keep change outcome (open/accepted/abandoned) separate from financial completeness (provisional/reconciled). Accepted changes include all known linked attempts. Abandoned changes retain expenditure. Reconciled means complete for a declared source interval/unit and supported evidence, never proof of invoice agreement without a bill comparison.

6. Aggregate only identical economic kind, unit and basis components, with matching currency for money and currency=null for nonmonetary quantities; report unknown counts and reasons next to known subtotals. Unbound evidence contributes to a repository remainder, not an arbitrary change. Use Decimal without intermediate display rounding.

## Dependencies and evidence

- [core-02-change-run-contracts](../core-02-change-run-contracts/proposal.md)

Shared boundaries and current provider evidence are recorded in the
[source assessment](../../../docs/research/pilot-source-assessment.md).
No provider-specific mapping becomes supported merely by appearing in this plan.

## Risks / Trade-offs

- Double counting → unique event keys and explicit lane precedence.
- Missing cost reads as free → unknown counters and provisional results.
- Late corrections contaminate backtests → keep both effective and recorded timestamps and immutable revisions.

## Migration Plan

After separate implementation authorization, land this change in dependency order
with spec-derived failing and passing evidence. Update docs/settlement.md, docs/contracts.md, and docs/cli.md.
Use synthetic fixtures before any authorized real-data evaluation. This is unreleased;
there is no deployed service to migrate. For local schema changes, export/backup
before migration and validate recovery without deleting the previous data.

Rollback the implementation commit if its checks fail; restore a compatible local
backup rather than forcing an older program to write a newer database. Planning
rollback is a commit revert plus closing the associated issue, preserving history.

## Verification

Each requirement has Given/When/Then scenarios. Exercise negative paths and privacy
boundaries alongside the success cases. Run strict OpenSpec validation and applicable
repository gates; record actual results, not anticipated test or review outcomes.
