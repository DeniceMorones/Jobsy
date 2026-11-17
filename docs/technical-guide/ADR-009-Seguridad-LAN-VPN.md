# ADR-009: Seguridad y acceso restringido LAN/VPN

Estado: propuesto; pendiente de aprobación de Benjamin, implementación y QA.
Fecha: 16 de noviembre de 2026.
Alcance: RF-20 (#90), RNF-12 (#91), RNF-13 (#92), RNF-16 (#94).
Documentos: [política LAN/VPN](seguridad-lan-vpn.md),
[modelo de amenazas](modelo-amenazas-lan-vpn.md), [protocolo v1](protocolo-red-v1.md).

## Contexto

Jobsy ejecuta comandos con la identidad del daemon. Trasladar esa capacidad
desde un socket Unix a una red amplía quién puede alcanzar el servicio. Una IP
privada o una VPN no identifican por sí solas a un operador; UUID y request_id
tampoco son credenciales. El código actual no implementa transporte remoto,
autenticación TLS ni autorización por propietario de trabajos.

## Decisión propuesta

1. Mantener red desactivada por defecto. Al habilitarla, usar loopback como
   dirección predeterminada y exigir puerto no privilegiado explícito. Rechazar
   bind comodín o público. LAN/VPN requieren configuración deliberada.
2. Aplicar una lista de IP/CIDR explícitos sobre el origen real de la conexión,
   denegando lo no permitido. Validar redes completas, normalizar mapped y no
   interpretar is_private como autorización. Los perfiles y la excepción de
   VPN sobre espacio compartido están delimitados en la política.
3. Exigir TLS mutuo y una lista de huellas de certificados cliente autorizados,
   también para TCP loopback o VPN. El cliente valida identidad/CA del servidor.
   Un error nunca habilita texto claro, otro endpoint o acceso anónimo.
4. Autorizar operadores de confianza con acceso compartido a las seis operaciones
   y a todo el historial de su instancia. No introducir permisos ficticios por
   Job ID ni afirmar aislamiento entre operadores.
5. Ejecutar con cuenta dedicada sin root, capacidades elevadas ni secretos del
   desarrollador. Reducir permisos y superficie accesible; conservar el límite
   explícito de que hijo y daemon comparten UID y no están aislados.
6. Separar cupos de conexiones y handshakes de las reservas del Scheduler.
   Aplicar plazos/tamaños de 3.2 y cerrar conexiones sin cancelar trabajos ya
   admitidos. No realizar TLS ni socket I/O bajo locks del gestor.

Los campos/valores propuestos se definen una sola vez en seguridad-lan-vpn.md.
No son opciones instaladas ni garantizan capacidad de carga. Se conserva IPC
Unix y su protección por permisos; no se cambia el comportamiento local actual.

## Alternativas evaluadas

- Solo filtrar IP: menor costo operativo, pero cualquier equipo permitido o
  comprometido podría actuar sin identidad; no protege el contenido en tránsito.
- VPN como única autenticación: delega confianza a toda la VPN y no cubre LAN
  directa ni identifica necesariamente operadores de Jobsy.
- TLS de servidor más token: viable, pero requiere diseñar distribución,
  almacenamiento y rotación de secretos adicionales en el protocolo. Se prefiere
  autenticación de cliente en TLS y un único mecanismo de enrolamiento.
- mTLS más huellas: permite identidad individual y admisión explícita con la
  biblioteca estándar, a costa de administrar CA, certificados y renovaciones.
- Separar el frontend TLS y el ejecutor en identidades distintas, o usar sandbox:
  mejor contención frente a operadores hostiles, pero modifica el despliegue y
  el modelo de ejecución. Se reserva para una ampliación explícita del alcance.

## Consecuencias y riesgos aceptables solo tras revisión

Se deben emitir/administrar certificados y mantener el entorno ssl/OpenSSL;
no se agrega un servidor externo de base de datos ni una dependencia pip.
Retirar un certificado exige actualizar su huella y reiniciar coordinadamente;
no se promete revocación en caliente o comprobación automática OCSP/CRL.

Los operadores autorizados conservan capacidad de ejecutar código arbitrario
bajo el UID del servicio, incluyendo acceso a sus archivos y potencialmente su
clave TLS. La cuenta dedicada limita el impacto sobre otros usuarios, pero no
es un aislamiento frente al propio operador. Ese modelo de confianza requiere
aprobación antes de habilitar acceso remoto.

La política de auditoría debe integrarse con RNF-15 de Backend. Los límites
de conexiones no garantizan resistencia a ataques volumétricos, cuotas de disco
ni memoria de resultados acotada. La exposición real del host/VPN requiere
revisión operativa aparte, especialmente en WSL.

## Verificación y coordinación

Los escenarios negativos y de integración se transfieren en la política y el
modelo de amenazas. No se han ejecutado pruebas funcionales de seguridad ni
se han modificado los documentos formales de QA. Backend implementa la propuesta
aprobada; Alexia verifica las cuatro condiciones de alcance y genera evidencia.
El [CR-001](CR-001-Migracion-Arquitectura-Red.md) del bloque 3.6 registra
impacto, riesgos, reversión y aprobaciones pendientes para #125.
[ADR-010](ADR-010-Concurrencia-Clientes-Remotos.md) especifica concurrencia
de conexiones y cierre sin alterar reservas. Estos documentos completan
la propuesta para revisión; no registran aprobación, implementación o QA.
