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
from changecost.claude_local import ClaudeProjectImportError
from changecost.codex_local import NativeImportError, select_codex_file
from changecost.codex_session_counter import CounterError
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
from changecost.sessions import CaptureOperation, Measurement, SessionError, Sessions
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
    except SessionError as exc:
        value = dict(schema="changecost/error-v1", code=exc.code, message=exc.message)
        format = get_current_context().meta.get("format", "json")
        typer.echo(human(value) if format == "human" else json.dumps(value), err=True)
        raise typer.Exit(2) from exc
    except CounterError as exc:
        value = exc.report()
        format = get_current_context().meta.get("format", "json")
        typer.echo(human(value) if format == "human" else json.dumps(value), err=True)
        raise typer.Exit(2) from exc
    except (NativeImportError, ClaudeProjectImportError) as exc:
        diagnostic = exc.diagnostic.model_dump(exclude_none=True)
        value = dict(schema="changecost/error-v1", message="native import rejected", **diagnostic)
        format = get_current_context().meta.get("format", "json")
        typer.echo(human(value) if format == "human" else json.dumps(value), err=True)
        raise typer.Exit(2) from exc
    except ContractError as exc:
        error_output(get_current_context().meta.get("format", "json"))
        raise typer.Exit(2) from exc
    except (ValueError, OSError, sqlite3.Error) as exc:
        error_output(get_current_context().meta.get("format", "json"))
        raise typer.Exit(2) from exc


@app.command("evaluate-synthetic")
def evaluate_synthetic_command(
    history: Annotated[Path, typer.Option(help="Portable declared synthetic history.")],
    protocol: Annotated[Path, typer.Option(help="Pre-registered evaluation protocol.")],
    measure_runs: Annotated[
        int, typer.Option(help="Separate overhead measurements, 0 to 20 runs.")
    ] = 0,
) -> None:
    """Report an isolated synthetic evaluation without using the runtime store."""
    from changecost.evaluation import evaluate_synthetic

    result: dict[str, Any] = {}

    def operation():
        nonlocal result
        result = evaluate_synthetic(history, protocol, measure_runs=measure_runs)
        return result

    execute(operation)
    if result and result["core"]["economic"]["status"] == "comparison_error":
        raise typer.Exit(2)


session_app = typer.Typer(help="Local provisional manual or Codex session estimates and totals.")
app.add_typer(session_app, name="session")


@session_app.callback()
def session_root(
    context: typer.Context,
    session_db: Annotated[
        Path, typer.Option("--session-db", help="Separate local session SQLite file.")
    ] = Path(".changecost/sessions.sqlite3"),
) -> None:
    context.obj = Sessions(session_db)


@session_app.command("start")
def session_start(
    context: typer.Context,
    session_id: str,
    task_kind: Annotated[str, typer.Option(help="Exact task-kind cohort label.")],
    cohort_context: Annotated[
        str, typer.Option("--context", help="Exact ecosystem/context label.")
    ],
    guess: Annotated[int | None, typer.Option(help="Cold-start guess in target tokens.")] = None,
    source: Annotated[str, typer.Option(help="manual or codex provisional target.")] = "manual",
) -> None:
    """Freeze a before-work estimate from previously measured matching sessions."""
    execute(lambda: context.obj.start(session_id, task_kind, cohort_context, guess, source=source))


@session_app.command("finish")
def session_finish(
    context: typer.Context,
    session_id: str,
    tokens: Annotated[int, typer.Option(help="Measured nonnegative total tokens.")],
    outcome: Annotated[str, typer.Option(help="completed, failed, or abandoned.")],
    coverage: Annotated[
        str, typer.Option(help="declared_session_total or partial.")
    ] = "declared_session_total",
) -> None:
    """Record the first manual measurement and compare it with the frozen estimate."""
    execute(lambda: context.obj.measure(session_id, Measurement(tokens, outcome, coverage)))


@session_app.command("correct")
def session_correct(
    context: typer.Context,
    session_id: str,
    tokens: Annotated[int, typer.Option(help="Corrected nonnegative total tokens.")],
    outcome: Annotated[str, typer.Option(help="completed, failed, or abandoned.")],
    revision: Annotated[int, typer.Option(help="Expected prior measurement revision.")],
    reason: Annotated[str, typer.Option(help="Nonblank reason retained with the correction.")],
    coverage: Annotated[
        str, typer.Option(help="declared_session_total or partial.")
    ] = "declared_session_total",
) -> None:
    """Append a correction while preserving all previous measurements and forecasts."""
    execute(
        lambda: context.obj.measure(
            session_id, Measurement(tokens, outcome, coverage, revision, reason)
        )
    )


