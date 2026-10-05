import os
import sys
import json
import time
import socket
import subprocess


# Ruta raiz del proyecto Jobsy
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

# Socket UNIX utilizado por Jobsy
SOCKET_PATH = "/tmp/jobsy.sock"

# Usamos el mismo interprete de Python que ejecuta este script
PYTHON_BIN = sys.executable

# Modulos principales
SERVER_MODULE = "src.daemon.server"
CLI_MODULE = "src.client.cli"


def check(condition, description):
    # Funcion auxiliar para mostrar PASS o FAIL
    if condition:
        print(f"PASS: {description}")
        return 0

    print(f"FAIL: {description}")
    return 1


def get_test_env():
    env = os.environ.copy()

    current_pythonpath = env.get("PYTHONPATH", "")

    if current_pythonpath:
        env["PYTHONPATH"] = (
            PROJECT_ROOT
            + os.pathsep
            + current_pythonpath
        )
    else:
        env["PYTHONPATH"] = PROJECT_ROOT

    return env


def run_cli(*arguments):
    # Ejecutamos la CLI como proceso independiente
    process = subprocess.run(
        [
            PYTHON_BIN,
            "-m",
            CLI_MODULE,
            *arguments,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=PROJECT_ROOT,
        env=get_test_env(),
    )

    return (
        process.returncode,
        process.stdout.strip(),
        process.stderr.strip(),
    )


def start_daemon():
    # Iniciamos el daemon y esperamos a que cree el socket
    process = subprocess.Popen(
        [
            PYTHON_BIN,
            "-m",
            SERVER_MODULE,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=PROJECT_ROOT,
        env=get_test_env(),
    )

    start = time.time()

    while time.time() - start < 5:
        if os.path.exists(SOCKET_PATH):
            return process

        if process.poll() is not None:
            break

        time.sleep(0.05)

    return process


def cleanup(server_process=None):
    # Detenemos el daemon si sigue activo
    if server_process is not None and server_process.poll() is None:
        server_process.terminate()

        try:
            server_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            server_process.kill()
            server_process.wait(timeout=2)

    # Eliminamos el socket si quedo de una prueba anterior
    if os.path.exists(SOCKET_PATH):
        try:
            os.remove(SOCKET_PATH)
        except OSError:
            pass


def send_raw_request(payload):
    # Enviamos directamente una peticion JSON al socket
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.connect(SOCKET_PATH)
        client.sendall(
            json.dumps(payload).encode("utf-8")
        )

        response = client.recv(4096)

    return json.loads(
        response.decode("utf-8")
    )


def send_invalid_json(raw_data):
    # Enviamos datos que no tienen formato JSON valido
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.connect(SOCKET_PATH)
        client.sendall(
            raw_data.encode("utf-8")
        )

        response = client.recv(4096)

    return json.loads(
        response.decode("utf-8")
    )


def main():
    failures = 0
    server_process = None

    cleanup()

    # ---------------------------------------------------------
    # TC-043 - CLI sin daemon activo
    # ---------------------------------------------------------

    print("========================================")
    print("TC-043 - EJECUTAR CLI SIN DAEMON ACTIVO")
    print("========================================")

    code, stdout, stderr = run_cli(
        "list"
    )

    print("Exit code:", code)
    print("STDOUT:", repr(stdout))
    print("STDERR:", repr(stderr))

    failures += check(
        code == 1,
        "La CLI termina con codigo 1 cuando el daemon no esta activo."
    )

    failures += check(
        "servicio Jobsy no está en ejecución" in stderr
        or "servicio Jobsy no esta en ejecucion" in stderr,
        "La CLI informa que el servicio Jobsy no esta en ejecucion."
    )

    try:
        # ---------------------------------------------------------
        # Iniciar daemon para las siguientes pruebas
        # ---------------------------------------------------------

        print("\n========================================")
        print("PREPARACION - INICIAR DAEMON")
        print("========================================")

        server_process = start_daemon()

        print("PID del daemon:", server_process.pid)
        print("Socket existe:", os.path.exists(SOCKET_PATH))

        failures += check(
            server_process.poll() is None,
            "El daemon permanece activo."
        )

        failures += check(
            os.path.exists(SOCKET_PATH),
            "El socket UNIX fue creado."
        )

        # ---------------------------------------------------------
        # TC-044 - Cancelar ID inexistente
        # ---------------------------------------------------------

        print("\n========================================")
        print("TC-044 - CANCELAR ID INEXISTENTE MEDIANTE IPC")
        print("========================================")

        code, stdout, stderr = run_cli(
            "cancel",
            "id-que-no-existe"
        )

        print("Exit code:", code)
        print("STDOUT:", repr(stdout))
        print("STDERR:", repr(stderr))

        failures += check(
            code == 1,
            "Cancelar un ID inexistente termina con codigo 1."
        )

        failures += check(
            "No existe un trabajo" in stderr,
            "La CLI informa que el trabajo no existe."
        )

        # ---------------------------------------------------------
        # TC-045 - Filtrar trabajos por estado
        # ---------------------------------------------------------

        print("\n========================================")
        print("TC-045 - FILTRAR TRABAJOS POR ESTADO MEDIANTE IPC")
        print("========================================")

        # Creamos un trabajo exitoso
        code_ok, out_ok, err_ok = run_cli(
            "run",
            "echo",
            "Filtro IPC"
        )

        time.sleep(0.3)

        # Creamos un trabajo fallido
        code_fail, out_fail, err_fail = run_cli(
            "run",
            "ls",
            "/directorio_inexistente_qa_123"
        )

        time.sleep(0.3)

        code, stdout, stderr = run_cli(
            "list",
            "--status",
            "SUCCEEDED"
        )

        print("Filtro SUCCEEDED:")
        print(stdout)

        failures += check(
            code == 0,
            "El filtro SUCCEEDED termina con codigo 0."
        )

        failures += check(
            "Estado: SUCCEEDED" in stdout,
            "El listado filtrado contiene trabajos SUCCEEDED."
        )

        failures += check(
            "Estado: FAILED" not in stdout,
            "El filtro SUCCEEDED no muestra trabajos FAILED."
        )

        code, stdout, stderr = run_cli(
            "list",
            "--status",
            "FAILED"
        )

        print("\nFiltro FAILED:")
        print(stdout)

        failures += check(
            code == 0,
            "El filtro FAILED termina con codigo 0."
        )

        failures += check(
            "Estado: FAILED" in stdout,
            "El listado filtrado contiene trabajos FAILED."
        )

        failures += check(
            "Estado: SUCCEEDED" not in stdout,
            "El filtro FAILED no muestra trabajos SUCCEEDED."
        )

        # ---------------------------------------------------------
        # TC-046 - Accion IPC invalida
        # ---------------------------------------------------------

        print("\n========================================")
        print("TC-046 - ENVIAR ACCION IPC INVALIDA")
        print("========================================")

        response = send_raw_request(
            {
                "action": "accion_invalida"
            }
        )

        print("Respuesta:", response)

        failures += check(
            response.get("status") == "error",
            "El daemon responde con status error."
        )

        failures += check(
            response.get("message") == "Acción no válida",
            "El daemon informa que la accion no es valida."
        )

        # ---------------------------------------------------------
        # TC-047 - JSON invalido
        # ---------------------------------------------------------

        print("\n========================================")
        print("TC-047 - ENVIAR JSON INVALIDO")
        print("========================================")

        response = send_invalid_json(
            "{esto no es json valido"
        )

        print("Respuesta:", response)

        failures += check(
            response.get("status") == "error",
            "El daemon responde de forma controlada ante JSON invalido."
        )

        failures += check(
            "message" in response,
            "La respuesta contiene un mensaje de error."
        )

        # ---------------------------------------------------------
        # TC-048 - El daemon sigue operativo despues de errores
        # ---------------------------------------------------------

        print("\n========================================")
        print("TC-048 - DAEMON SIGUE OPERATIVO DESPUES DE ERRORES")
        print("========================================")

        code, stdout, stderr = run_cli(
            "list"
        )

        print("Exit code:", code)
        print("STDOUT:")
        print(stdout)
        print("STDERR:", repr(stderr))

        failures += check(
            code == 0,
            "El daemon sigue respondiendo despues de solicitudes invalidas."
        )

        failures += check(
            server_process.poll() is None,
            "El proceso del daemon sigue activo."
        )

        # ---------------------------------------------------------
        # TC-049 - Limpieza del socket al apagar daemon
        # ---------------------------------------------------------

        print("\n========================================")
        print("TC-049 - ELIMINAR SOCKET DURANTE SHUTDOWN")
        print("========================================")

        socket_before = os.path.exists(SOCKET_PATH)

        print("Socket antes del shutdown:", socket_before)

        # Detenemos el daemon mediante SIGTERM
        server_process.terminate()

        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
            server_process.wait(timeout=2)

        # Damos un momento para terminar la limpieza
        time.sleep(0.1)

        socket_after = os.path.exists(SOCKET_PATH)

        print("Socket despues del shutdown:", socket_after)

        failures += check(
            socket_before,
            "El socket existia antes de apagar el daemon."
        )

        failures += check(
            not socket_after,
            "El socket fue eliminado durante el apagado del daemon."
        )

    finally:
        cleanup(server_process)

    # ---------------------------------------------------------
    # Resultado general
    # ---------------------------------------------------------

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