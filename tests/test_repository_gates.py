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


@pytest.mark.parametrize("verdict", ["PASS", "PASS_WITH_ADVISORY"])
def test_review_accepts_complete_native_profile(verdict):
    from quality.review import REQUIRED, evidence_errors

    report = {
        "digest": "abc",
        "assurance_status": "PASS",
        "overall_verdict": verdict,
        "enforcement_mode": "full",
        "ci_exit_code": 0,
        "has_unknown_required_evidence": False,
        "analyzer_evidence": [
            {"id": n, "evidence_outcome": "PASS", "execution_state": "ran"} for n in REQUIRED
        ],
    }
    assert evidence_errors(report, "abc") == []
    adverse = {
        "digest": "old",
        "assurance_status": "UNKNOWN",
        "overall_verdict": "FAIL",
        "ci_exit_code": 1,
        "has_unknown_required_evidence": True,
        "analyzer_evidence": [],
    }
    for field, value in adverse.items():
        assert evidence_errors({**report, field: value}, "abc")
    report["analyzer_evidence"][0]["evidence_outcome"] = "UNKNOWN"
    assert evidence_errors(report, "abc")
    report["analyzer_evidence"][0]["evidence_outcome"] = "PASS"
    for state in ("error", "skipped"):
        report["analyzer_evidence"][0]["execution_state"] = state
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

    monkeypatch.setattr(
        workflow.external_tools, "executable", lambda root, name: "/external/" + name
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
    monkeypatch.setattr(review.external_tools, "executable", lambda root, name: "/external/" + name)
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
        step
        for step in config["jobs"]["quality"]["steps"]
        if step.get("name") == "Check repository"
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
        Path(args[args.index("--out") + 1]).write_text(json.dumps(report), encoding="utf-8")
        return subprocess.CompletedProcess(args, 0)

    monkeypatch.setattr(review.external_tools, "executable", lambda root, name: "/external/" + name)
    monkeypatch.setattr(review.subprocess, "run", native_run)
    assert review.run(tmp_path, set()) == []


def test_openspec_configuration_change_requires_review(monkeypatch, tmp_path):
    from quality import __main__ as runner

    name = "openspec/config.yaml"
    policy = tmp_path / name
    policy.parent.mkdir()
    before = {name: b"schema: spec-driven\ncontext: Require strict validation.\n"}
    policy.write_text("schema: spec-driven\ncontext: Validation is optional.\n")
    calls = []
    monkeypatch.setattr(runner.review, "run", lambda *args: calls.append(args) or ["UNKNOWN"])
    assert runner.leaf("review", tmp_path, {name}, before) == ["UNKNOWN"]
    assert len(calls) == 1
    policy.write_bytes(before[name])
    assert runner.leaf("review", tmp_path, {name}, before) == []
    assert len(calls) == 1


def test_hygiene_policy_change_requires_review(monkeypatch, tmp_path):
    from quality import __main__ as runner

    policy = tmp_path / ".pre-commit-hygiene.yaml"
    policy.write_text("repos: []\n")
    before = {policy.name: b"repos:\n- hooks:\n  - id: detect-private-key\n"}
    calls = []
    monkeypatch.setattr(runner.review, "run", lambda *args: calls.append(args) or ["UNKNOWN"])
    assert runner.leaf("review", tmp_path, {policy.name}, before) == ["UNKNOWN"]
    assert len(calls) == 1


@pytest.mark.parametrize("invalid", ["new-typo.py", "directory"])
def test_manifest_rejects_missing_files_and_directories(tmp_path, invalid):
    from quality.repository import git, inventory

    git(tmp_path, "init", "-q")
    (tmp_path / "new.py").write_text("invalid syntax!\n")
    (tmp_path / "directory").mkdir()
    manifest = tmp_path / "manifest.txt"
    manifest.write_text(invalid + "\n")
    with pytest.raises(ValueError, match="manifest entry is not a file"):
        inventory(tmp_path, manifest)
    manifest.write_text("new.py\n")
    assert inventory(tmp_path, manifest) == {"new.py"}


def test_workflow_requires_scoped_capsule_prerequisite():
    import copy

    import yaml

    from quality.workflow import wiring_errors

    root = Path(__file__).resolve().parents[1]
    config = yaml.load((root / ".github/workflows/quality.yml").read_text(), Loader=yaml.BaseLoader)
    assert wiring_errors(config) == []
    missing = copy.deepcopy(config)
    job = missing["jobs"]["quality"]
    job["steps"] = [step for step in job["steps"] if step.get("id") != "capsule-userns"]
    assert "capsule namespace setup is missing or can be skipped" in wiring_errors(missing)
    wrong_runner = copy.deepcopy(config)
    wrong_runner["jobs"]["quality"]["runs-on"] = "ubuntu-latest"
    assert "capsule prerequisite requires the reviewed Ubuntu 24.04 runner" in wiring_errors(
        wrong_runner
    )
    wrong_cache = copy.deepcopy(config)
    setup = next(
        step
        for step in wrong_cache["jobs"]["quality"]["steps"]
        if step.get("id") == "capsule-userns"
    )
    setup["env"]["SPECFACT_CODE_REVIEW_CAPSULE_CACHE"] = "/tmp/unrelated"
    assert "capsule cache must match the job-local AppArmor attachment" in wiring_errors(
        wrong_cache
    )


@pytest.mark.parametrize("version", ["1.7.12", "v1.7.12", "1.7.11", "v1.7.120", "", "unknown"])
def test_workflow_validator_accepts_only_pinned_version(monkeypatch, tmp_path, version):
    import shutil
    import subprocess

    from quality import workflow

    root = Path(__file__).resolve().parents[1]
    shutil.copytree(root / ".github", tmp_path / ".github")
    calls = []

    def actionlint(args, **kwargs):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, stdout=version + "\n" if version else "")

    monkeypatch.setattr(
        workflow.external_tools, "executable", lambda root, name: "/external/" + name
    )
    monkeypatch.setattr(workflow.subprocess, "run", actionlint)
    errors = workflow.validate(tmp_path)
    if version in {"1.7.12", "v1.7.12"}:
        assert errors == []
        assert len(calls) == 2
    else:
        assert errors == ["actionlint 1.7.12 is required"]
        assert len(calls) == 1


