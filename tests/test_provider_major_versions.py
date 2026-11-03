"""Major compatibility without changing baseline proof, grammar or stored identity."""

import hashlib
import json
import sqlite3
from pathlib import Path

import pytest
from typer.testing import CliRunner

from changecost import claude_local as reader
from changecost.cli import app
from changecost.models import NativeUsage
from changecost.serialization import ContractError, dumps_bundle, loads_bundle
from changecost.store import Store
from tests.test_claude_desktop308 import (
    PROFILE,
    TERMINAL_PROFILE,
    _rehash_native_history,
    assistant,
    selection,
    terminal,
)
from tests.test_claude_local import TERMINAL, snapshot
from tests.test_codex_provisional_sessions import append, capture, source, start
from tests.test_sessions_cli import Journey

LEGACY = Path(__file__).parent / "fixtures/provider_major_legacy"
VALID = ["2.1.309", "2.3.0", "2.1.309-alpha.1+build.001"]
INVALID = [
    None,
    True,
    2,
    "",
    "2",
    "2.1",
    "2.1.309.0",
    "02.1.309",
    "2.01.309",
    "2.1.0309",
    "2.1.309-01",
    "2.1.309-",
    "2.1.309+",
    "2.1.309-a..b",
    "2.1.309+build..1",
    "2.1.309 ",
    " 2.1.309",
    "v2.1.309",
    "+2.1.309",
    "２.1.309",
    "2.1.309\n",
    "2.1.309_PRIVATE",
    "3.1.309",
    "2.1.0+" + "a" * 507,
]


def native(store):
    return [r for r in store.records() if isinstance(r, NativeUsage)]


@pytest.mark.parametrize("version", VALID + ["2.2.0"])
@pytest.mark.parametrize("profile", [PROFILE, TERMINAL_PROFILE])
def test_compatible_actual_producer_recovery_and_alias_replay(tmp_path, version, profile):
    rows = [assistant()] if profile == PROFILE else snapshot(terminal=TERMINAL)
    for row in rows:
        row["version"] = version
    selected = selection(tmp_path, rows, profile)
    store = Store(tmp_path / "db")
    result = reader.import_claude_project(store, selected)
    assert result.fact_count == 4
    assert result.inserted_fact_count == (4 if profile == PROFILE else 8)
    assert {r.producer.engine_version for r in native(store)} == {version}
    expected = reader._select_claude(profile).envelope["admission"]["producer"].copy()
    expected["engine_version"] = version
    assert all(r.producer.model_dump() == expected for r in native(store))
    assert all(r.ownership.state == "unknown" and r.model is None for r in native(store))
    before = store.export_bundle()
    recovered = Store(tmp_path / "recovered")
    recovered.import_bundle(loads_bundle(dumps_bundle(before)))
    alias = "claude-desktop-2" if profile == PROFILE else "claude-code-2"
    for target in (Store(store.path), recovered):
        for spelling in (profile, alias, profile, alias):
            replay = reader.import_claude_project(
                target, selected.model_copy(update={"profile_id": spelling})
            )
            assert replay.inserted_fact_count == replay.corrected_fact_count == 0
            assert replay.evidence_refs == result.evidence_refs
            assert target.records() == before.records


@pytest.mark.parametrize("profile", [PROFILE, TERMINAL_PROFILE])
@pytest.mark.parametrize("version", INVALID)
@pytest.mark.parametrize("existing", [False, True])
def test_bad_versions_are_private_and_atomic(tmp_path, profile, version, existing):
    store = Store(tmp_path / "db")
    make = assistant if profile == PROFILE else terminal
    if existing:
        reader.import_claude_project(store, selection(tmp_path, [make("old")], profile))
    before = store.path.read_bytes() if existing else None
    bad = make("bad")
    bad["version"] = version
    selected = selection(tmp_path, [make("good"), bad], profile)
    with pytest.raises(reader.ClaudeProjectImportError, match="^unsupported_producer:1$"):
        reader.import_claude_project(store, selected)
    assert (store.path.read_bytes() if store.path.exists() else None) == before


@pytest.mark.parametrize("marker", [None, "claude-desktop", "cli", "unknown"])
@pytest.mark.parametrize("shape", ["terminal", "partial", "child"])
def test_code_entrypoint_member_rejects_entire_batch(tmp_path, marker, shape):
    bad = terminal("bad")
    bad["entrypoint"] = marker
    if shape == "partial":
        bad["message"]["stop_reason"] = None
    if shape == "child":
        bad.update(isSidechain=True, agentId="agent")
    store = Store(tmp_path / "db")
    with pytest.raises(reader.ClaudeProjectImportError, match="^unsupported_producer:1$"):
        reader.import_claude_project(
            store, selection(tmp_path, [terminal("good"), bad], TERMINAL_PROFILE)
        )
    assert not store.path.exists()


