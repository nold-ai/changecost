"""Resolve external validators without accepting project-environment collisions."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def executable(root: Path, name: str) -> str:
    found = shutil.which(name)
    if found is None:
        raise ValueError(f"external validator is unavailable: {name}")
    target = Path(found).resolve()
    if target.is_relative_to(root.resolve()) or target.is_relative_to(Path(sys.prefix).resolve()):
        raise ValueError(f"project environment shadows external validator: {name}: {target}")
    return str(target)
