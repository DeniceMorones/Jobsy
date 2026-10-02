#validaciones NO mezclar con server.py

def validate_command(command: list[str]) -> None:#espera el comando, ejemplo: ["sleep", "10"] y no retorna nada

    if not isinstance(command, list):#valida si viene como lista
        raise ValueError(
            "El comando debe enviarse como una lista."
        )

    if len(command) == 0:#valida comando vacio
        raise ValueError(
            "El comando no puede estar vacio."
        )

    if not all(isinstance(arg, str) for arg in command):#tipos de datos erroneos, solo acepta texto
        raise ValueError(
            "El comando y sus argumentos deben ser texto."
        )

    if not command[0].strip():
        raise ValueError(
            "El nombre del programa no puede estar vacio."
        )