"""Thread-safe job registry and lifecycle coordinator."""
from dataclasses import replace
from datetime import datetime, timezone
import threading
import uuid

from .config import DaemonConfig
from .job import Job
from .scheduler import QueueFullError, Scheduler
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

    def attach_executor(self, executor):
        with self.condition:
            if self.executor is not None and self.executor is not executor:
                raise RuntimeError("El gestor ya tiene un ejecutor.")
            self.executor = executor

    def _create_locked(self, command):
        if not self.is_accepting_jobs:
            raise RuntimeError("El JobManager no esta aceptando nuevos trabajos.")
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
            if job.status in TERMINAL_STATES:
                raise ValueError(f"No se puede cancelar un trabajo con estado '{job.status}'.")
            job.cancel_requested.set()
            job.status = "CANCELED"
            if job.process is None:
                job.finished_at = datetime.now(timezone.utc)
                self.scheduler.cancel_queued_locked(job)
            self.condition.notify_all()
            return replace(job, command=list(job.command), process=None)

    def shutdown(self, timeout=5.0):
        with self.condition:
            self.is_accepting_jobs = False
            self.scheduler.stopping = True
            for job in self.jobs.values():
                if job.status == "QUEUED":
                    self.cancel_job(job.id)
            self.condition.notify_all()
            completed = self.condition.wait_for(
                lambda: not self.scheduler.reservations, timeout=max(0, timeout))
            if not completed:
                for job in self.jobs.values():
                    if job.status == "RUNNING":
                        self.cancel_job(job.id)
        self.scheduler.join()
        with self.condition:
            if self.scheduler.reservations:
                raise RuntimeError("No se confirmó la terminación de todos los procesos.")
