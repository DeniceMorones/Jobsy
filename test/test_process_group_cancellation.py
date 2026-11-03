#!/usr/bin/env python3
"""Pruebas QA para RNF-30: grupos de procesos y cancelación completa."""

from pathlib import Path
import os
import re
import subprocess
import tempfile
import time


FAILURES = 0


def section(title):
    print()
    print("=" * 40)
    print(title)
    print("=" * 40)


def check(condition, success, failure):
    global FAILURES

    if condition:
        print(f"PASS: {success}")
        return

    FAILURES += 1
    print(f"FAIL: {failure}")


def run(command, *, env=None, timeout=15):
    return subprocess.run(
        command,
        text=True,
        capture_output=True,
        env=env,
        timeout=timeout,
    )


def extract_job_id(stdout):
    match = re.search(r"ID:\s*([0-9a-fA-F-]{36})", stdout)

    if not match:
        raise RuntimeError(
            f"No se pudo extraer el ID del trabajo desde: {stdout!r}"
        )

    return match.group(1)


def wait_running(job_id, env, timeout=5):
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        result = run(["jobsy", "status", job_id], env=env)

        if result.returncode == 0 and "Estado: RUNNING" in result.stdout:
            return result

        time.sleep(0.05)

    raise RuntimeError(
        f"El trabajo {job_id} no alcanzó el estado RUNNING."
    )


def wait_terminal(job_id, env, timeout=5):
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        result = run(["jobsy", "status", job_id], env=env)

        if result.returncode == 0:
            if (
                "Estado: CANCELED" in result.stdout
                or "Estado: SUCCEEDED" in result.stdout
                or "Estado: FAILED" in result.stdout
            ):
                if "Fin: -" not in result.stdout:
                    return result

        time.sleep(0.05)

    raise RuntimeError(
        f"El trabajo {job_id} no alcanzó un estado terminal confirmado."
    )


def find_job_processes():
    result = subprocess.run(
        [
            "ps",
            "-eo",
            "pid=,ppid=,pgid=,sid=,stat=,cmd=",
        ],
        text=True,
        capture_output=True,
        check=True,
    )

    parent = None
    child = None

    for line in result.stdout.splitlines():
        if "sh -c sleep 600 & wait" in line:
            fields = line.split(None, 5)

            if len(fields) == 6:
                parent = {
                    "pid": int(fields[0]),
                    "ppid": int(fields[1]),
                    "pgid": int(fields[2]),
                    "sid": int(fields[3]),
                    "stat": fields[4],
                    "cmd": fields[5],
                }

    if parent is None:
        return None, None

    for line in result.stdout.splitlines():
        fields = line.split(None, 5)

        if len(fields) != 6:
            continue

        pid = int(fields[0])
        ppid = int(fields[1])
        pgid = int(fields[2])

        if (
            ppid == parent["pid"]
            and pgid == parent["pgid"]
            and "sleep 600" in fields[5]
        ):
            child = {
                "pid": pid,
                "ppid": ppid,
                "pgid": pgid,
                "sid": int(fields[3]),
                "stat": fields[4],
                "cmd": fields[5],
            }
            break

    return parent, child


def pid_exists(pid):
    result = subprocess.run(
        ["ps", "-p", str(pid), "-o", "pid="],
        text=True,
        capture_output=True,
    )

    return bool(result.stdout.strip())


def group_members(pgid):
    result = subprocess.run(
        ["ps", "-eo", "pid=,ppid=,pgid=,sid=,stat=,cmd="],
        text=True,
        capture_output=True,
        check=True,
    )

    members = []

    for line in result.stdout.splitlines():
        fields = line.split(None, 5)

        if len(fields) != 6:
            continue

        if int(fields[2]) == pgid:
            members.append(line.strip())

    return members


