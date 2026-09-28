"""Shared leaf gates and aggregate used locally, by hooks and by CI."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from quality import audit, build, docs, external_tools, index, metadata, review, workflow
from quality.repository import baseline, changed, checked_names, git, inventory, materialize_index

LEAVES = (
    "lock",
    "hygiene",
    "lint",
    "types",
    "docs",
    "index",
    "metadata",
    "workflow",
    "tests",
    "build",
    "audit",
    "review",
    "spec",
)
BEHAVIOR = ("src/", "quality/", "tests/", ".github/workflows/")
CONFIG = {
    "conftest.py",
    "openspec/config.yaml",
    "pyproject.toml",
    "uv.lock",
    "Makefile",
    ".pre-commit-config.yaml",
    ".pre-commit-hygiene.yaml",
    ".python-version",
}


def external(root: Path, args: list[str], *, env: dict[str, str] | None = None) -> list[str]:
    if args[0] in {"specfact", "actionlint", "openspec"}:
        args = [external_tools.executable(root, args[0]), *args[1:]]
    result = subprocess.run(args, cwd=root, check=False, env=env)
    return [] if result.returncode == 0 else [f"{args[0]} failed ({result.returncode})"]


def command_errors(root: Path, name: str, args: list[str]) -> list[str]:
    """Keep inherited selection options out of the required pytest subprocess."""
    if name == "tests":
        env = os.environ.copy()
        env.pop("PYTEST_ADDOPTS", None)
        return external(root, args, env=env)
    return external(root, args)


def leaf(name: str, root: Path, files: set[str], before: dict[str, bytes]) -> list[str]:
    changes = changed(root, files, before)
    commands = {
        "lock": ["uv", "lock", "--check"],
        "lint": ["ruff", "check", "src", "quality", "tests"],
        "types": ["basedpyright"],
        "tests": [sys.executable, "-m", "pytest", "-c", "pyproject.toml"],
        "spec": ["openspec", "validate", "--all", "--strict", "--no-interactive"],
    }
    if name in commands:
        errors = command_errors(root, name, commands[name])
        additional = {
            "lock": [sys.executable, "tests/tool_probes.py"],
            "lint": ["ruff", "format", "--check", "src", "quality", "tests"],
        }
        if name in additional:
            errors.extend(external(root, additional[name]))
        return errors
    if name == "hygiene":
        return external(
            root,
            [
                "pre-commit",
                "run",
                "--config",
                ".pre-commit-hygiene.yaml",
                "--files",
                *sorted(checked_names(files)),
            ],
        )
    if name == "docs":
        mapping = json.loads((root / "quality/docs.json").read_text())
        exceptions = json.loads((root / "quality/exceptions.json").read_text())
        return docs.validate(root, files, mapping, before, exceptions)
    if name == "index":
        return index.check_outputs(root, index.render(root))
    if name == "metadata":
        return metadata.validate(
            root, files, before, json.loads((root / "quality/exceptions.json").read_text())
        )
    if name == "workflow":
        return workflow.validate(root)
    if name == "build":
        return build.run(root)
    if name in {"audit", "review"}:
        return evidence_gate(name, root, files, changes)
    raise ValueError(f"unknown required validator: {name}")


def evidence_gate(name: str, root: Path, files: set[str], changes: set[str]) -> list[str]:
    if name == "audit":
        if changes & {"pyproject.toml", "uv.lock", "quality/audit.py"}:
            return audit.run(root)
        print("audit: not applicable (locked dependency/audit inputs unchanged)")
        return []
    if name == "review":
        if changes & CONFIG or any(p.startswith(BEHAVIOR) for p in changes):
            return review.run(root, files)
        print("review: not applicable (no behavior-affecting inputs changed)")
        return []
    raise ValueError(f"unknown evidence gate: {name}")


def staged(args: argparse.Namespace) -> int:
    root = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="changecost-index-") as directory:
        snapshot = Path(directory)
        files = materialize_index(root, snapshot)
        manifest = snapshot / ".quality-manifest"
        manifest.write_text("\n".join(sorted(files)) + "\n")
        if not (snapshot / "quality/__main__.py").is_file():
            raise ValueError("staged quality runner missing; stage the foundation files first")
        env = dict(
            os.environ,
            PYTHONPATH=str(snapshot / "src") + os.pathsep + str(snapshot),
            OPENSPEC_TELEMETRY="0",
        )
        # Invoke the staged validator implementation, not unstaged Python modules.
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "quality",
                "commit",
                "--base",
                args.base or "HEAD",
                "--git-root",
                str(root),
                "--manifest",
                str(manifest),
            ],
            cwd=snapshot,
            env=env,
            check=False,
        )
        return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gate", choices=[*LEAVES, "check", "commit", "staged"])
    parser.add_argument("--base", default=os.environ.get("BASE_REF", ""))
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--git-root", type=Path)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    root = Path.cwd()
    if args.gate == "staged":
        return staged(args)
    if args.write:
        if args.gate != "index":
            raise ValueError("--write is only valid for index generation")
        for name, content in index.render(root).items():
            (root / name).write_text(content)
        return 0
    source = args.git_root or root
    sha, before = baseline(source, args.base)
    files = (
        set(args.manifest.read_text().splitlines())
        if args.git_root
        else inventory(root, args.manifest)
    )
    head = git(source, "rev-parse", "HEAD").decode().strip()
    mode = "index" if args.git_root else "working tree"
    print(f"Comparison base: {sha}; head: {head}; input: {mode}", flush=True)
    selected = LEAVES if args.gate == "check" else (args.gate,)
    if args.gate == "commit":
        selected = ("lock", "lint", "types", "docs", "index", "metadata", "workflow")
    results: dict[str, list[str]] = {}
    for name in selected:
        print(f"Running {name}", flush=True)
        try:
            results[name] = leaf(name, root, files, before)
        except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
            results[name] = [f"incomplete {name}: {exc}"]
        for error in results[name]:
            print(error, file=sys.stderr)
    return int(any(results.values()))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"quality: {error}", file=sys.stderr)
        raise SystemExit(1) from error
