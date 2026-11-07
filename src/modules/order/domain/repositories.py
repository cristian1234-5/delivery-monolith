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
    def listar_todos(self, estado: Optional[str] = None) -> List[Pedido]:
        pass

    @abstractmethod
    def listar_por_usuario(self, usuario_id: int) -> List[Pedido]:
        pass

    @abstractmethod
    def guardar(self, pedido: Pedido) -> Pedido:
        pass
