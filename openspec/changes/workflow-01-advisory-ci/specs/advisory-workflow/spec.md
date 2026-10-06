# Advisory CLI checks and GitHub summaries

## Purpose

Complete operation-appropriate presentation and truthful read-only budget advice
using delivered contracts, with a safe optional CI summary. Provider approval and
calibration remain separate.

## ADDED Requirements

### Requirement: Stable human and JSON output

The CLI SHALL expose quote, bind, settle, check and explain with operation-appropriate JSON and opt-in human presentation through global --format json|human, defaulting to JSON. Existing successful JSON payloads and portable schemas SHALL remain unchanged; only new check and structured error results SHALL receive new internal version tags. Human output SHALL preserve the same values, scope, provenance and uncertainty while escaping terminal controls.

#### Scenario: Existing success payload remains stable

- **GIVEN** an existing bind, quote, settle or explain operation
- **WHEN** it completes in default or explicit JSON mode
- **THEN** stdout contains its existing parseable payload without a universal wrapper or added economic fields, and persistence/idempotency are unchanged.

#### Scenario: Human presentation carries uncertainty

- **GIVEN** a priced or unpriced Quote, incomplete Settlement or registration result
- **WHEN** the same operation runs with global --format human
- **THEN** stdout renders a readable operation-appropriate result with the same available values and uncertainty; embedded terminal controls remain data.

#### Scenario: New check machine output

- **GIVEN** a successful check request in JSON mode
- **WHEN** evaluation completes
- **THEN** stdout is one versioned result naming the selected record, budget/economic identity, scope/cutoff, provenance/completeness, applicable sample count, claimed versus verified comparison value and reasons.

### Requirement: Safe technical errors and offline invocation

The CLI SHALL distinguish technical failure from valid unknown advice. Invalid arguments/modes, malformed or unsupported portable schemas, unavailable stores/artifacts and missing or invalid record selection SHALL exit 2. JSON mode SHALL emit one versioned safe error with a stable code/message on stderr and no success stdout, including argument-parsing failures. Human mode SHALL emit safe diagnostics on stderr. Help/version SHALL retain text/offline exit-zero behavior; invalid invocation SHALL NOT create stores or expose rejected values, private paths, SQL or tracebacks.

#### Scenario: Malformed artifact

- **GIVEN** a malformed local bundle containing private rejected values
- **WHEN** check evaluates it
- **THEN** exit is 2, JSON stderr contains a safe structured error, stdout is empty and neither payload values nor traceback are emitted.

#### Scenario: Parser failure

- **GIVEN** a missing required argument, invalid option or invalid format value
- **WHEN** the CLI parses the request
- **THEN** exit is 2 with a safe stderr-only error; JSON is the fallback for an invalid format, and no store is created.

#### Scenario: Unavailable store or artifact

- **GIVEN** a missing or inaccessible requested input
- **WHEN** check runs
- **THEN** the input is not created, exit is 2, and no successful or unknown advisory result masks the technical failure.

#### Scenario: Offline help and version

- **GIVEN** no local store or network
- **WHEN** help or version runs
- **THEN** the existing text response succeeds with exit zero and creates no evidence/store; bare or unknown commands fail safely.

### Requirement: Reachable fresh-store regression workflow

The workflow SHALL reuse delivered bind registration/mapping, quote, settle normalized import/computation and explicit outcomes, then add check/explain and both presentation modes. Controlled synthetic normalized/portable coverage fixtures SHALL remain clearly synthetic. This capability SHALL NOT introduce a provider parser or coverage-authoring API, require handwritten database rows, or reinterpret delivered registration/outcome operations as unimplemented.

#### Scenario: First change from registration to advice

- **GIVEN** an empty store and named controlled synthetic fixtures
- **WHEN** the caller registers/quotes a Change, registers/binds a Run, imports/maps evidence, declares outcomes, computes a Settlement and uses check/explain
- **THEN** cold-start quoting is valid unpriced, existing provenance/retry semantics remain intact, and new advice/presentation are reachable through the five command families.

