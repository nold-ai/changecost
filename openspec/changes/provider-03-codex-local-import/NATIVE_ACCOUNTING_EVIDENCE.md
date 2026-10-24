# Codex native accounting evidence

Reviewed 2026-10-23 Europe/Berlin. Independent semantic review now approves the
exact finite diagnostic profile described in the [final disposition](#independent-finite-mapping-approval).
The maintainer subsequently authorized canonical activation; the register now
contains 24 profiles and one exact finite usage proof, preserving all 23 historical
profiles and their zero approvals. Reader implementation remains blocked and unstarted. Earlier
investigation and denial sections below preserve the evidence history; the later
finite policy closes those semantic blockers only for its exact snapshot. New
header observations alone do not prove producers for appended records.

## Selected native observations

Existing files were inspected read-only through bounded, strict JSONL parsing.
Only allowlisted identity, usage, lineage and timing metadata was projected into
ignored local evidence. Identifiers were replaced with keyed opaque values.
Original sources stayed unchanged during acquisition and subsequent hash checks.
No transcript, native path, raw identifier or token quantity is reproduced here.

| Snapshot SHA-256 | Declared creation originator | Records | Request usage records |
| --- | --- | ---: | ---: |
| `550db3df1e6f13f55744965c24db1825f4abd59443d9bd88600350ee25ba1a1f` | Codex Desktop | 123 | 16 |
| `978f9529a4c6082760ccc27bedebdd0058105df089275cdf36e2c28ed868e52a` | Codex Desktop | 579 | 46 |
| `71677f1a1d47931e84efb66e74c3c03f53dd75a2fa67883fdde649b86cf1330f` | codex_work_desktop | 87 | 12 |
| `32cf67498e8397cc019f5db132fd6d1512248843b8f3399460b2d02edae77622` | codex_work_desktop | 78 | 11 |

All four headers declare `0.163.0-alpha.10.2`. These are separate creation labels.
The Work label does not establish a coding-session classification. The old
September source pointers were unavailable. The historical 0.159 native bytes
were not reacquired, so this investigation cannot renew their compatibility claim.

All 85 selected request records contain thread, turn, session, root-turn and response
identity fields. Their reported total equals input plus output in these samples.
Cached input and reasoning output do not exceed their respective parent counts.
These observed relations do not prove universal inclusion semantics.

All 85 following snapshots agree on the shared request and accumulated fields.
Snapshots lack response identity, so this ordered comparison does not approve a
general join. An initial preceding-snapshot comparison was superseded locally.
Its zero matches are not producer discrepancies. No natural repeated response
identity, changed-meaning collision or counter decrease was observed. All four
selected files declare a parent absent from the original selected set. The first
source-only lineage projection missed one top-level parent field. Terminal markers
do not establish complete attempt coverage.

## Exact producer-source findings

Public tag `rust-v0.163.0-alpha.10.2` resolves to commit
`4ebc485ca321243727539187169425fcf972f2c4`. The historical tag
`rust-v0.159.0-alpha.12.1` resolves to `180d8caaac22c656bfc6329f2f573ee1430cbe20`.
These source identities are verified public references, not attestations of a
local binary. The following primary sources were inspected on 2026-10-23.

| Obligation | Established source behavior | Approval consequence |
| --- | --- | --- |
| Producer | The recorder writes the version at [creation](https://github.com/openai/codex/blob/4ebc485ca321243727539187169425fcf972f2c4/codex-rs/rollout/src/recorder.rs#L961), then [resumes without new metadata](https://github.com/openai/codex/blob/4ebc485ca321243727539187169425fcf972f2c4/codex-rs/rollout/src/recorder.rs#L994). | A retained header cannot prove the version or coding client of every later response. |
| Overlap | [Request recording](https://github.com/openai/codex/blob/4ebc485ca321243727539187169425fcf972f2c4/codex-rs/core/src/state/session.rs#L219) copies response usage into request, turn and thread scopes. | The three representations cannot supply additive contributions for the same work. |
| Missing categories | The [response parser](https://github.com/openai/codex/blob/4ebc485ca321243727539187169425fcf972f2c4/codex-rs/codex-api/src/sse/responses.rs#L118) supplies zero for absent optional detail fields. | Serialized zero is a source value with limited provenance. It does not always prove an explicitly reported backend zero. |
| Reset and estimates | [Context-window normalization](https://github.com/openai/codex/blob/4ebc485ca321243727539187169425fcf972f2c4/codex-rs/protocol/src/protocol.rs#L2438) replaces totals and zeros categories. [Context recomputation](https://github.com/openai/codex/blob/4ebc485ca321243727539187169425fcf972f2c4/codex-rs/core/src/session/mod.rs#L5106) overwrites last usage with an estimate. | Legacy last and total snapshots cannot universally represent an additive response or a monotonic spending counter. |
| Fork ownership | [Resume and fork restoration](https://github.com/openai/codex/blob/4ebc485ca321243727539187169425fcf972f2c4/codex-rs/core/src/session/mod.rs#L1707) seeds counters from inherited records. | A child's accumulated total can contain ancestor work. Parent absence remains unknown coverage. |
| Finality | The newer source can [persist usage from incomplete error responses](https://github.com/openai/codex/blob/4ebc485ca321243727539187169425fcf972f2c4/codex-rs/core/src/session/mod.rs#L4949). | A request usage row is an observation, not proof of successful completion or finalized accounting. |
| Completeness | Recording [omits rows without usage](https://github.com/openai/codex/blob/4ebc485ca321243727539187169425fcf972f2c4/codex-rs/core/src/session/mod.rs#L5011). The [upstream test](https://github.com/openai/codex/blob/4ebc485ca321243727539187169425fcf972f2c4/codex-rs/core/tests/suite/token_usage_rollout.rs#L29) expects three usage records for four completed responses. | No row does not mean zero work. The upstream test was read, not executed here. |
| Identity, interval and model | [TokenUsageRecord](https://github.com/openai/codex/blob/4ebc485ca321243727539187169425fcf972f2c4/codex-rs/protocol/src/protocol.rs#L2386) has response identities but no correction revision, request interval, model or model version. | A turn's configured model and a persistence timestamp cannot establish the served model or request interval. |

## Six decisions and remaining evidence

The following candidate boundaries are research conclusions. They are not approved
runtime policy and do not waive task 1.2 or its stronger accounting obligations.

| Decision | Candidate boundary | Evidence still needed |
| --- | --- | --- |
| `authority` | Direct request `usage` only, restricted to observed diagnostic response facts. | Stable acquisition bound to the producing build and coding client for the selected records, plus an exact profile and independently reviewed category mapping. |
| `interval` | Request interval stays unknown. Persistence time is separate observation metadata. | Any claimed non-null request interval needs native start/end association and defined semantics. |
| `replay` | Original namespaced thread/response/scope/category identity. Copied ancestor records retain their original identity. | Cross-acquisition native replay and collision reconciliation. Renamed/copied fixture controls prove a detector, not a producer's identity guarantee. |
| `reset` | No deltas from legacy snapshots or inherited counters. Unsupported forms reject. | Native resume/fork/reset evidence and proof that the selected mapping rejects or preserves each supported form without invented epochs or baselines. |
| `correction` | Changed meaning under one identity rejects. No inferred predecessor or last-write-wins. | A native correction mechanism with revision, predecessor and reason, or an explicitly accepted exclusion of corrections for the exact supported mapping. |
| `exclusions` | No complete-thread total, automatic Change binding, inferred finality, billed money or native demand authority. | Independent review of exact partial ownership/finality behavior. Restricting the selected accounting scope requires an explicit scope decision if existing obligations cannot be met. |

Private detector controls passed on all four unaltered projections. Mutating one
request quantity exposed a counter mismatch. Injecting changed meaning under one
identity exposed a conflict. Original source hashes stayed unchanged. These controls
are synthetic tests of the research detector, not native replay, correction or reset
examples and not runtime product TDD.

## Approval disposition and next evidence

Independent semantic review returned a negative approval verdict after reviewing
the sanitized native packet, detector controls, this document and pinned source
files. All 54 retained public-source manifest entries matched their recorded
digests. The reviewer did not reacquire raw native files. The verdict therefore
relies on the recorded native acquisition proof and independently inspected source.
It confirms that none of usage, attribution, finality or billed money qualifies for
approval. Its full report and digest remain in ignored local workflow evidence.

The exact producer binding is the first blocking gate. An existing acquisition or
process record must connect selected response identities to a verified engine build
and coding client. A matching header, installed CLI version, modification time or
current application build alone does not make that connection. No new model request
or collector is authorized to obtain it.

After producer binding, review existing native cross-acquisition replay and linked
resume/fork records with category reconciliation. Define the accepted unknowns and
unsupported correction/reset forms without claiming complete task consumption.
Then bind the six decisions, native digest, exact profile digest and named independent
reviewer in the register. Until that adjudication succeeds, task 1.2 remains open
and dependent implementation stops. The register's structural validator cannot
authenticate or substitute for semantic approval.

Confidence is high in the selected-byte observations and pinned source behavior.
Compatibility and full accounting approval remain unknown. A reliable producer
binding or independently accepted narrower accounting scope could change that
conclusion. Major failure modes are double counting overlapping scopes, accepting
stale producer metadata and mistaking partial records for complete consumption.
The proposed exclusions mitigate those risks only after mapping approval.

The work used local analysis and bounded public-source downloads, with no paid model
request. Rollback restores the original scoped planning stash while retaining its
recovery copy, native originals and ignored evidence. No persisted product data exists.

## Existing provenance and native edge-case follow-up

The maintainer requested a further existing-data search on 2026-10-23. The search
found historical application logs, three linked parent histories and the current
bundled engine. No telemetry was enabled or model request run to generate evidence.
Native metadata after 2026-10-23 22:26 Europe/Berlin was excluded from edge analysis.
Private projections, source hashes, scripts and the candidate mapping remain ignored.

### Producer and build evidence

Historical logs record a local stdio engine handshake reporting
`0.163.0-alpha.10.2` on 2026-10-18 at 20:34 and 2026-10-20 at 23:38 Europe/Berlin.
The latter application log identity continues across 2026-10-20 through 2026-10-22,
with one recorded local engine start. Native thread/turn identities match local
activity for three original samples. The fourth has only logical ancestor matches.
The retained application logs do not match the selected response IDs. These facts
corroborate historical process/thread context without proving a complete response
to exact producer/client chain.

A separate durable connection reports `0.1.0`. That frontend value cannot approve
the local engine or Work coding-session classification. The current executable at
the historical logged path reports `0.163.0-alpha.11.2`. Its enclosing app reports
`26.1016.62342`, build `21477`. Current binary and signing metadata therefore do not
attest the historical `0.163.0-alpha.10.2` executable. No historical binary hash was
recovered. The read-only engine-log database's main image retained only 2026-10-23
records. Its immutable query ignored the WAL and cannot establish 18/22 October
coverage or whole-database absence.

The exact tagged [session construction source](https://github.com/openai/codex/blob/4ebc485ca321243727539187169425fcf972f2c4/codex-rs/core/src/session/session.rs#L932),
accessed 2026-10-23, restores logical `session_id` on resume and shares root identity
with subagents. A single session ID is not a process nonce or build proof. Earlier
ignored output named `distinct_process_session_ids` incorrectly; its count describes
distinct logical session IDs only. This correction creates no new approval.

### Native replay and reset evidence

Independent rereads of the four original native files retained the same SHA-256
and all 85 request identities, categories and quantities. This is actual acquisition
replay of unchanged native bytes. It does not establish copied/appended acquisitions,
provider-level global uniqueness or a native revision mechanism.

The additional parent histories contain the following observed patterns:

| Declared creation version | New-turn counter restarts | Compaction-associated last-snapshot substitutions | Equal legacy total counters |
| --- | ---: | ---: | ---: |
| 0.159.0-alpha.12.1 | 63 | 19 | 72 |
| 0.162.0-alpha.17.2 | 91 | 36 | 454 |
| 0.163.0-alpha.10.2 | 119 | 26 | 449 |

The original 46-turn sample adds 45 new-turn restarts. All 318 observed transitions
start the new turn accumulator with its first request usage while the thread
accumulator continues. All 81 last-snapshot mismatches have an intervening compaction
record. These native observations support excluding legacy and turn/thread counters
from request contributions. They do not prove a universal reset or correction rule
for every appended producer version. The 975 equal legacy total counters lack request
identity and cannot become independent quantities. Of those adjacent pairs, 894
also retain equal projected last-usage fields. The remaining 81 change last usage
around compaction. Equal totals alone do not prove equal snapshot meaning.

All three parent files exceed the unchanged 10 MiB reader cap. Research streamed
their hashes and allowlisted metadata under separate bounds. Oversized content
lines were discarded without parsing or retention. This was not complete structural
validation or an eligible runtime acquisition. One source continued to grow after
capture, so its hash identifies that acquisition, not its later on-disk contents.
The bounded header search inspected 100 existing files and found no fork-parent
metadata. No repeated response identity, natural changed-meaning correction or
copied/appended request replay was found in the seven analyzed streams.

An ignored mapping candidate binds these observations and all six decisions to
profile digest `69db397ce2cdb5a6559308c80af33f322fe97537682d35409f60160171b3d866`.
Its capabilities remain partial or unverified, with no approvals. A future reader
must also recognize valid
producer provenance for a newly selected file; accepting its retained header or a
caller-supplied profile flag cannot solve that gate.

### Independent approval rerun

Fresh independent review denied the exact candidate and every runtime capability.
Its report SHA-256 is
`bdbee65676c1444008b28786ecdf10fc1c764652ed7c98501db79ef8c00951a5`, bound to candidate
packet `b062f2b13e849cff7dc4f712303b52c5704a719ce3373329796ca48b65130e2b`.
The reviewer verified all 30 packet artifact digests, 62 public-source receipts,
the canonical profile digest and the four unchanged native acquisitions. The
measurement-label finding is closed with equal-total and total-plus-last counts
kept distinct.

The review accepts medium-confidence historical producer corroboration for the
selected Desktop segment under the ordinary local trust model. Missing historical
binary signing or a response-ID log for every request is not itself a veto.
Unchanged-byte replay, observed new-turn resets and compaction-associated snapshot
changes close their narrow observational gaps. They do not approve arbitrary files
that share a header, Work usage, full task consumption or a general reset policy.

The remaining gates are an operational producer-binding contract for each accepted
segment across resume, explicit acceptance of the exact partial diagnostic policy,
and recognizable rejection boundaries for unsupported copied/appended replay, forks
and corrections. Source-backed exclusions may qualify without manufacturing a native
correction, provided the supported subset and rejection predicate are independently
reviewed. Complete historical-profile obligations remain unchanged. Task 1.2 and
dependent implementation stay blocked. The next step is that focused evidence/policy
decision, followed by a new digest-bound approval review. No approval was recorded.

## Producer-binding architecture follow-up

On 2026-10-23 Europe/Berlin the maintainer requested planning-only `/architect`
review of producer binding and partial diagnostics. Three configured candidates
and an independent judge compared finite snapshot admission with general producer
segment receipts. The [selected contract](PRODUCER_BINDING_POLICY.md) closes the
future-file boundary by admitting exact independently adjudicated bytes and a
frozen request projection. The [proposed profile](PROPOSED_PROFILE.json) is a
review input only. It cannot activate itself.

The selected scope is the existing Desktop native-1 snapshot and 16 direct request
observations, preserving six serialized categories separately. Backend presence,
served model/version, interval, completeness and finality remain unknown. Creation
headers and logical session IDs cannot extend admission across resume. Changed
bytes reject until separately reviewed; event identity stays independent of the
admission and first provenance remains immutable on later replay.

Independent exact-mapping review is recorded separately below when complete.
Prior denials remain historical evidence. At this planning stage the 23 canonical
profiles stayed unchanged with zero approvals; no runtime eligibility followed.

## Independent finite-mapping approval

On 2026-10-23 Europe/Berlin a fresh independent strongest-judgment reviewer
**approved the exact finite diagnostic mapping and all six decisions**: authority,
interval, replay, reset, correction and exclusions. This supersedes the prior
denial only for the newly defined finite subset, not for broader historical profiles.

- Proposed profile digest: `8be47bbc66c0b04d61bcc4e646271449b4eb653b460c24322cfd203bc5d2a991`.
- Projection SHA: `f18ea851d02c0d1da36893aa9fe4eb8de7710bcafa0b3a774e8ba44c190a3e2c`.
- Six-decision SHA: `def8aab045771a97748704c397d5630cdebce7bbdf3eacd5ab07ac7cd22a5e37`.
- Independent report SHA: `fcdaa2514279ce4444e3d389386c933d7cb0f057d4e3e38de8f5f798cb198916`.

The reviewer verified all 22 current packet hashes, 30 prior packet hashes and
62 pinned-source receipts, read the complete native snapshot, classified all
123 records and independently reproduced the full canonical 16-request/96-fact
projection. Source call paths and counter relationships support direct response
observations, while historical ordinary-local process/thread corroboration supports
the selected producer at medium confidence. No historical cryptographic attestation
or per-response trace claim is made. Corrective replacements and unreviewed bytes
remain excluded; natural correction evidence was not fabricated or required for
an unsupported form. Authored controls remain contract demonstrations only.

The report and exact semantic receipt are retained locally under
`.changecost/workflow/provider-03-codex-local-import/architect-producer-binding-20261023/`.
The proof-bound proposed candidate also passed structural register validation in
memory; that check authenticates neither semantics nor activation. The canonical
register at that stage remained unchanged at 23 profiles with zero approvals. Task
1.2 stayed unchecked because canonical adoption and the combined implementation-stage
evidence refresh were pending. Runtime implementation is unstarted and not authorized by
this planning-only request. Full SpecFact/Linux/provider assurance remains incomplete.

Confidence is high for exact-byte reproduction and finite policy coherence, medium
for historical producer provenance. Changed packet/source bytes, demonstrated writer
replacement or corrective/inherited meaning in selected rows invalidate this verdict.
Next action is separately authorized canonical adoption with structural validation
and deliberate historical-baseline maintenance, followed by implementation work.

## Canonical activation follow-up

The exact semantic profile/proof was canonically activated at the maintainer's
explicit request. [Activation evidence](TDD_EVIDENCE.md) records admission checks,
historical object preservation and fresh independent verification. Earlier
activation-pending sections preserve the preceding review stage. No approved
semantic payload, decision or producer claim was changed. Runtime implementation
stays blocked; contributor validation does not grant broader source authority.
