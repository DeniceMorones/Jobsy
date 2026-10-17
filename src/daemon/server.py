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
from src.daemon.config import parse_config

SOCKET_PATH = "/tmp/jobsy.sock"

class DaemonServer:
    def __init__(self, manager: JobManager = None, executor: Executor = None,
                 config=None, socket_path=None):
        self.manager = manager if manager is not None else JobManager(config)
        self.executor = executor if executor is not None else Executor(self.manager)
        if self.manager.executor is None:
            self.manager.attach_executor(self.executor)
        if self.manager.executor is not self.executor:
            raise ValueError("El servidor y el gestor deben compartir ejecutor.")
        self.socket_path = SOCKET_PATH if socket_path is None else socket_path
        self._owns_socket = False
        self.is_running = True
        self.server_socket = None

        # Registra manejadores de señales para un cierre controlado
        signal.signal(signal.SIGINT, self._handle_shutdown_signal)
        signal.signal(signal.SIGTERM, self._handle_shutdown_signal)

    def _handle_shutdown_signal(self, signum, frame):
        print("\n[Daemon] Señal de apagado recibida...")
        self.is_running = False

    def start(self):
        # Never unlink a socket that this server does not own.
        if os.path.exists(self.socket_path):
            raise FileExistsError("El socket ya existe; compruebe si hay un daemon activo.")

        self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_socket.bind(self.socket_path)
        self._owns_socket = True
        self.server_socket.listen(5)
        self.server_socket.settimeout(0.2)

        print(f"[Daemon] Servidor Jobsy activo escuchando en {self.socket_path}...")

        while self.is_running:
            try:
                conn, _ = self.server_socket.accept()
                conn.settimeout(1.0)
                self._handle_client(conn)
            except Exception:
                if not self.is_running:
                    break
        self.stop()

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
                    job = self.manager.submit_job(command)
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
                    job = self.manager.snapshot(job_id)
                    
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

        if self._owns_socket and os.path.exists(self.socket_path):
            os.remove(self.socket_path)
            self._owns_socket = False

        print("[Daemon] Servicio detenido.")
        sys.exit(0)

def main(argv=None):
    """Start the daemon with its existing signal handlers and lifecycle."""
    config = parse_config(argv)
    server = DaemonServer(config=config)
    server.start()


if __name__ == "__main__":
    main()
