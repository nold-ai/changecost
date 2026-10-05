"""Explicit budget advice, historical authority and no-write acceptance."""

import json
from decimal import Decimal

import pytest
from typer.testing import CliRunner

from changecost.cli import app
from changecost.models import Quote
from changecost.store import Store
from tests.advisory_oracle import advice
from tests.test_quotes import peer, setup
from tests.test_reconciliation import scope

runner = CliRunner()
ECONOMIC = [
    "--economic-kind",
    "monetary",
    "--unit",
    "USD",
    "--currency",
    "USD",
    "--basis",
    "billed",
]


def check_args(record, budget="15"):
    return [
        "check",
        "--record-kind",
        record.kind,
        "--record-id",
        record.record_id,
        "--budget",
        budget,
        *ECONOMIC,
    ]


def priced(tmp_path):
    from changecost.quotes import compute_quote

    store = setup(tmp_path)
    peer(store, "one", "10")
    peer(store, "two", "18")
    record = compute_quote(store, "target", scope(), "quote-operation", minimum=2)
    return store, record


def test_quantiles_exact_equality_and_no_write(tmp_path):
    store, record = priced(tmp_path)
    before = store.path.read_bytes()
    for quantile, expected in [(None, "over_budget"), ("p50", "within_budget")]:
        args = ["--db", str(store.path), *check_args(record)]
        if quantile:
            args += ["--quantile", quantile]
        result = runner.invoke(app, args)
        assert result.exit_code == 0, result.output
        output = json.loads(result.stdout)
        assert output["status"] == expected
        assert output["comparison"]["amount"] == getattr(record, quantile or "p90").amount
    assert record.p90.amount is not None
    equal = runner.invoke(app, ["--db", str(store.path), *check_args(record, record.p90.amount)])
    assert json.loads(equal.stdout)["status"] == "within_budget"
    assert store.path.read_bytes() == before


def test_artifact_claim_no_database(tmp_path, monkeypatch):
    store, record = priced(tmp_path)
    path = tmp_path / "artifact.json"
    path.write_text(store.export_bundle().model_dump_json(by_alias=True))

    def fail(*args, **kwargs):
        raise AssertionError("artifact mode opened database")

    monkeypatch.setattr(Store, "connect", fail)
    result = runner.invoke(
        app, ["--db", str(tmp_path / "absent"), *check_args(record), "--artifact", str(path)]
    )
    assert result.exit_code == 0, result.output
    value = json.loads(result.stdout)
    assert value["status"] == "unknown" and value["comparison"] is None
    assert value["declared"]


@pytest.mark.parametrize("budget", ["-1", "NaN", "Infinity", "private", ""])
def test_invalid_budget_before_store(tmp_path, budget):
    result = runner.invoke(
        app,
        [
            "--db",
            str(tmp_path / "absent"),
            "check",
            "--record-kind",
            "quote",
            "--record-id",
            "q",
            "--budget",
            budget,
            *ECONOMIC,
        ],
    )
    assert result.exit_code == 2 and result.stdout == ""
    assert not (tmp_path / "absent").exists()


def test_identity_mismatch_unknown(tmp_path):
    store, record = priced(tmp_path)
    args = check_args(record)
    args[args.index("--basis") + 1] = "other"
    result = runner.invoke(app, ["--db", str(store.path), *args])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["status"] == "unknown"


@pytest.mark.parametrize(
    "value,budget",
    [
        ("0", "0"),
        ("0.1", "0.1"),
        ("1.000000000000000000000000001", "1.000000000000000000000000000"),
        ("1e-100", "0"),
    ],
)
def test_independent_decimal_oracle(tmp_path, value, budget):
    from changecost.advisory import compare

    assert compare(value, budget) == advice(value, budget)
    assert isinstance(Decimal(value), Decimal)


def settlement(tmp_path, value="10", complete=True):
    from changecost.operations import bind_evidence
    from tests.test_reconciliation import (
        NOW,
        START,
        add_coverage,
        compute,
        event,
        import_events,
        setup_change,
    )

    store, change, members = setup_change(tmp_path)
    ident = import_events(store, event("charge", value))[0]
    bind_evidence(store, ident, members[0])
    if complete:
        add_coverage(store, members[0], ident, start=START, end=NOW)
    return store, compute(store)


