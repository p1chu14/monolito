````markdown
# Market-Place-Inc — Monolito hacia Microservicios

Proyecto académico de Sistemas Distribuidos basado en el caso ficticio **Market-Place-Inc (MPI)**.

El objetivo del proyecto es construir un monolito intencionalmente acoplado utilizando FastAPI y MySQL para demostrar problemas reales de concurrencia, locks, agotamiento del pool de conexiones y acoplamiento mediante recursos compartidos.

---

# Objetivos del trabajo

Este TP busca demostrar:

- Cómo un monolito puede degradarse bajo alta concurrencia.
- Cómo una base de datos compartida genera acoplamiento invisible.
- Cómo los locks afectan endpoints aparentemente inocentes.
- Cómo se generan SPOFs (Single Points of Failure).
- Por qué una arquitectura monolítica termina necesitando microservicios.

---

# Arquitectura actual

Todo el sistema corre en:

- Un único proceso FastAPI
- Un único archivo `main.py`
- Una única base de datos MySQL
- Un único pool de conexiones

```text
                ┌────────────────────┐
                │      FastAPI       │
                │      main.py       │
                ├────────────────────┤
                │ GET /products      │
                │ POST /orders       │
                │ GET /health        │
                └─────────┬──────────┘
                          │
                          │ Shared DB
                          ▼
                ┌────────────────────┐
                │       MySQL        │
                │   Base compartida  │
                └────────────────────┘
````

---

# Tecnologías utilizadas

* Python 3
* FastAPI
* Uvicorn
* SQLAlchemy 2.0 Async
* aiomysql
* MySQL
* Pydantic
* Locust

---

# Instalación

## 1. Clonar el repositorio

```bash
git clone https://github.com/usuario/market-place-inc.git

cd market-place-inc
```

---

## 2. Crear entorno virtual

### Linux

```bash
python3 -m venv venv

source venv/bin/activate
```

### Windows PowerShell

```powershell
python -m venv venv

