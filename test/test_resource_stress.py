#!/usr/bin/env python3

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path


STRESS_JOBS = 120
TERMINAL_STATES = {"SUCCEEDED", "FAILED", "CANCELED"}

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

    return json.loads(b"".join(chunks).decode("utf-8"))


def wait_for_socket(socket_path, daemon, timeout=8):
    deadline = time.time() + timeout

    while time.time() < deadline:
        if daemon.poll() is not None:
            raise RuntimeError(
                f"El daemon terminó inesperadamente "
                f"con código {daemon.returncode}"
            )

        if os.path.exists(socket_path):
            return

        time.sleep(0.05)

    raise RuntimeError("El daemon no creó el socket.")


def read_rss_kb(pid):
    path = Path(f"/proc/{pid}/status")

    for line in path.read_text().splitlines():
        if line.startswith("VmRSS:"):
            return int(line.split()[1])

    raise RuntimeError("No fue posible leer VmRSS.")


def read_fd_count(pid):
    return len(list(Path(f"/proc/{pid}/fd").iterdir()))


def read_children(pid):
    path = Path(f"/proc/{pid}/task/{pid}/children")

    if not path.exists():
        return []

    content = path.read_text().strip()

    if not content:
        return []

    return [int(value) for value in content.split()]


def read_deleted_fds(pid):
    deleted = []

    for fd in Path(f"/proc/{pid}/fd").iterdir():
        try:
            target = os.readlink(fd)

            if "(deleted)" in target:
                deleted.append((fd.name, target))
        except (FileNotFoundError, PermissionError):
            pass

    return deleted


def wait_all_terminal(socket_path, job_ids, timeout=30):
    deadline = time.time() + timeout
    pending = set(job_ids)
    final_states = {}

    while time.time() < deadline and pending:
        for job_id in list(pending):
            try:
                response = send_request(
                    socket_path,
                    {
                        "action": "status",
                        "job_id": job_id,
                    },
                )

                if response.get("status") != "ok":
                    continue

                state = response.get("job", {}).get("status")

                if state in TERMINAL_STATES:
                    final_states[job_id] = state
                    pending.remove(job_id)

            except (OSError, ValueError, json.JSONDecodeError):
                pass

        if pending:
            time.sleep(0.05)

    return final_states, pending


def start_daemon(socket_path, data_dir):
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
            "8",
            "--queue-capacity",
            "150",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    wait_for_socket(socket_path, daemon)
    return daemon


def stop_daemon(daemon):
    if daemon.poll() is not None:
        return

    daemon.terminate()

    try:
        daemon.wait(timeout=10)
    except subprocess.TimeoutExpired:
        daemon.kill()
        daemon.wait(timeout=5)


