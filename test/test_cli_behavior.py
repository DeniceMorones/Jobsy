import io
import sys
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch

from src.client.cli import main
from src.daemon.job_manager import JobManager
from src.daemon.executor import Executor


def check(condition, description):
    if condition:
        print(f"PASS: {description}")
        return 0

    print(f"FAIL: {description}")
    return 1


def run_cli(arguments, manager=None, executor=None):
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()

    exit_code = None

    argv = ["jobsy"] + arguments

    with patch.object(sys, "argv", argv):
        try:
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                main(
                    manager=manager,
                    executor=executor
                )

        except SystemExit as exc:
            exit_code = exc.code

    return (
        exit_code,
        stdout_buffer.getvalue(),
        stderr_buffer.getvalue()
    )


def main_test():

    failures = 0

    # ---------------------------------------------------------
    # TC-029
    # ---------------------------------------------------------

    print("========================================")
    print("TC-029 - MOSTRAR AYUDA SIN ARGUMENTOS")
    print("========================================")

    exit_code, stdout, stderr = run_cli([])

    print("Exit code:", exit_code)
    print("STDOUT:")
    print(stdout)

    failures += check(
        exit_code == 2,
        "La CLI termina con codigo 2 cuando no recibe argumentos."
    )

    failures += check(
        "usage: jobsy" in stdout
        and "Comandos disponibles" in stdout,
        "La CLI muestra informacion de ayuda."
    )

    # ---------------------------------------------------------
    # TC-030
    # ---------------------------------------------------------

    print("\n========================================")
    print("TC-030 - EJECUTAR COMANDO VALIDO")
    print("========================================")

    manager = JobManager()
    executor = Executor(manager)

    exit_code, stdout, stderr = run_cli(
        ["run", "echo", "Hola desde CLI"],
        manager,
        executor
    )

    print("Exit code:", exit_code)
    print("STDOUT:", repr(stdout))
    print("STDERR:", repr(stderr))

    jobs = manager.list_jobs()

    failures += check(
        exit_code == 0,
        "El comando run valido termina con codigo 0."
    )

    failures += check(
        len(jobs) == 1,
        "El comando run crea un trabajo."
    )

    failures += check(
        jobs[0].command == ["echo", "Hola desde CLI"],
        "El trabajo conserva correctamente el comando solicitado."
    )

    failures += check(
        "Trabajo creado y enviado a ejecución con ID:" in stdout,
        "La CLI informa el ID del trabajo creado."
    )

    # ---------------------------------------------------------
    # TC-031
    # ---------------------------------------------------------

    print("\n========================================")
    print("TC-031 - LISTAR TRABAJOS")
    print("========================================")

    manager = JobManager()
    executor = Executor(manager)

    job1 = manager.create_job(
        ["echo", "Trabajo 1"]
    )

    job2 = manager.create_job(
        ["sleep", "1"]
    )

    exit_code, stdout, stderr = run_cli(
        ["list"],
        manager,
        executor
    )

    print("Exit code:", exit_code)
    print("STDOUT:")
    print(stdout)

    failures += check(
        exit_code == 0,
        "El comando list termina con codigo 0."
    )

    failures += check(
        job1.id in stdout
        and job2.id in stdout,
        "La CLI lista los trabajos registrados."
    )

    failures += check(
        "Estado: QUEUED" in stdout,
        "La CLI muestra el estado de los trabajos."
    )

    # ---------------------------------------------------------
    # TC-032
    # ---------------------------------------------------------

    print("\n========================================")
    print("TC-032 - CONSULTAR ESTADO DE TRABAJO")
    print("========================================")

    manager = JobManager()
    executor = Executor(manager)

    job = manager.create_job(
        ["echo", "Consultar estado"]
    )

    exit_code, stdout, stderr = run_cli(
        ["status", job.id],
        manager,
        executor
    )

    print("Exit code:", exit_code)
    print("STDOUT:")
    print(stdout)

    failures += check(
        exit_code == 0,
        "El comando status valido termina con codigo 0."
    )

    failures += check(
        f"ID: {job.id}" in stdout,
        "La CLI muestra el ID correcto."
    )

    failures += check(
        "Estado: QUEUED" in stdout,
        "La CLI muestra el estado correcto."
    )

    failures += check(
        "Comando: echo Consultar estado" in stdout,
        "La CLI muestra el comando asociado."
    )

    # ---------------------------------------------------------
    # TC-033
    # ---------------------------------------------------------

    print("\n========================================")
    print("TC-033 - CANCELAR TRABAJO DESDE CLI")
    print("========================================")

    manager = JobManager()
    executor = Executor(manager)

    job = manager.create_job(
        ["sleep", "10"]
    )

    exit_code, stdout, stderr = run_cli(
        ["cancel", job.id],
        manager,
        executor
    )

    print("Exit code:", exit_code)
    print("STDOUT:")
    print(stdout)
    print("Estado final:", job.status)

    failures += check(
        exit_code == 0,
        "El comando cancel valido termina con codigo 0."
    )

    failures += check(
        job.status == "CANCELED",
        "La CLI cancela correctamente el trabajo."
    )

    failures += check(
        "Estado actual: CANCELED" in stdout,
        "La CLI informa el estado CANCELED."
    )

    # ---------------------------------------------------------
    # TC-034
    # ---------------------------------------------------------

    print("\n========================================")
    print("TC-034 - CONSULTAR ID INEXISTENTE")
    print("========================================")

    manager = JobManager()
    executor = Executor(manager)

    exit_code, stdout, stderr = run_cli(
        ["status", "id-que-no-existe"],
        manager,
        executor
    )

    print("Exit code:", exit_code)
    print("STDOUT:", repr(stdout))
    print("STDERR:", repr(stderr))

    failures += check(
        exit_code == 1,
        "La consulta de un ID inexistente termina con codigo 1."
    )

    failures += check(
        "No existe un trabajo" in stderr,
        "La CLI informa el error mediante STDERR."
    )

    # ---------------------------------------------------------
    # TC-035
    # ---------------------------------------------------------

    print("\n========================================")
    print("TC-035 - FILTRO DE ESTADO INVALIDO")
    print("========================================")

    manager = JobManager()
    executor = Executor(manager)

    exit_code, stdout, stderr = run_cli(
        ["list", "--status", "ESTADO_INVALIDO"],
        manager,
        executor
    )

    print("Exit code:", exit_code)
    print("STDOUT:", repr(stdout))
    print("STDERR:", repr(stderr))

    failures += check(
        exit_code == 2,
        "Un estado invalido en la CLI termina con codigo 2."
    )

    failures += check(
        "invalid choice" in stderr,
        "argparse informa que el estado proporcionado es invalido."
    )

    # ---------------------------------------------------------
    # TC-036
    # ---------------------------------------------------------

    print("\n========================================")
    print("TC-036 - SUBCOMANDO INVALIDO")
    print("========================================")

    exit_code, stdout, stderr = run_cli(
        ["comando-inexistente"]
    )

    print("Exit code:", exit_code)
    print("STDOUT:", repr(stdout))
    print("STDERR:", repr(stderr))

    failures += check(
        exit_code == 2,
        "Un subcomando invalido termina con codigo 2."
    )

    failures += check(
        "invalid choice" in stderr,
        "La CLI informa que el subcomando es invalido."
    )

    # ---------------------------------------------------------
    # RESULTADO GENERAL
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
    raise SystemExit(main_test())