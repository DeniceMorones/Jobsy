# Contrato del protocolo de red de Jobsy, versión 1

Estado: propuesta de arquitectura para revisión de Benjamin y transferencia a
Backend. Fecha: 16 de noviembre de 2026. No implementa ni habilita TCP.
Alcance: Avance 3.2, RF-21 (#86), RNF-14 (#19), RNF-24 (#87), RNF-32 (#88).
Los límites y plazos de este documento son decisiones propuestas, no criterios
numéricos fijados por las issues. Su implementación y certificación están pendientes.

## 1. Base actual y compatibilidad

El IPC vigente utiliza AF_UNIX/SOCK_STREAM y JSON UTF-8, sin versión ni cabecera
de longitud. Una conexión contiene una solicitud y una respuesta. El servidor
hace recv(4096) una vez; el cliente acumula fragmentos hasta poder interpretar
un JSON. Esto no constituye un protocolo con delimitación de mensajes.
Véanse los [contratos actuales](interfaces-publicas.md).

La versión 1 será un transporte adicional para el mismo JobManager, Scheduler,
Executor y repositorio SQLite. No cambia los cinco estados, la admisión durable,
la recuperación ni la semántica de cancelación. Se conservarán la CLI instalada,
los módulos heredados y el endpoint Unix con su formato actual. No se intentará
detectar automáticamente el protocolo ni degradar una conexión de red a IPC local.

El alcance es cliente-servidor con un único daemon ejecutor por instancia,
no un clúster de ejecutores ni una base SQLite compartida entre servidores.
La concurrencia de conexiones no concede reservas de ejecución adicionales.

## 2. Delimitación y transporte

Cada mensaje tiene una cabecera de **4 bytes**, entero sin signo en orden de
red (big-endian), seguida de exactamente esa cantidad de bytes de JSON UTF-8.
La longitud cuenta bytes del cuerpo; excluye la cabecera. No se añade salto de
línea ni terminador NUL. El equivalente Python es struct.pack("!I", len(body)).

| Parámetro propuesto | Valor y alcance |
| --- | --- |
| Versión | 1, entero exacto; true/false no son versiones válidas. |
| Tamaño de solicitud | 1 a 1 048 576 bytes de cuerpo. |
| Tamaño de respuesta | 1 a 1 048 576 bytes de cuerpo. |
| Espera entre solicitudes | 30 s sin recibir el primer byte; después se cierra la conexión inactiva. |
| Recepción de un mensaje | 5 s desde el primer byte de cabecera hasta el último del cuerpo, sin reiniciar el plazo con cada fragmento. |
| Envío de una respuesta | 5 s para cabecera y cuerpo completos. |
| Espera de respuesta del cliente | 30 s desde el envío completo; su vencimiento no cancela trabajos ni demuestra rechazo. |
| Profundidad JSON | Máximo 16 niveles de contenedores, incluida la raíz. |

Estos plazos limitan operaciones de transporte; no garantizan que una operación
de disco finalice en ese tiempo. Se usan relojes monotónicos y el tiempo restante
de la operación, no esperas ilimitadas ni reinicios del plazo por recv/send.

El receptor debe acumular los cuatro bytes de cabecera, validar la longitud
antes de reservar el cuerpo y recibir hasta completarlo. Debe conservar cualquier
sobrante para el mensaje siguiente. Una lectura puede contener parte de un
mensaje o varios mensajes juntos. El emisor usa sendall o un bucle que maneje
escrituras parciales; no supone que send transmite todo.

Una conexión permite múltiples solicitudes secuenciales: se procesa un mensaje
completo y se envía toda su respuesta antes de despachar el siguiente. El cliente
espera su respuesta antes de enviar otra. No se ofrece multiplexación ni ejecución
paralela dentro de una conexión; los mensajes agrupados siguen el mismo orden.
El cierre del cliente no cancela trabajos previamente admitidos.

## 3. Sobre y validación de solicitudes

```json
{"version":1,"request_id":"cli-0001","action":"run","command":["sleep","20"]}
```

- La raíz debe ser un objeto JSON. Se rechazan UTF-8 inválido, BOM, claves
  duplicadas, NaN/Infinity, texto extra tras el objeto y cadenas con sustitutos
  Unicode aislados. El límite de profundidad se verifica sin un recorrido recursivo
  no acotado; tampoco se permite que el parser exceda el límite de forma silenciosa.
- version es obligatorio. Solo se admite el entero 1; no se negocia ni adapta
  silenciosamente otra versión. Un cliente también valida la versión de respuesta.
- request_id es obligatorio: 1 a 64 caracteres ASCII de [A-Za-z0-9._:-]. Lo
  genera el cliente y el servidor lo devuelve sin alterarlo. No es un Job ID,
  credencial, clave de deduplicación ni garantía de ejecución exactamente una vez.
- action es uno de run, list, status, cancel, output, health; distingue mayúsculas.
- Se validan todos los campos antes de invocar JobManager. No se convierten
  números, listas, booleanos o null a cadenas para aceptar una solicitud inválida.
- Se rechazan campos desconocidos en solicitudes v1. Los clientes toleran campos
  adicionales en respuestas, pero verifican los obligatorios y sus tipos.

| Acción | Campos además del sobre | Resultado de éxito además de version/request_id/status |
| --- | --- | --- |
| run | command: lista no vacía de cadenas UTF-8 sin NUL; command[0] no vacío ni solo espacios. El tamaño total queda acotado por la trama. | job_id: UUID completo. Confirma admisión durable, no finalización. |
| list | status opcional: null o uno de los cinco estados en mayúsculas. | jobs: lista de objetos con id, status, command. No se promete orden FIFO del listado. |
| status | job_id: UUID completo o prefijo hexadecimal único de 8 a 32 caracteres sin guiones. | job: id, command, status, received_at, started_at, finished_at, exit_code, diagnostic. |
| cancel | job_id con las mismas reglas. | job_id completo y job_status=CANCELED. La recolección puede continuar después de responder. |
| output | job_id con las mismas reglas. | job_id completo, job_status, stdout y stderr, ambas cadenas independientes. |
| health | Sin campos adicionales. | health con los campos descritos debajo. |

Los estados son QUEUED, RUNNING, SUCCEEDED, FAILED y CANCELED. command conserva
los límites originales de argumentos y no introduce shell. exit_code es entero
o null; diagnostic es cadena o null. Las fechas conservan el formato UTC actual
YYYY-MM-DD HH:MM:SS UTC y "-" si se desconocen. No se inventan horas de salida
para trabajos reconciliados tras una interrupción.

health contiene service_active (booleano), storage_error (cadena segura o null),
running_count, queued_count y recent_errors_count (enteros no negativos), y las
listas running_jobs, queued_jobs y recent_errors. Sus elementos contienen id,
status, command, received_at, started_at, finished_at, exit_code y stderr.
recent_errors contiene como máximo diez FAILED, del más reciente al más antiguo,
según finished_at o received_at. Los conteos corresponden a las listas de la
misma instantánea. running_count cuenta estados RUNNING: no representa todas
las reservas, que pueden incluir QUEUED o CANCELED en limpieza.

Los UUID persistentes y los ID de respuesta permanecen completos. El acortamiento
es presentación de la CLI. La resolución de prefijos se realiza contra todo el
historial cargado y bajo la Condition del gestor antes de leer o cancelar.
Un prefijo ambiguo se rechaza; nunca se elige el primer resultado. Las consultas
automatizadas deben conservar el UUID completo.

## 4. Respuestas y errores

```json
{"version":1,"request_id":"cli-0001","status":"ok","job_id":"a1b2c3d4-1234-4567-89ab-123456789abc"}
```

```json
{"version":1,"request_id":"cli-0002","status":"error","code":"AMBIGUOUS_JOB_ID","operation":"cancel","cause":"El prefijo identifica varios trabajos.","suggestion":"Utilice más caracteres o consulte jobsy list --full-id."}
```

Toda respuesta contiene version=1, request_id y status. Para errores previos a
poder validar el sobre, request_id es null y operation es "desconocida"; no se
reflejan datos arbitrarios de una solicitud corrupta. El error añade code,
operation, cause y suggestion, todos cadenas. Las causas públicas no incluyen
tracebacks, SQL, secretos ni rutas privadas del servidor. La [política 3.4](seguridad-lan-vpn.md)
propone que operadores autenticados compartan acceso a todos los resultados
de su instancia; no incorpora ownership por trabajo. Estos errores JSON se
aplican después de autorizar el canal: un rechazo previo de IP o TLS cierra
la conexión sin emitir una respuesta JSON en texto claro.

| code | Tratamiento propuesto |
| --- | --- |
| INVALID_LENGTH | Longitud cero o superior al límite: error acotado y cierre sin leer el cuerpo declarado. |
| INVALID_ENCODING / INVALID_JSON | UTF-8/JSON inválido o profundidad excesiva: error y cierre. |
| INCOMPLETE_MESSAGE / READ_TIMEOUT | Cabecera/cuerpo parcial o plazo vencido: error si aún se puede escribir, seguido de cierre. |
| UNSUPPORTED_VERSION | Versión presente con tipo o valor incompatible: error y cierre, sin ejecutar la acción. |
| INVALID_REQUEST | Raíz, sobre, campos, tipos o argumentos inválidos: sin efectos. Puede continuar si version y request_id fueron validados; en otro caso, cierre. |
| UNKNOWN_ACTION | Sobre válido con acción desconocida: error y conexión disponible. |
| JOB_NOT_FOUND / AMBIGUOUS_JOB_ID | No resolver el identificador: error sin efectos y conexión disponible. |
| INVALID_JOB_STATE | Cancelación repetida o sobre un estado terminal: conservar el estado y responder error. |
| QUEUE_FULL | Rechazo atómico sin trabajo residual; conexión disponible. |
| SERVICE_UNAVAILABLE / STORAGE_ERROR | No aceptar nuevas ejecuciones si el gestor está cerrado o falló persistencia; conservar su política de bloqueo. |
| RESPONSE_TOO_LARGE | Respuesta que supera el límite: sustituirla por un error acotado, sin truncar JSON ni deshacer efectos ya confirmados. |
| INTERNAL_ERROR | Fallo inesperado de una operación: respuesta sanitizada y cierre de esa conexión. |

Antes de enviar se calcula el tamaño real del JSON codificado. list, health u
output pueden superar el límite; v1 responde RESPONSE_TOO_LARGE de forma explícita.
La paginación o transferencia de resultados grandes queda como extensión pendiente
de aprobación; esta propuesta no promete consultar salidas arbitrariamente grandes.

EOF entre mensajes es cierre normal. EOF a mitad de mensaje impide ejecutarlo;
si el par ya cerró ambos sentidos puede no recibir el error. Un fallo al enviar
no se resuelve enviando otro JSON sobre una trama parcial: se cierra la conexión.
El cliente verifica request_id y version antes de asociar o mostrar una respuesta.

## 5. Reintentos, atomicidad y límites de concurrencia

Cada run válido y aceptado es una nueva orden, incluso si se repiten command o
request_id. Consultas repetidas son lecturas sin efectos; los datos pueden cambiar
entre instantáneas. Una segunda cancelación terminal devuelve error. Se conserva
la semántica del sistema local, sin prometer deduplicación de reintentos.

Si se pierde la respuesta a run o cancel, el resultado es desconocido para el
cliente. No se reenvía automáticamente: el efecto pudo confirmarse en SQLite.
El cliente consulta el historial antes de decidir una nueva operación.

El manejador de red valida y llama a las interfaces públicas del mismo gestor.
No crea procesos, modifica estados ni libera reservas directamente. No mantiene
locks de JobManager durante recv/send, esperas de clientes ni joins. La cola
FIFO se ordena por admisión bajo la Condition, no por orden de llegada entre
clientes. El límite del Scheduler sigue siendo de procesos principales por daemon.

## 6. Integración y decisiones pendientes

La implementación de transporte y atención de múltiples clientes corresponde a
Backend, coordinada con Benjamin. Se propone separar codificación/framing,
validación del sobre, despacho de operaciones y transporte; las funciones de
framing deben aceptar un stream inyectable para pruebas sin una red real.
No se propone reemplazar JobManager, Scheduler, Executor ni SQLite.

La [política de Avance 3.4](seguridad-lan-vpn.md) y [ADR-009](ADR-009-Seguridad-LAN-VPN.md)
proponen red desactivada por defecto, bind explícito, lista LAN/VPN, cupos
de conexiones y TLS mutuo con operadores autorizados. El filtro del origen
real y la autenticación se realizan antes de procesar v1; el handshake tiene
un plazo propio, separado de los plazos de mensajes de este contrato.
Framing, request_id y Job ID no autentican a nadie; no se añade login ni
una credencial al JSON. Las seis operaciones permanecen sin cambios.

Se requiere aprobar e implementar ambas propuestas antes de habilitar red.
No se debe exponer el servicio públicamente ni presentar estos documentos
como implementación o certificación de seguridad.

## 7. Escenarios de verificación del contrato

Esta lista es transferencia técnica para Backend y QA, no casos formales ni
evidencia de ejecución. No se han implementado ni probado las funciones v1.

| Requisito | Escenarios que debe verificar la implementación |
| --- | --- |
| RF-21 #86 | Las seis operaciones y sus errores; Unicode y argumentos con espacios; admisión durable; envío parcial; desconexión tras confirmar run sin reintento automático. |
| RNF-14 #19 | Longitudes 0, 1, límite y límite+1; cuerpo menor que la longitud; UTF-8 inválido; tipos erróneos; claves duplicadas; profundidad excesiva; rechazo antes de efectos. |
| RNF-24 #87 | Cabecera byte a byte; cuerpo y caracteres UTF-8 partidos; dos tramas en una lectura; varias solicitudes secuenciales; EOF intermedio; plazos que no se renuevan con tráfico lento. |
| RNF-32 #88 | Versión ausente, 0, 2, "1", true y null; rechazo explícito; respuesta de otra versión o request_id; compatibilidad del socket Unix heredado. |
| Integración | Respuestas demasiado grandes; prefijos ambiguos; múltiples clientes sin exceder reservas; historial tras reinicio; socket y datos temporales. |

Referencias: [ADR-003](ADR-003-Protocolo-Red.md),
[ADR-008](ADR-008-Protocolo-de-Red-Versionado.md),
[interfaces públicas](interfaces-publicas.md),
[semántica de duplicados](semantica-duplicados.md).
