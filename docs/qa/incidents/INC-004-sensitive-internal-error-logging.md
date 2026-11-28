# INC-004 — Datos sensibles en bitácoras de excepciones internas

## 1. Identificación

- **ID del incidente:** INC-004 (OBS-07).
- **Requisito relacionado:** RNF-15.
- **Caso de prueba:** TC-228; control complementario TC-227.
- **Componente afectado:** `src/daemon/dispatcher.py`, función `_error_for`, y logging.
- **Estado:** Abierto, reproducido en regresión; corrección pendiente.
- **Severidad propuesta:** Media. **Prioridad propuesta:** Alta.
- **PR relacionado:** PR #135; commit `32bd487`, rama `alexia-test-pr135`.
- **Entorno:** Ubuntu sobre WSL2, Windows 11, Python 3.14.4, `.venv`.
- **Fecha de revalidación del defecto:** 2026-11-28.

---

## 2. Síntomas observados

Una excepción interna simulada que contiene un marcador ficticio sin etiqueta de secreto genera una respuesta controlada al cliente, pero el mensaje de la excepción queda registrado en la bitácora. TC-227 obtuvo PASS y TC-228 FAIL tanto en EV-031 como en EV-035.

### Reproducción

Desde la raíz del repositorio con `.venv` activo:

```bash
python test/test_remote_security.py
```

La prueba crea un `DaemonLogger` en un directorio temporal, sustituye el logger del dispatcher mediante `patch.object`, y utiliza un administrador simulado cuya operación `snapshot` genera `RuntimeError` con el marcador ficticio `QA_FAKE_INTERNAL_5828`. Envía al dispatcher una solicitud v1 `status` validada con ReqID `qa-internal` y job_id `aaaaaaaa`; luego lee el archivo de bitácora. No se modifica el código de producción ni se usan secretos reales.

**Resultado obtenido (EV-035):**

```text
Excepción procesando solicitud v1 'status' [ReqID: qa-internal]: RuntimeError: Fallo simulado con dato sensible QA_FAKE_INTERNAL_5828
Marcador ficticio presente en bitácora: True
FAIL: AssertionError: OBS-07: excepción interna registra dato sensible sin etiqueta
```

La respuesta al cliente contiene `status=error`, `code=INTERNAL_ERROR`, una causa genérica y sugerencia operativa, sin el marcador ficticio.

**Resultado esperado:** conservar el diagnóstico operativo y la correlación mediante ReqID sin incluir datos sensibles de la excepción ni en la respuesta ni en la bitácora.

---

## 3. Hipótesis inicial

El dispatcher utiliza el texto completo de la excepción para registrar errores internos. Las reglas de sanitización basadas en etiquetas no pueden identificar necesariamente un dato sensible que aparece como texto libre.

---

## 4. Causa identificada

En `_error_for`, se obtiene `message = str(error)` y, para la rama de error interno inesperado, se interpola ese mensaje en el log:

```python
logger.log("ERROR", f"Excepción procesando solicitud v1 '{operation}' [ReqID: {rid}]: "
                    f"{type(error).__name__}: {message}")
```

El sanitizador reconoce determinados formatos de secretos, pero el marcador sin etiqueta no coincide con esas reglas. La respuesta externa se construye separadamente con una causa genérica.

**Impacto:** existe riesgo de persistencia de datos sensibles si una excepción real incluye ese contenido. Se comprobó la persistencia de un marcador ficticio con inyección controlada, no la exposición de credenciales reales ni la alcanzabilidad del mismo escenario mediante una petición externa normal. Los permisos 0600 aprobados en TC-220 y TC-221 reducen el acceso al archivo, pero no evitan almacenar información sensible.

---

## 5. Corrección propuesta (pendiente)

Evitar registrar indiscriminadamente `str(error)` de excepciones inesperadas. Preferir campos operativos permitidos, como tipo de excepción, operación y ReqID, y detalles explícitamente considerados seguros. Conservar los diagnósticos útiles y el contrato de error externo. Revisar otros puntos de logging con mensajes de excepción como medida preventiva, sin clasificarlos como defectos adicionales sin verificación.

**Commit de corrección:** pendiente; QA no ha modificado producción.

---

## 6. Prueba de regresión y revalidación

EV-035 confirmó TC-228 FAIL y TC-227 PASS. El bloque obtuvo 12 PASS / 2 FAIL (el otro fallo corresponde a INC-003).

Después del fix:

- Ejecutar `python test/test_remote_security.py`.
- TC-228 debe confirmar la ausencia del marcador ficticio en la bitácora.
- TC-227 debe conservar la respuesta estructurada `INTERNAL_ERROR` sin marcador ni traceback.
- Comprobar que el log conserva información operativa segura y ReqID, sin texto sensible libre; este es un criterio complementario propuesto.
- Mantener las comprobaciones de permisos y omisión de argumentos. Tras corregir INC-003, el bloque debe obtener 14 PASS / 0 FAIL.
- Reejecutar la batería unificada después de integrar todas las correcciones y preservar las evidencias originales.

**Evidencias:**

- `docs/qa/evidence/avance-3/EV-031-remote-security-output.txt`
- `docs/qa/evidence/avance-3/EV-035-regression-output.txt`

---

## 7. Resultado final del incidente

Abierto. Debilidad reproducida mediante excepción simulada. Corrección y revalidación satisfactoria pendientes.

---

## 8. Conclusión

La sanitización de respuestas externas no es suficiente para garantizar la confidencialidad de la bitácora. QA recomienda limitar los datos registrados en excepciones internas antes de aprobar el PR #135.
