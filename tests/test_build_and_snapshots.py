"""Actual Git index isolation and locked build failure probes."""

import pytest

from quality.repository import baseline, git, materialize_index


def test_index_preserves_staged_defect_and_user_files(tmp_path):
    git(tmp_path, "init", "-q")
    (tmp_path / "guide.md").write_text("[missing](new.md)\n")
    git(tmp_path, "add", "guide.md")
    (tmp_path / "guide.md").write_text("# Repaired only in worktree\n")
    (tmp_path / "new.md").write_text("# Untracked target\n")
    index_before = git(tmp_path, "ls-files", "--stage")
    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    files = materialize_index(tmp_path, snapshot)
    assert files == {"guide.md"}
    assert (snapshot / "guide.md").read_text() == "[missing](new.md)\n"
    from quality.docs import link_errors

    assert link_errors(snapshot, "guide.md", files)
    assert git(tmp_path, "ls-files", "--stage") == index_before
    assert (tmp_path / "guide.md").read_text() == "# Repaired only in worktree\n"
    git(tmp_path, "add", "guide.md", "new.md")
    assert materialize_index(tmp_path, snapshot) == {"guide.md", "new.md"}
    assert link_errors(snapshot, "guide.md", {"guide.md", "new.md"}) == []


def test_missing_comparison_history_fails(tmp_path):
    git(tmp_path, "init", "-q")
    with pytest.raises(ValueError):
        baseline(tmp_path, "missing-base")


def test_build_gate_exists():
    import importlib.util

    assert importlib.util.find_spec("quality.build") is not None, "isolated build gate is missing"
