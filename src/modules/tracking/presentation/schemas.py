# modulo tracking
''' DTOs de Pydantic para validar entradas y salidas HTTP. '''
from datetime import date, time
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


# ============ Repartidor ============
class RepartidorCreate(BaseModel):
    tipo_vehiculo: Literal["Bicicleta", "Moto", "Taxi"]
    placa: Optional[str] = Field(default=None, max_length=20)
    usuario_id: Optional[int] = None
    disponible: bool = True


class DisponibilidadUpdate(BaseModel):
    disponible: bool


class RepartidorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    repartidor_id: int
    tipo_vehiculo: str
    placa: Optional[str] = None
    disponible: bool
    usuario_id: Optional[int] = None


# ============ Ubicación ============
class UbicacionCreate(BaseModel):
    latitud: float = Field(ge=-90, le=90)
    longitud: float = Field(ge=-180, le=180)


class UbicacionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ubicacion_tracking_id: int
    repartidor_id: int
    latitud: float
    longitud: float
    fecha: date
    hora: time


# ============ Seguimiento de pedido ============
class SeguimientoPedidoResponse(BaseModel):
    pedido_id: int
    estado_pedido: str
    repartidor: Optional[RepartidorResponse] = None
    ubicacion_actual: Optional[UbicacionResponse] = None
