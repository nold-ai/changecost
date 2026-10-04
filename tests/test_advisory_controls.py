"""Bounded scenario inventory and seeded real-target detector controls."""

from itertools import product

import pytest

from tests.advisory_oracle import advice
from tests.test_advisory import evaluate, priced, settlement, tamper


def test_bounded_scenario_inventory(tmp_path):
    # Literal cases are independent of production selection/replay implementations.
    for value, complete, budget in product(("0", "10", "20"), (False, True), ("0", "10", "15")):
        path = tmp_path / f"v{value}-c{complete}-b{budget}"
        path.mkdir()
        store, record = settlement(path, value, complete)
        output = evaluate(store, record, budget)
        assert output["status"] == advice(value, budget, complete=complete)
        assert (output["comparison"] is not None) == complete


def detect_unknown(store, record):
    assert evaluate(store, record)["status"] == "unknown"


def test_receipt_authority_fault_detected(tmp_path, monkeypatch):
    import changecost.advisory as target

    store, record = priced(tmp_path)
    with store.connect() as connection:
        connection.execute("DELETE FROM computations")
    detect_unknown(store, record)
    with monkeypatch.context() as control:
        control.setattr(target, "local_verification", lambda *args: (True, []))
        with pytest.raises(AssertionError):
            detect_unknown(store, record)
    detect_unknown(store, record)


def test_historical_result_fault_detected(tmp_path, monkeypatch):
    import changecost.advisory as target

    store, record = settlement(tmp_path)
    record = tamper(
        store, record, subtotals=[record.subtotals[0].model_copy(update={"amount": "999"})]
    )
    detect_unknown(store, record)
    with monkeypatch.context() as control:
        control.setattr(target, "settlement_reproduced", lambda *args: True)
        with pytest.raises(AssertionError):
            detect_unknown(store, record)
    detect_unknown(store, record)


def test_completeness_fault_detected(tmp_path, monkeypatch):
    import changecost.advisory as target

    store, record = settlement(tmp_path, "20", False)
    detect_unknown(store, record)
    real = target.record_values

    def faulty(*args):
        declared, selected, complete, reasons = real(*args)
        return declared, selected, True, []

    with monkeypatch.context() as control:
        control.setattr(target, "record_values", faulty)
        with pytest.raises(AssertionError):
            detect_unknown(store, record)
    detect_unknown(store, record)


def test_float_and_zero_faults_detected(tmp_path, monkeypatch):
    import changecost.advisory as target

    value, budget = "1.000000000000000000000000001", "1"

    def detector():
        assert target.compare(value, budget) == advice(value, budget)

    detector()
    with monkeypatch.context() as control:
        control.setattr(
            target,
            "compare",
            lambda value, budget: (
                "over_budget" if float(value) > float(budget) else "within_budget"
            ),
        )
        with pytest.raises(AssertionError):
            detector()
    detector()
    store, record = settlement(tmp_path, "0", True)

    def zero_detector():
        assert evaluate(store, record, "0")["status"] == "within_budget"

    zero_detector()
    real = target.record_values

    def faulty(*args):
        declared, selected, complete, reasons = real(*args)
        assert selected is not None
        return declared, selected, complete and bool(float(selected["amount"])), reasons

    with monkeypatch.context() as control:
        control.setattr(target, "record_values", faulty)
        with pytest.raises(AssertionError):
            zero_detector()
    zero_detector()


def test_current_history_replay_fault_detected(tmp_path, monkeypatch):
    import changecost.quotes as target
    from tests.test_quotes import peer

    store, record = priced(tmp_path)
    original = evaluate(store, record)
    peer(store, "later", "999")

    def detector():
        assert evaluate(store, record) == original

    detector()
    real = target.snapshot_records

    def current_history(connection, cutoff, records=None):
        sequence = connection.execute("SELECT sequence FROM metadata").fetchone()[0]
        return real(connection, cutoff.model_copy(update={"sequence": sequence}), records)

    with monkeypatch.context() as control:
        control.setattr(target, "snapshot_records", current_history)
        with pytest.raises(AssertionError):
            detector()
    detector()
