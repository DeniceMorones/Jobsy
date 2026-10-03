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

## 🎭 Asignación de roles:
* **Arquitectura:** Benjamin Lopez Fletes
* **Project Management & Backend:** Jocelyn Naomi Ibarra Bravo
* **Backend Development:** Denice Estefania Rico Morones
* **QA y Certificación:** Alexia Gomez Rubio

## 🛠️ Arquitectura y componentes implementados:
El proyecto está organizado de forma modular dentro del directorio src/

* **src/client/cli.py:** Interfaz de línea de comandos para parsear argumentos y formatear la salida en terminal.

* **src/daemon/executor.py:** Motor de ejecución asíncrona mediante subprocess.Popen e hilos.

* **src/daemon/job_manager.py:** Gestor del ciclo de vida de los trabajos, asignación de UUIDs y control de estados.

* **src/daemon/job.py:** Modelo de datos, estados (QUEUED, RUNNING, SUCCEEDED, FAILED, CANCELED) y metadatos.

* **src/daemon/server.py:** Guardián del servicio encargado del apagado seguro; por lo pronto su conexión solo esta en job_manager.py y sienta las bases para el avance 2.

* **src/protocol/validation.py:** Módulo para validación y sanitización de comandos.

## ⚙️ Construcción y ejecución:
**Requisitos previos**
*Linux o WSL
*Python 3.10 o superior

**1. Clonar repositorio**
git clone <URL_DEL_REPOSITORIO>
cd Jobsy

**2. Iniciar servidor**
Abre una terminal en WSL y levanta el servicio en segundo plano:
**python3 -m src.daemon.server**

**3. Interactuar desde CLI**
Abre una segunda terminal en WSL para enviar comandos:

* **Crear y ejecutar un trabajo:** python3 -m src.client.cli run -- sleep 20

* **Consultar la lista y persistencia de trabajos:** python3 -m src.client.cli list

* **Ver el estado detallado de un trabajo:** python3 -m src.client.cli status <UUID_DEL_TRABAJO>

* **Solicitar la cancelación de un trabajo activo:** python3 -m src.client.cli cancel <UUID_DEL_TRABAJO>

## 🔢 Códigos de Salida
El cliente CLI y las funciones del gestor retornan los siguientes códigos de estado para indicar el resultado del procesamiento:
* **0**: Ejecución exitosa
* **1**: Error de validación
* **2**: Error de sintaxis

## 📊 Estado del proyecto:
Estado: Avance 1 completado
Próximo hito: Avance 2