"""Negative and repaired fixtures for the repository contracts."""

import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def gates():
    assert importlib.util.find_spec("quality.docs") is not None, "documentation gate is missing"
    from quality import docs, metadata, repository

    return docs, metadata, repository


@pytest.fixture
def sample(tmp_path):
    (tmp_path / "guide.md").write_text("# Guide\n\n[Source](source.py)\n")
    (tmp_path / "source.py").write_text("value = 1\n")
    mapping = {
        "documents": [
            {"path": "guide.md", "owner": "core", "sources": ["source.py"], "kind": "manual"}
        ],
        "immutable": {},
    }
    return tmp_path, mapping


def test_document_ownership_and_repairs(gates, sample):
    docs, _, _ = gates
    root, mapping = sample
    files = {"guide.md", "source.py"}
    assert docs.validate(root, files, mapping, {}, {}) == []
    (root / "extra.md").write_text("# Extra\n")
    assert "unowned" in " ".join(docs.validate(root, files | {"extra.md"}, mapping, {}, {}))
    mapping["documents"].append(
        {"path": "extra.md", "owner": "core", "sources": ["source.py"], "kind": "manual"}
    )
    assert docs.validate(root, files | {"extra.md"}, mapping, {}, {}) == []
    mapping["documents"][0]["sources"] = ["gone.py"]
    assert "source" in " ".join(docs.validate(root, files, mapping, {}, {}))


def test_broken_anchor_and_repaired_target(gates, sample):
    docs, _, _ = gates
    root, mapping = sample
    (root / "guide.md").write_text("# Guide\n[bad](guide.md#missing)\n")
    assert "reference" in " ".join(docs.validate(root, {"guide.md", "source.py"}, mapping, {}, {}))
    (root / "guide.md").write_text("# Guide\n[ok](guide.md#guide)\n")
    assert docs.validate(root, {"guide.md", "source.py"}, mapping, {}, {}) == []


def test_source_drift_requires_content_bound_rationale(gates, sample):
    docs, _, repo = gates
    root, mapping = sample
    before = {"source.py": b"value = 0\n", "guide.md": (root / "guide.md").read_bytes()}
    files = {"guide.md", "source.py"}
    assert "stale" in " ".join(docs.validate(root, files, mapping, before, {}))
    digest = repo.digest(root, {"source.py"})
    exceptions = {
        "guide.md": {"reason": "Value detail does not alter this guide.", "digest": digest}
    }
    assert docs.validate(root, files, mapping, before, exceptions) == []
    (root / "source.py").write_text("value = 2\n")
    assert "stale" in " ".join(docs.validate(root, files, mapping, before, exceptions))


def test_immutable_exception_checks_bytes(gates, sample):
    docs, _, _ = gates
    import hashlib

    root, mapping = sample
    (root / "original.md").write_text("# Original\n")
    mapping["immutable"]["original.md"] = {
        "sha256": hashlib.sha256((root / "original.md").read_bytes()).hexdigest(),
        "reason": "Original supplied research",
    }
    files = {"guide.md", "source.py", "original.md"}
    assert docs.validate(root, files, mapping, {}, {}) == []
    (root / "original.md").write_text("# Changed\n")
    assert "immutable" in " ".join(docs.validate(root, files, mapping, {}, {}))


def test_changelog_requires_new_substantive_entry(gates):
    _, metadata, _ = gates
    old = "# Changelog\n\n## Unreleased\n\n- Previous behavior.\n"
    assert metadata.changelog_errors(old, old)
    assert metadata.changelog_errors(old + "\n2026-09-28\n", old)
    assert metadata.changelog_errors(old.replace("Previous", "Previous"), old)
    assert (
        metadata.changelog_errors(
            old.replace("- Previous", "- Add offline version output.\n- Previous"), old
        )
        == []
    )


def test_version_conflicts_and_first_version(gates):
    _, metadata, _ = gates
    assert metadata.version_errors("0.1.0.dev0", None, ["0.1.0.dev0"] * 3) == []
    assert metadata.version_errors("0.1.0", "0.1.0", ["0.1.0"]) == []
    assert metadata.version_errors("0.1.0", "0.2.0", ["0.1.0"])
    assert metadata.version_errors("0.1.0", None, ["0.2.0"])


def test_missing_and_stale_generated_output(tmp_path):
    assert importlib.util.find_spec("quality.index") is not None, "index generator is missing"
    from quality.index import check_outputs

    output = {"llms.txt": "# Index\n"}
    assert check_outputs(tmp_path, output)
    (tmp_path / "llms.txt").write_text("# Index\n[broken](missing)\n")
    assert check_outputs(tmp_path, output)
    (tmp_path / "llms.txt").write_text(output["llms.txt"])
    assert check_outputs(tmp_path, output) == []
    assert (tmp_path / "llms.txt").read_text() == output["llms.txt"]


