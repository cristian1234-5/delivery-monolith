# modulo restaurant
''' Implementación concreta del repositorio con SQLAlchemy.
Traduce RestauranteModel/ProductoModel (BD) <-> Restaurante/Producto (dominio).
Solo hace flush(): el commit lo decide el servicio (una transacción por caso de uso).
'''
from typing import Optional, List
from sqlalchemy.orm import Session

from src.modules.restaurant.domain.repositories import IRestaurantRepository
from src.modules.restaurant.domain.models import Restaurante, Producto
from src.modules.restaurant.infraestructure.models_db import RestauranteModel, ProductoModel


class RestaurantRepositorySqlAlchemy(IRestaurantRepository):
    def __init__(self, db: Session):
        self.db = db

    # ============ Mapeadores ============
    def _to_domain(self, model: RestauranteModel) -> Optional[Restaurante]:
        if not model:
            return None
        return Restaurante(
            restaurant_id=model.restaurant_id,
            nombre=model.nombre,
            direccion=model.direccion,
            contacto=model.contacto,
            horario_apertura=model.horario_apertura,
            horario_cierre=model.horario_cierre,
            estado=model.estado,
        )

    def _producto_to_domain(self, model: ProductoModel) -> Optional[Producto]:
        if not model:
            return None
        return Producto(
            producto_id=model.producto_id,
            nombre=model.nombre,
            descripcion=model.descripcion,
            precio=model.precio,
            disponible=model.disponible,
            categoria=model.categoria,
            restaurant_id=model.restaurant_id,
        )

    # ============ Restaurantes ============
    def obtener_por_id(self, restaurant_id: int) -> Optional[Restaurante]:
        model = self.db.query(RestauranteModel).filter(RestauranteModel.restaurant_id == restaurant_id).first()
        return self._to_domain(model)

    def listar_todos(self, solo_abiertos: bool = False, skip: int = 0, limit: int = 50) -> List[Restaurante]:
        query = self.db.query(RestauranteModel)
        if solo_abiertos:
            query = query.filter(RestauranteModel.estado == "Abierto")
        query = query.order_by(RestauranteModel.restaurant_id).offset(skip).limit(limit)
        return [self._to_domain(m) for m in query.all()]

    def guardar(self, restaurante: Restaurante) -> Restaurante:
        model = None
        if restaurante.restaurant_id:
            model = self.db.query(RestauranteModel).filter(
                RestauranteModel.restaurant_id == restaurante.restaurant_id
            ).first()
        if not model:
            model = RestauranteModel()
            self.db.add(model)

        model.nombre = restaurante.nombre
        model.direccion = restaurante.direccion
        model.contacto = restaurante.contacto
        model.horario_apertura = restaurante.horario_apertura
        model.horario_cierre = restaurante.horario_cierre
        model.estado = restaurante.estado

        self.db.flush()
        self.db.refresh(model)
        return self._to_domain(model)

    def eliminar(self, restaurant_id: int) -> None:
        model = self.db.query(RestauranteModel).filter(RestauranteModel.restaurant_id == restaurant_id).first()
        if model:
            self.db.delete(model)
            self.db.flush()

    # ============ Productos ============
    def obtener_producto(self, producto_id: int) -> Optional[Producto]:
        model = self.db.query(ProductoModel).filter(ProductoModel.producto_id == producto_id).first()
        return self._producto_to_domain(model)

    def listar_productos(
        self, restaurant_id: int, solo_disponibles: bool = False, skip: int = 0, limit: int = 50
    ) -> List[Producto]:
        query = self.db.query(ProductoModel).filter(ProductoModel.restaurant_id == restaurant_id)
        if solo_disponibles:
            query = query.filter(ProductoModel.disponible.is_(True))
        query = query.order_by(ProductoModel.producto_id).offset(skip).limit(limit)
        return [self._producto_to_domain(m) for m in query.all()]

    def guardar_producto(self, producto: Producto) -> Producto:
        model = None
        if producto.producto_id:
            model = self.db.query(ProductoModel).filter(ProductoModel.producto_id == producto.producto_id).first()
        if not model:
            model = ProductoModel()
            self.db.add(model)

        model.nombre = producto.nombre
        model.descripcion = producto.descripcion
        model.precio = producto.precio
        model.disponible = producto.disponible
        model.categoria = producto.categoria
        model.restaurant_id = producto.restaurant_id

        self.db.flush()
        self.db.refresh(model)
        return self._producto_to_domain(model)

    def eliminar_producto(self, producto_id: int) -> None:
        model = self.db.query(ProductoModel).filter(ProductoModel.producto_id == producto_id).first()
        if model:
            self.db.delete(model)
            self.db.flush()
