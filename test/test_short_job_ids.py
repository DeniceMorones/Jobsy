#!/usr/bin/env python3
"""Pruebas QA para IDs cortos de trabajos - PR #133."""

import os
import re
import subprocess
import tempfile
import time
from pathlib import Path

from src.protocol.job_ids import resolve_job_id


TOTAL = 0
PASSED = 0
FAILED = 0

TERMINAL_STATES = {
    "SUCCEEDED",
    "FAILED",
    "CANCELED",
}


def section(title):
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def check(condition, success_message, failure_message):
    global TOTAL, PASSED, FAILED

    TOTAL += 1

    if condition:
        PASSED += 1
        print(f"[PASS] {success_message}")
        return True

    FAILED += 1
    print(f"[FAIL] {failure_message}")
    return False


def run(command, env=None, timeout=10):
    return subprocess.run(
        command,
        env=env,
        text=True,
        capture_output=True,
        timeout=timeout,
    )


def extract_short_id(output):
    """Extrae un ID hexadecimal corto de 8 caracteres."""
    match = re.search(
        r"ID:\s*([0-9a-fA-F]{8})\b",
        output,
    )

    return match.group(1) if match else None


def extract_full_id(output):
    """Extrae un UUID completo."""
    match = re.search(
        r"\b"
        r"([0-9a-fA-F]{8}-"
        r"[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{12})"
        r"\b",
        output,
    )

    return match.group(1) if match else None


def extract_state(output):
    """Obtiene el estado desde la salida de jobsy status."""
    match = re.search(
        r"Estado:\s*(QUEUED|RUNNING|SUCCEEDED|FAILED|CANCELED)",
        output,
    )

    return match.group(1) if match else None


def wait_for_state(job_id, env, expected_states, timeout=10):
    """Espera hasta que un trabajo alcance alguno de los estados indicados."""
    deadline = time.time() + timeout
    last = None

    while time.time() < deadline:
        last = run(
            ["jobsy", "status", job_id],
            env=env,
        )

        if last.returncode == 0:
            state = extract_state(last.stdout)

            if state in expected_states:
                return last

        time.sleep(0.1)

    return last


def wait_terminal(job_id, env, timeout=10):
    return wait_for_state(
        job_id,
        env,
        TERMINAL_STATES,
        timeout,
    )


