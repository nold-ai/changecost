import hashlib
import importlib
import json
import os
from datetime import UTC, datetime

import pytest
from rich.text import Text
from typer.testing import CliRunner

from changecost.cli import app
from changecost.models import RunRef
from changecost.operations import bind_evidence, register_change, register_run
from changecost.serialization import ContractError, dumps_bundle, loads_bundle
from changecost.store import Store

NOW = datetime(2026, 10, 28, tzinfo=UTC)
PARTIAL = (11, 1, 13, 12)
TERMINAL = (12, 29, 14, 13)
SOURCE_FIELDS = (
    "input_tokens",
    "output_tokens",
    "cache_creation_input_tokens",
    "cache_read_input_tokens",
)
CATEGORIES = (
    "input_tokens",
    "output_tokens",
    "cache_write_input_tokens",
    "cached_input_tokens",
)


def assistant(block, values=PARTIAL, stop=None, event="request"):
    return {
        "type": "assistant",
        "version": "2.1.215",
        "uuid": "PRIVATE-block-" + block,
        "sessionId": "PRIVATE-session",
        "agentId": "PRIVATE-agent",
        "isSidechain": True,
        "requestId": "PRIVATE-request-" + event,
        "message": {
            "id": "PRIVATE-message-" + event,
            "role": "assistant",
            "stop_reason": stop,
            "model": "PRIVATE-unverified-model",
            "content": [{"type": "text", "text": "PRIVATE-PROMPT"}],
            "usage": dict(zip(SOURCE_FIELDS, values, strict=True)),
        },
    }


def snapshot(values=PARTIAL, terminal=None, reason="end_turn", event="request"):
    rows = [
        assistant(event + "-1", values, event=event),
        assistant(event + "-2", values, event=event),
    ]
    if terminal is not None:
        rows.append(assistant(event + "-3", terminal, reason, event))
    return rows


@pytest.fixture
def reader(monkeypatch):
    module = importlib.import_module("changecost.claude_local")
    from importlib.resources import files

    envelope = json.loads(files("changecost").joinpath("claude_admission.json").read_text())
    envelope.update(profile_id="synthetic-only", profile_digest="b" * 64, approval_digest="c" * 64)
    monkeypatch.setattr(
        module, "_claude_admissions", lambda: (module._ApprovedClaude("terminal215", envelope),)
    )
    return module, envelope


def selection(reader, tmp_path, rows, name="PRIVATE-source.jsonl"):
    module, envelope = reader
    raw = b"".join(json.dumps(row).encode() + b"\n" for row in rows)
    path = tmp_path / name
    path.write_bytes(raw)
    return module.ClaudeProjectSelection(
        repository_id="repo",
        path=path,
        profile_id=envelope["profile_id"],
        expected_sha256=hashlib.sha256(raw).hexdigest(),
    )


def facts(store):
    return [record for record in store.records() if record.kind == "native_usage"]


def test_partial_refinement_both_replays_and_actual_recovery(reader, tmp_path):
    module, _ = reader
    store = Store(tmp_path / "db", clock=lambda: NOW)
    a = selection(reader, tmp_path, snapshot(), "PRIVATE-a.jsonl")
    b = selection(reader, tmp_path, snapshot(terminal=TERMINAL), "PRIVATE-b.jsonl")
    first = module.import_claude_project(store, a)
    assert first.inserted_fact_count == 4 and first.corrected_fact_count == 0
    assert len(first.evidence_refs) == 1 and first.evidence_refs[0].kind == "evidence"
    second = module.import_claude_project(store, b)
    assert second.corrected_fact_count == 4
    assert second.evidence_refs == first.evidence_refs
    before = store.export_bundle()
    assert len(facts(store)) == 8
    final = {f.source_category: f.quantity for f in facts(store) if f.finality == "final"}
    assert final == dict(zip(CATEGORIES, TERMINAL, strict=True))
    _assert_refinement_provenance(facts(store))
    restored = Store(tmp_path / "restored", clock=lambda: NOW)
    restored.import_bundle(loads_bundle(dumps_bundle(before)))
    for target in (Store(store.path, clock=lambda: NOW), restored):
        _assert_replayed_history(module, target, (a, b, a, b), first.evidence_refs, before.records)
    assert "PRIVATE" not in dumps_bundle(before)
    _assert_unknown_diagnostic_authority(facts(store))


