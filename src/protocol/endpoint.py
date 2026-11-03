"""Shared validation for filesystem-based Linux Unix socket endpoints."""
import os
from pathlib import Path

DEFAULT_SOCKET_PATH = "/tmp/jobsy.sock"
SOCKET_PATH_ENV = "JOBSY_SOCKET_PATH"
MAX_SOCKET_PATH_BYTES = 107  # Linux sockaddr_un.sun_path, excluding trailing NUL.


def resolve_socket_path(path):
    """Validate without creating directories or resolving the final component."""
    path = os.fspath(path)
    if not isinstance(path, str) or not path.strip() or "\0" in path:
        raise ValueError("La ruta del socket debe ser texto no vacío y sin NUL.")
    path = os.path.expanduser(path)
    if not os.path.isabs(path) or path.rsplit("/", 1)[-1] in {"", ".", ".."}:
        raise ValueError("La ruta del socket debe ser absoluta y nombrar un archivo.")
    candidate = Path(path)
    if candidate.name in {"", ".", ".."}:
        raise ValueError("La ruta del socket debe nombrar un archivo.")
    try:
        parent = candidate.parent.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise ValueError("El directorio padre del socket debe existir y ser accesible.") from error
    if not parent.is_dir():
        raise ValueError("El padre del socket debe ser un directorio.")
    resolved = str(parent / candidate.name)
    if len(os.fsencode(resolved)) > MAX_SOCKET_PATH_BYTES:
        raise ValueError("La ruta del socket excede 107 bytes en Linux.")
    if os.path.islink(resolved):
        raise ValueError("La ruta final del socket no puede ser un enlace simbólico.")
    return resolved


def client_socket_path():
    """Read the environment per request; an empty override is an error."""
    return resolve_socket_path(os.environ.get(SOCKET_PATH_ENV, DEFAULT_SOCKET_PATH))
