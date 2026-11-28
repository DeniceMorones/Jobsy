#!/usr/bin/env python3
"""QA PR #135 — EV-032. TCP loopback, concurrencia y robustez."""
import os, sys, socket, struct, subprocess, tempfile, time, threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager, ExitStack
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.protocol.messages import MessageReader, build_request, send_message, decode_body

PASS = FAIL = 0

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def case(n, title, fn):
    global PASS, FAIL
    print(f'\n{"="*72}\nTC-{n} - {title}\n{"="*72}')
    try:
        fn()
    except Exception as exc:
        FAIL += 1
        print(f'FAIL: {type(exc).__name__}: {exc}')
    else:
        PASS += 1
        print(f'PASS: {title}')

class Peer:
    def __init__(self, port, source='127.0.0.1'):
        self.sock = socket.create_connection(('127.0.0.1', port), timeout=3, source_address=(source, 0))
        self.reader = MessageReader(self.sock, idle_timeout=8)
        self.count = 0
    def __enter__(self): return self
    def __exit__(self, *args): self.sock.close()
    def read(self):
        body = self.reader.read()
        require(body is not None, 'Conexión cerrada sin respuesta')
        response = decode_body(body)
        print('Respuesta:', response if 'jobs' not in response else {**response, 'jobs': len(response['jobs'])})
        return response
    def ask(self, action, **fields):
        self.count += 1
        rid = f'qa-{self.count}'
        send_message(self.sock, build_request(action, rid, **fields))
        response = self.read()
        require(response.get('request_id') == rid, 'Request ID no coincide')
        return response
    def ok(self, action, **fields):
        response = self.ask(action, **fields)
        require(response.get('status') == 'ok', 'Respuesta no exitosa')
        return response
    def closed(self):
        self.sock.settimeout(3)
        try:
            return self.sock.recv(1) == b''
        except ConnectionResetError:
            return True

