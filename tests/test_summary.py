"""Untrusted summary data and final UTF-8 limits."""

import json

import pytest


def result(label):
    return {
        "schema": "changecost/check-v1",
        "status": "unknown",
        "record": {"kind": "quote", "record_id": label},
        "budget": {
            "amount": "15",
            "economic_kind": "monetary",
            "unit": "USD",
            "basis": "billed",
            "currency": "USD",
        },
        "comparison": None,
        "declared": [
            dict(amount=None, economic_kind="monetary", unit="USD", basis="billed", currency="USD")
            for _ in range(2)
        ],
        "scope": {
            "repository_id": "repo",
            "economic": {
                "economic_kind": "monetary",
                "unit": "USD",
                "basis": "billed",
                "currency": "USD",
            },
        },
        "cutoff": {"store_id": "local", "at": "2026-10-05T00:00:00Z", "sequence": 1},
        "provenance": "producer_assertion; provider_support_not_verified",
        "completeness": "unknown",
        "sample_count": 0,
        "quantile": "p90",
        "reasons": [label],
    }


@pytest.mark.parametrize("separator", ["\u2028", "\u2029"])
@pytest.mark.parametrize("existing", [False, True])
def test_unicode_linebreak_summary_console(tmp_path, separator, existing):
    import os
    import subprocess
    import sys

    source, destination = tmp_path / "result.json", tmp_path / "summary.md"
    value = result(f"label{separator}Status: over_budget世界")
    source.write_text(json.dumps(value))
    if existing:
        destination.write_text("previous\n")
    checked = subprocess.run(
        [sys.executable, "-m", "changecost.summary", str(source)],
        env=dict(os.environ, GITHUB_STEP_SUMMARY=str(destination)),
        capture_output=True,
        text=True,
        check=False,
    )
    assert checked.returncode == 0 and checked.stdout == "" and checked.stderr == ""
    rendered = destination.read_text()
    assert separator not in rendered
    assert f"\\u{ord(separator):04x}" in rendered and "世界" in rendered
    if existing:
        assert rendered.startswith("previous\n")


def test_summary_escapes_and_unicode(tmp_path):
    from changecost.summary import render_summary, write_summary

    label = "$(touch pwned) <img src=x> [link](https://evil) ::error::\x1b[31m\n世界"
    output = render_summary(result(label))
    assert "<img" not in output and "\x1b" not in output
    assert "[link](https://evil)" not in output
    assert "世界" in output
    target = tmp_path / "summary"
    write_summary(result(label), target)
    assert target.read_text() == output
    assert not (tmp_path / "pwned").exists()


def test_summary_truncation():
    from changecost.summary import render_summary

    output = render_summary(result("世界&[" * 50000))
    assert len(output.encode()) <= 65536
    assert "truncated" in output.lower()
    assert output.encode().decode() == output


@pytest.mark.parametrize("payload", [{}, {"schema": "other"}, result("ok") | {"status": "other"}])
def test_summary_invalid(payload):
    from changecost.summary import render_summary

    with pytest.raises(ValueError):
        render_summary(payload)


def test_summary_write_error(tmp_path):
    from changecost.summary import write_summary

    with pytest.raises(OSError):
        write_summary(result("ok"), tmp_path)


@pytest.mark.parametrize(
    "mutation",
    [
        {"budget": {"amount": "NaN"}},
        {"comparison": {"amount": []}},
        {"status": "within_budget"},
        {"provenance": []},
        {"sample_count": True},
    ],
)
def test_summary_strict_machine_contract(mutation):
    from changecost.summary import render_summary

    with pytest.raises(ValueError):
        render_summary(result("ok") | mutation)


def test_advisory_does_not_mask_workflow_failure():
    from pathlib import Path

    import yaml

    from changecost.summary import render_summary
    from quality.workflow import security_errors

    config = yaml.load(Path(".github/workflows/advisory.yml").read_text(), Loader=yaml.BaseLoader)
    assert set(config["on"]) == {"workflow_dispatch"}
    assert security_errors(config) == []
    bad = config | {"permissions": {"contents": "write"}}
    assert render_summary(result("valid advice"))
    assert security_errors(bad) == ["workflow must declare contents: read permissions"]
    assert security_errors(config) == []
    for job in config["jobs"].values():
        assert not job.get("continue-on-error")
        for step in job["steps"]:
            assert not step.get("continue-on-error")
            assert "|| true" not in step.get("run", "")
            assert "${{" not in step.get("run", "")


