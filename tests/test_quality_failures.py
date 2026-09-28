"""Offline failure-path evidence complementing the real aggregate build/audit gates."""

import io
import json
import runpy
import subprocess
import sys
import tarfile
import zipfile
from email.message import Message
from pathlib import Path
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

from quality import __main__ as runner
from quality import audit, build


def test_cli_and_module_invocations_in_process(monkeypatch, capsys):
    from changecost.cli import app

    cli = CliRunner()
    assert cli.invoke(app, ["--help"]).exit_code == 0
    assert "ChangeCost" in cli.invoke(app, ["--help"]).stdout
    assert cli.invoke(app, ["--version"]).stdout.strip() == "0.1.0.dev0"
    assert cli.invoke(app, []).exit_code == 2
    assert cli.invoke(app, ["quote"]).exit_code == 2
    monkeypatch.setattr(sys, "argv", ["changecost", "--version"])
    with pytest.raises(SystemExit) as result:
        runpy.run_module("changecost", run_name="__main__")
    assert result.value.code == 0
    assert "0.1.0.dev0" in capsys.readouterr().out


def license_metadata(name, value=None, classifier=None):
    metadata = Message()
    metadata["Name"] = name
    if value is not None:
        metadata["License-Expression"] = value
    if classifier:
        metadata["Classifier"] = classifier
    return metadata


def test_license_sources_and_incomplete_evidence(monkeypatch, tmp_path):
    lock = """[[package]]
name="local"
version="0.1"
source={editable="."}
[[package]]
name="installed"
version="1"
source={registry="https://pypi.org/simple"}
[[package]]
name="remote"
version="2"
source={registry="https://pypi.org/simple"}
"""
    (tmp_path / "uv.lock").write_text(lock)
    dist = SimpleNamespace(version="1", metadata=license_metadata("installed", "MIT"))
    monkeypatch.setattr(audit.importlib.metadata, "distributions", lambda: [dist])
    info = {"license_expression": "Apache-2.0", "classifiers": []}
    urls = []

    def remote(url, **kwargs):
        urls.append(url)
        return io.BytesIO(json.dumps({"info": info}).encode())

    monkeypatch.setattr(audit.urllib.request, "urlopen", remote)
    assert audit.licenses(tmp_path) == []
    rows = json.loads((tmp_path / ".changecost/dependency-licenses.json").read_text())
    assert [(r["name"], r["version"], r["license"]) for r in rows] == [
        ("installed", "1", "MIT"),
        ("remote", "2", "Apache-2.0"),
    ]
    assert urls == ["https://pypi.org/pypi/remote/2/json"]
    dist.version = "wrong"
    dist.metadata = license_metadata("installed", "UNKNOWN")
    info["license_expression"] = "UNKNOWN"
    errors = audit.licenses(tmp_path)
    assert len(errors) == 3
    assert any("version differs" in e for e in errors)
    dist.version = "1"
    dist.metadata = license_metadata("installed", classifier="License :: MIT")
    info["license_expression"] = None
    info["classifiers"] = ["License :: Apache", "Programming Language :: Python"]
    assert audit.licenses(tmp_path) == []
    assert audit.license_name(None, "BSD", []) == "BSD"

    def unavailable(*args, **kwargs):
        raise OSError("offline")

    monkeypatch.setattr(audit.urllib.request, "urlopen", unavailable)
    assert audit.licenses(tmp_path) == ["license metadata unavailable: remote: offline"]


def test_audit_requires_complete_locked_hash_and_report_coverage(monkeypatch, tmp_path):
    (tmp_path / "uv.lock").write_text("""[[package]]
name="one"
version="1"
source={registry="https://pypi.org/simple"}
wheels=[{hash="sha256:abc"}]
""")
    monkeypatch.setattr(audit, "licenses", lambda _: [])
    (tmp_path / ".changecost").mkdir()
    dependencies = [{"name": "one", "version": "1"}]
    write_report = True

    def run(args, **kwargs):
        requirements = Path(args[args.index("-r") + 1]).read_text()
        assert "one==1 --hash=sha256:abc" in requirements
        if write_report:
            Path(args[args.index("--output") + 1]).write_text(
                json.dumps({"dependencies": dependencies})
            )
        return subprocess.CompletedProcess(args, 0)

    monkeypatch.setattr(audit.subprocess, "run", run)
    assert audit.run(tmp_path) == []
    dependencies.clear()
    assert audit.run(tmp_path) == ["dependency audit coverage differs from the complete lock"]
    (tmp_path / ".changecost/dependency-audit.json").unlink()
    write_report = False
    assert audit.run(tmp_path) == ["dependency audit report missing"]