#### Scenario: Retry and abandoned history remains visible

- **GIVEN** a failed attempt followed by a retry or abandoned Change
- **WHEN** the documented workflow runs
- **THEN** existing explicit outcomes and economic history are retained; presentation and advice do not erase retry or abandoned expenditure.

### Requirement: Explicit read-only record and budget selection

Check SHALL require an explicit quote, computed_settlement or legacy settlement kind and record ID, selecting from one read-only local-store snapshot or a strictly validated changecost/v1 bundle supplied through --artifact. Artifact mode SHALL NOT import or open/create a database. Check SHALL NOT select latest revisions implicitly, combine records, write records/receipts/revisions/observations or establish authority from artifact contents. Budget SHALL be a finite nonnegative Decimal string with explicit kind/unit/basis and monetary currency, using the existing economic identity rules. Quote quantile selection SHALL default to p90 and permit p50; an explicit Settlement quantile SHALL be invalid.

#### Scenario: Selected immutable revision

- **GIVEN** multiple Settlement revisions exist
- **WHEN** check selects one explicit record ID
- **THEN** only that historical revision and its declared scope are evaluated, without silently selecting newer records or writing state.

#### Scenario: Artifact evaluation bypasses database

- **GIVEN** a valid portable bundle and a nonexistent global database path
- **WHEN** check uses --artifact and a valid record selector
- **THEN** the record is inspected as a producer claim, advice is unknown, and the database path is neither opened nor created.

#### Scenario: Invalid selector and budget

- **GIVEN** a missing/other-kind record, explicit Settlement quantile, negative/nonfinite/malformed budget or invalid economic identity
- **WHEN** check validates the request
- **THEN** exit is 2 with safe technical diagnostics and no store creation or writes.

#### Scenario: Exact Decimal equality and zero

- **GIVEN** a verified complete compatible value of 0.1 or observed 0 and an equal valid budget
- **WHEN** check compares values
- **THEN** status is within_budget using exact Decimal comparison, without float conversion, currency conversion or rounding.

#### Scenario: Explicit quote quantile

- **GIVEN** a verified priced Quote with p50 10 and p90 18 USD billed, against 15 USD billed
- **WHEN** check runs with no quantile and then explicit p50
- **THEN** the default is over_budget and p50 is within_budget; each result states the selected quantile and exits zero.

### Requirement: Verified historical authority before numeric advice

Numeric advice SHALL require a supported valid local typed computation receipt and reproduction of the selected immutable result at its original store-local cutoff. Quote validation SHALL retain the delivered historical replay boundary. Computed Settlement validation SHALL reproduce values, requested-scope completeness and supporting inputs/exclusions/reasons through the existing reconciliation evaluator; receipt or input availability alone SHALL NOT suffice. Legacy, imported/artifact-only, unsupported, future/foreign-cutoff, missing-input or result-mismatch claims SHALL return unknown with declared values/provenance and no verified comparison value. Saved/imported completeness and receipt-like fields SHALL NOT create authority. Later evidence SHALL NOT change evaluation of the selected historical result.

The selected cutoff time SHALL NOT exceed the latest committed local metadata timestamp, even when it precedes an advanced wall clock and its sequence/store identity remain valid. Equality and earlier historical cutoffs SHALL remain eligible for reproduction. Quote and computed Settlement inspection SHALL apply the same committed timestamp authority boundary; unavailable timestamps SHALL NOT grant replay eligibility. A populated local store with no committed metadata timestamp SHALL be an invalid store for check and return the controlled technical error without writes.

Supported local producers SHALL anchor the original cutoff to the selected result's own availability: cutoff sequence equals its insertion sequence minus one, and cutoff time equals its availability time. The receipt, supported version and replay checks SHALL retain this anchor in advisory check and both historical inspectors, even after unrelated later history advances local metadata. No new receipt or persisted budget schema is required.