def test_renderer_technical_failures_subprocess(tmp_path):
    import os
    import subprocess
    import sys

    payload = tmp_path / "result.json"
    payload.write_text(json.dumps(result("valid")))
    destination = tmp_path / "summary"
    command = [sys.executable, "-m", "changecost.summary", str(payload)]
    env = dict(os.environ, GITHUB_STEP_SUMMARY=str(destination))
    successful = subprocess.run(command, env=env, capture_output=True, text=True)
    assert successful.returncode == 0 and not successful.stdout
    payload.write_text('{"schema":"unsupported"}')
    rejected = subprocess.run(command, env=env, capture_output=True, text=True)
    assert rejected.returncode == 2 and not rejected.stdout
    assert "unsupported" not in rejected.stderr
    payload.write_text(json.dumps(result("valid")))
    unwritable = subprocess.run(
        command, env=dict(env, GITHUB_STEP_SUMMARY=str(tmp_path)), capture_output=True
    )
    assert unwritable.returncode == 2 and not unwritable.stdout


def verified_result(kind, status):
    value = result("verified")
    value.update(
        status=status,
        record={"kind": kind, "record_id": "verified"},
        comparison=value["budget"] | {"amount": "10" if status == "within_budget" else "20"},
        cutoff={"store_id": "local", "at": "2026-10-05T00:00:00Z", "sequence": 1},
        provenance="locally_reproduced_synthetic; provider_support_not_verified",
        completeness="complete",
        quantile="p90" if kind == "quote" else None,
        sample_count=1 if kind == "quote" else None,
        reasons=[],
    )
    value["declared"] = (
        [value["comparison"] | {"amount": "0"}, dict(value["comparison"])]
        if kind == "quote"
        else [value["comparison"] | {"unknown_count": 0}]
    )
    return value


@pytest.mark.parametrize(
    "kind,status", [("quote", "over_budget"), ("computed_settlement", "within_budget")]
)
@pytest.mark.parametrize("existing", [False, True])
def test_numeric_summary_process_success(tmp_path, kind, status, existing):
    import os
    import subprocess
    import sys

    payload, destination = tmp_path / "result.json", tmp_path / "summary"
    payload.write_text(json.dumps(verified_result(kind, status)))
    if existing:
        destination.write_text("previous\n")
    checked = subprocess.run(
        [sys.executable, "-m", "changecost.summary", str(payload)],
        env=dict(os.environ, GITHUB_STEP_SUMMARY=str(destination)),
        capture_output=True,
        text=True,
        check=False,
    )
    assert checked.returncode == 0 and checked.stdout == "" and checked.stderr == ""
    rendered = destination.read_text()
    expected_status = {"over_budget": "over&#95;budget", "within_budget": "within&#95;budget"}[
        status
    ]
    expected_kind = {"quote": "quote", "computed_settlement": "computed&#95;settlement"}[kind]
    assert f"Status: {expected_status}" in rendered and f"kind: {expected_kind}" in rendered
    if existing:
        assert rendered.startswith("previous\n")


@pytest.mark.parametrize("kind", ["quote", "computed_settlement"])
@pytest.mark.parametrize("status", ["within_budget", "over_budget"])
def test_summary_rejects_legacy_numeric_authority(kind, status):
    from changecost.summary import render_summary

    value = verified_result(kind, status)
    assert render_summary(value)
    value["record"]["kind"] = "settlement"
    with pytest.raises(ValueError):
        render_summary(value)


def test_summary_accepts_legacy_unknown():
    from changecost.summary import render_summary

    value = result("legacy")
    value["record"]["kind"] = "settlement"
    value["quantile"] = None
    value["sample_count"] = None
    value["scope"] = "legacy"
    value["cutoff"] = None
    assert render_summary(value)