def main():
    global failures

    with tempfile.TemporaryDirectory(
        prefix="jobsy-resource-stress-"
    ) as temp_dir:

        temp = Path(temp_dir)

        socket_path = str(temp / "jobsy.sock")
        data_dir = temp / "data"

        daemon = start_daemon(socket_path, data_dir)

        try:
            # Dar tiempo al daemon para estabilizar su arranque.
            time.sleep(0.3)

            baseline_rss = read_rss_kb(daemon.pid)
            baseline_fds = read_fd_count(daemon.pid)

            section("RECURSOS BASE")

            print(f"PID daemon: {daemon.pid}")
            print(f"RSS inicial: {baseline_rss} KB")
            print(f"FD iniciales: {baseline_fds}")

            # ----------------------------------------------------------
            section("TC-134 - DAEMON ACEPTA CARGA DE 120 TRABAJOS")
            # ----------------------------------------------------------

            job_ids = []
            rejected = 0

            for index in range(STRESS_JOBS):
                response = send_request(
                    socket_path,
                    {
                        "action": "run",
                        "command": [
                            sys.executable,
                            "-c",
                            (
                                "import sys; "
                                f"print('stress-{index}'); "
                                "sys.stderr.write('')"
                            ),
                        ],
                    },
                )

                if (
                    response.get("status") == "ok"
                    and response.get("job_id")
                ):
                    job_ids.append(response["job_id"])
                else:
                    rejected += 1

            print(f"Solicitudes enviadas: {STRESS_JOBS}")
            print(f"Trabajos aceptados: {len(job_ids)}")
            print(f"Trabajos rechazados: {rejected}")

            check(
                len(job_ids) == STRESS_JOBS,
                "Las 120 solicitudes de estrés son aceptadas.",
            )

            # ----------------------------------------------------------
            section("TC-135 - TODOS LOS TRABAJOS TERMINAN")
            # ----------------------------------------------------------

            final_states, pending = wait_all_terminal(
                socket_path,
                job_ids,
                timeout=30,
            )

            succeeded = sum(
                state == "SUCCEEDED"
                for state in final_states.values()
            )

            print(f"SUCCEEDED: {succeeded}")
            print(f"Pendientes al finalizar: {len(pending)}")

            check(
                len(pending) == 0,
                "No quedan trabajos RUNNING o QUEUED después de la carga.",
            )

            check(
                succeeded == STRESS_JOBS,
                "Los 120 trabajos terminan en SUCCEEDED.",
            )

            # Dar tiempo al scheduler/executor para recolectar procesos.
            time.sleep(0.7)

            # ----------------------------------------------------------
            section("TC-136 - PROCESOS HIJOS SON LIBERADOS")
            # ----------------------------------------------------------

            children = read_children(daemon.pid)

            print(f"Procesos hijos restantes: {children}")

            check(
                len(children) == 0,
                "El daemon no conserva procesos hijos después de finalizar la carga.",
            )

            # ----------------------------------------------------------
            section("TC-137 - DESCRIPTORES DE ARCHIVO SE LIBERAN")
            # ----------------------------------------------------------

            fd_after = read_fd_count(daemon.pid)

            print(f"FD iniciales: {baseline_fds}")
            print(f"FD después del estrés: {fd_after}")
            print(f"Diferencia: {fd_after - baseline_fds}")

            check(
                fd_after <= baseline_fds + 3,
                "La cantidad de descriptores vuelve a un nivel equivalente al inicial.",
            )

            deleted_fds = read_deleted_fds(daemon.pid)

            print(f"FD abiertos sobre archivos eliminados: {deleted_fds}")

            check(
                len(deleted_fds) == 0,
                "No quedan archivos eliminados retenidos mediante descriptores abiertos.",
            )

            # ----------------------------------------------------------
            section("TC-138 - MEMORIA SE ESTABILIZA DESPUES DEL ESTRES")
            # ----------------------------------------------------------

            rss_samples = []

            for _ in range(8):
                rss_samples.append(read_rss_kb(daemon.pid))
                time.sleep(0.25)

            rss_min = min(rss_samples)
            rss_max = max(rss_samples)

            print(f"RSS inicial: {baseline_rss} KB")
            print(f"Muestras RSS en reposo: {rss_samples}")
            print(
                f"Variación durante reposo: "
                f"{rss_max - rss_min} KB"
            )

            # No exigimos volver al baseline porque el historial
            # permanece cargado. Verificamos estabilidad tras la carga.
            check(
                rss_max - rss_min <= 8192,
                "La memoria RSS permanece estable una vez finalizada la carga.",
            )

            # ----------------------------------------------------------
            section("TC-139 - DAEMON SIGUE OPERATIVO TRAS EL ESTRES")
            # ----------------------------------------------------------

            health = send_request(
                socket_path,
                {
                    "action": "health",
                },
            )

            check(
                health.get("status") == "ok",
                "El daemon responde correctamente a health después del estrés.",
            )

            check(
                daemon.poll() is None,
                "El proceso del daemon continúa activo.",
            )

            # ----------------------------------------------------------
            section("TC-140 - SOCKET SE LIBERA AL APAGAR EL DAEMON")
            # ----------------------------------------------------------

            socket_exists_before = os.path.exists(socket_path)

            check(
                socket_exists_before,
                "El socket existe mientras el daemon está activo.",
            )

            stop_daemon(daemon)

            deadline = time.time() + 5

            while (
                time.time() < deadline
                and os.path.exists(socket_path)
            ):
                time.sleep(0.05)

            check(
                not os.path.exists(socket_path),
                "El socket UNIX se elimina al apagar el daemon.",
            )

        finally:
            if daemon.poll() is None:
                stop_daemon(daemon)

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
