import os
import re
import sys
import time
import subprocess


# Ruta raiz del proyecto Jobsy
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

# Ruta donde el daemon crea el socket UNIX
SOCKET_PATH = "/tmp/jobsy.sock"

# Usamos el mismo interprete de Python que ejecuta este script
PYTHON_BIN = sys.executable

# Modulos que vamos a ejecutar durante las pruebas
SERVER_MODULE = "src.daemon.server"
CLI_MODULE = "src.client.cli"


def get_test_env():
    # Creamos un entorno para que Python pueda encontrar el paquete src
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


def check(condition, description):
    # Funcion auxiliar para mostrar si una comprobacion pasa o falla
    if condition:
        print(f"PASS: {description}")
        return 0

    print(f"FAIL: {description}")
    return 1


def cleanup(server_process=None):
    # Si el servidor sigue ejecutandose intentamos detenerlo correctamente
    if server_process is not None and server_process.poll() is None:
        server_process.terminate()

        try:
            server_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            # Si no termina dentro del tiempo esperado lo forzamos
            server_process.kill()
            server_process.wait(timeout=2)

    # Eliminamos el socket por si quedo creado despues de alguna prueba
    if os.path.exists(SOCKET_PATH):
        try:
            os.remove(SOCKET_PATH)
        except OSError:
            pass


def wait_for_socket(timeout=5):
    # Esperamos unos segundos a que el daemon cree el socket
    start = time.time()

    while time.time() - start < timeout:
        if os.path.exists(SOCKET_PATH):
            return True

        time.sleep(0.05)

    return False


def run_cli(*arguments):
    # Ejecutamos la CLI como un proceso independiente
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


def extract_job_id(output):
    # Buscamos el UUID que devuelve la CLI cuando se crea un trabajo
    match = re.search(
        r"ID:\s*([0-9a-fA-F-]{36})",
        output
    )

    if match:
        return match.group(1)

    return None


def wait_for_status(job_id, expected_status, timeout=5):
    # Consultamos el estado varias veces hasta obtener el esperado
    start = time.time()

    while time.time() - start < timeout:
        code, stdout, stderr = run_cli(
            "status",
            job_id
        )

        if (
            code == 0
            and f"Estado: {expected_status}" in stdout
        ):
            return True, stdout

        time.sleep(0.05)

    return False, ""


