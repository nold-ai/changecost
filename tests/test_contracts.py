"""Acceptance cases for the portable v1 input boundary."""

import json

import pytest

from changecost.models import Component, Features, Quote, RunRef
from changecost.serialization import ContractError, dumps_bundle, loads_bundle

TIME = "2026-09-29T08:00:00Z"


def change_record():
    return {
        "schema": "changecost/v1",
        "kind": "change",
        "record_id": "c1",
        "origin_store_id": "source",
        "recorded_at": TIME,
        "effective_at": TIME,
        "repository_id": "repo",
        "change_id": "change",
        "features": {
            "version": "features/v1",
            "captured_at": TIME,
            "recorded_at": TIME,
            "change_shape": "bugfix",
            "trajectory": "iterative",
            "execution_profile": None,
        },
    }


def payload(record=None):
    return {
        "schema": "changecost/v1",
        "source": {"store_id": "source", "at": TIME, "sequence": 1},
        "records": [record or change_record()],
        "observations": [],
    }


def test_bundle_roundtrip():
    parsed = loads_bundle(json.dumps(payload()))
    assert loads_bundle(dumps_bundle(parsed)) == parsed
    assert parsed.records[0].record_id == "c1"


@pytest.mark.parametrize("amount", ["0.12345678901234567890123456789", "1.00", "0", "-2.50", None])
def test_exact_component(amount):
    c = Component(
        economic_kind="monetary", unit="USD", basis="billed", currency="USD", amount=amount
    )
    assert c.model_dump(mode="json")["amount"] == amount


@pytest.mark.parametrize("amount", [1, 0.1, True, "NaN", "Infinity", "-Infinity", ""])
def test_amount_coercion_is_rejected(amount):
    with pytest.raises(ValueError):
        Component(
            economic_kind="monetary", unit="USD", basis="billed", currency="USD", amount=amount
        )


@pytest.mark.parametrize(
    "kind,amount,currency,valid",
    [
        ("monetary", "1", None, False),
        ("nonmonetary", "1", "USD", False),
        ("nonmonetary", "100", None, True),
        ("monetary", None, None, True),
        ("monetary", "1", "usd", False),
    ],
)
def test_currency_invariants(kind, amount, currency, valid):
    values = dict(
        economic_kind=kind,
        unit="tokens:provider:input",
        basis="reported",
        amount=amount,
        currency=currency,
    )
    if valid:
        assert Component.model_validate(values).amount == amount
    else:
        with pytest.raises(ValueError):
            Component.model_validate(values)


@pytest.mark.parametrize(
    "field,value",
    [
        ("schema", "changecost/v2"),
        ("kind", "alien"),
        ("repository_id", " "),
        ("recorded_at", "2026-09-29T08:00:00"),
        ("recorded_at", 123),
        ("prompt", "PRIVATE_SENTINEL"),
    ],
)
def test_reject_invalid_record_without_echo(field, value):
    record = change_record()
    record[field] = value
    with pytest.raises(ContractError) as exc:
        loads_bundle(json.dumps(payload(record)))
    assert "PRIVATE_SENTINEL" not in str(exc.value)


def test_reject_nested_extra_and_duplicate_members():
    record = change_record()
    record["features"]["secret"] = "PRIVATE_SENTINEL"
    with pytest.raises(ContractError) as exc:
        loads_bundle(json.dumps(payload(record)))
    assert "PRIVATE_SENTINEL" not in str(exc.value)
    for raw in ['{"schema":"x","schema":"changecost/v1"}', '{"x":NaN}', '{"x":Infinity}']:
        with pytest.raises(ContractError):
            loads_bundle(raw)


def test_normalized_feature_domain_and_identity():
    values = dict(
        captured_at=TIME,
        recorded_at=TIME,
        change_shape=" BugFix ",
        trajectory="ITERATIVE",
        execution_profile=" ",
    )
    f = Features.model_validate(values)
    assert (f.change_shape, f.trajectory, f.execution_profile) == ("bugfix", "iterative", None)
    with pytest.raises(ValueError):
        Features.model_validate({**values, "trajectory": "unknown"})
    a = RunRef(repository_id="Repo", provider="cursor", surface="ide", run_id="run")
    assert a != a.model_copy(update={"repository_id": "repo"})
    with pytest.raises(ValueError):
        RunRef(repository_id="repo", provider="cursor", surface="ide", run_id=" ")


