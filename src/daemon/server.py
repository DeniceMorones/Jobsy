#server.py
#servicio en segundo plano que mantiene el sistema en ejecución 
# y gestiona el apagado controlado para proteger los procesos activos
import signal
import sys

from src.daemon.job_manager import JobManager

class DaemonServer:
    def __init__(self, manager: JobManager, host: str = "127.0.0.1", port: int = 9999):
        self.manager = manager
        self.host = host
        self.port = port
        self.is_running = True

        #registra manejadores de señales para un cierre controlado
        signal.signal(signal.SIGINT, self._handle_shutdown_signal)
        signal.signal(signal.SIGTERM, self._handle_shutdown_signal)

    def _handle_shutdown_signal(self, signum, frame):
        print("\n[Daemon] Señal de apagado recibida...")
        self.stop()

    def stop(self):
        self.is_running = False

        print("[Daemon] Deteniendo recepción de trabajos y finalizando procesos activos...")

        self.manager.shutdown(timeout=5.0)

        print("[Daemon] Servicio detenido.")
        sys.exit(0)

