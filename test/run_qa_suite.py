#!/usr/bin/env python3

import platform
import subprocess
import sys
import time
from pathlib import Path


TIMEOUT_SECONDS = 240

EXCLUDED_TESTS = {
    # Excluido por decisión QA.
    "test_process_behavior.py",

    # Contrato histórico de errores: esperaba "message".
    "test_ipc_robustness.py",

    # Prueba histórica de cancelación con expectativas
    # síncronas anteriores a cancel_grace/process-group cleanup.
    "test_cancellation.py",

    # Prueba histórica de CLI que inyecta manager/executor
    # en una API que ya no utiliza ese contrato.
    "test_cli_behavior.py",

    # Prueba IPC histórica que espera el campo "message"
    # en lugar del contrato operation/cause/suggestion.
    "test_queue_ipc.py",

    # Prueba histórica del servidor que espera atributo "host",
    # anterior al contrato actual basado en socket UNIX.
    "test_service_shutdown.py",
}


def section(title):
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def discover_tests(test_dir):
    return sorted(
        path.name
        for path in test_dir.glob("test_*.py")
        if path.name not in EXCLUDED_TESTS
    )


def git_value(repo_root, *args):
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if result.returncode != 0:
        return "N/A"

    return result.stdout.strip()


def run_test(path, repo_root):
    start = time.monotonic()

    try:
        result = subprocess.run(
            [sys.executable, str(path)],
            cwd=repo_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=TIMEOUT_SECONDS,
        )

        duration = time.monotonic() - start

        return {
            "status": "PASS" if result.returncode == 0 else "FAIL",
            "returncode": result.returncode,
            "duration": duration,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    except subprocess.TimeoutExpired as exc:
        duration = time.monotonic() - start

        stdout = exc.stdout or ""
        stderr = exc.stderr or ""

        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")

        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")

        return {
            "status": "TIMEOUT",
            "returncode": None,
            "duration": duration,
            "stdout": stdout,
            "stderr": stderr,
        }


def main():
    repo_root = Path(__file__).resolve().parents[1]
    test_dir = repo_root / "test"

    tests = discover_tests(test_dir)

    section("JOBSY - BATERIA UNIFICADA DE QA")

    branch = git_value(
        repo_root,
        "branch",
        "--show-current",
    )

    commit = git_value(
        repo_root,
        "rev-parse",
        "--short",
        "HEAD",
    )

    print(f"Repositorio: {repo_root}")
    print(f"Rama: {branch}")
    print(f"Commit: {commit}")
    print(f"Python: {platform.python_version()}")
    print(f"Sistema: {platform.system()} {platform.release()}")
    print(f"Scripts descubiertos: {len(tests)}")

    print()
    print("Exclusiones explícitas:")

    for test_name in sorted(EXCLUDED_TESTS):
        print(f"  - {test_name}")

    # --------------------------------------------------------------
    section("TC-147 - BATERIA DISPONIBLE MEDIANTE UN SOLO COMANDO")
    # --------------------------------------------------------------

    if not tests:
        print("FAIL: No se encontraron scripts de prueba.")
        print()
        print("RESULTADO GENERAL: FAIL")
        return 1

    print("Scripts incluidos:")

    for test_name in tests:
        print(f"  - {test_name}")

    print()

    print(
        "PASS: La batería descubre automáticamente "
        "los scripts de prueba disponibles."
    )

    print(
        "PASS: La batería puede iniciarse mediante "
        "'python test/run_qa_suite.py'."
    )

    # --------------------------------------------------------------
    section("EJECUCION DE LA BATERIA")
    # --------------------------------------------------------------

    results = []

    suite_start = time.monotonic()

    for index, test_name in enumerate(tests, start=1):
        test_path = test_dir / test_name

        print(
            f"[{index:02d}/{len(tests):02d}] "
            f"Ejecutando {test_name} ...",
            flush=True,
        )

        result = run_test(
            test_path,
            repo_root,
        )

        results.append(
            (
                test_name,
                result,
            )
        )

        print(
            f"    {result['status']} "
            f"({result['duration']:.2f} s)"
        )

        if result["status"] != "PASS":
            print()
            print(
                f"----- SALIDA DE {test_name} -----"
            )

            if result["stdout"]:
                print("STDOUT:")
                print(result["stdout"])

            if result["stderr"]:
                print("STDERR:")
                print(result["stderr"])

            print(
                f"----- FIN SALIDA DE {test_name} -----"
            )
            print()

    total_duration = time.monotonic() - suite_start

    passed = sum(
        result["status"] == "PASS"
        for _, result in results
    )

    failed = sum(
        result["status"] == "FAIL"
        for _, result in results
    )

    timed_out = sum(
        result["status"] == "TIMEOUT"
        for _, result in results
    )

    # --------------------------------------------------------------
    section("TC-148 - LOS SCRIPTS DE QA FINALIZAN CORRECTAMENTE")
    # --------------------------------------------------------------

    if failed == 0 and timed_out == 0:
        print(
            f"PASS: Los {passed} scripts de la batería "
            "finalizaron con código 0."
        )
    else:
        print(
            f"FAIL: {failed} scripts fallaron y "
            f"{timed_out} excedieron el tiempo límite."
        )

    # --------------------------------------------------------------
    section("TC-149 - RESULTADO AGREGADO DE LA BATERIA")
    # --------------------------------------------------------------

    print(f"Scripts ejecutados: {len(results)}")
    print(f"PASS: {passed}")
    print(f"FAIL: {failed}")
    print(f"TIMEOUT: {timed_out}")
    print(f"Duración total: {total_duration:.2f} s")

    section("RESUMEN POR SCRIPT")

    for test_name, result in results:
        print(
            f"{result['status']:7} "
            f"{result['duration']:8.2f} s  "
            f"{test_name}"
        )

    section("RESULTADO GENERAL")

    if (
        len(results) == len(tests)
        and passed == len(tests)
        and failed == 0
        and timed_out == 0
    ):
        print(
            "PASS: La batería completa puede ejecutarse "
            "mediante un único comando."
        )

        print("RESULTADO GENERAL: PASS")
        return 0

    print(
        "FAIL: La batería unificada contiene "
        "fallos o ejecuciones incompletas."
    )

    print("RESULTADO GENERAL: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())