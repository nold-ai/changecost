import json
import shutil
import subprocess
import threading
from pathlib import Path

from quality import pytest_stage_capture as capture_module


def test_capture_survives_cleanup_before_native_return(tmp_path, monkeypatch):
    observed = threading.Event()
    original = capture_module._Capture.sample

    def acknowledge(capture):
        original(capture)
        if capture.latest:
            observed.set()

    monkeypatch.setattr(capture_module._Capture, "sample", acknowledge)
    output = tmp_path / "stages.json"
    report = tmp_path / "native.json"
    native_bytes = b'{"diagnostic":"sandbox_launch_failed:timeout"}\n'
    with capture_module.capture_pytest_stage("a" * 64, output) as root:
        assert root is not None
        member = root / "specfact-targeted-pytest-coverage-fixture"
        stage = member / "temporary/changecost-pytest-stage"
        stage.mkdir(parents=True)
        state = {
            "sequence": 7,
            "stage": "call-start",
            "test": {
                "module": "tests/test_fixture.py",
                "function": "test_blocked",
                "parameter_sha256": None,
            },
            "worker": "gw0",
            "process_nonce": "b" * 32,
            "elapsed_ms": 17,
            "write_limit_reached": False,
        }
        (stage / ("b" * 32 + ".json")).write_text(json.dumps(state))
        assert observed.wait(5), "producer did not observe the collector acknowledgement"
        shutil.rmtree(member)
        report.write_bytes(native_bytes)
        result = subprocess.CompletedProcess(["native-fixture"], 124)
        assert not list(root.glob("specfact-targeted-pytest-coverage-*"))
    assert result.returncode == 124
    assert report.read_bytes() == native_bytes
    diagnostic = json.loads(output.read_text())
    assert diagnostic["status"] == "incomplete"
    assert diagnostic["latest"][0]["state"]["stage"] == "call-start"
    assert diagnostic["latest"][0]["state"]["test"]["function"] == "test_blocked"
    assert not Path(root).exists()


def member_state(root, nonce="b" * 32, member="fixture", **changes):
    stage = (
        root / ("specfact-targeted-pytest-coverage-" + member) / "temporary/changecost-pytest-stage"
    )
    stage.mkdir(parents=True, exist_ok=True)
    state = dict(
        sequence=1,
        stage="call-start",
        test=None,
        worker="gw0",
        process_nonce=nonce,
        elapsed_ms=1,
        write_limit_reached=False,
    )
    state.update(changes)
    path = stage / (nonce + ".json")
    path.write_text(json.dumps(state))
    return path


def test_last_valid_state_survives_bad_replacements_and_disappearance(tmp_path):
    capture = capture_module._Capture(tmp_path, "binding")
    path = member_state(tmp_path)
    capture.sample()
    first = next(iter(capture.latest.values()))
    capture.sample()
    assert next(iter(capture.latest.values())) is first
    for replacement in ('{"stage":', " " * 1025, "[]"):
        path.write_text(replacement)
        capture.sample()
        assert next(iter(capture.latest.values())) is first
    member_state(tmp_path, sequence=8, elapsed_ms=8)
    capture.sample()
    advanced = next(iter(capture.latest.values()))
    assert advanced["state"]["sequence"] == 8
    member_state(tmp_path, sequence=2, elapsed_ms=2)
    capture.sample()
    assert next(iter(capture.latest.values())) is advanced
    path.unlink()
    path.with_suffix(".part").write_text('{"incomplete":')
    capture.sample()
    assert next(iter(capture.latest.values())) is advanced
    assert {"state_unavailable", "state_regressed_or_changed"} <= capture.reasons


def test_missed_sample_and_torn_temporary_are_unavailable(tmp_path):
    path = member_state(tmp_path)
    path.rename(path.with_suffix(".part"))
    capture = capture_module._Capture(tmp_path, "binding")
    capture.sample()
    shutil.rmtree(path.parents[2])
    capture.finish(tmp_path / "out.json")
    value = json.loads((tmp_path / "out.json").read_text())
    assert value["status"] == "unavailable"
    assert value["latest"] == []


def test_caps_and_restarted_worker_keep_distinct_bounded_streams(tmp_path):
    capture = capture_module._Capture(tmp_path, "binding", max_scans=2)
    for index in range(17):
        member_state(tmp_path, nonce=f"{index:032x}")
    member_state(tmp_path, member="second")
    member_state(tmp_path, member="third")
    capture.sample()
    assert len(capture.latest) == 16
    assert len(capture.members) == 2
    assert "stream_limit_reached" in capture.reasons
    assert "member_limit_reached" in capture.reasons
    assert {record["state"]["worker"] for record in capture.latest.values()} == {"gw0"}
    capture.sample()
    capture.sample()
    capture.finish(tmp_path / "out.json")
    assert capture.scans == 2
    assert "scan_limit_reached" in capture.reasons
    assert (tmp_path / "out.json").stat().st_size < 65536


def test_concurrent_invocations_never_mix(tmp_path):
    with (
        capture_module.capture_pytest_stage("first", tmp_path / "first.json") as first,
        capture_module.capture_pytest_stage("second", tmp_path / "second.json") as second,
    ):
        assert first != second
        member_state(first, stage="setup-start")
        member_state(second, stage="teardown-start")
    values = [json.loads((tmp_path / f"{name}.json").read_text()) for name in ("first", "second")]
    assert [value["input_digest"] for value in values] == ["first", "second"]
    assert [value["latest"][0]["state"]["stage"] for value in values] == [
        "setup-start",
        "teardown-start",
    ]
    assert not any(thread.name == "pytest-stage-observer" for thread in threading.enumerate())


