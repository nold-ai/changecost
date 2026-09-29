"""Strict JSON transport without leaking rejected payload values."""

import json

from pydantic import ValidationError

from changecost.models import Bundle


class ContractError(ValueError):
    """A controlled invalid-input or store operation diagnostic."""


def unique_members(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContractError("duplicate JSON member")
        result[key] = value
    return result


def reject_constant(_value):
    raise ContractError("nonfinite JSON value")


def loads_bundle(text: str) -> Bundle:
    try:
        data = json.loads(text, object_pairs_hook=unique_members, parse_constant=reject_constant)
        if not isinstance(data, dict) or data.get("schema") != "changecost/v1":
            raise ContractError("explicit supported bundle schema required")
        records = data.get("records")
        if not isinstance(records, list) or any(
            not isinstance(record, dict) or record.get("schema") != "changecost/v1"
            for record in records
        ):
            raise ContractError("explicit supported record schema required")
        return Bundle.model_validate(data)
    except ContractError:
        raise
    except ValidationError as exc:
        # Values and arbitrary unknown field names may themselves contain private text.
        raise ContractError("invalid portable record fields or values") from exc
    except (ValueError, RecursionError) as exc:
        raise ContractError("invalid portable JSON") from exc


def dumps_bundle(bundle: Bundle) -> str:
    return bundle.model_dump_json(by_alias=True, indent=2) + "\n"
