# ADR-006: Recuperación del historial y exclusividad del daemon

Estado: implementado en Avance 2.2B; certificación formal de QA pendiente.
Alcance: RF-12 (#56), RF-13 (#57), RNF-11 (#60), RNF-28 (#61).
Complementa ADR-004 y ADR-005; no modifica los cinco estados públicos.

## Orden de arranque y propiedad

DaemonServer comprueba primero que no existe la ruta del socket. Después,
PersistenceRuntime crea/resuelve el directorio de datos, adquiere flock exclusivo
no bloqueante sobre daemon.lock, abre y valida SQLite, ejecuta RecoveryService
y registra una nueva sesión. JobManager carga los registros antes de escuchar.
La inicialización no ejecuta comandos históricos.

El descriptor del lock se conserva hasta cerrar la base y la sesión. Nunca se
elimina daemon.lock: eliminar el inode permitiría locks independientes. Un
segundo daemon sobre el mismo directorio falla aunque use otro socket.
El lock es cooperativo: no protege contra editores externos de SQLite ni contra
un usuario que borre manualmente archivos. Usar almacenamiento Linux local.

## Recuperación conservadora

RecoveryService primero revisa todos los registros inciertos. Si uno no se
puede reconciliar, falla el arranque antes de cambiar estados o abrir el socket.
No existe un modo automático que ignore este bloqueo.

| Registro anterior | Tratamiento |
| --- | --- |
| Terminal con limpieza confirmada | Se restaura sin cambiar resultados, UUID ni timestamps. |
| QUEUED sin intención de lanzamiento | CANCELED, motivo restart_before_execution y finished_at de reconciliación. |
| QUEUED con intención o RUNNING | Solo con ausencia confirmada: FAILED, motivo supervision_lost_process_absent, exit_code desconocido. |
| Terminal con limpieza pendiente | Se bloquea hasta confirmar ausencia; conserva estado y resultados disponibles. |

Las reconciliaciones de cada trabajo son transaccionales e idempotentes.
Una caída entre trabajos deja registros individualmente coherentes; el siguiente
arranque continúa sin reejecutar. Se preservan received_at, started_at y salidas
disponibles. No se inventa la hora real de terminación: finished_at puede quedar
nulo en FAILED; recovered_at registra cuándo se reconoció la interrupción.
El servidor muestra IDs y motivos recuperados en stderr.

## Identidad y procesos supervivientes

process_identity.py solo lee /proc. Combina boot_id, PID y starttime en ticks;
un PID aislado nunca autoriza acciones. Un boot_id diferente prueba que el
proceso del arranque anterior no sigue activo en este sistema. En el mismo
arranque, PID ausente, ticks diferentes o estado zombie/exit permiten descartar
la ejecución del proceso principal original. Un zombie ya no ejecuta, pero
Jobsy no pretende recolectar un proceso que no sea su hijo.

PID vivo con identidad coincidente, lectura no autorizada, identidad incompleta
o intención sin PID confirmado bloquean el arranque. La recuperación no adopta
procesos ni les envía señales. Se requiere el mismo entorno Linux/namespace de
procesos y visibilidad de /proc; no se ofrece recuperación entre contenedores
con namespaces distintos compartiendo la misma base.

Existe una ventana inevitable entre confirmar intención y registrar Popen:
si el daemon cae allí, no puede saber si lanzó un proceso. En ese caso, volver
a iniciar el servicio en el mismo arranque no basta. No hay override destructivo;
no existe un comando para registrar una confirmación manual. Un nuevo arranque
Linux permite descartar el proceso solo si se conservó el boot_id anterior.
Si también falta esa identidad, el bloqueo permanece. No borrar la base para
eludir el bloqueo. El control de árboles de descendientes queda fuera del alcance.

## Persistencia durante ejecución

Orden de locks: Condition de JobManager -> lock del repositorio -> SQLite.
El repositorio no llama al gestor. Cada transacción termina antes de Popen,
communicate, wait, terminate, kill, join o IPC.

- La capacidad se verifica antes de insertar. La creación se confirma antes de
  habilitar el despacho y antes de responder éxito al cliente.
- La intención se confirma antes de Popen. Identidad, RUNNING y started_at se
  confirman juntos antes de publicarse en memoria.
- La cancelación y su timestamp son atómicos; si aún no hay proceso, también
  se guarda finished_at antes de liberar la reserva.
- Estado terminal, exit_code, stdout/stderr, finished_at y limpieza confirmada
  se confirman juntos antes de liberar capacidad.

Si SQLite falla, el gestor bloquea admisión y despacho, informa del fallo y
solicita limpieza de sus procesos conocidos mediante los supervisores existentes.
No publica una transición cuyo commit falló ni libera su reserva por ese fallo.
Se conserva la última vista durable, aunque quede RUNNING con proceso ya
recolectado; el diagnóstico explica el bloqueo y la recuperación lo reconciliará.
Los eventos internos de limpieza no significan una cancelación durable exitosa.

El cierre normal permite la gracia existente de cinco segundos, cancela
pendientes/restantes y espera a los supervisores. La sesión solo queda limpia
si la coordinación termina sin errores. Un kill del daemon deja la sesión sin
cierre limpio; un error detectado puede registrar fin con clean_shutdown=0.

## Límites y compatibilidad

Se mantienen FIFO, reservas y límite de procesos principales de 2.1. El historial
recuperado no ocupa slots y ningún ID histórico se vuelve a programar.
No cambia el protocolo JSON, ni los seis ejecutables instalados. La CLI sigue
sin ofrecer lectura de stdout/stderr: los resultados se conservan en SQLite.

Solo se garantizan resultados que llegaron a un commit. Las salidas aún en RAM
o en pipes pueden perderse al caer el daemon. Un commit de admisión seguido de
una desconexión del cliente conserva el trabajo, aunque el cliente no reciba
su ID: no se implementa deduplicación de reintentos IPC. No se promete exactly-once
para efectos externos de un comando.

La latencia de disco puede retrasar operaciones bajo la Condition. El límite
de concurrencia no se relaja para ocultar fallos de almacenamiento. Las pruebas
de interrupción de procesos no certifican resistencia física a cortes eléctricos.
Una ruta de socket sobrante requiere diagnóstico del operador; el servicio nunca
la elimina durante el arranque.

## Verificación local de desarrollo

Se utilizaron pruebas locales de repositorio, integración y reinicio para revisar
caída de daemon aislado, superviviente, ausencia, PID reutilizado, intención
incierta, rollback, carreras, exclusividad y slots. Durante esa ejecución los
datos y sockets eran temporales, incluida la adaptación local de la prueba IPC.

Ejecución técnica en Ubuntu WSL durante 2.2B: 105 pruebas aprobadas, cero
fallos y cero omisiones. Desglose: 28 de JobRepository, 21 de Scheduler,
20 de CLI, 3 de procesos reales, 2 de IPC, 27 de integración del gestor
con persistencia/recuperación y 4 de reinicio/caída real del daemon aislado.
Las pruebas de fallos inyectados imprimen diagnósticos de bloqueo esperados;
no representan fallos de la suite. Este resultado histórico corresponde a
verificación de desarrollo del alcance de Benjamin, no a certificación formal.
No se ejecutaron pruebas nuevas durante el cierre documental.

test_job_repository.py, test_persistence_runtime.py, test_persistence_restart.py
y la copia test_queue_ipc_local.py permanecen excluidos y solo en local.
El resultado de 105 pruebas no es reproducible únicamente con el commit
propuesto. La prueba IPC versionada conserva su forma anterior y requiere
adaptación independiente de QA para no utilizar el directorio persistente
predeterminado. No ejecutar indiscriminadamente toda la carpeta test.

## Traspaso técnico a Alexia

Este resumen comunica comportamiento esperado, no constituye su plan de pruebas,
casos formales, matriz de trazabilidad ni evidencia de certificación.

| Escenario para verificación independiente | Resultado esperado |
| --- | --- |
| Reinicio limpio con el mismo directorio | Conservar UUID, argumentos, timestamps conocidos, estados y ambas salidas; sesión limpia solo tras cierre exitoso. |
| Caída con QUEUED, RUNNING o CANCELED pendiente de limpieza | No reejecutar; reconciliar solo tras descartar supervivientes y conservar motivo/fecha de recuperación. |
| PID reutilizado, proceso vivo o intención sin identidad | Nunca señalar un PID histórico; bloquear ante incertidumbre. Verificar límites del mismo namespace y boot_id conocido. |
| Interrupción antes/después de commits y fallos de escritura | Registros completos o rollback; no confirmar una admisión fallida ni publicar transiciones fallidas; no liberar slots anticipadamente. |
| Corrupción, versión incompatible, permisos y contención | Error explícito sin recrear una base vacía; exclusividad y recursos correctamente liberados cuando proceda. |
| Solicitudes simultáneas, cancelación/finalización y reinicio | FIFO y límites 1/3 preservados; capacidad cero, rechazo sin residuo, IDs históricos no despachados y versiones obsoletas rechazadas. |
| Dos daemons y socket existente | Rechazar el segundo propietario del directorio; no borrar ni alterar un socket ajeno. |
| CLI y configuración | Conservar seis ejecutables y módulo heredado; validar --data-dir y resolución XDG sin cambios del protocolo. |

Preparación obligatoria: directorio de datos temporal explícito para cada
escenario y socket Unix temporal independiente. --data-dir no cambia el socket;
el constructor DaemonServer admite socket_path para un arnés aislado.
La prueba IPC versionada debe recibir ambos recursos temporales antes de usarse
con 2.2. Las pruebas de caída solo pueden terminar procesos propios y deben
limpiarlos. No utilizar /tmp/jobsy.sock, datos de usuario ni un daemon existente.
Alexia decidirá cómo implementar los casos, registrar resultados y mantener sus
documentos formales. No se le transfieren como certificadas las pruebas locales.
