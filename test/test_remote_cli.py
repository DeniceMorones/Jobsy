#!/usr/bin/env python3
"""QA PR #135 — EV-030 — cliente remoto TCP y paridad local."""
import os
import re
import socket
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def main():
    global PASS, FAIL
    print('PR #135 — EV-030 — Cliente remoto')
    with tempfile.TemporaryDirectory(prefix='jobsy-qa135-cli-') as tmp:
        sock = Path(tmp) / 'qa.sock'
        port = free_port()
        env = ENV | {'JOBSY_SOCKET_PATH': str(sock), 'XDG_STATE_HOME': tmp}
        remote = ['--host', '127.0.0.1', '--port', str(port)]
        log = Path(tmp) / 'console.txt'
        with log.open('w+') as f:
            daemon = subprocess.Popen(['jobsy-daemon', '--socket-path', str(sock), '--data-dir', str(Path(tmp)/'data'), '--listen-host', '127.0.0.1', '--listen-port', str(port), '--allow-cidr', '127.0.0.1/32', '--max-running', '2', '--queue-capacity', '20'], cwd=ROOT, env=env, stdout=f, stderr=subprocess.STDOUT)
            try:
                deadline = time.monotonic() + 8
                while True:
                    require(daemon.poll() is None, 'Daemon terminó durante el arranque')
                    try:
                        with socket.create_connection(('127.0.0.1', port), timeout=.3):
                            if sock.exists():
                                break
                    except OSError:
                        pass
                    require(time.monotonic() < deadline, 'Timeout de arranque')
                    time.sleep(.05)

                def cli(*args, local=False, custom_env=None, prefix=None):
                    flags = [] if local else remote if prefix is None else prefix
                    p = subprocess.run(['jobsy', *flags, *args], cwd=ROOT, env=env if custom_env is None else custom_env, capture_output=True, text=True, timeout=12)
                    print(f'CLI {[*flags, *args]}: rc={p.returncode}; stdout={p.stdout.strip()!r}; stderr={p.stderr.strip()!r}')
                    return p

                def ok(*args, **kwargs):
                    p = cli(*args, **kwargs)
                    require(p.returncode == 0, 'Código de salida distinto de cero')
                    return p

                def submit(*cmd, local=False):
                    p = ok('run', '--', *cmd, local=local)
                    m = re.search(r'ID:\s*([0-9a-f]{8})\s*$', p.stdout)
                    require(m is not None, 'No se mostró un ID corto válido')
                    return m.group(1)

                def wait_state(jid, state, local=False):
                    deadline = time.monotonic() + 6
                    while True:
                        p = ok('status', jid, local=local)
                        if f'Estado: {state}' in p.stdout:
                            return p
                        require(time.monotonic() < deadline, f'No alcanzó {state}: {jid}')
                        time.sleep(.1)

                ids = {}
                def health():
                    a = ok('health', local=True); b = ok('health')
                    require(a.stdout == b.stdout and 'Servicio Activo: Sí' in b.stdout, 'Health local y remoto distintos')
                def run():
                    ids['job'] = submit('bash', '-c', 'printf "hola remoto\\n"; printf "error de prueba\\n" >&2')
                    wait_state(ids['job'], 'SUCCEEDED')
                def job():
                    require('job' in ids, 'Dependencia TC-197 no disponible')
                    return ids['job']
                def listing():
                    a = ok('list'); b = ok('list', local=True)
                    require(a.stdout == b.stdout and f'ID: {job()}' in a.stdout, 'Listado inconsistente')
                def full_id():
                    p = ok('list', '--full-id')
                    m = re.search(r'ID: ('+job()+r'-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\b', p.stdout)
                    require(m is not None, 'UUID completo ausente')
                    ids['full'] = m.group(1)
                def status():
                    a = wait_state(job(), 'SUCCEEDED'); b = wait_state(job(), 'SUCCEEDED', local=True)
                    require(a.stdout == b.stdout and 'Código de salida: 0' in a.stdout, 'Status inconsistente')
                def status_full():
                    require('full' in ids, 'Dependencia TC-199 no disponible')
                    p = ok('status', ids['full']); require(f'ID: {job()}' in p.stdout and 'Estado: SUCCEEDED' in p.stdout, 'UUID no resuelto')
                def output():
                    a = ok('output', job()); b = ok('output', job(), local=True)
                    require(a.stdout == b.stdout == 'hola remoto\n' and a.stderr == b.stderr == 'error de prueba\n', 'stdout/stderr inconsistentes')
                def filter_list():
                    p = ok('list', '--status', 'SUCCEEDED'); require(f'ID: {job()}' in p.stdout, 'Filtro omitió trabajo exitoso')
                    p = ok('list', '--status', 'FAILED'); require(f'ID: {job()}' not in p.stdout, 'Filtro incluyó trabajo incorrecto')
                def local_to_remote():
                    jid = submit('true', local=True); wait_state(jid, 'SUCCEEDED')
                def cancel():
                    jid = submit('sleep', '30'); ids['cancel'] = jid
                    wait_state(jid, 'RUNNING'); ok('cancel', jid); wait_state(jid, 'CANCELED', local=True)
                def error(p, fragment):
                    require(p.returncode == 1 and fragment.lower() in p.stderr.lower() and 'Traceback' not in p.stderr, 'Error no controlado o mensaje incorrecto')
                def repeated():
                    require('cancel' in ids, 'Dependencia TC-204 no disponible')
                    error(cli('cancel', ids['cancel']), 'Causa')
                    wait_state(ids['cancel'], 'CANCELED')
                def missing():
                    # UUID válido no presente en el entorno aislado.
                    error(cli('status', '00000000-0000-0000-0000-000000000000'), 'No existe')
                def invalid_id():
                    error(cli('status', 'zzzzzzzz'), 'job_id')
                def env_remote():
                    p = ok('list', local=True, custom_env=env | {'JOBSY_HOST':'127.0.0.1', 'JOBSY_PORT':str(port), 'JOBSY_SOCKET_PATH':str(Path(tmp)/'no.sock')})
                    require(f'ID: {job()}' in p.stdout, 'Variables remotas ignoradas')
                def override():
                    p = ok('health', custom_env=env | {'JOBSY_HOST':'127.0.0.2', 'JOBSY_PORT':'1'})
                    require('Servicio Activo: Sí' in p.stdout, 'Opciones explícitas no tienen prioridad')
                def unavailable():
                    with socket.socket() as unused:
                        unused.bind(('127.0.0.1', 0))
                        error(cli('health', prefix=['--host','127.0.0.1','--port',str(unused.getsockname()[1])]), 'No se pudo comunicar')
                def invalid_port():
                    for value in ('0','65536','abc'):
                        p = cli('health', prefix=['--host','127.0.0.1','--port',value]); require(p.returncode == 2 and 'Traceback' not in p.stderr, 'Puerto inválido no manejado por argparse')
                def invalid_env():
                    p = cli('health', local=True, custom_env=env | {'JOBSY_HOST':'127.0.0.1','JOBSY_PORT':'abc'})
                    require(p.returncode != 0 and 'Traceback' not in p.stderr and 'port' in p.stderr.lower(), 'OBS-05: JOBSY_PORT inválido no manejado de forma controlada')
                def still_alive():
                    require('Servicio Activo: Sí' in ok('health').stdout and 'Servicio Activo: Sí' in ok('health',local=True).stdout, 'Daemon dejó de responder')
                for n, title, fn in [
                    (196,'Health remoto y local equivalentes',health),
                    (197,'Run remoto genera ID corto y ejecuta trabajo',run),
                    (198,'List remoto comparte trabajos con UNIX',listing),
                    (199,'List remoto --full-id muestra UUID',full_id),
                    (200,'Status remoto mediante ID corto y paridad local',status),
                    (201,'Status remoto mediante UUID completo',status_full),
                    (202,'Output remoto conserva stdout y stderr',output),
                    (203,'List remoto aplica filtro por estado',filter_list),
                    (204,'Trabajo remoto cancelado y consultado localmente',cancel),
                    (205,'Trabajo local consultado por TCP',local_to_remote),
                    (206,'Cancelación repetida controlada',repeated),
                    (207,'ID inexistente devuelve error controlado',missing),
                    (208,'ID inválido devuelve error controlado',invalid_id),
                    (209,'JOBSY_HOST y JOBSY_PORT seleccionan TCP',env_remote),
                    (210,'Opciones explícitas prevalecen sobre entorno',override),
                    (211,'Servidor no disponible devuelve error controlado',unavailable),
                    (212,'Puerto explícito inválido devuelve error de sintaxis',invalid_port),
                    (213,'JOBSY_PORT no numérico sin traceback',invalid_env),
                    (214,'Daemon permanece operativo tras errores',still_alive),
                ]:
                    case(n,title,fn)
            except Exception as exc:
                FAIL += 1
                print(f'FAIL: Infraestructura: {type(exc).__name__}: {exc}')
            finally:
                if daemon.poll() is None:
                    daemon.terminate()
                    try:
                        daemon.wait(timeout=12)
                    except subprocess.TimeoutExpired:
                        daemon.kill(); daemon.wait(); FAIL += 1
                        print('FAIL: Daemon no terminó ordenadamente')
                f.flush(); f.seek(0); print('\nConsola daemon:\n'+f.read())
    print('\n'+'='*72)
    print(f'Comprobaciones contabilizadas: {PASS+FAIL}\nPASS: {PASS}\nFAIL: {FAIL}')
    print('RESULTADO GENERAL: '+('PASS' if FAIL == 0 and PASS == 19 else 'FAIL'))
    print('='*72)
    return 0 if FAIL == 0 and PASS == 19 else 1


if __name__ == '__main__':
    raise SystemExit(main())
