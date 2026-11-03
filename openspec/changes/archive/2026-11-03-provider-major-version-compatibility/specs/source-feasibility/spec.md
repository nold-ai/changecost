## MODIFIED Requirements

### Requirement: Canonical profile register and honest approval

The closeout SHALL maintain versioned per-surface profiles with acquisition routes,
versions/tier, dated citations, opaque evidence identity/hash, capability dispositions,
verified field meanings and exact unresolved evidence. A deterministic compact
matrix SHALL derive from the register. Validation SHALL NOT infer approval from
synthetic, producer-reported or documentation-only evidence. Approved capabilities
SHALL reference inspected native evidence and a named independent semantic review;
structural inspection alone SHALL NOT establish accounting finality or completeness.
The semantic attestation SHALL bind the exact profile/version/capability and evidence
SHA-256, with explicit authority, interval, replay/reset/correction and exclusion
decisions. This contributor attestation is not independent authentication of facts.
Its dispositions describe reviewed source evidence; they do not extend the runtime's
synthetic-only accounting/coverage policy or grant local computation authority.
Provider policy and historical replay changes belong to later separately authorized
adapter work, not this source-feasibility closeout.

#### Scenario: Stale matrix or fabricated approval

- **GIVEN** a changed profile with an unchanged matrix, or approval citing synthetic evidence
- **WHEN** the research checker runs
- **THEN** it rejects the stale matrix or unsupported approval with safe diagnostics.

#### Scenario: Useful partial delivery without native evidence

- **GIVEN** passing tooling tests but missing intended Copilot/Cursor native source evidence
- **WHEN** approval and capability-based closeout are assessed
- **THEN** affected profile approvals stay incomplete with exact gaps; #9 can complete only after the capability inventory and reconciliation are independently reviewed, not from tooling success alone.

#### Scenario: Immutable baseline and separate compatibility decision

- **GIVEN** the maintainer-authorized 2026-10-31 major compatibility policy
- **WHEN** the selected operation runs
- **THEN** exact native baseline approvals and packaged envelopes remain immutable; runtime same-major compatibility creates no new observed-release proof, profile or billing/demand/calibration authority; future unimplemented Copilot/Cursor readers plan major-only compatibility subject to independent grammar approval