#### Scenario: Mutated result cutoff cannot acquire historical authority

- **GIVEN** a receipted local result has its cutoff altered to its own insertion, later unrelated history, an earlier equivalent snapshot, or another committed time
- **WHEN** check or either historical inspector evaluates it
- **THEN** it has no numeric advice or replay eligibility, while the unchanged original remains eligible after later history; reads leave the store unchanged.

#### Scenario: Corrupt selected result availability is a safe technical failure

- **GIVEN** selected local computation availability has a noninteger or nonpositive sequence, or an invalid timestamp
- **WHEN** check or explain validates that original-cutoff anchor in human or JSON mode
- **THEN** it exits 2 with empty stdout and a safe stderr diagnostic, without exposing the corrupt value or traceback or writing the store.

#### Scenario: Advanced wall clock cannot authorize a future committed cutoff time

- **GIVEN** a locally receipted Quote or computed Settlement claims a cutoff later than the latest committed store timestamp but earlier than the current wall clock
- **WHEN** check or explain inspects that selected record
- **THEN** check returns unknown with declared values and no verified comparison; explain returns replay_unavailable and Quote economic validation is not_computed; valid advisory/inspection responses exit zero without writes.

#### Scenario: Equality and older committed cutoffs remain historical

- **GIVEN** a locally receipted reproducible record has a cutoff equal to the latest committed timestamp or earlier than later committed history
- **WHEN** check or explain selects that original record
- **THEN** the original historical result retains numeric advice and replay eligibility without substituting current history.

#### Scenario: Missing committed timestamp is not authority

- **GIVEN** a populated local store has selected records but its committed metadata timestamp is absent, even if its metadata sequence is corrupted to zero or its receipt is absent
- **WHEN** check or explain inspects the record
- **THEN** check returns a controlled technical error with empty stdout and exit two; explain cannot certify replay eligibility; neither operation changes the store.

#### Scenario: Priced imported Quote remains a claim

- **GIVEN** a well-formed imported priced Quote declares 18 USD against budget 15 but lacks supported local verification
- **WHEN** check runs
- **THEN** status is unknown with declared amount/provenance, not over_budget, and exit is zero.

#### Scenario: Forged imported completeness

- **GIVEN** an imported legacy or computed Settlement declares a complete total with receipt-like portable fields
- **WHEN** check runs
- **THEN** status is unknown with producer-assertion provenance; supplied flags cannot establish local authority.

#### Scenario: Receipt availability is insufficient

- **GIVEN** a local Settlement has a receipt and available inputs but stored material values/completeness differ from historical reproduction
- **WHEN** check runs
- **THEN** status is unknown with mismatch reason and no verified comparison value, without changing the stored result.

#### Scenario: Unavailable or unsupported replay

- **GIVEN** an otherwise well-formed computation has a foreign/future cutoff, missing historical inputs or unsupported computation version
- **WHEN** check runs
- **THEN** advice is unknown with the applicable reason; no current-history fallback or result rewrite occurs.

#### Scenario: Later correction preserves historical advice

- **GIVEN** a verified historical computation is followed by a new import or correction
- **WHEN** check selects the same original record
- **THEN** it reproduces at the original cutoff and preserves the original advice; newer evidence is not leaked into that result.

#### Scenario: Narrow scope retains existing completeness policy

- **GIVEN** a reproduced Settlement uses a narrowed interval and the existing evaluator retains partial_change_scope
- **WHEN** check compares its declared scope to a compatible budget
- **THEN** advice is unknown with that scope/subtotal and reason; check does not filter reasons, certify narrower completeness or introduce a new coverage policy.

#### Scenario: Check never alters durable evidence

- **GIVEN** a local store with successful Quote/Settlement operation receipts
- **WHEN** check succeeds, returns unknown or rejects invalid input
- **THEN** logical records/receipts/revisions/availability remain unchanged and identical computation retries still return the original records.

### Requirement: Advisory budget semantics

