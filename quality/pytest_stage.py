from __future__ import annotations

import hashlib
import json
import os
import re
import time
import uuid
from contextlib import suppress
from pathlib import Path

import pytest

from quality.runtime_diagnostics import child_directory, directory

_SUFFIX = "changecost-pytest-stage"
_SCRATCH = Path("/opt/specfact/tmp")
_MAX_STATE = 1024
_MAX_WRITES = 24_000
_STAGES = {
    "pytest-started",
    "collection-start",
    "collection-end",
    "setup-start",
    "setup-end",
    "call-start",
    "call-end",
    "teardown-start",
    "teardown-end",
    "sessionfinish-enter",
    "sessionfinish-exit",
}


def _test_identity(nodeid):
    source, separator, parameter = nodeid.partition("[")
    parts = source.split("::")
    module, function = parts[0], "::".join(parts[1:])
    if not (
        re.fullmatch(r"tests/(?:[A-Za-z0-9_]+/)*[A-Za-z0-9_]+\.py", module)
        and len(module) <= 160
        and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(?:::[A-Za-z_][A-Za-z0-9_]*)*", function)
        and len(function) <= 120
    ):
        return None
    try:
        parameter_digest = hashlib.sha256(parameter.encode()).hexdigest() if separator else None
    except UnicodeEncodeError:
        return None
    return dict(
        module=module,
        function=function,
        parameter_sha256=parameter_digest,
    )


class _Writer:
    def __init__(self, scratch, worker, clock=time.monotonic, max_writes=_MAX_WRITES):
        self.scratch = scratch
        self.worker = worker if re.fullmatch(r"main|gw[0-9]{1,3}", worker) else "unknown"
        self.clock = clock
        self.start = clock()
        self.nonce = uuid.uuid4().hex
        self.sequence = 0
        self.max_writes = min(max_writes, _MAX_WRITES)
        self.disabled = False

    def emit(self, stage, nodeid=None):
        if self.disabled or self.sequence >= self.max_writes:
            return
        try:
            self.sequence += 1
            state = dict(
                sequence=self.sequence,
                stage=stage,
                test=_test_identity(nodeid) if nodeid is not None else None,
                worker=self.worker,
                process_nonce=self.nonce,
                elapsed_ms=max(0, int((self.clock() - self.start) * 1000)),
                write_limit_reached=self.sequence == self.max_writes,
            )
            raw = json.dumps(state, separators=(",", ":")).encode("ascii")
            if len(raw) > _MAX_STATE:
                raise ValueError("stage state exceeds bound")
            self._write(raw)
        except Exception:
            self.disabled = True

    def _write(self, raw):
        with directory(self.scratch) as scratch:
            with suppress(FileExistsError):
                os.mkdir(_SUFFIX, mode=0o700, dir_fd=scratch)
            with child_directory(scratch, _SUFFIX) as target:
                part = self.nonce + ".part"
                fd = os.open(
                    part, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=target
                )
                with os.fdopen(fd, "wb") as output:
                    output.write(raw)
                os.replace(part, self.nonce + ".json", src_dir_fd=target, dst_dir_fd=target)


_writer: _Writer | None = None


def pytest_configure(config):
    global _writer
    _writer = None
    if os.environ.get("SPECFACT_TARGET_PYTEST") != "1":
        return
    try:
        if _SCRATCH.is_dir():
            worker = getattr(config, "workerinput", {}).get("workerid", "main")
            _writer = _Writer(_SCRATCH, worker)
    except Exception:
        _writer = None


def _emit(stage, item=None):
    if _writer is not None:
        _writer.emit(stage, item.nodeid if item is not None else None)


def pytest_sessionstart(session):
    _emit("pytest-started")


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_collection(session):
    _emit("collection-start")
    try:
        return (yield)
    finally:
        _emit("collection-end")


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_setup(item):
    _emit("setup-start", item)
    try:
        return (yield)
    finally:
        _emit("setup-end", item)


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_call(item):
    _emit("call-start", item)
    try:
        return (yield)
    finally:
        _emit("call-end", item)


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_teardown(item, nextitem):
    _emit("teardown-start", item)
    try:
        return (yield)
    finally:
        _emit("teardown-end", item)


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_sessionfinish(session, exitstatus):
    _emit("sessionfinish-enter")
    try:
        return (yield)
    finally:
        _emit("sessionfinish-exit")
