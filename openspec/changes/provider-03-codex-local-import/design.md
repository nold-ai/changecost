# Design: Offline Codex coding-session reader

## Context

Prepared against main `6b6fab30e8030e04fc1a2d803000c640c9f64479` on 2026-10-23
Europe/Berlin. The maintainer requested an architect review in planning mode.
See the [proposal](proposal.md) for scope and [preparation evidence](PREPARATION_EVIDENCE.md)
for source freshness, independent comparisons and unresolved native evidence.

The subsequent [producer-binding policy](PRODUCER_BINDING_POLICY.md) defines the
selected finite-snapshot admission and explicit partial diagnostic semantics.
The [proposed profile](PROPOSED_PROFILE.json) is the retained pre-activation review
input. Its exact approved copy is now in the canonical register; the reader is blocked.

The existing `settle --import-evidence` path parses `NormalizedBatch` and writes
Evidence plus EconomicEvidence. Evidence has no quantity. EconomicInput lacks
native model, lineage and finality, and economic corrections require unchanged
windows. `DemandObservation` already requires legitimate pre-work assessment,
ecosystem and exact Run binding. It cannot stand in for unbound imported facts.
`Observation` is availability metadata, not measured usage.

#35 is accepted after PRs #43/#45. Its `policy_supported`, `run_truth` and
`synthetic_evidence` checks independently reject native demand. Financial coverage
also remains synthetic-only. Importing approved source facts must preserve these
separate authorities. The 23 historical profiles retain empty approvals. One
additional finite diagnostic usage profile is now canonically activated; runtime
reader implementation remains blocked.

## Goals and non-goals

Retain the metadata and quantities already required by #36 without pretending
that import creates complete task truth. Add one portable kind, one reader module
and a deliberate mode in the existing settle command. Reuse the existing store
and manual binding. No adapter framework, new service, SQLite source acquisition,
remote thread API, collection, account configuration or native demand projection.

## Usage before types

The following is proposed syntax. It is not an implemented command:

```sh
changecost settle --repository-id repo --import-codex selected.jsonl \
  --source-profile approved-profile --source-sha256 selected-sha256
```

The selected approved profile fixes provider, coding surface, producer version
and mapping revision. Match those against retained source evidence; neither a flag
nor the installed CLI version can authorize or relabel a producer. Unknown or
unapproved mappings reject before persistence, with no empty-success importer.
Stored creation headers can survive an engine upgrade and resumed appends. Exact
record producer/client binding therefore needs evidence beyond that header. See
the [native accounting investigation](NATIVE_ACCOUNTING_EVIDENCE.md).
The logical session ID also survives resume and root/subagent sharing. It cannot
substitute for a producing process or build identity. Historical log joins must
not become a header-only approval predicate for other selected files.
Native import is mutually exclusive with normalized import, computation and
lifecycle fields. Keep normal command behavior and JSON payloads unchanged.

Application usage, also proposed:

```python
result = import_codex_file(store, selection)
replayed = import_codex_file(store, selection)
bind_evidence(store, result.evidence_ids[0], exact_existing_run)
```

Import persists unbound source facts. Repeating an identical semantic event returns
its existing references. Manual binding uses the existing separate operation;
repository/session coincidence cannot bind a Change. The receipt returns bounded
local references, counts/status and diagnostic codes with optional ordinals. It
never echoes paths, native source identities, model/lineage metadata or exceptions.

## Shape and responsibilities

Sketch only. The additive data shape is a diagnostic `NativeUsage` fact linked
to Evidence. Proposed signatures are not existing APIs:

```python
@dataclass(frozen=True)
class CodexSelection:
    repository_id: Identifier
    path: Path
    profile_id: Identifier
    expected_sha256: Digest

class NativeUsage(Record):
    kind: Literal["native_usage"]
    evidence: RecordRef
    mapping_revision: Identifier
    producer_version: Identifier
    first_acquisition_digest: Digest
    first_admission: FirstNativeAdmission
    event_identity: Identifier
    source_category: NativeTokenCategory
    accounting_scope: NativeAccountingScope
    quantity: Nonnegative | None
    quantity_basis: Literal["serialized_source"]
    backend_presence: Literal["unknown"]
    model: Identifier | None
    model_version: Identifier | None
    interval: NativeInterval
    ownership: NativeOwnership
    finality: Literal["unknown", "partial", "final"]
    scope_completeness: Literal["unknown", "partial", "complete"]
    previous: RecordRef | None
    reason: Identifier | None

def import_codex_file(store: Store, selection: CodexSelection) -> NativeImportResult:
    raise NotImplementedError
```

