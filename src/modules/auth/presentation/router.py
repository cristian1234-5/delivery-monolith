# modulo auth
''' Endpoints HTTP del módulo auth. '''
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.modules.auth.presentation.schemas import UsuarioCreate, UsuarioLogin, UsuarioResponse
from src.modules.auth.application.services import AuthService
from src.modules.auth.domain.exceptions import (
    DomainException,
    EntidadNoEncontradaException,
    CredencialesInvalidasException,
)

router = APIRouter()


def _a_http(e: DomainException) -> HTTPException:
    """Traduce una excepción de dominio al código HTTP correspondiente."""
    if isinstance(e, EntidadNoEncontradaException):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    if isinstance(e, CredencialesInvalidasException):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/health")
def auth_health():
    return {"module": "auth", "status": "ok"}


@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar_usuario(data: UsuarioCreate, db: Session = Depends(get_db)):
    try:
        return AuthService(db).registrar_usuario(data)
    except DomainException as e:
        raise _a_http(e)


@router.post("/login", response_model=UsuarioResponse)
def login(data: UsuarioLogin, db: Session = Depends(get_db)):
    try:
        return AuthService(db).login(data)
    except DomainException as e:
        raise _a_http(e)


@router.get("/users", response_model=List[UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    return AuthService(db).listar_usuarios()


@router.get("/users/{usuario_id}", response_model=UsuarioResponse)
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    try:
        return AuthService(db).obtener_usuario(usuario_id)
    except DomainException as e:
        raise _a_http(e)
