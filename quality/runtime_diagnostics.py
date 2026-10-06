"""Collect bounded, identity-matched metadata; never copy runtime payloads."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import stat
import sys
import threading
import time
import uuid
from collections import deque
from contextlib import contextmanager, suppress
from itertools import islice
from pathlib import Path
from typing import Any

from packaging.version import Version

MAX_FILE = 16 * 1024 * 1024
MAX_OUTPUT = 65_536
MAX_ENTRIES = 256
MAX_PACKAGES = 1000
SCHEMA = "changecost/runtime-diagnostic-v1"
MARKERS = (
    "implementation_name",
    "implementation_version",
    "python_full_version",
    "python_version",
    "platform_python_implementation",
    "platform_machine",
    "sys_platform",
    "os_name",
)


def resource_limit(root, name, count):
    """Read only bounded numeric/max tokens from a fixed kernel limit file."""
    try:
        fd = os.open(root / name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, "rb") as source:
            raw = source.read(65)
        fields = raw.split()
        if len(raw) > 64 or len(fields) != count:
            return None
        if any(re.fullmatch(rb"max|[0-9]{1,20}", field) is None for field in fields):
            return None
        return ["max" if field == b"max" else int(field) for field in fields]
    except OSError:
        return None


def host_context(root=Path("/sys/fs/cgroup")):
    """Observe fixed host fields without printing environment or runtime payloads."""
    affinity = None
    if hasattr(os, "sched_getaffinity"):
        with suppress(OSError):
            affinity = len(os.sched_getaffinity(0))
    return dict(
        python_version=list(sys.version_info[:3]),
        cpu_count=os.cpu_count(),
        cpu_affinity_count=affinity,
        cgroup_cpu_max=resource_limit(root, "cpu.max", 2),
        cgroup_memory_max=resource_limit(root, "memory.max", 1),
    )


def require(condition):
    if not condition:
        raise ValueError("invalid diagnostic metadata")


@contextmanager
def directory(path):
    """Walk no-follow directory descriptors, preserving parents across replacement."""
    parts = Path(path).absolute().parts
    require(".." not in parts)
    fd = os.open(parts[0], os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for name in parts[1:]:
            child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        yield fd
    finally:
        os.close(fd)


@contextmanager
def child_directory(parent, name):
    fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
    try:
        yield fd
    finally:
        os.close(fd)


def unique_members(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result)
        result[key] = value
    return result


def reject_constant(_value):
    raise ValueError("invalid JSON constant")


def finite_float(value):
    result = float(value)
    require(math.isfinite(result))
    return result


def read_metadata(parent, name):
    fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
    try:
        metadata = os.fstat(fd)
        require(stat.S_ISREG(metadata.st_mode) and metadata.st_nlink == 1)
        require(0 < metadata.st_size <= MAX_FILE)
        with os.fdopen(fd, "rb", closefd=False) as source:
            raw = source.read(MAX_FILE + 1)
        require(len(raw) <= MAX_FILE)
        value = json.loads(
            raw,
            object_pairs_hook=unique_members,
            parse_constant=reject_constant,
            parse_float=finite_float,
        )
        require(isinstance(value, dict))
        return value
    finally:
        os.close(fd)


def digest_identity(value):
    require(isinstance(value, str) and re.fullmatch(r"sha256:[0-9a-f]{64}", value))
    return value


def report_runtime(report):
    require(report.get("schema_version") == "1.6")
    scope = report.get("scope_evidence")
    require(isinstance(scope, dict))
    runtime = scope.get("project_runtime")
    require(isinstance(runtime, dict) and runtime.get("status") == "PASS")
    require(runtime.get("schema") == "project-runtime-layer-v2")
    require(
        runtime.get("authority") == "local_build" and runtime.get("protected_pr_eligible") is False
    )
    for name in ("identity", "project_identity"):
        digest_identity(runtime.get(name))
    require(runtime.get("environment_id") in {"linux-x86_64-cp311", "linux-x86_64-cp313"})
    return runtime


def matched_descriptor(cache, runtime):
    with os.scandir(cache) as entries:
        candidates = [entry.name for entry in islice(entries, MAX_ENTRIES + 1)]
    require(len(candidates) <= MAX_ENTRIES)
    matches = []
    for name in candidates:
        if not re.fullmatch(r"[0-9a-f]{64}", name):
            continue
        with child_directory(cache, name) as folder:
            descriptor = read_metadata(folder, "project-runtime.json")
        unsigned = {k: v for k, v in descriptor.items() if k != "identity"}
        canonical = json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()
        identity = "sha256:" + hashlib.sha256(canonical).hexdigest()
        require(descriptor.get("identity") == identity)
        if identity == runtime["identity"]:
            matches.append(descriptor)
    require(len(matches) == 1)
    return matches[0]


def package_metadata(name, version):
    require(isinstance(name, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", name))
    require(
        isinstance(version, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.!+_-]{0,127}", version)
    )
    Version(version)
    return dict(name=name, version=version)


def installed_packages(inventory):
    installed = inventory.get("installed")
    require(isinstance(installed, list) and len(installed) <= MAX_PACKAGES)
    result = []
    for row in installed:
        require(isinstance(row, dict) and type(row.get("requested")) is bool)
        metadata = row.get("metadata")
        if not isinstance(metadata, dict):
            raise ValueError("invalid package metadata")
        result.append(
            dict(
                **package_metadata(metadata.get("name"), metadata.get("version")),
                requested=row["requested"],
            )
        )
    return result


def python_markers(inventory):
    environment = inventory.get("environment")
    require(isinstance(environment, dict))
    result = {}
    for key in MARKERS:
        if key in environment:
            value = environment[key]
            require(isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9._-]{1,64}", value))
            result[key] = value
    return result


def observation_graph(inventory):
    graphs = inventory.get("member_graphs")
    require(isinstance(graphs, dict))
    graph = graphs.get("pytest-observe")
    require(isinstance(graph, dict))
    installed = graph.get("installed")
    require(isinstance(installed, list) and len(installed) <= MAX_PACKAGES)
    result = []
    for row in installed:
        require(isinstance(row, dict))
        dependencies = row.get("dependencies")
        require(isinstance(dependencies, list) and len(dependencies) <= MAX_PACKAGES)
        for name in dependencies:
            package_metadata(name, "0")
        result.append(
            dict(**package_metadata(row.get("name"), row.get("version")), dependencies=dependencies)
        )
    return result


def project_diagnostic(descriptor, runtime):
    for key in ("schema", "identity", "project_identity", "environment_id"):
        require(descriptor.get(key) == runtime[key])
    provenance = dict(authority="local_build", protected_pr_eligible=False)
    require(descriptor.get("provenance") == provenance)
    worker = digest_identity(descriptor.get("worker_identity"))
    inventory = descriptor.get("inventory")
    require(isinstance(inventory, dict))
    return dict(
        schema=SCHEMA,
        status="collected",
        runtime_schema=runtime["schema"],
        runtime_identity=runtime["identity"],
        project_identity=runtime["project_identity"],
        worker_identity=worker,
        environment_id=runtime["environment_id"],
        provenance=provenance,
        python_markers=python_markers(inventory),
        packages=installed_packages(inventory),
        member_graph={"pytest-observe": observation_graph(inventory)},
    )


def encode_output(value):
    raw = (json.dumps(value, sort_keys=True, ensure_ascii=True) + "\n").encode()
    require(len(raw) <= MAX_OUTPUT)
    return raw


def collect(report_path, cache_path):
    try:
        report_path = Path(report_path)
        with directory(report_path.parent) as folder:
            runtime = report_runtime(read_metadata(folder, report_path.name))
        with directory(cache_path) as cache:
            result = project_diagnostic(matched_descriptor(cache, runtime), runtime)
        encode_output(result)
        return result
    except (OSError, ValueError, RecursionError) as exc:
        raise ValueError("unavailable or invalid runtime metadata") from exc


def write_output(path, value):
    raw = encode_output(value)
    path = Path(path)
    with directory(path.parent) as folder:
        fd = os.open(
            path.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=folder
        )
        with os.fdopen(fd, "wb") as target:
            target.write(raw)


PROCESS_LIMIT = 512
TREE_LIMIT = 32
SAMPLE_LIMIT = 120


def parse_process_stat(raw, pid):
    require(len(raw) <= 4096 and raw.startswith(f"{pid} (".encode()))
    _, separator, suffix = raw.rpartition(b")")
    fields = suffix.split()
    require(separator and len(fields) >= 22 and fields[0] in b"R S D T t Z X I P K W".split())
    indices = (1, 11, 12, 19, 21)
    require(all(re.fullmatch(rb"[0-9]{1,20}", fields[i]) for i in indices))
    parent, user, system, start, rss = (int(fields[i]) for i in indices)
    return dict(
        pid=pid,
        parent=parent,
        start_ticks=start,
        cpu_ticks=user + system,
        rss_pages=rss,
        state=fields[0].decode("ascii"),
    )


def read_process(folder, name):
    with child_directory(folder, name) as child:
        fd = os.open("stat", os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=child)
        with os.fdopen(fd, "rb") as source:
            return parse_process_stat(source.read(4097), int(name))


def process_descends(row, rows, root_identity, baseline):
    seen = set()
    while (row["pid"], row["start_ticks"]) != root_identity:
        identity = (row["pid"], row["start_ticks"])
        if identity in seen or identity in baseline:
            return False
        seen.add(identity)
        parent = rows.get(row["parent"])
        if parent is None or parent["start_ticks"] > row["start_ticks"]:
            return False
        row = parent
    return True


def process_tree(
    root_pid, start_ticks, proc_root=Path("/proc"), baseline: set | frozenset = frozenset()
):
    result: dict[str, Any] = dict(
        processes=[], unavailable=0, truncated=False, root_valid=False, lineage_exclusions=0
    )
    rows = {}
    try:
        with directory(proc_root) as folder:
            with os.scandir(folder) as entries:
                names = [e.name for e in islice(entries, PROCESS_LIMIT + 1)]
            result["truncated"] = len(names) > PROCESS_LIMIT
            for name in names[:PROCESS_LIMIT]:
                if not re.fullmatch(r"[0-9]{1,10}", name):
                    continue
                try:
                    rows[int(name)] = read_process(folder, name)
                except (OSError, ValueError):
                    result["unavailable"] += 1
            root = read_process(folder, str(root_pid))
            rows[root_pid] = root
        if root["start_ticks"] != start_ticks:
            return result
        result["root_valid"] = True
        result["processes"] = [
            r
            for pid, r in rows.items()
            if pid != root_pid and process_descends(r, rows, (root_pid, start_ticks), baseline)
        ]
        result["lineage_exclusions"] = len(rows) - 1 - len(result["processes"])
    except (OSError, ValueError):
        result["unavailable"] += 1
    return result


class NativeObservation:
    """Bounded live-process samples; no cumulative CPU or unique-memory claims."""

    def __init__(self, root_pid, input_digest, proc_root=Path("/proc")):
        require(type(root_pid) is int and root_pid > 0)
        require(isinstance(input_digest, str) and re.fullmatch(r"[0-9a-f]{64}", input_digest))
        self.root_pid, self.proc_root = root_pid, proc_root
        self.start_ticks = None
        try:
            with directory(proc_root) as folder:
                self.start_ticks = read_process(folder, str(root_pid))["start_ticks"]
        except (OSError, ValueError):
            pass
        initial = process_tree(root_pid, self.start_ticks, proc_root)
        self.baseline = {(r["pid"], r["start_ticks"]) for r in initial["processes"]}
        self.baseline_incomplete = (
            not initial["root_valid"] or initial["truncated"] or bool(initial["unavailable"])
        )
        self.units: dict[str, int | None] = dict(cpu_ticks_per_second=None, rss_page_bytes=None)
        for key, name in (
            ("cpu_ticks_per_second", "SC_CLK_TCK"),
            ("rss_page_bytes", "SC_PAGE_SIZE"),
        ):
            with suppress(OSError, ValueError):
                value = os.sysconf(name)
                self.units[key] = value if value > 0 else None
        self.binding = dict(
            input_digest=input_digest,
            root_pid=root_pid,
            root_start_ticks=self.start_ticks,
            invocation_id=uuid.uuid4().hex,
        )
        self.samples = deque(maxlen=SAMPLE_LIMIT)
        self.first_tree = None
        self.latest_tree = []
        self.truncated = False
        self.departures = False
        self.previous = set()
        self.status = "unavailable"
        self.sampling_error = False
        self.sample(0)

    def sample(self, elapsed):
        if self.baseline_incomplete:
            return
        result = process_tree(self.root_pid, self.start_ticks, self.proc_root, self.baseline)
        rows = result["processes"]
        identities = {(r["pid"], r["start_ticks"]) for r in rows}
        self.departures |= bool(self.previous - identities)
        self.previous = identities
        self.truncated |= result["truncated"] or len(rows) > TREE_LIMIT
        self.truncated |= len(self.samples) == SAMPLE_LIMIT
        self.status = "collected" if result["root_valid"] else "unavailable"
        self.latest_tree = sorted(rows, key=lambda r: r["pid"])[:TREE_LIMIT]
        if self.first_tree is None and rows:
            self.first_tree = self.latest_tree
        states = {state: sum(r["state"] == state for r in rows) for state in "RSDTtZXIPKW"}
        self.samples.append(
            dict(
                elapsed_seconds=round(elapsed, 3),
                processes=len(rows),
                live_cpu_ticks=sum(r["cpu_ticks"] for r in rows),
                live_rss_pages=sum(r["rss_pages"] for r in rows),
                states=states,
                unavailable=result["unavailable"],
                root_valid=result["root_valid"],
                lineage_exclusions=result["lineage_exclusions"],
            )
        )

    def finish(self, output, elapsed):
        self.sample(elapsed)
        write_output(
            output,
            dict(
                schema="changecost/native-process-diagnostic-v1",
                status=self.status,
                sampling_error=self.sampling_error,
                binding=self.binding,
                units=self.units,
                baseline_incomplete=self.baseline_incomplete,
                truncated=self.truncated,
                departures=self.departures,
                first_tree=self.first_tree or [],
                latest_tree=self.latest_tree,
                samples=list(self.samples),
                terminal_elapsed_seconds=round(elapsed, 3),
            ),
        )


@contextmanager
def observe_native(root_pid, input_digest, output, proc_root=Path("/proc"), interval: float = 5):
    """Observe one unchanged native command; diagnostic failures never mask its result."""
    start = time.monotonic()
    observation = NativeObservation(root_pid, input_digest, proc_root)
    stop = threading.Event()

    def sample_until_stopped():
        while not stop.wait(interval):
            observation.sample(time.monotonic() - start)

    thread = threading.Thread(target=sample_until_stopped, name="native-numeric-observer")
    started = False
    try:
        thread.start()
        started = True
    except RuntimeError:
        observation.sampling_error = True
    try:
        yield
    finally:
        stop.set()
        if started:
            thread.join()
        try:
            observation.finish(output, time.monotonic() - start)
        except (OSError, ValueError):
            print("native process diagnostics unavailable", file=sys.stderr)


def main(args=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("cache", type=Path)
    parser.add_argument("output", type=Path)
    options = parser.parse_args(args)
    status = 0
    try:
        result = collect(options.report, options.cache)
    except ValueError:
        result = dict(schema=SCHEMA, status="unavailable_or_invalid")
        status = 2
    try:
        write_output(options.output, result)
    except (OSError, ValueError):
        status = 2
    if status:
        print("runtime metadata diagnostics unavailable or invalid", file=sys.stderr)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
