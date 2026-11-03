"""Durable records only: no scheduling, recovery policy or process execution."""
from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import threading
from uuid import UUID

SCHEMA_VERSION = 1
STATES = frozenset({"QUEUED", "RUNNING", "SUCCEEDED", "FAILED", "CANCELED"})
SCHEMA = (
    """CREATE TABLE daemon_sessions (
        id TEXT PRIMARY KEY NOT NULL,
        started_at TEXT NOT NULL,
        finished_at TEXT,
        clean_shutdown INTEGER NOT NULL DEFAULT 0 CHECK(clean_shutdown IN (0,1)),
        boot_id TEXT,
        daemon_pid INTEGER CHECK(daemon_pid > 0),
        CHECK(clean_shutdown = 0 OR finished_at IS NOT NULL)
    )""",
    """CREATE TABLE jobs (
        id TEXT PRIMARY KEY NOT NULL CHECK(length(id) = 36),
        command_json TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('QUEUED','RUNNING','SUCCEEDED','FAILED','CANCELED')),
        received_at TEXT NOT NULL,
        started_at TEXT,
        finished_at TEXT,
        exit_code INTEGER CHECK(exit_code IS NULL OR typeof(exit_code) = 'integer'),
        stdout TEXT NOT NULL DEFAULT '',
        stderr TEXT NOT NULL DEFAULT '',
        version INTEGER NOT NULL DEFAULT 0 CHECK(typeof(version) = 'integer' AND version >= 0)
    )""",
    """CREATE TABLE job_execution (
        job_id TEXT PRIMARY KEY NOT NULL REFERENCES jobs(id),
        session_id TEXT REFERENCES daemon_sessions(id),
        admission_sequence INTEGER CHECK(admission_sequence >= 0),
        launch_intent_at TEXT,
        pid INTEGER CHECK(pid > 0),
        boot_id TEXT,
        process_start_ticks INTEGER CHECK(process_start_ticks >= 0),
        cancel_requested_at TEXT,
        cleanup_pending INTEGER NOT NULL DEFAULT 0 CHECK(cleanup_pending IN (0,1)),
        results_complete INTEGER NOT NULL DEFAULT 0 CHECK(results_complete IN (0,1)),
        recovered_at TEXT,
        recovery_reason TEXT
    )""",
)


class RepositoryError(RuntimeError):
    """Storage failure; callers must not acknowledge an uncommitted operation."""


class SchemaError(RepositoryError):
    """Unsupported or inconsistent database schema."""


class VersionConflict(RepositoryError):
    """The caller's snapshot is stale."""


class RecordNotFound(RepositoryError):
    """The requested durable record does not exist."""


def _uuid(value):
    if not isinstance(value, str) or str(UUID(value)) != value:
        raise ValueError("Expected a canonical UUID string.")
    return value


def _timestamp(value, required=False):
    if value is None:
        if required:
            raise ValueError("A timezone-aware timestamp is required.")
        return None
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError("Expected a timezone-aware datetime.")
    return value.astimezone(timezone.utc).isoformat()


def _integer(value, minimum=None, optional=False):
    if optional and value is None:
        return value
    if type(value) is not int or (minimum is not None and value < minimum):
        raise ValueError("Invalid integer value.")
    return value


