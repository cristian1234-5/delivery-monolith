# modulo restaurant
''' Contrato abstracto (ABC) del repositorio de restaurantes y productos. '''
from abc import ABC, abstractmethod
from typing import Optional, List

from src.modules.restaurant.domain.models import Restaurante, Producto


class IRestaurantRepository(ABC):

    # ----- Restaurantes -----
    @abstractmethod
    def obtener_por_id(self, restaurant_id: int) -> Optional[Restaurante]:
        pass

    @abstractmethod
    def listar_todos(self, solo_abiertos: bool = False, skip: int = 0, limit: int = 50) -> List[Restaurante]:
        pass

    @abstractmethod
    def guardar(self, restaurante: Restaurante) -> Restaurante:
        pass

    @abstractmethod
    def eliminar(self, restaurant_id: int) -> None:
        pass

    # ----- Productos -----
    @abstractmethod
    def obtener_producto(self, producto_id: int) -> Optional[Producto]:
        pass

    @abstractmethod
    def listar_productos(
        self, restaurant_id: int, solo_disponibles: bool = False, skip: int = 0, limit: int = 50
    ) -> List[Producto]:
        pass

    @abstractmethod
    def guardar_producto(self, producto: Producto) -> Producto:
        pass

    @abstractmethod
    def eliminar_producto(self, producto_id: int) -> None:
        pass