def test_review_missing_skipped_and_stale():
    assert importlib.util.find_spec("quality.review") is not None, "review evidence gate is missing"
    from quality.review import evidence_errors

    assert evidence_errors({}, "abc")
    assert evidence_errors({"digest": "old", "assurance_status": "PASS"}, "abc")
    assert evidence_errors({"digest": "abc", "assurance_status": "UNKNOWN"}, "abc")


def test_manifest_cannot_escape(gates, tmp_path):
    _, _, repo = gates
    with pytest.raises(ValueError):
        repo.safe_path(tmp_path, "../secret")


def test_real_index_is_current_and_offline():
    from quality.index import check_outputs, render

    root = Path(__file__).resolve().parents[1]
    first = render(root)
    assert render(root) == first
    assert check_outputs(root, first) == []


def test_generator_detects_changed_skill_and_duplicates(tmp_path):
    import shutil

    from quality.index import render

    root = Path(__file__).resolve().parents[1]
    shutil.copytree(root / ".agents", tmp_path / ".agents")
    (tmp_path / "quality").mkdir()
    (tmp_path / "quality/index.json").write_text("[]\n")
    first = render(tmp_path)
    skill = next((tmp_path / ".agents/skills").glob("*/SKILL.md"))
    skill.write_text(
        skill.read_text().replace("description:", "description: Changed description ", 1)
    )
    assert render(tmp_path) != first
    (tmp_path / ".agents/skills/duplicate").mkdir()
    shutil.copyfile(skill, tmp_path / ".agents/skills/duplicate/SKILL.md")
    with pytest.raises(ValueError, match="duplicate skill"):
        render(tmp_path)


def test_review_accepts_complete_native_profile():
    from quality.review import REQUIRED, evidence_errors

    report = {
        "digest": "abc",
        "assurance_status": "PASS",
        "overall_verdict": "PASS",
        "ci_exit_code": 0,
        "has_unknown_required_evidence": False,
        "analyzer_evidence": [
            {"id": n, "evidence_outcome": "PASS", "execution_state": "ran"} for n in REQUIRED
        ],
    }
    assert evidence_errors(report, "abc") == []
    report["analyzer_evidence"][0]["execution_state"] = "error"
    assert evidence_errors(report, "abc")


def test_explicit_manifest_includes_new_behavior(tmp_path):
    from quality.repository import git, inventory

    git(tmp_path, "init", "-q")
    (tmp_path / "pyproject.toml").write_text("[project]\n")
    with pytest.raises(ValueError, match="manifest"):
        inventory(tmp_path)
    manifest = tmp_path / "manifest.txt"
    manifest.write_text("pyproject.toml\n")
    assert inventory(tmp_path, manifest) == {"pyproject.toml"}


def test_archive_rejects_private_sentinels():
    from quality.build import archive_errors

    assert archive_errors(["x/LICENSE", "x/artifacts/billing.csv"])
    assert archive_errors(["x/LICENSE", "x/.specfact/report.json"])
    assert archive_errors(["x/LICENSE", "x/.env"])
    assert archive_errors(["x/LICENSE", "x/changecost/__init__.py"]) == []


def test_date_only_doc_change_cannot_satisfy_source_drift(gates, sample):
    docs, _, _ = gates
    root, mapping = sample
    (root / "guide.md").write_text("# Guide\nReviewed 2026-09-28\n")
    before = {"source.py": b"value = 0\n", "guide.md": b"# Guide\nReviewed 2026-09-27\n"}
    assert "stale" in " ".join(docs.validate(root, {"source.py", "guide.md"}, mapping, before, {}))


def test_changelog_date_only_entry_edit_is_insufficient(gates):
    _, metadata, _ = gates
    old = "# Changelog\n\n## Unreleased\n\n- Review source evidence on 2026-09-27.\n"
    assert metadata.changelog_errors(old.replace("2026-09-27", "2026-09-28"), old)


def test_aggregate_runs_required_children_and_propagates_failure(monkeypatch, tmp_path):
    from quality import __main__ as runner

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(runner, "baseline", lambda *_: ("base", {}))
    monkeypatch.setattr(runner, "inventory", lambda *_: set())
    monkeypatch.setattr(runner, "git", lambda *_: b"head")
    calls = []

    def check(name, *_):
        calls.append(name)
        return ["required test failed"] if name == "tests" else []

    monkeypatch.setattr(runner, "leaf", check)
    import sys

    monkeypatch.setattr(sys, "argv", ["quality", "check", "--base", "base"])
    assert runner.main() == 1
    assert set(calls) == {
        "lock",
        "hygiene",
        "lint",
        "types",
        "docs",
        "index",
        "metadata",
        "workflow",
        "tests",
        "build",
        "audit",
        "review",
        "spec",
    }


