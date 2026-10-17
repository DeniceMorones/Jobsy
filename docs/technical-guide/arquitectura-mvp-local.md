# Arquitectura de Jobsy: Avance 2.1 y referencia del MVP local

## Arquitectura vigente: Avance 2.1

Esta sección sustituye las descripciones del MVP histórico que siguen abajo.
Requisitos: RF-03 (#52), RF-05 (#23), RNF-07 (#26).
Decisiones y límites: [ADR-004](ADR-004-Cola-y-Limite-de-Concurrencia.md).

Flujo real: CLI instalada o módulo -> JSON por socket Unix -> DaemonServer ->
JobManager.submit_job -> Scheduler -> Executor -> proceso principal.
La respuesta de admisión devuelve el ID, no espera al fin de la ejecución.

- config.py: configuración inmutable validada y argumentos del daemon.
- job_manager.py: registro en RAM, admisión atómica, snapshots y cancelación.
- scheduler.py: FIFO acotada, reservas, despachador y supervisores.
- executor.py: Popen, captura separada, terminación y recolección.
- job.py: cinco estados públicos y evento interno de cancelación.
- server.py: IPC existente, señales y apagado coordinado.

La Condition compartida protege las decisiones de admisión, promoción,
lanzamiento y cancelación. Los procesos se esperan fuera del lock.
Una reserva cubre desde la admisión directa o promoción hasta la recolección,
incluso si el estado público ya es CANCELED y hay un proceso en limpieza.
El fallo de lanzamiento o la cancelación antes de crear el proceso libera
la reserva sin recolección. Si la limpieza de un proceso no se confirma, se
conserva su reserva para impedir exceso de procesos.

pending es la cola FIFO de espera acotada; ready es la cola de reservas listas
para lanzar. Un despachador único procesa ready y publica Popen bajo el lock.
admitted evita un segundo lanzamiento del mismo ID, pero no deduplica
solicitudes IPC reenviadas. FIFO se refiere al orden de admisión/lanzamiento,
no al de finalización. Con queue_capacity=0 no hay espera en pending, aunque
un trabajo reservado puede seguir QUEUED hasta su lanzamiento.

Por defecto se permiten tres procesos principales y cien trabajos en espera.
Las opciones --max-running y --queue-capacity se aplican al arranque, tanto
con jobsy-daemon como con python3 -m src.daemon.server.
No se añade persistencia, recuperación, control de descendientes ni un nuevo
protocolo. La recepción IPC sigue siendo secuencial; el gestor sí sincroniza
llamadas concurrentes desde varios hilos.

El apagado cancela pendientes y concede cinco segundos de gracia a los activos;
después solicita su terminación y une los hilos fuera del lock. No se garantiza
un tiempo total de apagado de cinco segundos. La política de escalamiento
permanece encapsulada en Executor.terminate_and_reap para integración con el
trabajo de Backend, sin introducir nuevos estados ni mensajes IPC.

La [nota técnica de ADR-004](ADR-004-Cola-y-Limite-de-Concurrencia.md#nota-técnica-de-verificación-de-benjamin)
registra las 46 pruebas aprobadas por Benjamin en Ubuntu WSL. No reemplaza
los entregables formales de QA de Alexia.

## Referencia histórica: diseño del Avance 01

El contenido siguiente documenta el diseño inicial, no el estado vigente.

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
