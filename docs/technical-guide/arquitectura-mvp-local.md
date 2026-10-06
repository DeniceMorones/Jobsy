# Arquitectura inicial del MVP local de Jobsy

**Proyecto:** Jobsy  
**Avance:** Avance 01 - Local MVP  
**Responsable:** Benjamin Lopez Fletes  
**Issue relacionado:** #42 - Arquitectura inicial del MVP local  

## 1. Objetivo

El MVP local de Jobsy tiene como objetivo permitir la ejecución y administración de trabajos en Linux desde una interfaz de línea de comandos.

En esta etapa el sistema funcionará únicamente de forma local. La comunicación remota será incorporada en avances posteriores.

El sistema deberá permitir:

- Enviar un trabajo.
- Obtener un identificador único.
- Ejecutar el trabajo como un proceso separado.
- Consultar su estado.
- Listar trabajos.
- Solicitar su cancelación.
- Obtener su código de salida.
- Manejar comandos inválidos sin detener el servicio.

## 2. Arquitectura general

La arquitectura inicial se divide en los siguientes componentes:

```text
Usuario
   |
   v
Cliente CLI
   |
   v
Job Manager
   |
   +------> Job Registry
   |
   v
Process Executor
   |
   v
Proceso Linux

```

## 3. Cliente CLI

El cliente CLI será la parte con la que interactúa el usuario.

Permitirá:

- Enviar un nuevo trabajo.
- Consultar el estado de un trabajo.
- Listar los trabajos registrados.
- Solicitar la cancelación de un trabajo.
- Consultar su código de salida.

El cliente no administrará directamente los procesos de Linux.

## 4. Job Manager

El Job Manager será el componente encargado de coordinar los trabajos.

Sus responsabilidades serán:

- Recibir las solicitudes del cliente.
- Registrar los trabajos.
- Asociar cada trabajo con un identificador único.
- Consultar su estado.
- Coordinar su ejecución.
- Coordinar su cancelación.
- Actualizar la información cuando un proceso termine.

## 5. Job Registry

El Job Registry mantendrá la información de los trabajos registrados.

Cada trabajo podrá almacenar:

- Job ID.
- Comando.
- Estado.
- PID.
- Código de salida.

El modelo formal de estados será definido en el Issue #43.

## 6. Process Executor

El Process Executor se encargará de ejecutar los comandos como procesos separados de Linux.

Sus responsabilidades serán:

- Crear el proceso.
- Obtener su PID.
- Detectar cuándo termina.
- Obtener su código de salida.
- Solicitar su terminación cuando el usuario cancele el trabajo.

Si un trabajo falla, el servicio principal de Jobsy deberá continuar funcionando.

## 7. Flujo de un trabajo

El flujo general será:

1. El usuario envía un comando mediante el cliente.
2. Jobsy registra el trabajo y genera un Job ID.
3. El Job Manager solicita su ejecución.
4. El Process Executor crea el proceso.
5. El PID queda relacionado con el Job ID.
6. Mientras el proceso se ejecuta, su estado puede ser consultado.
7. Cuando el proceso termina, Jobsy obtiene su código de salida.
8. El resultado queda registrado para futuras consultas.

## 8. Manejo de errores

Si el usuario intenta ejecutar un comando inválido, el error deberá afectar solamente a ese trabajo.

Jobsy deberá continuar funcionando y aceptar nuevas solicitudes.

## 9. Estructura relacionada

```text
src/
├── client/
│   └── Interfaz CLI
├── daemon/
│   └── Administración y ejecución de trabajos
└── protocol/
    └── Estructuras compartidas
```

La documentación técnica se encuentra en:

```text
docs/technical-guide/
```

La evidencia y pruebas se almacenarán en:

```text
verif/
├── verification-plan/
├── test-cases/
├── scripts/
├── test-data/
└── results/
```

## 10. Limitaciones actuales

Para el Avance 01:

- No existe comunicación remota.
- No existe operación mediante LAN o VPN.
- El modelo de estados todavía es preliminar.
- La persistencia definitiva todavía no está definida.
- La arquitectura podrá cambiar conforme avance el proyecto.

## 11. Evolución futura

Más adelante se agregará una capa de red:

```text
Cliente remoto
     |
     v
Capa de red
     |
     v
Job Manager
     |
     v
Process Executor
```

Esto permitirá reutilizar el núcleo local desarrollado durante el Avance 01.

## 12. Trazabilidad

Este documento corresponde al:

**Issue #42 - Arquitectura inicial del MVP local**

También está relacionado con:

- RF-06 - Ciclo de vida y consulta de trabajos.
- Issue #43 - Modelo preliminar de estados.
- Issue #46 - ADR iniciales.