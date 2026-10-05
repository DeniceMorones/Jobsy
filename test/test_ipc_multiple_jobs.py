import os
import re
import sys
import time
import subprocess


# Ruta raiz del proyecto Jobsy
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

SOCKET_PATH = "/tmp/jobsy.sock"
PYTHON_BIN = sys.executable

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
    # Configuramos PYTHONPATH para que Python encuentre src
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
    # Ejecutamos cada comando de la CLI como un proceso independiente
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
    # Obtenemos el UUID devuelto por el comando run
    match = re.search(
        r"ID:\s*([0-9a-fA-F-]{36})",
        output
    )

    if match:
        return match.group(1)

    return None


def start_daemon():
    # Iniciamos el daemon como proceso independiente
    process = subprocess.Popen(
        [
            PYTHON_BIN,
            "-m",
            SERVER_MODULE,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
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

    # Eliminamos cualquier socket que haya quedado
    if os.path.exists(SOCKET_PATH):
        try:
            os.remove(SOCKET_PATH)
        except OSError:
            pass


def wait_for_terminal_state(job_id, timeout=5):
    # Esperamos a que el trabajo llegue a un estado final
    start = time.time()

    while time.time() - start < timeout:
        code, stdout, stderr = run_cli(
            "status",
            job_id
        )

        if code == 0:
            if "Estado: SUCCEEDED" in stdout:
                return True, stdout

            if "Estado: FAILED" in stdout:
                return True, stdout

            if "Estado: CANCELED" in stdout:
                return True, stdout

        time.sleep(0.05)

    return False, ""


def main():
    failures = 0
    server_process = None

    cleanup()

    try:
        server_process = start_daemon()

        print("========================================")
        print("PREPARACION - INICIAR DAEMON")
        print("========================================")

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
        # TC-050 - Multiples trabajos consecutivos
        # ---------------------------------------------------------

        print("\n========================================")
        print("TC-050 - EJECUTAR MULTIPLES TRABAJOS MEDIANTE IPC")
        print("========================================")

        commands = [
            ("echo", "Trabajo 1"),
            ("echo", "Trabajo 2"),
            ("echo", "Trabajo 3"),
            ("true",),
            ("false",),
        ]

        job_ids = []

        for command in commands:
            code, stdout, stderr = run_cli(
                "run",
                *command
            )

            job_id = extract_job_id(stdout)

            print(
                "Comando:",
                " ".join(command),
                "| Exit code CLI:",
                code,
                "| Job ID:",
                job_id
            )

            failures += check(
                code == 0,
                f"El comando {' '.join(command)} fue aceptado por el daemon."
            )

            failures += check(
                job_id is not None,
                f"Se genero ID para {' '.join(command)}."
            )

            if job_id is not None:
                job_ids.append(job_id)

        failures += check(
            len(job_ids) == len(commands),
            "Todos los trabajos enviados recibieron un ID."
        )

        # ---------------------------------------------------------
        # TC-051 - IDs unicos
        # ---------------------------------------------------------

        print("\n========================================")
        print("TC-051 - VERIFICAR IDS UNICOS")
        print("========================================")

        print("IDs generados:")

        for job_id in job_ids:
            print(job_id)

        failures += check(
            len(job_ids) == len(set(job_ids)),
            "Todos los trabajos tienen identificadores unicos."
        )

        # ---------------------------------------------------------
        # TC-052 - Todos los trabajos siguen disponibles
        # ---------------------------------------------------------

        print("\n========================================")
        print("TC-052 - CONSERVAR MULTIPLES TRABAJOS EN LA SESION")
        print("========================================")

        terminal_jobs = 0

        for job_id in job_ids:
            completed, status_output = wait_for_terminal_state(
                job_id
            )

            print()
            print(status_output)

            failures += check(
                completed,
                f"El trabajo {job_id} puede consultarse despues de su ejecucion."
            )

            if completed:
                terminal_jobs += 1

        code, stdout, stderr = run_cli(
            "list"
        )

        print("\nListado final:")
        print(stdout)

        failures += check(
            code == 0,
            "El listado final termina con codigo 0."
        )

        all_present = all(
            job_id in stdout
            for job_id in job_ids
        )

        failures += check(
            all_present,
            "Todos los trabajos enviados permanecen en el listado del daemon."
        )

        failures += check(
            terminal_jobs == len(job_ids),
            "Todos los trabajos pudieron consultarse individualmente."
        )

        failures += check(
            server_process.poll() is None,
            "El daemon continua activo despues de multiples solicitudes."
        )

    finally:
        cleanup(server_process)

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