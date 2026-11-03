# ADR-002: Concurrencia e IPC

Nota de evolución: este ADR conserva el contexto histórico del MVP. El IPC
actual usa sockets Unix (ADR-003) y la planificación acotada se define en
[ADR-004](ADR-004-Cola-y-Limite-de-Concurrencia.md), que sustituye la decisión
de concurrencia sin límite. La ausencia de IPC descrita abajo ya no aplica.

**Estado:** Aceptado  
**Issue relacionado:** #46

## Contexto

Jobsy debe poder ejecutar trabajos sin bloquear la administración de otros trabajos.

Cada trabajo se ejecuta como un proceso independiente y el sistema necesita mantener información sobre su estado, salida y código de finalización.

## Decisión

Para el MVP local se utilizarán hilos de Python para iniciar la ejecución de trabajos sin bloquear el flujo principal de Jobsy.

Cada trabajo será ejecutado mediante `subprocess.Popen`, lo que permite mantener una referencia al proceso y realizar operaciones como consultar su resultado o solicitar su cancelación.

Durante este avance, la comunicación entre los componentes internos de Jobsy se realizará dentro del mismo programa, sin implementar todavía un mecanismo externo de IPC.

## Alternativas consideradas

- Ejecutar los trabajos de forma síncrona: se descartó porque un trabajo activo bloquearía el flujo principal del sistema.
- Usar `multiprocessing`: permite separar procesos de Python, pero agrega complejidad que no es necesaria para el MVP actual.
- Utilizar sockets locales desde este avance: permitiría separar más los componentes, pero se dejará para la etapa cliente-servidor.

## Consecuencias

El sistema puede ejecutar trabajos en segundo plano sin bloquear completamente la administración local.

La solución mantiene simple el MVP actual, aunque el manejo de concurrencia deberá revisarse en avances posteriores cuando se agreguen múltiples clientes, persistencia y operación remota.
