# main.py
from fastapi import FastAPI, Depends, HTTPException
import asyncio

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Float, select

# -------------------------------------------------------------------
# Configuración FastAPI
# -------------------------------------------------------------------
app = FastAPI(title="Monolito Marketplace")

# -------------------------------------------------------------------
# Base de datos (COMPARTIDA por todo el sistema)
# -------------------------------------------------------------------
DATABASE_URL = "mysql+aiomysql://root:angelito++@localhost/monolito"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with SessionLocal() as session:
        yield session

# -------------------------------------------------------------------
# Modelos ORM
# -------------------------------------------------------------------
class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    price = Column(Float)
    stock = Column(Integer)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer)
    quantity = Column(Integer)
    total = Column(Float)
    
# -------------------------------------------------------------------
# Catálogo
# -------------------------------------------------------------------
@app.get("/products")
async def list_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    products = result.scalars().all()
    return products

# -------------------------------------------------------------------
# Pedidos + pagos (TODO JUNTO, A PROPÓSITO)
# -------------------------------------------------------------------
@app.post("/orders", status_code=201)
async def create_order(
    product_id: int,
    quantity: int,
    db: AsyncSession = Depends(get_db),
):
    # PASO 1: leer producto → abre transacción y lock de fila
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if product.stock < quantity:
        raise HTTPException(status_code=400, detail="Stock insuficiente")

    # PASO 2: pago lento (lock SIGUE ACTIVO)
    await asyncio.sleep(5)

    # PASO 3: actualizar stock
    product.stock -= quantity

    order = Order(
        product_id=product.id,
        quantity=quantity,
        total=product.price * quantity,
    )

    db.add(order)
    await db.commit()

    return {"status": "ok", "order_total": order.total}

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)