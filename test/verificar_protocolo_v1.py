import json, socket, struct, threading, time, sys
sys.path.insert(0, ".")
from src.protocol.messages import *
from src.protocol import messages as M

ok = fail = 0
def check(name, cond):
    global ok, fail
    if cond: ok += 1
    else: fail += 1; print("FALLA:", name)

def frame(obj_or_bytes):
    body = obj_or_bytes if isinstance(obj_or_bytes, bytes) else json.dumps(obj_or_bytes).encode()
    return struct.pack("!I", len(body)) + body

class Fake:
    """Stream inyectable: entrega los trozos dados, uno por recv."""
    def __init__(self, chunks, then_timeout=False):
        self.chunks = list(chunks); self.then_timeout = then_timeout; self.sent = []; self.max_send = None
    def settimeout(self, t): pass
    def recv(self, n):
        if self.chunks: return self.chunks.pop(0)
        if self.then_timeout: raise TimeoutError()
        return b""
    def send(self, data):
        n = len(data) if self.max_send is None else min(self.max_send, len(data))
        self.sent.append(bytes(data[:n])); return n

def err(fn):
    try: fn(); return None
    except ProtocolError as e: return e.code
    except IdleTimeout: return "IDLE"

# --- RNF-24: fragmentación
msg = frame({"a": "ñandú 😀"})
r = MessageReader(Fake([bytes([b]) for b in msg]))                      # byte a byte (parte UTF-8)
check("byte a byte", json.loads(r.read())["a"] == "ñandú 😀")
r = MessageReader(Fake([msg + frame({"b": 2})]))                          # dos tramas en una lectura
check("dos tramas 1", json.loads(r.read())["a"].startswith("ñ")); check("dos tramas 2", json.loads(r.read()) == {"b": 2})
check("EOF limpio entre mensajes", r.read() is None)
r = MessageReader(Fake([msg[:2], msg[2:9], msg[9:]]))
check("trozos irregulares", r.read() is not None)
# --- RNF-14: longitudes
check("longitud 0", err(lambda: MessageReader(Fake([struct.pack("!I", 0)])).read()) == "INVALID_LENGTH")
check("longitud limite+1 sin leer cuerpo", err(lambda: MessageReader(Fake([struct.pack("!I", MAX_MESSAGE_BYTES + 1)])).read()) == "INVALID_LENGTH")
check("longitud 1", MessageReader(Fake([frame(b"7")])).read() == b"7")
big = b'"' + b"x" * (MAX_MESSAGE_BYTES - 2) + b'"'
check("longitud limite exacto", len(MessageReader(Fake([frame(big)])).read()) == MAX_MESSAGE_BYTES)
check("cuerpo menor que longitud + EOF", err(lambda: MessageReader(Fake([struct.pack("!I", 10) + b"abc"])).read()) == "INCOMPLETE_MESSAGE")
check("cabecera parcial + EOF", err(lambda: MessageReader(Fake([b"\x00\x00"])).read()) == "INCOMPLETE_MESSAGE")
check("timeout a mitad", err(lambda: MessageReader(Fake([struct.pack("!I", 10) + b"abc"], then_timeout=True)).read()) == "READ_TIMEOUT")
check("inactividad", err(lambda: MessageReader(Fake([], then_timeout=True)).read()) == "IDLE")
# plazo no se renueva con tráfico lento (socket real)
a, b = socket.socketpair()
def drip():
    data = frame({"x": "y" * 20})
    for byte in data:
        try: b.send(bytes([byte])); time.sleep(0.06)
        except OSError: return
