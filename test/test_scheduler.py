"""Deterministic scheduler tests; no real processes or sockets."""
import io
import subprocess
import threading
import unittest
from unittest.mock import patch

from src.daemon.config import DaemonConfig, parse_config
from src.daemon.executor import Executor
from src.daemon.job_manager import JobManager
from src.daemon.scheduler import QueueFullError


class ControlledProcess:
    def __init__(self, factory, command):
        self.factory = factory
        self.command = command
        self.done = threading.Event()
        self.reap = threading.Event()
        self.reap.set()
        self.returncode = None
        self.code = 0
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        self.ignore_term = False
        self.killed = False

    def complete(self, code=0):
        self.code = code
        self.done.set()

    def communicate(self, timeout=None):
        if not self.done.wait(timeout):
            raise subprocess.TimeoutExpired(self.command, timeout)
        self.wait(timeout=timeout)
        return "out", "err"

    def poll(self):
        return self.code if self.done.is_set() else None

    def wait(self, timeout=None):
        if not self.done.wait(timeout) or not self.reap.wait(timeout):
            raise subprocess.TimeoutExpired(self.command, timeout)
        self.returncode = self.code
        return self.returncode

    def terminate(self):
        if not self.ignore_term:
            self.complete(-15)

    def kill(self):
        self.killed = True
        self.complete(-9)


class Factory:
    def __init__(self):
        self.processes = []
        self.peak = 0
        self.entered = threading.Event()
        self.launch_gate = threading.Event()
        self.launch_gate.set()

    def __call__(self, command, **kwargs):
        self.entered.set()
        if not self.launch_gate.wait(3):
            raise RuntimeError("Test launch gate timeout")
        if command == ["spawn-failure"]:
            raise OSError("spawn failed")
        process = ControlledProcess(self, command)
        self.processes.append(process)
        self.peak = max(self.peak, sum(not p.done.is_set() for p in self.processes))
        return process


