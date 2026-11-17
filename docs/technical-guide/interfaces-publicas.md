# Interfaces públicas de Jobsy

Alcance: implementación local integrada de Avance 2 e IDs cortos de la CLI.
Actualizado para preparar Avance 3.2; describe contratos existentes, no certificación
de QA. El [contrato de red v1](protocolo-red-v1.md) es una propuesta separada,
pendiente de implementación. No hay listener TCP en esta versión.

## Ejecutables instalados

La instalación con pip genera seis console scripts dentro del entorno virtual.
Activarlo los incorpora al PATH; no son comandos globales automáticamente.

| Ejecutable | Argumentos y destino Python |
| --- | --- |
| `execute PROGRAMA [ARGUMENTOS...]` | `src.client.cli.execute_main(argv=None)` llama a `main(["run", "--", *argv], split_command_string=False)`. |
| `jobsy` | `src.client.cli.main(argv=None, *, split_command_string=True)`: subcomandos run, list, status, cancel, output y health. |
| `list [--status ESTADO] [--full-id]` | `list_main(argv=None)` antepone list y delega en main. |
| `status JOB_ID` | `status_main(argv=None)` antepone status y delega en main. |
| `cancel JOB_ID` | `cancel_main(argv=None)` antepone cancel y delega en main. |
| `jobsy-daemon [OPCIONES]` | `src.daemon.server.main(argv=None)` valida configuración y arranca DaemonServer. |

Formas completas: `jobsy run -- sleep 20`, `jobsy list`,
`jobsy list --status RUNNING`, `jobsy status JOB_ID`, `jobsy cancel JOB_ID`,
`jobsy output JOB_ID` y `jobsy health`. output y health son subcomandos de jobsy,
no ejecutables adicionales registrados en pyproject.toml.

JOB_ID puede ser el UUID completo o un prefijo hexadecimal único de 8 a 32
caracteres sin guiones; se admite mayúscula o minúscula. La CLI muestra los
primeros ocho caracteres de los UUID en run, list, status, cancel y health.
`jobsy list --full-id` y `list --full-id` muestran los UUID completos y pueden
combinarse con --status. No se modifica la respuesta IPC ni la identidad SQLite.
La resolución considera todo el historial cargado, incluidos los terminales,
bajo la Condition del gestor. Un prefijo ambiguo se rechaza antes de operar;
use más caracteres o el UUID completo. Los prefijos no son alias permanentes:
otro trabajo puede hacerlos ambiguos más adelante. Para scripts, conserve UUID.

Estados admitidos por argparse: QUEUED, RUNNING, SUCCEEDED, FAILED, CANCELED,
en mayúsculas. status, cancel y output requieren exactamente un ID; list y health no lo requieren.

Se conservan `python3 -m src.client.cli run -- sleep 20` y
`python3 -m src.daemon.server`. Después de instalar, no requieren estar en el clon.
Las formas de arranque son alternativas, no servicios para iniciar simultáneamente.

execute conserva los límites de argumentos y no añade shell. Por ejemplo,
`execute printf '%s\n' 'texto con espacios'` mantiene el último argumento unido.
`execute 'sleep 20'` busca un ejecutable con espacio en su nombre. La forma
heredada `jobsy run 'sleep 20'` sí divide esa cadena con shlex. Usar `--` en
jobsy run separa opciones de Jobsy de las opciones del programa.
execute no tiene una ayuda propia: `execute --help` intenta enviar ese nombre
como programa. Consultar `jobsy --help` y la ayuda de sus subcomandos.

Los nombres list, status y cancel pueden colisionar con herramientas, alias o
funciones de shell. Revisar `type -a list status cancel`; preferir `jobsy ...`
ante ambigüedad. No eliminar comandos del sistema.

### Códigos de salida

Clientes: 0 indica solicitud aceptada/procesada; 1 indica error de validación,
servicio o comunicación; 2 indica sintaxis inválida o ausencia de subcomando.
La ayuda de argparse devuelve 0. main y los adaptadores pueden lanzar SystemExit.
El éxito de execute no significa que el proceso haya terminado ni que haya salido
con 0: consultar status. Una cancelación aceptada no confirma recolección inmediata.

