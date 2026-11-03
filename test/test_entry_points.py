"""Entry-point regressions: no real IPC, child processes, or socket cleanup."""

import contextlib
import io
import json
import runpy
import socket
import sys
import unittest
from unittest.mock import patch

from src.client import cli
from src.daemon import server
from src.daemon.config import DaemonConfig


class EntryPointTests(unittest.TestCase):
    def invoke(self, function, argv, response=None, code=0):
        if response is None:
            response = {"status": "ok", "job_id": "example-id"}
        with patch.object(cli, "send_ipc_request", return_value=response) as request:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as result:
                    function(argv)
            self.assertEqual(result.exception.code, code)
        return request

    def test_execute_maps_to_run(self):
        request = self.invoke(cli.execute_main, ["sleep", "20"])
        request.assert_called_once_with({"action": "run", "command": ["sleep", "20"]})

    def test_execute_preserves_argument_boundaries(self):
        for command in (["ls", "-l", "/tmp"],
                        ["printf", "%s", "hello world", "", "--help", "--"],
                        ["/path with spaces/program"], ["sleep 20"]):
            with self.subTest(command=command):
                original = list(command)
                request = self.invoke(cli.execute_main, command)
                request.assert_called_once_with({"action": "run", "command": original})
                self.assertEqual(command, original)

    def test_execute_uses_sys_argv(self):
        with patch.object(sys, "argv", ["execute", "sleep", "20"]):
            request = self.invoke(cli.execute_main, None)
        request.assert_called_once_with({"action": "run", "command": ["sleep", "20"]})

    def test_missing_command_is_syntax_error(self):
        for function in (cli.main, cli.execute_main):
            with self.subTest(function=function.__name__):
                self.invoke(function, [], code=2).assert_not_called()

    def test_legacy_run_arguments_and_single_string(self):
        for argv in (["run", "--", "sleep", "20"], ["run", "sleep 20"]):
            with self.subTest(argv=argv):
                request = self.invoke(cli.main, argv)
                request.assert_called_once_with({"action": "run", "command": ["sleep", "20"]})

    def test_jobsy_uses_sys_argv(self):
        with patch.object(sys, "argv", ["jobsy", "list"]):
            request = self.invoke(cli.main, None, {"status": "ok", "jobs": []})
        request.assert_called_once_with({"action": "list", "status": None})

    def test_list_and_filter_mapping(self):
        for argv, status in ((["list"], None), (["list", "--status", "RUNNING"], "RUNNING")):
            with self.subTest(argv=argv):
                request = self.invoke(cli.main, argv, {"status": "ok", "jobs": []})
                request.assert_called_once_with({"action": "list", "status": status})

    def test_status_mapping(self):
        job = dict(id="example-id", command=["sleep", "20"], status="RUNNING",
                   received_at="now", started_at="now", finished_at="-", exit_code=None)
        request = self.invoke(cli.main, ["status", "example-id"], {"status": "ok", "job": job})
        request.assert_called_once_with({"action": "status", "job_id": "example-id"})

    def test_cancel_mapping(self):
        request = self.invoke(cli.main, ["cancel", "example-id"],
                              {"status": "ok", "job_id": "example-id", "job_status": "CANCELED"})
        request.assert_called_once_with({"action": "cancel", "job_id": "example-id"})

    def test_error_exit_codes_preserved(self):
        self.invoke(cli.main, ["list", "--status", "INVALID"], code=2).assert_not_called()
        self.invoke(cli.execute_main, ["sleep", "20"],
                    {"status": "error", "message": "rejected"}, code=1)

    def test_daemon_entry_point_delegates_once(self):
        with patch.object(server, "DaemonServer") as daemon:
            server.main([])
        daemon.assert_called_once_with(config=DaemonConfig())
        daemon.return_value.start.assert_called_once_with()

    def test_daemon_constructor_retains_signal_registration(self):
        with patch.object(server.signal, "signal") as register:
            daemon = server.DaemonServer()
        self.assertEqual(register.call_count, 2)
        register.assert_any_call(server.signal.SIGINT, daemon._handle_shutdown_signal)
        register.assert_any_call(server.signal.SIGTERM, daemon._handle_shutdown_signal)

    def test_legacy_cli_module_entry_point(self):
        # Run the real __main__ block, replacing socket operations before execution.
        with patch("socket.socket") as socket_factory, patch("os.path.exists", return_value=True), \
                patch.object(socket, "AF_UNIX", 1, create=True):
            connection = socket_factory.return_value.__enter__.return_value
            connection.recv.return_value = b'{"status":"ok","job_id":"example-id"}'
            with patch.object(sys, "argv", ["src.client.cli", "run", "--", "sleep", "20"]):
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as result:
                        # Avoid runpy's warning about this already imported module.
                        with patch.dict(sys.modules):
                            sys.modules.pop("src.client.cli", None)
                            runpy.run_module("src.client.cli", run_name="__main__")
            self.assertEqual(result.exception.code, 0)
            payload = json.loads(connection.sendall.call_args.args[0])
            self.assertEqual(payload, {"action": "run", "command": ["sleep", "20"]})

    def test_legacy_daemon_module_entry_point(self):
        # Stop at construction; start delegation and signals are tested separately.
        class StartupReached(Exception):
            pass

        with patch("src.daemon.job_manager.JobManager", side_effect=StartupReached) as manager:
            with patch.dict(sys.modules), patch.object(sys, "argv", ["src.daemon.server"]):
                sys.modules.pop("src.daemon.server", None)
                with self.assertRaises(StartupReached):
                    runpy.run_module("src.daemon.server", run_name="__main__")
            manager.assert_called_once_with(DaemonConfig())

    def test_short_commands_map_arguments(self):
        for function, action, argv in (
            (cli.list_main, "list", []),
            (cli.list_main, "list", ["--status", "RUNNING"]),
            (cli.status_main, "status", ["example-id"]),
            (cli.cancel_main, "cancel", ["example-id"]),
        ):
            with self.subTest(action=action, argv=argv):
                original = list(argv)
                with patch.object(cli, "main", return_value=7) as main:
                    self.assertEqual(function(argv), 7)
                main.assert_called_once_with([action, *original])
                self.assertEqual(argv, original)

    def test_short_commands_use_sys_argv(self):
        for function, action in ((cli.list_main, "list"), (cli.status_main, "status"),
                                 (cli.cancel_main, "cancel")):
            with self.subTest(action=action):
                with patch.object(sys, "argv", [action, "--help"]):
                    with patch.object(cli, "main") as main:
                        function()
                main.assert_called_once_with([action, "--help"])

    def test_short_commands_reach_existing_ipc(self):
        job = dict(id="example-id", command=["sleep", "20"], status="RUNNING",
                   received_at="now", started_at="now", finished_at="-", exit_code=None)
        cases = (
            (cli.list_main, [], {"status": "ok", "jobs": []}, {"action": "list", "status": None}),
            (cli.list_main, ["--status", "RUNNING"], {"status": "ok", "jobs": []},
             {"action": "list", "status": "RUNNING"}),
            (cli.status_main, ["example-id"], {"status": "ok", "job": job},
             {"action": "status", "job_id": "example-id"}),
            (cli.cancel_main, ["example-id"],
             {"status": "ok", "job_id": "example-id", "job_status": "CANCELED"},
             {"action": "cancel", "job_id": "example-id"}),
        )
        for function, argv, response, payload in cases:
            with self.subTest(function=function.__name__, argv=argv):
                self.invoke(function, argv, response).assert_called_once_with(payload)

    def test_short_commands_reject_invalid_syntax(self):
        cases = ((cli.status_main, []), (cli.cancel_main, []),
                 (cli.list_main, ["unexpected"]), (cli.list_main, ["--status"]),
                 (cli.list_main, ["--status", "INVALID"]),
                 (cli.status_main, ["id", "extra"]), (cli.cancel_main, ["--unknown"]))
        for function, argv in cases:
            with self.subTest(function=function.__name__, argv=argv):
                self.invoke(function, argv, code=2).assert_not_called()

    def test_short_commands_preserve_service_error_code(self):
        for function, argv in ((cli.list_main, []), (cli.status_main, ["missing"]),
                               (cli.cancel_main, ["missing"])):
            with self.subTest(function=function.__name__):
                self.invoke(function, argv, {"status": "error", "message": "rejected"}, code=1)

    def test_short_commands_help_does_not_use_ipc(self):
        for function in (cli.list_main, cli.status_main, cli.cancel_main):
            with self.subTest(function=function.__name__):
                self.invoke(function, ["--help"]).assert_not_called()


if __name__ == "__main__":
    unittest.main()
