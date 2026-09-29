# Lessons learned: the token cost of the review loop

**ChangeCost · First Python foundation · 28 September 2026**  
Evidence snapshot: **19:50 Europe/Berlin**. The snapshot's measurements remain
historical. This change implements the bounded-session recommendations; the
supported-Linux preflight and reviewer calibration remain pending.

ChangeCost aims to make the cost of a software change understandable. Its first
foundation exposed why that matters: a small runtime change can accumulate a large
implementation, verification, and review bill. The lesson is to measure the whole
change—and move defect discovery earlier—before this workflow becomes routine.

## What we observed

| Measure | At the snapshot |
| --- | --- |
| Elapsed session time | Approximately **6 hours 6 minutes** |
| Commit sequence | **1 initial implementation + 13 follow-up fixes** |
| Model responses | **2,110 unique response IDs** across the parent and six workers |
| Local model diversity | All seven recorded sessions used **`gpt-6-astra`** |
| Parent orchestration | **407 agent-wait calls** and **244 commentary messages** |
| Python line counts, initial → snapshot | Runtime **43 → 43**; quality tooling **946 → 1,189**; tests **523 → 1,611** |

### Token volume needs an accounting boundary

| Recorded usage | Tokens, rounded |
| --- | ---: |
| Cached input | **272.26 million** |
| Uncached input | **3.19 million** |
| Output, including reasoning | **0.619 million** |
| Total input + output | **276.07 million** |

Approximately **98.84% of input was cached**. These are accumulated request tokens,
including repeated context; they are neither unique written content nor uniformly
priced tokens. Reasoning is already included in output. **Actual monetary cost is
not established.** External review-bot inference, GitHub CI, and this retrospective
are outside this accounting boundary. Waiting calls indicate orchestration
activity; they do not establish how much token usage was avoidable.

## Five lessons to carry forward

1. **Fix the failure family.** Review findings progressed through environment
   overrides, matrix interpretation, and pytest configuration precedence. Each
   narrow fix left related paths unexplored. On a repeated finding in the same
   family, pause patching and test the underlying invariant with adversarial inputs,
   configuration combinations, and real subprocess behavior.
2. **Separate agents do not guarantee independent judgment.** The local workers
   shared one model. Add a reviewer from a different model family with fresh context
   and a contract-driven test challenger. Require reproducible evidence; benchmark
   reviewers on held-out defects before assuming diversity improves results.
3. **Define the trust boundary before hardening.** Ordinary quality checks and a
   verifier resistant to malicious pull-request code have different requirements.
   Agree which is needed before adding an expanding list of environment defenses.
   Keep acceptance criteria explicit so review cannot silently expand the change.
4. **Prove the supported execution path early.** The Mac capsule limitation was
   known; Linux setup and dependency issues still emerged later. Keep fast native
   checks locally and run the actual supported Linux preflight before promotion.
   Configuration inspection alone cannot establish execution parity.
5. **Spend model calls on changed evidence.** Frequent polling, narration, and
   repeated context accompanied the fix loop. Batch independent findings, use
   deterministic change detection, and re-review affected assumptions. A review
   budget should trigger replanning when exhausted, never an unsupported green check.

## What this means for ChangeCost

A useful change-level cost record should distinguish implementation, validation,
review, rework, and orchestration; retain cached-input, uncached-input, and output
units; and connect usage to commits and outcomes. More tests can be valuable work:
raw token volume alone cannot identify waste.

**Next experiment:** apply the proposed review process to a bounded change and
compare pre-PR defect discovery, review rounds, latency, model calls, token categories,
and billed cost where available. Retain only improvements supported by evidence.

---

**Evidence and limits.** Session `01a0e7d4-21d6-78a0-9c7f-6774999152ca`;
code snapshot `af6be6222d4e1830546286d28e13913ef1d196df`. Usage was summed from
deduplicated per-request records for the parent and six direct workers; raw
transcripts remain local. Line counts compare initial commit `5076104` with the
snapshot. This foundation included substantial custom assurance tooling: one case
does not establish exponential growth, typical feature cost, or future savings.
**Confidence: high** in the recorded measurements; **medium** in the proposed
remedies until tested in a cross-model pilot.
