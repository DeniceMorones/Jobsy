# Índice de decisiones arquitectónicas

Responsable: Benjamin, Arquitecto. Revisión documental: 16 de noviembre de 2026.
Alcance: [Avance 3.6, #123](https://github.com/DeniceMorones/Jobsy/issues/123).
Línea base inspeccionada: be1e71c en benjamin-dev, con cambios locales de 3.2/3.4.
Las propuestas no están implementadas ni aprobadas por el hecho de figurar aquí.

## Registro y vigencia

| ADR | Decisión y alcance | Estado al revisar | Relación y vigencia |
| --- | --- | --- | --- |
| [001](ADR-001-Lenguaje-y-Stack.md) | Python y biblioteca estándar, SQLite y plataforma Linux. | Aceptado; stack vigente. | No certifica versiones/plataformas no ejecutadas. |
| [002](ADR-002-Concurrencia-IPC.md) | Hilos/procesos e IPC del MVP inicial. | Histórico, parcialmente sustituido. | El IPC lo actualiza 003; la planificación acotada, 004. No aplicar la ausencia histórica de IPC. |
| [003](ADR-003-Protocolo-Red.md) | Socket Unix y configuración local. | Implementado localmente; evolución remota propuesta. | 008/009 definen propuestas de protocolo y seguridad; no habilitan TCP. |
| [004](ADR-004-Cola-y-Limite-de-Concurrencia.md) | FIFO, reservas, capacidad y sincronización. | Implementado; invariantes vigentes. | 010 extiende el acceso de clientes, no multiplica gestores ni reservas. |
| [005](ADR-005-Persistencia-SQLite.md) | Repositorio, esquema v1 y transacciones durables. | Implementado. | Se conserva en la migración; no implica SQLite compartida entre hosts. |
| [006](ADR-006-Recuperacion.md) | Exclusividad, identidad y recuperación sin reejecución. | Implementado. | Reconciliar antes de escuchar por cualquier transporte. |
| [007](ADR-007-Cancelacion.md) | Intención durable, señales, recolección y reservas. | Describe la implementación integrada. | Desconectar al cliente no es cancelar; 010 conserva ese límite. |
| [008](ADR-008-Protocolo-de-Red-Versionado.md) | Framing, versión, mensajes parciales, errores y correlación. | Propuesto; implementación/QA pendientes. | Especificación: protocolo-red-v1.md. Requiere 009 y 010. |
| [009](ADR-009-Seguridad-LAN-VPN.md) | Redes permitidas, mTLS, confianza y mínimo privilegio. | Propuesto; revisión/implementación/QA pendientes. | Política y modelo de amenazas separados; impacto en CR-001. |
| [010](ADR-010-Concurrencia-Clientes-Remotos.md) | Clientes remotos concurrentes y un núcleo compartido. | Propuesto; revisión/implementación/QA pendientes. | Explicita el alcance de «concurrencia distribuida» de #123. |

## Revisión del bloque 3.6

Se contrastaron los ADRs con server.py, JobManager, Scheduler, la persistencia y
los contratos actuales. Se conserva el contenido histórico y se aclara su vigencia;
no se reescriben decisiones correctas para aparentar una implementación nueva.
Los ADRs 001, 003, 005, 006 y 007 no requieren cambios de comportamiento en esta
revisión. 002 se identifica como histórico; 004, 008 y 009 se enlazan con 010 y
el control de cambios. El [CR-001](CR-001-Migracion-Arquitectura-Red.md) registra
alcance, impacto, riesgos, secuencia, reversión y aprobaciones pendientes.

La corrección local de IDs cortos conserva UUID, esquema y respuestas IPC; está
documentada en [interfaces públicas](interfaces-publicas.md) y no es evidencia
de transporte remoto, deduplicación o autorización.

## Evidencia y control de estados

Las notas de 46/105 pruebas de los ADRs son verificaciones históricas de desarrollo.
La [revisión formal de Alexia](../qa/technical-review-2.md) registra 149 PASS sobre
10c7a8e para su alcance de Avance 2. No se reejecutó ni extendió esa certificación
a los cambios pendientes de IDs ni a los diseños de red de Avance 3.
Las expresiones «QA pendiente» de las notas originales describen su momento de
registro; consultar la revisión de QA para su alcance posterior, sin alterar sus archivos.

Esta revisión comprueba coherencia documental, enlaces y diff; no ejecuta pruebas
funcionales. Para actualizar un ADR a implementado, registrar el cambio concreto
y su revisión; para afirmar verificación, enlazar resultados del alcance/versionado
real. Una aprobación arquitectónica, implementación y certificación son hitos distintos.

No se cierran #123/#125 ni se aprueba el despliegue mediante este índice. El
registro global de riesgos, cronograma, trazabilidad, guías finales y evidencias
siguen bajo los responsables de [la matriz de roles](../../project-management/Matriz-Roles.md).
