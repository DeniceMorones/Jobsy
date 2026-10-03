import signal
import time

from src.daemon.job_manager import JobManager
from src.daemon.executor import Executor
from src.daemon.server import DaemonServer


def check(condition, description):
    if condition:
        print(f"PASS: {description}")
        return 0

    print(f"FAIL: {description}")
    return 1


def wait_for_process(job, timeout=5):
    start = time.time()

    while time.time() - start < timeout:
        if job.status == "RUNNING" and job.process is not None:
            return True

        time.sleep(0.05)

    return False


def main():

    failures = 0

    # ---------------------------------------------------------
    # TC-023
    # ---------------------------------------------------------

    print("========================================")
    print("TC-023 - INICIALIZAR SERVICIO")
    print("========================================")

    manager = JobManager()
    server = DaemonServer(manager)

    print("Host:", server.host)
    print("Puerto:", server.port)
    print("is_running:", server.is_running)
    print("Aceptando trabajos:", manager.is_accepting_jobs)

    failures += check(
        server.is_running is True,
        "El servicio inicia con is_running=True."
    )

    failures += check(
        manager.is_accepting_jobs is True,
        "JobManager acepta trabajos al iniciar el servicio."
    )

    # ---------------------------------------------------------
    # TC-024
    # ---------------------------------------------------------

    print("\n========================================")
    print("TC-024 - SHUTDOWN CON TRABAJO QUEUED")
    print("========================================")

    manager = JobManager()
    server = DaemonServer(manager)

    queued_job = manager.create_job(
        ["echo", "Trabajo pendiente"]
    )

    print("Estado antes:", queued_job.status)

    exit_code = None

    try:
        server.stop()

    except SystemExit as exc:
        exit_code = exc.code

    print("Estado despues:", queued_job.status)
    print("Servidor activo:", server.is_running)
    print("Aceptando trabajos:", manager.is_accepting_jobs)
    print("Exit code:", exit_code)

    failures += check(
        queued_job.status == "CANCELED",
        "El shutdown cancela trabajos QUEUED."
    )

    failures += check(
        server.is_running is False,
        "El servidor queda marcado como detenido."
    )

    failures += check(
        manager.is_accepting_jobs is False,
        "JobManager deja de aceptar trabajos."
    )

    failures += check(
        exit_code == 0,
        "El servicio termina con codigo de salida 0."
    )

    # ---------------------------------------------------------
    # TC-025
    # ---------------------------------------------------------

    print("\n========================================")
    print("TC-025 - SHUTDOWN CON TRABAJO RUNNING")
    print("========================================")

    manager = JobManager()
    executor = Executor(manager)
    server = DaemonServer(manager)

    running_job = manager.create_job(
        ["sleep", "1"]
    )

    executor.execute(running_job)

    process_started = wait_for_process(
        running_job
    )

    print("Proceso iniciado:", process_started)
    print("Estado antes del shutdown:", running_job.status)

    process = running_job.process

    print(
        "PID:",
        process.pid if process is not None else None
    )

    exit_code = None
    start_shutdown = time.time()

    try:
        server.stop()

    except SystemExit as exc:
        exit_code = exc.code

    shutdown_duration = time.time() - start_shutdown

    print("Estado despues:", running_job.status)
    print("Duracion del shutdown:", round(shutdown_duration, 3))
    print("Exit code:", exit_code)

    failures += check(
        process_started,
        "El trabajo alcanza RUNNING antes del shutdown."
    )

    failures += check(
        running_job.status == "SUCCEEDED",
        "El shutdown permite que un trabajo corto termine limpiamente."
    )

    failures += check(
        process is not None
        and process.poll() is not None,
        "El proceso Linux termina durante el shutdown."
    )

    failures += check(
        manager.is_accepting_jobs is False,
        "El servicio deja de aceptar nuevos trabajos durante el shutdown."
    )

    failures += check(
        exit_code == 0,
        "El apagado controlado termina con codigo 0."
    )

    # ---------------------------------------------------------
    # TC-026
    # ---------------------------------------------------------

    print("\n========================================")
    print("TC-026 - RECHAZAR TRABAJOS DESPUES DEL SHUTDOWN")
    print("========================================")

    manager = JobManager()
    server = DaemonServer(manager)

    try:
        server.stop()
    except SystemExit:
        pass

    rejected = False

    try:
        manager.create_job(
            ["echo", "No debe aceptarse"]
        )

    except RuntimeError as exc:
        rejected = True
        print("Error controlado:", str(exc))

    failures += check(
        rejected,
        "Se rechazan nuevos trabajos despues de iniciar el shutdown."
    )

    # ---------------------------------------------------------
    # TC-027
    # ---------------------------------------------------------

    print("\n========================================")
    print("TC-027 - PROCESAR SENAL DE APAGADO")
    print("========================================")

    manager = JobManager()
    server = DaemonServer(manager)

    exit_code = None

    try:
        server._handle_shutdown_signal(
            signal.SIGTERM,
            None
        )

    except SystemExit as exc:
        exit_code = exc.code

    print("Servidor activo:", server.is_running)
    print("Aceptando trabajos:", manager.is_accepting_jobs)
    print("Exit code:", exit_code)

    failures += check(
        server.is_running is False,
        "La señal de apagado detiene el servidor."
    )

    failures += check(
        manager.is_accepting_jobs is False,
        "La señal activa el shutdown de JobManager."
    )

    failures += check(
        exit_code == 0,
        "La señal produce una terminacion controlada con codigo 0."
    )

    # ---------------------------------------------------------
    # TC-028
    # ---------------------------------------------------------

    print("\n========================================")
    print("TC-028 - FORZAR CANCELACION POR TIMEOUT")
    print("========================================")

    manager = JobManager()
    executor = Executor(manager)

    long_job = manager.create_job(
        ["sleep", "10"]
    )

    executor.execute(long_job)

    process_started = wait_for_process(
        long_job
    )

    process = long_job.process

    print("Proceso iniciado:", process_started)
    print("Estado antes del shutdown:", long_job.status)

    print(
        "PID:",
        process.pid if process is not None else None
    )

    start_shutdown = time.time()

    manager.shutdown(timeout=0.5)

    shutdown_duration = time.time() - start_shutdown

    print("Estado despues:", long_job.status)
    print("Duracion del shutdown:", round(shutdown_duration, 3))
    print("Aceptando trabajos:", manager.is_accepting_jobs)

    process_terminated = (
        process is not None
        and process.poll() is not None
    )

    failures += check(
        process_started,
        "El trabajo alcanza RUNNING antes del shutdown."
    )

    failures += check(
        long_job.status == "CANCELED",
        "El trabajo que excede el timeout termina en CANCELED."
    )

    failures += check(
        process_terminated,
        "El proceso Linux es terminado despues de exceder el timeout."
    )

    failures += check(
        long_job.finished_at is not None,
        "El trabajo cancelado registra finished_at."
    )

    failures += check(
        manager.is_accepting_jobs is False,
        "JobManager permanece sin aceptar nuevos trabajos."
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
    raise SystemExit(main())