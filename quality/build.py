"""Constrained sdist-to-wheel build and clean installed-package proof."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import zipfile
from email.parser import BytesParser
from pathlib import Path


def command(root: Path, *args: str) -> None:
    subprocess.run(args, cwd=root, check=True)


def archive_errors(names: list[str]) -> list[str]:
    forbidden = {".changecost", ".specfact", "artifacts", ".env", "tests", "quality"}
    errors = [
        f"private/development path in distribution: {n}"
        for n in names
        if forbidden & set(Path(n).parts) or n.endswith((".key", ".pem"))
    ]
    if not any("LICENSE" in n for n in names):
        errors.append("distribution license missing")
    return errors


def run(root: Path) -> list[str]:
    with tempfile.TemporaryDirectory(prefix="changecost-build-") as directory:
        temp = Path(directory)
        constraints = temp / "build.txt"
        runtime = temp / "runtime.txt"
        output = temp / "dist"
        command(
            root,
            "uv",
            "export",
            "--locked",
            "--only-group",
            "build",
            "--no-emit-project",
            "--output-file",
            str(constraints),
        )
        source = temp / "source"
        source.mkdir()
        for name in ("src", "pyproject.toml", "README.md", "LICENSE"):
            if (root / name).is_dir():
                shutil.copytree(
                    root / name, source / name, ignore=shutil.ignore_patterns("__pycache__")
                )
            else:
                shutil.copyfile(root / name, source / name)
        for name in (
            ".env",
            "artifacts/private.csv",
            ".changecost/private.json",
            ".specfact/review.json",
        ):
            sentinel = source / name
            sentinel.parent.mkdir(parents=True, exist_ok=True)
            sentinel.write_text("synthetic-private-sentinel")
        command(
            source,
            "uv",
            "build",
            "--build-constraints",
            str(constraints),
            "--require-hashes",
            "--out-dir",
            str(output),
        )
        (wheel,) = output.glob("*.whl")
        (sdist,) = output.glob("*.tar.gz")
        expected = tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"]
        with zipfile.ZipFile(wheel) as archive:
            errors = archive_errors(archive.namelist())
            (metadata_name,) = (n for n in archive.namelist() if n.endswith(".dist-info/METADATA"))
            metadata = BytesParser().parsebytes(archive.read(metadata_name))
            if metadata["Version"] != expected:
                errors.append("wheel version mismatch")
            if any("specfact" in dep.lower() for dep in metadata.get_all("Requires-Dist", [])):
                errors.append("SpecFact is a runtime dependency")
        with tarfile.open(sdist) as archive:
            errors.extend(archive_errors(archive.getnames()))
            (member,) = (m for m in archive.getmembers() if m.name.endswith("/PKG-INFO"))
            stream = archive.extractfile(member)
            if stream is None or BytesParser().parsebytes(stream.read())["Version"] != expected:
                errors.append("sdist version mismatch")
        command(root, "uv", "venv", "--python", sys.executable, str(temp / "venv"))
        python = temp / "venv/bin/python"
        command(
            root,
            "uv",
            "export",
            "--locked",
            "--no-dev",
            "--no-emit-project",
            "--output-file",
            str(runtime),
        )
        command(
            temp, "uv", "pip", "sync", "--python", str(python), "--require-hashes", str(runtime)
        )
        command(temp, "uv", "pip", "install", "--python", str(python), "--no-deps", str(wheel))
        env = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "VIRTUAL_ENV"}}
        env["PATH"] = str(python.parent) + os.pathsep + env.get("PATH", "")
        subprocess.run(
            [str(python), str(root / "tests/test_cli.py")], cwd=temp, env=env, check=True
        )
        command(
            temp,
            str(python),
            "-c",
            'import importlib.util; assert importlib.util.find_spec("specfact") is None',
        )
        # A contradictory constraint is a real negative probe, not an unavailable tool.
        constraints.write_text("hatchling==0.0.0 --hash=sha256:" + "0" * 64 + "\n")
        rejected = subprocess.run(
            [
                "uv",
                "build",
                "--offline",
                "--build-constraints",
                str(constraints),
                "--require-hashes",
                "--out-dir",
                str(temp / "rejected"),
            ],
            cwd=root,
            capture_output=True,
            check=False,
        )
        if rejected.returncode == 0:
            errors.append("build accepted contradictory backend constraint")
        return errors
