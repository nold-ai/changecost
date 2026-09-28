"""Explicit repository inputs and immutable comparison snapshots."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path


def git(root: Path, *args: str) -> bytes:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=False)
    if result.returncode:
        raise ValueError(result.stderr.decode().strip())
    return result.stdout


def safe_path(root: Path, name: str) -> Path:
    path = root / name
    if Path(name).is_absolute() or ".." in Path(name).parts or path.is_symlink():
        raise ValueError(f"unsafe repository path: {name}")
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"path escapes repository: {name}")
    return path


def checked_names(names: set[str]) -> set[str]:
    """Reject current root-relative filenames that downstream hooks parse as options."""
    for name in sorted(names):
        parts = Path(name).parts
        if parts and parts[0].startswith("-"):
            raise ValueError(f"option-shaped repository path must be renamed: {name}")
    return names


def inventory(root: Path, manifest: Path | None = None) -> set[str]:
    names = set(git(root, "ls-files", "-z").decode().strip("\0").split("\0")) - {""}
    untracked = git(root, "ls-files", "--others", "--exclude-standard", "-z").decode().strip("\0")
    if untracked and manifest is None:
        raise ValueError("untracked files require an explicit intended-file manifest (--manifest)")
    if manifest:
        for name in manifest.read_text().splitlines():
            if name:
                if not safe_path(root, name).is_file():
                    raise ValueError(f"manifest entry is not a file: {name}")
                names.add(name)
    return checked_names({name for name in names if safe_path(root, name).is_file()})


def baseline(root: Path, ref: str) -> tuple[str, dict[str, bytes]]:
    if not ref or ref.startswith("-"):
        raise ValueError("an explicit comparison base is required")
    sha = git(root, "rev-parse", "--verify", f"{ref}^{{commit}}").decode().strip()
    names = git(root, "ls-tree", "-r", "--name-only", "-z", sha).decode().split("\0")
    return sha, {name: git(root, "show", f"{sha}:{name}") for name in names if name}


def changed(root: Path, files: set[str], before: dict[str, bytes]) -> set[str]:
    return {
        name
        for name in files | before.keys()
        if (safe_path(root, name).read_bytes() if name in files else None) != before.get(name)
    }


def digest(root: Path, files: set[str]) -> str:
    """Bind both path identity and current content, including explicit deletions."""
    value = hashlib.sha256()
    for name in sorted(files):
        path = safe_path(root, name)
        content = path.read_bytes() if path.is_file() else b"<deleted>"
        value.update(name.encode() + b"\0" + hashlib.sha256(content).digest())
    return value.hexdigest()


def materialize_index(root: Path, destination: Path) -> set[str]:
    """Read index blobs directly; never stash, stage or rewrite user files."""
    names: set[str] = set()
    for record in git(root, "ls-files", "--stage", "-z").split(b"\0"):
        if not record:
            continue
        metadata, raw_name = record.split(b"\t", 1)
        mode, oid, stage = metadata.decode().split()
        name = raw_name.decode()
        checked_names({name})
        if stage != "0" or mode not in {"100644", "100755"}:
            raise ValueError(f"unmerged or unsupported index entry: {name}")
        path = safe_path(destination, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(git(root, "cat-file", "blob", oid))
        path.chmod(0o755 if mode == "100755" else 0o644)
        names.add(name)
    return names
