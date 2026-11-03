"""Sistema de bitácora centralizada para eventos operativos y errores (RF-14)."""
import os
import threading
from datetime import datetime, timezone
from pathlib import Path

class DaemonLogger:
    def __init__(self, data_dir: Path | str = None):
        self._lock = threading.Lock()
        self.log_file = None
        
        # Si no se proporciona un directorio, calcula la ruta por defecto (Estándar XDG / ~/.local/state/jobsy)
        if not data_dir:
            base = os.environ.get("XDG_STATE_HOME")
            root = Path(base) if base and Path(base).is_absolute() else Path.home() / ".local/state"
            data_dir = root / "jobsy"
            
        self.setup(data_dir)

    def setup(self, data_dir: Path | str):
        path = Path(data_dir).expanduser().resolve()
        path.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.log_file = path / "jobsy.log"

    def log(self, level: str, message: str, job_id: str | None = None):
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + " UTC"
        jid = job_id if job_id else "-"
        line = f"[{timestamp}] [{level.upper()}] [Job: {jid}] {message}\n"
        
        # Mantener visibilidad en la consola de desarrollo
        print(line.strip())

        if self.log_file:
            with self._lock:
                try:
                    with open(self.log_file, "a", encoding="utf-8") as f:
                        f.write(line)
                except Exception as e:
                    print(f"[Daemon Logger Error] No se pudo escribir en la bitácora: {e}")

# Instancia global lista para usar desde el primer segundo sin configuraciones manuales
logger = DaemonLogger()