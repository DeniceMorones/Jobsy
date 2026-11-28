# Observaciones de QA — PR #135

## 1. Identificación y alcance

- Proyecto: Jobsy — Avance 3.
- Rama QA: `alexia-test-pr135`.
- Commit evaluado: `32bd487`.
- Fecha de cierre de ejecución: 28 de noviembre de 2026.
- Evidencias de ejecución: `docs/qa/evidence/avance-3/`, EV-028 a EV-035.
- Alcance: revisión técnica, pruebas automatizadas TCP/UNIX y pruebas LAN entre dos equipos.

Las prioridades indicadas son propuestas de QA. Las observaciones no equivalen automáticamente a casos FAIL ni a incidentes independientes. OBS-05 y OBS-07 remiten a incidentes ya registrados; INC-003 se mantiene como incidente independiente detectado por TC-219. No se han aplicado correcciones al producto.

## 2. Resumen de observaciones

| ID | Hallazgo | Clasificación | Prioridad propuesta | Estado |
|---|---|---|---|---|
| OBS-01 | Archivo ajeno al proyecto incluido en el PR | Higiene del repositorio | Baja | Confirmado por revisión estática |
| OBS-02 | Verificadores del desarrollador no propagan fallos mediante exit code | Calidad de automatización | Media | Confirmado por revisión estática |
| OBS-03 | Medición RNF-05 puede declarar cumplimiento sin validar carga/respuestas | Calidad de medición | Alta | Confirmado por revisión estática |
| OBS-04 | TCP sin cifrado ni autenticación de cliente | Limitación de diseño documentada | Alta para exposición fuera de red confiable | Vigente |
| OBS-05 | JOBSY_PORT inválido genera traceback | Defecto / INC-002 | Alta | Reproducido |
| OBS-06 | Respuesta incompleta genera mensaje poco informativo | Mejora de diagnóstico | Baja | Reproducido; TC-239 PASS |
| OBS-07 | Excepciones internas registran datos sensibles ficticios | Defecto / INC-004 | Alta | Reproducido |
| OBS-08 | Posible carrera durante cierre de conexiones TCP | Riesgo técnico | Media | No reproducido |
| OBS-09 | Cancelación registrada como finalización fallida | Inconsistencia de observabilidad | Baja | Reproducido |
| OBS-10 | Mensaje final de apagado duplicado | Calidad de bitácora | Baja | Reproducido |

## 3. Detalle técnico

### OBS-01 — Archivo ajeno al proyecto incluido en el PR

**Componente:** raíz del repositorio.

**Hallazgo:** `git ls-tree --name-only HEAD` y el diff contra `origin/dev` muestran un archivo nuevo denominado `' 0ec754a aa662f7 6efe139` (la comilla inicial forma parte del nombre), con 314 líneas de ayuda del paginador `less` (`SUMMARY OF LESS COMMANDS`).

**Impacto:** ruido en el repositorio; no se demostró afectación funcional.

**Reproducción:** revisar `git ls-tree --name-only HEAD` y `git diff origin/dev...HEAD -- "' 0ec754a aa662f7 6efe139"` en el commit evaluado.

**Recomendación:** retirar únicamente ese archivo del PR de desarrollo tras confirmar que no tiene propósito. QA no lo modifica. No confundir con el archivo local no rastreado `tatus --short`, eliminado durante el cierre de QA.

**Aceptación:** el archivo ajeno deja de formar parte del diff del PR; no se eliminan archivos legítimos.

### OBS-02 — Verificadores sin código de salida de fallo

**Componente:** `test/verificar_protocolo_v1.py`, `test/verificar_remoto.py`, `test/verificar_cli_remoto.py`.

**Hallazgo:** los scripts contabilizan fallas e imprimen el resumen `OK`/`FALLAS`, pero no establecen un código de salida distinto de cero en función del contador de fallas al finalizar normalmente.

**Impacto:** una integración automatizada que evalúe únicamente el código de salida podría considerar aprobada una ejecución que contiene fallos. No se indujo una falla deliberada en estos scripts para demostrarlo en ejecución.

**Recomendación y aceptación:** devolver un código distinto de cero cuando exista cualquier comprobación fallida, y cero cuando todas pasen; validar ambos escenarios. La batería formal QA `test/run_qa_suite.py` es independiente y sí propagó el fallo agregado en EV-035.

