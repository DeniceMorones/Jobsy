#!/usr/bin/env python3
"""Pruebas QA para RNF-09: aislamiento de fallos de limpieza."""

from collections import deque
from types import SimpleNamespace
import subprocess
import threading
import time

from src.daemon.scheduler import Scheduler


FAILURES = 0


def section(title):
    print()
    print("=" * 40)
    print(title)
    print("=" * 40)


def check(condition, success, failure):
    global FAILURES

    if condition:
        print(f"PASS: {success}")
        return

    FAILURES += 1
    print(f"FAIL: {failure}")


class FakeProcess:
    """Proceso controlado que permanece vivo hasta que QA autoriza su fin."""

    def __init__(self):
        self.returncode = None
        self.release = threading.Event()
        self.first_wait = threading.Event()
        self.wait_calls = 0

    def wait(self, timeout=None):
        self.wait_calls += 1
        self.first_wait.set()

        if not self.release.is_set():
            # No esperamos el segundo completo de producción para mantener
            # rápida la prueba. Simulamos que el proceso sigue vivo.
            time.sleep(0.05)
            raise subprocess.TimeoutExpired(
                cmd="fake-cleanup-process",
                timeout=timeout,
            )

        self.returncode = -9
        return self.returncode


def build_scheduler():
    """
    Construye únicamente el estado que necesita _isolate_failed_cleanup().

    Se evita ejecutar __init__ porque esta prueba quiere aislar exactamente
    el comportamiento introducido para RNF-09.
    """
    scheduler = Scheduler.__new__(Scheduler)
    scheduler.condition = threading.Condition()
    scheduler.stopping = False

    # Estado mínimo utilizado por counts(), empleado como operación de
    # control para comprobar que el scheduler no queda bloqueado.
    scheduler.reservations = {"job-aislado"}
    scheduler.pending = deque(["job-pendiente"])

    return scheduler


def main():
    scheduler = build_scheduler()
    process = FakeProcess()
    job = SimpleNamespace(id="qa-rnf09-isolated-job")

    cleanup_error = RuntimeError(
        "fallo de cleanup provocado por QA"
    )

    result_holder = {}

    def isolate_worker():
        result_holder["result"] = scheduler._isolate_failed_cleanup(
            job,
            process,
            cleanup_error,
        )

    worker = threading.Thread(
        target=isolate_worker,
        name="qa-rnf09-isolation",
        daemon=True,
    )

    # ---------------------------------------------------------
    section("TC-088 - AISLAR FALLO DE CLEANUP DE UN TRABAJO")

    worker.start()

    process.first_wait.wait(timeout=1.0)
    time.sleep(0.05)

    print("Worker de aislamiento activo:", worker.is_alive())
    print("Intentos de wait:", process.wait_calls)

    check(
        worker.is_alive(),
        "El trabajo con fallo de cleanup permanece aislado mientras su proceso sigue vivo.",
        "El aislamiento terminó antes de confirmar la terminación del proceso.",
    )

    check(
        process.wait_calls >= 1,
        "El scheduler intenta confirmar periódicamente la terminación del proceso.",
        "No se intentó comprobar la terminación del proceso aislado.",
    )

    # ---------------------------------------------------------
    section("TC-089 - EL SCHEDULER SIGUE OPERATIVO DURANTE EL AISLAMIENTO")

    start = time.monotonic()
    running, pending = scheduler.counts()
    elapsed = time.monotonic() - start

    print("Reservas:", running)
    print("Pendientes:", pending)
    print(f"Tiempo de respuesta counts(): {elapsed:.6f} s")

    check(
        (running, pending) == (1, 1),
        "El scheduler puede consultar su estado mientras otro trabajo está aislado.",
        "El scheduler no devolvió el estado esperado durante el aislamiento.",
    )

    check(
        elapsed < 0.5,
        "El fallo de cleanup de un trabajo no bloquea las operaciones del scheduler.",
        "La operación del scheduler quedó bloqueada por el trabajo aislado.",
    )

    check(
        worker.is_alive(),
        "El cleanup continúa aislado sin bloquear al resto del scheduler.",
        "El worker de aislamiento terminó inesperadamente antes de liberar el proceso.",
    )

    # ---------------------------------------------------------
    section("TC-090 - FINALIZAR DE FORMA CONTROLADA EL TRABAJO AISLADO")

    process.release.set()
    worker.join(timeout=2.0)

    print("Worker activo después de liberar proceso:", worker.is_alive())
    print("Return code simulado:", process.returncode)
    print("Resultado de aislamiento:", result_holder.get("result"))

    expected_diagnostic = (
        "No se pudo confirmar la terminación del proceso: "
        "fallo de cleanup provocado por QA"
    )

    expected_result = (
        -9,
        "",
        expected_diagnostic,
    )

    check(
        not worker.is_alive(),
        "El aislamiento termina cuando se confirma que el proceso finalizó.",
        "El worker de aislamiento continúa activo después de finalizar el proceso.",
    )

    check(
        result_holder.get("result") == expected_result,
        "El scheduler devuelve código de salida y diagnóstico controlados.",
        "El resultado del proceso aislado no coincide con el esperado.",
    )

    check(
        "fallo de cleanup provocado por QA"
        in result_holder.get("result", (None, None, ""))[2],
        "El diagnóstico conserva la causa original del fallo de cleanup.",
        "El diagnóstico perdió la causa original del fallo.",
    )

    # ---------------------------------------------------------
    print()
    print("=" * 40)

    if FAILURES == 0:
        print("RESULTADO GENERAL: PASS")
        print("Todas las comprobaciones fueron exitosas.")
        return 0

    print("RESULTADO GENERAL: FAIL")
    print(f"Comprobaciones fallidas: {FAILURES}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
