# bounded-review-session Specification

## Purpose
Provide a durable, evidence-bound review session so contributors can stop review
loops deliberately while retaining the context needed for a later decision.

## Requirements

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

Schema-8 contracts SHALL name an expected PR base ref/SHA independently from the
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

Schema-8 initialization SHALL require typed, nonblank scope and exact identities,
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

### Requirement: Every declared path participates in input binding
Input capture SHALL require the current authorized keyset and bind each declared
path's fingerprint or explicit absence even when Git ignores it. Existing declared
content outside the index SHALL prevent clean published completion; planned absent
paths and tracked paths matching ignore patterns SHALL remain supported. Unrelated
ignored artifacts SHALL remain outside the declared-input binding.

#### Scenario: Ignored declared content changes
- **WHEN** an ignored declared file is created, edited or deleted after capture
- **THEN** status SHALL invalidate previous evidence and consistency reads during
  initialization or refresh SHALL detect such concurrent changes.

#### Scenario: Scope approval adds ignored intent
- **WHEN** an advance explicitly selects an approved manifest with an ignored path
- **THEN** both consistency reads SHALL use the selected new keyset and preserve
  explicit absence/content identity; prior receipts require recovery without reset.

### Requirement: Initial context requires fresh remote positives
The validated genesis creation timestamp SHALL establish the initial remote
freshness floor. Required positive checks, statuses and reviews SHALL be at or
after that floor; prior results cannot attest their original base context.
Ordinary refreshes and retries SHALL retain the floor, while explicit base adoption
SHALL update it. This conservative rule may require repeating valid same-base work.

#### Scenario: Old same-head evidence at initialization
- **WHEN** an initial session observes old, missing or invalid positive timestamps
- **THEN** it SHALL remain pending even if the PR head/base envelope matches.
- **AND** old objections and failed/pending evidence SHALL continue to block rather
  than being removed by the positive freshness filter.

### Requirement: Local adjudication covers every fetched report
Passing local reviewer evidence SHALL explicitly cover the exact current receipt
set for review threads, top-level reviews and general PR comments across all pages,
including historical and informational content. Typed namespaced identities SHALL
prevent cross-source collisions. Missing or malformed report identities/bodies and
duplicate identities SHALL invalidate monitoring, never silently omit a report.

#### Scenario: Non-thread report changes
- **WHEN** a review body or PR comment is added, edited or removed
- **THEN** prior local coverage SHALL no longer satisfy completion until explicit
  revalidation covers the current content; unchanged content may reuse coverage.

#### Scenario: Harmless metadata changes
- **WHEN** ordering, avatars, reactions, transport timestamps or lifecycle flags
  change without report-content changes
- **THEN** content receipts SHALL remain stable while objections, unresolved status,
  freshness and input requirements remain independent blockers.

### Requirement: Required checks provide positive success
Every completed check whose name is declared in required_checks SHALL conclude
success. Neutral is not evidence that a required validation executed successfully.
Optional neutral checks SHALL retain their existing nonblocking behavior; other
failure and pending states remain unchanged. This is the repository's assurance
policy, not a claim about GitHub's native merge rules.

#### Scenario: Required neutral conclusion
- **WHEN** a required check concludes neutral, including alongside another
  same-name successful result on a different page
- **THEN** completion SHALL remain blocked without silently selecting the success.

#### Scenario: Optional neutral conclusion
- **WHEN** all required checks succeed and an optional check concludes neutral
- **THEN** that optional neutral result SHALL not independently block completion.

### Requirement: Collection verifies bounded cross-surface consistency
Each observation SHALL collect all paginated check, status, review, PR-comment and
thread/comment surfaces twice under one existing deadline. Both passes SHALL retain
initial/final PR metadata checks. Only matching meaningful projections SHALL be
accepted, returning the second observation; drift, malformed data or second-pass
failure SHALL replace prior green evidence with incomplete monitoring.

#### Scenario: Report or gate changes during collection
- **WHEN** meaningful content, lifecycle state, freshness timestamps or PR identity
  differs between the two complete passes
- **THEN** the observation SHALL be rejected without a stabilization retry loop.

#### Scenario: Stable observations and limitations
- **WHEN** both passes agree apart from excluded transport metadata or page grouping
- **THEN** the second observation MAY be accepted with existing reviewer chronology.
- **AND** sequential APIs SHALL NOT be described as atomic or as detecting unobserved
  changes that revert between reads or occur after the final observation.

### Requirement: Efficient canonical Git input acquisition

Contributor review-input capture SHALL acquire index flags, tracked stage records
and visible untracked inventory with one Git invocation. It SHALL preserve the
existing schema-8 canonical index bytes, inventory, input digest and clean-state
semantics. This developer-gate repair SHALL NOT change product runtime contracts,
receipt schemas, required analyzers, test selection or enforcement deadlines.

#### Scenario: Historical fingerprint parity

