# Jobsy

## Avance 2.1: cola y concurrencia

El daemon incorpora una cola FIFO acotada y reservas de ejecución sincronizadas.
Por defecto admite hasta 3 procesos principales simultáneos y 100 trabajos en
espera. En una sesión propia sin daemon ni socket existente:

```bash
jobsy-daemon --max-running 3 --queue-capacity 100
```

La forma heredada acepta las mismas opciones:
`python3 -m src.daemon.server --max-running 3 --queue-capacity 100`.
No ejecutes ambas simultáneamente. La capacidad de espera puede ser 0; el límite
de ejecución debe ser al menos 1. La cola llena se rechaza sin registrar trabajos.
Cancelar no libera una reserva activa hasta confirmar la recolección del proceso.
Se conservan CLI y protocolo; Avance 2.2 añade persistencia SQLite y recuperación
conservadora sin reejecución automática.

Detalles operativos y ejemplos en la [guía de usuario](docs/user-guide/README.md)
y [ADR-004](docs/technical-guide/ADR-004-Cola-y-Limite-de-Concurrencia.md).

## 🎯 Propósito:
Desarrollar una herramienta sencilla para administrar tareas en el sistema Linux, permitiendo:
* Agregar comandos o programas.
* Ejecutarlos de manera simultánea (concurrente).
* Revisar su progreso en tiempo real.
* Obtener resultados (salidas y errores).
* Detener la ejecución cuando sea necesario.

## 👥 Integrantes:
* **Gomez Rubio Alexia**: alexia.gomez5516@alumnos.udg.mx
* **Ibarra Bravo Jocelyn Naomi**: jocelyn.ibarra4401@alumnos.udg.mx
* **Lopez Fletes Benjamin**: benjamin.lopez4157@alumnos.udg.mx
* **Rico Morones Denice Estefania**: denice.rico4211@alumnos.udg.mx

## 🎭 Asignación de roles:
* **Arquitectura:** Benjamin Lopez Fletes
* **Project Management & Backend:** Jocelyn Naomi Ibarra Bravo
* **Backend Development:** Denice Estefania Rico Morones
* **QA y Certificación:** Alexia Gomez Rubio

## 🛠️ Arquitectura y componentes implementados:
El proyecto está organizado de forma modular dentro del directorio src/

* **src/client/cli.py:** Interfaz de línea de comandos para parsear argumentos y formatear la salida en terminal.

* **src/daemon/executor.py:** Motor de ejecución asíncrona mediante subprocess.Popen e hilos.

* **src/daemon/job_manager.py:** Gestor del ciclo de vida de los trabajos, asignación de UUIDs y control de estados.

* **src/daemon/job.py:** Modelo de datos, estados (QUEUED, RUNNING, SUCCEEDED, FAILED, CANCELED) y metadatos.

* **src/daemon/server.py:** Guardián del servicio encargado del apagado seguro;

* **src/protocol/validation.py:** Módulo para validación y sanitización de comandos.

## Instalación y ejecución

Requiere Linux o WSL y Python 3.10+ con `venv` y `pip`. Desde la raíz del clon:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

La instalación editable mantiene los cambios del código disponibles. Para una
instalación normal, usa `python -m pip install .` en lugar de `-e .`.
Los comandos `execute`, `jobsy`, `jobsy-daemon`, `list`, `status` y `cancel` están disponibles después de
instalar y activar el entorno; no se convierten automáticamente en comandos
globales del sistema. Una vez instalado, puedes usarlos desde otro directorio.

Los comandos cortos equivalen a `jobsy list`, `jobsy status` y `jobsy cancel`.
Por ejemplo: `list --status RUNNING`, `status ID_DEVUELTO` y `cancel ID_DEVUELTO`.
Los nombres genéricos pueden coincidir con otras herramientas (por ejemplo,
`cancel` de un sistema de impresión). Comprueba `type -a list status cancel`
en la shell: la activación antepone `.venv/bin` al PATH, pero los alias y funciones
de shell pueden tener prioridad. Usa `jobsy list`, `jobsy status` o `jobsy cancel`
para evitar ambigüedades. Repite `python -m pip install -e .` tras esta actualización.

Si ya existe un daemon, reutilízalo: no inicies otro ni borres su socket.
En un entorno sin daemon ni socket previo, inicia el servicio en una terminal:

```bash
jobsy-daemon
```

En otra terminal activa el mismo entorno y ejecuta:

```bash
execute sleep 20
execute ls -l /tmp
jobsy list
jobsy list --status RUNNING
jobsy status ID_DEVUELTO
jobsy cancel ID_DEVUELTO
```

Sustituye `ID_DEVUELTO` por el UUID recibido. El daemon permanece en primer plano;
`Ctrl+C` solicita su apagado habitual. No uses ese apagado si atiende trabajos ajenos.
El listado recupera el historial al reiniciar con el mismo directorio de datos.

Puede seleccionarse un directorio fuera del repositorio:

```bash
jobsy-daemon --data-dir "$HOME/.local/state/jobsy" --max-running 3 --queue-capacity 100
# Alternativa heredada, no simultánea:
python3 -m src.daemon.server --data-dir "$HOME/.local/state/jobsy"
```

Sin --data-dir se usa $XDG_STATE_HOME/jobsy (si XDG_STATE_HOME es absoluto) o
~/.local/state/jobsy. Un lock impide dos daemons sobre el mismo directorio.
Los pendientes anteriores se cancelan; una ejecución interrumpida se marca
FAILED solo tras descartar procesos supervivientes. La incertidumbre bloquea
el arranque con diagnóstico. No borres la base, el lock ni el socket para evitarlo.
Se conservan resultados confirmados, no necesariamente salida parcial durante
una caída. Consulta [ADR-006](docs/technical-guide/ADR-006-Recuperacion.md).

Las invocaciones anteriores siguen disponibles desde la raíz del repositorio
o desde cualquier directorio si el paquete está instalado en el intérprete usado:

```bash
python3 -m src.client.cli run -- sleep 20
python3 -m src.daemon.server
```

Pruebas de los puntos de entrada, sin conectar al socket ni iniciar procesos de trabajo:

```bash
python -B -m unittest discover -s test -p 'test_entry_points.py' -v
```

Si aparece `command not found`, activa el entorno en esa terminal y comprueba
`command -v jobsy` y `python -m pip show jobsy`. Si el servicio no responde,
consulta la [guía de usuario](docs/user-guide/README.md), que incluye instalación,
argumentos con espacios y resolución de problemas. No elimines `/tmp/jobsy.sock`
como parte de una comprobación automática.

## 🔢 Códigos de Salida
El cliente CLI utiliza estos códigos para la solicitud, no para el resultado del proceso ejecutado:
* **0**: Solicitud procesada correctamente.
* **1**: Error de solicitud, comunicación o servicio.
* **2**: Error de sintaxis.

## 📊 Estado del proyecto:
El alcance de Benjamin en 2.2 incorpora persistencia y recuperación conservadora.
La verificación local de desarrollo registró 105 pruebas aprobadas en Ubuntu WSL,
sin fallos ni omisiones; no equivale a certificación formal ni al cierre de todo
Avance 02. Las pruebas nuevas permanecen locales y fuera del commit propuesto.
Alexia conserva la responsabilidad de verificación independiente y evidencia QA.
Consultar el [traspaso técnico](docs/technical-guide/ADR-006-Recuperacion.md#traspaso-técnico-a-alexia).
