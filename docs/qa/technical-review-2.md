# Technical Review 2 — Evidencia de versión demostrada y batería de pruebas

## 1. Identificación de la revisión

- **Proyecto:** Jobsy
- **Responsable QA:** Alexia Gomez Rubio
- **Rama QA:** `alexia-test-pr116`
- **Commit de referencia validado:** `10c7a8e`
- **PR principal validado:** PR #116
- **Entorno:** Ubuntu 26.04.1 LTS sobre WSL2
- **Kernel:** `6.18.33.2-microsoft-standard-WSL2`
- **Python:** `3.14.4`
- **Git:** `2.53.0`

---

## 2. Objetivo

Documentar la versión demostrada de Jobsy y la batería de pruebas ejecutada para la Technical Review 2, dejando evidencia reproducible del estado funcional, de robustez, recuperación, instalación y operación del sistema.

---

## 3. Alcance validado

La validación acumulada de QA comprende:

```text
TC-001 a TC-149
```

Resultado acumulado:

```text
149 casos con resultado final PASS
0 defectos bloqueantes abiertos dentro del alcance validado
```

La cobertura incluye, entre otros:

- ejecución y administración de trabajos;
- validación de entradas;
- cancelación;
- salida estándar y error;
- comunicación mediante socket UNIX;
- múltiples solicitudes;
- configuración del endpoint UNIX;
- aislamiento y cancelación de grupos de procesos;
- período de gracia de cancelación;
- cleanup;
- solicitudes duplicadas;
- health summary;
- errores estructurados;
- observabilidad y logging;
- correlación mediante `ReqID`;
- recuperación tras reinicio/interrupción;
- estrés y liberación de recursos;
- instalación desde clon limpio;
- operación sin privilegios root;
- instalación sin warnings;
- ejecución de una batería de QA mediante un único comando.

---

## 4. Evidencias acumuladas

Las evidencias de QA registradas comprenden:

```text
EV-001 a EV-025
```

Para la ampliación correspondiente a esta revisión se generaron específicamente:

| Evidencia | Cobertura |
|---|---|
| `EV-017-duplicate-requests-output.txt` | RF-27 — solicitudes duplicadas |
| `EV-018-health-summary-output.txt` | RF-24 — resumen de salud |
| `EV-019-structured-errors-output.txt` | RNF-21 / RF-28 — errores estructurados |
| `EV-020-request-logging-output.txt` | RF-14 / RNF-22 — logging y correlación ReqID |
| `EV-021-queue-observability-output.txt` | Observabilidad de cola y desconexiones |
| `EV-022-recovery-behavior-output.txt` | RNF-31 — recuperación |
| `EV-023-resource-stress-output.txt` | RNF-33 — estrés y liberación de recursos |
| `EV-024-clean-installation-output.txt` | RNF-02 / RNF-03 / RNF-19 |
| `EV-025-single-command-suite-output.txt` | RNF-20 — batería mediante un único comando |

---

## 5. Resultados de las pruebas adicionales para Technical Review 2

### RNF-31 — Recuperación

Casos:

```text
TC-127 a TC-133
```

Resultado:

```text
7 PASS
0 FAIL
```

Se verificó:

- conservación de trabajos terminales;
- persistencia de stdout/stderr;
- recuperación de `QUEUED` como `CANCELED`;
- recuperación de ejecuciones interrumpidas como `FAILED`;
- ausencia de reejecución automática;
- no ejecución automática de trabajos pendientes;
- continuidad operativa del daemon.

Evidencia:

```text
EV-022-recovery-behavior-output.txt
```

---

### RNF-33 — Estrés y liberación de recursos

Casos:

```text
TC-134 a TC-140
```

Resultado:

```text
7 PASS
0 FAIL
```

Carga aplicada:

```text
120 trabajos
120 aceptados
120 SUCCEEDED
0 rechazados
```

Resultados de recursos:

```text
FD iniciales: 6
FD después del estrés: 6
Procesos hijos residuales: 0
FD abiertos sobre archivos eliminados: 0
```

Memoria:

```text
RSS inicial: 26988 KB
RSS en reposo posterior: 29588 KB
Variación durante las muestras: 0 KB
```

La memoria permaneció estable una vez finalizada la carga.

También se verificó que:

- el daemon continuara operativo;
- el socket UNIX existiera durante la ejecución;
- el socket UNIX fuera eliminado al apagar el daemon.

Evidencia:

```text
EV-023-resource-stress-output.txt
```

---

### RNF-02 / RNF-03 / RNF-19 — Instalación limpia

Casos:

```text
TC-141 a TC-146
```

Resultado:

```text
6 PASS
0 FAIL
```

Datos de la ejecución:

```text
Commit probado: 10c7a8e
UID de ejecución: 1000
Exit code instalación: 0
Advertencias detectadas: 0
```

Se verificó:

