"""Synthetic rehashed contributor boundary controls."""

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from quality import source_feasibility as research
from quality.source_inspection import EvidenceError

ROOT = Path(__file__).parents[1]


def test_packaged_admission_is_generated_from_canonical_only(tmp_path):
    from quality.index import check_outputs, render

    outputs = render(ROOT)
    assert "src/changecost/codex_admission.json" in outputs
    envelope = json.loads(outputs["src/changecost/codex_admission.json"])
    p = register()["profiles"][-1]
    assert envelope["admission"] == p["admission"]
    assert envelope["profile_digest"] == research.profile_digest(p)
    assert (
        envelope["approval_digest"]
        == __import__("hashlib")
        .sha256(
            json.dumps(
                p["approvals"][0],
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
                allow_nan=False,
            ).encode()
        )
        .hexdigest()
    )
    target = tmp_path / "src/changecost"
    target.mkdir(parents=True)
    (target / "codex_admission.json").write_text("{}")
    assert check_outputs(
        tmp_path,
        {"src/changecost/codex_admission.json": outputs["src/changecost/codex_admission.json"]},
    )


def register():
    return json.loads((ROOT / "docs/providers/source-profiles.json").read_text())


def rebind(p):
    for proof in p["approvals"]:
        proof["profile_digest"] = research.profile_digest(p)


FAULTS = [
    ("", None),
    ("", []),
    ("", 3),
    ("", "private"),
    ("DELETE", None),
    ("kind", "bad"),
    ("mapping_revision", "bad"),
    ("format", "json"),
    ("approval_digest", "0000000000000000000000000000000000000000000000000000000000000000"),
    ("expected_request_count", True),
    ("expected_request_count", 15),
    ("expected_fact_count", 95),
    ("whole_record_count", True),
    ("whole_record_count", 10001),
    ("source_sha256", "0000000000000000000000000000000000000000000000000000000000000000"),
    ("projection_sha256", "bad"),
    ("projection_schema", {}),
    ("projection_schema.fixed_meaning.model", "configured"),
    ("projection_schema.producer.engine_version", "other"),
    ("projection_schema.fact_key_recipe", []),
    ("producer_claim.engine_version", "other"),
    ("producer_claim.client_build", "other"),
    ("producer_claim.corroboration_artifact_sha256", False),
    ("limits.bytes", 1),
    ("limits.depth", True),
    ("classification.records", 122),
    ("classification.outer_record_counts.event_msg", 49),
    ("classification.event_payload_type_counts.token_count", 15),
    ("classification.accepted_records", [18]),
    ("classification.source_refs.world_state", "http://example.org"),
    ("decisions.authority", "changed"),
    ("accepted_records", [True]),
    ("accepted_records", [18, 18]),
    ("accepted_records", [23, 18]),
    ("accepted_records", [0]),
    ("accepted_records", [124]),
]


@pytest.mark.parametrize("path,value", FAULTS)
def test_rehashed_fault_and_repair(path, value):
    data = register()
    original = copy.deepcopy(data)
    p = data["profiles"][-1]
    if path == "DELETE":
        del p["admission"]
        p["id"] = "renamed-codex"
    elif path:
        target = p["admission"]
        parts = path.split(".")
        for key in parts[:-1]:
            target = target[key]
        target[parts[-1]] = value
    else:
        p["admission"] = value
    rebind(p)
    assert research.validate_register(data)
    assert research.validate_register(original) == []


def test_optional_admission_is_checked():
    data = register()
    data["profiles"][0]["admission"] = None
    assert research.validate_register(data)


def test_invalid_admission_public_boundaries(tmp_path):
    data = register()
    p = data["profiles"][-1]
    p["admission"]["kind"] = "PRIVATE"
    rebind(p)
    path = tmp_path / "private.json"
    path.write_text(json.dumps(data))
    with pytest.raises(EvidenceError, match="register-invalid"):
        research.load_register(path)
    with pytest.raises(EvidenceError, match="register-invalid"):
        research.render_matrix(data)
    result = subprocess.run(
        [sys.executable, "-m", "quality.source_feasibility", "--register", str(path), "--matrix"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr == "register-invalid\n"


@pytest.mark.parametrize(
    "path", ["", "projection_schema", "classification", "producer_claim", "limits", "decisions"]
)
@pytest.mark.parametrize("fault", ["missing", "extra", "null", "list", "scalar"])
def test_closed_nested_shapes(path, fault):
    data = register()
    p = data["profiles"][-1]
    target = p["admission"]
    if path:
        target = target[path]
    if fault == "missing":
        del target[next(iter(target))]
    elif fault == "extra":
        target["unreviewed"] = "PRIVATE"
    elif path:
        p["admission"][path] = {"null": None, "list": [], "scalar": True}[fault]
    else:
        p["admission"] = {"null": None, "list": [], "scalar": True}[fault]
    rebind(p)
    assert research.validate_register(data)


def test_finite_selectors_remain_data_and_repaired_control_accepts():
    data = register()
    p = data["profiles"][-1]
    a = p["admission"]
    a["source_sha256"] = "1" * 64
    a["projection_sha256"] = "2" * 64
    proof = p["approvals"][0]
    proof["sha256"] = a["source_sha256"]
    next(e for e in p["evidence"] if e["id"] == proof["evidence_id"])["sha256"] = a["source_sha256"]
    a["accepted_records"].pop()
    a["expected_request_count"] -= 1
    a["expected_fact_count"] -= 6
    a["whole_record_count"] -= 2
    c = a["classification"]
    c["records"] -= 2
    c["accepted_records"].pop()
    c["outer_record_counts"]["token_usage_record"] -= 1
    c["outer_record_counts"]["event_msg"] -= 1
    c["event_payload_type_counts"]["token_count"] -= 1
    rebind(p)
    assert research.validate_register(data) == []


def test_historical_other_provider_usage_approval_is_unchanged():
    data = register()
    p = data["profiles"][0]
    assert p["provider"] != "Codex"
    e = p["evidence"][0]
    e["origin"] = "native"
    p["capabilities"]["usage"] = "supported"
    p["approvals"] = [
        {
            "capability": "usage",
            "evidence_id": e["id"],
            "sha256": e["sha256"],
            "reviewer": "synthetic control",
            "decisions": dict.fromkeys(research.DECISIONS, "synthetic control"),
        }
    ]
    rebind(p)
    assert research.validate_register(data) == []


@pytest.mark.parametrize("boundary,valid", [("zero", True), ("whole_count", False)])
def test_zero_based_ordinal_boundaries_preserve_cardinality(boundary, valid):
    data = register()
    p = data["profiles"][-1]
    a = p["admission"]
    index = 0 if boundary == "zero" else -1
    ordinal = 0 if boundary == "zero" else a["whole_record_count"]
    a["accepted_records"][index] = ordinal
    a["classification"]["accepted_records"][index] = ordinal
    rebind(p)
    assert (research.validate_register(data) == []) is valid


@pytest.mark.parametrize("capability", ["attribution", "billed_money", "finality"])
def test_finite_diagnostic_policy_rejects_retagged_supported_proof(capability):
    data = register()
    original = copy.deepcopy(data)
    p = data["profiles"][-1]
    p["capabilities"][capability] = "supported"
    proof = copy.deepcopy(p["approvals"][0])
    proof["capability"] = capability
    p["approvals"].append(proof)
    rebind(p)
    assert research.validate_register(data)
    assert research.validate_register(original) == []
