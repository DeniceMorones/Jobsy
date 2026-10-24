#!/usr/bin/env python3
"""Pruebas QA para RF-30: plazo configurable SIGTERM -> SIGKILL."""

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


def parse_config(value):
    return subprocess.run(
        [
            "python",
            "-c",
            (
                "from src.daemon.config import parse_config; "
                f"c=parse_config(['--cancel-grace','{value}']); "
                "print(c.cancel_grace_seconds)"
            ),
        ],
        text=True,
        capture_output=True,
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
        f"El trabajo {job_id} no alcanzó RUNNING."
    )


def wait_finished(job_id, env, timeout=5):
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        result = run(["jobsy", "status", job_id], env=env)

        if (
            result.returncode == 0
            and "Estado: CANCELED" in result.stdout
            and "Fin: -" not in result.stdout
        ):
            return result

        time.sleep(0.05)

    raise RuntimeError(
        f"El trabajo {job_id} no confirmó la cancelación."
    )


def find_group_for_command(fragment):
    result = subprocess.run(
        ["ps", "-eo", "pid=,ppid=,pgid=,sid=,stat=,cmd="],
        text=True,
        capture_output=True,
        check=True,
    )

    for line in result.stdout.splitlines():
        if fragment not in line:
            continue

        fields = line.split(None, 5)

        if len(fields) != 6:
            continue

        return {
            "pid": int(fields[0]),
            "ppid": int(fields[1]),
            "pgid": int(fields[2]),
            "sid": int(fields[3]),
            "stat": fields[4],
            "cmd": fields[5],
        }

    return None


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
    # ---------------------------------------------------------
    section("TC-082 - ACEPTAR CANCEL-GRACE VALIDO")

    result = parse_config("2")

    print("Exit code:", result.returncode)
    print("STDOUT:", repr(result.stdout))
    print("STDERR:", repr(result.stderr))

    check(
        result.returncode == 0 and result.stdout.strip() == "2.0",
        "--cancel-grace 2 es aceptado correctamente.",
        "--cancel-grace 2 no fue aceptado como valor válido.",
    )

    # ---------------------------------------------------------
    section("TC-083 - ACEPTAR CANCEL-GRACE FRACCIONARIO")

    result = parse_config("0.5")

    print("Exit code:", result.returncode)
    print("STDOUT:", repr(result.stdout))
    print("STDERR:", repr(result.stderr))

    check(
        result.returncode == 0 and result.stdout.strip() == "0.5",
        "--cancel-grace 0.5 es aceptado correctamente.",
        "--cancel-grace 0.5 no fue aceptado.",
    )

    # ---------------------------------------------------------
    section("TC-084 - RECHAZAR CANCEL-GRACE IGUAL A CERO")

    result = parse_config("0")

    print("Exit code:", result.returncode)
    print("STDOUT:", repr(result.stdout))
    print("STDERR:", repr(result.stderr))

    check(
        result.returncode != 0,
        "--cancel-grace 0 es rechazado.",
        "--cancel-grace 0 fue aceptado aunque debe ser mayor que 0.",
    )

    # ---------------------------------------------------------
    section("TC-085 - RECHAZAR CANCEL-GRACE NEGATIVO")

    result = parse_config("-1")

    print("Exit code:", result.returncode)
    print("STDOUT:", repr(result.stdout))
    print("STDERR:", repr(result.stderr))

    check(
        result.returncode != 0,
        "--cancel-grace negativo es rechazado.",
        "--cancel-grace -1 fue aceptado aunque es inválido.",
    )

    # ---------------------------------------------------------
    section("TC-086 - RECHAZAR CANCEL-GRACE MAYOR A 60")

    result = parse_config("61")

    print("Exit code:", result.returncode)
    print("STDOUT:", repr(result.stdout))
    print("STDERR:", repr(result.stderr))

    check(
        result.returncode != 0,
        "--cancel-grace mayor a 60 es rechazado.",
        "--cancel-grace 61 fue aceptado aunque supera el límite permitido.",
    )

    # ---------------------------------------------------------
    section("TC-087 - VALIDAR TIPO Y ESCALAMIENTO SIGTERM A SIGKILL")

    invalid_text = subprocess.run(
        ["jobsy-daemon", "--cancel-grace", "abc"],
        text=True,
        capture_output=True,
    )

    print("Exit code texto inválido:", invalid_text.returncode)
    print("STDOUT:", repr(invalid_text.stdout))
    print("STDERR:", repr(invalid_text.stderr))

    check(
        invalid_text.returncode == 2,
        "Un valor no numérico es rechazado con código 2.",
        "Un valor no numérico no produjo el código esperado.",
    )

    with tempfile.TemporaryDirectory(prefix="jobsy-qa-cancel-grace-") as temp_dir:
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

            created = run(
                [
                    "execute",
                    "sh",
                    "-c",
                    'trap "" TERM; while true; do sleep 1; done',
                ],
                env=env,
            )

            print("Exit code execute:", created.returncode)
            print("STDOUT execute:", repr(created.stdout))
            print("STDERR execute:", repr(created.stderr))

            job_id = extract_job_id(created.stdout)
            wait_running(job_id, env)

            deadline = time.monotonic() + 3
            process = None

            while time.monotonic() < deadline:
                process = find_group_for_command('trap "" TERM')

                if process is not None:
                    break

                time.sleep(0.05)

            print("Proceso principal:", process)

            check(
                process is not None,
                "Se localiza el proceso que ignora SIGTERM.",
                "No se localizó el proceso de prueba.",
            )

            if process is None:
                raise RuntimeError(
                    "No se puede continuar sin identificar el proceso."
                )

            pgid = process["pgid"]

            started = time.monotonic()

            canceled = run(
                ["cancel", job_id],
                env=env,
            )

            status = wait_finished(job_id, env)

            elapsed = time.monotonic() - started

            print("Exit code cancel:", canceled.returncode)
            print("Tiempo hasta estado terminal:", f"{elapsed:.3f} s")
            print(status.stdout.rstrip())

            deadline = time.monotonic() + 3

            while time.monotonic() < deadline:
                if not group_members(pgid):
                    break

                time.sleep(0.05)

            members = group_members(pgid)

            print("Miembros restantes del grupo:", members)

            check(
                canceled.returncode == 0,
                "La cancelación del trabajo termina con código 0.",
                "La cancelación devolvió un error.",
            )

            check(
                "Código de salida: -9" in status.stdout,
                "El proceso que ignora SIGTERM termina mediante SIGKILL.",
                "El proceso no terminó con SIGKILL como se esperaba.",
            )

            check(
                len(members) == 0,
                "El grupo de procesos queda completamente eliminado.",
                "Quedaron procesos activos después del escalamiento.",
            )

            check(
                elapsed >= 0.4,
                "Se respeta aproximadamente el plazo configurado antes de SIGKILL.",
                "El escalamiento ocurrió demasiado pronto para el plazo configurado.",
            )

            check(
                daemon.poll() is None,
                "El daemon permanece operativo después del escalamiento.",
                "El daemon terminó durante la cancelación.",
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
