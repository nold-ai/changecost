# A Lightweight FinOps Primitive for Agentic Software Work

## Executive finding

**TL;DR:** There is a real opportunity here, but it is narrower—and more interesting—than “AI token observability.”

The market already has a growing number of products that can tell you **how many tokens were consumed, what they cost, which model generated them, which engineer/session/project used them, and whether a budget was exceeded**. Langfuse, Datadog, Arize Phoenix, Helicone, LiteLLM, vendor-native Cursor/GitHub telemetry, and newer coding-specific products already cover much of that territory. Some products now explicitly attribute AI spend to pull requests. citeturn5search0turn8search13turn8search5turn8search9turn18search3turn18search5

The interesting unsolved primitive is instead:

> **Before an agentic software change begins, give it an evidence-backed cost distribution and an execution budget; afterward, settle the complete cost of producing the accepted change against that quote, then use that settlement to calibrate the next quote.**

That is substantially different from another token dashboard.

I would describe it as **“Infracost semantics for stochastic agent work.”** Infracost can deterministically price a proposed infrastructure graph before deployment. Agentic software work cannot be priced deterministically because execution trajectories vary, so the equivalent primitive is a **calibrated quote**—for example `$0.65 p50 / $1.90 p90`, with sample size and historical coverage—followed by settlement. Infracost itself demonstrates why the “cost before change” workflow is powerful: it surfaces infrastructure economics directly in terminals, agents, CI, and pull requests instead of requiring engineers to visit a separate FinOps dashboard. citeturn3search1turn18search1

The Claude proposal in the attached README got an important part of this exactly right: its central feedback loop is **declare → underwrite → execute → settle → calibrate**, and it deliberately separates scope settlement from delayed cost settlement. fileciteturn0file0

However, after reviewing the current ecosystem as of **September 27, 2026**, I would simplify that design significantly.

**Keep:**

**quote → bind → meter → settle → calibrate**

**Do not build initially:**

custom token instrumentation, a proprietary price database, a general LLM gateway, another observability backend, another AI-spend dashboard, an elaborate hash-chain ledger, employee-level productivity economics, or a sophisticated ML estimator.

The “Karpathy move” is to make the economic primitive itself tiny and composable.

One correction to the framing is worth making. I could not verify an Andrej Karpathy publication called **“WikiLLM.”** What *is* strongly characteristic of Karpathy's public projects is the design philosophy represented by projects such as `micrograd` and `nanochat`: make an end-to-end system unusually small, understandable and hackable while retaining the essential mechanism. `micrograd`, for example, demonstrates backpropagation with a tiny scalar autograd engine; `nanochat` deliberately packages the entire LLM pipeline into a compact experimental harness with a small number of meaningful controls. citeturn13search3turn13search12

That is the philosophy I would apply here.

> **One economic unit: an accepted software change.  
> One prediction: its cost distribution.  
> One join: change ↔ agent runs.  
> One truth: provider-reported usage/billing.  
> One learning loop: quote ↔ settlement.**

That is small enough to become infrastructure rather than another platform.

**Confidence: High** on the existence of the gap and on the viability of the measurement architecture. **Medium** on how accurately pre-change cost can ultimately be predicted; recent empirical work shows agentic coding costs are intrinsically noisy, which is exactly why calibrated distributions rather than deterministic estimates are necessary. citeturn15academia0


## What already exists and should not be rebuilt

The most important result of the research is that the competitive landscape has moved considerably beyond “token dashboards.” Even several ideas that looked novel in the Claude discussion now exist commercially or as open source.

### Observability and metering are increasingly commodity capabilities

Langfuse already calculates model usage and cost per LLM call, supports model-specific and custom pricing, cache/input/output token distinctions, metrics, and cost analytics. Datadog's Agent Observability surfaces token consumption and cost across calls and models. Arize and Phoenix provide tracing and token/cost instrumentation around LLM, retrieval, and tool operations. Helicone provides gateway-level logging, observability, and unified billing across many models. citeturn5search0turn8search13turn8search5turn8search9turn7search2

LiteLLM similarly provides spend attribution by virtual key, user and team, budget enforcement, project-level tracking, and cost calculation. Its budget controls extend to agents and sessions. citeturn9search0turn9search1turn9search2

Therefore:

> **A new solution should not put itself in the LLM request path merely to meter tokens.**

Doing that introduces credentials, availability, latency, security and operational responsibility while duplicating infrastructure that increasingly already exists.

### Even “AI cost per pull request” is no longer an empty category

This finding materially changes the proposed positioning.

SuperPenguin currently markets cross-provider AI spend attribution and specifically a “cost per merged PR” capability covering coding-agent spending. Its product connects GitHub and local coding-tool telemetry to associate spend with pull requests. citeturn18search3

