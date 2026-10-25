# Registro de Riesgos — JobRunner Network Edition

**Proyecto:** JobRunner  
**Avance:** Entrega final  

## Riesgos identificados

| ID | Riesgo | Impacto | Mitigación |
|---|---|---|---|
| R-01 | Retrasos en la implementación del servicio de red y el cliente remoto. | Alto | Priorizar la comunicación remota y dividir las tareas entre los integrantes. |
| R-02 | Vulnerabilidades de seguridad que permitan conexiones no autorizadas. | Alto | Restringir el acceso a localhost, LAN autorizada o VPN y probar el rechazo de clientes no autorizados. |
| R-03 | Fallos por mensajes fragmentados, desconexiones o múltiples clientes simultáneos. | Alto | Implementar pruebas de integración para comunicación, concurrencia y recuperación ante desconexiones. |
| R-04 | Regresiones en la cola, cancelación o persistencia al integrar los nuevos componentes de red. | Alto | Ejecutar las pruebas existentes y las pruebas de regresión después de cada cambio importante. |
| R-05 | Pérdida o inconsistencia del historial y las salidas después de una falla o reinicio. | Alto | Validar la recuperación de trabajos y la integridad de los datos persistidos. |
| R-06 | Liberación incompleta de procesos, archivos o sockets durante fallos o cierres del servicio. | Alto | Probar el cierre controlado, la cancelación y la recuperación de recursos. |
| R-07 | Documentación, matriz de trazabilidad o entregables de QA incompletos. | Medio | Asignar responsables y revisar periódicamente la lista de entregables finales. |
| R-08 | Construcción no reproducible o fallos al instalar desde un clon limpio. | Alto | Verificar la instalación y ejecución en un entorno limpio siguiendo la guía de usuario. |
| R-09 | Defectos detectados durante la verificación cruzada o la demostración final. | Alto | Reservar tiempo para corregir defectos, ejecutar regresiones y recopilar evidencias. |
| R-10 | Dificultad de algún integrante para explicar o demostrar su implementación. | Medio | Revisar los módulos, ADR, requisitos y pruebas asignados a cada integrante. |

## Seguimiento

Los riesgos se revisarán durante el desarrollo y antes de la entrega final. Cada riesgo deberá actualizarse según su estado y las evidencias de mitigación disponibles.

**Criterio de cierre:** No considerar mitigado un riesgo crítico hasta contar con evidencia verificable de las pruebas correspondientes.