t = threading.Thread(target=drip, daemon=True); t.start()
t0 = time.monotonic()
check("plazo absoluto con goteo", err(lambda: MessageReader(a, message_timeout=0.3).read()) == "READ_TIMEOUT")
check("goteo cortado cerca del plazo", time.monotonic() - t0 < 0.6)
a.close(); b.close()
# --- envío parcial y tamaño
f = Fake([]); f.max_send = 3
send_message(f, {"k": "valor largo para forzar varios envios"})
data = b"".join(f.sent); check("envío parcial", struct.unpack("!I", data[:4])[0] == len(data) - 4 and len(f.sent) > 3)
check("respuesta demasiado grande", err(lambda: encode_message({"x": "y" * MAX_MESSAGE_BYTES})) == "RESPONSE_TOO_LARGE")
# --- decode_body
def dec(b): return err(lambda: decode_body(b))
check("BOM", dec(b"\xef\xbb\xbf{}") == "INVALID_ENCODING")
check("utf8 invalido", dec(b'{"a":"\xff"}') == "INVALID_ENCODING")
check("clave duplicada", dec(b'{"a":1,"a":2}') == "INVALID_JSON")
check("NaN", dec(b'{"a":NaN}') == "INVALID_JSON"); check("Infinity", dec(b'{"a":Infinity}') == "INVALID_JSON")
check("texto extra", dec(b'{"a":1} x') == "INVALID_JSON")
check("sustituto aislado", dec(b'{"a":"\\ud800"}') == "INVALID_ENCODING")
check("par sustituto valido", decode_body(b'{"a":"\\ud83d\\ude00"}')["a"] == "😀")
check("profundidad 16 ok", dec(b"[" * 16 + b"]" * 16) is None)
check("profundidad 17", dec(b"[" * 17 + b"]" * 17) == "INVALID_JSON")
check("profundidad 200000 sin romper", dec(b"[" * 200000 + b"]" * 200000) == "INVALID_JSON")
check("corchetes en cadenas no cuentan", dec(b'{"a":"' + b"[" * 500 + b'"}') is None)
# --- validate_request
def req(**kw):
    base = {"version": 1, "request_id": "cli-0001", "action": "list"}; base.update(kw); return base
def val(o):
    try: return validate_request(o)
    except ProtocolError as e: return e
check("run valido", val(req(action="run", command=["sleep", "20"])).params == {"command": ["sleep", "20"]})
for label, v in [("ausente", None), ("0", 0), ("2", 2), ('"1"', "1"), ("true", True), ("null", None)]:
    o = req(); 
    if label == "ausente": del o["version"]
    else: o["version"] = v
    e = val(o)
    check("version " + label, isinstance(e, ProtocolError) and e.code in ("UNSUPPORTED_VERSION", "INVALID_REQUEST") and e.close)
check("version 'true' es UNSUPPORTED", val(req(version=True)).code == "UNSUPPORTED_VERSION")
check("request_id invalido cierra", val(req(request_id="a b")).close)
check("request_id 65", val(req(request_id="a" * 65)).code == "INVALID_REQUEST")
check("raíz lista", val([]).code == "INVALID_REQUEST")
e = val(req(action="borrar")); check("accion desconocida", e.code == "UNKNOWN_ACTION" and not e.close and e.request_id == "cli-0001")
check("campos extra", val(req(action="health", x=1)).code == "INVALID_REQUEST")
check("falta job_id", val(req(action="status")).code == "INVALID_REQUEST")
check("job_id prefijo", val(req(action="cancel", job_id="a1b2c3d4")).params["job_id"] == "a1b2c3d4")
check("job_id corto", val(req(action="cancel", job_id="a1b2")).code == "INVALID_REQUEST")
check("job_id no hex", val(req(action="cancel", job_id="zzzzzzzz")).code == "INVALID_REQUEST")
check("job_id numero", val(req(action="cancel", job_id=12345678)).code == "INVALID_REQUEST")
for bad in ([], "ls", [""], ["  "], [1], ["a\x00b"], None):
    check(f"run comando {bad!r}", val(req(action="run", command=bad)).code == "INVALID_REQUEST")
check("list status minuscula", val(req(status="running")).code == "INVALID_REQUEST")
check("list status null", val(req(status=None)).params["status"] is None)
check("list status valido", val(req(status="RUNNING")).params["status"] == "RUNNING")
check("argumentos con espacios y unicode", val(req(action="run", command=["echo", "hola mundo", "ñ"])).params["command"][1] == "hola mundo")
# --- validate_response
good = ok_response("cli-0001", job_id="x")
check("resp ok", validate_response(good, "cli-0001") is good)
check("resp otra version", err(lambda: validate_response({**good, "version": 2}, "cli-0001")) == "UNSUPPORTED_VERSION")
check("resp otro request_id", err(lambda: validate_response(good, "cli-9999")) == "INVALID_RESPONSE")
e = error_response(None, "INVALID_JSON", "desconocida", "c", "s")
check("resp error sin id", validate_response(e, "cli-0001") is e)
check("resp error incompleta", err(lambda: validate_response({**e, "cause": 5}, "cli-0001")) == "INVALID_RESPONSE")
check("resp campos extra tolerados", validate_response({**good, "nuevo": 1}, "cli-0001"))
print(f"\nOK: {ok}   FALLAS: {fail}")