@pytest.mark.parametrize("kind", ["quote", "computed_settlement"])
@pytest.mark.parametrize("status", ["within_budget", "over_budget"])
@pytest.mark.parametrize("existing", [False, True])
def test_legacy_numeric_cli_preserves_summary(tmp_path, kind, status, existing):
    import os
    import subprocess
    import sys

    value = verified_result(kind, status)
    value["record"]["kind"] = "settlement"
    payload = tmp_path / "result.json"
    payload.write_text(json.dumps(value))
    destination = tmp_path / "summary"
    original = b"Earlier summary: \xe4\xb8\x96\xe7\x95\x8c\n"
    if existing:
        destination.write_bytes(original)
    rejected = subprocess.run(
        [sys.executable, "-m", "changecost.summary", str(payload)],
        env=dict(os.environ, GITHUB_STEP_SUMMARY=str(destination)),
        capture_output=True,
        text=True,
    )
    assert rejected.returncode == 2
    assert rejected.stdout == ""
    assert rejected.stderr == "cannot render or write advisory summary\n"
    if existing:
        assert destination.read_bytes() == original
    else:
        assert not destination.exists()


@pytest.mark.parametrize(
    "field,malformed",
    [
        (field, malformed)
        for field in ("status", "record_kind", "quantile", "completeness")
        for malformed in (["private-canary"], {"private-canary": "secret"}, True, 0)
    ]
    + [(field, None) for field in ("status", "record_kind", "completeness")],
)
@pytest.mark.parametrize("existing", [False, True])
def test_summary_malformed_enum_safe_cli(tmp_path, field, malformed, existing):
    import os
    import subprocess
    import sys

    value = result("valid")
    if field == "record_kind":
        value["record"]["kind"] = malformed
    else:
        value[field] = malformed
    payload = tmp_path / "result.json"
    payload.write_text(json.dumps(value))
    destination = tmp_path / "summary"
    original = b"Earlier advisory summary\n"
    if existing:
        destination.write_bytes(original)
    rejected = subprocess.run(
        [sys.executable, "-m", "changecost.summary", str(payload)],
        env=dict(os.environ, GITHUB_STEP_SUMMARY=str(destination)),
        capture_output=True,
        text=True,
    )
    assert rejected.returncode == 2
    assert rejected.stdout == ""
    assert rejected.stderr == "cannot render or write advisory summary\n"
    assert "private-canary" not in rejected.stderr
    if existing:
        assert destination.read_bytes() == original
    else:
        assert not destination.exists()


@pytest.mark.parametrize("existing", [False, True])
def test_summary_deep_json_safe_cli(tmp_path, existing):
    import os
    import subprocess
    import sys

    payload = tmp_path / "result.json"
    payload.write_text("[" * 12000 + "0" + "]" * 12000)
    destination = tmp_path / "summary"
    original = b"Earlier advisory summary\n"
    if existing:
        destination.write_bytes(original)
    rejected = subprocess.run(
        [sys.executable, "-m", "changecost.summary", str(payload)],
        env=dict(os.environ, GITHUB_STEP_SUMMARY=str(destination)),
        capture_output=True,
        text=True,
    )
    assert rejected.returncode == 2 and rejected.stdout == ""
    assert rejected.stderr == "cannot render or write advisory summary\n"
    if existing:
        assert destination.read_bytes() == original
    else:
        assert not destination.exists()


@pytest.mark.parametrize("field", ["provenance", "completeness"])
@pytest.mark.parametrize("existing", [False, True])
def test_summary_unsupported_authority_values(tmp_path, field, existing):
    import os
    import subprocess
    import sys

    value = result("ok")
    value["provenance"] = "producer_assertion; provider_support_not_verified"
    value[field] = "unsupported-private-authority"
    payload = tmp_path / "result.json"
    payload.write_text(json.dumps(value))
    destination = tmp_path / "summary"
    original = b"Earlier advisory summary\n"
    if existing:
        destination.write_bytes(original)
    checked = subprocess.run(
        [sys.executable, "-m", "changecost.summary", str(payload)],
        env=dict(os.environ, GITHUB_STEP_SUMMARY=str(destination)),
        capture_output=True,
        text=True,
    )
    assert checked.returncode == 2 and checked.stdout == ""
    assert checked.stderr == "cannot render or write advisory summary\n"
    if existing:
        assert destination.read_bytes() == original
    else:
        assert not destination.exists()


