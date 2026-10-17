# ADR-003: Protocolo y red

Estado: IPC local implementado; red remota pendiente.
**Issue relacionado:** #46

## Contexto

Jobsy deberá permitir en avances posteriores que un cliente pueda comunicarse con el servicio desde otro equipo dentro de una red autorizada.

La operación implementada es local. RF-16 menciona interfaz y puerto; su
interpretación y el alcance de red siguen pendientes de aprobación, no se
consideran satisfechos por el transporte Unix.

## Decisión

El transporte actual es AF_UNIX/SOCK_STREAM, por defecto en /tmp/jobsy.sock. cli.py envía
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

## Configuración local: Avance 2.5B

Se añade --socket-path al daemon, incluido el módulo heredado, y
JOBSY_SOCKET_PATH a todos los clientes. El daemon no lee esa variable: ambos
extremos deben seleccionar explícitamente la misma ruta. El predeterminado
continúa siendo /tmp/jobsy.sock. endpoint.py centraliza resolución y validación.

Se exigen rutas absolutas con padre existente, sin NUL ni enlace final, hasta
107 bytes después de resolver el padre. No se crean directorios ni se cambian
permisos del socket. Usar un directorio privado de confianza; no hay garantía
frente a sustituciones maliciosas del directorio por un usuario con acceso.
El arranque no borra ninguna ruta existente. El cierre solo elimina el inode
propio, comprobado sin seguir enlaces finales. Se conservan flock del directorio
de datos, JSON, Scheduler y recuperación. No se añade transporte de red.

Se evita usar --socket-path como opción de execute para no consumir argumentos
del programa enviado. La variable se lee por solicitud, no al importar el módulo.
RF-16 sigue parcialmente satisfecho: falta la decisión del profesor sobre
interfaz IP y puerto TCP. Una ruta Unix no equivale a esas opciones.

La comunicación remota deberá reutilizar las mismas operaciones principales de Jobsy, como crear, consultar, listar y cancelar trabajos.

## Alternativas consideradas en el diseño inicial

- Implementar sockets de red desde el MVP local anticiparía comunicación remota,
  pero ampliaba el alcance inicial. Los sockets Unix locales sí se implementaron.
- Integrar la comunicación directamente en `JobManager`: sería más rápido inicialmente, pero mezclaría la lógica de red con la administración de trabajos.

## Consecuencias

La separación entre IPC y gestión conserva el funcionamiento local sin añadir
red ni modificar las garantías de concurrencia y persistencia.

Más adelante será necesario definir el formato de mensajes, manejo de errores, conexiones parciales y restricciones de acceso para la operación remota.

## Verificación de desarrollo de 2.5B

En Ubuntu WSL con Python 3.14.4: 12 comprobaciones específicas del endpoint,
20 pruebas existentes de CLI, 21 de Scheduler y 3 de procesos reales aprobadas;
56 en total, sin fallos ni omisiones en esas ejecuciones. El primer intento de
cargar las tres suites como test.* falló con tres errores de importación antes
de ejecutar casos; se usó después discover con patrón explícito por archivo.

El arnés específico permanece fuera del repositorio. Utilizó sockets y datos
temporales, los seis ejecutables y procesos propios; comprobó rechazo de un
segundo daemon sobre el socket ocupado, validación, variables y protección de
enlaces al cerrar. No se accedió al daemon habitual ni a /tmp/jobsy.sock.
No se modificaron tests, exclusiones ni evidencia QA. Esta verificación técnica
no sustituye la certificación de Alexia ni repite las 105 pruebas de 2.2.
