#!/usr/bin/env python3

import json
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path


failures = 0


def section(title):
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def check(condition, message):
    global failures

    if condition:
        print(f"PASS: {message}")
    else:
        print(f"FAIL: {message}")
        failures += 1


def send_request(socket_path, payload):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.connect(socket_path)
        client.sendall(json.dumps(payload).encode("utf-8"))
        client.shutdown(socket.SHUT_WR)

        chunks = []

        while True:
            data = client.recv(65536)

            if not data:
                break

            chunks.append(data)

    raw = b"".join(chunks).decode("utf-8")
    return json.loads(raw)


def wait_for_socket(socket_path, daemon, timeout=8):
    deadline = time.time() + timeout

    while time.time() < deadline:
        if daemon.poll() is not None:
            raise RuntimeError(
                f"El daemon terminó durante el arranque "
                f"con código {daemon.returncode}."
            )

        if os.path.exists(socket_path):
            return

        time.sleep(0.05)

    raise RuntimeError("El daemon no creó el socket dentro del tiempo esperado.")


def wait_for_state(socket_path, job_id, expected_states, timeout=10):
    deadline = time.time() + timeout
    last = None

    while time.time() < deadline:
        try:
            last = send_request(
                socket_path,
                {
                    "action": "status",
                    "job_id": job_id,
                },
            )

            if (
                last.get("status") == "ok"
                and last.get("job", {}).get("status") in expected_states
            ):
                return last
        except (OSError, ValueError, json.JSONDecodeError):
            pass

        time.sleep(0.05)

    return last


def wait_for_file(path, timeout=5):
    deadline = time.time() + timeout

    while time.time() < deadline:
        if path.exists():
            return True

        time.sleep(0.05)

    return False


def start_daemon(socket_path, data_dir, stdout_path, stderr_path):
    stdout_file = open(stdout_path, "ab")
    stderr_file = open(stderr_path, "ab")

    daemon = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "src.daemon.server",
            "--socket-path",
            socket_path,
            "--data-dir",
            str(data_dir),
            "--max-running",
            "1",
            "--queue-capacity",
            "4",
        ],
        stdout=stdout_file,
        stderr=stderr_file,
    )

    daemon._qa_stdout_file = stdout_file
    daemon._qa_stderr_file = stderr_file

    wait_for_socket(socket_path, daemon)
    return daemon


def close_daemon_files(daemon):
    for name in ("_qa_stdout_file", "_qa_stderr_file"):
        handle = getattr(daemon, name, None)

        if handle is not None:
            try:
                handle.close()
            except Exception:
                pass


def stop_daemon_gracefully(daemon):
    if daemon.poll() is not None:
        close_daemon_files(daemon)
        return

    daemon.terminate()

    try:
        daemon.wait(timeout=8)
    except subprocess.TimeoutExpired:
        daemon.kill()
        daemon.wait(timeout=5)

    close_daemon_files(daemon)


def stop_daemon_abruptly(daemon):
    if daemon.poll() is None:
        daemon.kill()
        daemon.wait(timeout=5)

    close_daemon_files(daemon)


def remove_test_socket(socket_path):
    try:
        os.unlink(socket_path)
    except FileNotFoundError:
        pass


