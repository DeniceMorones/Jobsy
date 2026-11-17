# ADR-008: Protocolo de red versionado

Estado: propuesto; pendiente de revisión arquitectónica e implementación.
Fecha: 16 de noviembre de 2026.
Requisitos: RF-21 (#86), RNF-14 (#19), RNF-24 (#87), RNF-32 (#88).
Especificación: [contrato v1](protocolo-red-v1.md).

## Contexto

SOCK_STREAM transporta bytes, no mensajes. El servidor local actual hace una
única lectura de 4096 bytes y el cliente acumula hasta interpretar un JSON.
No hay delimitación, versión ni soporte para varias solicitudes por conexión.
El siguiente avance necesita un contrato común antes de implementar la red.

## Decisión propuesta

Usar JSON UTF-8 precedido por una longitud de cuatro bytes sin signo big-endian.
Acotar a 1 MiB el cuerpo de cada solicitud y respuesta, validar antes del despacho
y procesar secuencialmente varios mensajes por conexión. Establecer plazos
absolutos de recepción/envío y profundidad JSON máxima según el contrato.

Incluir version=1 y request_id en el sobre. Rechazar versiones incompatibles,
conservar las seis operaciones y definir códigos de error estables junto a los
campos operation, cause y suggestion. request_id solo correlaciona; reenviar
run sigue siendo una nueva orden. No se introduce ejecución exactamente una vez.

La capa de red reutilizará un único gestor y su Scheduler por instancia.
La concurrencia entre clientes no equivale a ejecución distribuida entre nodos.
Los UUID durables se conservan; la CLI puede presentar prefijos y el gestor
debe rechazar ambigüedades. La autorización no se deduce del conocimiento del ID.

Se conserva el IPC Unix sin cabecera en su propio endpoint. No se detectan ni
mezclan formatos en una conexión y no se añade degradación automática. El
contrato propuesto sustituye la decisión pendiente de red de ADR-003 solo cuando
sea aprobado e implementado; no modifica hoy el transporte local.

## Alternativas

- JSON separado por saltos de línea: viable con reglas de serialización, pero
  requiere buscar delimitadores y acotar igualmente los buffers.
- JSON sin cabecera hasta EOF: conserva el esquema local pero impide múltiples
  solicitudes por conexión y no resuelve una longitud explícita.
- HTTP con un framework: ofrece convenciones conocidas, pero añade otra interfaz
  y posiblemente dependencias para un alcance centrado en sockets.

La longitud explícita permite rechazar el tamaño antes de recibir el cuerpo y
separa el framing de la lógica de trabajos usando la biblioteca estándar.

## Consecuencias y pendientes

Backend debe implementar bucles de recepción/envío parcial, validadores y
despacho; QA debe certificar fragmentación, errores y compatibilidad. Las
respuestas que superen 1 MiB se rechazan sin truncarlas; paginación/transferencia
de salidas grandes requiere una extensión acordada. No hay promesa de memoria
acotada de toda la captura del proceso por el límite de una trama.

Quedan para Avance 3.4 la interfaz de escucha, puerto, límite de conexiones,
lista de redes autorizadas, autenticación, protección del canal y amenazas.
Ninguna decisión de este ADR habilita exposición pública. No se cambia la
persistencia, recuperación, cancelación ni el límite de procesos de Avance 2.

Los escenarios de conformidad están en el contrato; son requisitos para pruebas
futuras, no resultados ejecutados ni certificación de QA.