def evaluate(store, record, budget="15", **options):
    from changecost.advisory import budget_component, check_record
    from changecost.store import reference

    return check_record(
        store,
        reference(record),
        budget_component(budget, "monetary", "USD", "billed", "USD"),
        **options,
    )


@pytest.mark.parametrize(
    "value,complete",
    [("10", True), ("18", True), ("0", True), ("0.1", True), ("10", False), ("20", False)],
)
def test_settlement_complete_and_partial_both_sides(tmp_path, value, complete):
    store, record = settlement(tmp_path, value, complete)
    before = store.export_bundle()
    budget = value if value in {"0", "0.1"} else "15"
    assert evaluate(store, record, budget)["status"] == advice(value, budget, complete=complete)
    assert store.export_bundle() == before
    from tests.test_reconciliation import compute

    assert compute(store) == record


def tamper(store, record, **updates):
    """Fault injection into an existing valid local record; never a fixture authority shortcut."""
    changed = record.model_copy(update=updates)
    with store.connect() as connection:
        connection.execute(
            "UPDATE records SET payload=? WHERE kind=? AND id=?",
            (changed.model_dump_json(by_alias=True), record.kind, record.record_id),
        )
    return changed


def cutoff_timestamp_fixture(tmp_path, kind, boundary):
    from datetime import timedelta

    store, record = priced(tmp_path) if kind == "quote" else settlement(tmp_path)
    original = record.cutoff.at
    store.clock = lambda: original + timedelta(minutes=2)
    if boundary == "future":
        record = tamper(
            store,
            record,
            cutoff=record.cutoff.model_copy(update={"at": original + timedelta(minutes=1)}),
        )
    elif boundary == "older":
        peer(store, "later-timestamp", "999")
    return store, record


def inspect_selected_computation(store, record):
    from changecost.quotes import inspect_quote
    from changecost.reconciliation import inspect_computation

    return (
        inspect_quote(store, record)
        if isinstance(record, Quote)
        else inspect_computation(store, record)
    )


def assert_cutoff_advice(output, unavailable):
    assert bool(output["comparison"] is None) == unavailable
    assert output["declared"]
    if unavailable:
        assert output["status"] == "unknown"
        assert "foreign_or_future_cutoff" in output["reasons"]
    else:
        assert output["status"] in {"within_budget", "over_budget"}


def assert_cutoff_inspection(output, unavailable, kind):
    assert output["local_computation"] is True
    assert output["replay_eligibility"] == (
        "replay_unavailable" if unavailable else "inputs_available"
    )
    if kind == "quote":
        assert output["economic_validation"] == ("not_computed" if unavailable else "reproduced")
    else:
        assert output["current_eligibility"] == "snapshot_only"


@pytest.mark.parametrize("kind", ["quote", "computed_settlement"])
@pytest.mark.parametrize("boundary", ["future", "equal", "older"])
@pytest.mark.parametrize("entrypoint", ["check", "inspect"])
def test_committed_cutoff_timestamp_authority(tmp_path, kind, boundary, entrypoint):
    store, record = cutoff_timestamp_fixture(tmp_path, kind, boundary)
    before = store.path.read_bytes()
    if entrypoint == "check":
        assert_cutoff_advice(evaluate(store, record), boundary == "future")
    else:
        assert_cutoff_inspection(
            inspect_selected_computation(store, record), boundary == "future", kind
        )
    assert store.path.read_bytes() == before


@pytest.mark.parametrize("kind", ["quote", "computed_settlement"])
@pytest.mark.parametrize("format", ["json", "human"])
def test_future_committed_cutoff_cli_unknown_no_write(tmp_path, kind, format):
    store, record = cutoff_timestamp_fixture(tmp_path, kind, "future")
    before = store.path.read_bytes()
    prefix = ["--db", str(store.path), "--format", format]
    checked = runner.invoke(app, [*prefix, *check_args(record)])
    explained = runner.invoke(
        app, [*prefix, "explain", "--record-kind", kind, "--record-id", record.record_id]
    )
    assert checked.exit_code == explained.exit_code == 0
    assert not checked.stderr and not explained.stderr
    if format == "json":
        assert_cutoff_advice(json.loads(checked.stdout), True)
        assert_cutoff_inspection(json.loads(explained.stdout), True, kind)
    else:
        assert "status: unknown" in checked.stdout
        assert "replay_eligibility: replay_unavailable" in explained.stdout
    assert store.path.read_bytes() == before


