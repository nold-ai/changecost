# Spec Delta

## Purpose

Provide a durable, evidence-bound review session so contributors can stop review
loops deliberately while retaining the context needed for a later decision.

## ADDED Requirements

### Requirement: Numeric aggregates preserve finite canonical totals

Active time, granted minute budgets and measured usage SHALL be summed canonically
from their original recorded components. Batch counts remain integers; unmeasured
usage remains unknown. Aggregation overflow or nonfinite totals SHALL reject atomic
updates and require recovery for malformed persisted history, never create infinite
allowance. No epsilon may add review allowance.

#### Scenario: Fractional grants exactly match measured activity
- **WHEN** fractional extensions and measured components sum to the same limit
- **THEN** genuine completion at that limit succeeds
- **AND** additional review activity replans at exhaustion, regardless of rounding direction.

#### Scenario: Finite components overflow their aggregate
- **WHEN** recorded components cannot produce a finite total
- **THEN** the write fails without changing the receipt and replay/status fail closed.

### Requirement: Observation epochs are captured before collection

Every positive observation SHALL carry an explicit collection-time input epoch.
Ingestion SHALL NOT fill missing metadata with the current generation. Missing,
null, malformed and stale epochs SHALL persist as incomplete observations,
replacing any earlier passing evidence. Error observations without epochs remain
storable incomplete evidence and SHALL NOT produce thread-adjudication receipts.

#### Scenario: An unbound old observation arrives after a same-head refresh
- **WHEN** a retained snapshot lacks its collection epoch
- **THEN** ingestion does not relabel it as current, including generation zero
- **AND** status and packets remain incomplete until explicitly bound fresh evidence arrives.

### Requirement: Completion exceptions cannot authorize further investigation

An otherwise complete session with a remaining family investigation SHALL replan
when either budget is exhausted. Exact-limit completion remains permitted only
when all evidence and family obligations are satisfied.

#### Scenario: Corrected recurrence exhausts a budget
- **WHEN** a genuine fixed or accepted-exception recurrence still needs investigation
- **AND** batches or active minutes reach their limit
- **THEN** status, packet and watcher return replan instead of investigate.

### Requirement: Resolved thread reports require explicit local adjudication coverage

Reviewer evidence SHALL explicitly acknowledge current remote thread reports by
stable thread IDs and semantic comment/content digests, bound to current inputs.
Resolved remote flags alone SHALL NOT establish adjudication. Local unresolved
findings SHALL still block independently. Missing coverage is incomplete evidence.

#### Scenario: A resolved report is new or changed
- **WHEN** a thread or paginated comment is added/edited after local review
- **THEN** prior reviewer evidence cannot establish completion until explicit updated coverage.

#### Scenario: An adjudicated thread is reopened
- **WHEN** the remote thread is unresolved, including outdated threads
- **THEN** it blocks completion regardless of local coverage
- **AND** reclosure without changed report content or inputs may reuse that adjudication.

### Requirement: Handoffs use a single receipt revision

Packet status and body SHALL derive from one loaded receipt while retaining the
actual-input drift check. Changed watcher output SHALL use that packet's status
for its exit decision and that packet's monitor observation for emitted evidence.

#### Scenario: Another writer changes the receipt during handoff
- **WHEN** scope or monitor data changes between potential reads
- **THEN** the emitted packet, associated observation and exit decision describe
  one revision rather than combining earlier success with later incomplete data.

### Requirement: Required event strings contain non-whitespace text

Required event identities and semantic strings, including extension approved_by,
SHALL reject nonstrings, empty and whitespace-only values, including Unicode
whitespace. Supplied supersedes references SHALL use the same validation. Nonblank
values SHALL retain exact bytes without trimming or creating aliases.

#### Scenario: Blank extension approval is submitted or recovered
- **WHEN** an extension has only whitespace in approved_by
- **THEN** recording rejects it without changing counters or revision
- **AND** malformed persisted history requires recovery rather than an allowance.