def make_distributions(output, *, version="0.1.0.dev0", private=False):
    output.mkdir(parents=True, exist_ok=True)
    wheel, sdist = output / "test.whl", output / "test.tar.gz"
    metadata = f"Metadata-Version: 2.4\nName: changecost\nVersion: {version}\n"
    if private:
        metadata += "Requires-Dist: specfact-cli\n"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("changecost.dist-info/METADATA", metadata)
        archive.writestr("changecost.dist-info/licenses/LICENSE", "license")
        if private:
            archive.writestr("artifacts/private.csv", "sentinel")
    with tarfile.open(sdist, "w:gz") as archive:
        for name, content in {"test/PKG-INFO": metadata, "test/LICENSE": "license"}.items():
            data = content.encode()
            member = tarfile.TarInfo(name)
            member.size = len(data)
            archive.addfile(member, io.BytesIO(data))
    return wheel, sdist


def test_distribution_metadata_and_privacy_are_rejected(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nversion="0.1.0.dev0"\n')
    wheel, sdist = make_distributions(tmp_path / "dist")
    assert build.distribution_errors(tmp_path, wheel, sdist) == []
    wheel, sdist = make_distributions(tmp_path / "dist", version="wrong", private=True)
    errors = build.distribution_errors(tmp_path, wheel, sdist)
    assert "wheel version mismatch" in errors
    assert "sdist version mismatch" in errors
    assert "SpecFact is a runtime dependency" in errors
    assert any("private/development" in e for e in errors)


def test_build_orchestration_checks_hashes_and_contradictory_constraints(monkeypatch, tmp_path):
    (tmp_path / "src").mkdir()
    for name, text in {
        "README.md": "readme",
        "LICENSE": "license",
        "pyproject.toml": '[project]\nversion="0.1.0.dev0"\n',
    }.items():
        (tmp_path / name).write_text(text)
    reject = 1
    calls = []

    def run(args, **kwargs):
        calls.append((args, kwargs))
        if len(args) > 1 and args[1] == "build" and "--offline" not in args:
            source = Path(kwargs["cwd"])
            assert (source / "artifacts/private.csv").read_text() == "synthetic-private-sentinel"
            assert "--require-hashes" in args
            make_distributions(Path(args[args.index("--out-dir") + 1]))
        return subprocess.CompletedProcess(args, reject if "--offline" in args else 0)

    monkeypatch.setattr(build.subprocess, "run", run)
    assert build.run(tmp_path) == []
    assert any("--require-hashes" in args and "sync" in args for args, _ in calls)
    proof_env = next(
        kwargs["env"] for args, kwargs in calls if any(str(x).endswith("test_cli.py") for x in args)
    )
    assert "VIRTUAL_ENV" not in proof_env and "PYTHONPATH" not in proof_env
    assert proof_env["PATH"].split(":")[0].endswith("/venv/bin")
    reject = 0
    assert build.run(tmp_path) == ["build accepted contradictory backend constraint"]


def test_quality_dispatch_propagates_errors_and_comparison(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(runner, "baseline", lambda *a: ("base", {}))
    monkeypatch.setattr(runner, "inventory", lambda *a: set())
    monkeypatch.setattr(runner, "git", lambda *a: b"head")
    monkeypatch.setattr(sys, "argv", ["quality", "lint", "--base", "explicit"])
    monkeypatch.setattr(runner, "leaf", lambda *a: (_ for _ in ()).throw(OSError("tool absent")))
    assert runner.main() == 1
    monkeypatch.setattr(sys, "argv", ["quality", "lint", "--write"])
    with pytest.raises(ValueError, match="only valid"):
        runner.main()
    monkeypatch.setattr(sys, "argv", ["quality", "index", "--write"])
    monkeypatch.setattr(runner.index, "render", lambda *a: {"llms.txt": "generated"})
    assert runner.main() == 0
    assert (tmp_path / "llms.txt").read_text() == "generated"


def test_quality_leaf_external_failures(monkeypatch, tmp_path):
    monkeypatch.setattr(
        runner.subprocess, "run", lambda args, **kw: subprocess.CompletedProcess(args, 3)
    )
    assert runner.external(tmp_path, ["missing"]) == ["missing failed (3)"]
    assert len(runner.leaf("lint", tmp_path, set(), {})) == 2
    assert runner.leaf("hygiene", tmp_path, set(), {})
    monkeypatch.setattr(runner.build, "run", lambda *a: ["bad wheel"])
    assert runner.leaf("build", tmp_path, set(), {}) == ["bad wheel"]
    monkeypatch.setattr(runner.audit, "run", lambda *a: ["audit unavailable"])
    assert runner.evidence_gate("audit", tmp_path, set(), {"uv.lock"}) == ["audit unavailable"]
    assert runner.evidence_gate("audit", tmp_path, set(), set()) == []
    assert runner.evidence_gate("review", tmp_path, set(), {"README.md"}) == []
    with pytest.raises(ValueError, match="unknown required"):
        runner.leaf("absent", tmp_path, set(), {})
    with pytest.raises(ValueError, match="unknown evidence"):
        runner.evidence_gate("absent", tmp_path, set(), set())


def test_license_evidence_preserves_marker_split_versions(monkeypatch, tmp_path):
    (tmp_path / "uv.lock").write_text("""[[package]]
name="demo"
version="1"
source={registry="https://pypi.org/simple"}
resolution-markers=["python_version < '3.12'"]
[[package]]
name="demo"
version="2"
source={registry="https://pypi.org/simple"}
resolution-markers=["python_version >= '3.12'"]
""")
    dist = SimpleNamespace(version="1", metadata=license_metadata("demo", "MIT"))
    monkeypatch.setattr(audit.importlib.metadata, "distributions", lambda: [dist])
    queried = []

    def metadata(url, **kwargs):
        queried.append(url)
        version = url.split("/")[-2]
        return io.BytesIO(
            json.dumps(
                {"info": {"license_expression": f"license-{version}", "classifiers": []}}
            ).encode()
        )

    monkeypatch.setattr(audit.urllib.request, "urlopen", metadata)
    assert audit.licenses(tmp_path) == []
    rows = json.loads((tmp_path / ".changecost/dependency-licenses.json").read_text())
    assert [(row["version"], row["license"]) for row in rows] == [("1", "MIT"), ("2", "license-2")]
    assert queried == ["https://pypi.org/pypi/demo/2/json"]
    queried.clear()
    dist.version = "3"
    assert audit.licenses(tmp_path) == ["installed license version differs from lock: demo"]
    rows = json.loads((tmp_path / ".changecost/dependency-licenses.json").read_text())
    assert [(row["version"], row["license"]) for row in rows] == [
        ("1", "license-1"),
        ("2", "license-2"),
    ]
    assert queried == ["https://pypi.org/pypi/demo/1/json", "https://pypi.org/pypi/demo/2/json"]


@pytest.mark.parametrize("location", ["repository", "environment", "symlink"])
def test_review_rejects_project_validator_shadow(monkeypatch, tmp_path, location):
    from quality import review

    root = tmp_path / "repo"
    root.mkdir()
    environment = tmp_path / "custom-environment"
    environment.mkdir()
    monkeypatch.setattr(sys, "prefix", str(environment))
    monkeypatch.setattr(sys, "base_prefix", str(tmp_path / "base-python"))
    target = (environment if location == "environment" else root) / "specfact"
    report = {
        "assurance_status": "PASS",
        "overall_verdict": "PASS",
        "ci_exit_code": 0,
        "has_unknown_required_evidence": False,
        "analyzer_evidence": [
            {"id": name, "execution_state": "ran", "evidence_outcome": "PASS"}
            for name in review.REQUIRED
        ],
    }
    target.write_text(
        f"#!{sys.executable}\nimport pathlib,sys\n"
        f"pathlib.Path(sys.argv[sys.argv.index('--out')+1]).write_text({json.dumps(report)!r})\n"
    )
    target.chmod(0o755)
    search = target.parent
    if location == "symlink":
        search = tmp_path / "external-path"
        search.mkdir()
        (search / "specfact").symlink_to(target)
    monkeypatch.setenv("PATH", str(search))
    with pytest.raises(ValueError, match="project environment shadows external validator"):
        review.run(root, set())


@pytest.mark.parametrize("name", ["specfact", "actionlint", "openspec"])
def test_external_validator_resolution_and_repair(monkeypatch, tmp_path, name):
    from quality import external_tools

    root = tmp_path / "repo"
    root.mkdir()
    external = tmp_path / "external"
    external.mkdir()
    target = external / name
    target.write_text("#!/bin/sh\nexit 0\n")
    target.chmod(0o755)
    collision = root / name
    collision.symlink_to(target)
    monkeypatch.setenv("PATH", str(root))
    # A symlink outside the project resolves to the same absolute authority.
    assert external_tools.executable(root, name) == str(target)
    collision.unlink()
    collision.write_text("#!/bin/sh\nexit 0\n")
    collision.chmod(0o755)
    monkeypatch.setenv("PATH", str(root) + ":" + str(external))
    with pytest.raises(ValueError, match="project environment shadows"):
        external_tools.executable(root, name)
    # Repair removes the collision; there is no silent fallback while it exists.
    collision.unlink()
    assert external_tools.executable(root, name) == str(target)
    target.unlink()
    with pytest.raises(ValueError, match="external validator is unavailable"):
        external_tools.executable(root, name)


def test_spec_leaf_invokes_resolved_external_validator(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(runner.external_tools, "executable", lambda root, name: "/external/" + name)
    monkeypatch.setattr(
        runner.subprocess,
        "run",
        lambda args, **kwargs: calls.append(args) or subprocess.CompletedProcess(args, 0),
    )
    assert runner.leaf("spec", tmp_path, set(), {}) == []
    assert calls == [["/external/openspec", "validate", "--all", "--strict", "--no-interactive"]]


@pytest.mark.parametrize("options", ["test_safe.py", "-k test_safe"])
def test_required_suite_ignores_inherited_pytest_selection(monkeypatch, tmp_path, options):
    import os

    (tmp_path / "test_safe.py").write_text("def test_safe():\n    assert True\n")
    required = tmp_path / "test_required.py"
    required.write_text("def test_required():\n    assert False\n")
    monkeypatch.setenv("PYTEST_ADDOPTS", options)
    assert runner.leaf("tests", tmp_path, set(), {})
    required.write_text("def test_required():\n    assert True\n")
    assert runner.leaf("tests", tmp_path, set(), {}) == []
    assert os.environ["PYTEST_ADDOPTS"] == options


def test_tests_leaf_only_removes_addopts_from_child_environment(monkeypatch, tmp_path):
    import os

    monkeypatch.setenv("PYTEST_ADDOPTS", "-k selected")
    monkeypatch.setenv("CHANGECOST_TEST_ENV", "preserved")
    calls = []

    def capture(args, **kwargs):
        calls.append((args, kwargs.get("env")))
        return subprocess.CompletedProcess(args, 0)

    monkeypatch.setattr(runner.subprocess, "run", capture)
    assert runner.leaf("tests", tmp_path, set(), {}) == []
    assert calls[0][0] == [sys.executable, "-m", "pytest"]
    child = calls[0][1]
    assert child == {key: value for key, value in os.environ.items() if key != "PYTEST_ADDOPTS"}
    assert os.environ["PYTEST_ADDOPTS"] == "-k selected"
    assert runner.leaf("types", tmp_path, set(), {}) == []
    assert calls[1][1] is None
