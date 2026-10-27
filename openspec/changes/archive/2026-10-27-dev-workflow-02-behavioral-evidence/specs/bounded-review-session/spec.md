# Bounded review session post-replan delta

## MODIFIED Requirements

### Requirement: Bounded correction decisions

The workflow SHALL treat a correction batch as one collected finding set followed
by correction and verification, independent of its number of commits.

#### Scenario: Exhausted budget

- **WHEN** a session with valid state and local prerequisite evidence reaches its effective correction-batch or active-time limit, including any explicit extension
- **AND** work, family obligations, or external checks/reviews remain pending
- **THEN** status requires replanning rather than waiting or investigating
- **AND** completion at the exact limit remains permitted only when all current evidence and obligations are satisfied
- **AND** exceeding either limit requires replanning for an otherwise complete session
- **AND** missing, malformed or stale session/evidence inputs retain their incomplete-recovery outcome rather than being overridden by budget replanning.

#### Scenario: Explicit extension

- **WHEN** a maintainer records a budget extension
- **THEN** status retains existing counters and applies only the recorded additional allowance.

#### Scenario: Corrected PR head

- **WHEN** a verified correction creates a new PR head
- **THEN** the session advances its reviewed head while preserving its existing
  budget counters, findings and event history.

#### Scenario: Observation does not grant correction authority

- **GIVEN** correction allowance is exhausted and required checks/reviews are already running
- **WHEN** the operator explicitly requests observation or adjudicates their fetched current evidence
- **THEN** explicit observation continues through budget-only REPLAN without changing its status or counters or authorizing another correction/investigation; other actionable blockers and the absolute deadline still stop observation
- **AND** pending results remain pending, exact-limit completion requires every obligation satisfied, and over-limit completion remains replan.

#### Scenario: Clean verification is not a correction batch

- **WHEN** monitoring or clean verification completes without a collected correction set
- **THEN** no correction batch SHALL be charged; actual prior batch events remain immutable.


### Requirement: Finding-family investigation

The workflow SHALL retain finding identities, evidence, family assignment and
disposition without automatically accepting a moved or repeated finding.

#### Scenario: First escape after correction

- **WHEN** a finding in a corrected family recurs
- **THEN** status requires an investigation of the family invariant, variants, callers and missing tests.

#### Scenario: Escape after investigation

- **WHEN** a finding in an investigated family recurs again
- **THEN** status requires replanning.

#### Scenario: Explicitly resolve named historical escalation findings

- **GIVEN** genuine escalation findings have verified fixed dispositions and current closure evidence
- **WHEN** an authorized approved scope decision names their exact IDs, the current full binding and that verified evidence reference
- **THEN** only those named historical escalation obligations are resolved, retaining all findings, dispositions, investigations and budget counters
- **AND** closure evidence explicitly covers each named finding; current binding and closure are validated at insertion, and valid historical resolution survives subsequent head adoption
- **AND** unknown, nonfixed, unlisted or stale/unbound claims cannot clear an escalation; allowance extension alone has no resolution effect.

#### Scenario: Later escape cannot inherit historical resolution

- **GIVEN** an approved decision resolved named earlier escalation findings
- **WHEN** another genuine finding appears in that family after its investigation
- **THEN** the new finding requires replan; the old decision cannot resolve it by family name or a broad wildcard.


### Requirement: Compact, truthful handoff and monitoring

The workflow SHALL produce a compact packet of scope, pending findings, evidence
and budget state, and SHALL report only meaningful external review changes.

#### Scenario: Unchanged poll

- **WHEN** a monitor poll has the same reviewed state as its previous poll
- **THEN** it emits no finding update.

#### Scenario: Unknown external evidence

- **WHEN** a monitor cannot obtain complete reviewer or check state
- **THEN** status remains incomplete and names the failed evidence source.

#### Scenario: No-progress watch limit

- **WHEN** the operator explicitly selects the legacy 30-minute inactivity limit and no meaningful progress occurs for that interval
- **THEN** the watcher returns a pending/wait handoff within the absolute deadline without resetting the session budget; 30 minutes is no longer the implicit default.

#### Scenario: Absolute watch deadline

- **WHEN** the watcher runs without an explicitly supplied limit
- **THEN** it stops within one absolute 45-minute deadline from invocation, including collection and sleep, without resetting the deadline after meaningful progress
- **AND** timeout returns a pending/wait handoff, never a passing review or fabricated failure, and does not reset session budgets.

#### Scenario: Explicit watch controls and adjudication handoff

