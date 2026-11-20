# modulo restaurant
''' Endpoints HTTP del módulo restaurant.
Consultar el catálogo es público; crear/modificar/eliminar es solo para el admin.
'''
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.pagination import Paginacion
from src.core.security import UsuarioActual, solo_admin
from src.modules.restaurant.presentation.schemas import (
    RestauranteCreate,
    RestauranteEstadoUpdate,
    RestauranteResponse,
    ProductoCreate,
    ProductoResponse,
)
from src.modules.restaurant.application.services import RestaurantService
from src.modules.restaurant.domain.exceptions import DomainException, EntidadNoEncontradaException

router = APIRouter()


def _a_http(e: DomainException) -> HTTPException:
    """Traduce una excepción de dominio al código HTTP correspondiente."""
    if isinstance(e, EntidadNoEncontradaException):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/health")
def restaurant_health():
    return {"module": "restaurant", "status": "ok"}


# ==================== Restaurantes ====================

@router.post("/", response_model=RestauranteResponse, status_code=status.HTTP_201_CREATED)
def crear_restaurante(
    data: RestauranteCreate, db: Session = Depends(get_db), _: UsuarioActual = Depends(solo_admin)
):
    try:
        return RestaurantService(db).crear_restaurante(data)
    except DomainException as e:
        raise _a_http(e)


@router.get("/", response_model=List[RestauranteResponse])
def listar_restaurantes(solo_abiertos: bool = False, pag: Paginacion = Depends(), db: Session = Depends(get_db)):
    return RestaurantService(db).listar_restaurantes(solo_abiertos, pag.skip, pag.limit)


@router.get("/{restaurant_id}", response_model=RestauranteResponse)
def obtener_restaurante(restaurant_id: int, db: Session = Depends(get_db)):
    try:
        return RestaurantService(db).obtener_restaurante(restaurant_id)
    except DomainException as e:
        raise _a_http(e)


@router.put("/{restaurant_id}", response_model=RestauranteResponse)
def actualizar_restaurante(
    restaurant_id: int,
    data: RestauranteCreate,
    db: Session = Depends(get_db),
    _: UsuarioActual = Depends(solo_admin),
):
    try:
        return RestaurantService(db).actualizar_restaurante(restaurant_id, data)
    except DomainException as e:
        raise _a_http(e)


@router.patch("/{restaurant_id}/estado", response_model=RestauranteResponse)
def cambiar_estado(
    restaurant_id: int,
    data: RestauranteEstadoUpdate,
    db: Session = Depends(get_db),
    _: UsuarioActual = Depends(solo_admin),
):
    try:
        return RestaurantService(db).cambiar_estado(restaurant_id, data.estado)
    except DomainException as e:
        raise _a_http(e)


@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_restaurante(
    restaurant_id: int, db: Session = Depends(get_db), _: UsuarioActual = Depends(solo_admin)
):
    try:
        RestaurantService(db).eliminar_restaurante(restaurant_id)
    except DomainException as e:
        raise _a_http(e)


# ==================== Productos (menú) ====================

@router.post(
    "/{restaurant_id}/productos",
    response_model=ProductoResponse,
    status_code=status.HTTP_201_CREATED,
)
def agregar_producto(
    restaurant_id: int,
    data: ProductoCreate,
    db: Session = Depends(get_db),
    _: UsuarioActual = Depends(solo_admin),
):
    try:
        return RestaurantService(db).agregar_producto(restaurant_id, data)
    except DomainException as e:
        raise _a_http(e)


@router.get("/{restaurant_id}/productos", response_model=List[ProductoResponse])
def listar_productos(
    restaurant_id: int,
    solo_disponibles: bool = False,
    pag: Paginacion = Depends(),
    db: Session = Depends(get_db),
):
    try:
        return RestaurantService(db).listar_productos(restaurant_id, solo_disponibles, pag.skip, pag.limit)
    except DomainException as e:
        raise _a_http(e)


@router.get("/productos/{producto_id}", response_model=ProductoResponse)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    try:
        return RestaurantService(db).obtener_producto(producto_id)
    except DomainException as e:
        raise _a_http(e)


@router.put("/productos/{producto_id}", response_model=ProductoResponse)
def actualizar_producto(
    producto_id: int,
    data: ProductoCreate,
    db: Session = Depends(get_db),
    _: UsuarioActual = Depends(solo_admin),
):
    try:
        return RestaurantService(db).actualizar_producto(producto_id, data)
    except DomainException as e:
        raise _a_http(e)


@router.delete("/productos/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(producto_id: int, db: Session = Depends(get_db), _: UsuarioActual = Depends(solo_admin)):
    try:
        RestaurantService(db).eliminar_producto(producto_id)
    except DomainException as e:
        raise _a_http(e)