@pytest.mark.parametrize("kind", ["quote", "computed_settlement"])
@pytest.mark.parametrize("zero_sequence", [False, True])
@pytest.mark.parametrize("format", ["json", "human"])
@pytest.mark.parametrize("receipt", [False, True])
def test_missing_committed_timestamp_cannot_grant_authority(
    tmp_path, kind, zero_sequence, format, receipt
):
    from changecost.serialization import ContractError

    store, record = cutoff_timestamp_fixture(tmp_path, kind, "equal")
    with store.connect() as connection:
        connection.execute("UPDATE metadata SET last_at=NULL")
        if zero_sequence:
            connection.execute("UPDATE metadata SET sequence=0")
        if not receipt:
            connection.execute("DELETE FROM computations")
    before = store.path.read_bytes()
    with pytest.raises(ContractError):
        evaluate(store, record)
    inspected = inspect_selected_computation(store, record)
    assert inspected["local_computation"] is receipt
    assert inspected["replay_eligibility"] == "replay_unavailable"
    checked = runner.invoke(app, ["--db", str(store.path), "--format", format, *check_args(record)])
    assert checked.exit_code == 2 and not checked.stdout
    if format == "json":
        assert json.loads(checked.stderr)["schema"] == "changecost/error-v1"
    else:
        assert checked.stderr
    assert "Traceback" not in checked.stderr
    assert store.path.read_bytes() == before


@pytest.mark.parametrize("kind", ["quote", "computed_settlement"])
@pytest.mark.parametrize(
    "mutation", ["unsupported", "foreign", "future", "mismatch", "missing_input", "missing_receipt"]
)
def test_local_authority_and_replay_rejections(tmp_path, kind, mutation):
    store, record = priced(tmp_path) if kind == "quote" else settlement(tmp_path)
    if mutation == "unsupported":
        record = tamper(store, record, algorithm_version="unsupported/v9")
    elif mutation in {"foreign", "future"}:
        cutoff = record.cutoff.model_copy(
            update={"store_id": "foreign"} if mutation == "foreign" else {"sequence": 2**62}
        )
        record = tamper(store, record, cutoff=cutoff)
    elif mutation == "mismatch":
        updates = (
            {"p90": record.p90.model_copy(update={"amount": "999"})}
            if isinstance(record, Quote)
            else {"subtotals": [record.subtotals[0].model_copy(update={"amount": "999"})]}
        )
        record = tamper(store, record, **updates)
    elif mutation == "missing_receipt":
        with store.connect() as connection:
            connection.execute("DELETE FROM computations WHERE record_id=?", (record.record_id,))
    else:
        dependency = record.inputs[0]
        with store.connect() as connection:
            connection.execute(
                "UPDATE records SET sequence=? WHERE kind=? AND id=?",
                (2**62, dependency.kind, dependency.record_id),
            )
    before = store.path.read_bytes()
    output = evaluate(store, record)
    assert output["status"] == "unknown" and output["comparison"] is None
    assert output["reasons"] and output["declared"]
    assert store.path.read_bytes() == before


@pytest.mark.parametrize("kind", ["quote", "computed_settlement"])
def test_imported_claim_and_later_history(tmp_path, kind):
    store, record = priced(tmp_path) if kind == "quote" else settlement(tmp_path)
    original = evaluate(store, record)
    peer(store, "later", "999")
    assert evaluate(store, record) == original
    destination = Store(tmp_path / "imported", clock=store.clock)
    destination.import_bundle(store.export_bundle())
    output = evaluate(destination, record)
    assert output["status"] == "unknown" and output["comparison"] is None


def test_scope_and_completeness_mismatch(tmp_path):
    from datetime import timedelta

    from tests.test_reconciliation import NOW, START, compute

    store, _ = settlement(tmp_path)
    record = compute(store, "partial", start=START + timedelta(minutes=1), end=NOW)
    output = evaluate(store, record)
    assert output["status"] == "unknown" and "partial_change_scope" in output["reasons"]
    record = tamper(store, record, unknown_reasons=[], full_change=True)
    assert evaluate(store, record)["comparison"] is None


def legacy_claim(store):
    from changecost.models import Component, Settlement
    from changecost.operations import common
    from changecost.store import reference

    change = next(r for r in store.records() if r.kind == "change")
    record = Settlement(
        **common("producer", store.clock()),
        change=reference(change),
        components=[
            Component(
                economic_kind="monetary", unit="USD", currency="USD", basis="billed", amount="18"
            )
        ],
        completeness="reconciled",
        scope="claimed",
        coverage=[],
        inputs=[reference(change)],
        unknown_reasons=[],
    )
    store.apply(lambda records, store_id, now: ([record], record))
    return record


