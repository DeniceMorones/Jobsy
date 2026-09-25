#cerebro de Jobsy create_job(), get_job(), list_jobs(), update_status()

import uuid

from .job import Job

class JobManager:
    def __init__(self):
        self.jobs: dict[str, Job] = {}
        
    def create_job(self, command: list[str]) -> Job: #va devolver un objeto Job
        job_id = str(uuid.uuid4())
        
        job = Job(id = job_id, command = command)
        
        self.jobs[job_id] = job #se guarda el trabajo en el diccionario jobs, job_id seria el key
        #y referenciando ese key se puede acceder al objeto Job (Job guardaris los metadatos: job_id, command, ...)
        
        return job