def test_staged_hook_defaults_to_head_without_overriding_explicit_base(monkeypatch, tmp_path):
    import argparse
    import subprocess

    from quality import __main__ as runner

    monkeypatch.chdir(tmp_path)
    seen = []

    def snapshot(root, destination):
        (destination / "quality").mkdir()
        (destination / "quality/__main__.py").write_text("# staged runner\n")
        return {"quality/__main__.py"}

    def run(args, **kwargs):
        seen.append(args[args.index("--base") + 1])
        return subprocess.CompletedProcess(args, 7)

    monkeypatch.setattr(runner, "materialize_index", snapshot)
    monkeypatch.setattr(runner.subprocess, "run", run)
    assert runner.staged(argparse.Namespace(base="")) == 7
    assert runner.staged(argparse.Namespace(base="explicit-base")) == 7
    assert seen == ["HEAD", "explicit-base"]


@pytest.mark.parametrize("failed_command", ["uv", "probe"])
def test_lock_leaf_requires_real_host_probe(monkeypatch, tmp_path, failed_command):
    from quality import __main__ as runner

    calls = []

    def external(root, args):
        command = "uv" if args[0] == "uv" else "probe"
        calls.append(command)
        if command == "probe":
            assert args[-1] == "tests/tool_probes.py"
        return [command + " failed"] if command == failed_command else []

    monkeypatch.setattr(runner, "external", external)
    assert runner.leaf("lock", tmp_path, set(), {}) == [failed_command + " failed"]
    assert calls == ["uv", "probe"]


@pytest.mark.parametrize(
    "mutation",
    [
        "workflow-env",
        "job-env",
        "step-env",
        "resolver-script",
        "resolver-input",
        "resolver-head",
        "resolver-condition",
        "resolver-order",
        "later-write",
    ],
)
def test_workflow_rejects_comparison_base_bypass(mutation):
    import yaml

    from quality.workflow import wiring_errors

    root = Path(__file__).resolve().parents[1]
    config = yaml.load((root / ".github/workflows/quality.yml").read_text(), Loader=yaml.BaseLoader)
    assert wiring_errors(config) == []
    job = config["jobs"]["quality"]
    steps = job["steps"]
    resolver = next(step for step in steps if step.get("name") == "Resolve comparison base")
    check = next(step for step in steps if step.get("name") == "Check repository")
    overrides = {
        "workflow-env": (config, "env", {"BASE_REF": "HEAD"}),
        "job-env": (job["env"], "BASE_REF", "HEAD"),
        "step-env": (check, "env", {"BASE_REF": "HEAD"}),
        "resolver-script": (resolver, "run", 'echo "BASE_REF=HEAD" >> "$GITHUB_ENV"'),
        "resolver-input": (resolver["env"], "PR_BASE", "${{ github.event.pull_request.head.sha }}"),
        "resolver-condition": (resolver, "if", "false"),
        "resolver-head": (
            resolver["env"],
            "EXPECTED_HEAD",
            "${{ github.event.pull_request.base.sha }}",
        ),
    }
    if mutation in overrides:
        target, key, value = overrides[mutation]
        target[key] = value
    elif mutation == "resolver-order":
        steps.remove(resolver)
        steps.append(resolver)
    else:
        steps.insert(steps.index(check), {"run": 'echo "BASE_REF=HEAD" >> "$GITHUB_ENV"'})
    assert any("comparison" in error for error in wiring_errors(config))
    repaired = yaml.load(
        (root / ".github/workflows/quality.yml").read_text(), Loader=yaml.BaseLoader
    )
    assert wiring_errors(repaired) == []


