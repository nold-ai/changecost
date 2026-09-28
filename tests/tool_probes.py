"""Required host-tool contracts; invoked by the lock leaf, outside capsule pytest."""

import os
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


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="changecost-lock-proof-") as directory:
        check_locked_sync(Path(directory))
    print("Host uv missing/stale/repaired lock proof passed")