def kill_test_process(pid):
    if not pid:
        return

    try:
        os.killpg(pid, signal.SIGKILL)
    except ProcessLookupError:
        return
    except PermissionError:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def main():
    global failures

    with tempfile.TemporaryDirectory(prefix="jobsy-recovery-qa-") as temp_dir:
        temp = Path(temp_dir)

        socket_path = str(temp / "jobsy.sock")
        data_dir = temp / "data"

        stdout_path = temp / "daemon-stdout.log"
        stderr_path = temp / "daemon-stderr.log"

        interrupted_pid_file = temp / "interrupted.pid"
        interrupted_marker = temp / "interrupted-starts.txt"
        queued_marker = temp / "queued-executed.txt"

        daemon = None

        try:
            # ==========================================================
            # ESCENARIO 1:
            # trabajo terminal + reinicio limpio
            # ==========================================================

            daemon = start_daemon(
                socket_path,
                data_dir,
                stdout_path,
                stderr_path,
            )

            terminal = send_request(
                socket_path,
                {
                    "action": "run",
                    "command": [
                        sys.executable,
                        "-c",
                        (
                            "import sys; "
                            "print('RECOVERY_STDOUT'); "
                            "print('RECOVERY_STDERR', file=sys.stderr)"
                        ),
                    ],
                },
            )

            terminal_id = terminal.get("job_id")

            terminal_status_before = wait_for_state(
                socket_path,
                terminal_id,
                {"SUCCEEDED"},
            )

            terminal_output_before = send_request(
                socket_path,
                {
                    "action": "output",
                    "job_id": terminal_id,
                },
            )

            stop_daemon_gracefully(daemon)
            daemon = None

            remove_test_socket(socket_path)

            daemon = start_daemon(
                socket_path,
                data_dir,
                stdout_path,
                stderr_path,
            )

            # ----------------------------------------------------------
            section("TC-127 - TRABAJO TERMINADO SE CONSERVA TRAS REINICIO")
            # ----------------------------------------------------------

            terminal_status_after = send_request(
                socket_path,
                {
                    "action": "status",
                    "job_id": terminal_id,
                },
            )

            check(
                terminal_status_before
                and terminal_status_before.get("job", {}).get("status")
                == "SUCCEEDED",
                "El trabajo termina en SUCCEEDED antes del reinicio.",
            )

            check(
                terminal_status_after.get("status") == "ok",
                "El trabajo terminal sigue disponible después del reinicio.",
            )

            check(
                terminal_status_after.get("job", {}).get("status")
                == "SUCCEEDED",
                "El trabajo terminal conserva el estado SUCCEEDED.",
            )

            # ----------------------------------------------------------
            section("TC-128 - RESULTADOS TERMINALES PERSISTEN TRAS REINICIO")
            # ----------------------------------------------------------

            terminal_output_after = send_request(
                socket_path,
                {
                    "action": "output",
                    "job_id": terminal_id,
                },
            )

            check(
                terminal_output_after.get("status") == "ok",
                "La salida del trabajo puede consultarse después del reinicio.",
            )

            check(
                terminal_output_before.get("stdout")
                == terminal_output_after.get("stdout"),
                "stdout se conserva sin cambios después del reinicio.",
            )

            check(
                terminal_output_before.get("stderr")
                == terminal_output_after.get("stderr"),
                "stderr se conserva sin cambios después del reinicio.",
            )

            # ==========================================================
            # ESCENARIO 2:
            # RUNNING interrumpido + QUEUED pendiente
            # ==========================================================

            interrupted_code = (
                "import os, pathlib, time; "
                f"pid_file=pathlib.Path({str(interrupted_pid_file)!r}); "
                f"marker=pathlib.Path({str(interrupted_marker)!r}); "
                "pid_file.write_text(str(os.getpid())); "
                "marker.write_text("
                "(marker.read_text() if marker.exists() else '') + 'START\\n'"
                "); "
                "time.sleep(60)"
            )

            interrupted = send_request(
                socket_path,
                {
                    "action": "run",
                    "command": [
                        sys.executable,
                        "-c",
                        interrupted_code,
                    ],
                },
            )

            interrupted_id = interrupted.get("job_id")

            interrupted_running = wait_for_state(
                socket_path,
                interrupted_id,
                {"RUNNING"},
            )

            check(
                interrupted_running
                and interrupted_running.get("job", {}).get("status")
                == "RUNNING",
                "El trabajo destinado a interrupción alcanza RUNNING.",
            )

            check(
                wait_for_file(interrupted_pid_file),
                "El proceso RUNNING registra su PID de prueba.",
            )

            queued_code = (
                "import pathlib; "
                f"pathlib.Path({str(queued_marker)!r})"
                ".write_text('EJECUTADO')"
            )

            queued = send_request(
                socket_path,
                {
                    "action": "run",
                    "command": [
                        sys.executable,
                        "-c",
                        queued_code,
                    ],
                },
            )

            queued_id = queued.get("job_id")

            queued_status_before = wait_for_state(
                socket_path,
                queued_id,
                {"QUEUED"},
            )

            check(
                queued_status_before
                and queued_status_before.get("job", {}).get("status")
                == "QUEUED",
                "El segundo trabajo permanece pendiente en QUEUED.",
            )

            # Simulamos caída abrupta únicamente del daemon de prueba.
            stop_daemon_abruptly(daemon)
            daemon = None

            interrupted_pid = None

            if interrupted_pid_file.exists():
                try:
                    interrupted_pid = int(
                        interrupted_pid_file.read_text().strip()
                    )
                except ValueError:
                    interrupted_pid = None

            # Eliminamos únicamente el proceso de trabajo creado por este test.
            kill_test_process(interrupted_pid)

            # Esperar a que el proceso haya desaparecido.
            time.sleep(0.3)

            # SIGKILL no permite al daemon retirar su socket.
            # Es un socket temporal propiedad exclusiva de este test.
            remove_test_socket(socket_path)

            # Reinicio usando exactamente el mismo data-dir.
            daemon = start_daemon(
                socket_path,
                data_dir,
                stdout_path,
                stderr_path,
            )

            # ----------------------------------------------------------
            section("TC-129 - TRABAJO PENDIENTE SE RECUPERA COMO CANCELED")
            # ----------------------------------------------------------

            queued_after = send_request(
                socket_path,
                {
                    "action": "status",
                    "job_id": queued_id,
                },
            )

            check(
                queued_after.get("status") == "ok",
                "El trabajo anteriormente QUEUED sigue disponible.",
            )

            check(
                queued_after.get("job", {}).get("status") == "CANCELED",
                "El trabajo pendiente se recupera como CANCELED.",
            )

            # ----------------------------------------------------------
            section("TC-130 - EJECUCION INTERRUMPIDA SE RECUPERA COMO FAILED")
            # ----------------------------------------------------------

            interrupted_after = send_request(
                socket_path,
                {
                    "action": "status",
                    "job_id": interrupted_id,
                },
            )

            check(
                interrupted_after.get("status") == "ok",
                "El trabajo interrumpido sigue disponible en el historial.",
            )

            check(
                interrupted_after.get("job", {}).get("status") == "FAILED",
                "La ejecución interrumpida se recupera como FAILED.",
            )

            # ----------------------------------------------------------
            section("TC-131 - TRABAJO INTERRUMPIDO NO SE REEJECUTA")
            # ----------------------------------------------------------

            time.sleep(0.5)

            starts = []

            if interrupted_marker.exists():
                starts = [
                    line
                    for line in interrupted_marker.read_text().splitlines()
                    if line.strip()
                ]

            check(
                len(starts) == 1,
                "El trabajo interrumpido se inició una sola vez y no fue reejecutado.",
            )

            # ----------------------------------------------------------
            section("TC-132 - TRABAJO PENDIENTE NO SE EJECUTA AL RECUPERAR")
            # ----------------------------------------------------------

            check(
                not queued_marker.exists(),
                "El trabajo que estaba QUEUED no se ejecuta automáticamente al recuperar.",
            )

            # ----------------------------------------------------------
            section("TC-133 - DAEMON QUEDA OPERATIVO DESPUES DE RECUPERACION")
            # ----------------------------------------------------------

            list_response = send_request(
                socket_path,
                {
                    "action": "list",
                },
            )

            check(
                list_response.get("status") == "ok",
                "El daemon responde a solicitudes después de la recuperación.",
            )

            check(
                daemon.poll() is None,
                "El proceso del daemon permanece activo después de recuperar el historial.",
            )

        finally:
            if daemon is not None:
                stop_daemon_gracefully(daemon)

            # Salvaguarda final: matar únicamente el PID creado por esta prueba.
            if interrupted_pid_file.exists():
                try:
                    pid = int(interrupted_pid_file.read_text().strip())
                    kill_test_process(pid)
                except (ValueError, OSError):
                    pass

            remove_test_socket(socket_path)

    section("RESULTADO GENERAL")

    if failures == 0:
        print("RESULTADO GENERAL: PASS")
        return 0

    print(
        f"RESULTADO GENERAL: FAIL "
        f"({failures} comprobaciones fallidas)"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