def test_offsets_normalize_to_utc():
    record = change_record()
    record["recorded_at"] = "2026-09-29T10:00:00+02:00"
    parsed = loads_bundle(json.dumps(payload(record)))
    assert parsed.records[0].recorded_at.utcoffset() == __import__("datetime").timedelta(0)
    assert "08:00:00" in dumps_bundle(parsed)


@pytest.mark.parametrize("where", ["bundle", "record"])
def test_wire_schema_is_explicit(where):
    value = payload()
    del (value if where == "bundle" else value["records"][0])["schema"]
    with pytest.raises(ContractError):
        loads_bundle(json.dumps(value))


def test_observed_run_start_cannot_postdate_registration():
    from changecost.models import Run

    record = {
        k: v
        for k, v in change_record().items()
        if k not in {"kind", "repository_id", "change_id", "features"}
    }
    record.update(
        kind="run",
        ref={"repository_id": "repo", "provider": "cursor", "surface": "ide", "run_id": "r"},
        observed_start="2026-09-30T00:00:00Z",
    )
    with pytest.raises(ValueError):
        Run.model_validate(record)


@pytest.mark.parametrize(
    "value",
    [
        "2026-09-29T08:00:00+00:60",
        "2026-09-29T08:00:00+00:99",
        "0001-01-01T00:00:00+01:00",
        "9999-12-31T23:59:59-01:00",
    ],
)
def test_timestamp_rejects_invalid_offset_and_utc_overflow(value):
    value_bundle = payload()
    value_bundle["source"]["at"] = value
    with pytest.raises(ContractError):
        loads_bundle(json.dumps(value_bundle))


@pytest.mark.parametrize("where", ["bundle", "record"])
def test_unsupported_schema_has_safe_specific_diagnostic(where):
    value = payload()
    (value if where == "bundle" else value["records"][0])["schema"] = "changecost/v99_PRIVATE"
    with pytest.raises(ContractError, match="schema") as exc:
        loads_bundle(json.dumps(value))
    assert "PRIVATE" not in str(exc.value)


@pytest.mark.parametrize("field", ["source", "observation", "quote"])
@pytest.mark.parametrize("sequence", [2**63, 2**100])
def test_portable_sequence_range(field, sequence):
    data = payload()
    if field == "source":
        data["source"]["sequence"] = sequence
    elif field == "observation":
        data["observations"] = [
            {
                "reference": {"kind": "change", "record_id": "c1"},
                "store_id": "source",
                "available_at": TIME,
                "sequence": sequence,
            }
        ]
    else:
        data["records"].append(sequence_quote(sequence))
    with pytest.raises(ContractError):
        loads_bundle(json.dumps(data))


def sequence_quote(sequence):
    component = {
        "economic_kind": "monetary",
        "unit": "USD",
        "basis": "billed",
        "currency": "USD",
        "amount": None,
    }
    return {
        "schema": "changecost/v1",
        "kind": "quote",
        "record_id": "q",
        "origin_store_id": "source",
        "recorded_at": TIME,
        "effective_at": TIME,
        "change": {"kind": "change", "record_id": "c1"},
        "state": "unpriced",
        "p50": component,
        "p90": component,
        "reason": "unavailable",
        "sample_count": 2**100,
        "cohort": "repository",
        "algorithm_version": "future",
        "inputs": [],
        "cutoff": {"store_id": "source", "at": TIME, "sequence": sequence},
    }


def test_maximum_nested_cutoff_preserves_unbounded_json_sample_count():
    data = payload()
    data["records"].append(sequence_quote(2**63 - 1))
    bundle = loads_bundle(json.dumps(data))
    assert isinstance(bundle.records[1], Quote)
    assert bundle.records[1].sample_count == 2**100
    assert bundle.records[1].cutoff.sequence == 2**63 - 1
    assert loads_bundle(dumps_bundle(bundle)) == bundle


def test_maximum_sequence_portable_roundtrip():
    data = payload()
    data["source"]["sequence"] = 2**63 - 1
    data["observations"] = [
        {
            "reference": {"kind": "change", "record_id": "c1"},
            "store_id": "source",
            "available_at": TIME,
            "sequence": 2**63 - 1,
        }
    ]
    bundle = loads_bundle(json.dumps(data))
    assert loads_bundle(dumps_bundle(bundle)) == bundle
    assert bundle.observations[0].sequence == bundle.source.sequence == 2**63 - 1
