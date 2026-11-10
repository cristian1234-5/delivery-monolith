# modulo order
''' Entidades puras de dominio
========================================
Pedido (raíz del agregado) y DetallePedido, con las reglas del ciclo de vida del pedido.
'''
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from src.modules.order.domain.exceptions import (
    PedidoInvalidoException,
    TransicionEstadoInvalidaException,
    CancelacionNoPermitidaException,
)

ESTADOS_PEDIDO = ("Pendiente", "En_Preparacion", "En_Camino", "Entregado", "Cancelado")

# Flujo permitido del pedido: estado actual -> estados siguientes válidos
TRANSICIONES = {
    "Pendiente": ("En_Preparacion", "Cancelado"),
    "En_Preparacion": ("En_Camino",),
    "En_Camino": ("Entregado",),
    "Entregado": (),
    "Cancelado": (),
}


@dataclass
class DetallePedido:
    producto_id: int
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal = Decimal("0.00")
    detalle_pedido_id: Optional[int] = None

    def __post_init__(self):
        if self.cantidad <= 0:
            raise PedidoInvalidoException("La cantidad de cada producto debe ser mayor a 0.")
        self.precio_unitario = Decimal(str(self.precio_unitario))
        self.subtotal = (self.precio_unitario * self.cantidad).quantize(Decimal("0.01"))


@dataclass
class Pedido:
    usuario_id: int
    restaurant_id: int
    detalles: List[DetallePedido] = field(default_factory=list)
    notas_cliente: Optional[str] = None
    estado: str = "Pendiente"
    tiempo_estimado_min: int = 30
    permite_cancelacion: bool = True
    repartidor_id: Optional[int] = None
    direccion_id: Optional[int] = None
    sum_total: Decimal = Decimal("0.00")
    fecha_hora: Optional[datetime] = None
    pedido_id: Optional[int] = None

    # ---------- Reglas de creación ----------
    def validar_nuevo(self):
        if not self.detalles:
            raise PedidoInvalidoException("El pedido debe tener al menos un producto.")
        if not self.direccion_id:
            raise PedidoInvalidoException("El pedido debe tener una dirección de entrega.")
        self.calcular_total()

    def calcular_total(self) -> Decimal:
        self.sum_total = sum((d.subtotal for d in self.detalles), Decimal("0.00"))
        return self.sum_total

    # ---------- Ciclo de vida ----------
    def cambiar_estado(self, nuevo_estado: str):
        if nuevo_estado not in ESTADOS_PEDIDO:
            raise TransicionEstadoInvalidaException(f"Estado inválido. Use: {', '.join(ESTADOS_PEDIDO)}.")
        if nuevo_estado == "Cancelado":
            return self.cancelar()
        if nuevo_estado not in TRANSICIONES[self.estado]:
            raise TransicionEstadoInvalidaException(
                f"No se puede pasar de '{self.estado}' a '{nuevo_estado}'."
            )
        if nuevo_estado == "En_Camino" and not self.repartidor_id:
            raise TransicionEstadoInvalidaException("Asigne un repartidor antes de enviar el pedido.")

        self.estado = nuevo_estado
        # Una vez que el restaurante empieza a preparar, ya no se puede cancelar
        if nuevo_estado != "Pendiente":
            self.permite_cancelacion = False

    def cancelar(self):
        if not self.permite_cancelacion or "Cancelado" not in TRANSICIONES[self.estado]:
            raise CancelacionNoPermitidaException(
                f"El pedido en estado '{self.estado}' ya no puede cancelarse."
            )
        self.estado = "Cancelado"
        self.permite_cancelacion = False

    def asignar_repartidor(self, repartidor_id: int):
        if self.estado in ("Entregado", "Cancelado", "En_Camino"):
            raise PedidoInvalidoException(
                f"No se puede asignar repartidor a un pedido en estado '{self.estado}'."
            )
        self.repartidor_id = repartidor_id

    def esta_finalizado(self) -> bool:
        return self.estado in ("Entregado", "Cancelado")
