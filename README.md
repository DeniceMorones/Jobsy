# Jobsy

Jobsy es una herramienta para Linux que permite administrar la ejecución de tareas mediante una interfaz de línea de comandos (CLI) y un daemon. Ofrece ejecución concurrente, seguimiento de trabajos, consulta de resultados, cancelación, persistencia y recuperación conservadora.

## 🎯 Propósito

Desarrollar una herramienta sencilla para:

- Ejecutar comandos y programas de forma concurrente.
- Consultar estados y resultados en tiempo real.
- Cancelar trabajos.
- Conservar el historial de ejecución y recuperarse de interrupciones.

## ✨ Funcionalidades implementadas

- **Cola FIFO y concurrencia (Avance 2.1):** hasta 3 procesos principales simultáneos y 100 trabajos en espera por defecto. Límites configurables y rechazo de solicitudes cuando se agota la capacidad.
- **Persistencia y recuperación (Avance 2.2):** almacenamiento SQLite y recuperación conservadora, sin reejecución automática de trabajos.
- **Socket Unix configurable (Avance 2.5B):** selección del endpoint mediante `--socket-path` y `JOBSY_SOCKET_PATH`.
- **Observabilidad:** consulta del estado del daemon mediante `jobsy health` y registro de eventos en bitácoras.
- **Administración de trabajos:** identificación mediante UUID y estados `QUEUED`, `RUNNING`, `SUCCEEDED`, `FAILED` y `CANCELED`.
- **Semántica de duplicados (RF-27):** se incorpora el comportamiento definido para identificar y gestionar solicitudes duplicadas, documentado en [`semantica-duplicados.md`](docs/technical-guide/semantica-duplicados.md).

## 👥 Integrantes

- **Gomez Rubio Alexia:** alexia.gomez5516@alumnos.udg.mx
- **Ibarra Bravo Jocelyn Naomi:** jocelyn.ibarra4401@alumnos.udg.mx
- **Lopez Fletes Benjamin:** benjamin.lopez4157@alumnos.udg.mx
- **Rico Morones Denice Estefania:** denice.rico4211@alumnos.udg.mx

## 🎭 Asignación de roles

- **Arquitectura:** Benjamin Lopez Fletes.
- **Project Management & Backend:** Jocelyn Naomi Ibarra Bravo.
- **Backend Development:** Denice Estefania Rico Morones.
- **QA y Certificación:** Alexia Gomez Rubio.

## 🏗️ Arquitectura

El proyecto está organizado modularmente dentro de `src/`.

| Componente | Responsabilidad |
| --- | --- |
| `src/client/cli.py` | Interfaz de línea de comandos. |
| `src/daemon/config.py` | Configuración y validación del daemon. |
| `src/daemon/executor.py` | Ejecución de procesos. |
| `src/daemon/job_manager.py` | Gestión del ciclo de vida y estados de los trabajos. |
| `src/daemon/job_repository.py` | Almacenamiento persistente e integridad de los registros de trabajos.|
| `src/daemon/job.py` | Modelo de datos y metadatos. |
| `src/daemon/logger.py` | Registro de eventos y errores del sistema. |
| `src/daemon/persistence.py` | Gestión de persistencia, sesiones y recuperación del daemon. |
| `src/daemon/process_identity.py` | Identificación y verificación de procesos Linux. |
| `src/daemon/recovery.py` | Recuperación y reconciliación del estado de los trabajos tras un reinicio. |
| `src/daemon/scheduler.py` | Planificación de trabajos, gestión de cola y control de ejecuciones concurrentes. |
| `src/daemon/server.py` | Servicio daemon y apagado controlado. |
| `src/protocol/endpoint.py` | Validación y resolución de rutas del socket Unix. |
| `src/protocol/validation.py` | Validación y sanitización de comandos. |

## 💻 Instalación

**Entorno de referencia:** Ubuntu 26.04.1 LTS sobre WSL2 con Python 3.14.4. Python >=3.10 es el mínimo declarado, pero no se verificó en esta tarea. No se certifican Linux nativo ni otras distribuciones.

