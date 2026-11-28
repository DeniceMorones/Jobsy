# Quality Assurance

Este directorio contiene la documentación relacionada con las actividades de
pruebas y aseguramiento de calidad de Jobsy, desde el MVP del primer avance
hasta la evaluación del acceso remoto del Avance 3.

## Objetivo

Documentar la estrategia de pruebas, los casos de prueba, la trazabilidad
entre requisitos y pruebas, los incidentes técnicos, las observaciones y las
evidencias generadas durante la verificación de Jobsy.

## Documentos

- [test-plan.md](test-plan.md): alcance y estrategia general de pruebas.
- [test-cases.md](test-cases.md): definición y resultados acumulados de los casos de prueba.
- [traceability-matrix.md](traceability-matrix.md): relación entre requisitos, pruebas y evidencias.
- [technical-review-2.md](technical-review-2.md): consolidación de la versión demostrada y las pruebas de la Technical Review 2.
- [observations-pr135.md](observations-pr135.md): observaciones técnicas del PR #135 (OBS-01 a OBS-10).
- [qa-report-pr135.md](qa-report-pr135.md): reporte consolidado del PR #135, resultados, incidentes y criterios de revalidación.
- [incidents/](incidents/): documentación de incidentes técnicos y su revalidación.
- [evidence/](evidence/): resultados y evidencias de las ejecuciones de QA.

## Alcance de las pruebas

La cobertura incluye las funcionalidades locales del MVP, la comunicación IPC
mediante sockets UNIX, el ciclo de vida de los trabajos, cancelación, colas,
recuperación, bitácoras, errores estructurados, instalación, estrés de recursos
e identificadores cortos. El Avance 3 incorpora la comunicación remota TCP
mediante el protocolo v1, configuración de host y puerto, control de acceso por
IP, cliente remoto, seguridad de bitácoras, concurrencia, rendimiento y pruebas
entre dos equipos en una red LAN privada.

Las validaciones acumuladas corresponden a los PR #101, #102, #104, #110,
#114, #116, #133 y #135.

## Evidencias

| Directorio | Evidencias | Alcance |
|---|---|---|
| [avance-1](evidence/avance-1/) | EV-001 a EV-009 | MVP y comunicación IPC inicial |
| [avance-2](evidence/avance-2/) | EV-010 a EV-025 | Socket configurable, ciclo de vida, robustez y Technical Review 2 |
| [avance-3](evidence/avance-3/) | EV-026 a EV-035 | IDs cortos, operación remota y regresión |

### Avance 3 — PR #135

| Evidencia | Casos | PASS | FAIL |
|---|---|---:|---:|
| [EV-028](evidence/avance-3/EV-028-network-protocol-v1-output.txt) | TC-165 a TC-180 — Protocolo v1 | 16 | 0 |
| [EV-029](evidence/avance-3/EV-029-remote-server-config-output.txt) | TC-181 a TC-195 — Configuración TCP | 15 | 0 |
| [EV-030](evidence/avance-3/EV-030-remote-cli-output.txt) | TC-196 a TC-214 — Cliente remoto | 18 | 1 |
| [EV-031](evidence/avance-3/EV-031-remote-security-output.txt) | TC-215 a TC-228 — Seguridad | 12 | 2 |
| [EV-032](evidence/avance-3/EV-032-remote-concurrency-output.txt) | TC-229 a TC-239 — Concurrencia | 11 | 0 |
| [EV-033](evidence/avance-3/EV-033-remote-performance-output.txt) | TC-240 a TC-246 — Rendimiento | 7 | 0 |
| [EV-034](evidence/avance-3/EV-034-remote-lan-output.txt) | TC-247 a TC-260 — LAN | 14 | 0 |
| **Total** | **96 casos nuevos** | **93** | **3** |

Evidencias complementarias: [reproducción de INC-002](evidence/avance-3/EV-030-INC-002-reproduction.txt),
[bitácora LAN](evidence/avance-3/EV-034-remote-lan-daemon.txt) y
[EV-035 — regresión general](evidence/avance-3/EV-035-regression-output.txt).

## Ejecución de pruebas

Desde la raíz del repositorio, con Jobsy instalado y el entorno virtual de
Python activo, ejecutar:

```bash
python test/run_qa_suite.py
```

El runner descubre los scripts `test/test_*.py`, respeta las exclusiones
históricas y devuelve un código distinto de cero si algún script falla o
excede su timeout. Las pruebas LAN manuales se documentan por separado.

La batería vigente para el PR #135 incluye 29 scripts. Se mantienen las
exclusiones explícitas del runner, incluido `test_process_behavior.py`.

## Incidentes técnicos

| Incidente | Caso | Estado |
|---|---|---|
| [INC-001](incidents/INC-001-request-id-correlation.md) — Correlación de ReqID | TC-119 | Resuelto y revalidado |
| [INC-002](incidents/INC-002-invalid-jobsy-port.md) — JOBSY_PORT inválido | TC-213 | Abierto |
| [INC-003](incidents/INC-003-bearer-token-sanitization.md) — Sanitización Bearer | TC-219 | Abierto |
| [INC-004](incidents/INC-004-sensitive-internal-error-logging.md) — Datos sensibles en excepciones | TC-228 | Abierto |

Las observaciones OBS-01 a OBS-10 se documentan por separado. OBS-05 y OBS-07
corresponden a incidentes ya contabilizados; no representan defectos adicionales.

## Estado actual

Última evaluación: **28 de noviembre de 2026**, PR #135, commit `32bd487`,
rama de QA `alexia-test-pr135`.

| Indicador | Resultado |
|---|---:|
| Casos históricos (TC-001 a TC-164) | 164 PASS en sus ejecuciones históricas |
| Casos nuevos (TC-165 a TC-260) | 96 |
| PASS nuevos | 93 |
| FAIL nuevos | 3 |
| Casos únicos acumulados | 260 |
| Resultados originales acumulados | 257 PASS / 3 FAIL |
| Regresión EV-035 | 27 PASS / 2 FAIL / 0 TIMEOUT (29 scripts) |
| Scripts históricos en EV-035 | 23 PASS / 0 FAIL |
| Duración EV-035 | 70.76 s |
| Incidentes abiertos del PR #135 | 3 |

Los resultados históricos se conservan y no implican que los 164 casos hayan
sido reejecutados individualmente. EV-035 se contabiliza por separado, sin
incrementar el número de casos únicos. Los fallos de la regresión corresponden
a TC-213, TC-219 y TC-228; no se detectaron fallos adicionales en la batería
vigente.

**Dictamen de QA del PR #135: NO APROBADO — requiere correcciones y revalidación.**

La comunicación LAN y el rendimiento resultaron satisfactorios bajo las
condiciones evaluadas. RNF-05 se verificó mediante loopback con 100 trabajos
registrados y finalizados, no con 100 trabajos activos ni en LAN. Las pruebas
de sanitización utilizaron datos ficticios y no demuestran exposición de
credenciales reales. El acceso TCP se evaluó en una red privada controlada;
no se considera validado para exposición a redes no confiables.