@pytest.mark.parametrize("permissions", [{"contents": "write"}, "write-all", {"issues": "write"}])
@pytest.mark.parametrize("job_name", ["quality", "auxiliary"])
def test_workflow_jobs_cannot_override_read_only_permissions(permissions, job_name):
    import yaml

    from quality.workflow import security_errors

    root = Path(__file__).resolve().parents[1]
    config = yaml.load((root / ".github/workflows/quality.yml").read_text(), Loader=yaml.BaseLoader)
    job = config["jobs"].setdefault(
        job_name, {"runs-on": "ubuntu-24.04", "steps": [{"run": "true"}]}
    )
    assert security_errors(config) == []
    job["permissions"] = permissions
    assert any("contents: read permissions" in error for error in security_errors(config))
    job["permissions"] = {"contents": "read"}
    assert security_errors(config) == []


@pytest.mark.parametrize(
    ("section", "key", "value"),
    [
        ("with", "ref", "${{ github.event.pull_request.base.sha }}"),
        ("with", "fetch-depth", "1"),
        ("with", "persist-credentials", "true"),
        (None, "if", "false"),
        (None, "continue-on-error", "true"),
        (None, "uses", "actions/checkout@main"),
    ],
)
def test_workflow_rejects_checkout_drift(section, key, value):
    import copy

    import yaml

    from quality.workflow import wiring_errors

    root = Path(__file__).resolve().parents[1]
    config = yaml.load((root / ".github/workflows/quality.yml").read_text(), Loader=yaml.BaseLoader)
    steps = config["jobs"]["quality"]["steps"]
    original = copy.deepcopy(steps[0])
    target = steps[0][section] if section else steps[0]
    target[key] = value
    assert any("checkout" in error for error in wiring_errors(config))
    steps[0] = original
    assert wiring_errors(config) == []


@pytest.mark.parametrize("mutation", ["duplicate", "late"])
def test_workflow_requires_one_initial_checkout(mutation):
    import yaml

    from quality.workflow import wiring_errors

    root = Path(__file__).resolve().parents[1]
    config = yaml.load((root / ".github/workflows/quality.yml").read_text(), Loader=yaml.BaseLoader)
    steps = config["jobs"]["quality"]["steps"]
    checkout = steps[0]
    if mutation == "duplicate":
        steps.append(checkout)
    else:
        steps.remove(checkout)
        steps.append(checkout)
    assert any("checkout" in error for error in wiring_errors(config))
    steps.pop()
    if mutation == "late":
        steps.insert(0, checkout)
    assert wiring_errors(config) == []


