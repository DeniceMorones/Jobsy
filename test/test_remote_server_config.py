#!/usr/bin/env python3
"""QA PR #135 — configuración y ciclo de vida del servidor TCP."""
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.daemon.config import DaemonConfig

ENV = os.environ.copy()
for key in ('JOBSY_HOST', 'JOBSY_PORT', 'JOBSY_SOCKET_PATH', 'JOBSY_DATA_DIR'):
    ENV.pop(key, None)
PASS = FAIL = 0


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def case(number, title, fn):
    global PASS, FAIL
    print('\n' + '=' * 72)
    print(f'TC-{number} - {title}')
    print('=' * 72)
    try:
        fn()
    except Exception as exc:
        FAIL += 1
        print(f'FAIL: {type(exc).__name__}: {exc}')
    else:
        PASS += 1
        print(f'PASS: {title}')


def config(**kwargs):
    return DaemonConfig(**({'listen_host': '127.0.0.1', 'allow_cidrs': ('127.0.0.1/32',)} | kwargs))


def rejected(**kwargs):
    try:
        config(**kwargs)
    except ValueError as exc:
        print(f'Error controlado: {exc}')
    else:
        raise AssertionError(f'Configuración aceptada indebidamente: {kwargs}')


def reject_many(items):
    for item in items:
        rejected(**item)


def defaults():
    c = DaemonConfig()
    require(not c.remote_enabled(), 'TCP habilitado por defecto')
    require((c.listen_port, c.max_remote_connections, c.max_connections_per_ip) == (8765, 8, 2), 'Valores predeterminados incorrectos')
    print('TCP deshabilitado; puerto=8765; global=8; por IP=2')


def valid_networks():
    c = config(listen_host='192.168.10.2', allow_cidrs=('192.168.10.0/24', '10.0.0.5/32'))
    require(c.remote_enabled(), 'TCP no habilitado')
    require([str(n) for n in c.allowed_networks()] == ['192.168.10.0/24', '10.0.0.5/32'], 'Allowlist incorrecta')
    print('Configuración privada y allowlist múltiple aceptadas')


def valid_limits():
    for n in (1, 64):
        c = config(max_remote_connections=n, max_connections_per_ip=n)
        require(c.max_remote_connections == n and c.max_connections_per_ip == n, 'Límite alterado')
    for port in (1, 65535):
        require(config(listen_port=port).listen_port == port, 'Puerto alterado')


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def cli(args, env):
    p = subprocess.run(['jobsy', *args], env=env, cwd=ROOT, capture_output=True, text=True, timeout=10)
    print(f'CLI {args}: rc={p.returncode}; stdout={p.stdout.strip()!r}; stderr={p.stderr.strip()!r}')
    require(p.returncode == 0, 'CLI no respondió correctamente')
    return p.stdout


def daemon_scenario(remote):
    with tempfile.TemporaryDirectory(prefix='jobsy-qa135-') as tmp:
        sock = Path(tmp) / 'qa.sock'
        port = free_port()
        env = ENV | {'JOBSY_SOCKET_PATH': str(sock), 'XDG_STATE_HOME': tmp}
        args = ['jobsy-daemon', '--socket-path', str(sock), '--data-dir', str(Path(tmp)/'data'), '--listen-port', str(port)]
        if remote:
            args += ['--listen-host', '127.0.0.1', '--allow-cidr', '127.0.0.1/32']
        log = Path(tmp)/'console.txt'
        with log.open('w+') as f:
            p = subprocess.Popen(args, env=env, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT)
            try:
                deadline = time.monotonic()+8
                while not sock.exists() and p.poll() is None and time.monotonic()<deadline:
                    time.sleep(.05)
                require(p.poll() is None and sock.exists(), 'Daemon no inició')
                require('Resumen de Salud' in cli(['health'], env), 'Health local inválido')
                if remote:
                    # El socket UNIX puede estar disponible antes que el listener TCP.
                    deadline = time.monotonic()+5
                    while True:
                        try:
                            with socket.create_connection(('127.0.0.1', port), timeout=.3):
                                break
                        except OSError:
                            if time.monotonic() >= deadline:
                                raise
                            time.sleep(.05)
                    require('Resumen de Salud' in cli(['--host','127.0.0.1','--port',str(port),'health'], env), 'Health TCP inválido')
                    # Verificar dirección real de escucha en Linux.
                    result = subprocess.run(['ss','-H','-ltn'], capture_output=True, text=True, check=True)
                    lines = [line for line in result.stdout.splitlines() if line.split()[3].rsplit(':',1)[-1] == str(port)]
                    print('Listeners:', lines)
                    require(len(lines)==1 and lines[0].split()[3]==f'127.0.0.1:{port}', 'Listener no restringido a loopback')
                else:
                    with socket.socket() as probe:
                        probe.bind(('127.0.0.1', port))
                    print('Puerto TCP libre con acceso remoto deshabilitado')
            finally:
                if p.poll() is None:
                    p.terminate()
                    try:
                        p.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        p.kill(); p.wait()
                        raise AssertionError('Daemon no finalizó dentro del plazo')
                f.flush(); f.seek(0); print('Consola daemon:\n'+f.read())
            require(not sock.exists(), 'Socket UNIX residual')
            with socket.socket() as probe:
                probe.settimeout(1)
                require(probe.connect_ex(('127.0.0.1', port)) != 0, 'Puerto TCP aún abierto')
            print('Socket UNIX eliminado y puerto TCP cerrado')


