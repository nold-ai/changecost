"""Independent source-boundary expectations and adversarial inspection controls."""

from __future__ import annotations

import copy
import csv
import hashlib
import json
import subprocess
import sys
from itertools import product
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
    historical_hashes = {
        "copilot-hosted": "6023c198c83e255c55a98712d357c9978a87e5063d0e24d1e760319fcbf44180",
        "copilot-cli": "abcd4945121a12b1dd02c622ea03bff176955f3b621ea5cf7a9f165abaef0364",
        "copilot-ide": "aff5df04a3e0d37b6ded31fd6eacfff01925ec887fecdc5c342a6b29701784f7",
        "cursor-local": "5b2e9263b9eb2dc677529b1030683be7ee2809aff1a56228cef0ea81cf4c655d",
        "cursor-personal-csv": "afc0017691d66b21b1184adb6f19d97e79033514d2de84df79bfbd4bfa9c1d67",
        "codex-app-server": "ffda8d3ebdf76fb04abc50cfe3c29c6365f62698f7f9de374ee69719811a5248",
        "codex-desktop": "98889ece4d50b656de0958ad6e1a0315641f65b8be4f272e7642d21a9feab77b",
        "claude-2-1-275": "4ca23a027f36639d1cd4e8750ed7d1a49285048dbf7bee7eb70aea8496bbf8cc",
        "claude-2-1-215": "5550865b536ab7b4338d0f60630b999329a0164c214d247f1b60b2908010e201",
        "claude-2-1-257": "20b0668a52ad10e8ab0d90dba45e04157e7d5a9d974ed7407f3a2430293211f9",
        "enterprise-copilot-projections": (
            "926efcfbec9b2a3ecb10575b0e1aaa5c978256b060b48980aa4d30b2eaa105cb"
        ),
        "enterprise-cursor-projections": (
            "4065aa2d7ec17d1a504c8cf235b8ba2895621c8eecc4c58bac8f3f469d1a3de0"
        ),
        "codex-ide": "6830ffcf14ed1c6a73600354d56563d1c2dd3a725ddb0116be0fb351cffb0c27",
        "claude-ide": "ac9320d7ee47858dd2cb3da13504dc1f874a24463149540aa6d92afe80736d89",
        "codex-desktop-0-159-discovery": (
            "fe070af271281e3462a7bdbfad68ec76489c0cb4fac01a407e6a540aa4509a57"
        ),
        "claude-project-2-1-275-discovery": (
            "b7646d8cebeecde115d372441ed22fd5ee8e52545a98e2d5606c5ef119f51909"
        ),
        "claude-desktop-2-1-221-discovery": (
            "6a7a846904d5b71c800c07b6cd996415dfdd6f74edb9b08b94dbef02149bc65f"
        ),
        "claude-desktop-2-1-234-discovery": (
            "0966b73d63e297ff9377a749db992c28a9e538fd41e69ff357ea9ea738d0b849"
        ),
        "claude-desktop-result-mixed-headers": (
            "c8e479658daab7cdf3223d185e2e725c449bd316111b61f64e9b2c70415fc3f9"
        ),
        "claude-desktop-2-1-202-inventory": (
            "c9b59c26807b371cc2510526b185d85fb937e7560cadd89eb713795e737c5dbf"
        ),
        "claude-desktop-2-1-205-inventory": (
            "c4d508319e0aec010fcd1793429843ad323348eda19ab11e572315f856b5d9cd"
        ),
        "copilot-hosted-local-discovery": (
            "04e4237a91813223d017609dd5d25fd3373c88df65c7f728b096d6e5a83cd1da"
        ),
        "cursor-local-discovery": (
            "42c637e43803fa67e941c20ffd35dd03a6378282be322c2120318b8ceb55da23"
        ),
    }
    historical = {p["id"]: p for p in data["profiles"] if p["id"] in historical_hashes}
    assert set(historical) == set(historical_hashes)
    for identity, profile in historical.items():
        assert profile["approvals"] == []
        assert (
            hashlib.sha256(
                json.dumps(profile, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
            ).hexdigest()
            == historical_hashes[identity]
        )


def test_exact_finite_profile_and_proof_activation():
    data = registry()
    assert len(data["profiles"]) == 24
    activated = [p for p in data["profiles"] if p["approvals"]]
    assert len(activated) == 1
    assert (
        research.profile_digest(activated[0])
        == "8be47bbc66c0b04d61bcc4e646271449b4eb653b460c24322cfd203bc5d2a991"
    )
    assert len(activated[0]["approvals"]) == 1
    assert (
        hashlib.sha256(
            json.dumps(
                activated[0]["approvals"][0], sort_keys=True, separators=(",", ":"), allow_nan=False
            ).encode()
        ).hexdigest()
        == "081da0ec49ad6eb0b7bc17ff1757ce197f60a8f4dcc21ce49eddfcd2205d2e59"
    )


def test_matrix_drift_rejects_changed_capability():
    data = registry()
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
        assert output.out == ""
        assert json.loads(output.err) == {
            "error": "hash-mismatch",
            "profile": request["entries"][0]["profile"],
            "evidence_id": request["entries"][0]["evidence_id"],
        }
    else:
        assert json.loads(output.out) == inspect_manifest(request, data)
        assert output.err == ""
    assert source.read_bytes() == original


def test_cli_matrix_drift_fault_and_repair(tmp_path, monkeypatch, capsys):
    register_path = ROOT / "docs/providers/source-profiles.json"
    fixture_path = tmp_path / "docs/providers/fixtures/source-feasibility-cases.json"
    fixture_path.parent.mkdir(parents=True)
    fixture_path.write_bytes(
        (ROOT / "docs/providers/fixtures/source-feasibility-cases.json").read_bytes()
    )
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


ABSENT_IDENTITY = object()
INVALID_ID_LABELS = [ABSENT_IDENTITY, None, "", " ", "\t\u2003", True, 3, [], {}]
IDENTITY_CONSUMERS = [
    ("cli-repeated-billing", "spans", "conversation", "authoritative_nano_aiu"),
    ("cli-repeated-billing", "spans", "span", "authoritative_nano_aiu"),
    ("codex-usage-snapshot", "snapshot", "threadId", "snapshot_total_tokens"),
    ("codex-usage-snapshot", "snapshot", "turnId", "snapshot_total_tokens"),
    ("codex-rollout-cache-write", "rollout", "id", "snapshot_total_tokens"),
    ("codex-rollout-cache-write", "rollout", "cli_version", "snapshot_total_tokens"),
    (
        "copilot-hosted-usage-boundaries",
        "hosted",
        "host_session_id",
        "identity_namespaces_distinct",
    ),
    ("copilot-hosted-usage-boundaries", "hosted", "sdk_session_id", "identity_namespaces_distinct"),
]


def _assign_identity_label(mapping, key, value):
    if value is ABSENT_IDENTITY:
        mapping.pop(key, None)
    else:
        mapping[key] = value


@pytest.mark.parametrize("label", INVALID_ID_LABELS)
@pytest.mark.parametrize("name,strategy,field,result_key", IDENTITY_CONSUMERS)
def test_affirmative_identity_requires_nonblank_string(label, name, strategy, field, result_key):
    sample = case(name)
    if strategy == "spans":
        for row in sample["records"]:
            if field == "conversation":
                _assign_identity_label(row["attributes"], "gen_ai.conversation.id", label)
            else:
                _assign_identity_label(row, "span_id", label)
    elif strategy == "rollout":
        for row in sample["records"]:
            if row.get("type") == "session_meta":
                _assign_identity_label(row["payload"], field, label)
    elif strategy == "hosted":
        _assign_identity_label(sample["identity_evidence"], field, label)
    else:
        for row in sample["records"]:
            _assign_identity_label(row, field, label)
    result = evaluate_case(sample, strategy)
    assert result[result_key] is (False if strategy == "hosted" else None)
    assert result["approved_profile"] is False
    assert evaluate_case(case(name), strategy)[result_key] not in (None, False)


@pytest.mark.parametrize("field", ["event_id", "currency", "billing_basis"])
@pytest.mark.parametrize("label", INVALID_ID_LABELS)
def test_correction_requires_complete_economic_identity(field, label):
    sample = case("correction")
    for row in sample["records"]:
        _assign_identity_label(row, field, label)
    assert evaluate_case(sample, "replacement")["current_amount"] is None
    assert evaluate_case(case("correction"), "replacement")["current_amount"] == "0.03"


@pytest.mark.parametrize("field", ["event_id", "currency", "billing_basis"])
def test_correction_missing_or_mixed_basis_unresolved(field):
    sample = case("correction")
    for row in sample["records"]:
        row.pop(field)
    assert evaluate_case(sample, "replacement")["current_amount"] is None
    sample = case("correction")
    for row in sample["records"][1:]:
        row[field] = "another-valid-label"
    assert evaluate_case(sample, "replacement")["current_amount"] is None


@pytest.mark.parametrize("revision", [None, True, "1", 1.0, -1])
def test_required_revision_identity_rejects_optional_quantity_null(revision):
    sample = case("correction")
    sample["records"] = [sample["records"][0]]
    sample["records"][0]["revision"] = revision
    with pytest.raises(EvidenceError):
        evaluate_case(sample, "replacement")
    sample["records"][0]["revision"] = 0
    assert evaluate_case(sample, "replacement")["current_amount"] == "0.05"


def test_missing_revision_and_explicit_null_reference_reject():
    sample = case("correction")
    sample["records"] = [sample["records"][0]]
    sample["records"][0].pop("revision")
    with pytest.raises(EvidenceError):
        evaluate_case(sample, "replacement")
    sample = case("correction")
    for row in sample["records"][1:]:
        row["replaces_revision"] = None
    with pytest.raises(EvidenceError):
        evaluate_case(sample, "replacement")


def test_exact_labels_not_trimmed_and_correction_replay_preserved():
    sample = case("codex-usage-snapshot")
    sample["records"][1]["threadId"] = " " + sample["records"][0]["threadId"]
    assert evaluate_case(sample, "snapshot")["snapshot_total_tokens"] is None
    sample = case("correction")
    result = evaluate_case(sample, "replacement")
    assert result["current_amount"] == "0.03"
    assert result["retained_revision_count"] == 2
    assert result["billed_money"] is None


@pytest.mark.parametrize(
    "name,strategy",
    [("codex-usage-snapshot", "snapshot"), ("codex-rollout-cache-write", "rollout")],
)
@pytest.mark.parametrize(
    "amounts", [(1, True), (True, 1), (120, 120.0), (120.0, 120), (1, -1), (-1, 1)]
)
def test_every_total_validated_before_unique_selection(name, strategy, amounts):
    sample = case(name)
    records = (
        sample["records"]
        if strategy == "snapshot"
        else [
            r["payload"]
            for r in sample["records"]
            if r.get("payload", {}).get("type") == "token_count"
        ]
    )
    for row, amount in zip(records, amounts, strict=True):
        total = (
            row["tokenUsage"]["total"]
            if strategy == "snapshot"
            else row["info"]["total_token_usage"]
        )
        total["totalTokens" if strategy == "snapshot" else "total_tokens"] = amount
    with pytest.raises(EvidenceError):
        evaluate_case(sample, strategy)
    assert evaluate_case(case(name), strategy)["snapshot_total_tokens"] == 120


@pytest.mark.parametrize(
    "name,strategy",
    [("codex-usage-snapshot", "snapshot"), ("codex-rollout-cache-write", "rollout")],
)
@pytest.mark.parametrize(
    "amounts,expected",
    [((0, 0), 0), ((None, None), None), ((120, None), None), ((120, 121), None), ((120, 120), 120)],
)
def test_valid_zero_missing_conflict_and_replay_totals(name, strategy, amounts, expected):
    sample = case(name)
    records = (
        sample["records"]
        if strategy == "snapshot"
        else [
            r["payload"]
            for r in sample["records"]
            if r.get("payload", {}).get("type") == "token_count"
        ]
    )
    for row, amount in zip(records, amounts, strict=True):
        total = (
            row["tokenUsage"]["total"]
            if strategy == "snapshot"
            else row["info"]["total_token_usage"]
        )
        total["totalTokens" if strategy == "snapshot" else "total_tokens"] = amount
    assert evaluate_case(sample, strategy)["snapshot_total_tokens"] == expected


@pytest.mark.parametrize("field", ["uuid", "requestId", "message_id"])
@pytest.mark.parametrize("label", INVALID_ID_LABELS)
def test_message_correlation_identity_missing_partial_rows(field, label):
    sample = case("claude-message-revisions")
    row = sample["records"][1]
    mapping, key = (row["message"], "id") if field == "message_id" else (row, field)
    _assign_identity_label(mapping, key, label)
    result = evaluate_case(sample, "messages")
    assert result["request_count"] is None
    assert result["message_count"] is None
    assert result["record_count"] == 3
    assert result["usage_variant_count"] == 2
    assert result["additive_total"] is None
    repaired = evaluate_case(case("claude-message-revisions"), "messages")
    assert repaired["request_count"] == repaired["message_count"] == 1


def test_message_correlation_exact_replay_and_conflicting_record_mapping():
    sample = case("claude-message-revisions")
    sample["records"].append(copy.deepcopy(sample["records"][0]))
    result = evaluate_case(sample, "messages")
    assert result["record_count"] == 4
    assert result["request_count"] == result["message_count"] == 1
    sample["records"][-1]["requestId"] = "another-request"
    result = evaluate_case(sample, "messages")
    assert result["request_count"] is None and result["message_count"] is None
    sample["records"][-1]["uuid"] = "another-record"
    assert evaluate_case(sample, "messages")["request_count"] == 2


def test_message_correlation_true_distinct_exact_labels():
    sample = case("claude-message-revisions")
    sample["records"][1]["requestId"] = "request-002"
    sample["records"][1]["message"]["id"] = "message-002"
    result = evaluate_case(sample, "messages")
    assert result["record_count"] == 3
    assert result["request_count"] == result["message_count"] == 2
    assert result["final_usage"] == "unverified"


@pytest.mark.parametrize(
    "name,strategy",
    [("codex-usage-snapshot", "snapshot"), ("codex-rollout-cache-write", "rollout")],
)
def test_absent_total_is_unknown_not_zero(name, strategy):
    sample = case(name)
    row = sample["records"][0] if strategy == "snapshot" else sample["records"][-1]["payload"]
    total = (
        row["tokenUsage"]["total"] if strategy == "snapshot" else row["info"]["total_token_usage"]
    )
    total.pop("totalTokens" if strategy == "snapshot" else "total_tokens")
    assert evaluate_case(sample, strategy)["snapshot_total_tokens"] is None


def test_all_message_identifiers_missing_keep_physical_rows():
    sample = case("claude-message-revisions")
    for row in sample["records"]:
        row.pop("uuid")
        row.pop("requestId")
        row["message"].pop("id")
    result = evaluate_case(sample, "messages")
    assert result["request_count"] is None and result["message_count"] is None
    assert result["record_count"] == 3 and result["usage_variant_count"] == 2


@pytest.mark.parametrize("order", [(0, 1), (1, 0), (0, 1, 0)])
def test_public_registered_provenance_survives_order_and_replay(tmp_path, order):
    raw = b'{"usage":0,"requestId":"PRIVATE-SENTINEL"}'
    request, data, source = manifest(tmp_path, raw)
    profile = data["profiles"][0]
    other = copy.deepcopy(profile["evidence"][0])
    other["id"] = "second-safe-evidence"
    other["origin"] = "producer"
    profile["evidence"].append(other)
    entries = [request["entries"][0], copy.deepcopy(request["entries"][0])]
    entries[1]["evidence_id"] = other["id"]
    request["entries"] = [copy.deepcopy(entries[i]) for i in order]
    for entry in request["entries"]:
        entry["caller_label"] = "PRIVATE-CALLER-LABEL"
    reports = inspect_manifest(request, data)
    assert [(r["profile"], r["evidence_id"]) for r in reports] == [
        (profile["id"], entries[i]["evidence_id"]) for i in order
    ]
    assert len({r["sha256"] for r in reports}) == 1
    assert all(r["semantic_approval"] is False for r in reports)
    encoded = json.dumps(reports)
    assert "PRIVATE" not in encoded and str(source) not in encoded
    assert "requestId" not in encoded and "origin" not in encoded and "usage" not in encoded
    assert source.read_bytes() == raw


def test_public_reference_pair_scopes_same_evidence_label(tmp_path):
    request, data, _ = manifest(tmp_path, b'{"usage":0}')
    second = copy.deepcopy(data["profiles"][0])
    second["id"] = "second-safe-profile"
    data["profiles"].append(second)
    entry = copy.deepcopy(request["entries"][0])
    entry["profile"] = second["id"]
    request["entries"].append(entry)
    reports = inspect_manifest(request, data)
    assert reports[0]["evidence_id"] == reports[1]["evidence_id"]
    assert reports[0]["profile"] != reports[1]["profile"]


@pytest.mark.parametrize("kind", ["profile", "evidence"])
@pytest.mark.parametrize(
    "unsafe",
    [None, True, 7, [], {}, "", "PRIVATE-LABEL", "private/path", "private\nlabel", "a" * 81],
)
def test_direct_public_references_reject_unsafe_and_repair(tmp_path, kind, unsafe):
    request, data, _ = manifest(tmp_path, b'{"usage":0}')
    repaired = copy.deepcopy((request, data))
    if kind == "profile":
        data["profiles"][0]["id"] = unsafe
        request["entries"][0]["profile"] = unsafe
    else:
        data["profiles"][0]["evidence"][0]["id"] = unsafe
        request["entries"][0]["evidence_id"] = unsafe
    with pytest.raises(EvidenceError, match="^manifest-binding$"):
        inspect_manifest(request, data)
    reports = inspect_manifest(*repaired)
    assert reports[0]["profile"] == repaired[0]["entries"][0]["profile"]
    assert reports[0]["evidence_id"] == repaired[0]["entries"][0]["evidence_id"]


@pytest.mark.parametrize("kind", ["profile", "evidence"])
def test_public_reference_rejects_ambiguous_register_and_repairs(tmp_path, kind):
    request, data, _ = manifest(tmp_path, b'{"usage":0}')
    repaired = copy.deepcopy(data)
    if kind == "profile":
        data["profiles"].append(copy.deepcopy(data["profiles"][0]))
    else:
        items = data["profiles"][0]["evidence"]
        items.append(copy.deepcopy(items[0]))
    with pytest.raises(EvidenceError, match="^manifest-binding$"):
        inspect_manifest(request, data)
    assert (
        inspect_manifest(request, repaired)[0]["evidence_id"]
        == request["entries"][0]["evidence_id"]
    )


@pytest.mark.parametrize("kind", ["profile", "evidence_id"])
def test_public_reference_unknown_manifest_label_does_not_echo(tmp_path, kind):
    request, data, _ = manifest(tmp_path, b'{"usage":0}')
    repaired = copy.deepcopy(request)
    request["entries"][0][kind] = "private-unregistered-label"
    with pytest.raises(EvidenceError, match="^manifest-binding$"):
        inspect_manifest(request, data)
    assert inspect_manifest(repaired, data)[0]["profile"] == repaired["entries"][0]["profile"]


@pytest.mark.parametrize("fault", ["hash", "malformed", "fields", "later-entry"])
def test_validated_provenance_failure_diagnostic_and_atomic_output(
    tmp_path, monkeypatch, capsys, fault
):
    request, data, source = manifest(tmp_path, b'{"usage":0,"secret":"PRIVATE-PAYLOAD"}')
    raw = source.read_bytes()
    if fault == "hash":
        request["entries"][0]["sha256"] = "0" * 64
    elif fault == "malformed":
        source.write_bytes(b'{"PRIVATE-PAYLOAD":')
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        request["entries"][0]["sha256"] = digest
        data["profiles"][0]["evidence"][0]["sha256"] = digest
    elif fault == "fields":
        request["entries"][0]["fields"] = "PRIVATE-SELECTOR"
    else:
        other = copy.deepcopy(request["entries"][0])
        other["sha256"] = "0" * 64
        request["entries"].append(other)
    register_path = tmp_path / "PRIVATE-register.json"
    manifest_path = tmp_path / "PRIVATE-manifest.json"
    register_path.write_text(json.dumps(data))
    manifest_path.write_text(json.dumps(request))
    monkeypatch.setattr(
        sys,
        "argv",
        ["source-check", "--register", str(register_path), "--manifest", str(manifest_path)],
    )
    assert research.main() == 1
    output = capsys.readouterr()
    assert output.out == ""
    diagnostic = json.loads(output.err)
    assert diagnostic["profile"] == request["entries"][0]["profile"]
    assert diagnostic["evidence_id"] == request["entries"][0]["evidence_id"]
    assert "sha256" not in diagnostic  # failed hashing/parsing never asserts verified success
    assert "PRIVATE" not in output.err and str(source) not in output.err
    # The same valid reference succeeds after repairing the targeted fault.
    source.write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    data["profiles"][0]["evidence"][0]["sha256"] = digest
    request["entries"] = [request["entries"][0]]
    request["entries"][0]["sha256"] = digest
    request["entries"][0]["fields"] = [["usage"]]
    register_path.write_text(json.dumps(data))
    manifest_path.write_text(json.dumps(request))
    assert research.main() == 0
    repaired = capsys.readouterr()
    assert repaired.err == ""
    assert json.loads(repaired.out)[0]["evidence_id"] == diagnostic["evidence_id"]


@pytest.mark.parametrize("kind", ["profile", "evidence"])
def test_unsafe_registered_cli_labels_remain_redacted(tmp_path, monkeypatch, capsys, kind):
    request, data, _ = manifest(tmp_path, b'{"usage":0}')
    if kind == "profile":
        data["profiles"][0]["id"] = "PRIVATE/IDENTIFIER"
        request["entries"][0]["profile"] = "PRIVATE/IDENTIFIER"
    else:
        data["profiles"][0]["evidence"][0]["id"] = "PRIVATE/IDENTIFIER"
        request["entries"][0]["evidence_id"] = "PRIVATE/IDENTIFIER"
    register_path = tmp_path / "PRIVATE-register.json"
    manifest_path = tmp_path / "PRIVATE-manifest.json"
    register_path.write_text(json.dumps(data))
    manifest_path.write_text(json.dumps(request))
    monkeypatch.setattr(
        sys,
        "argv",
        ["source-check", "--register", str(register_path), "--manifest", str(manifest_path)],
    )
    assert research.main() == 1
    output = capsys.readouterr()
    assert output.out == "" and output.err == "register-invalid\n"


def test_safe_reference_length_boundary_and_unknown_later_entry(tmp_path):
    request, data, _ = manifest(tmp_path, b'{"usage":0}')
    data["profiles"][0]["id"] = "p" * 80
    data["profiles"][0]["evidence"][0]["id"] = "e" * 80
    request["entries"][0]["profile"] = "p" * 80
    request["entries"][0]["evidence_id"] = "e" * 80
    assert inspect_manifest(request, data)[0]["evidence_id"] == "e" * 80
    other = copy.deepcopy(request["entries"][0])
    other["evidence_id"] = "PRIVATE-UNREGISTERED"
    request["entries"].append(other)
    with pytest.raises(EvidenceError) as failure:
        inspect_manifest(request, data)
    assert failure.value.public_diagnostic() == "manifest-binding"


@pytest.mark.parametrize(
    "labels",
    [
        (True, True),
        (1, 1),
        (1.0, 1.0),
        (" ", " "),
        ("\t\u2003", "\t\u2003"),
        (None, None),
        ("valid.metric", None),
        (True, 1),
        (1, True),
        ([], {}),
        (ABSENT_IDENTITY, "claude_code.cost.usage"),
    ],
)
def test_cumulative_metric_identity_fault_and_repaired_series(labels):
    sample = case("claude-estimated-cost")
    for row, label in zip(sample["records"], labels, strict=True):
        if label is ABSENT_IDENTITY:
            row.pop("metric")
        else:
            row["metric"] = label
    result = evaluate_case(sample, "cumulative")
    assert result["estimate_amount"] is None
    assert result["currency"] == "USD" and result["attribution"] == "unbound"
    assert result["billed_money"] is None and result["approved_profile"] is False
    repaired = evaluate_case(case("claude-estimated-cost"), "cumulative")
    assert repaired["estimate_amount"] == "0.03"


def test_cumulative_identity_exact_strings_and_validation_precedence():
    sample = case("claude-estimated-cost")
    sample["records"][1]["metric"] += " "
    assert evaluate_case(sample, "cumulative")["estimate_amount"] is None
    sample["records"][0]["metric"] = sample["records"][1]["metric"]
    assert evaluate_case(sample, "cumulative")["estimate_amount"] == "0.03"
    for row in sample["records"]:
        row["value"] = "0.000000001"
    assert evaluate_case(sample, "cumulative")["estimate_amount"] == "0.000000001"
    for row in sample["records"]:
        row["value"] = "0"
    assert evaluate_case(sample, "cumulative")["estimate_amount"] == "0"
    sample["records"][0]["metric"] = None
    sample["records"][0]["value"] = "not-a-decimal"
    with pytest.raises(EvidenceError, match="^invalid-decimal$"):
        evaluate_case(sample, "cumulative")


@pytest.mark.parametrize("reference", [None, True, 0, 1, "1", " ", [], {}])
def test_projection_reference_presence_never_proves_billing_correction(reference):
    sample = case("enterprise-projection-boundaries")
    sample["records"][0].update(
        {
            "replaces_revision": reference,
            "revision": 2,
            "event_id": "event-001",
            "amount": "0.03",
            "currency": "USD",
            "billing_basis": "claimed-charge",
        }
    )
    result = evaluate_case(sample, "projection")
    assert result["billing_correction_observed"] is False
    assert result["native_wire_compatible"] is False
    assert result["cross_session_overlap"] == "unverified"
    assert result["consumed_tokens"] is None and result["billed_money"] is None
    assert result["approved_profile"] is False
    assert (
        evaluate_case(case("enterprise-projection-boundaries"), "projection")[
            "billing_correction_observed"
        ]
        is False
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("event_id", "another-event"),
        ("event_id", None),
        ("event_id", " "),
        ("event_id", True),
        ("event_id", []),
        ("currency", "EUR"),
        ("currency", None),
        ("billing_basis", "another-basis"),
        ("billing_basis", {}),
    ],
)
def test_unsupported_correction_scope_cannot_claim_retained_revision_count(field, value):
    sample = case("correction")
    extra = copy.deepcopy(sample["records"][0])
    extra[field] = value
    sample["records"].append(extra)
    result = evaluate_case(sample, "replacement")
    assert result["current_amount"] is None
    assert result["retained_revision_count"] is None
    repaired = evaluate_case(case("correction"), "replacement")
    assert repaired["current_amount"] == "0.03" and repaired["retained_revision_count"] == 2