Se requieren `venv` y `pip`. Desde la raíz del repositorio:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

La instalación editable refleja los cambios del código del clon. Para una instalación normal, utiliza `python -m pip install .`.

## 🚀 Inicio rápido

Antes de iniciar el daemon, comprueba que no exista un servicio o socket previo. Si existe `/tmp/jobsy.sock`, **no inicies otro daemon ni elimines el socket**; consulta con su operador.

En una sesión de prueba autorizada sin daemon ni socket previo, ejecuta:

```bash
jobsy-daemon
```

En otra terminal, activa el mismo entorno virtual:

```bash
execute sleep 20
jobsy list
jobsy status ID_DEVUELTO
jobsy output ID_DEVUELTO
jobsy health
jobsy cancel ID_DEVUELTO
```

Sustituye `ID_DEVUELTO` por el UUID del trabajo propio. Para detener tu daemon de prueba, utiliza `Ctrl+C` únicamente si estás autorizado y no atiende trabajos ajenos.

La forma histórica `python3 -m src.daemon.server` también está disponible desde la raíz del repositorio. **No ejecutes ambas formas simultáneamente para la misma instancia.**

## ⚠️ Advertencias importantes

- Una solicitud aceptada no garantiza que el proceso termine correctamente; verifica su estado y resultados.
- La cancelación activa no libera la reserva hasta confirmar la finalización y recolección del proceso.
- La recuperación no reejecuta automáticamente trabajos y puede bloquear el arranque ante procesos supervivientes o situaciones inciertas.
- **No mates procesos solo por su PID registrado ni borres SQLite, journals, `daemon.lock` o sockets para eludir bloqueos de recuperación.**
- Cambiar `--data-dir` selecciona otra base de datos; no migra el historial ni resuelve de forma segura un bloqueo previo.
- RF-16 sigue parcial: no hay opciones `--host` ni `--port`. La interfaz TCP requiere aprobación posterior.
- Los comandos cortos `list`, `status` y `cancel` pueden colisionar con herramientas del sistema. Usa `jobsy list`, `jobsy status` y `jobsy cancel` si existe una ambigüedad.

Consulta la [guía de usuario](docs/user-guide/README.md) antes de realizar operaciones de configuración, recuperación o diagnóstico.

## 🧪 Pruebas y verificación

La verificación local registró **105 pruebas aprobadas en Ubuntu WSL**, sin fallos ni omisiones en esa ejecución. Este resultado corresponde a verificación de desarrollo; no constituye certificación formal de QA ni acredita compatibilidad con todas las plataformas declaradas.

Las pruebas nuevas permanecen en la copia local excluida del commit descrito. No ejecutes `test_queue_ipc.py` ni el descubrimiento global de pruebas hasta que QA adapte la prueba IPC para utilizar un socket y un directorio de datos temporales.

La verificación independiente y la evidencia de QA corresponden a Alexia Gomez Rubio. Consulta el [traspaso técnico a Alexia](docs/technical-guide/ADR-006-Recuperacion.md#traspaso-técnico-a-alexia).

## 📚 Documentación importante para este segundo avance

- [Guía de usuario](docs/user-guide/README.md): instalación, comandos, configuración y solución de problemas.
- [Contratos públicos](docs/technical-guide/interfaces-publicas.md): interfaces del sistema.
- [ADR-004: Cola y límite de concurrencia](docs/technical-guide/ADR-004-Cola-y-Limite-de-Concurrencia.md).
- [ADR-006: Recuperación](docs/technical-guide/ADR-006-Recuperacion.md).
- [ADR-007: Cancelación](docs/technical-guide/ADR-007-Cancelacion.md).
- [Semántica de duplicados (RF-27)](docs/technical-guide/semantica-duplicados.md): definición del comportamiento de Jobsy ante solicitudes duplicadas.


## 📌 Estado del proyecto

Jobsy incorpora ejecución concurrente, cola acotada, persistencia SQLite, recuperación conservadora y socket Unix configurable. La verificación independiente y la certificación formal de QA siguen pendientes según el estado documentado del proyecto.

Proximo hito: Avance Final
