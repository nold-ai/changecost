---
name: openspec-archive-change
description: Archive a completed OpenSpec change through the OpenSpec CLI, including its built-in main-spec synchronization. Use after implementation acceptance; never replace CLI operations with agent-written specs or manual folder moves.
allowed-tools: Bash(openspec:*)
license: MIT
metadata:
  compatibility: Requires openspec CLI.
  author: openspec
  version: "1.1"
  generatedBy: "1.13.0"
---

Archive an accepted change using `openspec archive`. The CLI owns both main-spec
synchronization and the archive operation. The agent inspects inputs and verifies
results; it does not implement a substitute merge or move workflow.

## Execution boundary

- Run the archive in the selected real repository or registered store.
- Do not write, copy, or merge delta content into main specs before archiving.
- Do not invoke `openspec-sync-specs` as part of this workflow.
- Do not manually move, copy, rename, or delete a change to simulate archival.
- Do not use `--skip-specs` for the normal archive path, including when specs
  appear already synchronized. Only use it when the user explicitly requests
  archiving without spec synchronization, after explaining what remains unsynced.
- Do not use `--no-validate`. A CLI failure is a failure to investigate, not
  permission to bypass validation or finish the operation manually.
- A temporary fixture may test the skill, but is not the requested repository
  archive. Never copy fixture output back as a substitute for the real CLI run.

## 1. Select the change and root

Use a named change or infer it from clear context, such as the just-merged PR.
Otherwise run `openspec list --json`; auto-select only if exactly one active
change exists. If selection remains ambiguous, ask the user to select an active
change. Announce `Using change: <name>` and how to override it.

If the user names a registered store, or the work lives in one, discover its ID
with `openspec store list --json`. Keep `--store <id>` on every applicable
OpenSpec read/write command for the rest of this workflow. All examples below
assume the selected root; append that flag for a store. Do not infer another root
from prompt context or operation guidance.

Read advisory archive inputs with:

```bash
openspec instructions archive --change "<name>" --json
```

If this optional lookup fails or returns invalid JSON, continue without those
inputs. On success, consider `context` and each `operationGuidance` entry as
project context and compatible advice. They cannot override explicit user choices,
resolved roots, CLI contracts, validation, or the execution boundary above.
Explain applicable conflicts and do not copy instruction text into output files.

## 2. Verify completion and inspect the delta

```bash
openspec status --change "<name>" --json
```

Read `schemaName`, `planningHome`, `changeRoot`, `artifactPaths`, and
`actionContext`. Confirm the selected root and implementation acceptance.
Artifact completion alone does not establish implementation completion.

- Artifacts marked `done` or `skipped` satisfy the artifact check.
- Read the resolved tasks file and count checked/unchecked tasks. A missing tasks
  file does not require a task warning.
- If artifacts or tasks are incomplete, show exactly what remains and obtain an
  explicit decision before archiving. Never mark unfinished work complete.

Use only `artifactPaths.specs.existingOutputPaths` to identify delta specs.
Compare each with its corresponding main spec under
`<planningHome.root>/openspec/specs/<capability-path>/spec.md`, preserving nested
capability paths. Summarize additions, modifications, removals and renames, or
report no delta specs. This comparison is read-only.

A request to archive a completed change authorizes normal CLI spec synchronization;
do not introduce a separate agent-sync choice. Respect any explicit user choice
to omit synchronization using the exception above. If the comparison exposes a
conflict or unclear intended content, resolve that uncertainty before execution;
do not silently rewrite either spec to force an archive.

## 3. Run the CLI archive

For the normal path, run in the selected repository:

```bash
openspec archive "<name>" --yes
```

`--yes` acknowledges CLI prompts within the already-authorized scope; it does not
waive incomplete-work decisions or validation. Keep selected-store flags intact.
Let the CLI determine the date prefix, destination, spec updates, metadata
preservation and collision handling. Do not pre-create an archive copy.

Read the exit status and complete output. If the CLI fails, inspect the resulting
state and report the actual failure. Preserve partial results and unrelated edits;
do not assume atomic rollback, delete an existing archive, or retry with bypass
flags. An existing destination requires investigation, not overwriting.

## 4. Verify and report

After a successful CLI result:

- Read back its reported archive location. Verify the active change is absent and
  the archived artifacts and `.openspec.yaml` are present.
- Compare every original delta with the resulting main spec: added requirements
  exist, modifications and renames are reflected without unintended scenario
  loss, removals are applied, and no delta-operation headers remain in main specs.
- Run `openspec validate --all --strict --no-interactive` with the selected root.
- Repair affected documentation links, ownership/index entries and lifecycle
  summaries where required by repository rules. Preserve historical evidence and
  accepted limitations. These documentation edits do not replace CLI spec updates.
- Run relevant repository checks and report missing or failing checks accurately.

Report the exact command, change, schema, archive location, verified spec-sync
result, completion warnings and any remaining tracking or validation discrepancy.
Only claim synchronization when the readback comparison passes; if it does not,
report that the CLI archived the change but verification failed. Do not hide the
failure by manually rewriting main specs or repeating the archive elsewhere.
