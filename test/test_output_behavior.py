#!/usr/bin/env python3
"""Pruebas QA para RF-11: stdout y stderr por separado."""

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
    match = re.search(
        r"ID:\s*([0-9a-fA-F-]{36})",
        stdout,
    )
    if not match:
        match = re.search(
            r"ID:\s*([0-9a-fA-F-]+)",
            stdout,
        )

    if not match:
        raise RuntimeError(
            f"No se pudo extraer el ID del trabajo desde: {stdout!r}"
        )

    return match.group(1)


def wait_terminal(job_id, env, timeout=10):
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        result = run(
            ["jobsy", "status", job_id],
            env=env,
        )

        if result.returncode == 0:
            if (
                "Estado: SUCCEEDED" in result.stdout
                or "Estado: FAILED" in result.stdout
                or "Estado: CANCELED" in result.stdout
            ):
                return result

        time.sleep(0.1)

    raise RuntimeError(
        f"El trabajo {job_id} no alcanzó un estado terminal."
    )


def main():
    with tempfile.TemporaryDirectory(prefix="jobsy-qa-output-") as temp_dir:
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
            section("TC-071 - SEPARAR STDOUT Y STDERR")

            created = run(
                [
                    "execute",
                    "sh",
                    "-c",
                    "echo SALIDA_STDOUT; echo SALIDA_STDERR >&2",
                ],
                env=env,
            )

            print("Exit code execute:", created.returncode)
            print("STDOUT execute:", repr(created.stdout))
            print("STDERR execute:", repr(created.stderr))

            check(
                created.returncode == 0,
                "El trabajo con stdout y stderr es aceptado por el daemon.",
                "El trabajo con stdout y stderr no pudo enviarse.",
            )

            job_id = extract_job_id(created.stdout)
            status = wait_terminal(job_id, env)

            print("Job ID:", job_id)
            print(status.stdout.rstrip())

            output = run(
                ["jobsy", "output", job_id],
                env=env,
            )

            print("STDOUT output:", repr(output.stdout))
            print("STDERR output:", repr(output.stderr))

            check(
                output.stdout == "SALIDA_STDOUT\n",
                "stdout contiene únicamente la salida estándar del trabajo.",
                "stdout no contiene exactamente la salida esperada.",
            )

            check(
                output.stderr == "SALIDA_STDERR\n",
                "stderr contiene únicamente la salida de error del trabajo.",
                "stderr no contiene exactamente la salida esperada.",
            )

            # ---------------------------------------------------------
            section("TC-072 - RECIBIR STDOUT MAYOR A 4096 BYTES")

            created = run(
                [
                    "execute",
                    "python3",
                    "-c",
                    'print("A"*10000)',
                ],
                env=env,
            )

            job_id = extract_job_id(created.stdout)
            wait_terminal(job_id, env)

            output = run(
                ["jobsy", "output", job_id],
                env=env,
            )

            print("Job ID:", job_id)
            print("Longitud stdout:", len(output.stdout))
            print("Longitud stderr:", len(output.stderr))

            check(
                len(output.stdout) == 10001,
                "stdout mayor a 4096 bytes se recibe completo.",
                "stdout grande llegó truncado o con longitud incorrecta.",
            )

            check(
                output.stdout == ("A" * 10000 + "\n"),
                "El contenido completo de stdout conserva integridad.",
                "El contenido de stdout grande fue alterado.",
            )

            # ---------------------------------------------------------
            section("TC-073 - RECIBIR STDERR MAYOR A 4096 BYTES")

            created = run(
                [
                    "execute",
                    "python3",
                    "-c",
                    'import sys; sys.stderr.write("E"*10000 + "\\n")',
                ],
                env=env,
            )

            job_id = extract_job_id(created.stdout)
            wait_terminal(job_id, env)

            output = run(
                ["jobsy", "output", job_id],
                env=env,
            )

            print("Job ID:", job_id)
            print("Longitud stdout:", len(output.stdout))
            print("Longitud stderr:", len(output.stderr))

            check(
                len(output.stderr) == 10001,
                "stderr mayor a 4096 bytes se recibe completo.",
                "stderr grande llegó truncado o con longitud incorrecta.",
            )

            check(
                output.stderr == ("E" * 10000 + "\n"),
                "El contenido completo de stderr conserva integridad.",
                "El contenido de stderr grande fue alterado.",
            )

            # ---------------------------------------------------------
            section("TC-074 - MANTENER VACIO EL STREAM NO UTILIZADO")

            check(
                output.stdout == "",
                "stdout permanece vacío cuando el trabajo solo escribe en stderr.",
                "stdout contiene datos inesperados.",
            )

            # ---------------------------------------------------------
            section("TC-075 - OUTPUT TERMINA CON CODIGO 0")

            check(
                output.returncode == 0,
                "El comando jobsy output termina con código 0.",
                f"jobsy output terminó con código {output.returncode}.",
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
