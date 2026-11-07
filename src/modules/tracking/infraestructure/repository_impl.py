# modulo tracking
''' Implementación concreta del repositorio con SQLAlchemy.
Traduce RepartidorModel/UbicacionTrackingModel (BD) <-> Repartidor/UbicacionTracking (dominio).
'''
from typing import Optional, List
from sqlalchemy.orm import Session

from src.modules.tracking.domain.repositories import ITrackingRepository
from src.modules.tracking.domain.models import Repartidor, UbicacionTracking
from src.modules.tracking.infraestructure.models_db import RepartidorModel, UbicacionTrackingModel


class TrackingRepositorySqlAlchemy(ITrackingRepository):
    def __init__(self, db: Session):
        self.db = db

    # ============ Mapeadores ============
    def _repartidor_to_domain(self, model: RepartidorModel) -> Optional[Repartidor]:
        if not model:
            return None
        return Repartidor(
            repartidor_id=model.repartidor_id,
            tipo_vehiculo=model.tipo_vehiculo,
            placa=model.placa,
            disponible=model.disponible,
            usuario_id=model.usuario_id,
        )

    def _ubicacion_to_domain(self, model: UbicacionTrackingModel) -> Optional[UbicacionTracking]:
        if not model:
            return None
        return UbicacionTracking(
            ubicacion_tracking_id=model.ubicacion_tracking_id,
            repartidor_id=model.repartidor_id,
            latitud=float(model.latitud),
            longitud=float(model.longitud),
            fecha=model.fecha,
            hora=model.hora,
        )

    # ============ Repartidores ============
    def obtener_repartidor(self, repartidor_id: int) -> Optional[Repartidor]:
        model = self.db.query(RepartidorModel).filter(RepartidorModel.repartidor_id == repartidor_id).first()
        return self._repartidor_to_domain(model)

    def listar_repartidores(self, solo_disponibles: bool = False) -> List[Repartidor]:
        query = self.db.query(RepartidorModel)
        if solo_disponibles:
            query = query.filter(RepartidorModel.disponible.is_(True))
        return [self._repartidor_to_domain(m) for m in query.order_by(RepartidorModel.repartidor_id).all()]

    def guardar_repartidor(self, repartidor: Repartidor) -> Repartidor:
        model = None
        if repartidor.repartidor_id:
            model = self.db.query(RepartidorModel).filter(
                RepartidorModel.repartidor_id == repartidor.repartidor_id
            ).first()
        if not model:
            model = RepartidorModel()
            self.db.add(model)

        model.tipo_vehiculo = repartidor.tipo_vehiculo
        model.placa = repartidor.placa
        model.disponible = repartidor.disponible
        model.usuario_id = repartidor.usuario_id

        self.db.commit()
        self.db.refresh(model)
        return self._repartidor_to_domain(model)

    # ============ Ubicaciones ============
    def registrar_ubicacion(self, ubicacion: UbicacionTracking) -> UbicacionTracking:
        model = UbicacionTrackingModel(
            repartidor_id=ubicacion.repartidor_id,
            latitud=ubicacion.latitud,
            longitud=ubicacion.longitud,
            fecha=ubicacion.fecha,
            hora=ubicacion.hora,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._ubicacion_to_domain(model)

    def listar_ubicaciones(self, repartidor_id: int) -> List[UbicacionTracking]:
        query = (
            self.db.query(UbicacionTrackingModel)
            .filter(UbicacionTrackingModel.repartidor_id == repartidor_id)
            .order_by(UbicacionTrackingModel.ubicacion_tracking_id.desc())
        )
        return [self._ubicacion_to_domain(m) for m in query.all()]

    def ultima_ubicacion(self, repartidor_id: int) -> Optional[UbicacionTracking]:
        model = (
            self.db.query(UbicacionTrackingModel)
            .filter(UbicacionTrackingModel.repartidor_id == repartidor_id)
            .order_by(UbicacionTrackingModel.ubicacion_tracking_id.desc())
            .first()
        )
        return self._ubicacion_to_domain(model)
