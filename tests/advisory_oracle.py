"""Independent budget oracle: standard library only, from the advisory scenarios."""

from decimal import Decimal


def advice(amount, budget, *, local=True, reproduced=True, complete=True, compatible=True):
    if amount is None or not all((local, reproduced, complete, compatible)):
        return "unknown"
    return "over_budget" if Decimal(amount) > Decimal(budget) else "within_budget"
