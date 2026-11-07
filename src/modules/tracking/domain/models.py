# modulo tracking
''' Entidades puras de dominio
========================================
Repartidor y UbicacionTracking con sus reglas de negocio, sin depender de SQLAlchemy.
'''
from dataclasses import dataclass, field
from datetime import date, time, datetime
from typing import Optional

from src.modules.tracking.domain.exceptions import (
    DatosRepartidorInvalidosException,
    UbicacionInvalidaException,
)

TIPOS_VEHICULO = ("Bicicleta", "Moto", "Taxi")


@dataclass
class Repartidor:
    tipo_vehiculo: str
    placa: Optional[str] = None
    disponible: bool = True
    usuario_id: Optional[int] = None
    repartidor_id: Optional[int] = None

    def __post_init__(self):
        if self.tipo_vehiculo not in TIPOS_VEHICULO:
            raise DatosRepartidorInvalidosException(
                f"Tipo de vehículo inválido. Use: {', '.join(TIPOS_VEHICULO)}."
            )
        # Regla de negocio: los vehículos motorizados deben tener placa
        if self.tipo_vehiculo in ("Moto", "Taxi") and not (self.placa and self.placa.strip()):
            raise DatosRepartidorInvalidosException(f"Un repartidor en {self.tipo_vehiculo} debe registrar placa.")

    def marcar_disponible(self):
        self.disponible = True

    def marcar_ocupado(self):
        self.disponible = False


@dataclass
class UbicacionTracking:
    repartidor_id: int
    latitud: float
    longitud: float
    fecha: date = field(default_factory=date.today)
    hora: time = field(default_factory=lambda: datetime.now().time().replace(microsecond=0))
    ubicacion_tracking_id: Optional[int] = None

    def __post_init__(self):
        if not -90 <= float(self.latitud) <= 90:
            raise UbicacionInvalidaException("La latitud debe estar entre -90 y 90.")
        if not -180 <= float(self.longitud) <= 180:
            raise UbicacionInvalidaException("La longitud debe estar entre -180 y 180.")
