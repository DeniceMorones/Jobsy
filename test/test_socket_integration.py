import os
import sys
import time
import socket
import tempfile
import subprocess
from pathlib import Path


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

PYTHON_BIN = sys.executable


def check(condition, description):
    if condition:
        print(f"PASS: {description}")
        return 0

    print(f"FAIL: {description}")
    return 1


def make_env(extra=None):
    env = os.environ.copy()
    env["PYTHONPATH"] = PROJECT_ROOT

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


def run_cli(args, env=None):
    process = subprocess.run(
        [
            PYTHON_BIN,
            "-m",
            "src.client.cli",
            *args,
        ],
        cwd=PROJECT_ROOT,
        env=env or make_env(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=10,
    )

    return (
        process.returncode,
        process.stdout.strip(),
        process.stderr.strip(),
    )


def main():
    failures = 0

    # ---------------------------------------------------------
    # TC-055 / TC-056
    # Socket personalizado + CLI por JOBSY_SOCKET_PATH
    # ---------------------------------------------------------

    print("========================================")
    print("TC-055 / TC-056 - SOCKET PERSONALIZADO")
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
                PYTHON_BIN,
                "-m",
                "src.daemon.server",
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
            socket_created = wait_for_socket(custom_socket)

            failures += check(
                socket_created,
                "El daemon crea el socket personalizado."
            )

            cli_env = make_env({
                "JOBSY_SOCKET_PATH": custom_socket
            })

            code, stdout, stderr = run_cli(
                ["list"],
                env=cli_env,
            )

            print("Exit code:", code)
            print("STDOUT:", repr(stdout))
            print("STDERR:", repr(stderr))

            failures += check(
                code == 0,
                "La CLI puede conectarse usando JOBSY_SOCKET_PATH."
            )

            failures += check(
                "error" not in stdout.lower(),
                "La operacion list no devuelve error."
            )

        finally:
            stop_process(daemon)

        failures += check(
            not os.path.exists(custom_socket),
            "El socket personalizado se elimina al detener el daemon."
        )

    # ---------------------------------------------------------
    # TC-061
    # No sobrescribir una ruta existente
    # ---------------------------------------------------------

    print("\n========================================")
    print("TC-061 - NO SOBRESCRIBIR RUTA EXISTENTE")
    print("========================================")

    with tempfile.TemporaryDirectory() as temp_dir:

        occupied_path = os.path.join(
            temp_dir,
            "control.sock"
        )

        Path(occupied_path).write_text(
            "archivo existente",
            encoding="utf-8"
        )

        data_dir = os.path.join(
            temp_dir,
            "data"
        )

        os.mkdir(data_dir)

        daemon = subprocess.run(
            [
                PYTHON_BIN,
                "-m",
                "src.daemon.server",
                "--socket-path",
                occupied_path,
                "--data-dir",
                data_dir,
            ],
            cwd=PROJECT_ROOT,
            env=make_env(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
        )

        print("Exit code:", daemon.returncode)
        print("STDOUT:", repr(daemon.stdout.strip()))
        print("STDERR:", repr(daemon.stderr.strip()))

        failures += check(
            daemon.returncode != 0,
            "El daemon no inicia si la ruta ya existe."
        )

        failures += check(
            os.path.exists(occupied_path),
            "La ruta existente no es eliminada."
        )

        content = Path(occupied_path).read_text(
            encoding="utf-8"
        )

        failures += check(
            content == "archivo existente",
            "El contenido existente permanece intacto."
        )

    # ---------------------------------------------------------
    # TC-062
    # Sin variable -> vuelve a /tmp/jobsy.sock
    # ---------------------------------------------------------

    print("\n========================================")
    print("TC-062 - FALLBACK AL SOCKET PREDETERMINADO")
    print("========================================")

    env = make_env()

    env.pop(
        "JOBSY_SOCKET_PATH",
        None
    )

    process = subprocess.run(
        [
            PYTHON_BIN,
            "-c",
            (
                "from src.protocol.endpoint "
                "import client_socket_path; "
                "print(client_socket_path())"
            ),
        ],
        cwd=PROJECT_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    stdout = process.stdout.strip()
    stderr = process.stderr.strip()

    print("Exit code:", process.returncode)
    print("STDOUT:", repr(stdout))
    print("STDERR:", repr(stderr))

    failures += check(
        process.returncode == 0,
        "La resolucion del socket funciona sin variable de entorno."
    )

    failures += check(
        stdout == "/tmp/jobsy.sock",
        "Sin JOBSY_SOCKET_PATH se usa /tmp/jobsy.sock."
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
