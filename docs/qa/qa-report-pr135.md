# Reporte consolidado de QA — PR #135

## 1. Identificación y dictamen

| Campo | Valor |
|---|---|
| Proyecto | Jobsy — Avance 3 |
| PR | [#135](https://github.com/DeniceMorones/Jobsy/pull/135) |
| Rama QA | `alexia-test-pr135` |
| Commit del producto evaluado | `32bd487` |
| Fecha de cierre de ejecución | 28 de noviembre de 2026 |
| Dictamen | **NO APROBADO — requiere correcciones y revalidación** |

Se completaron los ocho bloques planificados. La comunicación remota TCP, la coexistencia con UNIX, la concurrencia y la operación LAN resultaron satisfactorias en los escenarios probados. Se confirmaron tres incidentes abiertos, reproducidos en la regresión. No se modificó el código del producto. Las severidades y prioridades son propuestas de QA.

## 2. Alcance y entorno

Se evaluó el protocolo v1 (framing de cuatro bytes big endian, JSON, límites y timeouts), configuración y control de acceso TCP, comandos remotos, protección de bitácoras, concurrencia, rendimiento, comunicación LAN y regresión de la batería vigente.

- PC A: Windows 11, Ubuntu WSL2, kernel `6.18.33.2-microsoft-standard-WSL2`, Python 3.14.4, entorno `.venv`, red mirrored. Daemon LAN en `192.168.100.64:8765`.
- PC B: Mac Apple Silicon, Ubuntu Server en UTM ARM64, hostname `jobsy-client`, IP `192.168.100.151`, rama `qa-remote-client`, commit `32bd487`, Jobsy 0.1.0 instalado en entorno virtual.
- LAN privada con allowlist inicial `192.168.100.151/32`; se probó también rechazo con `127.0.0.1/32` y posterior restauración.
- Los scripts automatizados se ejecutaron en PC A; las pruebas LAN se realizaron manualmente entre ambos equipos.

## 3. Resultados de los casos nuevos

| Evidencia | Casos | Script / modalidad | PASS | FAIL |
|---|---|---|---:|---:|
| [EV-028](evidence/avance-3/EV-028-network-protocol-v1-output.txt) | TC-165 a TC-180 | `test/test_network_protocol_v1.py` | 16 | 0 |
| [EV-029](evidence/avance-3/EV-029-remote-server-config-output.txt) | TC-181 a TC-195 | `test/test_remote_server_config.py` | 15 | 0 |
| [EV-030](evidence/avance-3/EV-030-remote-cli-output.txt) | TC-196 a TC-214 | `test/test_remote_cli.py` | 18 | 1 |
| [EV-031](evidence/avance-3/EV-031-remote-security-output.txt) | TC-215 a TC-228 | `test/test_remote_security.py` | 12 | 2 |
| [EV-032](evidence/avance-3/EV-032-remote-concurrency-output.txt) | TC-229 a TC-239 | `test/test_remote_concurrency.py` | 11 | 0 |
| [EV-033](evidence/avance-3/EV-033-remote-performance-output.txt) | TC-240 a TC-246 | `test/test_remote_performance.py` | 7 | 0 |
| [EV-034](evidence/avance-3/EV-034-remote-lan-output.txt) | TC-247 a TC-260 | Manual LAN | 14 | 0 |
| **Total** | **96** | | **93** | **3** |

Tasa de aprobación de casos nuevos: 96.875 %. Los 164 casos históricos conservan sus resultados originales PASS. El acumulado de resultados originales es de 260 casos únicos (257 PASS y 3 FAIL), no una reejecución individual de los 260 en este commit. EV-035 se contabiliza por separado.

## 4. Incidentes abiertos

| Incidente | Caso | Resultado observado | Severidad / prioridad propuestas |
|---|---|---|---|
| [INC-002](incidents/INC-002-invalid-jobsy-port.md) | TC-213 | `JOBSY_PORT=abc` provoca `ValueError` y traceback durante `build_parser()` | Media / Alta |
| [INC-003](incidents/INC-003-bearer-token-sanitization.md) | TC-219 | `Authorization=[REDACTADO] QA_FAKE_219` conserva el token ficticio | Media / Alta |
| [INC-004](incidents/INC-004-sensitive-internal-error-logging.md) | TC-228 | Una excepción simulada deja `QA_FAKE_INTERNAL_5828` en la bitácora | Media / Alta |

INC-002: la conversión anticipada del valor ambiental también afecta ayuda, modo local y precedencia de un puerto explícito válido. Véase [reproducción complementaria](evidence/avance-3/EV-030-INC-002-reproduction.txt).

INC-003 e INC-004 se relacionan con RNF-15. Se utilizaron marcadores ficticios; no se demostró exposición de credenciales reales ni una filtración en el flujo normal para INC-003. TC-227 confirmó que la respuesta al cliente oculta el detalle interno, aunque TC-228 confirmó su presencia en el log simulado. INC-001 pertenece a un PR anterior y permanece resuelto y revalidado.

## 5. Observaciones técnicas

Detalle y criterios de aceptación en [observations-pr135.md](observations-pr135.md).

| ID | Hallazgo | Clasificación |
|---|---|---|
| OBS-01 | Archivo ajeno al proyecto incluido en el PR | Confirmado por revisión estática |
| OBS-02 | Verificadores del desarrollador no propagan fallos mediante exit code | Confirmado por revisión estática |
| OBS-03 | Verificador de rendimiento puede declarar cumplimiento sin validar toda la carga y respuestas | Confirmado por revisión estática; no inducido en ejecución |
| OBS-04 | TCP sin cifrado ni autenticación de cliente | Limitación de diseño |
| OBS-05 | JOBSY_PORT inválido genera traceback | INC-002 |
| OBS-06 | Respuesta incompleta de servidor simulado produce `Error: 'jobs'` | Mejora de diagnóstico; TC-239 PASS |
| OBS-07 | Excepción interna registra dato sensible ficticio | INC-004 |
| OBS-08 | Posible carrera durante apagado TCP | Riesgo no reproducido |
| OBS-09 | Bitácora registra finalización fallida para trabajo CANCELED | Inconsistencia de observabilidad reproducida |
| OBS-10 | Mensaje final de apagado duplicado | Observabilidad; reproducida |

OBS-05 y OBS-07 no son defectos adicionales a los incidentes. OBS-09 y OBS-10 se observaron en LAN y loopback; no se determinó si fueron introducidas por este PR. El archivo accidental local `tatus --short` ya fue eliminado y no corresponde a OBS-01.

## 6. Rendimiento y operación LAN

### RNF-05 — EV-033

100 trabajos registrados, todos finalizados en SUCCEEDED, con identificadores únicos. Se validaron 90 consultas status, 30 list y 30 health mediante loopback.

| Operación | Consultas | Mínimo (ms) | Mediana (ms) | Máximo (ms) |
|---|---:|---:|---:|---:|
| status | 90 | 0.078 | 0.101 | 0.711 |
| list | 30 | 0.516 | 0.551 | 0.713 |
| health | 30 | 0.073 | 0.123 | 0.299 |

Resultado PASS frente al umbral de 1000 ms en las condiciones ensayadas. No equivale a una carga de 100 trabajos simultáneamente activos ni a una medición LAN con 100 trabajos.

### EV-034 — LAN real

14 PASS de 14 casos: conectividad TCP, health, ejecución de hostname en PC A desde PC B, IDs cortos/completos, estado, stdout/stderr, cancelación, estado compartido UNIX/TCP, registro de IP real, rechazo por allowlist, variables de entorno, latencia, reconexión y apagado.

TC-258: 30 consultas status válidas sobre una conexión persistente y cuatro trabajos registrados; mínimo 1.847 ms, mediana 2.493 ms, máximo 3.425 ms. No incluye establecimiento TCP ni arranque de CLI. TC-259 probó cierre controlado de conexión, no caída física de red. TC-260 confirmó cierre con código 0, eliminación del socket UNIX y ausencia de listener TCP.

La evidencia manual es un resumen consolidado del operador, no una transcripción íntegra. Se conserva la [bitácora LAN](evidence/avance-3/EV-034-remote-lan-daemon.txt). La eliminación de reglas temporales de firewall se solicitó y ejecutó; falta confirmar de forma inequívoca la consulta final de la regla Hyper-V.

## 7. Regresión general — EV-035

Comando: `python test/run_qa_suite.py`. [Evidencia](evidence/avance-3/EV-035-regression-output.txt).

| Indicador | Resultado |
|---|---:|
| Scripts ejecutados | 29 |
| PASS | 27 |
| FAIL | 2 |
| TIMEOUT | 0 |
| Duración | 70.76 s |
| Exit code | 1 |
| Scripts históricos | 23 PASS / 0 FAIL |
| Scripts nuevos | 4 PASS / 2 FAIL |

Los fallos se limitaron a `test_remote_cli.py` (18 PASS, 1 FAIL: TC-213) y `test_remote_security.py` (12 PASS, 2 FAIL: TC-219 y TC-228). TC-147 pasó; TC-148 y TC-149 fallaron en esta reejecución debido al resultado agregado, sin constituir incidentes independientes. El runner funcionó correctamente al detectar y propagar los fallos. No se detectaron daemons residuales mediante `pgrep -af jobsy-daemon` tras la ejecución.

Se mantuvieron las exclusiones explícitas: `test_cancellation.py`, `test_cli_behavior.py`, `test_ipc_robustness.py`, `test_process_behavior.py`, `test_queue_ipc.py` y `test_service_shutdown.py`. El runner no muestra el detalle individual de los scripts PASS; la conclusión histórica se limita a los scripts ejecutados, no a todos los casos históricos ni a todas las condiciones posibles.

## 8. Acciones requeridas y criterios de revalidación

1. INC-002: validar el puerto ambiental con error controlado cuando corresponda; comprobar modo local, ayuda, puerto explícito válido y precedencia. Reejecutar EV-030 y la reproducción complementaria.
2. INC-003: ocultar íntegramente el marcador Bearer; comprobar también formatos de secretos ya aprobados por TC-217 y TC-218.
3. INC-004: evitar datos sensibles de excepciones en logs conservando diagnóstico seguro; verificar TC-227 y TC-228 y el resto de EV-031.
4. Revisar OBS-01 a OBS-10 según su clasificación y prioridad; decidir el tratamiento de la limitación de seguridad TCP y del riesgo de cierre concurrente sin atribuirles un FAIL no demostrado.
5. Registrar commit de corrección y ejecutar nuevamente los bloques afectados y el runner vigente; objetivo: cero fallos y cero timeouts. Repetir LAN si los cambios afectan transporte, control de acceso o cierre. Conservar EV-028 a EV-035 y asignar identificadores nuevos a la evidencia de revalidación.

No se han aplicado fixes ni se ha realizado revalidación posterior a correcciones. El acceso TCP no se considera apto para redes no confiables por el mero hecho de superar las pruebas de allowlist.

## 9. Entregables y conclusión

- [Casos de prueba](test-cases.md) y [matriz de trazabilidad](traceability-matrix.md).
- [Índice de QA](README.md), [índice de evidencias](evidence/README.md) e [incidentes](incidents/).
- [Observaciones](observations-pr135.md), seis scripts nuevos y evidencias EV-028 a EV-035 con sus archivos complementarios.

**QA recomienda no aprobar el PR #135 en el commit evaluado hasta corregir y revalidar INC-002, INC-003 e INC-004.** La ejecución planificada ha concluido; la aprobación del producto y el cierre de los incidentes quedan pendientes. La incorporación definitiva y publicación de los entregables se verifican por separado en el repositorio de QA.