def invalid_entry_point():
    with tempfile.TemporaryDirectory(prefix='jobsy-qa135-invalid-') as tmp:
        p = subprocess.run(['jobsy-daemon','--socket-path',tmp+'/qa.sock','--data-dir',tmp+'/data','--listen-host','0.0.0.0','--allow-cidr','127.0.0.0/8'], env=ENV, cwd=ROOT, capture_output=True, text=True, timeout=5)
        print('Código:',p.returncode,'STDERR:',p.stderr.strip())
        require(p.returncode==2 and '0.0.0.0' in p.stderr and 'Traceback' not in p.stderr, 'Error CLI no controlado')
        require(not Path(tmp+'/qa.sock').exists(), 'Configuración inválida creó socket')


def main():
    print('PR #135 — EV-029 — Configuración y servidor TCP')
    case(181, 'Acceso remoto deshabilitado por defecto', defaults)
    case(182, 'Aceptar IP privada y allowlist múltiple', valid_networks)
    case(183, 'Rechazar direcciones comodín IPv4 e IPv6', lambda: reject_many([{'listen_host':h} for h in ('0.0.0.0','::')]))
    case(184, 'Rechazar IP pública de escucha', lambda: rejected(listen_host='8.8.8.8'))
    case(185, 'Rechazar hostname y dirección inválida', lambda: reject_many([{'listen_host':h} for h in ('localhost','999.1.1.1')]))
    case(186, 'Exigir allowlist al habilitar TCP', lambda: rejected(allow_cidrs=()))
    case(187, 'Rechazar redes públicas y rutas universales', lambda: reject_many([{'allow_cidrs':(n,)} for n in ('8.8.8.0/24','0.0.0.0/0','::/0')]))
    case(188, 'Rechazar CIDR inválido', lambda: rejected(allow_cidrs=('127.0.0.0/99',)))
    case(189, 'Rechazar puertos fuera de rango', lambda: reject_many([{'listen_port':p} for p in (0,-1,65536)]))
    case(190, 'Rechazar límites globales inválidos', lambda: reject_many([{'max_remote_connections':n} for n in (0,65,True)]))
    case(191, 'Rechazar límites por IP inválidos', lambda: reject_many([{'max_connections_per_ip':n} for n in (0,65,True)]))
    case(192, 'Aceptar límites exactos de configuración', valid_limits)
    case(193, 'Configuración inválida rechazada por entry point', invalid_entry_point)
    case(194, 'Daemon local operativo sin listener TCP y limpieza al apagar', lambda: daemon_scenario(False))
    case(195, 'Daemon TCP en IP concreta, IPC local y limpieza al apagar', lambda: daemon_scenario(True))
    print('\n'+'='*72)
    print(f'Casos ejecutados: {PASS+FAIL}\nPASS: {PASS}\nFAIL: {FAIL}\nRESULTADO GENERAL: {"PASS" if FAIL==0 else "FAIL"}')
    print('='*72)
    return int(FAIL != 0)


if __name__ == '__main__':
    raise SystemExit(main())
