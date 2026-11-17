# Modelo básico de amenazas: Jobsy en LAN/VPN

Estado: análisis de arquitectura propuesto para RNF-16 (#94), Avance 3.4.
Fecha: 16 de noviembre de 2026. No es una auditoría ejecutada, una certificación
ni el registro formal de riesgos de gestión. Complementa
[la política LAN/VPN](seguridad-lan-vpn.md) y [ADR-009](ADR-009-Seguridad-LAN-VPN.md).

## Activos y límites de confianza

Activos: capacidad de ejecutar comandos Linux, integridad/disponibilidad del
daemon, historial SQLite, stdout/stderr, claves TLS, configuración, bitácoras,
reservas del Scheduler y recursos del host.

Límites de confianza:

1. Red -> aceptación del socket: IP real, perfil y lista explícita.
2. Conexión permitida -> sesión autorizada: TLS mutuo y huella cliente.
3. Sesión autorizada -> operación: validar framing, versión, tipos y límites
   antes de consultar o mutar el gestor.
4. Gestor -> procesos/SQLite: coordinación y transacciones existentes. El proceso
   hijo comparte UID con el servicio: **no existe una frontera de aislamiento
   de privilegios entre el daemon y el comando ejecutado**.
5. Servicio -> auditoría/resultados: los logs de operación no deben copiar secretos
   de comandos o resultados; las salidas solo se entregan a operadores autorizados.

Se confía en el administrador del host, la CA emisora y los operadores enrolados.
Se considera hostil una conexión externa o de un equipo no enrolado, incluso
dentro de la misma LAN. Un cliente enrolado comprometido es un riesgo residual
crítico, porque conserva la capacidad legítima de ejecutar comandos.

## Amenazas y tratamiento propuesto

Los controles de red siguientes están pendientes de implementación. La tabla
es análisis de diseño; no representa PASS/FAIL ni reemplaza la matriz de Alexia.

| Amenaza | Impacto | Control propuesto y límite residual | Escenario para verificación independiente |
| --- | --- | --- | --- |
| Exposición por bind comodín, interfaz equivocada o reenvío del host | Ejecución remota fuera del entorno previsto. | TCP desactivado; bind explícito privado; denegar comodines; operador revisa host/VPN/firewall. Un NAT o proxy externo no se detecta únicamente por la IP local. | Arranque por defecto, IP pública, 0.0.0.0/:: y revisión de exposición del host. |
| Equipo no autorizado en la misma LAN/VPN | Consulta de datos, cancelación o ejecución ajena. | Lista CIDR más mTLS y huella. Pertenencia a red y conocimiento del ID no conceden acceso. | IP permitida sin certificado; certificado válido desde IP no permitida. |
| Suplantación de servidor o escucha de tráfico | Robo/modificación de comandos y resultados. | Cliente valida CA y SAN; TLS obligatorio también dentro de VPN. No protege un endpoint ya comprometido. | Certificado de otra identidad, caducado o desconocido y cliente sin TLS. |
| Evasión de reglas por IPv6, mapped, CIDR incorrecto o campo JSON falso | Acceso más amplio que el aprobado. | Normalización explícita, redes completas dentro del perfil, no DNS/proxy headers ni ampliación implícita. | Regla con bits de host, IPv4-mapped, /0, IP declarada distinta del peer real. |
| Mensajes incompletos, gigantes o malformados | Consumo de memoria/CPU, desincronización o servicio bloqueado. | Longitud/validación/plazos de 3.2 antes del despacho. Un límite de trama no acota toda la memoria del proceso ni la salida de trabajos. | Cabeceras fragmentadas, tamaño límite+1, profundidad excesiva y tráfico lento. |
| Saturación de conexiones y TLS | Agotamiento de workers/descriptores y rechazo a operadores. | Cupos global/por IP que incluyen handshakes, plazo absoluto y liberación en finally. No garantiza resistencia a ataques volumétricos; requiere red autorizada y controles del host. | Saturación seguida de desconexión: liberar cupos y conservar trabajos aceptados. |
| Respuesta perdida y reenvío de run/cancel | Ejecuciones duplicadas o incertidumbre del cliente. | No reintentar automáticamente; request_id solo correlaciona; conservar admisión durable y política terminal. No se promete exactamente una vez. | Cortar conexión después de commit; consultar historial antes de reenviar. |
| Robo de credencial de operador | Un atacante actúa como operador legítimo. | Certificados individuales, huella explícita, CA privada fuera del servicio y rotación/reinicio coordinado. La baja no es instantánea mientras la política antigua siga cargada. | Retirar una huella, cerrar sesiones antiguas y verificar rechazo tras reinicio autorizado. |
| Comando malicioso de operador autorizado | Lectura/modificación de SQLite, claves/logs accesibles y ejecución con permisos del servicio. | Cuenta dedicada sin root y datos mínimos. No existe sandbox ni segregación por usuario; permisos del mismo UID no contienen esta amenaza. | Revisar permisos/entorno en instancia desechable y documentar el alcance de confianza; no afirmar aislamiento inexistente. |
| Fuga o falsificación de bitácoras | Exposición de secretos o evidencia engañosa. | Metadatos acotados, caracteres de control escapados, no comandos/salidas/excepciones crudas; implementación de RNF-15 asignada a Backend. El logger actual aún imprime comandos. | Argumentos con secretos de prueba y saltos de línea; revisar que el evento no los replique. |
| Proceso que escapa del grupo o consume disco/salidas sin límite | Daño al usuario del servicio y recursos agotados. | Mantener reservas y cancelación existentes; entorno dedicado. No se promete controlar todos los descendientes, cuotas de disco o salida ilimitada. | Pruebas de recursos en entorno aislado por QA; nunca extender la garantía del límite de procesos principales. |
| Sustitución del socket local o acceso por permisos demasiado amplios | Suplantación o bypass del control remoto desde el host. | Directorio Unix privado, comparación del inode propio al limpiar y acceso local restringido. mTLS no protege un socket Unix expuesto a otro usuario. | Revisar permisos de la instancia de prueba; conservar sockets ajenos y comprobar ambos canales. |

## Supuestos que requieren aceptación del arquitecto

- Todos los operadores autorizados tienen los mismos derechos sobre todos los
  trabajos. Si se necesita confidencialidad entre usuarios, ownership y permisos
  por operación requieren ampliar protocolo/modelo antes de dar acceso remoto.
- La ejecución de comandos arbitrarios es la función del servicio. shell=False
  conserva límites de argumentos, pero no restringe qué programa puede ejecutar
  el operador ni evita que envíe explícitamente una shell.
- Un trabajo bajo el UID del daemon puede acceder a la clave privada del servidor
  si esa cuenta puede leerla. El esquema reduce amenazas externas, no resuelve
  compromiso por un operador o trabajo autorizado. No almacenar allí claves de
  CA ni credenciales personales; separar identidades/procesos es una alternativa
  futura si cambia el modelo de confianza.
- VPN, firewall y configuración de WSL/host son responsabilidades operativas
  externas. El hecho de usar RFC 1918, ULA o espacio compartido no prueba que
  el trayecto esté protegido ni que el origen sea una persona autorizada.
- La base y el socket pertenecen a una instancia; no compartir SQLite entre
  hosts/namespaces ni multiplicar daemons para eludir reservas o recuperación.

## Criterio de habilitación y transferencia

No habilitar acceso remoto basándose solo en este diseño. Antes de la
demostración se requiere implementación coherente de filtrado, TLS/autorización,
mínimo privilegio, límites y auditoría; validación por QA en LAN/VPN autorizada;
y revisión del operador sobre exposición y credenciales. No se instala ni
configura infraestructura de red como parte de esta documentación.

Benjamin mantiene las decisiones y límites arquitectónicos; Denice implementa
el servicio y la seguridad, incluyendo sus requisitos RNF-15 y RNF-26; Alexia
produce casos, pruebas y evidencia independiente. Los análisis e incidentes de
gestión permanecen en los documentos de Jocelyn, sin cambios en esta tarea.