@pytest.mark.parametrize("suffix", ["yml", "yaml"])
@pytest.mark.parametrize(
    "mutation", ["root-write", "root-write-all", "root-missing", "job-write", "event"]
)
def test_sibling_workflows_retain_security_policy(monkeypatch, tmp_path, suffix, mutation):
    import shutil
    import subprocess

    import yaml

    from quality import workflow

    root = Path(__file__).resolve().parents[1]
    shutil.copytree(root / ".github", tmp_path / ".github")
    monkeypatch.setattr(workflow.external_tools, "executable", lambda *args: "/external/actionlint")
    monkeypatch.setattr(
        workflow.subprocess,
        "run",
        lambda args, **kwargs: subprocess.CompletedProcess(args, 0, stdout="1.7.12\n"),
    )
    sibling = tmp_path / f".github/workflows/additional.{suffix}"
    config = {
        "on": "push",
        "permissions": {"contents": "read"},
        "jobs": {"inspect": {"runs-on": "ubuntu-24.04", "steps": [{"run": "true"}]}},
    }
    sibling.write_text(yaml.safe_dump(config))
    assert workflow.validate(tmp_path) == []
    job = config["jobs"]["inspect"]
    changes = {
        "root-write": (config, "permissions", {"contents": "write"}),
        "root-write-all": (config, "permissions", "write-all"),
        "root-missing": (config, "permissions", None),
        "job-write": (job, "permissions", {"contents": "write"}),
        "event": (config, "on", "pull_request_target"),
    }
    target, key, value = changes[mutation]
    previous = target.get(key)
    if value is None:
        del target[key]
    else:
        target[key] = value
    sibling.write_text(yaml.safe_dump(config))
    assert any(sibling.name in error for error in workflow.validate(tmp_path))
    target[key] = previous
    job["permissions"] = {"contents": "read"}
    sibling.write_text(yaml.safe_dump(config))
    assert workflow.validate(tmp_path) == []


@pytest.mark.parametrize("remove", ["all", "MAKEFLAGS", "GNUMAKEFLAGS", "MFLAGS"])
def test_workflow_requires_clean_make_environment(remove):
    import yaml

    from quality.workflow import wiring_errors

    root = Path(__file__).resolve().parents[1]
    config = yaml.load((root / ".github/workflows/quality.yml").read_text(), Loader=yaml.BaseLoader)
    job = config["jobs"]["quality"]
    check = next(step for step in job["steps"] if step.get("name") == "Check repository")
    required = "/usr/bin/env -u MAKEFLAGS -u GNUMAKEFLAGS -u MFLAGS /usr/bin/make check"
    assert check["run"] == required
    for scope in (config, job, check):
        scope.setdefault("env", {})["MAKEFLAGS"] = "-i"
    assert wiring_errors(config) == []
    check["run"] = "make check" if remove == "all" else required.replace(f"-u {remove} ", "")
    assert any("aggregate" in error for error in wiring_errors(config))
    check["run"] = required
    assert wiring_errors(config) == []


@pytest.mark.parametrize("name", ["--help", "-h", "./--help"])
def test_option_root_filename_cannot_bypass_hygiene(monkeypatch, tmp_path, name):
    from quality import __main__ as runner
    from quality.repository import git, inventory, materialize_index

    git(tmp_path, "init", "-q")
    (tmp_path / name).write_text("harmless fixture\n")
    git(tmp_path, "add", "--", name)
    calls = []
    monkeypatch.setattr(runner, "external", lambda *args: calls.append(args) or [])
    with pytest.raises(ValueError, match="option-shaped repository path"):
        inventory(tmp_path)
    with pytest.raises(ValueError, match="option-shaped repository path"):
        materialize_index(tmp_path, tmp_path / "snapshot")
    with pytest.raises(ValueError, match="option-shaped repository path"):
        runner.leaf("hygiene", tmp_path, {name}, {})
    assert calls == []
    git(tmp_path, "rm", "-f", "--", name)
    assert inventory(tmp_path) == set()
    assert materialize_index(tmp_path, tmp_path / "repaired") == set()
    assert runner.leaf("hygiene", tmp_path, set(), {name: b"harmless fixture\n"}) == []
    assert len(calls) == 1


@pytest.mark.parametrize("name", ["fixtures/--help", ".--help", "help.txt"])
def test_harmless_hyphen_paths_remain_valid(tmp_path, name):
    from quality.repository import git, inventory, materialize_index

    git(tmp_path, "init", "-q")
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("harmless fixture\n")
    git(tmp_path, "add", "--", name)
    assert inventory(tmp_path) == {name}
    assert materialize_index(tmp_path, tmp_path / "snapshot") == {name}


@pytest.mark.parametrize("scope", ["workflow", "job"])
@pytest.mark.parametrize(("field", "value"), [("shell", "python"), ("working-directory", "other")])
def test_quality_execution_defaults_reject_drift(scope, field, value):
    import copy

    import yaml

    from quality.workflow import wiring_errors

    root = Path(__file__).resolve().parents[1]
    config = yaml.load((root / ".github/workflows/quality.yml").read_text(), Loader=yaml.BaseLoader)
    target = config if scope == "workflow" else config["jobs"]["quality"]
    original = copy.deepcopy(target.get("defaults"))
    target.setdefault("defaults", {}).setdefault("run", {})[field] = value
    assert any("execution" in error for error in wiring_errors(config))
    if original is None:
        del target["defaults"]
    else:
        target["defaults"] = original
    assert wiring_errors(config) == []


