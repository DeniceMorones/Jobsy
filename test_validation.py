from src.daemon.job_manager import JobManager


manager = JobManager()

tests = [
    [],
    "",
    ["", "10"],
    ["sleep", 10],
    ["echo", "Hola"]
]

for command in tests:

    try:
        job = manager.create_job(command)
        print(f"ACEPTADO: {job.command}")

    except ValueError as error:
        print(f"RECHAZADO: {command}")
        print(f"Motivo: {error}")