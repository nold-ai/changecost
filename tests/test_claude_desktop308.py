import copy
import hashlib
import json
from collections.abc import Mapping
from datetime import UTC, datetime

import pytest
from typer.testing import CliRunner

from changecost import claude_local as reader
from changecost.cli import app
from changecost.models import NativeUsage
from changecost.serialization import ContractError, dumps_bundle, loads_bundle
from changecost.store import Store

PROFILE = "claude-desktop-2-1-308-root-terminal"


def assistant(event="one"):
    return {
        "type": "assistant",
        "version": "2.1.308",
        "entrypoint": "claude-desktop",
        "uuid": "block-" + event,
        "sessionId": "session",
        "requestId": "request-" + event,
        "isSidechain": False,
        "message": {
            "id": "message-" + event,
            "role": "assistant",
            "stop_reason": "end_turn",
            "usage": {
                "input_tokens": 0,
                "output_tokens": 7,
                "cache_creation_input_tokens": 11,
                "cache_read_input_tokens": 13,
            },
        },
    }


def selection(tmp_path, rows, profile=PROFILE, name="source.jsonl"):
    raw = b"".join(json.dumps(row).encode() + b"\n" for row in rows)
    path = tmp_path / name
    path.write_bytes(raw)
    return reader.ClaudeProjectSelection(
        repository_id="repo",
        path=path,
        profile_id=profile,
        expected_sha256=hashlib.sha256(raw).hexdigest(),
    )


def test_desktop_root_terminal_literal_zero_and_replay(tmp_path):
    store = Store(tmp_path / "db")
    selected = selection(tmp_path, [assistant()])
    result = reader.import_claude_project(store, selected)
    assert result.fact_count == result.inserted_fact_count == 4
    assert result.corrected_fact_count == 0
    before = store.export_bundle()
    assert reader.import_claude_project(store, selected).replayed_fact_count == 4
    assert store.records() == before.records
    facts = [r for r in before.records if r.kind == "native_usage"]
    assert {f.source_category: f.quantity for f in facts} == {
        "input_tokens": 0,
        "output_tokens": 7,
        "cache_write_input_tokens": 11,
        "cached_input_tokens": 13,
    }


TERMINAL_PROFILE = "claude-project-2-1-215-request-stages"
FIELDS = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")


def terminal(event="one"):
    row = assistant(event)
    row["version"] = "2.1.215"
    del row["entrypoint"]
    return row


def test_desktop_cli_reopen_recovery_preserve_first_provenance(tmp_path):
    selected = selection(tmp_path, [assistant()])
    path = tmp_path / "db"
    result = CliRunner().invoke(
        app,
        [
            "--db",
            str(path),
            "settle",
            "--repository-id",
            "repo",
            "--import-claude-project",
            str(selected.path),
            "--source-profile",
            PROFILE,
            "--source-sha256",
            selected.expected_sha256,
        ],
    )
    assert result.exit_code == 0, result.output
    original = Store(path).export_bundle()
    restored = Store(tmp_path / "restored")
    restored.import_bundle(loads_bundle(dumps_bundle(original)))
    row = assistant()
    row["message"]["stop_reason"] = "tool_use"
    row["message"]["usage"]["cache_creation"] = {"ephemeral_5m_input_tokens": 11}
    replay = selection(tmp_path, [row], name="other.jsonl")
    for store in (Store(path), restored):
        result = reader.import_claude_project(store, replay)
        assert result.replayed_fact_count == 4 and result.inserted_fact_count == 0
        assert store.records() == original.records
        facts = [f for f in store.records() if isinstance(f, NativeUsage)]
        assert all(f.model is None and f.ownership.state == "unknown" for f in facts)
        assert all(f.previous is None and f.reason is None for f in facts)


@pytest.mark.parametrize("field", FIELDS)
@pytest.mark.parametrize("bad", [None, True, False, -1, 1.5, "7", "ABSENT"])
def test_desktop_strict_counters_reject_whole_batch(tmp_path, field, bad):
    row = assistant()
    if bad == "ABSENT":
        del row["message"]["usage"][field]
    else:
        row["message"]["usage"][field] = bad
    store = Store(tmp_path / "db")
    with pytest.raises(reader.ClaudeProjectImportError):
        reader.import_claude_project(store, selection(tmp_path, [assistant("good"), row]))
    assert not store.path.exists()


