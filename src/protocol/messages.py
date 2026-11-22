"""Protocolo de red v1 de Jobsy (RF-21, RNF-14, RNF-24, RNF-32).
Contiene el delimitado de mensajes (cabecera de 4 bytes + JSON UTF-8), la
validación de solicitudes y los sobres de respuesta. No conoce JobManager ni
abre sockets: trabaja sobre cualquier objeto con recv/send/settimeout, de modo
que se puede probar sin red real. Contrato: docs/technical-guide/protocolo-red-v1.md
"""
import json
import re
import struct
import time
import uuid
from dataclasses import dataclass, field

from .validation import validate_command

PROTOCOL_VERSION = 1
HEADER_SIZE = 4
MAX_MESSAGE_BYTES = 1_048_576      # 1 MiB por solicitud o respuesta
MAX_JSON_DEPTH = 16                # contenedores anidados, incluida la raíz
IDLE_TIMEOUT = 30.0                # espera del primer byte entre solicitudes
MESSAGE_TIMEOUT = 5.0              # recibir un mensaje completo (no se renueva)
SEND_TIMEOUT = 5.0                 # enviar un mensaje completo
RESPONSE_TIMEOUT = 30.0            # espera del cliente por una respuesta
_RECV_CHUNK = 65536

ACTIONS = ("run", "list", "status", "cancel", "output", "health")
JOB_STATES = ("QUEUED", "RUNNING", "SUCCEEDED", "FAILED", "CANCELED")

_REQUEST_ID = re.compile(r"[A-Za-z0-9._:-]{1,64}")
_UUID = re.compile(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}")
_PREFIX = re.compile(r"[0-9a-fA-F]{8,32}")
_SURROGATE = re.compile("[\ud800-\udfff]")

_ACTION_FIELDS = {"run": {"command"}, "list": {"status"}, "status": {"job_id"},
                  "cancel": {"job_id"}, "output": {"job_id"}, "health": set()}
_REQUIRED_FIELDS = {"run": {"command"}, "list": set(), "status": {"job_id"},
                    "cancel": {"job_id"}, "output": {"job_id"}, "health": set()}


class ProtocolError(Exception):
    """Error del protocolo con código estable; `close` indica si se cierra la conexión."""

    def __init__(self, code, cause, suggestion, *, operation="desconocida",
                 request_id=None, close=True):
        super().__init__(cause)
        self.code = code
        self.cause = cause
        self.suggestion = suggestion
        self.operation = operation
        self.request_id = request_id
        self.close = close

    def to_response(self):
        return error_response(self.request_id, self.code, self.operation,
                              self.cause, self.suggestion)


class IdleTimeout(Exception):
    """El par no envió nada en el plazo de inactividad: se cierra sin error."""


@dataclass(frozen=True)
class Request:
    request_id: str
    action: str
    params: dict = field(default_factory=dict)


# ---------------------------------------------------------------- sobres
def new_request_id():
    return "cli-" + uuid.uuid4().hex[:12]


def build_request(action, request_id, **fields):
    return {"version": PROTOCOL_VERSION, "request_id": request_id, "action": action, **fields}


def ok_response(request_id, **fields):
    return {"version": PROTOCOL_VERSION, "request_id": request_id, "status": "ok", **fields}


def error_response(request_id, code, operation, cause, suggestion):
    return {"version": PROTOCOL_VERSION, "request_id": request_id, "status": "error",
            "code": code, "operation": operation, "cause": cause, "suggestion": suggestion}


# ---------------------------------------------------------------- envío
def encode_message(obj, too_large_code="RESPONSE_TOO_LARGE"):
    """Serializa a cabecera + JSON. Un mensaje fuera de límite se rechaza, nunca se trunca."""
    try:
        body = json.dumps(obj, ensure_ascii=False, allow_nan=False,
                          separators=(",", ":")).encode("utf-8")
    except (TypeError, ValueError):
        raise ProtocolError("INTERNAL_ERROR", "No se pudo serializar el mensaje.",
                            "Consulte la bitácora del servicio.") from None
    if not 1 <= len(body) <= MAX_MESSAGE_BYTES:
        raise ProtocolError(too_large_code,
                            "El mensaje excede el tamaño máximo permitido (1 MiB).",
                            "Reduzca el tamaño del mensaje o consulte menos datos.",
                            close=False)
    return struct.pack("!I", len(body)) + body


