"""Validated daemon configuration (RF-05, RF-18, RNF-26)."""
import argparse
import ipaddress
import os
from pathlib import Path
from dataclasses import dataclass
from src.protocol.endpoint import DEFAULT_SOCKET_PATH, resolve_socket_path


def _is_private(ip):
    return ip.is_private or ip.is_loopback or ip.is_link_local


@dataclass(frozen=True)
class DaemonConfig:
    max_running: int = 3
    queue_capacity: int = 100
    data_dir: str | None = None
    socket_path: str = DEFAULT_SOCKET_PATH
    cancel_grace_seconds: float = 2.0
    # Acceso remoto (RF-18, RNF-26). Apagado por defecto: sin listen_host no se abre ningún puerto.
    listen_host: str | None = None
    listen_port: int = 8765
    allow_cidrs: tuple = ()
    max_remote_connections: int = 8
    max_connections_per_ip: int = 2

    def remote_enabled(self):
        return self.listen_host is not None

    def allowed_networks(self):
        return tuple(ipaddress.ip_network(c, strict=False) for c in self.allow_cidrs)

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
        self._validate_remote()

    def _validate_remote(self):
        for name in ("max_remote_connections", "max_connections_per_ip"):
            value = getattr(self, name)
            if type(value) is not int or not 1 <= value <= 64:
                raise ValueError(f"{name} debe ser un entero entre 1 y 64.")
        if self.listen_host is None:
            return
        try:
            ip = ipaddress.ip_address(self.listen_host)
        except (ValueError, TypeError):
            raise ValueError("--listen-host debe ser una dirección IP concreta (no un nombre).")
        if ip.is_unspecified:
            raise ValueError("--listen-host no puede ser 0.0.0.0 ni :: (expondría todas las interfaces).")
        if not _is_private(ip):
            raise ValueError("--listen-host debe ser una dirección privada o de loopback (RNF-26).")
        if type(self.listen_port) is not int or not 1 <= self.listen_port <= 65535:
            raise ValueError("--listen-port debe estar entre 1 y 65535.")
        if not self.allow_cidrs:
            raise ValueError("Con --listen-host se requiere al menos un --allow-cidr (redes permitidas).")
        object.__setattr__(self, "allow_cidrs", tuple(self.allow_cidrs))
        for cidr in self.allow_cidrs:
            try:
                net = ipaddress.ip_network(cidr, strict=False)
            except ValueError:
                raise ValueError(f"--allow-cidr inválido: {cidr!r}.")
            if net.prefixlen == 0 or not _is_private(net):
                raise ValueError(f"--allow-cidr {cidr} no es una red privada (RNF-26: sin exposición a Internet).")


def parse_config(argv=None):
    parser = argparse.ArgumentParser(prog="jobsy-daemon")
    parser.add_argument("--max-running", type=int, default=3)
    parser.add_argument("--queue-capacity", type=int, default=100)
    parser.add_argument("--data-dir", help="Directorio persistente (predeterminado: XDG_STATE_HOME/jobsy)")
    parser.add_argument("--socket-path", default=DEFAULT_SOCKET_PATH,
                        help=f"Ruta absoluta del socket Unix (predeterminado: {DEFAULT_SOCKET_PATH})")
    parser.add_argument("--cancel-grace", type=float, default=2.0,
                        help="Segundos entre SIGTERM y SIGKILL al cancelar un trabajo (predeterminado: 2)")
    parser.add_argument("--listen-host", help="IP privada donde escuchar acceso remoto (apagado si se omite)")
    parser.add_argument("--listen-port", type=int, default=8765, help="Puerto TCP remoto (predeterminado: 8765)")
    parser.add_argument("--allow-cidr", action="append", default=[], metavar="CIDR",
                        help="Red permitida, p. ej. 192.168.1.0/24 (repetible; obligatoria con --listen-host)")
    parser.add_argument("--max-remote-connections", type=int, default=8)
    parser.add_argument("--max-connections-per-ip", type=int, default=2)
    args = parser.parse_args(argv)
    try:
        return DaemonConfig(args.max_running, args.queue_capacity, args.data_dir, args.socket_path,
                            args.cancel_grace, args.listen_host, args.listen_port, tuple(args.allow_cidr),
                            args.max_remote_connections, args.max_connections_per_ip)
    except ValueError as error:
        parser.error(str(error))