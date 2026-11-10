# modulo order
''' Contrato abstracto (ABC) del repositorio de pedidos. '''
from abc import ABC, abstractmethod
from typing import Optional, List

from src.modules.order.domain.models import Pedido


class IOrderRepository(ABC):

    @abstractmethod
    def obtener_por_id(self, pedido_id: int) -> Optional[Pedido]:
        pass

    @abstractmethod
    def listar_todos(
        self, estado: Optional[str] = None, usuario_id: Optional[int] = None, skip: int = 0, limit: int = 50
    ) -> List[Pedido]:
        pass

    @abstractmethod
    def listar_por_repartidor(self, repartidor_id: int, skip: int = 0, limit: int = 50) -> List[Pedido]:
        pass

    @abstractmethod
    def guardar(self, pedido: Pedido) -> Pedido:
        pass
