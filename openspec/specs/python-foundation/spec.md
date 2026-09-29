# python-foundation Specification

## Purpose
Provide a reproducible standalone Python package and explicit repository quality gates before adding economic behavior or provider integrations.

## Requirements

### Requirement: Reproducible contributor environment

A contributor SHALL be able to install the declared development environment from
a committed lockfile without manual dependency selection. Verification SHALL reject
missing or stale locks without updating them. Build dependencies SHALL have explicit
version/hash constraints derived from the same project dependency authority.

#### Scenario: Clean checkout

- **GIVEN** a supported Python interpreter and pinned uv
- **WHEN** the documented locked sync and checks run
- **THEN** the lockfile remains unchanged and all required tools resolve from project metadata.

#### Scenario: Missing or stale lock

- **GIVEN** an absent lockfile or dependency metadata incompatible with the committed lock
- **WHEN** a documented verification command runs
- **THEN** it fails with a lock diagnostic without creating or changing the lock.

#### Scenario: Build dependency drift

- **GIVEN** an isolated build whose resolved build dependency differs from its declared version/hash constraint
- **WHEN** the build gate runs
- **THEN** it rejects the mismatch; a build using the constrained dependencies succeeds without modifying dependency authority.

### Requirement: Installable offline CLI

The built package SHALL expose an offline CLI with help and version information
and SHALL NOT require SpecFact at runtime. Help, version and invalid invocation
SHALL leave working and user data directories unchanged. Distributions SHALL
exclude private evidence, credentials and local review/runtime output.

#### Scenario: Isolated wheel

- **GIVEN** a wheel built from the sdist and installed with declared runtime dependencies into a clean environment without SpecFact or source-checkout imports
- **WHEN** its installed CLI is invoked with --help and --version from outside the checkout while network access is blocked
- **THEN** both exit zero, the version matches installed metadata and no working-directory or user-data files are created; dependency installation is a separate setup step.

#### Scenario: Unimplemented operation

- **GIVEN** a command not yet delivered
- **WHEN** a user invokes it
- **THEN** it returns a clear non-success result rather than fabricated output.

#### Scenario: Bare invocation

- **GIVEN** the installed foundation CLI
- **WHEN** it is invoked without arguments
- **THEN** it displays usage and exits nonzero without creating configuration, database or evidence files.

#### Scenario: Private files near build inputs

- **GIVEN** synthetic credential and private-evidence sentinels in local-only repository directories
- **WHEN** wheel and sdist contents are inspected
- **THEN** neither contains the sentinels, both retain required metadata/license files, and the sdist can build without the original checkout.

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

#### Scenario: Complete native review with nonblocking advisories

- **GIVEN** full native review returns `PASS_WITH_ADVISORY`, assurance PASS, no unknown evidence, exit code zero and all required analyzers ran with PASS evidence
- **WHEN** the repository validates the content-bound report
- **THEN** it accepts this native success verdict while retaining the advisories for review; failed, missing, unknown or stale evidence still fails. The promotion review records a scoped disposition for each finding before declaring its review loop complete.

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

#### Scenario: Staged document with an unstaged correction

- **GIVEN** a staged new document with a broken reference and a correction only in the working tree
- **WHEN** the local commit gate checks the complete index snapshot
- **THEN** it rejects the staged defect without altering the index or working tree; staging the correction allows the repaired snapshot to pass.

#### Scenario: Referenced document not staged

- **GIVEN** a staged reference to a new document present only as an untracked working-tree file
- **WHEN** the local commit gate runs
- **THEN** it fails because the target is absent from the commit snapshot; the working-tree preview cannot substitute for this check.

#### Scenario: Documentation-only pull request

- **GIVEN** a PR changing only documentation, skill metadata or llms.txt
- **WHEN** CI runs
- **THEN** applicable ownership, consistency, generated-index and metadata gates run with the same validator semantics as local checks.

#### Scenario: Incomplete gate or comparison base

- **GIVEN** a required validator that fails or is skipped, or an unresolved required comparison SHA
- **WHEN** the aggregate check completes
- **THEN** it reports failure/incomplete evidence and names the missing check or base rather than treating it as no changes.

#### Scenario: Behavior review required by aggregate

- **GIVEN** changed source, tests, dependency/build configuration, validators or CI wiring
- **WHEN** the complete aggregate runs with missing or stale required review evidence
- **THEN** it is incomplete/non-success even if a manual review hook was skipped; a docs-only applicability decision remains explicit and still runs the documentation gates.

#### Scenario: Make test uses the shared required test gate

- **GIVEN** inherited pytest selection options or an alternate root configuration that would hide a failing test
- **WHEN** `make test` runs
- **THEN** it invokes the same canonical tests leaf as the aggregate, fails for that required test and passes after repair
- **AND** this non-diff target defaults its inventory baseline to HEAD while honoring explicit BASE_REF and MANIFEST; aggregate comparison requirements and direct developer pytest filtering remain unchanged.

#### Scenario: The required suite uses canonical pytest configuration

