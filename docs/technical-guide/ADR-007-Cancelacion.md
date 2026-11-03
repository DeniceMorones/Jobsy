# ADR-007: Cancelación y liberación de reservas

Estado: documentación de la implementación existente; no introduce cambios.
Alcance: RNF-18 (#78), coordinación con concurrencia y persistencia de 2.1/2.2.
La certificación formal y el trabajo adicional de escalamiento del equipo son
independientes de este registro de arquitectura.

## Decisión implementada

JobManager.cancel_job valida existencia y rechaza estados terminales. Bajo la
Condition compartida confirma en SQLite la intención y el estado CANCELED antes
de publicarlos en memoria y activar cancel_requested. Se mantienen los cinco
estados; no se añade CANCELING. El éxito IPC confirma la solicitud durable,
no que el proceso haya desaparecido en ese instante.

### Trabajo sin proceso

La cancelación confirma finished_at y limpieza no pendiente, retira el trabajo
de pending o ready y descarta su reserva si la tenía. Scheduler promueve la
siguiente espera FIFO cuando corresponde. No necesita enviar señales ni esperar.
Un trabajo QUEUED puede tener reserva; no significa que Popen ya haya ocurrido.

### Carrera con lanzamiento

El despachador comprueba QUEUED, confirma intención, llama a Popen y publica la
referencia al proceso bajo la misma Condition utilizada para cancelar. Si gana
la cancelación, el trabajo no se lanza; si gana el lanzamiento, la cancelación
encuentra un proceso propio y solicita limpieza. No se mantiene una transacción
SQLite abierta durante Popen. Este diseño evita doble inicio a costa de que
un Popen o commit lento pueda retrasar otras solicitudes.

### Proceso activo

Executor.collect consulta cancel_requested entre intentos de communicate con
timeout de 0,1 s. terminate_and_reap realiza:

1. Si poll indica proceso activo, terminate envía SIGTERM en Linux.
2. wait espera hasta 2 s.
3. Si vence, kill envía SIGKILL y wait espera hasta otros 2 s.

ProcessLookupError al señalar se tolera porque el proceso pudo terminar en la
carrera. Después, collect intenta capturar ambas salidas con communicate
(timeout 0,5 s) y confirma wait. Si falla la captura intenta limpieza, cierra
pipes y registra el error; si no puede confirmar recolección, propaga el fallo.
No se promete recuperar toda salida cuando la captura falla.

Las operaciones communicate, wait, terminate, kill y join ocurren fuera de la
Condition. El monitor confirma estado terminal, exit_code, salidas, finished_at
y limpieza en una transacción antes de retirar la reserva y promover FIFO.
El estado sigue CANCELED aunque el proceso salga con 0. finish_locked ignora una
segunda finalización sin reserva, evitando liberar capacidad dos veces.

Si falla persistencia o limpieza, se conserva la reserva, se bloquean admisión
y despacho y se informa del error. Nunca se concede capacidad basándose solo
en CANCELED. La solicitud inicial puede esperar lock/commit, pero no espera
deliberadamente toda la terminación del proceso.

## Apagado y recuperación

SIGINT/SIGTERM del daemon solicitan cierre coordinado: cerrar admisión, cancelar
pendientes, conceder hasta cinco segundos de gracia a activos y cancelar los
restantes. Los joins no tienen timeout; cinco segundos no es una cota total.
La sesión solo se marca limpia al terminar sin error. Una ruta de socket ajena
no se borra. La recuperación de ADR-006 nunca señala PIDs históricos, adopta
supervivientes ni reejecuta trabajos; bloquea ante incertidumbre.

## Alternativas y límites

Liberar el slot al publicar CANCELED permitiría exceder el límite mientras el
proceso sigue vivo. Señalar desde el manejador IPC bloquearía solicitudes y
duplicaría la propiedad de limpieza; se conserva el monitor como supervisor.
Un estado público adicional requeriría cambiar contratos sin necesidad actual.

La política no envía SIGINT al trabajo, no controla grupos de procesos ni todos
los descendientes y no garantiza apagado acotado. Los descendientes pueden
conservar pipes. No se amplía aquí la política de escalamiento ni se altera el
trabajo de Backend o QA. La implementación está en job_manager.py, scheduler.py
y executor.py; los contratos de consumo están en interfaces-publicas.md.
