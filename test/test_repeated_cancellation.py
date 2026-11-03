#!/usr/bin/env python3
"""Pruebas QA para RF-26: cancelación repetida."""

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


def wait_finished_cancel(job_id, env, timeout=5):
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
        f"El trabajo {job_id} no confirmó su cancelación."
    )


def main():
    with tempfile.TemporaryDirectory(prefix="jobsy-qa-repeat-cancel-") as temp_dir:
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
            section("TC-080 - PRIMERA CANCELACION")

            created = run(
                ["execute", "sleep", "600"],
                env=env,
            )

            print("Exit code execute:", created.returncode)
            print("STDOUT execute:", repr(created.stdout))
            print("STDERR execute:", repr(created.stderr))

            check(
                created.returncode == 0,
                "El trabajo de larga duración es aceptado por el daemon.",
                "No se pudo crear el trabajo de larga duración.",
            )

            job_id = extract_job_id(created.stdout)
            running = wait_running(job_id, env)

            print("Job ID:", job_id)
            print(running.stdout.rstrip())

            first_cancel = run(
                ["cancel", job_id],
                env=env,
            )

            print("Exit code primera cancelación:", first_cancel.returncode)
            print("STDOUT primera cancelación:", repr(first_cancel.stdout))
            print("STDERR primera cancelación:", repr(first_cancel.stderr))

            check(
                first_cancel.returncode == 0,
                "La primera cancelación termina con código 0.",
                "La primera cancelación devolvió un error.",
            )

            status = wait_finished_cancel(job_id, env)

            print(status.stdout.rstrip())

            check(
                "Estado: CANCELED" in status.stdout,
                "El trabajo queda en estado CANCELED.",
                "El trabajo no quedó en estado CANCELED.",
            )

            check(
                "Fin: -" not in status.stdout,
                "El trabajo cancelado registra finished_at.",
                "El trabajo cancelado no registra finished_at.",
            )

            # ---------------------------------------------------------
            section("TC-081 - SEGUNDA CANCELACION")

            second_cancel = run(
                ["cancel", job_id],
                env=env,
            )

            print("Exit code segunda cancelación:", second_cancel.returncode)
            print("STDOUT segunda cancelación:", repr(second_cancel.stdout))
            print("STDERR segunda cancelación:", repr(second_cancel.stderr))

            expected_message = (
                "La cancelación de este trabajo ya fue solicitada "
                "(estado CANCELED)."
            )

            check(
                second_cancel.returncode == 1,
                "La segunda cancelación termina con código 1.",
                f"La segunda cancelación terminó con código {second_cancel.returncode}.",
            )

            check(
                expected_message in second_cancel.stderr,
                "La segunda cancelación informa claramente que ya fue solicitada.",
                "El mensaje de la segunda cancelación no coincide con el esperado.",
            )

            final_status = run(
                ["jobsy", "status", job_id],
                env=env,
            )

            check(
                "Estado: CANCELED" in final_status.stdout,
                "El estado permanece CANCELED después del segundo intento.",
                "El estado cambió después de la segunda cancelación.",
            )

            listed = run(
                ["jobsy", "list"],
                env=env,
            )

            check(
                listed.returncode == 0 and daemon.poll() is None,
                "El daemon continúa operativo después de la cancelación repetida.",
                "El daemon dejó de responder después de la cancelación repetida.",
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