class SchedulerTests(unittest.TestCase):
    def make_manager(self, n=1, q=10):
        manager = JobManager(DaemonConfig(n, q))
        factory = Factory()
        Executor(manager, factory)
        self.addCleanup(manager.shutdown, 0)
        return manager, factory

    def wait_for(self, manager, predicate):
        with manager.condition:
            self.assertTrue(manager.condition.wait_for(predicate, 3), "Condition timed out")

    def running(self, manager, job):
        self.wait_for(manager, lambda: job.status == "RUNNING")

    def finished(self, manager, job):
        self.wait_for(manager, lambda: job.id not in manager.scheduler.reservations)

    def test_fifo_and_automatic_scheduling(self):
        manager, factory = self.make_manager()
        jobs = [manager.submit_job([str(i)]) for i in range(4)]
        for job in jobs:
            self.running(manager, job)
            self.assertEqual(factory.processes[-1].command, job.command)
            job.process.complete()
            self.finished(manager, job)
        self.assertEqual([p.command for p in factory.processes], [[str(i)] for i in range(4)])
        self.assertEqual(factory.peak, 1)

    def test_limits_one_and_three(self):
        for n in (1, 3):
            with self.subTest(n=n):
                manager, factory = self.make_manager(n=n)
                jobs = [manager.submit_job([str(i)]) for i in range(n + 2)]
                for job in jobs[:n]:
                    self.running(manager, job)
                self.assertEqual(manager.scheduler.counts(), (n, 2))
                self.assertTrue(all(job.status == "QUEUED" for job in jobs[n:]))
                self.assertEqual(factory.peak, n)

    def test_zero_waiting_capacity(self):
        manager, factory = self.make_manager(q=0)
        first = manager.submit_job(["first"])
        with self.assertRaises(QueueFullError):
            manager.submit_job(["rejected"])
        self.assertEqual(len(manager.jobs), 1)
        self.running(manager, first)
        first.process.complete()
        self.finished(manager, first)
        self.running(manager, manager.submit_job(["next"]))

    def test_full_queue_rejection_leaves_no_residual(self):
        manager, factory = self.make_manager(q=1)
        manager.submit_job(["first"])
        manager.submit_job(["second"])
        before = set(manager.jobs)
        with self.assertRaises(QueueFullError):
            manager.submit_job(["third"])
        self.assertEqual(set(manager.jobs), before)
        self.assertEqual(manager.scheduler.counts(), (1, 1))

    def test_simultaneous_submissions(self):
        manager, factory = self.make_manager(n=3, q=5)
        barrier = threading.Barrier(21)
        accepted, rejected, errors = [], [], []
        result_lock = threading.Lock()

        def submit(i):
            barrier.wait()
            try:
                job = manager.submit_job([str(i)])
                with result_lock:
                    accepted.append(job)
            except QueueFullError:
                with result_lock:
                    rejected.append(i)
            except Exception as error:
                with result_lock:
                    errors.append(error)

        threads = [threading.Thread(target=submit, args=(i,)) for i in range(20)]
        for thread in threads:
            thread.start()
        barrier.wait()
        for thread in threads:
            thread.join(3)
            self.assertFalse(thread.is_alive())
        self.assertEqual(errors, [])
        self.assertEqual((len(accepted), len(rejected)), (8, 12))
        self.assertEqual(len(manager.jobs), 8)
        self.assertEqual(manager.scheduler.counts(), (3, 5))
        self.assertLessEqual(factory.peak, 3)

    def test_cancel_queued_never_launches(self):
        manager, factory = self.make_manager()
        first = manager.submit_job(["first"])
        self.running(manager, first)
        canceled = manager.submit_job(["canceled"])
        last = manager.submit_job(["last"])
        manager.cancel_job(canceled.id)
        first.process.complete()
        self.running(manager, last)
        self.assertEqual([p.command for p in factory.processes], [["first"], ["last"]])
        self.assertEqual(canceled.status, "CANCELED")
        self.assertIsNone(canceled.started_at)

    def test_cancel_reserved_before_launch(self):
        manager, factory = self.make_manager(q=0)
        with manager.condition:
            job = manager.submit_job(["canceled"])
            manager.cancel_job(job.id)
        self.assertEqual(manager.scheduler.counts(), (0, 0))
        manager.shutdown(0)
        self.assertEqual(factory.processes, [])

    def test_cancel_during_startup(self):
        manager, factory = self.make_manager()
        factory.launch_gate.clear()
        job = manager.submit_job(["starting"])
        self.assertTrue(factory.entered.wait(3))
        attempted = threading.Event()
        errors = []

        def cancel():
            attempted.set()
            try:
                manager.cancel_job(job.id)
            except Exception as error:
                errors.append(error)

        thread = threading.Thread(target=cancel)
        thread.start()
        self.assertTrue(attempted.wait(3))
        factory.launch_gate.set()
        thread.join(3)
        self.assertFalse(thread.is_alive())
        self.finished(manager, job)
        self.assertEqual(errors, [])
        self.assertEqual(job.status, "CANCELED")
        self.assertEqual(len(factory.processes), 1)
        self.assertIsNotNone(factory.processes[0].returncode)

    def test_normal_failure_and_spawn_failure(self):
        manager, factory = self.make_manager()
        for code in (0, 7):
            job = manager.submit_job(["process"])
            self.running(manager, job)
            job.process.complete(code)
            self.finished(manager, job)
            self.assertEqual(job.status, "SUCCEEDED" if code == 0 else "FAILED")
            self.assertEqual(job.exit_code, code)
        job = manager.submit_job(["spawn-failure"])
        self.finished(manager, job)
        self.assertEqual(job.status, "FAILED")
        self.assertIsNone(job.started_at)
        self.assertIn("spawn failed", job.stderr)
        self.running(manager, manager.submit_job(["after-failure"]))

    def test_release_exactly_once_and_execute_at_most_once(self):
        manager, factory = self.make_manager()
        job = manager.create_job(["legacy"])
        manager.executor.execute(job)
        with self.assertRaises(ValueError):
            manager.executor.execute(job)
        self.running(manager, job)
        job.process.complete()
        self.finished(manager, job)
        next_job = manager.submit_job(["next"])
        with manager.condition:
            self.assertFalse(manager.scheduler.finish_locked(job, 0))
        self.assertEqual(manager.scheduler.counts()[0], 1)
        self.running(manager, next_job)
        self.assertEqual(len(factory.processes), 2)

    def test_capacity_retained_until_reaped(self):
        manager, factory = self.make_manager(q=0)
        job = manager.submit_job(["first"])
        self.running(manager, job)
        process = job.process
        process.reap.clear()
        manager.cancel_job(job.id)
        with self.assertRaises(QueueFullError):
            manager.submit_job(["too-early"])
        self.assertEqual(manager.scheduler.counts()[0], 1)
        process.reap.set()
        self.finished(manager, job)
        self.running(manager, manager.submit_job(["after-reap"]))

    def test_shutdown_cancels_queue_and_running(self):
        manager, factory = self.make_manager()
        active = manager.submit_job(["active"])
        self.running(manager, active)
        pending = manager.submit_job(["pending"])
        manager.shutdown(0)
        self.assertEqual(active.status, "CANCELED")
        self.assertEqual(pending.status, "CANCELED")
        self.assertEqual(manager.scheduler.counts(), (0, 0))
        self.assertEqual(len(factory.processes), 1)
        self.assertFalse(manager.scheduler.dispatcher.is_alive())
        with self.assertRaises(RuntimeError):
            manager.submit_job(["after-stop"])

    def test_shutdown_allows_normal_completion(self):
        manager, factory = self.make_manager()
        job = manager.submit_job(["short"])
        self.running(manager, job)
        job.process.complete()
        manager.shutdown(1)
        self.assertEqual(job.status, "SUCCEEDED")

    def test_monitor_thread_start_failure_reaps(self):
        manager, factory = self.make_manager()
        original = threading.Thread.start

        def start(thread):
            if thread.name.startswith("jobsy-job-"):
                raise RuntimeError("No thread resources")
            return original(thread)

        with patch.object(threading.Thread, "start", start):
            job = manager.submit_job(["process"])
            self.finished(manager, job)
        self.assertIsNotNone(factory.processes[0].returncode)
        self.assertEqual(manager.scheduler.counts(), (0, 0))

    def test_dispatcher_start_failure_rolls_back(self):
        manager, factory = self.make_manager()
        with patch.object(threading.Thread, "start", side_effect=RuntimeError("no threads")):
            with self.assertRaises(RuntimeError):
                manager.submit_job(["process"])
        self.assertEqual(manager.jobs, {})
        self.assertEqual(manager.scheduler.counts(), (0, 0))

    def test_legacy_full_queue_leaves_no_residual(self):
        manager, factory = self.make_manager(q=0)
        manager.submit_job(["first"])
        job = manager.create_job(["legacy-rejected"])
        with self.assertRaises(QueueFullError):
            manager.executor.execute(job)
        self.assertNotIn(job.id, manager.jobs)

    def test_termination_escalation_waits_after_kill(self):
        from unittest.mock import Mock
        process = Mock()
        process.poll.return_value = None
        process.wait.side_effect = [subprocess.TimeoutExpired("test", 2), -9]
        Executor.terminate_and_reap(process)
        process.terminate.assert_called_once_with()
        process.kill.assert_called_once_with()
        self.assertEqual(process.wait.call_count, 2)

    def test_slow_collection_does_not_hold_shared_lock(self):
        manager, factory = self.make_manager()
        job = manager.submit_job(["first"])
        self.running(manager, job)
        # communicate is blocked on the fake process until completion.
        acquired = threading.Event()
        def inspect():
            manager.list_jobs()
            acquired.set()
        thread = threading.Thread(target=inspect)
        thread.start()
        self.assertTrue(acquired.wait(2))
        thread.join(2)


class ConfigTests(unittest.TestCase):
    def test_defaults_and_custom(self):
        self.assertEqual(parse_config([]), DaemonConfig(3, 100))
        self.assertEqual(parse_config(["--max-running", "1", "--queue-capacity", "0"]),
                         DaemonConfig(1, 0))

    def test_invalid_config(self):
        for n, q in ((0, 1), (-1, 1), (1, -1), (True, 1), (1, False)):
            with self.subTest(n=n, q=q), self.assertRaises(ValueError):
                DaemonConfig(n, q)

    def test_invalid_arguments_exit_two(self):
        import contextlib
        for args in (["--max-running", "0"], ["--queue-capacity", "-1"],
                     ["--max-running", "abc"], ["--unknown"]):
            with self.subTest(args=args), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as result:
                    parse_config(args)
                self.assertEqual(result.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
