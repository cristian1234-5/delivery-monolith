"""
Pruebas unitarias del DOMINIO: no usan base de datos, ni FastAPI, ni Docker.
Es la ventaja principal de DDD: las reglas de negocio se prueban solas.
"""
from datetime import time
from decimal import Decimal

import pytest

from src.modules.auth.domain.models import Usuario, Direccion
from src.modules.auth.domain.exceptions import DatosInvalidosException
from src.modules.restaurant.domain.models import Restaurante, Producto
from src.modules.restaurant.domain.exceptions import DomainException as RestaurantError
from src.modules.order.domain.models import Pedido, DetallePedido
from src.modules.order.domain.exceptions import (
    PedidoInvalidoException,
    TransicionEstadoInvalidaException,
    CancelacionNoPermitidaException,
)
from src.modules.payment.domain.models import Pago
from src.modules.payment.domain.exceptions import PagoInvalidoException
from src.modules.tracking.domain.models import Repartidor, UbicacionTracking
from src.modules.tracking.domain.exceptions import (
    DatosRepartidorInvalidosException,
    UbicacionInvalidaException,
)


# ==================== auth ====================

def test_usuario_password_minima():
    u = Usuario(nombre_usuario="ana", email="a@a.com", contrasenia="", rol_id=1, estado_id=1)
    with pytest.raises(ValueError):
        u.cambiar_password("123")
    u.cambiar_password("123456")
    assert u.contrasenia == "123456"


def test_usuario_estado():
    u = Usuario(nombre_usuario="ana", email="a@a.com", contrasenia="x", rol_id=1, estado_id=1)
    assert u.esta_activo()
    u.cambiar_estado(3)
    assert not u.esta_activo()
    with pytest.raises(DatosInvalidosException):
        u.cambiar_estado(99)


def test_direccion_coordenadas():
    with pytest.raises(DatosInvalidosException):
        Direccion(usuario_id=1, direccion_texto="Calle", latitud=120)
    with pytest.raises(DatosInvalidosException):
        Direccion(usuario_id=1, direccion_texto="  ")


# ==================== restaurant ====================

def test_restaurante_horario_normal():
    r = Restaurante(nombre="R", direccion="D", horario_apertura=time(10), horario_cierre=time(22))
    assert r.esta_en_horario(time(12))
    assert not r.esta_en_horario(time(23))
    assert not r.esta_en_horario(time(22))  # a la hora de cierre ya no atiende


def test_restaurante_horario_cruza_medianoche():
    r = Restaurante(nombre="R", direccion="D", horario_apertura=time(18), horario_cierre=time(2))
    assert r.esta_en_horario(time(23))
    assert r.esta_en_horario(time(1))
    assert not r.esta_en_horario(time(12))


def test_restaurante_sin_horario_atiende_siempre():
    assert Restaurante(nombre="R", direccion="D").esta_en_horario(time(3))


def test_restaurante_y_producto_invalidos():
    with pytest.raises(RestaurantError):
        Restaurante(nombre="R", direccion="D", estado="Raro")
    with pytest.raises(RestaurantError):
        Producto(nombre="P", precio=-1, categoria="C", restaurant_id=1)


# ==================== order ====================

def _pedido():
    return Pedido(
        usuario_id=1,
        restaurant_id=1,
        direccion_id=1,
        detalles=[
            DetallePedido(producto_id=1, cantidad=2, precio_unitario=Decimal("25.50")),
            DetallePedido(producto_id=2, cantidad=1, precio_unitario=Decimal("10")),
        ],
    )


def test_pedido_calcula_total():
    p = _pedido()
    p.validar_nuevo()
    assert p.sum_total == Decimal("61.00")


def test_pedido_requiere_items_y_direccion():
    with pytest.raises(PedidoInvalidoException):
        Pedido(usuario_id=1, restaurant_id=1, direccion_id=1).validar_nuevo()
    p = _pedido()
    p.direccion_id = None
    with pytest.raises(PedidoInvalidoException):
        p.validar_nuevo()
    with pytest.raises(PedidoInvalidoException):
        DetallePedido(producto_id=1, cantidad=0, precio_unitario=1)


def test_pedido_ciclo_de_vida():
    p = _pedido()
    with pytest.raises(TransicionEstadoInvalidaException):
        p.cambiar_estado("Entregado")  # no se puede saltar estados
    p.cambiar_estado("En_Preparacion")
    with pytest.raises(CancelacionNoPermitidaException):
        p.cancelar()  # ya se está preparando
    with pytest.raises(TransicionEstadoInvalidaException):
        p.cambiar_estado("En_Camino")  # falta repartidor
    p.asignar_repartidor(7)
    p.cambiar_estado("En_Camino")
    p.cambiar_estado("Entregado")
    assert p.esta_finalizado()


def test_pedido_cancelar_pendiente():
    p = _pedido()
    p.cancelar()
    assert p.estado == "Cancelado"
    with pytest.raises(CancelacionNoPermitidaException):
        p.cancelar()


# ==================== payment ====================

def test_pago_reglas():
    with pytest.raises(PagoInvalidoException):
        Pago(pedido_id=1, monto=0, metodo_pago="QR")
    with pytest.raises(PagoInvalidoException):
        Pago(pedido_id=1, monto=10, metodo_pago="Bitcoin")
    pago = Pago(pedido_id=1, monto=10, metodo_pago="Efectivo")
    assert pago.es_contra_entrega() and pago.estado_pago == "Pendiente"
    pago.completar("EFE-1")
    with pytest.raises(PagoInvalidoException):
        pago.completar("EFE-2")  # no se cobra dos veces


# ==================== tracking ====================

def test_repartidor_placa_obligatoria():
    with pytest.raises(DatosRepartidorInvalidosException):
        Repartidor(tipo_vehiculo="Moto")
    with pytest.raises(DatosRepartidorInvalidosException):
        Repartidor(tipo_vehiculo="Avion", placa="X")
    assert Repartidor(tipo_vehiculo="Bicicleta").disponible


def test_ubicacion_valida():
    with pytest.raises(UbicacionInvalidaException):
        UbicacionTracking(repartidor_id=1, latitud=95, longitud=0)
    with pytest.raises(UbicacionInvalidaException):
        UbicacionTracking(repartidor_id=1, latitud=0, longitud=-181)
