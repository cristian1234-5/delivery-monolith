# modulo auth
''' Entidades puras de dominio
========================================
Representan el concepto de negocio sin depender de SQLAlchemy ni de la BD.
'''
from dataclasses import dataclass
from typing import Optional

from src.modules.auth.domain.exceptions import DatosInvalidosException

# IDs de los catálogos (init.sql)
ROLES_VALIDOS = (1, 2, 3)            # cliente, repartidor, admin
ESTADO_ACTIVO = 1
ESTADOS_VALIDOS = (1, 2, 3, 4)       # activo, inactivo, suspendido, eliminado


@dataclass
class Usuario:
    nombre_usuario: str
    email: str
    contrasenia: str
    rol_id: int
    estado_id: int
    usuario_id: Optional[int] = None

    def cambiar_password(self, nueva_contrasenia: str):
        """Ejemplo de regla de negocio pura dentro de la entidad."""
        if len(nueva_contrasenia) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")
        self.contrasenia = nueva_contrasenia

    def esta_activo(self) -> bool:
        return self.estado_id == ESTADO_ACTIVO

    def cambiar_estado(self, estado_id: int):
        if estado_id not in ESTADOS_VALIDOS:
            raise DatosInvalidosException("Estado de usuario inválido.")
        self.estado_id = estado_id


@dataclass
class Contacto:
    usuario_id: int
    phone_personal: Optional[str] = None
    phone_trabajo: Optional[str] = None
    domicilio: Optional[str] = None
    contacto_id: Optional[int] = None


@dataclass
class Direccion:
    usuario_id: int
    direccion_texto: str
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    referencia: Optional[str] = None
    etiqueta: Optional[str] = None        # ej. "Casa", "Trabajo"
    es_temporal: bool = False
    direccion_id: Optional[int] = None

    def __post_init__(self):
        if not self.direccion_texto or not self.direccion_texto.strip():
            raise DatosInvalidosException("La dirección es obligatoria.")
        if self.latitud is not None and not -90 <= float(self.latitud) <= 90:
            raise DatosInvalidosException("La latitud debe estar entre -90 y 90.")
        if self.longitud is not None and not -180 <= float(self.longitud) <= 180:
            raise DatosInvalidosException("La longitud debe estar entre -180 y 180.")
