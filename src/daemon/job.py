#trabajo y metadatos
from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass #genera el constructor y otros metodos automaticamente
class Job:
    id: str
    command: list[str]
    status: str = "QUEUED" #de mientras ya que una tarea inicia formada en la cola no entra ejecutandose
    
    received_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc)) #cuando se creo el trabajo, se inicializa con la fecha actual
    started_at: datetime | None = None
    finished_at: datetime | None = None
    
    exit_code: int | None = None
    