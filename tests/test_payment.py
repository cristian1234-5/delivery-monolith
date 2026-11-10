"""Pruebas HTTP del módulo payment."""
from tests.conftest import A


def _preparar(api, precio=20):
    rid = api.crear_restaurante()
    p = api.crear_producto(rid, precio)
    cliente = api.crear_cliente()
    pedido = api.crear_pedido(cliente, rid, [{"producto_id": p, "cantidad": 1}])
    return cliente, pedido["pedido_id"]


def test_pago_con_tarjeta(client, api):
    cliente, pid = _preparar(api)
    otro = api.crear_cliente()
    pagar = lambda monto, metodo, headers: client.post(  # noqa: E731
        f"{A}/payments/", json={"pedido_id": pid, "monto": monto, "metodo_pago": metodo}, headers=headers
    )

    assert pagar(5, "Tarjeta", cliente["headers"]).status_code == 400  # monto distinto al total
    assert pagar(20, "Tarjeta", otro["headers"]).status_code == 403  # no es su pedido
    assert pagar(20, "Bitcoin", cliente["headers"]).status_code == 422

    r = pagar(20, "Tarjeta", cliente["headers"])
    assert r.status_code == 201
    pago = r.json()
    assert pago["estado_pago"] == "Completado" and pago["transaccion_id"].startswith("TXN-")
    assert pagar(20, "QR", cliente["headers"]).status_code == 400  # ya pagado

    assert client.get(f"{A}/payments/pedido/{pid}", headers=cliente["headers"]).status_code == 200
    assert client.get(f"{A}/payments/{pago['pago_id']}", headers=otro["headers"]).status_code == 403
    assert client.get(f"{A}/payments/", headers=cliente["headers"]).status_code == 403
    assert client.get(f"{A}/payments/?limit=1", headers=api.admin).status_code == 200
    # Solo el efectivo se confirma a mano
    assert client.patch(f"{A}/payments/{pago['pago_id']}/confirmar", headers=api.admin).status_code == 400


def test_efectivo_lo_confirma_el_repartidor_asignado(client, api):
    cliente, pid = _preparar(api, precio=30)
    repartidor, otro_repartidor = api.crear_repartidor(), api.crear_repartidor()

    r = client.post(f"{A}/payments/", json={"pedido_id": pid, "monto": 30, "metodo_pago": "Efectivo"},
                    headers=cliente["headers"])
    pago_id = r.json()["pago_id"]

    api.asignar(pid, repartidor)
    assert client.patch(f"{A}/payments/{pago_id}/confirmar", headers=otro_repartidor["headers"]).status_code == 403
    assert client.patch(f"{A}/payments/{pago_id}/confirmar", headers=cliente["headers"]).status_code == 403
    r = client.patch(f"{A}/payments/{pago_id}/confirmar", headers=repartidor["headers"])
    assert r.status_code == 200 and r.json()["estado_pago"] == "Completado"


def test_no_se_paga_un_pedido_cancelado(client, api):
    cliente, pid = _preparar(api, precio=10)
    client.post(f"{A}/orders/{pid}/cancelar", headers=cliente["headers"])
    r = client.post(f"{A}/payments/", json={"pedido_id": pid, "monto": 10, "metodo_pago": "QR"},
                    headers=cliente["headers"])
    assert r.status_code == 400
