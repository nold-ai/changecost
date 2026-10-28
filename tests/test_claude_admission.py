import copy
import json
from pathlib import Path

import pytest

from quality.source_feasibility import profile_digest, validate_register

ROOT = Path(__file__).parents[1]
PROFILE = "claude-project-2-1-215-request-stages"


def register():
    return json.loads((ROOT / "docs/providers/source-profiles.json").read_text())


def test_exact_canonical_claude_profile_has_independent_usage_attestation():
    data = register()
    matches = [p for p in data["profiles"] if p["id"] == PROFILE]
    assert len(matches) == 1
    profile = matches[0]
    assert (
        profile_digest(profile)
        == "b79d44303e6b73075ea8f1ca2d8d26bc8153e8a19d39f0766b63b2c4aaafd16c"
    )
    assert profile["approvals"][0]["reviewer"] == "claude37/implement/exact-profile-4-delta-review"
    assert profile["approvals"][0]["decisions"] == profile["admission"]["decisions"]
    assert validate_register(data) == []


@pytest.mark.parametrize(
    "path,value",
    [
        ("kind", "other"),
        ("mapping_revision", "other"),
        ("producer.engine_version", "2.1.257"),
        ("producer.client_surface", "desktop-coding"),
        ("limits.bytes", True),
        ("source_categories.output_tokens", "total_tokens"),
        ("terminal_stop_reasons", ["end_turn", "max_tokens"]),
        ("classification.metadata.types", ["progress"]),
        ("classification.user.message.role", "assistant"),
        ("classification.member_absence", "null_equals_absent"),
        ("classification.unknown_types", "ignore"),
        ("event_key_recipe", ["path"]),
        ("revision_key_recipe", ["hidden_reason_hash"]),
        ("native_evidence_id", "missing"),
        ("producer_evidence_id", "missing"),
        ("refinement_reason", "other"),
    ],
)
def test_rehashed_invalid_claude_admission_cannot_broaden_policy(path, value):
    data = register()
    p = copy.deepcopy(next(p for p in data["profiles"] if p["id"] == PROFILE))
    data["profiles"] = [p]
    target = p["admission"]
    parts = path.split(".")
    for part in parts[:-1]:
        if parts[0] == "classification" and parts[-2:] == ["message", "role"]:
            break
        target = target[part]
    if path == "classification.user.message.role":
        p["admission"]["classification"]["user"]["message.role"] = value
    else:
        target[parts[-1]] = value
    p["approvals"][0]["profile_digest"] = profile_digest(p)
    assert validate_register(data)


def test_supported_claude_usage_requires_recognized_admission():
    data = register()
    p = next(p for p in data["profiles"] if p["id"] == PROFILE)
    del p["admission"]
    p["approvals"][0]["profile_digest"] = profile_digest(p)
    assert validate_register(data)
