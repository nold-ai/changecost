## Why

Run a first local manual coding-session loop now. A user enters a cohort and optional guess before work, records a measured total afterward, and sees frozen estimate versus actual and later cohort medians.

## What Changes

Add a separate local SQLite session owner and `session start`, `finish`, `correct`, `show`, and `history` commands. Add an isolated deterministic walkthrough using the actual CLI. All results remain manual, provisional and uncalibrated.

## Capabilities

### New Capabilities
- `local-sessions`: immutable chronological forecasts, append-only measurement corrections and disclosed total-token errors.

### Modified Capabilities
None. Existing demand, core Store, source approvals and economic contracts stay unchanged.

## Impact

Touch the session module, CLI wiring, focused tests, quickstart, session guide and generated command/index references. Independent review and aggregate assurance remain separate pending work. SQLite persistence and correction retries are principal risks. Rollback removes commands while preserving the separate database.

## Non-goals

No native collection, provider reader changes, billing, automatic import, calibration claim, release, merge or deployment.
