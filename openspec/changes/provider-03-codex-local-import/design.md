# Design: Offline Codex coding-session reader

## Context

Normalized imports and synthetic reconciliation exist; native accounting is
unapproved. Discovery on 2026-10-06 supplies structural metadata, not complete
usage semantics. Persisted request-level token_usage_record response/turn/root-turn fields and legacy event_msg/token_count snapshots overlap. Indexed tokens_used is metadata, not another additive quantity. Recorded producer versions may differ from the installed CLI. See [proposal](proposal.md) and
[native evidence summary](../../../docs/research/adaptive-demand-evidence.md).

## Goals / Non-Goals

Enable selected, verified local metadata inputs without exports/admin access.
No background discovery, model execution, ordinary chat or financial inference.

## Decisions

1. Use explicit local file arguments in the existing settle workflow and require
   provider/surface/producer-version/profile selection. CLI, IDE and Desktop coding
   profiles stay separate. Undocumented storage is an explicitly researched local
   compatibility boundary, not an official export guarantee. Unknown versions
   reject before persistence; retention/layout changes need new inspection.
2. Select a reviewed request or snapshot representation per version; never add both. Require response identity, revision/reset/finality and root/subagent ownership. Preserve cache/reasoning categories as reported, without guessed equivalence.
3. Independently approve source semantics and versioned accounting/coverage before
   enabling totals. A structural receipt cannot approve a mapping. Full-demand
   coverage is distinct from complete billed money; preserve partial diagnostics,
   unresolved corrections, session/root/subagent gaps and declared exclusions.
4. Normalize bounded allowlisted metadata only (identities, model/version, times,
   usage categories, revision/ownership and explicit economic basis). Existing
   inspector limits guide readers: 10 MiB/file, 10,000 records, depth 32. Reject
   duplicate JSON keys, malformed/nonfinite quantities and unsafe inputs with
   ordinal/code-only diagnostics. Never persist/log prompts, arbitrary payloads,
   secrets or raw account/path identifiers. App version is not producer version.
5. Originals remain read-only. Require a stable selected snapshot/hash; active-file
   changes during acquisition reject or remain explicitly partial. No write-capable
   DB opens, forced checkpoint or WAL bypass. SQLite/index support would require
   separate inspected acquisition scope; this plan starts with session JSON/JSONL.
6. Normalize atomically and replay idempotently using approved native identities;
   conflicts remain visible rather than last-write-wins. Source correction ordering
   and subtraction/reset semantics come from approved policy, not file position.
   A repository/session label alone does not bind work: manual maps reference exact
   evidence -> Run -> Change. Provider-backed attribution needs a verified join.

## Migration Plan

Separate implementation authorization, native evidence approval and policy review
precede source mappings. Verify synthetic relationship-preserving fixtures first.
Reuse core persistence; review additive schema needs and backup/recovery before
any migration. Rollback leaves original files and economic history intact.

## Verification

Cover overlap/replay, revised quantities, reset/finality, cache categories,
root/subagent boundaries, unknown versions, partial logs, private fields, malformed
input and manual binding with actual red/green evidence. Applicable repository and
supported-Linux assurance remain required; no native support is claimed by planning.
