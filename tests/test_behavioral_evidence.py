"""Scenario-derived packet freshness and affected-scope checks."""

import copy
import importlib
import importlib.util

import pytest

from quality import repository, review_session


def validator():
    assert importlib.util.find_spec("quality.behavioral_evidence"), "packet validator is missing"
    return importlib.import_module("quality.behavioral_evidence").validate_packet


@pytest.fixture
def packet(tmp_path):
    repository.git(tmp_path, "init", "-q")
    (tmp_path / ".gitignore").write_text(".changecost/\n")
    (tmp_path / "input.py").write_text("original\n")
    repository.git(tmp_path, "add", ".")
    repository.git(
        tmp_path,
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.com",
        "commit",
        "-qm",
        "base",
    )
    sha = repository.git(tmp_path, "rev-parse", "HEAD").decode().strip()
    inputs = {"input.py": review_session.file_fingerprint(tmp_path, "input.py")}
    review_session.initialize(
        tmp_path,
        "pilot",
        dict(
            repository="test/repo",
            requirements=["intent"],
            acceptance_criteria=["evidence"],
            non_goals=[],
            trust_boundary="local",
            intended_files=inputs,
            base=sha,
            head=sha,
            pr_base={"ref": "main", "sha": sha},
            required_reviewers=["reviewer"],
            required_checks=["tests"],
            required_statuses=[],
        ),
    )
    report = tmp_path / ".changecost/report.json"
    report.write_text('{"executed":true}\n')
    binding = review_session.packet(tmp_path, "pilot")["binding"]
    data = dict(
        schema_version=1,
        change_id="pilot",
        intent="selected behavior",
        invariants={"history": "append only"},
        trust_boundary="local",
        entrypoints=["public API"],
        assumptions={"clock": "UTC"},
        known_findings=[],
        binding=binding,
        inputs=inputs,
        input_roles={
            "specification": ["input.py"],
            "oracle": ["input.py"],
            "generator": ["input.py"],
            "configuration": ["input.py"],
        },
        dependencies={
            "input.py": {
                "invariants": ["history"],
                "assumptions": ["clock"],
                "review_scope": "behavior",
            }
        },
        evidence=[
            dict(
                id="tests",
                command="pytest",
                tool="pytest",
                version="9",
                required=True,
                applicable=True,
                outcome="pass",
                binding=binding,
                report=".changecost/report.json",
                report_sha256=review_session.file_fingerprint(tmp_path, ".changecost/report.json"),
                rationale="",
            )
        ],
    )
    return tmp_path, data


def test_current_packet_preserves_session_obligations(packet):
    root, data = packet
    result = validator()(root, data)
    assert result["evidence_status"] == "current"
    assert result["passed_required"] == ["tests"]
    assert result["session_status"]["action"] != "complete"


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(lambda root, data: (root / "input.py").write_text("changed\n"), id="source"),
        pytest.param(
            lambda root, data: (root / ".changecost/report.json").write_text("replaced\n"),
            id="report",
        ),
        pytest.param(
            lambda root, data: (root / ".changecost/report.json").unlink(), id="missing_report"
        ),
        pytest.param(lambda root, data: data["input_roles"].pop("oracle"), id="missing_role"),
        pytest.param(lambda root, data: data.update(dependencies={}), id="unmapped"),
        pytest.param(
            lambda root, data: data["evidence"][0].update(outcome="skipped"), id="skipped"
        ),
        pytest.param(lambda root, data: data["evidence"][0].update(binding={}), id="unbound"),
        pytest.param(
            lambda root, data: data["evidence"][0].update(
                applicable=False, rationale="not supported"
            ),
            id="not_applicable",
        ),
    ],
)
def test_changed_or_unusable_evidence_cannot_pass(packet, mutate):
    root, data = packet
    mutate(root, data)
    assert validator()(root, data)["evidence_status"] == "incomplete"