def send_message(stream, obj, timeout=SEND_TIMEOUT, too_large_code="RESPONSE_TOO_LARGE"):
    """Envía un mensaje completo manejando escrituras parciales y un plazo total."""
    view = memoryview(encode_message(obj, too_large_code))
    deadline = time.monotonic() + timeout
    while view:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("Plazo de envío vencido.")
        stream.settimeout(remaining)
        sent = stream.send(view)
        if not sent:
            raise ConnectionError("La conexión se cerró durante el envío.")
        view = view[sent:]


# ------------------------------------------------------------- recepción
class MessageReader:
    """Lee mensajes delimitados de un stream, tolerando lecturas parciales o agrupadas."""

    def __init__(self, stream, *, idle_timeout=IDLE_TIMEOUT,
                 message_timeout=MESSAGE_TIMEOUT, max_bytes=MAX_MESSAGE_BYTES):
        self._stream = stream
        self._buffer = bytearray()
        self._idle_timeout = idle_timeout
        self._message_timeout = message_timeout
        self._max_bytes = max_bytes

    def _fill(self, timeout):
        self._stream.settimeout(timeout)
        chunk = self._stream.recv(_RECV_CHUNK)
        if not chunk:
            return False
        self._buffer.extend(chunk)
        return True

    def _need(self, count, deadline):
        while len(self._buffer) < count:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ProtocolError("READ_TIMEOUT", "Se agotó el plazo para recibir el mensaje.",
                                    "Reintente la operación.")
            try:
                received = self._fill(remaining)
            except TimeoutError:
                raise ProtocolError("READ_TIMEOUT", "Se agotó el plazo para recibir el mensaje.",
                                    "Reintente la operación.") from None
            if not received:
                raise ProtocolError("INCOMPLETE_MESSAGE", "La conexión se cerró a mitad de un mensaje.",
                                    "Reenvíe el mensaje completo.")

    def read(self):
        """Devuelve el cuerpo del siguiente mensaje, o None si el par cerró entre mensajes."""
        if not self._buffer:
            try:
                if not self._fill(self._idle_timeout):
                    return None
            except TimeoutError:
                raise IdleTimeout() from None
        deadline = time.monotonic() + self._message_timeout   # no se renueva por fragmento
        self._need(HEADER_SIZE, deadline)
        (length,) = struct.unpack("!I", bytes(self._buffer[:HEADER_SIZE]))
        if not 1 <= length <= self._max_bytes:
            raise ProtocolError("INVALID_LENGTH", "La longitud declarada del mensaje no es válida.",
                                "Use mensajes de 1 byte a 1 MiB.")
        self._need(HEADER_SIZE + length, deadline)
        body = bytes(self._buffer[HEADER_SIZE:HEADER_SIZE + length])
        del self._buffer[:HEADER_SIZE + length]
        return body


# ------------------------------------------------------------ validación
def _reject_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("clave duplicada")
        result[key] = value
    return result


def _reject_constant(name):
    raise ValueError("constante no permitida")


def _check_depth(text):
    """Cuenta niveles sin recursión; evita que el parser decida el límite."""
    if text.count("[") + text.count("{") <= MAX_JSON_DEPTH:
        return
    depth, in_string, escaped = 0, False, False
    for char in text:
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
        elif char in "[{":
            depth += 1
            if depth > MAX_JSON_DEPTH:
                raise ValueError("profundidad excesiva")
        elif char in "]}":
            depth -= 1


def _has_lone_surrogate(value):
    stack = [value]
    while stack:
        item = stack.pop()
        if isinstance(item, str):
            if _SURROGATE.search(item):
                return True
        elif isinstance(item, dict):
            for key, val in item.items():
                stack.append(key)
                stack.append(val)
        elif isinstance(item, list):
            stack.extend(item)
    return False


def decode_body(body):
    """Cuerpo en bytes -> valor JSON, con las validaciones de RNF-14."""
    if body.startswith(b"\xef\xbb\xbf"):
        raise ProtocolError("INVALID_ENCODING", "El mensaje no debe comenzar con BOM.",
                            "Envíe UTF-8 sin BOM.")
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError:
        raise ProtocolError("INVALID_ENCODING", "El mensaje no es UTF-8 válido.",
                            "Envíe JSON codificado en UTF-8.") from None
    try:
        _check_depth(text)
        value = json.loads(text, object_pairs_hook=_reject_duplicates,
                           parse_constant=_reject_constant)
    except (ValueError, RecursionError):
        raise ProtocolError("INVALID_JSON", "El mensaje no es un JSON válido o supera los límites.",
                            "Envíe un único objeto JSON sin claves duplicadas, NaN ni más de "
                            "16 niveles.") from None
    if _has_lone_surrogate(value):
        raise ProtocolError("INVALID_ENCODING", "El mensaje contiene caracteres Unicode inválidos.",
                            "Envíe texto Unicode válido.")
    return value


