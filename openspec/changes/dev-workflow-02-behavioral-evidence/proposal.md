# Proposal

## Why

Repeated full-context review and late behavioral findings remain expensive after the
bounded-review workflow. A small, independently authored lifecycle oracle and reusable,
content-bound review packet can test whether earlier mechanical evidence reduces those
loops without weakening final assurance; the benefit remains a hypothesis to measure.

## What Changes

- Add a compact contributor review packet with intent, invariants, trust boundaries,
  public entrypoints, explicit dependency/assumption mappings, known findings and
  content-bound mechanical evidence. Reuse the existing review-session ledger.
- Add bounded deterministic stateful tests against existing Change/Run operations
  and real SQLite, with an independent model of retry, rejection, correction,
  chronology and representation boundaries.
- Prove the harness detects deliberately faulty controls and passes repaired controls.
  Record actual SpecFact non-capsule inventory/drift/repro coverage separately from
  independent behavioral tests and required supported-Linux capsule review.
- Teach follow-up review to consume the packet plus delta and affected assumptions;
  require renewed broad review when scope, trust boundaries or dependency coverage change.
- Dogfood one bounded pilot and report observed tokens, turns, correction batches,
  drift, pre-PR discoveries, escaped findings and elapsed time. Unknown billing stays
  unknown; historical differences do not establish causal savings.

## Capabilities

### New Capabilities

- `behavioral-evidence-review`: compact evidence validation, independent lifecycle
  testing and a bounded empirical review workflow.

### Modified Capabilities

None. Existing lifecycle behavior and bounded-review counters/budgets remain the
accepted baseline. A proven runtime defect requires a separately described scoped
spec/test correction before runtime edits.

## Impact

Contributor-only `quality/` tooling, test helpers and tests, the four workflow skills,
review/development guidance, documentation ownership/index, generated `llms.txt`,
changelog and change-order mapping. No runtime dependency or published package change
is planned; pytest and standard-library sequence generation suffice for the pilot.

Prerequisites are the delivered [bounded-review story #23](https://github.com/nold-ai/changecost/issues/23)
and [Core-02 story #11](https://github.com/nold-ai/changecost/issues/11), implemented
by merged PRs #24 and #25. Story #11 remains administratively open at preparation;
that discrepancy does not erase the merged code or block this authorized pilot.
The story belongs under [Local core and contracts #6](https://github.com/nold-ai/changecost/issues/6).
Tracking story: [#26](https://github.com/nold-ai/changecost/issues/26).
Issue synchronization is recorded in preparation evidence; artifacts remain locally
prepared/unpublished until a real branch/PR is published.

Verification requires spec-derived failing/passing evidence, faulty/fixed controls,
strict OpenSpec validation, the existing complete quality gate, fresh independent
review and current-head CodeRabbit/hosted review. A successful tool exit without
analyzer execution or current input binding is insufficient evidence.

## Non-goals

No general AST correctness engine, orchestration framework, additional ledger,
SpecFact upstream change, provider adapter, live collection, economic algorithm,
release, deployment, or claim that tests prove all behavior. No import of unrelated
settlement edits or uncommitted retrospective reports.

## Assumptions, risks and rollback

Confirmed: the base includes lifecycle contracts/SQLite and the schema-8 review
session; a generator probe does not bind SpecFact's generic OpenAPI sidecar to these
Python domain operations. Hypothesis: targeted early behavioral evidence and delta
review reduce repeated context and late corrections. No numerical savings target
is justified by one pilot.

The model may repeat implementation mistakes (derive it from scenarios and independently
review it); narrow generation may miss cases (name bounds and retain explicit boundary
fixtures); stale packets may create false confidence (invalidate on input/dependency
changes and keep final current-head gates). Confidence is high in feasibility, medium
in defect yield, and unknown in billing savings. Bound effort by the existing three
correction batches/90 active minutes unless the maintainer explicitly extends it.
Rollback reverts contributor tooling/tests/docs while preserving ignored pilot evidence
and review-session history. No existing store migration is introduced.
