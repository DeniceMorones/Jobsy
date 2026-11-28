#!/usr/bin/env python3
"""QA PR #135 — EV-031 — seguridad y RNF-15. Solo datos ficticios y loopback."""
import os
import socket
import subprocess
import tempfile
import time
import stat
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
PASS = FAIL = 0


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def case(n, title, fn):
    global PASS, FAIL
    print('\n' + '=' * 72 + f'\nTC-{n} - {title}\n' + '=' * 72)
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


class Server:
    def __init__(self, root, cidr):
        self.root = root
        self.data = root / 'data'
        self.sock = root / 'qa.sock'
        self.port = free_port()
        self.cidr = cidr
        self.env = os.environ.copy()
        for key in ('JOBSY_HOST', 'JOBSY_PORT', 'JOBSY_SOCKET_PATH', 'JOBSY_DATA_DIR'):
            self.env.pop(key, None)
        self.env.update(JOBSY_SOCKET_PATH=str(self.sock), XDG_STATE_HOME=str(root / 'xdg'))
        self.proc = None
        self.console = None

    def __enter__(self):
        self.root.mkdir(parents=True, exist_ok=True)
        self.console = (self.root / 'console.txt').open('w+')
        try:
            self.proc = subprocess.Popen(['jobsy-daemon', '--socket-path', str(self.sock), '--data-dir', str(self.data), '--listen-host', '127.0.0.1', '--listen-port', str(self.port), '--allow-cidr', self.cidr], cwd=ROOT, env=self.env, stdout=self.console, stderr=subprocess.STDOUT)
            deadline = time.monotonic() + 8
            while True:
                require(self.proc.poll() is None, 'Daemon terminó durante arranque')
                if self.sock.exists():
                    try:
                        with socket.create_connection(('127.0.0.1', self.port), timeout=.3):
                            return self
                    except OSError:
                        pass
                require(time.monotonic() < deadline, 'Timeout de arranque')
                time.sleep(.05)
        except BaseException:
            self.__exit__(*sys.exc_info())
            raise

    def __exit__(self, *args):
        if self.proc is not None and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=12)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait()
                self.console.close()
                raise AssertionError('Daemon no terminó ordenadamente')
        if self.console is not None:
            self.console.close()

    def cli(self, *args, remote=False):
        flags = ['--host', '127.0.0.1', '--port', str(self.port)] if remote else []
        p = subprocess.run(['jobsy', *flags, *args], cwd=ROOT, env=self.env, capture_output=True, text=True, timeout=10)
        print(f'CLI {[*flags, *args]}: rc={p.returncode}; stdout={p.stdout!r}; stderr={p.stderr!r}')
        return p

    def log(self):
        return (self.data / 'jobsy.log').read_text(encoding='utf-8')

    def wait_log(self, fragment):
        deadline = time.monotonic() + 4
        while time.monotonic() < deadline:
            if (self.data / 'jobsy.log').exists() and fragment in self.log():
                return
            time.sleep(.05)
        raise AssertionError(f'No aparece en bitácora: {fragment}')


