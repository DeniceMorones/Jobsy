# RF-27: Especificación y Documentación de Semántica para Solicitudes Duplicadas

## 1. Contexto y Alcance
El requisito **RF-27** establece que:
> *"Una solicitud duplicada o reenviada no deberá crear estados contradictorios; el equipo deberá documentar la semántica elegida para identificar o tratar duplicados."*

En **Jobsy**, las solicitudes se transmiten mediante un protocolo IPC basado en Sockets UNIX de flujo de bytes (`SOCK_STREAM`) utilizando payloads JSON. Debido a reintentos del cliente, fallas parciales de red o dobles ejecuciones accidentales, una misma solicitud puede ser procesada más de una vez.

Esta documentación detalla las garantías del sistema para evitar estados contradictorios, la clasificación por cada tipo de acción del socket IPC y los mecanismos de consistencia implementados.

---

## 2. Semántica Elegida por Acción (IPC Request)

Jobsy aplica distintas estrategias según el impacto de la operación en el estado del sistema:

### A. Operaciones de Consulta (`list`, `status`, `output`)
* **Semántica:** **Idempotencia Absoluta (Lectura Segura)**.
* **Comportamiento:**
  * Son operaciones de solo lectura que retornan instantáneas (*snapshots*) inmutables de los objetos `Job`.
  * Reenviar o duplicar cualquiera de estas solicitudes N veces produce resultados consistentes y no altera contadores, marcas de tiempo ni estados internos.

### B. Operación de Cancelación (`cancel`)
* **Semántica:** **Idempotencia Condicionada / Transición Terminal Protegida**.
* **Comportamiento:**
  * Si se recibe una petición de cancelación sobre un trabajo activo (`QUEUED` o `RUNNING`), el sistema cambia su estado a `CANCELED` e inicia la terminación controlada del proceso.
  * Si se reenvía la solicitud de cancelación sobre un trabajo que ya se encuentra en estado `CANCELED` o en un estado terminal (`SUCCEEDED`, `FAILED`), el sistema no altera el historial ni reactiva procesos de limpieza. En su lugar, responde de forma determinista con un error explícito (`ValueError`):
    * *"La cancelación de este trabajo ya fue solicitada (estado CANCELED)."*
    * *"No se puede cancelar un trabajo con estado 'SUCCEEDED'/'FAILED'."*

### C. Operación de Creación y Ejecución (`run`)
* **Semántica:** **Atomicidad de Instancia y Unicidad por UUID**.
* **Comportamiento:**
  * Cada petición `run` representa una orden discreta de ejecución.
  * Ante la llegada de una solicitud duplicada o idéntica en comando (ej. `["sleep", "10"]`), el sistema **genera una nueva entidad independiente** asignándole un nuevo identificador universal único (**UUIDv4**).
  * La admisión y la verificación de capacidad de cola (`QueueFullError`) ocurren de forma atómica bajo exclusión mutua, garantizando que nunca se corrompa el orden de la cola FIFO ni se sobreescriba información existente.

---

## 3. Arquitectura y Mecanismos de Consistencia Tecnológica

La prevención de estados contradictorios se soporta sobre tres pilares arquitectónicos en el backend:

1. **Control de Concurrencia mediante Exclusión Mutua (`JobManager` & `Scheduler`):**
   * Las solicitudes concurrentes se procesan bajo un bloqueo de hilos explícito (`threading.Condition` con `RLock`).
   * No existen condiciones de carrera al consultar o alterar la máquina de estados de un trabajo.

2. **Control de Versiones Optimista (`JobRepository`):**
   * Toda modificación de un trabajo exige hacer coincidir el número de versión esperado (`expected_version`).
   * Si una solicitud retrasada o duplicada intenta actualizar un trabajo cuya versión ya fue incrementada por otro hilo, el almacenamiento rechaza la transacción con un `VersionConflict`.

3. **Reconciliación Segura al Reiniciar (`RecoveryService` & `process_identity`):**
   * Durante un reinicio o recuperación tras fallos del daemon, el sistema inspecciona los PIDs activos e identificadores de arranque en `/proc` (`boot_id` y `process_start_ticks`) antes de modificar estados inconclusos, impidiendo que reejecuciones o comandos huérfanos interfieran con nuevos procesos.

---

## 4. Matriz Resumen de Cumplimiento RF-27

| Acción IPC | Propiedad de Red | Resultado ante Solicitud Duplicada | Garantía de Consistencia |
| :--- | :--- | :--- | :--- |
| **`list`** | Idempotente | Mismo listado de trabajos sin modificaciones. | Snapshots desconectadas de lectura. |
| **`status`** | Idempotente | Mismos metadatos y diagnósticos del trabajo. | Consulta de solo lectura. |
| **`output`** | Idempotente | Mismos flujos `stdout` y `stderr`. | Lectura inmutable de resultados. |
| **`cancel`** | Idempotente / Controlada | Confirmación inicial o rechazo explícito con `ValueError`. | Máquina de estados con transición unidireccional a terminales. |
| **`run`** | No Idempotente (Atómica) | Creación de un trabajo adicional con UUID independiente. | Registro atómico con UUID + Transacción `BEGIN IMMEDIATE` en SQLite. |