# CR-001: Migración controlada a arquitectura de red

## 1. Identificación y estado

| Campo | Registro |
| --- | --- |
| Proyecto / entregable | Jobsy, Avance 3.6, [Change Request #125](https://github.com/DeniceMorones/Jobsy/issues/125). |
| Identificador | CR-001, identificador documental local de esta solicitud; no se encontró otro CR numerado en los Markdown revisados. |
| Versión y fecha | 0.1, 16 de noviembre de 2026. |
| Autor del análisis | Benjamin, Arquitecto de Software. |
| Origen | Migración requerida por Avance 3 y solicitud de preparar el entregable arquitectónico #125. No se atribuye aprobación al profesor ni al equipo. |
| Línea base | Commit be1e71c98ca0bf405eb98f9eca62b1a9696abd74 en benjamin-dev. Incluye Avance 2 integrado; hay cambios locales no confirmados de 3.2/3.4 e IDs cortos. |
| Destino de integración previsto | PR de benjamin-dev hacia dev; no hacia main. No se crea ni publica un PR en esta revisión. |
| Estado | Propuesto para revisión; análisis redactado. Migración de red no implementada ni certificada. |

Las issues [#123](https://github.com/DeniceMorones/Jobsy/issues/123) y #125 tienen
título, pero no descripción adicional ni comentarios al consultarlas. La épica
[#120](https://github.com/DeniceMorones/Jobsy/issues/120) pide reunir los entregables
finales. No se encontró una plantilla de CR con campos de aprobación obligatorios.
Este registro propone el cambio y su control; no inventa una solicitud aprobada
ni una migración ya aplicada. Su numeración puede conciliarse con Gestión sin
alterar el contenido técnico.

## 2. Motivo, situación actual y resultado esperado

Hoy CLI y daemon se comunican por socket Unix en el mismo entorno Linux. La
recepción del servidor es secuencial, sin framing/versionado. Hay Scheduler FIFO,
reservas acotadas, SQLite durable, recuperación conservadora y seis operaciones:
run, list, status, cancel, output, health. No hay TCP, TLS ni reglas remotas CIDR.

[RF-18 #84](https://github.com/DeniceMorones/Jobsy/issues/84) requiere operar desde
otro equipo; [RF-19 #85](https://github.com/DeniceMorones/Jobsy/issues/85) exige
conservar la semántica local/remota. Se propone añadir un transporte remoto
opcional y protegido, compartiendo el núcleo existente, sin reemplazar IPC Unix.

El objetivo arquitectónico es separar framing, validación, seguridad, transporte
y despacho. Un cliente lento o desconectado no debe retener un lock del gestor,
corromper un trabajo ni cerrar el servicio ([RF-22 #89](https://github.com/DeniceMorones/Jobsy/issues/89)).

## 3. Alcance y decisiones vinculadas

| Decisión propuesta | Documento normativo de diseño | Impacto |
| --- | --- | --- |
| Cuerpo JSON con longitud, versión, correlación y errores estables; mensajes secuenciales. | [ADR-008](ADR-008-Protocolo-de-Red-Versionado.md) y [contrato v1](protocolo-red-v1.md). | Adaptadores nuevos; Unix conserva su formato. |
| TCP desactivado por defecto; bind explícito, lista IP/CIDR, mTLS y certificados autorizados. | [ADR-009](ADR-009-Seguridad-LAN-VPN.md), [política](seguridad-lan-vpn.md), [amenazas](modelo-amenazas-lan-vpn.md). | Configuración, credenciales y despliegue adicionales; no es seguridad ya disponible. |
| Clientes en distintos equipos, un único daemon con workers de conexión acotados. | [ADR-010](ADR-010-Concurrencia-Clientes-Remotos.md). | Concurrencia de red separada de reservas; cierre coordinado de ambos transportes. |
| Conservar estados, UUID, FIFO, commits, señales y recuperación. | ADR-004 a ADR-007, en el [índice](indice-adrs.md). | Sin migración de esquema ni reejecución del historial como parte de este CR. |

Los valores numéricos de red se mantienen en los contratos 3.2/3.4 para evitar
copias divergentes. Son propuestas que requieren revisión; no criterios añadidos
a las issues. RF-16 (#72) permanece parcial hasta implementar la configuración
de interfaz/puerto acordada y verificar su aceptación.

Fuera del alcance propuesto: clúster, consenso, failover entre ejecutores,
replicación/SQLite compartida entre hosts, exactly-once, ownership por usuario,
sandbox, exposición pública y paginación de resultados. Si «concurrencia
distribuida» exige varios ejecutores, #123 necesita aclaración y una revisión
del alcance; no se puede dar por satisfecho con locks locales.

Los IDs cortos son una corrección local independiente ya pendiente en el árbol:
src/protocol/job_ids.py, src/client/cli.py y src/daemon/job_manager.py. No cambian
UUID durables, esquema ni protocolo. Se preservan; no justifican afirmar que la
migración remota está implementada y no se revierten por desactivar la red.

## 4. Impacto técnico y archivos previstos

Esta tabla orienta la implementación de Denice; **ninguno de estos cambios de
código se realiza en la revisión 3.6**. Nombres de módulos nuevos propuestos,
pendientes de conciliación con Backend.

| Archivo o área | Cambio previsto y condición de compatibilidad |
| --- | --- |
| src/protocol/framing.py, src/protocol/messages.py (nuevos) | Codec de bytes y validación v1 sin procesos ni SQLite; stream inyectable. No reutilizar la lectura única de 4096 bytes como framing. |
| src/protocol/security.py (nuevo) | Política IP/CIDR y certificados/contextos TLS, independiente del gestor. |
| src/daemon/network_server.py (nuevo) | Listener, workers acotados, peer real, plazos, registro/cierre de conexiones. Sin colas de trabajos propias. |
| src/daemon/request_dispatcher.py (nuevo) | Extraer despacho reutilizable de server.py, conservando los contratos Unix; adaptar sobre y errores v1 por separado. No duplicar lógica de trabajos. |
| src/daemon/server.py | Composición de transportes y ciclo de vida único; persistencia antes de escuchar y cierre del repositorio después de workers/núcleo. Mantener protección del socket ajeno. |
| src/daemon/config.py | Validar toda la configuración propuesta de red; valores locales existentes conservados. Un error no activa otra interfaz ni texto claro. |
| src/client/transport.py (nuevo), src/client/cli.py | Selección explícita local/remota, TLS/framing/plazos; sin reintentar run/cancel ni consumir flags del programa enviado a execute. UX de configuración remota por acordar antes de editar argparse. |
| src/daemon/logger.py y puntos de log de server.py/job_manager.py | Integración de RNF-15 de Denice: sanitizar metadatos, correlación por conexión y evitar argumentos/salidas/errores crudos. Hoy se registran comandos; cambiar solo el transporte no resuelve esa fuga. |
| JobManager, Scheduler, Executor, JobRepository, PersistenceRuntime, RecoveryService | Reutilizar interfaces/invariantes. No se prevé cambiar esquema, estados ni planificación; cualquier necesidad nueva se revisa en el CR. |
| pyproject.toml / instalación | Conservar seis console scripts y biblioteca estándar; sin dependencia pip de ejecución nueva prevista. Revisar disponibilidad de ssl/OpenSSL del entorno, no afirmar compatibilidad no probada. |
| Documentación final de uso y QA | Jocelyn actualizará guías/README finales; Alexia definirá pruebas, scripts, matriz y evidencia. Esta tarea aporta enlaces y escenarios, no modifica sus archivos. |

Impacto alto: servidor/cierre, credenciales, política de acceso y observabilidad.
Impacto medio: cliente, selección de transporte, codec y validadores. Impacto
esperado bajo en el modelo de datos, pero debe verificarse mediante regresión.
Es una valoración cualitativa para revisión, no una estimación de horas o costo.

### Consistencia, rendimiento y recursos

Ambos transportes usan un solo gestor; solo submit_job admite trabajos. Se
conservan los cinco estados, reservas hasta recolección, rechazo sin residuo,
publicación después de commit y recuperación sin ejecutar comandos históricos.
Los workers no acceden directamente a la base ni liberan reservas del Scheduler.

La nueva frontera de red agrega latencia TLS, buffers, descriptores e hilos. Los
cupos de conexión limitan admisión de sockets, no CPU, todo el historial o las
salidas en memoria. La serialización puede ser costosa antes de detectar una
respuesta demasiado grande; v1 requiere error explícito, no truncamiento.

[RNF-05 #96](https://github.com/DeniceMorones/Jobsy/issues/96) exige status en un
máximo de 1 segundo con 100 trabajos en el entorno de prueba. No está demostrado
para red. Popen/commits bajo la Condition y almacenamiento lento pueden demorar
consultas; añadir hilos no elimina esa contención. Backend/QA deben acordar y
registrar si la medición incluye conexión y handshake, además de hardware,
dataset, carga y transporte, sin reducir silenciosamente el criterio de la issue.

## 5. Riesgos y verificación asociada

Análisis técnico de Benjamin para aportar a [RNF-34 #97](https://github.com/DeniceMorones/Jobsy/issues/97).
No sustituye el registro de riesgos de Jocelyn ni los casos o resultados de Alexia.
Cada escenario es una comprobación requerida, **no una prueba ejecutada**.

| Riesgo / impacto | Mitigación y límite | Escenario para revisión independiente |
| --- | --- | --- |
| Exposición pública o acceso no autorizado: crítico. | Política 3.4, TLS mutuo y redes explícitas; revisión del host/WSL/VPN. La IP privada sola no autentica. | Defaults, bind comodín/público, CIDR inválido, peer fuera de lista, certificado/SAN/huella incorrectos; confirmar que no se invoca el gestor. |
| Operador comprometido o trabajo malicioso: crítico. | Cuenta dedicada sin root y operadores de confianza; mismo UID permite acceder a DB, logs y futura clave TLS. No es sandbox. | Revisar permisos/entorno en instancia desechable y aceptación del modelo compartido; si se exige aislamiento, detener habilitación y ampliar diseño. |
| Duplicación por respuesta perdida: alto. | No reintentar automáticamente; request_id no deduplica. Conservar commit y consultar historial. | Desconexión después de commit de run/cancel; verificar efecto durable sin reejecución automática. |
| Varios gestores o liberación prematura: alto. | Un núcleo para ambos transportes y cupos separados. | Mezclar clientes Unix/remotos; máximos 1/3, cola cero/llena, cancelación/lanzamiento concurrentes y recolección. |
| Cierre de SQLite con worker activo: alto. | Barrera de cierre y joins antes de cerrar el núcleo/repositorio, sin locks durante I/O. | Apagar una instancia propia con clientes leyendo, enviando y ejecutando operaciones; verificar limpieza y reapertura coherente. |
| Bloqueo tras caída o pérdida de salida aún no persistida: alto. | Conservar recuperación conservadora; no reejecutar, matar PIDs históricos ni borrar base para desbloquear. | Caída aislada, identidad incierta/superviviente, cola persistida, rollback y base corrupta; comparar con ADR-006. |
| Cliente lento, saturación o memoria de resultados: alto. | Cupos/plazos, framing acotado y error de respuesta grande; no garantiza memoria total ni defensa volumétrica. | Fragmentación, handshake lento, límite de conexiones, EOF parcial y retorno exacto de cupos. |
| Secretos en bitácoras: alto. | Adaptar RNF-15 en todos los puntos de log, no solo el listener. | Enviar datos sintéticos sensibles y caracteres de control; revisar que no se copien a logs. |
| Regresión local o incompatibilidad de versión: alto. | Endpoints y formatos explícitos; sin fallback; conservar seis ejecutables y módulos heredados. | Suite local más mensajes v1 incompatibles, IDs completos/cortos y límites de argumentos de execute. |
| Latencia superior a RNF-05: medio/alto. | Medición reproducible antes de optimizar; no relajar locks/durabilidad para ocultar latencia. | Consulta de estado con 100 trabajos, carga documentada y tiempo de conexión identificado. |

## 6. Secuencia de implementación y puntos de revisión

1. Benjamin confirma alcance de un daemon, protocolo, política mTLS y confianza
   compartida, así como límites iniciales y configuración de cliente. Registrar
   decisiones en los ADRs y revisión del CR; no hay aprobación registrada todavía.
2. Denice implementa codec/validación/dispatcher con streams controlados, y después
   configuración y seguridad. Mantener la red desactivada por defecto.
3. Integrar listener/workers y cliente remoto usando el mismo núcleo; coordinar
   cierre y auditoría antes de habilitar acceso a una LAN/VPN autorizada.
4. Benjamin revisa invariantes y desviaciones; Denice aporta verificación técnica.
   Alexia diseña/ejecuta la certificación en entornos temporales, sin reutilizar
   datos ni sockets de usuarios. Fallos de seguridad/consistencia impiden habilitar red.
5. Jocelyn integra guías, limitaciones y control de entrega; la liberación requiere
   evidencia y revisiones del equipo. El cronograma sigue en su documento original.

La secuencia describe dependencias, no asigna nuevas fechas ni compromete plazos
de compañeras. No se crea infraestructura, se emiten certificados ni se abren
puertos con este documento.

## 7. Reversión y preservación de datos

Reversión operativa propuesta: deshabilitar el transporte remoto mediante su
configuración futura y reiniciar coordinadamente, conservando el IPC Unix y el
mismo directorio de datos. No existe hoy una bandera de red que pueda ejecutarse.
Cerrar listeners/conexiones propios y aplicar el apagado/recovery existentes;
un reinicio puede cancelar pendientes y activos, por lo que debe anunciarse y
planificarse. No prometer una reversión sin interrupción.

No borrar SQLite, journal, daemon.lock o un socket ajeno; no restaurar una copia
antigua sobre datos más recientes ni matar un PID por su número. No se necesita
migración de esquema en la propuesta: el historial y los UUID deben conservarse.
Si Backend cambia el esquema o la recuperación, detener este plan y añadir una
migración/reversión explícita revisada antes de desplegar. Volver a binarios de
otra versión exige verificar compatibilidad; no se indica git reset/revert como
solución operativa ni se revierten los IDs cortos.

## 8. Criterios de cierre, evidencia y responsables

El cierre técnico de este CR requiere: interfaces local/remota equivalentes;
framing/errores/versiones conformes; acceso LAN/VPN autorizado con autenticación;
un núcleo y reservas consistentes; desconexiones/cierre sin pérdida de commits;
regresión de CLI/persistencia/recuperación; medición RNF-05; documentación de
limitaciones y evidencia independiente de Alexia sobre una versión identificada.
Las decisiones que cambien seguridad, consistencia o recuperación deben conservar
su riesgo y escenario asociado; el PASS/FAIL formal pertenece a QA.

Las 46/105 pruebas de desarrollo anteriores y los 149 PASS que QA registró sobre
10c7a8e son antecedentes del alcance local, no pruebas del transporte propuesto.
Esta revisión solo verifica documentos, enlaces y diff. No certifica Avance 3
ni autoriza cerrar las issues por disponer de un diseño.

| Responsable / hito | Estado registrado |
| --- | --- |
| Benjamin: análisis y ADRs | Documentos redactados para revisión; decisión final de alcance/seguridad pendiente. |
| Denice: implementación e integración | Pendiente; este documento no acredita aceptación o implementación por ella. |
| Alexia: revisión y certificación | Pendiente para la versión de red; sus archivos permanecen intactos. |
| Jocelyn: control de entrega y gestión | Pendiente de integrar este aporte en sus entregables; sin cambios en ellos. |

Historial: versión 0.1, primera propuesta documental basada en la implementación
local y los diseños 3.2/3.4. No se han registrado aprobaciones, commits de red,
fecha de despliegue ni resultados remotos inexistentes. Las revisiones posteriores
deben indicar decisión, responsable, fecha y enlace a su evidencia real.
