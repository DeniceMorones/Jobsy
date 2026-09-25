#trabajo y metadatos
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Job:
    id: str
    command: list[str]
    status: str
    
    received_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    
    exit_code: int | None = None
    