@pytest.mark.parametrize("existing", [False, True])
@pytest.mark.parametrize("claim", ["producer_complete", "local_missing_cutoff", "legacy_local"])
def test_summary_impossible_authority_combinations(tmp_path, claim, existing):
    import os
    import subprocess
    import sys

    value = result("ok")
    value["provenance"] = "producer_assertion; provider_support_not_verified"
    if claim == "producer_complete":
        value["completeness"] = "complete"
    else:
        value["provenance"] = "locally_reproduced_synthetic; provider_support_not_verified"
    if claim == "local_missing_cutoff":
        value["cutoff"] = None
    if claim == "legacy_local":
        value["record"]["kind"] = "settlement"
        value["cutoff"] = verified_result("quote", "within_budget")["cutoff"]
    payload = tmp_path / "result.json"
    payload.write_text(json.dumps(value))
    destination = tmp_path / "summary"
    original = b"Earlier advisory summary\n"
    if existing:
        destination.write_bytes(original)
    checked = subprocess.run(
        [sys.executable, "-m", "changecost.summary", str(payload)],
        env=dict(os.environ, GITHUB_STEP_SUMMARY=str(destination)),
        capture_output=True,
        text=True,
    )
    assert checked.returncode == 2 and checked.stdout == ""
    assert checked.stderr == "cannot render or write advisory summary\n"
    if existing:
        assert destination.read_bytes() == original
    else:
        assert not destination.exists()


@pytest.mark.parametrize("complete", [False, True])
def test_summary_real_unknown_local_completeness(tmp_path, complete):
    from changecost.advisory import budget_component, check_record
    from changecost.store import reference
    from changecost.summary import render_summary
    from tests.test_advisory import settlement

    store, record = settlement(tmp_path, complete=complete)
    output = check_record(
        store, reference(record), budget_component("15", "monetary", "EUR", "billed", "EUR")
    )
    assert output["status"] == "unknown"
    assert output["completeness"] == ("complete" if complete else "unknown")
    assert render_summary(output)


@pytest.mark.parametrize("imported", [False, True])
@pytest.mark.parametrize("sample_count", [0, 1, 2])
@pytest.mark.parametrize("existing", [False, True])
def test_summary_real_unpriced_quote(tmp_path, imported, sample_count, existing):
    import os
    import subprocess
    import sys

    from changecost.quotes import compute_quote
    from changecost.summary import render_summary
    from tests.test_advisory import evaluate
    from tests.test_quotes import setup
    from tests.test_reconciliation import scope

    store = setup(tmp_path)
    record = compute_quote(store, "target", scope(), "unpriced", minimum=2)
    output = evaluate(store, record)
    assert output["status"] == "unknown" and output["completeness"] == "unknown"
    assert output["sample_count"] == 0
    assert render_summary(output)
    output["sample_count"] = sample_count
    if imported:
        output["provenance"] = "producer_assertion; provider_support_not_verified"
    source, destination = tmp_path / "result.json", tmp_path / "summary.md"
    source.write_text(json.dumps(output))
    previous = b"Previous summary\n"
    if existing:
        destination.write_bytes(previous)
    checked = subprocess.run(
        [sys.executable, "-m", "changecost.summary", str(source)],
        env={**os.environ, "GITHUB_STEP_SUMMARY": str(destination)},
        capture_output=True,
        text=True,
        check=False,
    )
    if not imported and sample_count > 0:
        assert checked.returncode == 2 and checked.stdout == ""
        assert checked.stderr == "cannot render or write advisory summary\n"
        if existing:
            assert destination.read_bytes() == previous
        else:
            assert not destination.exists()
    else:
        assert checked.returncode == 0 and checked.stdout == "" and checked.stderr == ""
        rendered = destination.read_text()
        assert f"sample_count: {sample_count}\n\n" in rendered
        assert "Status: unknown\n\n" in rendered
        if existing:
            assert rendered.startswith(previous.decode())


