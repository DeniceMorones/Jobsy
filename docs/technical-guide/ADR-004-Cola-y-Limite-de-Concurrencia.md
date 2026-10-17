# ADR-004: Cola y límite de concurrencia

Estado: implementado; verificación técnica ejecutada por Benjamin en Ubuntu WSL.
Alcance: Avance 2.1, RF-03 (#52), RF-05 (#23), RNF-07 (#26).
Complementa ADR-002 y conserva el protocolo de ADR-003.

## Contexto y decisión

La creación de un hilo por solicitud no limita los procesos simultáneos.
Se incorpora Scheduler con una cola FIFO acotada y reservas de ejecución.
DaemonConfig valida max_running=3 (mínimo 1) y queue_capacity=100 (mínimo 0).
Ambos valores se fijan al arrancar; no hay reconfiguración dinámica.

JobManager controla admisión, registro, cancelación y snapshots. Scheduler
controla espera, reservas, despacho y supervisores. Executor crea procesos,
captura stdout/stderr y confirma su terminación. DaemonServer conserva el
protocolo JSON por socket Unix y los seis ejecutables existentes.

## Sincronización e invariantes

Una Condition con RLock protege registro, estados, colas y reservas.
La admisión asigna una reserva libre o agrega al final de la cola; si ambas
capacidades están ocupadas, QueueFullError produce el sobre IPC existente
(status=error, message), sin dejar un trabajo registrado. La cola cuenta solo
trabajos sin reserva; queue_capacity=0 permite admisión solo con reserva libre.
El lanzamiento sigue siendo asíncrono: disponer de reserva no significa que
Popen ya se haya ejecutado.

pending contiene la espera acotada; ready contiene trabajos con reserva aún
sin proceso. reservations identifica los slots ocupados y admitted impide
reprogramar un mismo ID. Los métodos terminados en _locked requieren la
Condition adquirida por su llamador.

La promoción extrae del principio de la cola bajo el mismo lock. Un único
despachador serializa la última comprobación de cancelación, Popen y publicación
del proceso. Las reservas listas conservan su orden de admisión. FIFO significa
orden de lanzamiento, no orden de finalización ni orden de llegada a la red
entre solicitudes concurrentes: se ordenan al adquirir el lock de admisión.

- Procesos principales activos <= reservas <= max_running.
- Trabajos en espera <= queue_capacity.
- Cada ID admitido se despacha como máximo una vez durante la sesión.
- Un trabajo cancelado antes del lanzamiento nunca se ejecuta.
- Una reserva con proceso no se libera hasta confirmar terminación y recolección.
- Una segunda finalización no libera otra reserva.

Popen se realiza dentro de la sección crítica, sin preexec_fn. Esto simplifica
la carrera lanzamiento/cancelación; un lanzamiento lento puede retrasar otras
solicitudes. communicate, wait, terminate, kill, joins e IPC quedan fuera del lock.
Los monitores consultan el evento de cancelación mediante esperas de captura
de 0,1 s. No se espera al fin del proceso dentro de una solicitud de cancelación.

## Estados, errores y apagado

Se mantienen QUEUED, RUNNING, SUCCEEDED, FAILED y CANCELED. Una reserva lista
puede seguir públicamente QUEUED. Un proceso cancelado puede seguir ocupando
una reserva; finished_at se asigna después de recolectarlo.
Un fallo de Popen produce QUEUED -> FAILED y libera la reserva.
Si no se puede confirmar la limpieza, se retiene capacidad por seguridad
y shutdown informa del error; no se presume que el proceso desapareció.

El apagado cierra admisión, cancela trabajos no iniciados, permite hasta cinco
segundos a los activos y solicita cancelación de los restantes. Después une
los supervisores fuera del lock. El Executor conserva la secuencia de
terminación, espera de dos segundos y escalamiento, y espera también tras kill.
La política de terminación está aislada en terminate_and_reap para coordinar
el trabajo de escalamiento asignado por separado. En Linux la secuencia actual
es SIGTERM -> espera de hasta 2 s -> SIGKILL -> espera de hasta 2 s; no incluye
SIGINT. Los cinco segundos son el periodo de gracia del servidor, no un límite
total de apagado: los joins no tienen timeout.

Cancelar un trabajo reservado pero todavía sin proceso libera su reserva sin
esperar recolección. Si falla la creación o el arranque del hilo supervisor,
el Scheduler marca CANCELED y ejecuta la limpieza desde el despachador, fuera
del lock. No abandona el proceso ni libera anticipadamente su reserva.

El servidor rechaza arrancar sobre una ruta de socket existente; solo limpia
su propia ruta. Esta protección evita desconectar un daemon ajeno.

## Alternativas y consecuencias

Un semáforo aislado no resuelve FIFO, admisión acotada ni cancelación atómica.
Un pool externo añadiría dependencias sin eliminar la coordinación del proceso.
Se eligen deque, Condition y subprocess de la biblioteca estándar.

El límite es por instancia y para procesos principales; no limita descendientes,
memoria de salida ni historial. El registro y la cola viven en RAM: no hay
persistencia, recuperación ni deduplicación de reintentos IPC. Se preservan
create_job/execute como interfaz interna heredada; el servidor usa submit_job
para admisión atómica. Los antiguos mutadores de estado sin coordinación
mark_job_started/mark_job_finished se sustituyen por el ciclo del Scheduler.

## Verificación reproducible

Desde la raíz, con el entorno activado:

```bash
python -B -m unittest discover -s test -p 'test_scheduler.py' -v
python -B -m unittest discover -s test -p 'test_entry_points.py' -v
python -B -m unittest discover -s test -p 'test_queue_processes.py' -v
python -B -m unittest discover -s test -p 'test_queue_ipc.py' -v
```

test_scheduler usa procesos controlados, barreras y eventos para FIFO,
capacidades, rechazo, carreras de cancelación, fallos y liberación única.
test_queue_processes ejecuta únicamente hijos propios. test_queue_ipc inicia
un daemon propio con socket temporal, nunca /tmp/jobsy.sock, y se omite cuando
faltan sockets Unix. No se modifican ni regeneran evidencias históricas de QA.

Antecedente de verificación (17 de octubre de 2026): ejecución conjunta
con Python en Windows, 46 pruebas descubiertas, 44 aprobadas y 2 omitidas por
requerir Linux/WSL; ningún fallo. Las 20 pruebas existentes de entry points
están incluidas. Los procesos reales utilizados fueron exclusivamente hijos
de la suite. El lanzador WSL no respondió, por lo que no se verificó aquí
el IPC real ni las señales POSIX en aquella ejecución.

### Nota técnica de verificación de Benjamin

Benjamin ejecutó posteriormente las cuatro suites anteriores en Ubuntu WSL,
desde el entorno virtual del repositorio. Según la salida de terminal que
compartió, se aprobaron 46 pruebas: 21 de Scheduler y configuración, 20 de CLI,
3 de procesos reales y 2 de IPC Unix; cero fallos y cero omisiones.
Esta ejecución cubre la integración Unix que había quedado pendiente.

La nota registra la verificación técnica del alcance de Benjamin: RF-03 (#52),
RF-05 (#23) y RNF-07 (#26). No sustituye la evidencia formal, el plan, los casos
ni la matriz de trazabilidad de QA, bajo responsabilidad de Alexia; tampoco
certifica todo el Avance 02 ni el trabajo de rechazo/escalamiento del equipo.
