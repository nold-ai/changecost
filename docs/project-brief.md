# Project brief

Status: **To-Validate**. Recorded from maintainer-provided context on 2026-09-27
(Europe/Berlin). This is a scope boundary, not an implementation plan.

## Confirmed direction

- Name: **ChangeCost**, under `nold-ai/changecost`; repository remains private.
- Standalone project with a possible later, thin SpecFact integration.
- Explore cost estimates and settlement for AI-assisted software changes.
- Keep the first project small and codify quality before writing product code.
- Use Apache-2.0 and OpenSpec; do not start implementation planning in bootstrap.

## Research hypotheses

The supplied report proposes a quote → bind → meter → settle → calibrate loop,
with candidate Change, Run, and Settlement objects. It argues for empirical
cost distributions and explicit attribution of retries and abandoned attempts.
These are design inputs, not approved APIs or evidence that prediction works.

The central question is whether change-level history can produce useful cost
bounds compared with a simple repository-wide baseline. Provider charges, token
usage, credits, and estimated list-price cost should remain distinguishable.

Proposed guardrails are data minimization, honest uncertainty, visible unbound
spend, and independence from provider gateways or observability platforms.
No employee scoring, prompt collection, custom ledger protocol, or ML platform
is needed to bootstrap this investigation.

## Decisions deferred

Language and packaging; supported providers and accessible telemetry; precise
data contracts and storage; command names; estimator and cold-start semantics;
pilot sample size, evaluation criteria, schedule, and enforcement policy.

The report's dates and thresholds are proposals, not a committed roadmap.
Domain ownership is maintainer-reported; no trademark clearance is asserted.

## Evidence risks to carry forward

| Failure mode | Mitigation when planning starts |
| --- | --- |
| Incorrect attribution or duplicate usage | Inspect bindings; preserve ambiguous records; test deduplication and reconciliation. |
| False precision from sparse history | Report sample counts; allow an unpriced state; evaluate held-out calibration against a baseline. |
| Unavailable telemetry or sensitive data exposure | Verify provider access against primary docs; use synthetic fixtures and minimal retention. |

Confidence is high in the recorded repository boundary; prediction feasibility
and provider compatibility remain unverified. See [research provenance](research/README.md).