Git AI advertises aggregation of the token expenditure from multiple agent sessions and subagents into individual pull requests, including work that preceded the final code-producing session. citeturn18search5

Nori advertises token/dollar cost by pull request together with agent/user attribution, routing and spend caps. citeturn18search6

AgentMeter tracks Cursor and Claude Code sessions, CI agent executions, tokens, costs, projects, engineers and tasks, and can place cost summaries on pull requests. citeturn18search4

A small open-source project literally called `agent-cost` maps coding-agent spend to Git commits and attempts to derive per-task cost and ROI signals. citeturn18search2

So **“we attribute tokens to a Git change” is insufficient as the product thesis in September 2026.**

That idea is already being productized.

### The major gateways already own runtime budgets

LiteLLM can enforce spend budgets at several dimensions, while coding vendors themselves are introducing richer usage controls. citeturn9search1turn9search3

GitHub Copilot's current economics are especially important here. Its APIs/SDK expose usage events and accumulated token/AI-credit consumption, and GitHub's model interfaces expose current token prices rather than expecting clients to maintain hard-coded price tables. GitHub explicitly advises consumers not to hard-code model prices. Copilot also supports session usage limits in its newer credit-based economics. citeturn17search0turn17search7turn17search8

Therefore a second conclusion follows:

> **Do not build a generic runtime budget enforcement platform either. Consume native budget controls when available.**

Our system should decide *what budget is appropriate* for a change; the execution environment can enforce it.

### Cursor and Copilot already expose much better telemetry than the original design assumed

The attached prototype relies heavily on Cursor hooks, session files, API ingestion and custom trace records. fileciteturn0file0

That should now be reconsidered.

Cursor's current hook platform does provide useful control points around tool invocation, edits, subagents, compaction and lifecycle events. That remains an excellent mechanism for **scope policy** or for obtaining a small binding signal. citeturn1search3

But Cursor now also provides Enterprise OpenTelemetry export for server-side agent telemetry. Cursor's wire format exports token usage and agent-related operational data, with conversation IDs and usage-event identifiers in relevant logs; the documentation describes reconciliation using `cursor.usage_event.id`. Cursor's Admin API also provides detailed usage and cost information. citeturn16search0turn16search1turn1search10

GitHub Copilot likewise now exposes OpenTelemetry for agent monitoring as well as SDK-level usage metrics. citeturn17search0turn17search1

This produces an important architecture principle:

> **Hooks should be the control plane, not the metering plane.**

Meter from native billing/usage/OTel feeds whenever possible. Use hooks only for something the provider telemetry cannot tell us—primarily **“this agent session belongs to this software change”** and, optionally, scope violations.

That alone removes a large amount of fragile implementation.

### Standards are emerging, so avoid inventing another billing ontology

OpenTelemetry already has generative-AI semantic conventions covering concepts including provider, model, conversation identifiers and input/output/cache/reasoning token usage. OTel also warns that prompt/content telemetry can contain sensitive material, giving another reason not to collect it. citeturn4search0turn4search1turn4search2

FOCUS is also moving directly into AI economics. FOCUS 1.4 was ratified on June 4, 2026, while the 1.5 work currently includes AI model identity, token-oriented pricing scenarios and a SKU price dataset; FOCUS 1.5 is scheduled for ratification in December 2026. citeturn3search5turn10search4turn10search1

This means the Claude prototype's Infracost-inspired static model-price file is useful only as a **fallback adapter**, not as a system of record.

The preferred hierarchy should be:

```text
actual provider charge / AI credits
        ↓
provider runtime pricing API
        ↓
FOCUS-compatible price data
        ↓
versioned static fallback
```

Not the reverse.

### The market map reveals the actual whitespace

| Existing category | What it already solves | What remains interesting |
|---|---|---|
| Langfuse / Datadog / Arize / Phoenix | LLM traces, tokens, cost, model analytics | Does not make a calibrated pre-change economic contract the primary developer primitive. citeturn5search0turn8search13turn8search5turn8search9 |
| LiteLLM / Helicone | Gateway metering, routing, spend attribution, budgets | Runtime/request economics rather than empirical “what should this software change cost?” underwriting. citeturn9search0turn9search1turn7search2 |
| Cursor / Copilot | Native usage, billing, agent/session telemetry and control | Vendor-specific; does not normalize an economic unit around an accepted cross-tool software change. citeturn16search0turn17search0 |
| SuperPenguin / Git AI / AgentMeter / Nori | Post-hoc AI cost per PR/task | The space is increasingly occupied; pre-execution *calibrated quote + settlement feedback* remains a stronger differentiation. citeturn18search3turn18search5turn18search4turn18search6 |
| LiteLLM ROI tooling | Relates spend to merged PRs / engineering work | Still predominantly retrospective; employee-level correlations also create governance concerns. citeturn9search5 |
| Infracost | Shift-left cost impact for deterministic infrastructure | No equivalent stochastic quote/settlement primitive for agent trajectories. citeturn3search1 |
| FOCUS / Tokenomics Foundation | Economic ontology and normalization | Standards, not a developer workflow or per-change underwriting engine. citeturn10search4turn12search0 |

