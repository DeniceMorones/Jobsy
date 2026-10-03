import time

from src.daemon.job_manager import JobManager
from src.daemon.executor import Executor


TERMINAL_STATES = {
    "SUCCEEDED",
    "FAILED",
    "CANCELED",
}


def check(condition, description):
    if condition:
        print(f"PASS: {description}")
        return 0

    print(f"FAIL: {description}")
    return 1


def wait_for_terminal(job, timeout=5):
    start = time.time()

    while time.time() - start < timeout:
        if job.status in TERMINAL_STATES:
            return True

        time.sleep(0.05)

    return False


def wait_for_process(job, timeout=5):
    start = time.time()

    while time.time() - start < timeout:
        if job.status == "RUNNING" and job.process is not None:
            return True

        time.sleep(0.05)

    return False


def wait_for_process_cleanup(job, timeout=5):
    start = time.time()

    while time.time() - start < timeout:
        if job.process is None:
            return True

        time.sleep(0.05)

    return False


def main():

    manager = JobManager()
    executor = Executor(manager)

    failures = 0

    # ---------------------------------------------------------
    # TC-018
    # ---------------------------------------------------------

    print("========================================")
    print("TC-018 - CANCELAR TRABAJO EN QUEUED")
    print("========================================")

    queued_job = manager.create_job(
        ["echo", "Trabajo en cola"]
    )

    print("Job ID:", queued_job.id)
    print("Estado antes:", queued_job.status)

    manager.cancel_job(queued_job.id)

    print("Estado despues:", queued_job.status)
    print("finished_at:", queued_job.finished_at)

    failures += check(
        queued_job.status == "CANCELED",
        "El trabajo QUEUED cambia a CANCELED."
    )

    failures += check(
        queued_job.finished_at is not None,
        "El trabajo cancelado registra finished_at."
    )

    # ---------------------------------------------------------
    # TC-019
    # ---------------------------------------------------------

    print("\n========================================")
    print("TC-019 - CANCELAR TRABAJO EN RUNNING")
    print("========================================")

    running_job = manager.create_job(
        ["sleep", "10"]
    )

    executor.execute(running_job)

    process_started = wait_for_process(
        running_job
    )

    print("Proceso iniciado:", process_started)
    print("Estado antes de cancelar:", running_job.status)

    process = running_job.process

    print(
        "PID:",
        process.pid if process is not None else None
    )

    failures += check(
        process_started
        and running_job.status == "RUNNING"
        and process is not None,
        "El trabajo alcanza RUNNING y tiene un proceso Linux asociado."
    )

    manager.cancel_job(running_job.id)

    print("Estado despues:", running_job.status)
    print("finished_at:", running_job.finished_at)

    failures += check(
        running_job.status == "CANCELED",
        "El trabajo RUNNING cambia a CANCELED."
    )

    failures += check(
        running_job.finished_at is not None,
        "El trabajo cancelado registra finished_at."
    )

    process_terminated = (
        process is not None
        and process.poll() is not None
    )

    failures += check(
        process_terminated,
        "El proceso Linux asociado termina despues de la cancelacion."
    )

    cleanup_completed = wait_for_process_cleanup(
        running_job
    )

    failures += check(
        cleanup_completed
        and running_job.process is None,
        "Executor limpia la referencia al proceso."
    )

    failures += check(
        running_job.status == "CANCELED",
        "Executor conserva el estado CANCELED al terminar el proceso."
    )

    # ---------------------------------------------------------
    # TC-020
    # ---------------------------------------------------------

    print("\n========================================")
    print("TC-020 - CANCELAR ID INEXISTENTE")
    print("========================================")

    nonexistent_rejected = False

    try:
        manager.cancel_job(
            "id-que-no-existe"
        )

    except Exception as exc:
        nonexistent_rejected = True
        print("Error controlado:", str(exc))

    failures += check(
        nonexistent_rejected,
        "Se rechaza la cancelacion de un ID inexistente."
    )

    # ---------------------------------------------------------
    # TC-021
    # ---------------------------------------------------------

    print("\n========================================")
    print("TC-021 - CANCELAR TRABAJO FINALIZADO")
    print("========================================")

    finished_job = manager.create_job(
        ["echo", "Trabajo finalizado"]
    )

    executor.execute(finished_job)

    finished = wait_for_terminal(
        finished_job
    )

    print("Estado antes de cancelar:", finished_job.status)

    finished_rejected = False

    try:
        manager.cancel_job(
            finished_job.id
        )

    except ValueError as exc:
        finished_rejected = True
        print("Error controlado:", str(exc))

    failures += check(
        finished
        and finished_job.status == "SUCCEEDED",
        "El trabajo finaliza correctamente antes de intentar cancelarlo."
    )

    failures += check(
        finished_rejected,
        "Se rechaza la cancelacion de un trabajo finalizado."
    )

    # ---------------------------------------------------------
    # TC-022
    # ---------------------------------------------------------

    print("\n========================================")
    print("TC-022 - CANCELAR DOS VECES")
    print("========================================")

    duplicate_job = manager.create_job(
        ["echo", "Cancelar dos veces"]
    )

    manager.cancel_job(
        duplicate_job.id
    )

    second_cancel_rejected = False

    try:
        manager.cancel_job(
            duplicate_job.id
        )

    except ValueError as exc:
        second_cancel_rejected = True
        print("Error controlado:", str(exc))

    failures += check(
        duplicate_job.status == "CANCELED",
        "La primera cancelacion deja el trabajo en CANCELED."
    )

    failures += check(
        second_cancel_rejected,
        "La segunda cancelacion es rechazada."
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
    print(
        f"Comprobaciones fallidas: {failures}"
    )

    return 1


if __name__ == "__main__":
    raise SystemExit(main())