def main():
    with tempfile.TemporaryDirectory(prefix="jobsy-qa-process-group-") as temp_dir:
        root = Path(temp_dir)
        socket_path = root / "jobsy.sock"
        data_dir = root / "data"

        env = os.environ.copy()
        env["JOBSY_SOCKET_PATH"] = str(socket_path)

        daemon = subprocess.Popen(
            [
                "jobsy-daemon",
                "--data-dir",
                str(data_dir),
                "--socket-path",
                str(socket_path),
                "--cancel-grace",
                "0.5",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            deadline = time.monotonic() + 5

            while time.monotonic() < deadline:
                if socket_path.exists():
                    break

                if daemon.poll() is not None:
                    stdout, stderr = daemon.communicate()
                    raise RuntimeError(
                        "El daemon terminó antes de crear el socket.\n"
                        f"STDOUT: {stdout}\n"
                        f"STDERR: {stderr}"
                    )

                time.sleep(0.05)

            if not socket_path.exists():
                raise RuntimeError("El daemon no creó el socket UNIX.")

            # ---------------------------------------------------------
            section("TC-076 - CREAR GRUPO DE PROCESOS INDEPENDIENTE")

            created = run(
                [
                    "execute",
                    "sh",
                    "-c",
                    "sleep 600 & wait",
                ],
                env=env,
            )

            print("Exit code execute:", created.returncode)
            print("STDOUT execute:", repr(created.stdout))
            print("STDERR execute:", repr(created.stderr))

            check(
                created.returncode == 0,
                "El trabajo de prueba es aceptado por el daemon.",
                "El trabajo de prueba no pudo enviarse.",
            )

            job_id = extract_job_id(created.stdout)
            status = wait_running(job_id, env)

            print("Job ID:", job_id)
            print(status.stdout.rstrip())

            deadline = time.monotonic() + 3
            parent = None
            child = None

            while time.monotonic() < deadline:
                parent, child = find_job_processes()

                if parent is not None and child is not None:
                    break

                time.sleep(0.05)

            print("Proceso padre:", parent)
            print("Proceso hijo:", child)

            check(
                parent is not None,
                "Se localiza el proceso principal del trabajo.",
                "No se encontró el proceso principal del trabajo.",
            )

            check(
                parent is not None
                and parent["pid"] == parent["pgid"]
                and parent["pid"] == parent["sid"],
                "El proceso principal lidera su propio grupo y sesión.",
                "El proceso principal no lidera un grupo/sesión independiente.",
            )

            # ---------------------------------------------------------
            section("TC-077 - HIJO PERTENECE AL MISMO GRUPO")

            check(
                child is not None,
                "Se localiza el proceso hijo del trabajo.",
                "No se encontró el proceso hijo.",
            )

            check(
                parent is not None
                and child is not None
                and child["ppid"] == parent["pid"]
                and child["pgid"] == parent["pgid"]
                and child["sid"] == parent["sid"],
                "El proceso hijo pertenece al mismo grupo y sesión del trabajo.",
                "El proceso hijo no pertenece al grupo esperado.",
            )

            if parent is None or child is None:
                raise RuntimeError(
                    "No es posible continuar sin PID padre e hijo."
                )

            parent_pid = parent["pid"]
            child_pid = child["pid"]
            pgid = parent["pgid"]

            # ---------------------------------------------------------
            section("TC-078 - CANCELAR TODO EL GRUPO DE PROCESOS")

            canceled = run(
                ["cancel", job_id],
                env=env,
            )

            print("Exit code cancel:", canceled.returncode)
            print("STDOUT cancel:", repr(canceled.stdout))
            print("STDERR cancel:", repr(canceled.stderr))

            check(
                canceled.returncode == 0,
                "La cancelación del trabajo termina con código 0.",
                "La cancelación del trabajo devolvió un error.",
            )

            status = wait_terminal(job_id, env)

            print(status.stdout.rstrip())

            deadline = time.monotonic() + 3

            while time.monotonic() < deadline:
                if (
                    not pid_exists(parent_pid)
                    and not pid_exists(child_pid)
                    and not group_members(pgid)
                ):
                    break

                time.sleep(0.05)

            parent_alive = pid_exists(parent_pid)
            child_alive = pid_exists(child_pid)
            members = group_members(pgid)

            print("PID padre activo:", parent_alive)
            print("PID hijo activo:", child_alive)
            print("Miembros restantes del PGID:", members)

            check(
                not parent_alive,
                "El proceso padre termina después de cancelar el trabajo.",
                "El proceso padre continúa activo después de la cancelación.",
            )

            check(
                not child_alive,
                "El proceso hijo termina después de cancelar el trabajo.",
                "El proceso hijo continúa activo después de la cancelación.",
            )

            check(
                len(members) == 0,
                "No quedan procesos pertenecientes al grupo del trabajo.",
                "Quedaron procesos activos en el grupo del trabajo.",
            )

            check(
                "Estado: CANCELED" in status.stdout,
                "El trabajo conserva el estado CANCELED.",
                "El trabajo no quedó en estado CANCELED.",
            )

            check(
                "Fin: -" not in status.stdout,
                "El trabajo cancelado registra finished_at.",
                "El trabajo cancelado no registra finished_at.",
            )

            # ---------------------------------------------------------
            section("TC-079 - DAEMON SIGUE OPERATIVO")

            listed = run(
                ["jobsy", "list"],
                env=env,
            )

            print("Exit code list:", listed.returncode)
            print("Daemon activo:", daemon.poll() is None)

            check(
                listed.returncode == 0,
                "El daemon continúa respondiendo después de cancelar el grupo.",
                "El daemon dejó de responder después de cancelar el grupo.",
            )

            check(
                daemon.poll() is None,
                "El proceso del daemon permanece activo.",
                "El daemon terminó inesperadamente.",
            )

        finally:
            if daemon.poll() is None:
                daemon.terminate()

                try:
                    daemon.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    daemon.kill()
                    daemon.wait(timeout=5)

    print()
    print("=" * 40)

    if FAILURES == 0:
        print("RESULTADO GENERAL: PASS")
        print("Todas las comprobaciones fueron exitosas.")
        return 0

    print("RESULTADO GENERAL: FAIL")
    print(f"Comprobaciones fallidas: {FAILURES}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
