# 🎭 Asignación de Roles y Responsabilidades — Avance 2

## Benjamín — Arquitecto
*Líder técnico en arquitectura de concurrencia, diseño de persistencia y estructura de código local.*

### Avance 2.1 Cola y concurrencia (#9)
- **RF-03** (#52) Cola cuando no exista capacidad inmediata.
- **RF-05** (#23) Límite configurable de trabajos simultáneos.
- **RNF-07** (#26) Control de concurrencia para no superar el límite.

### Avance 2.2 Salidas, persistencia y recuperación (#10)
- **RF-12** (#56) Conservación de metadatos y resultados post-reinicie.
- **RF-13** (#57) Recuperación del historial persistente al arrancar.
- **RNF-11** (#60) Escritura persistente para evitar estados parcialmente actualizados.
- **RNF-28** (#61) Actualizaciones persistentes atómicas y recuperables.

### Avance 2.5 Configuración, operación y calidad local (#13)
- **RF-16** (#72) Configuración de directorio de datos, concurrencia, interfaz y puerto.
- **RNF-01** (#74) Compilación y ejecución en la distribución Linux declarada.
- **RNF-17** (#77) Organización modular de código sin archivos monolíticos.
- **RNF-18** (#78) Documentación de interfaces públicas y ADRs de concurrencia, persistencia, recuperación y cancelación.

---

## Denice — Backend Developer
*Desarrollo del núcleo de ejecución, captura de I/O, políticas de cancelación y escalamiento.*

### Avance 2.1 Cola y concurrencia (#9)
- **RNF-04** (#25) Soportar al menos 3 trabajos simultáneos bajo el límite.

### Avance 2.2 Salidas, persistencia y recuperación (#10)
- **RF-11** (#55) Captura separada de stdout y stderr sin mezclarlos.
- **RNF-06** (#58) Soporte de al menos 500 registros sin pérdida de metadatos.
- **RNF-10** (#59) No reportar como `RUNNING` procesos no controlados tras reinicio.

### Avance 2.3 Cancelación y condiciones de conflicto (#11)
- **RF-26** (#63) Coherencia ante solicitudes concurrentes de cancelación.
- **RF-29** (#24) Detección de terminación inesperada, liberación de recursos y diagnóstico.
- **RF-30** (#65) Política de escalamiento documentada para cancelación de trabajos hung/stuck.

### Avance 2.4 Observabilidad y robustez (#12)
- **RNF-09** (#27) Aislamiento de fallas: terminación anormal de un trabajo no afecta a otros.
- **RNF-30** (#29) Prevención de procesos huérfanos tras falla del servicio.

---

## Jocelyn — PM y Backend Developer
*Coordinación, desarrollo de robustez, límites de la cola, observabilidad y operación.*

### Avance 2.1 Cola y concurrencia (#9)
- **RF-25** (#53) Rechazo explícito cuando la cola alcance capacidad.
- **RNF-29** (#54) Aplicación de contrapresión ante límites de cola/memoria/descriptores.

### Avance 2.3 Cancelación y condiciones de conflicto (#11)
- **RF-27** (#64) Definición semántica y manejo de solicitudes duplicadas/reenviadas.

### Avance 2.4 Observabilidad y robustez (#12)
- **RF-14** (#66) Bitácora de eventos y errores con marca temporal e ID de trabajo.
- **RF-23** (#67) Rechazo y registro de solicitudes que excedan límites.
- **RF-28** (#68) Conservación de estado coherente ante desconexión de clientes.
- **RNF-08** (#69) Resiliencia del servicio ante solicitudes inválidas o desconexiones.
- **RNF-27** (#70) Garantía de transiciones de estado consistentes.

### Avance 2.5 Configuración, operación y calidad local (#13)
- **RF-24** (#73) Resumen de salud del servicio (trabajos activos, en cola, errores).
- **RNF-21** (#81) Mensajes de error claros con causa y acción sugerida.
- **RNF-22** (#82) Correlación en bitácora entre solicitud y trabajo.
- **RNF-23** (#83) Guía de Usuario actualizada, seguimiento de entregables, AI-LOG, Registro de Riesgos e Issues/Cronograma.

---

## Alexia — QA y Certificación
*Validación técnica de robustez, estrés de recursos, pruebas automatizadas e incidentes.*

### Avance 2.2 Salidas, persistencia y recuperación (#10)
- **RNF-31** (#62) Verificación de recuperación distinguiendo pendientes, terminados e interrumpidos.

### Avance 2.4 Observabilidad y robustez (#12)
- **RNF-33** (#71) Pruebas de estrés y verificación de liberación de memoria, procesos, archivos y sockets.

### Avance 2.5 Configuración, operación y calidad local (#13)
- **RNF-02** (#75) Pruebas de construcción reproducible desde clon limpio.
- **RNF-03** (#76) Verificación de operación sin privilegios de root.
- **RNF-19** (#79) Verificación de compilación limpia sin advertencias.
- **RNF-20** (#80) Automatización del script de verificación mediante un único comando.

### Entregables de QA y Certificación para TR2
- Casos de integración y robustez (códigos `TC-XXX`).
- Matriz de trazabilidad actualizada para el Avance 02.
- Reporte de al menos 1 incidente técnico documentado (síntomas, causa, hipótesis, fix y prueba de regresión).
- Evidencia de la versión demostrada y batería de pruebas ejecutada para la Technical Review 2.

# 🚀 Plan de Ejecución Secuencial y Flujo de Trabajo — Avance 2

Para garantizar que nadie dependa de un módulo no implementado, el desarrollo se organizará en **4 Fases Secuenciales**. Cada fase define qué debe integrar cada miembro antes de avanzar a la siguiente.

---

## 📌 Fase 1: Fundamentos de Arquitectura, Configuración e I/O
> **Objetivo:** Establecer las estructuras de datos base, módulo de configuración y captura independiente de streams antes de manejar concurrencia compleja.

1. **Benjamín (Arquitectura):**
   - Configuración global del servicio: directorio de datos, límites, interfaz/puerto (`#72` / RF-16).
   - Refactorización modular inicial (`#77` / RNF-17).
   - Definición del modelo de datos para la cola en memoria y límites configurables (`#23` / RF-05).

2. **Denice (Backend):**
   - Implementación de captura separada de `stdout` y `stderr` sin interbloqueos (`#55` / RF-11).
   - Aislamiento de ejecución para soportar múltiples procesos sin interferencia (`#25` / RNF-04).

3. **Jocelyn (PM & Backend):**
   - Módulo centralizado de Bitácora / Logging con marca temporal y `job_id` (`#66` / RF-14, `#82` / RNF-22).
   - Esquema básico de manejo y formateo de errores (`#81` / RNF-21).

4. **Alexia (QA):**
   - Diseño inicial de la Matriz de Trazabilidad y plantillas de Casos de Prueba (`TC-XXX`).
   - Verificación del entorno de construcción limpio y permisos no-root (`#75` / RNF-02, `#76` / RNF-03).

---

## 📌 Fase 2: Concurrencia, Manejo de Cola y Cancelaciones
> **Objetivo:** Controlar el flujo de ejecución simultánea, políticas de límites, contrapresión y terminación limpia de procesos.

1. **Benjamín (Arquitectura):**
   - Implementación de la cola de trabajo en memoria cuando se supera la capacidad inmediata (`#52` / RF-03).
   - Control de concurrencia activa para no rebasar el límite configurado (`#26` / RNF-07).

2. **Jocelyn (PM & Backend):**
   - Implementación del rechazo explícito por cola llena (`#53` / RF-25).
   - Mecanismo de contrapresión ante límites de memoria/sockets/cola (`#54` / RNF-29).
   - Validación y semántica de solicitudes duplicadas (`#64` / RF-27).

3. **Denice (Backend):**
   - Detección de terminación inesperada de procesos hijos y recolección de recursos/exit codes (`#24` / RF-29).
   - Prevención de procesos huérfanos/zombis (`#29` / RNF-30).
   - Lógica de cancelación e implementación de política de escalamiento (`SIGINT` -> `SIGTERM` -> `SIGKILL`) (`#63` / RF-26, `#65` / RF-30).

4. **Alexia (QA):**
   - Automatización de pruebas de concurrencia y saturación de cola.
   - Casos de prueba para cancelación de trabajos y verificación de no huérfanos (`#27` / RNF-09).

---

## 📌 Fase 3: Persistencia Atómica, Recuperación y Resiliencia
> **Objetivo:** Guardar el estado en disco de forma segura y garantizar la recuperación consistente tras un reinicio inesperado.
1. **Benjamín (Arquitectura):**
   - Serialización y escritura atómica de metadatos en disco (`.json` / archivos temporales + `rename`) (`#56` / RF-12, `#60` / RNF-11, `#61` / RNF-28).
   - Lógica de lectura e hidratación del historial al arrancar el servicio (`#57` / RF-13).

2. **Denice (Backend):**
   - Validación de estados tras reinicio: marcado coherente de trabajos interrumpidos para no reportar `RUNNING` en procesos extintos (`#59` / RNF-10).
   - Verificación de rendimiento para conservar al menos 500 registros de metadatos (`#58` / RNF-06).

3. **Jocelyn (PM & Backend):**
   - Módulo de salud del servicio (estatus global, activos, en cola, errores) (`#73` / RF-24).
   - Resiliencia del daemon ante clientes desconectados o payloads malformados (`#67` / RF-23, `#68` / RF-28, `#69` / RNF-08).
   - Garantía de máquina de estados consistentes sin regresiones (`#70` / RNF-27).

4. **Alexia (QA):**
   - Pruebas de recuperación de desastres (matar el daemon con `kill -9` y verificar consistencia al reiniciar) (`#62` / RNF-31).
   - Pruebas de estrés y fugas de memoria/descriptores (`#71` / RNF-33).

---

## 📌 Fase 4: Estabilización, Documentación y Evidencia TR2
> **Objetivo:** Consolidar entregables, redacción de ADRs, incidentes técnicos y script único de verificación.

1. **Benjamín (Arquitecto):**
   - Redacción de ADRs definitivos (Concurrencia, Persistencia, Recuperación, Cancelación) (`#78` / RNF-18).
   - Verificación de compilación sin advertencias (`#79` / RNF-19) y soporte Linux oficial (`#74` / RNF-01).

2. **Jocelyn (PM & Backend):**
   - Actualización de Guía de Usuario, AI-LOG, Registro de Riesgos y Cronograma final (`#83` / RNF-23).
   - Coordinación de la presentación y asignación de temas técnicos a defender para la revisión presencial.

3. **Denice (Backend):**
   - Apoyo en la documentación del reporte de al menos 1 Incidente Técnico (síntoma, causa raíz, fix y regresión).
   - Profiling de recursos e inspección final de fuga de descriptores de archivo.

4. **Alexia (QA y Certificación):**
   - Integración del script de verificación ejecutable en un único comando (`#80` / RNF-20).
   - Matriz de Trazabilidad final y generación del reporte con capturas/evidencia de ejecución de la batería de pruebas TR2.