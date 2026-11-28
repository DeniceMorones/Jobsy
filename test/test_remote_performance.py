#!/usr/bin/env python3
"""QA PR #135 — EV-033 — RNF-05, TCP loopback."""
import os
import sys
import socket
import subprocess
import tempfile
import time
import statistics
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.protocol.messages import (MessageReader, build_request, send_message,
                                   decode_body, validate_response)

results = {}

def require(condition, message):
    if not condition:
        raise AssertionError(message)


def case(number, title, fn):
    print('\n' + '=' * 72)
    print(f'TC-{number} - {title}')
    print('=' * 72)
    try:
        fn()
    except Exception as exc:
        results[number] = False
        print(f'FAIL: {type(exc).__name__}: {exc}')
    else:
        results[number] = True
        print(f'PASS: {title}')


def main():
    print('PR #135 — EV-033 — Rendimiento RNF-05')
    env = os.environ.copy()
    for key in ('JOBSY_HOST', 'JOBSY_PORT', 'JOBSY_SOCKET_PATH', 'JOBSY_DATA_DIR'):
        env.pop(key, None)
    infrastructure_ok = True
    with tempfile.TemporaryDirectory(prefix='qa135-perf-') as tmp:
        sock = Path(tmp) / 'qa.sock'
        env['JOBSY_SOCKET_PATH'] = str(sock)
        env['XDG_STATE_HOME'] = tmp
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 0))
            port = probe.getsockname()[1]
        with (Path(tmp) / 'console.txt').open('w+') as log:
            daemon = None
            try:
                daemon = subprocess.Popen([
                    'jobsy-daemon', '--socket-path', str(sock), '--data-dir',
                    str(Path(tmp) / 'data'), '--listen-host', '127.0.0.1',
                    '--listen-port', str(port), '--allow-cidr', '127.0.0.1/32',
                    '--max-running', '4', '--queue-capacity', '100',
                ], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
                deadline = time.monotonic() + 10
                while True:
                    require(daemon.poll() is None, 'Daemon terminó durante arranque')
                    try:
                        with socket.create_connection(('127.0.0.1', port), timeout=.25):
                            if sock.exists():
                                break
                    except OSError:
                        pass
                    require(time.monotonic() < deadline, 'Timeout de arranque')
                    time.sleep(.05)
                with socket.create_connection(('127.0.0.1', port), timeout=5) as conn:
                    reader = MessageReader(conn, idle_timeout=10)
                    ids = []
                    status_times, list_times, health_times = [], [], []

                    def ask(action, **fields):
                        rid = 'qa-' + uuid.uuid4().hex
                        start = time.perf_counter()
                        send_message(conn, build_request(action, rid, **fields))
                        body = reader.read()
                        require(body is not None, 'Servidor cerró sin respuesta')
                        response = validate_response(decode_body(body), rid)
                        elapsed = time.perf_counter() - start
                        require(response['status'] == 'ok', f'{action}: {response}')
                        return response, elapsed

                    def create():
                        for i in range(100):
                            response, _ = ask('run', command=['sleep', '0.2'])
                            jid = response['job_id']
                            require(str(uuid.UUID(jid)) == jid, 'UUID inválido')
                            ids.append(jid)
                        print(f'Trabajos creados: {len(ids)}')
                        require(len(ids) == 100, 'No se crearon 100 trabajos')

                    def listed():
                        require(len(ids) == 100, 'Dependencia TC-240 fallida')
                        response, _ = ask('list')
                        jobs = response['jobs']
                        require(len(set(ids)) == 100, 'UUID duplicados')
                        require(len(jobs) == 100 and {j['id'] for j in jobs} == set(ids), 'Listado incompleto o inconsistente')
                        print('100 UUID únicos; 100 trabajos en listado')

                    def completed():
                        require(len(ids) == 100, 'Dependencia TC-240 fallida')
                        deadline = time.monotonic() + 90
                        while True:
                            jobs = ask('list')[0]['jobs']
                            require(len(jobs) == 100 and {j['id'] for j in jobs} == set(ids), 'Listado inconsistente')
                            require(not any(j['status'] in ('FAILED', 'CANCELED') for j in jobs), 'Trabajo fallido o cancelado')
                            if all(j['status'] == 'SUCCEEDED' for j in jobs):
                                break
                            require(time.monotonic() < deadline, 'No finalizaron los 100 trabajos')
                            time.sleep(.2)
                        print('100 trabajos SUCCEEDED')

                    def measure_status():
                        require(results.get(242), 'Dependencia TC-242 fallida')
                        for _ in range(30):
                            for jid in (ids[0], ids[49], ids[-1]):
                                response, elapsed = ask('status', job_id=jid)
                                job = response['job']
                                require(job['id'] == jid and job['status'] == 'SUCCEEDED' and job['exit_code'] == 0, 'Status inválido')
                                status_times.append(elapsed)
                        require(len(status_times) == 90, 'Muestras incompletas')
                        print(f'Consultas válidas: {len(status_times)}')

                    def report(name, values):
                        print(f'{name}: n={len(values)} min={min(values)*1000:.3f} ms mediana={statistics.median(values)*1000:.3f} ms max={max(values)*1000:.3f} ms')

                    def threshold():
                        require(len(status_times) == 90, 'No existen 90 muestras válidas')
                        report('status', status_times)
                        require(max(status_times) <= 1.0, 'RNF-05: latencia máxima superior a 1000 ms')
                        print('RNF-05: CUMPLE en loopback, con 100 trabajos registrados')

                    def complementary():
                        require(results.get(242), 'Dependencia TC-242 fallida')
                        for _ in range(30):
                            response, elapsed = ask('list')
                            require(len(response['jobs']) == 100 and {j['id'] for j in response['jobs']} == set(ids), 'List inválido')
                            list_times.append(elapsed)
                            response, elapsed = ask('health')
                            h = response['health']
                            require(h['service_active'] is True and h['running_count'] == 0 and h['queued_count'] == 0, 'Health inválido')
                            health_times.append(elapsed)
                        report('list', list_times)
                        report('health', health_times)

                    def alive():
                        require(daemon.poll() is None, 'Daemon terminó')
                        require(ask('health')[0]['health']['service_active'] is True, 'TCP no operativo')
                        p = subprocess.run(['jobsy', 'health'], cwd=ROOT, env=env, capture_output=True, text=True, timeout=10)
                        require(p.returncode == 0 and 'Servicio Activo: Sí' in p.stdout, 'IPC local no operativo')
                        print('TCP e IPC local operativos')

                    for n, title, fn in [
                        (240, 'Crear exactamente 100 trabajos mediante TCP', create),
                        (241, 'Verificar UUID únicos y listado completo', listed),
                        (242, 'Completar los 100 trabajos correctamente', completed),
                        (243, 'Ejecutar 90 consultas status válidas', measure_status),
                        (244, 'Latencia máxima status <= 1000 ms', threshold),
                        (245, 'Medir list y health con 100 trabajos', complementary),
                        (246, 'Daemon operativo después de la carga', alive),
                    ]:
                        case(n, title, fn)
            except Exception as exc:
                infrastructure_ok = False
                print(f'FAIL infraestructura: {type(exc).__name__}: {exc}')
            finally:
                if daemon is not None and daemon.poll() is None:
                    daemon.terminate()
                    try:
                        daemon.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        daemon.kill(); daemon.wait()
                        infrastructure_ok = False
                        print('FAIL infraestructura: apagado forzado')
                if daemon is not None and (daemon.returncode != 0 or sock.exists()):
                    infrastructure_ok = False
                    print(f'FAIL infraestructura: rc={daemon.returncode}, socket restante={sock.exists()}')
                log.flush(); log.seek(0)
                if not infrastructure_ok or not all(results.values()):
                    print('\nÚltimas líneas del daemon:\n' + ''.join(log.readlines()[-40:]))
    passed = sum(results.values())
    failed = len(results) - passed
    success = infrastructure_ok and passed == 7 and failed == 0
    print('\n' + '=' * 72)
    print(f'Casos ejecutados: {len(results)}\nPASS: {passed}\nFAIL: {failed}\nNO EJECUTADOS: {7-len(results)}')
    print('RESULTADO GENERAL: ' + ('PASS' if success else 'FAIL'))
    print('=' * 72)
    return 0 if success else 1


if __name__ == '__main__':
    raise SystemExit(main())
