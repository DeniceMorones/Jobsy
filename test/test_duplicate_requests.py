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

    raw = b"".join(chunks).decode("utf-8")
    return json.loads(raw)


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


def wait_for_terminal(socket_path, job_id, timeout=10):
    deadline = time.time() + timeout
    last_response = None

    while time.time() < deadline:
        last_response = send_request(
            socket_path,
            {
                "action": "status",
                "job_id": job_id,
            },
        )

        if last_response.get("status") == "ok":
            state = last_response["job"]["status"]

            if state in {"SUCCEEDED", "FAILED", "CANCELED"}:
                return last_response

        time.sleep(0.05)

    return last_response


def wait_for_finished_at(socket_path, job_id, timeout=5):
    deadline = time.time() + timeout
    last_response = None

    while time.time() < deadline:
        last_response = send_request(
            socket_path,
            {
                "action": "status",
                "job_id": job_id,
            },
        )

        if last_response.get("status") == "ok":
            job = last_response["job"]

            if job["status"] == "CANCELED" and job["finished_at"] != "-":
                return last_response

        time.sleep(0.05)

    return last_response


def is_uuid4(value):
    try:
        parsed = uuid.UUID(value)
        return parsed.version == 4 and str(parsed) == value
    except (ValueError, TypeError, AttributeError):
        return False