Check SHALL return within_budget, over_budget or unknown, all with exit zero for valid advice. It SHALL compare only verified complete compatible values, without FX, basis conversion or credit-to-cash conversion. Unpriced or incomplete requested-scope results SHALL remain unknown, displaying available claimed amounts/known subtotals and reasons on either side of budget. Compatible complete values greater than budget SHALL be over_budget; equal or lower values SHALL be within_budget.

#### Scenario: Over budget

- **GIVEN** a locally verified priced p90 of 18 USD billed and a compatible budget of 15 USD billed
- **WHEN** check runs
- **THEN** status is over_budget with the verified value, original cutoff, provenance and sample count; exit is zero.

#### Scenario: Unknown comparison

- **GIVEN** an unpriced Quote or a valid credit budget against USD billed value
- **WHEN** check runs
- **THEN** status is unknown with unpriced/incompatible explanation and no converted comparison value; exit is zero.

#### Scenario: Missing charge below budget

- **GIVEN** 10 USD known and one missing same-unit charge, against budget 15
- **WHEN** check evaluates that incomplete scope
- **THEN** status is unknown with the known subtotal and missing-evidence reason, never within_budget; exit is zero.

#### Scenario: Provisional subtotal above budget

- **GIVEN** 20 USD known with an unresolved correction, against budget 15
- **WHEN** check evaluates that scope
- **THEN** status is unknown with provisional subtotal/reason, not final over_budget; exit is zero.

#### Scenario: Complete settlement within budget

- **GIVEN** a locally reproduced complete compatible 10 USD settlement and budget 15 for its declared scope
- **WHEN** check runs
- **THEN** status is within_budget and exit is zero.

### Requirement: Safe standalone CI summary

The example SHALL be workflow_dispatch-only and independent of required quality jobs, using local synthetic artifacts, existing pinned setup and read-only permissions without provider credentials or automatic PR/account/branch-protection changes. A Python helper SHALL validate/allowlist the new check result and write directly to GITHUB_STEP_SUMMARY, treating all labels as data. It SHALL escape HTML/Markdown/control characters and preserve benign Unicode; final UTF-8 output SHALL be at most 65,536 bytes including a visible truncation notice. Valid advice SHALL stay nonblocking while malformed result, renderer or write failures remain nonzero. No continue-on-error or shell fallback SHALL suppress technical failures.

The helper SHALL enforce record-kind authority: legacy settlement results SHALL only have unknown status with no verified comparison. A payload relabeled from a valid numeric Quote or computed Settlement to legacy settlement SHALL fail validation before opening or appending to the summary destination.

#### Scenario: Legacy kind cannot claim verified numeric advice

- **GIVEN** an otherwise valid within_budget or over_budget Quote/computed-Settlement result is relabeled as legacy settlement
- **WHEN** the summary helper runs
- **THEN** it exits 2 with empty stdout and a safe diagnostic, leaves an existing summary unchanged and creates no absent summary; valid legacy unknown advice remains accepted.

#### Scenario: Malicious display value

- **GIVEN** a display label contains shell substitution, HTML/Markdown syntax and terminal/workflow control strings
- **WHEN** the summary helper renders it
- **THEN** no embedded command executes, no workflow command is emitted through stdout, and displayed values are escaped data.

#### Scenario: Unicode and bounded truncation

- **GIVEN** a result has large multibyte Unicode display values
- **WHEN** the helper renders its summary
- **THEN** final UTF-8 output is valid, at most 65,536 bytes including the visible truncation notice, with valid escapes and benign Unicode preserved.

The summary helper SHALL accept only the two producer provenance values, `locally_reproduced_synthetic; provider_support_not_verified` and `producer_assertion; provider_support_not_verified`, and completeness `complete` or `unknown`. Unknown advice may retain complete local reproduction when the budget identity is incompatible, or unknown local completeness for incomplete/unpriced results. Arbitrary strings SHALL NOT create provenance or completeness authority.

