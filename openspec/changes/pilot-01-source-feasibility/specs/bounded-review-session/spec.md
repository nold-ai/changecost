## ADDED Requirements

### Requirement: Efficient canonical Git input acquisition

Contributor review-input capture SHALL acquire index flags, tracked stage records
and visible untracked inventory with one Git invocation. It SHALL preserve the
existing schema-8 canonical index bytes, inventory, input digest and clean-state
semantics. This developer-gate repair SHALL NOT change product runtime contracts,
receipt schemas, required analyzers, test selection or enforcement deadlines.

#### Scenario: Historical fingerprint parity

- **GIVEN** unchanged repository contents and declared inputs, including staged/working divergence, executable modes, intent-to-add or conflicting index stages
- **WHEN** the combined inventory is normalized and the input binding is captured
- **THEN** its ordered index bytes, inventory, digest and clean state equal the historical separate-probe capture.

#### Scenario: Untracked names cannot become index metadata

- **GIVEN** visible untracked filenames containing tabs, newlines or stage-looking text, and declared ignored or absent paths
- **WHEN** input acquisition parses Git's NUL-delimited tagged records
- **THEN** untracked tags determine the record category before filename parsing, and all existing inventory and declared-input semantics remain intact.

#### Scenario: Hidden flags remain globally rejected

- **GIVEN** an assume-unchanged or skip-worktree flag on any index entry, including an undeclared path
- **WHEN** review inputs are captured
- **THEN** capture rejects the unsupported flag without silently restoring or changing the user's index.

#### Scenario: Freshness and race guards remain active

- **GIVEN** inputs changing during initialization or refresh, a mismatched HEAD, or dirty declared contents
- **WHEN** the optimized acquisition participates in normal capture
- **THEN** independent HEAD/status checks, all declared fingerprints and both captures during initialization/refresh remain active and reject inconsistent evidence.

#### Scenario: Acquisition stays bounded without weaker assurance

- **GIVEN** a valid stable repository requiring one capture
- **WHEN** capture invokes Git
- **THEN** one combined index/inventory query replaces the three prior queries while HEAD and status verification remain separate, and full current-head native assurance remains required.
