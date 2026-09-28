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

1. Store schema-3 state plus a durable genesis marker under
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
   time. Duplicate ingestion retains the original timestamp and counter.
8. Bind the exact repository, selected PR, head and input epoch. Preserve exact
   REST reviewer identities. Normalize meaningful observation content and replay
   cached monitor classifications from the raw receipt; transport or shape failures
   replace prior green evidence. Requests and sleeps consume the remaining wait
   deadline. Dirty local inputs may be reviewed but cannot complete publication.
   Clean provider summaries without REST submissions remain a documented helper
   limitation, requiring separately verified coordinator evidence.

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