### Requirement: Helper identities cannot collide with caller events

Input epochs SHALL be generation-tagged values derived from the count of recorded
head-advance events, independently of caller IDs. Ordinary events, monitor revisions
and exact retries SHALL NOT advance the generation. Original event, finding and
scope identities SHALL remain unchanged. Incompatible persisted epochs require
explicit recovery rather than another allowance.

#### Scenario: Caller uses an internal-looking event identity
- **WHEN** caller events use genesis, bind-pr or generation-like IDs
- **THEN** refreshes still invalidate all prior input epochs and retain original IDs.

#### Scenario: Automatic PR binding encounters occupied IDs or concurrent writers
- **WHEN** candidate bind IDs are occupied or another writer binds the target
- **THEN** atomic selection uses a deterministic unused identity
- **AND** matching targets are idempotent while conflicting targets are rejected.

### Requirement: Outstanding reviewer requests invalidate completion

Every monitor snapshot SHALL include a validated array of requested users with exact
GitHub logins, retaining bot suffixes. Required reviewers who are requested again
SHALL remain pending despite earlier same-head results. The collector SHALL compare
normalized requested identities before and after collection; changes invalidate the
observation. Sorting, duplicate entries and incidental user metadata SHALL NOT create
semantic changes. Nonrequired requests are informational; no team expansion is implied.

#### Scenario: A reviewer is requested again after approval
- **GIVEN** a required reviewer's qualifying current-head result
- **WHEN** that exact user is requested again
- **THEN** completion remains pending until the request is absent
- **AND** cancellation restores only existing evidence that still satisfies all gates.

#### Scenario: Request metadata is incomplete or changes during collection
- **WHEN** requested users are missing, malformed, added or removed during collection
- **THEN** the observation is incomplete instead of retaining earlier green evidence.

### Requirement: Explicit comparison and target-base evidence binding

Initial and adopted base IDs SHALL identify commit objects exactly. Annotated-tag
object IDs SHALL be rejected without silently replacing caller-supplied identities.

Schema-6 contracts SHALL name an expected PR base ref/SHA independently from the
immutable comparison commit. Current comparison/base context SHALL be replayed
separately and exposed in packets. Explicit atomic adoption through advance_head
SHALL verify local commits and capture provenance without rewriting original scope,
history or counters. Adoption invalidates prior local and remote completion proof.

#### Scenario: Target base changes with an unchanged head
- **WHEN** the PR base ref/SHA differs from the approved tuple or changes during collection
- **THEN** monitoring is incomplete rather than reusing same-head completion

#### Scenario: Adopt a new comparison and target base explicitly
- **WHEN** an advance_head event supplies both comparison_base and pr_base
- **THEN** captured local commit facts and an adoption timestamp establish a new input epoch
- **AND** pure replay preserves the immutable original contract and counters

#### Scenario: Old evidence is not silently rebound
- **WHEN** local evidence omits or supplies a stale explicit head/input/epoch/comparison/PR-base binding
- **THEN** recording rejects it even under a new event ID
- **AND** after adoption required positive remote checks/statuses/reviews must have valid timestamps at or after adoption, while existing objections still block

### Requirement: Visible local terminal decisions and consistent commit identities

The watcher SHALL emit every terminal local decision even when remote evidence
is unchanged, and SHALL recheck local state at the no-progress deadline before
reporting wait. Contract initialization, input refresh and pure replay SHALL use
one full commit-ID validation rule supporting hexadecimal SHA-1 and SHA-256 IDs.

#### Scenario: Local transition while remote state is unchanged
- **WHEN** the receipt becomes complete, investigative, replanning or incomplete while remote evidence stays unchanged
- **THEN** watch emits the current terminal decision exactly once
- **AND** a budget exhausted during the final sleep is reported as replanning rather than wait

