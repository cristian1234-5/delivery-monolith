# modulo order
''' Adaptadores externos del módulo order.
========================================
En un monolito modular, un módulo NO toca las tablas de otro directamente:
lo consulta a través de un adaptador. Si mañana "restaurant" se separa en un
microservicio, solo se reescribe este archivo (por ejemplo, con llamadas HTTP)
y el dominio y los servicios de order no cambian.

Todos los adaptadores comparten la misma sesión, así que sus cambios entran
en la misma transacción que el pedido.
'''
import uuid
from sqlalchemy.orm import Session

from src.modules.auth.infrastructure.repository_impl import AuthRepositorySqlAlchemy
from src.modules.restaurant.infraestructure.repository_impl import RestaurantRepositorySqlAlchemy
from src.modules.tracking.infraestructure.repository_impl import TrackingRepositorySqlAlchemy
from src.modules.payment.infraestructure.repository_impl import PaymentRepositorySqlAlchemy


class UsuarioAdapter:
    """Consulta el módulo auth (usuarios y direcciones)."""

    def __init__(self, db: Session):
        self._repo = AuthRepositorySqlAlchemy(db)

    def esta_activo(self, usuario_id: int) -> bool:
        usuario = self._repo.obtener_por_id(usuario_id)
        return usuario is not None and usuario.esta_activo()

    def direccion_pertenece(self, direccion_id: int, usuario_id: int) -> bool:
        direccion = self._repo.obtener_direccion(direccion_id)
        return direccion is not None and direccion.usuario_id == usuario_id


class CatalogoAdapter:
    """Consulta el módulo restaurant (restaurantes y productos)."""

    def __init__(self, db: Session):
        self._repo = RestaurantRepositorySqlAlchemy(db)

    def obtener_restaurante(self, restaurant_id: int):
        return self._repo.obtener_por_id(restaurant_id)

    def obtener_producto(self, producto_id: int):
        return self._repo.obtener_producto(producto_id)


class RepartidorAdapter:
    """Consulta y actualiza la disponibilidad de repartidores en el módulo tracking."""

    def __init__(self, db: Session):
        self._repo = TrackingRepositorySqlAlchemy(db)

    def obtener_repartidor(self, repartidor_id: int):
        return self._repo.obtener_repartidor(repartidor_id)

    def obtener_por_usuario(self, usuario_id: int):
        return self._repo.obtener_por_usuario(usuario_id)

    def marcar_disponibilidad(self, repartidor_id: int, disponible: bool) -> None:
        repartidor = self._repo.obtener_repartidor(repartidor_id)
        if repartidor:
            repartidor.marcar_disponible() if disponible else repartidor.marcar_ocupado()
            self._repo.guardar_repartidor(repartidor)


class PagoAdapter:
    """Actualiza el módulo payment cuando el pedido se entrega."""

    def __init__(self, db: Session):
        self._repo = PaymentRepositorySqlAlchemy(db)

    def confirmar_efectivo_pendiente(self, pedido_id: int) -> None:
        """Al entregar, el repartidor cobró en efectivo: el pago pasa a Completado."""
        pago = self._repo.obtener_por_pedido(pedido_id)
        if pago and pago.es_contra_entrega() and pago.estado_pago == "Pendiente":
            pago.completar(f"EFE-{uuid.uuid4().hex[:12].upper()}")
            self._repo.guardar(pago)
