# Finite-snapshot producer binding and diagnostic policy

Planning contract, 2026-10-23 Europe/Berlin. This defines one proposed narrow
mapping for independent semantic review. It activates no profile and implements
no reader. [The proposed profile](PROPOSED_PROFILE.json) contains the exact admission
payload and six decisions. The canonical register remains the sole approval owner.

## Problem and selected scope

Creation headers and logical session IDs survive resume. They cannot identify the
writer of arbitrary later bytes. Historical local process/version/thread evidence
corroborates one Desktop coding-subagent segment under an ordinary, nonhostile local
trust assumption. This contract admits only an independently adjudicated immutable
snapshot and its exact request subset. It does not promise a general reader for all
files sharing a producer version, nor complete task consumption.

The selected source is the existing 875,189-byte, 123-record snapshot with SHA-256
`550db3df1e6f13f55744965c24db1825f4abd59443d9bd88600350ee25ba1a1f`.
Its 16 direct request observations contain six serialized token categories each.
Known child/parent metadata remains partial. Request interval, served model, model
version, source finality and total completeness remain unknown. No Work source or
other snapshot inherits this proposed policy.

## Caller usage

The CLI and library sketches are proposals, not available commands or APIs:

```sh
changecost settle --repository-id repo --import-codex selected.jsonl \
  --source-profile approved-finite-profile --source-sha256 selected-sha256
```

```python
result = import_codex_file(store, selection)
replayed = import_codex_file(store, renamed_byte_identical_selection)
bind_evidence(store, result.evidence_ids[0], exact_existing_run)
```

Callers select a file, registered profile and expected digest. They supply no producer
assertion or approval. One operation hides acquisition, admission, projection, replay
and the existing atomic store transaction. Results expose bounded local references,
inserted/replayed counts and fixed codes with optional ordinals. They expose no paths,
native identities, source quantities, model/lineage values or exception text.

## Three separate gates

1. Independent semantic review decides the exact proposed profile, admission payload,
   native evidence and six decisions. A positive report approves only those semantics.
2. Later canonical activation records that approval in `source-profiles.json`, validates
   the admission structure, updates the derived matrix and deliberately maintains the
   historical zero-approval baseline test. This is not performed by this planning task.
3. Runtime eligibility additionally needs the generated checked package derivative,
   implemented safe acquisition/mapping and all applicable implementation assurance.

A planning artifact or positive review report is not a second runtime authority.
An unregistered proposal stays ineligible. All 23 historical profiles and their
broader evidence requirements remain unchanged. A newly named profile may support
serialized request observations while attribution stays partial and billed money
and finality unverified. That support means exactly the finite diagnostic subset.

## Admission and hash construction

Let `H(x)` be SHA-256 over
`json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")`.
Integers are exact and array order is preserved. No hash input contains its own digest.

- Admission payload `A` contains source SHA, zero-based accepted record ordinals,
  source classification, producer claim, mapping identity, canonical projection SHA,
  limits, and the six decisions. It contains no profile or approval digest.
- Proposed profile `P` embeds `A`. `H(P)` uses the existing profile-digest recipe,
  excluding only its `approvals` member.
- A positive canonical proof `R` binds capability `usage`, native evidence ID/SHA,
  `H(P)`, named reviewer and the six decisions copied from `A`. `H(R)` identifies
  the actual proof. No pre-existing approval-ID field is assumed.
- The generated runtime envelope carries `A`, `H(P)` and `H(R)`. It is derived and
  checked against the canonical profile/proof, never a separately editable allowlist.

Supporting evidence and the independent report remain separately hash-bound review
artifacts. A report's own digest is not embedded in an object the report must hash.
Contribution/build checks reject a stale derivative. An already installed immutable
package cannot discover later revocation without a package update; no live canonical
lookup, revocation service or runtime `quality.*` dependency is proposed.

The admission predicate is the conjunction of the following conditions:

1. Native-only CLI mode is valid before acquisition. The selected path is a regular
   file reached without symlink traversal or blocking on a nonregular leaf.
2. One bounded descriptor supplies the bytes hashed and parsed. Pre/post descriptor
   identity, size and modification metadata agree. Whole-input limits are 10 MiB,
   10,000 records and depth 32. Strict JSONL rejects empty records, duplicate keys,
   malformed/truncated data, nonfinite values and excessive numeric representation.
