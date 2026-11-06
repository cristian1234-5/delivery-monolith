'''
from fastapi import FastAPI
from src.core.database import Base, engine

# Importar los routers de cada módulo del dominio
from src.modules.auth.router import router as auth_router
from src.modules.order.router import router as order_router
from src.modules.restaurant.router import router as restaurant_router
from src.modules.payment.router import router as payment_router
from src.modules.tracking.router import router as tracking_router

# Crear tablas en la base de datos única
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Delivery Platform - Monolito Modular (Fase 1)",
    description="Arquitectura Monolítica basada en DDD para sistema de Delivery",
    version="1.0.0"
)

# Registrar rutas de cada módulo aislados lógicamente
app.include_router(auth_router, prefix="/api/v1/auth", tags=["AuthModule"])
app.include_router(restaurant_router, prefix="/api/v1/restaurants", tags=["RestaurantModule"])
app.include_router(order_router, prefix="/api/v1/orders", tags=["OrderModule"])
app.include_router(payment_router, prefix="/api/v1/payments", tags=["PaymentModule"])
app.include_router(tracking_router, prefix="/api/v1/tracking", tags=["TrackingModule"])

@app.get("/")
def root():
    return {"status": "OK", "message": "Servidor Monolítico Modular de Delivery activo"} '''

'''
from fastapi import FastAPI
from src.core.database import engine, Base

# Importar los modelos de TODOS los módulos para que SQLAlchemy los registre en los metadatos
import src.modules.auth.models
import src.modules.restaurant.models
import src.modules.order.models
import src.modules.payment.models
import src.modules.tracking.models

# Creación automática de las tablas físicas en la base de datos PostgreSQL
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Delivery Platform - Monolito Modular",
    description="Arquitectura modular con FastAPI y SQLAlchemy organizada por dominios (DDD)",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {
        "message": "Servidor del monolito modular de delivery funcionando correctamente",
        "modulos_activos": ["auth", "restaurant", "order", "payment", "tracking"]
    }
'''




from fastapi import FastAPI
from src.core.database import Base, engine

# Importar los modelos de todos los módulos
import src.modules.auth.models
import src.modules.restaurant.models
import src.modules.order.models
import src.modules.payment.models
import src.modules.tracking.models

# Importar los routers de cada módulo
from src.modules.auth.router import router as auth_router
from src.modules.order.router import router as order_router
from src.modules.restaurant.router import router as restaurant_router
from src.modules.payment.router import router as payment_router
from src.modules.tracking.router import router as tracking_router

# Crear las tablas en PostgreSQL
Base.metadata.create_all(bind=engine)

# Crear la aplicación FastAPI
app = FastAPI(
    title="Delivery Platform - Monolito Modular",
    description="Arquitectura modular con FastAPI y SQLAlchemy organizada por dominios (DDD)",
    version="1.0.0"
)

# Registrar las rutas de cada módulo
app.include_router(auth_router, prefix="/api/v1/auth", tags=["AuthModule"])
app.include_router(restaurant_router, prefix="/api/v1/restaurants", tags=["RestaurantModule"])
app.include_router(order_router, prefix="/api/v1/orders", tags=["OrderModule"])
app.include_router(payment_router, prefix="/api/v1/payments", tags=["PaymentModule"])
app.include_router(tracking_router, prefix="/api/v1/tracking", tags=["TrackingModule"])

# Ruta principal
@app.get("/")
def read_root():
    return {
        "message": "Servidor del monolito modular de delivery funcionando correctamente",
        "modulos_activos": [
            "auth",
            "restaurant",
            "order",
            "payment",
            "tracking"
        ]
    }
