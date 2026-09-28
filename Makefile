.PHONY: check hygiene lock lint format types test docs index metadata workflow build audit review spec-check generate

BASE_REF ?=
MANIFEST ?=
QUALITY = uv run --locked python -m quality
INPUTS = --base "$(BASE_REF)" $(if $(MANIFEST),--manifest "$(MANIFEST)",)

check:
	$(QUALITY) check $(INPUTS)

hygiene lock lint types docs index metadata workflow build audit review:
	$(QUALITY) $@ $(INPUTS)

test:
	uv run --locked python -m pytest

format:
	uv run --locked ruff format src quality tests

spec-check:
	OPENSPEC_TELEMETRY=0 openspec validate --all --strict --no-interactive

generate:
	$(QUALITY) index --write
