from sqlalchemy.orm import Session
from src.modules.auth.infrastructure.repository_impl import AuthRepositorySqlAlchemy
from src.modules.auth.domain.models import Usuario
from src.modules.auth.domain.exceptions import EmailYaRegistradoException
from src.modules.auth.presentation.schemas import UsuarioCreate

class AuthService:
    def __init__(self, db: Session):
        self.repository = AuthRepositorySqlAlchemy(db)

    def registrar_usuario(self, data: UsuarioCreate) -> Usuario:
        # 1. Verificar si el email ya existe a través del contrato
        usuario_existente = self.repository.obtener_por_email(data.email)
        if usuario_existente:
            raise EmailYaRegistradoException(f"El correo {data.email} ya está registrado en el sistema.")

        # 2. Instanciar la Entidad Pura de Dominio (Independiente de SQLAlchemy)
        nuevo_usuario = Usuario(
            nombre_usuario=data.nombre_usuario,
            email=data.email,
            contrasenia=data.contrasenia,  # Idealmente hasheada aquí o en un servicio de dominio
            rol_id=data.rol_id,
            estado_id=data.estado_id
        )

        # 3. Guardar la entidad pura mediante el repositorio
        return self.repository.guardar(nuevo_usuario)