- **GIVEN** unchanged repository contents and declared inputs, including staged/working divergence, executable modes, intent-to-add or conflicting index stages
- **WHEN** the combined inventory is normalized and the input binding is captured
- **THEN** its ordered index bytes, inventory, digest and clean state equal the historical separate-probe capture.

#### Scenario: Untracked names cannot become index metadata

- **GIVEN** visible untracked filenames containing tabs, newlines or stage-looking text, and declared ignored or absent paths
- **WHEN** input acquisition parses Git's NUL-delimited tagged records
- **THEN** untracked tags determine the record category before filename parsing, and all existing inventory and declared-input semantics remain intact.

#### Scenario: Hidden flags remain globally rejected

- **GIVEN** an assume-unchanged or skip-worktree flag on any index entry, including an undeclared path
- **WHEN** review inputs are captured
- **THEN** capture rejects the unsupported flag without silently restoring or changing the user's index.

#### Scenario: Freshness and race guards remain active

- **GIVEN** inputs changing during initialization or refresh, a mismatched HEAD, or dirty declared contents
- **WHEN** the optimized acquisition participates in normal capture
- **THEN** independent HEAD/status checks, all declared fingerprints and both captures during initialization/refresh remain active and reject inconsistent evidence.

#### Scenario: Acquisition stays bounded without weaker assurance

- **GIVEN** a valid stable repository requiring one capture
- **WHEN** capture invokes Git
- **THEN** one combined index/inventory query replaces the three prior queries while HEAD and status verification remain separate, and full current-head native assurance remains required.

### Requirement: Explicit retirement preserves a merged stage's review history

An `advance_head` event MAY retire the currently bound PR only through an explicitly
selected prior approved scope decision. The decision SHALL name a nonblank approver,
the complete intended-file manifest, the exact old repository, PR, head and merge
commit, and the same adopted main commit for comparison and target context.
Recording SHALL fetch stable complete old-source lifecycle and report facts through
the existing bounded GitHub collection boundary. The source SHALL be closed and
literally merged with a valid nonfuture merge timestamp, matching expected identities
and the same repository's main destination. The merge commit SHALL exist locally and
be an ancestor of both adopted main and current HEAD. A historical squash source head
need not be an ancestor of HEAD. Open, unmerged, malformed, mismatched, unavailable or
changing source evidence SHALL reject before persistence. Effective objections,
unresolved threads, required reviewer requests, failed/pending/missing gates and local
unresolved findings SHALL prevent retirement. Old positive freshness is not a
retirement prerequisite and retirement SHALL grant no completion.

#### Scenario: The merged preparation stage precedes the runtime PR
- **GIVEN** a bound merged PR with a historical head distinct from current HEAD and an explicit matching scope approval
- **WHEN** retirement captures complete stable source proof and valid local ancestry
- **THEN** one atomic refresh clears the active PR and monitor, advances the input epoch and freshness floor, and recaptures the authorized inputs
- **AND** genesis, contract, events, provenance, findings, family history, measurements, usage and budget totals remain preserved.

#### Scenario: Source proof or authorization is invalid
- **WHEN** exact source/destination approval, closed merged lifecycle, complete reports, ancestry or stable local inputs cannot be established, or a blocking finding remains
- **THEN** retirement rejects with the persisted receipt unchanged, without another allowance or session.

#### Scenario: Replay and retry preserve causal facts
- **WHEN** a retired receipt is replayed offline or an exact event is retried
- **THEN** replay validates retained lifecycle, report, approval and ancestry facts without Git or network access, and retry does not append or recapture
- **AND** missing or contradictory facts fail closed; existing schema-8 receipts continue to load and older code rejects the new provenance.

#### Scenario: Retired sources cannot return through delayed observations
- **WHEN** an explicit bind or delayed snapshot attempts to bind a retired repository and PR
- **THEN** binding rejects using canonical retirement history, without changing the receipt
- **AND** a different runtime PR binds normally with collision-safe identities.

#### Scenario: Recovery cannot reuse positive evidence
- **WHEN** the new runtime PR is bound after retirement
- **THEN** prior local, native-provider, remote and timing proof cannot certify it; current report coverage, post-retirement positives, clean inputs, family obligations and existing budgets still govern completion.

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

### Requirement: Critical safety assumptions receive early observable proof

Before dependent implementation of a nontrivial behavior change, the contributor workflow SHALL select one or two existing-system safety assumptions most likely to invalidate the chosen approach. It SHALL identify affected obligations, observable checks, expected results, actual evidence and exclusions in existing planning/evidence artifacts. Proof SHALL exercise the relevant existing CLI, API or dependency boundary with the smallest sufficient safe probe. A disproved or unverified critical assumption SHALL prevent the dependent decision being represented as safe; unaffected authorized work may continue. Expected failing tests for newly proposed behavior SHALL remain separate from failures of existing safety assumptions. Documentation-only scope SHALL retain an applicability rationale rather than inventing runtime probes.

