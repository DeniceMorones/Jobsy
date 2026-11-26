"""Listener TCP remoto del protocolo v1 (RF-18, RF-22, RNF-25, RNF-26).

Segundo transporte del mismo daemon (ADR-010): comparte el JobManager con el socket Unix y usa el
mismo despachador, de modo que local y remoto tienen la misma semántica (RF-19). Un hilo por conexión,
con tope global y por IP reservado antes de crear el hilo. No se retiene ningún candado durante E/S de red.
"""
import ipaddress
import socket
import threading

from src.daemon.dispatcher import dispatch
from src.daemon.logger import logger
from src.protocol.messages import (
    IdleTimeout, MessageReader, ProtocolError, decode_body, error_response,
    send_message, validate_request)

REJECT_SEND_TIMEOUT = 1.0
JOIN_TIMEOUT = 5.0


class RemoteListener:
    def __init__(self, manager, config):
        self.manager = manager
        self.host = config.listen_host
        self.port = config.listen_port
        self.networks = config.allowed_networks()
        self.max_total = config.max_remote_connections
        self.max_per_ip = config.max_connections_per_ip
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._listener = None
        self._accept_thread = None
        self._clients = {}            # socket -> ip
        self._workers = set()

    # ------------------------------------------------------------ ciclo de vida
    def start(self):
        sock = socket.socket(socket.AF_INET6 if ":" in self.host else socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.host, self.port))
            sock.listen(16)
            sock.settimeout(0.5)
        except OSError:
            sock.close()
            raise
        self._listener = sock
        self.port = sock.getsockname()[1]
        self._accept_thread = threading.Thread(target=self._accept_loop, name="jobsy-remote-accept", daemon=True)
        self._accept_thread.start()
        logger.log("INFO", f"Acceso remoto habilitado en {self.host}:{self.port} "
                           f"(redes permitidas: {', '.join(str(n) for n in self.networks)})")

    def stop(self):
        """Orden de ADR-010: dejar de aceptar, cerrar listener, cerrar clientes, esperar hilos."""
        self._stop.set()
        if self._listener is not None:
            try:
                self._listener.close()
            except OSError:
                pass
        with self._lock:
            clients = list(self._clients)
            workers = list(self._workers)
        for client in clients:
            try:
                client.shutdown(socket.SHUT_RDWR)      # despierta recv() bloqueado
            except OSError:
                pass
        for thread in [self._accept_thread, *workers]:
            if thread is not None and thread is not threading.current_thread():
                thread.join(JOIN_TIMEOUT)
        logger.log("INFO", "Acceso remoto detenido.")

    # ------------------------------------------------------------ aceptación
    def _allowed(self, ip):
        try:
            address = ipaddress.ip_address(ip)
        except ValueError:
            return False
        return any(address in network for network in self.networks)

    def _accept_loop(self):
        while not self._stop.is_set():
            try:
                conn, peer = self._listener.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            ip = peer[0]
            if not self._allowed(ip):
                logger.log("WARNING", f"Conexión remota rechazada: {ip} fuera de las redes permitidas.")
                self._close(conn)
                continue
            reason = self._reserve(conn, ip)
            if reason:
                logger.log("WARNING", f"Conexión remota rechazada desde {ip}: {reason}.")
                self._reject_busy(conn)
                continue
            worker = threading.Thread(target=self._serve, args=(conn, ip), name=f"jobsy-remote-{ip}", daemon=True)
            with self._lock:
                self._workers.add(worker)
            worker.start()

    def _reserve(self, conn, ip):
        with self._lock:
            if len(self._clients) >= self.max_total:
                return "límite global de conexiones"
            if sum(1 for v in self._clients.values() if v == ip) >= self.max_per_ip:
                return "límite de conexiones por IP"
            self._clients[conn] = ip
        return None

    def _release(self, conn):
        with self._lock:
            self._clients.pop(conn, None)
            self._workers.discard(threading.current_thread())
        self._close(conn)

    @staticmethod
    def _close(conn):
        try:
            conn.close()
        except OSError:
            pass

    def _reject_busy(self, conn):
        try:
            send_message(conn, error_response(
                None, "SERVICE_UNAVAILABLE", "conexion", "El servicio alcanzó su límite de conexiones remotas.",
                "Intente de nuevo en unos instantes."), timeout=REJECT_SEND_TIMEOUT)
        except (OSError, ProtocolError):
            pass
        self._close(conn)

    # ------------------------------------------------------------ atención
    def _serve(self, conn, ip):
        reader = MessageReader(conn)
        try:
            while not self._stop.is_set():
                try:
                    body = reader.read()
                    if body is None:                    # el cliente cerró limpiamente
                        break
                    request = validate_request(decode_body(body))
                    response, close = dispatch(self.manager, request)
                    send_message(conn, response)
                    if close:
                        break
                except ProtocolError as error:
                    # Un error de protocolo de una conexión no afecta a las demás ni a los trabajos.
                    try:
                        send_message(conn, error.to_response(), too_large_code="INTERNAL_ERROR")
                    except (OSError, ProtocolError):
                        break
                    if error.close:
                        break
        except IdleTimeout:
            logger.log("INFO", f"Conexión remota de {ip} cerrada por inactividad.")
        except (OSError, ConnectionError, TimeoutError):
            logger.log("INFO", f"Conexión remota de {ip} terminó de forma abrupta.")   # RF-22
        except Exception as error:
            logger.log("ERROR", f"Error inesperado en conexión remota de {ip}: {type(error).__name__}")
        finally:
            self._release(conn)