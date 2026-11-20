# modulo payment
''' DTOs de Pydantic para validar entradas y salidas HTTP. '''
from datetime import date
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class PagoCreate(BaseModel):
    pedido_id: int
    monto: float = Field(gt=0)
    metodo_pago: Literal["Efectivo", "Tarjeta", "QR"]


class PagoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pago_id: int
    pedido_id: int
    monto: float
    metodo_pago: str
    estado_pago: str
    transaccion_id: Optional[str] = None
    fecha: date
