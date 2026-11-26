#cly.py
#interfaz de línea de comandos que procesa los argumentos del usuario, 
#invoca las acciones requeridas y muestra las respuestas o errores formateados en la terminal.
import os
import sys
import json
import shlex
import socket
import argparse

from src.protocol.endpoint import client_socket_path
from src.protocol.job_ids import short_job_id
from src.protocol.messages import (
    IdleTimeout, MessageReader, ProtocolError, build_request, decode_body,
    new_request_id, send_message, validate_response, RESPONSE_TIMEOUT)

DEFAULT_REMOTE_PORT = 8765
CONNECT_TIMEOUT = 5.0

def build_parser():
    parser = argparse.ArgumentParser(
        prog='jobsy',
        description="Jobsy: CLI para gestión de trabajos",
    )

    # RF-18: acceso remoto opcional. Sin --host se usa el socket Unix local, igual que siempre.
    parser.add_argument("--host", default=os.environ.get("JOBSY_HOST"),
                        help="IP del daemon remoto en la red privada (o variable JOBSY_HOST)")
    parser.add_argument("--port", type=int, default=int(os.environ.get("JOBSY_PORT", DEFAULT_REMOTE_PORT)),
                        help=f"Puerto del daemon remoto (predeterminado: {DEFAULT_REMOTE_PORT}, o JOBSY_PORT)")

    subparsers = parser.add_subparsers(dest="subcommand", help="Comandos disponibles")

    # comando run
    run_parser = subparsers.add_parser("run", help="Ejecuta un trabajo")
    run_parser.add_argument("command", nargs="+", help="Comando a ejecutar")

    # comando list
    list_parser = subparsers.add_parser("list", help="Lista los trabajos")
    list_parser.add_argument("--status", choices=["QUEUED", "RUNNING", "SUCCEEDED", "FAILED", "CANCELED"])

    list_parser.add_argument("--full-id", action="store_true",
                             help="Muestra los UUID completos en lugar de IDs cortos")

    # comando status
    status_parser = subparsers.add_parser("status", help="Muestra el estado de un trabajo")
    status_parser.add_argument("job_id", help="UUID completo o prefijo hexadecimal único de al menos 8 caracteres")

    # comando cancel
    cancel_parser = subparsers.add_parser("cancel", help="Cancela un trabajo")
    cancel_parser.add_argument("job_id", help="UUID completo o prefijo hexadecimal único de al menos 8 caracteres")
    
    # comando output
    output_parser = subparsers.add_parser("output", help="Muestra stdout y stderr de un trabajo")
    output_parser.add_argument("job_id", help="UUID completo o prefijo hexadecimal único de al menos 8 caracteres")

    # comando health
    health_parser = subparsers.add_parser("health", help="Muestra el resumen de salud del servicio y estado de los trabajos")


    return parser

def send_ipc_request(payload: dict) -> dict:
    """Envía la petición en JSON al socket UNIX y retorna la respuesta."""
    socket_path = client_socket_path()
    if not os.path.exists(socket_path):
        print("Error: El servicio Jobsy no está en ejecución.", file=sys.stderr)
        sys.exit(1)

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(socket_path)
        client_socket.sendall(json.dumps(payload).encode("utf-8"))
        response_data = _recv_all(client_socket)
        return json.loads(response_data.decode("utf-8"))
    
def send_remote_request(host, port, payload: dict) -> dict:
    """Envía la petición por TCP con el protocolo v1 y valida la respuesta (RF-18, RF-19)."""
    action = payload["action"]
    fields = {k: v for k, v in payload.items() if k != "action" and v is not None}
    request_id = new_request_id()
    try:
        with socket.create_connection((host, port), timeout=CONNECT_TIMEOUT) as sock:
            send_message(sock, build_request(action, request_id, **fields))
            body = MessageReader(sock, idle_timeout=RESPONSE_TIMEOUT).read()
            if body is None:
                raise ProtocolError("INVALID_RESPONSE", "El servidor cerró la conexión sin responder.",
                                    "Verifique que el daemon siga activo e intente de nuevo.", operation=action)
            return validate_response(decode_body(body), request_id)
    except ProtocolError as error:
        return {"status": "error", "operation": action, "cause": error.cause, "suggestion": error.suggestion}
    except IdleTimeout:
        return {"status": "error", "operation": action,
                "cause": "El servidor no respondió a tiempo.", "suggestion": "Verifique el daemon y la red."}
    except (OSError, TimeoutError):
        return {"status": "error", "operation": action,
                "cause": f"No se pudo comunicar con {host}:{port}.",
                "suggestion": "Verifique que el daemon tenga --listen-host, que la IP esté permitida (--allow-cidr) "
                              "y que ambos equipos estén en la misma red privada."}


def send_request(args, payload: dict) -> dict:
    """Transporte único para todos los comandos: remoto si hay --host, local en caso contrario."""
    if getattr(args, "host", None):
        return send_remote_request(args.host, args.port, payload)
    return send_ipc_request(payload)


def _recv_all(sock):
    chunks = []
    while True:
        chunk = sock.recv(65536)
        if not chunk:
            break
        chunks.append(chunk)
        try:
            json.loads(b"".join(chunks).decode("utf-8"))
            break
        except (ValueError, UnicodeDecodeError):
            continue
    return b"".join(chunks)