- **GIVEN** an alternate root pytest configuration that selects only a passing subset
- **WHEN** the required tests leaf invokes pytest
- **THEN** it explicitly loads `pyproject.toml`, detects a failing required test despite the alternate configuration, and passes after the test is repaired
- **AND** a changed root `conftest.py` remains a behavior input requiring full review because explicit configuration does not disable Python collection hooks; unchanged hook content alone does not trigger review.

#### Scenario: Inherited pytest options cannot narrow the required suite

- **GIVEN** the required tests leaf inherits PYTEST_ADDOPTS from a local or CI environment
- **WHEN** it starts the repository's pytest subprocess
- **THEN** it removes that variable from a copy of the child environment so inherited filename or selection options cannot omit required tests
- **AND** unrelated environment values, repository pytest configuration, other gate subprocesses and the caller's environment remain unchanged; ordinary failing tests still fail the gate and repaired tests pass.

#### Scenario: Host-side external lock proof remains required

- **GIVEN** a review capsule whose attached interpreter cannot accept the isolation flag used by uv's interpreter probe
- **WHEN** local, staged-hook or CI lock validation runs
- **THEN** the ordinary host executes both the project lock check and the real offline missing/stale/repaired fixture, and either failure fails the gate; capsule unit tests check failure propagation without weakening runtime protection or skipping the proof. The stale fixture SHALL use offline-resolvable metadata drift, prove unchanged lock bytes on check failure, and prove that ordinary locking updates the lock successfully before a subsequent check passes.

#### Scenario: Project environment shadows an external validator

- **GIVEN** PATH resolves SpecFact, actionlint or OpenSpec to the repository or active project environment, including through a symlink
- **WHEN** the gate invokes that external validator
- **THEN** it rejects the collision explicitly instead of executing it or silently falling through to another executable; a resolved external installation is invoked by absolute path. This prevents accidental tool-role collisions and is not malicious-PR attestation.

#### Scenario: Manual CI comparison cannot use the tested head

- **GIVEN** a manual workflow dispatch with an explicit comparison reference
- **WHEN** the resolved comparison SHA equals the expected tested head
- **THEN** resolution fails before exporting BASE_REF rather than creating an empty comparison interval
- **AND** a distinct resolved manual base remains valid; this restriction does not change PR merge-base, push-before or local staged-HEAD semantics.

#### Scenario: Manual comparison evidence retains its declared scope

- **GIVEN** an operator-selected distinct manual comparison base
- **WHEN** that interval contains no behavior changes, including an identical-tree or docs-only interval
- **THEN** changed-input applicability may report behavior gates as not applicable; this is scoped comparison evidence, not full ten-analyzer assurance
- **AND** it cannot replace behavior evidence required by the actual PR/promotion interval; manual selection does not establish a trusted-main baseline.

#### Scenario: CI comparison base override

- **GIVEN** a workflow that replaces the reviewed event-based resolver, changes its inputs/order, or overrides BASE_REF at another workflow/job/step scope
- **WHEN** workflow validation runs
- **THEN** it rejects the changed comparison wiring instead of allowing empty-diff applicability to hide required gates; the ordinary staged-hook HEAD default remains valid.

#### Scenario: Checkout targets the actual event head

- **GIVEN** a pull request, push or manual workflow event with an expected head commit
- **WHEN** the checked-out HEAD differs from that event head or the reviewed checkout wiring is changed
- **THEN** verification fails before resolving the comparison base; the canonical checkout remains unique, unconditional, first, pinned, with full history and no persisted credentials.

#### Scenario: Python matrix labels select their actual interpreters

- **GIVEN** the required Python matrix entries
- **WHEN** the matrix mapping differs from the exact two-version Python mapping, the quality job lacks its canonical `UV_PYTHON` binding, or any run step lacks that same binding
- **THEN** workflow validation fails instead of accepting altered matrix expansion or inherited interpreter selection
- **AND** every run step explicitly binds `${{ matrix.python }}` so step environment precedence supersedes earlier GITHUB_ENV values; action steps may omit the variable or use the exact binding, but may not substitute another value. Unsupported include/exclude entries and extra axes require gate reconciliation.

#### Scenario: Quality Bash startup does not inherit environment hooks

- **GIVEN** the ordinary-user Ubuntu quality job
- **WHEN** a run step starts with inherited Bash startup variables or exported shell functions, regardless of their environment source
- **THEN** its canonical shell template is `/bin/bash --noprofile --norc -p -e -o pipefail {0}`, retaining fail-fast behavior and ignoring inherited Bash startup configuration
- **AND** workflow validation rejects altered templates in defaults or explicit run-step overrides; this grants no new operating-system privilege and does not authenticate child interpreters, host tools or outputs.

#### Scenario: Quality steps retain their reviewed execution context

- **GIVEN** the quality job declares Bash and the repository root as its run defaults
- **WHEN** workflow/job defaults or any run-step override changes the shell or working directory
- **THEN** workflow validation rejects the unreviewed execution context, even if the aggregate command text is unchanged
- **AND** absent workflow defaults and inherited or identical step settings remain valid; the explicit quality-job defaults are required.

