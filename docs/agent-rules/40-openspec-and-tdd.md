# OpenSpec and test-driven development

OpenSpec 1.13.0 initialized this repository with the `spec-driven` schema and
shared `.agents/skills/` integration. `openspec/config.yaml` provides concise
context and artifact rules. No product spec or change is approved at bootstrap.

When the maintainer requests a behavior change:

1. Verify requested scope against the current repo; state uncertain assumptions.
2. Create a focused branch and OpenSpec change; define requirements and
   Given/When/Then scenarios before implementation.
3. Derive meaningful tests and run them before changing behavior. Confirm failures
   are caused by missing behavior, not broken tooling.
4. Implement the minimum behavior; rerun tests and relevant quality gates.
5. Record failing-before and passing-after commands, timestamps, exit outcomes,
   and summaries in `openspec/changes/<change-id>/TDD_EVIDENCE.md`.
6. Update documentation and record fresh review evidence for the final diff.
7. Validate with `openspec validate <change-id> --strict --no-interactive`.
8. Archive completed changes with `openspec archive <change-id>`; do not manually
   move folders or mark unfinished work complete.

Pure documentation/scaffold edits need relevant verification, not fabricated
runtime tests or a product capability spec. Generated skills describe workflow
mechanics; they do not authorize implementation beyond the user's scope.

No automatic issue hierarchy, roadmap, version bump, or release is required.
Use issue links when they already exist and help trace the requested change.
