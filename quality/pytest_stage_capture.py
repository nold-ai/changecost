from __future__ import annotations

import json
import os
import re
import stat
import sys
import tempfile
import threading
import time
from contextlib import contextmanager
from itertools import islice
from pathlib import Path

from quality.pytest_stage import _MAX_STATE, _MAX_WRITES, _STAGES, _SUFFIX, _test_identity
from quality.runtime_diagnostics import (
    child_directory,
    directory,
    require,
    unique_members,
    write_output,
)

_PREFIX = "specfact-targeted-pytest-coverage-"
_MAX_STREAMS = 16
_MAX_MEMBERS = 2
_MAX_SCANS = 1800


def _read_state(parent, name):
    fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
    try:
        metadata = os.fstat(fd)
        require(stat.S_ISREG(metadata.st_mode) and metadata.st_nlink == 1)
        require(metadata.st_uid == os.getuid() and 0 < metadata.st_size <= _MAX_STATE)
        raw = os.read(fd, _MAX_STATE + 1)
    finally:
        os.close(fd)
    require(len(raw) <= _MAX_STATE)
    value = json.loads(raw, object_pairs_hook=unique_members)
    _validate_state(value, name[:-5])
    return value, len(raw)


def _validate_state(value, nonce):
    require(
        isinstance(value, dict)
        and set(value)
        == {
            "sequence",
            "stage",
            "test",
            "worker",
            "process_nonce",
            "elapsed_ms",
            "write_limit_reached",
        }
    )
    require(type(value["sequence"]) is int and 1 <= value["sequence"] <= _MAX_WRITES)
    require(type(value["elapsed_ms"]) is int and 0 <= value["elapsed_ms"] <= 10**12)
    require(type(value["write_limit_reached"]) is bool)
    require(isinstance(value["stage"], str) and value["stage"] in _STAGES)
    require(value["process_nonce"] == nonce)
    require(
        isinstance(value["worker"], str)
        and re.fullmatch(r"main|unknown|gw[0-9]{1,3}", value["worker"])
    )
    _validate_test(value["test"])


def _validate_test(test):
    if test is not None:
        require(isinstance(test, dict) and set(test) == {"module", "function", "parameter_sha256"})
        require(isinstance(test["module"], str) and isinstance(test["function"], str))
        require(
            _test_identity(test["module"] + "::" + test["function"])
            == {**test, "parameter_sha256": None}
        )
        parameter = test["parameter_sha256"]
        require(
            parameter is None
            or isinstance(parameter, str)
            and re.fullmatch(r"[0-9a-f]{64}", parameter)
        )


class _Capture:
    def __init__(self, root, binding, clock=time.monotonic, max_scans=_MAX_SCANS):
        self.root = root
        self.binding = binding
        self.clock = clock
        self.start = clock()
        self.max_scans = min(max_scans, _MAX_SCANS)
        self.scans = 0
        self.members = {}
        self.latest = {}
        self.reasons = set()
        self.bytes_read = 0
        self.work_seconds = 0.0

    def sample(self):
        if self.scans >= self.max_scans:
            self.reasons.add("scan_limit_reached")
            return
        self.scans += 1
        started = self.clock()
        try:
            with directory(self.root) as root:
                with os.scandir(root) as entries:
                    names = [entry.name for entry in islice(entries, 65)]
                if len(names) > 64:
                    self.reasons.add("directory_limit_reached")
                if self.members.keys() - set(names):
                    self.reasons.add("member_disappeared")
                for name in names[:64]:
                    if name.startswith(_PREFIX):
                        self._member(root, name)
        except Exception:
            self.reasons.add("sample_unavailable")
        finally:
            self.work_seconds += max(0, self.clock() - started)

    def _member(self, root, name):
        if name not in self.members and len(self.members) >= _MAX_MEMBERS:
            self.reasons.add("member_limit_reached")
            return
        try:
            with child_directory(root, name) as member:
                metadata = os.fstat(member)
                require(metadata.st_uid == os.getuid())
                identity = (metadata.st_dev, metadata.st_ino)
                previous = self.members.setdefault(name, identity)
                if previous != identity:
                    self.reasons.add("member_replaced")
                    return
                with (
                    child_directory(member, "temporary") as scratch,
                    child_directory(scratch, _SUFFIX) as folder,
                ):
                    self._folder(folder, name)
        except Exception:
            self.reasons.add("member_unavailable")

    def _folder(self, folder, member):
        with os.scandir(folder) as entries:
            names = [entry.name for entry in islice(entries, 34)]
        if len(names) > 33:
            self.reasons.add("directory_limit_reached")
        if any(key[0] == member and key[1] not in names for key in self.latest):
            self.reasons.add("state_disappeared")
        for name in names[:33]:
            if not re.fullmatch(r"[0-9a-f]{32}\.json", name):
                continue
            key = (member, name)
            if key not in self.latest and len(self.latest) >= _MAX_STREAMS:
                self.reasons.add("stream_limit_reached")
                continue
            try:
                value, size = _read_state(folder, name)
                self.bytes_read += size
                self._accept(key, value)
            except Exception:
                self.reasons.add("state_unavailable")

    def _accept(self, key, value):
        previous = self.latest.get(key)
        if previous is not None:
            old = previous["state"]
            if value["sequence"] <= old["sequence"]:
                if value != old:
                    self.reasons.add("state_regressed_or_changed")
                return
            if value["elapsed_ms"] < old["elapsed_ms"] or value["worker"] != old["worker"]:
                self.reasons.add("state_regressed_or_changed")
                return
        self.latest[key] = dict(
            member=list(self.members).index(key[0]),
            state=value,
            captured_elapsed_ms=max(0, int((self.clock() - self.start) * 1000)),
        )
        if value["write_limit_reached"]:
            self.reasons.add("write_limit_reached")

    def finish(self, output):
        self.sample()
        value = dict(
            status="incomplete" if self.latest else "unavailable",
            input_digest=self.binding,
            member_seen=bool(self.members),
            latest=list(self.latest.values()),
            reasons=sorted(self.reasons),
            scans=self.scans,
            bytes_read=self.bytes_read,
            sampling_seconds=round(self.work_seconds, 6),
            elapsed_seconds=round(max(0, self.clock() - self.start), 3),
        )
        write_output(output, value)


@contextmanager
def capture_pytest_stage(input_digest, output):
    """Yield an owned child TMPDIR, or None when diagnostics cannot start."""
    temporary = None
    capture = None
    started = False
    stop = threading.Event()
    thread = None
    root = None
    try:
        temporary = tempfile.TemporaryDirectory(prefix="changecost-pytest-stage-")
        root = Path(temporary.name).resolve()
        capture = _Capture(root, input_digest)

        def observe():
            while not stop.wait(1):
                capture.sample()

        thread = threading.Thread(target=observe, name="pytest-stage-observer")
        thread.start()
        started = True
    except Exception:
        if capture is not None:
            capture.reasons.add("startup_unavailable")
        print("pytest stage diagnostics unavailable", file=sys.stderr)
    try:
        yield root
    finally:
        stop.set()
        if started and thread is not None:
            thread.join()
        try:
            if capture is not None:
                capture.finish(output)
        except Exception:
            print("pytest stage diagnostics unavailable", file=sys.stderr)
        finally:
            if temporary is not None:
                try:
                    temporary.cleanup()
                except OSError:
                    print("pytest stage diagnostics cleanup unavailable", file=sys.stderr)
