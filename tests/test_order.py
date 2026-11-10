"""Pruebas HTTP del módulo order (incluye la integración con los demás módulos)."""
from datetime import timedelta

from src.core.clock import ahora_local
from tests.conftest import A


def test_flujo_completo_de_un_pedido(client, api):
    rid = api.crear_restaurante()
    p1, p2 = api.crear_producto(rid, 25.5), api.crear_producto(rid, 10)
    cliente, otro_cliente = api.crear_cliente(), api.crear_cliente()
    repartidor = api.crear_repartidor()

    # 1. El cliente crea el pedido; el total lo calcula el sistema
    pedido = api.crear_pedido(cliente, rid, [{"producto_id": p1, "cantidad": 2}, {"producto_id": p2, "cantidad": 1}])
    pid = pedido["pedido_id"]
    assert pedido["sum_total"] == 61.0
    assert pedido["usuario_id"] == cliente["usuario_id"]
    assert pedido["direccion_id"] == cliente["direccion_id"]

    # 2. Permisos de lectura
    assert client.get(f"{A}/orders/{pid}", headers=cliente["headers"]).status_code == 200
    assert client.get(f"{A}/orders/{pid}", headers=otro_cliente["headers"]).status_code == 403
    assert client.get(f"{A}/orders/{pid}", headers=repartidor["headers"]).status_code == 403  # aún no asignado
    assert pid in [p["pedido_id"] for p in client.get(f"{A}/orders/mios", headers=cliente["headers"]).json()]
    assert client.get(f"{A}/orders/", headers=cliente["headers"]).status_code == 403
    assert client.get(f"{A}/orders/?estado=Pendiente", headers=api.admin).status_code == 200

    # 3. Ciclo de vida
    assert api.estado(pid, "En_Preparacion", cliente["headers"]).status_code == 403  # el cliente no prepara
    assert api.estado(pid, "Entregado", api.admin).status_code == 400  # no se saltan estados
    assert api.estado(pid, "En_Preparacion", api.admin).status_code == 200
    assert client.post(f"{A}/orders/{pid}/cancelar", headers=cliente["headers"]).status_code == 400
    assert api.estado(pid, "En_Camino", api.admin).status_code == 400  # falta repartidor

    # 4. Asignar repartidor -> queda ocupado
    api.asignar(pid, repartidor)
    perfil = client.get(f"{A}/tracking/repartidores/me", headers=repartidor["headers"]).json()
    assert perfil["disponible"] is False
    assert client.get(f"{A}/orders/{pid}", headers=repartidor["headers"]).status_code == 200
    assert pid in [p["pedido_id"] for p in client.get(f"{A}/orders/mios", headers=repartidor["headers"]).json()]

    # 5. Pago en efectivo (queda Pendiente hasta la entrega)
    r = client.post(f"{A}/payments/", json={"pedido_id": pid, "monto": 61, "metodo_pago": "Efectivo"},
                    headers=cliente["headers"])
    assert r.status_code == 201 and r.json()["estado_pago"] == "Pendiente"

    # 6. El repartidor lleva y entrega
    assert api.estado(pid, "En_Camino", repartidor["headers"]).status_code == 200
    assert api.estado(pid, "Entregado", repartidor["headers"]).status_code == 200

    # 7. Al entregar: repartidor libre y pago en efectivo cobrado automáticamente
    perfil = client.get(f"{A}/tracking/repartidores/me", headers=repartidor["headers"]).json()
    assert perfil["disponible"] is True
    pago = client.get(f"{A}/payments/pedido/{pid}", headers=cliente["headers"]).json()
    assert pago["estado_pago"] == "Completado" and pago["transaccion_id"].startswith("EFE-")


