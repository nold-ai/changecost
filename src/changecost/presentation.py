"""Safe operation presentation and parser diagnostics."""

from __future__ import annotations

import json
import sys
import unicodedata
from decimal import Decimal

from typer import _click as click
from typer.core import TyperGroup
from typer.exceptions import Exit


def display(value: str) -> str:
    return "".join(
        f"\\u{ord(c):04x}" if unicodedata.category(c) in {"Cc", "Cf", "Cs", "Zl", "Zp"} else c
        for c in value
    )


def human(value, depth=0) -> str:
    if (
        depth == 0
        and isinstance(value, dict)
        and value.get("schema")
        in {"changecost/manual-sessions-v1", "changecost/codex-provisional-sessions-v1"}
    ):
        return human_sessions(value)
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


def _amount(value) -> str:
    return "unknown" if value is None else format(Decimal(str(value)), ",f")


def _session_error(error: dict) -> str:
    if error["excluded_reason"] is not None:
        return f"Error unavailable ({error['excluded_reason']})"
    signed = Decimal(error["signed_tokens"])
    direction = "low" if signed < 0 else "high" if signed > 0 else "matched"
    absolute = _amount(error["absolute_tokens"])
    percentage = error["absolute_percentage_error"]
    relative = (
        "relative error unavailable (zero target)"
        if percentage is None
        else f"absolute relative error {Decimal(percentage['rounded_decimal']):.2f}%"
    )
    return f"Estimate {direction} | absolute error {absolute} tokens | {relative}"


def _session_lines(value: dict) -> list[str]:
    codex = value.get("source") == "codex"
    forecast = value["forecast"]
    capture = value.get("capture")
    actual = capture if codex else value["measurement"]
    outcome = actual["outcome"] if actual else "in progress"
    source = "Codex provisional" if codex else "Manual provisional"
    origin = forecast["source"].replace("_", " ")
    estimate = (
        f"Estimate {_amount(forecast['amount'])} tokens | {origin} | "
        f"{forecast['sample_count']} samples"
    )
    if forecast["input_guess"] is not None:
        estimate += f" | original guess {_amount(forecast['input_guess'])}"
    total = "Source-reported lifetime counter" if codex else "Manual measured total"
    quantity = (
        capture["snapshot"]["reported_tokens"]
        if capture
        else (actual["tokens"] if actual else None)
    )
    lines = [
        f"{value['session_id']} | {outcome} | {source}",
        estimate,
        f"{total} {_amount(quantity)} tokens",
        _session_error(value["error"]),
    ]
    if actual:
        lines.append(f"Revision {actual['revision']} | outcome {outcome}")
    if not codex and actual:
        lines.append(f"Coverage {actual['coverage']}")
    native = value.get("native_diagnostics")
    if native:
        lines.append(
            f"Finite Codex diagnostics (manual: False) | {native['request_count']} requests | "
            f"{native['fact_count']} category facts | "
            "native_partial_diagnostics | learning excluded"
        )
    return lines


def _history_row(value: dict) -> str:
    codex = value.get("source") == "codex"
    actual = value.get("capture") if codex else value["measurement"]
    quantity = (
        actual["snapshot"]["reported_tokens"]
        if codex and actual
        else (actual["tokens"] if actual else None)
    )
    forecast = value["forecast"]
    origin = forecast["source"].replace("_", " ")
    total_label = "reported" if codex else "measured"
    error = value["error"]
    error_text = f"error unavailable ({error['excluded_reason']})"
    if error["excluded_reason"] is None:
        signed = Decimal(error["signed_tokens"])
        direction = "low" if signed < 0 else "high" if signed > 0 else "matched"
        error_text = f"error {_amount(error['absolute_tokens'])} {direction}"
        if error["absolute_percentage_error"] is not None:
            percent = Decimal(error["absolute_percentage_error"]["rounded_decimal"])
            error_text += f" ({percent:.2f}%)"
    revision = f"r{actual['revision']} {actual['outcome']}" if actual else "in progress"
    row = (
        f"{value['session_id']} | estimate {_amount(forecast['amount'])} "
        f"({origin}, n={forecast['sample_count']}) | {total_label} {_amount(quantity)} | "
        f"{error_text} | {revision}"
    )
    if value.get("native_diagnostics"):
        row += " | finite diagnostics excluded"
    return row


def human_sessions(value: dict) -> str:
    """Render safe session summaries without expanding private-source fact arrays."""
    codex = value.get("source") == "codex"
    if "session_id" in value:
        lines = _session_lines(value)
    else:
        lines = ["Codex provisional history" if codex else "Manual provisional history"]
        for session in value["sessions"]:
            lines.append(_history_row(session))
        evaluation = value["evaluation"]
        mae = evaluation["mean_absolute_error"]
        amount = "unknown" if mae is None else _amount(mae["rounded_decimal"])
        lines.append(
            f"Descriptive MAE {amount} tokens | evaluated {evaluation['included_count']} | "
            f"excluded {evaluation['excluded_count']}"
        )
        if codex:
            lines.append(
                f"Learning attempts {value['learning_count']} (latest capture once per attempt)"
            )
        if evaluation["excluded"]:
            lines.append(
                "Exclusions "
                + ", ".join(
                    f"{key}={count}" for key, count in sorted(evaluation["excluded"].items())
                )
            )
    if codex:
        lines.extend(
            [
                "Coverage UNKNOWN | completeness UNKNOWN | finality UNKNOWN | "
                "subagent inclusion UNKNOWN",
                "Producer claim unverified | lifetime target may include work before start | "
                "no billing or calibration authority",
            ]
        )
    return "\n".join(display(line) for line in lines)


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