def _invalid(cause, suggestion, request_id=None, operation="desconocida", close=True):
    return ProtocolError("INVALID_REQUEST", cause, suggestion, operation=operation,
                         request_id=request_id, close=close)


def validate_request(obj):
    """Valida el sobre y los campos de una solicitud v1 antes de tocar el gestor."""
    if not isinstance(obj, dict):
        raise _invalid("La solicitud debe ser un objeto JSON.",
                       "Envíe un objeto con version, request_id y action.")
    raw_id = obj.get("request_id")
    valid_id = isinstance(raw_id, str) and _REQUEST_ID.fullmatch(raw_id) is not None
    echo = raw_id if valid_id else None

    if "version" not in obj:
        raise _invalid("Falta el campo version.", "Incluya version=1.", echo)
    version = obj["version"]
    if type(version) is not int or version != PROTOCOL_VERSION:
        raise ProtocolError("UNSUPPORTED_VERSION", "La versión del protocolo no es compatible.",
                            "Use la versión 1.", request_id=echo)
    if not valid_id:
        raise _invalid("request_id ausente o inválido.",
                       "Use de 1 a 64 caracteres de [A-Za-z0-9._:-].")

    # Desde aquí el sobre es válido: los errores no obligan a cerrar la conexión.
    action = obj.get("action")
    if not isinstance(action, str):
        raise _invalid("Falta el campo action o no es texto.", "Indique una acción válida.",
                       echo, close=False)
    if action not in ACTIONS:
        raise ProtocolError("UNKNOWN_ACTION", "La acción solicitada no existe.",
                            "Use: " + ", ".join(ACTIONS) + ".", request_id=echo, close=False)

    def fail(cause, suggestion="Revise los campos de la solicitud."):
        return _invalid(cause, suggestion, echo, action, close=False)

    if set(obj) - ({"version", "request_id", "action"} | _ACTION_FIELDS[action]):
        raise fail("La solicitud contiene campos no permitidos para esta acción.")
    missing = _REQUIRED_FIELDS[action] - set(obj)
    if missing:
        raise fail("Faltan campos obligatorios: " + ", ".join(sorted(missing)) + ".")

    params = {}
    if action == "run":
        command = obj["command"]
        try:
            validate_command(command)
        except ValueError as error:
            raise fail(str(error)) from None
        if any("\x00" in arg for arg in command):
            raise fail("Los argumentos no pueden contener caracteres NUL.")
        params["command"] = command
    elif action == "list":
        status = obj.get("status")
        if status is not None and (not isinstance(status, str) or status not in JOB_STATES):
            raise fail("El filtro status no es válido.", "Use null o: " + ", ".join(JOB_STATES) + ".")
        params["status"] = status
    elif action in ("status", "cancel", "output"):
        job_id = obj["job_id"]
        if not isinstance(job_id, str) or not (_UUID.fullmatch(job_id) or _PREFIX.fullmatch(job_id)):
            raise fail("job_id debe ser un UUID o un prefijo hexadecimal de 8 a 32 caracteres.",
                       "Consulte jobsy list --full-id.")
        params["job_id"] = job_id
    return Request(echo, action, params)


def validate_response(obj, expected_request_id):
    """Validación del cliente: versión, request_id y campos obligatorios (RNF-32)."""
    if not isinstance(obj, dict):
        raise ProtocolError("INVALID_RESPONSE", "La respuesta del servicio no es un objeto JSON.",
                            "Verifique que el servidor use el mismo protocolo.")
    version = obj.get("version")
    if type(version) is not int or version != PROTOCOL_VERSION:
        raise ProtocolError("UNSUPPORTED_VERSION", "El servidor respondió con otra versión del protocolo.",
                            "Actualice el cliente o el servidor.")
    status = obj.get("status")
    if status not in ("ok", "error"):
        raise ProtocolError("INVALID_RESPONSE", "La respuesta no indica un estado válido.",
                            "Verifique la versión del servidor.")
    rid = obj.get("request_id")
    if not (rid == expected_request_id or (status == "error" and rid is None)):
        raise ProtocolError("INVALID_RESPONSE", "La respuesta no corresponde a la solicitud enviada.",
                            "Reintente la operación.")
    if status == "error" and not all(isinstance(obj.get(k), str)
                                     for k in ("code", "operation", "cause", "suggestion")):
        raise ProtocolError("INVALID_RESPONSE", "La respuesta de error está incompleta.",
                            "Verifique la versión del servidor.")
    return obj