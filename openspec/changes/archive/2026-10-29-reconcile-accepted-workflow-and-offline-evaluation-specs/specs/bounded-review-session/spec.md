# Accepted risk-first workflow guidance

## ADDED Requirements

### Requirement: Critical safety assumptions receive early observable proof

Before dependent implementation of a nontrivial behavior change, the contributor workflow SHALL select one or two existing-system safety assumptions most likely to invalidate the chosen approach. It SHALL identify affected obligations, observable checks, expected results, actual evidence and exclusions in existing planning/evidence artifacts. Proof SHALL exercise the relevant existing CLI, API or dependency boundary with the smallest sufficient safe probe. A disproved or unverified critical assumption SHALL prevent the dependent decision being represented as safe; unaffected authorized work may continue. Expected failing tests for newly proposed behavior SHALL remain separate from failures of existing safety assumptions. Documentation-only scope SHALL retain an applicability rationale rather than inventing runtime probes.

#### Scenario: Routine bounded behavior change
- **GIVEN** a narrow change with a known caller and unchanged trust boundary
- **WHEN** preparation selects its critical safety assumption
- **THEN** the workflow records a relevant observed boundary check and its limits for the existing upfront independent review
- **AND** no additional reviewer or competing implementation is required solely by this checkpoint.

#### Scenario: Existing assumption is disproved
- **GIVEN** an approach that depends on an existing interface preserving a named invariant
- **WHEN** the probe contradicts that invariant
- **THEN** the dependent approach is revised or explicitly replanned before implementation
- **AND** the contrary evidence remains recorded rather than being described as passing proof.

#### Scenario: Probe cannot run on the available controller
- **WHEN** a selected critical check is unavailable or inconclusive
- **THEN** the workflow names the missing evidence and supported next check without marking the assumption proven
- **AND** a successful proxy command or configuration read cannot substitute for execution evidence.

#### Scenario: Expected new-behavior failure and documentation applicability
- **WHEN** a spec-derived test fails because proposed behavior is not implemented
- **THEN** it remains valid TDD evidence rather than a disproved existing-system assumption
- **AND** documentation-only changes record why a runtime safety probe does not apply.

### Requirement: Existing review slots consume a compact execution checkpoint

The workflow SHALL place the selected assumptions, proof references, affected obligations and exclusions in the existing upfront independent review. Its execution checkpoint SHALL identify blocking work, the sole writer and any independent read-only work that can proceed safely. Follow-up handoffs SHALL contain the current comparison/head/input binding, actual delta, affected assumptions, unresolved findings and necessary evidence references. Unknown dependencies or changed scope, entrypoints or trust boundaries SHALL require the existing broader review path. This checkpoint SHALL NOT create another review lane, mandatory design competition, receipt schema or authoritative ledger.

#### Scenario: Mapped correction has a stable baseline
- **GIVEN** a reviewed same-change baseline and a correction confined to covered dependencies
- **WHEN** the next review starts
- **THEN** its handoff contains the affected delta and assumptions with current evidence
- **AND** required final gate and provider coverage remains unchanged.

#### Scenario: Correction introduces an unknown boundary
- **WHEN** a correction adds an entrypoint or unmapped dependency
- **THEN** the coordinator renews the affected scope/obligation review before claiming narrow closure
- **AND** earlier unrelated findings and budget history are preserved.

### Requirement: Finding triage distinguishes defects from preferences using evidence

Each actionable finding SHALL identify the violated accepted obligation, reachable failure path and supporting reproduction, regression or inspected-path evidence. The coordinator SHALL deduplicate reports without erasing distinct defects or their source identities. Preferences and speculative concerns SHALL receive reasoned dispositions; credible but unverified defects SHALL remain unresolved pending evidence. Confirmed defects SHALL remain blocking until verified fixed or explicitly dispositioned under existing exception policy. Reviewer agreement, disagreement, severity labels or implementation inconvenience SHALL NOT alone establish or dismiss a defect. Existing authoritative finding dispositions SHALL remain unchanged.

#### Scenario: Confirmed defect is reported by one reviewer
- **WHEN** one reviewer demonstrates a reachable violation of an accepted requirement
- **THEN** the finding remains actionable regardless of another reviewer's silence or disagreement.

#### Scenario: Preference has no demonstrated violation
- **WHEN** a report proposes an alternative style or abstraction without a violated obligation or concrete failure
- **THEN** the coordinator records its rationale and nonblocking preference disposition without changing code solely to quiet the reviewer.

#### Scenario: Credible evidence remains incomplete
- **WHEN** a security, persistence or assurance concern cannot yet be verified or disproved
- **THEN** the concern remains unresolved and its smallest evidence-gathering step is named
- **AND** lack of a runnable reproduction alone does not dismiss it.

### Requirement: Risk-first execution preserves all existing completion controls

The contributor workflow SHALL preserve its mechanical gates, supported-Linux/Python assurance, independent upfront review, affected-scope closure, Codex default and risk-triggered CodeRabbit. Critical-assumption proof and compact handoffs SHALL supplement those controls rather than certify completion. One writer SHALL collect compatible confirmed fixes into the existing correction batches; batches, measured review time and family investigation/replanning history SHALL NOT reset. Required stale, missing, failed or unavailable evidence SHALL remain incomplete.

#### Scenario: Assurance or persistence scope requires both providers
- **WHEN** scope changes security/trust boundaries, persistence/data-loss behavior or assurance/gate policy, or contains contradictory evidence
- **THEN** both Codex and CodeRabbit remain required by the existing risk policy
- **AND** an early proof cannot waive their current-head completion or mandatory checks.

#### Scenario: Budget or current-input evidence is exhausted
- **WHEN** review allowance is exhausted or evaluated inputs change
- **THEN** existing replan/recovery and evidence-invalidation rules apply
- **AND** a compact checkpoint does not grant another allowance or relabel old evidence as current.