Producer assertions SHALL have unknown completeness. Local reproduction SHALL require a computation kind with a declared cutoff; a legacy Settlement or missing cutoff SHALL NOT claim local reproduction.

#### Scenario: Unsupported provenance or completeness claim

- **GIVEN** an unknown result contains an unsupported provenance or completeness value
- **WHEN** the summary helper runs
- **THEN** it exits 2 with empty stdout and the fixed safe diagnostic, without creating or changing the summary destination; valid producer combinations remain accepted.

#### Scenario: Malformed summary enum containers

- **GIVEN** status, record kind, quantile or completeness contains a JSON list or object instead of a permitted value
- **WHEN** the summary helper runs
- **THEN** it exits 2 with empty stdout and the fixed safe diagnostic without exposing private input or a traceback, leaves existing summary bytes unchanged and creates no absent destination.

#### Scenario: Summary technical failure

- **GIVEN** deeply nested JSON exceeds the decoder's recursion limit
- **WHEN** the summary helper reads it
- **THEN** it exits 2 with empty stdout and the fixed safe diagnostic without a traceback, leaves existing summary bytes unchanged and creates no absent destination.

#### Scenario: Summary destination or version failure

- **GIVEN** an invalid check-result version or unwritable summary destination
- **WHEN** the example runs
- **THEN** the helper/job fails nonzero instead of presenting successful budget advice or masking the failure.

#### Scenario: Advisory only

- **GIVEN** a valid verified over-budget result or unverifiable artifact claim
- **WHEN** the example runs
- **THEN** it records over_budget or unknown advice respectively with exit zero; no required budget gate or provider credential is introduced.

### Requirement: Current documented workflow and independent repository gates

The locked test tooling SHALL support two local pytest workers for the complete configured suite. Distributed native coverage SHALL preserve every collected target's terminal execution, reject worker errors and report combined coverage. Parallel execution SHALL NOT change test selection, required analyzers, enforcement or the signed launcher's deadline.

Implemented examples SHALL match actual command, output and exit contracts, with current ownership/source mappings, generated references and llms.txt. This change SHALL reuse the foundation validators and existing required Python/native assurance; advisory statuses SHALL NOT suppress tests, docs, metadata or workflow failures. Preparation SHALL remain distinct from runtime delivery, with actual red/green and independent review evidence recorded before acceptance.

#### Scenario: Stale documented command

- **GIVEN** an executable example uses a removed option or outdated JSON/exit expectation
- **WHEN** existing documentation/example and generated-reference checks run
- **THEN** they fail until implementation, examples and generated references agree.

#### Scenario: Budget advice alongside quality failure

- **GIVEN** a valid over-budget result and a failing documentation/test/workflow gate
- **WHEN** advisory and repository checks run
- **THEN** advice stays nonblocking while the independent required quality result remains failed.

#### Scenario: Missing native assurance

- **GIVEN** macOS required analyzers report unsupported_controller_platform
- **WHEN** verification is handed off
- **THEN** the evidence remains incomplete until fresh supported-Linux assurance, without reusing an older feature/archive result as current certification.

#### Scenario: Settlement receipt binds the operation identity

- **GIVEN** a local computed Settlement has a receipt but its payload operation ID differs from that receipt's primary key
- **WHEN** check or historical inspection evaluates it, or the original operation is retried
- **THEN** check returns unknown without a verified value, inspection cannot certify local replay, and retry rejects the inconsistent operation without writing; a second receipt for the altered ID cannot authorize retry under the original ID.

#### Scenario: Summary preserves operation-specific scope and fields

- **GIVEN** a check-v1 Quote or computed Settlement result
- **WHEN** the summary helper validates it
- **THEN** its scope is a valid EconomicScope mapping and its cutoff is present; Quotes declare p50/p90 and a nonnegative integer sample count, while computed and legacy Settlements have null quantile/sample count; legacy cutoff is null. Numeric comparison economic identity matches the computation scope. Missing, legacy-string or contradictory numeric scopes and wrong-kind fields cause a safe exit two before any summary write; valid incompatible-budget unknown and unpriced results remain accepted.