@pytest.mark.parametrize("kind", ["quote", "computed_settlement"])
@pytest.mark.parametrize(
    "mutation", ["missing", "legacy", "economic", "cutoff", "quantile", "sample"]
)
@pytest.mark.parametrize("existing", [False, True])
def test_summary_computation_scope_contract(tmp_path, kind, mutation, existing):
    import os
    import subprocess
    import sys

    from changecost.summary import render_summary

    value = verified_result(kind, "within_budget")
    assert render_summary(value)
    if mutation == "missing":
        value["scope"] = None
    elif mutation == "legacy":
        value["scope"] = "legacy"
    elif mutation == "economic":
        value["scope"]["economic"]["currency"] = "EUR"
        value["scope"]["economic"]["unit"] = "EUR"
    elif mutation == "cutoff":
        value["cutoff"] = None
    elif mutation == "quantile":
        value["quantile"] = None if kind == "quote" else "p90"
    else:
        value["sample_count"] = None if kind == "quote" else 0
    payload = tmp_path / "result.json"
    payload.write_text(json.dumps(value))
    destination = tmp_path / "summary"
    original = b"Earlier summary: unchanged\n"
    if existing:
        destination.write_bytes(original)
    rejected = subprocess.run(
        [sys.executable, "-m", "changecost.summary", str(payload)],
        env=dict(os.environ, GITHUB_STEP_SUMMARY=str(destination)),
        capture_output=True,
        text=True,
    )
    assert rejected.returncode == 2
    assert rejected.stdout == ""
    assert rejected.stderr == "cannot render or write advisory summary\n"
    assert destination.read_bytes() == original if existing else not destination.exists()


@pytest.mark.parametrize(
    "cutoff",
    [
        None,
        "private-cutoff",
        [],
        True,
        {"store_id": "local", "at": "2026-10-05T00:00:00Z", "sequence": 1},
    ],
)
@pytest.mark.parametrize("existing", [False, True])
def test_summary_legacy_cutoff_contract(tmp_path, cutoff, existing):
    import os
    import subprocess
    import sys

    value = result("legacy")
    value.update(
        record={"kind": "settlement", "record_id": "legacy"},
        scope="legacy",
        sample_count=None,
        quantile=None,
        cutoff=cutoff,
    )
    payload = tmp_path / "result.json"
    payload.write_text(json.dumps(value))
    destination = tmp_path / "summary"
    original = b"Earlier summary unchanged\n"
    if existing:
        destination.write_bytes(original)
    checked = subprocess.run(
        [sys.executable, "-m", "changecost.summary", str(payload)],
        env=dict(os.environ, GITHUB_STEP_SUMMARY=str(destination)),
        capture_output=True,
        text=True,
    )
    assert checked.stdout == ""
    if cutoff is None:
        assert checked.returncode == 0 and checked.stderr == ""
        assert destination.exists()
    else:
        assert checked.returncode == 2
        assert checked.stderr == "cannot render or write advisory summary\n"
        assert destination.read_bytes() == original if existing else not destination.exists()


def contradictory_declaration(kind, fault):
    value = verified_result(kind, "within_budget")
    selected = 1 if kind == "quote" else 0
    if fault == "empty":
        value["declared"] = []
    if fault == "amount":
        value["declared"][selected]["amount"] = "11"
    if fault == "identity":
        value["declared"][selected]["basis"] = "other"
    if fault == "null":
        value["declared"][selected]["amount"] = None
    if fault == "duplicate":
        value["declared"].append(dict(value["declared"][selected]))
    if fault == "selection":
        value["quantile"] = "p50"
    if fault == "samples":
        value["sample_count"] = 0
    if fault == "incomplete":
        value["declared"][0]["unknown_count"] = 1
    if fault == "missing_completeness":
        del value["declared"][0]["unknown_count"]
    return value


DECLARATION_FAULTS = [
    (kind, fault)
    for kind in ("quote", "computed_settlement")
    for fault in ("empty", "amount", "identity", "null", "duplicate")
] + [
    ("quote", "selection"),
    ("quote", "samples"),
    ("computed_settlement", "incomplete"),
    ("computed_settlement", "missing_completeness"),
]


@pytest.mark.parametrize("kind,fault", DECLARATION_FAULTS)
@pytest.mark.parametrize("existing", [False, True])
def test_selected_declaration_cli_preserves_destination(
    tmp_path, kind, fault, existing, monkeypatch, capsys
):
    assert_rejected_summary(
        tmp_path, contradictory_declaration(kind, fault), existing, monkeypatch, capsys
    )


