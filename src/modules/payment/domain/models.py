# modulo payment
''' Entidades puras de dominio
========================================
Pago de un pedido con sus reglas de negocio, sin depender de SQLAlchemy.
'''
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional

from src.modules.payment.domain.exceptions import PagoInvalidoException

METODOS_PAGO = ("Efectivo", "Tarjeta", "QR")
ESTADOS_PAGO = ("Pendiente", "Completado", "Fallido")


@dataclass
class Pago:
    pedido_id: int
    monto: Decimal
    metodo_pago: str
    estado_pago: str = "Pendiente"
    transaccion_id: Optional[str] = None
    fecha: date = field(default_factory=date.today)
    pago_id: Optional[int] = None

    def __post_init__(self):
        self.monto = Decimal(str(self.monto)).quantize(Decimal("0.01"))
        if self.monto <= 0:
            raise PagoInvalidoException("El monto del pago debe ser mayor a 0.")
        if self.metodo_pago not in METODOS_PAGO:
            raise PagoInvalidoException(f"Método de pago inválido. Use: {', '.join(METODOS_PAGO)}.")
        if self.estado_pago not in ESTADOS_PAGO:
            raise PagoInvalidoException(f"Estado de pago inválido. Use: {', '.join(ESTADOS_PAGO)}.")

    def completar(self, transaccion_id: str):
        if self.estado_pago == "Completado":
            raise PagoInvalidoException("El pago ya fue completado.")
        self.estado_pago = "Completado"
        self.transaccion_id = transaccion_id

    def marcar_fallido(self, transaccion_id: Optional[str] = None):
        self.estado_pago = "Fallido"
        self.transaccion_id = transaccion_id

    def es_contra_entrega(self) -> bool:
        return self.metodo_pago == "Efectivo"
