# modulo payment
''' Adaptadores externos del módulo payment.
========================================
- PedidoAdapter: consulta el módulo order (total, estado y dueño del pedido).
- RepartidorAdapter: consulta el módulo tracking (para permisos del repartidor).
- PasarelaPagoSimulada: simula una pasarela real (Stripe, PayPal, QR bancario...).
  Para conectar una pasarela real solo se reemplaza esta clase.
'''
import uuid
from decimal import Decimal
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from src.modules.order.infraestructure.repository_impl import OrderRepositorySqlAlchemy
from src.modules.tracking.infraestructure.repository_impl import TrackingRepositorySqlAlchemy


class PedidoAdapter:
    """Consulta el módulo order."""

    def __init__(self, db: Session):
        self._repo = OrderRepositorySqlAlchemy(db)

    def obtener_pedido(self, pedido_id: int):
        return self._repo.obtener_por_id(pedido_id)


class RepartidorAdapter:
    """Consulta el módulo tracking."""

    def __init__(self, db: Session):
        self._repo = TrackingRepositorySqlAlchemy(db)

    def repartidor_id_de_usuario(self, usuario_id: int) -> Optional[int]:
        repartidor = self._repo.obtener_por_usuario(usuario_id)
        return repartidor.repartidor_id if repartidor else None


class PasarelaPagoSimulada:
    """Simula el cobro con tarjeta o QR. Devuelve (aprobado, transaccion_id)."""

    def cobrar(self, monto: Decimal, metodo_pago: str) -> Tuple[bool, str]:
        prefijo = "TXN" if metodo_pago == "Tarjeta" else "QR"
        transaccion_id = f"{prefijo}-{uuid.uuid4().hex[:12].upper()}"
        aprobado = monto > 0  # Simulación: se aprueba todo cobro válido
        return aprobado, transaccion_id

    def generar_comprobante_efectivo(self) -> str:
        return f"EFE-{uuid.uuid4().hex[:12].upper()}"