def test_child_exception_and_output_failure_preserve_exception_and_cleanup(tmp_path):
    import pytest

    output = tmp_path / "absent/out.json"
    roots = []
    with (
        pytest.raises(RuntimeError, match="original child error"),
        capture_module.capture_pytest_stage("binding", output) as root,
    ):
        assert root is not None
        roots.append(root)
        member_state(root)
        raise RuntimeError("original child error")
    assert not roots[0].exists()
    assert not any(thread.name == "pytest-stage-observer" for thread in threading.enumerate())


def test_sampler_and_startup_failures_do_not_mask_child_result(tmp_path, monkeypatch):
    class BrokenCapture(capture_module._Capture):
        def finish(self, output):
            raise OSError("unavailable")

    monkeypatch.setattr(capture_module, "_Capture", BrokenCapture)
    with capture_module.capture_pytest_stage("binding", tmp_path / "out.json") as root:
        assert root is not None
        result = 124
    assert result == 124
    assert root is not None and not root.exists()

    class NoCapture:
        def __init__(self, *args):
            raise RuntimeError("startup unavailable")

    monkeypatch.setattr(capture_module, "_Capture", NoCapture)
    with capture_module.capture_pytest_stage("binding", tmp_path / "out.json") as root:
        assert root is not None
        result = 125
    assert result == 125
    assert root is not None and not root.exists()


def test_no_follow_at_each_directory_and_nonregular_leaf(tmp_path):
    import os

    for level in ("root", "member", "temporary", "stage", "leaf", "fifo"):
        root = tmp_path / level
        root.mkdir()
        path = member_state(root)
        capture = capture_module._Capture(root, "binding")
        target = {
            "root": root,
            "member": path.parents[2],
            "temporary": path.parents[1],
            "stage": path.parent,
            "leaf": path,
            "fifo": path,
        }[level]
        if level == "fifo":
            target.unlink()
            os.mkfifo(target)
        else:
            moved = tmp_path / ("moved-" + level)
            target.rename(moved)
            target.symlink_to(moved, target_is_directory=moved.is_dir())
        capture.sample()
        assert not capture.latest, level


def test_replaced_member_and_exhaustion_are_explicit(tmp_path):
    capture = capture_module._Capture(tmp_path, "binding")
    path = member_state(tmp_path, write_limit_reached=True)
    capture.sample()
    old = dict(capture.latest)
    member = path.parents[2]
    member.rename(tmp_path / "old")
    member_state(tmp_path, stage="setup-start")
    capture.sample()
    assert capture.latest == old
    assert {"member_replaced", "write_limit_reached"} <= capture.reasons


def test_review_scopes_child_tmpdir_and_preserves_native_command_report(tmp_path, monkeypatch):
    import os
    from types import SimpleNamespace

    from quality import review

    environment = dict(os.environ)
    native = dict(
        assurance_status="PASS",
        overall_verdict="PASS",
        ci_exit_code=0,
        has_unknown_required_evidence=False,
        analyzer_evidence=[
            dict(id=name, execution_state="ran", evidence_outcome="PASS")
            for name in sorted(review.REQUIRED)
        ],
    )
    raw = (json.dumps(native, indent=2) + "\n").encode()
    invocations = []

    def invoke(argv, **options):
        invocations.append((argv, options))
        Path(argv[-1]).write_bytes(raw)
        return subprocess.CompletedProcess(argv, 124)

    monkeypatch.setattr(review, "subprocess", SimpleNamespace(run=invoke))
    monkeypatch.setattr(
        review, "external_tools", SimpleNamespace(executable=lambda *_: "/validator")
    )
    assert review.run(tmp_path, set()) == ["SpecFact exited 124"]
    argv, options = invocations[0]
    assert argv[:-1] == [
        "/validator",
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
    assert options["cwd"] == tmp_path and options["check"] is False
    child_tmp = Path(options["env"]["TMPDIR"])
    assert options["env"] == {**environment, "TMPDIR": str(child_tmp)}
    assert dict(os.environ) == environment
    assert not child_tmp.exists()
    assert Path(argv[-1]).read_bytes() == raw
    assert (tmp_path / ".specfact/code-review.json").read_bytes() == raw
    sidecar = next((tmp_path / ".specfact").glob("pytest-stage-*.json"))
    assert json.loads(sidecar.read_text())["status"] == "unavailable"


def test_missing_tmpdir_and_thread_start_leave_child_available(tmp_path, monkeypatch):
    from types import SimpleNamespace

    class CannotStart:
        def __init__(self, **_options):
            pass

        def start(self):
            raise RuntimeError("thread unavailable")

    monkeypatch.setattr(
        capture_module,
        "threading",
        SimpleNamespace(
            Event=threading.Event,
            Thread=CannotStart,
        ),
    )
    output = tmp_path / "thread.json"
    with capture_module.capture_pytest_stage("binding", output) as root:
        assert root is not None
        member_state(root)
    assert json.loads(output.read_text())["reasons"] == ["startup_unavailable"]
    assert not root.exists()

    def unavailable(**_options):
        raise OSError("no temporary storage")

    monkeypatch.setattr(capture_module, "tempfile", SimpleNamespace(TemporaryDirectory=unavailable))
    with capture_module.capture_pytest_stage("binding", tmp_path / "absent.json") as root:
        assert root is None
        result = 124
    assert result == 124
