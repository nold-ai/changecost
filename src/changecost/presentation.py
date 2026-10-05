"""Safe operation presentation and parser diagnostics."""

from __future__ import annotations

import json
import sys
import unicodedata

from typer import _click as click
from typer.core import TyperGroup
from typer.exceptions import Exit


def display(value: str) -> str:
    return "".join(
        f"\\u{ord(c):04x}" if unicodedata.category(c) in {"Cc", "Cf", "Cs", "Zl", "Zp"} else c
        for c in value
    )


def human(value, depth=0) -> str:
    if isinstance(value, dict):
        return "\n".join(
            f"{'  ' * depth}{display(str(k))}:\n{human(v, depth + 1)}"
            if isinstance(v, (dict, list))
            else f"{'  ' * depth}{display(str(k))}: {display(str(v))}"
            for k, v in value.items()
        )
    if isinstance(value, list):
        return "\n".join(human(v, depth) for v in value) or "  " * depth + "none"
    return "  " * depth + display(str(value))


def error_output(format: str, code="invalid_request") -> None:
    message = (
        "invalid request" if code == "invalid_request" else "unavailable local store or artifact"
    )
    value = dict(schema="changecost/error-v1", code=code, message=message)
    click.echo(message if format == "human" else json.dumps(value), err=True)


def requested_format(command, args) -> str:
    # Reuse the root parser without callbacks: consume option values, stop at the
    # actual command, and preserve the parser's last-value semantics on failures.
    with click.Context(command, resilient_parsing=True) as context:
        values, _arguments, _order = command.make_parser(context).parse_args(list(args))
    return "human" if values.get("format") == "human" else "json"


class SafeGroup(TyperGroup):
    """Intercept Click parser failures before it echoes rejected argument values."""

    def main(
        self,
        args=None,
        prog_name=None,
        complete_var=None,
        standalone_mode=True,
        windows_expand_args=True,
        **extra,
    ):
        arguments = list(sys.argv[1:] if args is None else args)
        standalone = standalone_mode
        try:
            result = super().main(
                args=arguments,
                prog_name=prog_name,
                complete_var=complete_var,
                standalone_mode=False,
                windows_expand_args=windows_expand_args,
                **extra,
            )
            if standalone:
                raise SystemExit(result if isinstance(result, int) else 0)
            return result
        except click.ClickException as exc:
            error_output(requested_format(self, arguments))
            if standalone:
                raise SystemExit(2) from exc
            raise Exit(2) from exc
