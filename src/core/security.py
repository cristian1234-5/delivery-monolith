"""
Seguridad compartida por todos los módulos (Shared Kernel).
========================================
- Genera y valida tokens JWT.
- Dependencias de FastAPI para exigir login y roles.

El módulo auth emite el token al hacer login; los demás módulos solo
lo validan, sin consultar la base de datos de usuarios.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES

ALGORITHM = "HS256"

# IDs de la tabla rol (init.sql)
ROL_CLIENTE = 1
ROL_REPARTIDOR = 2
ROL_ADMIN = 3


@dataclass(frozen=True)
class UsuarioActual:
    """Datos del usuario que hace la petición (extraídos del token)."""
    usuario_id: int
    rol_id: int

    @property
    def es_admin(self) -> bool:
        return self.rol_id == ROL_ADMIN

    @property
    def es_cliente(self) -> bool:
        return self.rol_id == ROL_CLIENTE

    @property
    def es_repartidor(self) -> bool:
        return self.rol_id == ROL_REPARTIDOR


def crear_token(usuario_id: int, rol_id: int) -> str:
    expira = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(usuario_id), "rol": rol_id, "exp": expira}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _no_autorizado(mensaje: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=mensaje,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _decodificar(token: str) -> UsuarioActual:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return UsuarioActual(usuario_id=int(payload["sub"]), rol_id=int(payload["rol"]))
    except jwt.ExpiredSignatureError:
        raise _no_autorizado("El token expiró. Inicie sesión nuevamente.")
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise _no_autorizado("Token inválido.")


_bearer = HTTPBearer(auto_error=False)


def get_usuario_actual(
    credenciales: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> UsuarioActual:
    """Exige un token válido (header Authorization: Bearer <token>)."""
    if not credenciales:
        raise _no_autorizado("Debe iniciar sesión (falta el token).")
    return _decodificar(credenciales.credentials)


def get_usuario_opcional(
    credenciales: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> Optional[UsuarioActual]:
    """Igual que get_usuario_actual, pero permite peticiones sin token."""
    if not credenciales:
        return None
    return _decodificar(credenciales.credentials)


def requiere_roles(*roles: int):
    """Dependencia que solo deja pasar a los roles indicados."""

    def _verificar(usuario: UsuarioActual = Depends(get_usuario_actual)) -> UsuarioActual:
        if usuario.rol_id not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para realizar esta acción.",
            )
        return usuario

    return _verificar


solo_admin = requiere_roles(ROL_ADMIN)
