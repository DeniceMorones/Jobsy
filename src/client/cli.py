#cly.py
#interfaz de línea de comandos que procesa los argumentos del usuario, 
#invoca las acciones requeridas y muestra las respuestas o errores formateados en la terminal.
import argparse
import sys
import shlex

from src.daemon.job_manager import JobManager
from src.daemon.executor import Executor

def build_parser():
    parser = argparse.ArgumentParser(
        prog='jobsy',
        description="Jobsy: CLI para gestión de trabajos",
        epilog="Ejemplo: jobsy run -- sleep 10"
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

def main(manager: JobManager = None, executor: Executor = None):
    parser = build_parser()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(2) # código de salida 2 indica error de sintaxis

    args = parser.parse_args()

    # Instancias por defecto para ejecuciones directas
    if manager is None:
        manager = JobManager()
    if executor is None:
        executor = Executor(manager)

    try: 
        if args.subcommand == "run":
                    raw_command = args.command
                    if len(raw_command) == 1 and " " in raw_command[0]:
                        command_list = shlex.split(raw_command[0])
                    else:
                        command_list = raw_command

                    job = manager.create_job(command_list)
                    executor.execute(job)
                    print(f"Trabajo creado y enviado a ejecución con ID: {job.id}")
                    sys.exit(0)

        elif args.subcommand == "list":
            jobs = manager.list_jobs(status=args.status)
            if not jobs:
                print("No se encontraron trabajos.")
            else:
                for j in jobs:
                    print(f"ID: {j.id} | Estado: {j.status} | Comando: {' '.join(j.command)}")
            sys.exit(0)

        elif args.subcommand == "status":
                    job = manager.get_job(args.job_id)

                    def format_dt(dt):
                        return dt.strftime("%Y-%m-%d %H:%M:%S UTC") if dt else "-"

                    print(f"ID: {job.id}")
                    print(f"Estado: {job.status}")
                    print(f"Comando: {' '.join(job.command)}")
                    print(f"Recibido: {format_dt(job.received_at)}")
                    print(f"Inicio: {format_dt(job.started_at)}")
                    print(f"Fin: {format_dt(job.finished_at)}")
                    print(f"Código de salida: {job.exit_code if job.exit_code is not None else '-'}")
                    sys.exit(0)

        elif args.subcommand == "cancel":
            job = manager.cancel_job(args.job_id)
            print(f"Cancelando trabajo con ID: {job.id}")
            print(f"Estado actual: {job.status}")
            sys.exit(0)

        else:
            parser.print_help()
            sys.exit(2)

    except ValueError as ve:
        print(f"Error de validación: {ve}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()