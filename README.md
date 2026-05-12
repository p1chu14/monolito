# TP1: De Monolito a Microservicios - Market-Place-Inc

Este repositorio contiene la implementación del sistema monolítico inicial desarrollado para la cátedra de **Sistemas Distribuidos**.
El objetivo es demostrar las limitaciones de una arquitectura centralizada bajo condiciones de alta concurrencia y documentar el proceso
de diagnóstico previo a la migración a microservicios.

## Instrucciones de Ejecución

### 1. Requisitos previos
* Python 3.10 o superior.
* MySQL Server en ejecución.
* Un entorno virtual activo (`venv`).

### 2. Configuración de la Base de Datos
Crear una base de datos llamada `marketplace_db`. El sistema utiliza las tablas `products` y `orders`. 
Asegúrate de que las credenciales en `main.py` coincidan con tu instancia local.

```sql
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    stock INT,
    price DECIMAL(10,2)
);

CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    quantity INT,
    status VARCHAR(50)
);

-- Insertar datos de prueba
INSERT INTO products (name, stock, price) VALUES ('Smartphone', 50, 800.00), ('Laptop', 20, 1500.00);

sql```

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el servidor (Monolito)
uvicorn main:app --reload
