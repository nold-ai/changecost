# Quality gates and review

## Current planning gates

Run `make check` from the repo root. It invokes the pinned pre-commit hygiene
checks and `openspec validate --all --strict --no-interactive`.
GitHub Actions runs the same target on pull requests and pushes to `main`.
No source tests or product-security checks are claimed by this scaffold.
Documentation ownership, changelog/version and `llms.txt` consistency are currently
review responsibilities, not automated gates. Agent instructions do not enforce them.

Check Markdown relative links after documentation edits. Keep the original
research export immutable; it is excluded from whitespace normalization.
Check generated files and credentials before staging, even when ignore rules exist.

## Before the first product implementation

Implement the approved Python foundation: `pyproject.toml`, committed `uv.lock`,
uv-managed environments, Hatchling builds, pytest, Ruff and BasedPyright. Add runnable
commands and matching CI gates. The foundation proposal defines the smoke tests. Review dependency licenses and security
advisories. Test numerical units, rounding, missing usage, retries, and deduplication
when relevant to the approved behavior. Do not add empty tests to claim coverage.

The [foundation design](../../openspec/changes/core-01-python-foundation/design.md#repository-gate-contract)
also requires executable documentation ownership/source mappings, internal links,
generated command/skill/`llms.txt` integrity, changelog/version coherence, workflow
syntax and local/pre-commit/CI parity checks. Each requires negative fixtures that
fail before correction. Checks cover staged additions and docs-only CI changes;
missing base history or required validators cannot produce green results.
These gates remain **planned** until that change is implemented and verified.

Adapt SpecFact's canonical-source and freshness patterns to this standalone project.
Preserve immutable research with explicit provenance exceptions, avoid per-PR
release bumps for unreleased work, and exclude module signing, registry, paired
repository checkout and publication/deployment machinery. The later advisory-CI
change reuses foundation gates; advisory cost policy never waives repository quality.

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

## CodeRabbit review policy

[.coderabbit.yaml](../../.coderabbit.yaml) adapts the SpecFact review configuration
for this standalone project. Automatic reviews target `main`, skip drafts and
review subsequent pushes. The quiet profile and review instructions request only
high/critical and medium defects (P0–P2), with concrete impact. Low-severity nits,
grammar/Markdown lint, decorative summaries and metadata suggestions are suppressed;
repository quality gates still run independently.

The [official configuration reference](https://docs.coderabbit.ai/reference/configuration)
and v2 schema were checked on 2026-09-28 (Europe/Berlin). They expose no native
severity cutoff: these instructions are a review policy, not a guaranteed alert
filter. Verify actual bot output and configuration acceptance on the PR. Automatic
reviews may pause after five reviewed commits by default; if paused during a fix
loop, explicitly request another review instead of treating the pause as a pass.

Knowledge context is repository-local, external integrations are disabled, and
chat requires an organization member's mention. Automatic approval, label/reviewer
assignment, issue planning and generated fixes are disabled. No account-wide
settings or subscription changes are implied. A completed review of the current
head plus green applicable checks is required before reporting the loop complete;
absence of a bot response is not a passing review. Revert the configuration commit
to roll back this policy.