def main():
    global FAIL
    print('PR #135 — EV-031 — Seguridad y RNF-15')
    with tempfile.TemporaryDirectory(prefix='jobsy-qa135-security-') as tmp:
        # Aislar también la instancia global del logger importada en este proceso.
        os.environ['XDG_STATE_HOME'] = str(Path(tmp) / 'unit-xdg')
        from src.daemon.logger import DaemonLogger, sanitize
        from src.daemon import dispatcher
        from src.protocol.messages import validate_request, build_request
        root = Path(tmp)
        try:
            with Server(root / 'allowed', '127.0.0.1/32') as s:
                def arguments(remote):
                    marker = 'QA_FAKE_REMOTE_5817' if remote else 'QA_FAKE_LOCAL_5817'
                    p = s.cli('run', '--', 'echo', marker, remote=remote)
                    require(p.returncode == 0, 'No se creó el trabajo')
                    import re
                    m = re.search(r'ID:\s*([0-9a-f]{8})', p.stdout)
                    require(m is not None, 'ID ausente')
                    deadline = time.monotonic() + 5
                    while True:
                        q = s.cli('status', m.group(1), remote=remote)
                        require(q.returncode == 0, 'No se pudo consultar trabajo')
                        if 'Estado: SUCCEEDED' in q.stdout:
                            break
                        require(time.monotonic() < deadline, 'Trabajo no terminó exitosamente')
                        time.sleep(.1)
                    q = s.cli('output', m.group(1), remote=remote)
                    require(q.returncode == 0 and q.stdout.strip() == marker, 'Trabajo no produjo el marcador esperado')
                    require(marker not in s.log(), 'Argumento ficticio expuesto en bitácora')
                    print('Argumento presente en output autorizado, ausente en bitácora')
                case(215, 'No registrar argumentos locales', lambda: arguments(False))
                case(216, 'No registrar argumentos remotos', lambda: arguments(True))

                def sanitized(value, secret):
                    result = sanitize(value)
                    print('Resultado:', result)
                    require(secret not in result and '[REDACTADO]' in result, 'Secreto ficticio no ocultado completamente')
                case(217, 'Sanitizar secretos clave=valor', lambda: sanitized('DB_PASSWORD=QA_FAKE_217', 'QA_FAKE_217'))
                case(218, 'Sanitizar opciones con secretos', lambda: sanitized('--api-key QA_FAKE_218', 'QA_FAKE_218'))
                case(219, 'Sanitizar autorización HTTP Bearer', lambda: sanitized('Authorization: Bearer QA_FAKE_219', 'QA_FAKE_219'))

                def mode(path):
                    value = stat.S_IMODE(path.stat().st_mode)
                    print(f'Permisos: {value:04o}')
                    require(value == 0o600, 'Permisos diferentes de 0600')
                case(220, 'Crear jobsy.log con permisos 0600', lambda: mode(s.data / 'jobsy.log'))

                def existing():
                    directory = root / 'existing'
                    directory.mkdir()
                    file = directory / 'jobsy.log'
                    file.write_text('QA\n')
                    file.chmod(0o644)
                    DaemonLogger(directory).log('INFO', 'QA prueba de permisos')
                    mode(file)
                case(221, 'Corregir permisos de bitácora existente', existing)

                def data_dir():
                    require((s.data / 'jobsy.log').is_file(), 'No existe bitácora en --data-dir')
                    s.wait_log('Acceso remoto habilitado')
                    print('Bitácora configurada:', s.data / 'jobsy.log')
                case(222, 'Usar bitácora de --data-dir', data_dir)
                case(223, 'Registrar IP autorizada', lambda: s.wait_log('Conexión remota aceptada desde 127.0.0.1'))

            with Server(root / 'denied', '10.0.0.0/8') as s:
                def denied():
                    p = s.cli('health', remote=True)
                    require(p.returncode == 1 and 'Traceback' not in p.stderr and 'Servicio Activo: Sí' not in p.stdout, 'Acceso no autorizado o error no controlado')
                    with socket.create_connection(('127.0.0.1', s.port), timeout=2) as c:
                        try:
                            data = c.recv(1)
                        except ConnectionResetError:
                            data = b''
                        require(data == b'', 'Servidor respondió a IP no autorizada')
                case(224, 'Rechazar conexión fuera de allowlist', denied)
                case(225, 'Registrar IP rechazada', lambda: s.wait_log('127.0.0.1 fuera de las redes permitidas'))
                def alive():
                    p = s.cli('health')
                    require(p.returncode == 0 and 'Servicio Activo: Sí' in p.stdout, 'Daemon local no responde')
                case(226, 'Daemon operativo después de rechazo', alive)

            def internal():
                # Inyección controlada de una excepción en el despachador, sin modificar producción.
                marker = 'QA_FAKE_INTERNAL_5828'
                logger = DaemonLogger(root / 'internal')
                class Manager:
                    storage_error = None
                    is_accepting_jobs = True
                    def snapshot(self, job_id):
                        raise RuntimeError('Fallo simulado con dato sensible ' + marker)
                request = validate_request(build_request('status', 'qa-internal', job_id='aaaaaaaa'))
                with patch.object(dispatcher, 'logger', logger):
                    response, close = dispatcher.dispatch(Manager(), request)
                return marker, response, close, logger.log_file.read_text(encoding='utf-8')
            def response_safe():
                marker, response, close, _ = internal()
                print('Respuesta:', response, 'close=', close)
                require(response.get('status') == 'error' and response.get('code') == 'INTERNAL_ERROR' and marker not in repr(response) and 'Traceback' not in repr(response), 'Respuesta interna no sanitizada')
            def log_safe():
                marker, _, _, log = internal()
                print('Marcador ficticio presente en bitácora:', marker in log)
                require(marker not in log, 'OBS-07: excepción interna registra dato sensible sin etiqueta')
            case(227, 'Sanitizar respuestas de errores internos', response_safe)
            case(228, 'Evitar secretos en logs de excepciones internas', log_safe)
        except Exception as exc:
            FAIL += 1
            print(f'FAIL: Infraestructura: {type(exc).__name__}: {exc}')
    print('\n' + '=' * 72)
    print(f'Comprobaciones contabilizadas: {PASS + FAIL}\nPASS: {PASS}\nFAIL: {FAIL}')
    success = PASS == 14 and FAIL == 0
    print('RESULTADO GENERAL: ' + ('PASS' if success else 'FAIL'))
    print('=' * 72)
    return 0 if success else 1


if __name__ == '__main__':
    raise SystemExit(main())