def test_workflow_syntax_failure_is_propagated(monkeypatch, tmp_path):
    import shutil
    import subprocess

    from quality import workflow

    root = Path(__file__).resolve().parents[1]
    shutil.copytree(root / ".github", tmp_path / ".github")
    syntax_exit = 0

    def actionlint(args, **kwargs):
        return subprocess.CompletedProcess(
            args, 0 if "--version" in args else syntax_exit, stdout="1.7.12\n"
        )

    monkeypatch.setattr(workflow.subprocess, "run", actionlint)
    assert workflow.validate(tmp_path) == []
    syntax_exit = 1
    assert workflow.validate(tmp_path) == ["workflow syntax validation failed"]
    syntax_exit = 0
    assert workflow.validate(tmp_path) == []


def test_advisory_outage_never_passes(monkeypatch, tmp_path):
    import subprocess

    from quality import audit

    (tmp_path / "uv.lock").write_text("package = []\n")
    (tmp_path / ".changecost").mkdir()
    monkeypatch.setattr(audit, "licenses", lambda _: [])
    monkeypatch.setattr(audit.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 1))
    assert audit.run(tmp_path)


def test_stale_native_report_is_not_reused(monkeypatch, tmp_path):
    import json
    import subprocess

    from quality import review

    (tmp_path / ".specfact").mkdir()
    old = tmp_path / ".specfact/code-review.json"
    old.write_text(json.dumps({"assurance_status": "PASS"}))
    monkeypatch.setattr(review.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 1))
    assert review.run(tmp_path, set()) == ["SpecFact produced no review report"]


def test_changelog_exception_is_bound_and_editorial_only(tmp_path):
    from quality.metadata import validate
    from quality.repository import digest

    (tmp_path / "pyproject.toml").write_text('[project]\nname="x"\nversion="0.1.0"\n')
    (tmp_path / "uv.lock").write_text('[[package]]\nname="x"\nversion="0.1.0"\n')
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n\n## Unreleased\n")
    (tmp_path / "guide.md").write_text("# Guide\nOriginal prose.\n")
    files = {"pyproject.toml", "uv.lock", "CHANGELOG.md", "guide.md"}
    before = {n: (tmp_path / n).read_bytes() for n in files}
    (tmp_path / "guide.md").write_text("# Guide\nCorrected prose.\n")
    assert validate(tmp_path, files, before, {})
    exception = {
        "changelog": {
            "reason": "Editorial correction only",
            "digest": digest(tmp_path, {"guide.md"}),
        }
    }
    assert validate(tmp_path, files, before, exception) == []
    (tmp_path / "guide.md").write_text("# Guide\nDifferent scope.\n")
    assert validate(tmp_path, files, before, exception)


def test_workflow_cannot_hide_required_check():
    import yaml

    from quality.workflow import wiring_errors

    root = Path(__file__).resolve().parents[1]
    config = yaml.load((root / ".github/workflows/quality.yml").read_text(), Loader=yaml.BaseLoader)
    assert wiring_errors(config) == []
    step = next(
        step for step in config["jobs"]["quality"]["steps"] if step.get("run") == "make check"
    )
    step["if"] = "${{ github.event_name == 'workflow_dispatch' }}"
    assert wiring_errors(config)
    del step["if"]
    assert wiring_errors(config) == []


def test_generator_tracks_command_tree_and_options(monkeypatch, tmp_path):
    import typer

    from quality import index

    (tmp_path / "quality").mkdir()
    (tmp_path / "quality/index.json").write_text("[]\n")
    app = typer.Typer()

    @app.callback()
    def root():
        pass

    @app.command()
    def inspect(verbose: bool = False):
        pass

    monkeypatch.setattr(index, "app", app)
    output = index.render(tmp_path)["docs/commands.md"]
    assert "changecost inspect" in output
    assert "--verbose" in output


def test_review_activates_every_required_member(monkeypatch, tmp_path):
    """Mirror the pinned native profile's conditional semgrep-bugs evidence."""
    import json
    import subprocess

    from quality import review

    def native_run(args, **kwargs):
        entries = [
            {"id": name, "execution_state": "ran", "evidence_outcome": "PASS"}
            for name in review.REQUIRED
        ]
        if "--bug-hunt" not in args:
            member = next(item for item in entries if item["id"] == "semgrep-bugs")
            member.update(execution_state="not_applicable", evidence_outcome="NOT_APPLICABLE")
        report = {
            "assurance_status": "PASS",
            "overall_verdict": "PASS",
            "ci_exit_code": 0,
            "has_unknown_required_evidence": False,
            "analyzer_evidence": entries,
        }
        Path(args[args.index("--out") + 1]).write_text(json.dumps(report))
        return subprocess.CompletedProcess(args, 0)

    monkeypatch.setattr(review.subprocess, "run", native_run)
    assert review.run(tmp_path, set()) == []
