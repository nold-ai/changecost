# Design

## Context

See [proposal](proposal.md). Existing quality gates bind review reports to a
complete input digest but do not preserve review-session decisions or enforce a
bounded iteration policy.

## Goals / Non-Goals

**Goals:** Keep review state outside model context, make progress decisions
deterministic, and give skills a small command interface they can consult.

**Non-Goals:** No runtime feature, hosted database, background daemon, review-bot
mutation, or hostile-runner integrity guarantee.

## Decisions

1. Store schema-8 state plus a durable genesis marker under
   `.changecost/workflow/<change-id>/`. Pure replay of original event payloads and
   separately captured time/input facts reconciles every derived field. Atomic
   replacement preserves recoverability; a missing state file with a marker
   requires recovery. This is local accidental-loss detection, not tamper-proof
   storage or protection against deletion of the entire ignored directory.
   Verify initial typed scope, existing full commits and safe file fingerprints,
   including changed/index/untracked paths. Capture those facts once for pure
   replay, permitting unchanged intended files and explicit `<absent>` planned
   paths. Older schemas require recovery without invented provenance.
2. Use standard-library JSON, `gh api --paginate --slurp` for REST collections and
   `gh api graphql` cursor pagination for review threads and their comments. The
   helper parses the complete returned JSON document, including pretty-printed pages. The
   helper receives explicit JSON records for updates; it does not parse model
   transcripts.
3. Compute a status enum from counters, elapsed active time, finding family
   history, declared scope decisions and evidence completeness. The enum is a
   workflow checkpoint, not a mechanism to block arbitrary shell/model activity.
4. Keep historical finding IDs. A content-key comparison may flag a likely repeat,
   but a disposition never transfers automatically after a report changes.
5. The watcher snapshots checks, commit statuses, reviews, GraphQL review threads
   (including resolved/outdated state and comments), and issue comments; it hashes
   the normalized result and emits only a changed snapshot or explicit error. It
   has no GitHub mutation command.
6. The contract names the required GitHub reviewer logins. The watcher fails
   closed until each latest current-head review is APPROVED or COMMENTED. The
   effective CHANGES_REQUESTED from any reviewer blocks completion; later comments,
   pending reviews or dismissal of another review do not withdraw it. A later
   approval or dismissal of the original rejecting review clears it; required pending
   or dismissed reviews cannot reuse an earlier approval. It polls
   changed nonterminal state through the separate 30-minute no-progress limit.
7. Record manually measured active minutes with separate UTC recording timestamps
   linked to immutable event IDs. Missing measurements differ from measured zero;
   completion requires an explicit measurement after the latest input refresh.
   Timestamps document receipt provenance and do not infer active time from wall
   time. Duplicate ingestion retains the original timestamp and counter. Minute grants,
   active measurements and usage sum original components with finite canonical
   summation, never the previously rounded total. Overflow becomes a controlled
   rejection before persistence; malformed history requires recovery. No tolerance
   widens a budget and unmeasured usage remains unknown.
   Integer counters retain exact nonnegative values; floating measurement conversion
   overflow is a controlled validation error, including during replay.
8. Bind the exact repository, selected PR, head, expected target ref/SHA and input epoch. Preserve exact
   REST reviewer identities. Normalize meaningful observation content and replay
   cached monitor classifications from the raw receipt; transport or shape failures
   replace prior green evidence. Requests and sleeps consume the remaining wait
   deadline. Dirty local inputs may be reviewed but cannot complete publication.
   Clean provider summaries without REST submissions remain a documented helper
   limitation, requiring separately verified coordinator evidence.
9. Preserve immutable initial comparison/base facts separately from the current
   comparison commit and PR target. Explicit atomic `advance_head` adoption checks
   both commits locally, captures its UTC timestamp, and starts a new evidence epoch
   without resetting history. Local evidence supplies the complete reviewed binding;
   collection rereads target ref/SHA at both ends. After adoption, required positive
   remote checks/statuses/reviews need timestamps at or after adoption, while all
   current-head objections continue to block. This is timestamp-bound freshness,
   not authentication of remote execution or reinterpretation of SpecFact digests.