That is the gap I would pursue.


## The missing primitive: an economic contract for a software change

The fundamental unit should not be a prompt, token, conversation, employee or even necessarily a pull request.

It should be a **change**.

A change may have:

```text
one ticket
    ├── Cursor planning session
    ├── Copilot implementation session
    ├── second agent / subagent attempts
    ├── failed iteration
    ├── test-fix session
    └── accepted commit / pull request
```

Economically, all of that expenditure belongs to the same attempted outcome.

This matters because recent empirical research on coding agents strongly suggests that request- or session-level intuition is unreliable. A 2026 study of frontier models on SWE-bench Verified found agentic coding token usage dramatically larger than conventional code-reasoning usage, substantial variation between runs of the same task, weak relationships between token expenditure and success, and poor pre-task token estimates from the models themselves. The researchers observed same-task token variation as high as roughly 30×, and LLM self-predictions were only weakly to moderately correlated with actual expenditure. citeturn15academia0

The FinOps Foundation reaches a complementary conclusion from the billing side: GenAI unit cost depends on model, context, cache behavior, repeated calls and execution structure, so a useful cost unit is a **distribution around an outcome**, rather than a fixed “price per prompt.” citeturn11search2

That evidence argues against several tempting approaches:

**Do not ask the LLM “how many tokens will this task take?” as the estimator.**

**Do not quote one deterministic dollar number.**

**Do not use lines of code as a proxy for economic value.**

**Do not optimize tokens independently of whether the change succeeds.**

Instead, define the settlement unit as:

> **Total attributable agent expenditure required to reach the terminal outcome of a change.**

For a successful change:

```text
change_cost =
    Σ all bound agent runs
    from first attempt
    through accepted/merged result
```

For an abandoned change:

```text
change_cost =
    Σ all bound attempts before abandonment

outcome = abandoned
```

Now something powerful becomes possible:

```text
                   historical settlements
                           │
                           ▼
change intent ──► signature ──► quote distribution
                                p50 / p90
                                   │
                                   ▼
                            execute agents
                                   │
                                   ▼
                        provider telemetry
                                   │
                                   ▼
                           settle actual
                                   │
                                   └─────────► calibration
```

This is more meaningful than “token tracking.”

### Make uncertainty part of the product

The killer UX should not be:

> “Budget = $2.”

It should be something more like:

```text
$ aifin quote BILL-412

Agent cost
  p50          $0.74
  p90          $1.82
  confidence   34 comparable changes
  p90 coverage 87% over last 60 settlements

Work shape
  scope        small
  topology     2 boundaries
  trajectory   T(n·k)
  execution    Cursor / Sonnet

Suggested ceiling
  $2.25

Why
  + cross-module change
  + integration tests
  - no schema migration
  - no parallel-agent expansion
```

After merge:

```text
Agent cost settled

  quoted p50     $0.74
  quoted p90     $1.82
  actual         $1.13
  outcome        accepted

  ✓ inside quoted range
```

That feedback is intuitively useful to a developer without requiring them to understand FinOps.

And it provides finance/platform teams with the statistically meaningful question:

> **When we say p90, do approximately 90% of comparable future changes actually land below it?**

That is far superior to pretending that prediction error can be eliminated.

### Token economics should have two layers

Do not conflate computational consumption and vendor economics.

Store both when possible:

```text
work quantity
─────────────
input_tokens
output_tokens
cache_read_tokens
cache_write_tokens
reasoning_tokens
tool_calls
agent depth
attempts

economic settlement
───────────────────
provider_billed_cost
provider_billing_unit
normalized_list_cost   # optional
```

Why?

A Cursor subscription, GitHub AI credits and direct model API billing can assign different economic costs to approximately comparable model consumption. GitHub's current AI-credit model, for example, gives the platform a vendor billing unit in addition to underlying token consumption. citeturn17search8turn17search9

Therefore the **provider charge is accounting truth**, while token consumption is a causal/explanatory measure.

This also protects the model from pricing changes. Historical workload remains historical workload; only economic normalization has to change.

### Introduce one architecture-complexity dimension

