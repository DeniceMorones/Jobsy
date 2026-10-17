# Guía de usuario de Jobsy

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

Pruebas nuevas, desde la raíz del clon:

```bash
python -B -m unittest discover -s test -p 'test_scheduler.py' -v
python -B -m unittest discover -s test -p 'test_queue*.py' -v
```

La primera suite usa procesos simulados. La segunda crea hijos propios y,
solo en Linux/WSL, un daemon con socket temporal privado; no usa /tmp/jobsy.sock.
El límite abarca procesos principales por daemon, no árboles de descendientes.

## Instalación en Linux o WSL

Se necesita Python 3.10 o superior con `venv` y `pip`. Dentro del clon:

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

## Arranque y verificación manual

Primero comprueba si ya existe `/tmp/jobsy.sock` (`test -S /tmp/jobsy.sock`).
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
- Trabajo desconocido después de reiniciar: los trabajos actuales viven en RAM;
  esta implementación no añade persistencia ni recuperación.

La CLI actual muestra metadatos, pero no ofrece una acción para leer stdout/stderr.

## Pruebas seguras de los adaptadores

Desde la raíz del clon, con el entorno activado:

```bash
python -B -m unittest discover -s test -p 'test_entry_points.py' -v
```

Estas pruebas usan IPC simulado y sustituyen el arranque del servidor. No se
conectan a `/tmp/jobsy.sock`, no lo eliminan y no ejecutan trabajos reales.
