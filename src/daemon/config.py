"""Validated daemon configuration (RF-05)."""
import argparse
import os
from pathlib import Path
from dataclasses import dataclass
from src.protocol.endpoint import DEFAULT_SOCKET_PATH, resolve_socket_path


@dataclass(frozen=True)
class DaemonConfig:
    max_running: int = 3
    queue_capacity: int = 100
    data_dir: str | None = None
    socket_path: str = DEFAULT_SOCKET_PATH
    cancel_grace_seconds: float = 2.0

    def data_directory(self):
        if self.data_dir is not None:
            return Path(self.data_dir).expanduser().resolve()
        base = os.environ.get("XDG_STATE_HOME")
        root = Path(base) if base and Path(base).is_absolute() else Path.home() / ".local/state"
        return root / "jobsy"

    def __post_init__(self):
        object.__setattr__(self, "socket_path", resolve_socket_path(self.socket_path))
        if self.data_dir is not None and (
                not isinstance(self.data_dir, str) or not self.data_dir.strip()):
            raise ValueError("data_dir debe ser una ruta no vacía.")
        for name, minimum in (("max_running", 1), ("queue_capacity", 0)):
            value = getattr(self, name)
            if type(value) is not int or value < minimum:
                raise ValueError(f"{name} debe ser un entero >= {minimum}.")
                grace = self.cancel_grace_seconds
                if isinstance(grace, bool) or not isinstance(grace, (int, float)) or not 0 < grace <= 60:
                    raise ValueError("cancel_grace_seconds debe ser un número mayor que 0 y menor o igual a 60.")


def parse_config(argv=None):
    parser = argparse.ArgumentParser(prog="jobsy-daemon")
    parser.add_argument("--max-running", type=int, default=3)
    parser.add_argument("--queue-capacity", type=int, default=100)
    parser.add_argument("--data-dir", help="Directorio persistente (predeterminado: XDG_STATE_HOME/jobsy)")
    parser.add_argument("--socket-path", default=DEFAULT_SOCKET_PATH,
                        help=f"Ruta absoluta del socket Unix (predeterminado: {DEFAULT_SOCKET_PATH})")
    parser.add_argument("--cancel-grace", type=float, default=2.0,
                        help="Segundos entre SIGTERM y SIGKILL al cancelar un trabajo (predeterminado: 2)")
    args = parser.parse_args(argv)
    try:
        return DaemonConfig(args.max_running, args.queue_capacity, args.data_dir, args.socket_path, args.cancel_grace)
    except ValueError as error:
        parser.error(str(error))