#### Scenario: Generated provenance matches the original cutoff

- **GIVEN** a locally receipted Quote or computed Settlement
- **WHEN** its origin store or recorded/effective timestamp differs from the supported producer's original cutoff
- **THEN** check returns unknown with no verified value and historical inspection cannot certify replay, without changing the store. Origin equals cutoff store and both generated timestamps equal cutoff time; opaque record IDs remain unrestricted.

#### Scenario: Reproduce a Settlement's original predecessor

- **GIVEN** a later locally computed Settlement with available local predecessors for the same Change at its original cutoff
- **WHEN** its previous reference and ledger identity are coherently changed to re-root the revision while leaving numeric details unchanged
- **THEN** check returns unknown without a verified value or store writes. Replay reproduces the producer's predecessor selection across economic scopes at that cutoff, retains the predecessor's ledger identity, and ignores later computations; the first ledger's opaque ID needs no independent authentication.

#### Scenario: Historical local predecessor authority is incomplete
- **GIVEN** an earlier same-Change computation from the local store exists at the selected Settlement's original cutoff
- **WHEN** that earlier receipt is missing, invalid or ambiguous, or its supported producer cutoff evidence is invalid, even if the selected result is coherently rewritten as a new root
- **THEN** check returns unknown with no verified comparison and preserves the store; receipt filtering cannot turn unresolved prior local history into absence
- **AND** a unique coherent prior local tip is required; genuine first results, later-cutoff isolation, unrelated Changes and different-origin imported claims retain their existing treatment

#### Scenario: Pruned history cannot manufacture a first computation
- **GIVEN** an earlier local same-Change computation is time/sequence-available at the selected original cutoff
- **WHEN** altered dependencies or declarations exclude it from the replay snapshot and the selected result is coherently rerooted
- **THEN** check returns unknown without verified comparison or writes; potential predecessors are discovered from stored availability before graph pruning, while genuinely later computations remain excluded

#### Scenario: Incomplete local Settlement declarations retain producer structure

All computed Settlement summary declarations, including unverified producer claims, SHALL retain mandatory nonnegative integer unknown_count metadata. Unverified claims may retain empty, duplicate or unmatched economic groups accepted by the portable record model; those declarations SHALL NOT gain local reproduction or numeric advice through summary rendering.

Verification SHALL retain every test, combined worker coverage and controller/test observations with four locked pytest workers, all ten native analyzers and the existing native deadline. Missing, failed or incomplete worker evidence SHALL NOT pass.

Human and summary presentation SHALL escape Unicode line and paragraph separators U+2028/U+2029 alongside existing controls. User labels SHALL NOT introduce text line boundaries; valid Unicode and spaces remain data, and JSON record values remain exact.

- **GIVEN** a locally reproduced computed Settlement with unknown completeness
- **WHEN** the summary validates its declarations
- **THEN** each subtotal has an explicit nonnegative integer unknown_count, economic identities are unique, and exactly one subtotal matches the declared scope. Missing or ambiguous scope subtotals, missing counts and duplicate identities fail safely before destination access. Null amounts, positive unknown counts and additional economic groups remain valid incomplete advice. Locally complete results require known amounts and zero unknown counts for every economic group, even with an incompatible budget and unknown advisory status. The summary validates result structure without accessing the store or authenticating amounts from JSON alone.

Only the scope identity may have an empty subtotal with null amount and zero unknown count. A non-scope null subtotal SHALL have a positive unknown count, because additional groups come from selected events.

#### Scenario: Numeric summary agrees with selected declarations