def assert_rejected_summary(tmp_path, value, existing, monkeypatch, capsys):
    """Exercise the public parser and output boundary; process smokes remain separate."""
    import os
    import sys

    from changecost.summary import main

    payload = tmp_path / "result.json"
    payload.write_text(json.dumps(value))
    destination = tmp_path / "summary"
    original = b"Earlier summary\n"
    if existing:
        destination.write_bytes(original)
    previous_argv, previous_destination = list(sys.argv), os.environ.get("GITHUB_STEP_SUMMARY")
    with monkeypatch.context() as invocation:
        invocation.setattr(sys, "argv", ["changecost.summary", str(payload)])
        invocation.setenv("GITHUB_STEP_SUMMARY", str(destination))
        with pytest.raises(SystemExit) as rejected:
            main()
        assert rejected.value.code == 2
    output = capsys.readouterr()
    assert output.out == ""
    assert output.err == "cannot render or write advisory summary\n"
    assert sys.argv == previous_argv
    assert os.environ.get("GITHUB_STEP_SUMMARY") == previous_destination
    assert destination.read_bytes() == original if existing else not destination.exists()


@pytest.mark.parametrize("kind", ["quote", "computed_settlement"])
@pytest.mark.parametrize("amount", ["0", "10.00"])
def test_selected_declaration_exact_decimal_controls(kind, amount):
    from changecost.summary import render_summary

    value = verified_result(kind, "within_budget")
    value["comparison"] = value["budget"] | {"amount": amount}
    selected = 1 if kind == "quote" else 0
    value["declared"][selected]["amount"] = "0.00" if amount == "0" else "10"
    assert render_summary(value)


@pytest.mark.parametrize("fault", ["inverted", "mixed_null", "scope"])
def test_quote_unknown_pair_must_remain_coherent(fault):
    from changecost.summary import render_summary

    value = result("unknown")
    if fault == "inverted":
        value["declared"][0]["amount"] = "20"
        value["declared"][1]["amount"] = "10"
    elif fault == "mixed_null":
        value["declared"][0]["amount"] = "10"
    else:
        value["declared"][0]["basis"] = "other"
    with pytest.raises(ValueError):
        render_summary(value)


@pytest.mark.parametrize("kind", ["quote", "computed_settlement"])
@pytest.mark.parametrize("status", ["within_budget", "over_budget"])
@pytest.mark.parametrize("spoofed_reason", [False, True])
@pytest.mark.parametrize("existing", [False, True])
def test_unknown_cannot_conceal_complete_compatible(
    tmp_path, kind, status, spoofed_reason, existing, monkeypatch, capsys
):
    value = verified_result(kind, status)
    value.update(status="unknown", comparison=None)
    value["reasons"] = ["incompatible_economic_identity"] if spoofed_reason else []
    assert_rejected_summary(tmp_path, value, existing, monkeypatch, capsys)


def local_unknown_complete(kind):
    value = verified_result(kind, "within_budget")
    value.update(status="unknown", comparison=None, reasons=["incompatible_economic_identity"])
    value["budget"] = value["budget"] | {"unit": "EUR", "currency": "EUR"}
    return value


@pytest.mark.parametrize(
    "fault",
    [
        "quote_null_complete",
        "quote_finite_unknown",
        "subtotal_empty",
        "subtotal_null",
        "subtotal_incomplete",
        "subtotal_duplicate",
        "empty_reasons",
    ],
)
@pytest.mark.parametrize("existing", [False, True])
def test_unknown_consistency_preserves_destination(tmp_path, fault, existing, monkeypatch, capsys):
    value = local_unknown_complete("quote" if fault.startswith("quote") else "computed_settlement")
    if fault == "quote_null_complete":
        value["declared"] = result("null")["declared"]
        value["sample_count"] = 0
    if fault == "quote_finite_unknown":
        value["completeness"] = "unknown"
        value["reasons"] = ["incomplete_or_unpriced"]
    if fault == "subtotal_empty":
        value["declared"] = []
    if fault == "subtotal_null":
        value["declared"][0]["amount"] = None
    if fault == "subtotal_incomplete":
        value["declared"][0]["unknown_count"] = 1
    if fault == "subtotal_duplicate":
        value["declared"].append(dict(value["declared"][0]))
    if fault == "empty_reasons":
        value = result("unknown")
        value["reasons"] = []
    assert_rejected_summary(tmp_path, value, existing, monkeypatch, capsys)


