# Design: Define change, run, quote and settlement contracts

## Context

See [proposal](proposal.md) and [capability spec](specs/change-run-contracts/spec.md).
The current repository contains documentation and hygiene gates, with no product
package or runtime. This design describes later implementation, not delivered behavior.

## Goals / Non-Goals

**Goals:** Make the specified capability local, reproducible and explicit about missing evidence.

**Non-Goals:** No provider importers, price service, distributed ledger, remote storage, automatic Git/IDE attribution, or additional public command family.

## Decisions

1. Use Pydantic contracts with explicit kind and schema=changecost/v1. Change has a caller-supplied stable change_id within an explicit repository_id, optional commit/PR references and separate outcome. Run identity is the structured RunRef tuple (repository_id, provider, surface, run_id), with optional provider session/trace IDs as separate metadata. Quote embeds quantiles or unpriced reason, unit/basis, cohort, evidence cutoff, algorithm version and creation time. Settlement embeds aggregate components, completeness, provenance and revision references.

2. Use standard-library SQLite under .changecost/changecost.sqlite3 by default, with explicit path override. Tables for records/bindings/revisions use uniqueness constraints and transactions; schema migrations are numbered. No ORM or daemon is needed. Portable JSON is independent of SQLite and contains only allowlisted economic metadata.

3. Bind supports two explicit relationships: a namespaced run to a repository/change,
   and an exact source-evidence record to that run. The latter accepts an evidence_id
   selector in the existing bind command family, including for records with no
   provider session ID. A changecost/v1 evidence reference carries evidence_id,
   provider/surface, source profile and identity scope: either a verified namespaced
   source event key, or an exact-file digest plus logical record ordinal. Import
   results and explain expose these references so users can select a record without
   retaining its raw payload. File-scoped references make no cross-export identity claim.
   A portable mapping carries evidence_id, the complete target RunRef, method (manual or
   verified_provider), recorded_at and effective_at; an explicit user mapping is always
   manual. Referenced evidence and target run must exist, or be present in the same
   atomic artifact import. Repeating either identical relationship is idempotent;
   conflicting relationships fail without mutation, including a manual assignment that
   disagrees with an existing verified provider join. Export/import preserves mappings
   and identity scope. A later rebind requires a separately authorized audited correction,
   not silent overwrite. Neither runs nor record mappings are inferred from time proximity.

4. Decimal values serialize as finite decimal strings. Each economic component has
   a kind (monetary or nonmonetary), unit and basis. Known monetary amounts require a
   currency; unknown monetary currency remains null and cannot participate in currency
   comparisons. Nonmonetary quantities such as tokens, provider credits and nano AIU
   have currency=null (not applicable), even when their amount is known. Keep provider
   denomination and token category in the unit identity so unrelated credits or token
   categories cannot be combined. A null amount means unknown; zero means observed zero.
   Reject nonmonetary components with a currency, known monetary amounts without one,
   NaN, infinity, unsupported major versions and incompatible aggregates. Round only
   presentation, with displayed precision and half-even rounding; keep exact amounts.

5. Use UTC timestamps with offsets normalized, plus recorded_at and effective_at to support historical replay. Local display may use Europe/Berlin. Atomic import validates the entire artifact before commit; unknown versions and conflicts leave state unchanged. Export/import round trips retain stable IDs and correction links.

## Run identity and references

Use the same structured RunRef (repository_id, provider, surface, run_id) in persisted
keys, portable records, both binding relationships, bind/settle/explain selectors,
outcome revisions and settlement coverage references. Tuple fields are separate
strings, not delimiter-concatenated keys; compare exact values without case folding
raw identifiers. A bare run_id is not a valid Run selector, even if locally unique.
Do not infer the target Run namespace from source evidence: a manual mapping names
its target explicitly. Equal raw IDs in different repositories/providers/surfaces
are distinct Runs and survive export/import without collision. Same full RunRef with
conflicting metadata remains an atomic conflict, not a second Run.

## Work intervals and availability

Each Run has revisioned nullable work_started_at and work_ended_at UTC timestamps,
plus interval method (manual or verified_provider), source references when applicable,
and recorded_at/effective_at. Bounds describe actual work, not record creation or
outcome declaration. The interval is closed [start, end]; equal bounds allow a
single instant. Evidence is still deduplicated by identity, never by interval alone.
A missing bound means unknown; do not substitute registration, outcome, first/last
observed event or import time. Known bounds must satisfy start <= end and cannot
be later than their declaration's recorded_at. Bounds on portable records are
validated against original declaration time, not silently rewritten on import.

`bind --register-run --work-start <UTC>` may supply an observed start; omission is
allowed. `settle` with a full RunRef accepts `--work-start` and/or `--work-end` to
fill unknown bounds, independently of outcome flags. Source import may fill bounds
only using a feasibility-verified profile that defines actual Run start/end semantics.
Manual values stay manual; source agreement does not relabel their provenance.
Identical updates are idempotent. Replacing a known bound requires `--correct-interval`
and a nonempty reason, appending a revision; invalid ordering or a conflicting
uncorrected value fails atomically, including any combined outcome update. Provider
interval corrections require a documented correction relationship.

