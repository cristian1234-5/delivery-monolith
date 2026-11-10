# modulo order
''' Casos de uso del módulo order.
Cada caso de uso que modifica datos termina con UN solo commit:
si cualquier paso falla (pedido, repartidor o pago), se revierte todo.
'''
from typing import List, Optional
from sqlalchemy.orm import Session

from src.core.clock import ahora_local
from src.core.security import UsuarioActual
from src.modules.order.infraestructure.repository_impl import OrderRepositorySqlAlchemy
from src.modules.order.infraestructure.external_adapters import (
    UsuarioAdapter,
    CatalogoAdapter,
    RepartidorAdapter,
    PagoAdapter,
)
from src.modules.order.domain.models import Pedido, DetallePedido
from src.modules.order.domain.exceptions import (
    AccesoDenegadoException,
    PedidoNoEncontradoException,
    UsuarioNoValidoException,
    DireccionNoValidaException,
    RestauranteNoDisponibleException,
    ProductoNoValidoException,
    RepartidorNoDisponibleException,
)
from src.modules.order.presentation.schemas import PedidoCreate

# Qué estados puede poner cada rol (el admin puede todos)
ESTADOS_POR_REPARTIDOR = ("En_Camino", "Entregado")
ESTADOS_POR_CLIENTE = ("Cancelado",)


class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = OrderRepositorySqlAlchemy(db)
        self.usuarios = UsuarioAdapter(db)
        self.catalogo = CatalogoAdapter(db)
        self.repartidores = RepartidorAdapter(db)
        self.pagos = PagoAdapter(db)

    # ============ Permisos ============
    def _repartidor_id_de(self, actor: UsuarioActual) -> Optional[int]:
        if not actor.es_repartidor:
            return None
        repartidor = self.repartidores.obtener_por_usuario(actor.usuario_id)
        return repartidor.repartidor_id if repartidor else None

    def _verificar_acceso(self, pedido: Pedido, actor: UsuarioActual) -> None:
        if actor.es_admin:
            return
        if actor.es_cliente and pedido.usuario_id == actor.usuario_id:
            return
        if actor.es_repartidor and pedido.repartidor_id and pedido.repartidor_id == self._repartidor_id_de(actor):
            return
        raise AccesoDenegadoException("No tiene acceso a este pedido.")

    # ============ Crear ============
    def crear_pedido(self, data: PedidoCreate, actor: UsuarioActual) -> Pedido:
        usuario_id = actor.usuario_id

        # 1. El cliente debe existir y estar activo (módulo auth)
        if not self.usuarios.esta_activo(usuario_id):
            raise UsuarioNoValidoException("Su cuenta no está activa; no puede realizar pedidos.")

        # 2. La dirección de entrega debe ser del cliente (módulo auth)
        if not self.usuarios.direccion_pertenece(data.direccion_id, usuario_id):
            raise DireccionNoValidaException(f"La dirección {data.direccion_id} no le pertenece.")

        # 3. El restaurante debe existir, estar abierto y en horario (módulo restaurant)
        restaurante = self.catalogo.obtener_restaurante(data.restaurant_id)
        if not restaurante:
            raise RestauranteNoDisponibleException(f"No existe el restaurante con id {data.restaurant_id}.")
        if not restaurante.esta_abierto():
            raise RestauranteNoDisponibleException(f"El restaurante '{restaurante.nombre}' está cerrado.")
        if not restaurante.esta_en_horario(ahora_local().time()):
            raise RestauranteNoDisponibleException(
                f"El restaurante '{restaurante.nombre}' atiende de "
                f"{restaurante.horario_apertura:%H:%M} a {restaurante.horario_cierre:%H:%M}."
            )

        # 4. Cada producto debe pertenecer al restaurante y estar disponible.
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

        # 5. Crear la entidad de dominio, calcular el total y guardar
        pedido = Pedido(
            usuario_id=usuario_id,
            restaurant_id=data.restaurant_id,
            direccion_id=data.direccion_id,
            detalles=detalles,
            notas_cliente=data.notas_cliente,
        )
        pedido.validar_nuevo()
        pedido = self.repository.guardar(pedido)
        self.db.commit()
        return pedido

    # ============ Consultar ============
    def obtener_pedido(self, pedido_id: int, actor: UsuarioActual) -> Pedido:
        pedido = self.repository.obtener_por_id(pedido_id)
        if not pedido:
            raise PedidoNoEncontradoException(f"No existe el pedido con id {pedido_id}.")
        self._verificar_acceso(pedido, actor)
        return pedido

    def listar_pedidos(
        self, estado: Optional[str] = None, usuario_id: Optional[int] = None, skip: int = 0, limit: int = 50
    ) -> List[Pedido]:
        return self.repository.listar_todos(estado, usuario_id, skip, limit)

    def listar_mis_pedidos(self, actor: UsuarioActual, skip: int = 0, limit: int = 50) -> List[Pedido]:
        """Cliente: sus pedidos. Repartidor: los que tiene asignados. Admin: todos."""
        if actor.es_admin:
            return self.repository.listar_todos(skip=skip, limit=limit)
        if actor.es_repartidor:
            repartidor_id = self._repartidor_id_de(actor)
            return self.repository.listar_por_repartidor(repartidor_id, skip, limit) if repartidor_id else []
        return self.repository.listar_todos(usuario_id=actor.usuario_id, skip=skip, limit=limit)

    # ============ Ciclo de vida ============
    def cambiar_estado(self, pedido_id: int, nuevo_estado: str, actor: UsuarioActual) -> Pedido:
        pedido = self.obtener_pedido(pedido_id, actor)

        if not actor.es_admin:
            permitidos = ESTADOS_POR_REPARTIDOR if actor.es_repartidor else ESTADOS_POR_CLIENTE
            if nuevo_estado not in permitidos:
                raise AccesoDenegadoException(f"Su rol no puede cambiar el pedido a '{nuevo_estado}'.")

        pedido.cambiar_estado(nuevo_estado)  # la entidad valida la transición
        pedido = self.repository.guardar(pedido)

        # Al finalizar el pedido, el repartidor vuelve a quedar libre
        if pedido.esta_finalizado() and pedido.repartidor_id:
            self.repartidores.marcar_disponibilidad(pedido.repartidor_id, True)
        # Al entregar, el pago en efectivo queda cobrado
        if pedido.estado == "Entregado":
            self.pagos.confirmar_efectivo_pendiente(pedido.pedido_id)

        self.db.commit()  # todo o nada
        return pedido

    def cancelar_pedido(self, pedido_id: int, actor: UsuarioActual) -> Pedido:
        return self.cambiar_estado(pedido_id, "Cancelado", actor)

    def asignar_repartidor(self, pedido_id: int, repartidor_id: int, actor: UsuarioActual) -> Pedido:
        pedido = self.obtener_pedido(pedido_id, actor)

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

        self.db.commit()  # pedido y repartidor se guardan juntos
        return pedido