def test_complete_history_cardinality_separate_from_current_amount():
    sample = case("correction")
    sample["records"].append(copy.deepcopy(sample["records"][0]))
    result = evaluate_case(sample, "replacement")
    assert result["retained_revision_count"] == 2 and result["current_amount"] == "0.03"
    sample["records"][-1]["amount"] = "0.06"
    result = evaluate_case(sample, "replacement")
    assert result["retained_revision_count"] == 2 and result["current_amount"] is None
    sample = case("correction")
    later = copy.deepcopy(sample["records"][1])
    later.update({"revision": 3, "replaces_revision": 2, "amount": "0.02"})
    sample["records"].append(later)
    result = evaluate_case(sample, "replacement")
    assert result["retained_revision_count"] == 3 and result["current_amount"] == "0.02"


@pytest.mark.parametrize("quantity", [0, None, ABSENT_IDENTITY, True, False, -1])
def test_inventory_context_occupancy_quantity_and_native_boundaries(quantity):
    sample = case("cursor-context-not-consumption")
    if quantity is ABSENT_IDENTITY:
        sample["records"][0].pop("contextTokensUsed")
    else:
        sample["records"][0]["contextTokensUsed"] = quantity
    if type(quantity) is bool or quantity == -1:
        with pytest.raises(EvidenceError, match="^invalid-quantity$"):
            evaluate_case(sample, "context")
    else:
        result = evaluate_case(sample, "context")
        assert result["context_occupancy_tokens"] == (0 if quantity == 0 else None)
        assert result["consumed_tokens"] is None and result["session_finality"] == "unverified"
    assert (
        evaluate_case(case("cursor-context-not-consumption"), "context")["context_occupancy_tokens"]
        == 120
    )


