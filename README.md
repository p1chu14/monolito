# TP1 - Sistemas Distribuidos  
## Monolito hacia Microservicios (Market-Place-Inc)

### Descripción

Este proyecto implementa una versión simplificada de un sistema de e-commerce utilizando una arquitectura monolítica desarrollada con FastAPI y una base de datos MySQL compartida.

El objetivo principal es evidenciar los problemas de concurrencia, escalabilidad y acoplamiento que surgen en este tipo de arquitectura bajo condiciones de alta carga.

---

## Arquitectura

El sistema está compuesto por:

- FastAPI (aplicación monolítica en un solo archivo `main.py`)
- MySQL (base de datos compartida)
- SQLAlchemy + aiomysql (acceso async a datos)

### Endpoints

- `GET /products` → listado de productos  
- `POST /orders` → creación de pedidos (simula pago lento)  
- `GET /health` → estado del sistema  

---

## Instalación y ejecución

### 1. Instalar dependencias

```bash
pip install fastapi uvicorn sqlalchemy aiomysql pydantic locust
````
***

### 2. Crear base de datos

```sql
CREATE DATABASE monolito;
```

***

### 3. Ejecutar la aplicación

```bash
uvicorn main:app --reload --port 8000
```

***

### 4. Acceder a la API

    http://localhost:8000/docs

***

## Test de carga

Se utilizó **Locust** para simular un escenario de alta concurrencia:

### Configuración

*   50 usuarios concurrentes
*   Ramp-up: 5 usuarios/segundo
*   30% solicitudes → `/orders`
*   70% solicitudes → `/products`

Ejecutar:

```bash
locust -f locustfile.py --host http://localhost:8000
```

***

## Resultados observados

*   `/orders`:
    *   Tiempo promedio: \~7–10 segundos
    *   Picos: hasta 11 segundos

*   `/products`:
    *   Tiempo promedio: \~2.6 segundos
    *   Picos: hasta 6 segundos

*   \~10 solicitudes por segundo en total

***

## Conclusiones

El test de carga demuestra:

*   La base de datos es un cuello de botella
*   Los locks afectan a operaciones no relacionadas
*   Existe fuerte acoplamiento entre módulos
*   El sistema no escala correctamente

***

## Problemas detectados

### SPOFs

*   Base de datos única (MySQL)
*   Proceso único de FastAPI

### Cuellos de botella

*   Pool limitado de conexiones
*   Locks prolongados en la DB

***

## Conceptos clave evidenciados

*   Locks en base de datos
*   Contención de recursos
*   Acoplamiento por DB compartida
*   Falta de aislamiento entre módulos

***

## Estructura del proyecto

    .
    ├── main.py
    ├── locustfile.py
    ├── README.md


## IA Log – Proceso de desarrollo

---

### Interacción 1 – Generación del monolito

**Prompt:**
"Haceme un monolito en FastAPI con MySQL que tenga endpoints /products, /orders y /health. Todo en un solo archivo."

**Respuesta de la IA:**
Generó un proyecto completo en FastAPI, separando el código en módulos (routers, services, etc.) e incluyendo buenas prácticas como manejo de errores y separación por capas.

**Correcciones realizadas:**
Se unificó todo el código en un solo archivo (`main.py`) y se eliminaron capas adicionales.

**Aprendizaje:**
La IA tiende a aplicar buenas prácticas automáticamente, pero en este TP se necesita un diseño intencionalmente acoplado para evidenciar problemas.

---

### Interacción 2 – Endpoint `/orders`

**Prompt:**
"Implementá un endpoint POST /orders que simule un pago lento con asyncio.sleep(3) y produzca locks en la base de datos."

**Respuesta de la IA:**
Generó un endpoint funcional pero inicialmente utilizó `time.sleep()`.

**Correcciones realizadas:**
Se reemplazó `time.sleep()` por `asyncio.sleep()`.

**Aprendizaje:**
La diferencia entre `time.sleep` y `asyncio.sleep` es crítica: uno bloquea el thread, el otro no. El TP busca demostrar locks de DB, no bloqueo del servidor.

---

### Interacción 3 – Problema con test de carga

**Prompt:**
"Estoy ejecutando Locust y todas las requests fallan."

**Respuesta de la IA:**
Sugirió revisar el estado del stock en la base de datos.

**Correcciones realizadas:**
Se detectó que el producto tenía stock = 0, lo que generaba errores inmediatos. Se actualizó el stock a 100.

```sql
UPDATE products SET stock = 100 WHERE id = 1;
````

**Aprendizaje:**
Para observar problemas de concurrencia es necesario que las transacciones se ejecuten realmente. Si fallan antes, no se generan locks.

***

### Interacción 4 – Análisis del test de carga

**Prompt:**
"Analizá estos resultados de Locust."

**Respuesta de la IA:**
Interpretó correctamente:

*   aumento de latencia
*   cola de requests
*   impacto en `/products`

**Correcciones realizadas:**
Se ajustó el texto para adaptarlo a los resultados reales obtenidos.

**Aprendizaje:**
El comportamiento observado confirma que el problema no está en el código Python sino en la base de datos compartida.

***

### Interacción 5 – Diagnóstico arquitectónico

**Prompt:**
"Identificá SPOFs y cuellos de botella."

**Respuesta de la IA:**
Identificó:

*   DB como SPOF
*   proceso único como SPOF
*   locks y pool como cuellos de botella

**Correcciones realizadas:**
Se ajustó la redacción para alinear con los resultados experimentales.

**Aprendizaje:**
El sistema presenta acoplamiento estructural fuerte y falta de aislamiento, lo que limita la escalabilidad.

***

## Conclusión del IA Log

El uso de IA permitió acelerar el desarrollo y análisis del sistema, pero fue necesario ajustar múltiples aspectos manualmente para alinearse con los objetivos del TP.

Se evidenció que la IA tiende a:

*   aplicar buenas prácticas automáticamente
*   evitar escenarios problemáticos

Sin embargo, en este trabajo práctico el objetivo es precisamente exponer dichos problemas, por lo que fue necesario guiar explícitamente las respuestas.
