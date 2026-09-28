"""Offline, read-only foundation entry point."""

from importlib.metadata import version
from typing import Annotated

import typer

app = typer.Typer(add_completion=False, help="ChangeCost local CLI foundation.")


def show_version(value: bool) -> None:
    """Read the installed distribution's canonical version."""
    if value:
        typer.echo(version("changecost"))
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def root(
    context: typer.Context,
    version_option: Annotated[
        bool,
        typer.Option(
            "--version", callback=show_version, is_eager=True, help="Show version and exit."
        ),
    ] = False,
) -> None:
    """Display usage until a real operation is implemented."""
    if context.invoked_subcommand is None:
        typer.echo(context.get_help())
        raise typer.Exit(2)


def main() -> None:
    """Run the installed command."""
    app()
