# server.py
# Servicio en segundo plano que mantiene el sistema en ejecución,
# atiende peticiones via Socket IPC y gestiona el apagado controlado.
import os
import sys
import json
import socket
import signal


#from aiohttp import request

from src.daemon.job_manager import JobManager
from src.daemon.executor import Executor
from src.daemon.config import parse_config
from src.daemon.persistence import PersistenceRuntime
from src.daemon.scheduler import QueueFullError
from src.protocol.endpoint import resolve_socket_path
from src.daemon.logger import logger

def diagnose(job):
    """Texto de diagnóstico derivado del estado y exit_code; None si no aplica """
    code = job.exit_code
    if job.status == "CANCELED":
        return "cancelado por solicitud del usuario"
    if code is None or code == 0:
        return None
    if code < 0:
        try:
            name = signal.Signals(-code).name
        except ValueError:
            name = f"señal {-code}"
        return f"terminado inesperadamente por {name}"
    return f"terminó con código de salida {code}"

class DaemonServer:
    def __init__(self, manager: JobManager = None, executor: Executor = None,
                 config=None, socket_path=None):
        self.manager = manager if manager is not None else JobManager(config)
        self.executor = executor if executor is not None else Executor(self.manager)
        if self.manager.executor is None:
            self.manager.attach_executor(self.executor)
        if self.manager.executor is not self.executor:
            raise ValueError("El servidor y el gestor deben compartir ejecutor.")
        self.socket_path = resolve_socket_path(
            self.manager.config.socket_path if socket_path is None else socket_path)
        self._owns_socket = False
        self.is_running = True
        self.server_socket = None
        self.persistence = None
        self._socket_identity = None

        # Registra manejadores de señales para un cierre controlado
        signal.signal(signal.SIGINT, self._handle_shutdown_signal)
        signal.signal(signal.SIGTERM, self._handle_shutdown_signal)

    def _handle_shutdown_signal(self, signum, frame):
        logger.log("WARNING", "Señal de apagado recibida (SIGINT/SIGTERM).")
        self.is_running = False

    def start(self):
        # Never unlink a socket that this server does not own.
        if os.path.lexists(self.socket_path):
            raise FileExistsError("El socket ya existe; compruebe si hay un daemon activo.")

        self.persistence = PersistenceRuntime(self.manager.config.data_directory()).open()
        try:
            self.manager.enable_persistence(self.persistence)
            self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.server_socket.bind(self.socket_path)
            self._owns_socket = True
            info = os.lstat(self.socket_path)
            self._socket_identity = (info.st_dev, info.st_ino)
            self.server_socket.listen(5)
            self.server_socket.settimeout(0.2)
            logger.log("INFO", f"Servidor Jobsy activo escuchando en {self.socket_path}")
            for record in self.persistence.records:
                reason = record["execution"]["recovery_reason"]
                if reason:
                    logger.log("WARNING", f"Historial recuperado: {reason}", job_id=record['id'])
            while self.is_running:
                try:
                    conn, _ = self.server_socket.accept()
                    conn.settimeout(1.0)
                    self._handle_client(conn)
                except Exception:
                    if not self.is_running:
                        break
        finally:
            self.stop()

    def _handle_client(self, conn):
        with conn:
            action = None
            job_id = None
            response = {}
            operation_status = "sin_efecto"
            
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
                    job_id = job.id
                    operation_status = "aceptada"
                    logger.log("INFO", f"Solicitud 'run' procesada con éxito para comando: {' '.join(command)}", job_id=job.id)
                    response = {"status": "ok", "job_id": job.id}

                elif action == "list":
                    status_filter = request.get("status")
                    jobs = self.manager.list_jobs(status=status_filter)
                    operation_status = "sin_efecto"
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
                    operation_status = "sin_efecto"
                    
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
                            "exit_code": job.exit_code,
                            "diagnostic": diagnose(job)
                        }
                    }

                elif action == "cancel":
                    job_id = request.get("job_id")
                    job = self.manager.cancel_job(job_id)
                    operation_status = "aceptada"
                    logger.log("INFO", f"Solicitud 'cancel' procesada", job_id=job.id)
                    response = {
                        "status": "ok",
                        "job_id": job.id,
                        "job_status": job.status
                    }
                
                elif action == "output":
                    job_id = request.get("job_id")
                    job = self.manager.snapshot(request.get("job_id"))
                    operation_status = "sin_efecto"
                    response = {
                        "status": "ok",
                        "job_id": job.id,
                        "job_status": job.status,
                        "stdout": job.stdout,
                        "stderr": job.stderr,
                    }

                else:
                    operation_status = "rechazada"
                    logger.log("WARNING", f"Acción IPC no válida recibida: {action}")
                    response = {"status": "error", "message": "Acción no válida"}

            except QueueFullError as qfe:
                operation_status = "rechazada"
                # RF-23: Rechazo explícito por exceder límites configurados de capacidad
                logger.log("WARNING", f"Solicitud 'run' rechazada por límite de capacidad: {qfe}")
                response = {"status": "error", "message": str(qfe)}
            except ValueError as ve:
                operation_status = "rechazada"
                logger.log("ERROR", f"Error de validación en petición IPC: {ve}")
                response = {"status": "error", "message": str(ve)}
            except Exception as e:
                operation_status = "rechazada"
                logger.log("ERROR", f"Excepción no controlada procesando cliente: {e}")
                response = {"status": "error", "message": str(e)}

            # RF-28: Intento de envío de respuesta con captura explícita de desconexión del cliente
            try:
                conn.sendall(json.dumps(response).encode("utf-8"))
            except (BrokenPipeError, ConnectionResetError, socket.error) as conn_err:
                logger.log(
                    "WARNING",
                    f"Cliente desconectado prematuramente durante la solicitud '{action}'. "
                    f"Estado de la operación: {operation_status.upper()} (socket cerrado: {conn_err})",
                    job_id=job_id
                )

    def stop(self):
        self.is_running = False
        logger.log("INFO", "Deteniendo recepción de trabajos y finalizando procesos activos...")
        
        if self.server_socket:
            self.server_socket.close()

        clean = False
        try:
            self.manager.shutdown(timeout=5.0)
            clean = True
        finally:
            try:
                if self.persistence is not None:
                    self.persistence.close(clean=clean)
                    self.persistence = None
            finally:
                if self._owns_socket:
                    try:
                        info = os.lstat(self.socket_path)
                    except FileNotFoundError:
                        info = None
                    if info is not None and (info.st_dev, info.st_ino) == self._socket_identity:
                        os.remove(self.socket_path)
                    self._owns_socket = False
        logger.log("INFO", "Servicio detenido completamente.")

def main(argv=None):
    """Start the daemon with its existing signal handlers and lifecycle."""
    config = parse_config(argv)
    server = DaemonServer(config=config)
    server.start()


if __name__ == "__main__":
    main()
