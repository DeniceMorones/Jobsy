"""Short job references without changing durable UUID identities."""
import re
from collections.abc import Collection

SHORT_ID_LENGTH = 8
_UUID = re.compile(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}")
_PREFIX = re.compile(r"[0-9a-fA-F]{8,32}")


def short_job_id(job_id: str) -> str:
    """Display eight UUID characters; preserve non-UUID legacy identifiers."""
    return job_id[:SHORT_ID_LENGTH].lower() if _UUID.fullmatch(job_id) else job_id


def resolve_job_id(job_id: str, known_ids: Collection[str]) -> str:
    """Resolve against the complete registry while its owner holds the lock.

    Exact identifiers take precedence. UUID prefixes must match exactly one
    record, including terminal history. Never choose the first ambiguous match.
    """
    if not isinstance(job_id, str):
        raise ValueError("El ID del trabajo debe ser texto.")
    if job_id in known_ids:
        return job_id
    if _UUID.fullmatch(job_id):
        canonical = job_id.lower()
        if canonical in known_ids:
            return canonical
    elif _PREFIX.fullmatch(job_id):
        prefix = job_id.lower()
        match = None
        for candidate in known_ids:
            if _UUID.fullmatch(candidate) and candidate.replace("-", "").lower().startswith(prefix):
                if match is not None:
                    raise ValueError(
                        f"El ID corto '{job_id}' es ambiguo. Use más caracteres o "
                        "el UUID completo; consulte 'jobsy list --full-id'."
                    )
                match = candidate
        if match is not None:
            return match
    else:
        raise ValueError(
            "Use un UUID completo o un prefijo de 8 a 32 caracteres "
            "hexadecimales sin guiones; consulte 'jobsy list --full-id'."
        )
    raise ValueError(f"No existe un trabajo con el ID '{job_id}'.")