#### Scenario: Repository object format survives refresh and restart
- **WHEN** a real SHA-1 or SHA-256 repository advances its head
- **THEN** the full head ID is validated consistently through recording and replay while retaining scope/history/counters
- **AND** malformed IDs or mismatched actual heads are rejected

### Requirement: Usable initial scope and effective reviewer objections

Schema-6 initialization SHALL require typed, nonblank scope and exact identities,
full commit IDs and a safe path-to-SHA256 manifest using `<absent>` for planned
absent paths. It SHALL verify the initial base and actual manifest, including
changed/index/untracked paths, and preserve captured facts for filesystem-free
replay. Unchanged intended paths and future absent paths remain allowed. Existing
incompatible receipts require recovery without fabricated history or budget reset.

#### Scenario: Reject unusable contracts
- **WHEN** scope is mistyped/blank, a base is unknown, a path/hash is unsafe or inaccurate, or an existing changed path is omitted
- **THEN** initialization rejects the contract before persisting a session
- **AND** a valid initial contract remains immutable and retryable after later head refreshes

#### Scenario: Preserve an effective changes-requested objection
- **WHEN** a reviewer requests changes then submits COMMENTED, PENDING or a separate DISMISSED review
- **THEN** their objection remains blocking across pages for required and other reviewers
- **AND** a later APPROVED result clears it, or a complete fresh snapshot reflects dismissal of the original rejecting review itself

#### Scenario: Exact active-minute boundary with fractional increments
- **WHEN** 89 measured minutes are followed by ten measurements of 0.1 minute
- **THEN** canonical accumulation reaches exactly 90 minutes across restart, permits legitimate final completion, and requires replanning for more correction work

#### Scenario: Unsupported index flags cannot conceal inputs
- **WHEN** a tracked entry uses assume-unchanged or skip-worktree
- **THEN** initialization, input refresh and completion checks require recovery rather than accepting incomplete Git change/cleanliness evidence
- **AND** the helper preserves the user's index flags without changing them

### Requirement: Validate collection and event transaction boundaries
The helper SHALL bind observations to the input epoch captured before collection,
validate all consumed comment/thread fields and optional event references before
persisting them, and accept an identical successful retry even when its original
optimistic revision is now stale.

#### Scenario: Concurrent same-head input refresh
- **WHEN** an input refresh occurs during a monitor collection
- **THEN** that collection cannot be relabelled as evidence for the new epoch

#### Scenario: Malformed optional references or nested evidence
- **WHEN** a scope reference is not a nonempty identity or comment/thread evidence lacks required typed fields
- **THEN** event recording rejects the invalid update or monitoring persists incomplete evidence
- **AND** malformed values cannot poison subsequent status evaluation

#### Scenario: Unknown reviewer state cannot erase a rejection
- **WHEN** a required or other reviewer returns a state outside GitHub's documented review-state enum
- **THEN** the observation is incomplete, including after a prior changes-requested result
- **AND** documented PENDING states retain their existing pending behavior

#### Scenario: Retry after successful optimistic write
- **WHEN** the same event payload is retried with its original expected revision
- **THEN** the recorded result is returned without a second update
- **AND** new events or conflicting payloads still fail optimistic concurrency checks

### Requirement: Canonical review history and exact external identity

The helper SHALL replay validated events from durable genesis with separately captured
input/time facts, reconcile every derived persisted field, and bind observations to
the selected repository, pull request, head and exact reviewer login.

#### Scenario: Corrupted cached state
- **WHEN** any derived counter, scope decision, finding, phase, evidence, usage, timing or monitor summary contradicts its retained history
- **THEN** status requires recovery and does not accept cached completion

#### Scenario: State file lost after initialization
- **WHEN** a genesis marker remains but the state file is missing
- **THEN** initialization refuses a fresh allowance and requests recovery

#### Scenario: Dirty preflight cannot complete
- **WHEN** frozen local inputs contain unpublished staged, unstaged or untracked changes
- **THEN** review may proceed but completion requires clean inputs bound to the published head

