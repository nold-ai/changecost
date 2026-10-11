"""Offline core contracts, explicit lifecycle declarations and portable records."""

from __future__ import annotations

import json
import os
import sqlite3
import tempfile
from importlib.metadata import version
from pathlib import Path
from typing import Annotated, Any

import typer
from typer._click.globals import get_current_context

from changecost import operations
from changecost.models import (
    ComputedSettlement,
    EconomicScope,
    RecordRef,
    Run,
    RunRef,
    timestamp,
)
from changecost.presentation import SafeGroup, error_output, human
from changecost.serialization import ContractError, dumps_bundle, loads_bundle
from changecost.store import Store, key, lookup, reference, subject

app = typer.Typer(
    cls=SafeGroup, add_completion=False, help="ChangeCost offline contract and lifecycle records."
)


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
    format: Annotated[str, typer.Option("--format", help="Output format: json or human.")] = "json",
    db: Annotated[
        Path, typer.Option(help="Local SQLite store; opened only by valid operations.")
    ] = Path(".changecost/changecost.sqlite3"),
) -> None:
    """Keep help, version and invalid invocation free of store writes."""
    if format not in {"json", "human"}:
        error_output("json")
        raise typer.Exit(2)
    context.meta["format"] = format
    context.obj = Store(db)
    if context.invoked_subcommand is None:
        error_output(format)
        raise typer.Exit(2)


def execute(operation) -> None:
    try:
        result = operation()
        if hasattr(result, "model_dump"):
            result = result.model_dump(mode="json", by_alias=True)
        format = get_current_context().meta.get("format", "json")
        typer.echo(human(result) if format == "human" else json.dumps(result, ensure_ascii=True))
    except ContractError as exc:
        error_output(get_current_context().meta.get("format", "json"))
        raise typer.Exit(2) from exc
    except (ValueError, OSError, sqlite3.Error) as exc:
        error_output(get_current_context().meta.get("format", "json"))
        raise typer.Exit(2) from exc


def run_selector(repository_id, provider, surface, run_id) -> RunRef:
    return RunRef.model_validate(
        dict(repository_id=repository_id, provider=provider, surface=surface, run_id=run_id)
    )


def target(store, repository_id, change_id, provider, surface, run_id) -> RecordRef:
    is_run = any(value is not None for value in (provider, surface, run_id))
    if is_run and change_id is not None:
        raise ContractError("select a Change or a complete RunRef, not both")
    records = {key(reference(r)): r for r in store.records()}
    if is_run:
        return reference(
            operations.run_in(records, run_selector(repository_id, provider, surface, run_id))
        )
    if repository_id is None or change_id is None:
        raise ContractError("incomplete Change selector")
    change = operations.change_in(records, repository_id, change_id)
    if change is None:
        raise ContractError("unknown or incomplete Change selector")
    return reference(change)


@app.command()
def bind(
    context: typer.Context,
    repository_id: str | None = None,
    change_id: str | None = None,
    provider: str | None = None,
    surface: str | None = None,
    run_id: str | None = None,
    register_change: bool = False,
    register_run: bool = False,
    evidence_id: str | None = None,
    import_artifact: Path | None = None,
    change_shape: str | None = None,
    trajectory: str | None = None,
    execution_profile: str | None = None,
    work_start: str | None = None,
) -> None:
    """Register identities, bind explicit references, or import a v1 bundle."""
    options = dict(
        repository_id=repository_id,
        change_id=change_id,
        provider=provider,
        surface=surface,
        run_id=run_id,
        register_change=register_change,
        register_run=register_run,
        evidence_id=evidence_id,
        import_artifact=import_artifact,
        change_shape=change_shape,
        trajectory=trajectory,
        execution_profile=execution_profile,
        work_start=work_start,
    )
    execute(lambda: bind_request(context.obj, options))


