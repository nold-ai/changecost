"""Metadata collection fails closed without uploading private runtime payloads."""

import hashlib
import json
from typing import Any

import pytest


@pytest.mark.parametrize(
    "cpu,memory", [(b"200000 100000\n", b"1073741824\n"), (b"max 100000\n", b"max\n")]
)
def test_host_context_allowlist(tmp_path, cpu, memory):
    from quality.runtime_diagnostics import host_context

    (tmp_path / "cpu.max").write_bytes(cpu)
    (tmp_path / "memory.max").write_bytes(memory)
    (tmp_path / "private").write_text("PRIVATE_CANARY")
    context = host_context(tmp_path)
    assert set(context) == {
        "python_version",
        "cpu_count",
        "cpu_affinity_count",
        "cgroup_cpu_max",
        "cgroup_memory_max",
    }
    assert context["cgroup_cpu_max"] == [int(v) if v != b"max" else "max" for v in cpu.split()]
    assert context["cgroup_memory_max"] == [
        int(v) if v != b"max" else "max" for v in memory.split()
    ]
    assert "PRIVATE_CANARY" not in json.dumps(context)


@pytest.mark.parametrize(
    "raw", [b"PRIVATE_CANARY", b"1" * 65, b"1 2 3", b"-1 100000", b"\xff 100000"]
)
def test_host_context_rejects_invalid_limits(tmp_path, raw):
    from quality.runtime_diagnostics import host_context

    (tmp_path / "cpu.max").write_bytes(raw)
    (tmp_path / "memory.max").write_bytes(raw)
    context = host_context(tmp_path)
    assert context["cgroup_cpu_max"] is None
    assert context["cgroup_memory_max"] is None
    assert "PRIVATE_CANARY" not in json.dumps(context)


def test_host_context_missing_limits(tmp_path):
    from quality.runtime_diagnostics import host_context

    context = host_context(tmp_path)
    assert context["cgroup_cpu_max"] is None and context["cgroup_memory_max"] is None


def test_host_context_unavailable_affinity(monkeypatch, tmp_path):
    import os

    from quality.runtime_diagnostics import host_context

    def unavailable(_pid):
        raise OSError("PRIVATE_CANARY")

    monkeypatch.setattr(os, "sched_getaffinity", unavailable, raising=False)
    context = host_context(tmp_path)
    assert context["cpu_affinity_count"] is None
    assert "PRIVATE_CANARY" not in json.dumps(context)


def test_host_context_does_not_follow_limit_symlinks(tmp_path):
    from quality.runtime_diagnostics import host_context

    (tmp_path / "private").write_text("PRIVATE_CANARY")
    for name in ("cpu.max", "memory.max"):
        (tmp_path / name).symlink_to(tmp_path / "private")
    context = host_context(tmp_path)
    assert context["cgroup_cpu_max"] is None and context["cgroup_memory_max"] is None


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
        return
    if fault == "identity":
        descriptor["payload"] = {}
        path.write_text(json.dumps(descriptor))
        return
    if fault == "symlink":
        path.rename(target / "other")
        path.symlink_to(target / "other")
        return
    if fault == "hardlink":
        (target / "other").hardlink_to(path)
        return
    if fault == "directory":
        path.unlink()
        path.mkdir()
        return
    if fault == "oversize":
        path.write_bytes(b"x" * (16 * 1024 * 1024 + 1))
        return
    if fault == "ambiguous":
        other = cache / ("d" * 64)
        other.mkdir()
        (other / path.name).write_bytes(path.read_bytes())
        return
    if fault == "cache-link":
        cache.rename(cache.parent / "real-cache")
        cache.symlink_to(cache.parent / "real-cache", target_is_directory=True)
        return
    if fault == "parent-link":
        target.rename(cache / "real-dir")
        target.symlink_to(cache / "real-dir", target_is_directory=True)


def corrupt_runtime_metadata(fixture_values, fault):
    report, cache, target, descriptor = fixture_values
    path = target / "project-runtime.json"
    if fault == "context":
        data = json.loads(report.read_text())
        data["scope_evidence"]["project_runtime"]["environment_id"] = "linux-x86_64-cp311"
        report.write_text(json.dumps(data))
        return
    if fault == "duplicate":
        report.write_text('{"schema_version":"1.6","schema_version":"1.6"}')
        return
    if fault == "invalid-name":
        descriptor["inventory"]["installed"][0]["metadata"]["name"] = "https://CANARY"
        seal(descriptor)
        path.write_text(json.dumps(descriptor))
        data = json.loads(report.read_text())
        data["scope_evidence"]["project_runtime"]["identity"] = descriptor["identity"]
        report.write_text(json.dumps(data))
        return
    if fault == "nonfinite":
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