@pytest.mark.parametrize("value", [True, "70", None, ABSENT_IDENTITY])
def test_inventory_counter_type_observation_and_repaired_input(value):
    sample = case("enterprise-message-counter-boundary")
    metadata = sample["records"][0]["v"]["metadata"]
    if value is ABSENT_IDENTITY:
        metadata.pop("promptTokens")
    else:
        metadata["promptTokens"] = value
    result = evaluate_case(sample, "counters")
    assert result["field_type_evidence"] == "unverified"
    assert result["additive_session_tokens"] is None and result["billed_money"] is None
    repaired = evaluate_case(case("enterprise-message-counter-boundary"), "counters")
    assert repaired["field_type_evidence"] == "producer-reported integer paths"
    assert repaired["approved_profile"] is False


@pytest.mark.parametrize("value", [True, "1", 2, None])
def test_inventory_enum_scalar_observation_not_native_compatibility(value):
    sample = case("documented-example-not-wire-evidence")
    for row in sample["records"]:
        row["aggregationTemporality"] = value
    result = evaluate_case(sample, "encoding")
    assert result["integer_enum_valid_for_delta"] is False
    assert result["native_export_observed"] is False and result["hook_mapping_verified"] is False
    repaired = case("documented-example-not-wire-evidence")
    repaired["records"][0]["aggregationTemporality"] = 1
    assert evaluate_case(repaired, "encoding")["integer_enum_valid_for_delta"] is True


