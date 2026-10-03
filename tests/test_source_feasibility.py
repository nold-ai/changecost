"""Independent source-boundary expectations and adversarial inspection controls."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from quality import source_feasibility as research
from quality.source_cases import STRATEGIES, evaluate_case
from quality.source_inspection import EvidenceError, inspect_manifest, read_document

ROOT = Path(__file__).parents[1]
CASES = json.loads((ROOT / "docs/providers/fixtures/source-feasibility-cases.json").read_text())


def case(name):
    return copy.deepcopy(next(c for c in CASES["cases"] if c["id"] == name))


@pytest.mark.parametrize("sample", CASES["cases"], ids=lambda c: c["id"])
def test_all_original_semantic_conclusions(sample):
    actual = evaluate_case(sample, STRATEGIES[sample["id"]])
    assert {key: actual[key] for key in sample["expected"]} == sample["expected"]


def test_evaluation_ignores_declared_answers_and_case_identity():
    sample = case("cli-repeated-billing")
    sample["expected"] = {"authoritative_nano_aiu": 999}
    sample["id"] = "unrelated-id"
    assert evaluate_case(sample, "spans")["authoritative_nano_aiu"] == 100
    for row in sample["records"]:
        row["attributes"]["github.copilot.nano_aiu"] = 17
    assert evaluate_case(sample, "spans")["authoritative_nano_aiu"] == 17


def test_root_identity_conflict_and_child_forgery():
    sample = case("cli-repeated-billing")
    other = copy.deepcopy(sample["records"][0])
    other["span_id"] = "another-root"
    other["attributes"]["gen_ai.conversation.id"] = "another-conversation"
    sample["records"].append(other)
    assert evaluate_case(sample, "spans")["authoritative_nano_aiu"] == 200
    sample["records"][2]["attributes"]["github.copilot.nano_aiu"] = 200
    assert evaluate_case(sample, "spans")["authoritative_nano_aiu"] is None
    child = case("cli-missing-root")
    child["records"][0]["attributes"]["gen_ai.operation.name"] = "invoke_agent"
    assert evaluate_case(child, "spans")["authoritative_nano_aiu"] is None


def test_counter_reset_and_mixed_units_remain_unresolved():
    sample = case("claude-estimated-cost")
    assert evaluate_case(sample, "cumulative")["estimate_amount"] == "0.03"
    sample["records"][1]["value"] = "0.01"
    sample["records"][1]["interval_start"] = "2000-01-01T00:01:00Z"
    assert evaluate_case(sample, "cumulative")["estimate_amount"] is None
    sample["records"][1]["unit"] = "credits"
    assert evaluate_case(sample, "cumulative")["estimate_amount"] is None


@pytest.mark.parametrize("quantity,expected", [(None, None), (0, 0), (11, 11)])
def test_missing_null_zero_are_distinct(quantity, expected):
    sample = case("tokens-only")
    sample["records"][0]["input_tokens"] = quantity
    assert evaluate_case(sample, "tokens")["input_tokens"] == expected
    del sample["records"][0]["input_tokens"]
    assert evaluate_case(sample, "tokens")["input_tokens"] is None


def test_bool_quantity_and_disconnected_correction_reject():
    sample = case("tokens-only")
    sample["records"][0]["input_tokens"] = True
    with pytest.raises(EvidenceError):
        evaluate_case(sample, "tokens")
    sample = case("correction")
    sample["records"][1]["replaces_revision"] = 9
    sample["records"][2]["replaces_revision"] = 9
    assert evaluate_case(sample, "replacement")["current_amount"] is None


def test_exact_decimal_replacement_is_input_derived():
    sample = case("correction")
    for row in sample["records"][1:]:
        row["amount"] = "0.030000000000000000000000000000000001"
    assert evaluate_case(sample, "replacement")["current_amount"] == sample["records"][1]["amount"]


def test_case_detector_fault_and_repair():
    broken = copy.deepcopy(CASES)
    broken["cases"][0]["expected"]["authoritative_nano_aiu"] = 300
    assert research.check_cases(broken) == ["case:0:conclusion-mismatch"]
    broken["cases"][0]["expected"]["authoritative_nano_aiu"] = 100
    assert research.check_cases(broken) == []


def registry():
    return research.load_register(ROOT / "docs/providers/source-profiles.json")


def test_matrix_drift_and_original_register_has_no_approvals():
    data = registry()
    assert research.validate_register(data) == []
    assert all(not p["approvals"] for p in data["profiles"])
    text = (ROOT / "docs/providers/source-feasibility.md").read_text()
    assert research.matrix_matches(text, data)
    changed = copy.deepcopy(data)
    changed["profiles"][0]["capabilities"]["usage"] = "supported"
    assert not research.matrix_matches(text, changed)


def approval(data):
    profile = data["profiles"][0]
    evidence = profile["evidence"][0]
    evidence["origin"] = "native"
    profile["capabilities"]["usage"] = "supported"
    return {
        "capability": "usage",
        "evidence_id": evidence["id"],
        "sha256": evidence["sha256"],
        "profile_digest": research.profile_digest(profile),
        "reviewer": "independent-reviewer",
        "decisions": {k: "verified boundary; exclusions recorded" for k in research.DECISIONS},
    }


@pytest.mark.parametrize("fault", ["synthetic", "version", "digest", "capability", "decisions"])
def test_native_approval_binding_fault_and_repair(fault):
    data = registry()
    profile = data["profiles"][0]
    proof = approval(data)
    profile["approvals"] = [proof]
    assert research.validate_register(data) == []
    repaired = copy.deepcopy(data)
    if fault == "synthetic":
        profile["evidence"][0]["origin"] = "synthetic"
    elif fault == "version":
        profile["version"] += "-changed"
    elif fault == "digest":
        proof["sha256"] = "0" * 64
    elif fault == "capability":
        proof["capability"] = "billed_money"
    else:
        proof["decisions"].pop("reset")
    assert research.validate_register(data)
    assert research.validate_register(repaired) == []


def manifest(tmp_path, raw, fmt="json"):
    data = registry()
    profile = data["profiles"][0]
    path = tmp_path / "private-source"
    path.write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    profile["evidence"][0]["sha256"] = digest
    entry = {
        "profile": profile["id"],
        "evidence_id": profile["evidence"][0]["id"],
        "path": str(path),
        "sha256": digest,
        "format": fmt,
        "fields": [["usage"]],
    }
    return {"format": "source-inspection/v1", "entries": [entry]}, data, path


@pytest.mark.parametrize(
    "fmt,raw",
    [
        ("json", b'{"usage":0,"secret":"PRIVATE"}'),
        ("jsonl", b'{"usage":0}\n{"usage":null}\n{}\n'),
        ("csv", b"usage,private\n0,PRIVATE\n"),
    ],
)
def test_safe_read_only_reports(tmp_path, fmt, raw):
    request, data, source = manifest(tmp_path, raw, fmt)
    report = inspect_manifest(request, data)
    encoded = json.dumps(report)
    assert "PRIVATE" not in encoded and str(source) not in encoded and "usage" not in encoded
    assert source.read_bytes() == raw
    assert report[0]["semantic_approval"] is False
    assert "field_types" in report[0]


@pytest.mark.parametrize(
    "fmt,raw",
    [
        ("json", b'{"secret":1,"secret":2}'),
        ("jsonl", b'{}\n{"secret":NaN}\n'),
        ("json", b'{"nested":{"x":1,"x":2}}'),
        ("json", b"\xff"),
        ("json", b'{"n":1e9999}'),
        ("csv", b"a,a\n1,2\n"),
        ("csv", b"a,b\n1\n"),
        ("csv", b'a\n"unterminated\n'),
    ],
)
def test_malformed_inputs_reject_atomically(tmp_path, fmt, raw):
    request, data, source = manifest(tmp_path, raw, fmt)
    with pytest.raises(EvidenceError) as exc:
        inspect_manifest(request, data)
    assert str(source) not in str(exc.value) and "secret" not in str(exc.value)
    assert source.read_bytes() == raw


@pytest.mark.parametrize(
    "fault", ["hash", "profile", "evidence_id", "symlink", "bytes", "depth", "records"]
)
def test_hash_limits_and_caller_metadata_are_safe(tmp_path, fault):
    raw = b'{"usage":0}'
    if fault == "bytes":
        raw = b" " * (10 * 1024 * 1024 + 1)
    elif fault == "depth":
        raw = b"[" * 34 + b"0" + b"]" * 34
    elif fault == "records":
        raw = b"[" + b",".join([b"{}"] * 10001) + b"]"
    request, data, source = manifest(tmp_path, raw)
    entry = request["entries"][0]
    if fault == "hash":
        source.write_bytes(b"{}")
    elif fault in {"profile", "evidence_id"}:
        entry[fault] = "PRIVATE-SENTINEL"
    elif fault == "symlink":
        link = tmp_path / "link"
        link.symlink_to(source)
        entry["path"] = str(link)
    with pytest.raises(EvidenceError) as exc:
        inspect_manifest(request, data)
    assert "PRIVATE" not in str(exc.value) and str(source) not in str(exc.value)


def test_cli_errors_do_not_echo_arguments_and_documents_are_bounded(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "quality.source_feasibility", "--PRIVATE"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode and "PRIVATE" not in result.stdout + result.stderr
    source = tmp_path / "large-register"
    source.write_bytes(b" " * (10 * 1024 * 1024 + 1))
    with pytest.raises(EvidenceError):
        read_document(source)


@pytest.mark.parametrize("mode", ["check", "matrix"])
def test_cli_success_reports_do_not_approve_profiles(monkeypatch, capsys, mode):
    monkeypatch.setattr(sys, "argv", ["source-check", *(["--matrix"] if mode == "matrix" else [])])
    assert research.main() == 0
    output = capsys.readouterr()
    assert output.err == ""
    if mode == "matrix":
        assert output.out == research.render_matrix(registry()) + "\n"
    else:
        assert json.loads(output.out) == {"errors": [], "semantic_approval": False}


@pytest.mark.parametrize("changed_hash", [False, True])
def test_cli_private_manifest_report_and_hash_fault(tmp_path, monkeypatch, capsys, changed_hash):
    request, data, source = manifest(tmp_path, b'{"usage":0,"secret":"PRIVATE-SENTINEL"}')
    original = source.read_bytes()
    if changed_hash:
        request["entries"][0]["sha256"] = "0" * 64
    register_path = tmp_path / "PRIVATE-register.json"
    manifest_path = tmp_path / "PRIVATE-manifest.json"
    register_path.write_text(json.dumps(data))
    manifest_path.write_text(json.dumps(request))
    monkeypatch.setattr(
        sys,
        "argv",
        ["source-check", "--register", str(register_path), "--manifest", str(manifest_path)],
    )
    assert research.main() == int(changed_hash)
    output = capsys.readouterr()
    assert "PRIVATE" not in output.out + output.err
    assert str(tmp_path) not in output.out + output.err
    if changed_hash:
        assert output.out == "" and output.err == "hash-mismatch\n"
    else:
        assert json.loads(output.out) == inspect_manifest(request, data)
        assert output.err == ""
    assert source.read_bytes() == original


def test_cli_matrix_drift_fault_and_repair(tmp_path, monkeypatch, capsys):
    register_path = ROOT / "docs/providers/source-profiles.json"
    fixture_path = tmp_path / "docs/providers/fixtures/source-feasibility-cases.json"
    fixture_path.parent.mkdir(parents=True)
    fixture_path.write_text(json.dumps(CASES))
    matrix_path = tmp_path / "docs/providers/source-feasibility.md"
    matrix_path.write_text("PRIVATE incorrect matrix")
    monkeypatch.setattr(research, "ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["source-check", "--register", str(register_path)])
    assert research.main() == 1
    assert json.loads(capsys.readouterr().out) == {
        "errors": ["matrix-drift"],
        "semantic_approval": False,
    }
    matrix_path.write_text(research.render_matrix(registry()))
    assert research.main() == 0
    assert json.loads(capsys.readouterr().out) == {"errors": [], "semantic_approval": False}


@pytest.mark.parametrize("fault", ["argument", "duplicate-register", "missing-register"])
def test_cli_rejections_keep_private_inputs_out_of_diagnostics(
    tmp_path, monkeypatch, capsys, fault
):
    private_path = tmp_path / "PRIVATE-register.json"
    arguments = ["--register", str(private_path)]
    expected = "source-unavailable"
    if fault == "argument":
        arguments = ["--PRIVATE-SENTINEL"]
        expected = "arguments-invalid"
    elif fault == "duplicate-register":
        private_path.write_text('{"PRIVATE":1,"PRIVATE":2}')
        expected = "duplicate-member"
    monkeypatch.setattr(sys, "argv", ["source-check", *arguments])
    assert research.main() == 1
    output = capsys.readouterr()
    assert output.out == "" and output.err == expected + "\n"
    assert "PRIVATE" not in output.err and str(tmp_path) not in output.err


@pytest.mark.parametrize("sample", CASES["cases"], ids=lambda c: c["id"])
def test_every_case_has_a_fault_and_repaired_oracle_control(sample):
    broken = copy.deepcopy(CASES)
    selected = next(c for c in broken["cases"] if c["id"] == sample["id"])
    field = next(iter(selected["expected"]))
    selected["expected"][field] = {"fault": True}
    assert research.check_cases(broken)
    selected["expected"] = copy.deepcopy(sample["expected"])
    assert research.check_cases(broken) == []


@pytest.mark.parametrize("field", ["span_id", "conversation"])
def test_missing_root_identity_has_no_accounting_authority(field):
    sample = case("cli-repeated-billing")
    for row in sample["records"]:
        if field == "span_id":
            row.pop("span_id")
        else:
            row["attributes"].pop("gen_ai.conversation.id")
    assert evaluate_case(sample, "spans")["authoritative_nano_aiu"] is None


def test_conflicting_corrections_and_unbound_snapshots():
    sample = case("correction")
    sample["records"][2]["amount"] = "0.04"
    assert evaluate_case(sample, "replacement")["current_amount"] is None
    sample = case("codex-usage-snapshot")
    sample["records"][1]["tokenUsage"]["total"]["totalTokens"] = 121
    assert evaluate_case(sample, "snapshot")["snapshot_total_tokens"] is None
    sample["records"][1]["tokenUsage"]["total"]["totalTokens"] = 120
    sample["records"][1].pop("turnId")
    assert evaluate_case(sample, "snapshot")["snapshot_total_tokens"] is None


def test_conflicting_checkpoints_are_not_terminal_usage():
    sample = case("copilot-hosted-usage-boundaries")
    checkpoint = copy.deepcopy(sample["records"][1])
    checkpoint["data"]["totalNanoAiu"] = 1
    sample["records"].append(checkpoint)
    assert evaluate_case(sample, "hosted")["checkpoint_conflict"] is True
    assert evaluate_case(sample, "hosted")["final_session_nano_aiu"] is None
    sample["records"].pop()
    assert evaluate_case(sample, "hosted")["checkpoint_conflict"] is False


@pytest.mark.parametrize(
    "kind,expected",
    [("progress", False), ("replay", False), ("conflict", True), ("other-session", False)],
)
def test_checkpoint_conflicts_are_scoped_to_sdk_session_and_event(kind, expected):
    sample = case("copilot-hosted-usage-boundaries")
    checkpoint = copy.deepcopy(sample["records"][1])
    if kind != "replay":
        checkpoint["data"]["totalNanoAiu"] = 400000000
    if kind == "progress":
        checkpoint["id"] = "event-002"
    elif kind == "other-session":
        # Authored scope context is not a claimed native event field.
        checkpoint["synthetic_context"] = {"sdk_session_id": "sdk-session-002"}
    sample["records"].append(checkpoint)
    result = evaluate_case(sample, "hosted")
    assert result["checkpoint_conflict"] is expected
    assert result["final_session_nano_aiu"] is None
    assert result["overlapping_totals_additive"] is False
    assert result["approved_profile"] is False


@pytest.mark.parametrize(
    "missing", ["event", "blank-event", "session", "blank-session", "record-scope"]
)
def test_checkpoint_missing_identity_is_unresolved(missing):
    sample = case("copilot-hosted-usage-boundaries")
    checkpoint = sample["records"][1]
    if missing == "event":
        checkpoint.pop("id")
    elif missing == "blank-event":
        checkpoint["id"] = " "
    elif missing == "session":
        sample["identity_evidence"].pop("sdk_session_id")
    elif missing == "blank-session":
        sample["identity_evidence"]["sdk_session_id"] = " "
    else:
        checkpoint["synthetic_context"] = {}
    result = evaluate_case(sample, "hosted")
    assert result["checkpoint_conflict"] is None
    assert result["final_session_nano_aiu"] is None
    assert result["overlapping_totals_additive"] is False


def test_parent_link_and_manifest_limits(tmp_path):
    request, data, source = manifest(tmp_path, b"{}")
    link = tmp_path / "directory-link"
    link.symlink_to(tmp_path, target_is_directory=True)
    request["entries"][0]["path"] = str(link / source.name)
    with pytest.raises(EvidenceError):
        inspect_manifest(request, data)
    with pytest.raises(EvidenceError):
        inspect_manifest({"entries": [{}] * 10001}, data)


def test_absent_parent_is_not_a_demonstrated_root():
    sample = case("cli-repeated-billing")
    for row in sample["records"]:
        row.pop("parent_span_id")
    assert evaluate_case(sample, "spans")["authoritative_nano_aiu"] is None


def test_orphaned_first_correction_and_missing_interval_remain_unknown():
    sample = case("correction")
    sample["records"] = sample["records"][1:]
    assert evaluate_case(sample, "replacement")["current_amount"] is None
    sample = case("claude-estimated-cost")
    for row in sample["records"]:
        row.pop("interval_start")
    assert evaluate_case(sample, "cumulative")["estimate_amount"] is None


def test_empty_and_incomplete_oracles_cannot_pass():
    for expected in ({}, {"billed_money": None}):
        bundle = copy.deepcopy(CASES)
        bundle["cases"][0]["expected"] = expected
        assert research.check_cases(bundle)
    assert research.check_cases(CASES) == []


@pytest.mark.parametrize("timestamp", ["definitely-not-a-date", "2000-01-01T00:00:00Z"])
def test_synthetic_wire_shapes_never_establish_native_compatibility(timestamp):
    sample = case("enterprise-projection-boundaries")
    for row in sample["records"]:
        row["created_at"] = timestamp
    assert evaluate_case(sample, "projection")["native_wire_compatible"] is False


def test_rollout_requires_events_and_one_explicit_versioned_session():
    sample = case("codex-rollout-cache-write")
    sample["records"] = sample["records"][:2]
    result = evaluate_case(sample, "rollout")
    assert result["cache_write_field"] == "absent"
    assert result["token_event_turn_id"] == "absent"
    assert result["snapshot_total_tokens"] is None
    sample = case("codex-rollout-cache-write")
    other = copy.deepcopy(sample["records"][0])
    other["payload"]["id"] = "other-session"
    other["payload"]["cli_version"] = "other-version"
    sample["records"].append(other)
    assert evaluate_case(sample, "rollout")["snapshot_total_tokens"] is None
    sample["records"].pop()
    assert evaluate_case(sample, "rollout")["snapshot_total_tokens"] == 120


def test_catalog_export_flag_does_not_claim_payload_inspection():
    sample = case("copilot-container-absence")
    sample["records"][1]["payload_exported"] = True
    actual = evaluate_case(sample, "containers")
    assert actual["sdk_usage_checkpoint"] == "not inspected"
    assert actual["per_session_turn_usage"] == "not inspected"


@pytest.mark.parametrize("fault", ["references", "requirements", "fields", "reference_date"])
def test_register_required_evidence_metadata(fault):
    data = registry()
    profile = data["profiles"][0]
    if fault == "references":
        profile.pop("references")
    elif fault == "reference_date":
        profile["references"][0]["accessed"] = "2026-99-99"
    else:
        profile[fault] = [123] if fault == "requirements" else {"counter": 123}
    assert research.validate_register(data)
    assert research.validate_register(registry()) == []


def test_enterprise_derivative_hash_provenance():
    data = registry()
    digest = hashlib.sha256(
        (ROOT / "docs/providers/fixtures/source-feasibility-cases.json").read_bytes()
    ).hexdigest()
    for profile in data["profiles"]:
        for evidence in profile["evidence"]:
            if evidence["sha256"] == digest:
                assert evidence["origin"] == "synthetic"
    assert {"codex-ide", "claude-ide"} <= {p["id"] for p in data["profiles"]}


@pytest.mark.parametrize("replacement", [True, False, "1", 1.0, -1])
def test_replacement_reference_requires_exact_integer(replacement):
    sample = case("correction")
    for row in sample["records"]:
        if "replaces_revision" in row:
            row["replaces_revision"] = replacement
    with pytest.raises(EvidenceError):
        evaluate_case(sample, "replacement")
    assert evaluate_case(case("correction"), "replacement")["current_amount"] == "0.03"


@pytest.mark.parametrize(
    "start,end",
    [
        ("bad", "also bad"),
        ("2000-01-01", "2000-01-02"),
        ("2000-01-01T00:00:00", "2000-01-01T00:01:00"),
        ("2000-01-01T00:02:00Z", "2000-01-01T00:01:00Z"),
        (None, "2000-01-01T00:01:00Z"),
    ],
)
def test_invalid_cumulative_interval_is_unresolved(start, end):
    sample = case("claude-estimated-cost")
    for row in sample["records"]:
        row["interval_start"], row["interval_end"] = start, end
    assert evaluate_case(sample, "cumulative")["estimate_amount"] is None
    assert evaluate_case(case("claude-estimated-cost"), "cumulative")["estimate_amount"] == "0.03"


def test_cumulative_offset_instants_and_normalized_duplicate_ends():
    sample = case("claude-estimated-cost")
    first = copy.deepcopy(sample["records"][0])
    first.update(
        interval_start="2000-01-01T00:00:00Z",
        interval_end="2000-01-01T02:01:00+02:00",
        value="0.01",
    )
    second = copy.deepcopy(first)
    second.update(
        interval_start="1999-12-31T19:00:00-05:00",
        interval_end="2000-01-01T00:02:00Z",
        value="0.03",
    )
    sample["records"] = [second, first, copy.deepcopy(second)]
    assert evaluate_case(sample, "cumulative")["estimate_amount"] == "0.03"
    conflict = copy.deepcopy(second)
    conflict.update(interval_end="2000-01-01T02:02:00+02:00", value="0.04")
    sample["records"].append(conflict)
    assert evaluate_case(sample, "cumulative")["estimate_amount"] is None


@pytest.mark.parametrize("mode", ["absent", "missing", "null"])
def test_absent_or_missing_checkpoint_quantity_is_unresolved(mode):
    sample = case("copilot-hosted-usage-boundaries")
    checkpoint = next(r for r in sample["records"] if r.get("type") == "session.usage_checkpoint")
    if mode == "absent":
        sample["records"] = [
            r for r in sample["records"] if r.get("type") != "session.usage_checkpoint"
        ]
    elif mode == "missing":
        checkpoint["data"].pop("totalNanoAiu")
    else:
        checkpoint["data"]["totalNanoAiu"] = None
    result = evaluate_case(sample, "hosted")
    assert result["checkpoint_conflict"] is None
    assert result["final_session_nano_aiu"] is None
    assert result["approved_profile"] is False


def test_known_checkpoint_conflict_precedes_incomplete_evidence():
    sample = case("copilot-hosted-usage-boundaries")
    checkpoint = next(r for r in sample["records"] if r.get("type") == "session.usage_checkpoint")
    incomplete = copy.deepcopy(checkpoint)
    incomplete.pop("id")
    conflict = copy.deepcopy(checkpoint)
    conflict["data"]["totalNanoAiu"] += 1
    sample["records"].extend([incomplete, conflict])
    assert evaluate_case(sample, "hosted")["checkpoint_conflict"] is True
    sample["records"].pop()
    assert evaluate_case(sample, "hosted")["checkpoint_conflict"] is None
