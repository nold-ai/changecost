# Spec Delta

## Purpose

Provide a durable, evidence-bound review session so contributors can stop review
loops deliberately while retaining the context needed for a later decision.

## ADDED Requirements

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
