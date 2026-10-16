import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from quality.pytest_stage import _MAX_WRITES, _test_identity, _Writer


def test_private_writer_bounds_identity_and_failure_isolation(tmp_path, monkeypatch):
    writer = _Writer(tmp_path, "gw0", max_writes=3)
    writer.emit("call-start", "tests/test_case.py::TestCase::test_secret[private payload]")
    path = tmp_path / "changecost-pytest-stage" / (writer.nonce + ".json")
    raw = path.read_bytes()
    value = json.loads(raw)
    assert len(raw) <= 1024
    assert b"private payload" not in raw
    assert value["test"]["function"] == "TestCase::test_secret"
    assert len(value["test"]["parameter_sha256"]) == 64
    assert _test_identity("/outside/secret.py::test_case") is None
    assert _test_identity("tests/test_case.py::" + "a" * 121) is None
    writer.emit("call-end")
    writer.emit("teardown-start")
    final = path.read_bytes()
    assert json.loads(final)["write_limit_reached"] is True
    writer.emit("teardown-end")
    assert path.read_bytes() == final
    failed = _Writer(tmp_path, "gw1")

    def unavailable(_raw):
        raise OSError("isolated writer failure")

    monkeypatch.setattr(failed, "_write", unavailable)
    failed.emit("call-start")
    assert failed.disabled
    healthy = _Writer(tmp_path, "gw1")
    healthy.emit("call-start", "tests/test_case.py::test_next")
    assert not healthy.disabled
    assert healthy.nonce != failed.nonce != writer.nonce
    assert len(list(path.parent.glob("*.json"))) == 2


def test_unencodable_identity_keeps_phase(tmp_path):
    writer = _Writer(tmp_path, "gw0")
    writer.emit("call-end", "tests/test_case.py::test_next[" + chr(0xD800) + "]")
    assert not writer.disabled
    path = tmp_path / "changecost-pytest-stage" / (writer.nonce + ".json")
    retained = json.loads(path.read_text())
    assert retained["stage"] == "call-end" and retained["test"] is None


def test_full_write_budget_and_fake_clock_are_instance_local(tmp_path, monkeypatch):
    times = iter([2, 1])
    writer = _Writer(tmp_path, "main", clock=lambda: next(times))
    writer.emit("pytest-started")
    path = tmp_path / "changecost-pytest-stage" / (writer.nonce + ".json")
    assert json.loads(path.read_text())["elapsed_ms"] == 0
    writer.emit("collection-start")
    assert writer.disabled
    bounded = _Writer(tmp_path, "main")
    count = 0
    total = 0
    last = None

    def count_write(raw):
        nonlocal count, total, last
        count += 1
        total += len(raw)
        last = json.loads(raw)

    monkeypatch.setattr(bounded, "_write", count_write)
    for _ in range(_MAX_WRITES + 1):
        bounded.emit("call-start", "tests/test_case.py::test_case")
    assert count == _MAX_WRITES
    assert total <= _MAX_WRITES * 1024
    assert last is not None
    assert last["write_limit_reached"]
    assert not bounded.disabled