3. The acquired SHA equals both the caller's expectation and the canonically approved
   finite snapshot SHA for the selected profile/mapping. No header or flag adds one.
4. Every record is structurally parsed. The exact approved request ordinals and source
   shapes match `A`; all request/accounting/lifecycle rows have been classified during
   independent adjudication. No prefix scan, cutoff or skipped tail grants eligibility.
5. The accepted projection matches the frozen projection SHA and cardinality. Selected
   rows require nonempty thread/turn/session/root-turn/response identities and all six
   exact nonnegative integer categories. Booleans, fractions, negative values and
   representations beyond the existing 4096-digit bound reject. Missing never fills zero.
6. Canonical semantic comparison and repository/graph consistency succeed for the whole
   batch before the sole `Store.apply` transaction commits anything.

SHA proves equality to adjudicated bytes, not authorship by itself. The producer
claim is the separately reviewed historical engine `0.163.0-alpha.10.2` and Desktop
coding surface for the selected request subset. Client build remains unknown. The
claim assumes no unobserved writer replacement within the corroborated lifetime.
Current executable version/hash, source commit, root-only match and logical session
identity cannot supply that claim. Historical binary signing is not a separate gate.

## Exact source classification and partial meaning

Only the selected `token_usage_record.payload.usage` objects yield quantities.
Request, turn and thread scopes are not additive views of separate work. Legacy
snapshots, response content, context, world-state diffs and inter-agent communication
metadata yield no usage facts. Their complete syntax is validated, but no private
content or arbitrary payload survives projection. Exact tagged producer source
classifies the metadata variants, so the earlier scanner's `other` bucket is not an
approval oracle. The proposed profile records all outer/event counts and row membership.

Six separate source categories are preserved. Cached input and reasoning output
are never added to their parent categories, cache-write inclusion is not guessed,
and reported total is never recomputed. Every value is a serialized source observation.
Backend field presence stays unknown, including a serialized zero that may have been
defaulted by the producer. No backend-explicit-zero claim is made.

This mapping makes no turn-context model join. Both `model` and `model_version` remain
null with served-model meaning unknown. A configured model is not a served model.
No persistence timestamp becomes a request interval, effort or historical availability.
Imported facts become locally available through the existing store clock only.

Known source lineage is retained as partial reported metadata. Header parent, original
thread/turn/session/root-turn values are distinct fields, not inferred ownership of
every descendant or attempt. No final marker establishes successful request finality,
full Run/Change coverage or a finalized account total.

## Canonical identity and projection

Define `J(x)` as the compact JSON encoding used by `H`. For this revision all hashed
identifier inputs are strings. Use these unambiguous arrays rather than concatenation:

```text
event = H(["codex-request-event-v1", "Codex", "desktop-coding", thread_id, response_id])
fact  = H(["codex-request-fact-v1", event, "request", source_category])
```

Event/fact identifiers exclude filename, ordinal, repository attachment, source SHA,
profile/approval digest, producer version and admission reference. Mapping revisions
cannot mint duplicate identities for the same source event; incompatible semantic
revision needs a separate migration decision. Repository mismatch against an existing
event rejects rather than creating another copy of the event.

For each accepted row, produce one canonical fact per source category. The exact JSON
object schema is frozen in `A.projection_schema`: opaque fact/event keys, original
thread/turn/session/root-turn/header-parent values encoded as domain-separated opaque
keys, source category, exact count, serialized-source basis, unknown backend presence,
request scope, producer claim, partial coverage and fixed unknown model/time/finality.
Sort unique facts by `fact_key`. Equal duplicates collapse; differing meaning under
one key rejects. The projection SHA is `H` of that sorted array. It excludes source
ordinal and acquisition/admission provenance. The same canonicalizer owns the
projection commitment and immutable store comparison, preventing comparator drift.

One namespaced Evidence record identifies each original response event. Its six
NativeUsage facts retain their original Evidence reference and first acquisition.
Meaning includes producer and reported lineage, so a changed producer/lineage under
the same key conflicts. Meaning excludes first source/profile/approval digests,
first local availability and later admission identity. A separately admitted snapshot
can replay existing events without changing their first provenance or availability.

## Types and ownership sketch

These are sketches only. Types do not exist yet and bodies are not implemented:

