# Behavioral evidence before review

This contributor pilot supplies a small JSON evidence packet and independent bounded
Change/Run scenario tests. It supplements the existing schema-8 review session; it
cannot approve a PR, clear findings, reset budgets or prove all runtime behavior.
SpecFact is development tooling. No runtime dependency or store migration is added.

## Run the behavioral checks

```sh
uv sync --locked
uv run --locked pytest tests/test_behavioral_evidence.py tests/test_lifecycle_stateful.py -q
```

The lifecycle oracle imports only Python standard-library modules and derives its
expected transitions from the accepted Core-02 scenarios. Its adapter calls public
registration/declaration operations and real temporary SQLite stores. After every
operation it compares acceptance, logical histories and persisted state, checks
append-only records, and requires an unchanged full export after rejection or an
accepted operation that leaves the independent model unchanged. Accepted appends
also preserve old observations and source identity, advance the source boundary, and
require complete unique local observations at the fixed clock/shared new boundary.
Fresh import retains foreign evidence while establishing coherent local observations;
source and destination sequences need not be equal.
The writer inspected production APIs and some implementation before authoring it;
helper independence is not independent human authorship. Independent review and
fault controls address, but do not eliminate, correlated mistakes.

The deterministic inventory is eight seeds (0 through 7), each with two setup
operations and 24 generated operations, plus a 12-operation adversarial trace.
Generation includes registration replay/conflict, terminal Change registration,
reasoned outcome/interval corrections and combined-operation rollback. Separate
chronology tests exercise equal wall times, local sequence cutoffs, later destination
import and unchanged reimport. This is bounded evidence, not exhaustive exploration.
Changing clocks inside a trace, generalized merge/observation-only imports,
concurrency, economic contracts, arbitrary graph topology and all possible integer,
timestamp, filesystem and serialization boundaries are outside this model.

Four synthetic controls deliberately alter the exercised target while retaining the
same oracle, projection and trace:

| Family | Fault at the real boundary | Detector |
| --- | --- | --- |
| Retry/history | Rewrite persisted history/source/availability after retry or append | No-op full export equality; append old evidence preservation and coherent new observations |
| Combined transaction | Persist the outcome before a real invalid interval declaration | Rejected operation must preserve the full export |
| Chronology | Ignore captured sequence or corrupt fresh-import foreign/local observations | Historical cutoff exclusion and preserved/coherent import evidence |
| Representation | Retry a rejected naive timestamp after silently adding UTC | Acceptance must match the scenario model |

The naive-timestamp control selects one representation boundary. It does not establish
coverage of every portable integer/decimal/Unicode domain. Each detector must reject
the faulty target and accept the repaired target on the same trace. Setup exceptions
or mutations solely to the expected result/projection are not valid controls.

## Build and validate a packet

The review-session test suite uses an opt-in pristine arrangement for 67 ordinary
event-test functions (198 existing parameterized cases). Each worker creates the
seed with the real initializer. Before copying its receipt, the helper loads and
replays the seed, requires an unchanged default contract and captures the destination's
current Git inputs. Each test retains separate repository, index, genesis and receipt
files; no runtime validation is mocked or cached. Initialization, race, corruption,
replay, loss and scope controls continue to call the real initializer. Additional
controls check isolation and reject changed inputs, contracts or nonpristine seeds
before copying. This test arrangement does not initialize or authorize live sessions.