def bind_request(store: Store, args: dict) -> Any:
    supplied = {
        name
        for name, value in args.items()
        if (value if name in {"register_change", "register_run"} else value is not None)
    }
    modes = {"register_change", "register_run", "evidence_id", "import_artifact"}
    if len(supplied & modes) > 1:
        raise ContractError("binding modes are mutually exclusive")
    if args["import_artifact"] is not None:
        if supplied - {"import_artifact"}:
            raise ContractError("artifact import cannot use other binding options")
        store.import_bundle(loads_bundle(args["import_artifact"].read_text()))
        return {"imported": True, "provider_support": "not_verified"}
    if args["register_change"]:
        return register_change_request(store, args)
    if any(args[name] is not None for name in ("change_shape", "trajectory", "execution_profile")):
        raise ContractError("features require Change registration")
    ref = run_selector(args["repository_id"], args["provider"], args["surface"], args["run_id"])
    return bind_run_request(store, args, ref)


def register_change_request(store, args):
    if any(args[name] is not None for name in ("provider", "surface", "run_id", "work_start")):
        raise ContractError("Change registration cannot use Run fields")
    return operations.register_change(
        store,
        args["repository_id"],
        args["change_id"],
        change_shape=args["change_shape"],
        trajectory=args["trajectory"],
        execution_profile=args["execution_profile"],
    )


def bind_run_request(store, args, ref):
    if args["register_run"]:
        return operations.register_run(
            store,
            ref,
            args["change_id"],
            work_start=timestamp(args["work_start"]) if args["work_start"] is not None else None,
        )
    if args["work_start"] is not None:
        raise ContractError("work start requires registration or settle")
    if args["evidence_id"] is not None:
        if args["change_id"] is not None:
            raise ContractError("evidence binding names a Run, not a Change")
        return operations.bind_evidence(store, args["evidence_id"], ref)
    change = target(store, ref.repository_id, args["change_id"], None, None, None)
    return operations.bind_run(store, ref, change)


@app.command()
def quote(
    context: typer.Context,
    repository_id: Annotated[str, typer.Option()],
    change_id: Annotated[str, typer.Option()],
    operation_id: Annotated[str, typer.Option()],
    economic_kind: Annotated[str | None, typer.Option()] = None,
    unit: Annotated[str | None, typer.Option()] = None,
    basis: Annotated[str | None, typer.Option()] = None,
    currency: Annotated[str | None, typer.Option()] = None,
    minimum: Annotated[int, typer.Option(min=1)] = 20,
    demand: Annotated[bool, typer.Option()] = False,
    assessment_id: Annotated[str | None, typer.Option()] = None,
    ecosystem_id: Annotated[str | None, typer.Option()] = None,
    price_id: Annotated[str | None, typer.Option()] = None,
) -> None:
    """Compute an economic Quote or an explicit separate offline demand forecast."""
    from changecost.quotes import compute_quote

    def operation():
        if demand:
            return demand_request(
                context,
                repository_id,
                change_id,
                operation_id,
                assessment_id,
                ecosystem_id,
                price_id,
                (economic_kind, unit, basis, currency),
                minimum,
            )
        if any(v is not None for v in (assessment_id, ecosystem_id, price_id)):
            raise ContractError("demand selectors require explicit demand mode")
        if any(v is None for v in (economic_kind, unit, basis)):
            raise ContractError("economic mode requires kind, unit and basis")
        scope = EconomicScope.model_validate(
            dict(
                repository_id=repository_id,
                economic=dict(
                    economic_kind=economic_kind, unit=unit, basis=basis, currency=currency
                ),
            )
        )
        return compute_quote(context.obj, change_id, scope, operation_id, minimum)

    execute(operation)


def demand_request(
    context,
    repository_id,
    change_id,
    operation_id,
    assessment_id,
    ecosystem_id,
    price_id,
    economic,
    minimum,
):
    from changecost.demand import compute_demand

    source = context.get_parameter_source("minimum")
    if any(v is not None for v in economic) or minimum != 20 or source.name != "DEFAULT":
        raise ContractError("demand cannot use economic selectors")
    if assessment_id is None or ecosystem_id is None:
        raise ContractError("demand requires assessment and ecosystem")
    return compute_demand(
        context.obj, repository_id, change_id, operation_id, assessment_id, ecosystem_id, price_id
    )