#### Scenario: Routine bounded behavior change
- **GIVEN** a narrow change with a known caller and unchanged trust boundary
- **WHEN** preparation selects its critical safety assumption
- **THEN** the workflow records a relevant observed boundary check and its limits for the existing upfront independent review
- **AND** no additional reviewer or competing implementation is required solely by this checkpoint.

#### Scenario: Existing assumption is disproved
- **GIVEN** an approach that depends on an existing interface preserving a named invariant
- **WHEN** the probe contradicts that invariant
- **THEN** the dependent approach is revised or explicitly replanned before implementation
- **AND** the contrary evidence remains recorded rather than being described as passing proof.

#### Scenario: Probe cannot run on the available controller
- **WHEN** a selected critical check is unavailable or inconclusive
- **THEN** the workflow names the missing evidence and supported next check without marking the assumption proven
- **AND** a successful proxy command or configuration read cannot substitute for execution evidence.

#### Scenario: Expected new-behavior failure and documentation applicability
- **WHEN** a spec-derived test fails because proposed behavior is not implemented
- **THEN** it remains valid TDD evidence rather than a disproved existing-system assumption
- **AND** documentation-only changes record why a runtime safety probe does not apply.

### Requirement: Existing review slots consume a compact execution checkpoint

The workflow SHALL place the selected assumptions, proof references, affected obligations and exclusions in the existing upfront independent review. Its execution checkpoint SHALL identify blocking work, the sole writer and any independent read-only work that can proceed safely. Follow-up handoffs SHALL contain the current comparison/head/input binding, actual delta, affected assumptions, unresolved findings and necessary evidence references. Unknown dependencies or changed scope, entrypoints or trust boundaries SHALL require the existing broader review path. This checkpoint SHALL NOT create another review lane, mandatory design competition, receipt schema or authoritative ledger.

#### Scenario: Mapped correction has a stable baseline
- **GIVEN** a reviewed same-change baseline and a correction confined to covered dependencies
- **WHEN** the next review starts
- **THEN** its handoff contains the affected delta and assumptions with current evidence
- **AND** required final gate and provider coverage remains unchanged.

#### Scenario: Correction introduces an unknown boundary
- **WHEN** a correction adds an entrypoint or unmapped dependency
- **THEN** the coordinator renews the affected scope/obligation review before claiming narrow closure
- **AND** earlier unrelated findings and budget history are preserved.

### Requirement: Finding triage distinguishes defects from preferences using evidence

Each actionable finding SHALL identify the violated accepted obligation, reachable failure path and supporting reproduction, regression or inspected-path evidence. The coordinator SHALL deduplicate reports without erasing distinct defects or their source identities. Preferences and speculative concerns SHALL receive reasoned dispositions; credible but unverified defects SHALL remain unresolved pending evidence. Confirmed defects SHALL remain blocking until verified fixed or explicitly dispositioned under existing exception policy. Reviewer agreement, disagreement, severity labels or implementation inconvenience SHALL NOT alone establish or dismiss a defect. Existing authoritative finding dispositions SHALL remain unchanged.

#### Scenario: Confirmed defect is reported by one reviewer
- **WHEN** one reviewer demonstrates a reachable violation of an accepted requirement
- **THEN** the finding remains actionable regardless of another reviewer's silence or disagreement.

#### Scenario: Preference has no demonstrated violation
- **WHEN** a report proposes an alternative style or abstraction without a violated obligation or concrete failure
- **THEN** the coordinator records its rationale and nonblocking preference disposition without changing code solely to quiet the reviewer.

#### Scenario: Credible evidence remains incomplete
- **WHEN** a security, persistence or assurance concern cannot yet be verified or disproved
- **THEN** the concern remains unresolved and its smallest evidence-gathering step is named
- **AND** lack of a runnable reproduction alone does not dismiss it.

### Requirement: Risk-first execution preserves all existing completion controls

The contributor workflow SHALL preserve its mechanical gates, supported-Linux/Python assurance, independent upfront review, affected-scope closure, Codex default and risk-triggered CodeRabbit. Critical-assumption proof and compact handoffs SHALL supplement those controls rather than certify completion. One writer SHALL collect compatible confirmed fixes into the existing correction batches; batches, measured review time and family investigation/replanning history SHALL NOT reset. Required stale, missing, failed or unavailable evidence SHALL remain incomplete.

#### Scenario: Assurance or persistence scope requires both providers
- **WHEN** scope changes security/trust boundaries, persistence/data-loss behavior or assurance/gate policy, or contains contradictory evidence
- **THEN** both Codex and CodeRabbit remain required by the existing risk policy
- **AND** an early proof cannot waive their current-head completion or mandatory checks.

#### Scenario: Budget or current-input evidence is exhausted
- **WHEN** review allowance is exhausted or evaluated inputs change
- **THEN** existing replan/recovery and evidence-invalidation rules apply
- **AND** a compact checkpoint does not grant another allowance or relabel old evidence as current.
