# modulo order
''' Casos de uso del módulo order. '''
from typing import List, Optional
from sqlalchemy.orm import Session

from src.modules.order.infraestructure.repository_impl import OrderRepositorySqlAlchemy
from src.modules.order.infraestructure.external_adapters import (
    UsuarioAdapter,
    CatalogoAdapter,
    RepartidorAdapter,
)
from src.modules.order.domain.models import Pedido, DetallePedido
from src.modules.order.domain.exceptions import (
    PedidoNoEncontradoException,
    UsuarioNoValidoException,
    RestauranteNoDisponibleException,
    ProductoNoValidoException,
    RepartidorNoDisponibleException,
)
from src.modules.order.presentation.schemas import PedidoCreate


class OrderService:
    def __init__(self, db: Session):
        self.repository = OrderRepositorySqlAlchemy(db)
        self.usuarios = UsuarioAdapter(db)
        self.catalogo = CatalogoAdapter(db)
        self.repartidores = RepartidorAdapter(db)

    def crear_pedido(self, data: PedidoCreate) -> Pedido:
        # 1. El cliente debe existir (módulo auth)
        if not self.usuarios.existe_usuario(data.usuario_id):
            raise UsuarioNoValidoException(f"No existe el usuario con id {data.usuario_id}.")

        # 2. El restaurante debe existir y estar abierto (módulo restaurant)
        restaurante = self.catalogo.obtener_restaurante(data.restaurant_id)
        if not restaurante:
            raise RestauranteNoDisponibleException(f"No existe el restaurante con id {data.restaurant_id}.")
        if not restaurante.esta_abierto():
            raise RestauranteNoDisponibleException(f"El restaurante '{restaurante.nombre}' está cerrado.")

        # 3. Cada producto debe pertenecer al restaurante y estar disponible.
        #    El precio SIEMPRE se toma del catálogo, nunca del cliente.
        detalles = []
        for item in data.items:
            producto = self.catalogo.obtener_producto(item.producto_id)
            if not producto or producto.restaurant_id != data.restaurant_id:
                raise ProductoNoValidoException(
                    f"El producto {item.producto_id} no pertenece al restaurante {data.restaurant_id}."
                )
            if not producto.puede_venderse():
                raise ProductoNoValidoException(f"El producto '{producto.nombre}' no está disponible.")
            detalles.append(
                DetallePedido(
                    producto_id=producto.producto_id,
                    cantidad=item.cantidad,
                    precio_unitario=producto.precio,
                )
            )

        # 4. Crear la entidad de dominio, calcular el total y guardar
        pedido = Pedido(
            usuario_id=data.usuario_id,
            restaurant_id=data.restaurant_id,
            detalles=detalles,
            notas_cliente=data.notas_cliente,
        )
        pedido.validar_nuevo()
        return self.repository.guardar(pedido)

    def obtener_pedido(self, pedido_id: int) -> Pedido:
        pedido = self.repository.obtener_por_id(pedido_id)
        if not pedido:
            raise PedidoNoEncontradoException(f"No existe el pedido con id {pedido_id}.")
        return pedido

    def listar_pedidos(self, estado: Optional[str] = None) -> List[Pedido]:
        return self.repository.listar_todos(estado)

    def listar_pedidos_usuario(self, usuario_id: int) -> List[Pedido]:
        return self.repository.listar_por_usuario(usuario_id)

    def cambiar_estado(self, pedido_id: int, nuevo_estado: str) -> Pedido:
        pedido = self.obtener_pedido(pedido_id)
        pedido.cambiar_estado(nuevo_estado)  # la entidad valida la transición
        pedido = self.repository.guardar(pedido)

        # Al finalizar el pedido, el repartidor vuelve a quedar libre
        if pedido.esta_finalizado() and pedido.repartidor_id:
            self.repartidores.marcar_disponibilidad(pedido.repartidor_id, True)
        return pedido

    def cancelar_pedido(self, pedido_id: int) -> Pedido:
        return self.cambiar_estado(pedido_id, "Cancelado")

    def asignar_repartidor(self, pedido_id: int, repartidor_id: int) -> Pedido:
        pedido = self.obtener_pedido(pedido_id)

        repartidor = self.repartidores.obtener_repartidor(repartidor_id)
        if not repartidor:
            raise RepartidorNoDisponibleException(f"No existe el repartidor con id {repartidor_id}.")
        if not repartidor.disponible and pedido.repartidor_id != repartidor_id:
            raise RepartidorNoDisponibleException(f"El repartidor {repartidor_id} no está disponible.")

        anterior = pedido.repartidor_id
        pedido.asignar_repartidor(repartidor_id)
        pedido = self.repository.guardar(pedido)

        # Liberar al repartidor anterior (si cambió) y ocupar al nuevo
        if anterior and anterior != repartidor_id:
            self.repartidores.marcar_disponibilidad(anterior, True)
        self.repartidores.marcar_disponibilidad(repartidor_id, False)
        return pedido
