import os, sys, time, tempfile, socket, subprocess, re
os.environ["XDG_STATE_HOME"] = tempfile.mkdtemp()
sys.path.insert(0, ".")
from src.daemon.config import DaemonConfig
from src.daemon.job_manager import JobManager
from src.daemon.remote_server import RemoteListener
ok = fail = 0
def check(n, c):
    global ok, fail
    if c: ok += 1
    else: fail += 1; print("FALLA:", n)
s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
cfg = DaemonConfig(socket_path="/tmp/cc.sock", listen_host="127.0.0.1", listen_port=port, allow_cidrs=("127.0.0.0/8",), queue_capacity=0, max_running=1)
m = JobManager(cfg); L = RemoteListener(m, cfg); L.start()
env = {**os.environ, "PYTHONPATH": ".", "JOBSY_SOCKET_PATH": "/tmp/no-existe.sock"}
def cli(*a, e=None):
    p = subprocess.run([sys.executable, "-c", "import sys; from src.client.cli import main; main()", *a],
                       capture_output=True, text=True, env=e or env, timeout=30)
    return p.returncode, p.stdout, p.stderr
R = ["--host", "127.0.0.1", "--port", str(port)]
rc, out, err = cli(*R, "run", "--", "bash", "-c", "echo hola remoto; echo err >&2")
check("run", rc == 0 and "Trabajo creado" in out); jid8 = re.search(r"ID: (\w+)", out).group(1)
time.sleep(0.6)
rc, out, err = cli(*R, "status", jid8)
check("status", rc == 0 and "Estado: SUCCEEDED" in out and "Código de salida: 0" in out and "Diagnóstico" not in out)
rc, out, err = cli(*R, "output", jid8); check("output", out == "hola remoto\n" and err == "err\n")
rc, out, err = cli(*R, "list"); check("list", rc == 0 and f"ID: {jid8}" in out and "SUCCEEDED" in out)
rc, out, err = cli(*R, "list", "--status", "FAILED"); check("list filtro", "No se encontraron" in out)
rc, out, err = cli(*R, "list", "--full-id"); check("list full-id", re.search(r"ID: [0-9a-f-]{36}", out))
rc, out, err = cli(*R, "health"); check("health", rc == 0 and "Resumen de Salud" in out and "Errores Recientes (0)" in out)
rc, out, err = cli(*R, "status", "bbbbbbbb"); check("error not found", rc == 1 and "'status'" in err and "Causa" in err and "Acción sugerida" in err)
rc, out, err = cli(*R, "run", "--", "sleep", "5"); check("run largo", rc == 0); sid = re.search(r"ID: (\w+)", out).group(1)
rc, out, err = cli(*R, "run", "--", "sleep", "5"); check("cola llena", rc == 1 and "Cola llena" in err)
rc, out, err = cli(*R, "cancel", sid); check("cancel", rc == 0 and "Cancelando" in out)
rc, out, err = cli(*R, "cancel", sid); check("cancel repetido", rc == 1 and "Causa" in err)
# variables de entorno
e2 = {**env, "JOBSY_HOST": "127.0.0.1", "JOBSY_PORT": str(port)}
rc, out, err = cli("list", e=e2); check("env JOBSY_HOST", rc == 0 and jid8 in out)
# servidor caído / IP no permitida
rc, out, err = cli("--host", "127.0.0.1", "--port", "1", "list"); check("sin servidor", rc == 1 and "No se pudo comunicar" in err and "Traceback" not in err)
rc, out, err = cli("--host", "127.0.0.1", "--port", "70000", "list"); check("puerto invalido", rc == 2)
# local sin demonio: comportamiento original
rc, out, err = cli("list"); check("local intacto", rc == 1 and "no está en ejecución" in err)
L.stop(); m.shutdown(timeout=3)
print(f"\nOK: {ok}   FALLAS: {fail}")