The Tokenomics Foundation's 2026 Big-T proposal is useful here because it intentionally tries to do for agent economics what Big-O does for computational reasoning: describe how an agent architecture amplifies model calls through input size, calls per task and agent depth. It proposes classes around structures such as `T(n)`, `T(n·k)`, and `T(n·k·a)` rather than pretending token consumption is merely a model-price problem. citeturn12search0turn12search4

I would borrow that conceptual idea, but **not make Big-T a required user-facing standard**.

Internally, we need one simple “trajectory shape” field:

```text
single       one bounded agent path
iterative    repeated tool/test loop
parallel     subagents / fan-out
recursive    agents spawning agents
unbounded    no defensible ceiling
```

The quote then understands something that LOC-based estimators miss:

> A ten-line change executed with recursive agent fan-out may have a much more dangerous economic shape than a 500-line mechanical refactor.

That is precisely where FinOps becomes useful.


## A much smaller architecture

The original `envelope` README is directionally strong but contains too many mechanisms for a first proof. It stores envelopes, session files, traces, usage records and an append-only hash-chained settlement ledger, with hooks participating deeply in telemetry capture. fileciteturn0file0

I would reduce the MVP to **three objects and five operations**.

### The three objects

#### Change

What is being attempted.

```json
{
  "change_id": "BILL-412",
  "repo": "billing-service",
  "base_sha": "81e9e9a",
  "scope": [
    "src/billing/**",
    "tests/billing/**"
  ],
  "shape": {
    "scope_bucket": "small",
    "boundaries": 2,
    "trajectory": "iterative"
  }
}
```

No employee.

No prompt.

No source code.

No ticket prose is needed after classification.

#### Run

A vendor-neutral pointer from an agent execution to the change.

```json
{
  "change_id": "BILL-412",
  "provider": "cursor",
  "run_id": "conversation:abc123"
}
```

This mapping is the **only piece that may require a hook**.

Everything else should come from Cursor/Copilot usage telemetry.

#### Settlement

The final economic fact.

```json
{
  "change_id": "BILL-412",
  "revision": "9a7cf1d",
  "outcome": "accepted",

  "usage": {
    "input_tokens": 824130,
    "output_tokens": 19340,
    "cache_read_tokens": 611200
  },

  "cost": {
    "amount": 1.13,
    "currency": "USD",
    "source": "provider_billed"
  },

  "quote": {
    "p50": 0.74,
    "p90": 1.82,
    "peer_count": 34
  }
}
```

Everything interesting can be derived from those three objects.

### The five operations

```text
quote
bind
settle
check
explain
```

No server should be required for the initial pilot.

`quote` is a deterministic function of current change features and historical settlements.

`bind` associates one agent execution with the current change.

`settle` collects vendor usage and writes the final record.

`check` decides whether cost/scope policy is satisfied.

`explain` tells a human why a quote looks the way it does.

The CLI should remain provider-independent:

```text
aifin quote
aifin bind
aifin settle
aifin check
aifin explain
```

The adapters can be tiny:

```text
providers/
    cursor.py
    github_copilot.py
    otel.py
```

### The telemetry flow

For Cursor:

```text
Cursor agent
    │
    ├── tiny binding hook ─────► change ↔ conversation ID
    │
    └── Cursor telemetry
          ├── OTel
          └── Admin usage
                  │
                  ▼
             normalized usage
```

Cursor's OTel data already exposes the identifiers needed to correlate relevant events, while its Admin usage APIs provide billing/usage records; hooks remain available for write/scope control. citeturn16search1turn1search10turn1search3

For GitHub Copilot:

```text
Copilot agent
    │
    ├── hook / session binding ─► change ↔ session
    │
    └── usage
          ├── Copilot SDK usage
          └── OpenTelemetry
                  │
                  ▼
             normalized usage
```

Copilot's current SDK exposes per-model-call usage and accumulated session metrics, while its agent monitoring supports OTel. citeturn17search0turn17search1

This makes the adapters almost boring.

That is good.

### Normalize around OTel concepts instead of inventing a giant event model

A minimal internal record can borrow the relevant OTel GenAI semantics:

```text
provider
model
conversation/run ID

input tokens
output tokens
cache tokens
reasoning tokens

provider cost
timestamp
```

OpenTelemetry's current GenAI semantic conventions already standardize many of these dimensions. citeturn4search0turn4search1

Anything provider-specific can live under:

```json
"provider_fields": {}
```

Do not attempt perfect normalization in v1.

FOCUS can become the cost-export layer once its AI extensions stabilize rather than something the developer workflow must directly understand. FOCUS 1.5 is still in flight as of September 27, 2026, so building to a narrow internal schema plus later FOCUS adapter avoids prematurely coupling the project to an unfinished specification. citeturn10search4

### Do not build the hash-chain ledger yet

