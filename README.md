# ChangeCost

**Cost estimates and settlement for AI-assisted software changes.**

ChangeCost is an early NOLD AI project exploring how to quote the cost of an
agentic software change, reconcile its actual provider-reported cost, and use
that history to improve future estimates.

**Status: unreleased 0.x alpha/preview feasibility study; pilot To-Validate.** The merged implementation provides explicit Change/Run registration, bindings, lifecycle declarations and
portable import/export. See [CLI examples](docs/cli.md), [v1 contracts](docs/contracts.md)
and [verification evidence](openspec/changes/archive/2026-09-29-core-02-change-run-contracts/TDD_EVIDENCE.md).
[Offline normalized reconciliation](docs/settlement.md), exact subtotals and
immutable computation merged in [PR #28](https://github.com/nold-ai/changecost/pull/28).
This checkout implements [offline empirical Quotes](docs/quotes.md) from complete
synthetic history; verification/publication is tracked in the active change. Native
provider imports and calibration remain pending.
Live collection requires a separate request. This repository remains private.

The delivered [Python foundation](openspec/specs/python-foundation/spec.md) and
[bounded review workflow](openspec/specs/bounded-review-session/spec.md) are archived
alongside [Core-02 contracts](openspec/specs/change-run-contracts/spec.md) as of
2026-09-29. Settlement is accepted and archived as of 2026-10-02, with synchronized
[reconciliation requirements](openspec/specs/evidence-reconciliation/spec.md) and
[final verification evidence](openspec/changes/archive/2026-10-02-settlement-01-reconciliation/TDD_EVIDENCE.md).

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
No provider import profile or runtime adapter is approved yet. The token research
case requires one record. Supported or partial source claims retain field meanings;
partial or unverified claims retain unresolved evidence requirements.

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
committed `uv.lock`. Pydantic 2 validates the portable contracts; Typer exposes the offline CLI.
SpecFact is separate contributor tooling and is absent from the runtime dependency set.

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
unknown. Fractional budgets, time and usage retain finite canonical totals from
original measurements; overflowing updates are rejected without granting unlimited allowance.
Every refresh validates current changed-path coverage. Changing authorized paths
requires an explicitly referenced approved scope manifest; packets retain both
the original contract and recaptured current manifest.
Remote collection makes exactly two complete paginated passes under one deadline
and accepts only matching meaningful evidence, returning the second observation.
Drift or second-pass failure invalidates prior green monitoring. This bounded check
is not an atomic API snapshot and cannot detect reverted or post-final-read changes.
Contract-required completed checks must conclude `success`; `neutral` cannot prove
required validation ran. Optional neutral checks retain their nonblocking policy.
This repository assurance rule is stricter than GitHub's native merge eligibility.
Local reviewer coverage includes every fetched thread, review body and PR comment,
including historical and informational reports. Namespaced thread/review/comment IDs
bind exact content without metadata noise; new, edited or removed reports require
explicit revalidation. Bot-summary churn can therefore require another local
attestation. Empty bodies are valid; missing or malformed identities/bodies and duplicate identities
invalidate monitoring. Coverage never clears objections or unresolved findings.
Input binding includes every declared path, even ignored files or explicit absence.
Existing declared content outside the index prevents clean completion; unrelated
ignored artifacts remain excluded. Remote positive evidence must also postdate
initialization, because its earlier base context cannot be attested. This may
require rerunning valid same-base checks; exact timestamp comparison has no rounding
allowance for coarse provider timestamps. Objections remain blocking regardless of age.
Integer counters retain exact nonnegative values without floating conversion;
unrepresentable floating measurements reject atomically with controlled recovery
for malformed persisted history.
Latest changes-requested reviews block readiness even without inline threads.
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
with unchanged HEAD; schema-8 receipts preserve the original contract and counters.
Input generations are independent of caller event IDs; automatic PR binding chooses
an unused identity atomically, retaining existing finding/scope references.
Renewed requests to required reviewers block completion even with a prior approval;
missing or changing request metadata cannot retain a green result.
Handoff status, evidence and watcher exit decisions use one receipt revision.
Required event text rejects whitespace-only values without rewriting valid identities.
Resolved remote reports require explicit local reviewer coverage of current thread
content; resolution alone does not adjudicate a finding. Budget exhaustion overrides
remaining investigation even when all other completion evidence passes.
Observations must retain their collection-time input epoch; missing or stale metadata
replaces earlier green evidence with incomplete status instead of being relabeled.

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

Contributor review can use the [behavioral evidence pilot](docs/development/behavioral-evidence.md) for bounded
lifecycle controls and content-bound delta review. Final required gates remain mandatory.

Quote #15 runtime implementation was authorized on 2026-10-03. This checkout adds
offline synthetic empirical estimation and historical replay; verification/publication
remain tracked in the active change evidence. No provider collection is authorized.

Source feasibility now includes [offline development evidence checks](docs/providers/source-feasibility.md#executable-closeout-checks-2026-10-03). Issue #9 remains open for native profile approval; adapters remain separate planned changes.
CLI controls exercise safe private-manifest reports, changed-hash rejection and
matrix drift/repair; structural success does not approve native provider profiles.
Checkpoint controls distinguish cumulative progress/replay from conflicts within
one SDK session/event identity and leave finality unknown.

Source evidence detector controls reject boolean replacement revisions, normalize
cumulative interval timestamps to UTC, and leave absent checkpoints unresolved.

The source checker requires exact nonblank identity strings before affirmative
scope claims, and complete stable economic-basis and revision identities for corrections.

Source snapshot totals validate each quantity before replay deduplication. Claude
correlation counts require complete stable identities; physical row counts remain observations.

Inspection reports and validated-reference failures retain registered opaque profile/
evidence keys. Unknown or unsafe references remain redacted; source approval stays separate.

Cumulative estimates require exact nonblank metric identities; correction history
counts require a complete single scope. Projection fields do not demonstrate billing corrections.
