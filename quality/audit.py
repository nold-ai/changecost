"""Audit the locked environment; unavailable advisory/license data is incomplete."""

from __future__ import annotations

import importlib.metadata
import json
import subprocess
import tempfile
import tomllib
import urllib.request
from pathlib import Path

from packaging.utils import canonicalize_name


def licenses(root: Path) -> list[str]:
    locked = tomllib.loads((root / "uv.lock").read_text())["package"]
    names = {p["name"] for p in locked if "registry" in p["source"]}
    installed = {
        canonicalize_name(d.metadata["Name"]): d for d in importlib.metadata.distributions()
    }
    errors: list[str] = []
    rows = []
    for name in sorted(names):
        dist = installed.get(name)
        if dist is None:
            package = next(p for p in locked if p["name"] == name)
            url = f"https://pypi.org/pypi/{name}/{package['version']}/json"
            try:
                with urllib.request.urlopen(url, timeout=30) as response:
                    info = json.load(response)["info"]
                license_name = info.get("license_expression") or info.get("license")
                if not license_name:
                    license_name = "; ".join(
                        c for c in info["classifiers"] if c.startswith("License ::")
                    )
                if not license_name or license_name.upper() == "UNKNOWN":
                    errors.append(f"license evidence unavailable: {name}")
                rows.append(
                    {
                        "name": name,
                        "version": package["version"],
                        "license": license_name,
                        "source": url,
                    }
                )
            except (OSError, ValueError, KeyError) as exc:
                errors.append(f"license metadata unavailable: {name}: {exc}")
            continue
        locked_versions = {p["version"] for p in locked if p["name"] == name}
        if dist.version not in locked_versions:
            errors.append(f"installed license version differs from lock: {name}")
        metadata = dist.metadata
        license_name = metadata["License-Expression"] or metadata["License"]
        if not license_name:
            license_name = "; ".join(
                v for v in metadata.get_all("Classifier", []) if v.startswith("License ::")
            )
        if not license_name or license_name.strip().upper() == "UNKNOWN":
            errors.append(f"license evidence unavailable: {name}")
        rows.append({"name": name, "version": dist.version, "license": license_name})
    output = root / ".changecost/dependency-licenses.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(rows, indent=2) + "\n")
    return errors


def run(root: Path) -> list[str]:
    errors = licenses(root)
    with tempfile.TemporaryDirectory(prefix="changecost-audit-") as directory:
        requirements = Path(directory) / "locked.txt"
        packages = tomllib.loads((root / "uv.lock").read_text())["package"]
        registry = [p for p in packages if "registry" in p["source"]]
        lines = []
        for package in registry:
            artifacts = package.get("wheels", []) + (
                [package["sdist"]] if "sdist" in package else []
            )
            hashes = " ".join("--hash=" + artifact["hash"] for artifact in artifacts)
            if not hashes:
                errors.append(f"locked hashes unavailable: {package['name']}")
            lines.append(f"{package['name']}=={package['version']} {hashes}")
        requirements.write_text("\n".join(lines) + "\n")
        report = root / ".changecost/dependency-audit.json"
        result = subprocess.run(
            [
                "pip-audit",
                "--no-deps",
                "--disable-pip",
                "--require-hashes",
                "-r",
                str(requirements),
                "--format",
                "json",
                "--output",
                str(report),
            ],
            cwd=root,
            check=False,
        )
        if result.returncode:
            errors.append(
                "dependency audit failed or advisory data unavailable; inspect audit output"
            )
        if not report.exists():
            errors.append("dependency audit report missing")
        else:
            data = json.loads(report.read_text())
            audited = {(p["name"], p.get("version")) for p in data.get("dependencies", [])}
            expected = {(p["name"], p["version"]) for p in registry}
            if audited != expected:
                errors.append("dependency audit coverage differs from the complete lock")
    return errors
