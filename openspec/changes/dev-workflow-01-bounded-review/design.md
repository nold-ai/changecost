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

1. Store one JSON state document under `.changecost/workflow/<change-id>/`. It is
   ignored local evidence, validated on read, and atomically replaced so an
   interrupted update remains recoverable.
2. Use standard-library JSON, `gh api --paginate` for REST collections and
   `gh api graphql` cursor pagination for review threads and their comments. The
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
   closed until each has a non-pending review bound to the frozen head; it polls
   changed nonterminal state through the separate 30-minute no-progress limit.

## Risks / Trade-offs

- [Manual time recording is inaccurate] → retain timestamps and treat missing
  elapsed data as incomplete rather than free time.
- [A family is misclassified] → require explicit family assignment and preserve
  raw evidence for review.
- [GitHub API shape changes] → fail closed with an incomplete monitor result.
- [A reviewer adds noise] → calibration is advisory and has recorded thresholds.

## Migration Plan

New sessions opt in through the revised skills. Existing PRs have no synthetic
history; initialize a record with the current head and pending findings. Revert
the change to remove the helper and skill requirements while keeping ignored local
receipts and the lessons document.
