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
from contextlib import contextmanager
from itertools import islice
from pathlib import Path

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
