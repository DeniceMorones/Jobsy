#!/usr/bin/env python3

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def section(title):
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


failures = 0


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

    return json.loads(b"".join(chunks).decode("utf-8"))


def send_and_disconnect(socket_path, payload):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    try:
        client.connect(socket_path)
        client.sendall(json.dumps(payload).encode("utf-8"))

        # Cerramos sin esperar la respuesta.
        client.shutdown(socket.SHUT_RDWR)

    except OSError:
        pass

    finally:
        client.close()


def wait_for_socket(path, daemon, timeout=5):
    deadline = time.time() + timeout

    while time.time() < deadline:
        if daemon.poll() is not None:
            raise RuntimeError(
                f"El daemon terminó inesperadamente con código {daemon.returncode}"
            )

        if os.path.exists(path):
            return

        time.sleep(0.05)

    raise RuntimeError("El daemon no creó el socket.")


def wait_for_state(socket_path, job_id, states, timeout=10):
    deadline = time.time() + timeout
    last = None

    while time.time() < deadline:
        last = send_request(
            socket_path,
            {
                "action": "status",
                "job_id": job_id,
            },
        )

        if (
            last.get("status") == "ok"
            and last["job"]["status"] in states
        ):
            return last

        time.sleep(0.05)

    return last


def read_log(path):
    time.sleep(0.2)

    if not path.exists():
        return ""

    return path.read_text(encoding="utf-8")


def main():
    global failures

    with tempfile.TemporaryDirectory(prefix="jobsy-queue-observability-") as temp_dir:
        temp = Path(temp_dir)

        socket_path = str(temp / "jobsy.sock")
        data_dir = temp / "data"
        log_path = data_dir / "jobsy.log"

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
                "1",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        try:
            wait_for_socket(socket_path, daemon)

            # ----------------------------------------------------------
            section("TC-121 - COLA LLENA QUEDA REGISTRADA EN JOBSY.LOG")
            # ----------------------------------------------------------

            running = send_request(
                socket_path,
                {
                    "action": "run",
                    "command": [
                        sys.executable,
                        "-c",
                        "import time; time.sleep(30)",
                    ],
                },
            )

            running_id = running.get("job_id")

            check(
                running.get("status") == "ok"
                and bool(running_id),
                "El primer trabajo ocupa la reserva de ejecución.",
            )

            wait_for_state(
                socket_path,
                running_id,
                {"RUNNING"},
            )

            queued = send_request(
                socket_path,
                {
                    "action": "run",
                    "command": [
                        sys.executable,
                        "-c",
                        "import time; time.sleep(30)",
                    ],
                },
            )

            queued_id = queued.get("job_id")

            check(
                queued.get("status") == "ok"
                and bool(queued_id),
                "El segundo trabajo ocupa la cola.",
            )

            wait_for_state(
                socket_path,
                queued_id,
                {"QUEUED"},
            )

            before_full = read_log(log_path)

            rejected = send_request(
                socket_path,
                {
                    "action": "run",
                    "command": [
                        sys.executable,
                        "-c",
                        "print('no debe ejecutarse')",
                    ],
                },
            )

            check(
                rejected.get("status") == "error",
                "La tercera solicitud es rechazada por falta de capacidad.",
            )

            after_full = read_log(log_path)
            full_text = after_full[len(before_full):]

            check(
                "rechazada por límite de capacidad" in full_text
                or "Cola llena" in full_text,
                "El rechazo por cola llena queda registrado en jobsy.log.",
            )

            # ----------------------------------------------------------
            section("TC-122 - RECHAZO POR COLA LLENA INCLUYE REQID")
            # ----------------------------------------------------------

            check(
                "[ReqID:" in full_text,
                "El evento de rechazo por capacidad contiene un ReqID.",
            )

            # Limpiar cola antes del siguiente escenario.
            send_request(
                socket_path,
                {
                    "action": "cancel",
                    "job_id": queued_id,
                },
            )

            send_request(
                socket_path,
                {
                    "action": "cancel",
                    "job_id": running_id,
                },
            )

            wait_for_state(
                socket_path,
                running_id,
                {"CANCELED"},
            )

            # ----------------------------------------------------------
            section("TC-123 - DESCONEXION PREMATURA DEL CLIENTE QUEDA REGISTRADA")
            # ----------------------------------------------------------

            before_disconnect = read_log(log_path)

            send_and_disconnect(
                socket_path,
                {
                    "action": "run",
                    "command": [
                        sys.executable,
                        "-c",
                        "import time; time.sleep(0.2)",
                    ],
                },
            )

            time.sleep(0.5)

            after_disconnect = read_log(log_path)
            disconnect_text = after_disconnect[len(before_disconnect):]

            check(
                "Cliente desconectado prematuramente" in disconnect_text,
                "La desconexión prematura del cliente queda registrada.",
            )

            # ----------------------------------------------------------
            section("TC-124 - LOG INDICA ESTADO DE OPERACION TRAS DESCONEXION")
            # ----------------------------------------------------------

            check(
                "Estado de la operación:" in disconnect_text,
                "El log indica el estado de la operación cuando el cliente se desconecta.",
            )

            check(
                "ACEPTADA" in disconnect_text
                or "RECHAZADA" in disconnect_text
                or "SIN_EFECTO" in disconnect_text,
                "El estado registrado de la operación es explícito.",
            )

            # ----------------------------------------------------------
            section("TC-125 - DAEMON SOBREVIVE A DESCONEXION DEL CLIENTE")
            # ----------------------------------------------------------

            check(
                daemon.poll() is None,
                "El proceso del daemon continúa activo después de la desconexión.",
            )

            # ----------------------------------------------------------
            section("TC-126 - SOLICITUD POSTERIOR SIGUE FUNCIONANDO")
            # ----------------------------------------------------------

            final_response = send_request(
                socket_path,
                {
                    "action": "list",
                },
            )

            check(
                final_response.get("status") == "ok",
                "El daemon procesa una solicitud válida después de la desconexión.",
            )

            check(
                daemon.poll() is None,
                "El daemon permanece operativo al finalizar la prueba.",
            )

        finally:
            if daemon.poll() is None:
                daemon.terminate()

                try:
                    daemon.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    daemon.kill()
                    daemon.wait(timeout=5)

    section("RESULTADO GENERAL")

    if failures == 0:
        print("RESULTADO GENERAL: PASS")
        return 0

    print(f"RESULTADO GENERAL: FAIL ({failures} comprobaciones fallidas)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
