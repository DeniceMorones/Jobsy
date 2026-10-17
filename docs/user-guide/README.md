# Guía de usuario de Jobsy

## Persistencia y recuperación: Avance 2.2

El daemon guarda jobsy.sqlite3 en --data-dir. El predeterminado es
$XDG_STATE_HOME/jobsy cuando XDG_STATE_HOME es absoluto; de lo contrario,
~/.local/state/jobsy. Usa un directorio privado en el sistema Linux local,
fuera del clon. No compartas la base entre namespaces de procesos distintos.

En una sesión autorizada sin otro daemon ni socket existente:

```bash
jobsy-daemon --data-dir "$HOME/.local/state/jobsy-prueba" --max-running 3 --queue-capacity 100
# Alternativa, no iniciar simultáneamente:
python3 -m src.daemon.server --data-dir "$HOME/.local/state/jobsy-prueba"
```

--data-dir no cambia /tmp/jobsy.sock. Dos instancias no pueden compartir ni el
socket ni el directorio de datos. No se agregan opciones de interfaz o puerto.
RF-16 sigue parcial: interfaz TCP y puerto configurables requieren una decisión
posterior. No hay opción --host ni --port. El daemon acepta --socket-path;
los clientes seleccionan esa misma ruta mediante JOBSY_SOCKET_PATH.
Cambiar --data-dir selecciona otra base, no migra el historial existente.
Véanse los [contratos públicos](../technical-guide/interfaces-publicas.md) y
[ADR-007](../technical-guide/ADR-007-Cancelacion.md).

Para verificar un reinicio limpio, envía execute printf 'persistente', conserva
el ID y espera a que jobsy status ID_DEVUELTO indique SUCCEEDED. Detén solo tu
daemon con Ctrl+C y vuelve a iniciarlo con el mismo --data-dir. jobsy list y
jobsy status ID_DEVUELTO deben conservar el historial. stdout/stderr se guardan
en SQLite; la CLI actual no incorpora un comando para leerlos.

No hay reejecución automática. Los trabajos anteriores QUEUED sin intención de
lanzamiento se recuperan como CANCELED; los terminales verificados se conservan.
Una ejecución interrumpida se marca
FAILED con código desconocido solo cuando se confirma que el proceso principal
ya no ejecuta. Sus timestamps conocidos se preservan; finished_at puede ser -.
El daemon informa IDs y motivos de recuperación en su terminal.

Si hay un proceso superviviente o una intención sin identidad confirmada,
el arranque se bloquea. No mates un PID solo por aparecer en la base. No borres
SQLite, journals, daemon.lock ni sockets para saltarte la comprobación.
Una intención sin PID puede seguir siendo incierta tras terminar el proceso:
no hay override automático en el mismo arranque Linux. Consulta ADR-006 antes
de cualquier intervención; un nuevo arranque Linux permite descartar procesos
del arranque anterior solo si su boot_id está registrado. No existe un comando
para levantar manualmente el bloqueo; si falta esa identidad, permanece.
No reinicies un entorno compartido sin autorización.

Ante un error de escritura, se bloquean nuevas ejecuciones, se informa del
fallo y se intenta limpiar los procesos propios. La sesión no se marca limpia.
Resuelve el problema de almacenamiento antes de reiniciar. Una base corrupta
o incompatible no se reemplaza por una vacía.

La garantía cubre metadatos y resultados confirmados en SQLite. No garantiza
salida parcial que estaba en RAM/pipes ni efectos externos exactamente una vez.
No cambies el directorio para esquivar un bloqueo por procesos supervivientes.