@pytest.mark.parametrize("profile", [PROFILE, TERMINAL_PROFILE])
@pytest.mark.parametrize("reverse", [False, True])
def test_cross_version_collision_both_orders_and_distinct_events(tmp_path, profile, reverse):
    make = assistant if profile == PROFILE else terminal
    versions = ["2.1.309", "2.3.0"]
    if reverse:
        versions.reverse()
    store = Store(tmp_path / "db")
    a, b = make(), make()
    a["version"], b["version"] = versions
    reader.import_claude_project(store, selection(tmp_path, [a], profile))
    before = store.path.read_bytes()
    with pytest.raises(reader.ClaudeProjectImportError):
        reader.import_claude_project(store, selection(tmp_path, [make("new"), b], profile))
    assert store.path.read_bytes() == before
    distinct = make("distinct")
    distinct["version"] = versions[1]
    reader.import_claude_project(store, selection(tmp_path, [distinct], profile))
    assert len(native(store)) == 8


@pytest.mark.parametrize("desktop_first", [False, True])
def test_same_version_cross_profile_collision(tmp_path, desktop_first):
    store = Store(tmp_path / "db")
    choices = [(PROFILE, assistant()), (TERMINAL_PROFILE, terminal())]
    if desktop_first:
        choices.reverse()
    for _, row in choices:
        row["version"] = "2.1.309"
    profile, row = choices[0]
    reader.import_claude_project(store, selection(tmp_path, [row], profile))
    before = store.path.read_bytes()
    profile, row = choices[1]
    with pytest.raises(reader.ClaudeProjectImportError):
        reader.import_claude_project(store, selection(tmp_path, [row], profile))
    assert store.path.read_bytes() == before


@pytest.mark.parametrize("profile", [PROFILE, TERMINAL_PROFILE])
@pytest.mark.parametrize("fault", ["version-major", "version-malformed", "client-build", "surface"])
def test_rehashed_portable_producer_policy_rejects_atomically(tmp_path, profile, fault):
    store = Store(tmp_path / "db")
    make = assistant if profile == PROFILE else terminal
    reader.import_claude_project(store, selection(tmp_path, [make()], profile))
    payload = json.loads(dumps_bundle(store.export_bundle()))
    for record in payload["records"]:
        if record["kind"] != "native_usage":
            continue
        producer = record["producer"]
        if fault.startswith("version"):
            producer["engine_version"] = "3.1.309" if fault == "version-major" else "2.1.309-01"
        else:
            producer["client_build" if fault == "client-build" else "client_surface"] = "forged"
    _rehash_native_history(reader, payload)
    before = store.path.read_bytes()
    with pytest.raises(ContractError):
        store.import_bundle(loads_bundle(json.dumps(payload)))
    assert store.path.read_bytes() == before
    fresh = Store(tmp_path / "fresh")
    with pytest.raises(ContractError):
        fresh.import_bundle(loads_bundle(json.dumps(payload)))
    assert not fresh.path.exists()


def test_fixed_baseline_graphs_recover_replay_and_preserve_all_old_records(tmp_path):
    manifest = json.loads((LEGACY / "sha256.json").read_text())
    for name, digest in manifest.items():
        assert hashlib.sha256((LEGACY / name).read_bytes()).hexdigest() == digest
    for label, profile in (
        ("code-partial", TERMINAL_PROFILE),
        ("code-final", TERMINAL_PROFILE),
        ("desktop", PROFILE),
    ):
        store = Store(tmp_path / label)
        bundle = loads_bundle((LEGACY / (label + ".json")).read_text())
        store.import_bundle(bundle)
        raw = (LEGACY / (label + ".jsonl")).read_bytes()
        path = tmp_path / (label + ".jsonl")
        path.write_bytes(raw)
        selected = reader.ClaudeProjectSelection(
            repository_id="repo",
            path=path,
            profile_id=profile,
            expected_sha256=hashlib.sha256(raw).hexdigest(),
        )
        assert reader.import_claude_project(store, selected).inserted_fact_count == 0
        assert store.records() == bundle.records
        row = assistant("new") if profile == PROFILE else terminal("new")
        row["version"] = "2.2.0"
        reader.import_claude_project(store, selection(tmp_path, [row], profile))
        assert all(record in store.records() for record in bundle.records)
        recovered = Store(tmp_path / (label + "-recovered"))
        recovered.import_bundle(loads_bundle(dumps_bundle(store.export_bundle())))
        assert reader.import_claude_project(recovered, selected).inserted_fact_count == 0
        assert recovered.records() == store.records()


