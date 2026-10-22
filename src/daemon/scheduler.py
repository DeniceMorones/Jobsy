"""Bounded FIFO admission and execution reservations (RF-03, RNF-07)."""
from collections import deque
from datetime import datetime, timezone
import subprocess
import sys
import threading

ISOLATION_POLL_SECONDS = 1.0

class QueueFullError(ValueError):
    """Compatible with the existing IPC error envelope."""


class Scheduler:
    def __init__(self, manager, config):
        self.manager = manager
        self.config = config
        self.condition = manager.condition
        self.pending = deque()
        self.ready = deque()
        self.reservations = set()
        self.admitted = set()
        self.dispatcher = None
        self.monitors = set()
        self.stopping = False

    def admit_locked(self, job):
        if self.stopping:
            raise RuntimeError("El servicio no acepta nuevos trabajos.")
        if job.id in self.admitted:
            raise ValueError("El trabajo ya fue programado.")
        if job.status != "QUEUED":
            raise ValueError("Solo se pueden programar trabajos QUEUED.")
        if len(self.reservations) >= self.config.max_running:
            if len(self.pending) >= self.config.queue_capacity:
                raise QueueFullError("Cola llena: no hay capacidad disponible.")
        if self.dispatcher is None:
            thread = threading.Thread(target=self._dispatch, name="jobsy-scheduler", daemon=True)
            thread.start()
            self.dispatcher = thread
        self.manager.persist_creation_locked(job)
        self.admitted.add(job.id)
        if len(self.reservations) < self.config.max_running:
            self.reservations.add(job.id)
            self.ready.append(job)
        else:
            self.pending.append(job)
        self.condition.notify_all()

    def _promote_locked(self):
        while not self.stopping and self.pending and len(self.reservations) < self.config.max_running:
            job = self.pending.popleft()
            self.reservations.add(job.id)
            self.ready.append(job)
        self.condition.notify_all()

    def cancel_queued_locked(self, job):
        # Only jobs without a process reach here; launch uses the same lock.
        if job in self.pending:
            self.pending.remove(job)
        if job in self.ready:
            self.ready.remove(job)
        self.reservations.discard(job.id)
        self._promote_locked()

    def finish_locked(self, job, exit_code, stdout="", stderr=""):
        # Called only after failed spawn or confirmed reaping.
        if job.id not in self.reservations:
            return False
        at = datetime.now(timezone.utc)
        status = job.status if job.status == "CANCELED" else (
            "SUCCEEDED" if exit_code == 0 else "FAILED")
        self.manager._persist_locked(job, "store_results", status=status,
            exit_code=exit_code, stdout=stdout, stderr=stderr, finished_at=at)
        job.stdout = stdout
        job.stderr = stderr
        job.exit_code = exit_code
        job.finished_at = at
        if job.status != "CANCELED":
            job.status = "SUCCEEDED" if exit_code == 0 else "FAILED"
        job.process = None
        self.reservations.remove(job.id)
        self._promote_locked()
        if exit_code is not None and exit_code < 0 and job.status != "CANCELED":
            print(f"[Daemon] Trabajo {job.id} terminó por señal {-exit_code}; recursos liberados.",
                file=sys.stderr)
        return True

    def _dispatch(self):
        while True:
            with self.condition:
                self.condition.wait_for(lambda: self.stopping or self.ready)
                if self.stopping:
                    return
                job = self.ready.popleft()
                if job.status != "QUEUED":
                    self.cancel_queued_locked(job)
                    continue
                try:
                    self.manager.persist_launch_locked(job)
                except Exception:
                    return
                try:
                    # Serialize the final cancellation check, spawn and publication.
                    # No preexec_fn, communicate, wait, kill or joins in this section.
                    process = self.manager.executor.spawn(job.command)
                except Exception as error:
                    try:
                        self.finish_locked(job, 1, stderr=str(error))
                    except Exception:
                        return
                    continue
                job.process = process
                at = datetime.now(timezone.utc)
                try:
                    self.manager.persist_running_locked(job, process, at)
                except Exception:
                    # Retain ownership and reservation; cleanup happens outside the lock.
                    job.cancel_requested.set()
                else:
                    job.status = "RUNNING"
                    job.started_at = at
                self.condition.notify_all()
            monitor = None
            try:
                monitor = threading.Thread(target=self._monitor, args=(job, process),
                                           name=f"jobsy-job-{job.id}", daemon=True)
                with self.condition:
                    self.monitors.add(monitor)
                monitor.start()
            except Exception:
                with self.condition:
                    self.monitors.discard(monitor)
                    try:
                        self.manager.cancel_job(job.id)
                    except Exception as error:
                        self.manager.fail_closed_locked(error)
                    job.cancel_requested.set()
                # Keep ownership and reap even if a supervisor cannot be started.
                self._monitor(job, process)

    def _monitor(self, job, process):
        try:
            try:
                result = self.manager.executor.collect(job, process)
            except Exception as error:
                #un fallo de limpieza de ESTE trabajo no bloquea el servicio.
                result = self._isolate_failed_cleanup(job, process, error)
                if result is None:
                    return
            with self.condition:
                self.finish_locked(job, *result)
        except Exception as error:
            # Fallos de persistencia siguen siendo globales: fail closed.
            with self.condition:
                self.manager.fail_closed_locked(
                    f"No se pudo confirmar la limpieza o persistencia del proceso: {error}")
        finally:
            with self.condition:
                self.monitors.discard(threading.current_thread())
                self.condition.notify_all()

    def _isolate_failed_cleanup(self, job, process, error):
        diagnostic = f"No se pudo confirmar la terminación del proceso: {error}"
        print(f"[Daemon] Trabajo {job.id} aislado: {diagnostic}", file=sys.stderr)
        while True:
            with self.condition:
                if self.stopping:
                    return None
            try:
                process.wait(timeout=ISOLATION_POLL_SECONDS)
                break
            except subprocess.TimeoutExpired:
                continue
            except Exception:
                continue
        return (process.returncode or 1), "", diagnostic

    def counts(self):
        with self.condition:
            return len(self.reservations), len(self.pending)

    def join(self):
        # Shutdown has closed admission; dispatcher cannot create more monitors
        # after it has been joined. Never join while holding the condition.
        if self.dispatcher is not None:
            self.dispatcher.join()
        with self.condition:
            monitors = list(self.monitors)
        for thread in monitors:
            thread.join()
