# Casos de prueba — Jobsy

Este documento registra los casos de prueba ejecutados por QA sobre los alcances funcionales revisados de Jobsy en los PR #101, #102, #104, #110, #114, #116, #133 y #135.

La numeración de los casos se mantiene de forma acumulativa para conservar la trazabilidad entre pruebas, requisitos, scripts y evidencias.

Hasta el momento se han documentado y ejecutado los casos **TC-001 a TC-260**.

Las pruebas cubren validación de entradas, ejecución de trabajos, estados y metadatos, cancelación, apagado seguro, comportamiento de la CLI, comunicación IPC mediante sockets UNIX, robustez ante solicitudes inválidas, múltiples trabajos durante una misma sesión y configuración de sockets UNIX personalizados.

Los casos **TC-053 a TC-070** corresponden a la validación del **PR #110**, relacionado con la configuración del socket UNIX local.

Los casos **TC-071 a TC-090** corresponden a la validación del **PR #114**, relacionado con la gestión del ciclo de vida de trabajos, separación de salidas, grupos de procesos, cancelación repetida, período de gracia configurable y aislamiento de fallos de limpieza.

Los casos **TC-091 a TC-126** corresponden a la validación del **PR #116**, relacionado con solicitudes duplicadas, resumen de salud, errores estructurados, bitácora centralizada, correlación mediante `ReqID`, observabilidad de cola y robustez ante desconexiones del cliente.

Los casos **TC-127 a TC-149** corresponden al cierre de QA para la **Technical Review 2**, cubriendo recuperación, estrés y liberación de recursos, instalación limpia, ejecución sin privilegios root, ausencia de warnings y batería de pruebas ejecutable mediante un único comando.

Los casos **TC-150 a TC-164** corresponden al PR #133 (IDs cortos). Los casos **TC-165 a TC-260** corresponden al PR #135 (cliente remoto TCP).

### Entorno de ejecución del PR #135

- Fecha: 2026-11-28; commit `32bd487`; rama `alexia-test-pr135`.
- PC A: Windows 11, Ubuntu WSL2 mirrored, Python 3.14.4, entorno `.venv`.
- PC B: Mac/UTM, Ubuntu Server 26.04.1 ARM64, Python 3.14.4, IP 192.168.100.151; PC A: 192.168.100.64, TCP 8765.
- Pruebas automatizadas en loopback y pruebas manuales LAN; sin credenciales reales.

### Entorno de ejecución del PR #110

Las pruebas del PR #110 fueron ejecutadas en:

- Ubuntu 26.04.1 LTS.
- Arquitectura ARM64 (`aarch64`).
- Linux kernel 7.0.0-38-generic.
- Python 3.14.4.
- Git 2.53.0.
- Máquina virtual Linux ejecutada sobre MacBook Pro con Apple Silicon M1.

Para las pruebas de los puntos de entrada públicos se utilizó un entorno virtual de Python (`.venv`) con Jobsy instalado en modo editable.

### Entorno de ejecución del PR #114

Las pruebas del PR #114 fueron ejecutadas en:

- Windows 11 como sistema host.
- Ubuntu 26.04.1 LTS mediante WSL2.
- Arquitectura x86_64.
- Linux kernel `6.18.33.2-microsoft-standard-WSL2`.
- Python 3.14.4.
- Git 2.53.0.
- Repositorio ubicado en `/mnt/e/Alexia/Sistemas Avanzados/Jobsy`.
- Entorno virtual de Python (`.venv`) con Jobsy instalado para las pruebas.

### Entorno de ejecución del PR #116

Las pruebas del PR #116 fueron ejecutadas en:

- Windows 11 como sistema host.
- Ubuntu 26.04.1 LTS mediante WSL2.
- Arquitectura x86_64.
- Linux kernel `6.18.33.2-microsoft-standard-WSL2`.
- Python 3.14.4.
- Git 2.53.0.
- Repositorio ubicado en `/mnt/e/Alexia/Sistemas Avanzados/Jobsy`.
- Entorno virtual de Python (`.venv`) con Jobsy instalado para las pruebas.

## Estados

Cada caso puede encontrarse en uno de los siguientes estados:

- `PASS`: el resultado obtenido coincide con el resultado esperado.
- `FAIL`: el resultado obtenido no coincide con el resultado esperado.
- `BLOCKED`: la prueba no pudo ejecutarse.
- `PENDING`: la prueba todavía no ha sido ejecutada.

## Evidencias asociadas

- `EV-001-validation-output.txt`: salida de `test_validation.py`.
- `EV-002-executor-output.txt`: salida de `test_executor.py`.
- `EV-003-job-manager-output.txt`: salida de `test_job_manager.py`.
- `EV-004-cancellation-output.txt`: pruebas de cancelación del RF-10.
- `EV-005-service-shutdown-output.txt`: pruebas de inicio y apagado controlado del RF-15.
- `EV-006-cli-output.txt`: pruebas de ayuda, comandos y códigos de salida del RF-17.
- `EV-007-ipc-flow-output.txt`: salida de `test_ipc_flow.py`.
- `EV-008-ipc-robustness-output.txt`: salida de `test_ipc_robustness.py`.
- `EV-009-ipc-multiple-jobs-output.txt`: salida de `test_ipc_multiple_jobs.py`.
- `EV-010-socket-config-output.txt`: configuración, validación e integración básica del socket UNIX configurable.
- `EV-011-socket-cli-contract-output.txt`: contrato público de CLI, variable `JOBSY_SOCKET_PATH`, códigos de salida y puntos de entrada.
- `EV-012-output-behavior-output.txt`: separación de `stdout` y `stderr`, integridad de salidas mayores a 4096 bytes y código de salida del comando `output`.
- `EV-013-process-group-cancellation-output.txt`: creación de grupos/sesiones de procesos y cancelación completa de procesos padre e hijos.
- `EV-014-repeated-cancellation-output.txt`: comportamiento de la primera y segunda solicitud de cancelación sobre un mismo trabajo.
- `EV-015-cancel-grace-output.txt`: validación de `--cancel-grace`, rechazo de valores fuera de rango y escalamiento de `SIGTERM` a `SIGKILL`.
- `EV-016-cleanup-isolation-output.txt`: aislamiento de fallos de cleanup sin bloquear el scheduler ni el servicio.
- `EV-017-duplicate-requests-output.txt`: validación de solicitudes duplicadas y semántica de RF-27.
- `EV-018-health-summary-output.txt`: validación del resumen de salud `health` de RF-24.
- `EV-019-structured-errors-output.txt`: validación de errores estructurados y sugerencias operativas de RNF-21 / RF-28.
- `EV-020-request-logging-output.txt`: validación de bitácora, Job ID y correlación mediante `ReqID` de RF-14 / RNF-22.
- `EV-021-queue-observability-output.txt`: validación de robustez, observabilidad de cola y desconexiones del cliente.
- `EV-022-recovery-behavior-output.txt`: validación de recuperación de trabajos terminales, pendientes e interrumpidos.
- `EV-023-resource-stress-output.txt`: estrés y liberación de memoria, procesos, archivos y sockets.
- `EV-024-clean-installation-output.txt`: clon limpio, instalación sin root, sin sudo y sin warnings.
- `EV-025-single-command-suite-output.txt`: batería consolidada de QA ejecutable mediante un único comando.

- EV-026 y EV-027: IDs cortos y regresión del PR #133.

### Avance 3

- `EV-028-network-protocol-v1-output.txt`: PR #135.
- `EV-029-remote-server-config-output.txt`: PR #135.
- `EV-030-remote-cli-output.txt`: PR #135.
- `EV-031-remote-security-output.txt`: PR #135.
- `EV-032-remote-concurrency-output.txt`: PR #135.
- `EV-033-remote-performance-output.txt`: PR #135.
- `EV-034-remote-lan-output.txt`: PR #135.
- `EV-035-regression-output.txt`: PR #135.
- `EV-030-INC-002-reproduction.txt`: reproducción complementaria.
- `EV-034-remote-lan-daemon.txt`: bitácora original respaldada.

### Avance 1

- EV-001 a EV-009: evidencias correspondientes a las pruebas del Avance 1.

### Avance 2

- `EV-010-socket-config-output.txt`: configuración, validación e integración básica del socket UNIX configurable.
- `EV-011-socket-cli-contract-output.txt`: contrato público de CLI, variable `JOBSY_SOCKET_PATH`, códigos de salida y puntos de entrada.
- `EV-012-output-behavior-output.txt`: separación e integridad de stdout/stderr.
- `EV-013-process-group-cancellation-output.txt`: grupos de procesos y cancelación completa.
- `EV-014-repeated-cancellation-output.txt`: cancelación repetida.
- `EV-015-cancel-grace-output.txt`: período de gracia configurable y escalamiento a SIGKILL.
- `EV-016-cleanup-isolation-output.txt`: aislamiento de fallos de cleanup.
- `EV-017-duplicate-requests-output.txt`: solicitudes duplicadas.
- `EV-018-health-summary-output.txt`: resumen de salud.
- `EV-019-structured-errors-output.txt`: errores estructurados y sugerencias operativas.
- `EV-020-request-logging-output.txt`: bitácora y correlación mediante ReqID.
- `EV-021-queue-observability-output.txt`: robustez y observabilidad de cola.
- `EV-022-recovery-behavior-output.txt`: recuperación de trabajos tras reinicio/interrupción.
- `EV-023-resource-stress-output.txt`: estrés y liberación de recursos.
- `EV-024-clean-installation-output.txt`: instalación limpia y sin privilegios root.
- `EV-025-single-command-suite-output.txt`: batería unificada de QA mediante un único comando.

---

## Plantilla

### TC-XXX — Nombre del caso

**Requisito relacionado:**
**Tipo:**
**Prioridad:**

#### Objetivo

Descripción del comportamiento que se desea verificar.

#### Precondiciones

- ...

#### Datos de prueba

