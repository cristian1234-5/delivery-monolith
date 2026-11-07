# modulo payment
''' Contrato abstracto (ABC) del repositorio de pagos. '''
from abc import ABC, abstractmethod
from typing import Optional, List

from src.modules.payment.domain.models import Pago


class IPaymentRepository(ABC):

    @abstractmethod
    def obtener_por_id(self, pago_id: int) -> Optional[Pago]:
        pass

    @abstractmethod
    def obtener_por_pedido(self, pedido_id: int) -> Optional[Pago]:
        pass

    @abstractmethod
    def listar_todos(self) -> List[Pago]:
        pass

    @abstractmethod
    def guardar(self, pago: Pago) -> Pago:
        pass