@app.command()
def settle(
    context: typer.Context,
    repository_id: str | None = None,
    change_id: str | None = None,
    provider: str | None = None,
    surface: str | None = None,
    run_id: str | None = None,
    outcome: str | None = None,
    run_outcome: str | None = None,
    work_start: str | None = None,
    work_end: str | None = None,
    correct_outcome: bool = False,
    correct_interval: bool = False,
    reason: str | None = None,
    import_evidence: Path | None = None,
    compute: bool = False,
    operation_id: str | None = None,
    economic_kind: str | None = None,
    unit: str | None = None,
    currency: str | None = None,
    basis: str | None = None,
    source_start: str | None = None,
    source_end: str | None = None,
) -> None:
    """Import normalized economics, compute a revision, or declare lifecycle facts."""
    economic_options = dict(
        economic_kind=economic_kind,
        unit=unit,
        currency=currency,
        basis=basis,
        source_start=source_start,
        source_end=source_end,
    )
    lifecycle = (provider, surface, run_id, outcome, run_outcome, work_start, work_end, reason)

    def perform():
        economic = import_evidence is not None or compute
        fields = operation_id is not None or any(v is not None for v in economic_options.values())
        if economic:
            if any(v is not None for v in lifecycle) or correct_outcome or correct_interval:
                raise ContractError("settle modes are mutually exclusive")
            return economic_request(
                context.obj,
                repository_id,
                change_id,
                import_evidence,
                compute,
                operation_id,
                economic_options,
            )
        if fields:
            raise ContractError("economic options require computation")
        return lifecycle_request()

    def lifecycle_request():
        if outcome is not None and run_outcome is not None:
            raise ContractError("outcome modes are mutually exclusive")
        ref = target(context.obj, repository_id, change_id, provider, surface, run_id)
        if (outcome is not None and ref.kind != "change") or (
            run_outcome is not None and ref.kind != "run"
        ):
            raise ContractError("outcome mode does not match selector")
        return {
            "revisions": [
                r.model_dump()
                for r in operations.declare(
                    context.obj,
                    ref,
                    operations.LifecycleDeclaration(
                        outcome=outcome or run_outcome,
                        start=timestamp(work_start) if work_start is not None else None,
                        end=timestamp(work_end) if work_end is not None else None,
                        correct_outcome=correct_outcome,
                        correct_interval=correct_interval,
                        reason=reason,
                    ),
                )
            ],
            "economic_status": "not_computed",
        }

    execute(perform)


@app.command()
def explain(
    context: typer.Context,
    repository_id: str | None = None,
    change_id: str | None = None,
    provider: str | None = None,
    surface: str | None = None,
    run_id: str | None = None,
    record_kind: str | None = None,
    record_id: str | None = None,
    export_artifact: Path | None = None,
    repository_remainder: bool = False,
    economic_kind: str | None = None,
    unit: str | None = None,
    currency: str | None = None,
    basis: str | None = None,
    source_start: str | None = None,
    source_end: str | None = None,
) -> None:
    """Inspect stored claims/revisions or export a consistent portable snapshot."""

    def perform():
        selectors = (repository_id, change_id, provider, surface, run_id, record_kind, record_id)
        options = dict(
            economic_kind=economic_kind,
            unit=unit,
            currency=currency,
            basis=basis,
            source_start=source_start,
            source_end=source_end,
        )
        if repository_remainder:
            if export_artifact is not None or any(v is not None for v in selectors[1:]):
                raise ContractError("repository reporting cannot use record selectors")
            from changecost.reconciliation import repository_report

            return repository_report(context.obj, economic_scope(repository_id, options))
        if any(v is not None for v in options.values()):
            raise ContractError("economic options require repository remainder mode")
        if export_artifact is not None:
            if any(value is not None for value in selectors):
                raise ContractError("export cannot use record selectors")
            export_file(context.obj, export_artifact)
            return {"exported": True}
        if record_kind is not None or record_id is not None:
            if any(value is not None for value in selectors[:5]) or record_kind in {
                "run",
                "change",
            }:
                raise ContractError("Change/Run inspection requires complete domain selectors")
            ref = RecordRef.model_validate(dict(kind=record_kind, record_id=record_id))
        else:
            ref = target(context.obj, *selectors[:5])
        return inspect_record(context.obj, ref)

    execute(perform)


