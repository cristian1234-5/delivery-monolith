# modulo payment
''' Endpoints HTTP del módulo payment. '''
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.pagination import Paginacion
from src.core.security import UsuarioActual, get_usuario_actual, solo_admin
from src.modules.payment.presentation.schemas import PagoCreate, PagoResponse
from src.modules.payment.application.services import PaymentService
from src.modules.payment.domain.exceptions import (
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
def payment_health():
    return {"module": "payment", "status": "ok"}


@router.post("/", response_model=PagoResponse, status_code=status.HTTP_201_CREATED)
def procesar_pago(data: PagoCreate, db: Session = Depends(get_db), actor: UsuarioActual = Depends(get_usuario_actual)):
    try:
        return PaymentService(db).procesar_pago(data, actor)
    except DomainException as e:
        raise _a_http(e)


@router.get("/", response_model=List[PagoResponse])
def listar_pagos(pag: Paginacion = Depends(), db: Session = Depends(get_db), _: UsuarioActual = Depends(solo_admin)):
    return PaymentService(db).listar_pagos(pag.skip, pag.limit)


@router.get("/pedido/{pedido_id}", response_model=PagoResponse)
def obtener_pago_de_pedido(
    pedido_id: int, db: Session = Depends(get_db), actor: UsuarioActual = Depends(get_usuario_actual)
):
    try:
        return PaymentService(db).obtener_pago_de_pedido(pedido_id, actor)
    except DomainException as e:
        raise _a_http(e)


@router.get("/{pago_id}", response_model=PagoResponse)
def obtener_pago(pago_id: int, db: Session = Depends(get_db), actor: UsuarioActual = Depends(get_usuario_actual)):
    try:
        return PaymentService(db).obtener_pago(pago_id, actor)
    except DomainException as e:
        raise _a_http(e)


@router.patch("/{pago_id}/confirmar", response_model=PagoResponse)
def confirmar_pago_efectivo(
    pago_id: int, db: Session = Depends(get_db), actor: UsuarioActual = Depends(get_usuario_actual)
):
    try:
        return PaymentService(db).confirmar_pago_efectivo(pago_id, actor)
    except DomainException as e:
        raise _a_http(e)
