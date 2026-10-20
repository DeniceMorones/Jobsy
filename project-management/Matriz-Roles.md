# 🎭 Asignación de Roles y Responsabilidades — Avance 2

## Benjamín — Arquitecto
*Líder técnico en arquitectura de concurrencia, diseño de persistencia y estructura de código local.*
##COMPLETADO
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
## Periodo: 19 de octubre al 21 de octubre

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
## Revisión de pr de Denice (Alexia)
## Periodo: 21 de octubre al 22 de octubre

---

## Jocelyn — PM y Backend Developer
*Coordinación, desarrollo de robustez, límites de la cola, observabilidad y operación.*
## Periodo: 23 de octubre al 26 de octubre

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
## Revisión Pr de Naomi (Alexia)
## Periodo: 26 de octubre al 27 de octubre

---

## Alexia — QA y Certificación
*Validación técnica de robustez, estrés de recursos, pruebas automatizadas e incidentes.*
## Periodo para terminar lo que haga falta de Alexia: 27 de octubre al 30 de octubre

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
