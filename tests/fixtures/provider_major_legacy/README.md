# Fixed pre-change synthetic compatibility assets

These bytes were generated with the unchanged runtime at
`7df8be778f7c4a40992a4c048c77b6599fe4859c` before the major-compatibility source
edits on 2026-10-31 Europe/Berlin. They contain synthetic test rows and safe
portable records only. `sha256.json` freezes all nine original data assets.
The capture command was `PYTHONPATH=.:src .venv/bin/python /tmp/capture-major-legacy.py`.
The implementation workflow retains that script and exact command evidence locally.
Do not regenerate these fixtures using the changed implementation.

Code partial and final exports share an original store and preserve first provenance
and correction chains. Desktop has its own final export. The corresponding JSONL
files allow real reader replay. The Codex SQL dump contains an original capture and
the next session's frozen forecast. Its JSONL and forecast JSON are fixed separately.

SQLite `iterdump()` omits database pragmas. The restore test therefore supplies
literal `application_id=0x43435331` and `user_version=3`, grounded in the baseline
`src/changecost/sessions.py` constants and initialization/migration code. These
pragmas were not captured before implementation. The original SQL and manifest
bytes remain unchanged. Initial restore failures were setup errors, not TDD RED.

Recovery tests consume these fixed bytes, replay original sources, add new compatible
events and compare the complete old records and frozen forecast. This is synthetic
historical compatibility evidence, not native producer approval or full assurance.
