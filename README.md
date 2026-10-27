# ChangeCost

Generated references are checked against their actual generator output. Changes to internal skill prose do not require reference rewrites when the rendered output is unchanged.

**Cost estimates and settlement for AI-assisted software changes.**

ChangeCost is an early NOLD AI project exploring how to quote the cost of an
agentic software change, reconcile its actual provider-reported cost, and use
that history to improve future estimates.

**Status: unreleased 0.x alpha/preview feasibility study; pilot To-Validate.** The merged implementation provides explicit Change/Run registration, bindings, lifecycle declarations and
portable import/export. See [CLI examples](docs/cli.md), [v1 contracts](docs/contracts.md)
and [verification evidence](openspec/changes/archive/2026-09-29-core-02-change-run-contracts/TDD_EVIDENCE.md).
[Offline normalized reconciliation](docs/settlement.md), exact subtotals and
immutable computation merged in [PR #28](https://github.com/nold-ai/changecost/pull/28).
Offline [empirical Quotes](docs/quotes.md) merged in [PR #32](https://github.com/nold-ai/changecost/pull/32)
from complete synthetic history. Native CLI archival on 2026-10-04 synchronized the
[accepted specification](openspec/specs/empirical-quotes/spec.md);
[archived verification](openspec/changes/archive/2026-10-04-quote-01-empirical-estimation/TDD_EVIDENCE.md)
retains accepted limits. The exact finite Codex diagnostic import is implemented locally; broader provider imports and calibration remain pending.
The current branch adds [read-only advisory check](docs/cli.md#presentation-errors-and-advisory-budgets), opt-in human output and an [optional synthetic CI summary](docs/ci.md). Verified local historical values can be compared to exact budgets; imported and incomplete claims remain unknown. All valid advice exits zero; technical failures exit 2.
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
One exact finite Codex diagnostic profile is approved and its local reader is implemented; broader source support remains unapproved. The token research
case requires one record. Supported or partial source claims retain field meanings;
partial or unverified claims retain unresolved evidence requirements. Inspection
keeps malformed nested cases and unrepresentable UTC endpoints controlled, and
CSV fields share the existing input byte bound. The hosted research bundle also
requires a computed conflict-free checkpoint outcome; this does not approve native
accounting authority or finality.

[Offline adaptive demand](docs/forecasting.md) is accepted and archived after
PR #43 and the issue-44 correction in PR #45. `quote --demand` references supplied
task and ecosystem artifacts; learning remains synthetic-only until reader approval.
Acceptance covers offline contracts and synthetic checks. It does not publish a
release or establish native accuracy.

## Try local session learning

The current branch provides separate manual and Codex provisional session loops.
For Codex, use a fresh thread per attempt when possible. Before work, freeze an
estimate with an explicit task kind and context:

```sh
uv run --locked changecost --format human session start work-01 --source codex --task-kind bug-fix --context changecost/python --guess 12000
```

After work, explicitly select the local Codex file and outcome without typing tokens:

```sh
uv run --locked changecost --format human session capture-codex work-01 --file /selected/codex-session.jsonl --repository-id my-repository --outcome completed
uv run --locked changecost --format human session history --source codex --task-kind bug-fix --context changecost/python
```

The report compares the frozen estimate to the latest source-reported lifetime
counter. A long-running thread includes work before start. Coverage, completeness,
finality and subagent inclusion remain unknown, and producer claims are unverified.
The next comparable Codex attempt learns from one latest capture per provider
session. Append refresh uses explicit `--revision` and `--reason`. Old forecasts
stay frozen. Inconsistent cohorts can worsen estimates. No collection runs automatically.

Manual is still the default. Omit `--source codex`, then record an independently
measured total with `session finish ID --tokens INTEGER --outcome completed`.
Manual and Codex histories, errors and learning never pool. The existing
`session observe-codex ID --file PATH --repository-id REPO` still attaches only the
exact approved finite diagnostic snapshot. Its partial category facts remain
excluded from totals and learning. The provisional counter mapping grants no
canonical, full-Change, billing or calibration authority.

Back up the separate session database before its first Codex-target start, which
upgrades it to v3. Read-only old-store reports do not migrate. See the
[sessions guide](docs/sessions.md) for producer limits, revisions and rollback.

Run the isolated example in a directory that does not exist:

```sh
uv run --locked python -m changecost.session_demo .changecost/session-demo-01
```

It shows absolute errors of 100, 0, then 800 tokens. Learning can worsen an
estimate. The separate demo never seeds your real `.changecost/sessions.sqlite3`.
See [record and compare your sessions](docs/sessions.md) for finish, correction,
history, storage selection and limitations. Full assurance and acceptance remain pending.

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

Temporary pytest phase tracing is retired after the native timeout investigation.
Historical reports remain retained. Summary rejection tests now reuse the public
entrypoint helper alongside retained process tests. Full Linux matrix assurance
is still required. See the [investigation record](docs/development/quality-gates.md#retired-pytest-phase-investigation).

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

Quote #15 merged in PR #32 on 2026-10-03. Native CLI archival on 2026-10-04
synchronized the accepted offline synthetic estimation and historical replay contract
into main specs. Archived evidence preserves verification and accepted limitations.
Provider collection and calibration remain separate gates.

Source feasibility includes [offline development evidence checks](docs/providers/source-feasibility.md#executable-closeout-checks-2026-10-03).
Issue #9 is closed after accepted capability reconciliation in PR #39 and native
CLI archival. The register now contains 24 profiles: the 23 historical profiles
retain zero approvals, and one exact finite Codex diagnostic mapping has native
usage approval. The finite reader is implemented locally under the separate 2026-10-24 authorization; activation alone grants
no demand, financial or complete-accounting authority.
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

The research checker rejects malformed expectation containers with fixed diagnostics; mapping coverage and exact conclusion types remain separate checks.

Each registered evidence entry retains a nonblank provenance/coverage scope note; uncertainty notes remain claims requiring independent review and never appear in structural reports.

The multiplier-only research strategy admits exactly one record. Fixture expectation shape and key coverage are checked before detector semantics, preserving safe structural diagnostics for compound faults.

Registered citations require a parsed HTTPS destination hostname; this structural check does not probe reachability or provider authority.

Default research checking binds the exact canonical fixture bytes to all twelve registered synthetic references before parsing. In-memory semantic checks and matrix-only rendering make no fixture-byte provenance claim.

## Accepted offline adaptive demand, 2026-10-18

[Adaptive forecasting](docs/forecasting.md) is accepted under #35:
`quote --demand` starts with honest zero knowledge, learns from eligible full-Change
synthetic outcomes and exposes explicit directional transfer hypotheses. It adds
to the delivered economic/advisory CLI.
Missing measurements remain unknown. Broader Codex and Claude readers, approved native demand
accounting and measured pilot evaluation remain separate planned changes.
Missing optional exports/admin access did not block accepted capability closeout;
it did not approve native lanes or establish forecasting accuracy.

### Offline synthetic evaluation

`changecost evaluate-synthetic --history examples/evaluation/history.json --protocol examples/evaluation/protocol.json`
replays a declared synthetic timeline in a disposable store and prints economic,
adaptive, attribution and abandoned-spend metrics. It does not open the normal
runtime database or validate live accuracy. See the
[reproduction guide](docs/pilot/evaluation.md) and [findings](docs/pilot/findings.md).
