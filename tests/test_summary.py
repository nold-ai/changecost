"""Untrusted summary data and final UTF-8 limits."""

import json

import pytest


def result(label):
    return {
        "schema": "changecost/check-v1",
        "status": "unknown",
        "record": {"kind": "quote", "record_id": label},
        "budget": {
            "amount": "15",
            "economic_kind": "monetary",
            "unit": "USD",
            "basis": "billed",
            "currency": "USD",
        },
        "comparison": None,
        "declared": [],
        "scope": None,
        "cutoff": None,
        "provenance": "producer_assertion",
        "completeness": "unknown",
        "sample_count": None,
        "quantile": "p90",
        "reasons": [label],
    }


def test_summary_escapes_and_unicode(tmp_path):
    from changecost.summary import render_summary, write_summary

    label = "$(touch pwned) <img src=x> [link](https://evil) ::error::\x1b[31m\n世界"
    output = render_summary(result(label))
    assert "<img" not in output and "\x1b" not in output
    assert "[link](https://evil)" not in output
    assert "世界" in output
    target = tmp_path / "summary"
    write_summary(result(label), target)
    assert target.read_text() == output
    assert not (tmp_path / "pwned").exists()


def test_summary_truncation():
    from changecost.summary import render_summary

    output = render_summary(result("世界&[" * 50000))
    assert len(output.encode()) <= 65536
    assert "truncated" in output.lower()
    assert output.encode().decode() == output


@pytest.mark.parametrize("payload", [{}, {"schema": "other"}, result("ok") | {"status": "other"}])
def test_summary_invalid(payload):
    from changecost.summary import render_summary

    with pytest.raises(ValueError):
        render_summary(payload)


def test_summary_write_error(tmp_path):
    from changecost.summary import write_summary

    with pytest.raises(OSError):
        write_summary(result("ok"), tmp_path)


@pytest.mark.parametrize(
    "mutation",
    [
        {"budget": {"amount": "NaN"}},
        {"comparison": {"amount": []}},
        {"status": "within_budget"},
        {"provenance": []},
        {"sample_count": True},
    ],
)
def test_summary_strict_machine_contract(mutation):
    from changecost.summary import render_summary

    with pytest.raises(ValueError):
        render_summary(result("ok") | mutation)


def test_advisory_does_not_mask_workflow_failure():
    from pathlib import Path

    import yaml

    from changecost.summary import render_summary
    from quality.workflow import security_errors

    config = yaml.load(Path(".github/workflows/advisory.yml").read_text(), Loader=yaml.BaseLoader)
    assert set(config["on"]) == {"workflow_dispatch"}
    assert security_errors(config) == []
    bad = config | {"permissions": {"contents": "write"}}
    assert render_summary(result("valid advice"))
    assert security_errors(bad) == ["workflow must declare contents: read permissions"]
    assert security_errors(config) == []
    for job in config["jobs"].values():
        assert not job.get("continue-on-error")
        for step in job["steps"]:
            assert not step.get("continue-on-error")
            assert "|| true" not in step.get("run", "")
            assert "${{" not in step.get("run", "")


def test_renderer_technical_failures_subprocess(tmp_path):
    import os
    import subprocess
    import sys

    payload = tmp_path / "result.json"
    payload.write_text(json.dumps(result("valid")))
    destination = tmp_path / "summary"
    command = [sys.executable, "-m", "changecost.summary", str(payload)]
    env = dict(os.environ, GITHUB_STEP_SUMMARY=str(destination))
    successful = subprocess.run(command, env=env, capture_output=True, text=True)
    assert successful.returncode == 0 and not successful.stdout
    payload.write_text('{"schema":"unsupported"}')
    rejected = subprocess.run(command, env=env, capture_output=True, text=True)
    assert rejected.returncode == 2 and not rejected.stdout
    assert "unsupported" not in rejected.stderr
    payload.write_text(json.dumps(result("valid")))
    unwritable = subprocess.run(
        command, env=dict(env, GITHUB_STEP_SUMMARY=str(tmp_path)), capture_output=True
    )
    assert unwritable.returncode == 2 and not unwritable.stdout


