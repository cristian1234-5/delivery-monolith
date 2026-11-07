# modulo tracking
''' Casos de uso del módulo tracking. '''
from typing import List
from sqlalchemy.orm import Session

from src.modules.tracking.infraestructure.repository_impl import TrackingRepositorySqlAlchemy
from src.modules.tracking.infraestructure.external_adapters import UsuarioAdapter, PedidoAdapter
from src.modules.tracking.domain.models import Repartidor, UbicacionTracking
from src.modules.tracking.domain.exceptions import (
    RepartidorNoEncontradoException,
    PedidoNoEncontradoException,
    SinUbicacionException,
    UsuarioNoValidoException,
)
from src.modules.tracking.presentation.schemas import RepartidorCreate, UbicacionCreate


class TrackingService:
    def __init__(self, db: Session):
        self.repository = TrackingRepositorySqlAlchemy(db)
        self.usuarios = UsuarioAdapter(db)
        self.pedidos = PedidoAdapter(db)

    # ============ Repartidores ============
    def registrar_repartidor(self, data: RepartidorCreate) -> Repartidor:
        # Si se vincula a un usuario, debe existir y tener rol repartidor (módulo auth)
        if data.usuario_id is not None and not self.usuarios.es_repartidor(data.usuario_id):
            raise UsuarioNoValidoException(
                f"El usuario {data.usuario_id} no existe o no tiene rol de repartidor."
            )
        repartidor = Repartidor(**data.model_dump())
        return self.repository.guardar_repartidor(repartidor)

    def obtener_repartidor(self, repartidor_id: int) -> Repartidor:
        repartidor = self.repository.obtener_repartidor(repartidor_id)
        if not repartidor:
            raise RepartidorNoEncontradoException(f"No existe el repartidor con id {repartidor_id}.")
        return repartidor

    def listar_repartidores(self, solo_disponibles: bool = False) -> List[Repartidor]:
        return self.repository.listar_repartidores(solo_disponibles)

    def cambiar_disponibilidad(self, repartidor_id: int, disponible: bool) -> Repartidor:
        repartidor = self.obtener_repartidor(repartidor_id)
        repartidor.marcar_disponible() if disponible else repartidor.marcar_ocupado()
        return self.repository.guardar_repartidor(repartidor)

    # ============ Ubicaciones (GPS) ============
    def registrar_ubicacion(self, repartidor_id: int, data: UbicacionCreate) -> UbicacionTracking:
        self.obtener_repartidor(repartidor_id)
        ubicacion = UbicacionTracking(
            repartidor_id=repartidor_id, latitud=data.latitud, longitud=data.longitud
        )
        return self.repository.registrar_ubicacion(ubicacion)

    def historial_ubicaciones(self, repartidor_id: int) -> List[UbicacionTracking]:
        self.obtener_repartidor(repartidor_id)
        return self.repository.listar_ubicaciones(repartidor_id)

    def ubicacion_actual(self, repartidor_id: int) -> UbicacionTracking:
        self.obtener_repartidor(repartidor_id)
        ubicacion = self.repository.ultima_ubicacion(repartidor_id)
        if not ubicacion:
            raise SinUbicacionException(f"El repartidor {repartidor_id} aún no reportó ubicación.")
        return ubicacion

    # ============ Seguimiento de un pedido ============
    def seguimiento_pedido(self, pedido_id: int) -> dict:
        pedido = self.pedidos.obtener_pedido(pedido_id)
        if not pedido:
            raise PedidoNoEncontradoException(f"No existe el pedido con id {pedido_id}.")

        repartidor = None
        ubicacion = None
        if pedido.repartidor_id:
            repartidor = self.repository.obtener_repartidor(pedido.repartidor_id)
            ubicacion = self.repository.ultima_ubicacion(pedido.repartidor_id)

        return {
            "pedido_id": pedido.pedido_id,
            "estado_pedido": pedido.estado,
            "repartidor": repartidor,
            "ubicacion_actual": ubicacion,
        }
