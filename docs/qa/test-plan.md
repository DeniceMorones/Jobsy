# Plan de pruebas — MVP Avance 1

## 1. Objetivo

Verificar que el MVP de Jobsy implemente correctamente las funciones
mínimas requeridas para la administración local de trabajos y que la
versión presentada sea reproducible.

## 2. Alcance

Las pruebas del primer avance contemplan:

- Envío y creación de trabajos.
- Generación de identificadores únicos.
- Ejecución de trabajos como procesos separados.
- Consulta del estado de los trabajos.
- Listado de trabajos.
- Solicitud de cancelación.
- Obtención del código de salida.
- Manejo de comandos inválidos sin provocar la terminación del servicio.

También se verificarán, cuando corresponda:

- Validación de comandos.
- Captura de stdout.
- Captura de stderr.
- Transiciones de estado.
- Registro de tiempos de ejecución.

## 3. Fuera de alcance

Para este avance no se consideran:

- Operación remota.
- Pruebas de carga a gran escala.
- Persistencia entre reinicios.
- Seguridad avanzada.
- Rendimiento a gran escala.

## 4. Componentes bajo prueba

Actualmente se consideran:

- Modelo de trabajo (`Job`).
- Administrador de trabajos (`JobManager`).
- Validación de comandos.
- Ejecutor de procesos.
- Cliente y servicio, conforme sean integrados.
- Mecanismo de cancelación, conforme sea integrado.

## 5. Tipos de prueba

Se utilizarán principalmente:

- Pruebas funcionales.
- Pruebas negativas.
- Pruebas de integración.
- Pruebas de flujo de extremo a extremo.

## 6. Ambiente

El MVP está orientado a un entorno Linux.

El ambiente específico utilizado durante la ejecución de las pruebas es WSL2.

## 7. Criterios de entrada

Para comenzar la ejecución de pruebas se requiere:

- Código del alcance disponible.
- Dependencias instaladas.
- Instrucciones suficientes para ejecutar el sistema.
- Funcionalidades correspondientes integradas o disponibles en la rama
  bajo prueba.

## 8. Criterios de salida

El avance podrá considerarse verificado cuando:

- Las funciones mínimas del MVP tengan al menos un caso de prueba asociado.
- Las pruebas críticas hayan sido ejecutadas.
- Los resultados estén documentados.
- Los defectos conocidos estén registrados.
- Exista evidencia reproducible del flujo principal.

## 9. Riesgos y limitaciones

Esta sección se actualizará conforme se revise e integre la implementación.

## 10. Evidencias

Las evidencias de ejecución se almacenarán en:

`docs/qa/evidence/`
