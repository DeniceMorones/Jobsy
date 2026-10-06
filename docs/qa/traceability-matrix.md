# Matriz de trazabilidad — MVP Avance 1

Esta matriz relaciona las funcionalidades requeridas del MVP, los requisitos formales y los entregables de QA con sus casos de prueba, scripts, artefactos y evidencias.

| ID | Requisito / funcionalidad | Caso(s) de prueba | Automatización / artefacto | Evidencia | Estado | Requisito formal / Issue |
|---|---|---|---|---|---|---|
| MVP-01 | Enviar un trabajo | TC-030, TC-038, TC-050 | `test/test_cli_behavior.py`, `test/test_ipc_flow.py`, `test/test_ipc_multiple_jobs.py` | EV-006, EV-007, EV-009 | PASS | RF-01 / #30 |
| MVP-02 | Obtener identificador único | TC-006, TC-030, TC-038, TC-051 | `test/test_executor.py`, `test/test_cli_behavior.py`, `test/test_ipc_flow.py`, `test/test_ipc_multiple_jobs.py` | EV-002, EV-006, EV-007, EV-009 | PASS | RF-01 / #30 |
| MVP-03 | Ejecutar trabajos sin bloquear nuevas solicitudes | TC-007, TC-019, TC-050, TC-052 | `test/test_executor.py`, `test/test_cancellation.py`, `test/test_ipc_multiple_jobs.py` | EV-002, EV-004, EV-009 | PARCIAL | RF-04 / #32 |
| MVP-04 | Consultar estado y metadatos por ID | TC-015, TC-016, TC-032, TC-034, TC-039, TC-042 | `test/test_job_manager.py`, `test/test_cli_behavior.py`, `test/test_ipc_flow.py` | EV-003, EV-006, EV-007 | PASS | RF-08 / #35 |
| MVP-05 | Listar trabajos y filtrar por estado | TC-017, TC-031, TC-035, TC-040, TC-045, TC-052 | `test/test_job_manager.py`, `test/test_cli_behavior.py`, `test/test_ipc_flow.py`, `test/test_ipc_robustness.py`, `test/test_ipc_multiple_jobs.py` | EV-003, EV-006, EV-007, EV-008, EV-009 | PASS | RF-09 / #36 |
| MVP-06 | Solicitar cancelación | TC-018 a TC-022, TC-033, TC-041, TC-044 | `test/test_cancellation.py`, `test/test_cli_behavior.py`, `test/test_ipc_flow.py`, `test/test_ipc_robustness.py` | EV-004, EV-006, EV-007, EV-008 | PASS | RF-10 / #37 |
| MVP-07 | Registrar código de salida y tiempos | TC-010, TC-013, TC-014, TC-039, TC-052 | `test/test_executor.py`, `test/test_ipc_flow.py`, `test/test_ipc_multiple_jobs.py` | EV-002, EV-007, EV-009 | PASS | RF-07 / #34 |
| MVP-08 | Validar entradas incorrectas de forma controlada | TC-001 a TC-005, TC-034 a TC-036, TC-042 a TC-047 | `test/test_validation.py`, `test/test_cli_behavior.py`, `test/test_ipc_flow.py`, `test/test_ipc_robustness.py` | EV-001, EV-006, EV-007, EV-008 | PASS | RF-02 / #31; RF-17 / #39 |
| MVP-09 | Representar estados mínimos del trabajo | TC-007, TC-008, TC-011, TC-018, TC-019, TC-039, TC-041, TC-045, TC-052 | `test/test_executor.py`, `test/test_cancellation.py`, `test/test_ipc_flow.py`, `test/test_ipc_robustness.py`, `test/test_ipc_multiple_jobs.py` | EV-002, EV-004, EV-007, EV-008, EV-009 | PASS | RF-06 / #33 |
| MVP-10 | Inicio y apagado controlado del servicio | TC-023 a TC-028, TC-037, TC-049 | `test/test_service_shutdown.py`, `test/test_ipc_flow.py`, `test/test_ipc_robustness.py` | EV-005, EV-007, EV-008 | PASS | RF-15 / #38 |
| MVP-11 | Ayuda y códigos de salida del cliente | TC-029 a TC-036, TC-038, TC-042 a TC-044 | `test/test_cli_behavior.py`, `test/test_ipc_flow.py`, `test/test_ipc_robustness.py` | EV-006, EV-007, EV-008 | PASS | RF-17 / #39 |
| MVP-12 | Comunicación entre CLI y daemon mediante socket UNIX | TC-037 a TC-041, TC-045, TC-050 a TC-052 | `test/test_ipc_flow.py`, `test/test_ipc_robustness.py`, `test/test_ipc_multiple_jobs.py` | EV-007, EV-008, EV-009 | PASS | PR #104 / Issues #41, #44, #45 |
| MVP-13 | Mantener trabajos disponibles durante la sesión del daemon | TC-039, TC-040, TC-052 | `test/test_ipc_flow.py`, `test/test_ipc_multiple_jobs.py` | EV-007, EV-009 | PASS | PR #104 / Issues #41, #44, #45 |
| MVP-14 | Manejar solicitudes inválidas sin detener el servicio | TC-043, TC-046 a TC-048 | `test/test_ipc_robustness.py` | EV-008 | PASS | PR #104 / Issues #41, #44, #45 |
| MVP-15 | Eliminar el socket UNIX al detener el daemon | TC-049 | `test/test_ipc_robustness.py` | EV-008 | PASS | PR #104 / Issues #41, #44, #45 |
| MVP-16 | Atender múltiples solicitudes consecutivas durante una misma sesión | TC-050 a TC-052 | `test/test_ipc_multiple_jobs.py` | EV-009 | PASS | PR #104 / Issues #41, #44, #45 |
| RNF-25 | Liberar procesos hijos al cerrar el servicio | TC-028 | `test/test_service_shutdown.py` | EV-005 | PASS | RNF-25 / #28 |
| RNF-30 | Evitar procesos huérfanos tras terminación o falla del servicio | TC-019, TC-028 | `test/test_cancellation.py`, `test/test_service_shutdown.py` | EV-004, EV-005 | PASS | RNF-30 / #29 |
| QA-01 | Documentar casos de prueba ejecutados | TC-001 a TC-052 | `docs/qa/test-cases.md` | EV-001 a EV-009 | PASS | QA / #47 |
| QA-02 | Mantener scripts reproducibles de verificación | TC-001 a TC-052 | `test/*.py` | EV-001 a EV-009 | PASS | QA / #48 |
| QA-03 | Mantener matriz de trazabilidad requisito → prueba → evidencia | TC-001 a TC-052 | `docs/qa/traceability-matrix.md` | EV-001 a EV-009 | PASS | QA / #49 |
| QA-04 | Registrar evidencia de la versión demostrada | TC-001 a TC-052 | `docs/qa/evidence/avance-1/` | EV-001 a EV-009 | PASS | QA / #51 |
| QA-05 | Registrar usos representativos de IA durante el avance | N/A | `docs/technical-guide/Registros_uso_IA.pdf` | `Registros_uso_IA.pdf` | PASS | QA / #50 |