10. Validate and normalize requested users through one exact-login extractor for
    semantic hashing, required-reviewer pending decisions and both metadata reads.
    Request changes invalidate collection; ordering/duplicates/avatar changes do not.
    Cancellation restores only still-qualifying evidence. Nonrequired users are
    informational; team expansion is outside this contract. Schema 8 retains raw
    observations; older missing request data becomes incomplete without resetting history.
11. Derive generation-tagged epoch strings from recorded refresh counts, independently
    of caller event identities. Allocate deterministic unused automatic bind IDs under
    the same session lock as persistence. Keep original caller/finding/scope references;
    incompatible persisted epochs require recovery with no synthesized allowance.
12. Build packet status and body from one loaded receipt, retaining the actual-input
    drift check. Changed watcher output associates that packet's raw observation and
    exit decision, avoiding mixed revisions under concurrent writers. Required event
    text rejects whitespace-only values but preserves every nonblank byte and exact
    reference; no new family-label grammar or normalization is introduced.
13. Preserve exact-limit completion only when no family investigation remains;
    otherwise exhaustion of either budget requires replanning. Extend existing
    binding-qualified reviewer evidence with explicit thread ID/content-digest
    coverage. Compare it against all current report content before completion,
    independently of local finding dispositions and remote unresolved status.
    Resolution/outdated flips alone do not alter report content; unchanged reclosure
    may reuse explicit adjudication. This trusts local coordinator assertions, adds
    no resolver-permission architecture, and cannot detect unobserved transitions.
14. Preserve collection-time observation epoch metadata unchanged at ingestion.
    Never synthesize the current generation for missing values. Missing/malformed/
    stale metadata replaces previous green monitoring with persisted incomplete
    evidence; epochless API-error observations remain storable and yield no receipts.
    No additional identity, authorization or observation-history framework is needed.

## Risks / Trade-offs

Full hexadecimal commit IDs share one validator across initialization, captured
inputs, refresh and replay for SHA-1/SHA-256 repositories. Watcher output suppresses
unchanged remote polls, never terminal local decisions. Deadline handling rereads
the receipt so local budget exhaustion or incomplete scope takes precedence over
wait; a changed terminal packet is not printed twice.

- [Manual time recording is inaccurate] → retain timestamps and treat missing
  elapsed data as incomplete rather than free time.
- [A family is misclassified] → require explicit family assignment and preserve
  raw evidence for review.
- [GitHub API shape changes] → fail closed with an incomplete monitor result.
- [A reviewer adds noise] → calibration is advisory and has recorded thresholds.

## Migration Plan

New sessions opt in through the revised skills. Existing or incompatible receipts
require explicit recovery retaining original history and unknown measurements;
they do not authorize a fresh allowance. Revert
the change to remove the helper and skill requirements while keeping ignored local
receipts and the lessons document.

Schema 8 requires captured scope facts on each head refresh. The derived reviewed
manifest preserves authorized keys on ordinary refreshes; explicit prior approved
scope-decision references select a replacement complete keyset. Approval hashes
are immutable intent evidence, not a claim about current reviewed contents. Scope
capture recaptures fingerprints and validates changed/index/untracked coverage
against the effective adopted-or-current comparison base between consistent input
reads. Pure replay validates those facts without accessing historical files. The
original contract and counters remain unchanged; no one-use approval system is added.

Schema 8 binds all declared path fingerprints/absence in every input capture and
marks existing non-indexed declared content dirty even when ignored. Initialization,
selected-scope refreshes and live status use the same required declared keyset;
unrelated ignored output remains excluded. Prior receipt semantics require recovery,
not an implicit migration/reset. Remote freshness begins at validated genesis time,
remains through ordinary refreshes, and updates on explicit base adoption. Required
positive timestamps compare exactly with timezone awareness; valid pre-init or
coarse same-second results may need reruns. This is conservative contextual evidence,
not authenticated execution; older objections/failures are never filtered away.

Schema 8 generalizes local reviewer evidence to reviewed_reports, matching the
packet report_receipts map. Thread, review and comment namespaces preserve exact
source identities across all pages and historical reports. Stable content/context
hashes exclude reactions, avatars, transport timestamps and lifecycle flags;
independent objections, resolution, freshness and input gates still apply. Uniform
coverage includes empty and informational bodies rather than classifying intent.
Changes require fresh explicit local attestation, including summary churn. Missing or malformed report identities/bodies and duplicate identities fail closed. Earlier thread-only
receipts require recovery without resetting counters or synthesizing adjudication.
