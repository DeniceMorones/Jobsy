"""Process creation, output capture and termination; no admission decisions."""
import subprocess


class Executor:
    def __init__(self, manager, popen_factory=None):
        self.manager = manager
        self.popen_factory = popen_factory or subprocess.Popen
        manager.attach_executor(self)

    def execute(self, job):
        """Compatibility entry point: every execution still passes admission."""
        self.manager.schedule_job(job)

    def spawn(self, command):
        return self.popen_factory(command, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True)

    @staticmethod
    def terminate_and_reap(process):
        """Preserve SIGTERM -> 2s -> SIGKILL; always wait after escalation."""
        if process.poll() is None:
            try:
                process.terminate()
            except ProcessLookupError:
                pass
        try:
            process.wait(timeout=2.0)
        except subprocess.TimeoutExpired:
            try:
                process.kill()
            except ProcessLookupError:
                pass
            process.wait(timeout=2.0)

    def collect(self, job, process):
        stdout, stderr = "", ""
        capture_failed = False
        try:
            while True:
                if job.cancel_requested.is_set():
                    self.terminate_and_reap(process)
                    stdout, stderr = process.communicate(timeout=0.5)
                    break
                try:
                    stdout, stderr = process.communicate(timeout=0.1)
                    break
                except subprocess.TimeoutExpired:
                    continue
        except Exception as error:
            self.terminate_and_reap(process)
            capture_failed = True
            stderr = str(error)
            # Main process is reaped; descendants holding pipes are out of scope.
            for stream in (process.stdout, process.stderr):
                if stream is not None:
                    stream.close()
        process.wait()
        return (process.returncode or 1) if capture_failed else process.returncode, stdout, stderr
