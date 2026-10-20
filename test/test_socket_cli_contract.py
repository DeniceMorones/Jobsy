import os
import re
import sys
import time
import tempfile
import subprocess
from pathlib import Path


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

VENV_BIN = os.path.join(PROJECT_ROOT, ".venv", "bin")

JOBSY = os.path.join(VENV_BIN, "jobsy")
DAEMON = os.path.join(VENV_BIN, "jobsy-daemon")
EXECUTE = os.path.join(VENV_BIN, "execute")
LIST = os.path.join(VENV_BIN, "list")
STATUS = os.path.join(VENV_BIN, "status")
CANCEL = os.path.join(VENV_BIN, "cancel")


def check(condition, description):
    if condition:
        print(f"PASS: {description}")
        return 0

    print(f"FAIL: {description}")
    return 1


def make_env(extra=None):
    env = os.environ.copy()

    if extra:
        env.update(extra)

    return env


def wait_for_socket(path, timeout=5):
    deadline = time.time() + timeout

    while time.time() < deadline:
        if os.path.exists(path):
            return True
        time.sleep(0.05)

    return False


def stop_process(process):
    if process.poll() is None:
        process.terminate()

        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def run(command, env=None, timeout=10):
    process = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        env=env or make_env(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
    )

    return (
        process.returncode,
        process.stdout.strip(),
        process.stderr.strip(),
    )


def show_result(code, stdout, stderr):
    print("Exit code:", code)
    print("STDOUT:", repr(stdout))
    print("STDERR:", repr(stderr))


def extract_uuid(text):
    match = re.search(
        r"\b[0-9a-fA-F]{8}-"
        r"[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{12}\b",
        text,
    )

    return match.group(0) if match else None