def test_legacy_claim_and_unpriced_quote(tmp_path):
    from tests.test_quotes import quote

    store = setup(tmp_path)
    q = quote(store)
    assert evaluate(store, q)["status"] == "unknown"
    output = evaluate(store, legacy_claim(store))
    assert output["status"] == "unknown" and output["declared"][0]["amount"] == "18"


@pytest.mark.parametrize(
    "changes",
    [
        {"--record-kind": "change"},
        {"--record-id": "missing"},
        {"--quantile": "p95"},
        {"--currency": ""},
    ],
)
def test_invalid_selectors_and_identity(tmp_path, changes):
    store, record = priced(tmp_path)
    args = check_args(record)
    for option, value in changes.items():
        if option in args:
            args[args.index(option) + 1] = value
        else:
            args += [option, value]
    before = store.path.read_bytes()
    output = runner.invoke(app, ["--db", str(store.path), *args])
    assert output.exit_code == 2 and not output.stdout
    assert store.path.read_bytes() == before


def test_settlement_quantile_invalid(tmp_path):
    store, record = settlement(tmp_path)
    output = runner.invoke(app, ["--db", str(store.path), *check_args(record), "--quantile", "p50"])
    assert output.exit_code == 2


@pytest.mark.parametrize("fault", ["schema", "graph", "conflict", "observation"])
def test_artifact_strict_errors(tmp_path, fault):
    store, record = priced(tmp_path)
    data = store.export_bundle().model_dump(mode="json", by_alias=True)
    if fault == "schema":
        data["schema"] = "changecost/v9"
    elif fault == "graph":
        data["records"] = [r for r in data["records"] if r["kind"] == "quote"]
    elif fault == "conflict":
        data["records"].append(data["records"][0] | {"effective_at": "2026-09-28T00:00:00Z"})
    else:
        data["observations"][0]["reference"]["record_id"] = "missing"
    path = tmp_path / "private.json"
    path.write_text(json.dumps(data))
    result = runner.invoke(
        app, ["--db", str(tmp_path / "absent"), *check_args(record), "--artifact", str(path)]
    )
    assert result.exit_code == 2 and not result.stdout
    assert "private" not in result.stderr and not (tmp_path / "absent").exists()


def test_quote_declares_scope(tmp_path):
    store, record = priced(tmp_path)
    result = evaluate(store, record)
    assert result["scope"]["repository_id"] == "repo"
    assert result["scope"]["economic"]["currency"] == "USD"


def test_synthetic_demo(tmp_path):
    from changecost.demo import create_demo

    directory = tmp_path / "demo"
    create_demo(directory)
    expected = {
        "cold-start": "unknown",
        "local-quote": "over_budget",
        "local-settlement": "within_budget",
        "portable-claim": "unknown",
    }
    for name, status in expected.items():
        output = json.loads((directory / f"{name}.json").read_text())
        assert output["status"] == status
        from changecost.summary import render_summary

        assert render_summary(output)
    with pytest.raises(ValueError):
        create_demo(directory)


def test_one_read_snapshot(tmp_path, monkeypatch):
    store, record = priced(tmp_path)
    real = store.connect
    connections = []

    def tracked(*args, **kwargs):
        assert kwargs.get("readonly") is True
        connection = real(*args, **kwargs)
        connection.set_trace_callback(lambda sql: connections.append(sql))
        return connection

    monkeypatch.setattr(store, "connect", tracked)
    output = evaluate(store, record)
    assert output["status"] == "over_budget"
    assert connections.count("BEGIN") == 1
    assert not any(sql.startswith(("INSERT", "UPDATE", "DELETE")) for sql in connections)


@pytest.mark.parametrize("path_kind", ["store", "artifact"])
def test_missing_input_technical_failure(tmp_path, path_kind):
    args = [
        "--db",
        str(tmp_path / "missing"),
        "check",
        "--record-kind",
        "quote",
        "--record-id",
        "q",
        "--budget",
        "15",
        *ECONOMIC,
    ]
    if path_kind == "artifact":
        args += ["--artifact", str(tmp_path / "missing-artifact")]
    output = runner.invoke(app, args)
    assert output.exit_code == 2 and output.stdout == ""
    assert json.loads(output.stderr)["schema"] == "changecost/error-v1"
    assert not list(tmp_path.iterdir())


