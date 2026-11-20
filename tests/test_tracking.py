"""Pruebas HTTP del módulo tracking."""
from tests.conftest import A


def test_registro_de_repartidores(client, api):
    cliente = api.crear_usuario(rol_id=1)
    usuario_rep = api.crear_usuario(rol_id=2)
    url = f"{A}/tracking/repartidores"

    assert client.post(url, json={"tipo_vehiculo": "Moto"}, headers=api.admin).status_code == 400  # sin placa
    assert client.post(url, json={"tipo_vehiculo": "Bicicleta", "usuario_id": cliente["usuario_id"]},
                       headers=api.admin).status_code == 400  # no tiene rol repartidor
    assert client.post(url, json={"tipo_vehiculo": "Bicicleta"}, headers=cliente["headers"]).status_code == 403

    r = client.post(url, json={"tipo_vehiculo": "Bicicleta", "usuario_id": usuario_rep["usuario_id"]}, headers=api.admin)
    assert r.status_code == 201
    rep_id = r.json()["repartidor_id"]
    assert client.post(url, json={"tipo_vehiculo": "Bicicleta", "usuario_id": usuario_rep["usuario_id"]},
                       headers=api.admin).status_code == 400  # ya es repartidor

    assert client.get(url, headers=api.admin).status_code == 200
    assert client.get(url, headers=cliente["headers"]).status_code == 403
    assert client.get(f"{url}/me", headers=usuario_rep["headers"]).json()["repartidor_id"] == rep_id
    assert client.get(f"{url}/me", headers=cliente["headers"]).status_code == 403

    otro = api.crear_repartidor()
    assert client.get(f"{url}/{rep_id}", headers=otro["headers"]).status_code == 403
    r = client.patch(f"{url}/{rep_id}/disponibilidad", json={"disponible": False}, headers=usuario_rep["headers"])
    assert r.status_code == 200 and r.json()["disponible"] is False


def test_ubicaciones_y_seguimiento(client, api):
    rid = api.crear_restaurante()
    p = api.crear_producto(rid, 10)
    cliente, otro_cliente = api.crear_cliente(), api.crear_cliente()
    rep = api.crear_repartidor()
    pid = api.crear_pedido(cliente, rid, [{"producto_id": p, "cantidad": 1}])["pedido_id"]
    api.asignar(pid, rep)
    base = f"{A}/tracking/repartidores/{rep['repartidor_id']}"

    assert client.get(f"{base}/ubicacion-actual", headers=rep["headers"]).status_code == 404
    gps = {"latitud": -17.7833, "longitud": -63.1821}
    assert client.post(f"{base}/ubicaciones", json=gps, headers=api.admin).status_code == 403  # solo él mismo
    assert client.post(f"{base}/ubicaciones", json={"latitud": 100, "longitud": 0}, headers=rep["headers"]).status_code == 422
    assert client.post(f"{base}/ubicaciones", json=gps, headers=rep["headers"]).status_code == 201
    client.post(f"{base}/ubicaciones", json={"latitud": -17.79, "longitud": -63.19}, headers=rep["headers"])

    assert client.get(f"{base}/ubicacion-actual", headers=rep["headers"]).json()["latitud"] == -17.79
    assert len(client.get(f"{base}/ubicaciones?limit=1", headers=api.admin).json()) == 1

    seg = client.get(f"{A}/tracking/pedido/{pid}", headers=cliente["headers"])
    assert seg.status_code == 200
    assert seg.json()["repartidor"]["repartidor_id"] == rep["repartidor_id"]
    assert seg.json()["ubicacion_actual"]["latitud"] == -17.79
    assert client.get(f"{A}/tracking/pedido/{pid}", headers=otro_cliente["headers"]).status_code == 403
    assert client.get(f"{A}/tracking/pedido/999999", headers=api.admin).status_code == 404
