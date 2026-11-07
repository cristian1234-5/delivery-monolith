# modulo restaurant
''' Casos de uso del módulo restaurant. '''
from typing import List
from sqlalchemy.orm import Session

from src.modules.restaurant.infraestructure.repository_impl import RestaurantRepositorySqlAlchemy
from src.modules.restaurant.domain.models import Restaurante, Producto
from src.modules.restaurant.domain.exceptions import (
    RestauranteNoEncontradoException,
    ProductoNoEncontradoException,
)
from src.modules.restaurant.presentation.schemas import RestauranteCreate, ProductoCreate


class RestaurantService:
    def __init__(self, db: Session):
        self.repository = RestaurantRepositorySqlAlchemy(db)

    # ============ Restaurantes ============
    def crear_restaurante(self, data: RestauranteCreate) -> Restaurante:
        # La entidad de dominio valida sus propias reglas al instanciarse
        restaurante = Restaurante(**data.model_dump())
        return self.repository.guardar(restaurante)

    def obtener_restaurante(self, restaurant_id: int) -> Restaurante:
        restaurante = self.repository.obtener_por_id(restaurant_id)
        if not restaurante:
            raise RestauranteNoEncontradoException(f"No existe el restaurante con id {restaurant_id}.")
        return restaurante

    def listar_restaurantes(self, solo_abiertos: bool = False) -> List[Restaurante]:
        return self.repository.listar_todos(solo_abiertos)

    def actualizar_restaurante(self, restaurant_id: int, data: RestauranteCreate) -> Restaurante:
        self.obtener_restaurante(restaurant_id)  # valida que exista
        restaurante = Restaurante(restaurant_id=restaurant_id, **data.model_dump())
        return self.repository.guardar(restaurante)

    def cambiar_estado(self, restaurant_id: int, estado: str) -> Restaurante:
        restaurante = self.obtener_restaurante(restaurant_id)
        restaurante.abrir() if estado == "Abierto" else restaurante.cerrar()
        return self.repository.guardar(restaurante)

    def eliminar_restaurante(self, restaurant_id: int) -> None:
        self.obtener_restaurante(restaurant_id)
        self.repository.eliminar(restaurant_id)

    # ============ Productos (menú) ============
    def agregar_producto(self, restaurant_id: int, data: ProductoCreate) -> Producto:
        self.obtener_restaurante(restaurant_id)
        producto = Producto(restaurant_id=restaurant_id, **data.model_dump())
        return self.repository.guardar_producto(producto)

    def listar_productos(self, restaurant_id: int, solo_disponibles: bool = False) -> List[Producto]:
        self.obtener_restaurante(restaurant_id)
        return self.repository.listar_productos(restaurant_id, solo_disponibles)

    def obtener_producto(self, producto_id: int) -> Producto:
        producto = self.repository.obtener_producto(producto_id)
        if not producto:
            raise ProductoNoEncontradoException(f"No existe el producto con id {producto_id}.")
        return producto

    def actualizar_producto(self, producto_id: int, data: ProductoCreate) -> Producto:
        actual = self.obtener_producto(producto_id)
        producto = Producto(
            producto_id=producto_id, restaurant_id=actual.restaurant_id, **data.model_dump()
        )
        return self.repository.guardar_producto(producto)

    def eliminar_producto(self, producto_id: int) -> None:
        self.obtener_producto(producto_id)
        self.repository.eliminar_producto(producto_id)