`NativeTokenCategory` preserves reported input, cached-input, cache-write, output,
reasoning-output and total categories distinctly. The approved mapping retains
reported naming/inclusion semantics. Do not reuse DemandComponent, which has no
total category and already expresses demand interpretation. A serialized category
zero can result from the producer's default for an absent backend detail field.
Preserve that source provenance and do not claim explicit backend zero. Do not
reuse legacy snapshots as additive requests or infer request interval/served model
from persistence time/configured turn model. Token counts require
exact nonnegative integer semantics, with missing distinct from zero and the
existing 4096-digit arithmetic bound. Do not infer wall time or effort from tokens.

`NativeAccountingScope` distinguishes request, turn and thread representations.
`NativeInterval` distinguishes absent, partially bounded and ordered bounded time.
`NativeOwnership` distinguishes unknown, root and child with approved opaque
parent/root keys. These small typed variants avoid contradictory booleans. Partial
source lineage or a final source event never establishes full Run/Change coverage.
Preserve profile and surface through the referenced Evidence; no raw path/account
identifiers, transcripts or arbitrary payload blobs belong in portable records.

| Owner | Responsibility |
| --- | --- |
| Proposed `codex_local.py` | One public import operation; private acquisition and pure version-specific mapping; safe diagnostic receipt. |
| `models.py` | NativeUsage portable variant, strict field/quantity/interval variants and paired correction fields. |
| `store.py` and existing graph validation | Identity, Evidence dependency, correction subject/component consistency, forks/cycles, one Store.apply transaction and existing portable availability. |
| `cli.py` | Explicit native mode, conflict validation and existing controlled output/error handling. |
| Existing bind operations | Later exact Evidence-to-Run and Run-to-Change mapping. |

The reader hides source representation and acquisition behind one operation.
Callers do not orchestrate separate read/validate/normalize/save APIs. Runtime
imports no `quality.*` module. Approved mappings are packaged reviewed code tied
to authoritative profile approval IDs/digests and mapping revision. A contributor
consistency check binds those references to the canonical source register; there
is no separately editable runtime approval list or caller-provided approval flag.
The register is development evidence, not a runtime policy engine.

The initial mapping admits only a canonically approved exact snapshot and frozen
request subset. Independent producer adjudication binds that subset; runtime checks
the same whole-file SHA and canonical projection. Profile and approval hashes follow
the acyclic construction in the binding policy. Semantic review, later canonical
activation and implemented runtime eligibility are separate gates. All current
profiles remain unchanged. The initial mapping keeps model/version null and claims
only serialized source observations with unknown backend presence and completeness.

## Acquisition and immutable replay

Accept only explicitly selected existing JSON/JSONL files. Reject symlinks along
traversed paths and nonregular descriptors, including FIFOs without blocking.
Read one bounded descriptor, hash and parse the same bytes, compare the selected
expected digest and pre/post identity, size and modification metadata. Limits are
10 MiB per file, 10,000 records and depth 32. Reject duplicate keys, truncated or
malformed input, nonfinite/negative/fractional token counts and excessive numeric
representations before a write transaction. Project allowlisted metadata without
printing or retaining private fields. A stat comparison detects ordinary changes;
it cannot prove the absence of adversarial concurrent rewrite. Require a stable
selected snapshot for the mapping's support claim. No source writes or checkpoints.

An approved native event/component/mapping identity determines replay. Filename,
file ordinal, batch label and acquisition digest cannot substitute for that
identity. Compare canonical source semantics independently of snapshot hash. Exact
replay returns the original references and first-acquisition/admission provenance
without adding quantity or availability. A byte-identical copy shares admission.
An append or formatting change rejects until separately admitted. After such later
admission, a changed file digest alone does not cause a semantic conflict. Preserve changed categories or
scope as distinct approved facts, never overlapping contributions to a total.

Changed meaning under the same event identity rejects the entire batch. An approved
correction has a separately identified revision, predecessor and reason; allow
changed intervals only when that native policy proves their meaning. Store graph
validation rejects incompatible subjects/components, missing required predecessors,
forks and cycles. Do not inherit economic same-window restrictions or invent reset
epochs, subtraction, zero baselines or last-write-wins from file order. If the
mapping cannot establish stable identity or correction/reset semantics, reject
numeric import. Approved partial facts stay diagnostic with explicit unknowns.