@pytest.mark.parametrize(
    "key,value",
    [
        ("version", "2.1.215"),
        ("entrypoint", "cli"),
        ("entrypoint", None),
        ("isSidechain", True),
        ("isSidechain", 0),
        ("agentId", None),
        ("agentId", "child"),
        ("unknown", 1),
        ("usage", None),
        ("type", "progress"),
    ],
)
def test_desktop_producer_lineage_and_unknown_keys(tmp_path, key, value):
    row = assistant()
    row[key] = value
    store = Store(tmp_path / "db")
    with pytest.raises(reader.ClaudeProjectImportError):
        reader.import_claude_project(store, selection(tmp_path, [assistant("good"), row]))
    assert not store.path.exists()


@pytest.mark.parametrize("reason", [None, "max_tokens", False, "ABSENT"])
def test_desktop_no_partial_or_unknown_stage(tmp_path, reason):
    row = assistant()
    if reason == "ABSENT":
        del row["message"]["stop_reason"]
    else:
        row["message"]["stop_reason"] = reason
    store = Store(tmp_path / "db")
    with pytest.raises(reader.ClaudeProjectImportError):
        reader.import_claude_project(store, selection(tmp_path, [assistant("good"), row]))
    assert not store.path.exists()


@pytest.mark.parametrize("desktop_first", [False, True])
def test_cross_profile_equal_event_collision_both_orders_reopen_recovery(tmp_path, desktop_first):
    first, second = (assistant(), terminal()) if desktop_first else (terminal(), assistant())
    first_profile, second_profile = (
        (PROFILE, TERMINAL_PROFILE) if desktop_first else (TERMINAL_PROFILE, PROFILE)
    )
    store = Store(tmp_path / "db")
    reader.import_claude_project(store, selection(tmp_path, [first], first_profile))
    before = store.export_bundle()
    restored = Store(tmp_path / "restored")
    restored.import_bundle(loads_bundle(dumps_bundle(before)))
    second_good = copy.deepcopy(second)
    second_good["requestId"] += "good"
    second_good["message"]["id"] += "good"
    second_good["uuid"] += "good"
    selected = selection(tmp_path, [second_good, second], second_profile)
    for target in (Store(store.path), restored):
        with pytest.raises(reader.ClaudeProjectImportError, match="native_identity_conflict"):
            reader.import_claude_project(target, selected)
        assert target.records() == before.records


def test_mixed_profile_source_and_changed_quantities_reject_atomically(tmp_path):
    store = Store(tmp_path / "db")
    with pytest.raises(reader.ClaudeProjectImportError):
        reader.import_claude_project(store, selection(tmp_path, [assistant(), terminal("two")]))
    assert not store.path.exists()
    reader.import_claude_project(store, selection(tmp_path, [assistant()]))
    before = store.export_bundle()
    changed = assistant()
    changed["message"]["usage"]["output_tokens"] += 1
    with pytest.raises(reader.ClaudeProjectImportError, match="native_identity_conflict"):
        reader.import_claude_project(store, selection(tmp_path, [assistant("good"), changed]))
    assert store.records() == before.records


METADATA = (
    "cost-state",
    "mode",
    "agent-name",
    "api-request",
    "api-request-shape",
    "atis-latch",
    "attachment",
    "custom-title",
    "file-history-snapshot",
    "last-prompt",
    "queue-operation",
    "system",
)


@pytest.mark.parametrize("kind", METADATA)
@pytest.mark.parametrize("extra", [None, "message", "usage", "unknown"])
def test_desktop_closed_metadata(tmp_path, kind, extra):
    row = {"type": kind}
    if extra is not None:
        row[extra] = None
    store = Store(tmp_path / "db")
    selected = selection(tmp_path, [assistant(), row])
    if extra is None:
        assert reader.import_claude_project(store, selected).fact_count == 4
    else:
        with pytest.raises(reader.ClaudeProjectImportError):
            reader.import_claude_project(store, selected)
        assert not store.path.exists()


@pytest.mark.parametrize(
    "message", [None, "opaque", 7, True, [], [{"usage": 8}], {}, {"nested": {"usage": 8}}]
)
def test_blob_message_is_opaque_json(tmp_path, message):
    row = {"type": "api-request-blob", "hash": "opaque", "sessionId": "session", "message": message}
    assert (
        reader.import_claude_project(
            Store(tmp_path / "db"), selection(tmp_path, [assistant(), row])
        ).fact_count
        == 4
    )