def test_quality_execution_defaults_are_required():
    import yaml

    from quality.workflow import wiring_errors

    root = Path(__file__).resolve().parents[1]
    config = yaml.load((root / ".github/workflows/quality.yml").read_text(), Loader=yaml.BaseLoader)
    job = config["jobs"]["quality"]
    job.pop("defaults", None)
    assert any("execution" in error for error in wiring_errors(config))
    job["defaults"] = {
        "run": {
            "shell": "/bin/bash --noprofile --norc -p -e -o pipefail {0}",
            "working-directory": ".",
        }
    }
    assert wiring_errors(config) == []


@pytest.mark.parametrize(
    "step_name",
    [
        "Install pinned bootstrap tools",
        "Resolve comparison base",
        "Install locked project environment",
        "Install pinned review module",
        "Allow namespaces for this job's capsule launcher paths",
        "Check repository",
        "Remove job-local capsule profile",
    ],
)
@pytest.mark.parametrize(("field", "value"), [("shell", "python"), ("working-directory", "other")])
def test_quality_run_steps_reject_execution_overrides(step_name, field, value):
    import yaml

    from quality.workflow import wiring_errors

    root = Path(__file__).resolve().parents[1]
    config = yaml.load((root / ".github/workflows/quality.yml").read_text(), Loader=yaml.BaseLoader)
    step = next(
        step for step in config["jobs"]["quality"]["steps"] if step.get("name") == step_name
    )
    step[field] = value
    assert any("execution" in error for error in wiring_errors(config))
    step[field] = {
        "shell": "/bin/bash --noprofile --norc -p -e -o pipefail {0}",
        "working-directory": ".",
    }[field]
    assert wiring_errors(config) == []


def test_manual_dispatch_requires_distinct_comparison():
    import yaml

    from quality.workflow import wiring_errors

    root = Path(__file__).resolve().parents[1]
    config = yaml.load((root / ".github/workflows/quality.yml").read_text(), Loader=yaml.BaseLoader)
    step = next(
        step
        for step in config["jobs"]["quality"]["steps"]
        if step.get("name") == "Resolve comparison base"
    )
    guard = (
        'if test "$EVENT" = workflow_dispatch; then\n  test "$resolved" != "$EXPECTED_HEAD"\nfi\n'
    )
    assert guard in step["run"]
    original = step["run"]
    step["run"] = original.replace(guard, "")
    assert any("comparison" in error for error in wiring_errors(config))
    step["run"] = original
    assert wiring_errors(config) == []


@pytest.mark.parametrize("value", [None, "3.11.15", "3.13.14"])
def test_quality_interpreter_follows_matrix(value):
    import yaml

    from quality.workflow import wiring_errors

    root = Path(__file__).resolve().parents[1]
    config = yaml.load((root / ".github/workflows/quality.yml").read_text(), Loader=yaml.BaseLoader)
    env = config["jobs"]["quality"]["env"]
    if value is None:
        del env["UV_PYTHON"]
    else:
        env["UV_PYTHON"] = value
    assert any("interpreter" in error for error in wiring_errors(config))
    env["UV_PYTHON"] = "${{ matrix.python }}"
    assert wiring_errors(config) == []


@pytest.mark.parametrize("value", ["3.11.15", "3.13.14"])
def test_quality_steps_cannot_override_matrix_interpreter(value):
    import yaml

    from quality.workflow import wiring_errors

    root = Path(__file__).resolve().parents[1]
    config = yaml.load((root / ".github/workflows/quality.yml").read_text(), Loader=yaml.BaseLoader)
    for step in config["jobs"]["quality"]["steps"]:
        env = step.setdefault("env", {})
        env["UV_PYTHON"] = value
        assert any("interpreter" in error for error in wiring_errors(config))
        if "run" in step:
            env["UV_PYTHON"] = "${{ matrix.python }}"
        else:
            del env["UV_PYTHON"]
        assert wiring_errors(config) == []
        env["UV_PYTHON"] = "${{ matrix.python }}"
        assert wiring_errors(config) == []