- **GIVEN** a numeric check-v1 result
- **WHEN** the selected declaration is absent, ambiguous, incomplete or disagrees with the verified comparison
- **THEN** summary validation exits two safely before destination access. Quotes carry exactly two ordered p50/p90 components with the same scope identity, paired null or finite amounts and p50 no greater than p90; numeric advice requires a positive sample count and comparison equal to the selected quantile. Computed Settlements require exactly one scope-matching subtotal, explicit unknown_count zero and a nonnull matching amount. Decimal equality is exact without conversion or rounding; observed zero and minimum-one Quotes remain valid. Unknown unpriced/imported/legacy results retain their operation-specific declarations.


#### Scenario: Ambiguous local computation receipt ownership

- **GIVEN** two raw computation receipts reference one Quote or computed Settlement result, with equal or conflicting requests
- **WHEN** check, inspection or either operation ID's retry evaluates it
- **THEN** check is unknown with no verified value, inspection denies local computation authority and retries reject without writes. Receipt multiplicity is checked before filtering request or payload operation matches; a matching cloned receipt cannot legitimize an altered Settlement operation ID. Exactly one typed matching receipt remains supported, and unrelated result receipts do not invalidate it.


#### Scenario: Selected availability errors precede trust shortcuts

- **GIVEN** a local selected record has malformed availability time or sequence
- **WHEN** check evaluates it as legacy, unsupported, missing-receipt or ambiguous-receipt advice, or an unsupported Quote is explained
- **THEN** the selected typed Observation is validated before trust/version shortcuts: CLI exits two with empty stdout, safe stderr and unchanged store bytes, without displaying malformed private values. Valid unsupported/unverifiable records still give unknown advice with exit zero. Artifact mode performs no database access.

#### Scenario: Unknown summary retains consistent producer semantics

- **GIVEN** an unknown check-v1 result
- **WHEN** the summary helper validates it
- **THEN** reasons is nonempty. Locally reproduced Quote completeness agrees with its finite versus null quantile pair. Every locally complete result has a nonnull complete selected declaration, even if unknown. Locally complete unknown requires an actually incompatible budget identity and the incompatible_economic_identity reason; a compatible complete result cannot conceal numeric advice by changing status and clearing comparison. Incomplete computed results may retain known subtotals, and valid imported, legacy, unpriced and incompatible unknown results remain accepted. Invalid combinations fail safely before destination access.

#### Scenario: Local unpriced Quote sample counts match producer semantics
- **GIVEN** locally reproduced unknown Quote advice with paired null quantiles
- **WHEN** its sample count is positive
- **THEN** the summary exits two with empty stdout and the fixed safe diagnostic before creating or changing its destination. Local unpriced Quotes require zero samples. Imported producer assertions may retain nonnegative declared sample counts, including positive counts, without gaining verified comparison authority; valid priced local Quotes retain positive counts, including observed-zero amounts.

#### Scenario: Optional null amount remains safe for local unpriced advice
- **WHEN** a locally reproduced unpriced unknown Quote omits an optional amount field
- **THEN** the summary validates the existing null amount semantics without a traceback and preserves normal append behavior

#### Scenario: Selected local record belongs to the committed snapshot
- **WHEN** the selected local result availability sequence exceeds committed metadata sequence, including a reset to the result cutoff
- **THEN** check and both computation inspectors fail safely with exit 2 before trust or version shortcuts, with empty success stdout and unchanged store bytes
- **AND** equality with the committed sequence and later appended records remain valid; artifact mode does not consult local metadata
- **AND** committed upper bounds retain the strict nonnegative integer contract; malformed bounds produce safe technical errors before output

#### Scenario: Summary identifiers match producer contracts
- **WHEN** a check result has a missing, null or blank legacy Settlement scope, record ID or reason identifier
- **THEN** the summary rejects it through the existing safe technical error before opening the destination
- **AND** valid nonblank Unicode, padded, long and control-containing labels remain unchanged as data and safely escaped; no new taxonomy, normalization or length limit is introduced
### Requirement: Singleton metadata before selected inspection

