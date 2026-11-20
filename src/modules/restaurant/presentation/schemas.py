# modulo restaurant
''' DTOs de Pydantic para validar entradas y salidas HTTP. '''
from datetime import time
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


# ============ Restaurante ============
class RestauranteCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=128)
    direccion: str = Field(min_length=1, max_length=255)
    contacto: Optional[str] = Field(default=None, max_length=50)
    horario_apertura: Optional[time] = None
    horario_cierre: Optional[time] = None
    estado: Literal["Abierto", "Cerrado"] = "Abierto"


class RestauranteEstadoUpdate(BaseModel):
    estado: Literal["Abierto", "Cerrado"]


class RestauranteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    restaurant_id: int
    nombre: str
    direccion: str
    contacto: Optional[str] = None
    horario_apertura: Optional[time] = None
    horario_cierre: Optional[time] = None
    estado: str


# ============ Producto ============
class ProductoCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=128)
    descripcion: Optional[str] = None
    precio: float = Field(ge=0)
    disponible: bool = True
    categoria: str = Field(min_length=1, max_length=64)


class ProductoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    producto_id: int
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    disponible: bool
    categoria: str
    restaurant_id: int
