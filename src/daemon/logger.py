"""Sistema de bitácora centralizada para eventos operativos y errores (RF-14, RNF-15)."""
import os
import re
import threading
from datetime import datetime, timezone
from pathlib import Path

# RNF-15: palabras que delatan un secreto en un mensaje de bitácora.
_SECRET_WORDS = (r"(?:password|passwd|pwd|passphrase|secret|token|"
                 r"api[_-]?key|access[_-]?key|authorization|credential)")

# Forma clave=valor o clave: valor (por ejemplo DB_PASSWORD=abc, "token: xyz").
_KEY_VALUE = re.compile(
    rf"(?i)\b([\w.-]*{_SECRET_WORDS}[\w.-]*)\s*[=:]\s*(\"[^\"]*\"|'[^']*'|\S+)")
# Forma de opción de línea de comandos: --password abc, --api-key abc.
_FLAG_VALUE = re.compile(
    rf"(?i)(--?[\w-]*{_SECRET_WORDS}[\w-]*)\s+(\"[^\"]*\"|'[^']*'|\S+)")

REDACTED = "[REDACTADO]"


def sanitize(message: str) -> str:
    """Oculta valores que parecen secretos. Es una red de seguridad, no la defensa principal."""
    message = _KEY_VALUE.sub(lambda m: f"{m.group(1)}={REDACTED}", str(message))
    return _FLAG_VALUE.sub(lambda m: f"{m.group(1)} {REDACTED}", message)


def describe_command(command) -> str:
    """Describe un comando sin sus argumentos: solo el programa y cuántos argumentos tiene."""
    if not command:
        return "<vacío>"
    program = os.path.basename(str(command[0])) or str(command[0])
    count = len(command) - 1
    return f"{program} ({count} argumento{'s' if count != 1 else ''}, no registrados)"


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
        log_file = path / "jobsy.log"
        # RNF-15: la bitácora solo debe ser legible por su dueño, incluso si ya existía.
        try:
            if log_file.exists():
                os.chmod(log_file, 0o600)
        except OSError:
            pass
        with self._lock:
            self.log_file = log_file

    def log(self, level: str, message: str, job_id: str | None = None):
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + " UTC"
        jid = job_id if job_id else "-"
        line = f"[{timestamp}] [{level.upper()}] [Job: {jid}] {sanitize(message)}\n"

        # Mantener visibilidad en la consola de desarrollo
        print(line.strip())

        with self._lock:
            if self.log_file:
                try:
                    descriptor = os.open(self.log_file,
                                         os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
                    with os.fdopen(descriptor, "a", encoding="utf-8") as f:
                        f.write(line)
                except Exception as e:
                    print(f"[Daemon Logger Error] No se pudo escribir en la bitácora: {sanitize(e)}")


# Instancia global lista para usar desde el primer segundo sin configuraciones manuales
logger = DaemonLogger()