Daemon: ayuda 0, argumentos inválidos 2, retorno normal 0. Una excepción no
capturada de arranque/cierre termina con 1 y puede imprimir traceback; no existe
una taxonomía adicional de códigos del servicio. SIGINT y SIGTERM solicitan
cierre coordinado; señales externas como SIGKILL no son cierre limpio.

## Configuración efectiva

| Opción del daemon | Valor predeterminado y validación |
| --- | --- |
| `--max-running N` | 3; entero >=1, procesos principales por daemon. |
| `--queue-capacity N` | 100; entero >=0, trabajos esperando reserva. |
| `--data-dir RUTA` | Ruta explícita no vacía; expande ~ y resuelve rutas relativas respecto al directorio actual. |
| `--socket-path RUTA` | /tmp/jobsy.sock; ruta absoluta de socket Unix, padre existente, máximo 107 bytes resueltos. |
| `--cancel-grace SEGUNDOS` | 2.0; número >0 y <=60, espera entre SIGTERM y SIGKILL. |

Sin --data-dir se usa $XDG_STATE_HOME/jobsy si XDG_STATE_HOME es absoluto;
en otro caso ~/.local/state/jobsy. Cambiar la ruta selecciona otra base, no
migra datos. Se recomienda ruta absoluta privada en almacenamiento Linux local.
Los valores se fijan al inicio; no hay archivo de configuración ni recarga.

DaemonConfig(max_running=3, queue_capacity=100, data_dir=None,
socket_path="/tmp/jobsy.sock", cancel_grace_seconds=2.0) es inmutable;
data_directory() devuelve Path y parse_config(argv=None) usa argparse.
El daemon usa --socket-path o /tmp/jobsy.sock y no lee JOBSY_SOCKET_PATH.
El cliente lee JOBSY_SOCKET_PATH por solicitud, con el mismo predeterminado
si está ausente; una variable vacía es inválida. Afecta a los cinco ejecutables
cliente y al módulo heredado. No hay --host ni --port.
El argumento socket_path de DaemonServer prevalece sobre manager.config.socket_path;
sin gestor inyectado, se usa la configuración recibida por el servidor.

