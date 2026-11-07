# modulo auth
''' Entidades puras de dominio
========================================
Representan el concepto de negocio sin depender de SQLAlchemy ni de la BD.
'''
from dataclasses import dataclass
from typing import Optional


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
