# ADR-001: Lenguaje y stack

**Estado:** Aceptado  
**Issue relacionado:** #46

## Contexto

Jobsy necesita ejecutar y administrar procesos en Linux mediante una herramienta de línea de comandos.

El MVP actual utiliza Python y módulos de la biblioteca estándar para implementar la CLI, el manejo de procesos, la concurrencia y la representación de trabajos.

## Decisión

Se utilizará Python como lenguaje principal para el desarrollo de Jobsy.

Para el MVP local se utilizarán principalmente herramientas de la biblioteca estándar, entre ellas:

- `argparse` para la interfaz de línea de comandos.
- `subprocess` para ejecutar y controlar procesos.
- `threading` para evitar bloquear el servicio mientras se ejecutan trabajos.
- `dataclasses` para representar los trabajos y sus metadatos.

## Alternativas consideradas

- Java: ofrece buenas herramientas para concurrencia y aplicaciones de servicio, pero requiere una estructura y configuración más pesada para el alcance actual del MVP.
- JavaScript con Node.js: permite trabajar fácilmente con operaciones asíncronas, pero Python ofrece herramientas más directas para el manejo de procesos y se adapta mejor a la implementación actual del proyecto.

## Consecuencias

Python permite mantener el MVP simple y trabajar directamente con las herramientas necesarias para ejecutar y administrar procesos en Linux.

En avances posteriores será necesario revisar el rendimiento y el manejo de concurrencia conforme aumente la cantidad de trabajos y se agreguen nuevas funcionalidades.
