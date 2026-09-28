# Agent rules index

Always read [05-non-negotiable-checklist.md](05-non-negotiable-checklist.md).

| Task | Additional rules |
| --- | --- |
| Product behavior or OpenSpec work | [40-openspec-and-tdd.md](40-openspec-and-tdd.md) |
| Issues, projects, dependencies or planning PRs | [60-github-change-governance.md](60-github-change-governance.md) |
| Any edit, verification, or finalization | [50-quality-gates-and-review.md](50-quality-gates-and-review.md) |
| Prepare, implement, verify or promote a change | [30-change-workflow.md](30-change-workflow.md) |

These compact rules adapt the SpecFact repositories' bootstrap, scope discipline,
spec/test order, review evidence, and clean-code principles. Source checkouts were
read on 2026-09-27 (Europe/Berlin):

- `nold-ai/specfact-cli` at `d306d2a8e855cba493c8e5b07093565be75e89cc`
- `nold-ai/specfact-cli-modules` at `bdaab8a3fc48c7321d21127e2b0042946cd90bfa`

Sources: each repository's `AGENTS.md`, `openspec/config.yaml`, and
`docs/agent-rules/`; review command guidance also uses core
`docs/modules/code-review.md` and the installed CLI help.

Intentionally omitted: mandatory worktrees for every edit, internal wiki sync,
issue hierarchy caches, signed module registries, Jekyll conventions, mandatory
contract decorators, release matrices, and per-change version bumps before a
release exists. No sibling checkout is required to contribute to ChangeCost.