def test_missing_monetary_and_nonmonetary_currency(tmp_path):
    args = [
        "--db",
        str(tmp_path / "absent"),
        "check",
        "--record-kind",
        "quote",
        "--record-id",
        "q",
        "--budget",
        "15",
        *ECONOMIC,
    ]
    position = args.index("--currency")
    no_currency = args[:position] + args[position + 2 :]
    assert runner.invoke(app, no_currency).exit_code == 2
    args[args.index("--economic-kind") + 1] = "nonmonetary"
    assert runner.invoke(app, args).exit_code == 2
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize(
    "fault",
    [
        "missing",
        "multiple",
        "sequence-text",
        "sequence-float",
        "sequence-negative",
        "sequence-overflow",
        "store-id-blank",
        "store-id-bytes",
        "date-invalid",
        "date-integer",
    ],
)
@pytest.mark.parametrize("authority", ["local", "no-receipt"])
def test_corrupt_metadata_safe_error_no_write(tmp_path, fault, authority):
    import subprocess
    import sys

    store, record = priced(tmp_path)
    with store.connect() as connection:
        if authority == "no-receipt":
            connection.execute("DELETE FROM computations")
        if fault == "missing":
            connection.execute("DELETE FROM metadata")
        elif fault == "multiple":
            connection.execute("INSERT INTO metadata SELECT * FROM metadata")
        else:
            field, value = {
                "sequence-text": ("sequence", "private-sequence"),
                "sequence-float": ("sequence", 1.5),
                "sequence-negative": ("sequence", -1),
                "sequence-overflow": ("sequence", str(2**64)),
                "store-id-blank": ("store_id", ""),
                "store-id-bytes": ("store_id", b"private"),
                "date-invalid": ("last_at", "private-date"),
                "date-integer": ("last_at", 42),
            }[fault]
            connection.execute(f"UPDATE metadata SET {field}=?", (value,))
    before = store.path.read_bytes()
    arguments = ["--db", str(store.path), *check_args(record)]
    output = runner.invoke(app, arguments)
    assert output.exit_code == 2 and output.stdout == ""
    assert json.loads(output.stderr)["schema"] == "changecost/error-v1"
    assert "private" not in output.stderr and "Traceback" not in output.stderr
    console = subprocess.run(
        [sys.executable, "-m", "changecost", *arguments], capture_output=True, text=True
    )
    assert console.returncode == 2 and console.stdout == ""
    assert json.loads(console.stderr)["schema"] == "changecost/error-v1"
    assert "private" not in console.stderr and "Traceback" not in console.stderr
    assert store.path.read_bytes() == before


@pytest.mark.parametrize("kind", ["quote", "computed_settlement"])
@pytest.mark.parametrize("boundary", ["own", "later", "earlier", "time"])
@pytest.mark.parametrize("entrypoint", ["check", "inspect"])
def test_original_cutoff_bound_to_result_availability(tmp_path, kind, boundary, entrypoint):
    from datetime import timedelta

    store, record = priced(tmp_path) if kind == "quote" else settlement(tmp_path)
    original = record.cutoff
    if boundary in {"later", "time"}:
        store.clock = lambda: original.at + timedelta(minutes=1)
        peer(store, "unrelated-later", "999")
    with store.connect() as connection:
        own_sequence = connection.execute(
            "SELECT sequence FROM records WHERE kind=? AND id=?", (kind, record.record_id)
        ).fetchone()[0]
        latest_sequence = connection.execute("SELECT sequence FROM metadata").fetchone()[0]
    updates = {
        "own": {"sequence": own_sequence},
        "later": {"sequence": latest_sequence},
        "earlier": {"sequence": original.sequence - 1},
        "time": {"at": store.clock()},
    }
    changed = tamper(store, record, cutoff=original.model_copy(update=updates[boundary]))
    before = store.path.read_bytes()
    if entrypoint == "check":
        result = evaluate(store, changed)
        assert result["status"] == "unknown" and result["comparison"] is None
    else:
        result = inspect_selected_computation(store, changed)
        assert result["replay_eligibility"] == "replay_unavailable"
    assert store.path.read_bytes() == before


