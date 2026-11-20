# modulo auth
''' DTOs de la capa de aplicación.
Los DTOs HTTP (entrada/salida) se definen en presentation/schemas.py y se reutilizan aquí.
'''
from src.modules.auth.presentation.schemas import (
    UsuarioCreate,
    UsuarioLogin,
    UsuarioResponse,
    TokenResponse,
    UsuarioEstadoUpdate,
    ContactoUpdate,
    ContactoResponse,
    DireccionCreate,
    DireccionResponse,
)

__all__ = [
    "UsuarioCreate",
    "UsuarioLogin",
    "UsuarioResponse",
    "TokenResponse",
    "UsuarioEstadoUpdate",
    "ContactoUpdate",
    "ContactoResponse",
    "DireccionCreate",
    "DireccionResponse",
]