@pytest.mark.parametrize("kind", ["quote", "computed_settlement"])
def test_complete_unknown_actual_incompatibility_control(kind):
    from changecost.summary import render_summary

    assert render_summary(local_unknown_complete(kind))


def test_known_subtotal_can_remain_locally_incomplete():
    from changecost.summary import render_summary

    value = verified_result("computed_settlement", "within_budget")
    value.update(
        status="unknown",
        comparison=None,
        completeness="unknown",
        reasons=["incomplete_or_unpriced"],
    )
    assert render_summary(value)


def local_incomplete_settlement():
    value = verified_result("computed_settlement", "within_budget")
    value.update(
        status="unknown",
        comparison=None,
        completeness="unknown",
        reasons=["incomplete_or_unpriced"],
    )
    return value


@pytest.mark.parametrize("extra", [False, True])
@pytest.mark.parametrize("existing", [False, True])
def test_imported_subtotal_requires_count_cli(tmp_path, extra, existing, monkeypatch, capsys):
    value = local_incomplete_settlement()
    value["provenance"] = "producer_assertion; provider_support_not_verified"
    if extra:
        value["declared"].append(value["declared"][0] | {"unit": "EUR", "currency": "EUR"})
    value["declared"][-1].pop("unknown_count")
    assert_rejected_summary(tmp_path, value, existing, monkeypatch, capsys)


@pytest.mark.parametrize(
    "shape", ["empty", "duplicate", "unmatched", "null", "extra_null", "positive"]
)
def test_imported_subtotal_claims_remain_unknown(shape):
    from changecost.summary import render_summary

    value = local_incomplete_settlement()
    value["provenance"] = "producer_assertion; provider_support_not_verified"
    if shape == "empty":
        value["declared"] = []
    elif shape == "duplicate":
        value["declared"].append(dict(value["declared"][0]))
    elif shape == "unmatched":
        value["declared"][0]["basis"] = "other"
    elif shape == "null":
        value["declared"][0]["amount"] = None
    elif shape == "extra_null":
        value["declared"].append(
            value["declared"][0] | {"unit": "EUR", "currency": "EUR", "amount": None}
        )
    else:
        value["declared"][0]["unknown_count"] = 1
    assert "Status: unknown" in render_summary(value)


@pytest.mark.parametrize(
    "fault",
    [
        "empty",
        "unrelated",
        "duplicate_scope",
        "duplicate_extra",
        "missing",
        None,
        True,
        -1,
        "1",
        [],
        {},
    ],
)
@pytest.mark.parametrize("extra", [False, True])
@pytest.mark.parametrize("existing", [False, True])
def test_incomplete_local_subtotal_shape_cli(tmp_path, fault, extra, existing, monkeypatch, capsys):
    value = local_incomplete_settlement()
    other = value["declared"][0] | {"unit": "EUR", "currency": "EUR"}
    if extra:
        value["declared"].append(other)
    if fault == "empty":
        value["declared"] = []
    elif fault == "unrelated":
        value["declared"] = [other]
    elif fault == "duplicate_scope":
        value["declared"].append(dict(value["declared"][0]))
    elif fault == "duplicate_extra":
        value["declared"].extend([dict(other), dict(other)])
    elif fault == "missing":
        value["declared"][-1 if extra else 0].pop("unknown_count")
    else:
        value["declared"][-1 if extra else 0]["unknown_count"] = fault
    assert_rejected_summary(tmp_path, value, existing, monkeypatch, capsys)


@pytest.mark.parametrize("amount,count", [(None, 0), (None, 2), ("0", 0), ("10", 2)])
@pytest.mark.parametrize("extra", [False, True])
def test_incomplete_local_subtotal_producer_controls(amount, count, extra):
    from changecost.summary import render_summary

    value = local_incomplete_settlement()
    value["declared"][0].update(amount=amount, unknown_count=count)
    if extra:
        value["declared"].append(
            value["declared"][0]
            | {
                "unit": "EUR",
                "currency": "EUR",
                "unknown_count": count if amount is not None else 1,
            }
        )
    assert render_summary(value)


