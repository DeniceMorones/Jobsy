# INC-003 — Sanitización incompleta de autorización HTTP Bearer

## 1. Identificación

- **ID del incidente:** INC-003.
- **Requisito relacionado:** RNF-15.
- **Caso de prueba:** TC-219.
- **Componente afectado:** `src/daemon/logger.py`, función `sanitize`.
- **Estado:** Abierto, reproducido en regresión; corrección pendiente.
- **Severidad propuesta:** Media. **Prioridad propuesta:** Alta.
- **PR relacionado:** PR #135; commit `32bd487`, rama `alexia-test-pr135`.
- **Entorno:** Ubuntu sobre WSL2, Windows 11, Python 3.14.4, `.venv`.
- **Fecha de revalidación del defecto:** 2026-11-28.

---

## 2. Síntomas observados

La función de sanitización reemplaza la palabra `Bearer`, pero conserva el valor ficticio del token. TC-219 obtuvo FAIL tanto en EV-031 como en EV-035.

### Reproducción

Desde la raíz del repositorio con `.venv` activo:

```bash
python test/test_remote_security.py
```

Prueba mínima de la función:

```bash
python -c 'from src.daemon.logger import sanitize; print(sanitize("Authorization: Bearer QA_FAKE_219"))'
```

**Entrada:** `Authorization: Bearer QA_FAKE_219`

**Resultado obtenido:**

```text
Authorization=[REDACTADO] QA_FAKE_219
FAIL: AssertionError: Secreto ficticio no ocultado completamente
```

**Resultado esperado:** el valor `QA_FAKE_219` no debe aparecer y debe existir un marcador `[REDACTADO]`. Por ejemplo, `Authorization=[REDACTADO]`.

---

## 3. Hipótesis inicial

La expresión regular de pares clave/valor reconoce únicamente una palabra sin espacios cuando el valor no está entre comillas. En una cabecera Bearer, esa palabra es el esquema de autorización y no el token.

---

## 4. Causa identificada

`_KEY_VALUE` en `src/daemon/logger.py` reconoce `authorization` como palabra sensible, pero la alternativa `\S+` del patrón de valor captura solo `Bearer`. `sanitize()` sustituye esa coincidencia y `_FLAG_VALUE` no elimina el token restante porque no corresponde a una opción de CLI.

**Impacto:** la función no oculta completamente esta forma de secreto si el mensaje llega al sanitizador. Se comprobó con un marcador ficticio en una llamada directa; no se demostró exposición de credenciales reales ni que una operación normal genere esa cabecera. TC-215 y TC-216 aprobaron la ausencia de argumentos de comandos en bitácora.

---

## 5. Corrección propuesta (pendiente)

Reconocer el esquema Bearer y el valor completo asociado antes de aplicar la sustitución genérica, o adoptar otra estrategia equivalente que garantice la ocultación del token. Mantener las reglas de sanitización ya funcionales. Considerar pruebas adicionales de variantes de mayúsculas y espacios, usando exclusivamente datos ficticios.

**Commit de corrección:** pendiente; QA no ha modificado producción.

---

## 6. Prueba de regresión y revalidación

EV-035 confirmó TC-219 FAIL. El bloque EV-031 reejecutado obtuvo 12 PASS / 2 FAIL (el otro fallo corresponde a INC-004).

Después del fix:

- Ejecutar `python test/test_remote_security.py`.
- TC-219 debe ocultar completamente el marcador ficticio y conservar `[REDACTADO]`.
- TC-217 y TC-218 deben conservar PASS para pares clave/valor y opciones con secretos.
- TC-215 y TC-216 deben conservar PASS; TC-220 a TC-226 y TC-227 también deben mantener sus resultados.
- Tras corregir INC-004, el bloque completo debe obtener 14 PASS / 0 FAIL. Reejecutar además la batería unificada después de integrar todas las correcciones.

**Evidencias:**

- `docs/qa/evidence/avance-3/EV-031-remote-security-output.txt`
- `docs/qa/evidence/avance-3/EV-035-regression-output.txt`

---

## 7. Resultado final del incidente

Abierto. Sanitización incompleta confirmada; corrección y revalidación satisfactoria pendientes.

---

## 8. Conclusión

La protección de secretos no debe limitarse al esquema de autorización. QA recomienda corregir este comportamiento para fortalecer RNF-15 antes de aprobar el PR #135.