- **WHEN** the operator requests zero one-shot collection or a supported explicit legacy inactivity limit
- **THEN** that control remains available within the absolute deadline, with no implicit 30-minute default
- **AND** actionable feedback, evidence ready for adjudication or a terminal decision ends waiting without automatic review requests, retries or extensions.

#### Scenario: Review-thread state

- **WHEN** the watcher collects pull-request review feedback
- **THEN** it retrieves every page of GraphQL `reviewThreads` and their comments,
  including each thread's resolution and outdated state; a GraphQL failure leaves
  the session incomplete.

## ADDED Requirements

### Requirement: Native code completion is explicitly source-adjudicated

Existing reviewer evidence SHALL support independently adjudicated native code-review
completion when no normal REST submission exists. It SHALL bind the exact required
provider login, kind code, fetched comment identity/current digest, full commit SHA,
completion timestamp and current session binding. Native summaries SHALL retain their
source category; the helper SHALL NOT manufacture a REST review or infer completion
from silence, reactions, a parser guess or an unrelated security report. Normal current
REST reviews SHALL remain preferred and supported. Every existing negative reviewer,
requested-reviewer, check, thread, local-finding and report-coverage gate remains binding.
Old histories without this explicit evidence retain their existing obligations.
At recording, fetched source identity, author, digest and adjudicated head/time
association SHALL be retained as existing evidence provenance, validated during replay
without live network/monitor dependence and matched to current fetched receipts before
use. The full SHA association SHALL be explicit and unambiguous; literal full-SHA prose
is not required, and unrelated security metadata cannot establish that association.

#### Scenario: Correct native source supplies missing provider completion

- **GIVEN** a complete fetched native code-review source with the exact provider/full SHA and all other required current gates satisfied
- **WHEN** the independent reviewer adjudicates its source identity, content digest, kind and completion time in existing reviewer evidence
- **THEN** it can satisfy only that provider's completion obligation, distinctly from a REST review.

#### Scenario: Recorded native provenance replays and remains source-bound

- **GIVEN** native completion was recorded against a fetched source and explicit unambiguous full-head association
- **WHEN** historical events replay before restoring the current monitor snapshot
- **THEN** validation uses retained provenance without network access and preserves history
- **AND** current completion still requires matching current fetched source receipts; missing or edited sources invalidate use.

#### Scenario: Misbound or changed source remains incomplete

- **WHEN** author, full head, review kind, timestamp or digest is wrong/stale, source is absent, head is only an ambiguous abbreviation, or fetched content changes after adjudication
- **THEN** that native evidence cannot satisfy code-review completion and requires explicit fresh adjudication, without weakening negative gates.

#### Scenario: Positive native proof cannot waive an objection

- **GIVEN** adjudicated current native completion
- **WHEN** a required check is failed/pending/missing, a current review requests changes, a reviewer request remains pending, a thread/local finding is unresolved, or input/report coverage changes
- **THEN** completion remains blocked by that obligation despite positive provider proof.


#### Scenario: Native fallback respects an existing current-head REST result

- **GIVEN** bound native completion and acknowledged current report contents
- **WHEN** a normal current-head REST review exists for that provider
- **THEN** its ordinary state and freshness rules apply; PENDING or DISMISSED cannot be overridden by native completion
- **AND** absent REST remains eligible for explicitly adjudicated native fallback, while APPROVED/COMMENTED and negative-review rules remain unchanged.


#### Scenario: Closure coverage is causally valid for the named finding

- **GIVEN** a proposed named historical resolution and referenced passing closure evidence
- **WHEN** any named finding did not exist before that closure, or a later nonfixed disposition or explicit failing/incomplete reviewer evidence covering that same finding intervened before resolution
- **THEN** resolution rejects the stale causal claim until fresh closure follows the invalidation
- **AND** a reviewer may verify a known finding against the corrected current binding before its administrative fixed disposition; fixed-before-review also remains valid
- **AND** unrelated finding events do not invalidate coverage, while existing current-binding and genuine-fixed requirements remain mandatory.


#### Scenario: New report hands off while gates remain pending

- **GIVEN** a valid current snapshot with pending or missing CI and a new or changed unadjudicated report
- **WHEN** the watcher collects that snapshot
- **THEN** it hands off after that collection for independent adjudication while CI still blocks completion
- **AND** unchanged already-adjudicated incomplete reports and check-only progress do not repeatedly hand off; negative/error/budget precedence and the absolute deadline remain.
