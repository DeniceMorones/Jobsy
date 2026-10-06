#ejecutar procesos utilizar subprocees.Popen()

import subprocess
from sys import stderr
import threading

from .job import Job
from src.daemon import job
from .job_manager import JobManager

class Executor:

    def __init__(self, manager: JobManager):#constructor
        self.manager = manager

    def execute(self, job: Job) -> None:#no retorna ningun valor

        thread = threading.Thread(#funcion para ejecutar un hilo en paralelo, con esto no bloqueamos el flujo de atender otros procesos
            target=self._run_job,#nota: poner una funcio  con () hace que se ejecute inmediatamente, por eso no se pone () para que se ejecute cuando el hilo lo indique
            args=(job,),
            daemon=True#hilo que trabaja en segundo plano
        )

        thread.start()#empezar el hilo

    def _run_job(self, job: Job) -> None:

        self.manager.mark_job_started(job.id)

        try:
            process = subprocess.Popen(#popen para los subprocesos, permite ejecutar otros programas y comandos
                job.command,
                stdout=subprocess.PIPE,#salidas normales/correctas, el programa capturaria el contenido
                stderr=subprocess.PIPE,#errores
                text=True
            )

            #se asigna la referencia al proceso activo
            job.process = process

            stdout, stderr = process.communicate()
            
            job.stdout = stdout
            job.stderr = stderr

            ## Si el trabajo ya fue marcado como CANCELED por cancel_job(), respetamos ese estado
            if job.status != "CANCELED":
                self.manager.mark_job_finished(
                    job.id,
                    process.returncode#este codigo lo retorna el proceso
                )

        #si es diferente de CANCELED, se marca como finalizado
        except Exception:
            if job.status != "CANCELED":
                self.manager.mark_job_finished(
                    job.id,
                    1
                )
        finally:
            job.process = None #se limpia la referencia al finalizar
        