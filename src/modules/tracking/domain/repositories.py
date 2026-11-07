# modulo tracking
''' Contrato abstracto (ABC) del repositorio de repartidores y ubicaciones. '''
from abc import ABC, abstractmethod
from typing import Optional, List

from src.modules.tracking.domain.models import Repartidor, UbicacionTracking


class ITrackingRepository(ABC):

    # ----- Repartidores -----
    @abstractmethod
    def obtener_repartidor(self, repartidor_id: int) -> Optional[Repartidor]:
        pass

    @abstractmethod
    def listar_repartidores(self, solo_disponibles: bool = False) -> List[Repartidor]:
        pass

    @abstractmethod
    def guardar_repartidor(self, repartidor: Repartidor) -> Repartidor:
        pass

    # ----- Ubicaciones -----
    @abstractmethod
    def registrar_ubicacion(self, ubicacion: UbicacionTracking) -> UbicacionTracking:
        pass

    @abstractmethod
    def listar_ubicaciones(self, repartidor_id: int) -> List[UbicacionTracking]:
        pass

    @abstractmethod
    def ultima_ubicacion(self, repartidor_id: int) -> Optional[UbicacionTracking]:
        pass
