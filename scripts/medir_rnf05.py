"""RNF-05: 'status' responde en <= 1 s con 100 trabajos. Uso: python3 medir_rnf05.py HOST PORT
Requiere un daemon con --listen-host. Crea 100 trabajos y mide status/list/health por la red."""
import json, socket, statistics, sys, time
from src.protocol.messages import build_request, send_message, MessageReader

host, port = sys.argv[1], int(sys.argv[2])
c = socket.create_connection((host, port), timeout=10); r = MessageReader(c, idle_timeout=10)
def ask(action, **f):
    t = time.perf_counter(); send_message(c, build_request(action, f"m-{time.perf_counter_ns()}", **f))
    resp = json.loads(r.read()); return resp, time.perf_counter() - t

ids = []
for i in range(100):
    resp, _ = ask("run", command=["sleep", "0.2"])
    if resp["status"] != "ok": print("run fallo:", resp.get("code")); break
    ids.append(resp["job_id"])
print(f"trabajos creados: {len(ids)}")
res = {"status": [], "list": [], "health": []}
for _ in range(30):
    for jid in (ids[0], ids[len(ids)//2], ids[-1]):
        res["status"].append(ask("status", job_id=jid)[1])
    res["list"].append(ask("list")[1]); res["health"].append(ask("health")[1])
for k, v in res.items():
    print(f"{k:7s} n={len(v):3d} mediana={statistics.median(v)*1000:7.1f} ms  max={max(v)*1000:7.1f} ms")
worst = max(res["status"])
print("RNF-05:", "CUMPLE" if worst <= 1.0 else "NO CUMPLE", f"(peor status: {worst*1000:.1f} ms, límite 1000 ms)")