```text
TC-001
TC-002
TC-003
...

---


## TC-001 — Validar comando correcto

**Tipo:** Funcional
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que el módulo de validación acepte un comando con formato válido.

### Datos de prueba
```python
["echo", "Hola"]
```

### Procedimiento
1. Ejecutar `test_validation.py`.
2. Enviar el comando al módulo de validación.
3. Observar el resultado.

### Resultado esperado
El comando debe ser aceptado.

### Resultado obtenido
```text
ACEPTADO: ['echo', 'Hola']
```

### Evidencia
`EV-001-validation-output.txt`

---

## TC-002 — Rechazar comando vacío

**Tipo:** Negativa
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que Jobsy rechace una lista de comando vacía.

### Datos de prueba
```python
[]
```

### Resultado esperado
El comando debe ser rechazado indicando que no puede estar vacío.

### Resultado obtenido
```text
RECHAZADO: []
Motivo: El comando no puede estar vacio.
```

### Evidencia
`EV-001-validation-output.txt`

---

## TC-003 — Rechazar comando con formato incorrecto

**Tipo:** Negativa
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que Jobsy rechace un comando que no sea enviado como una lista.

### Resultado esperado
La entrada debe ser rechazada indicando que el comando debe enviarse como una lista.

### Resultado obtenido
```text
RECHAZADO:
Motivo: El comando debe enviarse como una lista.
```

### Evidencia
`EV-001-validation-output.txt`

---

## TC-004 — Rechazar nombre de programa vacío

**Tipo:** Negativa
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que Jobsy rechace un comando cuyo nombre de programa esté vacío.

### Datos de prueba
```python
["", "10"]
```

### Resultado esperado
El comando debe ser rechazado.

### Resultado obtenido
```text
RECHAZADO: ['', '10']
Motivo: El nombre del programa no puede estar vacio.
```

### Evidencia
`EV-001-validation-output.txt`

---

## TC-005 — Rechazar argumentos no textuales

**Tipo:** Negativa
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que Jobsy rechace comandos cuyos argumentos no sean texto.

### Datos de prueba
```python
["sleep", 10]
```

### Resultado esperado
El comando debe ser rechazado.

### Resultado obtenido
```text
RECHAZADO: ['sleep', 10]
Motivo: El comando y sus argumentos deben ser texto.
```

### Evidencia
`EV-001-validation-output.txt`

---

## TC-006 — Generar IDs únicos

**Tipo:** Funcional
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que Jobsy asigne identificadores diferentes a trabajos distintos.

### Datos de prueba
```python
["sleep", "10"]
["echo", "Hola desde Jobsy"]
["ls", "/carpeta-que-no-existe"]
```

### Resultado esperado
Cada trabajo debe recibir un identificador no vacío y diferente.

### Resultado obtenido
```text
ab33bbbe-b03e-47d0-81b2-1476b5348c97
297b82f7-8599-40ba-be76-b470ebd45f40
82f6add0-14d4-43c0-9bdc-106dcae628b8
```

Los tres identificadores fueron diferentes.

### Evidencia
`EV-002-executor-output.txt`

---

## TC-007 — Ejecutar trabajo sin bloquear otros trabajos

**Tipo:** Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que un trabajo de larga duración no impida que otro trabajo finalice.

### Datos de prueba
```python
["sleep", "10"]
["echo", "Hola desde Jobsy"]
```

### Resultado esperado
Mientras `sleep 10` permanezca en ejecución, el trabajo `echo` debe poder finalizar.

### Resultado obtenido
```text
sleep 10 -> RUNNING
echo -> SUCCEEDED
```

### Evidencia
`EV-002-executor-output.txt`

---

## TC-008 — Ejecutar trabajo exitosamente

**Tipo:** Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que un trabajo válido pueda ejecutarse y finalizar correctamente.

### Datos de prueba
```python
["echo", "Hola desde Jobsy"]
```

### Resultado esperado
El trabajo debe finalizar en estado `SUCCEEDED`.

### Resultado obtenido
```text
status='SUCCEEDED'
```

### Evidencia
`EV-002-executor-output.txt`

---

## TC-009 — Capturar stdout

**Tipo:** Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que Jobsy capture correctamente la salida estándar.

### Datos de prueba
```python
["echo", "Hola desde Jobsy"]
```

### Resultado esperado
`stdout` debe contener la salida generada por `echo`.

### Resultado obtenido
```text
stdout='Hola desde Jobsy\n'
```

### Evidencia
`EV-002-executor-output.txt`

---

## TC-010 — Registrar código de salida exitoso

**Tipo:** Funcional / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que Jobsy registre el código de salida de un trabajo exitoso.

### Resultado esperado
El código de salida debe ser `0`.

### Resultado obtenido
```text
exit_code=0
status='SUCCEEDED'
```

### Evidencia
`EV-002-executor-output.txt`

---

## TC-011 — Ejecutar trabajo que termina con error

**Tipo:** Negativa / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que Jobsy detecte un proceso que se ejecuta pero termina con error.

### Datos de prueba
```python
["ls", "/carpeta-que-no-existe"]
```

### Resultado esperado
El trabajo debe finalizar con código distinto de cero y estado `FAILED`.

### Resultado obtenido
```text
status='FAILED'
exit_code=2
```

### Evidencia
`EV-002-executor-output.txt`

---

## TC-012 — Capturar stderr

**Tipo:** Negativa / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que Jobsy capture correctamente la salida de error.

### Datos de prueba
```python
["ls", "/carpeta-que-no-existe"]
```

### Resultado esperado
`stderr` debe contener el mensaje de error generado por `ls`.

### Resultado obtenido
```text
stderr="ls: cannot access '/carpeta-que-no-existe': No such file or directory\n"
```

### Evidencia
`EV-002-executor-output.txt`

---

## TC-013 — Registrar código de salida de error

**Tipo:** Funcional / Negativa
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que Jobsy conserve el código de salida de un proceso fallido.

### Resultado esperado
El código de salida debe ser distinto de `0`.

### Resultado obtenido
```text
exit_code=2
```

### Evidencia
`EV-002-executor-output.txt`

---

## TC-014 — Registrar tiempos del ciclo de vida

**Tipo:** Funcional / Integración
**Prioridad:** Media
**Estado:** `PASS`

### Objetivo
Verificar que Jobsy registre marcas de tiempo coherentes durante el ciclo de vida de un trabajo.

### Datos de prueba
```python
["sleep", "10"]
```

### Resultado esperado
Debe cumplirse:

```text
received_at <= started_at <= finished_at
```

La duración debe ser aproximadamente de 10 segundos.

### Resultado obtenido
```text
received_at = 2026-10-02 05:14:53.104571+00:00
started_at  = 2026-10-02 05:14:53.104833+00:00
finished_at = 2026-10-02 05:15:03.106709+00:00
```

Se cumplió el orden temporal esperado y la duración fue aproximadamente de 10 segundos.

### Evidencia
`EV-002-executor-output.txt`

---


## TC-015 — Consultar trabajo con ID válido

**Tipo:** Funcional
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que Jobsy permita recuperar correctamente un trabajo existente mediante su identificador.

### Datos de prueba
```python
["echo", "Hola"]
```

ID utilizado:

```text
1a995a13-4442-4629-a915-49d64f0faf93
```

### Resultado esperado
El sistema debe recuperar el trabajo correspondiente al ID proporcionado.

Debe cumplirse:

```text
ID encontrado = ID buscado
Comando = ['echo', 'Hola']
Estado = QUEUED
```

### Resultado obtenido
```text
ID buscado: 1a995a13-4442-4629-a915-49d64f0faf93
ID encontrado: 1a995a13-4442-4629-a915-49d64f0faf93
Comando: ['echo', 'Hola']
Estado: QUEUED
```

El trabajo fue recuperado correctamente y la información obtenida coincidió con los datos esperados.

### Evidencia
`EV-003-job-manager-output.txt`

---

## TC-016 — Consultar trabajo con ID inexistente

**Tipo:** Negativa / Funcional
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que Jobsy rechace de forma controlada la consulta de un identificador que no corresponde a ningún trabajo registrado.

### Datos de prueba
```text
id-que-no-existe
```

### Resultado esperado
El sistema debe rechazar la consulta del ID inexistente y mostrar un error controlado indicando que el trabajo no existe.

### Resultado obtenido
```text
CORRECTO: se rechazó el ID inexistente
Motivo: No existe un trabajo con el ID 'id-que-no-existe'.
```

El sistema rechazó correctamente el identificador inexistente y reportó el motivo esperado.

### Evidencia
`EV-003-job-manager-output.txt`

---

## TC-017 — Listar trabajos y filtrar por estado

**Tipo:** Funcional / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que Jobsy permita listar los trabajos registrados, filtrarlos por un estado válido y rechazar un estado de filtro inválido.

### Datos de prueba
Trabajos creados:

```python
["echo", "Hola"]
["sleep", "1"]
```

Filtro válido:

```text
QUEUED
```

Filtro inválido:

```text
ESTADO_INEXISTENTE
```

### Resultado esperado
Sin filtro, el sistema debe devolver los dos trabajos registrados.

Al filtrar por `QUEUED`, debe devolver los dos trabajos en ese estado.

Al utilizar un estado inexistente, el sistema debe rechazar el filtro de forma controlada.

### Resultado obtenido
Listado sin filtro:

```text
Cantidad: 2
1a995a13-4442-4629-a915-49d64f0faf93 ['echo', 'Hola'] QUEUED
989a2eae-45d2-4d1a-8919-6549dba80cb5 ['sleep', '1'] QUEUED
```

Listado filtrando por `QUEUED`:

```text
Cantidad: 2
1a995a13-4442-4629-a915-49d64f0faf93 ['echo', 'Hola'] QUEUED
989a2eae-45d2-4d1a-8919-6549dba80cb5 ['sleep', '1'] QUEUED
```

Prueba con estado inválido:

```text
CORRECTO: se rechazó el estado inválido
Motivo: Estado no valido: 'ESTADO_INEXISTENTE'.
```

El listado general, el filtro por estado `QUEUED` y el rechazo del estado inválido funcionaron correctamente.

### Evidencia
`EV-003-job-manager-output.txt`

---

# Casos de prueba — PR #102

## RF-10 — Cancelación de trabajos — Issue #37

## TC-018 — Cancelar trabajo en estado QUEUED

**Requisito relacionado:** RF-10 — Issue #37
**Tipo:** Funcional / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que un trabajo en estado `QUEUED` pueda cancelarse antes de iniciar su ejecución.

### Datos de prueba
```python
["echo", "Trabajo en cola"]
```

### Resultado esperado
El trabajo debe cambiar de `QUEUED` a `CANCELED` y registrar `finished_at`.

### Resultado obtenido
```text
Estado antes: QUEUED
Estado después: CANCELED
finished_at: registrado
PASS: El trabajo QUEUED cambia a CANCELED.
PASS: El trabajo cancelado registra finished_at.
```

### Evidencia
`EV-004-cancellation-output.txt`

---

## TC-019 — Cancelar trabajo en estado RUNNING

**Requisito relacionado:** RF-10 — Issue #37
**Tipo:** Funcional / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que Jobsy cancele un trabajo en ejecución y termine el proceso Linux asociado sin sobrescribir el estado `CANCELED`.

### Datos de prueba
```python
["sleep", "10"]
```

### Resultado esperado
El trabajo debe alcanzar `RUNNING`, tener un PID asociado, cambiar a `CANCELED`, terminar su proceso Linux, registrar `finished_at` y limpiar la referencia al proceso.

### Resultado obtenido
```text
Proceso iniciado: True
Estado antes de cancelar: RUNNING
PID: 2791
Estado después: CANCELED
PASS: El trabajo alcanza RUNNING y tiene un proceso Linux asociado.
PASS: El trabajo RUNNING cambia a CANCELED.
PASS: El trabajo cancelado registra finished_at.
PASS: El proceso Linux asociado termina después de la cancelación.
PASS: Executor limpia la referencia al proceso.
PASS: Executor conserva el estado CANCELED al terminar el proceso.
```

### Evidencia
`EV-004-cancellation-output.txt`

---

## TC-020 — Cancelar trabajo con ID inexistente

**Requisito relacionado:** RF-10 — Issue #37
**Tipo:** Negativa / Funcional
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que Jobsy rechace de forma controlada la cancelación de un ID inexistente.

### Datos de prueba
```text
id-que-no-existe
```

### Resultado esperado
La operación debe ser rechazada mediante un error controlado.

### Resultado obtenido
```text
Error controlado: No existe un trabajo con el ID 'id-que-no-existe'.
PASS: Se rechaza la cancelación de un ID inexistente.
```

### Evidencia
`EV-004-cancellation-output.txt`

---

## TC-021 — Intentar cancelar un trabajo finalizado

**Requisito relacionado:** RF-10 — Issue #37
**Tipo:** Negativa / Funcional
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que no sea posible cancelar un trabajo que ya terminó correctamente.

### Datos de prueba
```python
["echo", "Trabajo finalizado"]
```

### Resultado esperado
El trabajo debe finalizar en `SUCCEEDED` y el intento posterior de cancelación debe ser rechazado.

### Resultado obtenido
```text
Estado antes de cancelar: SUCCEEDED
Error controlado: No se puede cancelar un trabajo con estado 'SUCCEEDED'.
PASS: El trabajo finaliza correctamente antes de intentar cancelarlo.
PASS: Se rechaza la cancelación de un trabajo finalizado.
```

### Evidencia
`EV-004-cancellation-output.txt`

---

## TC-022 — Intentar cancelar el mismo trabajo dos veces

**Requisito relacionado:** RF-10 — Issue #37
**Tipo:** Negativa / Funcional
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que una segunda solicitud de cancelación sobre un trabajo ya `CANCELED` sea rechazada.

### Resultado esperado
La primera cancelación debe dejar el trabajo en `CANCELED` y la segunda debe generar un error controlado.

### Resultado obtenido
```text
Error controlado: No se puede cancelar un trabajo con estado 'CANCELED'.
PASS: La primera cancelación deja el trabajo en CANCELED.
PASS: La segunda cancelación es rechazada.
```

### Evidencia
`EV-004-cancellation-output.txt`

---

## RF-15 — Inicio y apagado controlado del servicio — Issue #38

## TC-023 — Inicializar servicio

**Requisito relacionado:** RF-15 — Issue #38
**Tipo:** Funcional / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar el estado inicial de `DaemonServer` y `JobManager`.

### Resultado esperado
El servidor debe iniciar con `is_running=True` y el administrador debe aceptar trabajos.

### Resultado obtenido
```text
Host: 127.0.0.1
Puerto: 9999
is_running: True
Aceptando trabajos: True
PASS: El servicio inicia con is_running=True.
PASS: JobManager acepta trabajos al iniciar el servicio.
```

### Evidencia
`EV-005-service-shutdown-output.txt`

---

## TC-024 — Apagado con trabajo en QUEUED

**Requisito relacionado:** RF-15 — Issue #38
**Tipo:** Funcional / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que el apagado controlado cancele trabajos pendientes y detenga la aceptación de nuevos trabajos.

### Resultado esperado
El trabajo debe quedar `CANCELED`, el servidor debe marcarse detenido, `is_accepting_jobs` debe ser `False` y el cierre debe terminar con código `0`.

### Resultado obtenido
```text
Estado antes: QUEUED
Estado después: CANCELED
Servidor activo: False
Aceptando trabajos: False
Exit code: 0
```

Todas las comprobaciones asociadas obtuvieron `PASS`.

### Evidencia
`EV-005-service-shutdown-output.txt`

---

## TC-025 — Apagado con trabajo RUNNING de corta duración

**Requisito relacionado:** RF-15 — Issue #38
**Tipo:** Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que un trabajo corto en ejecución pueda finalizar normalmente durante la ventana de apagado.

### Datos de prueba
```python
["sleep", "1"]
```

### Resultado esperado
El trabajo debe terminar en `SUCCEEDED`, el proceso Linux debe finalizar y el servicio debe dejar de aceptar trabajos.

### Resultado obtenido
```text
Proceso iniciado: True
Estado antes del shutdown: RUNNING
Estado después: SUCCEEDED
Duración del shutdown: aproximadamente 1 segundo
Exit code: 0
```

Todas las comprobaciones asociadas obtuvieron `PASS`.

### Evidencia
`EV-005-service-shutdown-output.txt`

---

## TC-026 — Rechazar nuevos trabajos después del shutdown

**Requisito relacionado:** RF-15 — Issue #38
**Tipo:** Negativa / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que el sistema no acepte nuevos trabajos una vez iniciado/completado el apagado controlado.

### Resultado esperado
`JobManager.create_job()` debe rechazar nuevos trabajos mediante un error controlado.

### Resultado obtenido
```text
Error controlado: El JobManager no esta aceptando nuevos trabajos.
PASS: Se rechazan nuevos trabajos después de iniciar el shutdown.
```

### Evidencia
`EV-005-service-shutdown-output.txt`

---

## TC-027 — Procesar señal de apagado

**Requisito relacionado:** RF-15 — Issue #38
**Tipo:** Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que una señal de terminación active el apagado controlado.

### Datos de prueba
```text
SIGTERM
```

### Resultado esperado
La señal debe detener el servidor, deshabilitar la recepción de nuevos trabajos y finalizar con código `0`.

### Resultado obtenido
```text
[Daemon] Señal de apagado recibida...
Servidor activo: False
Aceptando trabajos: False
Exit code: 0
```

Todas las comprobaciones asociadas obtuvieron `PASS`.

### Evidencia
`EV-005-service-shutdown-output.txt`

---

## TC-028 — Forzar cancelación por timeout de shutdown

**Requisito relacionado:** RF-15 — Issue #38; RNF-25 — Issue #28; RNF-30 — Issue #29
**Tipo:** Integración / Robustez
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que un trabajo que continúa `RUNNING` después del timeout sea cancelado y que su proceso hijo no quede ejecutándose.

### Datos de prueba
```python
["sleep", "10"]
```

Timeout de prueba:

```text
0.5 segundos
```

### Resultado esperado
Al exceder el timeout, el trabajo debe finalizar en `CANCELED`, su proceso Linux debe terminar, `finished_at` debe registrarse y el administrador debe seguir rechazando nuevos trabajos.

### Resultado obtenido
La ejecución cumplió todas las comprobaciones esperadas y finalizó en `PASS`.

### Evidencia
`EV-005-service-shutdown-output.txt`

---

## RF-17 — Ayuda y códigos de salida del cliente — Issue #39

## TC-029 — Mostrar ayuda sin argumentos

**Requisito relacionado:** RF-17 — Issue #39
**Tipo:** Funcional
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que la CLI muestre ayuda cuando se ejecuta sin subcomandos y termine con código de uso inválido.

### Resultado esperado
Debe mostrar la ayuda de `jobsy` y finalizar con código `2`.

### Resultado obtenido
```text
Exit code: 2
usage: jobsy [-h] {run,list,status,cancel} ...
PASS: La CLI termina con codigo 2 cuando no recibe argumentos.
PASS: La CLI muestra informacion de ayuda.
```

### Evidencia
`EV-006-cli-output.txt`

---

## TC-030 — Ejecutar comando válido desde la CLI

**Requisito relacionado:** RF-01 — Issue #30; RF-17 — Issue #39
**Tipo:** Funcional / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que `jobsy run` cree un trabajo válido y termine con código `0`.

### Datos de prueba
```text
jobsy run echo "Hola desde CLI"
```

### Resultado esperado
La CLI debe crear un trabajo, conservar el comando solicitado, informar su ID y terminar con código `0`.

### Resultado obtenido
Todas las comprobaciones asociadas obtuvieron `PASS`.

### Evidencia
`EV-006-cli-output.txt`

---

## TC-031 — Listar trabajos desde la CLI

**Requisito relacionado:** RF-09 — Issue #36; RF-17 — Issue #39
**Tipo:** Funcional / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que `jobsy list` muestre los trabajos registrados y su estado.

### Resultado esperado
La CLI debe listar ambos trabajos y terminar con código `0`.

### Resultado obtenido
Los dos IDs creados y sus estados fueron mostrados correctamente; el comando terminó con código `0`.

### Evidencia
`EV-006-cli-output.txt`

---

## TC-032 — Consultar estado desde la CLI

**Requisito relacionado:** RF-08 — Issue #35; RF-17 — Issue #39
**Tipo:** Funcional / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que `jobsy status <ID>` muestre los metadatos del trabajo solicitado.

### Resultado esperado
Debe mostrar ID, estado, comando y marcas de tiempo disponibles, terminando con código `0`.

### Resultado obtenido
La CLI mostró el ID correcto, estado `QUEUED`, comando asociado y metadatos esperados.

### Evidencia
`EV-006-cli-output.txt`

---

## TC-033 — Cancelar trabajo desde la CLI

**Requisito relacionado:** RF-10 — Issue #37; RF-17 — Issue #39
**Tipo:** Funcional / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar la integración del comando `cancel` de la CLI con `JobManager.cancel_job()`.

### Resultado esperado
El trabajo debe quedar en `CANCELED`, la CLI debe informarlo y terminar con código `0`.

### Resultado obtenido
```text
Exit code: 0
Estado actual: CANCELED
Estado final: CANCELED
```

Todas las comprobaciones asociadas obtuvieron `PASS`.

### Evidencia
`EV-006-cli-output.txt`

---

## TC-034 — Consultar ID inexistente desde la CLI

**Requisito relacionado:** RF-08 — Issue #35; RF-17 — Issue #39
**Tipo:** Negativa / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que la CLI maneje de forma controlada la consulta de un ID inexistente.

### Resultado esperado
Debe escribir el error en `stderr` y terminar con código `1`.

### Resultado obtenido
```text
Exit code: 1
STDERR: Error de validación: No existe un trabajo con el ID 'id-que-no-existe'.
```

### Evidencia
`EV-006-cli-output.txt`

---

## TC-035 — Rechazar filtro de estado inválido en la CLI

**Requisito relacionado:** RF-09 — Issue #36; RF-17 — Issue #39
**Tipo:** Negativa / Funcional
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que `argparse` rechace un valor no permitido para `--status`.

### Datos de prueba
```text
ESTADO_INVALIDO
```

### Resultado esperado
La CLI debe terminar con código `2` y reportar `invalid choice` en `stderr`.

### Resultado obtenido
La CLI terminó con código `2` y `argparse` informó correctamente el valor inválido.

### Evidencia
`EV-006-cli-output.txt`

---

## TC-036 — Rechazar subcomando inexistente

**Requisito relacionado:** RF-17 — Issue #39
**Tipo:** Negativa / Funcional
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que la CLI rechace un subcomando inexistente.

### Datos de prueba
```text
comando-inexistente
```

### Resultado esperado
La CLI debe terminar con código `2` y reportar `invalid choice` en `stderr`.

### Resultado obtenido
La CLI terminó con código `2` e informó correctamente que el subcomando era inválido.

### Evidencia
`EV-006-cli-output.txt`

---

## TC-037 — Iniciar daemon y crear socket UNIX

**Tipo:** Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que el daemon de Jobsy pueda iniciar correctamente, mantenerse en ejecución y crear el socket UNIX utilizado para la comunicación con la CLI.

### Datos de prueba
```text
Socket: /tmp/jobsy.sock
```

### Resultado esperado
El daemon debe permanecer activo después de iniciar y crear el socket `/tmp/jobsy.sock`.

### Resultado obtenido
```text
Socket creado: True
Ruta: /tmp/jobsy.sock
PASS: El daemon permanece en ejecucion.
PASS: El daemon crea el socket UNIX.
```

### Evidencia
`EV-007-ipc-flow-output.txt`

---

## TC-038 — Enviar trabajo mediante CLI e IPC

**Tipo:** Funcional / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que la CLI pueda enviar un trabajo al daemon mediante el mecanismo IPC y recibir el identificador asignado.

### Datos de prueba
```text
echo Hola desde IPC
```

### Resultado esperado
La CLI debe terminar con código `0` y recibir un identificador válido para el trabajo creado.

### Resultado obtenido
```text
Exit code: 0
Trabajo creado y enviado a ejecución con ID: <UUID>
PASS: La CLI termina con codigo 0 al enviar un trabajo.
PASS: El daemon devuelve un identificador de trabajo.
```

### Evidencia
`EV-007-ipc-flow-output.txt`

---

## TC-039 — Consultar trabajo mediante IPC

**Tipo:** Funcional / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que un trabajo creado mediante una ejecución de la CLI pueda consultarse posteriormente mediante otra solicitud al daemon.

### Datos de prueba
```text
echo Hola desde IPC
```

### Resultado esperado
La consulta debe devolver el mismo trabajo con estado `SUCCEEDED`, comando correcto y código de salida `0`.

### Resultado obtenido
```text
Estado: SUCCEEDED
Comando: echo Hola desde IPC
Código de salida: 0

PASS: El trabajo puede consultarse desde otra invocacion de la CLI.
PASS: La consulta conserva el codigo de salida del trabajo.
PASS: La consulta conserva el comando asociado.
```

### Evidencia
`EV-007-ipc-flow-output.txt`

---

## TC-040 — Listar trabajos persistentes durante la sesión

**Tipo:** Funcional / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que los trabajos creados mediante la CLI permanezcan registrados en el daemon durante la misma sesión del servicio.

### Resultado esperado
Una nueva ejecución de `list` debe mostrar el trabajo creado previamente mediante otra invocación de la CLI.

### Resultado obtenido
```text
Exit code: 0
ID: <UUID> | Estado: SUCCEEDED | Comando: echo Hola desde IPC

PASS: El comando list termina con codigo 0.
PASS: El listado conserva el trabajo creado por una invocacion anterior.
```

### Evidencia
`EV-007-ipc-flow-output.txt`

---

## TC-041 — Cancelar trabajo mediante IPC

**Tipo:** Funcional / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que un trabajo en ejecución pueda cancelarse mediante una solicitud enviada desde la CLI al daemon.

### Datos de prueba
```text
sleep 10
```

### Resultado esperado
La operación `cancel` debe terminar con código `0` y una consulta posterior debe mostrar el trabajo en estado `CANCELED`.

### Resultado obtenido
```text
Exit code cancel: 0
Estado actual: CANCELED

Estado: CANCELED
Comando: sleep 10

PASS: La orden cancel mediante IPC termina con codigo 0.
PASS: El estado consultado posteriormente es CANCELED.
```

### Evidencia
`EV-007-ipc-flow-output.txt`

---

## TC-042 — Consultar ID inexistente mediante IPC

**Tipo:** Negativa / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que la consulta mediante IPC de un identificador inexistente sea rechazada de forma controlada.

### Datos de prueba
```text
id-que-no-existe
```

### Resultado esperado
La CLI debe finalizar con código `1` e informar que el trabajo solicitado no existe.

### Resultado obtenido
```text
Exit code: 1
Error de validación: No existe un trabajo con el ID 'id-que-no-existe'.

PASS: La consulta de un ID inexistente termina con codigo 1.
PASS: La CLI informa de forma controlada que el trabajo no existe.
```

### Evidencia
`EV-007-ipc-flow-output.txt`

---

## TC-043 — Ejecutar CLI sin daemon activo

**Tipo:** Negativa / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que la CLI detecte de forma controlada cuando el servicio Jobsy no se encuentra en ejecución.

### Datos de prueba
```text
list
Daemon detenido
```

### Resultado esperado
La CLI debe terminar con código `1` e indicar que el servicio Jobsy no está en ejecución.

### Resultado obtenido
```text
Exit code: 1
Error: El servicio Jobsy no está en ejecución.

PASS: La CLI termina con codigo 1 cuando el daemon no esta activo.
PASS: La CLI informa que el servicio Jobsy no esta en ejecucion.
```

### Evidencia
`EV-008-ipc-robustness-output.txt`

---

## TC-044 — Cancelar ID inexistente mediante IPC

**Tipo:** Negativa / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que Jobsy rechace de forma controlada una solicitud de cancelación para un trabajo inexistente.

### Datos de prueba
```text
id-que-no-existe
```

### Resultado esperado
La CLI debe terminar con código `1` e informar que el trabajo no existe.

### Resultado obtenido
```text
Exit code: 1
Error de validación: No existe un trabajo con el ID 'id-que-no-existe'.

PASS: Cancelar un ID inexistente termina con codigo 1.
PASS: La CLI informa que el trabajo no existe.
```

### Evidencia
`EV-008-ipc-robustness-output.txt`

---

## TC-045 — Filtrar trabajos por estado mediante IPC

**Tipo:** Funcional / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que el listado de trabajos pueda filtrarse correctamente por estado a través de la comunicación entre la CLI y el daemon.

### Datos de prueba
```text
Trabajo exitoso:
echo Filtro IPC

Trabajo fallido:
ls /directorio_inexistente_qa_123

Filtros:
SUCCEEDED
FAILED
```

### Resultado esperado
El filtro `SUCCEEDED` debe mostrar únicamente trabajos exitosos y el filtro `FAILED` únicamente trabajos fallidos.

### Resultado obtenido
```text
Filtro SUCCEEDED:
Estado: SUCCEEDED

PASS: El filtro SUCCEEDED termina con codigo 0.
PASS: El listado filtrado contiene trabajos SUCCEEDED.
PASS: El filtro SUCCEEDED no muestra trabajos FAILED.

Filtro FAILED:
Estado: FAILED

PASS: El filtro FAILED termina con codigo 0.
PASS: El listado filtrado contiene trabajos FAILED.
PASS: El filtro FAILED no muestra trabajos SUCCEEDED.
```

### Evidencia
`EV-008-ipc-robustness-output.txt`

---

## TC-046 — Enviar acción IPC inválida

**Tipo:** Negativa / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que el daemon rechace de forma controlada una acción IPC que no se encuentre soportada.

### Datos de prueba
```json
{
  "action": "accion_invalida"
}
```

### Resultado esperado
El daemon debe responder con estado de error e indicar que la acción no es válida.

### Resultado obtenido
```text
Respuesta: {'status': 'error', 'message': 'Acción no válida'}

