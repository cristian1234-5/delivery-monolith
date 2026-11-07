# modulo auth
''' Casos de uso del módulo auth (orquestación de la lógica de negocio). '''
from typing import List
from sqlalchemy.orm import Session

from src.modules.auth.infrastructure.repository_impl import AuthRepositorySqlAlchemy
from src.modules.auth.infrastructure.external_adapters import PasswordHasher
from src.modules.auth.domain.models import Usuario
from src.modules.auth.domain.exceptions import (
    DomainException,
    EmailYaRegistradoException,
    UsuarioNoEncontradoException,
    CredencialesInvalidasException,
    UsuarioInactivoException,
)
from src.modules.auth.presentation.schemas import UsuarioCreate, UsuarioLogin

ESTADO_ACTIVO_ID = 1  # 'activo' en la tabla estado (init.sql)


class AuthService:
    def __init__(self, db: Session):
        self.repository = AuthRepositorySqlAlchemy(db)

    def registrar_usuario(self, data: UsuarioCreate) -> Usuario:
        # 1. Regla de negocio: el email no debe existir
        if self.repository.obtener_por_email(data.email):
            raise EmailYaRegistradoException(f"El correo {data.email} ya está registrado en el sistema.")

        # 2. Entidad pura de dominio: valida la contraseña con su propia regla
        nuevo_usuario = Usuario(
            nombre_usuario=data.nombre_usuario,
            email=data.email,
            contrasenia="",
            rol_id=data.rol_id,
            estado_id=data.estado_id,
        )
        try:
            nuevo_usuario.cambiar_password(data.contrasenia)
        except ValueError as e:
            raise DomainException(str(e))

        # 3. Guardar la contraseña hasheada (nunca en texto plano)
        nuevo_usuario.contrasenia = PasswordHasher.hashear(nuevo_usuario.contrasenia)

        # 4. Guardar mediante el repositorio
        return self.repository.guardar(nuevo_usuario)

    def login(self, data: UsuarioLogin) -> Usuario:
        usuario = self.repository.obtener_por_email(data.email)
        if not usuario or not PasswordHasher.verificar(data.contrasenia, usuario.contrasenia):
            raise CredencialesInvalidasException("Email o contraseña incorrectos.")
        if usuario.estado_id != ESTADO_ACTIVO_ID:
            raise UsuarioInactivoException("La cuenta del usuario no está activa.")
        return usuario

    def obtener_usuario(self, usuario_id: int) -> Usuario:
        usuario = self.repository.obtener_por_id(usuario_id)
        if not usuario:
            raise UsuarioNoEncontradoException(f"No existe el usuario con id {usuario_id}.")
        return usuario

    def listar_usuarios(self) -> List[Usuario]:
        return self.repository.listar_todos()
