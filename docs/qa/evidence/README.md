# Evidencias de QA

Este directorio contiene las evidencias de ejecución de pruebas y aseguramiento de calidad de Jobsy, desde el MVP del Avance 1 hasta la validación de la operación remota del Avance 3 (PR #135).

Las evidencias permiten relacionar los resultados obtenidos con los casos de prueba, los requisitos evaluados y los incidentes identificados.

## Convención de nombres

Las evidencias utilizan el formato:

`EV-XXX-descripcion.ext`

- `EV`: prefijo de evidencia.
- `XXX`: identificador consecutivo de tres dígitos, mantenido de forma acumulativa.
- `descripcion`: nombre descriptivo de la prueba o artefacto.
- `ext`: extensión del archivo correspondiente.

Ejemplos de archivos utilizados en el proyecto:

- `EV-001-validation-output.txt`
- `EV-028-network-protocol-v1-output.txt`
- `EV-030-INC-002-reproduction.txt`

Un mismo identificador EV puede tener archivos complementarios cuando corresponden a la misma ejecución o bloque de validación. Estos archivos no representan casos de prueba adicionales.

## Organización por avance

| Directorio | Evidencias | Alcance |
|---|---|---|
| [avance-1/](avance-1/) | EV-001 a EV-009 | Validación, ejecución, cancelación, apagado, CLI e IPC local del MVP. |
| [avance-2/](avance-2/) | EV-010 a EV-025 | Socket UNIX configurable, ciclo de vida, recuperación, observabilidad, estrés, instalación y batería unificada de QA. |
| [avance-3/](avance-3/) | EV-026 a EV-035 | Identificadores cortos, protocolo v1, acceso remoto TCP, seguridad, concurrencia, rendimiento, LAN y regresión. |

## Índice de evidencias

### Avance 1

| ID | Alcance |
|---|---|
| EV-001 | Validación de entradas. |
| EV-002 | Ejecución de trabajos. |
| EV-003 | Gestión y consulta de trabajos. |
| EV-004 | Cancelación. |
| EV-005 | Apagado controlado del servicio. |
| EV-006 | Comportamiento de la CLI. |
| EV-007 | Flujo IPC. |
| EV-008 | Robustez IPC. |
| EV-009 | Múltiples trabajos mediante IPC. |

### Avance 2

| ID | Alcance |
|---|---|
| EV-010 | Configuración de socket UNIX. |
| EV-011 | Contrato de CLI y socket configurable. |
| EV-012 | Separación e integridad de stdout y stderr. |
| EV-013 | Cancelación de grupos de procesos. |
| EV-014 | Cancelación repetida. |
| EV-015 | Período de gracia de cancelación. |
| EV-016 | Aislamiento de fallos de cleanup. |
| EV-017 | Solicitudes duplicadas. |
| EV-018 | Resumen de salud. |
| EV-019 | Errores estructurados. |
| EV-020 | Bitácora y correlación mediante ReqID. |
| EV-021 | Robustez y observabilidad de cola. |
| EV-022 | Recuperación de trabajos. |
| EV-023 | Estrés y liberación de recursos. |
| EV-024 | Instalación limpia. |
| EV-025 | Batería unificada de QA. |

### Avance 3 — PR #133

| ID | Casos / alcance | Resultado histórico |
|---|---|---|
| EV-026 | TC-150 a TC-164 — Identificadores cortos | 15 PASS / 0 FAIL |
| EV-027 | Regresión de la batería vigente | 23 scripts PASS / 0 FAIL / 0 TIMEOUT |

### Avance 3 — PR #135

Versión evaluada: `32bd487`, rama de QA `alexia-test-pr135`.

| Evidencia | Casos / alcance | PASS | FAIL |
|---|---|---:|---:|
| [EV-028](avance-3/EV-028-network-protocol-v1-output.txt) | TC-165 a TC-180 — Protocolo v1 | 16 | 0 |
| [EV-029](avance-3/EV-029-remote-server-config-output.txt) | TC-181 a TC-195 — Configuración TCP | 15 | 0 |
| [EV-030](avance-3/EV-030-remote-cli-output.txt) | TC-196 a TC-214 — Cliente remoto | 18 | 1 |
| [EV-031](avance-3/EV-031-remote-security-output.txt) | TC-215 a TC-228 — Seguridad | 12 | 2 |
| [EV-032](avance-3/EV-032-remote-concurrency-output.txt) | TC-229 a TC-239 — Concurrencia | 11 | 0 |
| [EV-033](avance-3/EV-033-remote-performance-output.txt) | TC-240 a TC-246 — Rendimiento | 7 | 0 |
| [EV-034](avance-3/EV-034-remote-lan-output.txt) | TC-247 a TC-260 — Comunicación LAN | 14 | 0 |
| **Total de casos nuevos** | **96** | **93** | **3** |

#### Evidencias complementarias

| Archivo | Propósito |
|---|---|
| [EV-030-INC-002-reproduction.txt](avance-3/EV-030-INC-002-reproduction.txt) | Reproducción complementaria del manejo incorrecto de JOBSY_PORT. |
| [EV-034-remote-lan-daemon.txt](avance-3/EV-034-remote-lan-daemon.txt) | Respaldo de la bitácora del daemon durante las pruebas LAN. |
| [EV-035-regression-output.txt](avance-3/EV-035-regression-output.txt) | Regresión general de la batería unificada, posterior a las pruebas del PR #135. |

EV-034 contiene un registro consolidado de las comprobaciones manuales realizadas entre dos equipos físicos; la bitácora complementaria conserva los eventos del daemon. EV-035 registra 29 scripts ejecutados: 27 PASS, 2 FAIL, 0 TIMEOUT, duración de 70.76 segundos y código de salida 1. Los 23 scripts históricos incluidos finalizaron correctamente. Los fallos de los dos scripts nuevos corresponden a TC-213, TC-219 y TC-228.

La regresión se contabiliza por separado y no incrementa el número de casos únicos. El historial acumulado contiene 260 casos con 257 resultados originales PASS y 3 FAIL; esto no implica que los 164 casos históricos se hayan reejecutado individualmente en el PR #135. En EV-035, TC-147 obtuvo PASS y las comprobaciones agregadas TC-148 y TC-149 obtuvieron FAIL.

## Trazabilidad e incidentes

Las evidencias deben relacionarse con los casos correspondientes mediante la [matriz de trazabilidad](../traceability-matrix.md) y el [documento de casos de prueba](../test-cases.md).

| Incidente | Caso | Evidencias | Estado |
|---|---|---|---|
| [INC-001](../incidents/INC-001-request-id-correlation.md) | TC-119 | EV-020 | Resuelto y revalidado |
| [INC-002](../incidents/INC-002-invalid-jobsy-port.md) | TC-213 | EV-030, EV-035 y reproducción complementaria | Abierto |
| [INC-003](../incidents/INC-003-bearer-token-sanitization.md) | TC-219 | EV-031, EV-035 | Abierto |
| [INC-004](../incidents/INC-004-sensitive-internal-error-logging.md) | TC-228 | EV-031, EV-035 | Abierto |

Consultar también las [observaciones del PR #135](../observations-pr135.md) y la [documentación general de QA](../README.md).

## Conservación de evidencias

- Conservar las salidas originales, incluidos los resultados FAIL y los códigos de salida disponibles.
- Registrar la versión evaluada, entorno, comando ejecutado y fecha cuando estén disponibles.
- Identificar claramente las evidencias manuales, los respaldos de bitácora y las reconstrucciones de resultados.
- Utilizar datos ficticios en pruebas de seguridad; no incorporar credenciales reales ni información sensible al repositorio.
- Registrar las revalidaciones posteriores por separado, sin sobrescribir las evidencias iniciales de los incidentes.
- Mantener la numeración acumulativa y actualizar la matriz de trazabilidad cuando se incorporen nuevas evidencias.

## Estado actual

La batería planificada del PR #135 fue ejecutada completamente. Los tres incidentes confirmados permanecen abiertos y requieren corrección y revalidación antes de recomendar la aprobación del PR. Las evidencias de ejecuciones anteriores conservan su resultado histórico.
