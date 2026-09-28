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


def license_name(expression: str | None, legacy: str | None, classifiers: list[str]) -> str:
    """Prefer SPDX metadata and retain legacy/classifier evidence as fallbacks."""
    return expression or legacy or "; ".join(c for c in classifiers if c.startswith("License ::"))


def license_record(package: dict, installed: dict) -> tuple[dict, list[str]]:
    """Read one exact locked package's installed or registry license evidence."""
    name, version = package["name"], package["version"]
    dist = installed.get(name)
    errors = []
    row = {"name": name, "version": version}
    if dist is None or dist.version != version:
        url = f"https://pypi.org/pypi/{name}/{version}/json"
        with urllib.request.urlopen(url, timeout=30) as response:
            info = json.load(response)["info"]
        value = license_name(
            info.get("license_expression"), info.get("license"), info["classifiers"]
        )
        row["source"] = url
    else:
        metadata = dist.metadata
        value = license_name(
            metadata["License-Expression"], metadata["License"], metadata.get_all("Classifier", [])
        )
        row["version"] = dist.version
    row["license"] = value
    if not value or value.strip().upper() == "UNKNOWN":
        errors.append(f"license evidence unavailable: {name}")
    return row, errors


def installed_version_errors(locked: list[dict], installed: dict) -> list[str]:
    """Reject installed versions outside every locked registry alternative."""
    allowed: dict[str, set[str]] = {}
    for package in locked:
        if "registry" in package["source"]:
            allowed.setdefault(package["name"], set()).add(package["version"])
    return [
        f"installed license version differs from lock: {name}"
        for name, versions in allowed.items()
        if name in installed and installed[name].version not in versions
    ]


def licenses(root: Path) -> list[str]:
    """Persist every locked registry package's license evidence, failing on gaps."""
    locked = tomllib.loads((root / "uv.lock").read_text())["package"]
    installed = {
        canonicalize_name(d.metadata["Name"]): d for d in importlib.metadata.distributions()
    }
    errors = installed_version_errors(locked, installed)
    rows = []
    for package in sorted(locked, key=lambda item: (item["name"], item["version"])):
        if "registry" not in package["source"]:
            continue
        try:
            row, missing = license_record(package, installed)
            rows.append(row)
            errors.extend(missing)
        except (OSError, ValueError, KeyError) as exc:
            errors.append(f"license metadata unavailable: {package['name']}: {exc}")
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
