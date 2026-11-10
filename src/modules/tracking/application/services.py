# modulo tracking
''' Casos de uso del módulo tracking. '''
from typing import List
from sqlalchemy.orm import Session

from src.core.security import UsuarioActual
from src.modules.tracking.infraestructure.repository_impl import TrackingRepositorySqlAlchemy
from src.modules.tracking.infraestructure.external_adapters import UsuarioAdapter, PedidoAdapter
from src.modules.tracking.domain.models import Repartidor, UbicacionTracking
from src.modules.tracking.domain.exceptions import (
    AccesoDenegadoException,
    RepartidorNoEncontradoException,
    PedidoNoEncontradoException,
    SinUbicacionException,
    UsuarioNoValidoException,
)
from src.modules.tracking.presentation.schemas import RepartidorCreate, UbicacionCreate


class TrackingService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = TrackingRepositorySqlAlchemy(db)
        self.usuarios = UsuarioAdapter(db)
        self.pedidos = PedidoAdapter(db)

    # ============ Permisos ============
    def _es_el_mismo(self, repartidor: Repartidor, actor: UsuarioActual) -> bool:
        return actor.es_repartidor and repartidor.usuario_id == actor.usuario_id

    def _verificar_admin_o_mismo(self, repartidor: Repartidor, actor: UsuarioActual) -> None:
        if not actor.es_admin and not self._es_el_mismo(repartidor, actor):
            raise AccesoDenegadoException("Solo el propio repartidor o un admin pueden hacer esto.")

    # ============ Repartidores ============
    def registrar_repartidor(self, data: RepartidorCreate) -> Repartidor:
        if data.usuario_id is not None:
            # El usuario debe existir y tener rol repartidor (módulo auth)
            if not self.usuarios.es_repartidor(data.usuario_id):
                raise UsuarioNoValidoException(
                    f"El usuario {data.usuario_id} no existe o no tiene rol de repartidor."
                )
            # Un usuario solo puede tener un perfil de repartidor
            if self.repository.obtener_por_usuario(data.usuario_id):
                raise UsuarioNoValidoException(f"El usuario {data.usuario_id} ya está registrado como repartidor.")

        repartidor = self.repository.guardar_repartidor(Repartidor(**data.model_dump()))
        self.db.commit()
        return repartidor

    def obtener_repartidor(self, repartidor_id: int, actor: UsuarioActual) -> Repartidor:
        repartidor = self.repository.obtener_repartidor(repartidor_id)
        if not repartidor:
            raise RepartidorNoEncontradoException(f"No existe el repartidor con id {repartidor_id}.")
        self._verificar_admin_o_mismo(repartidor, actor)
        return repartidor

    def mi_perfil(self, actor: UsuarioActual) -> Repartidor:
        repartidor = self.repository.obtener_por_usuario(actor.usuario_id)
        if not repartidor:
            raise RepartidorNoEncontradoException("Su usuario no tiene un perfil de repartidor.")
        return repartidor

    def listar_repartidores(self, solo_disponibles: bool = False, skip: int = 0, limit: int = 50) -> List[Repartidor]:
        return self.repository.listar_repartidores(solo_disponibles, skip, limit)

    def cambiar_disponibilidad(self, repartidor_id: int, disponible: bool, actor: UsuarioActual) -> Repartidor:
        repartidor = self.obtener_repartidor(repartidor_id, actor)
        repartidor.marcar_disponible() if disponible else repartidor.marcar_ocupado()
        repartidor = self.repository.guardar_repartidor(repartidor)
        self.db.commit()
        return repartidor

    # ============ Ubicaciones (GPS) ============
    def registrar_ubicacion(self, repartidor_id: int, data: UbicacionCreate, actor: UsuarioActual) -> UbicacionTracking:
        repartidor = self.repository.obtener_repartidor(repartidor_id)
        if not repartidor:
            raise RepartidorNoEncontradoException(f"No existe el repartidor con id {repartidor_id}.")
        # Solo el propio repartidor envía su GPS
        if not self._es_el_mismo(repartidor, actor):
            raise AccesoDenegadoException("Solo el propio repartidor puede reportar su ubicación.")

        ubicacion = self.repository.registrar_ubicacion(
            UbicacionTracking(repartidor_id=repartidor_id, latitud=data.latitud, longitud=data.longitud)
        )
        self.db.commit()
        return ubicacion

    def historial_ubicaciones(
        self, repartidor_id: int, actor: UsuarioActual, skip: int = 0, limit: int = 50
    ) -> List[UbicacionTracking]:
        self.obtener_repartidor(repartidor_id, actor)
        return self.repository.listar_ubicaciones(repartidor_id, skip, limit)

    def ubicacion_actual(self, repartidor_id: int, actor: UsuarioActual) -> UbicacionTracking:
        self.obtener_repartidor(repartidor_id, actor)
        ubicacion = self.repository.ultima_ubicacion(repartidor_id)
        if not ubicacion:
            raise SinUbicacionException(f"El repartidor {repartidor_id} aún no reportó ubicación.")
        return ubicacion

    # ============ Seguimiento de un pedido ============
    def seguimiento_pedido(self, pedido_id: int, actor: UsuarioActual) -> dict:
        pedido = self.pedidos.obtener_pedido(pedido_id)
        if not pedido:
            raise PedidoNoEncontradoException(f"No existe el pedido con id {pedido_id}.")

        repartidor = self.repository.obtener_repartidor(pedido.repartidor_id) if pedido.repartidor_id else None

        # Pueden verlo: el cliente dueño, el repartidor asignado o un admin
        es_dueno = pedido.usuario_id == actor.usuario_id
        es_su_repartidor = repartidor is not None and self._es_el_mismo(repartidor, actor)
        if not (actor.es_admin or es_dueno or es_su_repartidor):
            raise AccesoDenegadoException("No tiene acceso al seguimiento de este pedido.")

        ubicacion = self.repository.ultima_ubicacion(repartidor.repartidor_id) if repartidor else None
        return {
            "pedido_id": pedido.pedido_id,
            "estado_pedido": pedido.estado,
            "repartidor": repartidor,
            "ubicacion_actual": ubicacion,
        }
