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

# Resumen de ejecución

| Rango | Alcance | Casos ejecutados | Estado | Evidencias |
|---|---|---:|---|---|
| TC-001 a TC-017 | PR #101 | 17 | PASS | EV-001, EV-002, EV-003 |
| TC-018 a TC-022 | PR #102 — RF-10 | 5 | PASS | EV-004 |
| TC-023 a TC-028 | PR #102 — RF-15 | 6 | PASS | EV-005 |
| TC-029 a TC-036 | PR #102 — RF-17 | 8 | PASS | EV-006 |

## Resultado general

Se ejecutaron **36 casos de prueba** documentados de forma continua: TC-001 a TC-017 corresponden al alcance revisado del PR #101 y TC-018 a TC-036 corresponden al PR #102. Todos los casos documentados obtuvieron resultado `PASS`.

La verificación explícita de que cada trabajo se ejecuta en un proceso Linux distinto mediante comparación de PID no forma parte de esta versión de la suite. Las pruebas de RF-10 sí comprobaron la existencia y terminación del PID asociado al trabajo cancelado en ejecución.
