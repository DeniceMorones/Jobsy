#archivo temporal para probar el executor y el job manager
import time

from src.daemon.job_manager import JobManager
from src.daemon.executor import Executor


manager = JobManager()
executor = Executor(manager)

job1 = manager.create_job(["sleep", "10"])
job2 = manager.create_job(["echo", "Hola desde Jobsy"])

executor.execute(job1)
executor.execute(job2)

print("Jobsy sigue disponible!")

time.sleep(1)

print(job1)
print(job2)

time.sleep(10)

print("\nDespues de esperar:")
print(job1)
print(job2)

print("\nSalida del job 2:")
print(job2.stdout)

print("Errores del job 2:")
print(job2.stderr)

job3 = manager.create_job(["ls", "/carpeta-que-no-existe"])
executor.execute(job3)

time.sleep(1)

print(job3)
print("STDOUT:", job3.stdout)
print("STDERR:", job3.stderr)