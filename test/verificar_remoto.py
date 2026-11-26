import os, sys, time, tempfile, socket, threading, json
os.environ["XDG_STATE_HOME"] = tempfile.mkdtemp()
sys.path.insert(0, ".")
from src.daemon.config import DaemonConfig
from src.daemon.job_manager import JobManager
from src.daemon.remote_server import RemoteListener
from src.protocol.messages import *

ok = fail = 0
def check(n, c):
    global ok, fail
    if c: ok += 1
    else: fail += 1; print("FALLA:", n)

cfg = DaemonConfig(socket_path="/tmp/rc.sock", listen_host="127.0.0.1", listen_port=1, allow_cidrs=("127.0.0.0/8",),
                   max_remote_connections=4, max_connections_per_ip=3)
# puerto 0 no pasa la validación: usamos uno libre
s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
cfg = DaemonConfig(socket_path="/tmp/rc.sock", listen_host="127.0.0.1", listen_port=port, allow_cidrs=("127.0.0.0/8",),
                   max_remote_connections=4, max_connections_per_ip=3)
m = JobManager(cfg); L = RemoteListener(m, cfg); L.start()

def connect():
    c = socket.create_connection(("127.0.0.1", port), timeout=5); return c, MessageReader(c, idle_timeout=5)
def ask(c, r, action, rid="r-1", **f):
    send_message(c, build_request(action, rid, **f)); return json.loads(r.read())

c1, r1 = connect()
h = ask(c1, r1, "health"); check("health remoto", h["status"] == "ok" and h["request_id"] == "r-1")
run = ask(c1, r1, "run", "r-2", command=["bash", "-c", "echo remoto"]); check("run", run["status"] == "ok")
time.sleep(0.5)
st = ask(c1, r1, "status", "r-3", job_id=run["job_id"]); check("status", st["job"]["status"] == "SUCCEEDED")
o = ask(c1, r1, "output", "r-4", job_id=run["job_id"]); check("output", o["stdout"] == "remoto\n")
e = ask(c1, r1, "status", "r-5", job_id="bbbbbbbb"); check("error sigue abierta", e["code"] == "JOB_NOT_FOUND")
check("misma conexion tras error", ask(c1, r1, "list", "r-6")["status"] == "ok")
# mensaje basura: error y cierre, sin afectar a otros clientes
c2, r2 = connect(); c2.sendall(b"\x00\x00\x00\x05{bad}")
bad = json.loads(r2.read()); check("INVALID_JSON", bad["code"] == "INVALID_JSON")
check("cliente 1 intacto", ask(c1, r1, "health", "r-7")["status"] == "ok")
# cliente que se desconecta a media petición y otro que se corta de golpe (RF-22)
c3, _ = connect(); c3.sendall(b"\x00\x00\x00\x40{\"ver"); c3.close()
c4, _ = connect(); c4.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, __import__("struct").pack("ii", 1, 0)); c4.close()
time.sleep(0.5)
check("servicio vivo tras cortes", ask(c1, r1, "health", "r-8")["status"] == "ok")
# varios clientes concurrentes
res = []
def worker(i):
    c, r = connect(); res.append(ask(c, r, "run", f"w-{i}", command=["true"])["status"]); c.close()
ts = [threading.Thread(target=worker, args=(i,)) for i in range(2)]
[t.start() for t in ts]; [t.join() for t in ts]; check("clientes concurrentes", res == ["ok", "ok"])
# límites: por IP = 3 (c1 abierto + 2 más) -> el siguiente es rechazado
time.sleep(0.3)
a, ra = connect(); b, rb = connect(); ask(a, ra, "list"); ask(b, rb, "list")
d, rd = connect(); rej = json.loads(rd.read()); check("límite por IP", rej["code"] == "SERVICE_UNAVAILABLE")
a.close(); b.close(); d.close(); time.sleep(0.3)
# apagado ordenado
threads_before = threading.active_count()
t0 = time.time(); L.stop(); dt = time.time() - t0
check("stop rápido", dt < 3)
check("sin clientes ni hilos", not L._clients and not L._workers and not L._accept_thread.is_alive())
try: socket.create_connection(("127.0.0.1", port), timeout=1); closed = False
except OSError: closed = True
check("puerto cerrado", closed)
try: c1.settimeout(2); closed = c1.recv(1) == b""
except OSError: closed = True
check("cliente 1 desconectado al apagar", closed)
m.shutdown(timeout=3)
# lista de permitidos: red que no incluye 127.x rechaza
cfg2 = DaemonConfig(socket_path="/tmp/rc.sock", listen_host="127.0.0.1", listen_port=port, allow_cidrs=("10.0.0.0/8",))
m2 = JobManager(cfg2); L2 = RemoteListener(m2, cfg2); L2.start()
c, r = connect()
try: data = c.recv(10)
except OSError: data = b""
check("IP fuera de allowlist cerrada sin respuesta", data == b"")
L2.stop(); m2.shutdown(timeout=3)
print(f"\nOK: {ok}   FALLAS: {fail}")