# Función auxiliar para manejar respuestas de error estructuradas
def handle_error_response(res):
    """Renderiza el error estructurado recibido directamente del servidor (RNF-21)."""
    print(f"Error en la operación '{res.get('operation', 'desconocida')}':", file=sys.stderr)
    print(f"  • Causa: {res.get('cause', res.get('message', 'Error desconocido'))}", file=sys.stderr)
    print(f"  • Acción sugerida: {res.get('suggestion', 'Verifique la sintaxis o el estado del servicio.')}", file=sys.stderr)
    sys.exit(1)


def main(argv=None, *, split_command_string=True):
    """Run the CLI; retain legacy single-string parsing unless disabled."""
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()

    if not argv:
        parser.print_help()
        sys.exit(2)  # código de salida 2 indica error de sintaxis

    args = parser.parse_args(argv)
    if args.host and not 1 <= args.port <= 65535:
        parser.error("--port debe estar entre 1 y 65535.")

    try:
        if args.subcommand == "run":
            raw_command = args.command
            if split_command_string and len(raw_command) == 1 and " " in raw_command[0]:
                command_list = shlex.split(raw_command[0])
            else:
                command_list = raw_command

            res = send_request(args, {"action": "run", "command": command_list})
            if res["status"] == "ok":
                print(f"Trabajo creado y enviado a ejecución con ID: {short_job_id(res['job_id'])}")
                sys.exit(0)
            else:
                handle_error_response(res)

        elif args.subcommand == "list":
            res = send_request(args, {"action": "list", "status": args.status})
            if res["status"] == "ok":
                jobs = res["jobs"]
                if not jobs:
                    print("No se encontraron trabajos.")
                else:
                    for j in jobs:
                        display_id = j['id'] if args.full_id else short_job_id(j['id'])
                        print(f"ID: {display_id} | Estado: {j['status']} | Comando: {' '.join(j['command'])}")
                sys.exit(0)
            else:
                handle_error_response(res)

        #rf-24: Resumen de salud del servicio y estado de los trabajos
        elif args.subcommand == "health":
                res = send_request(args, {"action": "health"})
                if res["status"] == "ok":
                    h = res["health"]
                    print(f"=== Resumen de Salud de Jobsy ===")
                    print(f"Servicio Activo: {'Sí' if h['service_active'] else 'No'}")
                    if h['storage_error']:
                        print(f"Error de Almacenamiento: {h['storage_error']}")
                    print(f"\n--- Trabajos en Ejecución ({h['running_count']}) ---")
                    if not h['running_jobs']:
                        print("  Ninguno")
                    else:
                        for j in h['running_jobs']:
                            print(f"  ID: {short_job_id(j['id'])} | Comando: {' '.join(j['command'])} | Inicio: {j['started_at']}")

                    print(f"\n--- Trabajos en Cola ({h['queued_count']}) ---")
                    if not h['queued_jobs']:
                        print("  Ninguno")
                    else:
                        for j in h['queued_jobs']:
                            print(f"  ID: {short_job_id(j['id'])} | Comando: {' '.join(j['command'])} | Recibido: {j['received_at']}")

                    print(f"\n--- Errores Recientes ({h['recent_errors_count']}) ---")
                    if not h['recent_errors']:
                        print("  Ninguno")
                    else:
                        for j in h['recent_errors']:
                            print(f"  ID: {short_job_id(j['id'])} | Comando: {' '.join(j['command'])} | Código: {j['exit_code']} | Fin: {j['finished_at']}")
                    sys.exit(0)
                else:
                    handle_error_response(res)

        elif args.subcommand == "status":
            res = send_request(args, {"action": "status", "job_id": args.job_id})
            if res["status"] == "ok":
                j = res["job"]
                print(f"ID: {short_job_id(j['id'])}")
                print(f"Estado: {j['status']}")
                print(f"Comando: {' '.join(j['command'])}")
                print(f"Recibido: {j['received_at']}")
                print(f"Inicio: {j['started_at']}")
                print(f"Fin: {j['finished_at']}")
                print(f"Código de salida: {j['exit_code'] if j['exit_code'] is not None else '-'}")
                if j.get("diagnostic"):
                    print(f"Diagnóstico: {j['diagnostic']}")
                sys.exit(0)
            else:
                handle_error_response(res)

        elif args.subcommand == "cancel":
            res = send_request(args, {"action": "cancel", "job_id": args.job_id})
            if res["status"] == "ok":
                print(f"Cancelando trabajo con ID: {short_job_id(res['job_id'])}")
                print(f"Estado actual: {res['job_status']}")
                sys.exit(0)
            else:
                handle_error_response(res)
        
        elif args.subcommand == "output":
            res = send_request(args, {"action": "output", "job_id": args.job_id})
            if res["status"] == "ok":
                sys.stdout.write(res["stdout"])
                sys.stderr.write(res["stderr"])
                sys.exit(0)
            else:
                handle_error_response(res)

        else:
            parser.print_help()
            sys.exit(2)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def execute_main(argv=None):
    """Submit literal command arguments through the existing run action."""
    argv = list(sys.argv[1:] if argv is None else argv)
    return main(["run", "--", *argv], split_command_string=False)


def list_main(argv=None):
    """Delegate the short list command to the existing CLI."""
    return main(["list", *(sys.argv[1:] if argv is None else argv)])


def status_main(argv=None):
    """Delegate the short status command to the existing CLI."""
    return main(["status", *(sys.argv[1:] if argv is None else argv)])


def cancel_main(argv=None):
    """Delegate the short cancel command to the existing CLI."""
    return main(["cancel", *(sys.argv[1:] if argv is None else argv)])


if __name__ == "__main__":
    main()