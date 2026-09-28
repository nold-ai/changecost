"""Required host-tool contracts; invoked by the lock leaf, outside capsule pytest."""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def check_locked_sync(tmp_path: Path) -> None:
    project = (
        '[project]\nname="lock-probe"\nversion="0.1.0"\nrequires-python=">=3.11"\ndependencies=[]\n'
    )
    (tmp_path / "pyproject.toml").write_text(project)
    args = ["uv", "lock", "--offline", "--no-python-downloads"]
    env = dict(os.environ, UV_PYTHON=sys.executable)
    missing = subprocess.run(
        [*args, "--check"], cwd=tmp_path, env=env, capture_output=True, check=False
    )
    assert missing.returncode != 0, (missing.stdout, missing.stderr)
    assert not (tmp_path / "uv.lock").exists()
    created = subprocess.run(
        args, cwd=tmp_path, env=env, check=False, capture_output=True, text=True
    )
    assert created.returncode == 0, created.stderr
    lock = (tmp_path / "uv.lock").read_bytes()
    drifted = project.replace('version="0.1.0"', 'version="0.2.0"')
    (tmp_path / "pyproject.toml").write_text(drifted)
    stale = subprocess.run(
        [*args, "--check"], cwd=tmp_path, env=env, capture_output=True, check=False
    )
    assert stale.returncode != 0, (stale.stdout, stale.stderr)
    assert (tmp_path / "uv.lock").read_bytes() == lock

    (tmp_path / "pyproject.toml").write_text(project)
    repaired = subprocess.run(
        [*args, "--check"], cwd=tmp_path, env=env, capture_output=True, check=False, text=True
    )
    assert repaired.returncode == 0, repaired.stderr
    assert (tmp_path / "uv.lock").read_bytes() == lock

    # The same drift resolves offline: only --check prevents the lock update.
    (tmp_path / "pyproject.toml").write_text(drifted)
    updated = subprocess.run(
        args, cwd=tmp_path, env=env, check=False, capture_output=True, text=True
    )
    assert updated.returncode == 0, updated.stderr
    assert (tmp_path / "uv.lock").read_bytes() != lock
    checked = subprocess.run(
        [*args, "--check"], cwd=tmp_path, env=env, check=False, capture_output=True, text=True
    )
    assert checked.returncode == 0, checked.stderr


def make_test_fixture(root: Path, target: Path) -> dict[str, str]:
    for name in ("Makefile", "pyproject.toml", "uv.lock", ".gitignore"):
        shutil.copy2(root / name, target / name)
    (target / "tests").mkdir()
    (target / "tests/test_safe.py").write_text("def test_safe():\n    assert True\n")
    (target / "tests/test_required.py").write_text("def test_required():\n    assert False\n")
    for args in (
        ["init", "-q"],
        ["add", "."],
        [
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@localhost",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-qm",
            "Fixture baseline",
        ],
    ):
        subprocess.run(["git", *args], cwd=target, check=True, capture_output=True)
    env = dict(
        os.environ,
        UV_PROJECT_ENVIRONMENT=sys.prefix,
        UV_NO_SYNC="1",
        UV_PYTHON=sys.executable,
        PYTHONPATH=str(root),
    )
    env.pop("BASE_REF", None)
    env.pop("MANIFEST", None)
    env.pop("PYTEST_ADDOPTS", None)
    return env


def check_make_test(tmp_path: Path) -> None:
    env = make_test_fixture(Path.cwd(), tmp_path)
    for selection in ("environment", "configuration"):
        if selection == "environment":
            env["PYTEST_ADDOPTS"] = "-k test_safe"
        else:
            env.pop("PYTEST_ADDOPTS")
            (tmp_path / "pytest.ini").write_text("[pytest]\naddopts = -k test_safe\n")
            subprocess.run(["git", "add", "pytest.ini"], cwd=tmp_path, check=True)
        failed = subprocess.run(
            ["make", "test"], cwd=tmp_path, env=env, capture_output=True, text=True, check=False
        )
        assert failed.returncode != 0, (selection, failed.stdout, failed.stderr)
        assert "test_required" in failed.stdout and "assert False" in failed.stdout, (
            selection,
            failed.stdout,
            failed.stderr,
        )
    (tmp_path / "tests/test_required.py").write_text("def test_required():\n    assert True\n")
    repaired = subprocess.run(
        ["make", "test"], cwd=tmp_path, env=env, capture_output=True, text=True, check=False
    )
    assert repaired.returncode == 0, (repaired.stdout, repaired.stderr)
    assert "2 passed" in repaired.stdout, repaired.stdout
    invalid = subprocess.run(
        ["make", "test", "BASE_REF=missing-comparison"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert invalid.returncode != 0 and "Needed a single revision" in invalid.stderr, invalid.stderr
    missing = subprocess.run(
        ["make", "test", "MANIFEST=missing-manifest"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert missing.returncode != 0 and "missing-manifest" in missing.stderr, missing.stderr


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="changecost-lock-proof-") as directory:
        check_locked_sync(Path(directory))
    print("Host uv missing/stale/repaired lock proof passed")
    with tempfile.TemporaryDirectory(prefix="changecost-make-test-proof-") as directory:
        check_make_test(Path(directory))
    print("Host make test selection/configuration/failure/repair and input proof passed")
