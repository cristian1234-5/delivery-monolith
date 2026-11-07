from fastapi import FastAPI

from src.core.database import Base, engine

# Importar los modelos ORM (capa infraestructura) de TODOS los módulos
# para que SQLAlchemy los registre en los metadatos y resuelva las relaciones.
import src.modules.auth.infrastructure.models_db  # noqa: F401
import src.modules.restaurant.infraestructure.models_db  # noqa: F401
import src.modules.tracking.infraestructure.models_db  # noqa: F401
import src.modules.order.infraestructure.models_db  # noqa: F401
import src.modules.payment.infraestructure.models_db  # noqa: F401

# Importar los routers (capa presentación) de cada módulo
from src.modules.auth.presentation.router import router as auth_router
from src.modules.restaurant.presentation.router import router as restaurant_router
from src.modules.order.presentation.router import router as order_router
from src.modules.payment.presentation.router import router as payment_router
from src.modules.tracking.presentation.router import router as tracking_router

# Crea solo las tablas que falten (init.sql ya crea las principales)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Delivery Platform - Monolito Modular",
    description="Arquitectura modular con FastAPI y SQLAlchemy organizada por dominios (DDD)",
    version="1.0.0",
)

# Registrar las rutas de cada módulo
app.include_router(auth_router, prefix="/api/v1/auth", tags=["AuthModule"])
app.include_router(restaurant_router, prefix="/api/v1/restaurants", tags=["RestaurantModule"])
app.include_router(order_router, prefix="/api/v1/orders", tags=["OrderModule"])
app.include_router(payment_router, prefix="/api/v1/payments", tags=["PaymentModule"])
app.include_router(tracking_router, prefix="/api/v1/tracking", tags=["TrackingModule"])


@app.get("/")
def read_root():
    return {
        "message": "Servidor del monolito modular de delivery funcionando correctamente",
        "modulos_activos": ["auth", "restaurant", "order", "payment", "tracking"],
    }
