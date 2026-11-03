#!/usr/bin/env python3

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


failures = 0


def section(title):
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def check(condition, message):
    global failures

    if condition:
        print(f"PASS: {message}")
    else:
        print(f"FAIL: {message}")
        failures += 1


def run(command, cwd=None, env=None):
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def main():
    global failures

    repo_root = Path(__file__).resolve().parents[1]

    with tempfile.TemporaryDirectory(
        prefix="jobsy-clean-install-"
    ) as temp_dir:

        temp = Path(temp_dir)
        clone_dir = temp / "Jobsy"
        venv_dir = clone_dir / ".venv-clean"

        # ----------------------------------------------------------
        section("TC-141 - CREAR CLON LIMPIO DEL REPOSITORIO")
        # ----------------------------------------------------------

        clone = run(
            [
                "git",
                "clone",
                "--quiet",
                "--no-local",
                str(repo_root),
                str(clone_dir),
            ]
        )

        check(
            clone.returncode == 0,
            "El repositorio puede clonarse desde cero.",
        )

        if clone.returncode != 0:
            print("STDOUT:")
            print(clone.stdout)
            print("STDERR:")
            print(clone.stderr)

            section("RESULTADO GENERAL")
            print(
                f"RESULTADO GENERAL: FAIL "
                f"({failures} comprobaciones fallidas)"
            )
            return 1

        status = run(
            ["git", "status", "--porcelain"],
            cwd=clone_dir,
        )

        check(
            status.returncode == 0
            and not status.stdout.strip(),
            "El clon inicia con working tree limpio.",
        )

        head = run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=clone_dir,
        )

        if head.returncode == 0:
            print(f"Commit probado: {head.stdout.strip()}")

        # ----------------------------------------------------------
        section("TC-142 - CREAR ENTORNO VIRTUAL DESDE EL CLON LIMPIO")
        # ----------------------------------------------------------

        create_venv = run(
            [
                sys.executable,
                "-m",
                "venv",
                str(venv_dir),
            ],
            cwd=clone_dir,
        )

        check(
            create_venv.returncode == 0,
            "Se crea un entorno virtual nuevo desde el clon limpio.",
        )

        venv_python = venv_dir / "bin" / "python"
        venv_pip = venv_dir / "bin" / "pip"

        check(
            venv_python.exists() and venv_pip.exists(),
            "El entorno virtual contiene Python y pip.",
        )

        # ----------------------------------------------------------
        section("TC-143 - INSTALAR JOBSY SIN PRIVILEGIOS ROOT")
        # ----------------------------------------------------------

        uid = os.geteuid()

        print(f"UID de ejecución: {uid}")

        check(
            uid != 0,
            "La prueba se ejecuta como usuario sin privilegios root.",
        )

        install_env = os.environ.copy()

        # Evita únicamente el aviso informativo de actualización de pip.
        # No silencia warnings del paquete o del proceso de construcción.
        install_env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"

        install = run(
            [
                str(venv_python),
                "-m",
                "pip",
                "install",
                "--no-input",
                ".",
            ],
            cwd=clone_dir,
            env=install_env,
        )

        print(f"Exit code instalación: {install.returncode}")

        check(
            install.returncode == 0,
            "Jobsy se instala correctamente desde el clon limpio.",
        )

        check(
            "sudo" not in " ".join(install.args),
            "La instalación no utiliza sudo.",
        )

        pip_show = run(
            [
                str(venv_python),
                "-m",
                "pip",
                "show",
                "jobsy",
            ],
            cwd=clone_dir,
            env=install_env,
        )

        check(
            pip_show.returncode == 0,
            "Jobsy queda instalado dentro del entorno virtual.",
        )

        location = None

        for line in pip_show.stdout.splitlines():
            if line.startswith("Location:"):
                location = line.split(":", 1)[1].strip()
                break

        if location:
            print(f"Location instalada: {location}")

        check(
            location is not None
            and str(venv_dir) in location,
            "La instalación queda contenida dentro del entorno virtual del usuario.",
        )

        # ----------------------------------------------------------
        section("TC-144 - INSTALACION LIMPIA SIN ADVERTENCIAS")
        # ----------------------------------------------------------

        install_output = install.stdout + "\n" + install.stderr

        warning_patterns = [
            r"(?im)^\s*WARNING:",
            r"(?im)^\s*ERROR:",
            r"\bDeprecationWarning\b",
            r"\bFutureWarning\b",
            r"\bRuntimeWarning\b",
            r"\bUserWarning\b",
            r"\bSetuptoolsDeprecationWarning\b",
        ]

        warnings_found = []

        for pattern in warning_patterns:
            for match in re.finditer(pattern, install_output):
                line_start = install_output.rfind(
                    "\n",
                    0,
                    match.start(),
                ) + 1

                line_end = install_output.find(
                    "\n",
                    match.start(),
                )

                if line_end == -1:
                    line_end = len(install_output)

                line = install_output[
                    line_start:line_end
                ].strip()

                if line and line not in warnings_found:
                    warnings_found.append(line)

        if warnings_found:
            print("Advertencias/errores detectados:")

            for warning in warnings_found:
                print(f"  {warning}")
        else:
            print("Advertencias detectadas: 0")

        check(
            not warnings_found,
            "La instalación finaliza sin warnings ni errores de construcción.",
        )

        # ----------------------------------------------------------
        section("TC-145 - PUNTOS DE ENTRADA SE INSTALAN CORRECTAMENTE")
        # ----------------------------------------------------------

        bin_dir = venv_dir / "bin"

        entry_points = [
            "jobsy",
            "jobsy-daemon",
            "execute",
            "list",
            "status",
            "cancel",
        ]

        missing = []

        for entry in entry_points:
            path = bin_dir / entry

            if not path.exists():
                missing.append(entry)

        print(
            "Puntos de entrada esperados: "
            + ", ".join(entry_points)
        )

        print(
            "Puntos de entrada faltantes: "
            + (
                ", ".join(missing)
                if missing
                else "ninguno"
            )
        )

        check(
            not missing,
            "Los puntos de entrada públicos quedan instalados.",
        )

        # ----------------------------------------------------------
        section("TC-146 - INSTALACION NUEVA ES OPERATIVA")
        # ----------------------------------------------------------

        jobsy_help = run(
            [str(bin_dir / "jobsy"), "--help"],
            cwd=clone_dir,
            env=install_env,
        )

        daemon_help = run(
            [str(bin_dir / "jobsy-daemon"), "--help"],
            cwd=clone_dir,
            env=install_env,
        )

        check(
            jobsy_help.returncode == 0,
            "jobsy --help funciona desde la instalación nueva.",
        )

        check(
            daemon_help.returncode == 0,
            "jobsy-daemon --help funciona desde la instalación nueva.",
        )

        check(
            "usage:" in jobsy_help.stdout.lower(),
            "La CLI instalada presenta su ayuda correctamente.",
        )

        check(
            "usage:" in daemon_help.stdout.lower(),
            "El daemon instalado presenta su ayuda correctamente.",
        )

    section("RESULTADO GENERAL")

    if failures == 0:
        print("RESULTADO GENERAL: PASS")
        return 0

    print(
        f"RESULTADO GENERAL: FAIL "
        f"({failures} comprobaciones fallidas)"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
