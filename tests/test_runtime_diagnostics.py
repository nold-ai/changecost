"""Metadata collection fails closed without uploading private runtime payloads."""

import hashlib
import json
from typing import Any

import pytest


def fixture(tmp_path):
    inventory: dict[str, Any] = {
        "environment": {
            "python_version": "3.13",
            "python_full_version": "3.13.14",
            "private": "CANARY",
        },
        "installed": [
            {
                "metadata": {
                    "name": "pytest",
                    "version": "9.1.1",
                    "requires_dist": ["CANARY"],
                    "secret": "CANARY",
                },
                "requested": True,
                "direct_url": "CANARY",
            }
        ],
        "pytest_arguments": ["CANARY"],
        "member_graphs": {
            "pytest-observe": {
                "installed": [
                    {"name": "pytest", "version": "9.1.1", "dependencies": [], "origin": "analyzer"}
                ],
                "sealed_imports": ["CANARY"],
            }
        },
    }
    descriptor: dict[str, Any] = dict(
        schema="project-runtime-layer-v2",
        project_identity="sha256:" + "b" * 64,
        environment_id="linux-x86_64-cp313",
        worker_identity="sha256:" + "c" * 64,
        provenance=dict(authority="local_build", protected_pr_eligible=False),
        inventory=inventory,
        project={"secret": "CANARY"},
        payload={"secret": "CANARY"},
    )
    seal(descriptor)
    runtime = {
        k: descriptor[k] for k in ("schema", "identity", "project_identity", "environment_id")
    }
    runtime.update(status="PASS", **descriptor["provenance"])
    report = tmp_path / "report.json"
    report.write_text(
        json.dumps(dict(schema_version="1.6", scope_evidence=dict(project_runtime=runtime)))
    )
    cache = tmp_path / "cache"
    target = cache / ("a" * 64)
    target.mkdir(parents=True)
    (target / "project-runtime.json").write_text(json.dumps(descriptor))
    return report, cache, target, descriptor