@pytest.mark.parametrize("existing", [False, True])
def test_incomplete_local_empty_additional_group_cli(tmp_path, existing, monkeypatch, capsys):
    value = local_incomplete_settlement()
    value["declared"].append(
        value["declared"][0]
        | {
            "unit": "EUR",
            "currency": "EUR",
            "amount": None,
            "unknown_count": 0,
        }
    )
    assert_rejected_summary(tmp_path, value, existing, monkeypatch, capsys)


@pytest.mark.parametrize("status", ["within_budget", "over_budget", "unknown"])
@pytest.mark.parametrize("amount,count", [("10", 1), (None, 0), (None, 1)])
@pytest.mark.parametrize("existing", [False, True])
def test_complete_local_subtotal_groups_cli(
    tmp_path, status, amount, count, existing, monkeypatch, capsys
):
    value = (
        local_unknown_complete("computed_settlement")
        if status == "unknown"
        else verified_result("computed_settlement", status)
    )
    value["declared"].append(
        value["declared"][0]
        | {
            "unit": "EUR",
            "currency": "EUR",
            "amount": amount,
            "unknown_count": count,
        }
    )
    assert_rejected_summary(tmp_path, value, existing, monkeypatch, capsys)


@pytest.mark.parametrize("missing", [(0,), (0, 1)])
@pytest.mark.parametrize("existing", [False, True])
def test_local_unpriced_optional_amount_cli(tmp_path, missing, existing):
    import os
    import subprocess
    import sys

    value = result("incomplete_or_unpriced")
    value["provenance"] = "locally_reproduced_synthetic; provider_support_not_verified"
    for index in missing:
        value["declared"][index].pop("amount")
    source, destination = tmp_path / "result.json", tmp_path / "summary.md"
    source.write_text(json.dumps(value))
    if existing:
        destination.write_text("previous\n")
    checked = subprocess.run(
        [sys.executable, "-m", "changecost.summary", str(source)],
        env={**os.environ, "GITHUB_STEP_SUMMARY": str(destination)},
        capture_output=True,
        text=True,
        check=False,
    )
    assert checked.returncode == 0 and checked.stdout == "" and checked.stderr == ""
    assert "Status: unknown" in destination.read_text()
    if existing:
        assert destination.read_text().startswith("previous\n")


IDENTIFIER_FIELDS = [
    (kind, field)
    for kind in ("quote", "computed_settlement", "settlement")
    for field in ("record_id", "reason")
] + [("settlement", "scope")]


def identifier_result(kind):
    value = result("safe")
    if kind == "computed_settlement":
        value = verified_result(kind, "within_budget")
        value.update(
            status="unknown",
            comparison=None,
            completeness="unknown",
            provenance="producer_assertion; provider_support_not_verified",
            reasons=["safe"],
        )
    if kind == "settlement":
        value.update(
            record={"kind": kind, "record_id": "safe"},
            scope="safe",
            cutoff=None,
            quantile=None,
            sample_count=None,
        )
    return value


def set_identifier_case(value, field, label):
    mapping = value["record"] if field == "record_id" else value
    name = "reasons" if field == "reason" else field
    if label == "missing":
        mapping.pop(name)
    else:
        mapping[name] = [label] if field == "reason" else label


@pytest.mark.parametrize(("kind", "field"), IDENTIFIER_FIELDS)
@pytest.mark.parametrize("invalid", [None, "", " \t\n", False, 1, {}, [], "missing"])
@pytest.mark.parametrize("existing", [False, True])
def test_summary_identifier_contract_cli(
    tmp_path, kind, field, invalid, existing, monkeypatch, capsys
):
    value = identifier_result(kind)
    set_identifier_case(value, field, invalid)
    assert_rejected_summary(tmp_path, value, existing, monkeypatch, capsys)


@pytest.mark.parametrize(("kind", "field"), IDENTIFIER_FIELDS)
@pytest.mark.parametrize(
    "label", ["世界", "e\u0301", "  padded  ", "<b>$(touch canary)\x1b", "x" * 10000]
)
def test_summary_identifier_valid_data_controls(kind, field, label):
    from copy import deepcopy

    from changecost.summary import render_summary

    value = identifier_result(kind)
    set_identifier_case(value, field, label)
    before = deepcopy(value)
    assert render_summary(value)
    assert value == before