def process_stat_bytes(pid, parent=0, start=10, cpu=5, rss=7, name="PRIVATE_CANARY"):
    fields = ["0"] * 22
    fields[0], fields[1] = "S", str(parent)
    fields[11], fields[12], fields[19], fields[21] = str(cpu), "2", str(start), str(rss)
    return (f"{pid} ({name}) " + " ".join(fields)).encode()


def proc_fixture(root, pid, **kwargs):
    path = root / str(pid)
    path.mkdir(exist_ok=True)
    (path / "stat").write_bytes(process_stat_bytes(pid, **kwargs))


def test_numeric_process_privacy_and_lineage(tmp_path):
    from quality.runtime_diagnostics import process_tree

    proc_fixture(tmp_path, 10, start=10)
    proc_fixture(tmp_path, 11, parent=10, start=11)
    proc_fixture(tmp_path, 12, parent=11, start=12)
    proc_fixture(tmp_path, 13, parent=999, start=13)
    proc_fixture(tmp_path, 14, parent=10, start=9)
    proc_fixture(tmp_path, 15, parent=16, start=15)
    proc_fixture(tmp_path, 16, parent=15, start=15)
    tree = process_tree(10, 10, tmp_path)
    assert {row["pid"] for row in tree["processes"]} == {11, 12}
    assert all(row["cpu_ticks"] == 7 and row["rss_pages"] == 7 for row in tree["processes"])
    assert "PRIVATE_CANARY" not in json.dumps(tree)
    mismatch = process_tree(10, 11, tmp_path)
    assert not mismatch["root_valid"] and not mismatch["processes"]


@pytest.mark.parametrize("fault", ["symlink", "oversize", "malformed", "wrong-pid", "negative"])
def test_numeric_process_faults(tmp_path, fault):
    from quality.runtime_diagnostics import process_tree

    proc_fixture(tmp_path, 10)
    proc_fixture(tmp_path, 11, parent=10, start=11)
    target = tmp_path / "11" / "stat"
    if fault == "symlink":
        target.rename(target.with_name("secret"))
        target.symlink_to(target.with_name("secret"))
    elif fault == "oversize":
        target.write_bytes(b"PRIVATE_CANARY" * 1000)
    elif fault == "malformed":
        target.write_bytes(b"PRIVATE_CANARY")
    elif fault == "wrong-pid":
        target.write_bytes(process_stat_bytes(99, parent=10))
    else:
        target.write_bytes(process_stat_bytes(11, parent=10, rss=-1))
    result = process_tree(10, 10, tmp_path)
    assert not result["processes"]
    assert result["unavailable"] > 0
    assert "PRIVATE_CANARY" not in json.dumps(result)


def test_process_parent_directory_symlink(tmp_path):
    from quality.runtime_diagnostics import process_tree

    proc_fixture(tmp_path, 10)
    proc_fixture(tmp_path, 11, parent=10, start=11)
    (tmp_path / "11").rename(tmp_path / "private")
    (tmp_path / "11").symlink_to(tmp_path / "private")
    assert not process_tree(10, 10, tmp_path)["processes"]


def test_process_preexisting_subtree_excluded(tmp_path):
    from quality.runtime_diagnostics import process_tree

    proc_fixture(tmp_path, 10)
    proc_fixture(tmp_path, 11, parent=10, start=11)
    proc_fixture(tmp_path, 12, parent=11, start=12)
    proc_fixture(tmp_path, 13, parent=10, start=13)
    result = process_tree(10, 10, tmp_path, {(11, 11)})
    assert {row["pid"] for row in result["processes"]} == {13}


def test_process_stat_parentheses_are_private():
    from quality.runtime_diagnostics import parse_process_stat

    value = parse_process_stat(process_stat_bytes(10, name="private) (name"), 10)
    assert value["pid"] == 10 and "private" not in json.dumps(value)


def test_native_observer_tail_and_exclusive_output(tmp_path, monkeypatch):
    import quality.runtime_diagnostics as target

    monkeypatch.setattr(target, "SAMPLE_LIMIT", 3)
    NativeObservation = target.NativeObservation

    proc = tmp_path / "proc"
    proc.mkdir()
    proc_fixture(proc, 10)
    observation = NativeObservation(10, "a" * 64, proc)
    for index in (0, 1, 2, 299):
        proc_fixture(proc, 11, parent=10, start=11, cpu=index)
        observation.sample(index)
    output = tmp_path / "diagnostic.json"
    observation.finish(output, 301)
    value = json.loads(output.read_text())
    assert value["truncated"] and value["samples"][-1]["elapsed_seconds"] == 301
    assert value["samples"][-1]["live_cpu_ticks"] == 301
    assert value["binding"]["input_digest"] == "a" * 64
    assert value["binding"]["root_start_ticks"] == 10
    assert len(output.read_bytes()) <= 65_536 and "PRIVATE_CANARY" not in output.read_text()
    with pytest.raises(OSError):
        observation.finish(output, 302)