def _assert_refinement_provenance(records):
    originals = {f.source_category: f for f in records if f.previous is None}
    for fact in records:
        original = originals[fact.source_category]
        assert fact.first_acquisition_digest == original.first_acquisition_digest
        assert fact.first_admission == original.first_admission
        assert fact.evidence == original.evidence
        if fact.finality == "final":
            assert fact.previous is not None
            assert fact.previous.record_id == original.record_id
            assert fact.reason == "claude-serialized-stage-refinement"


def _assert_replayed_history(module, target, selections, evidence_refs, records):
    for old in selections:
        replay = module.import_claude_project(target, old)
        assert replay.inserted_fact_count == replay.corrected_fact_count == 0
        assert replay.replayed_fact_count == 4
        assert replay.evidence_refs == evidence_refs
    assert target.records() == records


def _assert_unknown_diagnostic_authority(records):
    assert all(
        f.backend_presence == f.scope_completeness == f.interval.state == "unknown" for f in records
    )
    assert all(
        f.ownership.state == "unknown" and f.coverage == "partial_observed_subset" for f in records
    )


def test_quantity_equal_stage_advancement_still_appends_four(reader, tmp_path):
    module, _ = reader
    store = Store(tmp_path / "db", clock=lambda: NOW)
    module.import_claude_project(store, selection(reader, tmp_path, snapshot()))
    result = module.import_claude_project(
        store, selection(reader, tmp_path, snapshot(terminal=PARTIAL))
    )
    assert result.corrected_fact_count == 4
    assert len(facts(store)) == 8
    assert {f.finality for f in facts(store)} == {"partial", "final"}


def test_equal_terminal_reason_change_replays_after_valid_grammar(reader, tmp_path):
    module, _ = reader
    store = Store(tmp_path / "db", clock=lambda: NOW)
    first = module.import_claude_project(
        store, selection(reader, tmp_path, [assistant("a", TERMINAL, "end_turn")])
    )
    before = store.export_bundle()
    replay = module.import_claude_project(
        store, selection(reader, tmp_path, [assistant("b", TERMINAL, "tool_use")])
    )
    assert replay.replayed_fact_count == 4
    assert replay.inserted_fact_count == replay.corrected_fact_count == 0
    assert replay.evidence_refs == first.evidence_refs
    assert store.export_bundle() == before
    assert all("source_stop_reason" not in f.model_dump() for f in facts(store))


@pytest.mark.parametrize(
    "variant",
    ["missing-retained", "changed-terminal", "unseen-partial", "mixed-reasons", "changed-partial"],
)
def test_unsupported_revision_rolls_back_other_valid_new_facts(reader, tmp_path, variant):
    module, _ = reader
    store = Store(tmp_path / "db", clock=lambda: NOW)
    module.import_claude_project(store, selection(reader, tmp_path, snapshot()))
    if variant != "missing-retained":
        module.import_claude_project(
            store, selection(reader, tmp_path, snapshot(terminal=TERMINAL))
        )
    before = store.export_bundle()
    rows = {
        "missing-retained": [assistant("terminal", TERMINAL, "end_turn")],
        "changed-terminal": [assistant("terminal", (12, 30, 14, 13), "end_turn")],
        "unseen-partial": snapshot(values=(11, 2, 13, 12)),
        "mixed-reasons": [
            assistant("one", TERMINAL, "end_turn"),
            assistant("two", TERMINAL, "tool_use"),
        ],
        "changed-partial": snapshot(values=(11, 2, 13, 12), terminal=TERMINAL),
    }[variant]
    rows += [assistant("new", TERMINAL, "end_turn", "new")]
    with pytest.raises(ContractError):
        module.import_claude_project(store, selection(reader, tmp_path, rows))
    assert store.export_bundle() == before


def test_terminal_first_rejects_unseen_earlier_partial(reader, tmp_path):
    module, _ = reader
    store = Store(tmp_path / "db", clock=lambda: NOW)
    module.import_claude_project(
        store, selection(reader, tmp_path, [assistant("terminal", TERMINAL, "end_turn")])
    )
    before = store.export_bundle()
    with pytest.raises(ContractError):
        module.import_claude_project(store, selection(reader, tmp_path, snapshot()))
    assert store.export_bundle() == before


