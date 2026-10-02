# Casos de prueba — MVP Avance 1

Este documento registra los primeros casos de prueba ejecutados sobre el núcleo funcional de Jobsy correspondiente al PR #101.


## Estados

Cada caso puede encontrarse en uno de los siguientes estados:

- `PASS`: el resultado obtenido coincide con el resultado esperado.
- `FAIL`: el resultado obtenido no coincide con el resultado esperado.
- `BLOCKED`: la prueba no pudo ejecutarse.
- `PENDING`: la prueba todavía no ha sido ejecutada.

## Evidencias asociadas

- `EV-001-validation-output.txt`: salida de `test_validation.py`.
- `EV-002-executor-output.txt`: salida de `test_executor.py`.

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

## Resultado general

Los 14 casos ejecutados sobre el alcance revisado del PR #101 obtuvieron resultado `PASS`.

Estos resultados verifican parcialmente el MVP. Permanecen pendientes pruebas sobre consulta por ID, listado y filtrado de trabajos, ejecución de un programa inexistente, demostración explícita del proceso separado mediante PID, cancelación y continuidad del servicio ante comandos inválidos.
