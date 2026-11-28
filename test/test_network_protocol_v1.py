"""QA PR #135: protocolo de red v1 (EV-028). Ejecutar desde la raíz."""
import json
import socket
import struct
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.protocol import messages as M


def frame(body):
    return struct.pack('!I', len(body)) + body


class Stream:
    def __init__(self, chunks=(), timeout=False):
        self.chunks = bytearray(b''.join(chunks))
        self.sizes = [len(c) for c in chunks]
        self.timeout = timeout
        self.sent = bytearray()

    def settimeout(self, timeout):
        pass

    def recv(self, n):
        if self.chunks:
            size = min(n, self.sizes[0])
            data = bytes(self.chunks[:size])
            del self.chunks[:size]
            self.sizes[0] -= size
            if not self.sizes[0]:
                self.sizes.pop(0)
            return data
        if self.timeout:
            raise TimeoutError()
        return b''

    def send(self, data):
        chunk = bytes(data[:3])
        self.sent.extend(chunk)
        return len(chunk)


def expect_error(fn, code, close=None):
    try:
        fn()
    except M.ProtocolError as exc:
        assert exc.code == code, (exc.code, code)
        if close is not None:
            assert exc.close == close, (exc.close, close)
        print(f'Error controlado: {exc.code}; close={exc.close}')
    else:
        raise AssertionError(f'Se esperaba {code}')


def req(action='health', **fields):
    return M.build_request(action, 'qa-135', **fields)


def tc165():
    obj = req()
    data = M.encode_message(obj)
    assert struct.unpack('!I', data[:4])[0] == len(data[4:])
    assert json.loads(data[4:]) == obj


def tc166():
    body = json.dumps(req('run', command=['echo', 'México 😀']), ensure_ascii=False).encode()
    data = frame(body)
    reader = M.MessageReader(Stream([bytes([x]) for x in data]))
    assert M.decode_body(reader.read())['command'] == ['echo', 'México 😀']


def tc167():
    a, b = M.encode_message(req()), M.encode_message(req('list'))
    reader = M.MessageReader(Stream([a+b]))
    assert M.decode_body(reader.read())['action'] == 'health'
    assert M.decode_body(reader.read())['action'] == 'list'
    assert reader.read() is None


def tc168():
    stream = Stream()
    M.send_message(stream, req())
    assert bytes(stream.sent) == M.encode_message(req())


def tc169():
    for length in (0, M.MAX_MESSAGE_BYTES+1):
        expect_error(lambda: M.MessageReader(Stream([struct.pack('!I', length)])).read(), 'INVALID_LENGTH', True)


def tc170():
    assert M.MAX_MESSAGE_BYTES == 1048576
    body = b'"' + b'x'*(1048576-2) + b'"'
    assert M.MessageReader(Stream([frame(body)])).read() == body
    assert M.MessageReader(Stream([frame(b'7')])).read() == b'7'


def tc171():
    for data in (b'\x00\x00', struct.pack('!I', 10)+b'abc'):
        expect_error(lambda: M.MessageReader(Stream([data])).read(), 'INCOMPLETE_MESSAGE', True)


def tc172():
    expect_error(lambda: M.MessageReader(Stream([struct.pack('!I',10)+b'a'], timeout=True)).read(), 'READ_TIMEOUT', True)
    try:
        M.MessageReader(Stream(timeout=True)).read()
    except M.IdleTimeout:
        print('Inactividad detectada correctamente')
    else:
        raise AssertionError('Se esperaba IdleTimeout')


def tc173():
    a,b = socket.socketpair()
    def drip():
        for byte in frame(b'{"value":"test"}'):
            try:
                b.sendall(bytes([byte]))
            except OSError:
                return
            time.sleep(0.06)
    worker = threading.Thread(target=drip, daemon=True)
    try:
        worker.start()
        start = time.monotonic()
        expect_error(lambda: M.MessageReader(a, message_timeout=0.3, idle_timeout=2).read(), 'READ_TIMEOUT', True)
        elapsed = time.monotonic()-start
        print(f'Tiempo observado: {elapsed:.3f} s; plazo configurado: 0.3 s')
        assert elapsed < 1.0, elapsed
    finally:
        a.close(); b.close(); worker.join(2)


