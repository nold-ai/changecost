# Design: Claude Code project JSONL reader

## Context

See [proposal](proposal.md) for the selected outcome and exclusions. This planning
refresh uses main `c424eb8ac67b51af087dbe71a1516a24281c90a1`, inspected on
2026-10-27 (Europe/Berlin). No Claude runtime or source activation is delivered.

The core supports atomic Evidence/NativeUsage append, exact manual bindings and
linear corrections. The delivered finite Codex reader indexes original revisions
and rejects changed facts. Its replay algorithm is not a Claude correction policy.
Native graph validation requires Codex evidence. NativeUsage fixes serialized-source
basis, unknown backend presence and partial-observed coverage, with closed
categories/scopes and concrete thread/parent ownership fields. Reuse needs proof
that approved Claude meanings fit those constraints.

Historical project 2.1.275 observations contain revised message usage. Desktop
transcripts and SDK/result streams are separate profiles. Every Claude approval
remains empty at the revised-profile gate. See [native evidence requests](../../../docs/research/adaptive-demand-evidence.md)
and [provider metrics](../../../docs/providers/codex-claude-metrics.md).

## Goals / Non-Goals

Plan a reusable version-specific project JSONL reader with approved accounting,
corrections and replay. Honest partial coverage must not silently replace this
outcome with finite diagnostic snapshots.

No private-file inspection, collection, model execution, source activation or
runtime change occurs here. Other Claude surfaces and complete native demand,
billed money and calibration remain separate. Existing Codex support stays intact.

## Usage and interface sketch

The command and signatures below are prospective, not implemented features:

```text
changecost settle --repository-id REPO --import-claude-project selected.jsonl --source-profile APPROVED_PROFILE --source-sha256 SHA256
```

```python
class ClaudeProjectSelection(Model):
    repository_id: Identifier
    path: Path
    profile_id: Identifier
    expected_sha256: Digest


def import_claude_project(
    store: Store, selection: ClaudeProjectSelection
) -> ClaudeProjectImportResult:
    raise NotImplementedError
```

The result exposes safe evidence references, import/replay/correction outcomes and
closed diagnostic codes with optional bounded ordinals. It exposes no raw payload,
path, account or native identity. Exact result fields and diagnostic vocabulary
must be reconciled with approved policy before implementation. They grant no
financial or full-demand authority.

An approved selected snapshot imports allowlisted facts atomically. Exact replay,
including an old accepted snapshot after a correction, adds nothing and preserves
first-acquisition/admission provenance. A later snapshot can append a separately
identified approved correction with predecessor and reason. Ambiguous or conflicting
revisions reject the entire import. Existing exact manual evidence-to-Run-to-Change
binding remains a separate operation.

## Decisions and ownership

1. Give a Claude-owned `claude_local.py` one public import operation. It owns
   approval resolution, bounded acquisition, private wire parsing, source identity
   and correction interpretation. Keep internal projection pure where possible.
   Callers select file/profile/hash, never policy callbacks or source approval.
2. Keep CLI wiring mechanical. Add the planned project mode and existing
   profile/hash selectors. Reject competing Codex, economic, lifecycle and binding
   modes before acquisition/persistence. Shared source selectors must not silently
   choose Codex. Repository/session labels do not establish a Change join.
3. Reuse `Store.apply` for atomic validation and persistence. Resolve approved
   event/revision identities and correction chains inside its transaction. Filename,
   batch, ordinal and later acquisition hash cannot create a new contribution.
   Stale predecessors, forks and incompatible corrections reject. No universal
   first/last/maximum selection rule substitutes for approved source policy.
4. Extend native validation only for an exact independently approved provider/profile
   relationship with coherent provenance. Do not replace the Codex-only check with
   arbitrary provider strings. Store/bundle validation, provider-separated identities
   and immutable first-admission history remain obligations.