@session_app.command("observe-codex")
def session_observe_codex(
    context: typer.Context,
    session_id: str,
    file: Annotated[
        Path, typer.Option("--file", help="Explicit selected exact Codex source file.")
    ],
    repository_id: Annotated[str, typer.Option(help="Explicit repository association.")],
) -> None:
    """Attach approved finite partial diagnostics, without a session total or learning."""
    execute(lambda: context.obj.observe_codex(session_id, select_codex_file(repository_id, file)))


@session_app.command("capture-codex")
def session_capture_codex(
    context: typer.Context,
    session_id: str,
    file: Annotated[Path, typer.Option("--file", help="Explicit selected local Codex file.")],
    repository_id: Annotated[str, typer.Option(help="Explicit repository association.")],
    outcome: Annotated[str, typer.Option(help="completed, failed, or abandoned.")],
    revision: Annotated[
        int | None, typer.Option(help="Expected predecessor for changed capture.")
    ] = None,
    reason: Annotated[str | None, typer.Option(help="Nonblank reason for changed capture.")] = None,
) -> None:
    """Capture a provisional lifetime counter and explicit outcome in one operation."""
    execute(
        lambda: context.obj.capture_codex(
            session_id, file, repository_id, CaptureOperation(outcome, revision, reason)
        )
    )


@session_app.command("show")
def session_show(context: typer.Context, session_id: str) -> None:
    """Inspect one frozen estimate, measurements, revisions and current error."""
    execute(lambda: context.obj.report(session_id))


@session_app.command("history")
def session_history(
    context: typer.Context,
    task_kind: Annotated[str | None, typer.Option(help="Filter exact task kind.")] = None,
    cohort_context: Annotated[
        str | None, typer.Option("--context", help="Filter exact context.")
    ] = None,
    source: Annotated[str, typer.Option(help="manual or codex separate history.")] = "manual",
) -> None:
    """Show chronological sessions, cumulative errors and explicit exclusions."""
    execute(lambda: context.obj.report(task_kind=task_kind, context=cohort_context, source=source))


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
            return demand_request(context, context.params)
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


def demand_request(context, options):
    from changecost.demand import DemandRequest, compute_demand

    economic = [options[name] for name in ("economic_kind", "unit", "basis", "currency")]
    source = context.get_parameter_source("minimum")
    if any(v is not None for v in economic) or options["minimum"] != 20 or source.name != "DEFAULT":
        raise ContractError("demand cannot use economic selectors")
    if options["assessment_id"] is None or options["ecosystem_id"] is None:
        raise ContractError("demand requires assessment and ecosystem")
    selectors = DemandRequest(
        **{
            name: options[name]
            for name in (
                "repository_id",
                "change_id",
                "operation_id",
                "assessment_id",
                "ecosystem_id",
                "price_id",
            )
        }
    )
    return compute_demand(context.obj, selectors)


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
    import_codex: Path | None = None,
    import_claude_project: Path | None = None,
    source_profile: str | None = None,
    source_sha256: str | None = None,
    compute: bool = False,
    operation_id: str | None = None,
    economic_kind: str | None = None,
    unit: str | None = None,
    currency: str | None = None,
    basis: str | None = None,
    source_start: str | None = None,
    source_end: str | None = None,
) -> None:
    """Import approved native diagnostics, normalized economics, or declare/compute facts."""
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
        native = any(
            value is not None
            for value in (import_codex, import_claude_project, source_profile, source_sha256)
        )
        if native:
            if (import_codex is None) == (import_claude_project is None):
                raise ContractError("select exactly one native import mode")
            request = claude_native_request if import_claude_project is not None else native_request
            return request(
                context.obj,
                dict(
                    repository_id=repository_id,
                    path=import_claude_project
                    if import_claude_project is not None
                    else import_codex,
                    profile_id=source_profile,
                    expected_sha256=source_sha256,
                ),
                (economic, fields, correct_outcome, correct_interval),
                (change_id, *lifecycle),
            )
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


def native_request(store, selection, conflicting_modes, conflicting_selectors):
    if any(conflicting_modes) or any(value is not None for value in conflicting_selectors):
        raise ContractError("settle modes are mutually exclusive")
    from changecost.codex_local import CodexSelection, import_codex_file

    return import_codex_file(store, CodexSelection.model_validate(selection))


def claude_native_request(store, selection, conflicting_modes, conflicting_selectors):
    if any(conflicting_modes) or any(value is not None for value in conflicting_selectors):
        raise ContractError("settle modes are mutually exclusive")
    from changecost.claude_local import ClaudeProjectSelection, import_claude_project

    return import_claude_project(store, ClaudeProjectSelection.model_validate(selection))


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