.\venv\Scripts\Activate.ps1
```

---

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

O manualmente:

```bash
pip install fastapi uvicorn[standard] sqlalchemy aiomysql pydantic locust
```

---

# Configuración de MySQL

Ingresar a MySQL:

```bash
mysql -u root -p
```

Crear la base:

```sql
CREATE DATABASE IF NOT EXISTS monolito CHARACTER SET utf8mb4;
```

---

# Ejecutar el proyecto

```bash
uvicorn main:app --reload --port 8000
```

---

# Swagger UI

Acceder a:

```text
http://localhost:8000/docs
```

---

# Endpoints

## GET /products

Obtiene el catálogo de productos.

### Características

* Endpoint rápido
* Solo lectura
* No realiza operaciones lentas
* No tiene errores propios

Sin embargo, termina degradándose por culpa de `/orders` debido a la base compartida.

---

## POST /orders

Crea pedidos y simula pagos lentos.

### Flujo interno

1. Lee stock del producto
2. Abre transacción SQL
3. Simula pago lento con `asyncio.sleep(3)`
4. Actualiza stock
5. Ejecuta commit

### Punto clave

Durante esos 3 segundos:

* FastAPI sigue funcionando
* El event loop NO se bloquea
* PERO MySQL mantiene locks activos

Eso genera:

* Esperas
* Contención
* Latencia cruzada
* Agotamiento del pool

---

## GET /health

Endpoint de health check.

No utiliza base de datos.

Siempre responde rápido incluso bajo carga.

---

# Restricciones intencionales

Este proyecto NO implementa todavía:

* Circuit Breaker
* Background Tasks
* Arquitectura en capas
* Microservicios
* Retries
* Timeouts robustos
* Pools separados
* Event-driven architecture

---

# Uso intencional de asyncio.sleep

El sistema utiliza:

```python
await asyncio.sleep(3)
```

y NO:

```python
time.sleep(3)
```

La diferencia es importante:

* `asyncio.sleep()` libera el event loop
* Pero la transacción SQL sigue abierta
* Y el lock persiste igualmente

El objetivo del TP es demostrar precisamente ese comportamiento.

---

# Pool de conexiones

Configuración utilizada:

```python
pool_size=5
max_overflow=10
```

Máximo total:

```text
15 conexiones
```

Con múltiples usuarios concurrentes:

* Cada `/orders` mantiene una conexión ocupada
* El pool se agota rápidamente
* Nuevos requests esperan o fallan

---

# Problemas observados

## 1. Locks prolongados

Cada pedido mantiene bloqueada la fila del producto.

---

## 2. Latencia cruzada

`GET /products` comienza a responder lento aunque no tenga errores propios.

---

## 3. Acoplamiento invisible

El verdadero acoplamiento ocurre mediante la base compartida.

---

## 4. Agotamiento del pool

Error típico observado:

```text
sqlalchemy.exc.TimeoutError:
QueuePool limit of size 5 overflow 10 reached
```

---

# Experimento de concurrencia

## Hot Sale manual

Abrir múltiples pestañas y ejecutar simultáneamente:

```http
POST /orders
```

Mientras tanto ejecutar:

```http
GET /products
```

---

# Resultado esperado

* `/orders` tarda aproximadamente 3 segundos
* Los pedidos se encolan
* `/products` empieza a degradarse
* Se observan locks y latencias crecientes

---

# Test de carga con Locust

## Ejecutar Locust

```bash
locust -f locustfile.py --host http://localhost:8000
```

O en modo headless:

```bash
locust -f locustfile.py --headless -u 50 -r 5 --host http://localhost:8000
```

---

# Escenario simulado

* 30% usuarios realizan compras
* 70% usuarios navegan el catálogo

Esto replica un escenario tipo Hot Sale.

---

# Qué observar

## `/health`

* Siempre rápido
* No depende de DB

---

## `/products`

* Comienza rápido
* Luego aumenta la latencia

---

## `/orders`

* Genera locks
* Consume conexiones
* Produce contención

---

# SPOFs identificados

## 1. Base de datos MySQL única

Todo el sistema depende de una sola instancia MySQL.

Si cae:

```text
Toda la plataforma queda offline
```

---

## 2. Proceso único FastAPI

Todo corre dentro de un único proceso Uvicorn.

Si falla:

```text
Todo el sistema cae
```

---

## 3. Proveedor de pagos

El pago es síncrono y bloqueante.

Si responde lento:

* Se acumulan conexiones abiertas
* Aparecen colas
* Se degrada todo el sistema

---

# Conclusiones

El proyecto demuestra que un sistema puede ser asincrónico y aun así no escalar correctamente.

Aunque FastAPI libera el event loop durante `asyncio.sleep(3)`, la transacción SQL permanece abierta y mantiene locks activos.

El verdadero problema del monolito no está en Python sino en:

* La base de datos compartida
* Las transacciones prolongadas
* Los locks
* El pool limitado
* Los recursos compartidos

Todo esto convierte al monolito en una arquitectura frágil bajo alta concurrencia y justifica la futura migración hacia microservicios desacoplados.

---

# Próxima etapa

La siguiente fase del proyecto consistirá en:

* Separar módulos en microservicios
* Aislar pools de conexiones
* Separar bases de datos
* Incorporar colas de mensajes
* Implementar Circuit Breaker
* Desacoplar pagos e inventario

---

# Estructura actual del proyecto

```text
market-place-inc/
│
├── main.py
├── locustfile.py
├── requirements.txt
├── README.md
└── screenshots/
```

---

# IA Log

## Prompt utilizado

```text
“Haceme un endpoint POST /orders que muestre el problema
del acoplamiento entre pagos e inventario en un monolito.
Todo en un archivo, sin separar módulos.”
```

---

## Resultado generado por IA

La IA inicialmente intentó:

* Separar routers
* Crear services/
* Agregar retries
* Agregar Circuit Breaker

---

## Correcciones realizadas

Se eliminó:

* Arquitectura por capas
* Manejo resiliente
* Separación modular

Porque el objetivo del TP es:

```text
Mostrar el problema, no resolverlo todavía
```