def main():
    global FAILED

    section("PR #133 - IDS CORTOS DE TRABAJOS")

    with tempfile.TemporaryDirectory(
        prefix="jobsy-qa-short-id-"
    ) as temp_dir:

        temp = Path(temp_dir)

        socket_path = temp / "jobsy.sock"
        data_dir = temp / "data"

        data_dir.mkdir(parents=True, exist_ok=True)

        env = os.environ.copy()

        env["JOBSY_SOCKET_PATH"] = str(socket_path)
        env["JOBSY_DATA_DIR"] = str(data_dir)

        daemon = subprocess.Popen(
            [
                "jobsy-daemon",
                "--max-running",
                "2",
                "--queue-capacity",
                "20",
                "--data-dir",
                str(data_dir),
                "--socket-path",
                str(socket_path),
            ],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            # ---------------------------------------------------------
            # ARRANQUE DEL DAEMON
            # ---------------------------------------------------------

            deadline = time.time() + 5

            while time.time() < deadline:
                if socket_path.exists():
                    break

                if daemon.poll() is not None:
                    break

                time.sleep(0.05)

            daemon_started = (
                daemon.poll() is None
                and socket_path.exists()
            )

            check(
                daemon_started,
                "El daemon inició correctamente.",
                "El daemon no inició o el socket no fue creado.",
            )

            if not daemon_started:
                stdout, stderr = daemon.communicate(timeout=2)

                print("\nSTDOUT daemon:")
                print(stdout.rstrip())

                print("\nSTDERR daemon:")
                print(stderr.rstrip())

                raise SystemExit(1)

            # ---------------------------------------------------------
            # TC-150
            # ---------------------------------------------------------

            section(
                "TC-150 - RUN MUESTRA ID CORTO DE 8 CARACTERES"
            )

            created = run(
                [
                    "jobsy",
                    "run",
                    "--",
                    "python",
                    "-c",
                    "print('QA SHORT ID')",
                ],
                env=env,
            )

            print("Exit code:", created.returncode)
            print("STDOUT:", repr(created.stdout))
            print("STDERR:", repr(created.stderr))

            short_id = extract_short_id(
                created.stdout
            )

            check(
                created.returncode == 0
                and short_id is not None
                and len(short_id) == 8,
                "jobsy run muestra un ID corto de 8 caracteres.",
                "jobsy run no mostró correctamente el ID corto.",
            )

            if short_id is None:
                print(
                    "\n[ABORT] No se pudo obtener el ID corto "
                    "del trabajo."
                )
                print(
                    "Los casos siguientes dependen de ese ID "
                    "y no pueden ejecutarse correctamente."
                )
                raise SystemExit(1)

            print("ID corto obtenido:", short_id)

            # ---------------------------------------------------------
            # TC-151
            # ---------------------------------------------------------

            section(
                "TC-151 - LIST MUESTRA IDS CORTOS POR DEFECTO"
            )

            listed = run(
                ["jobsy", "list"],
                env=env,
            )

            print("Exit code:", listed.returncode)
            print(listed.stdout.rstrip())
            print(listed.stderr.rstrip())

            list_contains_short = (
                short_id.lower()
                in listed.stdout.lower()
            )

            list_contains_full_uuid = bool(
                re.search(
                    r"\b[0-9a-fA-F]{8}-"
                    r"[0-9a-fA-F]{4}-"
                    r"[0-9a-fA-F]{4}-"
                    r"[0-9a-fA-F]{4}-"
                    r"[0-9a-fA-F]{12}\b",
                    listed.stdout,
                )
            )

            check(
                listed.returncode == 0
                and list_contains_short
                and not list_contains_full_uuid,
                "jobsy list muestra IDs cortos por defecto.",
                "jobsy list mostró un formato de ID inesperado.",
            )

            # ---------------------------------------------------------
            # TC-152
            # ---------------------------------------------------------

            section(
                "TC-152 - LIST --FULL-ID MUESTRA UUID COMPLETO"
            )

            listed_full = run(
                [
                    "jobsy",
                    "list",
                    "--full-id",
                ],
                env=env,
            )

            print("Exit code:", listed_full.returncode)
            print(listed_full.stdout.rstrip())
            print(listed_full.stderr.rstrip())

            full_id = extract_full_id(
                listed_full.stdout
            )

            check(
                listed_full.returncode == 0
                and full_id is not None,
                "jobsy list --full-id muestra el UUID completo.",
                "jobsy list --full-id no mostró un UUID completo.",
            )

            if full_id is None:
                print(
                    "\n[ABORT] No se pudo recuperar el UUID completo."
                )
                raise SystemExit(1)

            print("UUID completo:", full_id)

            check(
                full_id.replace("-", "")
                .lower()
                .startswith(short_id.lower()),
                "El UUID completo corresponde al ID corto creado.",
                "El UUID completo no corresponde al ID corto.",
            )

            # ---------------------------------------------------------
            # TC-153
            # ---------------------------------------------------------

            section(
                "TC-153 - STATUS ACEPTA ID CORTO"
            )

            status_short = run(
                [
                    "jobsy",
                    "status",
                    short_id,
                ],
                env=env,
            )

            print("Exit code:", status_short.returncode)
            print(status_short.stdout.rstrip())
            print(status_short.stderr.rstrip())

            check(
                status_short.returncode == 0
                and f"id: {short_id.lower()}"
                in status_short.stdout.lower(),
                "status acepta correctamente el ID corto.",
                "status rechazó un ID corto válido.",
            )

            # ---------------------------------------------------------
            # TC-154
            # ---------------------------------------------------------

            section(
                "TC-154 - OUTPUT ACEPTA ID CORTO"
            )

            terminal = wait_terminal(
                short_id,
                env,
            )

            if terminal is not None:
                print(
                    "Estado terminal:",
                    extract_state(terminal.stdout),
                )

            output_short = run(
                [
                    "jobsy",
                    "output",
                    short_id,
                ],
                env=env,
            )

            print("Exit code:", output_short.returncode)
            print("STDOUT:", repr(output_short.stdout))
            print("STDERR:", repr(output_short.stderr))

            check(
                output_short.returncode == 0
                and "QA SHORT ID"
                in output_short.stdout,
                "output obtiene la salida usando el ID corto.",
                "output no resolvió correctamente el ID corto.",
            )

            # ---------------------------------------------------------
            # TC-155
            # ---------------------------------------------------------

            section(
                "TC-155 - CANCEL ACEPTA ID CORTO"
            )

            long_job = run(
                [
                    "jobsy",
                    "run",
                    "--",
                    "python",
                    "-c",
                    "import time; time.sleep(5)",
                ],
                env=env,
            )

            print("RUN:", long_job.stdout.rstrip())
            print(long_job.stderr.rstrip())

            cancel_short_id = extract_short_id(
                long_job.stdout
            )

            if cancel_short_id is None:
                check(
                    False,
                    "",
                    "No se pudo obtener el ID del trabajo "
                    "destinado a cancelación.",
                )
            else:
                running = wait_for_state(
                    cancel_short_id,
                    env,
                    {"RUNNING"},
                    timeout=5,
                )

                if running is not None:
                    print(
                        "Estado antes de cancelar:",
                        extract_state(running.stdout),
                    )

                canceled = run(
                    [
                        "jobsy",
                        "cancel",
                        cancel_short_id,
                    ],
                    env=env,
                )

                print(
                    "Exit code:",
                    canceled.returncode,
                )
                print(canceled.stdout.rstrip())
                print(canceled.stderr.rstrip())

                canceled_status = wait_for_state(
                    cancel_short_id,
                    env,
                    {"CANCELED"},
                    timeout=5,
                )

                check(
                    canceled.returncode == 0
                    and canceled_status is not None
                    and extract_state(
                        canceled_status.stdout
                    ) == "CANCELED",
                    "cancel acepta correctamente un ID corto.",
                    "cancel no pudo resolver o cancelar "
                    "el trabajo mediante ID corto.",
                )

            # ---------------------------------------------------------
            # TC-156
            # ---------------------------------------------------------

            section(
                "TC-156 - STATUS SIGUE ACEPTANDO UUID COMPLETO"
            )

            status_full = run(
                [
                    "jobsy",
                    "status",
                    full_id,
                ],
                env=env,
            )

            print("Exit code:", status_full.returncode)
            print(status_full.stdout.rstrip())
            print(status_full.stderr.rstrip())

            check(
                status_full.returncode == 0,
                "status conserva compatibilidad con UUID completo.",
                "status dejó de aceptar UUID completo.",
            )

            # ---------------------------------------------------------
            # TC-157
            # ---------------------------------------------------------

            section(
                "TC-157 - PREFIJO DE MAS DE 8 CARACTERES FUNCIONA"
            )

            prefix_12 = (
                full_id
                .replace("-", "")
                [:12]
            )

            print(
                "Prefijo utilizado:",
                prefix_12,
            )

            status_12 = run(
                [
                    "jobsy",
                    "status",
                    prefix_12,
                ],
                env=env,
            )

            print("Exit code:", status_12.returncode)
            print(status_12.stdout.rstrip())
            print(status_12.stderr.rstrip())

            check(
                status_12.returncode == 0,
                "Un prefijo hexadecimal de 12 caracteres "
                "se resuelve correctamente.",
                "El prefijo de más de 8 caracteres fue rechazado.",
            )

            # ---------------------------------------------------------
            # TC-158
            # ---------------------------------------------------------

            section(
                "TC-158 - PREFIJO EN MAYUSCULAS FUNCIONA"
            )

            upper_prefix = short_id.upper()

            print(
                "Prefijo utilizado:",
                upper_prefix,
            )

            status_upper = run(
                [
                    "jobsy",
                    "status",
                    upper_prefix,
                ],
                env=env,
            )

            print("Exit code:", status_upper.returncode)
            print(status_upper.stdout.rstrip())
            print(status_upper.stderr.rstrip())

            check(
                status_upper.returncode == 0,
                "El ID corto también se acepta en mayúsculas.",
                "El ID corto en mayúsculas fue rechazado.",
            )

            # ---------------------------------------------------------
            # TC-159
            # ---------------------------------------------------------

            section(
                "TC-159 - ID INEXISTENTE DEVUELVE ERROR"
            )

            # UUID hexadecimal válido pero extremadamente
            # improbable de existir en este entorno temporal.
            missing_id = "ffffffff"

            missing = run(
                [
                    "jobsy",
                    "status",
                    missing_id,
                ],
                env=env,
            )

            print("Exit code:", missing.returncode)
            print("STDOUT:", repr(missing.stdout))
            print("STDERR:", repr(missing.stderr))

            check(
                missing.returncode == 1
                and "No existe un trabajo"
                in missing.stderr,
                "Un ID inexistente devuelve un error controlado.",
                "El error de ID inexistente no fue el esperado.",
            )

            # ---------------------------------------------------------
            # TC-160
            # ---------------------------------------------------------

            section(
                "TC-160 - PREFIJO MENOR A 8 CARACTERES ES RECHAZADO"
            )

            too_short = run(
                [
                    "jobsy",
                    "status",
                    "1234567",
                ],
                env=env,
            )

            print("Exit code:", too_short.returncode)
            print("STDOUT:", repr(too_short.stdout))
            print("STDERR:", repr(too_short.stderr))

            check(
                too_short.returncode == 1
                and "8 a 32 caracteres"
                in too_short.stderr,
                "Un prefijo menor a 8 caracteres es rechazado.",
                "El prefijo corto inválido no fue "
                "rechazado correctamente.",
            )

            # ---------------------------------------------------------
            # TC-161
            # ---------------------------------------------------------

            section(
                "TC-161 - CARACTERES NO HEXADECIMALES SON RECHAZADOS"
            )

            invalid_chars = run(
                [
                    "jobsy",
                    "status",
                    "zzzzzzzz",
                ],
                env=env,
            )

            print("Exit code:", invalid_chars.returncode)
            print("STDOUT:", repr(invalid_chars.stdout))
            print("STDERR:", repr(invalid_chars.stderr))

            check(
                invalid_chars.returncode == 1
                and "hexadecimales"
                in invalid_chars.stderr,
                "Los IDs con caracteres no hexadecimales "
                "son rechazados.",
                "El formato hexadecimal inválido "
                "no fue detectado.",
            )

            # ---------------------------------------------------------
            # TC-162
            # ---------------------------------------------------------

            section(
                "TC-162 - PREFIJO AMBIGUO ES RECHAZADO"
            )

            known_ids = [
                "aaaaaaaa-1111-1111-1111-111111111111",
                "aaaaaaaa-2222-2222-2222-222222222222",
            ]

            ambiguous_rejected = False
            ambiguous_message = ""

            try:
                resolve_job_id(
                    "aaaaaaaa",
                    known_ids,
                )

            except ValueError as error:
                ambiguous_message = str(error)

                ambiguous_rejected = (
                    "ambiguo"
                    in ambiguous_message.lower()
                    and "uuid completo"
                    in ambiguous_message.lower()
                )

            print(
                "Mensaje:",
                ambiguous_message,
            )

            check(
                ambiguous_rejected,
                "Un prefijo ambiguo es rechazado "
                "sin seleccionar arbitrariamente un trabajo.",
                "resolve_job_id aceptó o manejó "
                "incorrectamente un prefijo ambiguo.",
            )

            # ---------------------------------------------------------
            # TC-163
            # ---------------------------------------------------------

            section(
                "TC-163 - ID CORTO FUNCIONA CON TRABAJO TERMINAL"
            )

            terminal_status = wait_terminal(
                short_id,
                env,
            )

            terminal_query = run(
                [
                    "jobsy",
                    "status",
                    short_id,
                ],
                env=env,
            )

            print("Exit code:", terminal_query.returncode)
            print(terminal_query.stdout.rstrip())
            print(terminal_query.stderr.rstrip())

            terminal_state = None

            if terminal_status is not None:
                terminal_state = extract_state(
                    terminal_status.stdout
                )

            check(
                terminal_query.returncode == 0
                and terminal_state
                in TERMINAL_STATES,
                "Un trabajo terminal sigue siendo "
                "localizable mediante ID corto.",
                "El historial terminal no pudo "
                "resolverse mediante ID corto.",
            )

            # ---------------------------------------------------------
            # TC-164
            # ---------------------------------------------------------

            section(
                "TC-164 - HEALTH MUESTRA IDS CORTOS"
            )

            health_job = run(
                [
                    "jobsy",
                    "run",
                    "--",
                    "python",
                    "-c",
                    "import time; time.sleep(5)",
                ],
                env=env,
            )

            print("RUN:", health_job.stdout.rstrip())
            print(health_job.stderr.rstrip())

            health_short_id = extract_short_id(
                health_job.stdout
            )

            if health_short_id is None:
                check(
                    False,
                    "",
                    "No se pudo crear el trabajo "
                    "para validar health.",
                )

            else:
                health_running = wait_for_state(
                    health_short_id,
                    env,
                    {"RUNNING"},
                    timeout=5,
                )

                if health_running is not None:
                    print(
                        "Estado:",
                        extract_state(
                            health_running.stdout
                        ),
                    )

                health = run(
                    ["jobsy", "health"],
                    env=env,
                )

                print("Exit code:", health.returncode)
                print(health.stdout.rstrip())
                print(health.stderr.rstrip())

                health_contains_short = (
                    health_short_id.lower()
                    in health.stdout.lower()
                )

                health_contains_full = bool(
                    re.search(
                        r"\b[0-9a-fA-F]{8}-"
                        r"[0-9a-fA-F]{4}-"
                        r"[0-9a-fA-F]{4}-"
                        r"[0-9a-fA-F]{4}-"
                        r"[0-9a-fA-F]{12}\b",
                        health.stdout,
                    )
                )

                check(
                    health.returncode == 0
                    and health_contains_short
                    and not health_contains_full,
                    "health muestra IDs cortos "
                    "en sus trabajos.",
                    "health no utilizó correctamente "
                    "el formato de ID corto.",
                )

                run(
                    [
                        "jobsy",
                        "cancel",
                        health_short_id,
                    ],
                    env=env,
                )

        finally:
            if daemon.poll() is None:
                daemon.terminate()

                try:
                    daemon.wait(
                        timeout=5
                    )

                except subprocess.TimeoutExpired:
                    daemon.kill()
                    daemon.wait(
                        timeout=5
                    )

    # -------------------------------------------------------------
    # RESULTADO FINAL
    # -------------------------------------------------------------

    section(
        "RESULTADO FINAL"
    )

    print(
        f"Checks ejecutados: {TOTAL}"
    )
    print(
        f"PASS: {PASSED}"
    )
    print(
        f"FAIL: {FAILED}"
    )

    if FAILED == 0:
        print(
            "\nRESULTADO GENERAL: PASS"
        )
        raise SystemExit(0)

    print(
        "\nRESULTADO GENERAL: FAIL"
    )
    raise SystemExit(1)


if __name__ == "__main__":
    main()
