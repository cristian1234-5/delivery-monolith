# modulo payment
''' Adaptadores externos del módulo payment.
========================================
- PedidoAdapter: consulta el módulo order (total y estado del pedido).
- PasarelaPagoSimulada: simula una pasarela real (Stripe, PayPal, QR bancario...).
  Para conectar una pasarela real solo se reemplaza esta clase.
'''
import uuid
from decimal import Decimal
from typing import Tuple
from sqlalchemy.orm import Session

from src.modules.order.infraestructure.repository_impl import OrderRepositorySqlAlchemy


class PedidoAdapter:
    """Consulta el módulo order."""

    def __init__(self, db: Session):
        self._repo = OrderRepositorySqlAlchemy(db)

    def obtener_pedido(self, pedido_id: int):
        return self._repo.obtener_por_id(pedido_id)


class PasarelaPagoSimulada:
    """Simula el cobro con tarjeta o QR. Devuelve (aprobado, transaccion_id)."""

    def cobrar(self, monto: Decimal, metodo_pago: str) -> Tuple[bool, str]:
        prefijo = "TXN" if metodo_pago == "Tarjeta" else "QR"
        transaccion_id = f"{prefijo}-{uuid.uuid4().hex[:12].upper()}"
        aprobado = monto > 0  # Simulación: se aprueba todo cobro válido
        return aprobado, transaccion_id

    def generar_comprobante_efectivo(self) -> str:
        return f"EFE-{uuid.uuid4().hex[:12].upper()}"
