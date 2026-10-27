#!/usr/bin/env python3

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import uuid
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


def send_raw(socket_path, raw):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.connect(socket_path)
        client.sendall(raw)
        client.shutdown(socket.SHUT_WR)

        chunks = []

        while True:
            data = client.recv(65536)

            if not data:
                break

            chunks.append(data)

    return json.loads(b"".join(chunks).decode("utf-8"))


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

    raise RuntimeError("El daemon no creó el socket dentro del tiempo esperado.")


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


def has_structured_error(response):
    return (
        response.get("status") == "error"
        and isinstance(response.get("operation"), str)
        and bool(response.get("operation"))
        and isinstance(response.get("cause"), str)
        and bool(response.get("cause"))
        and isinstance(response.get("suggestion"), str)
        and bool(response.get("suggestion"))
    )


def main():
    global failures

    with tempfile.TemporaryDirectory(prefix="jobsy-errors-") as temp_dir:
        temp = Path(temp_dir)

        socket_path = str(temp / "jobsy.sock")
        data_dir = temp / "data"

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
            section("TC-107 - ACCION IPC INVALIDA DEVUELVE ERROR ESTRUCTURADO")
            # ----------------------------------------------------------

            invalid_action = send_request(
                socket_path,
                {
                    "action": "accion_invalida",
                },
            )

            print(f"Respuesta: {invalid_action}")

            check(
                has_structured_error(invalid_action),
                "Una acción inválida devuelve status, operation, cause y suggestion.",
            )

            check(
                invalid_action.get("operation") == "accion_invalida",
                "El error conserva el nombre de la operación inválida.",
            )

            check(
                "no es reconocida" in invalid_action.get("cause", "").lower(),
                "La causa explica que la acción no es reconocida.",
            )

            # ----------------------------------------------------------
            section("TC-108 - JSON INVALIDO DEVUELVE ERROR ESTRUCTURADO")
            # ----------------------------------------------------------

            invalid_json = send_raw(
                socket_path,
                b"{esto_no_es_json",
            )

            print(f"Respuesta: {invalid_json}")

            check(
                has_structured_error(invalid_json),
                "Un JSON inválido devuelve un error estructurado.",
            )

            check(
                invalid_json.get("operation") == "desconocida",
                "Un JSON no interpretable utiliza la operación desconocida.",
            )

            check(
                bool(invalid_json.get("cause")),
                "La respuesta conserva la causa del error de JSON.",
            )

            # ----------------------------------------------------------
            section("TC-109 - STATUS DE ID INEXISTENTE DEVUELVE ERROR ESTRUCTURADO")
            # ----------------------------------------------------------

            missing_id = str(uuid.uuid4())

            missing_status = send_request(
                socket_path,
                {
                    "action": "status",
                    "job_id": missing_id,
                },
            )

            print(f"Respuesta: {missing_status}")

            check(
                has_structured_error(missing_status),
                "Consultar un ID inexistente devuelve un error estructurado.",
            )

            check(
                missing_status.get("operation") == "status",
                "El error identifica correctamente la operación status.",
            )

            check(
                missing_id in missing_status.get("cause", "")
                or "no existe" in missing_status.get("cause", "").lower()
                or "no encontrado" in missing_status.get("cause", "").lower(),
                "La causa informa que el trabajo solicitado no existe.",
            )

            # ----------------------------------------------------------
            section("TC-110 - CANCEL DE ID INEXISTENTE DEVUELVE ERROR ESTRUCTURADO")
            # ----------------------------------------------------------

            missing_cancel = send_request(
                socket_path,
                {
                    "action": "cancel",
                    "job_id": missing_id,
                },
            )

            print(f"Respuesta: {missing_cancel}")

            check(
                has_structured_error(missing_cancel),
                "Cancelar un ID inexistente devuelve un error estructurado.",
            )

            check(
                missing_cancel.get("operation") == "cancel",
                "El error identifica correctamente la operación cancel.",
            )

            # ----------------------------------------------------------
            section("TC-111 - COLA LLENA DEVUELVE CAUSA Y SUGERENCIA")
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
                "El primer trabajo ocupa la única reserva de ejecución.",
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
                "El segundo trabajo ocupa la única posición de la cola.",
            )

            wait_for_state(
                socket_path,
                queued_id,
                {"QUEUED"},
            )

            queue_full = send_request(
                socket_path,
                {
                    "action": "run",
                    "command": [
                        sys.executable,
                        "-c",
                        "print('no debe ser admitido')",
                    ],
                },
            )

            print(f"Respuesta: {queue_full}")

            check(
                has_structured_error(queue_full),
                "La cola llena devuelve un error estructurado.",
            )

            check(
                queue_full.get("operation") == "run",
                "El rechazo por capacidad identifica la operación run.",
            )

            check(
                "cola" in queue_full.get("cause", "").lower()
                or "capacidad" in queue_full.get("cause", "").lower(),
                "La causa del rechazo está relacionada con la capacidad de la cola.",
            )

            check(
                "espere" in queue_full.get("suggestion", "").lower()
                or "capacidad" in queue_full.get("suggestion", "").lower(),
                "El rechazo por cola llena incluye una acción sugerida útil.",
            )

            # Limpiar trabajos.
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

            # ----------------------------------------------------------
            section("TC-112 - CLI PRESENTA EL ERROR ESTRUCTURADO")
            # ----------------------------------------------------------

            cli_missing_id = str(uuid.uuid4())

            env = os.environ.copy()
            env["JOBSY_SOCKET_PATH"] = socket_path

            cli_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "src.client.cli",
                    "status",
                    cli_missing_id,
                ],
                env=env,
                capture_output=True,
                text=True,
                timeout=10,
            )

            print(f"Código CLI: {cli_result.returncode}")
            print(f"stdout: {cli_result.stdout!r}")
            print(f"stderr: {cli_result.stderr!r}")

            check(
                cli_result.returncode == 1,
                "La CLI devuelve código 1 ante un error del servidor.",
            )

            check(
                "Error en la operación 'status'" in cli_result.stderr,
                "La CLI muestra la operación que produjo el error.",
            )

            check(
                "Causa:" in cli_result.stderr,
                "La CLI muestra la causa del error.",
            )

            check(
                "Acción sugerida:" in cli_result.stderr,
                "La CLI muestra una acción sugerida.",
            )

            # ----------------------------------------------------------
            section("TC-113 - DAEMON SIGUE OPERATIVO DESPUES DE ERRORES")
            # ----------------------------------------------------------

            final_response = send_request(
                socket_path,
                {
                    "action": "list",
                },
            )

            check(
                daemon.poll() is None,
                "El proceso del daemon continúa activo después de solicitudes erróneas.",
            )

            check(
                final_response.get("status") == "ok",
                "El daemon continúa procesando solicitudes válidas después de errores.",
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