def test_delta_maps_assumptions_and_boundary_change_requires_broad_review(packet):
    root, data = packet
    previous = copy.deepcopy(data)
    previous["inputs"]["input.py"] = "0" * 64
    result = validator()(root, data, previous)
    assert result["changed_inputs"] == ["input.py"]
    assert result["affected_invariants"] == ["history"]
    assert result["affected_assumptions"] == ["clock"]
    assert not result["broader_review_required"]
    previous["entrypoints"] = ["different API"]
    assert validator()(root, data, previous)["broader_review_required"]


@pytest.mark.parametrize("bad", [None, {}, {"schema_version": True}])
def test_malformed_packets_are_controlled_incomplete(packet, bad):
    root, _ = packet
    assert validator()(root, bad)["evidence_status"] == "incomplete"


def test_unknown_dependency_and_unsafe_report_are_rejected(packet):
    root, data = packet
    (root / "new.py").write_text("new dependency")
    data["evidence"][0]["report"] = "../outside"
    result = validator()(root, data)
    assert result["evidence_status"] == "incomplete"
    assert result["broader_review_required"]


def test_staged_only_path_requires_dependency_coverage(packet):
    root, data = packet
    original = (root / ".gitignore").read_text()
    (root / ".gitignore").write_text(original + "another-ignore\n")
    repository.git(root, "add", ".gitignore")
    (root / ".gitignore").write_text(original)
    # A legitimate session covers the staged path, but the behavioral packet omits it.
    state = review_session.load(root, "pilot")
    manifest = dict(state["reviewed_manifest"])
    manifest[".gitignore"] = review_session.file_fingerprint(root, ".gitignore")
    review_session.record(
        root,
        "pilot",
        dict(
            id="staged-scope", kind="scope_decision", decision="approved", intended_files=manifest
        ),
    )
    review_session.record(
        root,
        "pilot",
        dict(
            id="staged-adopt",
            kind="advance_head",
            head=state["reviewed_head"],
            scope_decision_id="staged-scope",
        ),
    )
    binding = review_session.packet(root, "pilot")["binding"]
    data["binding"] = binding
    data["evidence"][0]["binding"] = binding
    result = validator()(root, data)
    assert result["evidence_status"] == "incomplete"
    assert ".gitignore" in result["changed_inputs"]
    assert result["broader_review_required"]


def test_ignored_packet_only_oracle_cannot_rebind_old_evidence(packet):
    root, data = packet
    name = ".changecost/oracle.py"
    (root / name).write_text("original oracle\n")
    data["inputs"][name] = review_session.file_fingerprint(root, name)
    data["input_roles"]["oracle"] = [name]
    data["dependencies"][name] = dict(
        invariants=["history"], assumptions=["clock"], review_scope="oracle"
    )
    # The recorded binding/report predates these changed bytes. Rehashing only the packet
    # must not turn that old execution into current evidence.
    (root / name).write_text("changed oracle\n")
    data["inputs"][name] = review_session.file_fingerprint(root, name)
    assert validator()(root, data)["evidence_status"] == "incomplete"


def test_initial_current_packet_requires_broad_review(packet):
    root, data = packet
    result = validator()(root, data)
    assert result["evidence_status"] == "current"
    assert result["broader_review_required"]


def test_foreign_previous_packet_cannot_authorize_narrow_review(packet):
    root, data = packet
    previous = copy.deepcopy(data)
    previous["change_id"] = "different-change"
    result = validator()(root, data, previous)
    assert result["evidence_status"] == "incomplete"
    assert result["broader_review_required"]
    assert any("same change" in error for error in result["errors"])


def test_matching_previous_packet_preserves_narrow_review(packet):
    root, data = packet
    result = validator()(root, data, copy.deepcopy(data))
    assert result["evidence_status"] == "current"
    assert not result["broader_review_required"]


@pytest.mark.parametrize("current", [[], ["replacement"]])
def test_prior_advisory_context_remains_inspectable(packet, current):
    root, data = packet
    prior = copy.deepcopy(data)
    prior["known_findings"] = ["earlier concern"]
    data["known_findings"] = current
    result = validator()(root, data, prior)
    assert result["evidence_status"] == "current"
    assert result["broader_review_required"]
    assert result["context_changes"]["known_findings"] == {
        "previous": ["earlier concern"],
        "current": current,
    }