def test_inventory_rollout_field_presence_is_only_metadata():
    sample = case("codex-rollout-cache-write")
    events = [
        r["payload"] for r in sample["records"] if r.get("payload", {}).get("type") == "token_count"
    ]
    for event in events:
        event["info"]["total_token_usage"].pop("cache_write_input_tokens")
    assert evaluate_case(sample, "rollout")["cache_write_field"] == "absent"
    for event in events:
        event["info"]["total_token_usage"]["cache_write_input_tokens"] = None
        event["turn_id"] = True
    result = evaluate_case(sample, "rollout")
    assert result["cache_write_field"] == "present" and result["token_event_turn_id"] == "present"
    assert result["snapshot_total_tokens"] == 120
    assert result["billed_money"] is None and result["approved_profile"] is False


@pytest.mark.parametrize("name", list(STRATEGIES))
def test_inventory_positive_looking_claims_never_promote_native_support(name):
    sample = case(name)
    sample.update(
        {
            "provenance": "native",
            "approved_profile": True,
            "native_export_observed": True,
            "hook_mapping_verified": True,
            "billed_money": "0.01",
        }
    )
    result = evaluate_case(sample, STRATEGIES[name])
    assert result["billed_money"] is None and result["approved_profile"] is False
    for key in ["native_export_observed", "hook_mapping_verified", "native_wire_compatible"]:
        if key in result:
            assert result[key] is False
    repaired = evaluate_case(case(name), STRATEGIES[name])
    assert repaired["billed_money"] is None and repaired["approved_profile"] is False