### OBS-03 — Medición RNF-05 insuficientemente validada

**Componente:** `scripts/medir_rnf05.py`.

**Hallazgo:** el bucle de creación puede terminar anticipadamente mediante `break` al recibir una respuesta `run` errónea. Si quedaron algunos IDs, el cálculo continúa sin exigir exactamente 100 trabajos. Además, la medición de `status`, `list` y `health` utiliza el tiempo devuelto por `ask()` sin comprobar sistemáticamente el éxito de cada respuesta. El dictamen `CUMPLE` depende únicamente del peor tiempo de `status`. Si no se creó ningún ID, el acceso por índice puede fallar.

**Impacto:** posibilidad de falso cumplimiento de RNF-05; confirmación estática, no una reproducción de falso positivo en ejecución.

**Evidencia complementaria:** EV-033, TC-240 a TC-246, prueba QA independiente: 100 trabajos únicos completados, 90 consultas `status` válidas, máximo 0.711 ms; límite de 1000 ms. Este PASS corresponde a loopback con 100 trabajos registrados y finalizados, no a 100 trabajos activos ni a una LAN con 100 trabajos.

**Recomendación y aceptación:** exigir la carga completa, verificar todas las respuestas y su correspondencia con las solicitudes, tratar errores o muestras insuficientes como medición fallida y devolver código no cero cuando no se cumpla el criterio.

### OBS-04 — Ausencia de cifrado y autenticación del cliente

**Componente:** transporte TCP remoto y guía de usuario.

**Hallazgo:** la guía del PR reconoce que no hay cifrado ni autenticación del cliente y que mTLS (ADR-009) no está implementado. La allowlist filtra por IP, pero no acredita identidad individual del cliente.

**Impacto:** un equipo cuya IP esté permitida puede ejecutar comandos con el contexto del daemon; el transporte no protege por sí mismo la confidencialidad ni integridad frente a terceros con acceso al tráfico. No se demostró un ataque ni acceso no autorizado en las pruebas.

**Evidencia:** revisión de guía; EV-029, EV-031 y EV-034 (control de acceso y rechazo fuera de allowlist).

**Recomendación:** limitar el uso actual a redes privadas confiables y allowlists mínimas; no exponer el servicio a Internet. Planificar autenticación y cifrado conforme al alcance acordado. No clasificar automáticamente como incumplimiento de una funcionalidad comprometida en este PR sin confirmar el requisito aplicable.

### OBS-05 — JOBSY_PORT no numérico provoca traceback

**Componente:** `src/client/cli.py`, `build_parser()`, línea 29.

**Hallazgo:** la conversión `int(os.environ.get("JOBSY_PORT", DEFAULT_REMOTE_PORT))` sucede antes de resolver los argumentos. Con `JOBSY_PORT=abc` se produce `ValueError` y código 1, con traceback. La reproducción complementaria también afectó modo local, `--help` y una opción explícita válida.

**Evidencia:** TC-213 / EV-030, `EV-030-INC-002-reproduction.txt`, EV-035.

**Acción y aceptación:** consultar [INC-002](incidents/INC-002-invalid-jobsy-port.md). Validar configuración remota de forma controlada, respetar precedencia explícita y no afectar ayuda o modo local cuando el puerto ambiental es irrelevante.

### OBS-06 — Diagnóstico poco informativo ante respuesta incompleta

**Componente:** cliente CLI remoto.

**Hallazgo:** un servidor simulado devuelve una respuesta exitosa de `list` sin el campo `jobs`. TC-239 obtiene código 1 y `Error: 'jobs'`, sin traceback. El criterio original se cumplió, por lo que TC-239 permanece PASS.

**Evidencia:** EV-032 / TC-239.

**Recomendación y aceptación:** validar la estructura de respuesta según la operación y mostrar un error de protocolo comprensible con causa y sugerencia, manteniendo código no cero y sin traceback. No se demostró que un daemon normal produzca esa respuesta.

### OBS-07 — Datos sensibles ficticios en logs de excepciones internas

**Componente:** dispatcher y logger.