@pytest.mark.parametrize("scope_name", ["workflow", "job", "steps"])
def test_quality_rejects_direct_path_overrides(scope_name):
    import yaml

    from quality.workflow import wiring_errors

    root = Path(__file__).resolve().parents[1]
    config = yaml.load((root / ".github/workflows/quality.yml").read_text(), Loader=yaml.BaseLoader)
    job = config["jobs"]["quality"]
    scopes = {"workflow": [config], "job": [job], "steps": job["steps"]}[scope_name]
    for scope in scopes:
        env = scope.setdefault("env", {})
        env["PATH"] = "/unreviewed/tool-directory"
        assert any("PATH" in error for error in wiring_errors(config))
        del env["PATH"]
        assert wiring_errors(config) == []


@pytest.mark.parametrize("command", ["env", "make"])
def test_quality_requires_absolute_aggregate_launchers(command):
    import yaml

    from quality.workflow import wiring_errors

    root = Path(__file__).resolve().parents[1]
    config = yaml.load((root / ".github/workflows/quality.yml").read_text(), Loader=yaml.BaseLoader)
    check = next(
        step
        for step in config["jobs"]["quality"]["steps"]
        if step.get("name") == "Check repository"
    )
    required = "/usr/bin/env -u MAKEFLAGS -u GNUMAKEFLAGS -u MFLAGS /usr/bin/make check"
    check["run"] = required.replace(f"/usr/bin/{command}", command)
    assert any("aggregate" in error for error in wiring_errors(config))
    check["run"] = required
    assert wiring_errors(config) == []


@pytest.mark.parametrize("scope", ["workflow", "job", "steps"])
@pytest.mark.parametrize(
    "remove", ["legacy", "/bin/", "--noprofile ", "--norc ", "-p ", "-e ", "-o pipefail ", "{0}"]
)
def test_quality_requires_canonical_bash_startup(scope, remove):
    import yaml

    from quality.workflow import wiring_errors

    root = Path(__file__).resolve().parents[1]
    config = yaml.load((root / ".github/workflows/quality.yml").read_text(), Loader=yaml.BaseLoader)
    job = config["jobs"]["quality"]
    required = "/bin/bash --noprofile --norc -p -e -o pipefail {0}"
    targets = [job["defaults"]["run"]]
    if scope == "workflow":
        config["defaults"] = {"run": dict(job["defaults"]["run"])}
        targets = [config["defaults"]["run"]]
    if scope == "steps":
        targets = [step for step in job["steps"] if "run" in step]
    for target in targets:
        target["shell"] = "bash" if remove == "legacy" else required.replace(remove, "")
        assert any("execution" in error for error in wiring_errors(config))
        target["shell"] = required
        assert wiring_errors(config) == []


@pytest.mark.parametrize("extra", ["include", "exclude", "platform"])
def test_quality_matrix_mapping_cannot_change_expansion(extra):
    import yaml

    from quality.workflow import wiring_errors

    root = Path(__file__).resolve().parents[1]
    config = yaml.load((root / ".github/workflows/quality.yml").read_text(), Loader=yaml.BaseLoader)
    matrix = config["jobs"]["quality"]["strategy"]["matrix"]
    matrix[extra] = ["other"] if extra == "platform" else [{"python": "3.13.14"}]
    assert any("matrix" in error for error in wiring_errors(config))
    del matrix[extra]
    assert wiring_errors(config) == []


@pytest.mark.parametrize("value", [None, "3.11.15", "3.13.14"])
def test_quality_run_steps_bind_interpreter_after_inherited_environment(value):
    import yaml

    from quality.workflow import wiring_errors

    root = Path(__file__).resolve().parents[1]
    config = yaml.load((root / ".github/workflows/quality.yml").read_text(), Loader=yaml.BaseLoader)
    for step in config["jobs"]["quality"]["steps"]:
        if "run" not in step:
            continue
        env = step.setdefault("env", {})
        env.pop("UV_PYTHON", None)
        if value is not None:
            env["UV_PYTHON"] = value
        assert any("interpreter" in error for error in wiring_errors(config))
        env["UV_PYTHON"] = "${{ matrix.python }}"
        assert wiring_errors(config) == []


def test_native_coverage_measures_product_and_quality_packages_only():
    import tomllib

    root = Path(__file__).resolve().parents[1]
    config = tomllib.loads((root / "pyproject.toml").read_text())

    assert config["tool"]["coverage"]["run"]["source_pkgs"] == ["changecost", "quality"]
    assert set(config["tool"]["coverage"]) == {"run"}
    assert config["tool"]["pytest"]["ini_options"]["testpaths"] == ["tests"]
    assert config["tool"]["pytest"]["ini_options"]["addopts"] == (
        "-ra -n 4 --dist load --maxschedchunk=1 --durations=25"
    )