@pytest.mark.parametrize(
    "extra",
    [
        {"input_tokens": 999, "output_tokens": 888},
        {"input_tokens": 100, "output_tokens": 20},
        {"input_tokens": True},
        {"input_tokens": "bad"},
        {},
        {"input_tokens": 0, "output_tokens": 0},
    ],
)
@pytest.mark.parametrize("reverse", [False, True])
def test_tokens_only_rejects_extra_records_without_first_row_selection(extra, reverse):
    sample = case("tokens-only")
    sample["records"].append(extra)
    if reverse:
        sample["records"].reverse()
    with pytest.raises(EvidenceError):
        evaluate_case(sample, STRATEGIES["tokens-only"])
    bundle = copy.deepcopy(CASES)
    bundle["cases"] = [sample if c["id"] == "tokens-only" else c for c in bundle["cases"]]
    assert research.check_cases(bundle) == ["case-invalid"]
    repaired = evaluate_case(case("tokens-only"), STRATEGIES["tokens-only"])
    assert (repaired["input_tokens"], repaired["output_tokens"]) == (100, 20)
    assert repaired["billed_money"] is None and repaired["approved_profile"] is False


@pytest.mark.parametrize(
    "record,expected", [({}, (None, None)), ({"input_tokens": 0, "output_tokens": 0}, (0, 0))]
)
def test_single_token_sample_preserves_zero_and_missing(record, expected):
    sample = case("tokens-only")
    sample["records"] = [record]
    result = evaluate_case(sample, STRATEGIES["tokens-only"])
    assert (result["input_tokens"], result["output_tokens"]) == expected
    for name in ["timestamp-only", "ambiguous-overlap"]:
        control = case(name)
        assert len(control["records"]) > 1
        assert {
            k: evaluate_case(control, STRATEGIES[name])[k] for k in control["expected"]
        } == control["expected"]


@pytest.mark.parametrize(
    "fields,requirements",
    [({}, None), (None, []), ({}, []), ({"x": " "}, None), (None, [" "]), ([], None), (None, {})],
)
def test_partial_profile_requires_nonempty_valid_evidence_details(fields, requirements):
    register = json.loads((ROOT / "docs/providers/source-profiles.json").read_text())
    profile = register["profiles"][0]
    if fields is not None:
        profile["fields"] = fields
    if requirements is not None:
        profile["requirements"] = requirements
    assert research.validate_register(register)
    repaired = json.loads((ROOT / "docs/providers/source-profiles.json").read_text())
    assert research.validate_register(repaired) == []


def test_nonpartial_profile_does_not_require_unresolved_details():
    register = json.loads((ROOT / "docs/providers/source-profiles.json").read_text())
    profile = register["profiles"][0]
    profile["capabilities"] = {key: "unavailable" for key in research.CAPABILITIES}
    profile["fields"] = {}
    profile["requirements"] = []
    assert research.validate_register(register) == []


def bind_supported_control_approvals(profile):
    evidence = profile["evidence"][0]
    profile["approvals"] = [
        {
            "capability": capability,
            "evidence_id": evidence["id"],
            "sha256": evidence["sha256"],
            "profile_digest": research.profile_digest(profile),
            "reviewer": "synthetic-control-reviewer",
            "decisions": {key: "synthetic boundary control" for key in research.DECISIONS},
        }
        for capability, disposition in profile["capabilities"].items()
        if disposition == "supported"
    ]


def test_all_register_dispositions_require_their_evidence_details():
    baseline = registry()
    for dispositions in product(["supported", "partial", "unverified", "unavailable"], repeat=4):
        for has_fields, has_requirements in product([False, True], repeat=2):
            data = copy.deepcopy(baseline)
            profile = data["profiles"][0]
            profile["capabilities"] = dict(zip(research.CAPABILITIES, dispositions, strict=True))
            profile["fields"] = {"quantity": "synthetic control meaning"} if has_fields else {}
            profile["requirements"] = ["synthetic unresolved boundary"] if has_requirements else []
            bind_supported_control_approvals(profile)
            fields_needed = any(value in {"supported", "partial"} for value in dispositions)
            requirements_needed = any(value in {"partial", "unverified"} for value in dispositions)
            expected_valid = (has_fields or not fields_needed) and (
                has_requirements or not requirements_needed
            )
            assert (research.validate_register(data) == []) is expected_valid, (
                dispositions,
                has_fields,
                has_requirements,
            )


@pytest.mark.parametrize("capability", research.CAPABILITIES)
@pytest.mark.parametrize(
    "disposition,field,value",
    [
        ("supported", "fields", {}),
        ("supported", "fields", []),
        ("supported", "fields", {"x": " "}),
        ("unverified", "requirements", []),
        ("unverified", "requirements", {}),
        ("unverified", "requirements", [" "]),
    ],
)
def test_required_register_details_reject_in_load_and_matrix(
    tmp_path, capability, disposition, field, value
):
    data = registry()
    profile = data["profiles"][0]
    profile["capabilities"] = {key: "unavailable" for key in research.CAPABILITIES}
    profile["capabilities"][capability] = disposition
    profile[field] = value
    bind_supported_control_approvals(profile)
    assert research.validate_register(data)
    path = tmp_path / "synthetic-register.json"
    path.write_text(json.dumps(data))
    with pytest.raises(EvidenceError):
        research.load_register(path)
    with pytest.raises(EvidenceError):
        research.render_matrix(data)
    profile[field] = (
        {"quantity": "synthetic meaning"}
        if field == "fields"
        else ["synthetic unresolved boundary"]
    )
    bind_supported_control_approvals(profile)
    assert research.validate_register(data) == []
    assert research.render_matrix(data)


@pytest.mark.parametrize("timestamp", ["0001-01-01T00:00:00+23:59", "9999-12-31T23:59:59-23:59"])
@pytest.mark.parametrize("field", ["interval_start", "interval_end"])
def test_utc_overflow_stays_unresolved_with_repaired_interval(timestamp, field):
    sample = case("claude-estimated-cost")
    sample["records"][0][field] = timestamp
    result = evaluate_case(sample, "cumulative")
    assert result["estimate_amount"] is None and result["billed_money"] is None
    assert evaluate_case(case("claude-estimated-cost"), "cumulative")["estimate_amount"] == "0.03"


