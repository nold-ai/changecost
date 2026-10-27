## Context

The maintainer authorized this local manual dogfood on 2026-10-25 Europe/Berlin. Existing full-Change demand only admits synthetic truth. A manual session must not broaden that policy.

## Decisions

Use independently reviewed candidate A with candidate C's `show ID` and filtered `history` journey. One `sessions.py` owns domain validation, SQLite transactions, frozen forecast JSON, revisions and reporting. Reuse exact `demand_history.summaries` arithmetic and existing `cli.execute` presentation. No service/repository layering or new gate machinery.

A session has exact task-kind/context labels and fixed total_tokens units. Start freezes the original guess, algorithm version, source, median/range/count, outcome counts and exact contributing session/revision/token inputs in a BEGIN IMMEDIATE transaction. A monotonic database event sequence orders starts and measurements. Learning uses only the latest committed declared-session-total revision per earlier finalized matching session. Failed and abandoned totals participate. Partial records do not train or receive full-total errors.

Finish appends the first measurement. Correction requires its expected predecessor and a nonblank reason. An identical operation retry returns its original revision; conflicting/stale payloads reject. Reports use current measurements while old forecasts retain original inputs. Error is forecast minus actual. Exact signed and absolute tokens use finite decimal strings. Percentage and MAE ratios include exact numerator/denominator and a six-place half-even decimal, avoiding nonterminating-decimal rejection. No percentage at actual zero.

A dedicated database identity/schema is checked before writes. Unfamiliar/core files reject without mutation. Help, invalid input and reads of missing databases create neither store. First use initializes and commits a private sibling SQLite database before publishing it atomically without replacing an existing file. A competing creator opens and recognizes the published winner. Interrupted preparation leaves the final path absent, so a retry can create it. SQLite transactions serialize operations on the published database. The default is `.changecost/sessions.sqlite3`; `session --session-db PATH` selects another file.

## Risk-first checkpoint

Static tracing confirmed pure summary arithmetic and lazy core Store construction at baseline de2c42b. Focused CLI tests prove actual missing-command red, safe reads and separate storage. The runnable demo proves errors 100, 0 and 800 tokens, then a median of 200 after the outlier. Tests also cover revisions and partial exclusion. Source approval and calibrated accuracy are outside this evidence.

## Tradeoffs and limits

Separate SQLite costs one local file but avoids core migrations and false full-Change authority. Manual totals and user cohort labels can be wrong. One local filesystem is supported; no shared-network database or merge feature. Back up the closed database. Rollback retains the file and removes command wiring.
