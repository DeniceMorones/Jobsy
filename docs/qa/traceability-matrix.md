# Matriz de trazabilidad — Jobsy

Esta matriz relaciona las funcionalidades requeridas del MVP, los requisitos formales y los entregables de QA con sus casos de prueba, scripts, artefactos y evidencias.

La matriz se mantiene de forma acumulativa e incluye las validaciones ejecutadas por QA sobre los PR #101, #102, #104 y #110.

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
| MVP-11 | Ayuda y códigos de salida del cliente | TC-029 a TC-036, TC-038, TC-042 a TC-044, TC-064 a TC-066 | `test/test_cli_behavior.py`, `test/test_ipc_flow.py`, `test/test_ipc_robustness.py`, `test/test_socket_cli_contract.py` | EV-006, EV-007, EV-008, EV-011 | PASS | RF-17 / #39; PR #110 / #72 |
| MVP-12 | Comunicación entre CLI y daemon mediante socket UNIX | TC-037 a TC-041, TC-045, TC-050 a TC-052, TC-055, TC-056, TC-068 a TC-070 | `test/test_ipc_flow.py`, `test/test_ipc_robustness.py`, `test/test_ipc_multiple_jobs.py`, `test/test_socket_integration.py`, `test/test_socket_cli_contract.py` | EV-007, EV-008, EV-009, EV-010, EV-011 | PASS | PR #104 / Issues #41, #44, #45; PR #110 / #72 |
| MVP-13 | Mantener trabajos disponibles durante la sesión del daemon | TC-039, TC-040, TC-052 | `test/test_ipc_flow.py`, `test/test_ipc_multiple_jobs.py` | EV-007, EV-009 | PASS | PR #104 / Issues #41, #44, #45 |
| MVP-14 | Manejar solicitudes inválidas sin detener el servicio | TC-043, TC-046 a TC-048 | `test/test_ipc_robustness.py` | EV-008 | PASS | PR #104 / Issues #41, #44, #45 |
| MVP-15 | Eliminar el socket UNIX al detener el daemon | TC-049, TC-056, TC-067, TC-068 | `test/test_ipc_robustness.py`, `test/test_socket_integration.py`, `test/test_socket_cli_contract.py` | EV-008, EV-010, EV-011 | PASS | PR #104 / Issues #41, #44, #45; PR #110 / #72 |
| MVP-16 | Atender múltiples solicitudes consecutivas durante una misma sesión | TC-050 a TC-052 | `test/test_ipc_multiple_jobs.py` | EV-009 | PASS | PR #104 / Issues #41, #44, #45 |
| MVP-17 | Configurar un socket UNIX local personalizado para daemon y clientes | TC-053 a TC-056, TC-062, TC-063, TC-067 a TC-070 | `test/test_socket_config.py`, `test/test_socket_integration.py`, `test/test_socket_cli_contract.py` | EV-010, EV-011 | PASS | PR #110 / Issue #72 |
| MVP-18 | Validar rutas y errores del endpoint UNIX configurable | TC-057 a TC-061, TC-064 a TC-066 | `test/test_socket_config.py`, `test/test_socket_integration.py`, `test/test_socket_cli_contract.py` | EV-010, EV-011 | PASS | PR #110 / Issue #72 |
| RNF-25 | Liberar procesos hijos al cerrar el servicio | TC-028 | `test/test_service_shutdown.py` | EV-005 | PASS | RNF-25 / #28 |
| RNF-30 | Evitar procesos huérfanos tras terminación o falla del servicio | TC-019, TC-028 | `test/test_cancellation.py`, `test/test_service_shutdown.py` | EV-004, EV-005 | PASS | RNF-30 / #29 |
| QA-01 | Documentar casos de prueba ejecutados | TC-001 a TC-070 | `docs/qa/test-cases.md` | EV-001 a EV-011 | PASS | QA / #47 |
| QA-02 | Mantener scripts reproducibles de verificación | TC-001 a TC-070 | `test/*.py` | EV-001 a EV-011 | PASS | QA / #48 |
| QA-03 | Mantener matriz de trazabilidad requisito → prueba → evidencia | TC-001 a TC-070 | `docs/qa/traceability-matrix.md` | EV-001 a EV-011 | PASS | QA / #49 |
| QA-04 | Registrar evidencia de la versión demostrada | TC-001 a TC-070 | `docs/qa/evidence/avance-1/` | EV-001 a EV-011 | PASS | QA / #51 |
| QA-05 | Registrar usos representativos de IA durante el avance | N/A | `docs/technical-guide/Registros_uso_IA.pdf` | `Registros_uso_IA.pdf` | PASS | QA / #50 |

## Observaciones

- `MVP-03 / RF-04` se mantiene como **PARCIAL** porque las pruebas actuales demuestran ejecución concurrente/no bloqueante y procesamiento de múltiples trabajos, pero todavía no incluyen una prueba dedicada que compare explícitamente el PID del daemon o de Jobsy contra el PID del proceso ejecutado.
- Los casos `TC-037` a `TC-052` corresponden a la validación funcional del PR #104 y utilizan las evidencias `EV-007`, `EV-008` y `EV-009`.
- `TC-037` a `TC-041` validan el flujo principal de comunicación entre la CLI y el daemon mediante socket UNIX.
- `TC-043` a `TC-049` validan manejo de errores, robustez del servicio y limpieza del socket durante el apagado.
- `TC-050` a `TC-052` validan múltiples solicitudes consecutivas, unicidad de identificadores y conservación de trabajos durante la misma sesión del daemon.
- Los casos `TC-053` a `TC-070` corresponden a la validación del PR #110 / Issue #72 y utilizan las evidencias `EV-010` y `EV-011`.
- `TC-053` a `TC-062` validan el endpoint predeterminado, rutas personalizadas, validaciones de ruta, protección frente a rutas existentes y retorno al socket predeterminado.
- `TC-063` a `TC-070` validan el contrato público entre `jobsy-daemon` y los clientes, el comportamiento de `JOBSY_SOCKET_PATH`, códigos de salida, expansión de `~` y los puntos de entrada `jobsy`, `execute`, `list`, `status` y `cancel`.
- El PR #110 fue validado en Ubuntu 26.04.1 LTS ARM64 (`aarch64`) sobre una máquina virtual Linux ejecutada en MacBook Pro con Apple Silicon M1, usando Python 3.14.4 y Git 2.53.0.
- La implementación validada del PR #110 mantiene `/tmp/jobsy.sock` como endpoint predeterminado y permite configurar un socket UNIX local mediante `--socket-path` para el daemon y `JOBSY_SOCKET_PATH` para los clientes.
- RF-16 continúa **PARCIAL**: las pruebas del PR #110 cubren el endpoint UNIX local configurable, pero no existe comunicación TCP ni configuración de host/puerto dentro del alcance validado.
- La persistencia validada previamente en los casos hasta PR #104 corresponde a la sesión activa del daemon; los casos ejecutados para PR #110 no añaden una prueba específica de persistencia después de reiniciar el servicio.
- Los Issues #47, #48, #49, #50 y #51 corresponden a los entregables de QA y certificación del Avance 1.
- RF-10 corresponde al Issue #37, RF-15 al Issue #38 y RF-17 al Issue #39.
- El PR #104 relaciona los Issues #41, #44 y #45 con la implementación del flujo mediante sockets. Hasta asociar cada Issue con su requisito formal individual, se mantienen agrupados en las funcionalidades de IPC correspondientes.
