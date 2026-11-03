"""Read-only Linux process identity; never signal or adopt historical PIDs."""
from pathlib import Path


def boot_id():
    value = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
    if not value:
        raise RuntimeError("No se pudo identificar el arranque Linux.")
    return value


def process_identity(pid):
    # comm may contain spaces and parentheses: split after its last closing ')'.
    text = Path(f"/proc/{pid}/stat").read_text()
    fields = text[text.rfind(")") + 2:].split()
    return fields[0], int(fields[19])  # state (3), starttime (22)


def absence_confirmed(execution, session, current_boot):
    old_boot = execution["boot_id"] or (session or {}).get("boot_id")
    if old_boot is None:
        return False
    if old_boot != current_boot:
        return True
    pid, ticks = execution["pid"], execution["process_start_ticks"]
    if pid is None or ticks is None:
        # Includes the crash window after Popen but before identity commit.
        return False
    try:
        state, observed_ticks = process_identity(pid)
    except FileNotFoundError:
        return True
    except (OSError, ValueError, IndexError):
        return False
    return observed_ticks != ticks or state in {"Z", "X"}
