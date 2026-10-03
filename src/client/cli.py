#cly.py
#interfaz de línea de comandos que procesa los argumentos del usuario, 
#invoca las acciones requeridas y muestra las respuestas o errores formateados en la terminal.
import os
import sys
import json
import shlex
import socket
import argparse

SOCKET_PATH = "/tmp/jobsy.sock"

def build_parser():
    parser = argparse.ArgumentParser(
        prog='jobsy',
        description="Jobsy: CLI para gestión de trabajos",
    )

    subparsers = parser.add_subparsers(dest="subcommand", help="Comandos disponibles")

    # comando run
    run_parser = subparsers.add_parser("run", help="Ejecuta un trabajo")
    run_parser.add_argument("command", nargs="+", help="Comando a ejecutar")

    # comando list
    list_parser = subparsers.add_parser("list", help="Lista los trabajos")
    list_parser.add_argument("--status", choices=["QUEUED", "RUNNING", "SUCCEEDED", "FAILED", "CANCELED"])

    # comando status
    status_parser = subparsers.add_parser("status", help="Muestra el estado de un trabajo")
    status_parser.add_argument("job_id", help="ID del trabajo")

    # comando cancel
    cancel_parser = subparsers.add_parser("cancel", help="Cancela un trabajo")
    cancel_parser.add_argument("job_id", help="ID del trabajo")

    return parser

def send_ipc_request(payload: dict) -> dict:
    """Envía la petición en JSON al socket UNIX y retorna la respuesta."""
    if not os.path.exists(SOCKET_PATH):
        print("Error: El servicio Jobsy no está en ejecución.", file=sys.stderr)
        sys.exit(1)

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(SOCKET_PATH)
        client_socket.sendall(json.dumps(payload).encode("utf-8"))
        response_data = client_socket.recv(4096)
        return json.loads(response_data.decode("utf-8"))

def main():
    parser = build_parser()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(2)  # código de salida 2 indica error de sintaxis

    args = parser.parse_args()

    try:
        if args.subcommand == "run":
            raw_command = args.command
            if len(raw_command) == 1 and " " in raw_command[0]:
                command_list = shlex.split(raw_command[0])
            else:
                command_list = raw_command

            res = send_ipc_request({"action": "run", "command": command_list})
            if res["status"] == "ok":
                print(f"Trabajo creado y enviado a ejecución con ID: {res['job_id']}")
                sys.exit(0)
            else:
                print(f"Error de validación: {res['message']}", file=sys.stderr)
                sys.exit(1)

        elif args.subcommand == "list":
            res = send_ipc_request({"action": "list", "status": args.status})
            if res["status"] == "ok":
                jobs = res["jobs"]
                if not jobs:
                    print("No se encontraron trabajos.")
                else:
                    for j in jobs:
                        print(f"ID: {j['id']} | Estado: {j['status']} | Comando: {' '.join(j['command'])}")
                sys.exit(0)
            else:
                print(f"Error: {res['message']}", file=sys.stderr)
                sys.exit(1)

        elif args.subcommand == "status":
            res = send_ipc_request({"action": "status", "job_id": args.job_id})
            if res["status"] == "ok":
                j = res["job"]
                print(f"ID: {j['id']}")
                print(f"Estado: {j['status']}")
                print(f"Comando: {' '.join(j['command'])}")
                print(f"Recibido: {j['received_at']}")
                print(f"Inicio: {j['started_at']}")
                print(f"Fin: {j['finished_at']}")
                print(f"Código de salida: {j['exit_code'] if j['exit_code'] is not None else '-'}")
                sys.exit(0)
            else:
                print(f"Error de validación: {res['message']}", file=sys.stderr)
                sys.exit(1)

        elif args.subcommand == "cancel":
            res = send_ipc_request({"action": "cancel", "job_id": args.job_id})
            if res["status"] == "ok":
                print(f"Cancelando trabajo con ID: {res['job_id']}")
                print(f"Estado actual: {res['job_status']}")
                sys.exit(0)
            else:
                print(f"Error de validación: {res['message']}", file=sys.stderr)
                sys.exit(1)

        else:
            parser.print_help()
            sys.exit(2)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()