5. Retain existing inspector bounds of 10 MiB, 10,000 records and depth 32. Read one
   stable regular JSONL snapshot without modifying originals. Reject symlinks,
   duplicate keys, malformed/nonfinite quantities and changing acquisition metadata.
   Expected SHA-256 pins bytes, not semantics. No SQLite/WAL bypass or settings change.
6. Keep categories and overlapping representations distinct until approved inclusion
   is known. Missing is not zero. Preserve unknown served model, intervals,
   ownership/finality and coverage instead of inferring them from nearby rows.
   Source facts or manual binding create no demand or monetary policy.

Boundary Discipline keeps source interpretation inside the Claude boundary.
Laziness Protocol favors one import API and existing persistence ownership. A
shared native engine would couple finite Codex admission to unresolved Claude
policies through callbacks or flags. Defer extraction until two implementations
demonstrate identical mechanics. Reject a select/preview/import API that makes
callers coordinate stages without an approved preview outcome. Accept bounded
acquisition duplication to preserve Codex behavior.

## Approval-to-contract execution checkpoint

The delegated reader owner is the sole tracked writer in the separate reader
worktree. Independent reviewers are read-only. Runtime work remains blocked until
fresh approval of the revised exact profile. The original preparation checkpoint
below remains historical; the selected 2026-10-28 policy follows it.

| Critical assumption | Observed evidence | Required closure and limit |
| --- | --- | --- |
| A reusable project-log mapping has reliable producer, identity, correction, inclusion and finality semantics. | Historical project observations contain revised usage; every Claude profile remains unapproved. SDK/result/monitoring docs describe separate surfaces. | Separately authorized minimized native evidence and independent version-specific approval. No generic header, row-order or SDK-rule substitution. |
| Approved Claude facts fit portable native contracts without weakening Codex. | NativeUsage has closed category/scope/ownership constraints; native_graph accepts Codex only. Store supports linear chains, unlike the finite reader's original-only replay index. | Demonstrate faithful category, lineage, basis and revision representation. Otherwise prepare an explicit additive contract delta with portability/backup tests before code. Retain the promised reader outcome. |

Runtime probes and product red/green tests are not applicable to this documentation-only
preparation. Actual strict, docs/generated-reference, aggregate checks and concrete-diff
review belong in the local receipt. Static inspection is not native accounting proof.

Independent architecture exploration selected the provider-owned module, grafted
an approval-to-contract checkpoint and exact provider/profile validation, and
rejected shared-engine and preview APIs. This supports the plan only; the actual
diff requires independent review. Later accepted deviations must update this
usage, responsibility and outcome contract before handoff.

## Evidence and unresolved implementation gates

