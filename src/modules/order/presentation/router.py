# modulo order
''' Endpoints HTTP del módulo order. '''
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.modules.order.presentation.schemas import (
    PedidoCreate,
    PedidoEstadoUpdate,
    AsignarRepartidor,
    PedidoResponse,
    EstadoPedido,
)
from src.modules.order.application.services import OrderService
from src.modules.order.domain.exceptions import DomainException, EntidadNoEncontradaException

router = APIRouter()


def _a_http(e: DomainException) -> HTTPException:
    """Traduce una excepción de dominio al código HTTP correspondiente."""
    if isinstance(e, EntidadNoEncontradaException):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Las rutas fijas (/health, /usuario/...) van ANTES de /{pedido_id}
@router.get("/health")
def order_health():
    return {"module": "order", "status": "ok"}


@router.post("/", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
def crear_pedido(data: PedidoCreate, db: Session = Depends(get_db)):
    try:
        return OrderService(db).crear_pedido(data)
    except DomainException as e:
        raise _a_http(e)


@router.get("/", response_model=List[PedidoResponse])
def listar_pedidos(estado: Optional[EstadoPedido] = None, db: Session = Depends(get_db)):
    return OrderService(db).listar_pedidos(estado)


@router.get("/usuario/{usuario_id}", response_model=List[PedidoResponse])
def listar_pedidos_usuario(usuario_id: int, db: Session = Depends(get_db)):
    return OrderService(db).listar_pedidos_usuario(usuario_id)


@router.get("/{pedido_id}", response_model=PedidoResponse)
def obtener_pedido(pedido_id: int, db: Session = Depends(get_db)):
    try:
        return OrderService(db).obtener_pedido(pedido_id)
    except DomainException as e:
        raise _a_http(e)


@router.patch("/{pedido_id}/estado", response_model=PedidoResponse)
def cambiar_estado(pedido_id: int, data: PedidoEstadoUpdate, db: Session = Depends(get_db)):
    try:
        return OrderService(db).cambiar_estado(pedido_id, data.estado)
    except DomainException as e:
        raise _a_http(e)


@router.post("/{pedido_id}/cancelar", response_model=PedidoResponse)
def cancelar_pedido(pedido_id: int, db: Session = Depends(get_db)):
    try:
        return OrderService(db).cancelar_pedido(pedido_id)
    except DomainException as e:
        raise _a_http(e)


@router.patch("/{pedido_id}/repartidor", response_model=PedidoResponse)
def asignar_repartidor(pedido_id: int, data: AsignarRepartidor, db: Session = Depends(get_db)):
    try:
        return OrderService(db).asignar_repartidor(pedido_id, data.repartidor_id)
    except DomainException as e:
        raise _a_http(e)
