# ChangeCost

**Cost estimates and settlement for AI-assisted software changes.**

ChangeCost is an early NOLD AI project exploring how to quote the cost of an
agentic software change, reconcile its actual provider-reported cost, and use
that history to improve future estimates.

**Status: unreleased CLI foundation / pilot To-Validate.** The local package now
provides offline `changecost --help` and `changecost --version`. Cost estimation,
provider imports, binding and settlement remain planned in
[the pilot backlog](openspec/CHANGE_ORDER.md). Live collection requires a separate
request. This repository remains private.

The [source-feasibility research](docs/providers/source-feasibility.md) now covers
Copilot, Cursor, Codex and Claude Code. Local Codex/Claude metadata supplies partial
usage evidence and synthetic fixtures. [Cursor Basic local metadata](docs/providers/cursor-local-metrics.md)
adds context evidence; [VS Code hosted Copilot](docs/providers/copilot-local-metrics.md)
adds linked usage/checkpoint evidence. Copilot OTel and Cursor CSV remain uninspected.
The [Enterprise artifact review](docs/providers/enterprise-schema-review.md) now
compares supplied projections with official contracts and records their limits.
Its [v2 review](docs/providers/enterprise-v2-schema-review.md) adds reported VS Code
message counters and checks synthetic examples without claiming native compatibility.
Work OTel is reported disabled; custom session-log hook output is the next evidence source.
No provider import profile or runtime adapter is approved yet.

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

Use Python 3.11+ and uv 0.12.19. The tested interpreter matrix is 3.11.15 and
3.13.14. Hatchling builds the package; uv owns dependency resolution and the
committed `uv.lock`. Pydantic is selected for later contracts but is not needed by
this help/version-only runtime.

```sh
uv sync --locked --group build
uv run --locked changecost --help
uv run --locked changecost --version
uv run --locked pre-commit install
npm install --global @fission-ai/openspec@1.13.2
```

Repository checks also need actionlint 1.7.12 and the supported SpecFact review
runtime. See [contributor setup](CONTRIBUTING.md#local-checks) and
[quality gate contracts](docs/development/quality-gates.md).

```sh
BASE_REF=origin/main make check
```

Resolve/fetch the intended base before checking. When new files are not staged,
pass an explicit reviewed newline-delimited path manifest with `MANIFEST=path`.
An unresolvable base or unavailable required analyzer fails the aggregate. On
macOS the installed SpecFact 0.50.1 capsules report an unsupported controller;
use a supported Linux x86-64 review environment before claiming the full gate passes.

The [generated CLI reference](docs/commands.md) and [agent index](llms.txt) describe
implemented behavior. [OpenSpec artifacts](openspec/CHANGE_ORDER.md) are future
contracts until their tasks and evidence establish delivery. See
[AGENTS.md](AGENTS.md) and [CONTRIBUTING.md](CONTRIBUTING.md) for the four-stage
workflow; implementation does not itself commit, publish, merge or deploy.
For changes with review/fix work, retain an ignored bounded session receipt so
repeated findings and exhausted review budgets trigger investigation or replanning.
The session names expected CI checks and commit statuses explicitly and binds
evidence to Git HEAD, working files and staged blobs/modes. Refreshing that binding
requires fresh passing evidence before completion.
Completion also requires explicit measured active time; a missing measurement is
unknown. Latest changes-requested reviews block readiness even without inline threads.
Canonical event replay checks saved decisions against their history. Exact repository,
PR and reviewer identities prevent unrelated evidence from satisfying the session.
Initialize only genuinely new sessions; recover existing missing receipts without
resetting counters. Published completion requires clean inputs.
Initial scope uses verified commit IDs and real file hashes (or `<absent>` for
planned files). Effective reviewer objections remain blocking until approval or
dismissal of the original rejecting review, rather than disappearing on a comment.
Watcher completion/replanning output remains visible even without a GitHub change;
local budget changes take precedence over a no-progress timeout.
Expected PR target ref/SHA is separate from the comparison commit. Retargeting or
base advancement requires explicit adoption and fresh local/remote evidence, even
with unchanged HEAD; schema-5 receipts preserve the original contract and counters.
Input generations are independent of caller event IDs; automatic PR binding chooses
an unused identity atomically, retaining existing finding/scope references.
Renewed requests to required reviewers block completion even with a prior approval;
missing or changing request metadata cannot retain a green result.
Handoff status, evidence and watcher exit decisions use one receipt revision.
Required event text rejects whitespace-only values without rewriting valid identities.
Resolved remote reports require explicit local reviewer coverage of current thread
content; resolution alone does not adjudicate a finding. Budget exhaustion overrides
remaining investigation even when all other completion evidence passes.

## Community and license

- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security reporting](SECURITY.md)
- [Support](SUPPORT.md)
- [Apache License 2.0](LICENSE)

Project domains reserved by the maintainer: `changecost.dev` and `changecost.io`.
No deployed site is claimed by this bootstrap.


The foundation's commit hook checks the staged snapshot against HEAD by default.
The required host lock gate includes real missing/stale/repaired lock probes. Its
stale fixture uses resolvable version drift, distinguishing lock freshness from
dependency resolution failure.
The complete local/CI gates additionally verify the installed CLI, distribution
privacy, dependency evidence and all required review analyzers; incomplete capsule
results remain failures. A native advisory-success verdict is accepted only with
complete passing analyzer evidence and a zero exit code. See the [gate guide](docs/development/quality-gates.md)
for the pinned analyzer composition and hosted-runner trust boundary.