@pytest.mark.parametrize(
    "name,path",
    [
        ("cli-repeated-billing", ["attributes"]),
        ("codex-usage-snapshot", ["tokenUsage"]),
        ("codex-usage-snapshot", ["tokenUsage", "total"]),
        ("codex-rollout-cache-write", ["payload"]),
        ("claude-message-revisions", ["message"]),
        ("enterprise-message-counter-boundary", ["v"]),
        ("enterprise-message-counter-boundary", ["v", "metadata"]),
        ("codex-rollout-cache-write", ["payload", "info"]),
        ("codex-rollout-cache-write", ["payload", "info", "total_token_usage"]),
        ("copilot-hosted-usage-boundaries", ["identity_evidence"]),
        ("copilot-hosted-usage-boundaries", ["data"]),
    ],
)
@pytest.mark.parametrize("malformed", [[], "private-malformed-payload", None])
def test_nested_case_mapping_faults_are_controlled(name, path, malformed):
    sample = case(name)
    candidates = [sample] if path[0] == "identity_evidence" else sample["records"]
    for target in candidates:
        try:
            for key in path[:-1]:
                target = target[key]
            if path[-1] in target:
                break
        except KeyError:
            continue
    else:
        pytest.fail("control path absent from original fixture")
    target[path[-1]] = malformed
    try:
        result = evaluate_case(sample, STRATEGIES[name])
    except EvidenceError as error:
        assert str(error) in {"case-shape", "invalid-quantity", "invalid-decimal"}
    else:
        assert result["approved_profile"] is False and result["billed_money"] is None
    bundle = copy.deepcopy(CASES)
    bundle["cases"] = [sample if item["id"] == name else item for item in bundle["cases"]]
    assert isinstance(research.check_cases(bundle), list)
    repaired = evaluate_case(case(name), STRATEGIES[name])
    assert {key: repaired[key] for key in case(name)["expected"]} == case(name)["expected"]


@pytest.mark.parametrize("wide_header", [False, True])
@pytest.mark.parametrize("multiline", [False, True])
def test_wide_csv_within_byte_bound_and_parser_limit_restored(tmp_path, wide_header, multiline):
    text = "é" * 100000 + ("\nquoted" if multiline else "")
    header, cell = (text, "value") if wide_header else ("value", text)
    raw = ('"' + header + '"\n"' + cell + '"\n').encode()
    original = csv.field_size_limit()
    csv.field_size_limit(64)
    try:
        local, data, _ = manifest(tmp_path, raw, "csv")
        local["entries"][0]["fields"] = [[header]]
        report = inspect_manifest(local, data)
        assert report[0]["semantic_approval"] is False
        assert csv.field_size_limit() == 64
        assert inspect_manifest(local, data) == report
        assert csv.field_size_limit() == 64
    finally:
        csv.field_size_limit(original)


def test_csv_parser_limit_restored_after_malformed_input(tmp_path):
    original = csv.field_size_limit()
    csv.field_size_limit(64)
    try:
        local, data, _ = manifest(tmp_path, b'header\n"unterminated', "csv")
        with pytest.raises(EvidenceError, match="malformed-input"):
            inspect_manifest(local, data)
        assert csv.field_size_limit() == 64
    finally:
        csv.field_size_limit(original)


@pytest.mark.parametrize("fault", ["nested", "overflow"])
def test_malformed_case_cli_has_fixed_private_diagnostics(monkeypatch, capsys, fault):
    bundle = copy.deepcopy(CASES)
    sample = next(
        c
        for c in bundle["cases"]
        if c["id"] == ("cli-repeated-billing" if fault == "nested" else "claude-estimated-cost")
    )
    if fault == "nested":
        sample["records"][0]["attributes"] = "private-native-payload-marker"
    else:
        sample["records"][0]["interval_start"] = "0001-01-01T00:00:00+23:59"
    # This control injects explicit in-memory semantics after real file provenance succeeds.
    original = research.check_cases
    monkeypatch.setattr(research, "check_cases", lambda checked_bundle: original(bundle))
    monkeypatch.setattr(sys, "argv", ["quality.source_feasibility"])
    assert research.main() == 1
    output = capsys.readouterr()
    assert json.loads(output.out)["semantic_approval"] is False
    assert "private-native-payload-marker" not in output.out + output.err
    assert "Traceback" not in output.out + output.err


def mutate_hosted_oracle_control(sample, fault):
    checkpoint = next(r for r in sample["records"] if r.get("type") == "session.usage_checkpoint")
    if fault in {"conflict", "conflict-and-incomplete", "replay", "progression", "cross-session"}:
        other = copy.deepcopy(checkpoint)
        if fault != "replay":
            other["data"]["totalNanoAiu"] += 1
        if fault == "progression":
            other["id"] = "another-event"
        if fault == "cross-session":
            other["synthetic_context"] = {"sdk_session_id": "another-synthetic-sdk-scope"}
        sample["records"].append(other)
        if fault == "conflict-and-incomplete":
            sample["records"].append({"type": "session.usage_checkpoint", "data": {}})
    elif fault == "missing-checkpoint":
        sample["records"] = [
            r for r in sample["records"] if r.get("type") != "session.usage_checkpoint"
        ]
    elif fault == "missing-amount":
        checkpoint["data"].pop("totalNanoAiu")
    elif fault == "missing-scope":
        sample["identity_evidence"].pop("sdk_session_id")
    elif fault == "missing-event":
        checkpoint.pop("id")


@pytest.mark.parametrize(
    "fault,rejected",
    [
        ("conflict", True),
        ("missing-checkpoint", True),
        ("missing-amount", True),
        ("missing-scope", True),
        ("missing-event", True),
        ("conflict-and-incomplete", True),
        ("replay", False),
        ("progression", False),
        ("cross-session", False),
        ("original", False),
    ],
)
def test_hosted_bundle_oracle_uses_computed_checkpoint_obligation(fault, rejected):
    bundle = copy.deepcopy(CASES)
    sample = next(c for c in bundle["cases"] if c["id"] == "copilot-hosted-usage-boundaries")
    expected = copy.deepcopy(sample["expected"])
    mutate_hosted_oracle_control(sample, fault)
    actual = evaluate_case(sample, "hosted")
    if fault == "conflict-and-incomplete":
        assert actual["checkpoint_conflict"] is True
    assert actual["approved_profile"] is False and actual["final_session_nano_aiu"] is None
    assert bool(research.check_cases(bundle)) is rejected
    assert sample["expected"] == expected
    assert research.check_cases(copy.deepcopy(CASES)) == []


@pytest.mark.parametrize("computed", [True, None, 0, "false"])
def test_hosted_bundle_requires_exact_false_not_falsy_or_declared_answers(monkeypatch, computed):
    original = research.evaluate_case

    def faulty(sample, strategy):
        result = original(sample, strategy)
        if strategy == "hosted":
            result["checkpoint_conflict"] = computed
        return result

    monkeypatch.setattr(research, "evaluate_case", faulty)
    assert research.check_cases(CASES)


def test_hosted_conflict_cli_rejects_without_private_identity(monkeypatch, capsys):
    bundle = copy.deepcopy(CASES)
    sample = next(c for c in bundle["cases"] if c["id"] == "copilot-hosted-usage-boundaries")
    checkpoint = next(r for r in sample["records"] if r.get("type") == "session.usage_checkpoint")
    checkpoint["id"] = "private-event-marker"
    other = copy.deepcopy(checkpoint)
    other["data"]["totalNanoAiu"] += 1
    sample["records"].append(other)
    # This control injects explicit in-memory semantics after real file provenance succeeds.
    original = research.check_cases
    monkeypatch.setattr(research, "check_cases", lambda checked_bundle: original(bundle))
    monkeypatch.setattr(sys, "argv", ["quality.source_feasibility"])
    assert research.main() == 1
    captured = capsys.readouterr()
    assert json.loads(captured.out)["errors"]
    assert "private-event-marker" not in captured.out + captured.err
    assert "Traceback" not in captured.out + captured.err


@pytest.mark.parametrize(
    "value", ["required-names", [], [["private-value"]], "private-value", 3, True, None]
)
def test_case_expectation_mapping_fault_repaired(value):
    bundle = copy.deepcopy(CASES)
    sample = bundle["cases"][0]
    sample["expected"] = (
        list(research.CONCLUSIONS[sample["id"]]) if value == "required-names" else value
    )
    assert research.check_cases(bundle) == ["case-invalid"]
    assert research.check_cases(copy.deepcopy(CASES)) == []


