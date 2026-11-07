# modulo order
''' DTOs de Pydantic para validar entradas y salidas HTTP. '''
from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

EstadoPedido = Literal["Pendiente", "En_Preparacion", "En_Camino", "Entregado", "Cancelado"]


class ItemPedidoCreate(BaseModel):
    producto_id: int
    cantidad: int = Field(gt=0)


class PedidoCreate(BaseModel):
    usuario_id: int
    restaurant_id: int
    items: List[ItemPedidoCreate] = Field(min_length=1)
    notas_cliente: Optional[str] = None


class PedidoEstadoUpdate(BaseModel):
    estado: EstadoPedido


class AsignarRepartidor(BaseModel):
    repartidor_id: int


class DetallePedidoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    detalle_pedido_id: Optional[int] = None
    producto_id: int
    cantidad: int
    precio_unitario: float
    subtotal: float


class PedidoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pedido_id: int
    fecha_hora: Optional[datetime] = None
    usuario_id: int
    restaurant_id: int
    repartidor_id: Optional[int] = None
    estado: str
    sum_total: float
    tiempo_estimado_min: int
    permite_cancelacion: bool
    notas_cliente: Optional[str] = None
    detalles: List[DetallePedidoResponse]
