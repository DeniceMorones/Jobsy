# INC-002 — JOBSY_PORT no numérico provoca un traceback en la CLI

## 1. Identificación

- **ID del incidente:** INC-002 (OBS-05)
- **Requisitos relacionados:** RF-16, RF-17, RF-28 y RNF-21 (manejo controlado de errores).
- **Caso de prueba:** TC-213.
- **Componente afectado:** `src/client/cli.py`, función `build_parser`, línea 29.
- **Estado:** Abierto, reproducido en regresión; corrección pendiente.
- **Severidad propuesta:** Media. **Prioridad propuesta:** Alta.
- **PR relacionado:** PR #135; commit evaluado `32bd487`, rama `alexia-test-pr135`.
- **Entorno:** Ubuntu sobre WSL2, Windows 11, Python 3.14.4, entorno virtual `.venv`.
- **Fecha de revalidación del defecto:** 2026-11-28.

---

## 2. Síntomas observados

Con `JOBSY_PORT=abc`, el cliente termina antes de procesar la operación y muestra un traceback de Python. TC-213 obtuvo FAIL en EV-030 y EV-035.

### Reproducción

Desde la raíz del repositorio, con el entorno virtual activo, ejecutar:

```bash
python test/test_remote_cli.py
```

Reproducción mínima de la conversión fallida (no requiere daemon activo):

```bash
JOBSY_HOST=127.0.0.1 JOBSY_PORT=abc jobsy health
```

Resultado observado en EV-035:

```text
rc=1
ValueError: invalid literal for int() with base 10: 'abc'
FAIL: AssertionError: OBS-05: JOBSY_PORT inválido no manejado de forma controlada
```

La reproducción complementaria EV-030-INC-002 documentó cuatro escenarios afectados: selección remota por entorno, uso local sin host, puerto explícito válido con entorno inválido y `--help`.

**Resultado esperado:** error controlado, sin traceback, cuando el puerto de entorno sea necesario e inválido. El modo local y la ayuda no deben depender de un puerto remoto innecesario; las opciones explícitas válidas deben prevalecer sobre el entorno.

---

## 3. Hipótesis inicial

La conversión de la variable de entorno ocurre antes del análisis de argumentos, por lo que el parser no puede manejar la entrada inválida ni aplicar la precedencia de opciones explícitas.

---

## 4. Causa identificada

En `src/client/cli.py:29`, `build_parser()` utiliza:

```python
parser.add_argument("--port", type=int, default=int(os.environ.get("JOBSY_PORT", DEFAULT_REMOTE_PORT)),
```

El `int()` del valor predeterminado se evalúa al construir el parser. La cadena `abc` provoca `ValueError` antes de que argparse procese las opciones. El traceback de EV-035 confirma esta ruta. En contraste, TC-212 aprueba el rechazo controlado de puertos explícitos inválidos y TC-210 aprueba la precedencia con valores de entorno válidos.

**Impacto:** una configuración incorrecta del entorno impide utilizar el cliente, incluso en operaciones que no necesitan el puerto remoto. No se observó caída del daemon (TC-214 PASS).

---

## 5. Corrección propuesta (pendiente)

Separar la construcción del parser de la resolución y validación del puerto efectivo. Aplicar primero la precedencia de opciones explícitas, validar el entorno cuando se requiera TCP y emitir un diagnóstico de configuración sin traceback. Mantener el rango 1–65535 y los contratos de salida existentes. El diseño final corresponde al desarrollador.

**Commit de corrección:** pendiente; QA no ha modificado producción.

---

## 6. Prueba de regresión y revalidación

EV-035 confirmó TC-213 FAIL; el bloque obtuvo 18 PASS / 1 FAIL.

Después del fix, ejecutar `python test/test_remote_cli.py` y repetir los cuatro escenarios de la reproducción complementaria. Verificar:

- Puerto inválido requerido: código distinto de cero y mensaje relacionado con el puerto, sin traceback.
- Modo local con daemon UNIX activo y ayuda: operación correcta aun con puerto remoto inválido en el entorno.
- Puerto explícito válido y daemon remoto disponible: conexión correcta pese al valor de entorno inválido.
- TC-196 a TC-214: 19 PASS; conservar la evidencia original y registrar la nueva ejecución.
- Reejecutar `python test/run_qa_suite.py` tras integrar las correcciones de los tres incidentes.

**Evidencias originales y de regresión:**

- `docs/qa/evidence/avance-3/EV-030-remote-cli-output.txt`
- `docs/qa/evidence/avance-3/EV-030-INC-002-reproduction.txt`
- `docs/qa/evidence/avance-3/EV-035-regression-output.txt`

---

## 7. Resultado final del incidente

Abierto. El defecto se reprodujo; aún no existe una corrección ni una revalidación satisfactoria registrada.

---

## 8. Conclusión

El cliente requiere una validación controlada del puerto efectivo que no interfiera con operaciones ajenas a TCP. QA recomienda corregir antes de aprobar el PR #135.
