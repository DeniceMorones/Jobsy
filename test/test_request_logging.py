#!/usr/bin/env python3

import json
import os
import re
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


def wait_for_log(path, timeout=5):
    deadline = time.time() + timeout

    while time.time() < deadline:
        if path.exists():
            return

        time.sleep(0.05)

    raise RuntimeError("No se creó jobsy.log dentro del tiempo esperado.")


def wait_for_state(socket_path, job_id, states, timeout=10):
    deadline = time.time() + timeout

    while time.time() < deadline:
        response = send_request(
            socket_path,
            {
                "action": "status",
                "job_id": job_id,
            },
        )

        if (
            response.get("status") == "ok"
            and response["job"]["status"] in states
        ):
            return response

        time.sleep(0.05)

    return response


def read_log(log_path):
    time.sleep(0.1)
    return log_path.read_text(encoding="utf-8")


def extract_reqids(text):
    return re.findall(r"\[ReqID:\s*([A-Za-z0-9-]+)\]", text)


def main():
    global failures

    with tempfile.TemporaryDirectory(prefix="jobsy-logging-") as temp_dir:
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
                "2",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        try:
            wait_for_socket(socket_path, daemon)
            wait_for_log(log_path)

            # ----------------------------------------------------------
            section("TC-114 - JOBSY.LOG SE CREA EN EL DATA-DIR")
            # ----------------------------------------------------------

            check(
                log_path.exists(),
                "El daemon crea jobsy.log dentro del data-dir configurado.",
            )

            check(
                log_path.is_file(),
                "jobsy.log es un archivo regular.",
            )

            # ----------------------------------------------------------
            section("TC-115 - FORMATO BASICO DE LA BITACORA")
            # ----------------------------------------------------------

            initial_log = read_log(log_path)

            print("Primeras líneas del log:")
            print("\n".join(initial_log.splitlines()[:5]))

            timestamp_pattern = re.compile(
                r"^\[\d{4}-\d{2}-\d{2} "
                r"\d{2}:\d{2}:\d{2}\.\d{3} UTC\] "
                r"\[(INFO|WARNING|ERROR)\] "
                r"\[Job: [^\]]+\]"
            )

            formatted_lines = [
                line
                for line in initial_log.splitlines()
                if timestamp_pattern.search(line)
            ]

            check(
                len(formatted_lines) > 0,
                "La bitácora utiliza timestamp UTC con milisegundos, nivel y Job ID.",
            )

            # ----------------------------------------------------------
            section("TC-116 - CADA SOLICITUD IPC RECIBE UN REQUEST_ID")
            # ----------------------------------------------------------

            before = read_log(log_path)

            list_response = send_request(
                socket_path,
                {
                    "action": "list",
                },
            )

            check(
                list_response.get("status") == "ok",
                "La solicitud list es procesada correctamente.",
            )

            after = read_log(log_path)
            new_text = after[len(before):]

            reqids = extract_reqids(new_text)

            check(
                len(reqids) >= 1,
                "La recepción de la solicitud IPC registra un ReqID.",
            )

            first_reqid = reqids[0] if reqids else None

            check(
                bool(first_reqid),
                "El ReqID registrado contiene un valor no vacío.",
            )

            # ----------------------------------------------------------
            section("TC-117 - SOLICITUDES DISTINTAS RECIBEN REQUEST_ID DIFERENTE")
            # ----------------------------------------------------------

            before_second = read_log(log_path)

            second_response = send_request(
                socket_path,
                {
                    "action": "list",
                },
            )

            after_second = read_log(log_path)
            second_text = after_second[len(before_second):]

            second_reqids = extract_reqids(second_text)
            second_reqid = second_reqids[0] if second_reqids else None

            check(
                second_response.get("status") == "ok",
                "La segunda solicitud list es procesada correctamente.",
            )

            check(
                first_reqid is not None
                and second_reqid is not None
                and first_reqid != second_reqid,
                "Dos solicitudes IPC distintas reciben ReqID diferentes.",
            )

            # ----------------------------------------------------------
            section("TC-118 - EVENTOS DE TRABAJO INCLUYEN JOB ID")
            # ----------------------------------------------------------

            run_response = send_request(
                socket_path,
                {
                    "action": "run",
                    "command": [
                        sys.executable,
                        "-c",
                        "print('qa-logging')",
                    ],
                },
            )

            job_id = run_response.get("job_id")

            check(
                run_response.get("status") == "ok"
                and bool(job_id),
                "El trabajo usado para validar logging es aceptado.",
            )

            wait_for_state(
                socket_path,
                job_id,
                {"SUCCEEDED", "FAILED"},
            )

            job_log = read_log(log_path)

            check(
                f"[Job: {job_id}]" in job_log,
                "Los eventos asociados al trabajo contienen su Job ID.",
            )

            check(
                "Trabajo creado en memoria" in job_log
                and "Iniciando ejecución" in job_log
                and "Trabajo finalizado" in job_log,
                "La bitácora registra creación, ejecución y finalización del trabajo.",
            )

            # ----------------------------------------------------------
            section("TC-119 - REQUEST_ID CORRELACIONA EL CICLO DE LA SOLICITUD RUN")
            # ----------------------------------------------------------

            before_run = read_log(log_path)

            correlated_run = send_request(
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

            correlated_job_id = correlated_run.get("job_id")

            check(
                correlated_run.get("status") == "ok"
                and bool(correlated_job_id),
                "La solicitud run para probar correlación es aceptada.",
            )

            wait_for_state(
                socket_path,
                correlated_job_id,
                {"SUCCEEDED", "FAILED"},
            )

            after_run = read_log(log_path)
            run_text = after_run[len(before_run):]

            run_reqids = extract_reqids(run_text)
            run_reqid = run_reqids[0] if run_reqids else None

            check(
                bool(run_reqid),
                "La solicitud run registra un ReqID al ser recibida.",
            )

            correlated_lines = [
                line
                for line in run_text.splitlines()
                if run_reqid and f"[ReqID: {run_reqid}]" in line
            ]

            check(
                len(correlated_lines) >= 2,
                "El mismo ReqID aparece en más de un evento del ciclo de la solicitud run.",
            )

            # ----------------------------------------------------------
            section("TC-120 - BITACORA PERSISTE Y DAEMON SIGUE OPERATIVO")
            # ----------------------------------------------------------

            final_response = send_request(
                socket_path,
                {
                    "action": "health",
                },
            )

            final_log = read_log(log_path)

            check(
                len(final_log) >= len(initial_log),
                "La bitácora conserva los eventos previamente registrados.",
            )

            check(
                daemon.poll() is None,
                "El daemon permanece activo después de generar eventos de bitácora.",
            )

            check(
                final_response.get("status") == "ok",
                "El daemon continúa respondiendo después de múltiples eventos de logging.",
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