@pytest.mark.parametrize("fault", ["hash", "message", "sessionId", "extra", "usage", "immediate"])
def test_blob_exact_boundary(tmp_path, fault):
    row = {"type": "api-request-blob", "hash": "opaque", "sessionId": "session", "message": {}}
    if fault in {"hash", "message", "sessionId"}:
        del row[fault]
    elif fault == "immediate":
        row["message"]["usage"] = None
    else:
        row[fault] = None
    store = Store(tmp_path / "db")
    with pytest.raises(reader.ClaudeProjectImportError):
        reader.import_claude_project(store, selection(tmp_path, [assistant(), row]))
    assert not store.path.exists()


@pytest.mark.parametrize(
    "message", [{"role": "user"}, {"role": "assistant"}, None, {"role": "user", "usage": None}]
)
def test_desktop_user_boundary(tmp_path, message):
    selected = selection(tmp_path, [assistant(), {"type": "user", "message": message}])
    store = Store(tmp_path / "db")
    if message == {"role": "user"}:
        assert reader.import_claude_project(store, selected).fact_count == 4
    else:
        with pytest.raises(reader.ClaudeProjectImportError):
            reader.import_claude_project(store, selected)
        assert not store.path.exists()


def test_unknown_profile_rejects_before_acquisition(tmp_path, monkeypatch):
    selected = selection(tmp_path, [assistant()], "unknown")

    def acquire(_):
        pytest.fail("unknown profile acquired source")

    monkeypatch.setattr(reader, "_acquire", acquire)
    with pytest.raises(reader.ClaudeProjectImportError, match="unsupported_profile"):
        reader.import_claude_project(Store(tmp_path / "db"), selected)


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
@pytest.mark.parametrize("profile", [PROFILE, TERMINAL_PROFILE])
def test_each_retained_claude_claim_requires_exact_association(tmp_path, retained, profile):
    module = reader
    envelope = reader._select_claude(profile).envelope
    store = Store(
        tmp_path / "source",
    )
    module.import_claude_project(
        store, selection(tmp_path, [assistant() if profile == PROFILE else terminal()], profile)
    )
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
    target = Store(
        tmp_path / "target",
    )
    with pytest.raises(ContractError, match="unapproved Claude native association"):
        target.import_bundle(loads_bundle(json.dumps(payload)))
    assert not target.path.exists()


@pytest.mark.parametrize("fault", ["partial", "missing", "reason", "borrowed", "cohort", "alias"])
def test_desktop_portable_history_rejects_unapproved_meaning(tmp_path, fault):
    store = Store(tmp_path / "source")
    reader.import_claude_project(store, selection(tmp_path, [assistant()]))
    payload = json.loads(dumps_bundle(store.export_bundle()))
    native = [r for r in payload["records"] if r["kind"] == "native_usage"]
    if fault == "cohort":
        removed = native.pop()
        payload["records"].remove(removed)
        payload["observations"] = [
            o
            for o in payload["observations"]
            if o["reference"]["record_id"] != removed["record_id"]
        ]
    elif fault == "alias":
        evidence = next(r for r in payload["records"] if r["kind"] == "evidence")
        old = evidence["record_id"]
        evidence["record_id"] = "alias"
        for row in native:
            row["evidence"]["record_id"] = "alias"
        for o in payload["observations"]:
            if o["reference"]["record_id"] == old:
                o["reference"]["record_id"] = "alias"
    else:
        env = reader._select_claude(TERMINAL_PROFILE).envelope
        changes = {
            "partial": {"finality": "partial"},
            "missing": {"quantity": None},
            "reason": {"reason": "claude-serialized-stage-refinement"},
            "borrowed": {
                "first_admission": {
                    "profile_digest": env["profile_digest"],
                    "approval_digest": env["approval_digest"],
                }
            },
        }
        for row in native:
            row.update(changes[fault])
            if fault == "reason":
                row["previous"] = {"kind": "native_usage", "record_id": row["record_id"]}
    _rehash_native_history(reader, payload)
    target = Store(tmp_path / "target")
    with pytest.raises(ContractError):
        target.import_bundle(loads_bundle(json.dumps(payload)))
    assert not target.path.exists()