```python
class CodexSelection:
    repository_id: Identifier
    path: Path
    profile_id: Identifier
    expected_sha256: Digest

class _AdmissionPayload:
    source_sha256: Digest
    selected_records: tuple[RecordOrdinal, ...]
    projection_sha256: Digest
    producer: ReportedProducer
    mapping_revision: Identifier
    decisions: SixDecisions

class _PackagedAdmission:
    payload: _AdmissionPayload
    profile_digest: Digest
    approval_digest: Digest

class FirstNativeAdmission:
    profile_digest: Digest
    approval_digest: Digest

def import_codex_file(store: Store, selection: CodexSelection) -> NativeImportResult:
    raise NotImplementedError
```

`codex_local.py` hides descriptor acquisition, private parsing, finite admission and
projection behind the one import operation. `models.py` owns strict portable NativeUsage
and its fixed unknown/provenance variants. It adds first-admission profile/proof digests
alongside the existing first-acquisition digest; these are excluded from semantic replay.
`Store.apply` remains sole writer and graph authority. `cli.py` owns mode validation and
safe receipts. Existing bind operations own later exact attribution. No parallel store,
public parse/verify/save stages, caller-created admission or general receipt engine exists.

## Lifecycle outcomes and exclusions

| Selected input | Outcome |
| --- | --- |
| Approved exact native-1 bytes | Eligible only after all three gates and acquisition checks. |
| Byte-identical regular copy or rename | Same admission and semantic replay. |
| Append, resume, formatting change, new file or mixed-version history | New SHA rejects. No admitted prefix or session/header inheritance. |
| Later independently admitted snapshot under the same mapping | Equal original events replay; new accepted events insert once; any conflict aborts all writes. |
| Fork/copied history or distinct-ID correction in unadjudicated bytes | Digest rejects. No claim of a generic runtime lifecycle detector. |
| Known selected direct request with changed identity meaning | Whole-batch conflict, even if an erroneous future admission exists. |
| Work/native-2/other producer or oversized parent history | Unsupported. No inherited approval or relaxed cap. |

No correction, reset-delta or inherited-aggregate support is claimed. Independent
adjudication must establish that each selected direct row is a response observation,
not an inherited adjustment or corrective replacement. Distinct-ID corrections cannot
be detected merely by same-key conflict logic. Such forms stay outside finite admission.
Natural correction evidence is unnecessary for an explicitly unsupported form; a
negative search alone is insufficient to classify an accepted row.

Authored copy/append/mutation controls prove contract consequences only. They are not
new native replay/reset observations. Existing unchanged-byte replay and compaction/
turn-counter evidence remain separately labelled native observations.

Successful import and later manual binding create no DemandObservation, MeasurementPolicy,
SourceCoverage or EconomicEvidence. Current synthetic financial/demand guards remain.
No full-usage, all-attempt, finality, billing, cost, forecast accuracy or publication claim
follows. Runtime implementation remains unstarted regardless of the planning verdict.

## Alternatives and synthesis

Three configured model candidates compared finite snapshot admission with a general
producer-segment receipt. The independent judge scored Astra 9/10, Sol 10/10 and Luna
6/10 as written. Scores are design judgments. Astra is the base for its precise whole-file
classification, selected-row and unsupported-correction contract. Sol supplies the acyclic
approval construction and engine/client distinction. Luna supplies the compact caller
view. This repairs Astra's approval-envelope ambiguity rather than accepting a second
authority. Model diversity was limited to configured GPT variants.

General receipts lose because no approved bounded derivation proves arbitrary future
record-to-process coverage across resumes. A receipt individually approved per digest
reduces to this finite design; a caller-authored receipt cannot certify itself. Finite
admission accepts repeated review cost for every changed snapshot in exchange for a
small, enforceable predicate. Broader compatible-file support remains future work.

## Risks, rollback and next review

The main risks are a misadjudicated historical producer, duplicate facts across new
admissions and accidental complete-task authority. Explicit ordinary-local trust,
stable source keys/canonical meaning, and fixed unknowns/exclusions address those risks.
Source-backed producer or lifecycle uncertainty still requires denial of the snapshot.
No signing infrastructure, collection or paid provider request is introduced.

Independent review must decide the exact proposed payload/profile and six decisions,
verify strict native bytes and complete row classification, reproduce the canonical
projection and assess source-backed direct-request semantics. It must distinguish an
approved design from approved native evidence, canonical activation and implemented
runtime eligibility. No positive verdict is assumed. Rollback reverts planning artifacts
while retaining original native files, the original stash and prior review history.
