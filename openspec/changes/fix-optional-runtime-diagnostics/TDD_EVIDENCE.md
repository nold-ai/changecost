# Scoped CI repair evidence

The maintainer authorized this correction in PR #50 on 2026-10-27. Original head
`427cf69c74caaa16ae4d04bda6331365bbd6e06d` and comparison base
`c424eb8ac67b51af087dbe71a1516a24281c90a1` were freshly confirmed.

Both jobs in [run 40591992208](https://github.com/nold-ai/changecost/actions/runs/40591992208)
passed the repository check (3,583 tests and 17 strict OpenSpec items) but failed
the unconditional diagnostic with no native report. Native review was explicitly
inapplicable to that documentation-only diff. The required review gate already
rejects a missing fresh report for behavior-affecting inputs.

The independent upfront review confirmed the guard and four-case regression
design. Failing/passing commands and exact-content closure are recorded below
as executed. Native/provider acceptance remains pending. No product runtime,
private evidence, source approval or billing authority is changed.

## Local red and green, 2026-10-27 Europe/Berlin

Command: `.venv/bin/python -m pytest tests/test_repository_gates.py
tests/test_runtime_diagnostics.py -k 'runtime_diagnostic_workflow_requires_present_report
or absent_native_report_respects_review_applicability or
present_report_cli_retains_validation' -q`.

Before the workflow edit: one failed, four passed. The regression reported actual
`always()` against required `always() && hashFiles('.specfact/code-review.json') != ''`.
The other cases established docs-only absence, required missing-report rejection,
and malformed/valid present-report CLI behavior. After the one-line edit: five
passed. Ruff lint and format checks passed for both affected test files.

Logs remain in ignored
`.changecost/workflow/provider-04-claude-local-import/promotion-ci-fix-20261027/`.
This is local synthetic behavior and workflow-wiring proof, not execution of the
GitHub expression engine or supported native analyzers. Full Linux assurance and
provider acceptance remain pending at candidate publication; the live PR receipt
and existing review ledger carry later current-head results.

## Candidate verification

All twelve applicable local leaves passed against the explicit main comparison
base and intended-file manifest: hygiene, lock, lint, types, docs, index, metadata,
workflow, tests, build, audit and spec. The full suite passed 3,588 tests; strict
OpenSpec validation passed all 18 items. Dependency audit was explicitly
inapplicable because locked dependency inputs did not change. The first hygiene
attempt encountered sandbox write restrictions on unchanged skill paths; its
authorized rerun passed without source changes.

Independent defect and documentation reviewers inspected the frozen 20-path
manifest and found no introduced defects. The defect reviewer explicitly closed
the missing optional diagnostic finding. Product/source approval files, Claude's
ten unchecked implementation tasks and live evaluation #17 remain unchanged.
Supported Linux native execution is deliberately pending through the documented
macOS publication route. This local result does not replace `make check` in CI.