def seal(value):
    unsigned = {k: v for k, v in value.items() if k != "identity"}
    value["identity"] = (
        "sha256:"
        + hashlib.sha256(
            json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
    )


def test_success_privacy(tmp_path):
    from quality.runtime_diagnostics import collect

    report, cache, _, _ = fixture(tmp_path)
    result = collect(report, cache)
    encoded = json.dumps(result)
    assert result["status"] == "collected"
    assert result["packages"] == [{"name": "pytest", "version": "9.1.1", "requested": True}]
    assert "CANARY" not in encoded
    assert all(
        word not in encoded
        for word in ["direct_url", "requires_dist", "pytest_arguments", "sealed_imports", "payload"]
    )


def corrupt_runtime_file(fixture_values, fault):
    report, cache, target, descriptor = fixture_values
    path = target / "project-runtime.json"
    if fault == "missing":
        path.unlink()
    elif fault == "identity":
        descriptor["payload"] = {}
        path.write_text(json.dumps(descriptor))
    elif fault == "symlink":
        path.rename(target / "other")
        path.symlink_to(target / "other")
    elif fault == "hardlink":
        (target / "other").hardlink_to(path)
    elif fault == "directory":
        path.unlink()
        path.mkdir()
    elif fault == "oversize":
        path.write_bytes(b"x" * (16 * 1024 * 1024 + 1))
    elif fault == "ambiguous":
        other = cache / ("d" * 64)
        other.mkdir()
        (other / path.name).write_bytes(path.read_bytes())
    elif fault == "cache-link":
        cache.rename(cache.parent / "real-cache")
        cache.symlink_to(cache.parent / "real-cache", target_is_directory=True)
    elif fault == "parent-link":
        target.rename(cache / "real-dir")
        target.symlink_to(cache / "real-dir", target_is_directory=True)


def corrupt_runtime_metadata(fixture_values, fault):
    report, cache, target, descriptor = fixture_values
    path = target / "project-runtime.json"
    if fault == "context":
        data = json.loads(report.read_text())
        data["scope_evidence"]["project_runtime"]["environment_id"] = "linux-x86_64-cp311"
        report.write_text(json.dumps(data))
    elif fault == "duplicate":
        report.write_text('{"schema_version":"1.6","schema_version":"1.6"}')
    elif fault == "invalid-name":
        descriptor["inventory"]["installed"][0]["metadata"]["name"] = "https://CANARY"
        seal(descriptor)
        path.write_text(json.dumps(descriptor))
        data = json.loads(report.read_text())
        data["scope_evidence"]["project_runtime"]["identity"] = descriptor["identity"]
        report.write_text(json.dumps(data))
    elif fault == "nonfinite":
        report.write_text('{"value":NaN}')


@pytest.mark.parametrize(
    "fault",
    [
        "missing",
        "identity",
        "context",
        "duplicate",
        "symlink",
        "hardlink",
        "directory",
        "oversize",
        "ambiguous",
        "cache-link",
        "parent-link",
        "invalid-name",
        "nonfinite",
    ],
)
def test_faults_rejected(tmp_path, fault):
    from quality.runtime_diagnostics import collect

    report, cache, target, descriptor = fixture(tmp_path)
    values = (report, cache, target, descriptor)
    if fault in {"context", "duplicate", "invalid-name", "nonfinite"}:
        corrupt_runtime_metadata(values, fault)
    else:
        corrupt_runtime_file(values, fault)
    with pytest.raises(ValueError):
        collect(report, cache)


def test_exclusive_output_and_write_failure(tmp_path):
    from quality.runtime_diagnostics import write_output

    output = tmp_path / "output.json"
    output.write_text("CANARY")
    with pytest.raises(OSError):
        write_output(output, {"status": "error"})
    assert output.read_text() == "CANARY"
    with pytest.raises(OSError):
        write_output(tmp_path / "missing" / "output", {"status": "error"})


def test_cli_error_is_bounded_private_and_nonzero(tmp_path, capsys):
    from quality.runtime_diagnostics import main

    output = tmp_path / "diagnostic.json"
    assert main([str(tmp_path / "CANARY"), str(tmp_path / "cache"), str(output)]) == 2
    assert json.loads(output.read_text()) == {
        "schema": "changecost/runtime-diagnostic-v1",
        "status": "unavailable_or_invalid",
    }
    captured = capsys.readouterr()
    assert not captured.out and "CANARY" not in captured.err


def test_output_bound_and_graph_validation(tmp_path):
    from quality.runtime_diagnostics import encode_output, observation_graph

    with pytest.raises(ValueError):
        encode_output({"safe": "x" * 65_536})
    with pytest.raises(ValueError):
        observation_graph(
            {
                "member_graphs": {
                    "pytest-observe": {
                        "installed": [
                            {
                                "name": "pytest",
                                "version": "9.1.1",
                                "dependencies": ["https://CANARY"],
                            }
                        ]
                    }
                }
            }
        )


def test_cache_count_and_report_links(tmp_path):
    from quality.runtime_diagnostics import collect

    report, cache, _, _ = fixture(tmp_path)
    original = tmp_path / "original.json"
    report.rename(original)
    report.symlink_to(original)
    with pytest.raises(ValueError):
        collect(report, cache)
    report.unlink()
    report.hardlink_to(original)
    with pytest.raises(ValueError):
        collect(report, cache)
    report.unlink()
    report.write_bytes(original.read_bytes())
    for n in range(257):
        (cache / f"unrelated-{n}").mkdir()
    with pytest.raises(ValueError):
        collect(report, cache)


def test_parent_replacement_does_not_redirect_reads(tmp_path, monkeypatch):
    import quality.runtime_diagnostics as target_module

    report, cache, _, _ = fixture(tmp_path)
    real_read = target_module.read_metadata

    def replace_parent(fd, name):
        if name == "project-runtime.json":
            cache.rename(tmp_path / "original-cache")
            cache.mkdir()
            child = cache / ("a" * 64)
            child.mkdir()
            (child / name).write_text("CANARY")
        return real_read(fd, name)

    monkeypatch.setattr(target_module, "read_metadata", replace_parent)
    assert target_module.collect(report, cache)["status"] == "collected"


def test_real_target_identity_detector_control(tmp_path, monkeypatch):
    import quality.runtime_diagnostics as target_module

    report, cache, folder, descriptor = fixture(tmp_path)
    descriptor["payload"] = {"corrupted": "CANARY"}
    (folder / "project-runtime.json").write_text(json.dumps(descriptor))

    def detector():
        try:
            target_module.collect(report, cache)
        except ValueError:
            return
        raise AssertionError("canonical identity guard was bypassed")

    detector()
    with monkeypatch.context() as fault:
        fault.setattr(target_module, "matched_descriptor", lambda *_args: descriptor)
        with pytest.raises(AssertionError):
            # The same detector rejects a real-target bypass of canonical identity.
            detector()
    detector()


def test_overflowed_json_number_rejected(tmp_path):
    from quality.runtime_diagnostics import collect

    report, cache, _, _ = fixture(tmp_path)
    report.write_text('{"value":1e999}')
    with pytest.raises(ValueError):
        collect(report, cache)