@pytest.mark.parametrize("kind", ["quote", "computed_settlement"])
@pytest.mark.parametrize("operation", ["check", "explain"])
@pytest.mark.parametrize("format", ["json", "human"])
@pytest.mark.parametrize(
    "corruption",
    [
        ("sequence", "private-corrupt-sequence"),
        ("sequence", 1.5),
        ("sequence", 0),
        ("available_at", "private-corrupt-availability"),
    ],
)
@pytest.mark.parametrize(
    "trust_state", ["supported", "algorithm", "policy", "missing", "duplicate"]
)
def test_corrupt_result_availability_safe_cli(
    tmp_path, kind, operation, format, corruption, trust_state
):
    column, value = corruption
    store, record = availability_trust_fixture(tmp_path, kind, trust_state)
    statement = {
        "sequence": "UPDATE records SET sequence=? WHERE kind=? AND id=?",
        "available_at": "UPDATE records SET available_at=? WHERE kind=? AND id=?",
    }[column]
    with store.connect() as connection:
        connection.execute(statement, (value, kind, record.record_id))
    before = store.path.read_bytes()
    args = (
        check_args(record)
        if operation == "check"
        else ["explain", "--record-kind", kind, "--record-id", record.record_id]
    )
    checked = runner.invoke(app, ["--db", str(store.path), "--format", format, *args])
    assert checked.exit_code == 2 and checked.stdout == ""
    assert checked.stderr
    assert "private-corrupt" not in checked.stderr and "Traceback" not in checked.stderr
    assert store.path.read_bytes() == before


@pytest.mark.parametrize("clone_receipt", [False, True])
def test_settlement_operation_receipt_identity(tmp_path, clone_receipt):
    from changecost.serialization import ContractError
    from tests.test_reconciliation import compute

    store, record = settlement(tmp_path)
    assert evaluate(store, record)["status"] == "within_budget"
    assert compute(store) == record
    altered = tamper(store, record, operation_id="different-operation")
    if clone_receipt:
        with store.connect() as connection:
            connection.execute(
                "INSERT INTO computations SELECT ?,request,record_id FROM computations "
                "WHERE operation_id=?",
                (altered.operation_id, record.operation_id),
            )
    before = store.path.read_bytes()
    output = evaluate(store, altered)
    assert output["status"] == "unknown" and output["comparison"] is None
    assert not inspect_selected_computation(store, altered)["local_computation"]
    with pytest.raises(ContractError):
        compute(store)
    assert store.path.read_bytes() == before


@pytest.mark.parametrize("kind", ["quote", "computed_settlement"])
@pytest.mark.parametrize("field", ["origin_store_id", "recorded_at", "effective_at"])
@pytest.mark.parametrize("output_format", ["json", "human"])
def test_generated_header_replay_authority(tmp_path, kind, field, output_format):
    from datetime import timedelta

    store, record = priced(tmp_path) if kind == "quote" else settlement(tmp_path)
    assert evaluate(store, record)["comparison"] is not None
    changed = tamper(
        store,
        record,
        **{
            field: "foreign"
            if field == "origin_store_id"
            else record.cutoff.at - timedelta(seconds=1)
        },
    )
    before = store.path.read_bytes()
    output = runner.invoke(
        app, ["--db", str(store.path), "--format", output_format, *check_args(changed)]
    )
    assert output.exit_code == 0, output.output
    if output_format == "json":
        value = json.loads(output.stdout)
        assert value["status"] == "unknown" and value["comparison"] is None
    else:
        assert "unknown" in output.stdout
    inspected = inspect_selected_computation(store, changed)
    assert inspected.get("replay_eligibility") == "replay_unavailable"
    assert store.path.read_bytes() == before


@pytest.mark.parametrize("different_scope", [False, True])
def test_settlement_replay_rejects_coherent_rerooting(tmp_path, different_scope):
    store, first = settlement(tmp_path)
    from changecost.reconciliation import compute_settlement

    second_scope = scope()
    if different_scope:
        second_scope = second_scope.model_copy(
            update={"economic": second_scope.economic.model_copy(update={"basis": "other"})}
        )
    # Scope changes do not create a different revision chain for the same Change.
    second = compute_settlement(store, "change", second_scope, "second")
    assert second.previous is not None and second.previous.record_id == first.record_id
    if not different_scope:
        assert evaluate(store, second)["comparison"] is not None
    changed = tamper(store, second, previous=None, ledger_id="coherently-new-ledger")
    before = store.path.read_bytes()
    result = evaluate(store, changed)
    assert result["status"] == "unknown" and result["comparison"] is None
    assert "historical_inputs_unavailable_or_result_mismatch" in result["reasons"]
    assert store.path.read_bytes() == before


