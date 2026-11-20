# modulo restaurant
''' DTOs de la capa de aplicación.
Los DTOs HTTP (entrada/salida) se definen en presentation/schemas.py y se reutilizan aquí.
'''
from src.modules.restaurant.presentation.schemas import (
    RestauranteCreate,
    RestauranteEstadoUpdate,
    RestauranteResponse,
    ProductoCreate,
    ProductoResponse,
)

__all__ = [
    "RestauranteCreate",
    "RestauranteEstadoUpdate",
    "RestauranteResponse",
    "ProductoCreate",
    "ProductoResponse",
]
