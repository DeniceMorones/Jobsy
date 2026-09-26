#ejecutar procesos utilizar subprocees.Popen()

import subprocess
import threading

from .job import Job
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

            stdout, stderr = process.communicate()

            self.manager.mark_job_finished(
                job.id,
                process.returncode#este codigo lo retorna el proceso
            )

        except Exception:
            self.manager.mark_job_finished(
                job.id,
                1
            )