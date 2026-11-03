# ChangeCost

**Cost estimates and usage history for AI-assisted software changes.**

ChangeCost is a local CLI for exploring what an AI coding task might cost and
comparing estimates with recorded usage. Its change-level accounting groups
attempts, retries, and abandoned runs so their evidence stays attached to the work.

**Early alpha preview.** The current package is `0.1.0.dev0`, available from source.
Forecast accuracy on real work is unvalidated, provider support is narrow, and
commands and data formats may change.

[Website](https://changecost.dev/) · [Quick start](#quick-start) ·
[Guides](#guides) · [Contributing](CONTRIBUTING.md)

## What you can try today

- Record local coding sessions, freeze a token estimate before work, and compare
  it with a supplied total afterward. Comparable sessions inform later estimates.
- Register software changes and their runs, bind evidence, and reconcile supplied
  cost records offline. Keep token counts, estimated costs, and billed charges distinct.
- Compute cost estimates from eligible synthetic history and inspect read-only
  budget advice. Missing or incomplete evidence stays unknown.
- Import selected local Codex and Claude diagnostics within the
  [provider limits](#provider-support). Importing diagnostics does not establish a bill.

Session experiments use a separate database from change-level cost accounting.
Neither workflow collects data automatically.

## Quick start

You need Git, Python 3.11 or newer, and
[uv](https://docs.astral.sh/uv/getting-started/installation/).
The checkout selects Python 3.13 by default. Install from source:

```sh
git clone https://github.com/nold-ai/changecost.git
cd changecost
uv sync --locked --no-dev
uv run --locked --no-dev changecost --help
```

### Run a session demo

This example needs no provider account, credentials, or private session files.
It runs three synthetic sessions and prints their estimates and errors:

```sh
uv run --locked --no-dev python -m changecost.session_demo .changecost/session-demo-01
```

The output includes:

```text
session  forecast  actual  signed_error  absolute_error
one           100     200          -100             100
two           200     200             0               0
three         200    1000          -800             800
Next forecast: 200 tokens from 3 samples.
```

All quantities above are tokens. The `actual` column contains the demo's supplied
measurements. The third session shows why learning from history can worsen an
estimate when tasks differ.

The demo writes `sessions.sqlite3` and `transcript.json` inside the named directory.
It leaves your normal session history untouched and refuses to overwrite an
existing directory. Choose a new directory name to run it again.

To try your own work, follow [Record and compare your sessions](docs/sessions.md).
That guide covers manual measurements and the separate provisional Codex counter
workflow, including supported producer versions, backups, and corrections.

### Explore cost estimation

Run the committed synthetic evaluation to exercise offline cost and token
forecasting with example history:

```sh
uv run --locked --no-dev changecost evaluate-synthetic \
  --history examples/evaluation/history.json \
  --protocol examples/evaluation/protocol.json
```

This prints a JSON report using disposable databases. The example's economic case
estimates USD 10 at the 50th percentile and USD 18 at the 90th percentile, against
supplied USD 15 truth. These are synthetic results, not evidence of real-world
accuracy. See the [evaluation guide](docs/pilot/evaluation.md) for the report fields
and [offline CLI guide](docs/cli.md) to register your own changes and runs.

## Provider support

Local readers require explicitly selected files. Compatibility is limited to the
versions and source shapes documented in each guide.

| Source | Current preview support |
| --- | --- |
| Manual sessions | You supply measured token totals and declare their coverage. Estimates use comparable local history. |
| Codex session counters | A provisional workflow reads a selected thread's lifetime counter from compatible major-0 producers. Exact versions and frozen forecasts are preserved. See [supported grammar and limits](docs/sessions.md#capture-a-new-codex-session-without-typing-totals). |
| Codex diagnostics | The approved diagnostic reader accepts one exact finite snapshot. It supplies no session totals or learning. See [finite snapshot limits](docs/sessions.md#attach-the-approved-finite-codex-observations). |
| Claude diagnostics | Explicit imports for compatible major-2 Code and Desktop producers through `claude-code-2` and `claude-desktop-2`, with separate source grammars and exact producer versions. See [import examples and limits](docs/settlement.md#import-approved-claude-project-diagnostics). |
| Copilot and Cursor | Research and planned readers. No implemented native imports. |

## Alpha limits

- Real-world forecast accuracy and calibration remain unvalidated. Offline
  economic and adaptive forecasting demonstrations use synthetic evidence.
- A Codex lifetime counter can include work before you started a ChangeCost session.
  Its completeness, finality, and inclusion of subagents remain unknown.
- Native diagnostics do not establish complete change usage, billed cost, or
  eligibility for the offline economic and adaptive forecasting workflows.
- Budget checks provide advice. They do not stop an agent or enforce spending limits.
- There is no automatic collection, hosted dashboard, or published stable release.
  Back up existing local stores before experimenting with upgrades.

The [evaluation findings](docs/pilot/findings.md) and
[source-feasibility guide](docs/providers/source-feasibility.md) record the evidence
gaps. Local data stays under `.changecost/` by default. Keep runtime databases,
exports, and original provider files private.

## Guides

| Goal | Read next |
| --- | --- |
| Track estimates and session measurements | [Local sessions](docs/sessions.md) |
| Register changes, runs, and evidence | [Offline CLI examples](docs/cli.md) |
| Understand cost records and reconciliation | [Settlement](docs/settlement.md) and [data contracts](docs/contracts.md) |
| Explore forecasting | [Cost estimates](docs/quotes.md) and [adaptive demand](docs/forecasting.md) |
| Look up a command or flag | [CLI reference](docs/commands.md) |
| Understand the project direction | [Project brief](docs/project-brief.md) and [change order](openspec/CHANGE_ORDER.md) |

## Contribute or get help

Reproducible bug reports and focused proposals help shape the preview. See
[Support](SUPPORT.md) for reporting details and
[Contributing](CONTRIBUTING.md#local-checks) for the development setup and checks.
Contributor review tools are separate from the runtime-only quick start above.

ChangeCost is a [NOLD AI](https://github.com/nold-ai) project under the
[Apache License 2.0](LICENSE).
[Code of conduct](CODE_OF_CONDUCT.md) · [Security reporting](SECURITY.md)
