# server.py
# Servicio en segundo plano que mantiene el sistema en ejecución,
# atiende peticiones via Socket IPC y gestiona el apagado controlado.
import os
import sys
import json
import socket
import signal

from src.daemon.job_manager import JobManager
from src.daemon.executor import Executor

SOCKET_PATH = "/tmp/jobsy.sock"

class DaemonServer:
    def __init__(self, manager: JobManager = None, executor: Executor = None):
        self.manager = manager if manager is not None else JobManager()
        self.executor = executor if executor is not None else Executor(self.manager)
        self.is_running = True
        self.server_socket = None

        # Registra manejadores de señales para un cierre controlado
        signal.signal(signal.SIGINT, self._handle_shutdown_signal)
        signal.signal(signal.SIGTERM, self._handle_shutdown_signal)

    def _handle_shutdown_signal(self, signum, frame):
        print("\n[Daemon] Señal de apagado recibida...")
        self.stop()

    def start(self):
        # Eliminar el archivo del socket si existía previamente
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)

        self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_socket.bind(SOCKET_PATH)
        self.server_socket.listen(5)

        print(f"[Daemon] Servidor Jobsy activo escuchando en {SOCKET_PATH}...")

        while self.is_running:
            try:
                conn, _ = self.server_socket.accept()
                self._handle_client(conn)
            except Exception:
                if not self.is_running:
                    break

    def _handle_client(self, conn):
        with conn:
            try:
                data = conn.recv(4096)
                if not data:
                    return

                request = json.loads(data.decode("utf-8"))
                action = request.get("action")
                response = {}

                if action == "run":
                    command = request.get("command")
                    job = self.manager.create_job(command)
                    self.executor.execute(job)
                    response = {"status": "ok", "job_id": job.id}

                elif action == "list":
                    status_filter = request.get("status")
                    jobs = self.manager.list_jobs(status=status_filter)
                    response = {
                        "status": "ok",
                        "jobs": [
                            {
                                "id": j.id,
                                "status": j.status,
                                "command": j.command
                            }
                            for j in jobs
                        ]
                    }

                elif action == "status":
                    job_id = request.get("job_id")
                    job = self.manager.get_job(job_id)
                    
                    def format_dt(dt):
                        return dt.strftime("%Y-%m-%d %H:%M:%S UTC") if dt else "-"

                    response = {
                        "status": "ok",
                        "job": {
                            "id": job.id,
                            "status": job.status,
                            "command": job.command,
                            "received_at": format_dt(job.received_at),
                            "started_at": format_dt(job.started_at),
                            "finished_at": format_dt(job.finished_at),
                            "exit_code": job.exit_code
                        }
                    }

                elif action == "cancel":
                    job_id = request.get("job_id")
                    job = self.manager.cancel_job(job_id)
                    response = {
                        "status": "ok",
                        "job_id": job.id,
                        "job_status": job.status
                    }

                else:
                    response = {"status": "error", "message": "Acción no válida"}

            except ValueError as ve:
                response = {"status": "error", "message": str(ve)}
            except Exception as e:
                response = {"status": "error", "message": str(e)}

            conn.sendall(json.dumps(response).encode("utf-8"))

    def stop(self):
        self.is_running = False
        print("[Daemon] Deteniendo recepción de trabajos y finalizando procesos activos...")
        
        if self.server_socket:
            self.server_socket.close()

        self.manager.shutdown(timeout=5.0)

        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)

        print("[Daemon] Servicio detenido.")
        sys.exit(0)

if __name__ == "__main__":
    server = DaemonServer()
    server.start()