def test_native_observer_production_capacity(tmp_path, monkeypatch):
    import quality.runtime_diagnostics as target

    proc_fixture(tmp_path, 10)
    observation = target.NativeObservation(10, "a" * 64, tmp_path)
    rows = [
        target.parse_process_stat(process_stat_bytes(pid, parent=10, start=pid), pid)
        for pid in range(11, 43)
    ]
    snapshot = dict(
        processes=rows, truncated=False, unavailable=0, root_valid=True, lineage_exclusions=0
    )
    monkeypatch.setattr(target, "process_tree", lambda *_args: snapshot)
    assert target.SAMPLE_LIMIT == 120
    for elapsed in range(1, 120):
        observation.sample(elapsed)
    assert len(observation.samples) == 120 and not observation.truncated
    output = tmp_path / "production-capacity.json"
    observation.finish(output, 120)
    value = json.loads(output.read_text())
    assert len(value["samples"]) == 120 and value["truncated"]
    assert value["samples"][0]["elapsed_seconds"] == 1
    assert value["samples"][-1]["elapsed_seconds"] == 120
    assert len(value["latest_tree"]) == 32 and len(output.read_bytes()) <= 65_536


def test_native_observer_unavailable_and_error_cleanup(tmp_path):
    import threading

    from quality.runtime_diagnostics import observe_native

    output = tmp_path / "diagnostic.json"
    before = set(threading.enumerate())
    with (
        pytest.raises(RuntimeError, match="sentinel"),
        observe_native(10, "a" * 64, output, tmp_path / "absent", interval=0.001),
    ):
        raise RuntimeError("sentinel")
    assert json.loads(output.read_text())["status"] == "unavailable"
    assert set(threading.enumerate()) == before


def test_native_observer_write_failure_preserves_execution(tmp_path):
    from quality.runtime_diagnostics import observe_native

    output = tmp_path / "existing"
    output.write_text("PRIVATE_CANARY")
    with observe_native(10, "a" * 64, output, tmp_path / "absent", interval=0.001):
        pass
    assert output.read_text() == "PRIVATE_CANARY"


def test_native_process_bound_and_discontinuities(tmp_path, monkeypatch):
    import quality.runtime_diagnostics as target

    proc_fixture(tmp_path, 10)
    observation = target.NativeObservation(10, "a" * 64, tmp_path)
    proc_fixture(tmp_path, 11, parent=10, start=11)
    observation.sample(1)
    (tmp_path / "11" / "stat").unlink()
    (tmp_path / "11").rmdir()
    observation.sample(2)
    assert observation.departures
    for pid in range(20, 27):
        proc_fixture(tmp_path, pid, parent=10, start=pid)
    monkeypatch.setattr(target, "PROCESS_LIMIT", 4)
    result = target.process_tree(10, 10, tmp_path)
    assert result["truncated"] and len(result["processes"]) <= 4


def test_native_binding_rejects_private_input(tmp_path):
    from quality.runtime_diagnostics import NativeObservation

    with pytest.raises(ValueError, match="invalid diagnostic metadata"):
        NativeObservation(10, "PRIVATE_CANARY", tmp_path)


@pytest.mark.parametrize("exit_code", [0, 3])
def test_native_observer_real_child_preserves_result(tmp_path, capfd, exit_code):
    import os
    import subprocess
    import sys

    from quality.runtime_diagnostics import observe_native

    output = tmp_path / "diagnostic.json"
    with observe_native(os.getpid(), "a" * 64, output, interval=0.001):
        result = subprocess.run(
            [sys.executable, "-c", f"import sys; print('child'); sys.exit({exit_code})"],
            cwd=tmp_path,
            check=False,
        )
    assert result.returncode == exit_code and capfd.readouterr().out == "child\n"
    assert json.loads(output.read_text())["binding"]["input_digest"] == "a" * 64