@pytest.mark.parametrize("version", ["0.163.1", "0.164.0-alpha.10.2", "0.165.1+build.001"])
def test_codex_fixed_history_cross_minor_cohort_append_and_rewrite(tmp_path, version):
    j = Journey(tmp_path)
    with sqlite3.connect(j.db) as db:
        db.executescript((LEGACY / "codex.sql").read_text())
        db.execute("PRAGMA application_id=0x43435331")
        db.execute("PRAGMA user_version=3")
    frozen = json.loads((LEGACY / "codex-forecast.json").read_text())
    assert j.invoke("show", "legacy-b")["forecast"] == frozen
    old = tmp_path / "old.jsonl"
    old.write_bytes((LEGACY / "codex.jsonl").read_bytes())
    before = j.db.read_bytes()
    capture(j, old, name="legacy-a")
    assert j.db.read_bytes() == before
    start(j, "new")
    path = source(tmp_path, totals=(300,), identity="new", version=version)
    result = capture(j, path, name="new")
    assert result["capture"]["snapshot"]["producer_version"] == version
    assert j.invoke("show", "legacy-b")["forecast"] == frozen
    future = start(j, "future")["forecast"]
    assert future["sample_count"] == 2 and future["amount"] == "250"
    append(path, 400)
    capture(j, path, name="new", revision=1, reason="append")
    before = j.db.read_bytes()
    raw = path.read_bytes()
    path.write_bytes(raw.replace(version.encode(), b"0.166.0"))
    capture(j, path, name="new", revision=2, reason="rewrite", ok=False)
    assert j.db.read_bytes() == before
    start(j, "duplicate")
    before = j.db.read_bytes()
    capture(j, path, name="duplicate", ok=False)
    assert j.db.read_bytes() == before
    assert j.invoke("show", "legacy-b")["forecast"] == frozen


def test_cli_stable_desktop_alias_and_help(tmp_path):
    row = assistant()
    row["version"] = "2.1.309"
    selected = selection(tmp_path, [row])
    args = [
        "--db",
        str(tmp_path / "db"),
        "settle",
        "--repository-id",
        "repo",
        "--import-claude-project",
        str(selected.path),
        "--source-profile",
        "claude-desktop-2",
        "--source-sha256",
        selected.expected_sha256,
    ]
    runner = CliRunner()
    first = runner.invoke(app, args)
    assert first.exit_code == 0, first.output
    assert json.loads(first.stdout)["inserted_fact_count"] == 4
    assert json.loads(runner.invoke(app, args).stdout)["replayed_fact_count"] == 4
    help_result = runner.invoke(app, ["settle", "--help"])
    assert "claude-desktop-2" in help_result.stdout and "claude-code-2" in help_result.stdout


@pytest.mark.parametrize("reported", INVALID + ["1.0.0", "0.164.0"])
def test_strict_shared_version_predicate_rejects(reported):
    from changecost.producer_versions import same_major

    assert not same_major(reported, "2.1.215")


@pytest.mark.parametrize("reported", VALID + ["2.0.0-0", "2.0.0-01a+001", "2.0.0+001"])
def test_strict_shared_version_predicate_preserves_full_syntax(reported):
    from changecost.producer_versions import same_major

    assert same_major(reported, "2.1.215")
    assert same_major(reported, "2.1.308")


def test_major_comparison_has_no_integer_conversion_or_unbounded_input():
    from changecost.producer_versions import same_major

    major = "9" * 500
    assert same_major(major + ".0.0", major + ".1.1")
    assert not same_major(major + "9.0.0", major + ".0.0")
    assert not same_major("2.0.0+" + "a" * 507, "2.0.0")


@pytest.mark.parametrize(
    "version", ["1.0.0", "0.164", "0.164.0-01", "0.164.0_PRIVATE", "０.164.0", None]
)
def test_codex_new_policy_bad_headers_leave_all_bytes_unchanged(tmp_path, version):
    j = Journey(tmp_path)
    start(j, "a")
    before = j.db.read_bytes()
    path = source(tmp_path, version=version)
    raw = path.read_bytes()
    error = capture(j, path, ok=False)
    assert error["code"] == "unsupported_source_header"
    assert "PRIVATE" not in json.dumps(error)
    assert j.db.read_bytes() == before and path.read_bytes() == raw


@pytest.mark.parametrize(
    "profile,alias,make",
    [(PROFILE, "claude-desktop-2", assistant), (TERMINAL_PROFILE, "claude-code-2", terminal)],
)
def test_alias_first_persists_only_canonical_profile(tmp_path, profile, alias, make):
    store = Store(tmp_path / "db")
    row = make()
    row["version"] = "2.2.0"
    selected = selection(tmp_path, [row], alias)
    first = reader.import_claude_project(store, selected)
    before = store.export_bundle()
    assert {r.profile for r in before.records if r.kind == "evidence"} == {profile}
    assert (
        reader.import_claude_project(
            store, selected.model_copy(update={"profile_id": profile})
        ).evidence_refs
        == first.evidence_refs
    )
    assert store.records() == before.records


def test_catalogue_rejects_alias_canonical_collision(monkeypatch):
    envelopes = [copy_entry.envelope.copy() for copy_entry in reader._claude_admissions()]
    envelopes[0]["profile_id"] = "claude-desktop-2"

    class Resource:
        def __init__(self, name=None):
            self.name = name

        def joinpath(self, name):
            return Resource(name)

        def read_text(self):
            return json.dumps(envelopes[0 if self.name == "claude_admission.json" else 1])

    monkeypatch.setattr(reader, "files", lambda _: Resource())
    with pytest.raises(reader.ClaudeProjectImportError, match="unsupported_profile"):
        reader._claude_admissions()
