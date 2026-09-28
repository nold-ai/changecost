# ChangeCost

**Cost estimates and settlement for AI-assisted software changes.**

ChangeCost is an early NOLD AI project exploring how to quote the cost of an
agentic software change, reconcile its actual provider-reported cost, and use
that history to improve future estimates.

**Status: pilot planning / To-Validate.** There is no installable
ChangeCost package, working CLI, validated estimator, or stable schema yet.
Nine changes are planned in [the pilot backlog](openspec/CHANGE_ORDER.md).
Product implementation and live collection require a subsequent request.
This repository remains private.

## Direction

The proposed feedback loop is **quote → bind → meter → settle → calibrate**.
The unit is a software change, including its retries and abandoned attempts.
Quotes should express uncertainty; settlements should distinguish provider
charges from estimated costs and raw usage. Missing evidence must remain visible.

ChangeCost is intended to be independently useful. SpecFact is a development
quality tool here; a future integration may consume ChangeCost artifacts after
their contract is proven. It is not a runtime dependency.

Initial boundaries exclude a general LLM gateway, observability backend,
dashboard, custom billing database, employee productivity scoring, and a complex
prediction model. The planned personal Cursor/Copilot pilot uses Python 3.11+, Typer/Pydantic,
SQLite/Decimal and the `quote`, `bind`, `settle`, `check`, `explain` command family.
Provider support is subject to the [evidence gate](docs/research/pilot-source-assessment.md).

Read the [project brief](docs/project-brief.md) and
[research provenance and limitations](docs/research/README.md) before proposing
implementation. Research examples are proposals, not supported commands.

## Work on the repository

Bootstrap tooling uses Python 3.11+ for pre-commit and Node.js 20.19+ for OpenSpec.
The current commands below run planning checks only. The
[Python foundation change](openspec/changes/core-01-python-foundation/proposal.md)
will introduce `pyproject.toml`, `uv.lock`, uv-managed environments and Hatchling
builds, then replace this temporary setup. No Python package exists yet.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
npm install --global @fission-ai/openspec@1.13.0
.venv/bin/pre-commit install
PATH="$PWD/.venv/bin:$PATH" make check
```

OpenSpec is already initialized with shared skills under `.agents/skills/`.
`make check` runs repository hygiene and validates OpenSpec artifacts. The nine
change specifications describe future behavior; passing validation does not prove
that behavior has been implemented.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the workflow and
[AGENTS.md](AGENTS.md) for coding-agent instructions. The
[quality rules](docs/agent-rules/50-quality-gates-and-review.md) document SpecFact
review setup and the gates required when implementation starts.

The [four-stage agent workflow](CONTRIBUTING.md#agent-workflow) supports interactive
change selection, plan freshness, implementation, delegated verification and PR
review resolution. [llms.txt](llms.txt) indexes the current agent entry points.

## Community and license

- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security reporting](SECURITY.md)
- [Support](SUPPORT.md)
- [Apache License 2.0](LICENSE)

Project domains reserved by the maintainer: `changecost.dev` and `changecost.io`.
No deployed site is claimed by this bootstrap.