Source coverage must enclose both declared bounds and all attributed work. Compare
work timestamps/spans defined by the verified source profile, not billing publication,
import or correction-arrival times. Evidence of work outside the bounds invalidates
full-change coverage until an explicit interval
correction or audited attribution correction resolves the conflict. Manual intervals
do not establish source completeness/finality: that requires separate verified
coverage evidence. Retain all interval revisions for cutoff-aware replay.

Every store has an immutable store_id. Every locally created or imported record,
revision and relationship has a store-local available_at set when first successfully
committed there: evidence, mappings, registrations/features, interval/outcome revisions,
coverage/settlement revisions and Quotes alike. Reimport preserves the first local
availability; rejected writes create none. available_at is not caller-settable or
backdated from recorded_at/effective_at. Derived records become available no earlier
than their own commit and all inputs. Export retains origin store/timing provenance;
import always adds destination store_id/available_at without treating origin times
as destination knowledge.

Historical selectors require local available_at, recorded_at and effective_at no
later than the cutoff for every selected dependency (including bindings, Run-set
membership, interval/outcome and completeness evidence). Quotes retain the store_id,
cutoff and exact revision references. An imported historical Quote remains inspectable,
but destination replay cannot claim to reproduce source-store knowledge: if required
inputs were not locally available at that cutoff, return replay_unavailable with a
reason instead of validating the old quote or backdating imports. Same-store history
and its intact original database can support original-cutoff replay; portable import
alone is not a restoration of that store's availability history.

## Registration, outcomes and cohort inputs

The following operations belong to the existing command families; no sixth family
or manually authored bootstrap artifact is required:

- `bind --register-change` takes repository_id, change_id and optional cohort inputs.
  It creates an open Change, even in an empty store, without inventing a Run.
- `bind --register-run` takes repository_id, change_id, provider, surface and run_id.
  The Change must exist and be open. It atomically creates an open Run and its
  explicit run-to-change binding. Register each retry with a different run_id.
- Plain `bind` associates existing records as defined above; it does not silently
  create missing targets. Registration modes and evidence-binding mode are mutually
  exclusive. Repeating a registration with identical immutable inputs is a no-op;
  conflicting metadata fails atomically. A repeated identical registration does not
  reopen an existing terminal record or replace its original timestamps.
- `settle --run-outcome succeeded|failed|cancelled` records a named Run's terminal
  outcome; `settle --outcome accepted|abandoned` records a named Change's terminal
  outcome. Outcome-only requests need no imported costs. Outcomes are explicit user
  declarations with recorded_at/effective_at, not inferred from cost completeness.
  Repeating the same outcome is idempotent. A different terminal outcome requires
  `--correct-outcome` and a nonempty reason; append a revision rather than overwriting
  history. Returning to open is outside this pilot. Late source evidence/corrections
  can still revise settlement amounts; they neither reopen records nor drop retries.
  New Runs cannot be registered against terminal Changes.

Change registration stores an immutable `features/v1` snapshot with captured_at and
recorded_at set to registration time in UTC. Optional values are:

| Field | Canonical values | Meaning at registration |
| --- | --- | --- |
| change_shape | bugfix, feature, refactor, docs, maintenance, other | Intended category of the requested change. |
| trajectory | single-pass, iterative, investigative | Intended work pattern, never observed retries or final outcome. |
| execution_profile | copilot-cli, copilot-ide, cursor-cli, cursor-ide, mixed | Intended tool/surface; mixed means multiple planned surfaces. |

For every field, trim ASCII whitespace and lowercase ASCII letters; missing or blank
input becomes null, and any other value is rejected rather than guessed. Null means
unavailable, not an additional cohort category. Registration persists the normalized
snapshot; later registration cannot update it. Inputs that change during execution
remain differences between intent and actual execution, not retroactive edits to the
quote's features. New feature semantics require a new version, never silent relabeling.

Portable records retain snapshot version, values and original capture/record times;
imports additionally record local available_at. Historical selectors use the actual
availability cutoff of the evaluated store, not a backdated import timestamp. A
pre-run feature snapshot must have been captured before the first run registration
and before any known earlier run evidence. Missing, late or incompatible snapshots
remain unusable for narrow cohorts; repository-wide eligibility is unaffected.

## Dependencies and evidence

- [core-01-python-foundation](../core-01-python-foundation/proposal.md)

Shared boundaries and current provider evidence are recorded in the
[source assessment](../../../docs/research/pilot-source-assessment.md).
No provider-specific mapping becomes supported merely by appearing in this plan.

## Risks / Trade-offs

- Identity collision → namespace identifiers and enforce uniqueness.
- Float drift or unit mixing → Decimal strings and explicit unit/basis validation.
- Interrupted migration → transaction plus portable backup; never destructively downgrade a database.

## Migration Plan

After separate implementation authorization, land this change in dependency order
with spec-derived failing and passing evidence. Update docs/contracts.md, docs/cli.md, and README.md.
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
