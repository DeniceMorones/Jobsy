"""Despachador del protocolo v1 (RF-18, RF-19).

Traduce solicitudes ya validadas (src.protocol.messages.validate_request) a llamadas de las
interfaces públicas del JobManager y devuelve el sobre de respuesta v1. No abre sockets, no crea
procesos ni toca el estado del gestor directamente (ADR-010). Los errores se convierten en
códigos estables con causas sanitizadas: nunca se reflejan tracebacks, rutas ni texto interno.
"""
import signal

from src.daemon.logger import logger, describe_command
from src.daemon.scheduler import QueueFullError
from src.protocol.messages import ok_response, error_response

STORAGE_ERROR_TEXT = "El servicio detuvo la ejecución por un error de almacenamiento."


def format_dt(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC") if dt else "-"


def diagnose(job):
    """Texto de diagnóstico derivado del estado y exit_code; None si no aplica (RF-29)."""
    code = job.exit_code
    if job.status == "CANCELED":
        return "cancelado por solicitud del usuario"
    if code is None or code == 0:
        return None
    if code < 0:
        try:
            name = signal.Signals(-code).name
        except ValueError:
            name = f"señal {-code}"
        return f"terminado inesperadamente por {name}"
    return f"terminó con código de salida {code}"


def _summary(job):
    return {"id": job.id, "status": job.status, "command": list(job.command)}


def _detail(job):
    return {"id": job.id, "command": list(job.command), "status": job.status,
            "received_at": format_dt(job.received_at), "started_at": format_dt(job.started_at),
            "finished_at": format_dt(job.finished_at), "exit_code": job.exit_code,
            "diagnostic": diagnose(job)}


def _health_item(job):
    return {"id": job.id, "status": job.status, "command": list(job.command),
            "received_at": format_dt(job.received_at), "started_at": format_dt(job.started_at),
            "finished_at": format_dt(job.finished_at), "exit_code": job.exit_code,
            "stderr": job.stderr}


def dispatch(manager, request):
    """Ejecuta la operación y devuelve (respuesta, cerrar_conexion)."""
    rid, action, params = request.request_id, request.action, request.params
    try:
        if action == "run":
            job = manager.submit_job(params["command"])
            logger.log("INFO", f"Solicitud v1 'run' procesada para comando: "
                               f"{describe_command(params['command'])} [ReqID: {rid}]", job_id=job.id)
            return ok_response(rid, job_id=job.id), False
        if action == "list":
            jobs = manager.list_jobs(status=params["status"])
            return ok_response(rid, jobs=[_summary(j) for j in jobs]), False
        if action == "status":
            return ok_response(rid, job=_detail(manager.snapshot(params["job_id"]))), False
        if action == "output":
            job = manager.snapshot(params["job_id"])
            return ok_response(rid, job_id=job.id, job_status=job.status,
                               stdout=job.stdout, stderr=job.stderr), False
        if action == "cancel":
            job = manager.cancel_job(params["job_id"])
            logger.log("INFO", f"Solicitud v1 'cancel' procesada [ReqID: {rid}]", job_id=job.id)
            return ok_response(rid, job_id=job.id, job_status=job.status), False
        if action == "health":
            h = manager.get_health_summary()
            return ok_response(rid, health={
                "service_active": h["service_active"],
                "storage_error": STORAGE_ERROR_TEXT if h["storage_error"] else None,
                "running_count": h["running_count"],
                "running_jobs": [_health_item(j) for j in h["running_jobs"]],
                "queued_count": h["queued_count"],
                "queued_jobs": [_health_item(j) for j in h["queued_jobs"]],
                "recent_errors_count": h["recent_errors_count"],
                "recent_errors": [_health_item(j) for j in h["recent_errors"]]}), False
        raise ValueError("acción sin despachador")      # no debería ocurrir tras validate_request
    except Exception as error:
        return _error_for(manager, request, error)


def _error_for(manager, request, error):
    rid, operation = request.request_id, request.action
    message = str(error)
    close = False
    if isinstance(error, QueueFullError):
        code, cause = "QUEUE_FULL", "Cola llena: no hay capacidad disponible."
        suggestion = "Espere a que finalicen los trabajos actuales o aumente la capacidad de la cola."
        logger.log("WARNING", f"Solicitud v1 '{operation}' rechazada por límite de capacidad [ReqID: {rid}]")
    elif isinstance(error, ValueError):
        if message.startswith("No existe un trabajo"):
            code, cause = "JOB_NOT_FOUND", "No existe un trabajo con ese identificador."
            suggestion = "Consulte los identificadores con 'jobsy list --full-id'."
        elif "es ambiguo" in message:
            code, cause = "AMBIGUOUS_JOB_ID", "El prefijo identifica varios trabajos."
            suggestion = "Utilice más caracteres o consulte 'jobsy list --full-id'."
        elif message.startswith(("La cancelación de este trabajo", "No se puede cancelar")):
            code, cause = "INVALID_JOB_STATE", message
            suggestion = "Consulte el estado del trabajo con 'jobsy status'."
        else:
            code, cause = "INVALID_REQUEST", "La solicitud no es válida para el estado actual del servicio."
            suggestion = "Revise los parámetros e intente de nuevo."
            logger.log("WARNING", f"Solicitud v1 '{operation}' rechazada: {message} [ReqID: {rid}]")
    elif manager.storage_error is not None:
        code, cause = "STORAGE_ERROR", STORAGE_ERROR_TEXT
        suggestion = "Consulte la bitácora del servicio y reinicie el daemon."
    elif not manager.is_accepting_jobs:
        code, cause = "SERVICE_UNAVAILABLE", "El servicio no está aceptando nuevos trabajos."
        suggestion = "El servicio se está deteniendo; intente más tarde."
    else:
        code, cause = "INTERNAL_ERROR", "Ocurrió un error interno al procesar la solicitud."
        suggestion = "Consulte la bitácora del servicio."
        close = True
        logger.log("ERROR", f"Excepción procesando solicitud v1 '{operation}' [ReqID: {rid}]: "
                            f"{type(error).__name__}: {message}")
    return error_response(rid, code, operation, cause, suggestion), close