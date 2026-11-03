"""Isolated real-child tests; no daemon or operational socket."""
import sys
import unittest

from src.daemon.config import DaemonConfig
from src.daemon.job_manager import JobManager


class ProcessTests(unittest.TestCase):
    def manager(self, n=1):
        manager = JobManager(DaemonConfig(n, 4))
        self.addCleanup(manager.shutdown, 0)
        return manager

    def wait_for(self, manager, predicate):
        with manager.condition:
            self.assertTrue(manager.condition.wait_for(predicate, 10))

    def test_real_limits_and_shutdown(self):
        for n in (1, 3):
            with self.subTest(n=n):
                manager = self.manager(n)
                jobs = [manager.submit_job([sys.executable, "-c", "import time; time.sleep(60)"])
                        for _ in range(n + 1)]
                self.wait_for(manager, lambda: all(j.status == "RUNNING" for j in jobs[:n]))
                children = [j.process for j in jobs[:n]]
                self.assertTrue(all(p.poll() is None for p in children))
                self.assertEqual(jobs[-1].status, "QUEUED")
                self.assertEqual(manager.scheduler.counts(), (n, 1))
                manager.shutdown(0)
                self.assertTrue(all(p.poll() is not None for p in children))
                self.assertTrue(all(j.status == "CANCELED" for j in jobs))
                self.assertIsNone(jobs[-1].started_at)

    def test_capture_exit_and_spawn_failure(self):
        manager = self.manager()
        commands = [
            [sys.executable, "-c", "import sys; print('out'); print('err', file=sys.stderr)"],
            [sys.executable, "-c", "raise SystemExit(7)"],
            ["jobsy-test-nonexistent-executable-4834"],
        ]
        jobs = [manager.submit_job(command) for command in commands]
        self.wait_for(manager, lambda: not manager.scheduler.reservations and not manager.scheduler.pending)
        self.assertEqual([j.status for j in jobs], ["SUCCEEDED", "FAILED", "FAILED"])
        self.assertEqual(jobs[0].stdout.strip(), "out")
        self.assertEqual(jobs[0].stderr.strip(), "err")
        self.assertEqual(jobs[1].exit_code, 7)

    def test_cancel_reaps_then_dispatches(self):
        manager = self.manager()
        active = manager.submit_job([sys.executable, "-c", "import time; time.sleep(60)"])
        self.wait_for(manager, lambda: active.status == "RUNNING")
        child = active.process
        following = manager.submit_job([sys.executable, "-c", "print('next')"])
        manager.cancel_job(active.id)
        self.wait_for(manager, lambda: following.status == "SUCCEEDED")
        self.assertIsNotNone(child.returncode)
        self.assertEqual(active.status, "CANCELED")
        self.assertIsNotNone(active.finished_at)
        self.assertEqual(manager.scheduler.counts(), (0, 0))


if __name__ == "__main__":
    unittest.main()
