# modulo tracking
''' Endpoints HTTP del módulo tracking. '''
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.modules.tracking.presentation.schemas import (
    RepartidorCreate,
    DisponibilidadUpdate,
    RepartidorResponse,
    UbicacionCreate,
    UbicacionResponse,
    SeguimientoPedidoResponse,
)
from src.modules.tracking.application.services import TrackingService
from src.modules.tracking.domain.exceptions import DomainException, EntidadNoEncontradaException

router = APIRouter()


def _a_http(e: DomainException) -> HTTPException:
    """Traduce una excepción de dominio al código HTTP correspondiente."""
    if isinstance(e, EntidadNoEncontradaException):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/health")
def tracking_health():
    return {"module": "tracking", "status": "ok"}


# ==================== Repartidores ====================

@router.post("/repartidores", response_model=RepartidorResponse, status_code=status.HTTP_201_CREATED)
def registrar_repartidor(data: RepartidorCreate, db: Session = Depends(get_db)):
    try:
        return TrackingService(db).registrar_repartidor(data)
    except DomainException as e:
        raise _a_http(e)


@router.get("/repartidores", response_model=List[RepartidorResponse])
def listar_repartidores(solo_disponibles: bool = False, db: Session = Depends(get_db)):
    return TrackingService(db).listar_repartidores(solo_disponibles)


@router.get("/repartidores/{repartidor_id}", response_model=RepartidorResponse)
def obtener_repartidor(repartidor_id: int, db: Session = Depends(get_db)):
    try:
        return TrackingService(db).obtener_repartidor(repartidor_id)
    except DomainException as e:
        raise _a_http(e)


@router.patch("/repartidores/{repartidor_id}/disponibilidad", response_model=RepartidorResponse)
def cambiar_disponibilidad(repartidor_id: int, data: DisponibilidadUpdate, db: Session = Depends(get_db)):
    try:
        return TrackingService(db).cambiar_disponibilidad(repartidor_id, data.disponible)
    except DomainException as e:
        raise _a_http(e)


# ==================== Ubicaciones (GPS) ====================

@router.post(
    "/repartidores/{repartidor_id}/ubicaciones",
    response_model=UbicacionResponse,
    status_code=status.HTTP_201_CREATED,
)
def registrar_ubicacion(repartidor_id: int, data: UbicacionCreate, db: Session = Depends(get_db)):
    try:
        return TrackingService(db).registrar_ubicacion(repartidor_id, data)
    except DomainException as e:
        raise _a_http(e)


@router.get("/repartidores/{repartidor_id}/ubicaciones", response_model=List[UbicacionResponse])
def historial_ubicaciones(repartidor_id: int, db: Session = Depends(get_db)):
    try:
        return TrackingService(db).historial_ubicaciones(repartidor_id)
    except DomainException as e:
        raise _a_http(e)


@router.get("/repartidores/{repartidor_id}/ubicacion-actual", response_model=UbicacionResponse)
def ubicacion_actual(repartidor_id: int, db: Session = Depends(get_db)):
    try:
        return TrackingService(db).ubicacion_actual(repartidor_id)
    except DomainException as e:
        raise _a_http(e)


# ==================== Seguimiento de pedido ====================

@router.get("/pedido/{pedido_id}", response_model=SeguimientoPedidoResponse)
def seguimiento_pedido(pedido_id: int, db: Session = Depends(get_db)):
    try:
        return TrackingService(db).seguimiento_pedido(pedido_id)
    except DomainException as e:
        raise _a_http(e)