@contextmanager
def server(total=4, per_ip=3):
    with tempfile.TemporaryDirectory(prefix='qa135-conc-') as tmp:
        path = Path(tmp); sock = path/'qa.sock'
        with socket.socket() as probe:
            probe.bind(('127.0.0.1',0)); port = probe.getsockname()[1]
        env = os.environ.copy()
        for key in ('JOBSY_HOST','JOBSY_PORT','JOBSY_SOCKET_PATH','JOBSY_DATA_DIR'):
            env.pop(key,None)
        env.update(JOBSY_SOCKET_PATH=str(sock), XDG_STATE_HOME=tmp)
        with (path/'console').open('w+') as log:
            p = subprocess.Popen(['jobsy-daemon','--socket-path',str(sock),'--data-dir',str(path/'data'),'--listen-host','127.0.0.1','--listen-port',str(port),'--allow-cidr','127.0.0.0/8','--max-remote-connections',str(total),'--max-connections-per-ip',str(per_ip),'--queue-capacity','20'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
            try:
                deadline = time.monotonic()+8
                while True:
                    require(p.poll() is None,'Daemon terminó durante arranque')
                    if sock.exists():
                        try:
                            with Peer(port) as peer: peer.ok('health')
                            break
                        except OSError: pass
                    require(time.monotonic()<deadline,'Timeout de arranque'); time.sleep(.05)
                time.sleep(.15)
                yield port,p,env,sock
            finally:
                if p.poll() is None:
                    p.terminate()
                    try: p.wait(timeout=12)
                    except subprocess.TimeoutExpired:
                        p.kill(); p.wait(); raise AssertionError('Daemon no terminó ordenadamente')
                log.seek(0); print('Consola daemon:\n'+log.read())

def persistent():
    with server() as (port,*_), Peer(port) as a:
        for action in ('health','list','health'): a.ok(action)

def concurrent():
    with server() as (port,*_):
        barrier = threading.Barrier(3)
        def worker(i):
            with Peer(port) as a:
                a.ok('health'); barrier.wait(timeout=5)
                return a.ok('run',command=['echo',f'qa-{i}'])['job_id']
        with ThreadPoolExecutor(max_workers=3) as pool:
            ids = list(pool.map(worker,range(3)))
        require(len(set(ids))==3,'IDs duplicados')
        with Peer(port) as a:
            jobs=a.ok('list')['jobs']; require(set(ids)<= {j['id'] for j in jobs},'Trabajos ausentes')

def recoverable():
    with server() as (port,*_), Peer(port) as a:
        e=a.ask('status',job_id='00000000-0000-0000-0000-000000000000')
        require(e.get('code')=='JOB_NOT_FOUND','Código incorrecto'); a.ok('health')
        e=a.ask('unknown'); require(e.get('code')=='UNKNOWN_ACTION','Código incorrecto'); a.ok('list')

def malformed():
    with server() as (port,*_), Peer(port) as a, Peer(port) as b:
        a.ok('health'); b.sock.sendall(struct.pack('!I',5)+b'{bad}')
        require(b.read().get('code')=='INVALID_JSON','Error incorrecto')
        require(b.closed(),'Conexión inválida no cerrada'); a.ok('health')

def interrupted():
    with server() as (port,*_), Peer(port) as a:
        jid=a.ok('run',command=['sleep','1'])['job_id']
        with Peer(port) as b: b.sock.sendall(struct.pack('!I',64)+b'{"ver')
        with Peer(port) as b:
            b.sock.setsockopt(socket.SOL_SOCKET,socket.SO_LINGER,struct.pack('ii',1,0))
        deadline=time.monotonic()+6
        while True:
            state=a.ok('status',job_id=jid)['job']['status']
            if state=='SUCCEEDED': break
            require(time.monotonic()<deadline,'Trabajo no terminó'); time.sleep(.1)
        a.ok('health')

def limits(global_limit=False):
    with server(total=2 if global_limit else 4,per_ip=4 if global_limit else 2) as (port,*_):
        with ExitStack() as stack:
            a=stack.enter_context(Peer(port)); a.ok('health')
            b=stack.enter_context(Peer(port,'127.0.0.2' if global_limit else '127.0.0.1')); b.ok('health')
            with Peer(port) as c:
                require(c.read().get('code')=='SERVICE_UNAVAILABLE','No se aplicó límite')
            a.ok('health'); b.ok('health')
        time.sleep(.4)
        with Peer(port) as c:
            c.ok('health')

def slow():
    with server() as (port,*_), Peer(port) as a, Peer(port) as b:
        b.sock.sendall(struct.pack('!I',100)+b'{')
        time.sleep(.1); start=time.monotonic(); a.ok('health')
        elapsed=time.monotonic()-start; print('Health con otro cliente incompleto:',elapsed)
        require(elapsed<1,'Health bloqueado por otro cliente')
        require(b.read().get('code')=='READ_TIMEOUT','No se respetó plazo de mensaje'); require(b.closed(),'Cliente lento no cerrado'); a.ok('health')

def coexist():
    with server() as (port,p,env,sock), Peer(port) as a:
        jid=a.ok('run',command=['true'])['job_id']
        result=subprocess.run(['jobsy','list','--full-id'],cwd=ROOT,env=env,capture_output=True,text=True,timeout=5)
        print(result.stdout,result.stderr); require(result.returncode==0 and jid in result.stdout,'IPC no comparte estado')
        a.ok('health')

def shutdown():
    with server() as (port,p,env,sock), Peer(port) as a, Peer(port) as b:
        a.ok('health'); b.ok('health'); start=time.monotonic(); p.terminate(); p.wait(timeout=12)
        print('Tiempo de apagado:',time.monotonic()-start,'rc:',p.returncode)
        require(p.returncode==0,'Salida no exitosa'); require(a.closed() and b.closed(),'Clientes siguen abiertos')
        require(not sock.exists(),'Socket UNIX permanece')
        with socket.socket() as probe:
            probe.settimeout(1); require(probe.connect_ex(('127.0.0.1',port))!=0,'Puerto sigue abierto')

def incomplete_response():
    # Servidor de prueba local: responde con sobre válido, pero sin los datos de list.
    with socket.socket() as listener:
        listener.bind(('127.0.0.1',0)); listener.listen(1); listener.settimeout(5)
        errors=[]
        def responder():
            try:
                with listener.accept()[0] as conn:
                    request=decode_body(MessageReader(conn,idle_timeout=5).read())
                    send_message(conn,{'version':1,'request_id':request['request_id'],'status':'ok'})
            except Exception as e: errors.append(str(e))
        thread=threading.Thread(target=responder,daemon=True); thread.start()
        env=os.environ.copy(); env.pop('JOBSY_PORT',None); env.pop('JOBSY_HOST',None)
        result=subprocess.run(['jobsy','--host','127.0.0.1','--port',str(listener.getsockname()[1]),'list'],cwd=ROOT,env=env,capture_output=True,text=True,timeout=10)
        thread.join(6); require(not thread.is_alive() and not errors,f'Infraestructura: {errors}')
        print('CLI:',result.returncode,repr(result.stdout),repr(result.stderr))
        require(result.returncode!=0 and 'Traceback' not in result.stderr and bool(result.stderr.strip()),'OBS-06: respuesta incompleta sin manejo controlado')

if __name__=='__main__':
    print('PR #135 — EV-032 — Concurrencia y robustez')
    for n,title,fn in [
        (229,'Solicitudes consecutivas en una conexión',persistent),
        (230,'Tres clientes concurrentes crean trabajos independientes',concurrent),
        (231,'Errores recuperables conservan conexión',recoverable),
        (232,'JSON inválido cierra solo al cliente afectado',malformed),
        (233,'Desconexiones abruptas no interrumpen trabajos',interrupted),
        (234,'Límite por IP y recuperación de cupo',limits),
        (235,'Límite global con distintas IP loopback',lambda:limits(True)),
        (236,'Cliente lento no bloquea otro cliente',slow),
        (237,'Coexistencia de IPC UNIX y TCP',coexist),
        (238,'Apagado con clientes activos',shutdown),
        (239,'CLI maneja respuesta exitosa incompleta',incomplete_response),
    ]: case(n,title,fn)
    print(f'\n{"="*72}\nCasos ejecutados: {PASS+FAIL}\nPASS: {PASS}\nFAIL: {FAIL}\nRESULTADO GENERAL: {"PASS" if FAIL==0 else "FAIL"}\n{"="*72}')
    sys.exit(0 if FAIL==0 and PASS==11 else 1)