src/protocol/endpoint.py centraliza DEFAULT_SOCKET_PATH, resolve_socket_path(path)
y client_socket_path(). Valida texto/ruta absoluta, expande ~, exige padre
existente y lo resuelve, rechaza NUL y enlaces simbólicos finales y limita a 107
bytes codificados para Linux. No crea, borra ni cambia permisos de archivos.
El componente final nunca se resuelve como enlace. Usar un padre privado de
confianza. Argumentos inválidos generan ValueError (argparse: salida 2; CLI: 1).
Un error de permisos al bind/connect se informa por el mecanismo existente.
El arranque conserva el rechazo de toda ruta existente; el cierre compara
dispositivo/inode con lstat, sin seguir enlaces finales. No hay limpieza automática
de sockets obsoletos. La exclusividad del directorio de datos permanece independiente.
RF-16 (#72) permanece parcial: interfaz TCP y puerto requieren aprobación futura.

## Contrato IPC actual

AF_UNIX/SOCK_STREAM, JSON UTF-8, una solicitud/respuesta por conexión. El cliente
envía con sendall y _recv_all acumula bloques de hasta 65536 bytes hasta interpretar
un JSON o recibir EOF. El servidor lee una sola vez hasta 4096 bytes. No existe
cabecera de longitud, versión ni múltiples solicitudes por conexión. La lectura
incremental del cliente no resuelve la fragmentación de solicitudes en el servidor;
4096 no es una garantía de entrega ni un rechazo explícito por longitud.
El servidor atiende conexiones secuencialmente y aplica timeout de 1 s al cliente;
el cliente no configura timeout. No se ofrece transporte remoto ni autenticación
de aplicación. Los comandos se ejecutan con las credenciales del daemon.

| Operación | Solicitud JSON | Respuesta de éxito |
| --- | --- | --- |
| run | `{"action":"run","command":["sleep","20"]}` | `{"status":"ok","job_id":"UUID"}` |
| list | `{"action":"list","status":null}` | `{"status":"ok","jobs":[{"id":"UUID","status":"RUNNING","command":["sleep","20"]}]}` |
| status | `{"action":"status","job_id":"UUID"}` | `{"status":"ok","job":{"id":"UUID","status":"RUNNING","command":["sleep","20"],"received_at":"2026-10-17 12:00:00 UTC","started_at":"2026-10-17 12:00:00 UTC","finished_at":"-","exit_code":null,"diagnostic":null}}` |
| cancel | `{"action":"cancel","job_id":"UUID"}` | `{"status":"ok","job_id":"UUID","job_status":"CANCELED"}` |
| output | `{"action":"output","job_id":"UUID"}` | `{"status":"ok","job_id":"UUID","job_status":"SUCCEEDED","stdout":"salida\n","stderr":""}` |
| health | `{"action":"health"}` | `{"status":"ok","health":{"service_active":true,"storage_error":null,"running_count":0,"running_jobs":[],"queued_count":0,"queued_jobs":[],"recent_errors_count":0,"recent_errors":[]}}` |

UUID representa un identificador real; las fechas del ejemplo son ilustrativas.
list admite omitir status o enviarlo null. El gestor normaliza filtros de texto
a mayúsculas; el parser CLI solo admite los cinco valores en mayúsculas.
No se promete orden FIFO en list: FIFO corresponde al despacho, no al listado.
Las fechas IPC tienen precisión de segundos y formato mostrado; la ausencia se
representa con "-". exit_code es entero o null, también desconocido tras recuperación.
output devuelve stdout/stderr como cadenas separadas; la CLI las escribe en
sus flujos correspondientes, sin añadir texto. Los resultados pueden estar vacíos
mientras se ejecuta el trabajo: no existe streaming. status añade diagnostic,
cadena o null. health devuelve conteos y listas de RUNNING, QUEUED y hasta diez
FAILED recientes, ordenados por finished_at o received_at descendente. Cada
elemento incluye id, status, command, fechas, exit_code y stderr. running_count
no equivale al número de reservas. No se exponen versión de registro ni identidad
del proceso por IPC. Las respuestas y bitácoras conservan UUID completos.

Los errores actuales usan `{"status":"error","operation":"status","cause":"descripción","suggestion":"acción sugerida"}`:
comando inválido, cola llena, ID inexistente/ambiguo, cancelación de estado terminal,
acción desconocida o error de persistencia. No hay campo code estable en el IPC
actual. La CLI conserva fallback de message para respuestas antiguas. El código
numérico de salida del cliente sigue siendo 1 para errores del servicio.
validate_command exige lista no vacía de cadenas y nombre de programa no vacío;
no comprueba previamente existencia, permisos ni autoriza el ejecutable.
Un fallo posterior de lanzamiento se registra como FAILED, no como rechazo IPC.
Un fallo de transporte puede impedir recibir incluso el sobre de error.

La admisión se confirma durablemente antes de responder éxito. No hay clave de
idempotencia: reenviar run después de perder la respuesta puede crear otro trabajo.
Cola llena no deja un trabajo admitido. Nunca reintentar ciegamente una solicitud.

## Interfaces Python de componentes

Son interfaces de integración del proyecto, no un SDK con estabilidad semántica
garantizada. No modificar directamente Job, colas, reservas ni conexiones SQLite.

| Componente | Contrato relevante |
| --- | --- |
| JobManager(config=None) | submit_job(command) valida y admite atómicamente; devuelve Job. snapshot(id) y list_jobs(status=None) devuelven copias con command independiente y sin process. get_job(id) devuelve el objeto vivo: no usar para mutar estados. |
| JobManager | cancel_job(id) persiste intención, coordina cancelación y devuelve copia; ValueError para ID inválido, ausente, ambiguo o estado terminal. shutdown(timeout=5.0) cierra admisión y espera limpieza; puede fallar sin liberar reservas inciertas. |
| JobManager | enable_persistence(runtime) debe preceder trabajos/despachador. attach_executor(executor) exige un único ejecutor. create_job(command) y schedule_job(job) son compatibilidad heredada; preferir submit_job. El registro heredado solo se admite al programarlo. |
| Scheduler(manager, config) | counts() devuelve (reservas, pendientes); join() espera hilos fuera de la Condition. admit_locked, cancel_queued_locked y finish_locked son interfaces internas que requieren la Condition adquirida, no llamadas de clientes. QueueFullError deriva de ValueError. |
| Executor(manager, popen_factory=None, grace_seconds=None) | execute(job) delega admisión; spawn(command) crea Popen con pipes separados, start_new_session=True y sin shell. collect(job, process) devuelve (exit_code, stdout, stderr) tras recolección. terminate_and_reap(process) implementa ADR-007; no invocarlo con PIDs históricos. |
| DaemonServer(manager=None, executor=None, config=None, socket_path=None) | Registra señales al construirse: requiere hilo principal. start() abre persistencia, recupera y escucha; stop() coordina cierre. Gestor y servidor deben compartir ejecutor. Solo elimina su socket identificado por dispositivo/inode. |
| PersistenceRuntime(directory) | open() adquiere flock, abre base, recupera y registra sesión; close(clean=False) cierra sesión/base y libera el descriptor. No borrar daemon.lock. |
| RecoveryService(repository, current_boot=..., probe=...) | recover() devuelve registros reconciliados, sin reejecución; RecoveryBlocked impide arranque ante identidad incierta o superviviente. Consultas de /proc, no señales a procesos antiguos. |
| Job | UUID, argumentos, cinco estados, timestamps, exit_code, stdout y stderr; process y cancel_requested son referencias de ejecución, no datos serializados. |
| protocol.job_ids | short_job_id(id) presenta ocho caracteres si es UUID; resolve_job_id(id, known_ids) resuelve coincidencia exacta o prefijo único. El llamador protege el registro durante la resolución. No accede a SQLite ni modifica estados. |
| JobManager.get_health_summary() | Devuelve conteos, listas copiadas y estado de servicio bajo la Condition; FAILED recientes limitado a diez. |

Las copias de Job no son estructuras profundamente inmutables: el Event interno
sigue compartido. No modificarlo desde consumidores. El modo directo de
JobManager sin enable_persistence es en memoria; el daemon normal utiliza SQLite.

### JobRepository

JobRepository(path, timeout=0.5) abre/valida SQLite; no crea el directorio padre.
Admite close() y context manager. get_job(id) y list_jobs(status=None) devuelven
diccionarios separados con execution y datetimes con zona; list_sessions()
devuelve timestamps almacenados como texto ISO 8601.

- create_job(job, *, session_id=None, admission_sequence=None): inserta trabajo
  y metadatos indivisiblemente, versión inicial 0.
- update_status(id, expected_version, status, *, started_at=None, finished_at=None):
  conserva timestamps omitidos; no decide la validez de la transición de negocio.
- store_results(id, expected_version, *, status, exit_code, stdout, stderr,
  finished_at): confirma resultado terminal y limpieza; requiere recolección previa.
- record_execution_intent, record_process_identity y record_running: guardan
  intención o identidad; record_running confirma también RUNNING y started_at.
- record_cancellation_intent(id, expected_version, *, at, without_process=False):
  confirma CANCELED y fecha de intención; sin proceso confirma también finished_at.
- reconcile_job y record_recovery: metadatos de recuperación; no ejecutan procesos.
- start_session, finish_session y list_sessions: ciclo durable del daemon.

Toda actualización de trabajo exige expected_version, incrementa version y
devuelve el registro actualizado. Crear/actualizar usa transacciones explícitas;
lecturas compuestas tienen snapshot transaccional. Un RLock serializa la conexión.
Errores: RepositoryError, SchemaError, VersionConflict y RecordNotFound; argumentos
inválidos producen ValueError. No hay sustitución silenciosa de bases fallidas.
Política: esquema 1, journal DELETE, synchronous EXTRA; detalles en ADR-005.

## Invariantes y límites

Orden de locks: Condition -> repositorio -> SQLite. Ninguna transacción abarca
Popen, espera de procesos o IPC. Popen sí se serializa bajo la Condition con
cancelación; un lanzamiento o commit lento puede retrasar solicitudes.
La reserva permanece hasta recolección y commit final. Un fallo de limpieza
se aísla por trabajo y retiene su reserva mientras se espera al proceso; otras
reservas pueden continuar. Al cerrar sin confirmar limpieza, shutdown informa
error. Un fallo de almacenamiento bloquea globalmente admisión/despacho.
El límite cubre procesos principales, no descendientes ni tamaño de resultados.
Se conserva historial sin reejecución; salida parcial en RAM puede perderse.
No se garantizan efectos externos exactamente una vez. Véanse ADR-004 a ADR-007.

## Verificación técnica de empaquetado de 2.5A

El 17 de octubre de 2026, en Ubuntu 26.04.1 LTS/WSL2 y Python 3.14.4:

- Construcción del wheel con setuptools 78.1.1 disponible en el sistema: correcta.
- Instalación del wheel sin red ni dependencias en un venv temporal: correcta.
- Instalación editable de la copia temporal con --no-build-isolation y el backend
  existente disponible solo para la construcción: correcta.
- Importación de 16 módulos y resolución de los seis entry points, tanto tras
  instalar el wheel como después de instalar editable: correctas.
- Ayuda de jobsy, jobsy-daemon, list, status y cancel: salida 0.
- execute sin argumentos: salida 2 esperada, sin solicitud IPC.
- Ayuda de los dos módulos heredados: salida 0.

Las comprobaciones se hicieron fuera del clon usando una copia de src,
pyproject.toml y README, sin iniciar daemon, crear trabajos ni tocar el socket.
No se instalaron paquetes del sistema ni se modificó el venv del proyecto.
La disponibilidad automática del backend mediante descarga de pip no se probó.
No se reejecutaron las 105 pruebas históricas, ni se verificaron Python 3.10,
Linux nativo, fallos de alimentación o aceptación formal de QA.


## Verificación técnica de IDs cortos

El 16 de noviembre de 2026, en Ubuntu 26.04.1 LTS/WSL y Python 3.14.4,
la ejecución final aprobó 75 pruebas: 20 de entry points, 21 de Scheduler,
3 de procesos reales existentes y 31 verificaciones locales nuevas. No hubo
fallos ni omisiones en esa ejecución final. En el primer intento, cuatro
subcasos del arnés nuevo fallaron por crear otro Executor para el mismo gestor;
se corrigió el montaje del arnés para reutilizarlo y se repitió la suite.

Las nuevas comprobaciones cubrieron formato, prefijos, ambigüedad con historial
terminal, cancelaciones simultáneas, CLI, sobres IPC mediante socketpair y una
instancia instalada aislada: envío, consulta, cancelación en cola y ejecución,
salidas y reinicio con el mismo historial. Se usaron datos, logs y sockets
temporales propios, sin acceder a /tmp/jobsy.sock ni al daemon habitual.

El arnés nuevo y sus salidas permanecen fuera del repositorio. Las pruebas de
QA, su evidencia y las exclusiones locales no se modificaron. Alexia debe
adaptar independientemente los scripts que extraen un UUID completo del texto
de execute/list/status: la CLI muestra prefijos; list --full-id y las respuestas
IPC mantienen UUID completos. No se ejecutó la batería formal completa de QA.
Estas verificaciones no prueban ni certifican el protocolo de red v1 propuesto.
