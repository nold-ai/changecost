.PHONY: check hygiene spec-check review

check: hygiene spec-check

hygiene:
	pre-commit run --all-files

spec-check:
	OPENSPEC_TELEMETRY=0 openspec validate --all --strict --no-interactive

review:
	mkdir -p .specfact
	specfact code review run --scope full --enforcement full --json --out .specfact/code-review.json