@pytest.mark.parametrize(
    "fault", ["empty", "wrong-key", "nested-value", "wrong-scalar", "bool-alias"]
)
def test_case_expectation_mapping_preserves_coverage_and_exact_types(fault):
    bundle = copy.deepcopy(CASES)
    sample = bundle["cases"][0]
    if fault == "empty":
        sample["expected"] = {}
    elif fault == "wrong-key":
        sample["expected"] = {"private-value": 1}
    else:
        key = next(iter(sample["expected"]))
        sample["expected"][key] = {
            "nested-value": ["private-value"],
            "wrong-scalar": "private-value",
            "bool-alias": True,
        }[fault]
    expected = "oracle-coverage" if fault in ("empty", "wrong-key") else "conclusion-mismatch"
    assert research.check_cases(bundle) == [f"case:0:{expected}"]
    assert research.check_cases(CASES) == []


@pytest.mark.parametrize(
    "fault", ["bundle", "cases", "sample", "missing-id", "list-id", "duplicate-id"]
)
def test_case_metadata_inventory_fault_repaired(fault):
    bundle = copy.deepcopy(CASES)
    if fault == "bundle":
        bundle = []
    elif fault == "cases":
        bundle["cases"] = None
    elif fault == "sample":
        bundle["cases"][0] = []
    elif fault == "missing-id":
        del bundle["cases"][0]["id"]
    elif fault == "list-id":
        bundle["cases"][0]["id"] = []
    else:
        bundle["cases"][0]["id"] = bundle["cases"][1]["id"]
    assert research.check_cases(bundle) == [
        "case-inventory" if fault == "duplicate-id" else "case-invalid"
    ]
    assert research.check_cases(CASES) == []


def test_case_expectation_mapping_cli_privacy(monkeypatch, capsys):
    bundle = copy.deepcopy(CASES)
    bundle["cases"][0]["expected"] = list(research.CONCLUSIONS[bundle["cases"][0]["id"]])
    # This control injects explicit in-memory semantics after real file provenance succeeds.
    original = research.check_cases
    monkeypatch.setattr(research, "check_cases", lambda checked_bundle: original(bundle))
    monkeypatch.setattr(sys, "argv", ["source-feasibility"])
    assert research.main() == 1
    output = capsys.readouterr()
    assert json.loads(output.out) == {"errors": ["case-invalid"], "semantic_approval": False}
    assert "Traceback" not in output.out + output.err
    assert "private-value" not in output.out + output.err


@pytest.mark.parametrize("origin", ["native", "synthetic", "documentation", "producer"])
@pytest.mark.parametrize("scope", ["MISSING", "", "\u2003\u00a0", None, True, 7, [], {}])
def test_registered_evidence_scope_fault_repaired(origin, scope):
    data = registry()
    evidence = data["profiles"][0]["evidence"][0]
    evidence["origin"] = origin
    if scope == "MISSING":
        evidence.pop("scope")
    else:
        evidence["scope"] = scope
    assert research.validate_register(data)
    evidence["scope"] = "Coverage remains unknown; inspected selected bytes only"
    assert research.validate_register(data) == []


@pytest.mark.parametrize("scope", ["MISSING", "", None, True, {}])
def test_native_evidence_scope_fresh_proof_fault_repaired(scope):
    data = registry()
    profile = data["profiles"][0]
    if scope == "MISSING":
        profile["evidence"][0].pop("scope")
    else:
        profile["evidence"][0]["scope"] = scope
    profile["approvals"] = [approval(data)]
    assert research.validate_register(data)
    profile["evidence"][0]["scope"] = "Selected bytes; completeness unknown"
    profile["approvals"] = [approval(data)]
    assert research.validate_register(data) == []
    profile["evidence"][0]["scope"] = "Different selected bytes; completeness unknown"
    assert research.validate_register(data)
    profile["approvals"] = [approval(data)]
    assert research.validate_register(data) == []


def test_registered_evidence_scope_load_matrix_fault_repaired(tmp_path):
    data = registry()
    data["profiles"][0]["evidence"][0].pop("scope")
    path = tmp_path / "register.json"
    path.write_text(json.dumps(data))
    with pytest.raises(EvidenceError):
        research.load_register(path)
    with pytest.raises(EvidenceError):
        research.render_matrix(data)
    data["profiles"][0]["evidence"][0]["scope"] = "Coverage unknown"
    path.write_text(json.dumps(data))
    assert research.load_register(path) == data
    assert research.render_matrix(data)


def test_registered_evidence_scope_report_privacy(tmp_path):
    local, data, source = manifest(tmp_path, b'{"usage":0}')
    data["profiles"][0]["evidence"][0]["scope"] = "PRIVATE_SCOPE_DESCRIPTION"
    report = inspect_manifest(local, data)
    assert "PRIVATE_SCOPE_DESCRIPTION" not in json.dumps(report)
    source.write_bytes(b"{")
    with pytest.raises(EvidenceError) as caught:
        inspect_manifest(local, data)
    assert "PRIVATE_SCOPE_DESCRIPTION" not in caught.value.public_diagnostic()


@pytest.mark.parametrize("extra", ["replay", 3, "malformed", True, None, "missing"])
@pytest.mark.parametrize("reverse", [False, True])
def test_single_multiplier_extra_record_fault_repaired(extra, reverse):
    bundle = copy.deepcopy(CASES)
    sample = next(s for s in bundle["cases"] if s["id"] == "multiplier-only")
    row = copy.deepcopy(sample["records"][0])
    if extra == "missing":
        row["attributes"].pop("github.copilot.cost")
    elif extra != "replay":
        row["attributes"]["github.copilot.cost"] = extra
    sample["records"].append(row)
    if reverse:
        sample["records"].reverse()
    with pytest.raises(EvidenceError):
        evaluate_case(sample, STRATEGIES[sample["id"]])
    assert research.check_cases(bundle) == ["case-invalid"]
    assert research.check_cases(CASES) == []
    assert evaluate_case(case("multiplier-only"), STRATEGIES["multiplier-only"])["multiplier"] == 2
    roots = case("cli-repeated-billing")
    roots["records"].append(copy.deepcopy(roots["records"][0]))
    assert evaluate_case(roots, STRATEGIES[roots["id"]])["authoritative_nano_aiu"] == 100


def malformed_hosted_control(fault):
    sample = case("copilot-hosted-usage-boundaries")
    if fault == "missing-id":
        sample.pop("identity_evidence")
    elif fault == "conflict":
        row = copy.deepcopy(sample["records"][-1])
        row["data"]["totalNanoAiu"] += 1
        sample["records"].append(row)
    else:
        sample["records"][-1]["data"] = []
    return sample


@pytest.mark.parametrize("fault", ["missing-id", "conflict", "nested"])
@pytest.mark.parametrize("expected", [None, [], "malformed", True, {}, {"wrong": 1}])
def test_case_metadata_precedes_hosted_semantics(fault, expected):
    bundle = copy.deepcopy(CASES)
    sample = malformed_hosted_control(fault)
    sample["expected"] = expected
    index = next(i for i, s in enumerate(bundle["cases"]) if s["id"] == sample["id"])
    bundle["cases"][index] = sample
    diagnostic = (
        [f"case:{index}:oracle-coverage"] if isinstance(expected, dict) else ["case-invalid"]
    )
    assert research.check_cases(bundle) == diagnostic
    assert research.check_cases(CASES) == []


def test_compound_case_metadata_cli_privacy(monkeypatch, capsys):
    bundle = copy.deepcopy(CASES)
    sample = malformed_hosted_control("missing-id")
    sample["expected"] = "PRIVATE_EXPECTATIONS"
    bundle["cases"][13] = sample
    # This control injects explicit in-memory semantics after real file provenance succeeds.
    original = research.check_cases
    monkeypatch.setattr(research, "check_cases", lambda checked_bundle: original(bundle))
    monkeypatch.setattr(sys, "argv", ["source-feasibility"])
    assert research.main() == 1
    output = capsys.readouterr()
    assert json.loads(output.out) == {"errors": ["case-invalid"], "semantic_approval": False}
    assert "PRIVATE_EXPECTATIONS" not in output.out + output.err
    assert "Traceback" not in output.out + output.err