The [Agent SDK cost guide](https://code.claude.com/docs/en/agent-sdk/cost-tracking)
and [monitoring reference](https://code.claude.com/docs/en/monitoring-usage), accessed
2026-10-27, describe SDK stream scopes, overlapping usage and client-side estimates.
They do not establish this installed producer's persisted project-log contract.
The `claude` symlink points to a 2.1.257 binary path; no CLI invocation occurred
in this preparation. Installation is not historical producer/accounting proof.

Before implementation, resolve exact producer/surface binding; stable event and
revision identities; repeated-message precedence; representation overlap; cache
inclusion; reset/correction ordering; root/subagent scope/finality; approval
granularity; and portable-contract fit. New native inspection or activation needs
separate authorization. These are implementation blockers, not guessed defaults.
Synthetic fixtures preserve approved relationships but cannot grant native approval.

## Verification, risks and rollback

Derive future failing tests from capability scenarios and retain actual red/green
proof. Cover old-snapshot and correction replay, stale predecessors/forks,
whole-batch rollback, profile/producer/proof mismatch, provider namespaces,
partial lineage, cache inclusion, missing/zero, privacy and acquisition bounds.
Exercise exact manual binding, current-version roundtrip/recovery and unchanged
Codex admission. New mapping/acquisition identities must not duplicate history.

Double counting needs approved inclusion rules. Misclassified corrections need
immutable-chain/replay tests. Admission broadening needs exact provider/profile
checks and Codex regressions. Unsupported evidence remains incomplete, with no
native demand, billed-money or calibration authority.

Preparation rollback reverts only planning/docs while preserving receipts,
approvals and archives. Later schema changes require backups and current-version
recovery proof; older binaries can reject additive records. Applicable strict,
aggregate, supported-Linux and risk-selected provider review requirements remain.
Historical archive exceptions waive nothing here. Issue #17 and dev03 trial remain
separate, with their unfinished obligations preserved.

## Selected serialized request-stage policy, 2026-10-28 Europe/Berlin

The retained exact-version producer control proves one 2.1.215 sidechain
partial-to-terminal append. The two minimized historical native observations
corroborate the four-category grouping grammar. The public
[native statement](../../../docs/providers/evidence/claude-project-2-1-215-native-observations.md)
and [producer statement](../../../docs/providers/evidence/claude-project-2-1-215-producer-controls.md)
have separate origins and exact digests in the draft profile. Original private
acquisitions and projections remain in ignored bindings. Existing public discovery
IDs are not exact-byte evidence for these new acquisitions. No further producer
or raw native inspection is selected.

The controlled positive child transition used `end_turn`. Root `tool_use`
persistence plus historical sidechain `tool_use` observations support applying the
same stage policy with Medium confidence. This is an explicit composition, not an
executed child-tool transition or approval for 2.1.257 or 2.1.275. Declared versions
and identities remain source claims, not cryptographic source authentication.

A private event contains coherent producer/session/optional-agent/request/message
metadata, an optional partial four-category vector and an optional terminal vector.
Each vector preserves input, output, aggregate cache-creation and cache-read
individually. Missing remains null and zero remains zero. Exclude cache-duration
subcategories, server-tool counts, totals and reasoning. Do not derive a served
model, interval, backend presence or root ownership. Reported sidechain/agent
metadata cannot supply the concrete parent required for child ownership.

Within one snapshot, explicit null-stop rows must agree on one partial vector.
Terminal rows must agree on one raw supported reason, `end_turn` or `tool_use`, and
one vector before projection. Missing, malformed or other stop metadata rejects.
Both supported terminal reasons then map to the same canonical `final` accounting
stage. Across valid snapshots, equal terminal quantities with different supported
reasons are the same accepted facts and replay as a no-op. This is a deliberate
accounting equivalence, not a claim that native reason mutation is valid. Mixed
terminal reasons within one snapshot still reject. Raw reason history is neither
promised nor stored or hashed into identifiers. `NativeUsage` and its serializer
remain unchanged. Its `partial` and `final` values mean serialized request stage
under this mapping only. Backend and scope completeness remain unknown, and
coverage remains `partial_observed_subset`.

Event identity uses provider/project surface/session/optional agent/request/message.
Version, profile, file path, ordinal and acquisition hash do not create a new event.
Validate request/message uniqueness in both directions, coherent immutable
metadata and conflicting duplicate UUIDs within a file. Do not promise cross-file
physical UUID continuity. Unknown contributor grammar rejects. Assistant usage
without required identity rejects even with zero counters or client-error-looking
keys. Retained `isApiErrorMessage`, `error` and `apiErrorStatus` key names do not
establish their values or an executable skip discriminator. Only explicit known
noncontributing row grammar can exclude a record.

A first event can be partial-only or terminal. Accepted partial A advances once to
terminal B only if the new snapshot retains the same canonical A in all four
categories under the same immutable metadata. Append all four category revisions
with their current partial predecessors and fixed reason
`claude-serialized-stage-refinement`. Quantity-equal advancement still appends
because the source stage changes. Index all accepted revisions. A, B, A, B imports
return prior exact references without downgrade or duplicate facts. Terminal-first
acceptance does not permit an unseen earlier partial to invent history later.
Unseen partial C, changed terminal quantities D, absent retained A, stale
predecessors, forks, cycles and resets reject the whole batch, including otherwise
valid new facts. Preserve first Evidence, acquisition and admission provenance.

Keep acquisition, policy lookup, parsing and source refinement in `claude_local.py`.
`Store.apply` remains the only atomic persistence owner. Portable graph validation
needs the exact approved Claude provider/profile/producer/mapping/first-admission
association, coherent four-category stage cohorts and legal category predecessors.
It cannot prove the later private source retained A; the importer owns that check.
Use one approved policy definition through packaged derivation where appropriate.
Keep the finite Codex validator and canonical projection unchanged. A reusable
Claude admission kind is a narrow contributor check, not authenticity proof.

The prior candidate's exact approval was blocked by its client-error skip and
unrepresentable cross-snapshot reason distinction. Candidate 2 removes that skip
and defines normalization explicitly. It has no approvals and is not in the
canonical register. Fresh independent review must bind its exact digest, all six
decisions and the native evidence/private binding before activation or code.

Tests must exercise A/B/A/B replay, equal-quantity advancement, terminal-first
then unseen partial, absent retained A, same-value terminal reason changes across
snapshots, mixed reasons within one file, identity/error-looking rejection, and
conflict-plus-valid-facts rollback. Reopen and actual bundle recovery must retain
all four coherent categories and first provenance. Existing Codex, manual binding,
economic and demand exclusions remain regression obligations. No behavior test
or aggregate assurance has run at this planning checkpoint. All ten tasks remain
unchecked. Verification owns aggregate gates; future promotion remains separate.

Confidence is Medium for the reusable exact-version policy, bounded by retained
producer/native observations. A contradictory supported-version trace can require
policy revision. Repeated blocks risk double counting, unseen revisions risk
false corrections and terminal labels risk false completeness. Grouping, immutable
refinement and explicit unknown authority fields respectively address those risks.
No provider spend or runtime activity occurred in this reconciliation. Rollback
reverts owned uncommitted planning changes while preserving candidate 1, source
proof, review history and the separately owned PR #50 ledger.

## Closed noncontributor grammar, 2026-10-28 Europe/Berlin

Candidate 3 closes candidate 2's unspecified noncontributor predicate. Bounded
metadata-only reinspection of the same two fixed-byte native sources identifies
the previously masked rows as `attachment`. Independent review of retained actual
2.1.215 producer traces also corroborates `queue-operation`, `last-prompt`, `mode`
and user shapes. Candidates 1 and 2 remain frozen; candidate 2 retains the exact
prior public evidence bytes. The revised native statement and ignored bindings
retain distinct native and controlled-producer origins. Fresh candidate-3 approval
is still required before activation or runtime code.

Only `assistant` rows contribute canonical facts. Their message must be an object
with exact role `assistant` and a usage object, with all required identities and
producer/stage metadata validated. Type `user` is excluded only with a message
object, exact role `user`, absent `message.usage` and absent direct `usage`. Types
`attachment`, `queue-operation`, `last-prompt` and `mode` are excluded only when
both top-level `message` and direct `usage` members are absent. A present null is
not absence. Unknown labels, mismatched shapes and unexpected usage on excluded
types reject the whole snapshot. No `progress`, `system` or generic other-type
skip is approved. Nested excluded payloads are ignored without recursive counter
inspection or completeness claims. This closed grammar is explicit admission data.
The quantitative accounting, normalized terminal meaning, refinement, replay and
unknown authority policies above are unchanged.

## Initial combined-stage acceptance, 2026-10-28 Europe/Berlin

The candidate-3 review exposed an unstored-history edge. A first source containing
A and B cannot store only B, replay that same source, and reject unseen C+B without
retaining an approved A witness. The selected candidate-4 amendment accepts the
two observed source stages as actual history in one current-time transaction. It
adds no field, hidden witness or producer claim. Candidate 3 and its prior local
activation/proof/package context are preserved. Candidate 4 requires fresh exact
delta approval before replacement or persistence. Evidence bytes are unchanged.

On first valid A+B, accept four partial A originals and four terminal B corrections
with A predecessors and the fixed refinement reason. Both cohorts have this import's
current recording time, the same full-snapshot first acquisition and the same first
admission. No earlier import, acquisition or availability is claimed. Only B is
current; never sum A and B. A-only first acceptance and later retained-A refinement
remain unchanged. B-only first acceptance stores four B originals, invents no A,
and rejects a later unseen partial even when that partial accompanies known B.

After initial A+B acceptance, exact A+B, B-only and A-only are accepted-history
replays. C+B and C-only reject. Equal-quantity A+B still stores two four-category
cohorts because the source stage changes. All rejection remains whole-batch atomic.
`fact_count` counts currently selected category facts, four per event.
`inserted_fact_count` counts persisted NativeUsage history revisions, eight for a
first combined event. `corrected_fact_count` counts new category revisions with
predecessors, four for that combined event. These counts never denote token sums.

## Implemented history reducer, 2026-10-28 Europe/Berlin

Exact candidate-4 approval and explicit activation authorization were received.
The reader uses a four-state accepted-history table (empty, partial, terminal,
refined). Canonical accepted stage comparisons precede all additions. Only empty
history or retained partial-to-final advancement permits new stages. Store.apply
validates and appends the entire batch atomically. Portable graph validation checks
provider/profile/producer, admission, category cohorts and predecessors. Evidence
provider, project surface or reserved mapping selects the Claude validation path,
so changing provider/surface labels cannot evade its exact policy.

The final review correction broadens the association recognizer to every retained
recognized claim: provider, both surfaces, mapping, profile ID and both admission
digests. Any one selects full exact Claude validation. Evidence ID must equal event
identity, matching the canonical reader and making imported history replayable.
This corrects dispatch omissions without changing the portable schema or approved
source semantics. The finite-claim corruption matrix and coherent Evidence-alias
rejection are recorded in [implementation evidence](TDD_EVIDENCE.md).

## Desktop additive scope, 2026-10-28 Europe/Berlin

The maintainer authorized exact Desktop 2.1.308 support after independent q3
source approval (profile digest d942dcb33a80294a7f25d4d4c9f31523e1e5338b02e84efd715a32aaa86f1708).
Two immutable packaged admissions and one private exact catalogue in claude_local
serve the unchanged public selection/result API. Catalogue claims select exact
portable validation globally by event identity. Desktop accepts only root terminal
four-category observations, preserves literal zero and rejects missing/null, partial,
child and changed-quantity records atomically. Closed metadata/blob grammar grants
no nested-counter authority. Existing 2.1.215 lifecycle and Codex remain unchanged.
Frozen source statements retain historical draft wording; their new canonical
approval establishes current source status. Source approval is not runtime assurance.
No collection, paid calls, telemetry, merge, release or #17 live authority is added.
Aggregate verification belongs to the verification stage owner.

## Approved q4 metadata revision, 2026-10-28 Europe/Berlin

Independent approval binds exact digest
`7e3cf00757e1eca8c91782848c59913a9e19bb39b78c7a15edf7be370b906b55`
and mapping `claude-desktop-root-terminal-r2`. It adds only closed cost-state and
mode exclusions. Their values, including modelUsage and costs, remain opaque.
Contributor, quantity, lifecycle and identity rules are unchanged. The unpublished
Desktop candidate replaces q3 after its full canonical/asset/proof snapshot was
frozen; no real q3 Desktop facts existed. Disposable authored q3 stores are retained
without a claim of binary compatibility. The first 25 profiles remain unchanged.
The separately identified depth/encoding defect is corrected by UTF-8-only parsing
with retained byte line boundaries, not by changing provider accounting rules.
