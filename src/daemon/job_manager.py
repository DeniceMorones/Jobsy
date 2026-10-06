#cerebro de Jobsy create_job(), get_job(), list_jobs(), update_status()

from datetime import datetime, timezone
import time
import subprocess
import uuid

from .job import Job
from ..protocol.validation import validate_command

class JobManager:
    def __init__(self):
        self.jobs: dict[str, Job] = {}
        self.is_accepting_jobs: bool = True #bandera para cumplir con el RF-15
        
    def create_job(self, command: list[str]) -> Job: #va devolver un objeto Job

        #si no se esta aceptando trabajos, se lanza un error
        if not self.is_accepting_jobs:
            raise RuntimeError(
                "El JobManager no esta aceptando nuevos trabajos."
            )
        
        validate_command(command)#la validacion antes que todo
       
        job_id = str(uuid.uuid4())
        
        job = Job(id = job_id, command = command)
        
        self.jobs[job_id] = job #se guarda el trabajo en el diccionario jobs, job_id seria el key
        #y referenciando ese key se puede acceder al objeto Job (Job guardaris los metadatos: job_id, command, ...)
        
        return job
    
    #detiene la aceptación de trabajos y cancela los activos
    def shutdown(self, timeout: float = 5.0) -> None:
        self.is_accepting_jobs = False

        #cancela los trabajos que estan en la cola
        for job in list(self.jobs.values()):
            if job.status == "QUEUED":
                self.cancel_job(job.id)

        #espera a que los trabajos activos terminen
        start_time = time.time()
        while time.time() - start_time < timeout:
            running_jobs = [j for j in self.jobs.values() if j.status == "RUNNING"]
            if not running_jobs:
                break #todos los procesos terminaron de forma limpia
            time.sleep(0.2) #espera un poco antes de volver a verificar

        #forzar la cancelacion de procesos que no temrinaron a tiempo
        for job in list(self.jobs.values()):
            if job.status == "RUNNING":
                try:
                    self.cancel_job(job.id)
                except Exception:
                    pass

    def mark_job_started(self, job_id: str) -> None:
        job = self.jobs[job_id]
        
        job.status = "RUNNING"
        job.started_at = datetime.now(timezone.utc)
    
    def mark_job_finished(
        self,
        job_id: str,
        exit_code: int
        ) -> None:
        
        job = self.jobs[job_id]
        
        job.finished_at = datetime.now(timezone.utc)
        job.exit_code = exit_code
        
        if exit_code == 0:
            job.status = "SUCCEEDED"
        else:
            job.status = "FAILED"
            
    def get_job(self, job_id: str) -> Job:

        job = self.jobs.get(job_id)

        if job is None:
            raise ValueError(
                f"No existe un trabajo con el ID '{job_id}'."
            )

        return job
    
    def list_jobs(self, status: str | None = None) -> list[Job]:

        jobs = list(self.jobs.values())

        if status is None:
            return jobs

        status = status.upper()

        valid_statuses = {
            "QUEUED",
            "RUNNING",
            "SUCCEEDED",
            "FAILED",
            "CANCELED"
        }

        if status not in valid_statuses:
            raise ValueError(
                f"Estado no valido: '{status}'."
            )

        return [
            job
            for job in jobs
            if job.status == status
        ]
    def cancel_job(self, job_id: str) -> Job:
        job = self.get_job(job_id)

        if job.status in {"SUCCEEDED", "FAILED", "CANCELED"}:
            raise ValueError(
                f"No se puede cancelar un trabajo con estado '{job.status}'."
            )
        
        #si el trabajo esta en la cola
        if job.status == "QUEUED":
            job.status = "CANCELED"
            job.finished_at = datetime.now(timezone.utc)
            return job

        #si el trabajo esta en ejecucion
        if job.status == "RUNNING":
            job.status = "CANCELED"
            job.finished_at = datetime.now(timezone.utc)

            if job.process is not None:
                #intenta terminación SIGTERM
                job.process.terminate()

                #espera la respuesta del proceso
                try:
                    job.process.wait(timeout=2.0)
                except subprocess.TimeoutExpired:
                    #si no responde, fuerza la terminación SIGKILL
                    job.process.kill()
            return job

                