def test_valid_expectations_do_not_mask_nested_detector_failure():
    bundle = copy.deepcopy(CASES)
    bundle["cases"][13] = malformed_hosted_control("nested")
    assert research.check_cases(bundle) == ["case-invalid"]


@pytest.mark.parametrize(
    "url",
    [
        "https://",
        "https:///path",
        "https://?query",
        "https://#fragment",
        "http://example.org",
        "file:///private/path",
        "https://[",
        "https://[]",
        "https://   ",
        None,
        True,
        4,
        [],
        {},
    ],
)
def test_citation_destination_fault_repaired(tmp_path, url):
    data = registry()
    profile = data["profiles"][0]
    profile["references"][0]["url"] = url
    assert research.validate_register(data)
    path = tmp_path / "register.json"
    path.write_text(json.dumps(data))
    with pytest.raises(EvidenceError):
        research.load_register(path)
    with pytest.raises(EvidenceError):
        research.render_matrix(data)
    profile["references"][0]["url"] = "https://example.org/reference?version=1#usage"
    path.write_text(json.dumps(data))
    assert research.load_register(path) == data
    assert research.render_matrix(data)


@pytest.mark.parametrize("url", ["https://", "https:///path", "https://[", None])
def test_native_citation_fresh_binding_fault_repaired(url):
    data = registry()
    profile = data["profiles"][0]
    profile["references"][0]["url"] = url
    profile["approvals"] = [approval(data)]
    assert research.validate_register(data)
    profile["references"][0]["url"] = "https://example.org/first"
    profile["approvals"] = [approval(data)]
    assert research.validate_register(data) == []
    profile["references"][0]["url"] = "https://example.org/second"
    assert research.validate_register(data)
    profile["approvals"] = [approval(data)]
    assert research.validate_register(data) == []


@pytest.mark.parametrize(
    "url", ["https://example.org", "https://example.org/path?q=1#usage", "https://[::1]/reference"]
)
def test_citation_destination_structural_only_valid(url):
    data = registry()
    data["profiles"][0]["references"][0]["url"] = url
    assert research.validate_register(data) == []


@pytest.mark.parametrize(
    "fault",
    [
        "reserialized",
        "semantic",
        "stale-first",
        "stale-last",
        "missing-first",
        "missing-last",
        "wrong-origin",
    ],
)
def test_default_research_digest_fault_repaired(tmp_path, monkeypatch, capsys, fault):
    data = registry()
    raw = (ROOT / "docs/providers/fixtures/source-feasibility-cases.json").read_bytes()
    fixture = tmp_path / "docs/providers/fixtures/source-feasibility-cases.json"
    fixture.parent.mkdir(parents=True)
    fixture.write_bytes(raw)
    profile = next(
        p
        for p in data["profiles"]
        if p["id"] == ("claude-ide" if fault.endswith("last") else "copilot-cli")
    )
    if fault == "reserialized":
        fixture.write_text(json.dumps(CASES))
    elif fault == "semantic":
        changed = copy.deepcopy(CASES)
        changed["cases"][0]["records"][0]["attributes"]["private"] = "PRIVATE_PAYLOAD"
        fixture.write_text(json.dumps(changed))
    elif fault.startswith("stale"):
        profile["evidence"][0]["sha256"] = "0" * 64
    elif fault.startswith("missing"):
        profile["evidence"][0]["id"] += "-other"
    else:
        profile["evidence"][0]["origin"] = "producer"
    register_path = tmp_path / "PRIVATE-register.json"
    register_path.write_text(json.dumps(data))
    matrix_path = tmp_path / "docs/providers/source-feasibility.md"
    matrix_path.write_text(research.render_matrix(data))
    monkeypatch.setattr(research, "ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["source-check", "--register", str(register_path)])
    assert research.main() == 1
    output = capsys.readouterr()
    assert output.err.strip() == "research-provenance-invalid"
    assert output.out == ""
    assert "PRIVATE" not in output.out + output.err
    assert str(tmp_path) not in output.out + output.err
    fixture.write_bytes(raw)
    repaired = registry()
    register_path.write_text(json.dumps(repaired))
    matrix_path.write_text(research.render_matrix(repaired))
    assert research.main() == 0
    assert json.loads(capsys.readouterr().out) == {"errors": [], "semantic_approval": False}


def test_default_research_digest_reads_once_and_matrix_has_no_fixture(monkeypatch, capsys):
    from quality import source_inspection

    original = source_inspection._read
    calls = []

    def observed(path):
        calls.append(path)
        return original(path)

    monkeypatch.setattr(source_inspection, "_read", observed)
    monkeypatch.setattr(sys, "argv", ["source-check"])
    assert research.main() == 0
    assert sum(p.name == "source-feasibility-cases.json" for p in calls) == 1
    capsys.readouterr()
    calls.clear()
    monkeypatch.setattr(sys, "argv", ["source-check", "--matrix"])
    assert research.main() == 0
    assert not any(p.name == "source-feasibility-cases.json" for p in calls)


@pytest.mark.parametrize(
    "profile_id",
    [
        "copilot-cli",
        "copilot-ide",
        "cursor-personal-csv",
        "codex-app-server",
        "codex-desktop",
        "claude-2-1-275",
        "claude-2-1-215",
        "claude-2-1-257",
        "enterprise-copilot-projections",
        "enterprise-cursor-projections",
        "codex-ide",
        "claude-ide",
    ],
)
@pytest.mark.parametrize("fault", ["stale", "missing", "origin"])
def test_each_canonical_research_alias_is_required(profile_id, fault):
    data = registry()
    profile = next(p for p in data["profiles"] if p["id"] == profile_id)
    evidence = profile["evidence"][0]
    if fault == "stale":
        evidence["sha256"] = "0" * 64
    elif fault == "missing":
        evidence["id"] += "-other"
    else:
        evidence["origin"] = "documentation"
    with pytest.raises(EvidenceError, match="research-provenance-invalid"):
        research._research_digest(data)
    assert (
        research._research_digest(registry())
        == hashlib.sha256(
            (ROOT / "docs/providers/fixtures/source-feasibility-cases.json").read_bytes()
        ).hexdigest()
    )


def test_checked_document_hash_precedes_parse_and_same_read_bytes(tmp_path, monkeypatch):
    from quality import source_inspection

    path = tmp_path / "PRIVATE-source.json"
    raw = b'{"quantity":7}'
    path.write_bytes(raw)
    parsed = []
    original_parse = source_inspection._parse
    original_read = source_inspection._read

    def observed_parse(value, fmt):
        parsed.append(value)
        return original_parse(value, fmt)

    def replace_after_read(value):
        received = original_read(value)
        value.write_bytes(b'{"quantity":999}')
        return received

    monkeypatch.setattr(source_inspection, "_parse", observed_parse)
    with pytest.raises(EvidenceError, match="hash-mismatch"):
        source_inspection.read_checked_document(path, "0" * 64)
    assert parsed == []
    monkeypatch.setattr(source_inspection, "_read", replace_after_read)
    assert source_inspection.read_checked_document(path, hashlib.sha256(raw).hexdigest()) == {
        "quantity": 7
    }
    assert parsed == [raw]


@pytest.mark.parametrize(
    "raw,diagnostic", [(b'{"x":1,"x":2}', "duplicate-member"), (b"\xff", "malformed-input")]
)
def test_checked_document_retains_parser_rejections(tmp_path, raw, diagnostic):
    from quality import source_inspection

    path = tmp_path / "source.json"
    path.write_bytes(raw)
    with pytest.raises(EvidenceError) as caught:
        source_inspection.read_checked_document(path, hashlib.sha256(raw).hexdigest())
    assert str(caught.value) == diagnostic
