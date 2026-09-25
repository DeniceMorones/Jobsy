#trabajo y metadatos
from dataclasses import dataclass
from datetime import datetime

@dataclass #genera el constructor y otros metodos automaticamente
class Job:
    id: str
    command: list[str]
    status: str = "QUEUED" #de mientras ya que una tarea inicia formada en la cola no entra ejecutandose
    
    received_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    
    exit_code: int | None = None
    