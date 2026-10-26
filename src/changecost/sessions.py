"""Separate manual and source-reported provisional session experiments."""

from __future__ import annotations

import json
import sqlite3
from collections import Counter
from contextlib import closing, contextmanager, suppress
from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from tempfile import TemporaryDirectory

from changecost.codex_local import CodexSelection, read_codex_file
from changecost.codex_session_counter import TARGET, read_codex_counter
from changecost.demand_history import decimal_string, summaries

APPLICATION_ID = 0x43435331
SCHEMA_VERSION = 3
ALGORITHM = "manual-session-median/v1"
OUTCOMES = {"completed", "failed", "abandoned"}
COVERAGES = {"declared_session_total", "partial"}
TABLES = {
    "events": ("sequence",),
    "sessions": ("session_id", "task_kind", "context", "guess", "start_sequence", "forecast"),
    "measurements": (
        "session_id",
        "revision",
        "sequence",
        "tokens",
        "outcome",
        "coverage",
        "previous_revision",
        "reason",
    ),
}

NATIVE_TABLES = {
    "native_snapshots": ("source_sha256", "repository_id", "diagnostic"),
    "native_links": ("session_id", "source_sha256", "sequence"),
}


CODEX_TABLES = {
    "codex_sessions": ("session_id", "source_identity_sha256", "repository_id"),
    "codex_captures": (
        "session_id",
        "revision",
        "sequence",
        "snapshot",
        "outcome",
        "previous_revision",
        "reason",
    ),
}
SCHEMAS = {1: TABLES, 2: TABLES | NATIVE_TABLES, 3: TABLES | NATIVE_TABLES | CODEX_TABLES}


