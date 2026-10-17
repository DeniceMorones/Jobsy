# Modelo de estados de Jobsy: Avance 2.1

Relacionado con RF-03, RF-05, RNF-07 y el modelo inicial del Issue #43.

## Estados y transiciones

| Origen | Evento | Destino |
| --- | --- | --- |
| QUEUED | Popen exitoso y proceso publicado | RUNNING |
| QUEUED | Error de lanzamiento | FAILED |
| QUEUED | Cancelación o apagado antes del lanzamiento | CANCELED |
| RUNNING | Proceso recolectado con código 0 y sin error de captura | SUCCEEDED |
| RUNNING | Proceso recolectado con código distinto de 0 o error de captura | FAILED |
| RUNNING | Solicitud de cancelación | CANCELED |
| RUNNING | Error al crear o arrancar el hilo supervisor | CANCELED |

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

Cancelar establece un evento y el estado CANCELED bajo la Condition. Si aún
no hay proceso, se retira de la cola o reservas listas. Si Popen ya comenzó,
la cancelación espera la publicación bajo el mismo lock. Si el lanzamiento
falla o la finalización gana la carrera y ya dejó un estado terminal, se
rechaza cancelar. En caso contrario, el supervisor termina y recolecta el
proceso. No hay resurrección del trabajo cancelado.

La reserva no depende de contar RUNNING: permanece durante limpieza y se
libera exactamente una vez. Una reserva sin proceso se puede liberar al
cancelar antes del lanzamiento. Si no se confirma la limpieza de un proceso,
permanece ocupada y se registra el diagnóstico en stderr; no se fuerza FAILED
ni finished_at. El estado conserva su valor previo (RUNNING o CANCELED).
Por ello una cancelación aceptada no significa que el slot esté libre todavía.

Ver [ADR-004](ADR-004-Cola-y-Limite-de-Concurrencia.md). Todo permanece en RAM;
este modelo no implementa persistencia ni recuperación después de reiniciar.
