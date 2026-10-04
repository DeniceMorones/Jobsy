#!/usr/bin/env python3
"""
Jobsy Local MVP - Script de Verificación en Python
Valida: Envió, ID Único, Estado, Salida, Listado, Cancelación y Robustez
"""

import os
import sys
import time
import socket
import subprocess

# Colores para la terminal
GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"

SOCKET_PATH = "/tmp/jobsy.sock"
PYTHON_BIN = sys.executable
CLI_PATH = "src/client/cli.py"
SERVER_PATH = "src/daemon/server.py"

PASSED = 0
FAILED = 0


def log_info(msg: str):
    print(f"{BLUE}[INFO]{NC} {msg}")


def log_success(msg: str):
    global PASSED
    print(f"{GREEN}[OK]{NC} {msg}")
    PASSED += 1


def log_fail(msg: str):
    global FAILED
    print(f"{RED}[FAIL]{NC} {msg}")
    FAILED += 1


def log_section(title: str):
    print(f"\n{YELLOW}=== {title} ==={NC}")


def run_cli(*args) -> tuple[int, str, str]:
    """Ejecuta el CLI con los argumentos pasados y retorna (returncode, stdout, stderr)."""
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    cmd = [PYTHON_BIN, CLI_PATH] + list(args)
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def cleanup(server_proc: subprocess.Popen | None):
    """Limpia el proceso del servidor y borra el socket UNIX."""
    log_info("Limpiando procesos y sockets de prueba...")
    if server_proc and server_proc.poll() is None:
        server_proc.terminate()
        try:
            server_proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            server_proc.kill()
    if os.path.exists(SOCKET_PATH):
        try:
            os.remove(SOCKET_PATH)
        except OSError:
            pass


def main():
    server_proc = None

    if not os.path.exists(CLI_PATH):
        log_fail(f"No se encontró el archivo del CLI en '{CLI_PATH}'")
        sys.exit(1)

    if not os.path.exists(SERVER_PATH):
        log_fail(f"No se encontró el archivo del servidor en '{SERVER_PATH}'")
        sys.exit(1)

    try:
        # ----------------------------------------------------------------------
        # 1. Precondiciones y Arranque del Servidor
        # ----------------------------------------------------------------------
        log_section("1. PREPARACIÓN DEL ENTORNO")
        cleanup(None)

        log_info(f"Iniciando Jobsy Daemon ({SERVER_PATH})...")
        
        # Inyectar el directorio actual en PYTHONPATH para evitar ModuleNotFoundError
        env = os.environ.copy()
        env["PYTHONPATH"] = os.getcwd()

        server_proc = subprocess.Popen([PYTHON_BIN, SERVER_PATH], env=env)
        time.sleep(1)  # Esperar a que el servidor cree el socket

        if not os.path.exists(SOCKET_PATH):
            log_fail(f"El socket UNIX '{SOCKET_PATH}' no fue creado por el servidor.")
            sys.exit(1)
        else:
            log_success(f"Servidor activo escuchando en '{SOCKET_PATH}' (PID: {server_proc.pid})")

        # ----------------------------------------------------------------------
        # 2. Requisito: Enviar Trabajo, ID Único y Ejecución Separada
        # ----------------------------------------------------------------------
        log_section("2. PRUEBA: RUN & ID ÚNICO (Comando exitoso)")
        code, out, err = run_cli("run", "echo 'Hello Jobsy'")

        job_id_1 = None
        if code == 0 and "ID:" in out:
            job_id_1 = out.split("ID:")[-1].strip()
            log_success(f"Trabajo enviado exitosamente. ID asignado: {job_id_1}")
        else:
            log_fail(f"No se pudo obtener el ID del trabajo. Salida: {out} | Error: {err}")

        # ----------------------------------------------------------------------
        # 3. Requisito: Consultar Estado y Código de Salida (SUCCEEDED / Exit Code 0)
        # ----------------------------------------------------------------------
        log_section("3. PRUEBA: STATUS & EXIT CODE (Exitoso)")
        time.sleep(1)  # Esperar que finalice echo

        if job_id_1:
            code, out, err = run_cli("status", job_id_1)
            print(out)
            if "Estado: SUCCEEDED" in out and "Código de salida: 0" in out:
                log_success("Estado SUCCEEDED y Código de salida 0 verificados correctamente.")
            else:
                log_fail("El estado o código de salida no corresponde a un trabajo exitoso.")

        # ----------------------------------------------------------------------
        # 4. Requisito: Código de salida en fallos (FAILED / Exit Code != 0)
        # ----------------------------------------------------------------------
        log_section("4. PRUEBA: STATUS & EXIT CODE (Trabajo Fallido)")
        code, out, err = run_cli("run", "ls /directorio_inexistente_123")
        
        job_id_fail = None
        if code == 0 and "ID:" in out:
            job_id_fail = out.split("ID:")[-1].strip()

        time.sleep(1)

        if job_id_fail:
            code, out, err = run_cli("status", job_id_fail)
            print(out)
            if "Estado: FAILED" in out and "Código de salida: 0" not in out:
                log_success("Trabajo fallido detectado correctamente (Estado FAILED con exit code != 0).")
            else:
                log_fail("No se reportó correctamente el estado FAILED o el código de salida.")

        # ----------------------------------------------------------------------
        # 5. Requisito: Listar Trabajos
        # ----------------------------------------------------------------------
        log_section("5. PRUEBA: LISTAR TRABAJOS")
        code, out, err = run_cli("list")
        print(out)

        if job_id_1 and job_id_fail and (job_id_1 in out) and (job_id_fail in out):
            log_success("El listado de trabajos contiene los IDs generados previamente.")
        else:
            log_fail("El listado no mostró los trabajos esperados.")

        # ----------------------------------------------------------------------
        # 6. Requisito: Cancelar Trabajo (CANCELED)
        # ----------------------------------------------------------------------
        log_section("6. PRUEBA: CANCELAR TRABAJO")
        code, out, err = run_cli("run", "sleep 10")
        
        job_id_long = None
        if code == 0 and "ID:" in out:
            job_id_long = out.split("ID:")[-1].strip()

        if job_id_long:
            code_cancel, out_cancel, err_cancel = run_cli("cancel", job_id_long)
            print(out_cancel)

            time.sleep(1)
            code_st, out_st, err_st = run_cli("status", job_id_long)
            print(out_st)

            if "Estado: CANCELED" in out_st:
                log_success("El trabajo fue cancelado con éxito (Estado: CANCELED).")
            else:
                log_fail(f"Falló la cancelación del trabajo {job_id_long}.")

        # ----------------------------------------------------------------------
        # 7. Requisito: Manejo de Comandos Inválidos sin Caer el Servicio
        # ----------------------------------------------------------------------
        log_section("7. PRUEBA: ROBUSTEZ Y MANEJO DE ERRORES")
        code, out, err = run_cli("run", "comando_que_no_existe_xyz")

        time.sleep(1)

        # Verificar si el daemon sigue respondiendo a 'list'
        code_list, out_list, _ = run_cli("list")
        if code_list == 0:
            log_success("El servidor se mantuvo estable tras la falla de ejecución de un comando inexistente.")
        else:
            log_fail("El servidor dejó de responder tras la ejecución del comando no válido.")

    finally:
        cleanup(server_proc)

if __name__ == "__main__":
    main()