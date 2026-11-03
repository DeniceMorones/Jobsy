# INC-001 — Pérdida de correlación de ReqID en eventos posteriores

## 1. Identificación

- **ID del incidente:** INC-001
- **Requisito relacionado:** RNF-22
- **Caso de prueba que detectó el incidente:** TC-119
- **Componente afectado:** Bitácora y correlación de solicitudes IPC
- **Estado:** Resuelto y revalidado
- **PR relacionado:** PR #116
- **Commit de corrección:** `a5f22f6` — `feat(daemon): corrige correlación de ReqID en bitácora y consolida pruebas de robustez y observabilidad`

---

## 2. Síntomas observados

Durante la ejecución inicial de `TC-119` se verificó que una solicitud IPC recibía correctamente un identificador de correlación `ReqID`, pero dicho identificador no se mantenía en todos los eventos posteriores asociados al mismo flujo de ejecución.

El comportamiento observado fue:

- La solicitud `run` recibía un `ReqID`.
- El evento inicial de recepción quedaba registrado.
- Los eventos posteriores relacionados con la misma solicitud no conservaban de forma consistente ese mismo `ReqID`.
- La bitácora permitía identificar el trabajo mediante su Job ID, pero no reconstruir de extremo a extremo el ciclo completo de la solicitud usando únicamente el `ReqID`.

### Resultado inicial de TC-119

```text
TC-119 — Correlación completa de una solicitud mediante ReqID

Resultado inicial: FAIL
```

El resto de la funcionalidad del trabajo continuaba operando, pero la trazabilidad requerida por RNF-22 era incompleta.

---

## 3. Hipótesis inicial

La hipótesis de QA fue que el `request_id` se generaba correctamente al recibir la solicitud en el servidor, pero no se propagaba hacia las llamadas de logging posteriores relacionadas con el procesamiento de la operación.

Esto explicaba por qué:

1. el evento inicial sí mostraba un `ReqID`;
2. el trabajo se creaba y ejecutaba correctamente;
3. los eventos posteriores podían contener Job ID;
4. pero no todos conservaban el mismo identificador de correlación de la solicitud.

---

## 4. Causa identificada

La implementación original correlacionaba el `ReqID` principalmente con la recepción de la solicitud IPC, pero no lo mantenía de manera consistente durante todo el ciclo posterior de procesamiento y registro de eventos.

Como consecuencia, la bitácora no garantizaba que un mismo `ReqID` pudiera utilizarse para seguir múltiples eventos pertenecientes a una misma solicitud.

Esto incumplía la intención de RNF-22: permitir la correlación de una solicitud a través de los diferentes eventos registrados durante su procesamiento.

---

## 5. Corrección aplicada

El equipo de desarrollo corrigió la propagación y uso del `ReqID` en el flujo de logging.

La corrección quedó registrada en:

```text
a5f22f6
feat(daemon): corrige correlación de ReqID en bitácora y consolida pruebas de robustez y observabilidad
```

Después de incorporar la corrección a la rama de QA, se volvió a ejecutar la batería de pruebas correspondiente a logging y correlación.

---

## 6. Prueba de regresión y revalidación

Se reejecutaron los casos:

```text
TC-114 a TC-120
```

correspondientes a RF-14 y RNF-22.

La revalidación confirmó:

- creación de `jobsy.log`;
- formato correcto de eventos;
- generación de `ReqID` por solicitud;
- `ReqID` distintos para solicitudes distintas;
- inclusión de Job ID en eventos de trabajo;
- reutilización del mismo `ReqID` en múltiples eventos de una misma solicitud;
- continuidad operativa del daemon.

### Resultado de TC-119 después del fix

```text
PASS: La solicitud run fue aceptada.
PASS: La solicitud run registró un ReqID.
PASS: El mismo ReqID aparece en más de un evento.
```

### Resultado final del bloque

```text
TC-114 a TC-120
7 PASS
0 FAIL

RESULTADO GENERAL: PASS
```

La evidencia final quedó registrada en:

```text
docs/qa/evidence/avance-2/EV-020-request-logging-output.txt
```

---

## 7. Resultado final del incidente

El incidente quedó **resuelto y revalidado**.

RNF-22 quedó cubierto mediante los casos:

```text
TC-116
TC-117
TC-119
TC-120
TC-122
```

y las evidencias:

```text
EV-020
EV-021
```

No se detectaron regresiones bloqueantes después de aplicar la corrección.

---

## 8. Conclusión

El incidente permitió detectar una diferencia entre generar un identificador de solicitud y mantener una correlación completa durante todo su ciclo de vida.

La corrección aseguró que el `ReqID` pueda utilizarse para relacionar múltiples eventos pertenecientes a la misma solicitud, mejorando la trazabilidad y observabilidad del daemon.

Este incidente satisface el entregable de QA correspondiente a:

> Reporte de al menos 1 incidente técnico documentado con síntomas, causa, hipótesis, fix y prueba de regresión.
