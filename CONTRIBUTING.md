# Contributing to ChangeCost

ChangeCost is in bootstrap. Discuss scope with the maintainer before starting
product implementation; the research does not authorize its proposed timeline,
adapters, schema, or CLI.

## Workflow

1. Read [AGENTS.md](AGENTS.md) and the applicable [agent rules](docs/agent-rules/INDEX.md).
2. Check `git status --short --branch`; preserve work belonging to others.
3. Use a focused branch (`codex/<topic>` for coding agents). Use a worktree when
   concurrent work needs isolation; a separate worktree is not mandatory.
4. For product behavior, agree scope, create an OpenSpec change, and follow
   spec → failing tests → implementation → passing tests. Record actual evidence.
5. Run `make check`; run language-appropriate gates and SpecFact review when
   source code exists. See the [quality rules](docs/agent-rules/50-quality-gates-and-review.md).
6. Open a focused pull request with scope, verification, limitations, and rollback.
   Archive completed OpenSpec changes with `openspec archive <change-id>`.

Documentation-only fixes need relevant checks, not artificial runtime tests.
The initial repository bootstrap does not create a product change or release.
Use conventional commit subjects such as `docs: ...`, `chore: ...`, or `fix: ...`.

## Local checks

Follow [README setup](README.md#work-on-the-repository), then run `make check`.
Pre-commit may fix whitespace or final newlines; review the diff and rerun it.
Tool versions are pinned in `requirements-dev.txt`, `.pre-commit-config.yaml`,
and CI. Update pins deliberately and verify local/CI parity.

## Contributions and data

Contributions are provided under the repository's Apache-2.0 license.
Preserve applicable upstream notices and attribution. Review dependency licenses
before adoption; avoid dependencies for behavior the standard library clearly
expresses. No contributor agreement or sign-off requirement is added here.

Use synthetic examples. Do not commit credentials, prompts, source transcripts,
real billing exports, or identifiable session data. Report vulnerabilities through
[SECURITY.md](SECURITY.md), not issues or pull requests.
