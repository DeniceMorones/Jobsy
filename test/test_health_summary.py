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


def health(socket_path):
    return send_request(
        socket_path,
        {
            "action": "health",
        },
    )


def main():
    global failures

    with tempfile.TemporaryDirectory(prefix="jobsy-health-") as temp_dir:
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
                "20",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        try:
            wait_for_socket(socket_path, daemon)

            # ----------------------------------------------------------
            section("TC-099 - HEALTH RESPONDE CON ESTRUCTURA ESPERADA")
            # ----------------------------------------------------------

            h = health(socket_path)

            check(
                h.get("status") == "ok",
                "La operación health responde con status ok.",
            )

            data = h.get("health", {})

            expected_keys = {
                "service_active",
                "storage_error",
                "running_count",
                "running_jobs",
                "queued_count",
                "queued_jobs",
                "recent_errors_count",
                "recent_errors",
            }

            check(
                expected_keys.issubset(data.keys()),
                "health contiene todos los campos esperados.",
            )

            # ----------------------------------------------------------
            section("TC-100 - HEALTH REPORTA SERVICIO ACTIVO")
            # ----------------------------------------------------------

            check(
                data.get("service_active") is True,
                "health reporta el daemon como servicio activo.",
            )

            check(
                data.get("storage_error") is None,
                "health no reporta error de almacenamiento en una sesión normal.",
            )

            # ----------------------------------------------------------
            section("TC-101 - HEALTH REPORTA TRABAJO RUNNING")
            # ----------------------------------------------------------

            running_run = send_request(
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

            running_id = running_run.get("job_id")

            check(
                running_run.get("status") == "ok"
                and bool(running_id),
                "El trabajo RUNNING de prueba es aceptado.",
            )

            running_state = wait_for_state(
                socket_path,
                running_id,
                {"RUNNING"},
            )

            check(
                running_state is not None
                and running_state.get("status") == "ok"
                and running_state["job"]["status"] == "RUNNING",
                "El trabajo alcanza el estado RUNNING.",
            )

            h_running = health(socket_path)["health"]

            running_ids = {
                job["id"]
                for job in h_running.get("running_jobs", [])
            }

            check(
                h_running.get("running_count") == 1,
                "health reporta exactamente un trabajo RUNNING.",
            )

            check(
                running_id in running_ids,
                "health incluye el trabajo RUNNING esperado.",
            )

            # ----------------------------------------------------------
            section("TC-102 - HEALTH REPORTA TRABAJO QUEUED")
            # ----------------------------------------------------------

            queued_run = send_request(
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

            queued_id = queued_run.get("job_id")

            check(
                queued_run.get("status") == "ok"
                and bool(queued_id),
                "El segundo trabajo es aceptado para quedar en cola.",
            )

            queued_state = wait_for_state(
                socket_path,
                queued_id,
                {"QUEUED"},
            )

            check(
                queued_state is not None
                and queued_state.get("status") == "ok"
                and queued_state["job"]["status"] == "QUEUED",
                "El segundo trabajo permanece en estado QUEUED.",
            )

            h_queued = health(socket_path)["health"]

            queued_ids = {
                job["id"]
                for job in h_queued.get("queued_jobs", [])
            }

            check(
                h_queued.get("queued_count") == 1,
                "health reporta exactamente un trabajo QUEUED.",
            )

            check(
                queued_id in queued_ids,
                "health incluye el trabajo QUEUED esperado.",
            )

            # Limpiar trabajos activos
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
            section("TC-103 - HEALTH REPORTA ERRORES RECIENTES")
            # ----------------------------------------------------------

            failed_run = send_request(
                socket_path,
                {
                    "action": "run",
                    "command": [
                        sys.executable,
                        "-c",
                        "import sys; sys.exit(7)",
                    ],
                },
            )

            failed_id = failed_run.get("job_id")

            check(
                failed_run.get("status") == "ok"
                and bool(failed_id),
                "El trabajo destinado a FAILED es aceptado.",
            )

            failed_state = wait_for_state(
                socket_path,
                failed_id,
                {"FAILED"},
            )

            check(
                failed_state is not None
                and failed_state.get("status") == "ok"
                and failed_state["job"]["status"] == "FAILED",
                "El trabajo termina en estado FAILED.",
            )

            h_failed = health(socket_path)["health"]

            recent_error_ids = {
                job["id"]
                for job in h_failed.get("recent_errors", [])
            }

            check(
                h_failed.get("recent_errors_count", 0) >= 1,
                "health reporta al menos un error reciente.",
            )

            check(
                failed_id in recent_error_ids,
                "health incluye el trabajo FAILED entre los errores recientes.",
            )

            # ----------------------------------------------------------
            section("TC-104 - HEALTH LIMITA ERRORES RECIENTES A 10")
            # ----------------------------------------------------------

            failed_ids = [failed_id]

            for index in range(11):
                response = send_request(
                    socket_path,
                    {
                        "action": "run",
                        "command": [
                            sys.executable,
                            "-c",
                            f"import sys; sys.exit({index % 10 + 1})",
                        ],
                    },
                )

                job_id = response.get("job_id")

                if job_id:
                    failed_ids.append(job_id)

                    wait_for_state(
                        socket_path,
                        job_id,
                        {"FAILED"},
                    )

            h_many_failed = health(socket_path)["health"]

            check(
                h_many_failed.get("recent_errors_count") == 10,
                "health limita los errores recientes a un máximo de 10.",
            )

            check(
                len(h_many_failed.get("recent_errors", [])) == 10,
                "La colección recent_errors contiene exactamente 10 elementos.",
            )

            # ----------------------------------------------------------
            section("TC-105 - HEALTH ES UNA OPERACION DE SOLO LECTURA")
            # ----------------------------------------------------------

            before = health(socket_path)

            time.sleep(0.1)

            after = health(socket_path)

            check(
                before.get("status") == "ok"
                and after.get("status") == "ok",
                "Dos solicitudes health consecutivas son procesadas correctamente.",
            )

            check(
                before.get("health") == after.get("health"),
                "Consultar health repetidamente no modifica el estado observado.",
            )

            # ----------------------------------------------------------
            section("TC-106 - DAEMON SIGUE OPERATIVO DESPUES DE HEALTH")
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
                "El daemon sigue respondiendo después de múltiples consultas health.",
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