The attached design's hash chain is clever:

```text
record[n].prev = hash(record[n-1])
```

but it is probably solving the wrong pilot problem. fileciteturn0file0

A self-maintained hash chain proves internal consistency only under certain assumptions. It does not by itself establish trustworthy authorship or make an administrator incapable of rewriting the entire chain.

Git already provides commit identity/history, while GitHub Actions supports cryptographically signed artifact attestations tied to repository, workflow, commit SHA and execution identity. GitHub's current attestation mechanism uses OIDC-backed provenance and can be verified with the GitHub CLI. citeturn19search0turn19search5

Therefore v1 only needs:

```text
settlement
+ source commit SHA
+ provider evidence ID
+ CI run ID
```

Should externally verifiable provenance become a genuine requirement later, produce a signed attestation rather than inventing another integrity protocol.

That removes another subsystem.

### Do not rebuild Infracost

Infrastructure economics and agent economics should remain orthogonal:

```text
PR economics
├── software-agent spend     ← this project
└── runtime infrastructure   ← Infracost
```

A PR presentation can compose them:

```text
Economic impact

AI implementation
  actual         $1.13 one-time
  p90 quote      $1.82

Infrastructure
  change         +$143/month
```

Infracost already has infrastructure parsing, pricing, policy and PR integration. Reusing it preserves clean boundaries. citeturn3search1


## The estimator should initially be embarrassingly simple

The research does **not** support beginning with an ML cost-prediction model.

The coding-agent study described earlier found weak alignment between intuitive task difficulty and actual token expenditure and very high within-task variability. citeturn15academia0

With forty or even a few hundred examples, a complicated model will mostly create false confidence.

The Karpathy-style solution is a **small empirical tariff table with hierarchical backoff**.

### Build a compact change signature

Start with perhaps four dimensions:

```text
scope bucket
boundary bucket
trajectory shape
agent/model family
```

Potentially:

```python
signature = (
    scope_bucket,
    boundary_bucket,
    trajectory,
    execution_profile,
)
```

Where:

```text
scope_bucket
  XS / S / M / L

boundary_bucket
  0 / 1 / 2+

trajectory
  single / iterative / parallel / recursive

execution_profile
  Cursor+Sonnet
  Copilot+GPT
  ...
```

Do **not** start with 25 features such as import fan-in, cyclomatic complexity, file entropy, AST metrics, test count, issue embeddings and ticket sentiment.

Collect some of those offline and test whether they add predictive power.

The estimator itself can be approximately:

```python
peers = settlements.match(signature)

if len(peers) < minimum:
    peers = settlements.backoff_one_dimension(signature)

if len(peers) < minimum:
    return UNPRICED

return {
    "p50": percentile(peers.cost, 50),
    "p90": percentile(peers.cost, 90),
    "n": len(peers),
}
```

No neural network.

No LLM estimator.

No training pipeline.

No model registry.

The first useful product can literally be an empirical distribution.

### Backoff makes sparse data usable

Exact matching will produce too many empty cells during the cold start.

So use an explicit hierarchy:

```text
repo + shape + trajectory + model
          ↓
repo + shape + trajectory
          ↓
shape + trajectory + model
          ↓
shape + trajectory
          ↓
UNPRICED
```

This gives every quote an understandable explanation.

For example:

```text
p90 $1.82

Basis:
  34 settlements
  same repo
  same scope class
  same trajectory class
  model dimension relaxed
```

That transparency is a feature.

### Calibration matters more than prediction error

For every historical p90 quote:

```text
covered =
    actual_cost <= quoted_p90
```

Then:

\[
\text{p90 coverage}
=
\frac{\sum_i \mathbf{1}(actual_i \le quote_{p90,i})}{N}
\]

A nominal p90 estimator should converge toward roughly 90% empirical coverage.

The initial Claude criterion of expecting observed p90 coverage in an 80–95% region is directionally sensible as a pilot diagnostic. fileciteturn0file0

But I would promote **coverage** above Spearman correlation as the primary metric.

Why?

Imagine:

```text
Quote A
correlation: excellent
p90 coverage: 54%
```

It ranks expensive changes correctly but is dangerous as a budget instrument.

Versus:

```text
Quote B
correlation: moderate
p90 coverage: 89%
```

The second system is much more useful for admission control.

Therefore the principal metrics should be:

| Question | Metric |
|---|---|
| Can people trust the ceiling? | p90 empirical coverage |
| How wide/expensive are our predictions? | p90−p50 interval width |
| Are rankings informative? | Spearman rank correlation |
| Is the system becoming better? | coverage and interval width over time |
| Is work succeeding economically? | cost per accepted change |
| How much spend produces no accepted result? | abandoned-attempt cost / total cost |
| Do agent architectures amplify spend? | cost distribution by trajectory class |