@pytest.mark.parametrize("missing", ["requestId", "sessionId", "message.id"])
@pytest.mark.parametrize("error_looking", [False, True])
def test_missing_identity_never_becomes_zero_or_error_skip(
    reader, tmp_path, missing, error_looking
):
    module, _ = reader
    row = assistant("a", (0, 0, 0, 0), "end_turn")
    if error_looking:
        row.update(isApiErrorMessage=True, error="PRIVATE-error", apiErrorStatus=529)
    if missing == "message.id":
        del row["message"]["id"]
    else:
        del row[missing]
    store = Store(tmp_path / "db")
    with pytest.raises(ContractError) as error:
        module.import_claude_project(store, selection(reader, tmp_path, [row]))
    assert "PRIVATE" not in str(error.value)
    assert not store.path.exists()


@pytest.mark.parametrize(
    "change", ["request", "message", "duplicate-uuid", "producer", "sidechain"]
)
def test_identity_and_producer_conflicts_reject_before_persistence(reader, tmp_path, change):
    module, _ = reader
    rows = snapshot()
    if change == "request":
        rows[1]["message"]["id"] = "PRIVATE-other-message"
    elif change == "message":
        rows[1]["requestId"] = "PRIVATE-other-request"
    elif change == "duplicate-uuid":
        rows[1]["uuid"] = rows[0]["uuid"]
        rows[1]["message"]["usage"]["output_tokens"] = 2
    elif change == "producer":
        rows[1]["version"] = "2.1.257"
    else:
        rows[1]["isSidechain"] = False
    store = Store(tmp_path / "db")
    with pytest.raises(ContractError):
        module.import_claude_project(store, selection(reader, tmp_path, rows))
    assert not store.path.exists()


def test_missing_zero_cache_exclusions_and_exact_manual_binding(reader, tmp_path):
    module, _ = reader
    row = assistant("a", (None, 0, 13, 12), "end_turn")
    del row["message"]["usage"]["input_tokens"]
    row["message"]["usage"].update(
        cache_creation={"ephemeral_5m_input_tokens": 100, "ephemeral_1h_input_tokens": 200},
        server_tool_use={"web_search_requests": 9},
        total_tokens=999,
        reasoning_tokens=555,
    )
    selected = selection(reader, tmp_path, [row])
    original = selected.path.read_bytes()
    store = Store(tmp_path / "db", clock=lambda: NOW)
    result = module.import_claude_project(store, selected)
    assert {f.source_category: f.quantity for f in facts(store)} == dict(
        zip(CATEGORIES, (None, 0, 13, 12), strict=True)
    )
    assert selected.path.read_bytes() == original
    register_change(store, "repo", "change")
    run = RunRef(repository_id="repo", provider="Claude", surface="project-jsonl", run_id="run")
    register_run(store, run, "change")
    evidence_id = result.evidence_refs[0].record_id
    bind_evidence(store, evidence_id, run)
    before = store.export_bundle()
    bind_evidence(store, evidence_id, run)
    assert store.export_bundle() == before
    forbidden = {"demand_observation", "demand_policy", "source_coverage", "economic_evidence"}
    assert not forbidden & {r.kind for r in store.records()}


@pytest.mark.parametrize(
    "raw",
    [
        b'{"x":1,"x":2}\n',
        b'{"x":NaN}\n',
        b'{"x":1e9999}\n',
        b'{"x":',
        b"\n",
        b'{"x":' + b"[" * 33 + b"0" + b"]" * 33 + b"}\n",
        b"{}\n" * 10001,
        b"x" * 10485761,
        b'{"x":' + b"1" * 4097 + b"}\n",
    ],
    ids=[
        "duplicate",
        "nonfinite",
        "overflow",
        "truncated",
        "blank",
        "depth",
        "records",
        "bytes",
        "digits",
    ],
)
def test_acquisition_limits_remain_private_and_atomic(reader, tmp_path, raw):
    module, _ = reader
    selected = selection(reader, tmp_path, snapshot())
    selected.path.write_bytes(raw)
    selected = selected.model_copy(update={"expected_sha256": hashlib.sha256(raw).hexdigest()})
    store = Store(tmp_path / "db")
    with pytest.raises(ContractError) as error:
        module.import_claude_project(store, selected)
    assert "PRIVATE" not in str(error.value) and str(selected.path) not in str(error.value)
    assert not store.path.exists()


