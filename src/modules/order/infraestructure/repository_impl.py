# modulo order
''' Implementación concreta del repositorio con SQLAlchemy.
Traduce PedidoModel/DetallePedidoModel (BD) <-> Pedido/DetallePedido (dominio).
'''
from typing import Optional, List
from sqlalchemy.orm import Session

from src.modules.order.domain.repositories import IOrderRepository
from src.modules.order.domain.models import Pedido, DetallePedido
from src.modules.order.infraestructure.models_db import PedidoModel, DetallePedidoModel


class OrderRepositorySqlAlchemy(IOrderRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_domain(self, model: PedidoModel) -> Optional[Pedido]:
        if not model:
            return None
        return Pedido(
            pedido_id=model.pedido_id,
            fecha_hora=model.fecha_hora,
            sum_total=model.sum_total,
            notas_cliente=model.notas_cliente,
            estado=model.estado,
            tiempo_estimado_min=model.tiempo_estimado_min,
            permite_cancelacion=model.permite_cancelacion,
            usuario_id=model.usuario_id,
            restaurant_id=model.restaurant_id,
            repartidor_id=model.repartidor_id,
            detalles=[
                DetallePedido(
                    detalle_pedido_id=d.detalle_pedido_id,
                    producto_id=d.producto_id,
                    cantidad=d.cantidad,
                    precio_unitario=d.precio_unitario,
                )
                for d in model.detalles
            ],
        )

    def obtener_por_id(self, pedido_id: int) -> Optional[Pedido]:
        model = self.db.query(PedidoModel).filter(PedidoModel.pedido_id == pedido_id).first()
        return self._to_domain(model)

    def listar_todos(self, estado: Optional[str] = None) -> List[Pedido]:
        query = self.db.query(PedidoModel)
        if estado:
            query = query.filter(PedidoModel.estado == estado)
        return [self._to_domain(m) for m in query.order_by(PedidoModel.pedido_id.desc()).all()]

    def listar_por_usuario(self, usuario_id: int) -> List[Pedido]:
        query = self.db.query(PedidoModel).filter(PedidoModel.usuario_id == usuario_id)
        return [self._to_domain(m) for m in query.order_by(PedidoModel.pedido_id.desc()).all()]

    def guardar(self, pedido: Pedido) -> Pedido:
        model = None
        if pedido.pedido_id:
            model = self.db.query(PedidoModel).filter(PedidoModel.pedido_id == pedido.pedido_id).first()

        if not model:
            # Pedido nuevo: se crea la cabecera junto con todos sus detalles
            model = PedidoModel(
                usuario_id=pedido.usuario_id,
                restaurant_id=pedido.restaurant_id,
                detalles=[
                    DetallePedidoModel(
                        producto_id=d.producto_id,
                        cantidad=d.cantidad,
                        precio_unitario=d.precio_unitario,
                        subtotal=d.subtotal,
                    )
                    for d in pedido.detalles
                ],
            )
            self.db.add(model)

        # Campos de la cabecera que pueden cambiar durante el ciclo de vida
        model.sum_total = pedido.sum_total
        model.notas_cliente = pedido.notas_cliente
        model.estado = pedido.estado
        model.tiempo_estimado_min = pedido.tiempo_estimado_min
        model.permite_cancelacion = pedido.permite_cancelacion
        model.repartidor_id = pedido.repartidor_id

        self.db.commit()
        self.db.refresh(model)
        return self._to_domain(model)