Later, once there are hundreds or thousands of settlements, split conformal calibration or quantile models may become attractive. They should earn their complexity rather than being architectural prerequisites.

### Budget based on the distribution, not arbitrary caps

A simple budget recommendation can be:

\[
budget = p90 \times safety\_factor
\]

For example:

\[
\$1.82 \times 1.20 = \$2.184
\]

Rounded to an operationally useful ceiling:

```text
suggested limit = $2.25
```

That can be translated into a vendor-native control.

For Copilot, for example:

```text
quote
   ↓
p90 economic ceiling
   ↓
equivalent AI-credit ceiling
   ↓
Copilot session limit
```

GitHub's current SDK/CLI platform exposes AI-credit usage and session-limit mechanisms, so the project can eventually turn prediction into enforcement without becoming the enforcement engine itself. citeturn17search0turn17search7

That is a very clean separation of responsibility.


## What makes this potentially “that’s awesome”

The “awesome” factor should not come from a large dashboard.

It should come from making something previously invisible feel obvious.

### The moment before starting

A developer invokes an agent and immediately gets:

```text
Implement BILL-412

Expected AI work       $0.74
Likely upper range     $1.82
Suggested ceiling      $2.25
Evidence               34 comparable changes

✓ normal economic shape
```

That is useful with virtually no cognitive load.

### The moment architecture accidentally explodes

Suppose someone turns:

```text
single agent
```

into:

```text
planner
  ├── researcher × 4
  ├── implementer × 3
  └── reviewer × 2
```

The tool should react:

```text
Economic shape changed

  previous    iterative
  now         parallel / depth 2

  historical p90
    $1.82  →  $7.40

This is not blocked in shadow mode.
```

That is a genuine FinOps intervention.

It explains the **economic consequence of orchestration design**, not merely the invoice afterward.

The Big-T work strongly supports treating calls, input/context scale and agent depth as fundamental multiplicative factors in agent economics. citeturn12search0turn12search4

### The pull request tells the complete story

A PR check could eventually be only this:

```text
AI ECONOMICS                     ✓

Quoted       $0.74 / $1.82 p50/p90
Settled      $1.13
Outcome      accepted
Coverage     within p90
Runs         3
Agents       Cursor

Infrastructure
              +$0/month
```

No portal required.

Finance can consume aggregated settlements separately.

### The scale-out decision becomes evidence-based

This is where the concept becomes more valuable than merely saving a few dollars.

Suppose Team A wants to introduce a multi-agent harness.

Run it in shadow mode and compare within comparable change classes:

```text
                         native      new harness

accepted-change p50      $0.71       $0.83
accepted-change p90      $1.88       $3.42
abandonment               8%          5%
median completion         ...
```

Then scaleout has an explicit economic question:

> Does the harness improve outcomes enough to justify the additional cost distribution?

That is far better than comparing gross team token totals.

The original Claude proposal correctly identified this use case, but framing it around **accepted-change economics** rather than raw usage makes the comparison much stronger. fileciteturn0file0

### Deliberately do not compute “engineer ROI”

This is an important design decision.

Some new products correlate spend with engineers, estimated engineering effort, productivity or individual usage. LiteLLM's recently published ROI approach, for example, relates AI spend and pull-request work in an attempt to estimate engineering economics. citeturn9search5

I would deliberately **not** compete there.

Apart from methodological problems, it fundamentally changes the trust model.

The system should answer:

```text
How expensive was the change?
```

not:

```text
How economically productive was Dom?
```

That distinction is particularly important in Germany.

Section 87(1)(6) of the German Works Constitution Act gives the works council co-determination rights over technical systems intended to monitor employee behavior or performance. German Federal Labour Court jurisprudence interprets this broadly: a system may fall within the rule when it is objectively capable of recording behavioral or performance information; the employer's subjective intention not to monitor employees is not necessarily decisive. citeturn20search12turn20search0turn20search3

GDPR Article 5 additionally requires purpose limitation and data minimization. citeturn20search5turn20search15

So the safest technical design is also the cleanest product design:

```text
change_id
repo
agent system
economic facts
```

not:

```text
employee
manager
personal consumption
ranking
productivity score
```

Conversation IDs should be considered potentially re-identifiable rather than magically anonymous simply because the email address was removed. They can be retained in the restricted binding layer and replaced by opaque run IDs in analytics.

This is a design recommendation, not legal advice; the concrete deployment should still be reviewed under the applicable Betriebsvereinbarung/data-protection framework.


## A defensible pilot and product path

I would **not build the entire README kit first**.

The experiment should be narrower:

