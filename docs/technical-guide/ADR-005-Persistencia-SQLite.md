# ADR-005: Persistencia SQLite, fases 2.2A y 2.2B

Estado: implementación revisada por desarrollo; certificación formal de QA pendiente.
Alcance: base técnica de RF-12 (#56), RF-13 (#57), RNF-11 (#60) y RNF-28 (#61).
La recuperación conservadora se documenta en ADR-006.

## Decisión

Usar sqlite3 de la biblioteca estándar mediante JobRepository. El constructor
recibe una ruta explícita; no crea directorios, no usa una ruta global y no
abre una base al importar el módulo. No se añaden dependencias.

JobManager y Scheduler utilizan el repositorio en el daemon. PersistenceRuntime
gestiona directorio, exclusividad, recuperación y sesión antes de admitir trabajos.
Los gestores construidos directamente sin enable_persistence conservan el modo
en memoria para pruebas y uso interno; el arranque normal siempre usa SQLite.
El repositorio almacena registros; no ejecuta comandos, recupera procesos ni
decide transiciones de negocio. Un estado válido no implica por sí solo una
transición válida: esa política corresponde al gestor y a RecoveryService.

## Esquema versión 1

- jobs: UUID canónico, argumentos JSON sin reinterpretación de shell, cinco
  estados públicos, timestamps UTC, código de salida nullable, stdout/stderr
  separados y versión optimista entera.
- job_execution: una fila por trabajo, sesión opcional, secuencia de admisión,
  intención de lanzamiento, PID, boot_id, ticks de inicio del proceso,
  intención de cancelación, limpieza pendiente, resultados completos y
  fecha/motivo de recuperación.
- daemon_sessions: UUID, inicio, fin, cierre limpio e identidad del daemon.
- PRAGMA user_version: versión del esquema, creada junto con las tablas en
  una transacción. No hay migraciones implícitas.

Se comprueban esquema, quick_check, claves foráneas, correspondencia de trabajos
con sus metadatos, comandos, UUID y timestamps al abrir. Una base ajena,
corrupta, incompatible o con versión futura produce un error. Nunca se elimina,
trunca ni sustituye por una base vacía. El esquema de tablas se compara con
su definición esperada: cambiarlo requiere una migración explícita futura.

## Atomicidad y concurrencia

Cada escritura usa BEGIN IMMEDIATE, COMMIT y ROLLBACK ante errores. La creación
de jobs y job_execution es indivisible. El resultado final y sus indicadores
de integridad/limpieza se guardan en una sola transacción.

Una conexión por instancia, protegida por RLock, admite llamadas desde varios
hilos. SQLite serializa escritores de distintas instancias; el timeout de
contención predeterminado es 0,5 segundos. Las lecturas compuestas también
usan transacciones para no mezclar versiones de ambas tablas.

Toda modificación de un trabajo exige expected_version e incrementa version,
incluyendo cambios en sus metadatos. Una versión obsoleta produce
VersionConflict sin escrituras. Las sesiones solo se cierran una vez.
No hay reintentos ciegos ni deduplicación de solicitudes de clientes.

## Política de durabilidad

journal_mode=DELETE y synchronous=EXTRA en la conexión operativa. Se elige
rollback journal por simplicidad y porque esta fase no requiere lectores
independientes con alta concurrencia. EXTRA añade sincronización del directorio
al eliminar el journal. WAL se reserva para una necesidad medida futura.

Las garantías dependen del almacenamiento y del sistema operativo que ejecuta
las sincronizaciones; las pruebas no simulan una pérdida física de alimentación.
La inicialización del esquema es transaccional; la política operativa se
configura y verifica antes de devolver el repositorio al llamador.

No eliminar journals para reparar una base. La recuperación de una transacción
interrumpida la realiza SQLite al abrirla. Esto no equivale a recuperar el
estado de ejecución de un trabajo.

## API

- create_job(job, session_id=None, admission_sequence=None): registra datos y
  metadatos de ejecución con versión inicial 0.
- get_job / list_jobs: snapshots separados del modelo vivo, con filtro opcional.
- update_status: actualiza estado y timestamps suministrados; los omitidos
  se conservan.
- store_results: guarda estado terminal, código, ambas salidas y fecha final;
  marca resultados completos y limpieza no pendiente. El llamador debe haber
  confirmado esas condiciones antes de invocarlo.
- record_execution_intent: registra sesión, intención y limpieza pendiente.
- record_process_identity: almacena identidad; no valida propiedad ni señala PIDs.
- record_cancellation_intent: registra intención y CANCELED atómicamente; con
  without_process guarda también finished_at y limpieza no pendiente.
- record_running: confirma RUNNING, started_at e identidad del proceso juntos.
- reconcile_job: confirma estado y motivo de recuperación; conserva las salidas
  existentes y no inventa exit_code para una ejecución interrumpida.
- record_recovery: almacena motivo y fecha, sin efectuar recuperación.
- start_session / finish_session / list_sessions: registros del ciclo del daemon.
- close y context manager: cierre explícito de conexiones.

Los métodos de modificación de trabajos devuelven el snapshot con la nueva
versión. Los registros de trabajos incluyen execution; sus timestamps se
devuelven como datetime con zona. list_sessions devuelve los campos almacenados,
con timestamps ISO 8601. No se serializan Popen, Event ni locks.

Errores: RepositoryError para almacenamiento, SchemaError para esquema,
VersionConflict para concurrencia y RecordNotFound para registros ausentes.
Los argumentos inválidos producen ValueError. Los errores SQLite conservan
su causa. Un rollback fallido cierra el repositorio para impedir su reutilización.

## Verificación local de desarrollo, no certificación QA

En Ubuntu WSL: 28 pruebas del repositorio aprobadas, cero fallos y cero
omisiones. Incluyen reapertura durable, rollback entre tablas, fallos de
inicialización, versiones obsoletas, múltiples conexiones e hilos, directorio
sin escritura, datos inválidos, corrupción y un proceso de prueba terminado
durante una transacción sin commit.

También se ejecutaron las 46 pruebas de regresión de 2.1: 21 de Scheduler,
20 de CLI, 3 de procesos reales y 2 de IPC Unix. Todas aprobaron.
Total de la verificación de 2.2A: 74 pruebas aprobadas, cero fallos u omisiones.
Las bases y los sockets de prueba son temporales; no se usa /tmp/jobsy.sock.

La ejecución posterior de 2.2B sumó 105 pruebas aprobadas en Ubuntu WSL,
sin fallos ni omisiones; véase el desglose en ADR-006. Son resultados históricos
de verificación de desarrollo del alcance de Benjamin, no una ejecución nueva
durante la revisión documental ni una certificación de aceptación.

Las pruebas nuevas de persistencia permanecen solo en la copia local y están
excluidas del commit propuesto. La variante IPC utilizada también incluía un
directorio temporal explícito; esa adaptación se conserva únicamente en local.
No se ofrece aquí un comando que reproduzca las 105 pruebas desde un clon limpio.
La elaboración y ejecución de las pruebas formales, evidencia, plan, casos y
trazabilidad corresponden a Alexia. El resumen de traspaso está en ADR-006.

## Integración 2.2B y límites

El daemon acepta --data-dir y carga el historial antes de abrir el socket.
La creación se confirma antes de responder éxito; los cambios se publican en
memoria después del commit. Se conserva el orden Condition -> repositorio.
No se mantiene una transacción durante operaciones de procesos o sockets.
RecoveryService bloquea el arranque ante supervivientes o lanzamiento incierto;
no reejecuta trabajos. Ver [ADR-006](ADR-006-Recuperacion.md).

El repositorio no garantiza resultados que nunca se le entregaron. Preservar
salida parcial durante una caída requiere trabajo adicional de captura.
No hay reejecución automática ni limpieza de procesos en esta capa.
