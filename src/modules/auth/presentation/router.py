# modulo auth
''' Endpoints HTTP del módulo auth. '''
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.pagination import Paginacion
from src.core.security import UsuarioActual, get_usuario_actual, get_usuario_opcional, solo_admin
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
from src.modules.auth.application.services import AuthService
from src.modules.auth.domain.exceptions import (
    DomainException,
    EntidadNoEncontradaException,
    CredencialesInvalidasException,
    AccesoDenegadoException,
)

router = APIRouter()


def _a_http(e: DomainException) -> HTTPException:
    """Traduce una excepción de dominio al código HTTP correspondiente."""
    if isinstance(e, EntidadNoEncontradaException):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    if isinstance(e, CredencialesInvalidasException):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    if isinstance(e, AccesoDenegadoException):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/health")
def auth_health():
    return {"module": "auth", "status": "ok"}


# ==================== Registro y login (públicos) ====================

@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar_usuario(
    data: UsuarioCreate,
    db: Session = Depends(get_db),
    actor: Optional[UsuarioActual] = Depends(get_usuario_opcional),
):
    try:
        return AuthService(db).registrar_usuario(data, actor)
    except DomainException as e:
        raise _a_http(e)


@router.post("/login", response_model=TokenResponse)
def login(data: UsuarioLogin, db: Session = Depends(get_db)):
    try:
        usuario, token = AuthService(db).login(data)
        return TokenResponse(access_token=token, usuario=UsuarioResponse.model_validate(usuario))
    except DomainException as e:
        raise _a_http(e)


# ==================== Mi cuenta (usuario autenticado) ====================

@router.get("/me", response_model=UsuarioResponse)
def mi_usuario(db: Session = Depends(get_db), actor: UsuarioActual = Depends(get_usuario_actual)):
    try:
        return AuthService(db).obtener_usuario(actor.usuario_id, actor)
    except DomainException as e:
        raise _a_http(e)


@router.get("/me/contacto", response_model=ContactoResponse)
def mi_contacto(db: Session = Depends(get_db), actor: UsuarioActual = Depends(get_usuario_actual)):
    try:
        return AuthService(db).obtener_contacto(actor.usuario_id)
    except DomainException as e:
        raise _a_http(e)


@router.put("/me/contacto", response_model=ContactoResponse)
def guardar_mi_contacto(
    data: ContactoUpdate,
    db: Session = Depends(get_db),
    actor: UsuarioActual = Depends(get_usuario_actual),
):
    return AuthService(db).guardar_contacto(actor.usuario_id, data)


@router.get("/me/direcciones", response_model=List[DireccionResponse])
def mis_direcciones(db: Session = Depends(get_db), actor: UsuarioActual = Depends(get_usuario_actual)):
    return AuthService(db).listar_direcciones(actor.usuario_id)


@router.post("/me/direcciones", response_model=DireccionResponse, status_code=status.HTTP_201_CREATED)
def agregar_direccion(
    data: DireccionCreate,
    db: Session = Depends(get_db),
    actor: UsuarioActual = Depends(get_usuario_actual),
):
    try:
        return AuthService(db).agregar_direccion(actor.usuario_id, data)
    except DomainException as e:
        raise _a_http(e)


@router.delete("/me/direcciones/{direccion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_direccion(
    direccion_id: int,
    db: Session = Depends(get_db),
    actor: UsuarioActual = Depends(get_usuario_actual),
):
    try:
        AuthService(db).eliminar_direccion(actor.usuario_id, direccion_id)
    except DomainException as e:
        raise _a_http(e)


# ==================== Administración de usuarios ====================

@router.get("/users", response_model=List[UsuarioResponse])
def listar_usuarios(
    pag: Paginacion = Depends(),
    db: Session = Depends(get_db),
    _: UsuarioActual = Depends(solo_admin),
):
    return AuthService(db).listar_usuarios(pag.skip, pag.limit)


@router.get("/users/{usuario_id}", response_model=UsuarioResponse)
def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    actor: UsuarioActual = Depends(get_usuario_actual),
):
    try:
        return AuthService(db).obtener_usuario(usuario_id, actor)
    except DomainException as e:
        raise _a_http(e)


@router.patch("/users/{usuario_id}/estado", response_model=UsuarioResponse)
def cambiar_estado_usuario(
    usuario_id: int,
    data: UsuarioEstadoUpdate,
    db: Session = Depends(get_db),
    actor: UsuarioActual = Depends(solo_admin),
):
    try:
        return AuthService(db).cambiar_estado_usuario(usuario_id, data.estado_id, actor)
    except DomainException as e:
        raise _a_http(e)