def verified_result(kind, status):
    value = result("verified")
    value.update(
        status=status,
        record={"kind": kind, "record_id": "verified"},
        comparison=value["budget"] | {"amount": "10" if status == "within_budget" else "20"},
        cutoff={"store_id": "local", "at": "2026-10-05T00:00:00Z", "sequence": 1},
        provenance="locally_reproduced_synthetic; provider_support_not_verified",
        completeness="complete",
        quantile="p90" if kind == "quote" else None,
        reasons=[],
    )
    return value


@pytest.mark.parametrize("kind", ["quote", "computed_settlement"])
@pytest.mark.parametrize("status", ["within_budget", "over_budget"])
def test_summary_rejects_legacy_numeric_authority(kind, status):
    from changecost.summary import render_summary

    value = verified_result(kind, status)
    assert render_summary(value)
    value["record"]["kind"] = "settlement"
    with pytest.raises(ValueError):
        render_summary(value)


def test_summary_accepts_legacy_unknown():
    from changecost.summary import render_summary

    value = result("legacy")
    value["record"]["kind"] = "settlement"
    value["quantile"] = None
    assert render_summary(value)


@pytest.mark.parametrize("kind", ["quote", "computed_settlement"])
@pytest.mark.parametrize("status", ["within_budget", "over_budget"])
@pytest.mark.parametrize("existing", [False, True])
def test_legacy_numeric_cli_preserves_summary(tmp_path, kind, status, existing):
    import os
    import subprocess
    import sys

    value = verified_result(kind, status)
    value["record"]["kind"] = "settlement"
    payload = tmp_path / "result.json"
    payload.write_text(json.dumps(value))
    destination = tmp_path / "summary"
    original = b"Earlier summary: \xe4\xb8\x96\xe7\x95\x8c\n"
    if existing:
        destination.write_bytes(original)
    rejected = subprocess.run(
        [sys.executable, "-m", "changecost.summary", str(payload)],
        env=dict(os.environ, GITHUB_STEP_SUMMARY=str(destination)),
        capture_output=True,
        text=True,
    )
    assert rejected.returncode == 2
    assert rejected.stdout == ""
    assert rejected.stderr == "cannot render or write advisory summary\n"
    if existing:
        assert destination.read_bytes() == original
    else:
        assert not destination.exists()


@pytest.mark.parametrize(
    "field,malformed",
    [
        (field, malformed)
        for field in ("status", "record_kind", "quantile", "completeness")
        for malformed in (["private-canary"], {"private-canary": "secret"}, True, 0)
    ]
    + [(field, None) for field in ("status", "record_kind", "completeness")],
)
@pytest.mark.parametrize("existing", [False, True])
def test_summary_malformed_enum_safe_cli(tmp_path, field, malformed, existing):
    import os
    import subprocess
    import sys

    value = result("valid")
    if field == "record_kind":
        value["record"]["kind"] = malformed
    else:
        value[field] = malformed
    payload = tmp_path / "result.json"
    payload.write_text(json.dumps(value))
    destination = tmp_path / "summary"
    original = b"Earlier advisory summary\n"
    if existing:
        destination.write_bytes(original)
    rejected = subprocess.run(
        [sys.executable, "-m", "changecost.summary", str(payload)],
        env=dict(os.environ, GITHUB_STEP_SUMMARY=str(destination)),
        capture_output=True,
        text=True,
    )
    assert rejected.returncode == 2
    assert rejected.stdout == ""
    assert rejected.stderr == "cannot render or write advisory summary\n"
    assert "private-canary" not in rejected.stderr
    if existing:
        assert destination.read_bytes() == original
    else:
        assert not destination.exists()
