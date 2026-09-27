# Quality gates and review

## Current planning gates

Run `make check` from the repo root. It invokes the pinned pre-commit hygiene
checks and `openspec validate --all --strict --no-interactive`.
GitHub Actions runs the same target on pull requests and pushes to `main`.
No source tests or product-security checks are claimed by this scaffold.

Check Markdown relative links after documentation edits. Keep the original
research export immutable; it is excluded from whitespace normalization.
Check generated files and credentials before staging, even when ignore rules exist.

## Before the first product implementation

Implement the approved Python foundation: `pyproject.toml`, committed `uv.lock`,
uv-managed environments, Hatchling builds, pytest, Ruff and BasedPyright. Add runnable
commands and matching CI gates. The foundation proposal defines the smoke tests. Review dependency licenses and security
advisories. Test numerical units, rounding, missing usage, retries, and deduplication
when relevant to the approved behavior. Do not add empty tests to claim coverage.

## SpecFact review readiness

SpecFact is contributor tooling only. This command surface was checked against
installed SpecFact CLI 0.55.4 on 2026-09-27 (Europe/Berlin):

```sh
specfact module install nold-ai/specfact-code-review
specfact code review run --help
mkdir -p .specfact
specfact code review run --scope full --enforcement full --json --out .specfact/code-review.json
```

Install the review module only if missing. Record the CLI and module version used.
During iteration `--scope changed` can narrow analysis; final review must cover
the changed behavior and required dependencies. Inspect the report's actual scope
and analyzer availability rather than relying on its filename or exit code alone.

The pre-commit configuration includes a **manual** hook for Python source paths:

```sh
pre-commit run specfact-code-review --hook-stage manual --all-files
```

Python is selected, but no source exists yet. Activate and verify review coverage
when the foundation is implemented. A hook with no matching source files is skipped,
not passed.

Portable dependency-sensitive review may require a supported Linux runtime.
The inspected SpecFact documentation describes automatic capsule preparation for
Linux x86-64 / CPython 3.11–3.13, not macOS or Windows. Verify the installed module's
current support; do not invent a runtime descriptor before the supported review environment has been verified.

For behavior changes, retain fresh `.specfact/code-review.json` locally, and record
the command, versions, reviewed commit/diff, timestamp, and result in
`TDD_EVIDENCE.md` or the PR. Regenerate after substantive source, test, config,
workflow, or spec edits. Do not commit machine-specific reports or private data.

Resolve findings at every severity, including naming, KISS, YAGNI, DRY, and SOLID
issues, or document a narrow justified exception. An unknown/skipped analyzer or
absent tool must be addressed before claiming the behavior gate is complete.
Code review supplements tests and independent security analysis.