class SessionError(Exception):
    """Fixed safe diagnostics for the local session command boundary."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def conflict() -> SessionError:
    return SessionError(
        "session_conflict",
        "Session input conflicts with saved history. Inspect show and use an explicit correction.",
    )


def missing() -> SessionError:
    return SessionError(
        "session_not_found", "Session not found. Start it before recording a total."
    )


def unrecognized() -> SessionError:
    return SessionError(
        "session_store_unrecognized",
        "Unrecognized session database. Choose a separate session file.",
    )


def label(value: str, limit: int = 200) -> None:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError("invalid session label")


def tokens(value: int) -> None:
    if type(value) is not int or not 0 <= value <= 2**63 - 1:
        raise ValueError("invalid integer token total")


@dataclass(frozen=True)
class Measurement:
    """One explicit measurement operation and its retry identity."""

    tokens: int
    outcome: str
    coverage: str = "declared_session_total"
    previous_revision: int | None = None
    reason: str | None = None

    def validate(self) -> None:
        tokens(self.tokens)
        if self.outcome not in OUTCOMES or self.coverage not in COVERAGES:
            raise ValueError("invalid measurement declaration")
        if self.previous_revision is None:
            if self.reason is not None:
                raise ValueError("finish cannot supply a correction reason")
            return
        tokens(self.previous_revision)
        if self.previous_revision in {0, 2**63 - 1} or self.reason is None:
            raise ValueError("correction needs a predecessor and reason")
        label(self.reason, 1000)

    def payload(self) -> tuple:
        return self.tokens, self.outcome, self.coverage, self.previous_revision, self.reason


@dataclass(frozen=True)
class CaptureOperation:
    """One explicit terminal capture, optionally correcting an immutable predecessor."""

    outcome: str
    previous_revision: int | None = None
    reason: str | None = None

    def validate(self) -> None:
        if self.outcome not in OUTCOMES:
            raise ValueError("invalid capture outcome")
        if self.previous_revision is None:
            if self.reason is not None:
                raise ValueError("first capture cannot supply a correction reason")
            return
        tokens(self.previous_revision)
        if self.previous_revision in {0, 2**63 - 1} or self.reason is None:
            raise ValueError("capture correction needs a predecessor and reason")
        label(self.reason, 1000)


def codex_header() -> dict:
    return dict(
        schema="changecost/codex-provisional-sessions-v1",
        unit="source_reported_total_tokens",
        source="codex",
        manual=False,
        provisional=True,
        calibrated=False,
        target=dict(TARGET),
        coverage="unknown",
        completeness="unknown",
        finality="unknown",
        subagent_inclusion="unknown",
        producer_verified=False,
        core_numeric_authority=False,
        billing_authority=False,
        calibration_authority=False,
    )


def header() -> dict:
    return dict(
        schema="changecost/manual-sessions-v1",
        unit="total_tokens",
        manual=True,
        provisional=True,
        calibrated=False,
    )


def ratio(numerator: Fraction, denominator: int) -> dict:
    """Keep the unreduced evaluation denominator and label the rounded display."""
    with localcontext() as context:
        context.prec = len(str(abs(numerator.numerator))) + len(str(denominator)) + 20
        value = Decimal(numerator.numerator) / Decimal(numerator.denominator * denominator)
        rounded = value.quantize(Decimal("0.000001"), rounding=ROUND_HALF_EVEN)
    return dict(
        numerator=decimal_string(numerator),
        denominator=denominator,
        rounded_decimal=str(rounded),
        rounding="half_even_6_decimal_places",
    )


def evaluation(forecast: dict, measurement: dict | None) -> dict:
    reason = None
    if measurement is None:
        reason = "pending"
    elif measurement["coverage"] != "declared_session_total":
        reason = "partial_measurement"
    elif forecast["amount"] is None:
        reason = "unknown_forecast"
    if reason:
        return dict(
            signed_tokens=None,
            absolute_tokens=None,
            absolute_percentage_error=None,
            excluded_reason=reason,
        )
    assert measurement is not None
    return quantity_error(forecast, measurement["tokens"])


def quantity_error(forecast: dict, quantity: int) -> dict:
    """Exact forecast-minus-target arithmetic, independent of target authority."""
    signed = Fraction(str(forecast["amount"])) - quantity
    absolute = abs(signed)
    return dict(
        signed_tokens=decimal_string(signed),
        absolute_tokens=decimal_string(absolute),
        absolute_percentage_error=ratio(absolute * 100, quantity) if quantity else None,
        excluded_reason=None,
    )


def codex_evaluation(forecast: dict, capture: dict | None) -> dict:
    if capture is not None and forecast["amount"] is not None:
        return quantity_error(forecast, capture["snapshot"]["reported_tokens"])
    return dict(
        signed_tokens=None,
        absolute_tokens=None,
        absolute_percentage_error=None,
        excluded_reason="pending" if capture is None else "unknown_forecast",
    )


def aggregate(views: list[dict]) -> dict:
    errors = [v["error"] for v in views]
    included = [e for e in errors if e["excluded_reason"] is None]
    absolute = sum((Fraction(e["absolute_tokens"]) for e in included), Fraction(0))
    signed = sum((Fraction(e["signed_tokens"]) for e in included), Fraction(0))
    return dict(
        included_count=len(included),
        excluded_count=len(errors) - len(included),
        excluded=dict(Counter(e["excluded_reason"] for e in errors if e["excluded_reason"])),
        total_signed_error_tokens=decimal_string(signed),
        total_absolute_error_tokens=decimal_string(absolute),
        mean_absolute_error=ratio(absolute, len(included)) if included else None,
    )


class Sessions:
    """Own the local schema, transactional snapshots and append-only measurements."""

    def __init__(self, path: Path):
        self.path = path

    @contextmanager
    def connection(self, *, write=False, create=False):
        if create and not self.path.exists():
            self.create_database()
        if not self.path.exists():
            raise missing()
        mode = "rw" if write else "ro"
        connection = sqlite3.connect(self.path.resolve().as_uri() + "?mode=" + mode, uri=True)
        connection.row_factory = sqlite3.Row
        try:
            try:
                connection.execute("BEGIN IMMEDIATE" if write else "BEGIN")
            except sqlite3.DatabaseError as exc:
                raise unrecognized() from exc
            self.recognize(connection)
            yield connection
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    def create_database(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(dir=self.path.parent, prefix=".sessions-") as directory:
            prepared = Path(directory) / "sessions.sqlite3"
            with closing(sqlite3.connect(prepared)) as connection, connection:
                connection.execute("BEGIN")
                self.initialize(connection)
            with suppress(FileExistsError):
                self.path.hardlink_to(prepared)

    @staticmethod
    def initialize(connection: sqlite3.Connection) -> None:
        connection.execute(f"PRAGMA application_id={APPLICATION_ID}")
        connection.execute("PRAGMA user_version=1")
        connection.execute("CREATE TABLE events (sequence INTEGER PRIMARY KEY AUTOINCREMENT)")
        connection.execute(
            "CREATE TABLE sessions (session_id TEXT PRIMARY KEY, task_kind TEXT NOT NULL, "
            "context TEXT NOT NULL, guess INTEGER, start_sequence INTEGER NOT NULL UNIQUE, "
            "forecast TEXT NOT NULL)"
        )
        connection.execute(
            "CREATE TABLE measurements (session_id TEXT NOT NULL, revision INTEGER NOT NULL, "
            "sequence INTEGER NOT NULL UNIQUE, tokens INTEGER NOT NULL, outcome TEXT NOT NULL, "
            "coverage TEXT NOT NULL, previous_revision INTEGER, reason TEXT, "
            "PRIMARY KEY (session_id, revision), UNIQUE (session_id, previous_revision))"
        )
        connection.execute("CREATE INDEX cohort ON sessions(task_kind, context)")

    @staticmethod
    def recognize(connection: sqlite3.Connection) -> None:
        try:
            identity = connection.execute("PRAGMA application_id").fetchone()[0]
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' "
                    "AND name != 'sqlite_sequence'"
                )
            }
            expected = SCHEMAS.get(version, {})
            if identity != APPLICATION_ID or version not in SCHEMAS or tables != expected.keys():
                raise unrecognized()
            for name, columns in expected.items():
                found = tuple(row[1] for row in connection.execute(f"PRAGMA table_info({name})"))
                if found != columns:
                    raise unrecognized()
        except sqlite3.Error as exc:
            raise unrecognized() from exc

    @staticmethod
    def migrate_native(connection: sqlite3.Connection) -> None:
        if connection.execute("PRAGMA user_version").fetchone()[0] >= 2:
            return
        connection.execute(
            "CREATE TABLE native_snapshots (source_sha256 TEXT PRIMARY KEY, "
            "repository_id TEXT NOT NULL, diagnostic TEXT NOT NULL)"
        )
        connection.execute(
            "CREATE TABLE native_links (session_id TEXT PRIMARY KEY, "
            "source_sha256 TEXT NOT NULL, sequence INTEGER NOT NULL UNIQUE)"
        )
        connection.execute("PRAGMA user_version=2")

    @staticmethod
    def migrate_codex(connection: sqlite3.Connection) -> None:
        if connection.execute("PRAGMA user_version").fetchone()[0] == 3:
            return
        Sessions.migrate_native(connection)
        connection.execute(
            "CREATE TABLE codex_sessions (session_id TEXT PRIMARY KEY, "
            "source_identity_sha256 TEXT UNIQUE, repository_id TEXT)"
        )
        connection.execute(
            "CREATE TABLE codex_captures (session_id TEXT NOT NULL, revision INTEGER NOT NULL, "
            "sequence INTEGER NOT NULL UNIQUE, snapshot TEXT NOT NULL, outcome TEXT NOT NULL, "
            "previous_revision INTEGER, reason TEXT, PRIMARY KEY (session_id, revision), "
            "UNIQUE (session_id, previous_revision))"
        )
        connection.execute("PRAGMA user_version=3")

    @staticmethod
    def is_codex(connection: sqlite3.Connection, session_id: str) -> bool:
        return connection.execute("PRAGMA user_version").fetchone()[0] == 3 and (
            connection.execute(
                "SELECT 1 FROM codex_sessions WHERE session_id=?", (session_id,)
            ).fetchone()
            is not None
        )

    @staticmethod
    def require_codex(connection: sqlite3.Connection, session_id: str) -> None:
        if (
            connection.execute(
                "SELECT forecast FROM sessions WHERE session_id=?", (session_id,)
            ).fetchone()
            is None
        ):
            raise missing()
        if not Sessions.is_codex(connection, session_id):
            raise conflict()
        forecast = connection.execute(
            "SELECT forecast FROM sessions WHERE session_id=?", (session_id,)
        ).fetchone()[0]
        if json.loads(forecast).get("target") != TARGET:
            raise conflict()

    def capture_codex(
        self, session_id: str, path: Path, repository_id: str, operation: CaptureOperation
    ) -> dict:
        """Acquire outside the lock, then bind and append a safe capture atomically."""
        label(session_id)
        label(repository_id)
        operation.validate()
        with self.connection() as connection:
            self.require_codex(connection, session_id)
            predecessor = self.capture_at(connection, session_id, operation.previous_revision)
            if operation.previous_revision is not None and predecessor is None:
                raise conflict()
        prefix_length = predecessor["snapshot"]["source_byte_count"] if predecessor else 0
        snapshot, prefix_hash = read_codex_counter(path, prefix_length=prefix_length)
        with self.connection(write=True) as connection:
            self.require_codex(connection, session_id)
            revision = self.record_capture(
                connection, session_id, repository_id, snapshot.report(), prefix_hash, operation
            )
            return dict(self.view(connection, session_id), operation_revision=revision)

    @staticmethod
    def capture_at(connection, session_id: str, revision: int | None) -> dict | None:
        if revision is None:
            return None
        row = connection.execute(
            "SELECT * FROM codex_captures WHERE session_id=? AND revision=?", (session_id, revision)
        ).fetchone()
        return None if row is None else dict(row, snapshot=json.loads(row["snapshot"]))

    def record_capture(
        self,
        connection,
        session_id: str,
        repository_id: str,
        snapshot: dict,
        prefix_hash: str,
        operation: CaptureOperation,
    ) -> int:
        previous = operation.previous_revision
        revision = 1 if previous is None else previous + 1
        binding = connection.execute(
            "SELECT * FROM codex_sessions WHERE session_id=?", (session_id,)
        ).fetchone()
        saved = self.capture_at(connection, session_id, revision)
        if saved is not None:
            if (
                saved["snapshot"],
                saved["outcome"],
                saved["previous_revision"],
                saved["reason"],
                binding["repository_id"],
            ) != (snapshot, operation.outcome, previous, operation.reason, repository_id):
                raise conflict()
            return revision
        latest = connection.execute(
            "SELECT MAX(revision) FROM codex_captures WHERE session_id=?", (session_id,)
        ).fetchone()[0]
        if latest != previous:
            raise conflict()
        self.bind_codex(connection, binding, repository_id, snapshot)
        if previous is not None:
            predecessor = self.capture_at(connection, session_id, previous)
            assert predecessor is not None
            self.check_continuity(predecessor["snapshot"], snapshot, prefix_hash)
        self.insert_capture(connection, session_id, revision, snapshot, operation)
        return revision

    @staticmethod
    def bind_codex(connection, binding, repository_id: str, snapshot: dict) -> None:
        identity = snapshot["source_identity_sha256"]
        if binding["source_identity_sha256"] is not None:
            if (binding["source_identity_sha256"], binding["repository_id"]) != (
                identity,
                repository_id,
            ):
                raise conflict()
            return
        existing = connection.execute(
            "SELECT 1 FROM codex_sessions WHERE source_identity_sha256=?", (identity,)
        ).fetchone()
        if existing is not None:
            raise conflict()
        connection.execute(
            "UPDATE codex_sessions SET source_identity_sha256=?, repository_id=? "
            "WHERE session_id=?",
            (identity, repository_id, binding["session_id"]),
        )

    @staticmethod
    def check_continuity(predecessor: dict, snapshot: dict, prefix_hash: str) -> None:
        semantics = (*TARGET, "source_identity_sha256", "source_kind", "producer_version")
        if (
            any(snapshot[key] != predecessor[key] for key in semantics)
            or snapshot["source_byte_count"] < predecessor["source_byte_count"]
            or prefix_hash != predecessor["source_sha256"]
            or snapshot["reported_tokens"] < predecessor["reported_tokens"]
        ):
            raise conflict()

    def insert_capture(
        self,
        connection,
        session_id: str,
        revision: int,
        snapshot: dict,
        operation: CaptureOperation,
    ) -> None:
        connection.execute(
            "INSERT INTO codex_captures VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                session_id,
                revision,
                self.sequence(connection),
                json.dumps(snapshot, sort_keys=True),
                operation.outcome,
                operation.previous_revision,
                operation.reason,
            ),
        )

    def observe_codex(self, session_id: str, selection: CodexSelection) -> dict:
        """Attach immutable partial diagnostics without manual or core authority."""
        self.report(session_id)
        diagnostic = read_codex_file(selection).diagnostics()
        with self.connection(write=True) as connection:
            if (
                connection.execute(
                    "SELECT 1 FROM sessions WHERE session_id=?", (session_id,)
                ).fetchone()
                is None
            ):
                raise missing()
            self.migrate_native(connection)
            self.record_native(connection, session_id, diagnostic)
            return self.view(connection, session_id)

    def record_native(self, connection, session_id: str, diagnostic: dict) -> None:
        source = diagnostic["source_sha256"]
        saved = connection.execute(
            "SELECT source_sha256 FROM native_links WHERE session_id=?", (session_id,)
        ).fetchone()
        if saved is not None and saved["source_sha256"] != source:
            raise conflict()
        self.compare_native(connection, diagnostic)
        connection.execute(
            "INSERT OR IGNORE INTO native_snapshots VALUES (?, ?, ?)",
            (source, diagnostic["repository_id"], json.dumps(diagnostic, sort_keys=True)),
        )
        if saved is None:
            connection.execute(
                "INSERT INTO native_links VALUES (?, ?, ?)",
                (session_id, source, self.sequence(connection)),
            )

    @staticmethod
    def compare_native(connection, diagnostic: dict) -> None:
        incoming = {fact["fact_key"]: fact for fact in diagnostic["facts"]}
        for row in connection.execute("SELECT * FROM native_snapshots"):
            saved = json.loads(row["diagnostic"])
            if row["source_sha256"] == diagnostic["source_sha256"]:
                if saved != diagnostic:
                    raise conflict()
                continue
            for fact in saved["facts"]:
                if fact["fact_key"] in incoming and (
                    row["repository_id"] != diagnostic["repository_id"]
                    or fact != incoming[fact["fact_key"]]
                ):
                    raise conflict()

    @staticmethod
    def native_view(connection: sqlite3.Connection, session_id: str) -> dict | None:
        if connection.execute("PRAGMA user_version").fetchone()[0] == 1:
            return None
        row = connection.execute(
            "SELECT s.diagnostic, l.sequence FROM native_links l "
            "JOIN native_snapshots s ON s.source_sha256=l.source_sha256 WHERE l.session_id=?",
            (session_id,),
        ).fetchone()
        return (
            None if row is None else dict(json.loads(row["diagnostic"]), sequence=row["sequence"])
        )

    @staticmethod
    def sequence(connection: sqlite3.Connection) -> int:
        result = connection.execute("INSERT INTO events DEFAULT VALUES")
        assert result.lastrowid is not None
        return result.lastrowid

    @staticmethod
    def forecast(connection: sqlite3.Connection, task_kind: str, context: str, guess) -> dict:
        exclusion = (
            "AND NOT EXISTS (SELECT 1 FROM codex_sessions c WHERE c.session_id=s.session_id) "
            if connection.execute("PRAGMA user_version").fetchone()[0] == 3
            else ""
        )
        rows = connection.execute(
            "SELECT m.session_id, m.revision, m.tokens, m.outcome FROM measurements m "
            "JOIN sessions s ON s.session_id=m.session_id "
            "WHERE s.task_kind=? AND s.context=? AND m.coverage='declared_session_total' "
            "AND m.revision=(SELECT MAX(latest.revision) FROM measurements latest "
            "WHERE latest.session_id=m.session_id) " + exclusion + "ORDER BY s.start_sequence",
            (task_kind, context),
        ).fetchall()
        inputs = [dict(row) for row in rows]
        return Sessions.forecast_summary(inputs, guess, ALGORITHM)

    @staticmethod
    def forecast_summary(inputs: list[dict], guess, algorithm: str, *, quantity="tokens") -> dict:
        summary = summaries([Fraction(row[quantity]) for row in inputs])
        source = "cohort_median" if inputs else "user_guess" if guess is not None else "unknown"
        amount = summary["median"] if inputs else str(guess) if guess is not None else None
        return dict(
            algorithm=algorithm,
            source=source,
            amount=amount,
            input_guess=guess,
            sample_count=len(inputs),
            summary=summary,
            inputs=inputs,
            outcomes={
                name: sum(row["outcome"] == name for row in inputs) for name in sorted(OUTCOMES)
            },
        )

    @staticmethod
    def codex_forecast(connection, task_kind: str, context: str, guess) -> dict:
        rows = connection.execute(
            "SELECT c.*, s.start_sequence, b.repository_id FROM codex_captures c "
            "JOIN sessions s ON s.session_id=c.session_id "
            "JOIN codex_sessions b ON b.session_id=c.session_id "
            "WHERE s.task_kind=? AND s.context=? AND c.revision=(SELECT MAX(l.revision) "
            "FROM codex_captures l WHERE l.session_id=c.session_id) ORDER BY s.start_sequence",
            (task_kind, context),
        ).fetchall()
        inputs = []
        for row in rows:
            snapshot = json.loads(row["snapshot"])
            if all(snapshot[key] == value for key, value in TARGET.items()):
                inputs.append(
                    dict(
                        session_id=row["session_id"],
                        revision=row["revision"],
                        outcome=row["outcome"],
                        sequence=row["sequence"],
                        start_sequence=row["start_sequence"],
                        repository_id=row["repository_id"],
                        **snapshot,
                    )
                )
        return dict(
            Sessions.forecast_summary(
                inputs, guess, "codex-provisional-median/v1", quantity="reported_tokens"
            ),
            target=dict(TARGET),
        )

    def start(
        self,
        session_id: str,
        task_kind: str,
        context: str,
        guess: int | None = None,
        *,
        source: str = "manual",
    ) -> dict:
        if source not in {"manual", "codex"}:
            raise ValueError("invalid session source")
        for value in (session_id, task_kind, context):
            label(value)
        if guess is not None:
            tokens(guess)
        with self.connection(write=True, create=True) as connection:
            existing = connection.execute(
                "SELECT * FROM sessions WHERE session_id=?", (session_id,)
            ).fetchone()
            if existing:
                if self.is_codex(connection, session_id) != (source == "codex"):
                    raise conflict()
                if source == "codex" and json.loads(existing["forecast"]).get("target") != TARGET:
                    raise conflict()
                if (existing["task_kind"], existing["context"], existing["guess"]) != (
                    task_kind,
                    context,
                    guess,
                ):
                    raise conflict()
            else:
                if source == "codex":
                    self.migrate_codex(connection)
                    forecast = self.codex_forecast(connection, task_kind, context, guess)
                else:
                    forecast = self.forecast(connection, task_kind, context, guess)
                sequence = self.sequence(connection)
                connection.execute(
                    "INSERT INTO sessions VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        session_id,
                        task_kind,
                        context,
                        guess,
                        sequence,
                        json.dumps(forecast),
                    ),
                )
                if source == "codex":
                    connection.execute(
                        "INSERT INTO codex_sessions VALUES (?, NULL, NULL)", (session_id,)
                    )
            return self.view(connection, session_id)

    def measure(self, session_id: str, measurement: Measurement) -> dict:
        label(session_id)
        measurement.validate()
        with self.connection(write=True) as connection:
            if (
                connection.execute(
                    "SELECT 1 FROM sessions WHERE session_id=?", (session_id,)
                ).fetchone()
                is None
            ):
                raise missing()
            if self.is_codex(connection, session_id):
                raise conflict()
            revision = self.record_measurement(connection, session_id, measurement)
            return dict(self.view(connection, session_id), operation_revision=revision)

    def record_measurement(self, connection, session_id: str, measurement: Measurement) -> int:
        previous = measurement.previous_revision
        revision = 1 if previous is None else previous + 1
        existing = connection.execute(
            "SELECT * FROM measurements WHERE session_id=? AND revision=?", (session_id, revision)
        ).fetchone()
        if existing:
            saved = tuple(
                existing[key]
                for key in ("tokens", "outcome", "coverage", "previous_revision", "reason")
            )
            if saved != measurement.payload():
                raise conflict()
            return revision
        latest = connection.execute(
            "SELECT MAX(revision) FROM measurements WHERE session_id=?", (session_id,)
        ).fetchone()[0]
        if latest != previous:
            raise conflict()
        sequence = self.sequence(connection)
        connection.execute(
            "INSERT INTO measurements VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                session_id,
                revision,
                sequence,
                *measurement.payload(),
            ),
        )
        return revision

    @staticmethod
    def view(connection: sqlite3.Connection, session_id: str) -> dict:
        row = connection.execute(
            "SELECT * FROM sessions WHERE session_id=?", (session_id,)
        ).fetchone()
        if row is None:
            raise missing()
        if Sessions.is_codex(connection, session_id):
            return Sessions.codex_view(connection, row)
        measurements = [
            dict(r)
            for r in connection.execute(
                "SELECT * FROM measurements WHERE session_id=? ORDER BY revision", (session_id,)
            )
        ]
        forecast = json.loads(row["forecast"])
        measurement = measurements[-1] if measurements else None
        native = Sessions.native_view(connection, session_id)
        error = evaluation(forecast, measurement)
        if native is not None and measurement is None:
            error["excluded_reason"] = "native_partial_diagnostics"
        result = dict(
            header(),
            session_id=session_id,
            task_kind=row["task_kind"],
            context=row["context"],
            start_sequence=row["start_sequence"],
            forecast=forecast,
            measurement=measurement,
            measurements=measurements,
            error=error,
        )
        if native is not None:
            result.update(
                manual_scope="forecast_measurements_and_error",
                unit_scope="forecast_measurements_and_error",
                native_diagnostics=native,
            )
        return result

    @staticmethod
    def codex_view(connection, row) -> dict:
        captures = [
            dict(record, snapshot=json.loads(record["snapshot"]))
            for record in connection.execute(
                "SELECT * FROM codex_captures WHERE session_id=? ORDER BY revision",
                (row["session_id"],),
            )
        ]
        forecast = json.loads(row["forecast"])
        capture = captures[-1] if captures else None
        binding = connection.execute(
            "SELECT repository_id FROM codex_sessions WHERE session_id=?", (row["session_id"],)
        ).fetchone()
        result = dict(
            codex_header(),
            session_id=row["session_id"],
            task_kind=row["task_kind"],
            context=row["context"],
            start_sequence=row["start_sequence"],
            forecast=forecast,
            measurement=None,
            measurements=[],
            repository_id=binding["repository_id"],
            capture=capture,
            captures=captures,
            error=codex_evaluation(forecast, capture),
            learning_eligible=capture is not None,
        )
        native = Sessions.native_view(connection, row["session_id"])
        if native is not None:
            result["native_diagnostics"] = native
        return result

    def report(self, session_id=None, *, task_kind=None, context=None, source="manual") -> dict:
        if source not in {"manual", "codex"}:
            raise ValueError("invalid session source")
        for value in (session_id, task_kind, context):
            if value is not None:
                label(value)
        if not self.path.exists():
            if session_id is not None:
                raise missing()
            if source == "manual":
                return dict(header(), sessions=[], evaluation=aggregate([]))
            return self.history([], source)
        with self.connection() as connection:
            if session_id is not None:
                return self.view(connection, session_id)
            rows = connection.execute(
                "SELECT session_id FROM sessions WHERE (? IS NULL OR task_kind=?) "
                "AND (? IS NULL OR context=?) ORDER BY start_sequence",
                (task_kind, task_kind, context, context),
            ).fetchall()
            views = [
                self.view(connection, row["session_id"])
                for row in rows
                if self.is_codex(connection, row["session_id"]) == (source == "codex")
            ]
            return self.history(views, source)

    @staticmethod
    def history(views: list[dict], source: str) -> dict:
        if source == "codex":
            return dict(
                codex_header(),
                sessions=views,
                evaluation=aggregate(views),
                learning_count=sum(view["learning_eligible"] for view in views),
            )
        return dict(
            header(),
            manual_scope="forecasts_measurements_and_evaluation",
            unit_scope="forecasts_measurements_and_evaluation",
            sessions=views,
            evaluation=aggregate(views),
        )
