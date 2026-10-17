# ADR-003: Protocolo y red

Estado: IPC local implementado; red remota pendiente.
**Issue relacionado:** #46

## Contexto

Jobsy deberá permitir en avances posteriores que un cliente pueda comunicarse con el servicio desde otro equipo dentro de una red autorizada.

La operación implementada es local. RF-16 menciona interfaz y puerto; su
interpretación y el alcance de red siguen pendientes de aprobación, no se
consideran satisfechos por el transporte Unix.

## Decisión

El transporte actual es AF_UNIX/SOCK_STREAM en /tmp/jobsy.sock. cli.py envía
JSON UTF-8 y server.py atiende run, list, status y cancel. El módulo
src/protocol/validation.py valida argumentos; no contiene el transporte ni
autoriza comandos. JobManager no realiza operaciones de socket.

Cada conexión contiene una solicitud y una respuesta. Cliente y servidor hacen
una única lectura de hasta 4096 bytes, sin framing ni lectura incremental.
No se garantizan mensajes grandes o fragmentados. La recepción es secuencial;
Scheduler ejecuta trabajos concurrentemente. Véanse los
[contratos públicos](interfaces-publicas.md).

RF-16 (#72) sigue parcial: existen --data-dir, --max-running y --queue-capacity,
pero no interfaz IP ni puerto configurables. Una ruta Unix no equivale a ambos.
No hay transporte TCP, autenticación remota ni exposición LAN implementados.
La decisión de transporte y seguridad requiere aprobación separada de 2.5A.

La comunicación remota deberá reutilizar las mismas operaciones principales de Jobsy, como crear, consultar, listar y cancelar trabajos.

## Alternativas consideradas en el diseño inicial

- Implementar sockets de red desde el MVP local anticiparía comunicación remota,
  pero ampliaba el alcance inicial. Los sockets Unix locales sí se implementaron.
- Integrar la comunicación directamente en `JobManager`: sería más rápido inicialmente, pero mezclaría la lógica de red con la administración de trabajos.

## Consecuencias

La separación entre IPC y gestión conserva el funcionamiento local sin añadir
red ni modificar las garantías de concurrencia y persistencia.

Más adelante será necesario definir el formato de mensajes, manejo de errores, conexiones parciales y restricciones de acceso para la operación remota.