def test_native_review_command_and_missing_report_preserved(tmp_path, monkeypatch, capfd):
    import sys

    import quality.review as target

    driver = tmp_path / "driver"
    driver.write_text(
        f"#!{sys.executable}\nimport json,sys\nfrom pathlib import Path\n"
        "Path('called.json').write_text(json.dumps(sys.argv[1:]))\n"
        "print('native-output')\nprint('native-error', file=sys.stderr)\nsys.exit(3)\n"
    )
    driver.chmod(0o700)
    monkeypatch.setattr(target.external_tools, "executable", lambda *_args: str(driver))
    assert target.run(tmp_path, set()) == ["SpecFact produced no review report"]
    captured = capfd.readouterr()
    assert captured.out == "native-output\n" and "native-error" in captured.err
    args = json.loads((tmp_path / "called.json").read_text())
    assert args[:-1] == [
        "code",
        "review",
        "run",
        "--scope",
        "full",
        "--include-tests",
        "--bug-hunt",
        "--enforcement",
        "full",
        "--json",
        "--out",
    ]
    diagnostics = list((tmp_path / ".specfact").glob("native-process-*.json"))
    assert len(diagnostics) == 1


@pytest.mark.parametrize("exit_code", [0, 3])
def test_native_observer_start_failure_preserves_child(tmp_path, monkeypatch, capfd, exit_code):
    import os
    import subprocess
    import sys
    import threading

    from quality.runtime_diagnostics import observe_native

    def unavailable(_thread):
        raise RuntimeError("PRIVATE_CANARY")

    before = set(threading.enumerate())
    monkeypatch.setattr(threading.Thread, "start", unavailable)
    output = tmp_path / "diagnostic.json"
    with observe_native(os.getpid(), "a" * 64, output):
        result = subprocess.run([sys.executable, "-c", f"import sys; sys.exit({exit_code})"])
    assert result.returncode == exit_code and set(threading.enumerate()) == before
    value = json.loads(output.read_text())
    assert value["sampling_error"] and "PRIVATE_CANARY" not in json.dumps(value)
    assert "PRIVATE_CANARY" not in capfd.readouterr().err


def test_native_observer_start_failure_preserves_body_exception(tmp_path, monkeypatch):
    import threading

    from quality.runtime_diagnostics import observe_native

    def unavailable(_thread):
        raise RuntimeError("PRIVATE_CANARY")

    monkeypatch.setattr(threading.Thread, "start", unavailable)
    output = tmp_path / "diagnostic.json"
    with pytest.raises(ValueError, match="body-sentinel"), observe_native(10, "a" * 64, output):
        raise ValueError("body-sentinel")
    assert json.loads(output.read_text())["sampling_error"]


@pytest.mark.parametrize("fault", ["truncated", "unreadable", "invalid-root"])
def test_native_incomplete_baseline_stays_unavailable(tmp_path, monkeypatch, fault):
    import quality.runtime_diagnostics as target

    proc_fixture(tmp_path, 10)
    proc_fixture(tmp_path, 11, parent=10, start=11)
    if fault == "truncated":
        monkeypatch.setattr(target, "PROCESS_LIMIT", 1)
    else:
        pid = 11 if fault == "unreadable" else 10
        (tmp_path / str(pid) / "stat").write_bytes(b"PRIVATE_CANARY")
    observation = target.NativeObservation(10, "a" * 64, tmp_path)
    assert observation.baseline_incomplete
    monkeypatch.setattr(target, "PROCESS_LIMIT", 512)
    proc_fixture(tmp_path, 10)
    proc_fixture(tmp_path, 11, parent=10, start=11)
    observation.sample(1)
    output = tmp_path / "diagnostic.json"
    observation.finish(output, 2)
    value = json.loads(output.read_text())
    assert value["status"] == "unavailable" and value["baseline_incomplete"]
    assert value["samples"] == value["first_tree"] == value["latest_tree"] == []
    assert value["binding"]["input_digest"] == "a" * 64
    assert value["binding"]["root_pid"] == 10 and value["binding"]["invocation_id"]
    assert value["terminal_elapsed_seconds"] == 2 and "PRIVATE_CANARY" not in output.read_text()


@pytest.mark.parametrize("exit_code", [0, 3])
def test_native_incomplete_baseline_preserves_child(tmp_path, monkeypatch, exit_code):
    import subprocess
    import sys

    from quality.runtime_diagnostics import observe_native

    proc_fixture(tmp_path, 10)
    proc_fixture(tmp_path, 11, parent=10, start=11)
    (tmp_path / "11" / "stat").write_bytes(b"PRIVATE_CANARY")
    output = tmp_path / "diagnostic.json"
    with observe_native(10, "a" * 64, output, tmp_path):
        proc_fixture(tmp_path, 11, parent=10, start=11)
        result = subprocess.run([sys.executable, "-c", f"import sys; sys.exit({exit_code})"])
    assert result.returncode == exit_code
    value = json.loads(output.read_text())
    assert value["status"] == "unavailable" and value["samples"] == []
