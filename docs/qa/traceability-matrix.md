# Matriz de trazabilidad — Jobsy

Esta matriz relaciona las funcionalidades requeridas del MVP, los requisitos formales y los entregables de QA con sus casos de prueba, scripts, artefactos y evidencias.

La matriz se mantiene de forma acumulativa e incluye las validaciones ejecutadas por QA sobre los PR #101, #102, #104, #110, #114, #116 y #133 y #135.

| ID | Requisito / funcionalidad | Caso(s) de prueba | Automatización / artefacto | Evidencia | Estado | Requisito formal / Issue |
|---|---|---|---|---|---|---|
| MVP-01 | Enviar un trabajo | TC-030, TC-038, TC-050 | `test/test_cli_behavior.py`, `test/test_ipc_flow.py`, `test/test_ipc_multiple_jobs.py` | EV-006, EV-007, EV-009 | PASS | RF-01 / #30 |
| MVP-02 | Obtener identificador único | TC-006, TC-030, TC-038, TC-051, TC-096, TC-097 | `test/test_executor.py`, `test/test_cli_behavior.py`, `test/test_ipc_flow.py`, `test/test_ipc_multiple_jobs.py`, `test/test_duplicate_requests.py` | EV-002, EV-006, EV-007, EV-009, EV-017 | PASS | RF-01 / #30; RF-27 |
| MVP-03 | Ejecutar trabajos sin bloquear nuevas solicitudes | TC-007, TC-019, TC-050, TC-052, TC-076 a TC-079 | `test/test_executor.py`, `test/test_cancellation.py`, `test/test_ipc_multiple_jobs.py`, `test/test_process_group_cancellation.py` | EV-002, EV-004, EV-009, EV-013 | PASS | RF-04 / #32; RNF-30 / #29 |
| MVP-04 | Consultar estado y metadatos por ID | TC-015, TC-016, TC-032, TC-034, TC-039, TC-042, TC-092, TC-109 | `test/test_job_manager.py`, `test/test_cli_behavior.py`, `test/test_ipc_flow.py`, `test/test_duplicate_requests.py`, `test/test_structured_errors.py` | EV-003, EV-006, EV-007, EV-017, EV-019 | PASS | RF-08 / #35; RF-27; RNF-21 / RF-28 |
| MVP-05 | Listar trabajos y filtrar por estado | TC-017, TC-031, TC-035, TC-040, TC-045, TC-052, TC-091 | `test/test_job_manager.py`, `test/test_cli_behavior.py`, `test/test_ipc_flow.py`, `test/test_ipc_robustness.py`, `test/test_ipc_multiple_jobs.py`, `test/test_duplicate_requests.py` | EV-003, EV-006, EV-007, EV-008, EV-009, EV-017 | PASS | RF-09 / #36; RF-27 |
| MVP-06 | Solicitar cancelación | TC-018 a TC-022, TC-033, TC-041, TC-044, TC-078, TC-080, TC-081, TC-087, TC-094, TC-095, TC-110 | `test/test_cancellation.py`, `test/test_cli_behavior.py`, `test/test_ipc_flow.py`, `test/test_ipc_robustness.py`, `test/test_process_group_cancellation.py`, `test/test_repeated_cancellation.py`, `test/test_cancel_grace.py`, `test/test_duplicate_requests.py`, `test/test_structured_errors.py` | EV-004, EV-006, EV-007, EV-008, EV-013, EV-014, EV-015, EV-017, EV-019 | PASS | RF-10 / #37; RF-26; RF-30; RF-27; RNF-21 / RF-28 |
| MVP-07 | Registrar código de salida y tiempos | TC-010, TC-013, TC-014, TC-039, TC-052 | `test/test_executor.py`, `test/test_ipc_flow.py`, `test/test_ipc_multiple_jobs.py` | EV-002, EV-007, EV-009 | PASS | RF-07 / #34 |
| MVP-08 | Validar entradas incorrectas de forma controlada | TC-001 a TC-005, TC-034 a TC-036, TC-042 a TC-047, TC-107 a TC-113 | `test/test_validation.py`, `test/test_cli_behavior.py`, `test/test_ipc_flow.py`, `test/test_ipc_robustness.py`, `test/test_structured_errors.py` | EV-001, EV-006, EV-007, EV-008, EV-019 | PASS | RF-02 / #31; RF-17 / #39; RNF-21; RF-28 |
| MVP-09 | Representar estados mínimos del trabajo | TC-007, TC-008, TC-011, TC-018, TC-019, TC-039, TC-041, TC-045, TC-052 | `test/test_executor.py`, `test/test_cancellation.py`, `test/test_ipc_flow.py`, `test/test_ipc_robustness.py`, `test/test_ipc_multiple_jobs.py` | EV-002, EV-004, EV-007, EV-008, EV-009 | PASS | RF-06 / #33 |
| MVP-10 | Inicio y apagado controlado del servicio | TC-023 a TC-028, TC-037, TC-049 | `test/test_service_shutdown.py`, `test/test_ipc_flow.py`, `test/test_ipc_robustness.py` | EV-005, EV-007, EV-008 | PASS | RF-15 / #38 |
| MVP-11 | Ayuda y códigos de salida del cliente | TC-029 a TC-036, TC-038, TC-042 a TC-044, TC-064 a TC-066, TC-075, TC-081, TC-084 a TC-087 | `test/test_cli_behavior.py`, `test/test_ipc_flow.py`, `test/test_ipc_robustness.py`, `test/test_socket_cli_contract.py`, `test/test_output_behavior.py`, `test/test_repeated_cancellation.py`, `test/test_cancel_grace.py` | EV-006, EV-007, EV-008, EV-011, EV-012, EV-014, EV-015 | PASS | RF-17 / #39; PR #110 / #72; RF-11; RF-26; RF-30 |
| MVP-12 | Comunicación entre CLI y daemon mediante socket UNIX | TC-037 a TC-041, TC-045, TC-050 a TC-052, TC-055, TC-056, TC-068 a TC-070 | `test/test_ipc_flow.py`, `test/test_ipc_robustness.py`, `test/test_ipc_multiple_jobs.py`, `test/test_socket_integration.py`, `test/test_socket_cli_contract.py` | EV-007, EV-008, EV-009, EV-010, EV-011 | PASS | PR #104 / Issues #41, #44, #45; PR #110 / #72 |
| MVP-13 | Mantener trabajos disponibles durante la sesión del daemon | TC-039, TC-040, TC-052 | `test/test_ipc_flow.py`, `test/test_ipc_multiple_jobs.py` | EV-007, EV-009 | PASS | PR #104 / Issues #41, #44, #45 |
| MVP-14 | Manejar solicitudes inválidas sin detener el servicio | TC-043, TC-046 a TC-048, TC-107 a TC-113, TC-123 a TC-126 | `test/test_ipc_robustness.py`, `test/test_structured_errors.py`, `test/test_queue_observability.py` | EV-008, EV-019, EV-021 | PASS | PR #104 / Issues #41, #44, #45; RNF-21; RF-28 |
| MVP-15 | Eliminar el socket UNIX al detener el daemon | TC-049, TC-056, TC-067, TC-068 | `test/test_ipc_robustness.py`, `test/test_socket_integration.py`, `test/test_socket_cli_contract.py` | EV-008, EV-010, EV-011 | PASS | PR #104 / Issues #41, #44, #45; PR #110 / #72 |
| MVP-16 | Atender múltiples solicitudes consecutivas durante una misma sesión | TC-050 a TC-052, TC-091 a TC-098, TC-116, TC-117 | `test/test_ipc_multiple_jobs.py`, `test/test_duplicate_requests.py`, `test/test_request_logging.py` | EV-009, EV-017, EV-020 | PASS | PR #104 / Issues #41, #44, #45; RF-27; RNF-22 |
| MVP-17 | Configurar un socket UNIX local personalizado para daemon y clientes | TC-053 a TC-056, TC-062, TC-063, TC-067 a TC-070 | `test/test_socket_config.py`, `test/test_socket_integration.py`, `test/test_socket_cli_contract.py` | EV-010, EV-011 | PASS | PR #110 / Issue #72 |
| MVP-18 | Validar rutas y errores del endpoint UNIX configurable | TC-057 a TC-061, TC-064 a TC-066 | `test/test_socket_config.py`, `test/test_socket_integration.py`, `test/test_socket_cli_contract.py` | EV-010, EV-011 | PASS | PR #110 / Issue #72 |
| RF-11 | Conservar y consultar stdout/stderr por separado | TC-071 a TC-075, TC-093 | `test/test_output_behavior.py`, `test/test_duplicate_requests.py` | EV-012, EV-017 | PASS | RF-11 |
| RF-14 | Registrar eventos relevantes en una bitácora centralizada | TC-114, TC-115, TC-118, TC-120 a TC-124 | `test/test_request_logging.py`, `test/test_queue_observability.py` | EV-020, EV-021 | PASS | RF-14 |
| RF-23 | Gestionar y observar rechazos por capacidad de cola | TC-111, TC-121, TC-122 | `test/test_structured_errors.py`, `test/test_queue_observability.py` | EV-019, EV-021 | PASS | RF-23 |
| RF-24 | Proporcionar resumen de salud del servicio | TC-099 a TC-106 | `test/test_health_summary.py` | EV-018 | PASS | RF-24 |
| RF-26 | Manejar cancelaciones repetidas de forma controlada | TC-080, TC-081, TC-094, TC-095 | `test/test_repeated_cancellation.py`, `test/test_duplicate_requests.py` | EV-014, EV-017 | PASS | RF-26 |
| RF-27 | Evitar estados contradictorios ante solicitudes duplicadas | TC-091 a TC-098 | `test/test_duplicate_requests.py`, `docs/technical-guide/semantica-duplicados.md` | EV-017 | PASS | RF-27 / #64 |
| RF-28 | Manejar errores y fallos de comunicación de forma controlada | TC-107 a TC-113, TC-123 a TC-126 | `test/test_structured_errors.py`, `test/test_queue_observability.py` | EV-019, EV-021 | PASS | RF-28 |
| RF-30 | Aplicar período de gracia configurable al cancelar procesos | TC-082 a TC-087 | `test/test_cancel_grace.py` | EV-015 | PASS | RF-30 |
| RNF-09 | Aislar fallos de cleanup sin bloquear scheduler ni servicio | TC-088 a TC-090 | `test/test_cleanup_isolation.py` | EV-016 | PASS | RNF-09 |
| RNF-21 | Presentar errores estructurados con causa y sugerencia operativa | TC-107 a TC-113 | `test/test_structured_errors.py` | EV-019 | PASS | RNF-21 / #81 |
| RNF-22 | Correlacionar solicitudes IPC mediante ReqID | TC-116, TC-117, TC-119, TC-120, TC-122 | `test/test_request_logging.py`, `test/test_queue_observability.py` | EV-020, EV-021 | PASS | RNF-22 / #82 |
| RNF-23 | Mantener guía de usuario actualizada y optimizada | Validación documental | `docs/user-guide/README.md` | PR #116 | PASS | RNF-23 / #83 |
| PR133-ID | Mostrar y resolver referencias cortas de trabajos sin modificar su UUID persistente | TC-150 a TC-164 | `test/test_short_job_ids.py` | EV-026, EV-027 | PASS | PR #133 |
| RNF-02 | Construcción e instalación reproducible desde un clon limpio | TC-141, TC-142, TC-145, TC-146 | `test/test_clean_installation.py` | EV-024 | PASS | RNF-02 |
| RNF-03 | Instalar y operar Jobsy sin privilegios root | TC-143, TC-145, TC-146 | `test/test_clean_installation.py` | EV-024 | PASS | RNF-03 |
| RNF-19 | Instalación limpia sin warnings ni errores | TC-144 | `test/test_clean_installation.py` | EV-024 | PASS | RNF-19 |
| RNF-20 | Ejecutar la batería de verificación mediante un único comando | TC-147 a TC-149 | `test/run_qa_suite.py` | EV-025, EV-035 | PARCIAL (runner operativo; regresión FAIL) | RNF-20 / #80 |
| RNF-31 | Recuperar y distinguir trabajos pendientes, terminados e interrumpidos | TC-127 a TC-133 | `test/test_recovery_behavior.py` | EV-022 | PASS | RNF-31 / #62 |
| RNF-33 | Ejecutar estrés y verificar liberación de memoria, procesos, archivos y sockets | TC-134 a TC-140 | `test/test_resource_stress.py` | EV-023 | PASS | RNF-33 / #71 |
| RNF-25 | Liberar procesos hijos al cerrar el servicio | TC-028 | `test/test_service_shutdown.py` | EV-005 | PASS | RNF-25 / #28 |
| RNF-30 | Evitar procesos huérfanos tras terminación o falla del servicio | TC-019, TC-028, TC-076 a TC-079, TC-087 | `test/test_cancellation.py`, `test/test_service_shutdown.py`, `test/test_process_group_cancellation.py`, `test/test_cancel_grace.py` | EV-004, EV-005, EV-013, EV-015 | PASS | RNF-30 / #29 |
| QA-01 | Documentar casos de prueba ejecutados | TC-001 a TC-260 | `docs/qa/test-cases.md` | EV-001 a EV-035 | PASS | QA / #47 |
| QA-02 | Mantener scripts reproducibles de verificación | TC-001 a TC-260 | `test/*.py` | EV-001 a EV-035 | PASS | QA / #48 |
| QA-03 | Mantener matriz de trazabilidad requisito → prueba → evidencia | TC-001 a TC-260 | `docs/qa/traceability-matrix.md` | EV-001 a EV-035 | PASS | QA / #49 |
| QA-04 | Registrar evidencia de la versión demostrada | TC-001 a TC-260 | `docs/qa/evidence/avance-1/`, `docs/qa/evidence/avance-2/`, `docs/qa/evidence/avance-3/`, `docs/qa/technical-review-2.md` | EV-001 a EV-035 | PASS | QA / #51 |
| QA-INC | Documentar al menos un incidente técnico con síntoma, hipótesis, causa, fix y regresión | TC-119 | `docs/qa/incidents/INC-001-request-id-correlation.md` | EV-020 | PASS | QA / Technical Review 2 |
| QA-05 | Registrar usos representativos de IA durante el avance | N/A | `docs/technical-guide/Registros_uso_IA.pdf` | `Registros_uso_IA.pdf` | PASS | QA / #50 |
| PR135-PROTO | Protocolo v1, framing, validación y errores | TC-165 a TC-180 | `test/test_network_protocol_v1.py` | EV-028 | PASS | PR #135 / RF-16 |
| RF-16 | Configuración host/puerto y acceso remoto TCP | TC-181 a TC-195; TC-247 a TC-260 | `test/test_remote_server_config.py; EV-034 manual` | EV-029, EV-034 | PASS configuración/LAN; PARCIAL integral (INC-002) | RF-16 / PR #135 |
| PR135-CLI | Operaciones CLI remotas y manejo de errores | TC-196 a TC-214 | `test/test_remote_cli.py` | EV-030, EV-035 | FAIL (TC-213 / INC-002) | RF-16; RF-17; RF-28; RNF-21 |
| RNF-15 | Protección de información sensible y permisos de bitácora | TC-215 a TC-222; TC-227, TC-228 | `test/test_remote_security.py` | EV-031, EV-035 | FAIL (TC-219, TC-228 / INC-003, INC-004) | RNF-15 |
| PR135-ACL | Allowlist, registro de IP y disponibilidad local | TC-223 a TC-226; TC-255, TC-256 | `test/test_remote_security.py; EV-034 manual` | EV-031, EV-034 | PASS | RF-14; RF-16 |
| PR135-CONC | Concurrencia, límites y recuperación TCP | TC-229 a TC-239 | `test/test_remote_concurrency.py` | EV-032 | PASS | PR #135 / RF-16; RF-28 |
| RNF-05 | Latencia status con 100 trabajos registrados completados | TC-240 a TC-246 | `test/test_remote_performance.py` | EV-033 | PASS (loopback) | RNF-05 |
| PR135-LAN | Comunicación real entre equipos físicos | TC-247 a TC-260 | `Pruebas manuales; bitácora daemon` | EV-034 | PASS | PR #135 / RF-16 |
| PR135-REG | Regresión de batería vigente | TC-147 a TC-149 (reejecución) | `test/run_qa_suite.py` | EV-035 | FAIL (27/29 scripts PASS) | RNF-20 / PR #135 |