**Hallazgo:** una excepción simulada con el marcador `QA_FAKE_INTERNAL_5828` deja ese dato en la bitácora. La respuesta al cliente sí oculta el detalle interno (TC-227 PASS), pero TC-228 falla.

**Evidencia:** EV-031 / TC-227 y TC-228; EV-035.

**Acción y aceptación:** consultar [INC-004](incidents/INC-004-sensitive-internal-error-logging.md). Evitar registrar texto sensible de excepciones, conservando información diagnóstica segura. No se demostraron filtraciones de credenciales reales.

### OBS-08 — Posible carrera durante el apagado TCP

**Componente:** `remote_server.py`, `stop()` y `_accept_loop()`.

**Hallazgo:** `stop()` activa la señal de parada, cierra el listener y toma una instantánea de clientes e hilos bajo bloqueo. El bucle de aceptación puede estar procesando una conexión ya aceptada; la reserva y el registro/inicio del worker ocurren en etapas separadas. Se plantea la posibilidad de que una conexión o un hilo queden fuera de la instantánea de cierre, o que se intente unir un hilo aún no iniciado.

**Evidencia:** revisión estática; EV-032 / TC-238: apagado con clientes activos en 0.515 s, código 0, PASS. No se reprodujo la carrera; no constituye un defecto confirmado.

**Recomendación y aceptación:** revisar sincronización entre aceptación, registro de workers y cierre; añadir una prueba repetida de conexiones durante apagado que verifique cierre controlado y ausencia de excepciones o recursos residuales.

### OBS-09 — Cancelación registrada como finalización fallida

**Componente:** ciclo de vida del trabajo y logging.

**Hallazgo:** para el mismo Job ID se registra `Trabajo cancelado por el usuario` y posteriormente `Trabajo finalizado con estado fallido (exit_code=-15)`. La consulta de estado confirma `CANCELED`, código -15 y diagnóstico de cancelación solicitada por el usuario.

**Evidencia:** EV-034 / TC-253 y bitácora `EV-034-remote-lan-daemon.txt`; reproducción en EV-035 / TC-204, por loopback. TC-253 y TC-204 permanecen PASS funcional.

**Impacto:** diagnóstico ambiguo para operadores que consulten únicamente la bitácora. No se ha establecido si el comportamiento fue introducido por PR #135.

**Recomendación y aceptación:** registrar una finalización coherente con el estado persistido `CANCELED`, manteniendo el código de salida y diferenciándola de `FAILED`.

### OBS-10 — Mensaje final de apagado duplicado

**Componente:** logging del cierre del daemon.

**Hallazgo:** `Servicio detenido completamente.` aparece dos veces al finalizar una sesión, con el mismo timestamp en las muestras observadas.

**Evidencia:** EV-034, tres sesiones LAN; EV-035, cierre del daemon durante `test_remote_cli.py` (16:55:48.602 UTC); también observado en EV-032. El apagado funcional obtuvo PASS en TC-260.

**Impacto:** ruido en bitácora y posibles conteos duplicados de eventos de cierre. No se ha determinado la causa ni si fue introducido por PR #135.

**Recomendación y aceptación:** revisar las rutas de emisión del mensaje y verificar un único evento final por sesión, sin alterar el apagado limpio.

## 4. Relación con incidentes y dictamen

Los tres incidentes abiertos son INC-002 (TC-213), INC-003 (TC-219) e INC-004 (TC-228). OBS-05 y OBS-07 son referencias a INC-002 e INC-004 respectivamente, no defectos adicionales. INC-003 documenta la sanitización incompleta de tokens Bearer; no se le asigna un número OBS nuevo.

Resultados: 96 casos nuevos, 93 PASS y 3 FAIL; regresión EV-035: 29 scripts, 27 PASS, 2 FAIL, 0 TIMEOUT, 70.76 s, código de salida 1. Los 23 scripts históricos incluidos pasaron. No se detectaron fallos adicionales dentro de la batería ejecutada.

**Dictamen QA:** no se recomienda aprobar PR #135 hasta corregir y revalidar los tres incidentes. Las demás observaciones requieren revisión y priorización del equipo; OBS-08 permanece como riesgo no reproducido y OBS-04 como limitación de diseño. Los criterios de aceptación propuestos no representan pruebas ya ejecutadas. Se conservan las evidencias originales y no se modifica el código del desarrollador.
