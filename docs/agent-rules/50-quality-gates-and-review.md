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