Initialize or recover the existing review session using the
[shared workflow](../agent-rules/30-change-workflow.md#bounded-review-contract).
Before executing checks, refresh its inputs with the explicitly authorized manifest
and capture `review_session.packet(...)["binding"]`. Keep that binding with the result;
never attach a newer binding to an older run. Store the report and packet under ignored
`.changecost/`, keeping report files outside the packet's own hashed input set.

This minimal runnable example assumes a current `pilot` review session whose manifest
covers its changed files plus every specification/oracle/generator/configuration and
runtime path referenced below. Add these paths by an explicit approved session scope
refresh before executing checks. Substitute the real change ID and inspected invariant maps.
Run the test command after binding capture and before packet creation, without changing
tracked inputs or the index. For an external tool, record its actual installed version
and analyzer-specific executed outcome, not only its command's exit code.

```python
import json
from pathlib import Path
from quality import review_session as session

root = Path.cwd()
change = "pilot"
current = session.packet(root, change)
binding = current["binding"]  # capture BEFORE the command
# Run the command and save its native output to .changecost/behavioral-report.txt.
# The example below requires an actual passing test report; never fabricate one.
report = ".changecost/behavioral-report.txt"
paths = set(current["reviewed_manifest"])
roles = {
    "specification": ["openspec/specs/change-run-contracts/spec.md"],
    "oracle": ["tests/behavioral_model.py", "tests/behavioral_payloads.py"],
    "generator": ["tests/test_lifecycle_stateful.py"],
    "configuration": ["pyproject.toml", "uv.lock"],
}
paths.update(name for names in roles.values() for name in names)
paths.update(["src/changecost/operations.py", "src/changecost/store.py",
              "src/changecost/models.py", "src/changecost/serialization.py"])
missing = paths - current["reviewed_manifest"].keys()
if missing:
    raise ValueError(f"Approve these paths in the session BEFORE executing checks: {sorted(missing)}")
index = session.index_entries(session.repository.git(root, "ls-files", "--stage", "-z"))
packet = {
    "schema_version": 1, "change_id": change,
    "intent": "Check selected lifecycle invariants before review",
    "invariants": {"history": "Retries preserve immutable history"},
    "trust_boundary": "Trusted contributor and local checkout",
    "entrypoints": ["register_change", "register_run", "declare", "Store.eligible"],
    "assumptions": {"bounds": "Eight seeds; selected synthetic lifecycle scenarios"},
    "known_findings": [], "binding": binding,
    "inputs": {name: session.input_fingerprint(root, name, index) for name in sorted(paths)},
    "input_roles": roles,
    "dependencies": {name: {"invariants": ["history"], "assumptions": ["bounds"],
                            "review_scope": "Inspect relevance to this lifecycle pilot"}
                     for name in sorted(paths)},
    "evidence": [{"id": "lifecycle-tests", "command": "pytest tests/test_lifecycle_stateful.py -q",
                  "tool": "pytest", "version": "9.1.1", "required": True,
                  "applicable": True, "outcome": "pass", "binding": binding,
                  "report": report, "report_sha256": session.file_fingerprint(root, report),
                  "rationale": ""}],
}
(root / ".changecost/behavioral-packet.json").write_text(json.dumps(packet, indent=2))
```

```sh
uv run --locked python -m quality.behavioral_evidence .changecost/behavioral-packet.json
uv run --locked python -m quality.behavioral_evidence .changecost/behavioral-packet.json --previous .changecost/previous-packet.json
```

Exit 0 means the packet's declared required evidence is current, not PR completion.
Without a prior packet, initial current evidence still requires broader review. A prior
packet from another change is rejected as incomplete; valid same-change history may
support narrow delta review. Prior review provenance is a human responsibility.
The output retains the authoritative session status and findings. Missing/changed
reports, input drift, stale binding, uncovered changes or non-passing required analyzers
produce exit 1/incomplete. Optional not-applicable evidence needs an explicit rationale;
it cannot satisfy required evidence. Paths must be normalized repository-relative files,
Every packet input, including ignored oracle/configuration files, must already belong
to the authoritative session manifest captured before execution. Staged-only paths
are included in changed-path coverage even if working bytes equal the base.
SHA256 binds actual report bytes, and specification/oracle/generator/configuration roles
must reference declared inputs. Reports need no self-referential packet hash.

Mapping is an explicit reviewer assertion, not automatic dependency inference or proof
that a tool exercised the named semantics. Inspect command selection, native analyzer
counts, oracle rules and mappings once. The validator does not execute packet commands,
authenticate reports or protect against a contributor forging its own evidence.

## Review the delta, keep final gates

Follow-up review consumes the previous reviewed packet, new packet, actual diff,
affected invariants/assumptions, native reports and unresolved findings. Unknown inputs
or changed intent, entrypoints, mapping, assumptions or trust boundary require renewed
broader review. Rerun affected behavioral checks and bind final gates to the final tree.
Never replace the full current-head quality, independent review or required external
reviewer obligations with a narrow packet result. Inspect the existing session status
before correction/publication and preserve its three-batch/90-minute default and
family investigation/replanning rules.

## Tool experiments and measurement

Non-capsule SpecFact import/contract/drift/repro experiments are recorded separately
from domain model tests and the mandatory supported-Linux capsule gate. Inventory or
hash drift can be useful without proving behavioral correctness. A zero exit with no
bound domain target or executed analyzer remains unbound/incomplete assurance.
Retain failed/unsupported experiments, exact commands, versions, digests and timeouts.
See the [pilot report](../lessons-learned/behavioral-evidence-pilot.md) for observed results.

Token categories, turns, correction batches, design ambiguities, genuine defects,
seeded detections and wall minutes have distinct units. Missing costs stay unknown;
one pilot cannot establish causal savings. Rollback reverts these contributor files
while retaining ignored evidence/session history and existing user stores.

## Bounded risk-first adoption trial

Use the [canonical execution checkpoint](../agent-rules/30-change-workflow.md#risk-first-execution-checkpoint)
for early proof and finding triage. Trial its benefit on one subsequently authorized
bounded change; implementing this guidance does not select or authorize that
change. Record observations at preparation, first stable candidate and final
handoff in existing design/evidence/receipts. Reuse the current session and budget,
not a new ledger, collector or measurement service. An unauthorized or incomplete
trial and its recommendation remain pending.

Separate one-time guidance/setup effort from recurring execution. For each
available observation, name its source identity, scope, start/end boundaries and
coverage. Describe these activities so comparisons use the same boundaries:

| Activity | Observation boundary |
| --- | --- |
| Preparation | Scope/assumption selection, probes and plan reconciliation |
| Implementation | Initial authorized behavior/guidance construction |
| Verification | Execution and interpretation of mechanical/scenario checks |
| Review | Independent obligation/closure and required provider review |
| Rework | Compatible correction sets, fixes and their affected verification |
| Orchestration | Dispatch, evidence transfer, adjudication and coordination |

These intervals may overlap. Do not add overlapping elapsed intervals as if they
were exclusive allocations or as if parallel workers reduced their total work.
Keep wall elapsed minutes, measured active reviewer minutes and measured active
maintainer minutes separate. Waiting or agent elapsed time cannot establish
active human effort; unavailable measurements remain unknown. Session active
review minutes are an existing budget measure, not inferred maintainer time.

Report observed cached-input, uncached-input and output tokens separately. Use
deduplicated response usage or supported deltas from the same cumulative source,
with a stable observation identity and nonoverlapping scope. Never add cumulative
snapshots together. For example, synthetic same-source cached-input counters of
1,200 then 1,700 tokens establish a 500-token interval only if counter semantics
and boundaries are known. They do not establish 2,900 consumed tokens, uncached
input/output totals or billed cost. Counter resets or incompatible scopes prevent
that subtraction; retain them as unknown until clarified. This example is a
measurement control, not observed trial usage.

Retain partial categories and missing billing in existing prose evidence; do not
encode a missing measurement as zero in numeric session usage events. A token
quantity is not a cash charge, and no pricing database or inferred cash amount is
added. Keep commands, versions, input bindings and full native logs/digests where
applicable; broad proof and current-input requirements remain unchanged.

Count early verified discoveries before dependent implementation separately from
later verified escapes after correction. Report actual compatible correction sets
alongside recorded batch events, preserving any difference. Separate genuine
product defects, assurance-tool defects, design ambiguities, duplicate reports and
synthetic controls. Distinct variants retain their failure coverage and source
identities. Preserve incomplete/negative acceptance and all original counters;
three batches/90 active minutes remain the default unless explicitly extended.

At trial closeout, recommend retain, revise or withdraw using observed benefit,
recurring effort, setup cost and limitations, even if benefit is unproven. Compare
history only when scope, phase/observation boundaries, measurement coverage and
acceptance conditions are comparable; state mismatches explicitly. One trial
cannot establish causal defect, token, billing or time-to-market savings. Keep
missing final assurance incomplete and publish real observations in maintained
lessons-learned documentation only after authorization and execution. Rollback
reverts guidance while retaining evidence/history; no user-store migration occurs.

A follow-up also compares advisory `known_findings` and analyzer definitions keyed by
ID (command, tool, version, required, applicable, rationale). Changed definitions or
advisory lists require broader review and appear in `context_changes` with previous
and current values; added/removed definitions have an explicit null counterpart.
These advisory strings never resolve authoritative session findings. Outcome, binding
and report path/hash refresh alone do not broaden unchanged policy, but required
current evidence must still pass. List ordering alone does not change these contexts.

Declared input fingerprints now bind raw bytes/absence, normalized user-execute mode,
and exact stage-zero Git mode/blob or index absence. Packet comparison and existing
session capture share this identity, parsing one index snapshot per capture rather
than spawning Git per declared file. Unsupported index types/conflicts are rejected.
Raw report SHA256 is unchanged. Old byte-only packets require regeneration and old
session bindings require explicit advance; historical events/reports are not rewritten.
Ownership, mtime and ACL metadata are outside this input identity.

The logical model is supplemented by a plain complete expected-record accumulator
prepared from copied command/fixture inputs before each call. It compares a canonical
payload multiset and cardinality for all five selected record kinds, including full
namespaces, typed refs, exact timestamps, reasons, provenance and null optional fields.
Finite literal fixture IDs and test-only store/record UUID allocation seams make these
pre-call expectations possible. UUID/stable-ID algorithm correctness is outside this
control; real public transition decisions and SQLite writes are still exercised.
No expected payload is learned from an export, operation return or production helper.

Observation provenance uses exact partitions: lifecycle append conserves the complete
foreign-observation multiset (empty on fresh creation); fresh import's foreign
multiset equals all input observations. Canonical lists preserve every field and
multiplicity. Local uniqueness/coverage/clock/boundary checks remain, and destination
identity cannot alias an original observer. Lifecycle source identity matches its
pre-call fixture even on first creation. These controls still exclude generalized
imports and the opaque identity-generation algorithm.

Every consumed non-absent export also anchors the literal `changecost/v1` envelope.
Source sequence is an exact integer (not bool/float) in0..2**63-1; observations use
exact integers in1..2**63-1. These small independent checks precede comparisons and
cover before/after, fresh import and reimport exports. They do not call the production
model validator or expand the pilot into arbitrary hostile-object testing.

## Observed pilot boundary

This oracle checks acceptance and persisted state/history, including the exported
payload and provenance envelope. It does not compare API return values. Existing
`tests/test_store.py` registration return/retry equality tests remain complementary
required coverage; a wrapper with a wrong return and unchanged state is outside this
oracle's claims. The pilot also excludes generalized imports, concurrency, and clocks
advancing within a generated trace.

The completed pilot exposed a coordinator limitation: historical family-escape
`REPLAN` remains sticky after explicit investigation and verified repairs. Native clean
summary evidence also does not necessarily produce the REST review record its monitor
requires. Preserve those outcomes; do not reset history, fabricate a passing monitor,
or describe manually verified checks as automatic coordinator completion.

Not-applicable evidence requires a nonblank rationale whether indicated by the
applicability flag or outcome. An applicable=true/not_applicable outcome contradicts
itself and is incomplete even with rationale. Optional applicable=false/pass with a
rationale remains permitted; required analyzers must still be applicable and pass.

For changed inputs, affected identifiers combine both previous and current dependency
mappings. Removed inputs retain old-only labels; additions use current labels; remapped
changed inputs retain both. Identifiers are deduplicated/sorted, and unrelated unchanged
inputs do not contribute. This preserves impact context without changing broad-review
or completion gates.

## Post-replan acceptance boundary

Use the [shared review policy](../agent-rules/30-change-workflow.md#review-selection-and-live-acceptance)
for named verified historical closure and native provider source adjudication. The
packet remains advisory; only the existing session evaluates completion. The PR body
records exact-head live acceptance; tracked pilot reports and unchecked publication-time
milestones remain historical without creating another receipt-only source commit.
Original f6dd negative results and fixed telemetry are retained separately.

## Review-session test isolation

Review-session tests initialize one actual committed seed repository per pytest
session and copy its working files and Git metadata into each fresh test directory.
Copies use separate files rather than hardlinks or shared object stores. Each test
continues to exercise actual Git capture, index, history and mutation behavior in
its own repository; setup reuse does not reduce test selection or assertions.
Independent mutation controls verify that a commit, index/config/hook change or
working-file edit in one copy cannot alter the seed or another copy. This removes
repeated Git initialization work, including capsule launcher startup, while fresh
required native coverage remains the authority for CI acceptance.


Review-input capture acquires flags, visible inventory and stage records in one
NUL-delimited Git query. Tagged untracked paths are classified before parsing any
tab; tracked records retain their original ordered stage bytes. Hidden index flags
remain rejected across the repository, including undeclared paths. Independent HEAD
and status reads and the two captures around initialization/scope refresh remain;
this optimization does not make working-tree capture atomic or change schema 8.
Real-Git compatibility cases compare historical fingerprints for staged/working
divergence, deleted files, unusual names, ignored declared files, planned absence,
intent-to-add, executable mode and undeclared unmerged entries.

Compatibility scenarios use independent guards for distinct immutable case values,
preserving their arrangements and assertions while keeping setup control flow shallow
enough for the required native KISS checks. A passing local depth probe supplements
tests; fresh full native assurance remains required.
