import os
import sys
import tempfile
import subprocess
from pathlib import Path


# Raiz del proyecto
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

PYTHON_BIN = sys.executable

CLI_MODULE = "src.client.cli"
SERVER_MODULE = "src.daemon.server"


def check(condition, description):
    if condition:
        print(f"PASS: {description}")
        return 0

    print(f"FAIL: {description}")
    return 1


def get_env(extra=None):
    # Creamos un entorno controlado para los procesos de prueba
    env = os.environ.copy()
    env["PYTHONPATH"] = PROJECT_ROOT

    if extra:
        env.update(extra)

    return env


def run_command(command, env=None):
    process = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        env=env or get_env(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    return (
        process.returncode,
        process.stdout.strip(),
        process.stderr.strip(),
    )


def main():
    failures = 0

    # ---------------------------------------------------------
    # TC-053 - Socket predeterminado
    # ---------------------------------------------------------

    print("========================================")
    print("TC-053 - SOCKET PREDETERMINADO")
    print("========================================")

    code, stdout, stderr = run_command(
        [
            PYTHON_BIN,
            "-c",
            (
                "from src.protocol.endpoint import DEFAULT_SOCKET_PATH; "
                "print(DEFAULT_SOCKET_PATH)"
            ),
        ]
    )

    print("Exit code:", code)
    print("STDOUT:", repr(stdout))
    print("STDERR:", repr(stderr))

    failures += check(
        code == 0,
        "La configuracion puede cargarse correctamente."
    )

    failures += check(
        stdout == "/tmp/jobsy.sock",
        "El socket predeterminado es /tmp/jobsy.sock."
    )

    # ---------------------------------------------------------
    # TC-054 - Ruta absoluta personalizada
    # ---------------------------------------------------------

    print("\n========================================")
    print("TC-054 - SOCKET PERSONALIZADO ABSOLUTO")
    print("========================================")

    with tempfile.TemporaryDirectory() as temp_dir:
        custom_socket = os.path.join(
            temp_dir,
            "control.sock"
        )

        code, stdout, stderr = run_command(
            [
                PYTHON_BIN,
                "-c",
                (
                    "from src.daemon.config import DaemonConfig; "
                    f"c=DaemonConfig(socket_path={custom_socket!r}); "
                    "print(c.socket_path)"
                ),
            ]
        )

        print("Exit code:", code)
        print("STDOUT:", repr(stdout))
        print("STDERR:", repr(stderr))

        failures += check(
            code == 0,
            "Se acepta una ruta absoluta valida."
        )

        failures += check(
            stdout == custom_socket,
            "La configuracion conserva la ruta personalizada."
        )

    # ---------------------------------------------------------
    # TC-057 - Ruta relativa
    # ---------------------------------------------------------

    print("\n========================================")
    print("TC-057 - RECHAZAR RUTA RELATIVA")
    print("========================================")

    code, stdout, stderr = run_command(
        [
            PYTHON_BIN,
            "-c",
            (
                "from src.protocol.endpoint import resolve_socket_path; "
                "resolve_socket_path('socket.sock')"
            ),
        ]
    )

    print("Exit code:", code)
    print("STDOUT:", repr(stdout))
    print("STDERR:", repr(stderr))

    failures += check(
        code != 0,
        "Una ruta relativa es rechazada."
    )

    failures += check(
        "absoluta" in stderr.lower(),
        "El error indica que la ruta debe ser absoluta."
    )

    # ---------------------------------------------------------
    # TC-058 - Directorio padre inexistente
    # ---------------------------------------------------------

    print("\n========================================")
    print("TC-058 - RECHAZAR DIRECTORIO PADRE INEXISTENTE")
    print("========================================")

    invalid_path = (
        "/tmp/jobsy-directorio-que-no-existe-qa/"
        "control.sock"
    )

    code, stdout, stderr = run_command(
        [
            PYTHON_BIN,
            "-c",
            (
                "from src.protocol.endpoint import resolve_socket_path; "
                f"resolve_socket_path({invalid_path!r})"
            ),
        ]
    )

    print("Exit code:", code)
    print("STDOUT:", repr(stdout))
    print("STDERR:", repr(stderr))

    failures += check(
        code != 0,
        "Se rechaza una ruta cuyo directorio padre no existe."
    )

    failures += check(
        "directorio padre" in stderr.lower(),
        "El error indica que el directorio padre debe existir."
    )

    # ---------------------------------------------------------
    # TC-059 - Symlink final
    # ---------------------------------------------------------

    print("\n========================================")
    print("TC-059 - RECHAZAR ENLACE SIMBOLICO")
    print("========================================")

    with tempfile.TemporaryDirectory() as temp_dir:
        real_file = os.path.join(
            temp_dir,
            "archivo-real"
        )

        symlink_path = os.path.join(
            temp_dir,
            "control.sock"
        )

        Path(real_file).touch()
        os.symlink(real_file, symlink_path)

        code, stdout, stderr = run_command(
            [
                PYTHON_BIN,
                "-c",
                (
                    "from src.protocol.endpoint import resolve_socket_path; "
                    f"resolve_socket_path({symlink_path!r})"
                ),
            ]
        )

        print("Exit code:", code)
        print("STDOUT:", repr(stdout))
        print("STDERR:", repr(stderr))

        failures += check(
            code != 0,
            "La ruta final como enlace simbolico es rechazada."
        )

        failures += check(
            "enlace simbólico" in stderr.lower()
            or "enlace simbolico" in stderr.lower(),
            "El error informa que no se permite un enlace simbolico."
        )

    # ---------------------------------------------------------
    # TC-060 - Ruta mayor a 107 bytes
    # ---------------------------------------------------------

    print("\n========================================")
    print("TC-060 - RECHAZAR RUTA MAYOR A 107 BYTES")
    print("========================================")

    with tempfile.TemporaryDirectory(
        dir="/tmp"
    ) as temp_dir:

        long_name = "a" * 100 + ".sock"

        long_path = os.path.join(
            temp_dir,
            long_name
        )

        code, stdout, stderr = run_command(
            [
                PYTHON_BIN,
                "-c",
                (
                    "from src.protocol.endpoint import resolve_socket_path; "
                    f"resolve_socket_path({long_path!r})"
                ),
            ]
        )

        print("Longitud bytes:", len(os.fsencode(long_path)))
        print("Exit code:", code)
        print("STDOUT:", repr(stdout))
        print("STDERR:", repr(stderr))

        failures += check(
            code != 0,
            "Se rechaza una ruta mayor a 107 bytes."
        )

        failures += check(
            "107 bytes" in stderr,
            "El error informa el limite maximo permitido."
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
