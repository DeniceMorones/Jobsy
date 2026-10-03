# Matriz de trazabilidad — MVP Avance 1

Esta matriz relaciona las funcionalidades requeridas del MVP y los requisitos formales verificados con sus casos de prueba, scripts y evidencias.

| ID | Requisito / funcionalidad | Caso(s) de prueba | Automatización | Evidencia | Estado | Requisito formal / Issue |
|---|---|---|---|---|---|---|
| MVP-01 | Enviar un trabajo | TC-030 | `test_cli_behavior.py` | EV-006 | PASS | RF-01 / #30 |
| MVP-02 | Obtener identificador único | TC-006, TC-030 | `test_executor.py`, `test_cli_behavior.py` | EV-002, EV-006 | PASS | RF-01 / #30 |
| MVP-03 | Ejecutar trabajos sin bloquear nuevas solicitudes | TC-007, TC-019 | `test_executor.py`, `test_cancellation.py` | EV-002, EV-004 | PARCIAL | RF-04 / #32 |
| MVP-04 | Consultar estado y metadatos por ID | TC-015, TC-016, TC-032, TC-034 | `test_job_manager.py`, `test_cli_behavior.py` | EV-003, EV-006 | PASS | RF-08 / #35 |
| MVP-05 | Listar trabajos y filtrar por estado | TC-017, TC-031, TC-035 | `test_job_manager.py`, `test_cli_behavior.py` | EV-003, EV-006 | PASS | RF-09 / #36 |
| MVP-06 | Solicitar cancelación | TC-018 a TC-022, TC-033 | `test_cancellation.py`, `test_cli_behavior.py` | EV-004, EV-006 | PASS | RF-10 / #37 |
| MVP-07 | Registrar código de salida y tiempos | TC-010, TC-013, TC-014 | `test_executor.py` | EV-002 | PASS | RF-07 / #34 |
| MVP-08 | Validar entradas incorrectas de forma controlada | TC-001 a TC-005, TC-034 a TC-036 | `test_validation.py`, `test_cli_behavior.py` | EV-001, EV-006 | PASS | RF-02 / #31; RF-17 / #39 |
| MVP-09 | Representar estados mínimos del trabajo | TC-007, TC-008, TC-011, TC-018, TC-019 | `test_executor.py`, `test_cancellation.py` | EV-002, EV-004 | PASS | RF-06 / #33 |
| MVP-10 | Inicio y apagado controlado del servicio | TC-023 a TC-028 | `test_service_shutdown.py` | EV-005 | PASS | RF-15 / #38 |
| MVP-11 | Ayuda y códigos de salida del cliente | TC-029 a TC-036 | `test_cli_behavior.py` | EV-006 | PASS | RF-17 / #39 |
| RNF-25 | Liberar procesos hijos al cerrar el servicio | TC-028 | `test_service_shutdown.py` | EV-005 | PASS | RNF-25 / #28 |
| RNF-30 | Evitar procesos huérfanos tras terminación o falla del servicio | TC-019, TC-028 | `test_cancellation.py`, `test_service_shutdown.py` | EV-004, EV-005 | PASS | RNF-30 / #29 |

## Observaciones

- `MVP-03 / RF-04` se mantiene como **PARCIAL** porque las pruebas actuales demuestran ejecución concurrente/no bloqueante y uso de procesos Linux en el flujo de cancelación, pero no incluyen una prueba dedicada que compare explícitamente el PID de Jobsy contra el PID del trabajo.
- RF-10 corresponde al Issue #37, RF-15 al Issue #38 y RF-17 al Issue #39.
