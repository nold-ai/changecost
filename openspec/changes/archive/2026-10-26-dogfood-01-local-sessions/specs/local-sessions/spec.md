## ADDED Requirements

### Requirement: Frozen chronological session forecasts
The system SHALL store immutable forecasts in total_tokens for an exact task-kind/context cohort using only previously committed latest declared-session-total measurements. Forecasts SHALL freeze guess, source, amount, algorithm version, sample count/range, outcomes and contributing session/revision/token values. Failed and abandoned measured totals SHALL participate. An empty cohort SHALL use a supplied integer guess or remain unknown.

#### Scenario: Learning can improve and worsen
- **GIVEN** a fresh cohort and a first guess of 100
- **WHEN** measured session totals are 200, 200, and 1000 in successive sessions
- **THEN** frozen forecasts are 100, 200, and 200, with absolute errors 100, 0, and 800 tokens
- **AND** the next median is 200 with three samples

#### Scenario: Pending and other cohorts do not train
- **GIVEN** pending sessions and measured sessions with a different exact task kind or context
- **WHEN** a new session starts
- **THEN** those sessions contribute no inputs to its forecast

#### Scenario: Idempotent start preserves history
- **GIVEN** a started session and later measurements
- **WHEN** identical start inputs are retried
- **THEN** the original forecast is returned unchanged
- **AND** conflicting reuse of the ID rejects without writes

### Requirement: Explicit append-only measurements
The system SHALL validate bounded nonblank labels and nonnegative integer token quantities within SQLite's signed integer range. Finish SHALL append the first revision. Correction SHALL append a revision with a nonblank reason and expected prior revision. Identical retries SHALL return the operation's existing revision and conflicting or stale operations SHALL reject atomically. Old measurements and forecasts SHALL remain inspectable across process restarts.

#### Scenario: Corrections affect only future learning
- **GIVEN** session A measured 200 and session B froze A revision 1
- **WHEN** A is explicitly corrected to 300 using expected revision 1
- **THEN** B retains the 200 input and later session C uses A revision 2 at 300
- **AND** both A measurement revisions remain visible

#### Scenario: Retry and stale correction
- **GIVEN** a correction from revision 1 to revision 2
- **WHEN** the same predecessor and payload are retried
- **THEN** revision 2 is returned without a new append
- **AND** a different payload with predecessor 1 rejects

### Requirement: Honest evaluation and local storage
Every report SHALL disclose manual, provisional, uncalibrated status, frozen forecasts, latest actuals, revision history and exclusions. Numeric total forecasts SHALL receive signed forecast-minus-actual and absolute token errors only for declared totals. Percentages SHALL be unavailable at actual zero. Cumulative MAE SHALL disclose exact numerator/denominator, included count and exclusions. Partial measurements SHALL remain visible but be excluded from learning and full-total evaluation.

#### Scenario: Partial, unknown and zero actual
- **GIVEN** partial, pending, unknown-forecast and zero-actual sessions
- **WHEN** history is displayed
- **THEN** partial, pending and unknown-forecast cases have explicit evaluation exclusion reasons
- **AND** the zero actual has token error and no percentage
- **AND** aggregate MAE counts only eligible total comparisons

#### Scenario: Safe isolated persistence
- **GIVEN** a missing session database or an unfamiliar existing SQLite file
- **WHEN** help, invalid input, read of missing storage, or start against the unfamiliar file is invoked
- **THEN** no core store or missing session store is created by help, invalid input or reads
- **AND** the unfamiliar file rejects without content changes or raw SQL/path disclosure

#### Scenario: Reopened concurrent commands
- **GIVEN** separate processes using one local session database
- **WHEN** starts and measurements commit
- **THEN** forecasts contain only already committed measurements and retries create no duplicate revisions

#### Scenario: Interrupted first creation is retryable
- **GIVEN** no session database exists
- **WHEN** initialization fails or the process stops before publication
- **THEN** the final path remains absent and a normal start retry succeeds
- **AND** normal exceptions clean up private preparation files

#### Scenario: Concurrent first creation preserves the winner
- **GIVEN** two starts begin before the first session database is published
- **WHEN** both commands initialize storage and commit their sessions
- **THEN** both sessions persist in one recognized database without an unfamiliar-file error
- **AND** a foreign file appearing before publication is preserved and rejected without adoption
