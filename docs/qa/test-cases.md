# Casos de prueba — Jobsy

Este documento registra los casos de prueba ejecutados por QA sobre los alcances funcionales revisados de Jobsy en los PR #101, #102, #104, #110 y #114.

La numeración de los casos se mantiene de forma acumulativa para conservar la trazabilidad entre pruebas, requisitos, scripts y evidencias.

Hasta el momento se han documentado y ejecutado los casos **TC-001 a TC-090**.

Las pruebas cubren validación de entradas, ejecución de trabajos, estados y metadatos, cancelación, apagado seguro, comportamiento de la CLI, comunicación IPC mediante sockets UNIX, robustez ante solicitudes inválidas, múltiples trabajos durante una misma sesión y configuración de sockets UNIX personalizados.

Los casos **TC-053 a TC-070** corresponden a la validación del **PR #110**, relacionado con la configuración del socket UNIX local.

Los casos **TC-071 a TC-090** corresponden a la validación del **PR #114**, relacionado con la gestión del ciclo de vida de trabajos, separación de salidas, grupos de procesos, cancelación repetida, período de gracia configurable y aislamiento de fallos de limpieza.

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

### Avance 1

- EV-001 a EV-009: evidencias correspondientes a las pruebas del Avance 1.

### Avance 2

- `EV-010-socket-config-output.txt`: configuración, validación e integración básica del socket UNIX configurable.
- `EV-011-socket-cli-contract-output.txt`: contrato público de CLI, variable `JOBSY_SOCKET_PATH`, códigos de salida y puntos de entrada.

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


## Resultado general

Se han ejecutado un total de **90 casos de prueba** sobre los alcances revisados de los PR #101, #102, #104, #110 y #114. Los 90 casos obtuvieron resultado `PASS`.

Para el PR #110 se añadieron **18 casos de prueba**, del `TC-053` al `TC-070`, enfocados en validar la configuración del socket UNIX local, el uso del endpoint predeterminado y personalizado, las validaciones de ruta, el comportamiento de `JOBSY_SOCKET_PATH`, los códigos de salida y los puntos de entrada públicos instalados.

Las pruebas confirmaron que `/tmp/jobsy.sock` continúa siendo el endpoint predeterminado, que el daemon puede utilizar `--socket-path`, que los clientes pueden seleccionar el endpoint mediante `JOBSY_SOCKET_PATH`, que el daemon no toma su configuración desde esa variable, y que las rutas inválidas se rechazan de forma controlada.

También se verificó que una ruta existente no sea sobrescrita, que una variable vacía sea rechazada, que una configuración inválida del daemon devuelva código `2`, que un error de endpoint del cliente devuelva código `1`, que `~` se expanda correctamente y que los comandos públicos `jobsy-daemon`, `jobsy`, `execute`, `list`, `status` y `cancel` funcionen utilizando un socket personalizado.

No se identificaron defectos bloqueantes dentro del alcance funcional validado del PR #110.

La implementación validada no incorpora comunicación TCP, host o puerto configurables, por lo que el alcance relacionado con RF-16 continúa siendo parcial.

La separación entre el proceso del daemon y los procesos de los trabajos quedó cubierta explícitamente mediante los casos `TC-076` a `TC-079`, que verifican PID, PGID, SID y la terminación completa del grupo de procesos.
