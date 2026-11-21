# ADR-010: Concurrencia entre clientes remotos

Estado: propuesto; pendiente de revisión de Benjamin, implementación de Backend
y verificación independiente de QA. Fecha: 16 de noviembre de 2026.
Entregable: [ADRs actualizados #123](https://github.com/DeniceMorones/Jobsy/issues/123).
Relacionados: RF-18 (#84), RF-19 (#85), RF-22 (#89), RNF-07 (#26), RNF-25 (#28).
Complementa [ADR-004](ADR-004-Cola-y-Limite-de-Concurrencia.md),
[ADR-008](ADR-008-Protocolo-de-Red-Versionado.md) y
[ADR-009](ADR-009-Seguridad-LAN-VPN.md). Impacto: [CR-001](CR-001-Migracion-Arquitectura-Red.md).

## Contexto y alcance de la distribución

El servidor actual atiende conexiones Unix secuencialmente; los trabajos sí se
ejecutan concurrentemente mediante Scheduler. El nuevo transporte debe atender
clientes en otros equipos sin multiplicar gestores ni reservas de ejecución.

La expresión «concurrencia distribuida» de #123 se concreta aquí como clientes
distribuidos que comparten un único daemon ejecutor. Las issues consultadas no
especifican varios nodos ejecutores, consenso, balanceo entre servidores ni alta
disponibilidad. Este alcance requiere confirmación arquitectónica; si se exige
un clúster, debe ampliarse el Change Request antes de implementar. No se presenta
el lock local ni SQLite como coordinación distribuida entre hosts.

## Decisión propuesta

### Una instancia y dos transportes

Mantener un JobManager, Scheduler, Executor y PersistenceRuntime por instancia.
El endpoint Unix heredado y el listener remoto opcional invocan el mismo núcleo.
La recuperación concluye antes de aceptar solicitudes por cualquiera de ellos.
No abrir un repositorio ni crear un gestor por cliente. La exclusividad del
directorio de datos continúa siendo la definida en ADR-006.

El formato Unix se conserva. El listener remoto exige los controles de ADR-009
y después procesa el contrato v1 de ADR-008. No detectar automáticamente ambos
formatos ni realizar fallback a otro endpoint tras un error de red.

### Conexiones concurrentes, solicitudes secuenciales

Se propone un worker de hilo por conexión remota admitida, con un cupo adquirido
antes de crearlo. Los límites global y por IP incluyen handshakes y conexiones
inactivas; sus valores y plazos se mantienen en [la política 3.4](seguridad-lan-vpn.md).
No crear hilos ilimitados ni una cola ilimitada de sockets esperando worker.
Si falla la creación del worker, cerrar el socket propio y devolver el cupo.

Dentro de cada conexión se completa una solicitud y su respuesta antes de
despachar la siguiente. Entre conexiones puede haber llamadas concurrentes al
gestor. No hay multiplexación por request_id ni un hilo adicional por mensaje.
Cada worker conserva sus buffers, identidad autorizada y datos de correlación;
no utiliza una variable global «cliente actual». Su excepción no cierra el servicio.

Los workers de red no son supervisores de trabajos. Una conexión cerrada devuelve
su cupo de red; un trabajo solo devuelve su reserva según las reglas de ADR-004
y ADR-007. El límite de conexiones no altera max_running ni queue_capacity.

### Despacho y sincronización

El dispatcher recibe datos ya validados y reutiliza estas interfaces:

| Operación | Interfaz del gestor |
| --- | --- |
| run | submit_job(command); la respuesta usa el UUID canónico admitido. |
| list | list_jobs(status); serializar las copias devueltas. |
| status / output | snapshot(job_id); no consultar objetos vivos mediante get_job. |
| cancel | cancel_job(job_id); el resultado confirma intención, no recolección inmediata. |
| health | get_health_summary(); serializar la instantánea obtenida bajo la Condition. |

La capa de transporte no modifica jobs, pending, ready, reservations ni tablas
SQLite. No usa create_job seguido de execute como sustituto de submit_job.
El dispatcher compartido debe preservar las respuestas Unix existentes; el
adaptador v1 añade su sobre, validación y errores estables sin copiarlos al IPC
heredado de forma incompatible. Sanitizar errores de red según ADR-008/009.

Se conservan Condition -> lock del repositorio -> SQLite. El lock de conexiones
solo protege cupos, registro de workers y cierre de admisión a mensajes; se
libera antes de llamar al gestor. No anidar ese lock con la Condition ni hacer
TLS, recv/send, cierre de sockets o joins bajo locks compartidos. Serializar y
enviar las copias después de que regresen las llamadas al gestor.

El orden FIFO se determina al admitir bajo la Condition, no por la hora del
cliente, conexión o request_id. No se promete equidad por usuario. Popen y los
commits siguen en las secciones críticas actuales: una operación lenta puede
retrasar otras consultas. Múltiples workers no garantizan por sí solos RNF-05.

### Fallos, desconexiones y cierre

Una trama incompleta se descarta sin despachar. Una vez iniciada la operación,
perder la conexión no revierte un commit ni cancela el trabajo. Si se pierde la
respuesta de run/cancel, el cliente no puede inferir si hubo efecto y no reintenta
automáticamente. request_id correlaciona, no deduplica. Consultas repetidas no
mutan trabajos, pero pueden observar estados distintos con el paso del tiempo.

Orden propuesto de apagado, coordinado por el hilo principal:

1. La señal solicita cierre; no hace joins ni operaciones de procesos en el handler.
2. Marcar cierre de admisión de conexiones y mensajes, y detener listeners.
   La comprobación de cierre y el registro de una operación en curso deben ser
   atómicos bajo el control de conexiones. Una operación que ganó esa carrera
   permanece registrada hasta regresar del gestor; las posteriores no se despachan.
3. Cerrar sockets propios para interrumpir lecturas/handshakes/esperas de envío.
   Dejar terminar las llamadas al gestor ya iniciadas; una respuesta puede perderse.
   Unir todos los workers fuera de locks antes de cerrar el gestor o su repositorio.
4. Ejecutar una sola vez el apagado de JobManager: cancelar pendientes, aplicar
   la gracia existente y terminar/recolectar mediante los supervisores.
5. Cerrar sesión/base/lock después del núcleo; marcar cierre limpio únicamente
   si terminó sin errores. Retirar solo el inode del socket Unix propio.

No cerrar SQLite mientras un worker aún puede usarla ni considerar que el flag
de cierre o un hilo daemon equivalen a limpieza. Los plazos de red no interrumpen
commits ni Popen y no constituyen una cota total del apagado. No se añade una
cancelación remota al desconectar; la política de apagado del servicio se conserva.

## Alternativas y consecuencias

- Un bucle secuencial para todos los clientes reduce complejidad, pero un peer
  lento ocupa la recepción de los demás; no satisface el objetivo de atención concurrente.
- asyncio/selectors permite multiplexar sockets, pero integrar sqlite3 y llamadas
  bloqueantes del gestor exige delegación adicional. Se difiere hasta medir necesidad.
- Un proceso/gestor por cliente fragmentaría la cola y el límite global; se descarta.
- Un clúster de ejecutores exige ownership de trabajos, coordinación entre nodos
  y otra persistencia/recuperación; queda fuera de la propuesta actual.

La solución conserva la biblioteca estándar y las invariantes de Avance 2.
Su capacidad real depende de memoria, disco, TLS y planificación del SO. El
límite de trama no acota toda la memoria de captura/serialización ni el historial.

## Verificación que se transfiere

Backend implementará y Alexia definirá casos/evidencia independientes: operaciones
Unix/remotas simultáneas con el mismo gestor; FIFO y cola llena; conexiones lentas
o fallidas sin fuga de cupos; cancelación en carrera; respuesta perdida después
del commit; cierre con workers en lectura y en una operación; reinicio sin
reejecución; consultas con 100 trabajos para RNF-05. Deben usarse exclusivamente
datos, sockets, certificados, puertos y procesos de prueba aislados.

Este ADR no registra resultados de esas pruebas ni certifica la red. Los riesgos
y condiciones de revisión se detallan en CR-001; no se modifican archivos de QA.
