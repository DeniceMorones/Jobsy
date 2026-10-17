"""Linux-only integration using a private temporary Unix socket."""
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import time
import unittest


@unittest.skipUnless(os.name == "posix" and hasattr(socket, "AF_UNIX"), "Requires Linux/WSL Unix sockets")
class QueueIPCTests(unittest.TestCase):
    def test_private_daemon_protocol_and_shutdown(self):
        with tempfile.TemporaryDirectory(prefix="jobsy-test-") as directory:
            path = str(Path(directory) / "private.sock")
            code = ("import sys; from src.daemon.server import DaemonServer; "
                    "from src.daemon.config import DaemonConfig; "
                    "DaemonServer(config=DaemonConfig(1,1), socket_path=sys.argv[1]).start()")
            child = subprocess.Popen([sys.executable, "-B", "-c", code, path],
                                     cwd=Path(__file__).resolve().parents[1],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                     start_new_session=True)
            try:
                deadline = time.monotonic() + 10
                while not os.path.exists(path):
                    self.assertIsNone(child.poll(), "Private daemon exited before binding")
                    self.assertLess(time.monotonic(), deadline)
                    time.sleep(0.01)

                def request(value):
                    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                        client.settimeout(3)
                        client.connect(path)
                        client.sendall(json.dumps(value).encode())
                        return json.loads(client.recv(65536))

                command = [sys.executable, "-c", "import time; time.sleep(60)"]
                first = request({"action": "run", "command": command})
                second = request({"action": "run", "command": command})
                rejected = request({"action": "run", "command": command})
                self.assertEqual(first["status"], "ok")
                self.assertEqual(second["status"], "ok")
                self.assertEqual(rejected["status"], "error")
                self.assertIn("Cola llena", rejected["message"])
                self.assertEqual(len(request({"action": "list"})["jobs"]), 2)
                canceled = request({"action": "cancel", "job_id": second["job_id"]})
                self.assertEqual(canceled["job_status"], "CANCELED")
                status = request({"action": "status", "job_id": second["job_id"]})
                self.assertEqual(status["job"]["started_at"], "-")
                child.send_signal(signal.SIGTERM)
                output, errors = child.communicate(timeout=12)
                self.assertEqual(child.returncode, 0, output + errors)
                self.assertFalse(os.path.exists(path))
            finally:
                if child.poll() is None:
                    child.send_signal(signal.SIGTERM)
                    try:
                        child.communicate(timeout=12)
                    except subprocess.TimeoutExpired:
                        # Only the isolated process group created by this test.
                        os.killpg(child.pid, signal.SIGKILL)
                        child.communicate(timeout=3)

    def test_legacy_invalid_configuration_exits_before_binding(self):
        result = subprocess.run([sys.executable, "-B", "-m", "src.daemon.server",
                                 "--max-running", "0"], capture_output=True, text=True,
                                cwd=Path(__file__).resolve().parents[1], timeout=5)
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