class JobRepository:
    """One serialized connection per instance; separate instances use SQLite locks.

    Returned dictionaries are detached snapshots. Every job mutation requires an
    expected version and increments it, including execution-metadata changes.
    """

    def __init__(self, path, timeout=0.5):
        self.path = Path(path).expanduser().resolve()
        self._lock = threading.RLock()
        self._connection = None
        # Do not create directories or replace an existing failed database.
        try:
            self._connection = sqlite3.connect(
                self.path.as_uri() + ("?mode=rw" if self.path.exists() else "?mode=rwc"),
                uri=True, timeout=timeout, isolation_level=None, check_same_thread=False)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys=ON")
            self._initialize()
            mode = self._connection.execute("PRAGMA journal_mode=DELETE").fetchone()[0]
            self._connection.execute("PRAGMA synchronous=EXTRA")
            if mode != "delete" or self._connection.execute("PRAGMA synchronous").fetchone()[0] != 3:
                raise RepositoryError("Required SQLite durability policy unavailable.")
            with self._lock:
                self._check_data()
        except (sqlite3.Error, RepositoryError, ValueError, TypeError) as error:
            self.close()
            if isinstance(error, RepositoryError):
                raise
            raise RepositoryError(f"Cannot open database {self.path}: {error}") from error

    @contextmanager
    def _transaction(self):
        with self._lock:
            connection = self._require_open()
            try:
                connection.execute("BEGIN IMMEDIATE")
                yield connection
                connection.execute("COMMIT")
            except BaseException as error:
                if connection.in_transaction:
                    try:
                        connection.rollback()
                    except sqlite3.Error as rollback_error:
                        self.close()
                        raise RepositoryError("Rollback failed; repository closed.") from rollback_error
                if isinstance(error, sqlite3.Error):
                    raise RepositoryError(f"SQLite transaction failed: {error}") from error
                raise

    def _require_open(self):
        if self._connection is None:
            raise RepositoryError("Repository is closed.")
        return self._connection

    def _initialize(self):
        with self._transaction() as connection:
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            objects = connection.execute(
                "SELECT name, sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'"
            ).fetchall()
            if version == 0 and not objects:
                for statement in SCHEMA:
                    connection.execute(statement)
                connection.execute(f"PRAGMA user_version={SCHEMA_VERSION}")
            elif version != SCHEMA_VERSION:
                raise SchemaError(f"Unsupported schema version: {version}; expected {SCHEMA_VERSION}.")
            expected = {statement.split()[2]: " ".join(statement.split()) for statement in SCHEMA}
            actual = {row["name"]: " ".join(row["sql"].split()) for row in connection.execute(
                "SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )}
            if actual != expected:
                raise SchemaError("Schema does not match version 1; explicit migration required.")

    def _check_data(self):
        connection = self._require_open()
        if connection.execute("PRAGMA quick_check").fetchall()[0][0] != "ok":
            raise SchemaError("SQLite consistency check failed.")
        if connection.execute("PRAGMA foreign_key_check").fetchone():
            raise SchemaError("Foreign-key consistency check failed.")
        missing = connection.execute(
            "SELECT id FROM jobs LEFT JOIN job_execution ON id=job_id WHERE job_id IS NULL"
        ).fetchone()
        if missing:
            raise SchemaError("Job execution metadata missing.")
        for row in connection.execute("SELECT * FROM jobs"):
            self._decode(row)
        for row in connection.execute("SELECT * FROM daemon_sessions"):
            _uuid(row["id"])
            for key in ("started_at", "finished_at"):
                if row[key] is not None:
                    _timestamp(datetime.fromisoformat(row[key]), required=True)
        for row in connection.execute("SELECT * FROM job_execution"):
            for key in ("launch_intent_at", "cancel_requested_at", "recovered_at"):
                if row[key] is not None:
                    _timestamp(datetime.fromisoformat(row[key]), required=True)

    @staticmethod
    def _decode(row):
        result = dict(row)
        _uuid(result["id"])
        command = json.loads(result.pop("command_json"))
        if not isinstance(command, list) or not command or any(
                not isinstance(arg, str) or "\x00" in arg for arg in command) or not command[0]:
            raise ValueError("Invalid persisted command.")
        result["command"] = command
        for key in ("received_at", "started_at", "finished_at"):
            if result[key] is not None:
                result[key] = datetime.fromisoformat(result[key])
                _timestamp(result[key], required=True)
        return result

    def _read(self, connection, job_id):
        row = connection.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        if row is None:
            raise RecordNotFound(job_id)
        result = self._decode(row)
        execution = connection.execute("SELECT * FROM job_execution WHERE job_id=?", (job_id,)).fetchone()
        if execution is None:
            raise SchemaError("Job execution metadata missing.")
        result["execution"] = dict(execution)
        for key in ("launch_intent_at", "cancel_requested_at", "recovered_at"):
            if result["execution"][key] is not None:
                result["execution"][key] = datetime.fromisoformat(result["execution"][key])
        return result

    def create_job(self, job, *, session_id=None, admission_sequence=None):
        _uuid(job.id)
        if session_id is not None:
            _uuid(session_id)
        _integer(admission_sequence, 0, optional=True)
        if job.status not in STATES:
            raise ValueError("Invalid public job state.")
        if not isinstance(job.command, list) or not job.command or any(
                not isinstance(arg, str) or "\x00" in arg for arg in job.command) or not job.command[0]:
            raise ValueError("Invalid command arguments.")
        if not isinstance(job.stdout, str) or not isinstance(job.stderr, str):
            raise ValueError("Results must be strings.")
        _integer(job.exit_code, optional=True)
        values = (job.id, json.dumps(job.command, ensure_ascii=False), job.status,
                  _timestamp(job.received_at, True), _timestamp(job.started_at),
                  _timestamp(job.finished_at), job.exit_code, job.stdout, job.stderr)
        with self._transaction() as connection:
            connection.execute(
                "INSERT INTO jobs(id,command_json,status,received_at,started_at,finished_at,"
                "exit_code,stdout,stderr) VALUES (?,?,?,?,?,?,?,?,?)", values)
            connection.execute(
                "INSERT INTO job_execution(job_id,session_id,admission_sequence) VALUES (?,?,?)",
                (job.id, session_id, admission_sequence))
            return self._read(connection, job.id)

    def get_job(self, job_id):
        with self._lock:
            try:
                # One read transaction keeps job + execution metadata consistent.
                connection = self._require_open()
                connection.execute("BEGIN")
                result = self._read(connection, job_id)
                connection.execute("COMMIT")
                return result
            except Exception as error:
                if self._connection is not None and self._connection.in_transaction:
                    self._connection.rollback()
                if isinstance(error, (sqlite3.Error, ValueError, TypeError)):
                    raise RepositoryError(f"Cannot read job: {error}") from error
                raise

    def list_jobs(self, status=None):
        if status is not None and status not in STATES:
            raise ValueError("Invalid public job state.")
        # Serialize a consistent history snapshot, without a write reservation.
        with self._lock:
            connection = self._require_open()
            try:
                connection.execute("BEGIN")
                rows = connection.execute(
                    "SELECT id FROM jobs WHERE (? IS NULL OR status=?) ORDER BY received_at,id",
                    (status, status)).fetchall()
                result = [self._read(connection, row["id"]) for row in rows]
                connection.execute("COMMIT")
                return result
            except Exception as error:
                if connection.in_transaction:
                    connection.rollback()
                if isinstance(error, (sqlite3.Error, ValueError, TypeError)):
                    raise RepositoryError(f"Cannot read history: {error}") from error
                raise

    def _change(self, job_id, expected_version, fields=None, execution=None):
        _integer(expected_version, 0)
        with self._transaction() as connection:
            row = connection.execute("SELECT version FROM jobs WHERE id=?", (job_id,)).fetchone()
            if row is None:
                raise RecordNotFound(job_id)
            if row["version"] != expected_version:
                raise VersionConflict(f"Stale version for {job_id}.")
            # Column names come only from the fixed public methods below.
            fields = fields or {}
            assignments = [f"{key}=?" for key in fields] + ["version=version+1"]
            connection.execute(
                f"UPDATE jobs SET {','.join(assignments)} WHERE id=? AND version=?",
                (*fields.values(), job_id, expected_version))
            if execution:
                connection.execute(
                    "UPDATE job_execution SET " + ",".join(f"{key}=?" for key in execution)
                    + " WHERE job_id=?", (*execution.values(), job_id))
            return self._read(connection, job_id)

    def update_status(self, job_id, expected_version, status, *, started_at=None, finished_at=None):
        if status not in STATES:
            raise ValueError("Invalid public job state.")
        fields = {"status": status}
        if started_at is not None:
            fields["started_at"] = _timestamp(started_at)
        if finished_at is not None:
            fields["finished_at"] = _timestamp(finished_at)
        return self._change(job_id, expected_version, fields)

    def store_results(self, job_id, expected_version, *, status, exit_code,
                      stdout, stderr, finished_at):
        if status not in {"SUCCEEDED", "FAILED", "CANCELED"}:
            raise ValueError("Results require a terminal state.")
        if not isinstance(stdout, str) or not isinstance(stderr, str):
            raise ValueError("Results must be strings.")
        _integer(exit_code, optional=True)
        return self._change(job_id, expected_version, {
            "status": status, "exit_code": exit_code, "stdout": stdout, "stderr": stderr,
            "finished_at": _timestamp(finished_at, True)},
            {"results_complete": 1, "cleanup_pending": 0})

    def record_execution_intent(self, job_id, expected_version, session_id, *, at):
        return self._change(job_id, expected_version, execution={
            "session_id": _uuid(session_id), "launch_intent_at": _timestamp(at, True),
            "cleanup_pending": 1})

    def record_process_identity(self, job_id, expected_version, *, pid, boot_id, process_start_ticks):
        if not isinstance(boot_id, str) or not boot_id:
            raise ValueError("boot_id is required.")
        return self._change(job_id, expected_version, execution={
            "pid": _integer(pid, 1), "boot_id": boot_id,
            "process_start_ticks": _integer(process_start_ticks, 0)})

    def record_cancellation_intent(self, job_id, expected_version, *, at, without_process=False):
        fields = {"status": "CANCELED"}
        execution = {"cancel_requested_at": _timestamp(at, True)}
        if without_process:
            fields["finished_at"] = _timestamp(at, True)
            execution["cleanup_pending"] = 0
        return self._change(job_id, expected_version, fields, execution)

    def record_running(self, job_id, expected_version, *, at, pid, boot_id, process_start_ticks):
        if not isinstance(boot_id, str) or not boot_id:
            raise ValueError("boot_id is required.")
        return self._change(job_id, expected_version,
            {"status": "RUNNING", "started_at": _timestamp(at, True)},
            {"pid": _integer(pid, 1), "boot_id": boot_id,
             "process_start_ticks": _integer(process_start_ticks, 0), "cleanup_pending": 1})

    def reconcile_job(self, job_id, expected_version, *, status, at, reason,
                      finished_at=None, preserve_results=False):
        if status not in {"FAILED", "CANCELED", "SUCCEEDED"} or not reason:
            raise ValueError("Invalid recovery transition.")
        fields = {"status": status}
        if not preserve_results:
            fields["exit_code"] = None
        if finished_at is not None:
            fields["finished_at"] = _timestamp(finished_at, True)
        return self._change(job_id, expected_version, fields,
            {"recovered_at": _timestamp(at, True), "recovery_reason": reason,
             "cleanup_pending": 0})

    def record_recovery(self, job_id, expected_version, *, at, reason):
        if not isinstance(reason, str) or not reason:
            raise ValueError("Recovery reason is required.")
        return self._change(job_id, expected_version, execution={
            "recovered_at": _timestamp(at, True), "recovery_reason": reason})

    def start_session(self, session_id, *, started_at, boot_id=None, daemon_pid=None):
        values = (_uuid(session_id), _timestamp(started_at, True), boot_id,
                  _integer(daemon_pid, 1, optional=True))
        with self._transaction() as connection:
            connection.execute(
                "INSERT INTO daemon_sessions(id,started_at,boot_id,daemon_pid) VALUES (?,?,?,?)", values)

    def finish_session(self, session_id, *, finished_at, clean_shutdown):
        if type(clean_shutdown) is not bool:
            raise ValueError("clean_shutdown must be boolean.")
        with self._transaction() as connection:
            cursor = connection.execute(
                "UPDATE daemon_sessions SET finished_at=?,clean_shutdown=? WHERE id=? AND finished_at IS NULL",
                (_timestamp(finished_at, True), int(clean_shutdown), session_id))
            if cursor.rowcount != 1:
                raise VersionConflict("Session missing or already closed.")

    def list_sessions(self):
        with self._lock:
            try:
                return [dict(row) for row in self._require_open().execute(
                    "SELECT * FROM daemon_sessions ORDER BY started_at,id")]
            except sqlite3.Error as error:
                raise RepositoryError(f"Cannot read sessions: {error}") from error

    def close(self):
        with self._lock:
            if self._connection is not None:
                self._connection.close()
                self._connection = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
