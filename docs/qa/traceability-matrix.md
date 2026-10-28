# Matriz de trazabilidad — Jobsy

Esta matriz relaciona las funcionalidades requeridas del MVP, los requisitos formales y los entregables de QA con sus casos de prueba, scripts, artefactos y evidencias.

La matriz se mantiene de forma acumulativa e incluye las validaciones ejecutadas por QA sobre los PR #101, #102, #104, #110, #114 y #116.

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
| RNF-25 | Liberar procesos hijos al cerrar el servicio | TC-028 | `test/test_service_shutdown.py` | EV-005 | PASS | RNF-25 / #28 |
| RNF-30 | Evitar procesos huérfanos tras terminación o falla del servicio | TC-019, TC-028, TC-076 a TC-079, TC-087 | `test/test_cancellation.py`, `test/test_service_shutdown.py`, `test/test_process_group_cancellation.py`, `test/test_cancel_grace.py` | EV-004, EV-005, EV-013, EV-015 | PASS | RNF-30 / #29 |
| QA-01 | Documentar casos de prueba ejecutados | TC-001 a TC-126 | `docs/qa/test-cases.md` | EV-001 a EV-021 | PASS | QA / #47 |
| QA-02 | Mantener scripts reproducibles de verificación | TC-001 a TC-126 | `test/*.py` | EV-001 a EV-021 | PASS | QA / #48 |
| QA-03 | Mantener matriz de trazabilidad requisito → prueba → evidencia | TC-001 a TC-126 | `docs/qa/traceability-matrix.md` | EV-001 a EV-021 | PASS | QA / #49 |
| QA-04 | Registrar evidencia de la versión demostrada | TC-001 a TC-126 | `docs/qa/evidence/avance-1/`, `docs/qa/evidence/avance-2/` | EV-001 a EV-021 | PASS | QA / #51 |
| QA-05 | Registrar usos representativos de IA durante el avance | N/A | `docs/technical-guide/Registros_uso_IA.pdf` | `Registros_uso_IA.pdf` | PASS | QA / #50 |

## Observaciones

- La cobertura acumulada comprende `TC-001` a `TC-126`, con evidencias `EV-001` a `EV-021`.
- `MVP-03 / RF-04` se considera **PASS**. La separación entre el proceso del daemon y los procesos de los trabajos quedó cubierta explícitamente mediante `TC-076` a `TC-079`, que verifican PID, PGID, SID y la terminación completa del grupo.
- Los casos `TC-037` a `TC-052` corresponden a la validación funcional del PR #104 y utilizan `EV-007` a `EV-009`.
- Los casos `TC-053` a `TC-070` corresponden a la validación del PR #110 / Issue #72 y utilizan `EV-010` y `EV-011`.
- Los casos `TC-071` a `TC-090` corresponden al PR #114 y cubren RF-11, RNF-30, RF-26, RF-30 y RNF-09 mediante `EV-012` a `EV-016`.
- Los casos `TC-091` a `TC-126` corresponden al PR #116 y utilizan `EV-017` a `EV-021`.
- `TC-091` a `TC-098` validan RF-27 y la semántica de solicitudes duplicadas para `list`, `status`, `output`, `cancel` y `run`.
- `TC-099` a `TC-106` validan RF-24 mediante el resumen `health`, incluyendo trabajos `RUNNING`, `QUEUED`, errores recientes y el límite de 10 registros.
- `TC-107` a `TC-113` validan RNF-21 / RF-28 mediante respuestas estructuradas con `operation`, `cause` y `suggestion`.
- `TC-114` a `TC-120` validan RF-14 / RNF-22 mediante `jobsy.log`, Job ID y correlación de solicitudes con `ReqID`.
- Durante la primera ejecución de `TC-119` se detectó que el `ReqID` no se propagaba a eventos posteriores. El defecto fue corregido en el PR #116 y la revalidación terminó en `PASS`.
- `TC-121` a `TC-126` validan observabilidad de cola, registro de rechazos, desconexiones prematuras y continuidad operativa del daemon.
- RNF-23 se validó como cambio documental mediante la actualización de `docs/user-guide/README.md`; no se añadió un caso funcional específico al no introducir por sí mismo un comportamiento ejecutable nuevo.
- Durante la regresión del PR #116, las comprobaciones históricas `TC-046` y `TC-047` requirieron reinterpretación porque el contrato de error cambió de `message` a `operation`, `cause` y `suggestion`. El comportamiento actual queda validado formalmente por `TC-107` y `TC-108`.
- RF-16 continúa **PARCIAL**: las pruebas del PR #110 cubren el endpoint UNIX local configurable, pero no existe comunicación TCP ni configuración de host/puerto dentro del alcance validado.
- Los Issues #47, #48, #49, #50 y #51 corresponden a entregables de QA y certificación.