def main():
    global failures

    with tempfile.TemporaryDirectory(prefix="jobsy-pr116-") as temp_dir:
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
                "2",
                "--queue-capacity",
                "10",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        try:
            wait_for_socket(socket_path, daemon)

            # ----------------------------------------------------------
            section("TC-091 - LIST DUPLICADO NO ALTERA EL ESTADO")
            # ----------------------------------------------------------

            list_1 = send_request(
                socket_path,
                {
                    "action": "list",
                },
            )

            list_2 = send_request(
                socket_path,
                {
                    "action": "list",
                },
            )

            check(
                list_1.get("status") == "ok"
                and list_2.get("status") == "ok",
                "Las dos solicitudes list son procesadas correctamente.",
            )

            check(
                list_1.get("jobs") == list_2.get("jobs"),
                "Repetir list devuelve el mismo estado sin modificar trabajos.",
            )

            # ----------------------------------------------------------
            section("TC-092 - STATUS DUPLICADO CONSERVA METADATOS")
            # ----------------------------------------------------------

            status_run = send_request(
                socket_path,
                {
                    "action": "run",
                    "command": [
                        sys.executable,
                        "-c",
                        "print('qa-status-duplicado')",
                    ],
                },
            )

            status_job_id = status_run.get("job_id")

            check(
                status_run.get("status") == "ok"
                and bool(status_job_id),
                "El trabajo usado para probar status es aceptado.",
            )

            terminal = wait_for_terminal(
                socket_path,
                status_job_id,
            )

            check(
                terminal is not None
                and terminal.get("status") == "ok"
                and terminal["job"]["status"] == "SUCCEEDED",
                "El trabajo termina correctamente antes de consultar status repetido.",
            )

            status_1 = send_request(
                socket_path,
                {
                    "action": "status",
                    "job_id": status_job_id,
                },
            )

            status_2 = send_request(
                socket_path,
                {
                    "action": "status",
                    "job_id": status_job_id,
                },
            )

            check(
                status_1.get("job") == status_2.get("job"),
                "Dos consultas status consecutivas conservan todos los metadatos.",
            )

            # ----------------------------------------------------------
            section("TC-093 - OUTPUT DUPLICADO CONSERVA STDOUT Y STDERR")
            # ----------------------------------------------------------

            output_run = send_request(
                socket_path,
                {
                    "action": "run",
                    "command": [
                        sys.executable,
                        "-c",
                        (
                            "import sys; "
                            "print('stdout-rf27'); "
                            "print('stderr-rf27', file=sys.stderr)"
                        ),
                    ],
                },
            )

            output_job_id = output_run.get("job_id")

            check(
                output_run.get("status") == "ok"
                and bool(output_job_id),
                "El trabajo usado para probar output es aceptado.",
            )

            wait_for_terminal(
                socket_path,
                output_job_id,
            )

            output_1 = send_request(
                socket_path,
                {
                    "action": "output",
                    "job_id": output_job_id,
                },
            )

            output_2 = send_request(
                socket_path,
                {
                    "action": "output",
                    "job_id": output_job_id,
                },
            )

            check(
                output_1.get("stdout") == output_2.get("stdout")
                and output_1.get("stderr") == output_2.get("stderr"),
                "Repetir output conserva exactamente stdout y stderr.",
            )

            check(
                output_1.get("stdout") == "stdout-rf27\n"
                and output_1.get("stderr") == "stderr-rf27\n",
                "La salida recuperada conserva el contenido original.",
            )

            # ----------------------------------------------------------
            section("TC-094 - CANCEL DUPLICADO NO GENERA SEGUNDA TRANSICION")
            # ----------------------------------------------------------

            cancel_run = send_request(
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

            cancel_job_id = cancel_run.get("job_id")

            check(
                cancel_run.get("status") == "ok"
                and bool(cancel_job_id),
                "El trabajo de larga duración es aceptado.",
            )

            first_cancel = send_request(
                socket_path,
                {
                    "action": "cancel",
                    "job_id": cancel_job_id,
                },
            )

            check(
                first_cancel.get("status") == "ok"
                and first_cancel.get("job_status") == "CANCELED",
                "La primera solicitud cancel cambia el trabajo a CANCELED.",
            )

            stable_cancel = wait_for_finished_at(
                socket_path,
                cancel_job_id,
            )

            before_duplicate = stable_cancel["job"].copy()

            second_cancel = send_request(
                socket_path,
                {
                    "action": "cancel",
                    "job_id": cancel_job_id,
                },
            )

            check(
                second_cancel.get("status") == "error",
                "La segunda cancelación es rechazada de forma controlada.",
            )

            check(
                "ya fue solicitada" in second_cancel.get("cause", "").lower()
                or "canceled" in second_cancel.get("cause", "").lower(),
                "La segunda cancelación informa que la cancelación ya fue solicitada.",
            )

            # ----------------------------------------------------------
            section("TC-095 - CANCEL DUPLICADO CONSERVA ESTADO Y TIMESTAMPS")
            # ----------------------------------------------------------

            after_duplicate_response = send_request(
                socket_path,
                {
                    "action": "status",
                    "job_id": cancel_job_id,
                },
            )

            after_duplicate = after_duplicate_response["job"]

            check(
                after_duplicate["status"] == "CANCELED",
                "El estado permanece CANCELED después del segundo cancel.",
            )

            check(
                before_duplicate["received_at"] == after_duplicate["received_at"]
                and before_duplicate["started_at"] == after_duplicate["started_at"]
                and before_duplicate["finished_at"] == after_duplicate["finished_at"],
                "La cancelación duplicada no modifica los timestamps del trabajo.",
            )

            # ----------------------------------------------------------
            section("TC-096 - RUN DUPLICADO CREA UUID DIFERENTES")
            # ----------------------------------------------------------

            duplicate_payload = {
                "action": "run",
                "command": [
                    sys.executable,
                    "-c",
                    "import time; time.sleep(30)",
                ],
            }

            run_1 = send_request(
                socket_path,
                duplicate_payload,
            )

            run_2 = send_request(
                socket_path,
                duplicate_payload,
            )

            duplicate_id_1 = run_1.get("job_id")
            duplicate_id_2 = run_2.get("job_id")

            check(
                run_1.get("status") == "ok"
                and run_2.get("status") == "ok",
                "Las dos solicitudes run idénticas son aceptadas.",
            )

            check(
                duplicate_id_1 != duplicate_id_2,
                "Dos solicitudes run idénticas generan identificadores diferentes.",
            )

            check(
                is_uuid4(duplicate_id_1)
                and is_uuid4(duplicate_id_2),
                "Los dos identificadores generados son UUIDv4 válidos.",
            )

            # ----------------------------------------------------------
            section("TC-097 - RUN DUPLICADO CREA TRABAJOS INDEPENDIENTES")
            # ----------------------------------------------------------

            duplicate_status_1 = send_request(
                socket_path,
                {
                    "action": "status",
                    "job_id": duplicate_id_1,
                },
            )

            duplicate_status_2 = send_request(
                socket_path,
                {
                    "action": "status",
                    "job_id": duplicate_id_2,
                },
            )

            check(
                duplicate_status_1.get("status") == "ok"
                and duplicate_status_2.get("status") == "ok",
                "Ambos trabajos creados pueden consultarse independientemente.",
            )

            check(
                duplicate_status_1["job"]["command"]
                == duplicate_status_2["job"]["command"],
                "Ambos trabajos conservan el mismo comando solicitado.",
            )

            send_request(
                socket_path,
                {
                    "action": "cancel",
                    "job_id": duplicate_id_1,
                },
            )

            status_after_cancel_1 = send_request(
                socket_path,
                {
                    "action": "status",
                    "job_id": duplicate_id_1,
                },
            )

            status_after_cancel_2 = send_request(
                socket_path,
                {
                    "action": "status",
                    "job_id": duplicate_id_2,
                },
            )

            check(
                status_after_cancel_1["job"]["status"] == "CANCELED",
                "Cancelar el primer trabajo duplicado afecta únicamente a ese trabajo.",
            )

            check(
                status_after_cancel_2["job"]["status"] != "CANCELED",
                "El segundo trabajo duplicado permanece independiente.",
            )

            # Limpiar segundo trabajo.
            if status_after_cancel_2["job"]["status"] in {"QUEUED", "RUNNING"}:
                send_request(
                    socket_path,
                    {
                        "action": "cancel",
                        "job_id": duplicate_id_2,
                    },
                )

            # ----------------------------------------------------------
            section("TC-098 - DAEMON SIGUE OPERATIVO TRAS SOLICITUDES DUPLICADAS")
            # ----------------------------------------------------------

            final_list = send_request(
                socket_path,
                {
                    "action": "list",
                },
            )

            check(
                daemon.poll() is None,
                "El proceso del daemon continúa activo.",
            )

            check(
                final_list.get("status") == "ok",
                "El daemon continúa respondiendo después de solicitudes duplicadas.",
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
