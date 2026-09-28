# Establish the reproducible Python CLI foundation

## Purpose

The repository currently runs documentation hygiene only. A reproducible Python package and explicit development gates are needed before adding any economic behavior.

## ADDED Requirements

### Requirement: Reproducible contributor environment

A contributor SHALL be able to install the declared development environment from a committed lockfile without manual dependency selection.

#### Scenario: Clean checkout

- **GIVEN** a supported Python interpreter and pinned uv
- **WHEN** the documented locked sync and checks run
- **THEN** the lockfile remains unchanged and all required tools resolve from project metadata.

### Requirement: Installable offline CLI

The built package SHALL expose an offline CLI with help and version information and SHALL NOT require SpecFact at runtime.

#### Scenario: Isolated wheel

- **GIVEN** a clean environment without SpecFact
- **WHEN** the built wheel is installed and CLI help/version are invoked
- **THEN** both succeed without network access.

#### Scenario: Unimplemented operation

- **GIVEN** a command not yet delivered
- **WHEN** a user invokes it
- **THEN** it returns a clear non-success result rather than fabricated output.

### Requirement: Truthful quality gates

Contributor and CI gates SHALL execute meaningful lint, format, typing and behavior
tests, review locked dependency licenses/advisories, and report unavailable review
analyzers or advisory data explicitly.

#### Scenario: Deliberate defect

- **GIVEN** a fixture with a known typing or behavior regression
- **WHEN** the applicable gate runs
- **THEN** it fails and identifies the defect.

#### Scenario: Review unavailable

- **GIVEN** a missing required analyzer
- **WHEN** review is requested
- **THEN** the result is incomplete and cannot be presented as a passing review.

#### Scenario: Dependency advisory service unavailable

- **GIVEN** a dependency change whose required advisory audit cannot obtain its data
- **WHEN** the gate runs against the locked dependencies
- **THEN** it reports incomplete evidence rather than claiming zero vulnerabilities or a passing audit.

### Requirement: Consistent local and CI gate execution

The repository SHALL expose the same applicable validator contracts through local
commands, pre-commit and CI, including documentation, metadata and workflow checks.
Complete CI validation SHALL cover PRs to main and pushes to main, including
docs-only changes. Missing comparison history or a missing, failed or skipped
required validator SHALL NOT produce a green aggregate result. CI SHALL NOT
publish/deploy or execute PR code with privileged repository credentials.

#### Scenario: New document omitted from Git tracking

- **GIVEN** an intended new document and unrelated unstaged changes
- **WHEN** the local commit gate checks the intended staged snapshot
- **THEN** it checks the new document and cannot use an unstaged correction to pass content that the commit omits.

#### Scenario: Documentation-only pull request

- **GIVEN** a PR changing only documentation, skill metadata or llms.txt
- **WHEN** CI runs
- **THEN** applicable ownership, consistency, generated-index and metadata gates run with the same validator semantics as local checks.

#### Scenario: Incomplete gate or comparison base

- **GIVEN** a required validator that fails or is skipped, or an unresolved required comparison SHA
- **WHEN** the aggregate check completes
- **THEN** it reports failure/incomplete evidence and names the missing check or base rather than treating it as no changes.

#### Scenario: Invalid workflow definition

- **GIVEN** a workflow fixture with an invalid job or expression reference
- **WHEN** the pinned workflow syntax validator runs locally and in CI
- **THEN** both reject the defect before any deployment or privileged PR execution.

### Requirement: Documentation ownership and source consistency

Maintained documentation SHALL have explicit repository-local owner and source
mappings with validated coverage, links and anchors. A source change SHALL require
corresponding documentation maintenance or a reviewed no-doc-change rationale bound
to the affected source contents. Exemptions SHALL be path-specific and justified;
the original research exports SHALL remain byte-identical. Dates alone SHALL NOT
establish freshness, and automated structural checks SHALL NOT be represented as
proof of arbitrary prose accuracy.

#### Scenario: Unowned or orphaned documentation

- **GIVEN** a new maintained page without an ownership record, or a record whose source no longer exists
- **WHEN** documentation validation runs
- **THEN** it fails with the affected page/source and the required mapping correction.

#### Scenario: Stale documentation decision

- **GIVEN** a source change with neither maintained documentation nor a content-matching no-doc-change rationale
- **WHEN** consistency validation runs
- **THEN** it fails even if a last-reviewed date was updated or an exception exists for older source contents.

#### Scenario: Valid provenance exception

- **GIVEN** an explicitly exempt immutable research export and maintained documentation with valid mappings and internal references
- **WHEN** documentation validation runs
- **THEN** it accepts the justified exception without rewriting the research bytes and continues validating the maintained documents.

#### Scenario: Broken internal reference

- **GIVEN** a maintained page linking to a removed page or nonexistent anchor
- **WHEN** documentation validation runs
- **THEN** it fails and identifies the referring document and invalid target.

### Requirement: Deterministic agent and command index integrity

llms.txt and generated command references SHALL match canonical local skill,
documentation and implemented CLI metadata. Generation SHALL be deterministic and
offline; a read-only check SHALL detect missing, stale, duplicate or dangling
entries without repairing them silently. The normal test/CI gate SHALL execute
the integrity check even when a contributor bypasses pre-commit. Planned commands
SHALL NOT be presented as implemented commands.

#### Scenario: Command or skill changed without regeneration

- **GIVEN** an added/renamed skill or changed implemented CLI option with unchanged generated output
- **WHEN** the integrity check runs
- **THEN** it fails with a regeneration diagnostic; regeneration and a subsequent check pass against the current inventory.

#### Scenario: Index tampering or missing output

- **GIVEN** a generated file that is missing or contains a duplicate, dangling entry or unsupported command
- **WHEN** normal tests and CI run
- **THEN** the check fails even if the pre-commit hook did not run.

#### Scenario: Repeat offline generation

- **GIVEN** unchanged local canonical inputs and no provider credentials, network or sibling checkout
- **WHEN** generation runs twice in the installed development environment
- **THEN** both outputs are byte-identical and contain only verified implemented command surfaces plus explicitly labeled planning references.

### Requirement: Changelog and version coherence

Meaningful behavior, contract or contributor-workflow changes SHALL carry a new
Unreleased changelog entry relative to an explicit comparison base, unless a
narrow reviewed exception is bound to the current change contents. Package,
installed CLI, build and lockfile version metadata SHALL agree with the canonical
project version; versions SHALL NOT decrease. Routine unreleased planning/docs
changes SHALL NOT require a version bump, release tag or network/PyPI lookup.

#### Scenario: Missing new changelog evidence

- **GIVEN** a meaningful change whose changelog is unchanged from the comparison base and has no valid scoped exception
- **WHEN** metadata validation runs
- **THEN** it fails; an old Unreleased entry, date-only touch or exception for different contents cannot satisfy the check.

#### Scenario: Conflicting versions

- **GIVEN** a package, CLI, built artifact or lockfile version inconsistent with the canonical project version, or a decrease from the base version
- **WHEN** version validation runs
- **THEN** it fails and identifies the conflicting source without consulting PyPI.

#### Scenario: Unreleased change without a bump

- **GIVEN** a consistent unchanged unreleased package version and a new changelog entry or valid narrow editorial exception
- **WHEN** validation runs for a planning/docs change
- **THEN** it passes without demanding a release number, tag or publication.

#### Scenario: First package version

- **GIVEN** a base with no package version and a newly introduced consistent initial version
- **WHEN** version validation runs
- **THEN** it accepts the initial metadata and changelog record without inventing a previous release.
