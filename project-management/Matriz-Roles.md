# 🎭 Asignación de Roles y Responsabilidades — Avance 3 (Entrega Final)

## Correciones antes de empezar Avance Final
*12 de Noviembre al 15 de noviembre*

---


## Benjamín — Arquitecto
*Diseño y especificación del protocolo de red, modelo de seguridad LAN/VPN, definición de arquitectura distribuida y documentación técnica estructural.*

*Fechas: 16 de noviembre al 19 de noviembre*

### Avance 3.2 Protocolo de comunicación (#15)
- **RF-21** (#86) El protocolo deberá delimitar mensajes, identificar errores, incluir comandos para todas las operaciones (incluido el resumen de salud del servicio) y tolerar lecturas o escrituras parciales.
- **RNF-14** (#19) El sistema deberá validar longitudes y formato de todos los mensajes de red.
- **RNF-24** (#87) El protocolo deberá funcionar con mensajes fragmentados y múltiples solicitudes secuenciales.
- **RNF-32** (#88) El protocolo deberá definir compatibilidad de versión y rechazar mensajes incompatibles de forma explícita.

### Avance 3.4 Seguridad y acceso remoto (#17)
- **RF-20** (#90)  El servicio deberá restringir el acceso remoto a una lista configurable de redes o direcciones permitidas de la LAN/VPN.
- **RNF-12** (#91) El servicio no deberá escuchar en interfaces públicas de forma predeterminada.
- **RNF-13** (#92) El acceso remoto deberá limitarse a localhost, subredes privadas autorizadas o VPN configurada.
- **RNF-16** (#94) El proceso deberá aplicar el principio de mínimo privilegio y documentar el modelo de amenazas básico.

### Avance 3.6 Entregables Finales y Documentación (#120)
- **ADRs completos y actualizados** (#123) Documentar las decisiones arquitectónicas referentes al protocolo de red, concurrencia distribuida y modelo de seguridad LAN/VPN.
- **Change Request y Análisis de Impacto** (#125) Documento formal del control de cambios aplicado para la migración a la arquitectura de red.

---
## Revisión de PR de Arquitectura (Alexia)
*Fechas: 19 de noviembre al 20 de noviembre*
---

## Denice — Backend Developer
*Implementación del servicio de red, cliente remoto, gestión de sockets, manejo de múltiples clientes, concurrencia de red y seguridad.*

*Fechas: 20 de noviembre al 24 de noviembre*

### Avance 3.1 Servicio de red y cliente remoto (#14)
- **RF-18** (#84) Un cliente en otro equipo deberá poder enviar, consultar status, consultar estado/salud del servicio, listar, recuperar salida (stdout/stderr) y cancelar trabajos mediante un protocolo documentado.
- **RF-19** (#85) El servicio deberá admitir operación local y remota sin cambiar la semántica de las operaciones.


### Avance 3.3 Desconexiones y múltiples clientes (#16)
- **RF-22** (#89) El sistema deberá manejar desconexiones del cliente/clientes sin terminar el servicio ni corromper trabajos.

### Avance 3.4 Seguridad y acceso remoto (#17)
- **RNF-15** (#93) Los registros no deberán exponer secretos ni contenido sensible de configuración.
- **RNF-26** (#95) La demostración remota se realizará exclusivamente en la misma red privada o por VPN; no se aceptará exposición directa a Internet.

### Avance 3.5 Verificación final (#20)
- **RNF-25** (#28) Asegurar la liberación de sockets, descriptores y procesos hijos al cerrar el servicio.
- **RNF-05** (#96) La consulta de estado deberá responder en máximo 1 segundo para 100 trabajos almacenados en el entorno de prueba.
---
## Revisión de PR de Backend (Alexia)
*Fechas: 24 de noviembre al 25 de noviembre*
---

## Jocelyn — Project Manager
*Gestión del repositorio, documentación final de entrega, seguimiento de incidentes, trazabilidad global y liberación de versión.*

*Fechas: 22 de noviembre al 28 de noviembre*

### Avance 3.5 Verificación final (#20)
- **RNF-34** (#97) Toda decisión que modifique seguridad, consistencia o recuperación deberá incluir análisis de riesgo y prueba asociada.

### Avance 3.6 Entregables Finales y Documentación (#120)
- **Informe de Lanzamiento y Etiquetado** (#121) Etiquetado de versión final en Git y Release Notes.
- **Guía de Usuario y Guía Técnica** (#122)  Incorporar las instrucciones de uso del cliente remoto, CLI, configuración de red y especificación detallada del protocolo IPC/Sockets.
- **Consolidación de uso de IA** (#124) Integración final de bitácoras de herramientas asistidas por IA.
- **README.md Principal** (#129) Instrucciones completas de clonación, compilación y ejecución de red.
- **Evidencia de Gestión** (#130) Registro de participación y coordinación del equipo.
- **Defectos y Limitaciones** (#131) Documentación de restricciones operativas y limitaciones técnicas.
- **Registro de Incidente Crítico** (#132) Análisis post-mortem documentado sobre sockets, concurrencia o red.

---

## Alexia — QA y Certificación
*Validación técnica de red, automatización de pruebas, matriz de trazabilidad y generación de evidencias de operación.*

*Fechas: 26 de noviembre al 30 de noviembre*

### Avance 3.6 Entregables Finales y Documentación (#120)
- **Matriz de Trazabilidad y Resultados PASS/FAIL** (#126) Mapeo integral de todos los requisitos (RF/RNF) desde la línea base local hasta la versión de red.
- **Script de Verificación y Pruebas Automatizadas** (#127) Actualización del script único de verificación (verify.sh) y la batería de pruebas automatizadas para validar la operación de red local/remota. 
- **Evidencia de Operación y Verificación Cruzada** (#128) Registro de logs, evidencias de ejecución en LAN/VPN y documentación del proceso de revisión por pares (Peer Review). 

### Entregables de QA y Certificación para Entrega Final
- Casos de prueba de integración remota y estrés de sockets.
- Ejecución completa del script `verify.sh` en limpio.
- Reporte cruzado de validación PASS/FAIL para la versión etiquetada.