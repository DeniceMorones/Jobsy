# Jobsy

## 🎯 Propósito:
Desarrollar una herramienta sencilla para administrar tareas en el sistema Linux, permitiendo:
* Agregar comandos o programas.
* Ejecutarlos de manera simultánea (concurrente).
* Revisar su progreso en tiempo real.
* Obtener resultados (salidas y errores).
* Detener la ejecución cuando sea necesario.

## 👥 Integrantes:
* **Gomez Rubio Alexia**: alexia.gomez5516@alumnos.udg.mx
* **Ibarra Bravo Jocelyn Naomi**: jocelyn.ibarra4401@alumnos.udg.mx
* **Lopez Fletes Benjamin**: benjamin.lopez4157@alumnos.udg.mx
* **Rico Morones Denice Estefania**: denice.rico4211@alumnos.udg.mx

## 🛠️ Construcción provisional:
Jobsy será desarrollado para linux como **una herramienta de línea de comandos (CLI)** para registrar, ejecutar, supervisar y controlaar trabajos.
### Consideraciones técnicas clave:
* **Administración:** Un servicio centralizado se encargará de gestionar el ciclo de vida de los trabajos, controlar la concurrencia, ejecutar procesos y capturar `stdout`y `stderr`.
* **Mecanismos del sistema:** Se utilizará primitivas nativas de Linux para procesos, señales, concurrencia e IPC.
* **Alcance de red:** El sistema funcionará de forma local en su primera etapa y posteriormente permitirá acceso remoto restringido a una red LAN autorizada o VPN.

> ⚠️ **Nota:** La arquitectura final, lenguaje de programación, protocolo de red, mecanismos de cancelación, persistencia y administración de recursos se encuentran en evaluación. Se formalizarán mediante registros de decisiones de arquitectura (**ADR**). Esta propuesta es provisional y está sujeta a cambios durante las revisiones técnicas.

## 📊 Estado del proyecto:
Estado: Inicio/Planeación
Código Funcional: No disponible todavía
Próximo hito: Avance 1