Selected Quote and computed Settlement explanations SHALL require exactly one
local metadata row before granting replay or local computation authority. Missing
or multiple rows SHALL produce the existing safe technical error with exit 2,
empty stdout and no store changes in human and JSON modes. Existing typed metadata
guards remain applicable. A missing committed timestamp at a positive sequence
SHALL retain the accepted inspection replay_unavailable behavior; check still
rejects unavailable metadata before numeric advice.

#### Scenario: Duplicate metadata cannot grant inspection authority
- **GIVEN** a local or imported selected Quote or computed Settlement and multiple metadata rows
- **WHEN** explain inspects it in human or JSON mode
- **THEN** the command returns safe error 2, prints no success output and leaves the store unchanged

#### Scenario: Quote summary scope retains the producer boundary
- **WHEN** a Quote check result declares a non-null time window under either local or imported provenance
- **THEN** the summary command rejects it with the safe technical error before destination access, since Quote projections have null window bounds
- **AND** null or omitted Quote bounds remain valid for priced, observed-zero and unpriced results under p50 or p90, while supported windowed computed Settlement results remain valid

### Requirement: Native diagnostic observations preserve assurance
The native review invocation SHALL retain its canonical command, exit and report validation. Optional process observations SHALL export only bounded numeric descendant metadata and fixed state labels, bind the fresh input digest and exact controller identity, exclude preexisting descendants, disclose missing links and truncation, retain the terminal tail, and never certify analyzer completion or expose arguments, environment, process names or payloads.

#### Scenario: Native execution times out or diagnostics are unavailable
- **WHEN** the unchanged required analyzer fails, or numeric process metadata cannot be collected
- **THEN** its failure remains blocking and a bounded diagnostic or explicit unavailable result may be retained with fresh invocation identity, without changing selection, limits or enforcement

#### Scenario: Descendant identities race or process history exceeds the bound
- **WHEN** a root identity changes, a parent link is missing or starts after its child, or retained observations reach their bound
- **THEN** uncertain lineage is excluded, discontinuities/truncation are disclosed, and the terminal observation remains retained within 64 KiB

#### Scenario: Diagnostic production capacity remains covered
- **WHEN** a controlled numeric process snapshot fills the production observation ring
- **THEN** all 120 retained frames fit within 64 KiB, overflow is disclosed and the terminal frame is retained; real stat and lifecycle controls remain required

#### Scenario: Initial descendant baseline is incomplete
- **WHEN** the initial process scan is truncated, contains unreadable records or lacks a valid controller identity, even if later scans could succeed
- **THEN** the invocation's diagnostic remains unavailable with no descendant trees or aggregate samples; its fresh binding and terminal elapsed time remain available without changing native execution or report checks

### Requirement: Synthetic demo preserves existing outputs
The synthetic demo SHALL preflight its database, bundle and four named check outputs before opening the store. Existing files, directories and symlinks, including dangling links, SHALL be rejected without modifying those paths or creating a database. Unrelated files remain permitted. JSON outputs SHALL be created exclusively so a late collision cannot overwrite an existing file. Late failure may retain newly created demo files and SHALL produce the existing safe technical exit two.

#### Scenario: A generated destination already exists
- **WHEN** any of the six generated paths exists or is a dangling symlink, even while the database is absent
- **THEN** no generated writes or database creation occur and the existing path, target and unrelated files remain unchanged

#### Scenario: A JSON destination appears after preflight
- **WHEN** a file or symlink appears at a bundle or result destination before its write
- **THEN** exclusive creation fails safely without overwriting that path or its target; a newly generated partial demo may remain

#### Scenario: Separately selected sealed timeout diagnosis
- **WHEN** the original required complete repository check fails
- **THEN** CI may run the unchanged review-session test family through the same pinned signed CLI using explicit-file selection and retain its report under a separate diagnostic filename
- **AND** the original full command, selection, limits, reports and failure remain unchanged; diagnostic exits are preserved and a selected success cannot satisfy full acceptance or establish the full-suite timeout cause
