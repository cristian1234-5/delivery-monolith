# modulo auth
''' Contrato abstracto (ABC) del repositorio de usuarios.
Los servicios usan esta interfaz sin saber qué base de datos hay detrás.
'''
from abc import ABC, abstractmethod
from typing import Optional, List

from src.modules.auth.domain.models import Usuario, Contacto, Direccion


class IAuthRepository(ABC):

    # ----- Usuarios -----
    @abstractmethod
    def obtener_por_id(self, usuario_id: int) -> Optional[Usuario]:
        pass

    @abstractmethod
    def obtener_por_email(self, email: str) -> Optional[Usuario]:
        pass

    @abstractmethod
    def guardar(self, usuario: Usuario) -> Usuario:
        pass

    @abstractmethod
    def listar_todos(self, skip: int = 0, limit: int = 50) -> List[Usuario]:
        pass

    @abstractmethod
    def existe_admin(self) -> bool:
        pass

    @abstractmethod
    def asegurar_catalogos(self) -> None:
        """Garantiza que existan los roles y estados base."""
        pass

    # ----- Contacto -----
    @abstractmethod
    def obtener_contacto(self, usuario_id: int) -> Optional[Contacto]:
        pass

    @abstractmethod
    def guardar_contacto(self, contacto: Contacto) -> Contacto:
        pass

    # ----- Direcciones -----
    @abstractmethod
    def listar_direcciones(self, usuario_id: int) -> List[Direccion]:
        pass

    @abstractmethod
    def obtener_direccion(self, direccion_id: int) -> Optional[Direccion]:
        pass

    @abstractmethod
    def guardar_direccion(self, direccion: Direccion) -> Direccion:
        pass

    @abstractmethod
    def eliminar_direccion(self, direccion_id: int) -> None:
        pass
