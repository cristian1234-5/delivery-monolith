# modulo auth
''' Casos de uso del módulo auth (orquestación de la lógica de negocio). '''
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from src.core.config import ADMIN_NOMBRE, ADMIN_EMAIL, ADMIN_PASSWORD
from src.core.security import UsuarioActual, crear_token, ROL_ADMIN
from src.modules.auth.infrastructure.repository_impl import AuthRepositorySqlAlchemy
from src.modules.auth.infrastructure.external_adapters import PasswordHasher
from src.modules.auth.domain.models import (
    Usuario,
    Contacto,
    Direccion,
    ROLES_VALIDOS,
    ESTADO_ACTIVO,
)
from src.modules.auth.domain.exceptions import (
    DomainException,
    AccesoDenegadoException,
    EmailYaRegistradoException,
    UsuarioNoEncontradoException,
    ContactoNoEncontradoException,
    DireccionNoEncontradaException,
    CredencialesInvalidasException,
    UsuarioInactivoException,
    DatosInvalidosException,
)
from src.modules.auth.presentation.schemas import (
    UsuarioCreate,
    UsuarioLogin,
    ContactoUpdate,
    DireccionCreate,
)


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = AuthRepositorySqlAlchemy(db)

    # ============ Arranque ============
    def inicializar_sistema(self) -> None:
        """Crea roles/estados base y el administrador inicial si no existen."""
        self.repository.asegurar_catalogos()
        if not self.repository.existe_admin() and not self.repository.obtener_por_email(ADMIN_EMAIL):
            admin = Usuario(
                nombre_usuario=ADMIN_NOMBRE,
                email=ADMIN_EMAIL,
                contrasenia=PasswordHasher.hashear(ADMIN_PASSWORD),
                rol_id=ROL_ADMIN,
                estado_id=ESTADO_ACTIVO,
            )
            self.repository.guardar(admin)
        self.db.commit()

    # ============ Registro y login ============
    def registrar_usuario(self, data: UsuarioCreate, actor: Optional[UsuarioActual] = None) -> Usuario:
        es_admin = actor is not None and actor.es_admin

        # 1. Reglas de negocio sobre el rol
        if data.rol_id not in ROLES_VALIDOS:
            raise DatosInvalidosException("Rol inválido. Use 1 (cliente), 2 (repartidor) o 3 (admin).")
        if data.rol_id == ROL_ADMIN and not es_admin:
            raise AccesoDenegadoException("Solo un administrador puede crear otros administradores.")

        # 2. El email no debe existir
        if self.repository.obtener_por_email(data.email):
            raise EmailYaRegistradoException(f"El correo {data.email} ya está registrado en el sistema.")

        # 3. Entidad pura de dominio: valida la contraseña con su propia regla
        nuevo_usuario = Usuario(
            nombre_usuario=data.nombre_usuario,
            email=data.email,
            contrasenia="",
            rol_id=data.rol_id,
            # Un registro público siempre queda activo; solo el admin elige el estado
            estado_id=data.estado_id if es_admin else ESTADO_ACTIVO,
        )
        try:
            nuevo_usuario.cambiar_password(data.contrasenia)
        except ValueError as e:
            raise DomainException(str(e))

        # 4. Guardar la contraseña hasheada (nunca en texto plano)
        nuevo_usuario.contrasenia = PasswordHasher.hashear(nuevo_usuario.contrasenia)

        usuario = self.repository.guardar(nuevo_usuario)
        self.db.commit()
        return usuario

    def login(self, data: UsuarioLogin) -> Tuple[Usuario, str]:
        usuario = self.repository.obtener_por_email(data.email)
        if not usuario or not PasswordHasher.verificar(data.contrasenia, usuario.contrasenia):
            raise CredencialesInvalidasException("Email o contraseña incorrectos.")
        if not usuario.esta_activo():
            raise UsuarioInactivoException("La cuenta del usuario no está activa.")
        return usuario, crear_token(usuario.usuario_id, usuario.rol_id)

    # ============ Usuarios ============
    def obtener_usuario(self, usuario_id: int, actor: UsuarioActual) -> Usuario:
        if not actor.es_admin and actor.usuario_id != usuario_id:
            raise AccesoDenegadoException("Solo puede ver su propio usuario.")
        usuario = self.repository.obtener_por_id(usuario_id)
        if not usuario:
            raise UsuarioNoEncontradoException(f"No existe el usuario con id {usuario_id}.")
        return usuario

    def listar_usuarios(self, skip: int = 0, limit: int = 50) -> List[Usuario]:
        return self.repository.listar_todos(skip, limit)

    def cambiar_estado_usuario(self, usuario_id: int, estado_id: int, actor: UsuarioActual) -> Usuario:
        if usuario_id == actor.usuario_id:
            raise DatosInvalidosException("Un administrador no puede cambiar su propio estado.")
        usuario = self.obtener_usuario(usuario_id, actor)
        usuario.cambiar_estado(estado_id)
        usuario = self.repository.guardar(usuario)
        self.db.commit()
        return usuario

    # ============ Contacto ============
    def obtener_contacto(self, usuario_id: int) -> Contacto:
        contacto = self.repository.obtener_contacto(usuario_id)
        if not contacto:
            raise ContactoNoEncontradoException("Aún no registró sus datos de contacto.")
        return contacto

    def guardar_contacto(self, usuario_id: int, data: ContactoUpdate) -> Contacto:
        contacto = self.repository.guardar_contacto(Contacto(usuario_id=usuario_id, **data.model_dump()))
        self.db.commit()
        return contacto

    # ============ Direcciones ============
    def listar_direcciones(self, usuario_id: int) -> List[Direccion]:
        return self.repository.listar_direcciones(usuario_id)

    def agregar_direccion(self, usuario_id: int, data: DireccionCreate) -> Direccion:
        direccion = self.repository.guardar_direccion(Direccion(usuario_id=usuario_id, **data.model_dump()))
        self.db.commit()
        return direccion

    def eliminar_direccion(self, usuario_id: int, direccion_id: int) -> None:
        direccion = self.repository.obtener_direccion(direccion_id)
        if not direccion or direccion.usuario_id != usuario_id:
            raise DireccionNoEncontradaException(f"No tiene una dirección con id {direccion_id}.")
        self.repository.eliminar_direccion(direccion_id)
        self.db.commit()
