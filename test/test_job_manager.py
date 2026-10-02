from src.daemon.job_manager import JobManager


def main():
    manager = JobManager() ##Crear administrador

    print("=== CREANDO TRABAJOS ===")

    job1 = manager.create_job(["echo", "Hola"]) ##Crear trabajo 1
    job2 = manager.create_job(["sleep", "1"]) ##Crear trabajo 2

    print("Job 1:", job1.id, job1.status) #Obtener status trabajo 1
    print("Job 2:", job2.id, job2.status) #Obtener status trabajo 1

    print("\n=== GET_JOB CON ID VALIDO ===") ##TC-015 Consultar trabajo por ID válido

    found = manager.get_job(job1.id)

    print("ID buscado:", job1.id)
    print("ID encontrado:", found.id)
    print("Comando:", found.command)
    print("Estado:", found.status)

    print("\n=== GET_JOB CON ID INEXISTENTE ===") ##TC-016 Rechazar consulta con ID inexistente

    try:
        manager.get_job("id-que-no-existe")
        print("ERROR: se esperaba una excepción")
    except ValueError as error:
        print("CORRECTO: se rechazó el ID inexistente")
        print("Motivo:", error)

    print("\n=== LIST_JOBS SIN FILTRO ===") ##TC-017 Listar todos los trabajos

    jobs = manager.list_jobs()

    print("Cantidad:", len(jobs))

    for job in jobs:
        print(job.id, job.command, job.status)

    print("\n=== LIST_JOBS FILTRANDO QUEUED ===")##TC-018 Filtrar trabajos por estado

    queued_jobs = manager.list_jobs("QUEUED")

    print("Cantidad:", len(queued_jobs))

    for job in queued_jobs:
        print(job.id, job.command, job.status)

    print("\n=== LIST_JOBS CON ESTADO INVALIDO ===") ##TC-019 Rechazar filtro con estado inválido

    try:
        manager.list_jobs("ESTADO_INEXISTENTE")
        print("ERROR: se esperaba una excepción")
    except ValueError as error:
        print("CORRECTO: se rechazó el estado inválido")
        print("Motivo:", error)


if __name__ == "__main__":
    main()