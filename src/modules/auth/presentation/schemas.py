<<<<<<< HEAD
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
=======
# modulo auth
''' DTOs de Pydantic para validar entradas y salidas HTTP. '''
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ============ Usuario ============
class UsuarioCreate(BaseModel):
    nombre_usuario: str = Field(min_length=1, max_length=64)
    email: EmailStr
    contrasenia: str
    rol_id: int = 1      # 1 = cliente, 2 = repartidor, 3 = admin (solo lo crea un admin)
    estado_id: int = 1   # 1 = activo (solo un admin puede elegir otro)


class UsuarioLogin(BaseModel):
    email: EmailStr
    contrasenia: str


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Mapea entidades/ORM directamente

    usuario_id: int
    nombre_usuario: str
    email: str
    rol_id: int
    estado_id: int


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse


class UsuarioEstadoUpdate(BaseModel):
    estado_id: int = Field(ge=1, le=4, description="1 activo, 2 inactivo, 3 suspendido, 4 eliminado")


# ============ Contacto ============
class ContactoUpdate(BaseModel):
    phone_personal: Optional[str] = Field(default=None, max_length=20)
    phone_trabajo: Optional[str] = Field(default=None, max_length=20)
    domicilio: Optional[str] = Field(default=None, max_length=255)


class ContactoResponse(ContactoUpdate):
    model_config = ConfigDict(from_attributes=True)

    contacto_id: int
    usuario_id: int


# ============ Dirección ============
class DireccionCreate(BaseModel):
    direccion_texto: str = Field(min_length=1, max_length=255)
    latitud: Optional[float] = Field(default=None, ge=-90, le=90)
    longitud: Optional[float] = Field(default=None, ge=-180, le=180)
    referencia: Optional[str] = Field(default=None, max_length=255)
    etiqueta: Optional[str] = Field(default=None, max_length=50)
    es_temporal: bool = False


class DireccionResponse(DireccionCreate):
    model_config = ConfigDict(from_attributes=True)

    direccion_id: int
    usuario_id: int
>>>>>>> f0e3673597fade5ddff7a343f2242a88a00b6c1f