La verificación de desarrollo registró 105 pruebas aprobadas en Ubuntu WSL,
sin fallos ni omisiones. Las pruebas nuevas permanecen solo en local; no se
distribuyen en este commit ni constituyen certificación formal de QA.
La validación independiente corresponde a Alexia; véase el
[traspaso técnico](../technical-guide/ADR-006-Recuperacion.md#traspaso-técnico-a-alexia).
No se proporciona un comando de pruebas de persistencia que presuponga esos
archivos en un clon limpio.

## Cola y concurrencia: Avance 2.1

En un entorno autorizado sin daemon ni socket previo:

```bash
jobsy-daemon --max-running 3 --queue-capacity 100
# Alternativa heredada; no ejecutar un segundo daemon:
python3 -m src.daemon.server --max-running 3 --queue-capacity 100
```

Los valores predeterminados son 3 y 100. max-running debe ser un entero >= 1;
queue-capacity, un entero >= 0. Los argumentos inválidos terminan con código 2
antes de abrir el socket. Los límites se fijan al iniciar; no cambian en caliente.

La capacidad de cola cuenta solo trabajos esperando una reserva. Con capacidad
0 se aceptan trabajos únicamente cuando hay una reserva libre. Al completarse,
fallar o recolectarse un proceso cancelado se despacha automáticamente el primer
trabajo pendiente. Si se llenan procesos y espera, execute/jobsy run reciben
un error de cola llena (salida CLI 1), sin un trabajo residual.

Para observarlo, inicia tu daemon de prueba con --max-running 1 --queue-capacity 1
y envía tres veces execute sleep 30 desde otra terminal. El primero ocupa una
reserva, el segundo espera y el tercero se rechaza mientras sigan ocupados.
Consulta jobsy list y cancela solo los IDs propios. Un cancelado en espera no
arranca. Una cancelación activa se confirma inmediatamente, pero el slot queda
ocupado hasta terminar y recolectar el proceso; finished_at puede aparecer como -.

Ctrl+C en tu daemon cierra admisión, cancela la espera, concede hasta cinco
segundos a los activos y cancela los restantes. No uses esta prueba con trabajos
ajenos. No borres sockets como parte de pruebas automáticas.

Comprobaciones existentes de Scheduler y procesos, desde la raíz del clon:

```bash
python -B -m unittest discover -s test -p 'test_scheduler.py' -v
python -B -m unittest discover -s test -p 'test_queue_processes.py' -v
```

La primera suite usa procesos simulados. La segunda crea hijos propios, sin
iniciar un daemon. No ejecutar test_queue_ipc.py ni descubrimiento global hasta
que QA adapte la prueba IPC a un directorio de datos y un socket temporales:
la versión actual no especifica directorio de datos. La adaptación de desarrollo
se conserva únicamente en la copia local excluida.
El límite abarca procesos principales por daemon, no árboles de descendientes.

## Instalación en Linux o WSL

Referencia de desarrollo: Ubuntu 26.04.1 LTS sobre WSL2 con Python 3.14.4.
Python >=3.10 es el mínimo declarado, no una versión verificada en esta tarea.
No se certifican Linux nativo ni otras distribuciones. Las 105 pruebas anteriores
en Ubuntu WSL son verificación de desarrollo, distinta de la certificación
formal de Alexia. Se necesitan `venv` y `pip`. Dentro del clon:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

`-e .` instala en modo editable: los cambios de código del clon se reflejan sin
reinstalar. Si cambian los metadatos o puntos de entrada, repite la instalación.
Para instalar una copia normal usa `python -m pip install .` en su lugar.
El backend de construcción es setuptools; pip puede descargarlo durante la
instalación. Jobsy no declara dependencias externas de ejecución.

Activa el mismo entorno en cada nueva terminal mediante
`source /ruta/a/Jobsy/.venv/bin/activate` (sustituye la ruta por tu clon).
Los ejecutables quedan dentro de `.venv/bin`, disponibles al activar ese entorno;
no se instalan automáticamente como comandos globales. Tras instalar, puedes
cambiar de directorio y seguir usando los comandos. Usa `deactivate` para salir.

## Socket Unix configurable: Avance 2.5B

El valor predeterminado es /tmp/jobsy.sock. Para una instancia propia aislada,
prepara un directorio privado y existente, por ejemplo con
`mkdir -p -m 700 "$HOME/.local/state/jobsy-local"` si aún no existe.
Comprueba que no contenga un socket de otra instancia; no lo elimines.

```bash
jobsy-daemon --socket-path "$HOME/.local/state/jobsy-local/control.sock" --data-dir "$HOME/.local/state/jobsy-local"
# Alternativa heredada, no ejecutar simultáneamente:
python3 -m src.daemon.server --socket-path "$HOME/.local/state/jobsy-local/control.sock" --data-dir "$HOME/.local/state/jobsy-local"
```

En otra terminal, activa el entorno y selecciona el mismo endpoint:

```bash
export JOBSY_SOCKET_PATH="$HOME/.local/state/jobsy-local/control.sock"
execute sleep 20
jobsy list
list --status RUNNING
status ID_DEVUELTO
cancel ID_DEVUELTO
```

Sustituye ID_DEVUELTO por el UUID propio. La variable se lee en cada solicitud
y afecta también a los subcomandos jobsy y al módulo heredado del cliente.
El daemon solo usa --socket-path o el predeterminado, no la variable.
`unset JOBSY_SOCKET_PATH` restaura el endpoint predeterminado del cliente.
Para una instalación no editable, reinstala el paquete tras actualizarlo.

Se exige ruta absoluta (se permite ~), sin NUL, con nombre de archivo y padre
existente. El padre se resuelve, pero no el componente final: se rechazan enlaces
simbólicos finales. El límite Linux es 107 bytes de ruta resuelta, no caracteres.
Una variable vacía es un error, no una solicitud de usar el predeterminado.
El daemon devuelve 2 ante configuración inválida; el cliente devuelve 1 ante
endpoint inválido o fallo de conexión. Los permisos se aplican por el sistema;
Jobsy no crea ni cambia permisos del padre del socket. Usa un directorio privado
de confianza: no se promete protección contra un usuario que pueda sustituirlo.

El arranque rechaza cualquier ruta final existente, incluso un socket obsoleto.
No la borra ni la sobrescribe. El cierre solo elimina su propia ruta si coincide
su identidad de dispositivo/inode, sin seguir enlaces finales. Cambiar de socket
no permite compartir un directorio de datos entre daemons: se conserva flock.
No cambian la cola, los estados, la persistencia ni el protocolo JSON.
RF-16 sigue parcial; interfaz IP y puerto TCP requieren aprobación del profesor.

## Arranque y verificación manual

Para el endpoint predeterminado, comprueba si ya existe `/tmp/jobsy.sock`
(`test -e /tmp/jobsy.sock || test -L /tmp/jobsy.sock`). Para uno personalizado,
comprueba la ruta elegida en su lugar.
Si existe, no arranques otro daemon ni borres el socket: confirma con su operador
si puedes reutilizarlo. El arranque rechaza una ruta de socket existente.
Un socket sobrante de una caída requiere diagnóstico manual de su propietario.

En una sesión de prueba autorizada sin daemon ni socket previo, inicia:

```bash
jobsy-daemon
```

El servicio permanece en primer plano. En otra terminal, activa el entorno y usa:

```bash
execute sleep 20
jobsy list
jobsy list --status RUNNING
jobsy status ID_DEVUELTO
jobsy cancel ID_DEVUELTO
```

Reemplaza `ID_DEVUELTO` por el UUID que devuelve `execute`. Consulta y cancela
únicamente el trabajo que acabas de crear. Puedes comparar con la CLI original:

```bash
python3 -m src.client.cli run -- sleep 20
```

El arranque original `python3 -m src.daemon.server` también se conserva; es una
alternativa a `jobsy-daemon`, no un segundo servicio para arrancar simultáneamente.
Para detener exclusivamente tu daemon de prueba, usa `Ctrl+C` en su terminal.
Este procedimiento crea trabajos y cambia el estado del servicio; es manual.

## Argumentos y comandos

Además de `execute`, `jobsy` y `jobsy-daemon`, la instalación ofrece:

| Comando corto | Equivalencia |
| --- | --- |
| `list` | `jobsy list` |
| `list --status RUNNING` | `jobsy list --status RUNNING` |
| `status ID_DEVUELTO` | `jobsy status ID_DEVUELTO` |
| `cancel ID_DEVUELTO` | `jobsy cancel ID_DEVUELTO` |

Estos comandos se encuentran en el entorno virtual activado. Pueden coincidir
con herramientas del sistema, especialmente `cancel` de servicios de impresión.
Comprueba `type -a list status cancel`: `.venv/bin` se antepone al PATH al activar
el entorno, pero los alias y funciones de shell pueden prevalecer. Usa las formas
`jobsy ...` si existe una colisión. No elimines comandos del sistema.
Reinstala con `python -m pip install -e .` para incorporar los nuevos ejecutables.

`list --help`, `status --help` y `cancel --help` muestran la ayuda de sus
subcomandos. `status` y `cancel` requieren un ID; `list` no requiere argumentos.

`execute` envía sus argumentos a la operación `run`, conservando sus límites:

```bash
execute ls -l /tmp
execute printf '%s\n' 'texto con espacios' '--literal'
execute '/ruta/con espacios/programa' --opcion 'valor con espacios'
jobsy run -- ls -l /tmp
```

Escribe `execute sleep 20`, sin encerrar todo el comando en una sola cadena.
`execute 'sleep 20'` intentaría ejecutar un programa cuyo nombre contiene un espacio.
La forma histórica `jobsy run 'sleep 20'` conserva su interpretación anterior.
`execute` no añade una shell, ni interpreta tuberías o redirecciones. Las comillas
las procesa tu shell antes de invocarlo. Usa `jobsy --help` para la ayuda;
las opciones que siguen al programa en `execute` pertenecen al programa ejecutado.

Los códigos de salida de la CLI se mantienen: `0` para solicitud correcta,
`1` para error y `2` para sintaxis incorrecta. Un envío exitoso no garantiza que
el trabajo termine correctamente; consulta `jobsy status ID_DEVUELTO`.

## Resolución de problemas

- `command not found`: activa el entorno; comprueba `command -v execute`,
  `command -v jobsy` y `command -v jobsy-daemon`. Confirma la instalación con
  `python -m pip show jobsy`. Si hay otro comando `execute`, comprueba su ruta.
- Falta `venv`/`ensurepip`: instala el soporte venv de tu distribución (en Ubuntu,
  el paquete `python3-venv`) y vuelve a crear el entorno siguiendo sus instrucciones.
- Error de instalación por red: pip necesita acceso al backend de construcción
  setuptools, o una copia previamente disponible en tu entorno/caché.
- Servicio no disponible: comprueba la terminal del daemon y la existencia del
  socket. No inicies un segundo daemon ni elimines el socket de un servicio activo.
- `ModuleNotFoundError: src`: usa el Python del entorno donde instalaste Jobsy o
  ejecuta las formas heredadas desde la raíz del repositorio.
- Trabajo desconocido después de reiniciar: comprueba que usas el mismo --data-dir
  y usuario. No se migran trabajos del daemon antiguo que solo existían en RAM.

La CLI actual muestra metadatos, pero no ofrece una acción para leer stdout/stderr.

## Pruebas seguras de los adaptadores

Desde la raíz del clon, con el entorno activado:

```bash
python -B -m unittest discover -s test -p 'test_entry_points.py' -v
```

Estas pruebas usan IPC simulado y sustituyen el arranque del servidor. No se
conectan a `/tmp/jobsy.sock`, no lo eliminan y no ejecutan trabajos reales.
