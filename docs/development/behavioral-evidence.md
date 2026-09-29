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
    "specification": ["openspec/changes/core-02-change-run-contracts/specs/change-run-contracts/spec.md"],
    "oracle": ["tests/behavioral_model.py"],
    "generator": ["tests/test_lifecycle_stateful.py"],
    "configuration": ["pyproject.toml", "uv.lock"],
}
paths.update(name for names in roles.values() for name in names)
paths.update(["src/changecost/operations.py", "src/changecost/store.py",
              "src/changecost/models.py", "src/changecost/serialization.py"])
missing = paths - current["reviewed_manifest"].keys()
if missing:
    raise ValueError(f"Approve these paths in the session BEFORE executing checks: {sorted(missing)}")
packet = {
    "schema_version": 1, "change_id": change,
    "intent": "Check selected lifecycle invariants before review",
    "invariants": {"history": "Retries preserve immutable history"},
    "trust_boundary": "Trusted contributor and local checkout",
    "entrypoints": ["register_change", "register_run", "declare", "Store.eligible"],
    "assumptions": {"bounds": "Eight seeds; selected synthetic lifecycle scenarios"},
    "known_findings": [], "binding": binding,
    "inputs": {name: session.file_fingerprint(root, name) for name in sorted(paths)},
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

A follow-up also compares advisory `known_findings` and analyzer definitions keyed by
ID (command, tool, version, required, applicable, rationale). Changed definitions or
advisory lists require broader review and appear in `context_changes` with previous
and current values; added/removed definitions have an explicit null counterpart.
These advisory strings never resolve authoritative session findings. Outcome, binding
and report path/hash refresh alone do not broaden unchanged policy, but required
current evidence must still pass. List ordering alone does not change these contexts.