def test_settlement_predecessor_replay_ignores_later_computations(tmp_path):
    from tests.test_reconciliation import compute

    store, first = settlement(tmp_path)
    second = compute(store, op="second")
    third = compute(store, op="third")
    before = store.path.read_bytes()
    assert third.previous is not None
    assert third.previous.record_id == second.record_id
    for record in (first, second, third):
        assert evaluate(store, record)["comparison"] is not None
    assert store.path.read_bytes() == before


@pytest.mark.parametrize("kind", ["quote", "computed_settlement"])
@pytest.mark.parametrize("matching_request", [False, True])
@pytest.mark.parametrize("entrypoint", ["check", "inspect", "retry"])
def test_duplicate_receipts_deny_authority(tmp_path, kind, matching_request, entrypoint):
    from changecost.quotes import compute_quote
    from changecost.serialization import ContractError
    from tests.test_reconciliation import compute

    store, record = priced(tmp_path) if kind == "quote" else settlement(tmp_path)
    assert evaluate(store, record)["comparison"] is not None
    with store.connect() as connection:
        request, record_id = connection.execute(
            "SELECT request,record_id FROM computations WHERE record_id=?", (record.record_id,)
        ).fetchone()
        connection.execute(
            "INSERT INTO computations VALUES (?,?,?)",
            ("receipt-alias", request if matching_request else "conflicting-request", record_id),
        )
    before = store.path.read_bytes()
    if entrypoint == "check":
        output = evaluate(store, record)
        assert output["status"] == "unknown" and output["comparison"] is None
        assert "no_local_computation_receipt" in output["reasons"]
    if entrypoint == "inspect":
        assert not inspect_selected_computation(store, record)["local_computation"]
    if entrypoint == "retry":
        operations = ["quote-operation" if kind == "quote" else "op", "receipt-alias"]
        for operation in operations:
            with pytest.raises(ContractError):
                if kind == "quote":
                    compute_quote(store, "target", scope(), operation, minimum=2)
                else:
                    compute(store, op=operation)
    assert store.path.read_bytes() == before


def availability_trust_fixture(tmp_path, kind, trust_state):
    store, record = priced(tmp_path) if kind == "quote" else settlement(tmp_path)
    if trust_state == "algorithm":
        record = tamper(store, record, algorithm_version="unsupported/v99")
    if trust_state == "policy":
        if isinstance(record, Quote):
            assert record.estimation is not None
            record = tamper(
                store,
                record,
                estimation=record.estimation.model_copy(
                    update={"policy_version": "unsupported/v99"}
                ),
            )
        else:
            record = tamper(store, record, policy_version="unsupported/v99")
    if trust_state in ("missing", "duplicate"):
        with store.connect() as connection:
            if trust_state == "missing":
                connection.execute(
                    "DELETE FROM computations WHERE record_id=?", (record.record_id,)
                )
            else:
                connection.execute(
                    "INSERT INTO computations SELECT ?,request,record_id FROM computations "
                    "WHERE record_id=?",
                    ("availability-alias", record.record_id),
                )
    return store, record


@pytest.mark.parametrize("output_format", ["json", "human"])
@pytest.mark.parametrize("column", ["sequence", "available_at"])
def test_legacy_selected_availability_precedes_claim(tmp_path, output_format, column):
    store = setup(tmp_path)
    record = legacy_claim(store)
    assert evaluate(store, record)["status"] == "unknown"
    query = {
        "sequence": "UPDATE records SET sequence=? WHERE kind=? AND id=?",
        "available_at": "UPDATE records SET available_at=? WHERE kind=? AND id=?",
    }[column]
    with store.connect() as connection:
        connection.execute(query, ("private-corrupt-value", record.kind, record.record_id))
    before = store.path.read_bytes()
    output = runner.invoke(
        app, ["--db", str(store.path), "--format", output_format, *check_args(record)]
    )
    assert output.exit_code == 2 and output.stdout == ""
    assert output.stderr and "private-corrupt" not in output.stderr
    assert "Traceback" not in output.stderr and store.path.read_bytes() == before
