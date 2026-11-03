"""Conservative durable-history reconciliation, without command reexecution."""
from datetime import datetime, timezone
from .process_identity import absence_confirmed, boot_id


class RecoveryBlocked(RuntimeError):
    pass


class RecoveryService:
    def __init__(self, repository, *, current_boot=None, probe=absence_confirmed):
        self.repository = repository
        self.current_boot = current_boot or boot_id()
        self.probe = probe

    def recover(self):
        records = self.repository.list_jobs()
        sessions = {row["id"]: row for row in self.repository.list_sessions()}
        blocked = []
        for record in records:
            execution = record["execution"]
            uncertain = (execution["cleanup_pending"] or record["status"] == "RUNNING"
                         or (record["status"] == "QUEUED" and execution["launch_intent_at"]))
            if uncertain and not self.probe(
                    execution, sessions.get(execution["session_id"]), self.current_boot):
                blocked.append(record["id"])
        if blocked:
            raise RecoveryBlocked(
                "Recuperación bloqueada: proceso superviviente o lanzamiento incierto para "
                + ", ".join(blocked)
                + ". No se ejecutará trabajo nuevo. No borre registros ni mate PIDs sin verificar.")
        now = datetime.now(timezone.utc)
        for record in records:
            execution = record["execution"]
            if record["status"] == "QUEUED" and not execution["launch_intent_at"]:
                self.repository.reconcile_job(record["id"], record["version"],
                    status="CANCELED", at=now, reason="restart_before_execution",
                    finished_at=now)
            elif record["status"] in {"QUEUED", "RUNNING"} or execution["cleanup_pending"]:
                status = record["status"] if record["status"] in {
                    "SUCCEEDED", "FAILED", "CANCELED"} else "FAILED"
                self.repository.reconcile_job(record["id"], record["version"],
                    status=status, at=now, reason="supervision_lost_process_absent",
                    preserve_results=record["status"] in {"SUCCEEDED", "FAILED", "CANCELED"})
        return self.repository.list_jobs()