## Observaciones

- La cobertura acumulada comprende `TC-001` a `TC-260`, con evidencias `EV-001` a `EV-035`. Los resultados históricos se conservan; los estados nuevos se muestran por separado.
- `MVP-03 / RF-04` se considera **PASS**. La separación entre el daemon y los procesos de trabajo quedó cubierta mediante `TC-076` a `TC-079`.
- Los casos `TC-091` a `TC-126` corresponden al PR #116 y utilizan `EV-017` a `EV-021`.
- Los casos `TC-127` a `TC-149` corresponden al cierre de QA para la Technical Review 2 y utilizan `EV-022` a `EV-025`.
- Los casos `TC-150` a `TC-164` corresponden al PR #133 y validan presentación y resolución de IDs cortos mediante `EV-026`.
- `EV-027` documenta la regresión completa posterior al PR #133, con la batería vigente finalizando en `PASS`.
- RNF-31 quedó cubierto mediante `TC-127` a `TC-133`, verificando conservación de terminales, `QUEUED → CANCELED`, ejecución interrumpida → `FAILED`, ausencia de reejecución automática y continuidad del daemon.
- RNF-33 quedó cubierto mediante `TC-134` a `TC-140`, incluyendo una carga de 120 trabajos, liberación de procesos hijos, descriptores, memoria estable y limpieza del socket UNIX.
- RNF-02, RNF-03 y RNF-19 quedaron cubiertos mediante `TC-141` a `TC-146`: clon limpio, entorno virtual nuevo, UID no root, instalación sin `sudo`, sin warnings y puntos de entrada operativos.
- RNF-20 quedó cubierto mediante `TC-147` a `TC-149`. Tras incorporar el PR #133, `python test/run_qa_suite.py` ejecutó la batería vigente con `23 PASS`, `0 FAIL` y `0 TIMEOUT`.
- Durante la primera ejecución de `TC-119` se detectó un defecto de propagación de `ReqID`. El incidente fue corregido y revalidado; se documenta en `docs/qa/incidents/INC-001-request-id-correlation.md`.
- La evidencia de la versión demostrada y la batería ejecutada para Technical Review 2 se consolida en `docs/qa/technical-review-2.md`.
- Las pruebas históricas con contratos anteriores se conservan como evidencia de ejecuciones previas, pero el runner consolidado utiliza únicamente la batería vigente.
- RNF-23 se validó como cambio documental mediante `docs/user-guide/README.md`.
- RF-16 amplía su cobertura a TCP, host/puerto y LAN en PR #135. La configuración y comunicación válida obtienen PASS; el manejo de JOBSY_PORT inválido permanece FAIL (INC-002), por lo que el alcance integral remoto requiere corrección.
- Al cierre histórico del PR #133 no se identificaban defectos bloqueantes abiertos. En PR #135 permanecen tres incidentes abiertos; dictamen NO APROBADO.

- PR #135 (`32bd487`): 96 casos nuevos, 93 PASS y 3 FAIL; EV-035 27/29 scripts PASS, 2 FAIL conocidos, 0 TIMEOUT.
- RNF-05 probado con 100 trabajos registrados y completados por loopback (máximo 0.711 ms). TC-258 complementario LAN: 4 trabajos, máximo 3.425 ms; no equivale a la carga RNF-05.
- RNF-15: fallos de sanitización y excepción simulada; no se demostró exposición real de credenciales.
- OBS-09 y OBS-10: inconsistencias de logging reproducidas en EV-034 y EV-035; no invalidan los casos funcionales.
- EV-035: TC-147 PASS; TC-148 y TC-149 FAIL en reejecución. RNF-20 mantiene capacidad de ejecución con un comando; resultado agregado no satisfactorio.
- Los vínculos de los nuevos casos con RF/RNF son asociaciones de QA por alcance; no se asignan nuevos números de issues sin confirmación documental.