For the proposed initial finite profile, corrections and reset differencing are
unsupported. Independent review must establish that selected rows represent direct
responses, rather than inherited adjustments or replacements. Whole-file admission
excludes unreviewed new bytes; same-key conflict logic alone cannot detect a distinct-ID
correction. One namespaced Evidence identifies a response; source SHA, ordinal,
repository and approval metadata never mint another event identity.

## Synthesis decision and alternatives

Three isolated model candidates compared thin normalized economics, direct demand
bundles and one additive native fact. Independent cross-judging and coordinator
inspection selected the portable-fact candidate. Existing economics lost required
metadata and could not reconcile native snapshots. Direct DemandObservation would
require invented historical assessment/binding or a larger native-policy change.
A sidecar would create a second persistence/availability owner.

Use the portable candidate's one record and Store.apply ownership. Adapt the thin
candidate's single approval authority and explicit native mode. Adapt the third
candidate's explicit producer/model retention, but replace boolean finality and
file-hash identity with typed unknowns and semantic replay. Remove optional atomic
binding, public parser stages and the deferred demand bridge from the public API.
All candidates were screened for split ownership, exposed transport, shallow
wrappers and manually synchronized policy lists. The comparison used configured
GPT model variants; model-family diversity was limited.

## Migration, verification and reconciliation

Reuse the existing records table and portable union unless inspected implementation
proves an additive physical schema change necessary. Current code must continue to
read old records/bundles. New NativeUsage records can be rejected by older binaries;
do not claim backward reading compatibility. Preserve backup/export and all
existing availability timestamps. No version bump or migration is performed by
this plan. After persisted native records exist, rollback retains their backups
and auditable history rather than deleting records or promising old-reader support.

The two delta specs drive red/green identity, changed-snapshot replay, corrections,
unknown states, portable recovery, atomic rejection, safe acquisition and privacy
checks. Keep every synthetic demand and financial regression. Runtime implementation
and native-demand bridging are outside this planning request. During a subsequent
authorized implementation, record accepted deviations here before closing affected
units; no implementation reconciliation has occurred yet.

## Evidence gates, risks and next step

Before runtime mapping, require independent approval for an exact producer/coding-surface
profile with matched request/snapshot evidence, stable opaque identity, revision,
reset, cache/reasoning inclusion, root/subagent ownership and source finality. The
installed 0.139.0 protocol schema does not supply persisted-file proof, and the
historical Desktop 0.159.0-alpha.12.1 observation is not current compatibility.
Native demand needs a separately authorized observation projection and coordinated
measurement/coverage-policy extension. It remains deferred, including after binding.

Double counting requires approved identity/overlap fixtures and copied/appended-file
replay tests. False completeness requires typed partial lineage/finality and negative
authority tests. Leakage requires descriptor/allowlist bounds and exact sanitized
output/store assertions. Planning cost is limited to artifacts; implementation
duration remains unestimated. The exact finite semantic mapping is now approved
as recorded below; the next step is separately authorized canonical adoption, then
spec-derived failing tests after implementation is separately requested. No runtime
support, complete accounting, accuracy or billed charge is approved.

## Finite-mapping review disposition

Fresh independent review approved the exact proposed finite diagnostic mapping
and all six decisions. The [bound evidence](NATIVE_ACCOUNTING_EVIDENCE.md#independent-finite-mapping-approval)
records the exact profile/projection/report digests and ordinary-local provenance
limit. The policy and proposed profile reviewed above remain byte-identical.
Canonical adoption was subsequently authorized below. Generated-package validation
and reader runtime/TDD work remain later authorized stages. This plan implements no reader and activates no profile.

## Canonical activation boundary, 2026-10-23

The maintainer subsequently authorized canonical activation and contributor
admission/baseline maintenance. The exact approved profile and proof are now
registered; the original 23 profiles remain unchanged with zero approvals.
[Activation evidence](TDD_EVIDENCE.md) records the contributor-only behavior checks
and fresh independent verification. Earlier activation-pending statements record
the preceding planning stage. Reader/runtime implementation remains blocked and
unstarted; all ten reader implementation tasks remain unchecked.