def test_validaciones_al_crear(client, api):
    rid, rid_otro = api.crear_restaurante(), api.crear_restaurante()
    p1 = api.crear_producto(rid, 10)
    p_agotado = api.crear_producto(rid, 10, disponible=False)
    p_ajeno = api.crear_producto(rid_otro, 10)
    cliente, otro = api.crear_cliente(), api.crear_cliente()
    h = cliente["headers"]

    def pedir(items, direccion_id=None, headers=h, restaurant_id=rid):
        body = {"restaurant_id": restaurant_id, "direccion_id": direccion_id or cliente["direccion_id"], "items": items}
        return client.post(f"{A}/orders/", json=body, headers=headers)

    assert pedir([]).status_code == 422
    assert pedir([{"producto_id": p_ajeno, "cantidad": 1}]).status_code == 400
    assert pedir([{"producto_id": p_agotado, "cantidad": 1}]).status_code == 400
    assert pedir([{"producto_id": p1, "cantidad": 1}], direccion_id=otro["direccion_id"]).status_code == 400
    assert pedir([{"producto_id": p1, "cantidad": 1}], headers=api.admin).status_code == 403  # solo clientes
    assert pedir([{"producto_id": p1, "cantidad": 1}], restaurant_id=999999).status_code == 400

    client.patch(f"{A}/restaurants/{rid}/estado", json={"estado": "Cerrado"}, headers=api.admin)
    assert pedir([{"producto_id": p1, "cantidad": 1}]).status_code == 400
    client.patch(f"{A}/restaurants/{rid}/estado", json={"estado": "Abierto"}, headers=api.admin)
    assert pedir([{"producto_id": p1, "cantidad": 1}]).status_code == 201


def test_fuera_de_horario(client, api):
    ahora = ahora_local()
    abre = (ahora + timedelta(hours=2)).strftime("%H:%M")
    cierra = (ahora + timedelta(hours=3)).strftime("%H:%M")
    rid = api.crear_restaurante(horario_apertura=abre, horario_cierre=cierra)
    p = api.crear_producto(rid, 10)
    cliente = api.crear_cliente()

    r = client.post(
        f"{A}/orders/",
        json={"restaurant_id": rid, "direccion_id": cliente["direccion_id"], "items": [{"producto_id": p, "cantidad": 1}]},
        headers=cliente["headers"],
    )
    assert r.status_code == 400 and "atiende" in r.json()["detail"]


def test_usuario_suspendido_no_puede_pedir(client, api):
    rid = api.crear_restaurante()
    p = api.crear_producto(rid, 10)
    cliente = api.crear_cliente()
    client.patch(f"{A}/auth/users/{cliente['usuario_id']}/estado", json={"estado_id": 3}, headers=api.admin)

    r = client.post(
        f"{A}/orders/",
        json={"restaurant_id": rid, "direccion_id": cliente["direccion_id"], "items": [{"producto_id": p, "cantidad": 1}]},
        headers=cliente["headers"],  # su token sigue vigente, pero la regla lo bloquea
    )
    assert r.status_code == 400


def test_cancelar_libera_al_repartidor(client, api):
    rid = api.crear_restaurante()
    p = api.crear_producto(rid, 10)
    cliente, repartidor = api.crear_cliente(), api.crear_repartidor()
    pedido = api.crear_pedido(cliente, rid, [{"producto_id": p, "cantidad": 1}])
    api.asignar(pedido["pedido_id"], repartidor)

    # El repartidor ocupado no puede tomar otro pedido
    otro = api.crear_pedido(cliente, rid, [{"producto_id": p, "cantidad": 1}])
    r = client.patch(f"{A}/orders/{otro['pedido_id']}/repartidor",
                     json={"repartidor_id": repartidor["repartidor_id"]}, headers=api.admin)
    assert r.status_code == 400

    r = client.post(f"{A}/orders/{pedido['pedido_id']}/cancelar", headers=cliente["headers"])
    assert r.status_code == 200 and r.json()["estado"] == "Cancelado"
    perfil = client.get(f"{A}/tracking/repartidores/me", headers=repartidor["headers"]).json()
    assert perfil["disponible"] is True
