# Modelo de estados de Jobsy: Avances 2.1 y 2.2

Relacionado con RF-03, RF-05, RNF-07 y el modelo inicial del Issue #43.
Persistencia y recuperación: RF-12 (#56), RF-13 (#57), RNF-11 (#60), RNF-28 (#61).

## Estados y transiciones

| Origen | Evento | Destino |
| --- | --- | --- |
| QUEUED | Popen exitoso, identidad y estado confirmados en SQLite | RUNNING |
| QUEUED | Error de lanzamiento | FAILED |
| QUEUED | Cancelación o apagado antes del lanzamiento | CANCELED |
| RUNNING | Proceso recolectado con código 0 y sin error de captura | SUCCEEDED |
| RUNNING | Proceso recolectado con código distinto de 0 o error de captura | FAILED |
| RUNNING | Solicitud de cancelación | CANCELED |
| RUNNING | Error al crear o arrancar el hilo supervisor | CANCELED |
| QUEUED sin intención | Recuperación tras reinicio | CANCELED |
| QUEUED con intención o RUNNING | Recuperación con ausencia de proceso confirmada | FAILED |

SUCCEEDED, FAILED y CANCELED son terminales: nunca regresan a QUEUED o RUNNING.
Una solicitud rechazada por capacidad no crea un estado ni deja un trabajo.
QUEUED incluye espera FIFO y reserva lista para lanzar: no se añade STARTING.

## Estado público y recursos internos

received_at se asigna al crear el trabajo; started_at al publicar Popen exitoso.
finished_at se asigna al fallo de lanzamiento, cancelación sin proceso o
recolección. En CANCELED con proceso aún en limpieza puede ser nulo.
exit_code se obtiene al recolectar; el fallo de lanzamiento se representa con 1.
Si falla la captura y el proceso termina con código 0, Executor devuelve 1
para representar ese fallo. La finalización conserva CANCELED aunque el proceso
termine con código 0; solo completa sus metadatos y libera su reserva.

Cancelar confirma primero la intención y el estado CANCELED en SQLite y después
publica el estado y establece el evento bajo la Condition. Si falla el commit,
la solicitud no confirma éxito; la limpieza de seguridad no equivale a una
cancelación durable. Si aún no hay proceso, se retira de la cola o reservas
listas. Si Popen ya comenzó,
la cancelación espera la publicación bajo el mismo lock. Si el lanzamiento
falla o la finalización gana la carrera y ya dejó un estado terminal, se
rechaza cancelar. En caso contrario, el supervisor termina y recolecta el
proceso. No hay resurrección del trabajo cancelado.

La reserva no depende de contar RUNNING: permanece durante limpieza y se
libera exactamente una vez. Una reserva sin proceso se puede liberar al
cancelar antes del lanzamiento. Si no se confirma la limpieza de un proceso,
permanece ocupada y se registra el diagnóstico en stderr del daemon; no se
fuerza FAILED ni finished_at. También un fallo de persistencia bloquea nuevas
ejecuciones y mantiene la última vista durable, incluso QUEUED si no se confirmó
RUNNING. La limpieza de procesos propios continúa sin publicar commits fallidos.
Por ello una cancelación aceptada no significa que el slot esté libre todavía.

En el daemon, cada transición se confirma en SQLite antes de publicarse en RAM.
Los registros recuperados conservan UUID, timestamps conocidos y salidas.
FAILED por interrupción tiene exit_code desconocido y puede no tener finished_at;
recovered_at y recovery_reason describen la reconciliación, no la muerte exacta.
Los terminales con limpieza pendiente no autorizan liberar capacidad al arrancar.
Si un proceso sobrevive o su ausencia es incierta, no se habilita el servicio.

Los estados terminales con limpieza confirmada no se alteran al recuperar.
Con limpieza pendiente, se conserva el estado y se confirma la ausencia antes
de actualizar metadatos de recuperación. La reconciliación es atómica por
trabajo, no una única transacción para todo el historial, y es idempotente.
Este modelo describe la implementación; la verificación local de desarrollo
no sustituye la certificación independiente de Alexia indicada en ADR-006.

Ver [ADR-004](ADR-004-Cola-y-Limite-de-Concurrencia.md),
[ADR-005](ADR-005-Persistencia-SQLite.md) y [ADR-006](ADR-006-Recuperacion.md).