def test_symlink_components_and_unstable_read_reject(reader, tmp_path, monkeypatch):
    module, _ = reader
    selected = selection(reader, tmp_path, snapshot())
    link = tmp_path / "link"
    link.symlink_to(selected.path)
    parent = tmp_path / "parent"
    parent.symlink_to(tmp_path, target_is_directory=True)
    fifo = tmp_path / "fifo"
    os.mkfifo(fifo)
    for path in (link, parent / selected.path.name, fifo, tmp_path):
        with pytest.raises(ContractError):
            module.import_claude_project(
                Store(tmp_path / "db"), selected.model_copy(update={"path": path})
            )
        assert not (tmp_path / "db").exists()
    original = os.read
    changed = False

    def mutate(descriptor, count):
        nonlocal changed
        data = original(descriptor, count)
        if not changed:
            changed = True
            with selected.path.open("ab") as stream:
                stream.write(b" ")
        return data

    monkeypatch.setattr(module.os, "read", mutate)
    with pytest.raises(ContractError):
        module.import_claude_project(Store(tmp_path / "db"), selected)
    assert not (tmp_path / "db").exists()


def test_profile_hash_and_repository_mismatch_reject(reader, tmp_path):
    module, _ = reader
    selected = selection(reader, tmp_path, snapshot())
    for update in ({"profile_id": "unsupported"}, {"expected_sha256": "0" * 64}):
        store = Store(tmp_path / "db")
        with pytest.raises(ContractError):
            module.import_claude_project(store, selected.model_copy(update=update))
        assert not store.path.exists()
    store = Store(tmp_path / "db", clock=lambda: NOW)
    module.import_claude_project(store, selected)
    before = store.export_bundle()
    with pytest.raises(ContractError):
        module.import_claude_project(
            store, selected.model_copy(update={"repository_id": "foreign"})
        )
    assert store.export_bundle() == before


@pytest.mark.parametrize(
    "extra",
    [
        ["--compute"],
        ["--import-codex", "PRIVATE"],
        ["--import-evidence", "PRIVATE"],
        ["--provider", "Claude"],
        ["--change-id", "change"],
        ["--correct-outcome"],
        ["--operation-id", "x"],
    ],
)
def test_cli_conflicts_are_recognized_before_acquisition(reader, tmp_path, monkeypatch, extra):
    module, _ = reader
    selected = selection(reader, tmp_path, snapshot())

    def forbidden(_path):
        pytest.fail("source acquisition preceded mode validation")

    monkeypatch.setattr(module, "_acquire", forbidden)
    result = CliRunner().invoke(
        app,
        [
            "--db",
            str(tmp_path / "db"),
            "settle",
            "--repository-id",
            "repo",
            "--import-claude-project",
            str(selected.path),
            "--source-profile",
            selected.profile_id,
            "--source-sha256",
            selected.expected_sha256,
            *extra,
        ],
    )
    assert result.exit_code == 2
    assert "No such option" not in result.output
    assert not (tmp_path / "db").exists()