def inspect_record(store: Store, ref: RecordRef) -> dict:
    if ref.kind == "demand_forecast":
        from changecost.demand import inspect_demand

        return inspect_demand(store, ref)
    if ref.kind == "quote":
        from changecost.quotes import inspect_quote

        return inspect_quote(store, ref)
    bundle = store.export_bundle()
    records = {key(reference(r)): r for r in bundle.records}
    record = lookup(records, ref)
    targets: set[Any] = {key(ref)}
    if isinstance(record, Run):
        targets.add(tuple(record.ref.model_dump().values()))
    revisions = [
        r
        for r in bundle.records
        if r.kind in {"outcome", "interval", "settlement"} and subject(r) in targets
    ]
    result = {
        "record": record.model_dump(mode="json", by_alias=True),
        "revisions": [
            r.model_dump(mode="json", by_alias=True) for r in ordered_revisions(revisions)
        ],
        "availability": [
            o.model_dump(mode="json") for o in bundle.observations if o.reference == ref
        ],
        "provenance_status": "producer_assertion; provider_support_not_verified",
    }
    if isinstance(record, ComputedSettlement):
        from changecost.reconciliation import inspect_computation

        result.update(inspect_computation(store, record))
    return result


def ordered_revisions(revisions):
    """Render graph-validated chains by predecessor, with a stable kind grouping."""
    successors = {key(r.previous): r for r in revisions if r.previous is not None}
    roots = sorted((r for r in revisions if r.previous is None), key=lambda r: r.kind)
    ordered = []
    for current in roots:
        while current is not None:
            ordered.append(current)
            current = successors.get(key(reference(current)))
    return ordered


def export_file(store: Store, path: Path) -> None:
    content = dumps_bundle(store.export_bundle())
    if path.exists():
        raise ContractError("export destination exists")
    fd, temporary = tempfile.mkstemp(prefix=".changecost-export-", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        os.link(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


@app.command()
def check(
    context: typer.Context,
    record_kind: Annotated[str, typer.Option()],
    record_id: Annotated[str, typer.Option()],
    budget: Annotated[str, typer.Option()],
    economic_kind: Annotated[str, typer.Option()],
    unit: Annotated[str, typer.Option()],
    basis: Annotated[str, typer.Option()],
    currency: str | None = None,
    quantile: str | None = None,
    artifact: Path | None = None,
) -> None:
    """Read one explicit historical record and compare a compatible budget."""
    from changecost.advisory import budget_component, check_record

    execute(
        lambda: check_record(
            context.obj,
            RecordRef.model_validate(dict(kind=record_kind, record_id=record_id)),
            budget_component(budget, economic_kind, unit, basis, currency),
            quantile,
            artifact,
        )
    )


def main() -> None:
    """Run the installed command."""
    app()


def economic_scope(repository_id, options) -> EconomicScope:
    return EconomicScope.model_validate(
        dict(
            repository_id=repository_id,
            economic={k: options[k] for k in ("economic_kind", "unit", "currency", "basis")},
            start=options["source_start"],
            end=options["source_end"],
        )
    )


def economic_request(store, repository_id, change_id, path, compute, operation_id, options):
    from changecost.normalized import MAX_INPUT_BYTES, import_evidence, load_input
    from changecost.reconciliation import compute_settlement

    if path is not None:
        if (
            compute
            or change_id is not None
            or operation_id is not None
            or any(v is not None for v in options.values())
        ):
            raise ContractError("normalized import cannot use computation selectors")
        if not repository_id:
            raise ContractError("normalized import requires repository selector")
        with path.open("rb") as stream:
            content = stream.read(MAX_INPUT_BYTES + 1)
        if len(content) > MAX_INPUT_BYTES:
            raise ContractError("normalized input size limit exceeded")
        return {
            "evidence_ids": import_evidence(store, load_input(content.decode()), repository_id),
            "provider_support": "not_verified",
        }
    scope = economic_scope(repository_id, options)
    if not change_id or not operation_id:
        raise ContractError("compute requires Change and operation selectors")
    return compute_settlement(store, change_id, scope, operation_id)