@pytest.mark.parametrize(
    "field,value",
    [
        ("command", "different command"),
        ("tool", "different analyzer"),
        ("version", "10"),
        ("required", False),
        ("applicable", False),
        ("rationale", "changed applicability"),
        ("id", "renamed"),
    ],
)
def test_evidence_definition_changes_require_broader_review(packet, field, value):
    root, data = packet
    extra = copy.deepcopy(data["evidence"][0])
    extra.update(id="optional", required=False, rationale="diagnostic")
    data["evidence"].append(extra)
    prior = copy.deepcopy(data)
    extra[field] = value
    # Demotion uses a formerly required second analyzer while retaining the first.
    prior["evidence"][1]["required"] = field == "required"
    result = validator()(root, data, prior)
    assert result["evidence_status"] == "current"
    assert result["broader_review_required"]
    assert (
        result["context_changes"]["evidence_definitions"]["optional"]["previous"]["command"]
        == prior["evidence"][1]["command"]
    )


@pytest.mark.parametrize("required", [True, False])
def test_removed_evidence_definition_remains_inspectable(packet, required):
    root, data = packet
    prior = copy.deepcopy(data)
    extra = copy.deepcopy(data["evidence"][0])
    extra.update(id="removed", required=required, outcome="pass" if required else "unavailable")
    prior["evidence"].append(extra)
    result = validator()(root, data, prior)
    assert result["evidence_status"] == "current"
    assert result["broader_review_required"]
    change = result["context_changes"]["evidence_definitions"]["removed"]
    assert change["previous"]["required"] is required
    assert change["current"] is None


def test_same_definitions_execution_refresh_stays_narrow(packet):
    root, data = packet
    extra = copy.deepcopy(data["evidence"][0])
    extra.update(id="optional", required=False)
    data["evidence"].append(extra)
    data["known_findings"] = ["second", "first"]
    prior = copy.deepcopy(data)
    prior["known_findings"].reverse()
    prior["evidence"].reverse()
    prior["evidence"][0].update(
        outcome="unavailable", binding={}, report="old.json", report_sha256="0" * 64
    )
    result = validator()(root, data, prior)
    assert result["evidence_status"] == "current"
    assert not result["broader_review_required"]
    assert result["context_changes"] == {}
    data["evidence"][0]["outcome"] = "fail"
    assert validator()(root, data, prior)["evidence_status"] == "incomplete"


def test_advisory_changes_do_not_clear_session_findings(packet):
    root, data = packet
    review_session.record(root, "pilot", dict(id="open-finding", kind="finding", family="history"))
    prior = copy.deepcopy(data)
    prior["known_findings"] = ["advisory history note"]
    before = review_session.packet(root, "pilot")["unresolved_findings"]
    result = validator()(root, data, prior)
    assert result["session_findings"] == before
    assert review_session.packet(root, "pilot")["unresolved_findings"] == before
    assert result["context_changes"]["known_findings"]["previous"] == prior["known_findings"]


def test_added_evidence_definition_is_inspectable(packet):
    root, data = packet
    prior = copy.deepcopy(data)
    extra = copy.deepcopy(data["evidence"][0])
    extra.update(id="additional", required=False)
    data["evidence"].append(extra)
    result = validator()(root, data, prior)
    assert result["evidence_status"] == "current"
    assert result["broader_review_required"]
    change = result["context_changes"]["evidence_definitions"]["additional"]
    assert change["previous"] is None
    assert change["current"] == {
        "command": "pytest",
        "tool": "pytest",
        "version": "9",
        "required": False,
        "applicable": True,
        "rationale": "",
    }


@pytest.mark.parametrize("duplicate_prior", [False, True])
def test_duplicate_evidence_ids_cannot_collapse_policy(packet, duplicate_prior):
    root, data = packet
    prior = copy.deepcopy(data)
    target = prior if duplicate_prior else data
    target["evidence"].append(copy.deepcopy(target["evidence"][0]))
    result = validator()(root, data, prior)
    assert result["evidence_status"] == "incomplete"
    assert result["broader_review_required"]
    assert "unique evidence identities" in result["errors"][0]