def test_cli_success_returns_safe_exact_references(reader, tmp_path):
    _, _ = reader
    selected = selection(reader, tmp_path, snapshot(terminal=TERMINAL))
    result = CliRunner().invoke(
        app,
        [
            "--db",
            str(tmp_path / "db"),
            "settle",
            "--repository-id",
            "repo",
            "--import-claude-project",
            str(selected.path),
            "--source-profile",
            selected.profile_id,
            "--source-sha256",
            selected.expected_sha256,
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["fact_count"] == 4
    assert payload["evidence_refs"][0]["kind"] == "evidence"
    assert "PRIVATE" not in result.output


def test_cli_help_exposes_selected_claude_project_mode():
    result = CliRunner().invoke(app, ["settle", "--help"], env={"COLUMNS": "160"})
    assert result.exit_code == 0
    assert "--import-claude-project" in Text.from_ansi(result.output).plain


@pytest.mark.parametrize(
    "fault",
    ["missing-stop", "unknown-stop", "malformed-stop", "bool", "negative", "fraction", "string"],
)
def test_stop_and_quantity_grammar_is_strict(reader, tmp_path, fault):
    module, _ = reader
    row = assistant("one")
    if fault == "missing-stop":
        del row["message"]["stop_reason"]
    elif fault in {"unknown-stop", "malformed-stop"}:
        row["message"]["stop_reason"] = "max_tokens" if fault == "unknown-stop" else {}
    else:
        row["message"]["usage"]["input_tokens"] = {
            "bool": True,
            "negative": -1,
            "fraction": 1.5,
            "string": "11",
        }[fault]
    store = Store(tmp_path / "db")
    with pytest.raises(ContractError):
        module.import_claude_project(store, selection(reader, tmp_path, [row]))
    assert not store.path.exists()


@pytest.mark.parametrize("kind", ["user", "attachment", "queue-operation", "last-prompt", "mode"])
def test_exact_noncontributor_shapes_add_no_facts(reader, tmp_path, kind):
    module, _ = reader
    ignored = {"type": kind, "data": {"PRIVATE": {"usage": 999}}}
    if kind == "user":
        ignored["message"] = {"role": "user", "content": "PRIVATE-user"}
    store = Store(tmp_path / "db", clock=lambda: NOW)
    result = module.import_claude_project(
        store, selection(reader, tmp_path, snapshot() + [ignored])
    )
    assert result.fact_count == 4 and len(facts(store)) == 4
    assert "PRIVATE" not in store.export_bundle().model_dump_json()


@pytest.mark.parametrize(
    "row",
    [
        {"type": "progress"},
        {"type": "system"},
        {"type": "unknown"},
        {"type": "attachment", "message": None},
        {"type": "mode", "usage": None},
        {"type": "queue-operation", "message": {}},
        {"type": "last-prompt", "usage": {}},
        {"type": "user"},
        {"type": "user", "message": None},
        {"type": "user", "message": {"role": "assistant"}},
        {"type": "user", "message": {"role": "user", "usage": None}},
        {"type": "user", "message": {"role": "user"}, "usage": None},
        {"type": "assistant"},
    ],
)
def test_unknown_or_malformed_exclusion_rolls_back_all_new_facts(reader, tmp_path, row):
    module, _ = reader
    store = Store(tmp_path / "db", clock=lambda: NOW)
    module.import_claude_project(store, selection(reader, tmp_path, snapshot()))
    before = store.export_bundle()
    incoming = [assistant("new", TERMINAL, "end_turn", "new"), row]
    with pytest.raises(ContractError):
        module.import_claude_project(store, selection(reader, tmp_path, incoming))
    assert store.export_bundle() == before


def test_path_replacement_after_descriptor_read_rejects(reader, tmp_path, monkeypatch):
    module, _ = reader
    selected = selection(reader, tmp_path, snapshot())
    original = module._read_descriptor

    def replace_after_read(descriptor):
        raw = original(descriptor)
        selected.path.unlink()
        selected.path.write_bytes(raw)
        return raw

    monkeypatch.setattr(module, "_read_descriptor", replace_after_read)
    with pytest.raises(ContractError):
        module._acquire(selected.path)


def test_metadata_only_snapshot_adds_no_facts_or_store(reader, tmp_path):
    module, _ = reader
    store = Store(tmp_path / "db")
    selected = selection(
        reader, tmp_path, [{"type": "attachment"}, {"type": "user", "message": {"role": "user"}}]
    )
    result = module.import_claude_project(store, selected)
    assert result.evidence_refs == [] and result.fact_count == result.inserted_fact_count == 0
    assert not store.path.exists()


@pytest.mark.parametrize("terminal", [TERMINAL, PARTIAL])
def test_initial_combined_stages_are_atomic_and_replayable(reader, tmp_path, terminal):
    module, _ = reader
    store = Store(tmp_path / "db", clock=lambda: NOW)
    both = selection(reader, tmp_path, snapshot(terminal=terminal))
    result = module.import_claude_project(store, both)
    assert result.fact_count == 4
    assert result.inserted_fact_count == 8
    assert result.corrected_fact_count == 4
    assert result.replayed_fact_count == 0
    assert len(facts(store)) == 8
    assert {f.recorded_at for f in facts(store)} == {NOW}
    before = store.export_bundle()
    restored = Store(tmp_path / "restored", clock=lambda: NOW)
    restored.import_bundle(loads_bundle(dumps_bundle(before)))
    for target in (Store(store.path, clock=lambda: NOW), restored):
        for rows in (
            snapshot(),
            [assistant("terminal", terminal, "end_turn")],
            snapshot(terminal=terminal),
        ):
            replay = module.import_claude_project(target, selection(reader, tmp_path, rows))
            assert replay.replayed_fact_count == 4
            assert replay.inserted_fact_count == replay.corrected_fact_count == 0
        assert target.records() == before.records
    assert store.export_bundle() == before


@pytest.mark.parametrize("combined", [False, True])
def test_terminal_only_history_rejects_unseen_partial_with_new_event(reader, tmp_path, combined):
    module, _ = reader
    store = Store(tmp_path / "db", clock=lambda: NOW)
    module.import_claude_project(
        store, selection(reader, tmp_path, [assistant("terminal", TERMINAL, "end_turn")])
    )
    before = store.export_bundle()
    rows = [assistant("new", TERMINAL, "end_turn", "new")]
    rows += snapshot(terminal=TERMINAL if combined else None)
    with pytest.raises(ContractError):
        module.import_claude_project(store, selection(reader, tmp_path, rows))
    assert store.export_bundle() == before


@pytest.mark.parametrize(
    "fault",
    [
        "proof",
        "provider",
        "provider-and-surface",
        "profile",
        "producer",
        "category",
        "cohort",
        "time",
        "first",
        "predecessor",
        "cycle",
        "fork",
        "reason",
        "backdated",
    ],
)
def test_invalid_portable_claude_history_rejects_atomically(reader, tmp_path, fault):
    module, _ = reader
    store = Store(tmp_path / "db", clock=lambda: NOW)
    module.import_claude_project(store, selection(reader, tmp_path, snapshot(terminal=TERMINAL)))
    payload = json.loads(dumps_bundle(store.export_bundle()))
    records = payload["records"]
    native = [r for r in records if r["kind"] == "native_usage"]
    final = next(r for r in native if r["finality"] == "final")
    partial = next(r for r in native if r["finality"] == "partial")
    evidence = next(r for r in records if r["kind"] == "evidence")
    _corrupt_history(module, payload, native, final, partial, evidence, fault)
    target = Store(tmp_path / "target", clock=lambda: NOW)
    with pytest.raises(ContractError):
        target.import_bundle(loads_bundle(json.dumps(payload)))

    assert not target.path.exists()


def _forge_provider_and_surface(module, payload, native, evidence):
    evidence["provider"] = "Codex"
    evidence["surface"] = "desktop-coding"
    from changecost.models import NativeUsage

    remapped = {}
    for row in native:
        old_id = row["record_id"]
        row["producer"]["client_surface"] = "desktop-coding"
        row["record_id"] = module._revision_id(NativeUsage.model_validate(row))
        remapped[old_id] = row["record_id"]
    for row in native:
        if row["previous"] is not None:
            row["previous"]["record_id"] = remapped[row["previous"]["record_id"]]
    for observation in payload["observations"]:
        ref = observation["reference"]
        ref["record_id"] = remapped.get(ref["record_id"], ref["record_id"])


def _corrupt_history(module, payload, native, final, partial, evidence, fault):
    mutations = {
        "proof": (final["first_admission"], "approval_digest", "0" * 64),
        "provider": (evidence, "provider", "Codex"),
        "profile": (evidence, "profile", "wrong"),
        "producer": (final["producer"], "engine_version", "2.1.257"),
        "category": (final, "source_category", "total_tokens"),
        "time": (final, "effective_at", "2026-10-27T00:00:00Z"),
        "first": (final, "first_acquisition_digest", "0" * 64),
        "predecessor": (final["previous"], "record_id", "0" * 64),
        "reason": (final, "reason", "other"),
    }
    if fault in mutations:
        target, field, value = mutations[fault]
        target[field] = value
        return
    if fault == "provider-and-surface":
        _forge_provider_and_surface(module, payload, native, evidence)
        return
    if fault == "cohort":
        payload["records"].remove(final)
        return
    if fault == "cycle":
        partial["previous"] = {"kind": "native_usage", "record_id": final["record_id"]}
        partial["reason"] = "claude-serialized-stage-refinement"
        return
    if fault == "fork":
        from changecost.models import NativeUsage

        duplicate = dict(final, quantity=99)
        duplicate["record_id"] = module._revision_id(NativeUsage.model_validate(duplicate))
        payload["records"].append(duplicate)
        return
    if fault == "backdated":
        for row in native:
            if row["finality"] == "final":
                row["recorded_at"] = row["effective_at"] = "2026-10-27T00:00:00Z"
        return
    raise AssertionError("unknown test fault")


def _rehash_native_history(module, payload):
    from changecost.models import NativeUsage

    native = [r for r in payload["records"] if r["kind"] == "native_usage"]
    remapped = {}
    for row in native:
        old = row["record_id"]
        row["record_id"] = module._revision_id(NativeUsage.model_validate(row))
        remapped[old] = row["record_id"]
    for row in native:
        if row["previous"] is not None:
            row["previous"]["record_id"] = remapped[row["previous"]["record_id"]]
    for observation in payload["observations"]:
        ref = observation["reference"]
        ref["record_id"] = remapped.get(ref["record_id"], ref["record_id"])


@pytest.mark.parametrize(
    "retained",
    [
        "provider",
        "evidence-surface",
        "producer-surface",
        "mapping",
        "profile",
        "profile-digest",
        "approval-digest",
    ],
)
def test_each_retained_claude_claim_requires_exact_association(reader, tmp_path, retained):
    module, envelope = reader
    store = Store(tmp_path / "source", clock=lambda: NOW)
    module.import_claude_project(store, selection(reader, tmp_path, snapshot(terminal=TERMINAL)))
    payload = json.loads(dumps_bundle(store.export_bundle()))
    evidence = next(r for r in payload["records"] if r["kind"] == "evidence")
    evidence["provider"] = "Claude" if retained == "provider" else "Codex"
    evidence["surface"] = "project-jsonl" if retained == "evidence-surface" else "desktop-coding"
    evidence["profile"] = envelope["profile_id"] if retained == "profile" else "other-profile"
    for row in payload["records"]:
        if row["kind"] != "native_usage":
            continue
        row["producer"]["client_surface"] = (
            "project-jsonl" if retained == "producer-surface" else "desktop-coding"
        )
        row["mapping_revision"] = (
            envelope["admission"]["mapping_revision"] if retained == "mapping" else "other-mapping"
        )
        row["first_admission"] = {
            "profile_digest": envelope["profile_digest"]
            if retained == "profile-digest"
            else "d" * 64,
            "approval_digest": envelope["approval_digest"]
            if retained == "approval-digest"
            else "e" * 64,
        }
        row["model"] = "unsupported-model"
        row["scope_completeness"] = "complete"
    _rehash_native_history(module, payload)
    target = Store(tmp_path / "target", clock=lambda: NOW)
    with pytest.raises(ContractError, match="unapproved Claude native association"):
        target.import_bundle(loads_bundle(json.dumps(payload)))
    assert not target.path.exists()


def test_portable_evidence_alias_rejects_without_breaking_canonical_replay(reader, tmp_path):
    module, _ = reader
    store = Store(tmp_path / "source", clock=lambda: NOW)
    selected = selection(reader, tmp_path, snapshot(terminal=TERMINAL))
    original = module.import_claude_project(store, selected)
    before = store.export_bundle()
    payload = json.loads(dumps_bundle(before))
    evidence = next(r for r in payload["records"] if r["kind"] == "evidence")
    old_id = evidence["record_id"]
    evidence["record_id"] = "coherent-evidence-alias"
    for row in payload["records"]:
        if row["kind"] == "native_usage":
            row["evidence"]["record_id"] = evidence["record_id"]
    for observation in payload["observations"]:
        ref = observation["reference"]
        if ref["kind"] == "evidence" and ref["record_id"] == old_id:
            ref["record_id"] = evidence["record_id"]
    target = Store(tmp_path / "target", clock=lambda: NOW)
    with pytest.raises(ContractError, match="unapproved Claude native association"):
        target.import_bundle(loads_bundle(json.dumps(payload)))
    assert not target.path.exists()
    replay = module.import_claude_project(store, selected)
    assert replay.evidence_refs == original.evidence_refs
    assert replay.inserted_fact_count == 0
    assert store.export_bundle() == before
