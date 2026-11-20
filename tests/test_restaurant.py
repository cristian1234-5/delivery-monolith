"""Pruebas HTTP del módulo restaurant."""
from tests.conftest import A


def test_catalogo_publico_y_escritura_solo_admin(client, api):
    cliente = api.crear_usuario()
    datos = {"nombre": "Pizza Express", "direccion": "Av. 2", "horario_apertura": "10:00", "horario_cierre": "22:00"}

    assert client.get(f"{A}/restaurants/").status_code == 200  # público
    assert client.post(f"{A}/restaurants/", json=datos).status_code == 401  # sin token
    assert client.post(f"{A}/restaurants/", json=datos, headers=cliente["headers"]).status_code == 403  # no admin
    assert client.post(f"{A}/restaurants/", json={**datos, "estado": "Raro"}, headers=api.admin).status_code == 422

    r = client.post(f"{A}/restaurants/", json=datos, headers=api.admin)
    assert r.status_code == 201
    rid = r.json()["restaurant_id"]

    r = client.put(f"{A}/restaurants/{rid}", json={**datos, "nombre": "Pizza Express 2"}, headers=api.admin)
    assert r.json()["nombre"] == "Pizza Express 2"
    r = client.patch(f"{A}/restaurants/{rid}/estado", json={"estado": "Cerrado"}, headers=api.admin)
    assert r.json()["estado"] == "Cerrado"
    assert client.get(f"{A}/restaurants/999999").status_code == 404


def test_productos(client, api):
    rid = api.crear_restaurante()
    for precio in (10, 20, 30):
        api.crear_producto(rid, precio)
    api.crear_producto(rid, 5, disponible=False)

    assert len(client.get(f"{A}/restaurants/{rid}/productos").json()) == 4
    assert len(client.get(f"{A}/restaurants/{rid}/productos?solo_disponibles=true").json()) == 3
    assert len(client.get(f"{A}/restaurants/{rid}/productos?limit=2").json()) == 2  # paginación

    pid = api.crear_producto(rid, 15)
    r = client.put(
        f"{A}/restaurants/productos/{pid}",
        json={"nombre": "Combo", "precio": 18.5, "categoria": "Combos"},
        headers=api.admin,
    )
    assert r.json()["precio"] == 18.5
    assert client.post(
        f"{A}/restaurants/{rid}/productos", json={"nombre": "X", "precio": -1, "categoria": "C"}, headers=api.admin
    ).status_code == 422
    assert client.delete(f"{A}/restaurants/productos/{pid}", headers=api.admin).status_code == 204
    assert client.get(f"{A}/restaurants/productos/{pid}").status_code == 404


def test_no_se_borra_lo_que_tiene_pedidos(client, api):
    """Antes daba error 500; ahora la API responde 409 con un mensaje claro."""
    rid = api.crear_restaurante()
    pid = api.crear_producto(rid, 10)
    api.crear_pedido(api.crear_cliente(), rid, [{"producto_id": pid, "cantidad": 1}])

    r = client.delete(f"{A}/restaurants/productos/{pid}", headers=api.admin)
    assert r.status_code == 409 and "relacionado" in r.json()["detail"]
    assert client.delete(f"{A}/restaurants/{rid}", headers=api.admin).status_code == 409
    # Después del error, la API sigue funcionando normalmente
    assert client.get(f"{A}/restaurants/{rid}").status_code == 200
