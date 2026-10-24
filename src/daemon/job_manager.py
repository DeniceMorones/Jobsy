"""Thread-safe job registry and lifecycle coordinator."""
from dataclasses import replace
from datetime import datetime, timezone
import threading
import uuid
import sys

from .config import DaemonConfig
from .job import Job
from .scheduler import QueueFullError, Scheduler
from .process_identity import process_identity
from ..protocol.validation import validate_command

TERMINAL_STATES = {"SUCCEEDED", "FAILED", "CANCELED"}
VALID_STATES = TERMINAL_STATES | {"QUEUED", "RUNNING"}


class JobManager:
    def __init__(self, config=None):
        self.config = config or DaemonConfig()
        self.condition = threading.Condition(threading.RLock())
        self.jobs = {}
        self.is_accepting_jobs = True
        self.executor = None
        self.scheduler = Scheduler(self, self.config)
        self.repository = None
        self.session_id = None
        self.boot_id = None
        self.versions = {}
        self.storage_error = None
        self.admission_sequence = 0

    def enable_persistence(self, runtime):
        with self.condition:
            if self.repository is not None or self.jobs or self.scheduler.dispatcher is not None:
                raise RuntimeError("La persistencia debe inicializarse antes de aceptar trabajos.")
            self.repository = runtime.repository
            self.session_id = runtime.session_id
            self.boot_id = runtime.boot_id
            for record in runtime.records:
                fields = {name: record[name] for name in (
                    "id", "command", "status", "received_at", "started_at",
                    "finished_at", "exit_code", "stdout", "stderr")}
                self.jobs[record["id"]] = Job(**fields)
                self.versions[record["id"]] = record["version"]
                self.scheduler.admitted.add(record["id"])
                self.admission_sequence = max(self.admission_sequence,
                    record["execution"]["admission_sequence"] or 0)

    def fail_closed_locked(self, error):
        if self.storage_error is None:
            self.storage_error = str(error)
            print(f"[Daemon] Ejecución bloqueada: {error}", file=sys.stderr)
        self.is_accepting_jobs = False
        self.scheduler.stopping = True
        for job in self.jobs.values():
            if job.process is not None:
                job.cancel_requested.set()
        self.condition.notify_all()

    def _persist_locked(self, job, method, **kwargs):
        if self.repository is None:
            return
        try:
            record = getattr(self.repository, method)(
                job.id, self.versions[job.id], **kwargs)
            self.versions[job.id] = record["version"]
        except Exception as error:
            self.fail_closed_locked(error)
            raise

    def persist_creation_locked(self, job):
        if self.repository is None:
            return
        try:
            self.admission_sequence += 1
            record = self.repository.create_job(job, session_id=self.session_id,
                admission_sequence=self.admission_sequence)
            self.versions[job.id] = record["version"]
        except Exception as error:
            self.fail_closed_locked(error)
            raise

    def persist_launch_locked(self, job):
        self._persist_locked(job, "record_execution_intent",
            session_id=self.session_id, at=datetime.now(timezone.utc))

    def persist_running_locked(self, job, process, at):
        if self.repository is not None:
            try:
                _, ticks = process_identity(process.pid)
            except Exception as error:
                self.fail_closed_locked(error)
                raise
            self._persist_locked(job, "record_running", at=at, pid=process.pid,
                boot_id=self.boot_id, process_start_ticks=ticks)

    def attach_executor(self, executor):
        with self.condition:
            if self.executor is not None and self.executor is not executor:
                raise RuntimeError("El gestor ya tiene un ejecutor.")
            self.executor = executor

    def _create_locked(self, command):
        if not self.is_accepting_jobs:
            raise RuntimeError(self.storage_error or "El JobManager no esta aceptando nuevos trabajos.")
        job = Job(id=str(uuid.uuid4()), command=list(command))
        self.jobs[job.id] = job
        return job

    def create_job(self, command):
        """Legacy registration API; execute(job) performs bounded admission."""
        validate_command(command)
        with self.condition:
            return self._create_locked(command)

    def submit_job(self, command):
        """Atomically register and admit; rejection leaves no residual job."""
        validate_command(command)
        with self.condition:
            if self.executor is None:
                from .executor import Executor
                Executor(self)
            job = self._create_locked(command)
            try:
                self.scheduler.admit_locked(job)
            except Exception:
                del self.jobs[job.id]
                raise
            return job

    def schedule_job(self, job):
        with self.condition:
            if not self.is_accepting_jobs:
                raise RuntimeError("El servicio no acepta nuevos trabajos.")
            if self.jobs.get(job.id) is not job:
                raise ValueError("El trabajo no pertenece a este gestor.")
            try:
                self.scheduler.admit_locked(job)
            except QueueFullError:
                del self.jobs[job.id]
                raise

    def _get_locked(self, job_id):
        if job_id not in self.jobs:
            raise ValueError(f"No existe un trabajo con el ID '{job_id}'.")
        return self.jobs[job_id]

    def get_job(self, job_id):
        with self.condition:
            return self._get_locked(job_id)

    def snapshot(self, job_id):
        with self.condition:
            job = self._get_locked(job_id)
            return replace(job, command=list(job.command), process=None)

    def list_jobs(self, status=None):
        with self.condition:
            if status is not None:
                status = status.upper()
                if status not in VALID_STATES:
                    raise ValueError(f"Estado no valido: '{status}'.")
            return [replace(job, command=list(job.command), process=None)
                    for job in self.jobs.values() if status is None or job.status == status]

    def cancel_job(self, job_id):
        with self.condition:
            job = self._get_locked(job_id)
            if job.status == "CANCELED":
                raise ValueError("La cancelación de este trabajo ya fue solicitada (estado CANCELED).")
            if job.status in TERMINAL_STATES:
                raise ValueError(f"No se puede cancelar un trabajo con estado '{job.status}'.")
            at = datetime.now(timezone.utc)
            self._persist_locked(job, "record_cancellation_intent", at=at,
                without_process=job.process is None)
            job.cancel_requested.set()
            job.status = "CANCELED"

            if job.process is None:
                job.finished_at = at
                self.scheduler.cancel_queued_locked(job)
            self.condition.notify_all()
            return replace(job, command=list(job.command), process=None)

    def shutdown(self, timeout=5.0):
        with self.condition:
            self.is_accepting_jobs = False
            self.scheduler.stopping = True
            for job in self.jobs.values():
                if job.status == "QUEUED" and job.process is None:
                    try:
                        self.cancel_job(job.id)
                    except Exception as error:
                        self.fail_closed_locked(error)
            self.condition.notify_all()
            completed = self.condition.wait_for(
                lambda: not self.scheduler.reservations or self.storage_error is not None,
                timeout=max(0, timeout))
            if not completed or self.storage_error is not None:
                for job in self.jobs.values():
                    if job.process is not None:
                        try:
                            if job.status not in TERMINAL_STATES:
                                self.cancel_job(job.id)
                        except Exception as error:
                            self.fail_closed_locked(error)
                        finally:
                            job.cancel_requested.set()
        self.scheduler.join()
        with self.condition:
            if self.scheduler.reservations or self.storage_error is not None:
                raise RuntimeError(self.storage_error or "No se confirmó la terminación de todos los procesos.")
