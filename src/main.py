from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from src.core.config import CORS_ORIGINS
from src.core.database import Base, engine, SessionLocal

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

from src.modules.auth.application.services import AuthService


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Crea solo las tablas que falten (init.sql ya crea las principales)
    Base.metadata.create_all(bind=engine)
    # Asegura catálogos (rol, estado) y un administrador inicial
    db = SessionLocal()
    try:
        AuthService(db).inicializar_sistema()
    finally:
        db.close()
    yield


app = FastAPI(
    title="Delivery Platform - Monolito Modular",
    description=(
        "Arquitectura modular con FastAPI y SQLAlchemy organizada por dominios (DDD).\n\n"
        "**Cómo autenticarse:** haga `POST /api/v1/auth/login`, copie el `access_token` "
        "y péguelo en el botón **Authorize**."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# CORS: permite que un frontend (React, Angular, etc.) consuma la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials="*" not in CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(_: Request, __: IntegrityError):
    """Errores de la BD (llaves foráneas, únicos) -> 409 con mensaje claro en vez de 500."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": (
                "No se puede completar la operación: el registro está relacionado con otros "
                "datos (por ejemplo, pedidos existentes) o repite un valor que debe ser único."
            )
        },
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
        "documentacion": "/docs",
    }
