"""Data-directory ownership and persistent daemon session lifecycle."""
from datetime import datetime, timezone
import os
from pathlib import Path
import uuid

from .job_repository import JobRepository
from .process_identity import boot_id
from .recovery import RecoveryService
from .logger import logger


class PersistenceRuntime:
    def __init__(self, directory):
        self.directory = Path(directory).expanduser().resolve()
        self.repository = None
        self._lock_file = None
        self.session_id = None
        self.records = []
        self.boot_id = None

    def open(self):
        import fcntl
        self.directory.mkdir(mode=0o700, parents=True, exist_ok=True)

        #se configura la bitacora centralizada (RF-14)
        logger.setup(self.directory)
        
        try:
            # Never unlink this inode: all daemon instances must lock the same file.
            descriptor = os.open(self.directory / "daemon.lock", os.O_RDWR | os.O_CREAT, 0o600)
            self._lock_file = os.fdopen(descriptor, "a+")
            try:
                fcntl.flock(self._lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise RuntimeError("El directorio de datos ya pertenece a otro daemon.") from error
            self.boot_id = boot_id()
            self.repository = JobRepository(self.directory / "jobsy.sqlite3")
            self.records = RecoveryService(self.repository, current_boot=self.boot_id).recover()
            session_id = str(uuid.uuid4())
            self.repository.start_session(session_id,
                started_at=datetime.now(timezone.utc), boot_id=self.boot_id, daemon_pid=os.getpid())
            self.session_id = session_id
            logger.log("INFO", f"Iniciando sesión de daemon con ID: {session_id}")
            return self
        except BaseException:
            self.close()
            raise

    def close(self, *, clean=False):
        try:
            if self.repository is not None:
                try:
                    if self.session_id is not None:
                        self.repository.finish_session(self.session_id,
                            finished_at=datetime.now(timezone.utc), clean_shutdown=clean)
                        logger.log("INFO", f"Finalizando sesión de daemon con ID: {self.session_id} (clean={clean})")
                        
                finally:
                    self.repository.close()
        finally:
            self.repository = None
            self.session_id = None
            if self._lock_file is not None:
                self._lock_file.close()
                self._lock_file = None