#### Scenario: Exact monitor identity
- **WHEN** another repository or pull request shares the reviewed commit, or a bot login resembles a human login
- **THEN** its evidence cannot substitute for the selected source or exact required reviewer

#### Scenario: Genuine family chronology
- **WHEN** a report is explicitly dispositioned as a non-finding
- **THEN** it contributes neither a correction nor an escape
- **AND** a genuine fixed or accepted escape remains in history, with investigation escalation armed only after a genuine recurrence

#### Scenario: Bounded meaningful observation
- **WHEN** metadata-only responses vary or API pagination consumes the remaining wait budget
- **THEN** incidental metadata does not reset progress and requests/backoff respect the deadline
- **AND** malformed nested evidence or transport errors persist an incomplete observation rather than retaining prior green state

#### Scenario: Fresh session versus recovery
- **WHEN** a contributor starts a genuinely new session
- **THEN** the documented init operation creates its contract before status checks
- **AND** a missing historical receipt or a different worktree requires recovery without resetting history

### Requirement: Durable review session contract

The contributor workflow SHALL persist a versioned session contract containing
scope, acceptance criteria, non-goals, trust boundary, intended inputs and a
review budget and required GitHub reviewer logins before a review/fix session begins.

#### Scenario: Initialize a session

- **WHEN** a contributor initializes a session with a change identifier and scope contract
- **THEN** the workflow stores the contract with repository, base and head identities and defaults to three correction batches and 90 active minutes.

#### Scenario: Missing session record

- **WHEN** a workflow asks for session status and the record is missing or malformed
- **THEN** the result is incomplete and does not grant a fresh review budget.

### Requirement: Bounded correction decisions

The workflow SHALL treat a correction batch as one collected finding set followed
by correction and verification, independent of its number of commits.

#### Scenario: Exhausted budget

- **WHEN** the session reaches three correction batches or 90 active minutes
- **THEN** status requires replanning and identifies pending findings without reporting completion.

#### Scenario: Explicit extension

- **WHEN** a maintainer records a budget extension
- **THEN** status retains existing counters and applies only the recorded additional allowance.

#### Scenario: Corrected PR head

- **WHEN** a verified correction creates a new PR head
- **THEN** the session advances its reviewed head while preserving its existing
  budget counters, findings and event history.

### Requirement: Finding-family investigation

The workflow SHALL retain finding identities, evidence, family assignment and
disposition without automatically accepting a moved or repeated finding.

#### Scenario: First escape after correction

- **WHEN** a finding in a corrected family recurs
- **THEN** status requires an investigation of the family invariant, variants, callers and missing tests.

#### Scenario: Escape after investigation

- **WHEN** a finding in an investigated family recurs again
- **THEN** status requires replanning.

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

- **WHEN** the watcher observes no terminal external-review change for 30 minutes
- **THEN** it returns a `wait` handoff without resetting the session budget.

#### Scenario: Review-thread state

- **WHEN** the watcher collects pull-request review feedback
- **THEN** it retrieves every page of GraphQL `reviewThreads` and their comments,
  including each thread's resolution and outdated state; a GraphQL failure leaves
  the session incomplete.
### Requirement: Preserve lifecycle decisions through ingestion
The helper SHALL distinguish evidence categories from event kinds, reject conflicting event
identities and malformed nested state, and retain correction and investigation chronology.

#### Scenario: Distinguish missing timing from measured zero
- **WHEN** completion is requested without an explicit active-minutes measurement after the latest input refresh
- **THEN** completion is incomplete even when stored counters are zero
- **AND** a finite measured zero is accepted, while an event omitting minutes is rejected

#### Scenario: Respect the latest current-head reviewer state
- **WHEN** the latest review from any reviewer requests changes on the current head
- **THEN** completion is blocked even when no inline thread exists
- **AND** an older approval cannot satisfy a required reviewer whose latest state is pending or dismissed

