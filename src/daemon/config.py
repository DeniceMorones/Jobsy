"""Validated daemon configuration (RF-05)."""
import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class DaemonConfig:
    max_running: int = 3
    queue_capacity: int = 100

    def __post_init__(self):
        for name, minimum in (("max_running", 1), ("queue_capacity", 0)):
            value = getattr(self, name)
            if type(value) is not int or value < minimum:
                raise ValueError(f"{name} debe ser un entero >= {minimum}.")


def parse_config(argv=None):
    parser = argparse.ArgumentParser(prog="jobsy-daemon")
    parser.add_argument("--max-running", type=int, default=3)
    parser.add_argument("--queue-capacity", type=int, default=100)
    args = parser.parse_args(argv)
    try:
        return DaemonConfig(args.max_running, args.queue_capacity)
    except ValueError as error:
        parser.error(str(error))
