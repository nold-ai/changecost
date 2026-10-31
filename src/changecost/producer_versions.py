"""Strict producer version syntax shared by source admission boundaries."""

import re

_CORE = r"(0|[1-9][0-9]*)"
_LABEL = r"[0-9A-Za-z-]+"
_VERSION = re.compile(
    rf"{_CORE}\.{_CORE}\.{_CORE}"
    rf"(?:-({_LABEL}(?:\.{_LABEL})*))?"
    rf"(?:\+{_LABEL}(?:\.{_LABEL})*)?"
)


def _major(value: object) -> str | None:
    if not isinstance(value, str) or len(value) > 512:
        return None
    match = _VERSION.fullmatch(value)
    if match is None:
        return None
    prerelease = match.group(4)
    if prerelease is not None and any(
        label.isdecimal() and len(label) > 1 and label.startswith("0")
        for label in prerelease.split(".")
    ):
        return None
    return match.group(1)


def same_major(reported: object, observed: str) -> bool:
    """Accept complete valid versions of the baseline major without normalizing them."""
    major = _major(reported)
    return major is not None and major == _major(observed)