#### Scenario: Parse complete paginated API documents
- **WHEN** the GitHub CLI returns pretty-printed paginated REST results
- **THEN** the helper requests a slurped page array and parses the complete JSON document
- **AND** failed API calls remain incomplete evidence

#### Scenario: Rebind changed review inputs
- **WHEN** an explicit head advancement refreshes input fingerprints, including staged blobs and modes
- **THEN** earlier passing evidence is invalidated even if the commit SHA is unchanged

#### Scenario: Require declared external gates
- **WHEN** a complete snapshot omits a check or status identity declared in the contract
- **THEN** completion remains pending
- **AND** the contract explicitly names expected checks and statuses, including an explicit empty status list

#### Scenario: Reject malformed finding dispositions
- **WHEN** persisted finding dispositions contain an unknown value or contradict recorded disposition events
- **THEN** state recovery is required rather than accepting completion

#### Scenario: Complete the final permitted correction
- **WHEN** the final batch has current passing gate and reviewer evidence and a complete current-head monitor snapshot
- **THEN** completion is allowed, but pending, failed, missing or unresolved external evidence prevents completion
- **AND** an exhausted budget takes precedence over waiting

#### Scenario: Resolve a scope decision explicitly
- **WHEN** a pending scope decision is superseded by an authorized decision naming its identity
- **THEN** only that pending decision is cleared

#### Scenario: Retain a corrected escape
- **WHEN** a family escapes after correction and investigation, even if an earlier escape was fixed
- **THEN** the session requires replanning
- **AND** multiple findings collected before any correction do not constitute an escape

#### Scenario: Collect bounded complete GitHub evidence
- **WHEN** GitHub supplies lowercase check conclusions, commit statuses, or outdated unresolved threads
- **THEN** each source contributes to the completion decision
- **AND** subprocess timeouts and invalid pagination cursors produce incomplete evidence

### Requirement: Numeric validation preserves integer semantics
Integer-only counters and identities SHALL be validated exactly without conversion
to floating point. Negative values and booleans SHALL remain invalid. Measurements
requiring floating-point representation SHALL reject conversion overflow as a
controlled validation error, before persistence.

#### Scenario: Oversized JSON measurement
- **WHEN** an event contains an integer too large for a floating measurement
- **THEN** recording SHALL reject it atomically and corrupted persisted history
  SHALL return incomplete recovery rather than an uncaught exception.

#### Scenario: Large exact integer counter
- **WHEN** an approved extension supplies a nonnegative integer batch count
- **THEN** recording and replay SHALL preserve the exact integer without imposing
  an incidental floating-point range limit.

### Requirement: Refresh preserves explicitly authorized scope
Every head refresh SHALL capture current fingerprints and complete changed,
staged, untracked, deleted and renamed path coverage against its effective
comparison base. The current reviewed manifest SHALL be exposed separately from
the immutable initial contract. An ordinary refresh SHALL preserve authorized keys.

#### Scenario: Undeclared correction path
- **WHEN** a refresh contains a changed path outside the authorized manifest
- **THEN** it SHALL reject atomically until an explicitly referenced prior approved
  scope decision supplies a complete validated intended-file manifest.

#### Scenario: Explicit scope reconciliation
- **WHEN** an advance references an approved scope decision's intended manifest
- **THEN** its exact keyset SHALL authorize the transition while fingerprints are
  recaptured from current inputs; planned-absent files may materialize and approved
  file contents may change, but fresh evidence remains required.
- **AND** pending, rejected, deferred, missing and unrelated decisions SHALL not
  authorize new paths; approval SHALL never be adopted implicitly.

#### Scenario: Replay and concurrent changes
- **WHEN** a receipt is replayed or inputs change during scope capture
- **THEN** replay SHALL validate captured scope facts without filesystem access and
  concurrent changes SHALL reject before persistence. Older receipts without these
  required facts SHALL require recovery without resetting counters.