@pytest.mark.parametrize("existing", [False, True])
def test_desktop_atomic_store_failure(tmp_path, monkeypatch, existing):
    store = Store(tmp_path / "db")
    if existing:
        reader.import_claude_project(store, selection(tmp_path, [assistant("old")]))
    before = store.records() if existing else []

    def fail(_):
        raise OSError("injected transaction interruption")

    with monkeypatch.context() as patch:
        patch.setattr(store, "commit", fail)
        with pytest.raises(ContractError):
            reader.import_claude_project(store, selection(tmp_path, [assistant()]))
    assert store.records() == before if existing else not store.path.exists()
    result = reader.import_claude_project(store, selection(tmp_path, [assistant()]))
    assert result.inserted_fact_count == 4


def test_catalogue_rejects_duplicate_profile_ids(monkeypatch):
    envelope = reader._select_claude(PROFILE).envelope

    class Resource:
        def joinpath(self, _):
            return self

        def read_text(self):
            return json.dumps(envelope)

    monkeypatch.setattr(reader, "files", lambda _: Resource())
    with pytest.raises(reader.ClaudeProjectImportError, match="unsupported_profile"):
        reader._claude_admissions()


def test_exact_desktop_activation_preserves_prior_profiles_and_resources():
    from pathlib import Path

    from quality.source_admission import packaged_claude_admission
    from quality.source_feasibility import profile_digest, validate_register

    root = Path(__file__).parents[1]
    register = json.loads((root / "docs/providers/source-profiles.json").read_text())
    assert len(register["profiles"]) == 26
    assert (
        hashlib.sha256(
            json.dumps(register["profiles"][:25], sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        == "0d58ab8219934b6b4ca297104e5343acfd7faa5dd70ce6d0c6ddd18abaf466ea"
    )
    profile = register["profiles"][-1]
    assert (
        profile_digest(profile)
        == "7e3cf00757e1eca8c91782848c59913a9e19bb39b78c7a15edf7be370b906b55"
    )
    assert validate_register(register) == []
    assert sum(len(p["approvals"]) for p in register["profiles"]) == 3
    for profile_id, filename in (
        (PROFILE, "claude_desktop308_admission.json"),
        (TERMINAL_PROFILE, "claude_admission.json"),
    ):
        assert json.loads(
            (root / "src/changecost" / filename).read_text()
        ) == packaged_claude_admission(register, profile_id)
    for name, expected in (
        ("native-observations", "3becddbfa1621db4628f19c3b3b32e1cce311a51bf347f9c095388e0c6763661"),
        ("producer-binding", "3a9e2563df85d4059cd90d8e8823127d74ad6989ae8658eb80489474ff82362a"),
    ):
        assert (
            hashlib.sha256(
                (
                    root / "docs/providers/evidence" / f"claude-desktop-2-1-308-{name}.md"
                ).read_bytes()
            ).hexdigest()
            == expected
        )


@pytest.mark.parametrize("profile", [PROFILE, TERMINAL_PROFILE])
@pytest.mark.parametrize("depth", [1, 64])
@pytest.mark.parametrize("encoding", ["utf-16-le", "utf-16-be", "utf-32-le", "utf-32-be"])
@pytest.mark.parametrize("bom", [False, True])
def test_non_utf8_wire_encodings_reject_atomically(tmp_path, profile, depth, encoding, bom):
    import codecs

    row = assistant() if profile == PROFILE else terminal()
    row["message"]["ignored_quote"] = '"'
    nested = 0
    for _ in range(depth):
        nested = {"nested": nested}
    row["message"]["ignored_payload"] = nested
    raw = json.dumps(row).encode(encoding)
    if bom:
        markers = {
            "utf-16-le": codecs.BOM_UTF16_LE,
            "utf-16-be": codecs.BOM_UTF16_BE,
            "utf-32-le": codecs.BOM_UTF32_LE,
            "utf-32-be": codecs.BOM_UTF32_BE,
        }
        raw = markers[encoding] + raw
    path = tmp_path / "source.jsonl"
    path.write_bytes(raw)
    selected = reader.ClaudeProjectSelection(
        repository_id="repo",
        path=path,
        profile_id=profile,
        expected_sha256=hashlib.sha256(raw).hexdigest(),
    )
    store = Store(tmp_path / "db")
    with pytest.raises(reader.ClaudeProjectImportError):
        reader.import_claude_project(store, selected)
    assert not store.path.exists()


@pytest.mark.parametrize("profile", [PROFILE, TERMINAL_PROFILE])
@pytest.mark.parametrize("depth", [1, 64])
@pytest.mark.parametrize("bom", [False, True])
def test_utf8_escaped_quotes_and_unicode_line_characters(tmp_path, profile, depth, bom):
    row = assistant() if profile == PROFILE else terminal()
    row["message"]["ignored_quote"] = '"\\\u2028\u0085'
    nested = 0
    for _ in range(depth):
        nested = {"nested": nested}
    row["message"]["ignored_payload"] = nested
    raw = json.dumps(row, ensure_ascii=False).encode("utf-8-sig" if bom else "utf-8")
    path = tmp_path / "source.jsonl"
    path.write_bytes(raw + b"\n")
    selected = reader.ClaudeProjectSelection(
        repository_id="repo",
        path=path,
        profile_id=profile,
        expected_sha256=hashlib.sha256(raw + b"\n").hexdigest(),
    )
    store = Store(tmp_path / "db")
    if depth == 64:
        with pytest.raises(reader.ClaudeProjectImportError, match="source_depth_limit"):
            reader.import_claude_project(store, selected)
        assert not store.path.exists()
    else:
        assert reader.import_claude_project(store, selected).inserted_fact_count == 4


@pytest.mark.parametrize("kind", ["cost-state", "mode"])
def test_q4_metadata_opaque_values_create_no_facts_or_authority(tmp_path, kind):
    row = (
        {
            "type": "cost-state",
            "sessionId": "session",
            "totalCostUSD": 99.5,
            "modelUsage": {"opaque": {"usage": {"input_tokens": 999}}},
            "hasUnknownModelCost": True,
            "totalDuration": 100,
        }
        if kind == "cost-state"
        else {"type": "mode", "mode": {"opaque": [1]}, "sessionId": "session"}
    )
    empty = Store(tmp_path / "empty")
    result = reader.import_claude_project(empty, selection(tmp_path, [row]))
    assert result.fact_count == result.inserted_fact_count == 0
    assert not empty.path.exists()
    store = Store(tmp_path / "db")
    result = reader.import_claude_project(store, selection(tmp_path, [assistant(), row]))
    assert result.fact_count == result.inserted_fact_count == 4
    assert {r.kind for r in store.records()} == {"evidence", "native_usage"}
    assert "modelUsage" not in dumps_bundle(store.export_bundle())


class _CountedRecords(Mapping):
    def __init__(self, records):
        self.records = records
        self.visits = 0

    def __getitem__(self, key):
        return self.records[key]

    def __len__(self):
        return len(self.records)

    def __iter__(self):
        for key in self.records:
            self.visits += 1
            yield key


@pytest.fixture
def history_work(monkeypatch):
    envelopes = []
    for approved in reader._claude_admissions():
        envelope = copy.deepcopy(approved.envelope)
        envelope.update(
            profile_id="synthetic-" + approved.kind,
            profile_digest=("a" if approved.kind == "terminal215" else "b") * 64,
            approval_digest=("c" if approved.kind == "terminal215" else "d") * 64,
        )
        envelopes.append(reader._ApprovedClaude(approved.kind, envelope))
    monkeypatch.setattr(reader, "_claude_admissions", lambda: tuple(envelopes))
    samples = []
    apply = Store.apply

    def measured_apply(store, operation):
        def measured(records, store_id, now):
            before = copy.deepcopy(records)
            counted = _CountedRecords(records)
            try:
                return operation(counted, store_id, now)
            finally:
                samples.append((len(records), counted.visits))
                assert counted == records == before

        return apply(store, measured)

    monkeypatch.setattr(Store, "apply", measured_apply)
    return samples


def _seed_mixed_history(store, tmp_path, count):
    for kind, row in (("terminal215", terminal), ("desktop308", assistant)):
        selected = selection(
            tmp_path,
            [row(f"retained-{kind}-{index}") for index in range(count)],
            "synthetic-" + kind,
            "retained-" + kind + ".jsonl",
        ).model_copy(update={"repository_id": "other-repository"})
        assert reader.import_claude_project(store, selected).inserted_fact_count == 4 * count


def _assert_linear_history_work(samples, incoming_events):
    retained, visits = samples[-1]
    assert visits <= 3 * (retained + incoming_events), (retained, incoming_events, visits)


@pytest.mark.parametrize("kind,row", [("terminal215", terminal), ("desktop308", assistant)])
@pytest.mark.parametrize("retained_events,incoming_events", [(30, 6), (60, 12)])
def test_growing_history_import_replay_and_conflicts(
    tmp_path, history_work, kind, row, retained_events, incoming_events
):
    store = Store(tmp_path / "db", clock=lambda: datetime(2026, 10, 29, tzinfo=UTC))
    _seed_mixed_history(store, tmp_path, retained_events)
    selected = selection(
        tmp_path,
        [row(f"incoming-{index}") for index in range(incoming_events)],
        "synthetic-" + kind,
    )
    result = reader.import_claude_project(store, selected)
    assert result.inserted_fact_count == result.fact_count == 4 * incoming_events
    assert result.corrected_fact_count == result.replayed_fact_count == 0
    _assert_linear_history_work(history_work, incoming_events)
    before = store.export_bundle()
    replay = reader.import_claude_project(store, selected)
    assert replay.replayed_fact_count == 4 * incoming_events
    assert replay.inserted_fact_count == replay.corrected_fact_count == 0
    assert replay.evidence_refs == result.evidence_refs
    assert store.export_bundle() == before
    _assert_linear_history_work(history_work, incoming_events)
    other_kind, other_row = (
        ("desktop308", assistant) if kind == "terminal215" else ("terminal215", terminal)
    )
    for conflict_kind, conflict_row, repository in (
        (other_kind, other_row, "repo"),
        (kind, row, "different-repository"),
    ):
        conflict = selection(
            tmp_path,
            [conflict_row("new-before-conflict"), conflict_row("incoming-0")],
            "synthetic-" + conflict_kind,
            "conflict.jsonl",
        ).model_copy(update={"repository_id": repository})
        with pytest.raises(reader.ClaudeProjectImportError, match="native_identity_conflict"):
            reader.import_claude_project(store, conflict)
        assert store.export_bundle() == before
        _assert_linear_history_work(history_work, 2)


@pytest.mark.parametrize("retained_events,incoming_events", [(30, 6), (60, 12)])
def test_growing_history_refinement_and_old_stage_replay(
    tmp_path, history_work, retained_events, incoming_events
):
    store = Store(tmp_path / "db", clock=lambda: datetime(2026, 10, 29, tzinfo=UTC))
    _seed_mixed_history(store, tmp_path, retained_events)
    partials = [terminal(f"incoming-{index}") for index in range(incoming_events)]
    for row in partials:
        row["message"]["stop_reason"] = None
    finals = copy.deepcopy(partials)
    for row in finals:
        row["uuid"] += "-final"
        row["message"]["stop_reason"] = "end_turn"
        row["message"]["usage"]["output_tokens"] += 1
    partial = selection(tmp_path, partials, "synthetic-terminal215", "partial.jsonl")
    combined = selection(tmp_path, partials + finals, "synthetic-terminal215", "combined.jsonl")
    first = reader.import_claude_project(store, partial)
    assert first.inserted_fact_count == 4 * incoming_events
    _assert_linear_history_work(history_work, incoming_events)
    refined = reader.import_claude_project(store, combined)
    assert refined.inserted_fact_count == refined.corrected_fact_count == 4 * incoming_events
    assert refined.evidence_refs == first.evidence_refs
    _assert_linear_history_work(history_work, incoming_events)
    before = store.export_bundle()
    _assert_refinement_history(before.records, incoming_events)
    for selected in (partial, combined):
        replay = reader.import_claude_project(store, selected)
        assert replay.replayed_fact_count == 4 * incoming_events
        assert replay.inserted_fact_count == replay.corrected_fact_count == 0
        assert replay.evidence_refs == first.evidence_refs
        assert store.export_bundle() == before
        _assert_linear_history_work(history_work, incoming_events)


def _assert_refinement_history(records, event_count):
    originals = {r.record_id: r for r in records if isinstance(r, NativeUsage)}
    corrections = [r for r in originals.values() if r.previous is not None]
    assert len(corrections) == 4 * event_count
    for fact in corrections:
        assert fact.previous is not None
        original = originals[fact.previous.record_id]
        assert fact.first_acquisition_digest == original.first_acquisition_digest
        assert fact.first_admission == original.first_admission
        assert fact.evidence == original.evidence
