# modulo auth
''' DTOs de Pydantic para validar entradas y salidas HTTP. '''
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioCreate(BaseModel):
    nombre_usuario: str = Field(min_length=1, max_length=64)
    email: EmailStr
    contrasenia: str
    rol_id: int = 1      # 1 = cliente, 2 = repartidor, 3 = admin
    estado_id: int = 1   # 1 = activo


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