def tc174():
    for body in (b'\xef\xbb\xbf{}', b'{"x":"\xff"}', b'{"x":"\\ud800"}'):
        expect_error(lambda: M.decode_body(body), 'INVALID_ENCODING', True)


def tc175():
    for body in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b'{} {}', b'['*17+b']'*17):
        expect_error(lambda: M.decode_body(body), 'INVALID_JSON', True)
    assert M.decode_body(b'['*16+b']'*16) is not None


def tc176():
    for version in (0,2,'1',True,None):
        expect_error(lambda: M.validate_request({**req(), 'version':version}), 'UNSUPPORTED_VERSION', True)
    missing = req(); del missing['version']
    expect_error(lambda: M.validate_request(missing), 'INVALID_REQUEST', True)


def tc177():
    for rid in ('', 'a b', 'a'*65, 123):
        expect_error(lambda: M.validate_request({**req(), 'request_id':rid}), 'INVALID_REQUEST', True)
    assert M.validate_request({**req(), 'request_id':'a'*64}).request_id == 'a'*64


def tc178():
    expect_error(lambda: M.validate_request(req('unknown')), 'UNKNOWN_ACTION', False)
    for obj in (req('status'), req('health', extra=1), req('run', command=[]), req('run', command=['echo','a\x00b']), req('list', status='running'), req('cancel', job_id='abc'), req('output', job_id='zzzzzzzz')):
        expect_error(lambda: M.validate_request(obj), 'INVALID_REQUEST', False)
    assert M.validate_request(req('status', job_id='ABCDEF12')).params['job_id'] == 'ABCDEF12'


def tc179():
    good = M.ok_response('qa-135', jobs=[])
    assert M.validate_response(good, 'qa-135') == good
    expect_error(lambda: M.validate_response(good, 'different'), 'INVALID_RESPONSE')
    expect_error(lambda: M.validate_response({**good,'version':2}, 'qa-135'), 'UNSUPPORTED_VERSION')
    error = M.error_response(None,'INVALID_JSON','desconocida','causa','sugerencia')
    assert M.validate_response(error,'qa-135') == error
    expect_error(lambda: M.validate_response({**error,'cause':None},'qa-135'), 'INVALID_RESPONSE')


def tc180():
    expect_error(lambda: M.encode_message({'x':'x'*M.MAX_MESSAGE_BYTES}), 'RESPONSE_TOO_LARGE', False)


CASES = [
    (165,'Cabecera de cuatro bytes y JSON UTF-8',tc165),
    (166,'Fragmentación byte a byte con Unicode',tc166),
    (167,'Tramas agrupadas y EOF limpio',tc167),
    (168,'Envío parcial sin pérdida de datos',tc168),
    (169,'Rechazo de longitudes fuera del límite',tc169),
    (170,'Aceptación de los límites exactos de framing',tc170),
    (171,'Detección de cabecera o cuerpo incompleto',tc171),
    (172,'Timeout de lectura e inactividad',tc172),
    (173,'Plazo absoluto ante tráfico fragmentado lento',tc173),
    (174,'Rechazo de codificación inválida',tc174),
    (175,'JSON inválido y límite de profundidad',tc175),
    (176,'Validación de versión del protocolo',tc176),
    (177,'Validación de request_id',tc177),
    (178,'Validación de acciones y parámetros',tc178),
    (179,'Validación de sobres de respuesta y correlación',tc179),
    (180,'Rechazo de respuesta superior a 1 MiB',tc180),
]


def main():
    failures = 0
    for number, name, test in CASES:
        print(f'\n{"="*72}\nTC-{number:03d} - {name}\n{"="*72}')
        try:
            test()
            print(f'PASS: {name}')
        except Exception as exc:
            failures += 1
            print(f'FAIL: {name}: {type(exc).__name__}: {exc}')
    print(f'\n{"="*72}\nCasos ejecutados: {len(CASES)}\nPASS: {len(CASES)-failures}\nFAIL: {failures}\nRESULTADO GENERAL: {"FAIL" if failures else "PASS"}\n{"="*72}')
    return int(failures != 0)


if __name__ == '__main__':
    sys.exit(main())
