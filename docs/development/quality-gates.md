# Repository quality gates

The foundation implements shared local, staged and CI validators in `quality/`.
They are development tooling and are excluded from distributions. `make check`
returns nonzero if any required child fails or cannot run. Python 3.11.15 and
3.13.14 use the same targets; OpenSpec 1.13.2, uv 0.12.19 and actionlint 1.7.12
are bootstrap pins. The lock resolves Python runtime, dev and build dependencies.
The dev group also pins uv so isolated repository tests can invoke it. Pytest
explicitly imports repository helpers from the checkout root; they stay outside
the distributed package. CLI tests resolve the active environment’s console script
from PATH, and the wheel proof puts its clean installation first.

## Inputs and comparison

Always supply `BASE_REF` explicitly. A PR checks its head and the merge-base with
the event base; main pushes use the event's before SHA, including all commits in
the push. Manual CI requires a comparison SHA. Missing history fails. Local
`make check` reads tracked working files plus an explicit `MANIFEST` for intended
new files; it refuses implicit omission when untracked files exist. Unrelated
private `artifacts/` directories are ignored at every depth.

The commit hook materializes Git index blobs into a temporary directory and runs
the staged validator code there. It checks staged additions, removals, renames and
links without stashing or modifying user files. It cannot read an unstaged fix or
untracked link target as part of the commit. Fast hooks run lock, lint, typing,
docs, generated-index, metadata and workflow checks. Complete CI runs tests,
build proof, dependency checks and applicable review too. Hygiene hooks have a
separate shared configuration to prevent aggregate recursion.

## Documentation ownership

`quality/docs.json` lists each maintained Markdown document and llms.txt once,
with a logical owner, manual/generated kind and canonical source path/globs.
New pages need an entry; empty/orphaned sources, duplicate owners and broken
local links/anchors fail. OpenSpec and skill documents are included. The two
original research exports have exact path/hash/reason exemptions; their bytes
are checked, not rewritten. License text is shipped verbatim and excluded from
Markdown analysis because it is not a maintained Markdown page.

Changed sources require a changed corresponding document, or a reviewed entry
in `quality/exceptions.json` keyed by document path:

```json
{"docs/example.md": {"reason": "Specific reason the source change needs no prose change", "digest": "sha256 of the complete mapped source contents"}}
```

Use `quality.repository.digest(root, source_paths)` to compute the binding.
Include path identity and deleted source paths; exclude the target document,
the rationale file and generated llms/command output. Rationale wording remains
a review responsibility. A different source digest invalidates the rationale.
The checker proves structural coverage and detectable drift, not prose accuracy.

## Generated references

`quality/index.json` supplies curated documentation entry points. The renderer
reads local skill frontmatter and the real Typer command parameters; it writes
`llms.txt` and `docs/commands.md` deterministically with `make generate`. Checks
are read-only and show a diff for missing/stale output. Duplicate/dangling inputs
fail. Normal tests run integrity checking even if pre-commit is bypassed. Future
cost commands are labeled as planned, never fabricated as working commands.

## Changelog and versions

`pyproject.toml` owns version 0.1.0.dev0. CLI version comes from installed metadata;
checks compare the project entry in uv.lock, built wheel/sdist and installed CLI.
Initial metadata is valid without inventing a prior release. Versions may not
decrease; ordinary unreleased work does not require a bump or PyPI lookup.
Changed behavior/workflow/contracts need a new substantive Unreleased entry.
An editorial/test-only exception uses key `changelog`, a specific `reason` and
the digest of the changed paths excluding CHANGELOG.md and the rationale file.
Old entries or dates alone fail. Human review still judges whether wording is useful.

## Build and dependency proof

The build gate exports hash-pinned build constraints from uv.lock, builds a wheel
through the sdist, checks archive members/version/license, installs in a clean
runtime-only environment, and runs help/version/error tests outside the checkout
with network attempts blocked. It rejects contradictory build constraints.
Package installation/auditing can use the network; CLI execution and generation
are offline. No publication target or deployment job is provided.

The advisory gate audits exported locked runtime/dev/build requirements using
pip-audit and records `.changecost/dependency-audit.json`; missing data fails.
Installed locked license metadata (release-specific PyPI metadata for dependencies
absent on this platform) is recorded in `.changecost/dependency-licenses.json`
and missing evidence fails. Review the actual license report before accepting new
dependencies; metadata reporting is not legal advice or a compatibility guarantee.

The workflow unit tests isolate the actionlint process boundary and exercise
syntax-failure propagation and conditional-gate rejection. The required workflow
leaf still runs real actionlint; verification also executes a malformed-and-repaired
workflow against that binary. Capsule tests do not depend on a host Go binary.

## Review and limitations

Full review enables `--bug-hunt`, including the required semgrep-bugs member.
`[tool.specfact.code-review]` declares native Git for index tests; pytest’s
`pythonpath` supplies the repository import root. These declarations repair
known setup defects but do not prove capsule execution on an unsupported host.

SpecFact CLI 0.55.4 and review module 0.50.1 produce the native ignored
`.specfact/code-review.json`. The runner binds its scope to a digest of the complete
input set in a sidecar and checks actual required analyzer states and assurance.
Behavior-affecting source, tests, dependencies, validator or CI edits require review;
docs-only work states non-applicability and still runs its gates. Missing/skipped
analyzers fail. The manual hook alone is not review completion.

Review capsules currently need a Linux x86-64 controller. Local macOS results
are UNKNOWN, not PASS. The gate must remain nonzero until the supported runtime
produces complete evidence; no fabricated runtime descriptor or bypass is allowed.
No branch-protection, paid infrastructure, provider collection or deployment is
configured by these files. Revert the foundation changes and recreate the prior
development environment to roll back, preserving all local evidence.


For core-01-python-foundation, the maintainer accepted the known Mac capsule
limitation on 2026-09-28 and deferred that assurance to GitHub CI. Local UNKNOWN
reports remain incomplete evidence. Passing local checks and independent reviews
permit this change’s commit/push handoff; the enabled full CI review must still
execute successfully before claiming merge readiness. This decision does not
turn an unavailable analyzer into a pass or disable the CI gate.