> **Can historical accepted-change settlements produce a useful calibrated cost distribution for the next software change?**

Everything else is secondary.

### Shadow pilot architecture

The first release could realistically be this small:

```text
                     ┌─────────────────────┐
                     │    aifin quote      │
                     │ empirical estimator │
                     └──────────┬──────────┘
                                │
                         Change ID + quote
                                │
             ┌──────────────────┴──────────────────┐
             │                                     │
        Cursor adapter                       Copilot adapter
             │                                     │
        native telemetry                      native telemetry
             └──────────────────┬──────────────────┘
                                │
                          normalize usage
                                │
                     ┌──────────▼──────────┐
                     │   aifin settle      │
                     └──────────┬──────────┘
                                │
                      settlements.jsonl
                                │
                                └──► next quote
```

One executable.

One ledger/table.

Two adapters.

No web UI.

No proxy.

No model training.

No separate database initially.

No prompt storage.

No employee dimension.

### Storage should remain boring

For the FDE experiment:

```text
.aifin/
  bindings.jsonl
  settlements.jsonl
```

or an equivalent small SQLite database.

For organization scale:

```text
native OTel
   ↓
existing telemetry/warehouse
   ↓
settlement materialized view/table
```

The project should not grow its own observability database if the organization already operates one.

### A stronger pilot sequence

Given the current date of **September 27, 2026**, the Claude proposal's planned dates beginning September 28 are still workable, but I would change what is being tested.

**September 28–October 2:** implement adapters, change binding and settlement only. Validate exact Cursor and Copilot reconciliation. Do not expose quotes yet.

**October 5–16:** shadow collection. Determine whether sessions can reliably be grouped into complete change costs. This is more important than building sophisticated feature extraction.

**October 19–30:** turn on empirical quotes where peer counts are sufficient. Leave all other changes `UNPRICED`.

**November 2:** evaluate calibration and usefulness.

The attached plan expected approximately 20 settlements after shadow mode and roughly 40 by the end of the advisory phase. fileciteturn0file0

Forty observations are enough to falsify obviously poor ideas, but **not enough to claim a generally reliable predictive model across many repositories, agents and task classes**. Treat the pilot as feasibility evidence, not statistical completion.

### Pre-register a smaller set of hypotheses

I would reduce the original five hypotheses to three.

| Hypothesis | Test |
|---|---|
| **Change-level attribution is reliable.** | ≥95% of pilot agent spend can either be bound to a change or explicitly classified as unbound. |
| **Empirical peers provide useful uncertainty bounds.** | p90 quote coverage approaches its nominal range without absurdly wide intervals. |
| **Execution shape explains meaningful variance.** | trajectory/model/harness dimensions materially improve quotes versus a repo-wide unconditional baseline. |

Then add two baselines:

```text
Baseline A: global median/p90 for repo
Baseline B: LLM self-estimated cost
Proposed:   empirical signature/backoff
```

The coding-agent research suggests Baseline B may perform poorly, which is precisely why it is scientifically useful to include it instead of assuming so. citeturn15academia0

### Success should not require finding a security issue

One criterion in the attached proposal is that the system should produce “at least one security or FinOps finding before any code is written.” fileciteturn0file0

I would remove this.

It encourages a system to manufacture findings in order to demonstrate value.

The pilot should measure an economic mechanism.

Security/privacy admission can later become independent plugins:

```text
quote plugins
├── cost
├── security
├── privacy
└── infrastructure
```

The core should not depend on them.

### A realistic MVP boundary

I would call the first version complete when this works:

```bash
$ aifin quote BILL-412
p50 $0.74 / p90 $1.82 · n=34 · calibrated 87%

# work happens

$ aifin settle BILL-412
actual $1.13 · accepted · inside p90
```

and the same records appear automatically in CI.

Anything beyond that must justify itself against this question:

> **Does this improve attribution, prediction, enforcement, or trust?**

If not, leave it out.


## Risks, assumptions, and recommendation

### The main risks

The largest technical risk is **attribution quality** rather than token counting. A developer may use multiple coding tools, continue a conversation across branches, perform exploratory work before a ticket exists, or abandon an attempt. Existing products that advertise per-PR attribution reinforce that this is both valuable and nontrivial. citeturn18search3turn18search5

The mitigation is to make the join explicit and inspectable:

```text
change
  ├── run A
  ├── run B
  └── run C
```

Never silently pretend ambiguous spend was correctly allocated.

Report:

```text
attributed spend       92%
unbound spend           8%
```

until coverage is genuinely good.

The second risk is **false precision**. Agent trajectories can vary greatly even for the same task, and cost does not monotonically translate into quality. citeturn15academia0

Mitigation: never display `$1.237 expected`. Display distributions, peer counts and coverage:

