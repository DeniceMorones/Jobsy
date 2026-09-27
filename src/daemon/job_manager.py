#cerebro de Jobsy create_job(), get_job(), list_jobs(), update_status()

from datetime import timezone, datetime
import uuid

from .job import Job
from ..protocol.validation import validate_command

class JobManager:
    def __init__(self):
        self.jobs: dict[str, Job] = {}
        
    def create_job(self, command: list[str]) -> Job: #va devolver un objeto Job
        validate_command(command)#la validacion antes que todo
       
        job_id = str(uuid.uuid4())
        
        job = Job(id = job_id, command = command)
        
        self.jobs[job_id] = job #se guarda el trabajo en el diccionario jobs, job_id seria el key
        #y referenciando ese key se puede acceder al objeto Job (Job guardaris los metadatos: job_id, command, ...)
        
        return job
    
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
            