# ADR-003: Protocolo y red

**Estado:** Provisional  
**Issue relacionado:** #46

## Contexto

Jobsy deberá permitir en avances posteriores que un cliente pueda comunicarse con el servicio desde otro equipo dentro de una red autorizada.

En el MVP actual la operación es local, por lo que todavía no se requiere implementar la comunicación por red.

## Decisión

La lógica de comunicación se mantendrá separada del resto de la aplicación dentro del módulo `src/protocol`.

En esta etapa no se implementará todavía un protocolo de red completo. La definición de mensajes, transporte y manejo de conexiones se realizará en un avance posterior.

La comunicación remota deberá reutilizar las mismas operaciones principales de Jobsy, como crear, consultar, listar y cancelar trabajos.

## Alternativas consideradas

- Implementar sockets desde el MVP local: permitiría avanzar desde ahora con la comunicación remota, pero agrega complejidad innecesaria para el alcance actual.
- Integrar la comunicación directamente en `JobManager`: sería más rápido inicialmente, pero mezclaría la lógica de red con la administración de trabajos.

## Consecuencias

La separación del módulo `protocol` permite desarrollar primero el funcionamiento local sin depender de la red.

Más adelante será necesario definir el formato de mensajes, manejo de errores, conexiones parciales y restricciones de acceso para la operación remota.