def main():
    failures = 0

    # =========================================================
    # TC-063
    # El daemon no utiliza JOBSY_SOCKET_PATH
    # =========================================================

    print("========================================")
    print("TC-063 - DAEMON IGNORA JOBSY_SOCKET_PATH")
    print("========================================")

    with tempfile.TemporaryDirectory() as temp_dir:
        actual_socket = os.path.join(
            temp_dir,
            "daemon.sock"
        )

        env_socket = os.path.join(
            temp_dir,
            "variable.sock"
        )

        data_dir = os.path.join(
            temp_dir,
            "data"
        )

        os.mkdir(data_dir)

        daemon_env = make_env({
            "JOBSY_SOCKET_PATH": env_socket
        })

        daemon = subprocess.Popen(
            [
                DAEMON,
                "--socket-path",
                actual_socket,
                "--data-dir",
                data_dir,
            ],
            cwd=PROJECT_ROOT,
            env=daemon_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            failures += check(
                wait_for_socket(actual_socket),
                "El daemon utiliza --socket-path."
            )

            failures += check(
                not os.path.exists(env_socket),
                "JOBSY_SOCKET_PATH no crea ni sustituye el socket del daemon."
            )

        finally:
            stop_process(daemon)

    # =========================================================
    # TC-064
    # Variable vacia
    # =========================================================

    print("\n========================================")
    print("TC-064 - JOBSY_SOCKET_PATH VACIO")
    print("========================================")

    env = make_env({
        "JOBSY_SOCKET_PATH": ""
    })

    code, stdout, stderr = run(
        [JOBSY, "list"],
        env=env,
    )

    show_result(code, stdout, stderr)

    failures += check(
        code == 1,
        "El cliente devuelve codigo 1 con JOBSY_SOCKET_PATH vacio."
    )

    combined = (stdout + "\n" + stderr).lower()

    failures += check(
        "ruta" in combined or "socket" in combined,
        "El cliente informa un error relacionado con el endpoint."
    )

    # =========================================================
    # TC-065
    # Ruta invalida del daemon -> codigo 2
    # =========================================================

    print("\n========================================")
    print("TC-065 - SOCKET INVALIDO DEL DAEMON")
    print("========================================")

    with tempfile.TemporaryDirectory() as temp_dir:
        data_dir = os.path.join(
            temp_dir,
            "data"
        )

        os.mkdir(data_dir)

        code, stdout, stderr = run(
            [
                DAEMON,
                "--socket-path",
                "ruta-relativa.sock",
                "--data-dir",
                data_dir,
            ]
        )

        show_result(code, stdout, stderr)

        failures += check(
            code == 2,
            "Una configuracion invalida del daemon devuelve codigo 2."
        )

    # =========================================================
    # TC-066
    # Endpoint valido pero sin daemon -> codigo 1
    # =========================================================

    print("\n========================================")
    print("TC-066 - ENDPOINT SIN SERVICIO")
    print("========================================")

    with tempfile.TemporaryDirectory() as temp_dir:
        missing_socket = os.path.join(
            temp_dir,
            "sin-daemon.sock"
        )

        env = make_env({
            "JOBSY_SOCKET_PATH": missing_socket
        })

        code, stdout, stderr = run(
            [JOBSY, "list"],
            env=env,
        )

        show_result(code, stdout, stderr)

        failures += check(
            code == 1,
            "El cliente devuelve codigo 1 cuando no existe el servicio."
        )

    # =========================================================
    # TC-067
    # Expansion de ~
    # =========================================================

    print("\n========================================")
    print("TC-067 - EXPANSION DE ~")
    print("========================================")

    with tempfile.TemporaryDirectory() as temp_dir:
        fake_home = os.path.join(
            temp_dir,
            "home"
        )

        os.mkdir(fake_home)

        data_dir = os.path.join(
            temp_dir,
            "data"
        )

        os.mkdir(data_dir)

        expected_socket = os.path.join(
            fake_home,
            "control.sock"
        )

        env = make_env({
            "HOME": fake_home
        })

        daemon = subprocess.Popen(
            [
                DAEMON,
                "--socket-path",
                "~/control.sock",
                "--data-dir",
                data_dir,
            ],
            cwd=PROJECT_ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            failures += check(
                wait_for_socket(expected_socket),
                "La ruta con ~ se expande al HOME del usuario."
            )

        finally:
            stop_process(daemon)

        failures += check(
            not os.path.exists(expected_socket),
            "El socket expandido se elimina al detener el daemon."
        )

    # =========================================================
    # TC-068
    # Entry point jobsy-daemon
    #
    # TC-069
    # jobsy/list/status/cancel usan JOBSY_SOCKET_PATH
    #
    # TC-070
    # execute usa JOBSY_SOCKET_PATH
    # =========================================================

    print("\n========================================")
    print("TC-068 / TC-069 / TC-070 - ENTRY POINTS")
    print("========================================")

    with tempfile.TemporaryDirectory() as temp_dir:
        custom_socket = os.path.join(
            temp_dir,
            "control.sock"
        )

        data_dir = os.path.join(
            temp_dir,
            "data"
        )

        os.mkdir(data_dir)

        daemon = subprocess.Popen(
            [
                DAEMON,
                "--socket-path",
                custom_socket,
                "--data-dir",
                data_dir,
            ],
            cwd=PROJECT_ROOT,
            env=make_env(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            socket_ready = wait_for_socket(
                custom_socket
            )

            failures += check(
                socket_ready,
                "jobsy-daemon inicia con un socket personalizado."
            )

            client_env = make_env({
                "JOBSY_SOCKET_PATH": custom_socket
            })

            # TC-070: execute
            code, stdout, stderr = run(
                [
                    EXECUTE,
                    "sleep",
                    "20",
                ],
                env=client_env,
            )

            print("\nexecute:")
            show_result(code, stdout, stderr)

            failures += check(
                code == 0,
                "execute utiliza JOBSY_SOCKET_PATH."
            )

            job_id = extract_uuid(
                stdout + "\n" + stderr
            )

            failures += check(
                job_id is not None,
                "execute devuelve un UUID de trabajo."
            )

            # jobsy list
            code, stdout, stderr = run(
                [JOBSY, "list"],
                env=client_env,
            )

            print("\njobsy list:")
            show_result(code, stdout, stderr)

            failures += check(
                code == 0,
                "jobsy list utiliza JOBSY_SOCKET_PATH."
            )

            if job_id:
                failures += check(
                    job_id in stdout,
                    "jobsy list muestra el trabajo creado."
                )

            # short list
            code, stdout, stderr = run(
                [LIST],
                env=client_env,
            )

            print("\nlist:")
            show_result(code, stdout, stderr)

            failures += check(
                code == 0,
                "El comando corto list utiliza JOBSY_SOCKET_PATH."
            )

            if job_id:
                # short status
                code, stdout, stderr = run(
                    [STATUS, job_id],
                    env=client_env,
                )

                print("\nstatus:")
                show_result(code, stdout, stderr)

                failures += check(
                    code == 0,
                    "El comando corto status utiliza JOBSY_SOCKET_PATH."
                )

                failures += check(
                    job_id in stdout,
                    "status consulta el trabajo correcto."
                )

                # short cancel
                code, stdout, stderr = run(
                    [CANCEL, job_id],
                    env=client_env,
                )

                print("\ncancel:")
                show_result(code, stdout, stderr)

                failures += check(
                    code == 0,
                    "El comando corto cancel utiliza JOBSY_SOCKET_PATH."
                )

        finally:
            stop_process(daemon)

        failures += check(
            not os.path.exists(custom_socket),
            "El socket del entry point se elimina al detener el daemon."
        )

    print("\n========================================")

    if failures == 0:
        print("RESULTADO GENERAL: PASS")
        print("Todas las comprobaciones fueron exitosas.")
        return 0

    print("RESULTADO GENERAL: FAIL")
    print(f"Comprobaciones fallidas: {failures}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
