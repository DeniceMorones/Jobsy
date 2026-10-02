# Modelo preliminar de estados de Jobsy

**Proyecto:** Jobsy  
**Avance:** Avance 01 - Local MVP  
**Issue relacionado:** #43 - Modelo preliminar de estados

## 1. Objetivo

Definir los estados por los que puede pasar un trabajo dentro del MVP local de Jobsy, desde su creación hasta que finaliza o es cancelado.

El modelo corresponde con el comportamiento implementado actualmente en el proyecto.

## 2. Estados

- `QUEUED`: el trabajo fue creado y está pendiente de ejecución.
- `RUNNING`: el trabajo se encuentra en ejecución.
- `SUCCEEDED`: el trabajo terminó correctamente con código de salida `0`.
- `FAILED`: el trabajo terminó con un código de salida diferente de `0`.
- `CANCELED`: el trabajo fue cancelado antes de terminar normalmente.

`QUEUED` es el estado inicial.

`SUCCEEDED`, `FAILED` y `CANCELED` son estados finales.

## 3. Diagrama de estados

```text
QUEUED
 ├──> RUNNING
 │      ├──> SUCCEEDED
 │      ├──> FAILED
 │      └──> CANCELED
 │
 └──> CANCELED
```

## 4. Transiciones válidas

| Estado actual | Evento | Nuevo estado |
| --- | --- | --- |
| QUEUED | Comienza la ejecución | RUNNING |
| QUEUED | Se solicita cancelación | CANCELED |
| RUNNING | Termina con código 0 | SUCCEEDED |
| RUNNING | Termina con código diferente de 0 | FAILED |
| RUNNING | Se solicita cancelación | CANCELED |

## 5. Reglas básicas

- Todo trabajo comienza en `QUEUED`.
- Un trabajo en `QUEUED` puede comenzar su ejecución o ser cancelado.
- Un trabajo en `RUNNING` puede terminar correctamente, fallar o ser cancelado.
- Los estados `SUCCEEDED`, `FAILED` y `CANCELED` son terminales.
- Un trabajo que llega a un estado terminal no debe regresar a `QUEUED` o `RUNNING`.

Este modelo es preliminar y puede ampliarse en avances posteriores si se requieren estados adicionales para persistencia, recuperación o manejo de cancelaciones.