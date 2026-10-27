# Bounded review session recovery delta

## ADDED Requirements

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
