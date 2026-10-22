import os
import signal
import subprocess

DEFAULT_GRACE_SECONDS = 2.0


class Executor:
    def __init__(self, manager, popen_factory=None, grace_seconds=None):
        self.manager = manager
        self.popen_factory = popen_factory or subprocess.Popen
        if grace_seconds is None:
            config = getattr(manager, "config", None)
            grace_seconds = getattr(config, "cancel_grace_seconds", DEFAULT_GRACE_SECONDS)
        self.grace_seconds = grace_seconds
        manager.attach_executor(self)

    def execute(self, job):
        """Compatibility entry point: every execution still passes admission."""
        self.manager.schedule_job(job)

    def spawn(self, command):
        # Each job leads its own process group so that cancellation and shutdown
        # can reach descendants (RNF-30) without ever signalling the daemon's group.
        process = self.popen_factory(command, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True,
                                     start_new_session=True)
        try:
            if os.getpgid(process.pid) == process.pid != os.getpgrp():
                process.jobsy_group = True
        except (OSError, AttributeError):
            pass
        return process

    @staticmethod
    def _send(process, sig):
        """Signal the whole job group when owned; otherwise only the process."""
        if getattr(process, "jobsy_group", False) is True:
            try:
                os.killpg(process.pid, sig)
            except ProcessLookupError:
                pass
            return
        try:
            if sig == signal.SIGKILL:
                process.kill()
            else:
                process.terminate()
        except ProcessLookupError:
            pass

    @staticmethod
    def terminate_and_reap(process, grace=DEFAULT_GRACE_SECONDS):
        """SIGTERM -> grace -> SIGKILL, applied to the job's process group."""
        if process.poll() is None:
            Executor._send(process, signal.SIGTERM)
        try:
            process.wait(timeout=grace)
        except subprocess.TimeoutExpired:
            Executor._send(process, signal.SIGKILL)
            process.wait(timeout=2.0)
        else:
            if getattr(process, "jobsy_group", False) is True:
                Executor._send(process, signal.SIGKILL)

    def collect(self, job, process):
        stdout, stderr = "", ""
        capture_failed = False
        try:
            while True:
                if job.cancel_requested.is_set():
                    self.terminate_and_reap(process, self.grace_seconds)
                    stdout, stderr = process.communicate(timeout=0.5)
                    break
                try:
                    stdout, stderr = process.communicate(timeout=0.1)
                    break
                except subprocess.TimeoutExpired:
                    continue
        except Exception as error:
            self.terminate_and_reap(process, self.grace_seconds)
            capture_failed = True
            stderr = str(error)
            for stream in (process.stdout, process.stderr):
                if stream is not None:
                    stream.close()
        process.wait()
        return (process.returncode or 1) if capture_failed else process.returncode, stdout, stderr