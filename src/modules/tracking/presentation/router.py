# modulo tracking
''' Endpoints HTTP del módulo tracking. '''
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.pagination import Paginacion
from src.core.security import UsuarioActual, get_usuario_actual, requiere_roles, solo_admin, ROL_REPARTIDOR
from src.modules.tracking.presentation.schemas import (
    RepartidorCreate,
    DisponibilidadUpdate,
    RepartidorResponse,
    UbicacionCreate,
    UbicacionResponse,
    SeguimientoPedidoResponse,
)
from src.modules.tracking.application.services import TrackingService
from src.modules.tracking.domain.exceptions import (
    DomainException,
    EntidadNoEncontradaException,
    AccesoDenegadoException,
)

router = APIRouter()


def _a_http(e: DomainException) -> HTTPException:
    """Traduce una excepción de dominio al código HTTP correspondiente."""
    if isinstance(e, EntidadNoEncontradaException):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    if isinstance(e, AccesoDenegadoException):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/health")
def tracking_health():
    return {"module": "tracking", "status": "ok"}


# ==================== Repartidores ====================

@router.post("/repartidores", response_model=RepartidorResponse, status_code=status.HTTP_201_CREATED)
def registrar_repartidor(data: RepartidorCreate, db: Session = Depends(get_db), _: UsuarioActual = Depends(solo_admin)):
    try:
        return TrackingService(db).registrar_repartidor(data)
    except DomainException as e:
        raise _a_http(e)


@router.get("/repartidores", response_model=List[RepartidorResponse])
def listar_repartidores(
    solo_disponibles: bool = False,
    pag: Paginacion = Depends(),
    db: Session = Depends(get_db),
    _: UsuarioActual = Depends(solo_admin),
):
    return TrackingService(db).listar_repartidores(solo_disponibles, pag.skip, pag.limit)


# /repartidores/me va ANTES de /repartidores/{repartidor_id}
@router.get("/repartidores/me", response_model=RepartidorResponse)
def mi_perfil_repartidor(
    db: Session = Depends(get_db), actor: UsuarioActual = Depends(requiere_roles(ROL_REPARTIDOR))
):
    try:
        return TrackingService(db).mi_perfil(actor)
    except DomainException as e:
        raise _a_http(e)


@router.get("/repartidores/{repartidor_id}", response_model=RepartidorResponse)
def obtener_repartidor(
    repartidor_id: int, db: Session = Depends(get_db), actor: UsuarioActual = Depends(get_usuario_actual)
):
    try:
        return TrackingService(db).obtener_repartidor(repartidor_id, actor)
    except DomainException as e:
        raise _a_http(e)


@router.patch("/repartidores/{repartidor_id}/disponibilidad", response_model=RepartidorResponse)
def cambiar_disponibilidad(
    repartidor_id: int,
    data: DisponibilidadUpdate,
    db: Session = Depends(get_db),
    actor: UsuarioActual = Depends(get_usuario_actual),
):
    try:
        return TrackingService(db).cambiar_disponibilidad(repartidor_id, data.disponible, actor)
    except DomainException as e:
        raise _a_http(e)


# ==================== Ubicaciones (GPS) ====================

@router.post(
    "/repartidores/{repartidor_id}/ubicaciones",
    response_model=UbicacionResponse,
    status_code=status.HTTP_201_CREATED,
)
def registrar_ubicacion(
    repartidor_id: int,
    data: UbicacionCreate,
    db: Session = Depends(get_db),
    actor: UsuarioActual = Depends(get_usuario_actual),
):
    try:
        return TrackingService(db).registrar_ubicacion(repartidor_id, data, actor)
    except DomainException as e:
        raise _a_http(e)


@router.get("/repartidores/{repartidor_id}/ubicaciones", response_model=List[UbicacionResponse])
def historial_ubicaciones(
    repartidor_id: int,
    pag: Paginacion = Depends(),
    db: Session = Depends(get_db),
    actor: UsuarioActual = Depends(get_usuario_actual),
):
    try:
        return TrackingService(db).historial_ubicaciones(repartidor_id, actor, pag.skip, pag.limit)
    except DomainException as e:
        raise _a_http(e)


@router.get("/repartidores/{repartidor_id}/ubicacion-actual", response_model=UbicacionResponse)
def ubicacion_actual(
    repartidor_id: int, db: Session = Depends(get_db), actor: UsuarioActual = Depends(get_usuario_actual)
):
    try:
        return TrackingService(db).ubicacion_actual(repartidor_id, actor)
    except DomainException as e:
        raise _a_http(e)


# ==================== Seguimiento de pedido ====================

@router.get("/pedido/{pedido_id}", response_model=SeguimientoPedidoResponse)
def seguimiento_pedido(pedido_id: int, db: Session = Depends(get_db), actor: UsuarioActual = Depends(get_usuario_actual)):
    try:
        return TrackingService(db).seguimiento_pedido(pedido_id, actor)
    except DomainException as e:
        raise _a_http(e)
