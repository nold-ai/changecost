# Provisional Codex session learning

## Why
The user needs to start with an estimate, explicitly capture a new local Codex file after work without typing token totals, inspect provisional error, and use one latest source counter per comparable attempt in future forecasts. The finite diagnostic reader cannot admit these new bytes or read the observed 34 MiB source.

## What changes
Add `session start --source codex`, `capture-codex`, and `history --source codex`. Map the pinned observed producer family to its latest cumulative total_token_usage.total_tokens. Keep unknown coverage, completeness, finality, subagent inclusion, and unauthenticated producer claims explicit. Store immutable capture revisions in additive schema v3 tables, globally deduplicate the provider identity, freeze forecast inputs, and render concise human output. Manual commands/defaults and exact finite admission remain intact.

## Capabilities
### New capabilities
- `codex-provisional-sessions`: explicit local source counter capture, revisions, provisional learning and error reporting.
### Modified capabilities
None. Core financial and admitted diagnostic contracts remain unchanged.

## Impact
Changes affect the separate session store, CLI, presentation, new bounded reader, focused tests, and session documentation. No external service or payment is involved. The reader streams one explicitly selected regular file under 128 MiB and 100,000 rows. A source can omit work, hide resets or exclude subagents, so reported counters do not establish complete actual usage. Back up the local SQLite file before v3. Rollback restores that backup and loses later writes unless the upgraded file is retained separately. Old binaries reject v3.

## Non-goals
No canonical approval, core numeric/billing/calibration authority, full-Change demand, automatic discovery, daemon, LLM invocation, upload, merge, or release. Aggregate Linux/provider/PR acceptance stays pending.