```text
$0.74 p50 / $1.82 p90
34 comparable settlements
```

The third risk is **Goodhart's law in organizational use**. Once per-change cost becomes an employee metric, developers may optimize visible spend instead of correctness, avoid experimentation, split changes artificially or perceive the system as surveillance.

Mitigation: prohibit employee rankings in the canonical data model. German co-determination and GDPR considerations make that governance boundary particularly important. citeturn20search0turn20search5

The fourth risk is **pricing semantics**. Subscription credits, token pricing, cached tokens and provider discounts make “cost” less universal than it looks. GitHub's move toward AI-credit economics is an example. citeturn17search8

Mitigation: preserve raw provider usage and provider billing units separately. Do not overwrite historical consumption when pricing changes.

The fifth risk is **building yesterday's missing feature**. This space is moving extremely fast: PR-cost attribution, OTel exports, usage APIs, credit controls and FinOps standards have all advanced substantially. citeturn16search0turn17search0turn18search3turn10search4

Mitigation: make vendor adapters replaceable and keep the unique IP/logic in the quote-settle-calibration engine.

### Assumptions that could flip the recommendation

The thesis weakens materially if Cursor or GitHub introduces a native, statistically calibrated **pre-task/change p50/p90 cost estimator with post-merge settlement**. I did not find evidence that either currently provides that capability in the researched material. Their current capabilities instead give us strong underlying telemetry on which to build. citeturn16search0turn17search0

It also weakens if agent costs become economically negligible relative to every other engineering cost. Current industry activity around usage-based agent billing, AI credits, budget controls and FinOps suggests the opposite direction for heavily agentic workloads, but the value must ultimately be demonstrated with *your* settlement distribution rather than market anecdotes. citeturn17search8turn11search2

Finally, the project is much less useful if session-to-change attribution cannot reach high coverage without invasive developer behavior. That is precisely the first thing I would test.

### What I would ship

The research leads me to a significantly smaller concept than the original envelope system:

> **Build a tiny open “change economics” engine, not an AI FinOps platform.**

Its contract is:

```text
             ┌──────────────┐
             │    CHANGE    │
             └──────┬───────┘
                    │
             quote before work
                    │
                    ▼
          p50 / p90 + evidence
                    │
                    ▼
               agent runs
                    │
        native provider telemetry
                    │
                    ▼
                 settle
                    │
                    ▼
          actual cost + outcome
                    │
                    └──────────────┐
                                   │
                         calibrate next quote
                                   │
                                   ▼
                              better bounds
```

The product principle is equally compact:

**Use Git for work identity.  
Use providers for metering.  
Use OTel for telemetry semantics.  
Use FOCUS for future FinOps interchange.  
Use Infracost for infrastructure.  
Use empirical distributions for prediction.  
Use CI for policy.  
Store no prompts and rank no humans.**

The genuinely novel primitive is the **calibrated economic contract around an accepted software change**.

And the thing I would specifically *not* build is the thing most AI FinOps products naturally become:

```text
             BIG AI FINOPS DASHBOARD
                         ↑
                       nope
```

Instead:

```text
$ aifin quote

p50  $0.74
p90  $1.82
n    34

$ aifin settle

$1.13 ✓
```

That is much closer to the Karpathy-style target: small enough that an engineer can understand essentially the whole mechanism, useful enough to drop into Cursor, VS Code, CI and an FDE engagement, and composable enough that existing observability, billing and FinOps systems can consume the result rather than being replaced.

**Overall confidence: High** that this is a stronger wedge than token observability, dashboards, generic budget enforcement, or simple PR-cost attribution. **Medium** that structural change signatures will predict cost well enough for narrow p90 intervals; that is the central empirical question the pilot should answer. **High** that native Cursor/Copilot telemetry substantially reduces the engineering required compared with the attached prototype. citeturn16search0turn16search1turn17search0turn17search1

The most valuable first artifact is therefore not a dashboard or a full repo scaffold. It is a **roughly few-hundred-line quote/bind/settle prototype** whose only scientific objective is to determine whether this equation is useful in your real engineering environment:

\[
\boxed{
\text{declared change shape}
\;\longrightarrow\;
P(\text{cost}\mid\text{historical peers})
\;\longrightarrow\;
\text{actual settlement}
\;\longrightarrow\;
\text{calibration}
}
\]

If that loop works, virtually everything else—budgets, agent routing, CI gates, FOCUS export, FinOps reporting, scale-out policy and eventually richer prediction—can be added around a sound primitive.

If that loop does **not** work, the pilot fails cheaply, and you have avoided building yet another AI-cost platform that explains yesterday's spend beautifully but cannot change tomorrow's economics.