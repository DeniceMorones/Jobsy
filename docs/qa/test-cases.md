# Casos de prueba — MVP Avance 1

Este documento registra los casos de prueba ejecutados sobre el núcleo funcional de Jobsy correspondiente a los PR #101 y #102 del Avance 1.


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

> Las evidencias del avance #1 del MVP se almacenan en `docs/qa/evidence/avance-1/`.

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


## Resultado general

Se han ejecutado un total de **52 casos de prueba** sobre los alcances revisados de los PR #101, #102 y #104. Los 52 casos obtuvieron resultado `PASS`.

Para el PR #104 se añadieron 16 casos de prueba, del `TC-037` al `TC-052`, enfocados en validar la comunicación entre la CLI y el daemon mediante socket UNIX, la conservación de trabajos durante una misma sesión, operaciones de consulta, listado y cancelación mediante IPC, manejo de solicitudes inválidas, comportamiento de la CLI cuando el servicio no está disponible, limpieza del socket durante el apagado y ejecución de múltiples solicitudes consecutivas.

Las pruebas confirmaron que el daemon permanece operativo ante errores de protocolo controlados, que múltiples ejecuciones independientes de la CLI pueden interactuar con el mismo estado mantenido por el servicio y que los trabajos conservan sus identificadores, estados y códigos de salida durante la sesión.

No se identificaron defectos bloqueantes dentro del alcance funcional validado del PR #104.

La demostración explícita de separación entre el proceso del daemon y los procesos de los trabajos mediante comparación directa de PID continúa fuera de los casos ejecutados actualmente.