def _child_project(tmp_path, body):
    root = Path(__file__).resolve().parents[1]
    (tmp_path / "tests").mkdir()
    (tmp_path / "scratch").mkdir()
    (tmp_path / "traces").mkdir()
    (tmp_path / "tests/test_case.py").write_text(body)
    registration = (root / "conftest.py").read_text()
    (tmp_path / "conftest.py").write_text(
        registration
        + """
import json
from pathlib import Path
from quality import pytest_stage
pytest_stage._SCRATCH = Path(__file__).parent / "scratch"
_original_write = pytest_stage._Writer._write

def traced_write(writer, raw):
    _original_write(writer, raw)
    path = Path(__file__).parent / "traces" / (writer.nonce + ".jsonl")
    with path.open("ab") as trace:
        trace.write(raw + b"\\n")

pytest_stage._Writer._write = traced_write
"""
    )
    environment = {**os.environ, "PYTHONPATH": str(root), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
    environment.pop("PYTEST_ADDOPTS", None)
    environment.pop("PYTEST_PLUGINS", None)
    environment.pop("SPECFACT_TARGET_PYTEST", None)
    command = [sys.executable, "-m", "pytest", "-o", "addopts=", "-q", "tests"]
    return command, environment


def _traces(root):
    return [
        json.loads(line)
        for path in (root / "traces").glob("*.jsonl")
        for line in path.read_text().splitlines()
    ]


@pytest.mark.parametrize(
    ("body", "code", "phase"),
    [
        ("def test_ok(): pass\n", 0, "call-end"),
        ("raise RuntimeError('collection failure')\n", 2, "collection-end"),
        (
            "import pytest\n@pytest.fixture(autouse=True)\n"
            "def broken(): raise RuntimeError('setup')\ndef test_case(): pass\n",
            1,
            "setup-end",
        ),
        (
            "import pytest\n@pytest.fixture(autouse=True)\ndef broken():\n    yield\n"
            "    raise RuntimeError('teardown')\ndef test_case(): pass\n",
            1,
            "teardown-end",
        ),
    ],
)
def test_real_pytest_phase_boundaries_preserve_outcomes(tmp_path, body, code, phase):
    command, environment = _child_project(tmp_path, body)
    environment["SPECFACT_TARGET_PYTEST"] = "1"
    result = subprocess.run(command, cwd=tmp_path, env=environment, capture_output=True, timeout=20)
    assert result.returncode == code, result.stdout.decode()
    records = _traces(tmp_path)
    stages = [record["stage"] for record in records]
    assert stages[:2] == ["pytest-started", "collection-start"]
    assert phase in stages
    assert stages[-2:] == ["sessionfinish-enter", "sessionfinish-exit"]
    tests = {record["test"]["function"] for record in records if record["test"]}
    assert tests == (set() if code == 2 else {"test_ok" if code == 0 else "test_case"})
    assert all(len(json.dumps(record).encode()) <= 1024 for record in records)


def test_real_xdist_inherits_marker_and_plain_pytest_writes_nothing(tmp_path):
    command, environment = _child_project(tmp_path, "def test_one(): pass\ndef test_two(): pass\n")
    plain = subprocess.run(command, cwd=tmp_path, env=environment, capture_output=True, timeout=20)
    assert plain.returncode == 0
    assert not _traces(tmp_path)
    assert not list((tmp_path / "scratch").iterdir())
    environment["SPECFACT_TARGET_PYTEST"] = "1"
    marked = subprocess.run(
        command + ["-p", "xdist.plugin", "-n", "4"],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        timeout=30,
    )
    assert marked.returncode == 0, marked.stdout.decode()
    records = _traces(tmp_path)
    assert {record["worker"] for record in records} == {"main", "gw0", "gw1", "gw2", "gw3"}
    called = [record["test"]["function"] for record in records if record["stage"] == "call-start"]
    assert sorted(called) == ["test_one", "test_two"]
    assert len({record["process_nonce"] for record in records}) == 5


def test_real_blocked_call_retains_entry_on_external_interrupt(tmp_path):
    import time

    command, environment = _child_project(
        tmp_path, "import time\ndef test_blocked(): time.sleep(30)\n"
    )
    environment["SPECFACT_TARGET_PYTEST"] = "1"
    process = subprocess.Popen(
        command, cwd=tmp_path, env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    try:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            paths = list((tmp_path / "scratch/changecost-pytest-stage").glob("*.json"))
            if paths and json.loads(paths[0].read_text())["stage"] == "call-start":
                break
            time.sleep(0.01)
        else:
            pytest.fail("blocked pytest did not write call entry")
        process.terminate()
        process.communicate(timeout=10)
        assert process.returncode != 0
        state = json.loads(paths[0].read_text())
        assert state["stage"] == "call-start"
        assert state["test"]["function"] == "test_blocked"
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate(timeout=10)