def main():

    failures = 0
    server_process = None

    # Limpiamos cualquier socket o proceso que pudiera quedar de una ejecucion anterior
    cleanup()

    try:

        # ---------------------------------------------------------
        # TC-037 - Verificar inicio del daemon y creacion del socket
        # ---------------------------------------------------------

        print("========================================")
        print("TC-037 - INICIAR DAEMON Y CREAR SOCKET UNIX")
        print("========================================")

        # Iniciamos el daemon como un proceso independiente
        server_process = subprocess.Popen(
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

        socket_created = wait_for_socket()

        # Si el daemon termino antes de crear el socket mostramos el error real
        if not socket_created and server_process.poll() is not None:
            daemon_stdout, daemon_stderr = server_process.communicate()

            print("Salida del daemon:", repr(daemon_stdout))
            print("Error del daemon:", repr(daemon_stderr))

        print("PID del daemon:", server_process.pid)
        print("Socket creado:", socket_created)
        print("Ruta:", SOCKET_PATH)

        # El daemon debe seguir activo despues de iniciar
        failures += check(
            server_process.poll() is None,
            "El daemon permanece en ejecucion."
        )

        # Tambien debe haber creado el socket UNIX para recibir peticiones
        failures += check(
            socket_created,
            "El daemon crea el socket UNIX."
        )

        # ---------------------------------------------------------
        # TC-038 - Enviar un trabajo desde la CLI usando IPC
        # ---------------------------------------------------------

        print("\n========================================")
        print("TC-038 - ENVIAR TRABAJO MEDIANTE CLI E IPC")
        print("========================================")

        code, stdout, stderr = run_cli(
            "run",
            "echo",
            "Hola desde IPC"
        )

        print("Exit code:", code)
        print("STDOUT:", repr(stdout))
        print("STDERR:", repr(stderr))

        # Obtenemos el ID generado para usarlo en las siguientes pruebas
        job_id = extract_job_id(stdout)

        print("Job ID:", job_id)

        failures += check(
            code == 0,
            "La CLI termina con codigo 0 al enviar un trabajo."
        )

        failures += check(
            job_id is not None,
            "El daemon devuelve un identificador de trabajo."
        )

        # ---------------------------------------------------------
        # TC-039 - Consultar el trabajo desde otra ejecucion de CLI
        # ---------------------------------------------------------

        print("\n========================================")
        print("TC-039 - CONSULTAR TRABAJO MEDIANTE IPC")
        print("========================================")

        succeeded = False
        status_output = ""

        if job_id is not None:
            # Esperamos hasta que el trabajo termine correctamente
            succeeded, status_output = wait_for_status(
                job_id,
                "SUCCEEDED"
            )

        print(status_output)

        failures += check(
            succeeded,
            "El trabajo puede consultarse desde otra invocacion de la CLI."
        )

        # Verificamos que se conserve el codigo de salida
        failures += check(
            "Codigo de salida: 0" in status_output
            or "Código de salida: 0" in status_output,
            "La consulta conserva el codigo de salida del trabajo."
        )

        # Tambien debe conservarse el comando que se ejecuto
        failures += check(
            "Comando: echo Hola desde IPC" in status_output,
            "La consulta conserva el comando asociado."
        )

        # ---------------------------------------------------------
        # TC-040 - Verificar que los trabajos se mantienen en la sesion
        # ---------------------------------------------------------

        print("\n========================================")
        print("TC-040 - LISTAR TRABAJOS PERSISTENTES EN LA SESION")
        print("========================================")

        code, stdout, stderr = run_cli(
            "list"
        )

        print("Exit code:", code)
        print("STDOUT:")
        print(stdout)

        failures += check(
            code == 0,
            "El comando list termina con codigo 0."
        )

        # El trabajo creado anteriormente debe seguir disponible
        # porque el JobManager permanece dentro del daemon
        failures += check(
            job_id is not None
            and job_id in stdout,
            "El listado conserva el trabajo creado por una invocacion anterior."
        )

        # ---------------------------------------------------------
        # TC-041 - Cancelar un trabajo que sigue en ejecucion
        # ---------------------------------------------------------

        print("\n========================================")
        print("TC-041 - CANCELAR TRABAJO MEDIANTE IPC")
        print("========================================")

        # Creamos un trabajo largo para tener tiempo de cancelarlo
        code, stdout, stderr = run_cli(
            "run",
            "sleep",
            "10"
        )

        long_job_id = extract_job_id(stdout)

        print("Job ID:", long_job_id)

        cancel_code = None
        cancel_stdout = ""
        cancel_stderr = ""

        if long_job_id is not None:
            # Solicitamos la cancelacion mediante otra llamada a la CLI
            cancel_code, cancel_stdout, cancel_stderr = run_cli(
                "cancel",
                long_job_id
            )

        print("Exit code cancel:", cancel_code)
        print("STDOUT cancel:", repr(cancel_stdout))
        print("STDERR cancel:", repr(cancel_stderr))

        canceled = False
        canceled_output = ""

        if long_job_id is not None:
            # Confirmamos despues que el estado realmente sea CANCELED
            canceled, canceled_output = wait_for_status(
                long_job_id,
                "CANCELED"
            )

        print(canceled_output)

        failures += check(
            long_job_id is not None,
            "Se obtiene el ID del trabajo de larga duracion."
        )

        failures += check(
            cancel_code == 0,
            "La orden cancel mediante IPC termina con codigo 0."
        )

        failures += check(
            canceled,
            "El estado consultado posteriormente es CANCELED."
        )

        # ---------------------------------------------------------
        # TC-042 - Consultar un ID que no existe
        # ---------------------------------------------------------

        print("\n========================================")
        print("TC-042 - CONSULTAR ID INEXISTENTE MEDIANTE IPC")
        print("========================================")

        code, stdout, stderr = run_cli(
            "status",
            "id-que-no-existe"
        )

        print("Exit code:", code)
        print("STDOUT:", repr(stdout))
        print("STDERR:", repr(stderr))

        # La CLI debe reportar el error sin cerrar o afectar al daemon
        failures += check(
            code == 1,
            "La consulta de un ID inexistente termina con codigo 1."
        )

        failures += check(
            "No existe un trabajo" in stderr,
            "La CLI informa de forma controlada que el trabajo no existe."
        )

    finally:
        # Sin importar si alguna prueba falla, limpiamos el proceso y el socket
        cleanup(server_process)

    # ---------------------------------------------------------
    # Resultado general de todas las pruebas
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