#### Scenario: CI aggregate launcher selection is explicit

- **GIVEN** the pinned Ubuntu quality job
- **WHEN** a workflow, quality job or quality step directly sets PATH, or the aggregate replaces the canonical `/usr/bin/env` and `/usr/bin/make` paths
- **THEN** workflow validation rejects the configuration; the canonical aggregate retains Make-flag clearing and normal tool installation through GITHUB_PATH
- **AND** these checks constrain launcher selection, not the authenticity of a mutable host or its output.

#### Scenario: Inherited Make flags cannot hide aggregate failures

- **GIVEN** Make flag variables are inherited from the workflow, job, step or runner environment
- **WHEN** CI invokes the required aggregate
- **THEN** its canonical command clears `MAKEFLAGS`, `GNUMAKEFLAGS` and `MFLAGS` before `make check`, so an ignore-errors option cannot turn a failing recipe into success
- **AND** workflow validation rejects aggregate commands that remove this protection; ordinary aggregate success still passes.

#### Scenario: Sibling workflows retain shared security policy

- **GIVEN** an additional `.yml` or `.yaml` workflow alongside the required quality workflow
- **WHEN** it declares broader or missing root permissions, a broader job override, or `pull_request_target`
- **THEN** workflow validation fails even if its syntax is valid
- **AND** a read-only sibling with inherited or identical job permissions passes shared security validation without requiring the quality workflow's matrix, checkout or comparison resolver.

#### Scenario: Any workflow job overrides repository read-only permissions

- **GIVEN** the workflow declares only `contents: read` at its root
- **WHEN** any job, including a sibling of the quality job, overrides permissions with write access or another unreviewed permission set
- **THEN** workflow validation fails
- **AND** an absent job override or an explicit identical `contents: read` override passes this contract.

#### Scenario: Ordinary commit without a comparison override

- **GIVEN** a repository with a valid HEAD and a staged change, with BASE_REF unset
- **WHEN** the installed commit hook validates its index snapshot
- **THEN** it compares that snapshot to HEAD and propagates validator failures; an explicit comparison override remains authoritative and ordinary CI commands still require their declared base.

#### Scenario: Marker-split license evidence

- **GIVEN** a lock containing multiple versions of the same registry package for different environments
- **WHEN** license evidence is collected
- **THEN** installed metadata is used only for its exact locked version, other locked versions use exact-release metadata, and an installed version absent from all locked alternatives remains an error.

#### Scenario: Reviewable gate failure paths

- **GIVEN** missing license metadata, contradictory package metadata, failed external checks or invalid contributor arguments
- **WHEN** their repository validators run
- **THEN** they return explicit failing diagnostics, with offline unit evidence for their failure paths and full coverage review remaining enforced.

#### Scenario: Pinned workflow validator distribution

- **GIVEN** actionlint 1.7.12 installed as a release binary or through its Go module
- **WHEN** the workflow validator checks the installed version
- **THEN** it accepts exactly `1.7.12` and `v1.7.12`, rejects missing, malformed or different versions, and still runs workflow syntax validation.

#### Scenario: OpenSpec configuration changes require review

- **GIVEN** a change only to `openspec/config.yaml`
- **WHEN** review applicability is evaluated
- **THEN** full required review runs and incomplete review evidence fails; unchanged configuration alone does not trigger review.

#### Scenario: Option-shaped root filenames cannot bypass hygiene

- **GIVEN** a current repository input whose root-relative path begins with `-`, including after normalizing a `./` prefix
- **WHEN** the working inventory, staged snapshot or hygiene leaf accepts its file list
- **THEN** it fails with a filename diagnostic before invoking hooks; such root filenames must be renamed because pre-commit and individual hooks may parse them as options
- **AND** deleting the unsupported input is allowed, while nested names such as `fixtures/--help` and root names such as `.--help` remain valid.

#### Scenario: Hygiene policy changes require review

- **GIVEN** a change only to the shared pre-commit hygiene configuration
- **WHEN** review applicability is evaluated
- **THEN** full required review runs even when the changed hygiene policy itself passes.

#### Scenario: Invalid intended-file manifest

- **GIVEN** an intended-file manifest naming a missing file or a directory
- **WHEN** working-tree inputs are inventoried
- **THEN** the gate rejects the invalid entry by name rather than silently omitting it; unrelated untracked files may remain intentionally excluded by a valid manifest.

#### Scenario: Restricted Linux capsule host

- **GIVEN** an Ubuntu 24.04 runner with AppArmor user-namespace restrictions
- **WHEN** CI prepares its signed review capsule
- **THEN** only the job-local cached launcher receives the required AppArmor userns permission, global restrictions remain enabled, and installation and full review execute as the ordinary runner user; setup failures remain failures.

#### Scenario: Comparison covers the tested contents

- **GIVEN** a PR head or a main push containing multiple commits
- **WHEN** change-sensitive validators run
- **THEN** they record the actual tested head and resolved comparison base, cover the complete change interval and reject unavailable history rather than silently comparing only the last commit.

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
