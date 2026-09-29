# Quality gates and review

## Foundation gates

The foundation now provides shared validators; see the executable contract and
setup in [the gate guide](../development/quality-gates.md). Run `make check` with
an explicit `BASE_REF` and an intended-file manifest before staging new files.
Local/CI checks cover hygiene, OpenSpec, locked resolution, formatting/lint,
typing/tests, documentation ownership/links, generated references, metadata,
workflow syntax, package builds, dependencies and applicable SpecFact review.
Missing tooling or analyzer coverage remains a failed/incomplete gate.

SpecFact CLI 0.55.4 and module 0.50.1 are contributor tooling, never package runtime.
The current macOS controller reports unsupported capsule execution; run the full
review in supported Linux x86-64 before claiming it passed. Keep actual report,
versions, content digest and outcomes in ignored .specfact and summarize them in
TDD_EVIDENCE.md. Review evidence supplements tests and security analysis.

Keep original research hashes unchanged. Do not fabricate product TDD for docs-only
work; record real negative and repaired fixtures for behavior and gate changes.
Resolve findings at every severity or document a narrow justified exception.

## Bounded review sessions

Input generations depend only on recorded refresh counts, not caller IDs. Automatic
binding atomically selects an unused event identity; retries preserve existing IDs
and counters. Older incompatible epoch receipts require recovery.
Packet status and evidence must describe one loaded revision; the watcher uses
that same packet for changed-output exit decisions. Required event strings reject
blank/Unicode-whitespace-only values, including budget-extension approvers.
Exact-limit completion is allowed only when no family investigation remains.
Fractional extensions and elapsed measurements use the same canonical summation
rule. Overflow rejects updates atomically and malformed histories require recovery;
unknown usage stays unknown.
Every refresh validates current changed-path coverage. Changing authorized paths
requires an explicitly referenced approved scope manifest; packets retain both
the original contract and recaptured current manifest.
Integer counters retain exact nonnegative values without floating conversion;
unrepresentable floating measurements reject atomically with controlled recovery
for malformed persisted history.
Resolved threads need explicit reviewer-evidence coverage of stable thread/comment
identities and content; new/edited reports invalidate it. Local unresolved findings
and remote unresolved status remain independent blockers.
Observation epochs are explicit collection-time facts. Missing, malformed or stale
epochs remain incomplete on ingestion; error observations without epochs are retained
to invalidate earlier passing monitoring and cannot supply report receipts.

Schema-6 contracts name the PR target ref/SHA separately from the comparison base.
Retargeting or target advancement invalidates monitoring. Explicit atomic base
adoption retains counters but requires a new evidence epoch: local results carry
their original full binding, and required remote positives postdate adoption.
Preserve older receipts for recovery; do not invent missing base provenance.
Required reviewer requests remain pending even after earlier same-head results.
Missing/malformed requested-user metadata or changes during collection are incomplete;
removing a request restores only evidence that still satisfies the other gates.

For review/fix work, initialize the ignored local record with
`python -m quality.review_session init <change-id> --json <contract.json>`. Before
each correction batch or publication, inspect its `status`. An escape after a
finding family's correction requires investigation; an escape after investigation, three
batches, 90 active minutes, a pending scope decision, or incomplete monitor evidence
requires replanning. A maintainer-recorded extension retains existing counters.
Declare nonempty `required_checks` names and explicit `required_statuses` contexts
(an empty status list is allowed). A missing expected identity blocks completion.
Review inputs include Git HEAD, working contents and staged blob identities/modes.
An explicit `advance_head` refresh invalidates earlier passing evidence even if
HEAD is unchanged; keep the historical receipt and obtain fresh evidence.
Missing active-time measurements block completion: record explicit measured minutes
after the latest input refresh. An effective current-head changes-requested review is
blocking, including top-level review bodies without inline threads. Required
reviewers must have a latest APPROVED or COMMENTED result.
Comments, pending submissions and dismissal of another review cannot clear that
objection. Only a later approval or a fresh snapshot showing the original rejecting
review dismissed can clear it.
Use exact REST logins, including `[bot]`, and bind the repository/PR once. Schema-6
replay reconciles all cached fields; missing or incompatible history requires
recovery, never reinitialization. Final published inputs must be clean. Exclude
non-findings from family escalation while retaining genuine fixed recurrences.
The initial typed scope and path/hash manifest must match real inputs and existing
base/head commits, including changed/staged/untracked paths. Explicit `<absent>`
entries permit future intended files; older receipts require recovery.

