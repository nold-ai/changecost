# Optional diagnostic collection

The native report is either absent or present. Presence selects diagnostic
collection; the collector remains responsible for validating present content.
The existing required review gate independently rejects missing native evidence.

Use GitHub Actions `always()` with a report-presence condition so failed native
reviews still yield diagnostics when a report exists. Leave unconditional evidence
upload and the mandatory repository check unchanged. No new dispatcher or
expression evaluator is needed.

The risk is accidentally hiding required evidence failures. Exercise the real
review dispatcher with a native process that emits no report, and preserve its
non-success result. Exercise malformed and valid present reports through the
collector CLI. A workflow assertion plus actionlint checks the wiring; hosted
matrix results establish actual native execution, separately from the synthetic
docs-only applicability regression.

On this macOS controller, follow the existing gate guide's supported route:
applicable local leaves and staged checks, independent closure, then a reviewed
feature push for Ubuntu assurance. No unsupported local native pass is claimed.
Keep all live acceptance pending until current-head checks and providers pass.