## Observaciones

- `MVP-03 / RF-04` se mantiene como **PARCIAL** porque las pruebas actuales demuestran ejecución concurrente/no bloqueante y procesamiento de múltiples trabajos, pero todavía no incluyen una prueba dedicada que compare explícitamente el PID del daemon o de Jobsy contra el PID del proceso ejecutado.
- Los casos `TC-037` a `TC-052` corresponden a la validación funcional del PR #104 y utilizan las evidencias `EV-007`, `EV-008` y `EV-009`.
- `TC-037` a `TC-041` validan el flujo principal de comunicación entre la CLI y el daemon mediante socket UNIX.
- `TC-043` a `TC-049` validan manejo de errores, robustez del servicio y limpieza del socket durante el apagado.
- `TC-050` a `TC-052` validan múltiples solicitudes consecutivas, unicidad de identificadores y conservación de trabajos durante la misma sesión del daemon.
- La persistencia validada actualmente corresponde únicamente a la sesión activa del daemon. Las pruebas no verifican persistencia permanente después de reiniciar el servicio.
- Los Issues #47, #48, #49, #50 y #51 corresponden a los entregables de QA y certificación del Avance 1.
- RF-10 corresponde al Issue #37, RF-15 al Issue #38 y RF-17 al Issue #39.
- El PR #104 relaciona los Issues #41, #44 y #45 con la implementación del flujo mediante sockets. Hasta asociar cada Issue con su requisito formal individual, se mantienen agrupados en las funcionalidades de IPC correspondientes.