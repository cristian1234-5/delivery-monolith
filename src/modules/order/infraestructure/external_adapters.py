# modulo order
''' Adaptadores externos del módulo order.
========================================
En un monolito modular, un módulo NO toca las tablas de otro directamente:
lo consulta a través de un adaptador. Si mañana "restaurant" se separa en un
microservicio, solo se reescribe este archivo (por ejemplo, con llamadas HTTP)
y el dominio y los servicios de order no cambian.
'''
from typing import Optional
from sqlalchemy.orm import Session

from src.modules.auth.infrastructure.repository_impl import AuthRepositorySqlAlchemy
from src.modules.restaurant.infraestructure.repository_impl import RestaurantRepositorySqlAlchemy
from src.modules.tracking.infraestructure.repository_impl import TrackingRepositorySqlAlchemy


class UsuarioAdapter:
    """Consulta el módulo auth."""

    def __init__(self, db: Session):
        self._repo = AuthRepositorySqlAlchemy(db)

    def existe_usuario(self, usuario_id: int) -> bool:
        return self._repo.obtener_por_id(usuario_id) is not None


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

    def marcar_disponibilidad(self, repartidor_id: int, disponible: bool) -> None:
        repartidor = self._repo.obtener_repartidor(repartidor_id)
        if repartidor:
            repartidor.disponible = disponible
            self._repo.guardar_repartidor(repartidor)
