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
remains empty. See [native evidence requests](../../../docs/research/adaptive-demand-evidence.md)
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

The parent preparation chat is the sole writer. Independent reviewers are
read-only. Preparation can complete as To-Validate while runtime remains blocked.

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