`packet` retains scope, unresolved findings and evidence across context windows.
`watch` is read-only and uses REST pagination with `--slurp` for checks/statuses/reviews/comments
and GraphQL `reviewThreads` pagination for thread resolution/outdated state and
comments. It requires a current-head non-pending result from each contract-named
GitHub reviewer, polls changed nonterminal state with 15/30/60-second backoff, and
returns `wait` after 30 minutes without progress without resetting budget counters.
It reports only meaningful GitHub changes or errors and does not make incomplete
external evidence look complete. This workflow control does not enlarge the
documented CI trust boundary or authenticate PR-controlled code.
Requests, pagination and sleep consume the same remaining no-progress deadline.
The helper stays pending when a provider emits only a clean summary without a REST
review; retain separately verified coordinator evidence and disclose this limit.
Local terminal results are still emitted when the remote snapshot is unchanged;
the no-progress deadline checks current local status before reporting wait.
Initialization, head refresh and replay share full SHA-1/SHA-256 ID validation.

## CodeRabbit review policy

[.coderabbit.yaml](../../.coderabbit.yaml) adapts the SpecFact review configuration
for this standalone project. Automatic reviews target `main`, skip drafts and
review subsequent pushes. The quiet profile and review instructions request only
high/critical and medium defects (P0–P2), with concrete impact. Low-severity nits,
grammar/Markdown lint, decorative summaries and metadata suggestions are suppressed;
repository quality gates still run independently.

The [official configuration reference](https://docs.coderabbit.ai/reference/configuration)
and v2 schema were checked on 2026-09-28 (Europe/Berlin). They expose no native
severity cutoff: these instructions are a review policy, not a guaranteed alert
filter. Verify actual bot output and configuration acceptance on the PR. Automatic
reviews may pause after five reviewed commits by default; if paused during a fix
loop, explicitly request another review instead of treating the pause as a pass.

Knowledge context is repository-local, external integrations are disabled, and
chat requires an organization member's mention. Automatic approval, label/reviewer
assignment, issue planning and generated fixes are disabled. No account-wide
settings or subscription changes are implied. A completed review of the current
head plus green applicable checks is required before reporting the loop complete;
absence of a bot response is not a passing review. Revert the configuration commit
to roll back this policy.


The staged commit hook uses HEAD only when no explicit comparison base is supplied.
Keep full aggregate/CI comparison bases explicit. Hosted capsule setup has now run;
read native current-head analyzer results rather than inferring complete assurance
from successful capsule launch. The [gate guide](../development/quality-gates.md)
records the disposable hosted-runner trust model and pinned analyzer compatibility.


Keep external-tool host proofs in the required gate path when a signed capsule
cannot perform the tool's own interpreter probe. The uv missing/stale/repaired
fixture runs through the lock leaf for local, hook and CI invocations; its move
out of pytest collection does not waive the proof or allow analyzer failures.

Verify the final complete staged snapshot with BASE_REF unset as well as the
explicit aggregate comparison. A passing main-branch comparison does not prove
that incremental documentation freshness passes against the hook's HEAD baseline.
For negative tool fixtures, show the same input succeeds when the guarded check
is removed or repaired; an unrelated resolution failure is not lock-check proof.

Interpret native review verdicts using the installed report contract: both PASS
and PASS_WITH_ADVISORY can accompany complete passing assurance. Keep the digest,
required-member execution/outcome, unknown-evidence and exit-code checks intact;
record dispositions for advisories instead of treating their presence as failure
or silently discarding them.
