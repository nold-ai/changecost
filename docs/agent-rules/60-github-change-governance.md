# GitHub change governance

Use the repository's private **ChangeCost** organization project. Preserve repository
visibility, description and topics, including `token-economics`. Do not copy the
SpecFact hierarchy cache, module registry or release automation into this project.

- Track the approved pilot as native **Epic → Feature → User Story** issue types.
  Labels describe scope; they do not replace native types or parent relationships.
- Reuse `Epic`, `Feature`, `enhancement`, `openspec`, `change-proposal`, `finops`,
  `telemetry`, `architecture` and `QA` from SpecFact where applicable, preserving
  their names, colors and descriptions.
- Search all existing issues and projects before creating an item. Match the stable
  OpenSpec identifier/marker or exact feature/epic title. Ambiguous matches require
  inspection, not another issue. Keep closed items in the search to prevent duplicates.
- Use real parent/sub-issue and blocked-by relationships. Keep readable parent,
  child and prerequisite links in bodies and reciprocal issue links in proposals.
- Every change issue needs acceptance criteria, scope/non-goals, its OpenSpec ID,
  dependencies and verification expectations. Source tracking must describe planned
  work honestly; a planning PR does not close implementation stories.
- Keep [CHANGE_ORDER.md](../../openspec/CHANGE_ORDER.md) aligned with native relationships.
  Dependencies are implementation prerequisites; the graph must remain acyclic.
- New pilot items start **Todo**, with assignees and delivery dates unset. Do not infer
  schedules or mark implementation complete because planning artifacts exist.
- Read back types, parents, dependencies, labels, private project membership and
  status after mutations. Record actual verification in the PR, not local cache files.

A planning-only PR may link the whole backlog but must not use issue-closing keywords
for unfinished implementation. Rollback preserves history: revert the plan commit,
close abandoned issues and close the project if appropriate; do not delete records.