PASS: El daemon responde con status error.
PASS: El daemon informa que la accion no es valida.
```

### Evidencia
`EV-008-ipc-robustness-output.txt`

---

## TC-047 — Enviar JSON inválido

**Tipo:** Negativa / Robustez
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que el daemon maneje de forma controlada una petición con formato JSON incorrecto.

### Datos de prueba
```text
{esto no es json valido
```

### Resultado esperado
El daemon debe responder con un error controlado sin finalizar el servicio.

### Resultado obtenido
```text
Respuesta: {
  'status': 'error',
  'message': 'Expecting property name enclosed in double quotes: line 1 column 2 (char 1)'
}

PASS: El daemon responde de forma controlada ante JSON invalido.
PASS: La respuesta contiene un mensaje de error.
```

### Evidencia
`EV-008-ipc-robustness-output.txt`

---

## TC-048 — Mantener daemon operativo después de solicitudes inválidas

**Tipo:** Robustez / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que una acción IPC inválida o una petición JSON incorrecta no provoquen la terminación del daemon.

### Resultado esperado
Después de procesar solicitudes inválidas, el daemon debe continuar activo y aceptar nuevas solicitudes válidas.

### Resultado obtenido
```text
Exit code: 0

PASS: El daemon sigue respondiendo despues de solicitudes invalidas.
PASS: El proceso del daemon sigue activo.
```

### Evidencia
`EV-008-ipc-robustness-output.txt`

---

## TC-049 — Eliminar socket durante el apagado del daemon

**Tipo:** Integración / Robustez
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que el socket UNIX utilizado por Jobsy sea eliminado durante el apagado controlado del daemon.

### Datos de prueba
```text
/tmp/jobsy.sock
SIGTERM
```

### Resultado esperado
El socket debe existir mientras el daemon está en ejecución y dejar de existir después del apagado.

### Resultado obtenido
```text
Socket antes del shutdown: True
Socket despues del shutdown: False

PASS: El socket existia antes de apagar el daemon.
PASS: El socket fue eliminado durante el apagado del daemon.
```

### Evidencia
`EV-008-ipc-robustness-output.txt`

---

## TC-050 — Ejecutar múltiples trabajos mediante IPC

**Tipo:** Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que el daemon pueda aceptar múltiples trabajos consecutivos enviados mediante distintas solicitudes de la CLI.

### Datos de prueba
```text
echo Trabajo 1
echo Trabajo 2
echo Trabajo 3
true
false
```

### Resultado esperado
Las cinco solicitudes deben ser aceptadas correctamente y cada trabajo debe recibir un identificador.

### Resultado obtenido
```text
echo Trabajo 1 -> Exit code CLI: 0
echo Trabajo 2 -> Exit code CLI: 0
echo Trabajo 3 -> Exit code CLI: 0
true -> Exit code CLI: 0
false -> Exit code CLI: 0

PASS: Todos los trabajos enviados recibieron un ID.
```

Los cinco trabajos fueron aceptados por el daemon.

### Evidencia
`EV-009-ipc-multiple-jobs-output.txt`

---

## TC-051 — Verificar IDs únicos en múltiples trabajos

**Tipo:** Funcional / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que múltiples trabajos enviados durante una misma sesión reciban identificadores diferentes.

### Datos de prueba
Cinco trabajos consecutivos enviados al daemon.

### Resultado esperado
Cada uno de los trabajos debe recibir un UUID diferente.

### Resultado obtenido
```text
0e79403c-c9d9-429b-a15b-a3c4173e8cc2
eecbc635-3832-42f6-82a3-8013b5eb0f9c
88455cb6-3e8c-4a2e-9d00-2265f62c67fa
8a4c9dd3-497c-4407-8933-d6476992261f
fea817f4-d6fb-407c-bc48-2ca01ad625d9

PASS: Todos los trabajos tienen identificadores unicos.
```

### Evidencia
`EV-009-ipc-multiple-jobs-output.txt`

---

## TC-052 — Conservar múltiples trabajos durante la sesión

**Tipo:** Funcional / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que múltiples trabajos enviados al daemon permanezcan disponibles para consulta y listado durante la misma sesión.

### Datos de prueba
```text
echo Trabajo 1
echo Trabajo 2
echo Trabajo 3
true
false
```

### Resultado esperado
Todos los trabajos deben poder consultarse individualmente y aparecer posteriormente en el listado general.

Los comandos exitosos deben finalizar en `SUCCEEDED` y el comando `false` debe finalizar en `FAILED`.

### Resultado obtenido
```text
echo Trabajo 1 -> SUCCEEDED / exit code 0
echo Trabajo 2 -> SUCCEEDED / exit code 0
echo Trabajo 3 -> SUCCEEDED / exit code 0
true           -> SUCCEEDED / exit code 0
false          -> FAILED / exit code 1

PASS: El listado final termina con codigo 0.
PASS: Todos los trabajos enviados permanecen en el listado del daemon.
PASS: Todos los trabajos pudieron consultarse individualmente.
PASS: El daemon continua activo despues de multiples solicitudes.
```

### Evidencia
`EV-009-ipc-multiple-jobs-output.txt`

---


# Casos de prueba — PR #110

## Socket UNIX configurable — Issue #72

## TC-053 — Utilizar socket UNIX predeterminado

**Requisito relacionado:** Issue #72 — Socket UNIX configurable
**Tipo:** Funcional
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que Jobsy utilice `/tmp/jobsy.sock` como ruta predeterminada del socket UNIX.

### Resultado esperado
La configuración debe resolver `/tmp/jobsy.sock` como socket predeterminado cuando no se especifica una ruta personalizada.

### Resultado obtenido
```text
Exit code: 0
STDOUT: '/tmp/jobsy.sock'
STDERR: ''

PASS: La configuracion puede cargarse correctamente.
PASS: El socket predeterminado es /tmp/jobsy.sock.
```

### Evidencia
`EV-010-socket-config-output.txt`

---

## TC-054 — Aceptar una ruta absoluta personalizada para el socket

**Requisito relacionado:** Issue #72 — Socket UNIX configurable
**Tipo:** Funcional
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que Jobsy permita configurar el daemon con una ruta absoluta válida para el socket UNIX.

### Resultado esperado
La ruta absoluta debe ser aceptada y conservarse como ruta del socket configurado.

### Resultado obtenido
```text
Exit code: 0
STDOUT: '/tmp/.../control.sock'
STDERR: ''

PASS: Se acepta una ruta absoluta valida.
PASS: La configuracion conserva la ruta personalizada.
```

### Evidencia
`EV-010-socket-config-output.txt`

---

## TC-055 — Utilizar JOBSY_SOCKET_PATH desde la CLI

**Requisito relacionado:** Issue #72 — Socket UNIX configurable
**Tipo:** Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que la CLI pueda conectarse al daemon utilizando la ruta definida mediante `JOBSY_SOCKET_PATH`.

### Resultado esperado
La CLI debe utilizar el socket indicado por la variable de entorno y comunicarse correctamente con el daemon.

### Resultado obtenido
```text
PASS: El daemon crea el socket personalizado.
Exit code: 0
STDOUT: 'No se encontraron trabajos.'
STDERR: ''

PASS: La CLI puede conectarse usando JOBSY_SOCKET_PATH.
```

### Evidencia
`EV-010-socket-config-output.txt`

---

## TC-056 — Ejecutar operaciones mediante un socket personalizado

**Requisito relacionado:** Issue #72 — Socket UNIX configurable
**Tipo:** Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que una operación real de la CLI pueda ejecutarse correctamente mediante un socket UNIX personalizado.

### Resultado esperado
La operación debe procesarse correctamente utilizando el socket personalizado y sin errores de comunicación.

### Resultado obtenido
```text
Exit code: 0
STDOUT: 'No se encontraron trabajos.'
STDERR: ''

PASS: La operacion list no devuelve error.
PASS: El socket personalizado se elimina al detener el daemon.
```

### Evidencia
`EV-010-socket-config-output.txt`

---

## TC-057 — Rechazar una ruta relativa de socket

**Requisito relacionado:** Issue #72 — Socket UNIX configurable
**Tipo:** Negativa
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que Jobsy rechace una ruta relativa al configurar el socket UNIX.

### Resultado esperado
La configuración debe fallar indicando que la ruta del socket debe ser absoluta.

### Resultado obtenido
```text
Exit code: 1
ValueError: La ruta del socket debe ser absoluta y nombrar un archivo.

PASS: Una ruta relativa es rechazada.
PASS: El error indica que la ruta debe ser absoluta.
```

### Evidencia
`EV-010-socket-config-output.txt`

---

## TC-058 — Rechazar un directorio padre inexistente

**Requisito relacionado:** Issue #72 — Socket UNIX configurable
**Tipo:** Negativa
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que Jobsy rechace una ruta de socket cuyo directorio padre no exista.

### Resultado esperado
La configuración debe fallar indicando que el directorio padre debe existir y ser accesible.

### Resultado obtenido
```text
Exit code: 1
ValueError: El directorio padre del socket debe existir y ser accesible.

PASS: Se rechaza una ruta cuyo directorio padre no existe.
PASS: El error indica que el directorio padre debe existir.
```

### Evidencia
`EV-010-socket-config-output.txt`

---

## TC-059 — Rechazar un enlace simbólico como ruta final del socket

**Requisito relacionado:** Issue #72 — Socket UNIX configurable
**Tipo:** Negativa
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que Jobsy no permita utilizar un enlace simbólico como componente final de la ruta del socket.

### Resultado esperado
La configuración debe rechazar la ruta indicando que el socket no puede ser un enlace simbólico.

### Resultado obtenido
```text
Exit code: 1
ValueError: La ruta final del socket no puede ser un enlace simbólico.

PASS: La ruta final como enlace simbolico es rechazada.
PASS: El error informa que no se permite un enlace simbolico.
```

### Evidencia
`EV-010-socket-config-output.txt`

---

## TC-060 — Rechazar una ruta de socket mayor a 107 bytes

**Requisito relacionado:** Issue #72 — Socket UNIX configurable
**Tipo:** Negativa
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que Jobsy respete el límite de longitud del socket UNIX en Linux.

### Resultado esperado
Una ruta resuelta que exceda 107 bytes debe ser rechazada.

### Resultado obtenido
```text
Longitud bytes: 122
Exit code: 1
ValueError: La ruta del socket excede 107 bytes en Linux.

PASS: Se rechaza una ruta mayor a 107 bytes.
PASS: El error informa el limite maximo permitido.
```

### Evidencia
`EV-010-socket-config-output.txt`

---

## TC-061 — No sobrescribir una ruta de socket existente

**Requisito relacionado:** Issue #72 — Socket UNIX configurable
**Tipo:** Negativa
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que el daemon no elimine ni sobrescriba una ruta que ya exista antes de iniciar.

### Resultado esperado
El daemon debe rechazar el inicio, conservar la ruta existente y no modificar su contenido.

### Resultado obtenido
```text
Exit code: 1
FileExistsError: El socket ya existe; compruebe si hay un daemon activo.

PASS: El daemon no inicia si la ruta ya existe.
PASS: La ruta existente no es eliminada.
PASS: El contenido existente permanece intacto.
```

### Evidencia
`EV-010-socket-config-output.txt`

---

## TC-062 — Volver al socket predeterminado sin JOBSY_SOCKET_PATH

**Requisito relacionado:** Issue #72 — Socket UNIX configurable
**Tipo:** Funcional
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que el cliente vuelva a utilizar `/tmp/jobsy.sock` cuando `JOBSY_SOCKET_PATH` no está definida.

### Resultado esperado
La resolución del endpoint debe devolver `/tmp/jobsy.sock`.

### Resultado obtenido
```text
Exit code: 0
STDOUT: '/tmp/jobsy.sock'
STDERR: ''

PASS: La resolucion del socket funciona sin variable de entorno.
PASS: Sin JOBSY_SOCKET_PATH se usa /tmp/jobsy.sock.
```

### Evidencia
`EV-010-socket-config-output.txt`

---

## TC-063 — Verificar que el daemon ignore JOBSY_SOCKET_PATH

**Requisito relacionado:** Issue #72 — Socket UNIX configurable
**Tipo:** Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que `JOBSY_SOCKET_PATH` afecte únicamente a los clientes y no modifique la ruta utilizada por el daemon.

### Resultado esperado
El daemon debe utilizar exclusivamente la ruta proporcionada mediante `--socket-path` y no crear el socket indicado por `JOBSY_SOCKET_PATH`.

### Resultado obtenido
```text
PASS: El daemon utiliza --socket-path.
PASS: JOBSY_SOCKET_PATH no crea ni sustituye el socket del daemon.
```

### Evidencia
`EV-011-socket-cli-contract-output.txt`

---

## TC-064 — Rechazar JOBSY_SOCKET_PATH vacío

**Requisito relacionado:** Issue #72 — Socket UNIX configurable
**Tipo:** Negativa
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que el cliente rechace una variable `JOBSY_SOCKET_PATH` definida con una cadena vacía.

### Resultado esperado
La solicitud debe ser rechazada y la CLI debe finalizar con código de salida 1.

### Resultado obtenido
```text
Exit code: 1
STDOUT: ''
STDERR: 'Error: La ruta del socket debe ser texto no vacío y sin NUL.'

PASS: El cliente devuelve codigo 1 con JOBSY_SOCKET_PATH vacio.
PASS: El cliente informa un error relacionado con el endpoint.
```

### Evidencia
`EV-011-socket-cli-contract-output.txt`

---

## TC-065 — Devolver código 2 ante socket inválido del daemon

**Requisito relacionado:** Issue #72 — Socket UNIX configurable
**Tipo:** Negativa
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar el código de salida del daemon cuando `--socket-path` recibe una configuración inválida.

### Resultado esperado
El daemon debe rechazar la configuración antes de iniciar y terminar con código de salida 2.

### Resultado obtenido
```text
Exit code: 2
STDOUT: ''
STDERR: 'jobsy-daemon: error: La ruta del socket debe ser absoluta y nombrar un archivo.'

PASS: Una configuracion invalida del daemon devuelve codigo 2.
```

### Evidencia
`EV-011-socket-cli-contract-output.txt`

---

## TC-066 — Devolver código 1 cuando el endpoint no tiene servicio

**Requisito relacionado:** Issue #72 — Socket UNIX configurable
**Tipo:** Negativa
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar el comportamiento del cliente cuando `JOBSY_SOCKET_PATH` apunta a un endpoint válido pero no existe un daemon atendiendo la solicitud.

### Resultado esperado
La CLI debe informar que el servicio no está disponible y finalizar con código de salida 1.

### Resultado obtenido
```text
Exit code: 1
STDOUT: ''
STDERR: 'Error: El servicio Jobsy no está en ejecución.'

PASS: El cliente devuelve codigo 1 cuando no existe el servicio.
```

### Evidencia
`EV-011-socket-cli-contract-output.txt`

---

## TC-067 — Expandir ~ en la ruta personalizada del socket

**Requisito relacionado:** Issue #72 — Socket UNIX configurable
**Tipo:** Funcional
**Prioridad:** Media
**Estado:** `PASS`

### Objetivo
Verificar que Jobsy expanda correctamente `~` al directorio HOME al recibir una ruta personalizada.

### Resultado esperado
El daemon debe crear el socket en el directorio HOME correspondiente y eliminarlo al apagarse.

### Resultado obtenido
```text
PASS: La ruta con ~ se expande al HOME del usuario.
PASS: El socket expandido se elimina al detener el daemon.
```

### Evidencia
`EV-011-socket-cli-contract-output.txt`

---

## TC-068 — Iniciar jobsy-daemon con un socket personalizado

**Requisito relacionado:** Issue #72 — Socket UNIX configurable
**Tipo:** Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que el punto de entrada público `jobsy-daemon` pueda iniciar el servicio utilizando `--socket-path`.

### Resultado esperado
El daemon debe iniciar correctamente y crear el socket UNIX en la ruta personalizada.

### Resultado obtenido
```text
PASS: jobsy-daemon inicia con un socket personalizado.
PASS: El socket del entry point se elimina al detener el daemon.
```

### Evidencia
`EV-011-socket-cli-contract-output.txt`

---

## TC-069 — Utilizar JOBSY_SOCKET_PATH desde los puntos de entrada de consulta y cancelación

**Requisito relacionado:** Issue #72 — Socket UNIX configurable
**Tipo:** Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que los puntos de entrada públicos `jobsy`, `list`, `status` y `cancel` utilicen el endpoint definido mediante `JOBSY_SOCKET_PATH`.

### Resultado esperado
Todos los comandos deben comunicarse correctamente con el daemon mediante el socket personalizado y operar sobre el trabajo correspondiente.

### Resultado obtenido
```text
jobsy list:
Exit code: 0
Estado del trabajo: RUNNING

PASS: jobsy list utiliza JOBSY_SOCKET_PATH.
PASS: jobsy list muestra el trabajo creado.

list:
Exit code: 0
PASS: El comando corto list utiliza JOBSY_SOCKET_PATH.

status:
Exit code: 0
Estado: RUNNING
PASS: El comando corto status utiliza JOBSY_SOCKET_PATH.
PASS: status consulta el trabajo correcto.

cancel:
Exit code: 0
Estado actual: CANCELED
PASS: El comando corto cancel utiliza JOBSY_SOCKET_PATH.
```

### Evidencia
`EV-011-socket-cli-contract-output.txt`

---

## TC-070 — Utilizar JOBSY_SOCKET_PATH desde execute

**Requisito relacionado:** Issue #72 — Socket UNIX configurable
**Tipo:** Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que el punto de entrada público `execute` utilice el socket definido mediante `JOBSY_SOCKET_PATH`.

### Resultado esperado
`execute` debe enviar el trabajo al daemon mediante el socket personalizado y devolver un UUID válido.

### Resultado obtenido
```text
Exit code: 0
STDOUT: 'Trabajo creado y enviado a ejecución con ID: 86072639-0da9-4052-843c-26ad2354b1f8'
STDERR: ''

PASS: execute utiliza JOBSY_SOCKET_PATH.
PASS: execute devuelve un UUID de trabajo.
```

### Evidencia
`EV-011-socket-cli-contract-output.txt`

---

### TC-071 — Separar stdout y stderr

**Requisito relacionado:** RF-11
**Tipo:** Funcional / Integración
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que Jobsy conserve por separado la salida estándar y la salida de error de un trabajo.

#### Datos de prueba
```text
sh -c 'echo SALIDA_STDOUT; echo SALIDA_STDERR >&2'
```

#### Resultado esperado
`stdout` debe contener únicamente `SALIDA_STDOUT` y `stderr` únicamente `SALIDA_STDERR`.

#### Resultado obtenido
```text
stdout: SALIDA_STDOUT
stderr: SALIDA_STDERR
PASS
```

#### Evidencia
`EV-012-output-behavior-output.txt`

---

### TC-072 — Recuperar stdout mayor a 4096 bytes

**Requisito relacionado:** RF-11
**Tipo:** Integración / Robustez
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que la CLI reciba íntegramente una salida estándar mayor a 4096 bytes.

#### Resultado esperado
La salida debe conservarse completa y sin truncamiento.

#### Resultado obtenido
```text
Tamaño esperado: 10001 bytes
Integridad: True
PASS
```

#### Evidencia
`EV-012-output-behavior-output.txt`

---

### TC-073 — Recuperar stderr mayor a 4096 bytes

**Requisito relacionado:** RF-11
**Tipo:** Integración / Robustez
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que la CLI reciba íntegramente una salida de error mayor a 4096 bytes.

#### Resultado esperado
`stderr` debe conservarse completo y sin truncamiento.

#### Resultado obtenido
```text
Tamaño esperado: 10001 bytes
Integridad: True
PASS
```

#### Evidencia
`EV-012-output-behavior-output.txt`

---

### TC-074 — Mantener vacío el stream no utilizado

**Requisito relacionado:** RF-11
**Tipo:** Funcional
**Prioridad:** Media
**Estado:** `PASS`

#### Objetivo
Verificar que cuando un trabajo escribe únicamente en uno de los streams, el otro permanezca vacío.

#### Resultado esperado
El stream no utilizado debe tener longitud cero.

#### Resultado obtenido
```text
PASS
```

#### Evidencia
`EV-012-output-behavior-output.txt`

---

### TC-075 — Devolver código 0 al consultar output correctamente

**Requisito relacionado:** RF-11
**Tipo:** Funcional / Integración
**Prioridad:** Media
**Estado:** `PASS`

#### Objetivo
Verificar que el comando de consulta de salida termine con código `0`.

#### Resultado esperado
La operación debe finalizar con código de salida `0`.

#### Resultado obtenido
```text
Exit code: 0
PASS
```

#### Evidencia
`EV-012-output-behavior-output.txt`

---

## RNF-30 — Gestión de grupos de procesos

### TC-076 — Crear cada trabajo en su propio grupo de procesos

**Requisito relacionado:** RNF-30
**Tipo:** Integración
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que un trabajo se ejecute en un grupo de procesos y sesión propios.

#### Resultado esperado
El PID del proceso principal debe coincidir con su PGID y SID.

#### Resultado obtenido
```text
PID = PGID = SID
PASS
```

#### Evidencia
`EV-013-process-group-cancellation-output.txt`

---

### TC-077 — Mantener procesos hijos en el mismo grupo

**Requisito relacionado:** RNF-30
**Tipo:** Integración
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que los procesos hijos creados por un trabajo pertenezcan al mismo grupo y sesión que el proceso principal.

#### Resultado esperado
Padre e hijo deben compartir PGID y SID.

#### Resultado obtenido
```text
PASS
```

#### Evidencia
`EV-013-process-group-cancellation-output.txt`

---

### TC-078 — Cancelar proceso principal y descendientes

**Requisito relacionado:** RNF-30
**Tipo:** Integración / Robustez
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que al cancelar un trabajo terminen tanto el proceso principal como sus descendientes.

#### Resultado esperado
El trabajo debe terminar en `CANCELED`, registrar `finished_at` y no dejar procesos pertenecientes al grupo.

#### Resultado obtenido
```text
Estado: CANCELED
finished_at: registrado
Miembros restantes del grupo: []
PASS
```

#### Evidencia
`EV-013-process-group-cancellation-output.txt`

---

### TC-079 — Mantener daemon operativo después de cancelar un grupo

**Requisito relacionado:** RNF-30
**Tipo:** Robustez / Integración
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que la cancelación completa de un grupo de procesos no afecte la disponibilidad del daemon.

#### Resultado esperado
El daemon debe continuar respondiendo después de la cancelación.

#### Resultado obtenido
```text
PASS
```

#### Evidencia
`EV-013-process-group-cancellation-output.txt`

---

## RF-26 — Cancelación repetida

### TC-080 — Cancelar un trabajo por primera vez

**Requisito relacionado:** RF-26
**Tipo:** Funcional / Integración
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que la primera solicitud de cancelación se procese correctamente.

#### Resultado esperado
El trabajo debe cambiar a estado `CANCELED`.

#### Resultado obtenido
```text
Estado: CANCELED
PASS
```

#### Evidencia
`EV-014-repeated-cancellation-output.txt`

---

### TC-081 — Rechazar una segunda cancelación con mensaje claro

**Requisito relacionado:** RF-26
**Tipo:** Negativa / Funcional
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que una segunda solicitud de cancelación sea rechazada con un mensaje específico.

#### Resultado esperado
La CLI debe terminar con código `1`, conservar el estado `CANCELED` e informar que la cancelación ya fue solicitada.

#### Resultado obtenido
```text
Error de validación: La cancelación de este trabajo ya fue solicitada (estado CANCELED).
Exit code: 1
PASS
```

#### Evidencia
`EV-014-repeated-cancellation-output.txt`

---

## RF-30 — Período de gracia configurable

### TC-082 — Aceptar cancel-grace entero válido

**Requisito relacionado:** RF-30
**Tipo:** Funcional
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que `--cancel-grace 2` sea aceptado.

#### Resultado esperado
La configuración debe aceptar el valor `2`.

#### Resultado obtenido
```text
Exit code: 0
Valor: 2.0
PASS
```

#### Evidencia
`EV-015-cancel-grace-output.txt`

---

### TC-083 — Aceptar cancel-grace fraccionario válido

**Requisito relacionado:** RF-30
**Tipo:** Funcional
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que `--cancel-grace 0.5` sea aceptado.

#### Resultado esperado
La configuración debe aceptar el valor `0.5`.

#### Resultado obtenido
```text
Exit code: 0
Valor: 0.5
PASS
```

#### Evidencia
`EV-015-cancel-grace-output.txt`

---

### TC-084 — Rechazar cancel-grace igual a cero

**Requisito relacionado:** RF-30
**Tipo:** Negativa
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que el daemon rechace un período de gracia igual a cero.

#### Resultado esperado
La configuración debe finalizar con código `2`.

#### Resultado obtenido
```text
Exit code: 2
jobsy-daemon: error: cancel_grace_seconds debe ser un número mayor que 0 y menor o igual a 60.
PASS
```

#### Evidencia
`EV-015-cancel-grace-output.txt`

---

### TC-085 — Rechazar cancel-grace negativo

**Requisito relacionado:** RF-30
**Tipo:** Negativa
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que el daemon rechace valores negativos para `--cancel-grace`.

#### Resultado esperado
La configuración debe finalizar con código `2`.

#### Resultado obtenido
```text
Exit code: 2
jobsy-daemon: error: cancel_grace_seconds debe ser un número mayor que 0 y menor o igual a 60.
PASS
```

#### Evidencia
`EV-015-cancel-grace-output.txt`

---

### TC-086 — Rechazar cancel-grace mayor a 60

**Requisito relacionado:** RF-30
**Tipo:** Negativa
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que el daemon rechace valores superiores a `60` segundos.

#### Resultado esperado
La configuración debe finalizar con código `2`.

#### Resultado obtenido
```text
Exit code: 2
jobsy-daemon: error: cancel_grace_seconds debe ser un número mayor que 0 y menor o igual a 60.
PASS
```

#### Evidencia
`EV-015-cancel-grace-output.txt`

---

### TC-087 — Escalar de SIGTERM a SIGKILL

**Requisito relacionado:** RF-30
**Tipo:** Integración / Robustez
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar el comportamiento cuando un proceso ignora `SIGTERM`.

#### Datos de prueba
```text
sh -c 'trap "" TERM; while true; do sleep 1; done'
cancel_grace = 0.5
```

#### Resultado esperado
Jobsy debe enviar `SIGTERM`, esperar aproximadamente el período configurado y posteriormente usar `SIGKILL`.

#### Resultado obtenido
```text
Estado: CANCELED
Código de salida: -9
Miembros restantes del grupo: []
Daemon operativo: True
PASS
```

#### Evidencia
`EV-015-cancel-grace-output.txt`

---

## RNF-09 — Aislamiento de fallos de cleanup

### TC-088 — Aislar un fallo de cleanup

**Requisito relacionado:** RNF-09
**Tipo:** Robustez / Integración
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que una excepción durante la limpieza de un trabajo sea aislada y no detenga el servicio.

#### Resultado esperado
El fallo debe registrarse como diagnóstico y no propagarse al scheduler.

#### Resultado obtenido
```text
PASS
```

#### Evidencia
`EV-016-cleanup-isolation-output.txt`

---

### TC-089 — Mantener scheduler responsivo durante cleanup fallido

**Requisito relacionado:** RNF-09
**Tipo:** Robustez
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que el scheduler continúe respondiendo mientras se procesa un fallo de cleanup aislado.

#### Resultado esperado
Las operaciones del scheduler deben permanecer disponibles sin bloqueo global.

#### Resultado obtenido
```text
counts() respondió correctamente.
PASS
```

#### Evidencia
`EV-016-cleanup-isolation-output.txt`

---

### TC-090 — Finalizar de forma controlada tras fallo de cleanup

**Requisito relacionado:** RNF-09
**Tipo:** Robustez / Integración
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que el monitor finalice de forma controlada después de aislar un fallo de cleanup.

#### Resultado esperado
Debe obtenerse un código de salida distinto de cero y conservarse un diagnóstico con la causa original.

#### Resultado obtenido
```text
Código de salida: -9
Diagnóstico: conservado
PASS
```

#### Evidencia
`EV-016-cleanup-isolation-output.txt`

---

# Casos de prueba — PR #116

---

## RF-27 — Semántica de solicitudes duplicadas

## TC-091 — List duplicado no altera el estado

**Requisito relacionado:** RF-27
**Tipo:** Funcional / Integración / Idempotencia
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que repetir una solicitud IPC `list` no modifique los trabajos ni el estado interno del daemon.

### Resultado esperado
Dos solicitudes `list` consecutivas deben responder correctamente y devolver el mismo estado cuando no existe ninguna modificación entre ambas.

### Resultado obtenido
Las dos solicitudes fueron procesadas correctamente y devolvieron el mismo listado sin alterar el estado.

### Evidencia
`EV-017-duplicate-requests-output.txt`

---

## TC-092 — Status duplicado conserva metadatos

**Requisito relacionado:** RF-27
**Tipo:** Funcional / Integración / Idempotencia
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que consultar repetidamente `status` sobre el mismo trabajo no modifique sus metadatos.

### Resultado esperado
Dos consultas consecutivas deben devolver los mismos datos del trabajo.

### Resultado obtenido
Las consultas consecutivas conservaron estado, comando, timestamps y demás metadatos.

### Evidencia
`EV-017-duplicate-requests-output.txt`

---

## TC-093 — Output duplicado conserva stdout y stderr

**Requisito relacionado:** RF-27; RF-11
**Tipo:** Funcional / Integración / Idempotencia
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que repetir `output` no modifique las salidas almacenadas de un trabajo.

### Resultado esperado
Las consultas repetidas deben devolver exactamente el mismo `stdout` y `stderr`.

### Resultado obtenido
Las dos consultas devolvieron exactamente el contenido original de ambos flujos.

### Evidencia
`EV-017-duplicate-requests-output.txt`

---

## TC-094 — Cancel duplicado no genera segunda transición

**Requisito relacionado:** RF-27; RF-26
**Tipo:** Funcional / Negativa / Idempotencia controlada
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que una segunda solicitud de cancelación no genere una nueva transición sobre un trabajo ya cancelado.

### Resultado esperado
La primera cancelación debe llevar el trabajo a `CANCELED`; la segunda debe rechazarse de forma controlada.

### Resultado obtenido
La primera solicitud canceló el trabajo y la segunda fue rechazada indicando que la cancelación ya había sido solicitada.

### Evidencia
`EV-017-duplicate-requests-output.txt`

---

## TC-095 — Cancel duplicado conserva estado y timestamps

**Requisito relacionado:** RF-27; RF-26
**Tipo:** Integración / Consistencia
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que una cancelación repetida no modifique nuevamente el estado ni las marcas de tiempo del trabajo.

### Resultado esperado
El trabajo debe permanecer `CANCELED` y conservar `received_at`, `started_at` y `finished_at`.

### Resultado obtenido
El estado permaneció `CANCELED` y los timestamps no cambiaron después del segundo intento.

### Evidencia
`EV-017-duplicate-requests-output.txt`

---

## TC-096 — Run duplicado crea UUID diferentes

**Requisito relacionado:** RF-27
**Tipo:** Funcional / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar la semántica no idempotente de `run`.

### Resultado esperado
Dos solicitudes `run` con el mismo comando deben crear trabajos distintos con UUIDv4 diferentes.

### Resultado obtenido
Ambas solicitudes fueron aceptadas y generaron identificadores UUIDv4 válidos y diferentes.

### Evidencia
`EV-017-duplicate-requests-output.txt`

---

## TC-097 — Run duplicado crea trabajos independientes

**Requisito relacionado:** RF-27
**Tipo:** Funcional / Integración / Consistencia
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que dos solicitudes `run` idénticas produzcan entidades independientes.

### Resultado esperado
Los dos trabajos deben conservar el mismo comando pero tener ciclos de vida independientes.

### Resultado obtenido
Ambos trabajos pudieron consultarse de forma independiente y cancelar uno no modificó el estado del otro.

### Evidencia
`EV-017-duplicate-requests-output.txt`

---

## TC-098 — Daemon sigue operativo tras solicitudes duplicadas

**Requisito relacionado:** RF-27
**Tipo:** Robustez / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que las solicitudes repetidas no afecten la disponibilidad del daemon.

### Resultado esperado
El proceso debe permanecer activo y aceptar solicitudes válidas después de las operaciones duplicadas.

### Resultado obtenido
El daemon permaneció activo y respondió correctamente a una solicitud `list` posterior.

### Evidencia
`EV-017-duplicate-requests-output.txt`

---

## RF-24 — Resumen de salud del servicio

## TC-099 — Health responde con estructura esperada

**Requisito relacionado:** RF-24
**Tipo:** Funcional / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que la acción `health` responda correctamente e incluya todos los campos definidos.

### Resultado esperado
Debe incluir `service_active`, `storage_error`, `running_count`, `running_jobs`, `queued_count`, `queued_jobs`, `recent_errors_count` y `recent_errors`.

### Resultado obtenido
La respuesta fue `ok` y contenía todos los campos esperados.

### Evidencia
`EV-018-health-summary-output.txt`

---

## TC-100 — Health reporta servicio activo

**Requisito relacionado:** RF-24
**Tipo:** Funcional
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar los indicadores generales de salud durante una sesión normal.

### Resultado esperado
`service_active` debe ser verdadero y `storage_error` debe ser nulo.

### Resultado obtenido
El servicio fue reportado activo y sin errores de almacenamiento.

### Evidencia
`EV-018-health-summary-output.txt`

---

## TC-101 — Health reporta trabajo RUNNING

**Requisito relacionado:** RF-24
**Tipo:** Funcional / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que `health` contabilice e identifique trabajos `RUNNING`.

### Resultado esperado
El resumen debe indicar un trabajo en ejecución e incluir su ID.

### Resultado obtenido
`running_count` fue correcto y el trabajo esperado apareció en `running_jobs`.

### Evidencia
`EV-018-health-summary-output.txt`

---

## TC-102 — Health reporta trabajo QUEUED

**Requisito relacionado:** RF-24
**Tipo:** Funcional / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que `health` contabilice e identifique trabajos `QUEUED`.

### Resultado esperado
El resumen debe indicar un trabajo en cola e incluir su ID.

### Resultado obtenido
`queued_count` fue correcto y el trabajo apareció en `queued_jobs`.

### Evidencia
`EV-018-health-summary-output.txt`

---

## TC-103 — Health reporta errores recientes

**Requisito relacionado:** RF-24
**Tipo:** Funcional / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que trabajos `FAILED` sean incluidos entre los errores recientes.

### Resultado esperado
`recent_errors_count` debe aumentar y el trabajo fallido debe aparecer en `recent_errors`.

### Resultado obtenido
El trabajo `FAILED` fue reportado correctamente entre los errores recientes.

### Evidencia
`EV-018-health-summary-output.txt`

---

## TC-104 — Health limita errores recientes a 10

**Requisito relacionado:** RF-24
**Tipo:** Funcional / Límite
**Prioridad:** Media
**Estado:** `PASS`

### Objetivo
Verificar el límite máximo de errores recientes devueltos por `health`.

### Resultado esperado
El resumen no debe devolver más de 10 errores recientes.

### Resultado obtenido
`recent_errors_count` y la colección `recent_errors` quedaron limitados a 10 elementos.

### Evidencia
`EV-018-health-summary-output.txt`

---

## TC-105 — Health es operación de solo lectura

**Requisito relacionado:** RF-24
**Tipo:** Integración / Consistencia
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que consultar `health` no modifique el estado del sistema.

### Resultado esperado
Dos consultas consecutivas, sin cambios externos, deben devolver el mismo estado.

### Resultado obtenido
Las dos solicitudes fueron procesadas correctamente y el contenido del resumen no cambió.

### Evidencia
`EV-018-health-summary-output.txt`

---

## TC-106 — Daemon sigue operativo después de health

**Requisito relacionado:** RF-24
**Tipo:** Robustez / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que múltiples consultas `health` no afecten la disponibilidad del daemon.

### Resultado esperado
El proceso debe continuar activo y aceptar nuevas solicitudes.

### Resultado obtenido
El daemon permaneció activo y respondió correctamente a `list`.

### Evidencia
`EV-018-health-summary-output.txt`

---

## RNF-21 / RF-28 — Errores estructurados y sugerencias operativas

## TC-107 — Acción IPC inválida devuelve error estructurado

**Requisito relacionado:** RNF-21; RF-28
**Tipo:** Negativa / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar el contrato estructurado de error ante una acción IPC desconocida.

### Resultado esperado
La respuesta debe contener `status`, `operation`, `cause` y `suggestion`.

### Resultado obtenido
El daemon respondió con los cuatro campos y conservó el nombre de la operación inválida.

### Evidencia
`EV-019-structured-errors-output.txt`

---

## TC-108 — JSON inválido devuelve error estructurado

**Requisito relacionado:** RNF-21; RF-28
**Tipo:** Negativa / Robustez
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar el manejo controlado de JSON no interpretable.

### Resultado esperado
Debe devolverse un error estructurado usando la operación `desconocida` y una causa explícita.

### Resultado obtenido
El daemon devolvió el formato estructurado y conservó la causa del error de parseo.

### Evidencia
`EV-019-structured-errors-output.txt`

---

## TC-109 — Status de ID inexistente devuelve error estructurado

**Requisito relacionado:** RNF-21; RF-28
**Tipo:** Negativa / Funcional
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar el contrato de error al consultar un ID inexistente.

### Resultado esperado
La operación debe identificarse como `status` y la causa debe indicar que el trabajo no existe.

### Resultado obtenido
La respuesta identificó correctamente la operación y la causa.

### Evidencia
`EV-019-structured-errors-output.txt`

---

## TC-110 — Cancel de ID inexistente devuelve error estructurado

**Requisito relacionado:** RNF-21; RF-28
**Tipo:** Negativa / Funcional
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar el contrato de error al cancelar un ID inexistente.

### Resultado esperado
La respuesta debe identificar la operación `cancel` y proporcionar causa y sugerencia.

### Resultado obtenido
El daemon devolvió el error estructurado esperado.

### Evidencia
`EV-019-structured-errors-output.txt`

---

## TC-111 — Cola llena devuelve causa y sugerencia

**Requisito relacionado:** RF-23; RF-28; RNF-21
**Tipo:** Negativa / Capacidad / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar el tratamiento estructurado de `QueueFullError`.

### Resultado esperado
Una solicitud `run` que exceda la capacidad debe rechazarse con operación `run`, causa relacionada con cola llena y una sugerencia operativa.

### Resultado obtenido
La solicitud fue rechazada con el formato y contenido esperados.

### Evidencia
`EV-019-structured-errors-output.txt`

---

## TC-112 — CLI presenta el error estructurado

**Requisito relacionado:** RNF-21; RF-28
**Tipo:** Funcional / CLI
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que la CLI traduzca correctamente el error estructurado recibido del daemon.

### Resultado esperado
La CLI debe terminar con código `1` y mostrar operación, causa y acción sugerida en `stderr`.

### Resultado obtenido
Los tres elementos fueron mostrados correctamente y la CLI terminó con código `1`.

### Evidencia
`EV-019-structured-errors-output.txt`

---

## TC-113 — Daemon sigue operativo después de errores

**Requisito relacionado:** RNF-21; RF-28
**Tipo:** Robustez / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que solicitudes erróneas no detengan el daemon.

### Resultado esperado
El daemon debe permanecer activo y aceptar una solicitud válida posterior.

### Resultado obtenido
El proceso siguió activo y respondió correctamente a una nueva solicitud.

### Evidencia
`EV-019-structured-errors-output.txt`

---

## RF-14 / RNF-22 — Bitácora y correlación de solicitudes

## TC-114 — jobsy.log se crea en el data-dir

**Requisito relacionado:** RF-14
**Tipo:** Funcional / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar la creación de la bitácora centralizada en el directorio de datos configurado.

### Resultado esperado
Debe existir un archivo regular `jobsy.log` dentro del `data-dir`.

### Resultado obtenido
El archivo fue creado correctamente.

### Evidencia
`EV-020-request-logging-output.txt`

---

## TC-115 — Formato básico de la bitácora

**Requisito relacionado:** RF-14
**Tipo:** Funcional / Observabilidad
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar el formato de los eventos escritos en la bitácora.

### Resultado esperado
Las líneas deben incluir timestamp UTC con milisegundos, nivel de log y Job ID.

### Resultado obtenido
El formato observado cumplió los campos esperados.

### Evidencia
`EV-020-request-logging-output.txt`

---

## TC-116 — Cada solicitud IPC recibe ReqID

**Requisito relacionado:** RNF-22
**Tipo:** Observabilidad / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que cada solicitud IPC sea identificada mediante `ReqID`.

### Resultado esperado
El evento de recepción debe contener un `ReqID` no vacío.

### Resultado obtenido
La solicitud fue registrada con un `ReqID` válido.

### Evidencia
`EV-020-request-logging-output.txt`

---

## TC-117 — Solicitudes distintas reciben ReqID diferentes

**Requisito relacionado:** RNF-22
**Tipo:** Observabilidad / Consistencia
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que solicitudes IPC diferentes no reutilicen el mismo identificador de correlación.

### Resultado esperado
Dos solicitudes distintas deben recibir `ReqID` diferentes.

### Resultado obtenido
Los identificadores registrados fueron diferentes.

### Evidencia
`EV-020-request-logging-output.txt`

---

## TC-118 — Eventos de trabajo incluyen Job ID

**Requisito relacionado:** RF-14
**Tipo:** Observabilidad / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que los eventos relacionados con un trabajo permitan identificar el Job correspondiente.

### Resultado esperado
La bitácora debe registrar el Job ID durante creación, ejecución y finalización.

### Resultado obtenido
Los eventos incluyeron el Job ID y se registraron las etapas esperadas.

### Evidencia
`EV-020-request-logging-output.txt`

---

## TC-119 — ReqID correlaciona el ciclo de la solicitud run

**Requisito relacionado:** RNF-22
**Tipo:** Observabilidad / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que un mismo `ReqID` permita relacionar más de un evento perteneciente a la misma solicitud `run`.

### Resultado esperado
El `ReqID` asignado al recibir la solicitud debe reaparecer en eventos posteriores relacionados con su procesamiento.

### Resultado obtenido
Después de la corrección aplicada durante la revisión del PR #116, el mismo `ReqID` apareció en más de un evento del ciclo de la solicitud.

### Evidencia
`EV-020-request-logging-output.txt`

### Nota de revalidación
En la primera ejecución este caso obtuvo `FAIL`, ya que el `ReqID` solo aparecía en el evento inicial de recepción. El defecto fue reportado al equipo, corregido y posteriormente revalidado. La ejecución final obtuvo `PASS`.

---

## TC-120 — Bitácora persiste y daemon sigue operativo

**Requisito relacionado:** RF-14; RNF-22
**Tipo:** Robustez / Observabilidad
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que los eventos ya registrados permanezcan en la bitácora y que el logging no afecte la disponibilidad del servicio.

### Resultado esperado
La bitácora debe conservar eventos anteriores y el daemon debe continuar respondiendo.

### Resultado obtenido
Los eventos permanecieron registrados y el daemon continuó activo y operativo.

### Evidencia
`EV-020-request-logging-output.txt`

---

## RF-23 / RF-28 — Robustez y observabilidad de cola

## TC-121 — Cola llena queda registrada en jobsy.log

**Requisito relacionado:** RF-23; RF-14
**Tipo:** Robustez / Observabilidad / Capacidad
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que un rechazo causado por falta de capacidad quede registrado en la bitácora.

### Resultado esperado
La solicitud adicional debe rechazarse y el evento de cola llena debe aparecer en `jobsy.log`.

### Resultado obtenido
La tercera solicitud fue rechazada y el evento quedó registrado correctamente.

### Evidencia
`EV-021-queue-observability-output.txt`

---

## TC-122 — Rechazo por cola llena incluye ReqID

**Requisito relacionado:** RF-23; RNF-22
**Tipo:** Observabilidad / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que los rechazos por capacidad puedan correlacionarse con su solicitud IPC.

### Resultado esperado
El evento de rechazo debe contener un `ReqID`.

### Resultado obtenido
El evento de rechazo por capacidad incluyó el identificador de solicitud.

### Evidencia
`EV-021-queue-observability-output.txt`

---

## TC-123 — Desconexión prematura del cliente queda registrada

**Requisito relacionado:** RF-28
**Tipo:** Robustez / IPC
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que el servidor maneje y registre una desconexión del cliente antes de recibir la respuesta.

### Resultado esperado
La desconexión debe registrarse sin provocar la terminación del daemon.

### Resultado obtenido
La bitácora registró explícitamente la desconexión prematura.

### Evidencia
`EV-021-queue-observability-output.txt`

---

## TC-124 — Log indica estado de operación tras desconexión

**Requisito relacionado:** RF-28; RF-14
**Tipo:** Observabilidad / Robustez
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que el diagnóstico de una desconexión indique si la operación había sido aceptada, rechazada o no había tenido efecto.

### Resultado esperado
El log debe contener `Estado de la operación` y un estado explícito.

### Resultado obtenido
La bitácora registró correctamente el estado de la operación.

### Evidencia
`EV-021-queue-observability-output.txt`

---

## TC-125 — Daemon sobrevive a desconexión del cliente

**Requisito relacionado:** RF-28
**Tipo:** Robustez / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar que una desconexión prematura no detenga el servicio.

### Resultado esperado
El proceso del daemon debe permanecer activo.

### Resultado obtenido
El daemon permaneció en ejecución.

### Evidencia
`EV-021-queue-observability-output.txt`

---

## TC-126 — Solicitud posterior sigue funcionando

**Requisito relacionado:** RF-28
**Tipo:** Robustez / Integración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar la recuperación operativa del daemon después de una desconexión prematura.

### Resultado esperado
Una nueva solicitud válida debe procesarse correctamente.

### Resultado obtenido
Una solicitud `list` posterior respondió correctamente y el daemon permaneció activo.

### Evidencia
`EV-021-queue-observability-output.txt`

---


# Casos de prueba — Technical Review 2

## RNF-31 — Recuperación de trabajos

### TC-127 — Conservar trabajo terminal tras reinicio

**Requisito relacionado:** RNF-31
**Tipo:** Integración / Persistencia / Recuperación
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que un trabajo que terminó correctamente antes del reinicio permanezca disponible y conserve su estado terminal.

#### Resultado esperado
El trabajo debe seguir disponible después del reinicio y conservar el estado `SUCCEEDED`.

#### Resultado obtenido
```text
PASS: El trabajo termina en SUCCEEDED antes del reinicio.
PASS: El trabajo terminal sigue disponible después del reinicio.
PASS: El trabajo terminal conserva el estado SUCCEEDED.
```

#### Evidencia
`EV-022-recovery-behavior-output.txt`

---

### TC-128 — Conservar stdout y stderr tras reinicio

**Requisito relacionado:** RNF-31
**Tipo:** Integración / Persistencia
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que las salidas almacenadas de un trabajo terminal se conserven después de reiniciar el daemon.

#### Resultado esperado
`stdout` y `stderr` deben coincidir con los valores registrados antes del reinicio.

#### Resultado obtenido
```text
PASS: La salida del trabajo puede consultarse después del reinicio.
PASS: stdout se conserva sin cambios después del reinicio.
PASS: stderr se conserva sin cambios después del reinicio.
```

#### Evidencia
`EV-022-recovery-behavior-output.txt`

---

### TC-129 — Recuperar trabajo pendiente como CANCELED

**Requisito relacionado:** RNF-31
**Tipo:** Recuperación / Consistencia
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que un trabajo que permanecía `QUEUED` antes de una interrupción no sea reejecutado automáticamente.

#### Resultado esperado
El trabajo debe permanecer disponible y recuperarse en estado `CANCELED`.

#### Resultado obtenido
```text
PASS: El trabajo anteriormente QUEUED sigue disponible.
PASS: El trabajo pendiente se recupera como CANCELED.
```

#### Evidencia
`EV-022-recovery-behavior-output.txt`

---

### TC-130 — Recuperar ejecución interrumpida como FAILED

**Requisito relacionado:** RNF-31
**Tipo:** Recuperación / Robustez
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que una ejecución interrumpida cuyo proceso ya no existe se marque como fallida durante la recuperación.

#### Resultado esperado
El trabajo debe permanecer disponible y recuperarse como `FAILED`.

#### Resultado obtenido
```text
PASS: El trabajo interrumpido sigue disponible en el historial.
PASS: La ejecución interrumpida se recupera como FAILED.
```

#### Evidencia
`EV-022-recovery-behavior-output.txt`

---

### TC-131 — No reejecutar automáticamente trabajo interrumpido

**Requisito relacionado:** RNF-31
**Tipo:** Recuperación / Seguridad
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que una ejecución interrumpida no se vuelva a lanzar automáticamente al reiniciar.

#### Resultado esperado
El marcador de ejecución debe indicar una sola ejecución.

#### Resultado obtenido
```text
PASS: El trabajo interrumpido se inició una sola vez y no fue reejecutado.
```

#### Evidencia
`EV-022-recovery-behavior-output.txt`

---

### TC-132 — No ejecutar automáticamente trabajo pendiente al recuperar

**Requisito relacionado:** RNF-31
**Tipo:** Recuperación / Seguridad
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que un trabajo previamente `QUEUED` no se ejecute de forma automática durante la recuperación.

#### Resultado esperado
No debe crearse el marcador de ejecución del trabajo pendiente.

#### Resultado obtenido
```text
PASS: El trabajo que estaba QUEUED no se ejecuta automáticamente al recuperar.
```

#### Evidencia
`EV-022-recovery-behavior-output.txt`

---

### TC-133 — Mantener daemon operativo después de recuperación

**Requisito relacionado:** RNF-31
**Tipo:** Robustez / Integración
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que el servicio permanezca disponible después de reconciliar el historial.

#### Resultado esperado
El daemon debe aceptar solicitudes nuevas y permanecer activo.

#### Resultado obtenido
```text
PASS: El daemon responde a solicitudes después de la recuperación.
PASS: El proceso del daemon permanece activo después de recuperar el historial.
```

#### Evidencia
`EV-022-recovery-behavior-output.txt`

---

## RNF-33 — Estrés y liberación de recursos

### TC-134 — Aceptar carga de 120 trabajos

**Requisito relacionado:** RNF-33
**Tipo:** Estrés / Integración
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que el daemon acepte una carga sostenida de trabajos cortos.

#### Resultado esperado
Las 120 solicitudes deben ser aceptadas sin rechazos.

#### Resultado obtenido
```text
Solicitudes enviadas: 120
Trabajos aceptados: 120
Trabajos rechazados: 0
PASS: Las 120 solicitudes de estrés son aceptadas.
```

#### Evidencia
`EV-023-resource-stress-output.txt`

---

### TC-135 — Finalizar todos los trabajos de la carga

**Requisito relacionado:** RNF-33
**Tipo:** Estrés / Robustez
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que la carga no deje trabajos en ejecución o cola.

#### Resultado esperado
Los 120 trabajos deben finalizar y quedar en `SUCCEEDED`.

#### Resultado obtenido
```text
PASS: No quedan trabajos RUNNING o QUEUED después de la carga.
PASS: Los 120 trabajos terminan en SUCCEEDED.
```

#### Evidencia
`EV-023-resource-stress-output.txt`

---

### TC-136 — Liberar procesos hijos después de la carga

**Requisito relacionado:** RNF-33
**Tipo:** Recursos / Robustez
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que no queden procesos hijos residuales después de terminar la carga.

#### Resultado esperado
El daemon no debe conservar PIDs hijos.

#### Resultado obtenido
```text
Procesos hijos restantes: []
PASS: El daemon no conserva procesos hijos después de finalizar la carga.
```

#### Evidencia
`EV-023-resource-stress-output.txt`

---

### TC-137 — Liberar descriptores de archivo

**Requisito relacionado:** RNF-33
**Tipo:** Recursos / Robustez
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que la carga no produzca fuga de descriptores de archivo.

#### Resultado esperado
La cantidad de FDs debe volver a un nivel equivalente al inicial y no debe haber archivos eliminados aún abiertos.

#### Resultado obtenido
```text
FD iniciales: 6
FD después del estrés: 6
FD abiertos sobre archivos eliminados: []
PASS
```

#### Evidencia
`EV-023-resource-stress-output.txt`

---

### TC-138 — Estabilizar memoria después del estrés

**Requisito relacionado:** RNF-33
**Tipo:** Recursos / Memoria / Estrés
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que el RSS se estabilice una vez finalizada la carga.

#### Resultado esperado
Las muestras sucesivas en reposo no deben presentar crecimiento continuo.

#### Resultado obtenido
```text
RSS inicial: 26988 KB
Muestras RSS en reposo: [29588, 29588, 29588, 29588, 29588, 29588, 29588, 29588]
PASS: La memoria RSS permanece estable una vez finalizada la carga.
```

#### Evidencia
`EV-023-resource-stress-output.txt`

---

### TC-139 — Mantener daemon operativo después del estrés

**Requisito relacionado:** RNF-33
**Tipo:** Robustez / Integración
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que el servicio continúe disponible después de la carga.

#### Resultado obtenido
```text
PASS: El daemon responde correctamente a health después del estrés.
PASS: El proceso del daemon continúa activo.
```

#### Evidencia
`EV-023-resource-stress-output.txt`

---

### TC-140 — Liberar socket al apagar el daemon

**Requisito relacionado:** RNF-33
**Tipo:** Recursos / Integración
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que el socket UNIX no quede residual después del apagado.

#### Resultado obtenido
```text
PASS: El socket existe mientras el daemon está activo.
PASS: El socket UNIX se elimina al apagar el daemon.
```

#### Evidencia
`EV-023-resource-stress-output.txt`

---

## RNF-02 / RNF-03 / RNF-19 — Instalación limpia

### TC-141 — Crear clon limpio del repositorio

**Requisito relacionado:** RNF-02
**Tipo:** Instalación / Reproducibilidad
**Prioridad:** Alta
**Estado:** `PASS`

#### Resultado obtenido
```text
PASS: El repositorio puede clonarse desde cero.
PASS: El clon inicia con working tree limpio.
Commit probado: 10c7a8e
```

#### Evidencia
`EV-024-clean-installation-output.txt`

---

### TC-142 — Crear entorno virtual nuevo

**Requisito relacionado:** RNF-02
**Tipo:** Instalación / Reproducibilidad
**Prioridad:** Alta
**Estado:** `PASS`

#### Resultado obtenido
```text
PASS: Se crea un entorno virtual nuevo desde el clon limpio.
PASS: El entorno virtual contiene Python y pip.
```

#### Evidencia
`EV-024-clean-installation-output.txt`

---

### TC-143 — Instalar Jobsy sin privilegios root

**Requisito relacionado:** RNF-03
**Tipo:** Instalación / Seguridad
**Prioridad:** Alta
**Estado:** `PASS`

#### Resultado obtenido
```text
UID de ejecución: 1000
PASS: La prueba se ejecuta como usuario sin privilegios root.
Exit code instalación: 0
PASS: Jobsy se instala correctamente desde el clon limpio.
PASS: La instalación no utiliza sudo.
PASS: Jobsy queda instalado dentro del entorno virtual.
```

#### Evidencia
`EV-024-clean-installation-output.txt`

---

### TC-144 — Instalar sin warnings ni errores

**Requisito relacionado:** RNF-19
**Tipo:** Instalación / Calidad
**Prioridad:** Alta
**Estado:** `PASS`

#### Resultado obtenido
```text
Advertencias detectadas: 0
PASS: La instalación finaliza sin warnings ni errores de construcción.
```

#### Evidencia
`EV-024-clean-installation-output.txt`

---

### TC-145 — Instalar puntos de entrada públicos

**Requisito relacionado:** RNF-02; RNF-03
**Tipo:** Instalación / Funcional
**Prioridad:** Alta
**Estado:** `PASS`

#### Resultado obtenido
```text
Puntos de entrada esperados: jobsy, jobsy-daemon, execute, list, status, cancel
Puntos de entrada faltantes: ninguno
PASS: Los puntos de entrada públicos quedan instalados.
```

#### Evidencia
`EV-024-clean-installation-output.txt`

---

### TC-146 — Verificar instalación nueva operativa

**Requisito relacionado:** RNF-02; RNF-03
**Tipo:** Instalación / Funcional
**Prioridad:** Alta
**Estado:** `PASS`

#### Resultado obtenido
```text
PASS: jobsy --help funciona desde la instalación nueva.
PASS: jobsy-daemon --help funciona desde la instalación nueva.
PASS: La CLI instalada presenta su ayuda correctamente.
PASS: El daemon instalado presenta su ayuda correctamente.
```

#### Evidencia
`EV-024-clean-installation-output.txt`

---

## RNF-20 — Batería de QA mediante un único comando

### TC-147 — Batería disponible mediante un único comando

**Requisito relacionado:** RNF-20
**Tipo:** Automatización / Reproducibilidad
**Prioridad:** Alta
**Estado:** `PASS`

#### Objetivo
Verificar que la batería vigente pueda iniciarse mediante un único comando.

#### Resultado obtenido
```text
PASS: La batería descubre automáticamente los scripts de prueba disponibles.
PASS: La batería puede iniciarse mediante 'python test/run_qa_suite.py'.
```

#### Evidencia
`EV-025-single-command-suite-output.txt`

---

### TC-148 — Scripts de la batería finalizan correctamente

**Requisito relacionado:** RNF-20
**Tipo:** Automatización / Regresión
**Prioridad:** Alta
**Estado:** `PASS`

#### Resultado obtenido
```text
PASS: Los 22 scripts de la batería finalizaron con código 0.
```

#### Evidencia
`EV-025-single-command-suite-output.txt`

---

### TC-149 — Resultado agregado de la batería

**Requisito relacionado:** RNF-20
**Tipo:** Automatización / Regresión
**Prioridad:** Alta
**Estado:** `PASS`

#### Resultado obtenido
```text
Scripts ejecutados: 22
PASS: 22
FAIL: 0
TIMEOUT: 0
Duración total: 31.31 s
RESULTADO GENERAL: PASS
```

#### Evidencia
`EV-025-single-command-suite-output.txt`

---

### Automatización QA — Technical Review 2

| Script | Casos | Evidencia |
|---|---|---|
| `test/test_recovery_behavior.py` | TC-127 a TC-133 | EV-022 |
| `test/test_resource_stress.py` | TC-134 a TC-140 | EV-023 |
| `test/test_clean_installation.py` | TC-141 a TC-146 | EV-024 |
| `test/run_qa_suite.py` | TC-147 a TC-149 | EV-025 |

---

### Automatización QA — PR #116

| Script | Casos | Evidencia |
|---|---|---|
| `test/test_duplicate_requests.py` | TC-091 a TC-098 | EV-017 |
| `test/test_health_summary.py` | TC-099 a TC-106 | EV-018 |
| `test/test_structured_errors.py` | TC-107 a TC-113 | EV-019 |
| `test/test_request_logging.py` | TC-114 a TC-120 | EV-020 |
| `test/test_queue_observability.py` | TC-121 a TC-126 | EV-021 |

---

# Casos de prueba — PR #135

Resultados registrados sobre `32bd487`. Los resultados obtenidos son síntesis de las ejecuciones reportadas; no transcripciones nuevas.

## TC-165 — Cabecera de cuatro bytes y JSON UTF-8

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Protocolo
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Cabecera de cuatro bytes y JSON UTF-8.

### Procedimiento
`python test/test_network_protocol_v1.py` Consultar el caso TC-165 en la evidencia correspondiente.

### Resultado esperado
Longitud big-endian de 4 bytes coincide con el cuerpo JSON UTF-8.

### Resultado obtenido
Cabecera y objeto decodificado coinciden.

### Evidencia
`EV-028-network-protocol-v1-output.txt`.

---

## TC-166 — Fragmentación byte a byte con Unicode

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Protocolo
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Fragmentación byte a byte con Unicode.

### Procedimiento
`python test/test_network_protocol_v1.py` Consultar el caso TC-166 en la evidencia correspondiente.

### Resultado esperado
Reconstruir una trama fragmentada byte a byte con México y emoji.

### Resultado obtenido
Se recuperó el comando Unicode íntegro.

### Evidencia
`EV-028-network-protocol-v1-output.txt`.

---

## TC-167 — Tramas agrupadas y EOF limpio

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Protocolo
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Tramas agrupadas y EOF limpio.

### Procedimiento
`python test/test_network_protocol_v1.py` Consultar el caso TC-167 en la evidencia correspondiente.

### Resultado esperado
Leer health y list concatenados y detectar EOF limpio.

### Resultado obtenido
Ambas tramas fueron recuperadas; lectura final None.

### Evidencia
`EV-028-network-protocol-v1-output.txt`.

---

## TC-168 — Envío parcial sin pérdida de datos

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Protocolo
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Envío parcial sin pérdida de datos.

### Procedimiento
`python test/test_network_protocol_v1.py` Consultar el caso TC-168 en la evidencia correspondiente.

### Resultado esperado
Completar envíos parciales de 3 bytes sin pérdida.

### Resultado obtenido
Bytes enviados iguales a la trama original.

### Evidencia
`EV-028-network-protocol-v1-output.txt`.

---

## TC-169 — Rechazo de longitudes fuera del límite

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Protocolo
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Rechazo de longitudes fuera del límite.

### Procedimiento
`python test/test_network_protocol_v1.py` Consultar el caso TC-169 en la evidencia correspondiente.

### Resultado esperado
Rechazar longitud 0 y superior a 1048576 con INVALID_LENGTH y cierre.

### Resultado obtenido
Ambas entradas rechazadas.

### Evidencia
`EV-028-network-protocol-v1-output.txt`.

---

## TC-170 — Aceptación de los límites exactos de framing

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Protocolo
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Aceptación de los límites exactos de framing.

### Procedimiento
`python test/test_network_protocol_v1.py` Consultar el caso TC-170 en la evidencia correspondiente.

### Resultado esperado
Aceptar cuerpos de 1 y 1048576 bytes.

### Resultado obtenido
Ambos límites aceptados por el lector.

### Evidencia
`EV-028-network-protocol-v1-output.txt`.

---

## TC-171 — Detección de cabecera o cuerpo incompleto

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Protocolo
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Detección de cabecera o cuerpo incompleto.

### Procedimiento
`python test/test_network_protocol_v1.py` Consultar el caso TC-171 en la evidencia correspondiente.

### Resultado esperado
Detectar cabecera truncada y cuerpo incompleto con INCOMPLETE_MESSAGE.

### Resultado obtenido
Ambos errores controlados con cierre.

### Evidencia
`EV-028-network-protocol-v1-output.txt`.

---

## TC-172 — Timeout de lectura e inactividad

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Protocolo
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Timeout de lectura e inactividad.

### Procedimiento
`python test/test_network_protocol_v1.py` Consultar el caso TC-172 en la evidencia correspondiente.

### Resultado esperado
Distinguir READ_TIMEOUT e IdleTimeout.

### Resultado obtenido
Ambas condiciones detectadas.

### Evidencia
`EV-028-network-protocol-v1-output.txt`.

---

## TC-173 — Plazo absoluto ante tráfico fragmentado lento

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Protocolo
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Plazo absoluto ante tráfico fragmentado lento.

### Procedimiento
`python test/test_network_protocol_v1.py` Consultar el caso TC-173 en la evidencia correspondiente.

### Resultado esperado
Respetar plazo absoluto de 0.3 s ante envío lento; criterio del script < 1 s.

### Resultado obtenido
READ_TIMEOUT a 0.301 s.

### Evidencia
`EV-028-network-protocol-v1-output.txt`.

---

## TC-174 — Rechazo de codificación inválida

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Protocolo
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Rechazo de codificación inválida.

### Procedimiento
`python test/test_network_protocol_v1.py` Consultar el caso TC-174 en la evidencia correspondiente.

### Resultado esperado
Rechazar BOM, UTF-8 inválido y surrogate aislado.

### Resultado obtenido
INVALID_ENCODING en los tres escenarios.

### Evidencia
`EV-028-network-protocol-v1-output.txt`.

---

## TC-175 — JSON inválido y límite de profundidad

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Protocolo
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: JSON inválido y límite de profundidad.

### Procedimiento
`python test/test_network_protocol_v1.py` Consultar el caso TC-175 en la evidencia correspondiente.

### Resultado esperado
Rechazar duplicados, NaN, Infinity, documentos concatenados y profundidad 17; aceptar 16.

### Resultado obtenido
INVALID_JSON en entradas inválidas; profundidad 16 aceptada.

### Evidencia
`EV-028-network-protocol-v1-output.txt`.

---

## TC-176 — Validación de versión del protocolo

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Protocolo
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Validación de versión del protocolo.

### Procedimiento
`python test/test_network_protocol_v1.py` Consultar el caso TC-176 en la evidencia correspondiente.

### Resultado esperado
Rechazar versiones distintas del entero 1 y versión ausente.

### Resultado obtenido
UNSUPPORTED_VERSION o INVALID_REQUEST según el escenario.

### Evidencia
`EV-028-network-protocol-v1-output.txt`.

---

## TC-177 — Validación de request_id

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Protocolo
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Validación de request_id.

### Procedimiento
`python test/test_network_protocol_v1.py` Consultar el caso TC-177 en la evidencia correspondiente.

### Resultado esperado
Rechazar ID vacío, espacios, longitud 65 y tipo numérico; aceptar 64 caracteres.

### Resultado obtenido
Validación de request_id correcta.

### Evidencia
`EV-028-network-protocol-v1-output.txt`.

---

## TC-178 — Validación de acciones y parámetros

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Protocolo
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Validación de acciones y parámetros.

### Procedimiento
`python test/test_network_protocol_v1.py` Consultar el caso TC-178 en la evidencia correspondiente.

### Resultado esperado
Rechazar acción desconocida y parámetros inválidos; aceptar prefijo hexadecimal válido.

### Resultado obtenido
UNKNOWN_ACTION e INVALID_REQUEST controlados; ABCDEF12 aceptado.

### Evidencia
`EV-028-network-protocol-v1-output.txt`.

---

## TC-179 — Validación de sobres de respuesta y correlación

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Protocolo
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Validación de sobres de respuesta y correlación.

### Procedimiento
`python test/test_network_protocol_v1.py` Consultar el caso TC-179 en la evidencia correspondiente.

### Resultado esperado
Validar respuesta, versión, request_id y campos de error.

### Resultado obtenido
Respuesta válida aceptada y variantes inválidas rechazadas.

### Evidencia
`EV-028-network-protocol-v1-output.txt`.

---

## TC-180 — Rechazo de respuesta superior a 1 MiB

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Protocolo
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Rechazo de respuesta superior a 1 MiB.

### Procedimiento
`python test/test_network_protocol_v1.py` Consultar el caso TC-180 en la evidencia correspondiente.

### Resultado esperado
Rechazar respuesta codificada mayor a 1 MiB.

### Resultado obtenido
RESPONSE_TOO_LARGE.

### Evidencia
`EV-028-network-protocol-v1-output.txt`.

---

## TC-181 — Acceso remoto deshabilitado por defecto

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Configuración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Acceso remoto deshabilitado por defecto.

### Procedimiento
`python test/test_remote_server_config.py` Consultar el caso TC-181 en la evidencia correspondiente.

### Resultado esperado
TCP deshabilitado por defecto; puerto 8765, global 8, por IP 2.

### Resultado obtenido
Valores predeterminados correctos.

### Evidencia
`EV-029-remote-server-config-output.txt`.

---

## TC-182 — Aceptar IP privada y allowlist múltiple

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Configuración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Aceptar IP privada y allowlist múltiple.

### Procedimiento
`python test/test_remote_server_config.py` Consultar el caso TC-182 en la evidencia correspondiente.

### Resultado esperado
Aceptar IP 192.168.10.2 y CIDR 192.168.10.0/24, 10.0.0.5/32.

### Resultado obtenido
Configuración y redes aceptadas.

### Evidencia
`EV-029-remote-server-config-output.txt`.

---

## TC-183 — Rechazar direcciones comodín IPv4 e IPv6

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Configuración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Rechazar direcciones comodín IPv4 e IPv6.

### Procedimiento
`python test/test_remote_server_config.py` Consultar el caso TC-183 en la evidencia correspondiente.

### Resultado esperado
Rechazar 0.0.0.0 y ::.

### Resultado obtenido
Ambos comodines rechazados.

### Evidencia
`EV-029-remote-server-config-output.txt`.

---

## TC-184 — Rechazar IP pública de escucha

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Configuración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Rechazar IP pública de escucha.

### Procedimiento
`python test/test_remote_server_config.py` Consultar el caso TC-184 en la evidencia correspondiente.

### Resultado esperado
Rechazar escucha en 8.8.8.8.

### Resultado obtenido
IP pública rechazada.

### Evidencia
`EV-029-remote-server-config-output.txt`.

---

## TC-185 — Rechazar hostname y dirección inválida

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Configuración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Rechazar hostname y dirección inválida.

### Procedimiento
`python test/test_remote_server_config.py` Consultar el caso TC-185 en la evidencia correspondiente.

### Resultado esperado
Rechazar localhost y 999.1.1.1.

### Resultado obtenido
Ambos valores rechazados.

### Evidencia
`EV-029-remote-server-config-output.txt`.

---

## TC-186 — Exigir allowlist al habilitar TCP

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Configuración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Exigir allowlist al habilitar TCP.

### Procedimiento
`python test/test_remote_server_config.py` Consultar el caso TC-186 en la evidencia correspondiente.

### Resultado esperado
Exigir allowlist no vacía al habilitar TCP.

### Resultado obtenido
Configuración rechazada.

### Evidencia
`EV-029-remote-server-config-output.txt`.

---

## TC-187 — Rechazar redes públicas y rutas universales

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Configuración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Rechazar redes públicas y rutas universales.

### Procedimiento
`python test/test_remote_server_config.py` Consultar el caso TC-187 en la evidencia correspondiente.

### Resultado esperado
Rechazar 8.8.8.0/24, 0.0.0.0/0 y ::/0.

### Resultado obtenido
Redes rechazadas.

### Evidencia
`EV-029-remote-server-config-output.txt`.

---

## TC-188 — Rechazar CIDR inválido

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Configuración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Rechazar CIDR inválido.

### Procedimiento
`python test/test_remote_server_config.py` Consultar el caso TC-188 en la evidencia correspondiente.

### Resultado esperado
Rechazar 127.0.0.0/99.

### Resultado obtenido
CIDR inválido rechazado.

### Evidencia
`EV-029-remote-server-config-output.txt`.

---

## TC-189 — Rechazar puertos fuera de rango

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Configuración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Rechazar puertos fuera de rango.

### Procedimiento
`python test/test_remote_server_config.py` Consultar el caso TC-189 en la evidencia correspondiente.

### Resultado esperado
Rechazar puertos 0, -1 y 65536.

### Resultado obtenido
Valores rechazados.

### Evidencia
`EV-029-remote-server-config-output.txt`.

---

## TC-190 — Rechazar límites globales inválidos

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Configuración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Rechazar límites globales inválidos.

### Procedimiento
`python test/test_remote_server_config.py` Consultar el caso TC-190 en la evidencia correspondiente.

### Resultado esperado
Rechazar límites globales 0, 65 y True.

### Resultado obtenido
Valores rechazados.

### Evidencia
`EV-029-remote-server-config-output.txt`.

---

## TC-191 — Rechazar límites por IP inválidos

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Configuración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Rechazar límites por IP inválidos.

### Procedimiento
`python test/test_remote_server_config.py` Consultar el caso TC-191 en la evidencia correspondiente.

### Resultado esperado
Rechazar límites por IP 0, 65 y True.

### Resultado obtenido
Valores rechazados.

### Evidencia
`EV-029-remote-server-config-output.txt`.

---

## TC-192 — Aceptar límites exactos de configuración

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Configuración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Aceptar límites exactos de configuración.

### Procedimiento
`python test/test_remote_server_config.py` Consultar el caso TC-192 en la evidencia correspondiente.

### Resultado esperado
Aceptar límites de conexión 1 y 64; puertos 1 y 65535.

### Resultado obtenido
Valores límite aceptados.

### Evidencia
`EV-029-remote-server-config-output.txt`.

---

## TC-193 — Configuración inválida rechazada por entry point

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Configuración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Configuración inválida rechazada por entry point.

### Procedimiento
`python test/test_remote_server_config.py` Consultar el caso TC-193 en la evidencia correspondiente.

### Resultado esperado
Entry point con escucha comodín devuelve 2 sin traceback ni socket.

### Resultado obtenido
Configuración inválida rechazada.

### Evidencia
`EV-029-remote-server-config-output.txt`.

---

## TC-194 — Daemon local operativo sin listener TCP y limpieza al apagar

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Configuración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Daemon local operativo sin listener TCP y limpieza al apagar.

### Procedimiento
`python test/test_remote_server_config.py` Consultar el caso TC-194 en la evidencia correspondiente.

### Resultado esperado
Health UNIX operativo sin listener TCP; socket eliminado al apagar.

### Resultado obtenido
Puerto libre y limpieza correcta.

### Evidencia
`EV-029-remote-server-config-output.txt`.

---

## TC-195 — Daemon TCP en IP concreta, IPC local y limpieza al apagar

**Requisito relacionado:** PR #135 / RF-16 (protocolo y configuración remota)
**Tipo:** Automatizada / Configuración
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Daemon TCP en IP concreta, IPC local y limpieza al apagar.

### Procedimiento
`python test/test_remote_server_config.py` Consultar el caso TC-195 en la evidencia correspondiente.

### Resultado esperado
Health UNIX/TCP y listener exclusivo 127.0.0.1; cierre de ambos endpoints.

### Resultado obtenido
Ambos transportes operativos y limpieza correcta.

### Evidencia
`EV-029-remote-server-config-output.txt`.

---

## TC-196 — Health remoto y local equivalentes

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / CLI
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Health remoto y local equivalentes.

### Procedimiento
`python test/test_remote_cli.py` Consultar el caso TC-196 en la evidencia correspondiente.

### Resultado esperado
Health local y remoto equivalentes con rc 0.

### Resultado obtenido
Ambas respuestas equivalentes.

### Evidencia
`EV-030-remote-cli-output.txt`.

---

## TC-197 — Run remoto genera ID corto y ejecuta trabajo

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / CLI
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Run remoto genera ID corto y ejecuta trabajo.

### Procedimiento
`python test/test_remote_cli.py` Consultar el caso TC-197 en la evidencia correspondiente.

### Resultado esperado
Run remoto devuelve ID corto y trabajo SUCCEEDED.

### Resultado obtenido
Trabajo bash exitoso con ID corto.

### Evidencia
`EV-030-remote-cli-output.txt`.

---

## TC-198 — List remoto comparte trabajos con UNIX

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / CLI
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: List remoto comparte trabajos con UNIX.

### Procedimiento
`python test/test_remote_cli.py` Consultar el caso TC-198 en la evidencia correspondiente.

### Resultado esperado
List UNIX y TCP muestran los mismos trabajos.

### Resultado obtenido
Listados coincidentes.

### Evidencia
`EV-030-remote-cli-output.txt`.

---

## TC-199 — List remoto --full-id muestra UUID

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / CLI
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: List remoto --full-id muestra UUID.

### Procedimiento
`python test/test_remote_cli.py` Consultar el caso TC-199 en la evidencia correspondiente.

### Resultado esperado
List --full-id muestra UUID completo.

### Resultado obtenido
UUID completo observado.

### Evidencia
`EV-030-remote-cli-output.txt`.

---

## TC-200 — Status remoto mediante ID corto y paridad local

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / CLI
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Status remoto mediante ID corto y paridad local.

### Procedimiento
`python test/test_remote_cli.py` Consultar el caso TC-200 en la evidencia correspondiente.

### Resultado esperado
Status con ID corto conserva paridad UNIX/TCP.

### Resultado obtenido
Metadatos coincidentes.

### Evidencia
`EV-030-remote-cli-output.txt`.

---

## TC-201 — Status remoto mediante UUID completo

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / CLI
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Status remoto mediante UUID completo.

### Procedimiento
`python test/test_remote_cli.py` Consultar el caso TC-201 en la evidencia correspondiente.

### Resultado esperado
Status acepta UUID completo.

### Resultado obtenido
Trabajo correcto recuperado.

### Evidencia
`EV-030-remote-cli-output.txt`.

---

## TC-202 — Output remoto conserva stdout y stderr

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / CLI
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Output remoto conserva stdout y stderr.

### Procedimiento
`python test/test_remote_cli.py` Consultar el caso TC-202 en la evidencia correspondiente.

### Resultado esperado
Output conserva stdout y stderr separados.

### Resultado obtenido
hola remoto / error de prueba, rc 0.

### Evidencia
`EV-030-remote-cli-output.txt`.

---

## TC-203 — List remoto aplica filtro por estado

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / CLI
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: List remoto aplica filtro por estado.

### Procedimiento
`python test/test_remote_cli.py` Consultar el caso TC-203 en la evidencia correspondiente.

### Resultado esperado
Filtrar SUCCEEDED y FAILED correctamente.

### Resultado obtenido
Filtro exitoso muestra trabajo; FAILED vacío.

### Evidencia
`EV-030-remote-cli-output.txt`.

---

## TC-204 — Trabajo remoto cancelado y consultado localmente

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / CLI
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Trabajo remoto cancelado y consultado localmente.

### Procedimiento
`python test/test_remote_cli.py` Consultar el caso TC-204 en la evidencia correspondiente.

### Resultado esperado
Cancelar por TCP y consultar CANCELED por UNIX.

### Resultado obtenido
CANCELED, código del trabajo -15.

### Evidencia
`EV-030-remote-cli-output.txt`.

---

## TC-205 — Trabajo local consultado por TCP

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / CLI
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Trabajo local consultado por TCP.

### Procedimiento
`python test/test_remote_cli.py` Consultar el caso TC-205 en la evidencia correspondiente.

### Resultado esperado
Crear true por UNIX y consultar por TCP.

### Resultado obtenido
SUCCEEDED, código 0.

### Evidencia
`EV-030-remote-cli-output.txt`.

---

## TC-206 — Cancelación repetida controlada

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / CLI
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Cancelación repetida controlada.

### Procedimiento
`python test/test_remote_cli.py` Consultar el caso TC-206 en la evidencia correspondiente.

### Resultado esperado
Segunda cancelación rechazada con rc 1 sin cambiar estado.

### Resultado obtenido
Error controlado; CANCELED conservado.

### Evidencia
`EV-030-remote-cli-output.txt`.

---

## TC-207 — ID inexistente devuelve error controlado

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / CLI
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: ID inexistente devuelve error controlado.

### Procedimiento
`python test/test_remote_cli.py` Consultar el caso TC-207 en la evidencia correspondiente.

### Resultado esperado
ID inexistente devuelve error controlado.

### Resultado obtenido
rc 1, causa y sugerencia.

### Evidencia
`EV-030-remote-cli-output.txt`.

---

## TC-208 — ID inválido devuelve error controlado

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / CLI
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: ID inválido devuelve error controlado.

### Procedimiento
`python test/test_remote_cli.py` Consultar el caso TC-208 en la evidencia correspondiente.

### Resultado esperado
ID zzzzzzzz rechazado de forma controlada.

### Resultado obtenido
rc 1, explicación de formato.

### Evidencia
`EV-030-remote-cli-output.txt`.

---

## TC-209 — JOBSY_HOST y JOBSY_PORT seleccionan TCP

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / CLI
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: JOBSY_HOST y JOBSY_PORT seleccionan TCP.

### Procedimiento
`python test/test_remote_cli.py` Consultar el caso TC-209 en la evidencia correspondiente.

### Resultado esperado
JOBSY_HOST y JOBSY_PORT seleccionan TCP sin flags.

### Resultado obtenido
List remoto correcto.

### Evidencia
`EV-030-remote-cli-output.txt`.

---

## TC-210 — Opciones explícitas prevalecen sobre entorno

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / CLI
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Opciones explícitas prevalecen sobre entorno.

### Procedimiento
`python test/test_remote_cli.py` Consultar el caso TC-210 en la evidencia correspondiente.

### Resultado esperado
Flags explícitos prevalecen sobre entorno con valores válidos.

### Resultado obtenido
Health correcto.

### Evidencia
`EV-030-remote-cli-output.txt`.

---

## TC-211 — Servidor no disponible devuelve error controlado

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / CLI
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Servidor no disponible devuelve error controlado.

### Procedimiento
`python test/test_remote_cli.py` Consultar el caso TC-211 en la evidencia correspondiente.

### Resultado esperado
Puerto sin servidor produce error controlado.

### Resultado obtenido
rc 1, causa y sugerencia.

### Evidencia
`EV-030-remote-cli-output.txt`.

---

## TC-212 — Puerto explícito inválido devuelve error de sintaxis

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / CLI
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Puerto explícito inválido devuelve error de sintaxis.

### Procedimiento
`python test/test_remote_cli.py` Consultar el caso TC-212 en la evidencia correspondiente.

### Resultado esperado
Puertos explícitos 0, 65536 y abc devuelven 2.

### Resultado obtenido
Los tres rechazados sin traceback.

### Evidencia
`EV-030-remote-cli-output.txt`.

---

## TC-213 — JOBSY_PORT no numérico sin traceback

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / CLI
**Prioridad:** Alta
**Estado:** `FAIL`

### Objetivo
Verificar: JOBSY_PORT no numérico sin traceback.

### Procedimiento
`python test/test_remote_cli.py` Consultar el caso TC-213 en la evidencia correspondiente.

### Resultado esperado
JOBSY_PORT=abc debe producir error controlado sin traceback.

### Resultado obtenido
rc 1 y traceback ValueError en cli.py:29; INC-002 (OBS-05).

### Evidencia
`EV-030-remote-cli-output.txt` y `EV-035-regression-output.txt` (fallo reproducido).

---

## TC-214 — Daemon permanece operativo tras errores

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / CLI
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Daemon permanece operativo tras errores.

### Procedimiento
`python test/test_remote_cli.py` Consultar el caso TC-214 en la evidencia correspondiente.

### Resultado esperado
Health local y remoto siguen operativos tras errores.

### Resultado obtenido
Ambos responden rc 0.

### Evidencia
`EV-030-remote-cli-output.txt`.

---

## TC-215 — No registrar argumentos locales

**Requisito relacionado:** RNF-15
**Tipo:** Automatizada / Seguridad
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: No registrar argumentos locales.

### Procedimiento
`python test/test_remote_security.py` Consultar el caso TC-215 en la evidencia correspondiente.

### Resultado esperado
Argumento ficticio local ausente del log, disponible en salida.

### Resultado obtenido
Marcador ausente en bitácora y presente en output.

### Evidencia
`EV-031-remote-security-output.txt`.

---

## TC-216 — No registrar argumentos remotos

**Requisito relacionado:** RNF-15
**Tipo:** Automatizada / Seguridad
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: No registrar argumentos remotos.

### Procedimiento
`python test/test_remote_security.py` Consultar el caso TC-216 en la evidencia correspondiente.

### Resultado esperado
Argumento ficticio remoto ausente del log, disponible en salida.

### Resultado obtenido
Marcador ausente en bitácora y presente en output.

### Evidencia
`EV-031-remote-security-output.txt`.

---

## TC-217 — Sanitizar secretos clave=valor

**Requisito relacionado:** RNF-15
**Tipo:** Automatizada / Seguridad
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Sanitizar secretos clave=valor.

### Procedimiento
`python test/test_remote_security.py` Consultar el caso TC-217 en la evidencia correspondiente.

### Resultado esperado
Ocultar DB_PASSWORD=QA_FAKE_217.

### Resultado obtenido
DB_PASSWORD=[REDACTADO].

### Evidencia
`EV-031-remote-security-output.txt`.

---

## TC-218 — Sanitizar opciones con secretos

**Requisito relacionado:** RNF-15
**Tipo:** Automatizada / Seguridad
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Sanitizar opciones con secretos.

### Procedimiento
`python test/test_remote_security.py` Consultar el caso TC-218 en la evidencia correspondiente.

### Resultado esperado
Ocultar --api-key QA_FAKE_218.

### Resultado obtenido
--api-key [REDACTADO].

### Evidencia
`EV-031-remote-security-output.txt`.

---

## TC-219 — Sanitizar autorización HTTP Bearer

**Requisito relacionado:** RNF-15
**Tipo:** Automatizada / Seguridad
**Prioridad:** Alta
**Estado:** `FAIL`

### Objetivo
Verificar: Sanitizar autorización HTTP Bearer.

### Procedimiento
`python test/test_remote_security.py` Consultar el caso TC-219 en la evidencia correspondiente.

### Resultado esperado
Ocultar por completo Authorization: Bearer QA_FAKE_219.

### Resultado obtenido
Authorization=[REDACTADO] QA_FAKE_219; INC-003.

### Evidencia
`EV-031-remote-security-output.txt` y `EV-035-regression-output.txt` (fallo reproducido).

---

## TC-220 — Crear jobsy.log con permisos 0600

**Requisito relacionado:** RNF-15
**Tipo:** Automatizada / Seguridad
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Crear jobsy.log con permisos 0600.

### Procedimiento
`python test/test_remote_security.py` Consultar el caso TC-220 en la evidencia correspondiente.

### Resultado esperado
Crear jobsy.log con modo 0600.

### Resultado obtenido
0600 observado.

### Evidencia
`EV-031-remote-security-output.txt`.

---

## TC-221 — Corregir permisos de bitácora existente

**Requisito relacionado:** RNF-15
**Tipo:** Automatizada / Seguridad
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Corregir permisos de bitácora existente.

### Procedimiento
`python test/test_remote_security.py` Consultar el caso TC-221 en la evidencia correspondiente.

### Resultado esperado
Corregir permisos de bitácora existente a 0600.

### Resultado obtenido
0600 observado.

### Evidencia
`EV-031-remote-security-output.txt`.

---

## TC-222 — Usar bitácora de --data-dir

**Requisito relacionado:** RF-14 / RF-16
**Tipo:** Automatizada / Seguridad
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Usar bitácora de --data-dir.

### Procedimiento
`python test/test_remote_security.py` Consultar el caso TC-222 en la evidencia correspondiente.

### Resultado esperado
Crear jobsy.log en --data-dir.

### Resultado obtenido
Ruta configurada utilizada.

### Evidencia
`EV-031-remote-security-output.txt`.

---

## TC-223 — Registrar IP autorizada

**Requisito relacionado:** RF-14 / RF-16
**Tipo:** Automatizada / Seguridad
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Registrar IP autorizada.

### Procedimiento
`python test/test_remote_security.py` Consultar el caso TC-223 en la evidencia correspondiente.

### Resultado esperado
Registrar IP autorizada 127.0.0.1.

### Resultado obtenido
Evento de aceptación observado.

### Evidencia
`EV-031-remote-security-output.txt`.

---

## TC-224 — Rechazar conexión fuera de allowlist

**Requisito relacionado:** RF-14 / RF-16
**Tipo:** Automatizada / Seguridad
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Rechazar conexión fuera de allowlist.

### Procedimiento
`python test/test_remote_security.py` Consultar el caso TC-224 en la evidencia correspondiente.

### Resultado esperado
Rechazar cliente fuera de allowlist.

### Resultado obtenido
Health remoto rc 1, error controlado.

### Evidencia
`EV-031-remote-security-output.txt`.

---

## TC-225 — Registrar IP rechazada

**Requisito relacionado:** RF-14 / RF-16
**Tipo:** Automatizada / Seguridad
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Registrar IP rechazada.

### Procedimiento
`python test/test_remote_security.py` Consultar el caso TC-225 en la evidencia correspondiente.

### Resultado esperado
Registrar IP rechazada.

### Resultado obtenido
Evento de rechazo observado.

### Evidencia
`EV-031-remote-security-output.txt`.

---

## TC-226 — Daemon operativo después de rechazo

**Requisito relacionado:** RF-14 / RF-16
**Tipo:** Automatizada / Seguridad
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Daemon operativo después de rechazo.

### Procedimiento
`python test/test_remote_security.py` Consultar el caso TC-226 en la evidencia correspondiente.

### Resultado esperado
Health UNIX sigue activo tras rechazo.

### Resultado obtenido
rc 0, servicio activo.

### Evidencia
`EV-031-remote-security-output.txt`.

---

## TC-227 — Sanitizar respuestas de errores internos

**Requisito relacionado:** RNF-15
**Tipo:** Automatizada / Seguridad
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Sanitizar respuestas de errores internos.

### Procedimiento
`python test/test_remote_security.py` Consultar el caso TC-227 en la evidencia correspondiente.

### Resultado esperado
No exponer marcador de excepción simulada en respuesta.

### Resultado obtenido
INTERNAL_ERROR genérico sin marcador.

### Evidencia
`EV-031-remote-security-output.txt`.

---

## TC-228 — Evitar secretos en logs de excepciones internas

**Requisito relacionado:** RNF-15
**Tipo:** Automatizada / Seguridad
**Prioridad:** Alta
**Estado:** `FAIL`

### Objetivo
Verificar: Evitar secretos en logs de excepciones internas.

### Procedimiento
`python test/test_remote_security.py` Consultar el caso TC-228 en la evidencia correspondiente.

### Resultado esperado
No persistir marcador sensible ficticio de excepción en log.

### Resultado obtenido
QA_FAKE_INTERNAL_5828 presente; INC-004 (OBS-07).

### Evidencia
`EV-031-remote-security-output.txt` y `EV-035-regression-output.txt` (fallo reproducido).

---

## TC-229 — Solicitudes consecutivas en una conexión

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / Robustez
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Solicitudes consecutivas en una conexión.

### Procedimiento
`python test/test_remote_concurrency.py` Consultar el caso TC-229 en la evidencia correspondiente.

### Resultado esperado
Procesar solicitudes consecutivas en una conexión.

### Resultado obtenido
Respuestas válidas consecutivas.

### Evidencia
`EV-032-remote-concurrency-output.txt`.

---

## TC-230 — Tres clientes concurrentes crean trabajos independientes

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / Robustez
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Tres clientes concurrentes crean trabajos independientes.

### Procedimiento
`python test/test_remote_concurrency.py` Consultar el caso TC-230 en la evidencia correspondiente.

### Resultado esperado
Tres clientes concurrentes crean trabajos independientes con IDs únicos.

### Resultado obtenido
Tres trabajos independientes y IDs únicos.

### Evidencia
`EV-032-remote-concurrency-output.txt`.

---

## TC-231 — Errores recuperables conservan conexión

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / Robustez
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Errores recuperables conservan conexión.

### Procedimiento
`python test/test_remote_concurrency.py` Consultar el caso TC-231 en la evidencia correspondiente.

### Resultado esperado
Error recuperable no cierra conexión.

### Resultado obtenido
Solicitud posterior válida procesada.

### Evidencia
`EV-032-remote-concurrency-output.txt`.

---

## TC-232 — JSON inválido cierra solo al cliente afectado

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / Robustez
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: JSON inválido cierra solo al cliente afectado.

### Procedimiento
`python test/test_remote_concurrency.py` Consultar el caso TC-232 en la evidencia correspondiente.

### Resultado esperado
JSON inválido afecta solo la conexión que lo envía.

### Resultado obtenido
Otro cliente continúa operativo.

### Evidencia
`EV-032-remote-concurrency-output.txt`.

---

## TC-233 — Desconexiones abruptas no interrumpen trabajos

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / Robustez
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Desconexiones abruptas no interrumpen trabajos.

### Procedimiento
`python test/test_remote_concurrency.py` Consultar el caso TC-233 en la evidencia correspondiente.

### Resultado esperado
Trabajo continúa tras desconexión abrupta.

### Resultado obtenido
Trabajo finaliza correctamente.

### Evidencia
`EV-032-remote-concurrency-output.txt`.

---

## TC-234 — Límite por IP y recuperación de cupo

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / Robustez
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Límite por IP y recuperación de cupo.

### Procedimiento
`python test/test_remote_concurrency.py` Consultar el caso TC-234 en la evidencia correspondiente.

### Resultado esperado
Aplicar límite por IP y recuperar cupo al cerrar conexión.

### Resultado obtenido
Límite y recuperación comprobados.

### Evidencia
`EV-032-remote-concurrency-output.txt`.

---

## TC-235 — Límite global con distintas IP loopback

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / Robustez
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Límite global con distintas IP loopback.

### Procedimiento
`python test/test_remote_concurrency.py` Consultar el caso TC-235 en la evidencia correspondiente.

### Resultado esperado
Aplicar límite global con distintas IP loopback y recuperar cupo.

### Resultado obtenido
Límite y recuperación comprobados.

### Evidencia
`EV-032-remote-concurrency-output.txt`.

---

## TC-236 — Cliente lento no bloquea otro cliente

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / Robustez
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Cliente lento no bloquea otro cliente.

### Procedimiento
`python test/test_remote_concurrency.py` Consultar el caso TC-236 en la evidencia correspondiente.

### Resultado esperado
Cliente lento no bloquea health de otro cliente.

### Resultado obtenido
Health de otro cliente: 0.246 ms.

### Evidencia
`EV-032-remote-concurrency-output.txt`.

---

## TC-237 — Coexistencia de IPC UNIX y TCP

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / Robustez
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Coexistencia de IPC UNIX y TCP.

### Procedimiento
`python test/test_remote_concurrency.py` Consultar el caso TC-237 en la evidencia correspondiente.

### Resultado esperado
UNIX y TCP comparten servicio.

### Resultado obtenido
Ambos transportes operativos.

### Evidencia
`EV-032-remote-concurrency-output.txt`.

---

## TC-238 — Apagado con clientes activos

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / Robustez
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Apagado con clientes activos.

### Procedimiento
`python test/test_remote_concurrency.py` Consultar el caso TC-238 en la evidencia correspondiente.

### Resultado esperado
Apagar con clientes activos y cerrar endpoints.

### Resultado obtenido
Apagado 0.515 s, rc 0; OBS-08 no reproducida.

### Evidencia
`EV-032-remote-concurrency-output.txt`.

---

## TC-239 — CLI maneja respuesta exitosa incompleta

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Automatizada / Robustez
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: CLI maneja respuesta exitosa incompleta.

### Procedimiento
`python test/test_remote_concurrency.py` Consultar el caso TC-239 en la evidencia correspondiente.

### Resultado esperado
Respuesta exitosa incompleta genera rc distinto de 0 sin traceback.

### Resultado obtenido
rc 1, Error: 'jobs'; PASS según criterio, OBS-06 por mensaje poco informativo.

### Evidencia
`EV-032-remote-concurrency-output.txt`.

---

## TC-240 — Crear exactamente 100 trabajos mediante TCP

**Requisito relacionado:** RNF-05 (rendimiento; alcance loopback)
**Tipo:** Automatizada / Rendimiento
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Crear exactamente 100 trabajos mediante TCP.

### Procedimiento
`python test/test_remote_performance.py` Consultar el caso TC-240 en la evidencia correspondiente.

### Resultado esperado
Crear exactamente 100 trabajos por TCP.

### Resultado obtenido
100 trabajos creados.

### Evidencia
`EV-033-remote-performance-output.txt`.

---

## TC-241 — Verificar UUID únicos y listado completo

**Requisito relacionado:** RNF-05 (rendimiento; alcance loopback)
**Tipo:** Automatizada / Rendimiento
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Verificar UUID únicos y listado completo.

### Procedimiento
`python test/test_remote_performance.py` Consultar el caso TC-241 en la evidencia correspondiente.

### Resultado esperado
Verificar UUID únicos y listado de 100 trabajos.

### Resultado obtenido
100 UUID únicos y listado completo.

### Evidencia
`EV-033-remote-performance-output.txt`.

---

## TC-242 — Completar los 100 trabajos correctamente

**Requisito relacionado:** RNF-05 (rendimiento; alcance loopback)
**Tipo:** Automatizada / Rendimiento
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Completar los 100 trabajos correctamente.

### Procedimiento
`python test/test_remote_performance.py` Consultar el caso TC-242 en la evidencia correspondiente.

### Resultado esperado
Los 100 trabajos finalizan SUCCEEDED.

### Resultado obtenido
100 SUCCEEDED.

### Evidencia
`EV-033-remote-performance-output.txt`.

---

## TC-243 — Ejecutar 90 consultas status válidas

**Requisito relacionado:** RNF-05 (rendimiento; alcance loopback)
**Tipo:** Automatizada / Rendimiento
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Ejecutar 90 consultas status válidas.

### Procedimiento
`python test/test_remote_performance.py` Consultar el caso TC-243 en la evidencia correspondiente.

### Resultado esperado
Validar 90 respuestas status.

### Resultado obtenido
90 respuestas válidas.

### Evidencia
`EV-033-remote-performance-output.txt`.

---

## TC-244 — Latencia máxima status <= 1000 ms

**Requisito relacionado:** RNF-05 (rendimiento; alcance loopback)
**Tipo:** Automatizada / Rendimiento
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Latencia máxima status <= 1000 ms.

### Procedimiento
`python test/test_remote_performance.py` Consultar el caso TC-244 en la evidencia correspondiente.

### Resultado esperado
Latencia máxima status <= 1000 ms con 100 trabajos registrados.

### Resultado obtenido
Mínimo 0.078, mediana 0.101, máximo 0.711 ms.

### Evidencia
`EV-033-remote-performance-output.txt`.

---

## TC-245 — Medir list y health con 100 trabajos

**Requisito relacionado:** RNF-05 (rendimiento; alcance loopback)
**Tipo:** Automatizada / Rendimiento
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Medir list y health con 100 trabajos.

### Procedimiento
`python test/test_remote_performance.py` Consultar el caso TC-245 en la evidencia correspondiente.

### Resultado esperado
Medir 30 list y 30 health válidos con 100 trabajos.

### Resultado obtenido
List min/med/max 0.516/0.551/0.713 ms; health 0.073/0.123/0.299 ms.

### Evidencia
`EV-033-remote-performance-output.txt`.

---

## TC-246 — Daemon operativo después de la carga

**Requisito relacionado:** RNF-05 (rendimiento; alcance loopback)
**Tipo:** Automatizada / Rendimiento
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Daemon operativo después de la carga.

### Procedimiento
`python test/test_remote_performance.py` Consultar el caso TC-246 en la evidencia correspondiente.

### Resultado esperado
Daemon operativo por UNIX y TCP tras carga.

### Resultado obtenido
Ambos transportes operativos.

### Evidencia
`EV-033-remote-performance-output.txt`.

---

## TC-247 — Conectividad TCP

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Integración / LAN
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Conectividad TCP.

### Procedimiento
Ejecución manual LAN según EV-034. Consultar el caso TC-247 en la evidencia correspondiente.

### Resultado esperado
TCP accesible, nc rc 0.

### Resultado obtenido
nc -vz -w 5 192.168.100.64 8765
Connection to 192.168.100.64 8765 port [tcp/*] succeeded!
Exit code: 0

### Evidencia
`EV-034-remote-lan-output.txt`.

---

## TC-248 — Health remoto

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Integración / LAN
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Health remoto.

### Procedimiento
Ejecución manual LAN según EV-034. Consultar el caso TC-248 en la evidencia correspondiente.

### Resultado esperado
Health indica servicio activo y rc 0.

### Resultado obtenido
jobsy --host 192.168.100.64 --port 8765 health
Servicio Activo: Sí; ejecución 0; cola 0; errores recientes 0.
Código de salida de la primera consulta no capturado; nueva consulta tras restaurar allowlist: 0.

### Evidencia
`EV-034-remote-lan-output.txt`.

---

## TC-249 — Ejecución remota

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Integración / LAN
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Ejecución remota.

### Procedimiento
Ejecución manual LAN según EV-034. Consultar el caso TC-249 en la evidencia correspondiente.

### Resultado esperado
hostname ejecutado en PC A devuelve PCERDA.

### Resultado obtenido
run -- hostname; ID 1f92fc5e; output: PCERDA.

### Evidencia
`EV-034-remote-lan-output.txt`.

---

## TC-250 — Listado

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Integración / LAN
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Listado.

### Procedimiento
Ejecución manual LAN según EV-034. Consultar el caso TC-250 en la evidencia correspondiente.

### Resultado esperado
Mostrar ID corto y UUID completo.

### Resultado obtenido
ID corto: 1f92fc5e; UUID: 1f92fc5e-7c47-416f-b95c-410099284e2f.
Estado SUCCEEDED; comando hostname; ambos formatos observados.

### Evidencia
`EV-034-remote-lan-output.txt`.

---

## TC-251 — Estado

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Integración / LAN
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Estado.

### Procedimiento
Ejecución manual LAN según EV-034. Consultar el caso TC-251 en la evidencia correspondiente.

### Resultado esperado
Estado SUCCEEDED y código del trabajo 0.

### Resultado obtenido
status 1f92fc5e: SUCCEEDED; código de salida del trabajo 0.

### Evidencia
`EV-034-remote-lan-output.txt`.

---

## TC-252 — stdout/stderr

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Integración / LAN
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: stdout/stderr.

### Procedimiento
Ejecución manual LAN según EV-034. Consultar el caso TC-252 en la evidencia correspondiente.

### Resultado esperado
Recuperar stdout y stderr separados.

### Resultado obtenido
run -- bash -c 'echo QA_STDOUT_LAN; echo QA_STDERR_LAN >&2'
ID b1e687b4; output redirigido a archivos separados.
Exit code: 0; stdout QA_STDOUT_LAN; stderr QA_STDERR_LAN.

### Evidencia
`EV-034-remote-lan-output.txt`.

---

## TC-253 — Cancelación

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Integración / LAN
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Cancelación.

### Procedimiento
Ejecución manual LAN según EV-034. Consultar el caso TC-253 en la evidencia correspondiente.

### Resultado esperado
RUNNING cambia a CANCELED sin perder estado.

### Resultado obtenido
run -- sleep 120; ID 1398370e; RUNNING -> CANCELED.
Código de salida del trabajo: -15; diagnóstico: cancelado por solicitud del usuario.
OBS-09: bitácora dice 'Trabajo finalizado con estado fallido (exit_code=-15)' pese a CANCELED. No afecta el resultado funcional.

### Evidencia
`EV-034-remote-lan-output.txt`.

---

## TC-254 — Estado compartido UNIX/TCP

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Integración / LAN
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Estado compartido UNIX/TCP.

### Procedimiento
Ejecución manual LAN según EV-034. Consultar el caso TC-254 en la evidencia correspondiente.

### Resultado esperado
Trabajos visibles y consultables desde ambos transportes.

### Resultado obtenido
PC A: cliente UNIX lista trabajos remotos y consulta 1f92fc5e y 1398370e.
PC A crea echo QA_LOCAL_TO_REMOTE, ID 22ac66b1.
PC B consulta SUCCEEDED, código 0, output QA_LOCAL_TO_REMOTE.

### Evidencia
`EV-034-remote-lan-output.txt`.

---

## TC-255 — IP real

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Integración / LAN
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: IP real.

### Procedimiento
Ejecución manual LAN según EV-034. Consultar el caso TC-255 en la evidencia correspondiente.

### Resultado esperado
Log registra 192.168.100.151.

### Resultado obtenido
Bitácora: Conexión remota aceptada desde 192.168.100.151.

### Evidencia
`EV-034-remote-lan-output.txt`.

---

## TC-256 — Allowlist

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Integración / LAN
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Allowlist.

### Procedimiento
Ejecución manual LAN según EV-034. Consultar el caso TC-256 en la evidencia correspondiente.

### Resultado esperado
Excluir PC B, registrar rechazo y mantener UNIX; restaurar acceso.

### Resultado obtenido
Daemon escucha en 192.168.100.64:8765 con allowlist 127.0.0.1/32.
Health remoto: error controlado, código 1.
Bitácora: Conexión remota rechazada: 192.168.100.151 fuera de las redes permitidas.
Health local UNIX: activo, código 0. Al restaurar allowlist original, health remoto activo, código 0.

### Evidencia
`EV-034-remote-lan-output.txt`.

---

## TC-257 — Variables de entorno

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Integración / LAN
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Variables de entorno.

### Procedimiento
Ejecución manual LAN según EV-034. Consultar el caso TC-257 en la evidencia correspondiente.

### Resultado esperado
Operaciones sin flags usan host y puerto del entorno.

### Resultado obtenido
JOBSY_HOST=192.168.100.64; JOBSY_PORT=8765.
health, list --full-id, status 1f92fc5e y output 1f92fc5e funcionan sin flags.
Variables eliminadas posteriormente.

### Evidencia
`EV-034-remote-lan-output.txt`.

---

## TC-258 — Latencia LAN

**Requisito relacionado:** PR #135 / rendimiento LAN complementario (no RNF-05 completo)
**Tipo:** Integración / LAN
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Latencia LAN.

### Procedimiento
Ejecución manual LAN según EV-034. Consultar el caso TC-258 en la evidencia correspondiente.

### Resultado esperado
30 respuestas status válidas y máximo <= 1000 ms.

### Resultado obtenido
30 solicitudes status sobre conexión TCP persistente, 4 trabajos registrados.
Valores ms, en orden:
3.250, 2.768, 2.607, 2.952, 3.425, 2.304, 2.273, 3.187, 2.433, 2.262,
2.362, 2.918, 1.847, 2.929, 2.283, 2.404, 2.381, 2.362, 2.494, 2.933,
2.492, 2.898, 2.613, 2.267, 2.929, 2.842, 2.458, 2.408, 2.345, 2.571.
Consultas válidas: 30; mínimo 1.847 ms; mediana 2.493 ms; máximo 3.425 ms.
Criterio utilizado: 30 respuestas válidas y máximo <= 1000 ms.
No equivale a RNF-05 con 100 trabajos ni incluye establecimiento TCP o inicio CLI.

### Evidencia
`EV-034-remote-lan-output.txt`.

---

## TC-259 — Desconexión y recuperación

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Integración / LAN
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Desconexión y recuperación.

### Procedimiento
Ejecución manual LAN según EV-034. Consultar el caso TC-259 en la evidencia correspondiente.

### Resultado esperado
Cerrar conexión con trabajo RUNNING y verificar SUCCEEDED tras reconexión.

### Resultado obtenido
ID 1879fda6-15b6-4b68-a326-754a90b08957; RUNNING antes de cerrar TCP.
Conexión restablecida; SUCCEEDED; código 0.
Cierre controlado de conexión; no se simuló caída física de red.

### Evidencia
`EV-034-remote-lan-output.txt`.

---

## TC-260 — Apagado

**Requisito relacionado:** PR #135 / RF-16
**Tipo:** Integración / LAN
**Prioridad:** Alta
**Estado:** `PASS`

### Objetivo
Verificar: Apagado.

### Procedimiento
Ejecución manual LAN según EV-034. Consultar el caso TC-260 en la evidencia correspondiente.

### Resultado esperado
Apagado rc 0, clean=True, sin listener ni socket; cliente falla controladamente.

### Resultado obtenido
SIGINT; Acceso remoto detenido; clean=True; daemon exit code 0.
ss: sin listener en 8765; socket UNIX eliminado.
PC B nc: timeout, código 1; health: error controlado, código 1.
OBS-10: mensaje 'Servicio detenido completamente.' duplicado en tres sesiones observadas.

### Evidencia
`EV-034-remote-lan-output.txt`.

---

# Resumen de ejecución

| Caso | Descripción | Estado | Evidencia |
|---|---|---|---|
| TC-001 | Validar comando correcto | PASS | EV-001 |
| TC-002 | Rechazar comando vacío | PASS | EV-001 |
| TC-003 | Rechazar comando con formato incorrecto | PASS | EV-001 |
| TC-004 | Rechazar nombre de programa vacío | PASS | EV-001 |
| TC-005 | Rechazar argumentos no textuales | PASS | EV-001 |
| TC-006 | Generar IDs únicos | PASS | EV-002 |
| TC-007 | Ejecutar trabajo sin bloquear otros trabajos | PASS | EV-002 |
| TC-008 | Ejecutar trabajo exitosamente | PASS | EV-002 |
| TC-009 | Capturar stdout | PASS | EV-002 |
| TC-010 | Registrar código de salida exitoso | PASS | EV-002 |
| TC-011 | Ejecutar trabajo que termina con error | PASS | EV-002 |
| TC-012 | Capturar stderr | PASS | EV-002 |
| TC-013 | Registrar código de salida de error | PASS | EV-002 |
| TC-014 | Registrar tiempos del ciclo de vida | PASS | EV-002 |
| TC-015 | Consultar trabajo con ID válido | PASS | EV-003 |
| TC-016 | Consultar trabajo con ID inexistente | PASS | EV-003 |
| TC-017 | Listar trabajos y filtrar por estado | PASS | EV-003 |
| TC-018 | Cancelar trabajo en estado QUEUED | PASS | EV-004 |
| TC-019 | Cancelar trabajo en estado RUNNING | PASS | EV-004 |
| TC-020 | Cancelar trabajo con ID inexistente | PASS | EV-004 |
| TC-021 | Rechazar cancelación de trabajo finalizado | PASS | EV-004 |
| TC-022 | Rechazar segunda cancelación del mismo trabajo | PASS | EV-004 |
| TC-023 | Inicializar servicio | PASS | EV-005 |
| TC-024 | Apagar servicio con trabajo QUEUED | PASS | EV-005 |
| TC-025 | Apagar servicio con trabajo RUNNING | PASS | EV-005 |
| TC-026 | Rechazar nuevos trabajos después del shutdown | PASS | EV-005 |
| TC-027 | Apagar servicio mediante señal | PASS | EV-005 |
| TC-028 | Forzar cancelación al agotarse el tiempo de shutdown | PASS | EV-005 |
| TC-029 | Mostrar ayuda al ejecutar CLI sin argumentos | PASS | EV-006 |
| TC-030 | Ejecutar comando válido desde la CLI | PASS | EV-006 |
| TC-031 | Listar trabajos desde la CLI | PASS | EV-006 |
| TC-032 | Consultar estado desde la CLI | PASS | EV-006 |
| TC-033 | Cancelar trabajo desde la CLI | PASS | EV-006 |
| TC-034 | Consultar ID inexistente desde la CLI | PASS | EV-006 |
| TC-035 | Rechazar filtro de estado inválido en la CLI | PASS | EV-006 |
| TC-036 | Rechazar subcomando inválido | PASS | EV-006 |
| TC-037 | Iniciar daemon y crear socket UNIX | PASS | EV-007 |
| TC-038 | Enviar trabajo mediante CLI e IPC | PASS | EV-007 |
| TC-039 | Consultar trabajo mediante IPC | PASS | EV-007 |
| TC-040 | Listar trabajos persistentes durante la sesión | PASS | EV-007 |
| TC-041 | Cancelar trabajo mediante IPC | PASS | EV-007 |
| TC-042 | Consultar ID inexistente mediante IPC | PASS | EV-007 |
| TC-043 | Ejecutar CLI sin daemon activo | PASS | EV-008 |
| TC-044 | Cancelar ID inexistente mediante IPC | PASS | EV-008 |
| TC-045 | Filtrar trabajos por estado mediante IPC | PASS | EV-008 |
| TC-046 | Enviar acción IPC inválida | PASS | EV-008 |
| TC-047 | Enviar JSON inválido | PASS | EV-008 |
| TC-048 | Mantener daemon operativo después de solicitudes inválidas | PASS | EV-008 |
| TC-049 | Eliminar socket durante el apagado del daemon | PASS | EV-008 |
| TC-050 | Ejecutar múltiples trabajos mediante IPC | PASS | EV-009 |
| TC-051 | Verificar IDs únicos en múltiples trabajos | PASS | EV-009 |
| TC-052 | Conservar múltiples trabajos durante la sesión | PASS | EV-009 |
| TC-053 | Utilizar socket UNIX predeterminado | PASS | EV-010 |
| TC-054 | Aceptar una ruta absoluta personalizada para el socket | PASS | EV-010 |
| TC-055 | Utilizar JOBSY_SOCKET_PATH desde la CLI | PASS | EV-010 |
| TC-056 | Ejecutar operaciones mediante un socket personalizado | PASS | EV-010 |
| TC-057 | Rechazar una ruta relativa de socket | PASS | EV-010 |
| TC-058 | Rechazar un directorio padre inexistente | PASS | EV-010 |
| TC-059 | Rechazar un enlace simbólico como ruta final del socket | PASS | EV-010 |
| TC-060 | Rechazar una ruta de socket mayor a 107 bytes | PASS | EV-010 |
| TC-061 | No sobrescribir una ruta de socket existente | PASS | EV-010 |
| TC-062 | Volver al socket predeterminado sin JOBSY_SOCKET_PATH | PASS | EV-010 |
| TC-063 | Verificar que el daemon ignore JOBSY_SOCKET_PATH | PASS | EV-011 |
| TC-064 | Rechazar JOBSY_SOCKET_PATH vacío | PASS | EV-011 |
| TC-065 | Devolver código 2 ante socket inválido del daemon | PASS | EV-011 |
| TC-066 | Devolver código 1 cuando el endpoint no tiene servicio | PASS | EV-011 |
| TC-067 | Expandir ~ en la ruta personalizada del socket | PASS | EV-011 |
| TC-068 | Iniciar jobsy-daemon con un socket personalizado | PASS | EV-011 |
| TC-069 | Utilizar JOBSY_SOCKET_PATH desde puntos de entrada públicos | PASS | EV-011 |
| TC-070 | Utilizar JOBSY_SOCKET_PATH desde execute | PASS | EV-011 |
| TC-071 | Separar stdout y stderr | PASS | EV-012 |
| TC-072 | Recuperar stdout mayor a 4096 bytes | PASS | EV-012 |
| TC-073 | Recuperar stderr mayor a 4096 bytes | PASS | EV-012 |
| TC-074 | Mantener vacío el stream no utilizado | PASS | EV-012 |
| TC-075 | Devolver código 0 al consultar output correctamente | PASS | EV-012 |
| TC-076 | Crear cada trabajo en su propio grupo de procesos | PASS | EV-013 |
| TC-077 | Mantener procesos hijos en el mismo grupo | PASS | EV-013 |
| TC-078 | Cancelar proceso principal y descendientes | PASS | EV-013 |
| TC-079 | Mantener daemon operativo después de cancelar un grupo | PASS | EV-013 |
| TC-080 | Cancelar un trabajo por primera vez | PASS | EV-014 |
| TC-081 | Rechazar una segunda cancelación con mensaje claro | PASS | EV-014 |
| TC-082 | Aceptar cancel-grace entero válido | PASS | EV-015 |
| TC-083 | Aceptar cancel-grace fraccionario válido | PASS | EV-015 |
| TC-084 | Rechazar cancel-grace igual a cero | PASS | EV-015 |
| TC-085 | Rechazar cancel-grace negativo | PASS | EV-015 |
| TC-086 | Rechazar cancel-grace mayor a 60 | PASS | EV-015 |
| TC-087 | Escalar de SIGTERM a SIGKILL | PASS | EV-015 |
| TC-088 | Aislar un fallo de cleanup | PASS | EV-016 |
| TC-089 | Mantener scheduler responsivo durante cleanup fallido | PASS | EV-016 |
| TC-090 | Finalizar de forma controlada tras fallo de cleanup | PASS | EV-016 |
| TC-091 | List duplicado no altera el estado | PASS | EV-017 |
| TC-092 | Status duplicado conserva metadatos | PASS | EV-017 |
| TC-093 | Output duplicado conserva stdout y stderr | PASS | EV-017 |
| TC-094 | Cancel duplicado no genera segunda transición | PASS | EV-017 |
| TC-095 | Cancel duplicado conserva estado y timestamps | PASS | EV-017 |
| TC-096 | Run duplicado crea UUID diferentes | PASS | EV-017 |
| TC-097 | Run duplicado crea trabajos independientes | PASS | EV-017 |
| TC-098 | Daemon sigue operativo tras solicitudes duplicadas | PASS | EV-017 |
| TC-099 | Health responde con estructura esperada | PASS | EV-018 |
| TC-100 | Health reporta servicio activo | PASS | EV-018 |
| TC-101 | Health reporta trabajo RUNNING | PASS | EV-018 |
| TC-102 | Health reporta trabajo QUEUED | PASS | EV-018 |
| TC-103 | Health reporta errores recientes | PASS | EV-018 |
| TC-104 | Health limita errores recientes a 10 | PASS | EV-018 |
| TC-105 | Health es operación de solo lectura | PASS | EV-018 |
| TC-106 | Daemon sigue operativo después de health | PASS | EV-018 |
| TC-107 | Acción IPC inválida devuelve error estructurado | PASS | EV-019 |
| TC-108 | JSON inválido devuelve error estructurado | PASS | EV-019 |
| TC-109 | Status de ID inexistente devuelve error estructurado | PASS | EV-019 |
| TC-110 | Cancel de ID inexistente devuelve error estructurado | PASS | EV-019 |
| TC-111 | Cola llena devuelve causa y sugerencia | PASS | EV-019 |
| TC-112 | CLI presenta el error estructurado | PASS | EV-019 |
| TC-113 | Daemon sigue operativo después de errores | PASS | EV-019 |
| TC-114 | jobsy.log se crea en el data-dir | PASS | EV-020 |
| TC-115 | Formato básico de la bitácora | PASS | EV-020 |
| TC-116 | Cada solicitud IPC recibe ReqID | PASS | EV-020 |
| TC-117 | Solicitudes distintas reciben ReqID diferentes | PASS | EV-020 |
| TC-118 | Eventos de trabajo incluyen Job ID | PASS | EV-020 |
| TC-119 | ReqID correlaciona el ciclo de la solicitud run | PASS | EV-020 |
| TC-120 | Bitácora persiste y daemon sigue operativo | PASS | EV-020 |
| TC-121 | Cola llena queda registrada en jobsy.log | PASS | EV-021 |
| TC-122 | Rechazo por cola llena incluye ReqID | PASS | EV-021 |
| TC-123 | Desconexión prematura del cliente queda registrada | PASS | EV-021 |
| TC-124 | Log indica estado de operación tras desconexión | PASS | EV-021 |
| TC-125 | Daemon sobrevive a desconexión del cliente | PASS | EV-021 |
| TC-126 | Solicitud posterior sigue funcionando | PASS | EV-021 |
| TC-127 | Conservar trabajo terminal tras reinicio | PASS | EV-022 |
| TC-128 | Conservar stdout y stderr tras reinicio | PASS | EV-022 |
| TC-129 | Recuperar trabajo pendiente como CANCELED | PASS | EV-022 |
| TC-130 | Recuperar ejecución interrumpida como FAILED | PASS | EV-022 |
| TC-131 | No reejecutar automáticamente trabajo interrumpido | PASS | EV-022 |
| TC-132 | No ejecutar automáticamente trabajo pendiente | PASS | EV-022 |
| TC-133 | Mantener daemon operativo después de recuperación | PASS | EV-022 |
| TC-134 | Aceptar carga de 120 trabajos | PASS | EV-023 |
| TC-135 | Finalizar todos los trabajos de la carga | PASS | EV-023 |
| TC-136 | Liberar procesos hijos después de la carga | PASS | EV-023 |
| TC-137 | Liberar descriptores de archivo | PASS | EV-023 |
| TC-138 | Estabilizar memoria después del estrés | PASS | EV-023 |
| TC-139 | Mantener daemon operativo después del estrés | PASS | EV-023 |
| TC-140 | Liberar socket al apagar el daemon | PASS | EV-023 |
| TC-141 | Crear clon limpio del repositorio | PASS | EV-024 |
| TC-142 | Crear entorno virtual nuevo | PASS | EV-024 |
| TC-143 | Instalar Jobsy sin privilegios root | PASS | EV-024 |
| TC-144 | Instalar sin warnings ni errores | PASS | EV-024 |
| TC-145 | Instalar puntos de entrada públicos | PASS | EV-024 |
| TC-146 | Verificar instalación nueva operativa | PASS | EV-024 |
| TC-147 | Batería disponible mediante un único comando | PASS | EV-025 |
| TC-148 | Scripts de la batería finalizan correctamente | PASS | EV-025 |
| TC-149 | Resultado agregado de la batería | PASS | EV-025 |
| TC-150 | Run muestra ID corto de 8 caracteres | PASS | EV-026 |
| TC-151 | List muestra IDs cortos por defecto | PASS | EV-026 |
| TC-152 | List --full-id muestra UUID completo | PASS | EV-026 |
| TC-153 | Status acepta ID corto válido | PASS | EV-026 |
| TC-154 | Output acepta ID corto válido | PASS | EV-026 |
| TC-155 | Cancel acepta ID corto válido | PASS | EV-026 |
| TC-156 | Status conserva compatibilidad con UUID completo | PASS | EV-026 |
| TC-157 | Resolver prefijo hexadecimal de más de 8 caracteres | PASS | EV-026 |
| TC-158 | Resolver ID corto escrito en mayúsculas | PASS | EV-026 |
| TC-159 | Rechazar ID corto inexistente de forma controlada | PASS | EV-026 |
| TC-160 | Rechazar prefijo menor a 8 caracteres | PASS | EV-026 |
| TC-161 | Rechazar ID con caracteres no hexadecimales | PASS | EV-026 |
| TC-162 | Rechazar prefijo ambiguo sin elegir arbitrariamente | PASS | EV-026 |
| TC-163 | Resolver ID corto de un trabajo terminal | PASS | EV-026 |
| TC-164 | Health muestra IDs cortos | PASS | EV-026 |
| TC-165 | Cabecera de cuatro bytes y JSON UTF-8 | PASS | EV-028 |
| TC-166 | Fragmentación byte a byte con Unicode | PASS | EV-028 |
| TC-167 | Tramas agrupadas y EOF limpio | PASS | EV-028 |
| TC-168 | Envío parcial sin pérdida de datos | PASS | EV-028 |
| TC-169 | Rechazo de longitudes fuera del límite | PASS | EV-028 |
| TC-170 | Aceptación de los límites exactos de framing | PASS | EV-028 |
| TC-171 | Detección de cabecera o cuerpo incompleto | PASS | EV-028 |
| TC-172 | Timeout de lectura e inactividad | PASS | EV-028 |
| TC-173 | Plazo absoluto ante tráfico fragmentado lento | PASS | EV-028 |
| TC-174 | Rechazo de codificación inválida | PASS | EV-028 |
| TC-175 | JSON inválido y límite de profundidad | PASS | EV-028 |
| TC-176 | Validación de versión del protocolo | PASS | EV-028 |
| TC-177 | Validación de request_id | PASS | EV-028 |
| TC-178 | Validación de acciones y parámetros | PASS | EV-028 |
| TC-179 | Validación de sobres de respuesta y correlación | PASS | EV-028 |
| TC-180 | Rechazo de respuesta superior a 1 MiB | PASS | EV-028 |
| TC-181 | Acceso remoto deshabilitado por defecto | PASS | EV-029 |
| TC-182 | Aceptar IP privada y allowlist múltiple | PASS | EV-029 |
| TC-183 | Rechazar direcciones comodín IPv4 e IPv6 | PASS | EV-029 |
| TC-184 | Rechazar IP pública de escucha | PASS | EV-029 |
| TC-185 | Rechazar hostname y dirección inválida | PASS | EV-029 |
| TC-186 | Exigir allowlist al habilitar TCP | PASS | EV-029 |
| TC-187 | Rechazar redes públicas y rutas universales | PASS | EV-029 |
| TC-188 | Rechazar CIDR inválido | PASS | EV-029 |
| TC-189 | Rechazar puertos fuera de rango | PASS | EV-029 |
| TC-190 | Rechazar límites globales inválidos | PASS | EV-029 |
| TC-191 | Rechazar límites por IP inválidos | PASS | EV-029 |
| TC-192 | Aceptar límites exactos de configuración | PASS | EV-029 |
| TC-193 | Configuración inválida rechazada por entry point | PASS | EV-029 |
| TC-194 | Daemon local operativo sin listener TCP y limpieza al apagar | PASS | EV-029 |
| TC-195 | Daemon TCP en IP concreta, IPC local y limpieza al apagar | PASS | EV-029 |
| TC-196 | Health remoto y local equivalentes | PASS | EV-030 |
| TC-197 | Run remoto genera ID corto y ejecuta trabajo | PASS | EV-030 |
| TC-198 | List remoto comparte trabajos con UNIX | PASS | EV-030 |
| TC-199 | List remoto --full-id muestra UUID | PASS | EV-030 |
| TC-200 | Status remoto mediante ID corto y paridad local | PASS | EV-030 |
| TC-201 | Status remoto mediante UUID completo | PASS | EV-030 |
| TC-202 | Output remoto conserva stdout y stderr | PASS | EV-030 |
| TC-203 | List remoto aplica filtro por estado | PASS | EV-030 |
| TC-204 | Trabajo remoto cancelado y consultado localmente | PASS | EV-030 |
| TC-205 | Trabajo local consultado por TCP | PASS | EV-030 |
| TC-206 | Cancelación repetida controlada | PASS | EV-030 |
| TC-207 | ID inexistente devuelve error controlado | PASS | EV-030 |
| TC-208 | ID inválido devuelve error controlado | PASS | EV-030 |
| TC-209 | JOBSY_HOST y JOBSY_PORT seleccionan TCP | PASS | EV-030 |
| TC-210 | Opciones explícitas prevalecen sobre entorno | PASS | EV-030 |
| TC-211 | Servidor no disponible devuelve error controlado | PASS | EV-030 |
| TC-212 | Puerto explícito inválido devuelve error de sintaxis | PASS | EV-030 |
| TC-213 | JOBSY_PORT no numérico sin traceback | FAIL | EV-030 |
| TC-214 | Daemon permanece operativo tras errores | PASS | EV-030 |
| TC-215 | No registrar argumentos locales | PASS | EV-031 |
| TC-216 | No registrar argumentos remotos | PASS | EV-031 |
| TC-217 | Sanitizar secretos clave=valor | PASS | EV-031 |
| TC-218 | Sanitizar opciones con secretos | PASS | EV-031 |
| TC-219 | Sanitizar autorización HTTP Bearer | FAIL | EV-031 |
| TC-220 | Crear jobsy.log con permisos 0600 | PASS | EV-031 |
| TC-221 | Corregir permisos de bitácora existente | PASS | EV-031 |
| TC-222 | Usar bitácora de --data-dir | PASS | EV-031 |
| TC-223 | Registrar IP autorizada | PASS | EV-031 |
| TC-224 | Rechazar conexión fuera de allowlist | PASS | EV-031 |
| TC-225 | Registrar IP rechazada | PASS | EV-031 |
| TC-226 | Daemon operativo después de rechazo | PASS | EV-031 |
| TC-227 | Sanitizar respuestas de errores internos | PASS | EV-031 |
| TC-228 | Evitar secretos en logs de excepciones internas | FAIL | EV-031 |
| TC-229 | Solicitudes consecutivas en una conexión | PASS | EV-032 |
| TC-230 | Tres clientes concurrentes crean trabajos independientes | PASS | EV-032 |
| TC-231 | Errores recuperables conservan conexión | PASS | EV-032 |
| TC-232 | JSON inválido cierra solo al cliente afectado | PASS | EV-032 |
| TC-233 | Desconexiones abruptas no interrumpen trabajos | PASS | EV-032 |
| TC-234 | Límite por IP y recuperación de cupo | PASS | EV-032 |
| TC-235 | Límite global con distintas IP loopback | PASS | EV-032 |
| TC-236 | Cliente lento no bloquea otro cliente | PASS | EV-032 |
| TC-237 | Coexistencia de IPC UNIX y TCP | PASS | EV-032 |
| TC-238 | Apagado con clientes activos | PASS | EV-032 |
| TC-239 | CLI maneja respuesta exitosa incompleta | PASS | EV-032 |
| TC-240 | Crear exactamente 100 trabajos mediante TCP | PASS | EV-033 |
| TC-241 | Verificar UUID únicos y listado completo | PASS | EV-033 |
| TC-242 | Completar los 100 trabajos correctamente | PASS | EV-033 |
| TC-243 | Ejecutar 90 consultas status válidas | PASS | EV-033 |
| TC-244 | Latencia máxima status <= 1000 ms | PASS | EV-033 |
| TC-245 | Medir list y health con 100 trabajos | PASS | EV-033 |
| TC-246 | Daemon operativo después de la carga | PASS | EV-033 |
| TC-247 | Conectividad TCP | PASS | EV-034 |
| TC-248 | Health remoto | PASS | EV-034 |
| TC-249 | Ejecución remota | PASS | EV-034 |
| TC-250 | Listado | PASS | EV-034 |
| TC-251 | Estado | PASS | EV-034 |
| TC-252 | stdout/stderr | PASS | EV-034 |
| TC-253 | Cancelación | PASS | EV-034 |
| TC-254 | Estado compartido UNIX/TCP | PASS | EV-034 |
| TC-255 | IP real | PASS | EV-034 |
| TC-256 | Allowlist | PASS | EV-034 |
| TC-257 | Variables de entorno | PASS | EV-034 |
| TC-258 | Latencia LAN | PASS | EV-034 |
| TC-259 | Desconexión y recuperación | PASS | EV-034 |
| TC-260 | Apagado | PASS | EV-034 |

## Resultado general

Se han ejecutado **260 casos únicos acumulados** sobre los alcances revisados de Jobsy: 257 PASS y 3 FAIL según los resultados originales por caso. Los resultados de regresión se registran por separado.

Los 164 casos históricos tenían resultado PASS al cierre del PR #133; el PR #135 añade 93 PASS y 3 FAIL. EV-035 reevalúa la batería vigente sin crear nuevos IDs.

Para el PR #116 se añadieron **36 casos de prueba**, del `TC-091` al `TC-126`, con resultado:

**36 PASS / 0 FAIL**

Para el cierre de QA de la Technical Review 2 se añadieron **23 casos de prueba**, del `TC-127` al `TC-149`, con resultado:

**23 PASS / 0 FAIL**

Para el PR #133 se añadieron **15 casos de prueba**, del `TC-150` al `TC-164`, con resultado:

**15 PASS / 0 FAIL**

La cobertura del PR #133 incluyó:

- visualización de IDs cortos de 8 caracteres;
- recuperación del UUID completo mediante `list --full-id`;
- uso de IDs cortos en `status`, `output` y `cancel`;
- compatibilidad con UUID completos y prefijos de más de 8 caracteres;
- validación de IDs inexistentes, inválidos y ambiguos;
- visualización de IDs cortos en `health`;
- regresión completa de la batería vigente mediante `EV-027`.

La batería consolidada posterior al PR #133 finalizó con:

```text
23 scripts
23 PASS
0 FAIL
0 TIMEOUT
```

La cobertura adicional de la Technical Review 2 incluyó:

- RNF-31 — recuperación de trabajos terminados, pendientes e interrumpidos.
- RNF-33 — estrés y liberación de memoria, procesos, archivos y sockets.
- RNF-02 — instalación reproducible desde un clon limpio.
- RNF-03 — instalación y operación sin privilegios root.
- RNF-19 — instalación limpia sin warnings ni errores.
- RNF-20 — batería de QA ejecutable mediante un único comando.

La batería consolidada final ejecutó:

```text
22 scripts
22 PASS
0 FAIL
0 TIMEOUT
Duración total: 31.31 s
```

Durante la primera validación de RNF-22 se detectó un defecto real mediante `TC-119`: el `ReqID` se generaba correctamente al recibir una solicitud, pero no se propagaba a eventos posteriores del mismo ciclo. El problema fue corregido y revalidado correctamente. El incidente se documenta en `docs/qa/incidents/INC-001-request-id-correlation.md`.

También se documentó la evidencia de versión demostrada y batería ejecutada en `docs/qa/technical-review-2.md`.

### Observaciones QA — cierre histórico Technical Review 2 y PR #133

- La cobertura acumulada comprende `TC-001` a `TC-164`.
- Las evidencias acumuladas comprenden `EV-001` a `EV-027`.
- RNF-31 quedó cubierto mediante `TC-127` a `TC-133` / `EV-022`.
- RNF-33 quedó cubierto mediante `TC-134` a `TC-140` / `EV-023`.
- RNF-02, RNF-03 y RNF-19 quedaron cubiertos mediante `TC-141` a `TC-146` / `EV-024`.
- RNF-20 quedó cubierto mediante `TC-147` a `TC-149` / `EV-025`.
- El PR #133 quedó cubierto mediante `TC-150` a `TC-164` / `EV-026`, validando IDs cortos, UUID completos, resolución de prefijos y manejo de errores.
- La regresión posterior al PR #133 quedó documentada en `EV-027`, con la batería vigente completa en `PASS`.
- La instalación limpia se ejecutó con UID `1000`, sin `sudo`, con código de salida `0` y `0` warnings detectados.
- La prueba de estrés procesó `120` trabajos, liberó todos los procesos hijos, conservó `6` descriptores de archivo antes y después de la carga y eliminó correctamente el socket al finalizar.
- La batería consolidada excluye pruebas históricas cuyas expectativas pertenecen a contratos anteriores del sistema; las funcionalidades actuales correspondientes cuentan con cobertura posterior vigente.
- No se identifican defectos bloqueantes abiertos dentro del alcance final validado.


## Cierre QA — PR #135

- TC-165 a TC-260: 96 casos, 93 PASS, 3 FAIL (TC-213, TC-219, TC-228).
- EV-035: 29 scripts, 27 PASS, 2 FAIL, 0 TIMEOUT, 70.76 s, rc 1; 23 scripts históricos PASS. TC-147 PASS; TC-148 y TC-149 FAIL en esta reejecución, sin cambiar el resultado histórico original.
- INC-002, INC-003 e INC-004 abiertos y reproducidos. OBS-09 y OBS-10 reproducidas en LAN y loopback.
- RNF-05: 100 trabajos registrados y completados en loopback, no 100 activos simultáneos. LAN: 4 trabajos, conexión persistente, sin incluir establecimiento TCP ni arranque CLI.
- EV-034 es consolidación manual más bitácora original; EV-035 registra detalle únicamente de scripts fallidos.
- Dictamen: NO APROBADO, pendiente de correcciones y revalidación.
- Los casos TC-150 a TC-164 se conservan en la tabla histórica tal como aparecen en el documento recibido; no se inventan fichas detalladas ausentes.