- clon limpio del repositorio;
- creación de un entorno virtual nuevo;
- instalación sin privilegios root;
- instalación sin `sudo`;
- instalación dentro del entorno virtual;
- ausencia de warnings y errores de construcción;
- instalación de los puntos de entrada:
  - `jobsy`
  - `jobsy-daemon`
  - `execute`
  - `list`
  - `status`
  - `cancel`
- funcionamiento de `jobsy --help`;
- funcionamiento de `jobsy-daemon --help`.

Evidencia:

```text
EV-024-clean-installation-output.txt
```

---

### RNF-20 — Batería ejecutable mediante un único comando

Casos:

```text
TC-147 a TC-149
```

Comando de ejecución:

```bash
python test/run_qa_suite.py
```

Resultado final:

```text
Scripts ejecutados: 22
PASS: 22
FAIL: 0
TIMEOUT: 0
Duración total: 31.31 s
RESULTADO GENERAL: PASS
```

Scripts incluidos en la batería final:

```text
test_cancel_grace.py
test_clean_installation.py
test_cleanup_isolation.py
test_duplicate_requests.py
test_entry_points.py
test_health_summary.py
test_ipc_flow.py
test_ipc_multiple_jobs.py
test_job_manager.py
test_output_behavior.py
test_process_group_cancellation.py
test_queue_observability.py
test_queue_processes.py
test_recovery_behavior.py
test_repeated_cancellation.py
test_request_logging.py
test_resource_stress.py
test_scheduler.py
test_socket_cli_contract.py
test_socket_config.py
test_socket_integration.py
test_structured_errors.py
```

Evidencia:

```text
EV-025-single-command-suite-output.txt
```

### Pruebas históricas excluidas del runner consolidado

La batería consolidada no utiliza algunos scripts históricos cuyas expectativas pertenecen a contratos anteriores del sistema:

- `test_process_behavior.py`
- `test_ipc_robustness.py`
- `test_cancellation.py`
- `test_cli_behavior.py`
- `test_queue_ipc.py`
- `test_service_shutdown.py`

Las funcionalidades actuales cubiertas originalmente por esos scripts se encuentran verificadas por casos y scripts posteriores compatibles con la arquitectura y contratos vigentes.

---

## 6. Incidente técnico documentado

Durante la validación de RNF-22 se detectó un defecto real en `TC-119`.

### Síntoma

El `ReqID` se generaba al recibir una solicitud `run`, pero no se conservaba de forma consistente en los eventos posteriores del mismo flujo.

### Resultado inicial

```text
TC-119: FAIL
```

### Corrección

Commit:

```text
a5f22f6
feat(daemon): corrige correlación de ReqID en bitácora y consolida pruebas de robustez y observabilidad
```

### Revalidación

Después del fix:

```text
PASS: La solicitud run fue aceptada.
PASS: La solicitud run registró un ReqID.
PASS: El mismo ReqID aparece en más de un evento.
```

El incidente completo se documenta en:

```text
docs/qa/incidents/INC-001-request-id-correlation.md
```

---

## 7. Requisitos del rol QA cubiertos

| Requisito / responsabilidad | Estado | Evidencia principal |
|---|---|---|
| RNF-31 — recuperación de pendientes, terminados e interrumpidos | PASS | TC-127 a TC-133 / EV-022 |
| RNF-33 — estrés y liberación de recursos | PASS | TC-134 a TC-140 / EV-023 |
| RNF-02 — construcción/instalación reproducible desde clon limpio | PASS | TC-141 a TC-146 / EV-024 |
| RNF-03 — operación sin privilegios root | PASS | TC-143 / EV-024 |
| RNF-19 — instalación limpia sin warnings | PASS | TC-144 / EV-024 |
| RNF-20 — script de verificación mediante un único comando | PASS | TC-147 a TC-149 / EV-025 |
| Incidente técnico documentado | PASS | `INC-001-request-id-correlation.md` |
| Evidencia de versión demostrada y batería TR2 | PASS | Este documento + EV-001 a EV-025 |

---

## 8. Resultado de la Technical Review 2

La versión validada cumple con la batería de QA definida para la Technical Review 2 dentro del alcance comprobado.

Resumen:

```text
TC-001 a TC-149
149 casos con resultado final PASS

EV-001 a EV-025

Batería consolidada:
22 scripts
22 PASS
0 FAIL
0 TIMEOUT
```

No se identifican defectos bloqueantes abiertos dentro del alcance final validado.

---

## 9. Conclusión QA

La versión demostrada queda respaldada por casos de prueba documentados, evidencias reproducibles, una matriz de trazabilidad, una batería automatizada ejecutable mediante un único comando y un incidente técnico documentado con su corrección y revalidación.

Con estos artefactos, los entregables de QA asignados para la Technical Review 2 quedan cubiertos dentro del alcance validado.
